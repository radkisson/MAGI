"""
Tavily Search Tool for Open WebUI

This tool connects the Cortex (Open WebUI) to Tavily API, a premium AI-optimized
search engine that provides comprehensive, real-time web search results designed
specifically for AI applications.

Tavily offers:
- AI-optimized search results with structured data
- Real-time information gathering
- Source citations and credibility scoring
- Alternative to self-hosted SearXNG
"""

import os
import requests
from typing import Callable, Any


class Tools:
    """Open WebUI Tool: AI-Optimized Web Search via Tavily API"""
    
    def __init__(self):
        # Get API key from environment
        self.api_key = os.environ.get("TAVILY_API_KEY", "")
        self.api_url = "https://api.tavily.com/search"
    
    def web_search(
        self,
        query: str,
        search_depth: str = "basic",
        max_results: int = 5,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Search the web using Tavily API (AI-Optimized Search Engine)
        
        Tavily provides AI-optimized search results designed for LLM consumption.
        Results include source citations, relevance scoring, and structured data.
        This is a premium alternative to self-hosted SearXNG.
        
        Args:
            query: The search query
            search_depth: "basic" for fast results or "advanced" for comprehensive search
            max_results: Maximum number of results to return (default: 5, max: 10)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results (provided by Open WebUI)
            
        Returns:
            Formatted search results with citations and sources
        """
        
        # Validate API key
        if not self.api_key:
            error_msg = (
                "❌ Tavily API key not configured.\n\n"
                "To use Tavily search:\n"
                "1. Get an API key from https://tavily.com\n"
                "2. Add to .env: TAVILY_API_KEY=tvly-your-key-here\n"
                "3. Restart RIN: ./rin restart\n\n"
                "Alternative: Use the built-in SearXNG tool for anonymous search."
            )
            
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": error_msg, "done": True},
                    }
                )
            
            return error_msg
        
        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🔍 Searching with Tavily AI ({search_depth} mode)...",
                        "done": False,
                    },
                }
            )
        
        try:
            # Make request to Tavily API
            response = requests.post(
                self.api_url,
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "search_depth": search_depth,
                    "max_results": min(max_results, 10),
                    "include_answer": True,
                    "include_raw_content": False,
                },
                timeout=15,
            )
            response.raise_for_status()
            
            result = response.json()
            
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {len(result.get('results', []))} results",
                            "done": True,
                        },
                    }
                )
            
            # Format the response
            formatted_output = f"# Search Results: {query}\n\n"
            
            # Add AI-generated answer if available
            if result.get("answer"):
                formatted_output += f"## AI Summary\n{result['answer']}\n\n"
            
            # Add search results
            if result.get("results"):
                formatted_output += "## Sources\n\n"
                for idx, item in enumerate(result["results"], 1):
                    title = item.get("title", "No title")
                    url = item.get("url", "")
                    content = item.get("content", "")
                    score = item.get("score", 0)
                    
                    formatted_output += f"### {idx}. {title}\n"
                    formatted_output += f"**URL**: {url}\n"
                    formatted_output += f"**Relevance**: {score:.2f}\n\n"
                    formatted_output += f"{content}\n\n"
                    formatted_output += "---\n\n"
                
                return formatted_output
            else:
                return f"No results found for: {query}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Tavily API: {str(e)}"
            
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            
            return f"Search failed: {error_msg}\n\nPlease verify your TAVILY_API_KEY in .env is valid."
    
    def quick_search(
        self,
        query: str,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Quick web search using Tavily (Fast Mode)
        
        Optimized for speed with basic search depth. Use this for quick fact-checking
        or when you need immediate results.
        
        Args:
            query: The search query
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results (provided by Open WebUI)
            
        Returns:
            Formatted search results with AI summary
        """
        return self.web_search(
            query=query,
            search_depth="basic",
            max_results=3,
            __user__=__user__,
            __event_emitter__=__event_emitter__,
        )
    
    def deep_search(
        self,
        query: str,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Deep web search using Tavily (Advanced Mode)
        
        Comprehensive search with advanced depth. Use this for research-heavy
        queries or when you need detailed, thorough results.
        
        Args:
            query: The search query
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results (provided by Open WebUI)
            
        Returns:
            Comprehensive search results with AI summary and detailed sources
        """
        return self.web_search(
            query=query,
            search_depth="advanced",
            max_results=10,
            __user__=__user__,
            __event_emitter__=__event_emitter__,
        )
