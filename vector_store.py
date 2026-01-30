import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
from config import EMBEDDING_MODEL, CHROMA_PERSIST_DIR, CHROMA_COLLECTION_NAME

class VectorStore:
    """
    Manages semantic search for Indian law sections using ChromaDB
    """
    
    def __init__(self, laws):
        """
        Initialize vector store with Indian laws
        
        Args:
            laws: list of law dictionaries from law_dataset.py
        """
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Initialize ChromaDB (in-memory for ephemeral use)
        self.client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            is_persistent=False
        ))
        
        # Create collection
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Add laws to collection
        self._index_laws(laws)
    
    def _index_laws(self, laws):
        """
        Index law sections into vector database
        """
        documents = []
        metadatas = []
        ids = []
        
        for idx, law in enumerate(laws):
            # Combine title and summary for better semantic matching
            text = f"{law['title']}. {law['summary']}"
            
            documents.append(text)
            metadatas.append({
                "section": law['section'],
                "act": law['act'],
                "title": law['title'],
                "full_text": law['text']
            })
            ids.append(f"law_{idx}")
        
        # Generate embeddings and add to collection
        embeddings = self.model.encode(documents).tolist()
        
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
    
    def find_relevant_law(self, clause_text, top_k=1):
        """
        Find most relevant law section for a given clause
        
        Args:
            clause_text: str - Contract clause text
            top_k: int - Number of results to return
        
        Returns:
            dict: Most relevant law with metadata
        """
        # Generate embedding for clause
        clause_embedding = self.model.encode([clause_text]).tolist()
        
        # Query collection
        results = self.collection.query(
            query_embeddings=clause_embedding,
            n_results=top_k
        )
        
        if not results['metadatas'] or not results['metadatas'][0]:
            return None
        
        # Return top result with metadata
        metadata = results['metadatas'][0][0]
        distance = results['distances'][0][0] if results['distances'] else None
        
        return {
            "section": metadata['section'],
            "act": metadata['act'],
            "title": metadata['title'],
            "text": metadata['full_text'],
            "relevance_score": 1 - distance if distance else None  # Convert distance to similarity
        }
    
    def find_multiple_relevant_laws(self, clause_text, top_k=3):
        """
        Find multiple relevant laws for a clause
        """
        clause_embedding = self.model.encode([clause_text]).tolist()
        
        results = self.collection.query(
            query_embeddings=clause_embedding,
            n_results=top_k
        )
        
        relevant_laws = []
        
        if results['metadatas'] and results['metadatas'][0]:
            for idx, metadata in enumerate(results['metadatas'][0]):
                distance = results['distances'][0][idx] if results['distances'] else None
                
                relevant_laws.append({
                    "section": metadata['section'],
                    "act": metadata['act'],
                    "title": metadata['title'],
                    "text": metadata['full_text'],
                    "relevance_score": 1 - distance if distance else None
                })
        
        return relevant_laws
    
    def search_by_keywords(self, keywords):
        """
        Search laws by keywords
        
        Args:
            keywords: list of str
        """
        query = " ".join(keywords)
        return self.find_relevant_law(query)