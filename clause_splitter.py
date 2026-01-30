import re
from config import MIN_CLAUSE_LENGTH, MAX_CLAUSE_LENGTH

def split_clauses(text):
    """
    Split contract text into meaningful clauses using regex and heuristics
    
    Args:
        text: str - Full contract text
    
    Returns:
        list: List of clause strings
    """
    # Normalize text
    text = normalize_text(text)
    
    # Try numbered clauses first (e.g., "1. ", "1.1 ", "Article 1")
    clauses = split_by_numbered_sections(text)
    
    # If that doesn't work well, split by periods and recombine
    if len(clauses) < 3:
        clauses = split_by_sentences(text)
    
    # Filter and clean clauses
    clauses = filter_clauses(clauses)
    
    return clauses

def normalize_text(text):
    """
    Normalize contract text for better parsing
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common formatting issues
    text = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', text)  # Fix "1 . 1" to "1.1"
    text = text.replace('\n', ' ')
    
    return text.strip()

def split_by_numbered_sections(text):
    """
    Split by numbered sections/clauses
    Patterns: "1.", "1.1", "Article 1", "Clause 1", etc.
    """
    # Common numbering patterns in contracts
    patterns = [
        r'(?:^|\s)(\d+\.\d+\.?\s+[A-Z])',  # "1.1 Title" or "1.1. Title"
        r'(?:^|\s)(\d+\.\s+[A-Z])',         # "1. Title"
        r'(?:^|\s)(Article\s+\d+)',         # "Article 1"
        r'(?:^|\s)(Clause\s+\d+)',          # "Clause 1"
        r'(?:^|\s)(Section\s+\d+)',         # "Section 1"
    ]
    
    # Try each pattern
    for pattern in patterns:
        matches = list(re.finditer(pattern, text, re.IGNORECASE))
        
        if len(matches) >= 3:  # Need at least 3 sections to be valid
            clauses = []
            
            for i in range(len(matches)):
                start = matches[i].start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                
                clause = text[start:end].strip()
                clauses.append(clause)
            
            return clauses
    
    return []

def split_by_sentences(text):
    """
    Split by sentences and intelligently recombine into clauses
    """
    # Split by sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    
    clauses = []
    current_clause = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        
        if not sentence:
            continue
        
        # Add sentence to current clause
        current_clause += " " + sentence if current_clause else sentence
        
        # Check if we should split here
        if should_split_clause(current_clause, sentence):
            clauses.append(current_clause.strip())
            current_clause = ""
    
    # Add remaining text
    if current_clause:
        clauses.append(current_clause.strip())
    
    return clauses

def should_split_clause(current_clause, last_sentence):
    """
    Heuristics to determine if we should split a clause here
    """
    # Split if clause is getting too long
    if len(current_clause) > MAX_CLAUSE_LENGTH:
        return True
    
    # Split if last sentence contains certain keywords
    split_keywords = [
        'provided that',
        'notwithstanding',
        'in consideration of',
        'the parties agree',
        'it is agreed',
        'whereas'
    ]
    
    for keyword in split_keywords:
        if keyword in last_sentence.lower():
            return True
    
    return False

def filter_clauses(clauses):
    """
    Filter out invalid/noise clauses
    """
    filtered = []
    
    for clause in clauses:
        clause = clause.strip()
        
        # Skip too short
        if len(clause) < MIN_CLAUSE_LENGTH:
            continue
        
        # Skip common header/footer noise
        noise_patterns = [
            r'^page\s+\d+',
            r'^\d+\s*$',
            r'^confidential$',
            r'^draft$',
        ]
        
        is_noise = False
        for pattern in noise_patterns:
            if re.match(pattern, clause, re.IGNORECASE):
                is_noise = True
                break
        
        if is_noise:
            continue
        
        # Skip if mostly numbers/special chars
        alpha_count = sum(c.isalpha() for c in clause)
        if alpha_count < len(clause) * 0.5:
            continue
        
        filtered.append(clause)
    
    return filtered

def extract_clause_number(clause_text):
    """
    Extract clause number if present (e.g., "1.1" from "1.1 Non-Compete")
    """
    match = re.match(r'^(\d+(?:\.\d+)?)', clause_text.strip())
    if match:
        return match.group(1)
    return None