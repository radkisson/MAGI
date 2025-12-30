"""
OpenAlex Academic Search Tool for Open WebUI

This tool connects the Cortex (Open WebUI) to OpenAlex, a free and open
catalog of the world's scholarly research. OpenAlex indexes over 250 million
works including papers, books, datasets, and more.

Features:
- No API key required (free and open)
- 100,000 API calls/day limit
- Covers all academic disciplines
- Excellent author/institution disambiguation via ORCID
- Citation data and open access status

Replaces Google Scholar for academic research without IP blocking issues.
"""

import datetime
import time
import requests
from typing import Callable, Any, Optional
from pydantic import BaseModel, Field


class Valves(BaseModel):
    """Configuration valves for OpenAlex integration"""

    OPENALEX_API_URL: str = Field(
        default="https://api.openalex.org",
        description="OpenAlex API base URL"
    )
    OPENALEX_EMAIL: str = Field(
        default="",
        description="Your email (optional but recommended for higher rate limits)"
    )
    DEFAULT_RESULTS: int = Field(
        default=10,
        description="Default number of results to return"
    )
    REQUEST_TIMEOUT: int = Field(
        default=15,
        description="Timeout in seconds for API requests"
    )
    MAX_OUTPUT_LENGTH: int = Field(
        default=15000,
        description="Maximum characters in output to prevent context overflow"
    )
    MAX_RETRIES: int = Field(
        default=2,
        description="Number of retries on rate limit errors"
    )


