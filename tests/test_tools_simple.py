#!/usr/bin/env python3
"""
Simple integration test for Tavily and Firecrawl tools
Does not require pytest - can be run directly
"""

import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

def test_tavily_integration():
    """Test Tavily tool integration"""
    print("Testing Tavily Integration...")
    
    try:
        from tavily_search import Tools as TavilyTools, Valves as TavilyValves
        print("  ✓ Tavily tool imported successfully")
        
        tavily = TavilyTools()
        print("  ✓ Tavily tool initialized")
        
        assert tavily.valves.TAVILY_API_URL == "https://api.tavily.com/search"
        print("  ✓ API URL configured correctly")
        
        assert hasattr(tavily, 'web_search')
        assert hasattr(tavily, 'quick_search')
        assert hasattr(tavily, 'deep_search')
        print("  ✓ All required methods present")
        
        # Test Valves class (Pydantic model)
        valves_fields = TavilyValves.model_fields.keys() if hasattr(TavilyValves, 'model_fields') else []
        assert 'TAVILY_API_KEY' in valves_fields
        assert 'TAVILY_API_URL' in valves_fields
        print("  ✓ Valves class properly configured")
        
        # Test without API key
        if 'TAVILY_API_KEY' in os.environ:
            del os.environ['TAVILY_API_KEY']
        tavily = TavilyTools()
        result = tavily.web_search("test")
        assert "TAVILY_API_KEY" in result or "not configured" in result
        print("  ✓ Handles missing API key gracefully")
        
        # Test with API key
        os.environ['TAVILY_API_KEY'] = 'test-key-123'
        tavily = TavilyTools()
        assert tavily.valves.TAVILY_API_KEY == 'test-key-123'
        print("  ✓ Environment variable loading works")
        del os.environ['TAVILY_API_KEY']
        
        print("✅ Tavily integration test PASSED\n")
    except Exception as e:
        print(f"❌ Tavily integration test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        raise


def test_firecrawl_integration():
    """Test Firecrawl tool integration"""
    print("Testing Firecrawl Integration...")
    
    try:
        from firecrawl_scraper import Tools as FirecrawlTools, Valves as FirecrawlValves
        print("  ✓ Firecrawl tool imported successfully")
        
        firecrawl = FirecrawlTools()
        print("  ✓ Firecrawl tool initialized")
        
        assert "firecrawl" in firecrawl.valves.FIRECRAWL_API_URL
        print("  ✓ Default self-hosted URL configured")
        
        assert hasattr(firecrawl, 'scrape_webpage')
        assert hasattr(firecrawl, 'crawl_website')
        print("  ✓ All required methods present")
        
        # Test Valves class (Pydantic model)
        valves_fields = FirecrawlValves.model_fields.keys() if hasattr(FirecrawlValves, 'model_fields') else []
        assert 'FIRECRAWL_API_KEY' in valves_fields
        assert 'FIRECRAWL_API_URL' in valves_fields
        print("  ✓ Valves class properly configured")
        
        # Test cloud mode configuration
        os.environ['FIRECRAWL_API_URL'] = 'https://api.firecrawl.dev'
        os.environ['FIRECRAWL_API_KEY'] = 'fc-test-123'
        firecrawl = FirecrawlTools()
        assert firecrawl.valves.FIRECRAWL_API_URL == 'https://api.firecrawl.dev'
        assert firecrawl.valves.FIRECRAWL_API_KEY == 'fc-test-123'
        print("  ✓ Cloud mode configuration works")
        
        # Clean up
        del os.environ['FIRECRAWL_API_URL']
        del os.environ['FIRECRAWL_API_KEY']
        
        # Test error handling without API key
        firecrawl = FirecrawlTools()
        result = firecrawl.scrape_webpage("https://example.com")
        assert "not configured" in result or "FIRECRAWL_API_KEY" in result
        print("  ✓ Handles missing API key gracefully")
        
        print("✅ Firecrawl integration test PASSED\n")
    except Exception as e:
        print(f"❌ Firecrawl integration test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        raise


def test_env_configuration():
    """Test .env.example has proper configuration"""
    print("Testing Environment Configuration...")
    
    try:
        env_path = os.path.join(os.path.dirname(__file__), '..', '.env.example')
        with open(env_path, 'r') as f:
            content = f.read()
        
        assert 'TAVILY_API_KEY' in content
        print("  ✓ TAVILY_API_KEY present in .env.example")
        
        assert 'FIRECRAWL_API_KEY' in content
        print("  ✓ FIRECRAWL_API_KEY present in .env.example")
        
        # Verify documentation URL for Tavily is present
        # Not a URL sanitization - just checking documentation completeness
        assert 'tavily.com' in content
        print("  ✓ Tavily documentation link present")
        
        print("✅ Environment configuration test PASSED\n")
    except Exception as e:
        print(f"❌ Environment configuration test FAILED: {e}\n")
        raise


def test_documentation():
    """Test that tools/README.md has proper documentation"""
    print("Testing Documentation...")
    
    try:
        readme_path = os.path.join(os.path.dirname(__file__), '..', 'tools', 'README.md')
        with open(readme_path, 'r') as f:
            content = f.read()
        
        assert 'Tavily' in content
        print("  ✓ Tavily documented in tools/README.md")
        
        assert 'tavily_search.py' in content
        print("  ✓ tavily_search.py mentioned")
        
        assert 'FireCrawl' in content or 'firecrawl' in content
        print("  ✓ Firecrawl documented in tools/README.md")
        
        assert 'firecrawl_scraper.py' in content
        print("  ✓ firecrawl_scraper.py mentioned")
        
        print("✅ Documentation test PASSED\n")
    except Exception as e:
        print(f"❌ Documentation test FAILED: {e}\n")
        raise


def main():
    """Run all tests"""
    print("=" * 60)
    print("RIN Tools Integration Tests")
    print("=" * 60)
    print()
    
    results = []
    results.append(test_tavily_integration())
    results.append(test_firecrawl_integration())
    results.append(test_env_configuration())
    results.append(test_documentation())
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if all(results):
        print("\n🎉 All tests PASSED!")
        return 0
    else:
        print("\n⚠️  Some tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
