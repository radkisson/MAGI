"""
Test suite for RIN Tools Integration
Tests the Tavily and Firecrawl tool integrations
"""

import sys
import os
import pytest

# Add tools directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))


def test_tavily_tool_import():
    """Test that Tavily tool can be imported"""
    from tavily_search import Tools as TavilyTools
    assert TavilyTools is not None


def test_tavily_tool_initialization():
    """Test Tavily tool initialization"""
    from tavily_search import Tools as TavilyTools
    tavily = TavilyTools()
    assert tavily is not None
    assert hasattr(tavily, 'valves')
    assert hasattr(tavily.valves, 'TAVILY_API_URL')
    assert tavily.valves.TAVILY_API_URL == "https://api.tavily.com/search"


def test_tavily_tool_methods_exist():
    """Test that Tavily tool has required methods"""
    from tavily_search import Tools as TavilyTools
    tavily = TavilyTools()
    
    assert hasattr(tavily, 'web_search')
    assert hasattr(tavily, 'quick_search')
    assert hasattr(tavily, 'deep_search')
    assert callable(tavily.web_search)
    assert callable(tavily.quick_search)
    assert callable(tavily.deep_search)


def test_tavily_tool_without_api_key():
    """Test Tavily tool behavior without API key"""
    from tavily_search import Tools as TavilyTools
    
    # Temporarily remove API key if it exists
    original_key = os.environ.get('TAVILY_API_KEY')
    if 'TAVILY_API_KEY' in os.environ:
        del os.environ['TAVILY_API_KEY']
    
    try:
        tavily = TavilyTools()
        result = tavily.web_search("test query")
        
        # Should return error message about missing API key
        assert "Tavily API key not configured" in result or "TAVILY_API_KEY" in result
    finally:
        # Restore original key if it existed
        if original_key:
            os.environ['TAVILY_API_KEY'] = original_key


def test_firecrawl_tool_import():
    """Test that Firecrawl tool can be imported"""
    from firecrawl_scraper import Tools as FirecrawlTools
    assert FirecrawlTools is not None


def test_firecrawl_tool_initialization():
    """Test Firecrawl tool initialization"""
    from firecrawl_scraper import Tools as FirecrawlTools
    firecrawl = FirecrawlTools()
    assert firecrawl is not None
    assert hasattr(firecrawl, 'valves')
    assert hasattr(firecrawl.valves, 'FIRECRAWL_API_URL')
    # Default should be internal Docker service
    assert "firecrawl" in firecrawl.valves.FIRECRAWL_API_URL


def test_firecrawl_tool_methods_exist():
    """Test that Firecrawl tool has required methods"""
    from firecrawl_scraper import Tools as FirecrawlTools
    firecrawl = FirecrawlTools()
    
    assert hasattr(firecrawl, 'scrape_webpage')
    assert hasattr(firecrawl, 'crawl_website')
    assert callable(firecrawl.scrape_webpage)
    assert callable(firecrawl.crawl_website)


def test_firecrawl_cloud_mode_configuration():
    """Test Firecrawl cloud mode configuration"""
    from firecrawl_scraper import Tools as FirecrawlTools
    
    # Set cloud API URL
    os.environ['FIRECRAWL_API_URL'] = 'https://api.firecrawl.dev'
    
    try:
        firecrawl = FirecrawlTools()
        assert firecrawl.valves.FIRECRAWL_API_URL == 'https://api.firecrawl.dev'
    finally:
        # Clean up
        if 'FIRECRAWL_API_URL' in os.environ:
            del os.environ['FIRECRAWL_API_URL']


def test_all_tools_have_proper_structure():
    """Test that all tools follow Open WebUI tool structure"""
    from tavily_search import Tools as TavilyTools
    from firecrawl_scraper import Tools as FirecrawlTools
    
    # Both should be classes
    assert isinstance(TavilyTools, type)
    assert isinstance(FirecrawlTools, type)
    
    # Both should have __init__
    tavily = TavilyTools()
    firecrawl = FirecrawlTools()
    
    assert tavily is not None
    assert firecrawl is not None


def test_env_example_has_tavily_key():
    """Test that .env.example includes TAVILY_API_KEY"""
    env_example_path = os.path.join(
        os.path.dirname(__file__), '..', '.env.example'
    )
    
    with open(env_example_path, 'r') as f:
        content = f.read()
        assert 'TAVILY_API_KEY' in content


def test_env_example_has_firecrawl_key():
    """Test that .env.example includes FIRECRAWL_API_KEY"""
    env_example_path = os.path.join(
        os.path.dirname(__file__), '..', '.env.example'
    )
    
    with open(env_example_path, 'r') as f:
        content = f.read()
        assert 'FIRECRAWL_API_KEY' in content


def test_tools_readme_documents_tavily():
    """Test that tools/README.md documents Tavily integration"""
    readme_path = os.path.join(
        os.path.dirname(__file__), '..', 'tools', 'README.md'
    )
    
    with open(readme_path, 'r') as f:
        content = f.read()
        assert 'Tavily' in content
        assert 'tavily_search.py' in content


def test_tools_readme_documents_firecrawl():
    """Test that tools/README.md documents Firecrawl integration"""
    readme_path = os.path.join(
        os.path.dirname(__file__), '..', 'tools', 'README.md'
    )
    
    with open(readme_path, 'r') as f:
        content = f.read()
        assert 'FireCrawl' in content or 'firecrawl' in content
        assert 'firecrawl_scraper.py' in content


if __name__ == "__main__":
    # Note: For proper pytest execution, run: pytest tests/test_tools_integration.py -v
    # This fallback is for environments without pytest installed
    print("Please run: pytest tests/test_tools_integration.py -v")
    print("Or use tests/test_tools_simple.py for direct execution without pytest")