class Tools:
    """Open WebUI Tool: Academic Search via OpenAlex"""

    def __init__(self):
        self.valves = Valves()

    def _make_request(self, endpoint: str, params: dict) -> dict:
        """Make a request to the OpenAlex API with retry logic."""
        # Add email for polite pool (higher rate limits)
        if self.valves.OPENALEX_EMAIL:
            params["mailto"] = self.valves.OPENALEX_EMAIL

        url = f"{self.valves.OPENALEX_API_URL}/{endpoint}"
        
        last_error = None
        for attempt in range(self.valves.MAX_RETRIES + 1):
            try:
                response = requests.get(url, params=params, timeout=self.valves.REQUEST_TIMEOUT)
                
                # Handle rate limiting with backoff
                if response.status_code == 429:
                    if attempt < self.valves.MAX_RETRIES:
                        time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                        continue
                    response.raise_for_status()
                
                response.raise_for_status()
                
                try:
                    return response.json()
                except ValueError as e:
                    raise requests.exceptions.RequestException(f"Invalid JSON response: {str(e)}")
                    
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < self.valves.MAX_RETRIES:
                    time.sleep(1)
                    continue
                raise
        
        raise last_error or requests.exceptions.RequestException("Request failed after retries")
    
    def _truncate_output(self, output: str) -> str:
        """Truncate output to prevent context overflow."""
        limit = self.valves.MAX_OUTPUT_LENGTH
        if len(output) <= limit:
            return output
        
        # Find last complete section (ending with ---)
        truncated = output[:limit]
        last_separator = truncated.rfind("\n---\n")
        if last_separator > limit // 2:
            truncated = truncated[:last_separator + 5]
        
        return truncated + "\n\n> ⚠️ **Output truncated** to fit context limits.\n"

    def _format_work(self, work: dict, idx: int) -> str:
        """Format a single work for display."""
        title = work.get("title", "No title")
        
        # Get publication year
        year = work.get("publication_year", "N/A")
        
        # Get authors (first 3)
        authorships = work.get("authorships", [])
        authors = []
        for auth in authorships[:3]:
            author_name = auth.get("author", {}).get("display_name", "Unknown")
            authors.append(author_name)
        if len(authorships) > 3:
            authors.append(f"et al. (+{len(authorships) - 3})")
        authors_str = ", ".join(authors) if authors else "Unknown authors"
        
        # Get venue/journal
        primary_location = work.get("primary_location", {}) or {}
        source = primary_location.get("source", {}) or {}
        venue = source.get("display_name", "Unknown venue")
        
        # Get DOI and URLs
        doi = work.get("doi", "")
        openalex_id = work.get("id", "")
        
        # Open access status
        oa = work.get("open_access", {}) or {}
        oa_status = "🔓 Open Access" if oa.get("is_oa") else "🔒 Closed"
        oa_url = oa.get("oa_url", "")
        
        # Citation count
        cited_by = work.get("cited_by_count", 0)
        
        # Abstract (if available)
        abstract_inverted = work.get("abstract_inverted_index") or {}
        abstract = ""
        if abstract_inverted and isinstance(abstract_inverted, dict):
            # Reconstruct abstract from inverted index
            word_positions = []
            for word, positions in abstract_inverted.items():
                if positions and isinstance(positions, list):
                    for pos in positions:
                        if isinstance(pos, int):
                            word_positions.append((pos, word))
            word_positions.sort()
            abstract = " ".join([w for _, w in word_positions])
            # Truncate at word boundary
            if len(abstract) > 300:
                abstract = abstract[:300].rsplit(" ", 1)[0] + "..."
        
        # Build output
        output = f"### {idx}. {title}\n"
        output += f"**Authors**: {authors_str}\n"
        output += f"**Year**: {year} | **Venue**: {venue}\n"
        output += f"**Citations**: {cited_by} | {oa_status}\n"
        
        if abstract:
            output += f"\n> {abstract}\n"
        
        if doi:
            output += f"\n**DOI**: {doi}\n"
        if oa_url:
            output += f"**PDF**: {oa_url}\n"
        
        output += f"**OpenAlex**: {openalex_id}\n"
        
        return output

    def search_papers(
        self,
        query: str,
        max_results: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        open_access_only: bool = False,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Search for academic papers using OpenAlex (Free Google Scholar Alternative)

        OpenAlex indexes 250M+ scholarly works across all disciplines.
        No API key required, no IP blocking issues.

        Args:
            query: Search query (searches title, abstract, and full text)
            max_results: Maximum number of results (default: 10, max: 50)
            year_from: Filter papers from this year onwards (optional)
            year_to: Filter papers up to this year (optional)
            open_access_only: Only return open access papers (default: False)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            Formatted list of academic papers with metadata
        """

        # Validate input
        if not query or not query.strip():
            return "❌ Please provide a search query."
        
        query = query.strip()

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"📚 Searching OpenAlex for: {query}...",
                        "done": False,
                    },
                }
            )

        try:
            # Build query parameters
            params = {
                "search": query,
                "per_page": min(max_results, 50),
                "sort": "relevance_score:desc",
            }

            # Add filters
            filters = []
            if year_from:
                filters.append(f"publication_year:>{year_from - 1}")
            if year_to:
                filters.append(f"publication_year:<{year_to + 1}")
            if open_access_only:
                filters.append("open_access.is_oa:true")

            if filters:
                params["filter"] = ",".join(filters)

            # Make request
            result = self._make_request("works", params)

            if not result or "results" not in result:
                if __event_emitter__:
                    __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": "⚠️ Empty response from OpenAlex",
                                "done": True,
                            },
                        }
                    )
                return f"No results found for: {query}"

            works = result.get("results", [])
            total_count = result.get("meta", {}).get("count", 0)

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {total_count:,} papers, showing top {len(works)}",
                            "done": True,
                        },
                    }
                )

            if not works:
                return f"No papers found matching: {query}"

            # Format output
            output = f"# Academic Search: {query}\n\n"
            output += f"Found **{total_count:,}** papers. Showing top {len(works)} results.\n\n"
            output += "---\n\n"

            for idx, work in enumerate(works, 1):
                output += self._format_work(work, idx)
                output += "\n---\n\n"

            return self._truncate_output(output)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to OpenAlex: {str(e)}"
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            return f"Search failed: {error_msg}"

    def search_by_author(
        self,
        author_name: str,
        max_results: int = 10,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Search for papers by a specific author

        Args:
            author_name: Name of the author to search for
            max_results: Maximum number of results (default: 10)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            Papers authored by the specified person
        """

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"👤 Searching for author: {author_name}...",
                        "done": False,
                    },
                }
            )

        try:
            # First, find the author
            author_result = self._make_request("authors", {
                "search": author_name,
                "per_page": 1,
            })

            authors = author_result.get("results", [])
            if not authors:
                return f"No author found matching: {author_name}"

            author = authors[0]
            author_id = author.get("id", "").replace("https://openalex.org/", "")
            author_display = author.get("display_name", author_name)
            works_count = author.get("works_count", 0)
            cited_by = author.get("cited_by_count", 0)
            
            # Get affiliations
            affiliations = author.get("affiliations", [])
            current_institution = "Unknown"
            if affiliations:
                current_institution = affiliations[0].get("institution", {}).get("display_name", "Unknown")

            # Now get their works
            works_result = self._make_request("works", {
                "filter": f"author.id:{author_id}",
                "per_page": min(max_results, 50),
                "sort": "cited_by_count:desc",
            })

            works = works_result.get("results", [])

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {len(works)} papers by {author_display}",
                            "done": True,
                        },
                    }
                )

            # Format output
            output = f"# Papers by {author_display}\n\n"
            output += f"**Institution**: {current_institution}\n"
            output += f"**Total Works**: {works_count:,} | **Total Citations**: {cited_by:,}\n\n"
            output += "---\n\n"

            for idx, work in enumerate(works, 1):
                output += self._format_work(work, idx)
                output += "\n---\n\n"

            return self._truncate_output(output)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to OpenAlex: {str(e)}"
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            return f"Search failed: {error_msg}"

    def get_citations(
        self,
        paper_title: str,
        max_results: int = 10,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Find papers that cite a given paper

        Args:
            paper_title: Title of the paper to find citations for
            max_results: Maximum number of citing papers to return (default: 10)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            List of papers that cite the specified work
        """

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🔗 Finding citations for: {paper_title}...",
                        "done": False,
                    },
                }
            )

        try:
            # First, find the paper
            paper_result = self._make_request("works", {
                "search": paper_title,
                "per_page": 1,
            })

            papers = paper_result.get("results", [])
            if not papers:
                return f"No paper found matching: {paper_title}"

            paper = papers[0]
            paper_id = paper.get("id", "").replace("https://openalex.org/", "")
            paper_title_actual = paper.get("title", paper_title)
            cited_by_count = paper.get("cited_by_count", 0)

            # Now get citing works
            citing_result = self._make_request("works", {
                "filter": f"cites:{paper_id}",
                "per_page": min(max_results, 50),
                "sort": "cited_by_count:desc",
            })

            citing_works = citing_result.get("results", [])

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {cited_by_count:,} citations, showing top {len(citing_works)}",
                            "done": True,
                        },
                    }
                )

            # Format output
            output = f"# Citations for: {paper_title_actual}\n\n"
            output += f"**Total Citations**: {cited_by_count:,}\n\n"
            output += "---\n\n"

            if not citing_works:
                output += "No citing papers found in OpenAlex.\n"
            else:
                for idx, work in enumerate(citing_works, 1):
                    output += self._format_work(work, idx)
                    output += "\n---\n\n"

            return self._truncate_output(output)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to OpenAlex: {str(e)}"
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            return f"Search failed: {error_msg}"

    def search_recent(
        self,
        query: str,
        days: int = 30,
        max_results: int = 10,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Search for recent papers published in the last N days

        Args:
            query: Search query
            days: How many days back to search (default: 30)
            max_results: Maximum number of results (default: 10)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            Recent papers matching the query
        """
        # Validate days parameter
        if days < 1:
            days = 1
        elif days > 365:
            days = 365

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"📅 Searching recent papers (last {days} days)...",
                        "done": False,
                    },
                }
            )

        try:
            # Calculate date range
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=days)

            params = {
                "search": query,
                "per_page": min(max_results, 50),
                "filter": f"from_created_date:{start_date.isoformat()}",
                "sort": "publication_date:desc",
            }

            result = self._make_request("works", params)
            works = result.get("results", [])
            total_count = result.get("meta", {}).get("count", 0)

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {total_count:,} recent papers",
                            "done": True,
                        },
                    }
                )

            # Format output
            output = f"# Recent Papers: {query}\n\n"
            output += f"Papers added in the last **{days} days**. Found {total_count:,} results.\n\n"
            output += "---\n\n"

            if not works:
                output += "No recent papers found matching your query.\n"
            else:
                for idx, work in enumerate(works, 1):
                    output += self._format_work(work, idx)
                    output += "\n---\n\n"

            return self._truncate_output(output)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to OpenAlex: {str(e)}"
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            return f"Search failed: {error_msg}"
