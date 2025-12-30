#!/usr/bin/env python3
"""
Integration tests for OpenAlex search tool
Tests the new methods added in v2
"""

import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))


def test_openalex_import():
    """Test that OpenAlex tool can be imported"""
    print("Testing OpenAlex Import...")
    
    try:
        from openalex_search import Tools as OpenAlexTools, Valves as OpenAlexValves
        print("  ✓ OpenAlex tool imported successfully")
        return True
    except Exception as e:
        print(f"  ❌ Failed to import: {e}")
        raise


def test_openalex_initialization():
    """Test OpenAlex tool initialization"""
    print("Testing OpenAlex Initialization...")
    
    try:
        from openalex_search import Tools as OpenAlexTools
        
        openalex = OpenAlexTools()
        print("  ✓ OpenAlex tool initialized")
        
        assert openalex is not None
        assert hasattr(openalex, 'valves')
        print("  ✓ Has valves attribute")
        
        assert hasattr(openalex.valves, 'OPENALEX_API_URL')
        assert openalex.valves.OPENALEX_API_URL == "https://api.openalex.org"
        print("  ✓ API URL configured correctly")
        
        return True
    except Exception as e:
        print(f"  ❌ Initialization failed: {e}")
        raise


def test_openalex_methods_exist():
    """Test that all required methods exist"""
    print("Testing OpenAlex Methods...")
    
    try:
        from openalex_search import Tools as OpenAlexTools
        
        openalex = OpenAlexTools()
        
        # Original methods
        assert hasattr(openalex, 'search_papers')
        assert callable(openalex.search_papers)
        print("  ✓ search_papers method exists")
        
        # New methods from v2
        assert hasattr(openalex, 'get_by_doi')
        assert callable(openalex.get_by_doi)
        print("  ✓ get_by_doi method exists")
        
        assert hasattr(openalex, 'get_references')
        assert callable(openalex.get_references)
        print("  ✓ get_references method exists")
        
        assert hasattr(openalex, 'search_by_institution')
        assert callable(openalex.search_by_institution)
        print("  ✓ search_by_institution method exists")
        
        assert hasattr(openalex, 'get_related_works')
        assert callable(openalex.get_related_works)
        print("  ✓ get_related_works method exists")
        
        assert hasattr(openalex, 'search_by_topic')
        assert callable(openalex.search_by_topic)
        print("  ✓ search_by_topic method exists")
        
        # Helper methods
        assert hasattr(openalex, '_reconstruct_abstract')
        assert callable(openalex._reconstruct_abstract)
        print("  ✓ _reconstruct_abstract helper method exists")
        
        return True
    except Exception as e:
        print(f"  ❌ Method check failed: {e}")
        raise


def test_method_signatures():
    """Test that methods have correct signatures"""
    print("Testing Method Signatures...")
    
    try:
        from openalex_search import Tools as OpenAlexTools
        import inspect
        
        openalex = OpenAlexTools()
        
        # Test get_by_doi signature
        sig = inspect.signature(openalex.get_by_doi)
        params = list(sig.parameters.keys())
        assert 'doi' in params
        assert '__user__' in params
        assert '__event_emitter__' in params
        print("  ✓ get_by_doi signature correct")
        
        # Test get_references signature
        sig = inspect.signature(openalex.get_references)
        params = list(sig.parameters.keys())
        assert 'paper_title' in params
        assert 'max_results' in params
        assert '__user__' in params
        assert '__event_emitter__' in params
        print("  ✓ get_references signature correct")
        
        # Test search_by_institution signature
        sig = inspect.signature(openalex.search_by_institution)
        params = list(sig.parameters.keys())
        assert 'institution_name' in params
        assert 'max_results' in params
        assert '__user__' in params
        assert '__event_emitter__' in params
        print("  ✓ search_by_institution signature correct")
        
        # Test get_related_works signature
        sig = inspect.signature(openalex.get_related_works)
        params = list(sig.parameters.keys())
        assert 'paper_title' in params
        assert 'max_results' in params
        assert '__user__' in params
        assert '__event_emitter__' in params
        print("  ✓ get_related_works signature correct")
        
        # Test search_by_topic signature
        sig = inspect.signature(openalex.search_by_topic)
        params = list(sig.parameters.keys())
        assert 'topic' in params
        assert 'max_results' in params
        assert 'year_from' in params
        assert 'min_citations' in params
        assert '__user__' in params
        assert '__event_emitter__' in params
        print("  ✓ search_by_topic signature correct")
        
        return True
    except Exception as e:
        print(f"  ❌ Signature check failed: {e}")
        raise


def test_error_handling():
    """Test error handling for invalid inputs"""
    print("Testing Error Handling...")
    
    try:
        from openalex_search import Tools as OpenAlexTools
        
        openalex = OpenAlexTools()
        
        # Test get_by_doi with invalid DOI
        result = openalex.get_by_doi("invalid-doi")
        assert "Invalid DOI format" in result or "Error" in result or "not found" in result.lower()
        print("  ✓ get_by_doi handles invalid DOI")
        
        # Test with empty string
        result = openalex.get_by_doi("")
        assert "Invalid DOI format" in result or "Error" in result
        print("  ✓ get_by_doi handles empty input")
        
        return True
    except Exception as e:
        print(f"  ❌ Error handling test failed: {e}")
        raise


def test_abstract_reconstruction():
    """Test the abstract reconstruction helper method"""
    print("Testing Abstract Reconstruction...")
    
    try:
        from openalex_search import Tools as OpenAlexTools
        
        openalex = OpenAlexTools()
        
        # Test with valid inverted index
        inverted_index = {
            "This": [0],
            "is": [1],
            "a": [2],
            "test": [3],
        }
        result = openalex._reconstruct_abstract(inverted_index)
        assert result == "This is a test"
        print("  ✓ Reconstructs simple abstract correctly")
        
        # Test with empty dict
        result = openalex._reconstruct_abstract({})
        assert result == ""
        print("  ✓ Handles empty dict")
        
        # Test with None
        result = openalex._reconstruct_abstract(None)
        assert result == ""
        print("  ✓ Handles None input")
        
        # Test with word in multiple positions
        inverted_index = {
            "The": [0, 4],
            "cat": [1],
            "sat": [2],
            "on": [3],
            "mat": [5],
        }
        result = openalex._reconstruct_abstract(inverted_index)
        assert result == "The cat sat on The mat"
        print("  ✓ Handles words in multiple positions")
        
        return True
    except Exception as e:
        print(f"  ❌ Abstract reconstruction test failed: {e}")
        raise


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("OpenAlex Tool Integration Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_openalex_import,
        test_openalex_initialization,
        test_openalex_methods_exist,
        test_method_signatures,
        test_error_handling,
        test_abstract_reconstruction,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print(f"✅ {test.__name__} PASSED\n")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} FAILED: {e}\n")
            import traceback
            traceback.print_exc()
    
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
