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


def test_firecrawl_new_valves():
    """Test that new valves are properly configured"""
    from firecrawl_scraper import Tools as FirecrawlTools, Valves as FirecrawlValves
    
    firecrawl = FirecrawlTools()
    
    # Check new valves exist
    assert hasattr(firecrawl.valves, 'REQUEST_TIMEOUT')
    assert hasattr(firecrawl.valves, 'MAX_CONTENT_LENGTH')
    assert hasattr(firecrawl.valves, 'CACHE_MAX_SIZE')
    assert hasattr(firecrawl.valves, 'CRAWL_TIMEOUT_BUFFER')
    
    # Check default values
    assert firecrawl.valves.REQUEST_TIMEOUT == 60
    assert firecrawl.valves.MAX_CONTENT_LENGTH == 20000
    assert firecrawl.valves.CACHE_MAX_SIZE == 100
    assert firecrawl.valves.CRAWL_TIMEOUT_BUFFER == 60
    
    # Test Valves class has new fields
    valves_fields = FirecrawlValves.model_fields.keys() if hasattr(FirecrawlValves, 'model_fields') else []
    assert 'REQUEST_TIMEOUT' in valves_fields
    assert 'MAX_CONTENT_LENGTH' in valves_fields
    assert 'CACHE_MAX_SIZE' in valves_fields
    assert 'CRAWL_TIMEOUT_BUFFER' in valves_fields


def test_firecrawl_cache_initialization():
    """Test that cache is initialized with thread safety"""
    from firecrawl_scraper import Tools as FirecrawlTools
    
    firecrawl = FirecrawlTools()
    assert hasattr(firecrawl, '_cache')
    assert hasattr(firecrawl, '_cache_lock')
    assert hasattr(firecrawl, '_cache_order')
    assert isinstance(firecrawl._cache, dict)
    assert len(firecrawl._cache) == 0


def test_firecrawl_cache_operations():
    """Test cache helper methods"""
    from firecrawl_scraper import Tools as FirecrawlTools
    
    firecrawl = FirecrawlTools()
    
    # Test adding to cache
    firecrawl._add_to_cache("url1", "content1")
    assert firecrawl._get_from_cache("url1") == "content1"
    assert len(firecrawl._cache) == 1
    
    # Test LRU behavior
    firecrawl._add_to_cache("url2", "content2")
    assert firecrawl._get_from_cache("url2") == "content2"
    
    # Access url1 again (should move to end)
    result = firecrawl._get_from_cache("url1")
    assert result == "content1"
    
    # Test cache miss
    assert firecrawl._get_from_cache("nonexistent") is None


def test_firecrawl_truncate_content_method():
    """Test the _truncate_content helper method"""
    from firecrawl_scraper import Tools as FirecrawlTools
    
    firecrawl = FirecrawlTools()
    
    # Test content under limit
    short_content = "A" * 1000
    result = firecrawl._truncate_content(short_content, "test.com")
    assert result == short_content
    assert "truncated" not in result
    
    # Test content over limit
    long_content = "B" * 30000
    result = firecrawl._truncate_content(long_content, "test.com")
    assert len(result) > 20000  # Should have content + truncation message
    assert len(result) < 21000  # But not too much more
    assert "truncated" in result
    assert "test.com" in result
    assert result.startswith("B" * 20000)


def test_firecrawl_crawl_website_signature():
    """Test that crawl_website has new path filtering parameters"""
    from firecrawl_scraper import Tools as FirecrawlTools
    import inspect
    
    firecrawl = FirecrawlTools()
    
    # Get the signature of crawl_website
    sig = inspect.signature(firecrawl.crawl_website)
    params = list(sig.parameters.keys())
    
    # Check that new parameters exist
    assert 'include_paths' in params
    assert 'exclude_paths' in params
    
    # Check that they have proper defaults (Optional)
    assert sig.parameters['include_paths'].default is None
    assert sig.parameters['exclude_paths'].default is None


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


def test_semantic_scholar_tool_import():
    """Test that Semantic Scholar tool can be imported"""
    from semantic_scholar import Tools as SemanticScholarTools
    assert SemanticScholarTools is not None


def test_semantic_scholar_tool_initialization():
    """Test Semantic Scholar tool initialization"""
    from semantic_scholar import Tools as SemanticScholarTools
    semantic_scholar = SemanticScholarTools()
    assert semantic_scholar is not None
    assert hasattr(semantic_scholar, 'valves')
    assert hasattr(semantic_scholar.valves, 'S2_API_URL')
    assert semantic_scholar.valves.S2_API_URL == "https://api.semanticscholar.org/graph/v1"


def test_semantic_scholar_tool_methods_exist():
    """Test that Semantic Scholar tool has required methods"""
    from semantic_scholar import Tools as SemanticScholarTools
    semantic_scholar = SemanticScholarTools()
    
    assert hasattr(semantic_scholar, 'search_papers')
    assert hasattr(semantic_scholar, 'get_paper')
    assert hasattr(semantic_scholar, 'get_author')
    assert hasattr(semantic_scholar, 'get_recommendations')
    assert hasattr(semantic_scholar, 'search_by_title')
    assert hasattr(semantic_scholar, 'get_citations')
    assert hasattr(semantic_scholar, 'get_references')
    assert hasattr(semantic_scholar, 'get_influential_citations')
    assert hasattr(semantic_scholar, 'search_recent')
    assert hasattr(semantic_scholar, 'get_paper_batch')
    
    assert callable(semantic_scholar.search_papers)
    assert callable(semantic_scholar.get_paper)
    assert callable(semantic_scholar.get_author)


