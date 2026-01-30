#!/usr/bin/env python3
"""
Test script for Contract Analysis Backend
Run this to verify all components work
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        import config
        import extractor
        import clause_splitter
        import law_dataset
        import vector_store
        import rule_engine
        import deviation_engine
        import risk_score
        import explanation
        import privacy_ttl
        import utils
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_law_loading():
    """Test Indian law dataset loading"""
    print("\nTesting law dataset...")
    try:
        from law_dataset import load_indian_laws
        laws = load_indian_laws()
        print(f"✅ Loaded {len(laws)} Indian law sections")
        return True
    except Exception as e:
        print(f"❌ Law loading failed: {e}")
        return False

def test_clause_splitting():
    """Test clause splitting"""
    print("\nTesting clause splitter...")
    try:
        from clause_splitter import split_clauses
        
        sample_text = """
        1. Non-Compete Agreement: The Employee agrees not to compete with the Company 
        for a period of 2 years after termination.
        
        2. Intellectual Property: All work created by Employee belongs to Company, 
        including personal projects.
        
        3. Termination: Company may terminate this agreement at sole discretion without notice.
        """
        
        clauses = split_clauses(sample_text)
        print(f"✅ Split into {len(clauses)} clauses")
        return True
    except Exception as e:
        print(f"❌ Clause splitting failed: {e}")
        return False

def test_rule_engine():
    """Test rule engine"""
    print("\nTesting rule engine...")
    try:
        from rule_engine import verify_clause
        
        # Test non-compete clause (should violate Section 27)
        test_clause = "Employee agrees not to compete with Company for 2 years after termination."
        result = verify_clause(test_clause)
        
        print(f"✅ Rule engine working")
        print(f"   - Violations found: {result['total_violations']}")
        print(f"   - Risk level: {result['risk_level']}")
        return True
    except Exception as e:
        print(f"❌ Rule engine failed: {e}")
        return False

def test_vector_store():
    """Test vector store"""
    print("\nTesting vector store...")
    try:
        from law_dataset import load_indian_laws
        from vector_store import VectorStore
        
        laws = load_indian_laws()
        store = VectorStore(laws)
        
        # Test search
        test_clause = "Employee shall not work for any competitor"
        result = store.find_relevant_law(test_clause)
        
        print(f"✅ Vector store working")
        print(f"   - Found: {result['section']}")
        return True
    except Exception as e:
        print(f"❌ Vector store failed: {e}")
        return False

def test_risk_scoring():
    """Test risk scoring"""
    print("\nTesting risk score calculator...")
    try:
        from risk_score import calculate_risk_score, get_risk_level
        
        # Mock data
        legal_check = {
            'violations': [
                {'type': 'section_27_violation', 'severity': 'critical'}
            ]
        }
        deviation = {
            'has_deviation': True,
            'deviations': [
                {'severity': 'high'}
            ]
        }
        
        score = calculate_risk_score(legal_check, deviation)
        level = get_risk_level(score)
        
        print(f"✅ Risk scoring working")
        print(f"   - Score: {score}/100")
        print(f"   - Level: {level}")
        return True
    except Exception as e:
        print(f"❌ Risk scoring failed: {e}")
        return False

def test_session_manager():
    """Test session manager"""
    print("\nTesting session manager...")
    try:
        from privacy_ttl import SessionManager
        
        manager = SessionManager()
        session_id = manager.create_session()
        manager.store_analysis(session_id, {"test": "data"})
        data = manager.get_session(session_id)
        
        print(f"✅ Session manager working")
        print(f"   - Session ID: {session_id[:8]}...")
        print(f"   - Data stored: {data is not None}")
        
        manager.shutdown()
        return True
    except Exception as e:
        print(f"❌ Session manager failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("CONTRACT ANALYSIS BACKEND - COMPONENT TESTS")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_law_loading,
        test_clause_splitting,
        test_rule_engine,
        test_vector_store,
        test_risk_scoring,
        test_session_manager,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("\n🎉 All tests passed! Backend is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run server: python app.py")
        print("3. Test API: curl http://localhost:5000/health")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())