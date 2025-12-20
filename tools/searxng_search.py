"""
SearXNG Search Tool for Open WebUI

This tool connects the Cortex (Open WebUI) to the Sensorium's Vision (SearXNG),
allowing RIN to search the web anonymously without tracking.
"""

import requests
from typing import Callable, Any


class Tools:
    """Open WebUI Tool: Anonymous Web Search via SearXNG"""
    
    def __init__(self):
        self.searxng_url = "http://searxng:8080"
    
    def web_search(
        self,
        query: str,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Search the web anonymously using SearXNG (The Sensorium's Vision)
        
        This tool allows RIN to "see" the web without revealing its IP address
        or being tracked by search engines. Results are aggregated from multiple
        sources (Google, Bing, etc.) through a privacy-respecting metasearch engine.
        
        Args:
            query: The search query
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results (provided by Open WebUI)
            
        Returns:
            Search results with titles, URLs, and snippets
        """
        
        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🔍 Searching web anonymously via SearXNG...",
                        "done": False,
                    },
                }
            )
        
        try:
            # Query SearXNG
            response = requests.get(
                f"{self.searxng_url}/search",
                params={
                    "q": query,
                    "format": "json",
                    "language": "en",
                },
                timeout=10,
            )
            response.raise_for_status()
            
            results = response.json()
            
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {len(results.get('results', []))} results",
                            "done": True,
                        },
                    }
                )
            
            # Format results for LLM consumption
            formatted_results = []
            for idx, result in enumerate(results.get("results", [])[:10], 1):
                formatted_results.append(
                    f"{idx}. **{result.get('title', 'No title')}**\n"
                    f"   URL: {result.get('url', 'N/A')}\n"
                    f"   {result.get('content', 'No description available')}\n"
                )
            
            if not formatted_results:
                return "No search results found."
            
            return (
                f"# Anonymous Web Search Results for: '{query}'\n\n"
                f"Powered by SearXNG (The Sensorium's Vision)\n\n"
                + "\n".join(formatted_results)
            )
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to SearXNG: {str(e)}"
            
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            
            return f"Search failed: {error_msg}\n\nNote: Ensure SearXNG service is running (docker-compose up -d)"