def test_semantic_scholar_tool_without_api_key():
    """Test Semantic Scholar tool behavior without API key"""
    from semantic_scholar import Tools as SemanticScholarTools
    
    # Temporarily remove API key if it exists
    original_key = os.environ.get('S2_API_KEY')
    if 'S2_API_KEY' in os.environ:
        del os.environ['S2_API_KEY']
    
    try:
        semantic_scholar = SemanticScholarTools()
        # Should initialize successfully even without API key (it's optional)
        assert semantic_scholar.valves.S2_API_KEY == ""
    finally:
        # Restore original key if it existed
        if original_key:
            os.environ['S2_API_KEY'] = original_key


def test_semantic_scholar_valves():
    """Test that Semantic Scholar valves are properly configured"""
    from semantic_scholar import Tools as SemanticScholarTools, Valves as SemanticScholarValves
    
    semantic_scholar = SemanticScholarTools()
    
    # Check valves exist
    assert hasattr(semantic_scholar.valves, 'S2_API_KEY')
    assert hasattr(semantic_scholar.valves, 'S2_API_URL')
    assert hasattr(semantic_scholar.valves, 'REQUEST_TIMEOUT')
    assert hasattr(semantic_scholar.valves, 'MAX_RETRIES')
    assert hasattr(semantic_scholar.valves, 'MAX_OUTPUT_LENGTH')
    
    # Check default values
    assert semantic_scholar.valves.S2_API_URL == "https://api.semanticscholar.org/graph/v1"
    assert semantic_scholar.valves.REQUEST_TIMEOUT == 15
    assert semantic_scholar.valves.MAX_RETRIES == 2
    assert semantic_scholar.valves.MAX_OUTPUT_LENGTH == 15000
    
    # Test Valves class has fields
    valves_fields = SemanticScholarValves.model_fields.keys() if hasattr(SemanticScholarValves, 'model_fields') else []
    assert 'S2_API_KEY' in valves_fields
    assert 'S2_API_URL' in valves_fields
    assert 'REQUEST_TIMEOUT' in valves_fields
    assert 'MAX_RETRIES' in valves_fields
    assert 'MAX_OUTPUT_LENGTH' in valves_fields


def test_semantic_scholar_helper_methods():
    """Test that Semantic Scholar has helper methods"""
    from semantic_scholar import Tools as SemanticScholarTools
    
    semantic_scholar = SemanticScholarTools()
    
    # Check helper methods exist
    assert hasattr(semantic_scholar, '_normalize_paper_id')
    assert hasattr(semantic_scholar, '_make_request')
    assert hasattr(semantic_scholar, '_truncate_output')
    assert hasattr(semantic_scholar, '_format_paper')
    
    assert callable(semantic_scholar._normalize_paper_id)
    assert callable(semantic_scholar._make_request)
    assert callable(semantic_scholar._truncate_output)


def test_semantic_scholar_normalize_paper_id():
    """Test paper ID normalization"""
    from semantic_scholar import Tools as SemanticScholarTools
    
    semantic_scholar = SemanticScholarTools()
    
    # Test DOI normalization
    assert semantic_scholar._normalize_paper_id("10.1234/test") == "DOI:10.1234/test"
    # DOI URL returns DOI with prefix
    assert semantic_scholar._normalize_paper_id("https://doi.org/10.1234/test") == "DOI:10.1234/test"
    
    # Test arXiv normalization
    result = semantic_scholar._normalize_paper_id("https://arxiv.org/abs/1234.5678")
    assert "arXiv:" in result
    assert "1234.5678" in result
    
    # Test Semantic Scholar URL
    result = semantic_scholar._normalize_paper_id("https://www.semanticscholar.org/paper/abc123")
    assert result == "abc123"
    
    # Test empty string
    assert semantic_scholar._normalize_paper_id("") == ""
    assert semantic_scholar._normalize_paper_id("   ") == ""


def test_env_example_has_s2_key():
    """Test that .env.example includes S2_API_KEY"""
    env_example_path = os.path.join(
        os.path.dirname(__file__), '..', '.env.example'
    )
    
    with open(env_example_path, 'r') as f:
        content = f.read()
        assert 'S2_API_KEY' in content


def test_tools_readme_documents_semantic_scholar():
    """Test that tools/README.md documents Semantic Scholar integration"""
    readme_path = os.path.join(
        os.path.dirname(__file__), '..', 'tools', 'README.md'
    )
    
    with open(readme_path, 'r') as f:
        content = f.read()
        assert 'Semantic Scholar' in content or 'semantic_scholar' in content
        assert 'semantic_scholar.py' in content


if __name__ == "__main__":
    # Note: For proper pytest execution, run: pytest tests/test_tools_integration.py -v
    # This fallback is for environments without pytest installed
    print("Please run: pytest tests/test_tools_integration.py -v")
    print("Or use tests/test_tools_simple.py for direct execution without pytest")
