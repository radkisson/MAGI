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

    def get_by_doi(
        self,
        doi: str,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Get full details for a paper by its DOI

        Args:
            doi: The DOI of the paper (e.g., "10.1038/nature12373" or full URL)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            Detailed information about the paper including abstract, citations, and references
        """
        import re

        # Clean up DOI input
        doi = doi.strip()
        if doi.startswith("http"):
            doi = doi.split("doi.org/")[-1]
        if not doi.startswith("10."):
            match = re.search(r'(10\.\d{4,}/[^\s]+)', doi)
            if match:
                doi = match.group(1)
            else:
                return f"❌ Invalid DOI format: {doi}\n\nExpected format: 10.1038/nature12373"

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🔍 Looking up DOI: {doi}...",
                        "done": False,
                    },
                }
            )

        try:
            result = self._make_request("works", {
                "filter": f"doi:https://doi.org/{doi}",
                "per_page": 1,
            })

            works = result.get("results", [])
            if not works:
                if __event_emitter__:
                    __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": "⚠️ DOI not found", "done": True},
                        }
                    )
                return f"No paper found with DOI: {doi}"

            work = works[0]

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "✅ Paper found", "done": True},
                    }
                )

            title = work.get("title", "No title")
            year = work.get("publication_year", "N/A")
            cited_by = work.get("cited_by_count", 0)

            authorships = work.get("authorships", [])
            authors_list = []
            for auth in authorships:
                name = auth.get("author", {}).get("display_name", "Unknown")
                institution = ""
                institutions = auth.get("institutions", [])
                if institutions:
                    institution = f" ({institutions[0].get('display_name', '')})"
                authors_list.append(f"- {name}{institution}")

            primary_location = work.get("primary_location", {}) or {}
            source = primary_location.get("source", {}) or {}
            venue = source.get("display_name", "Unknown venue")

            oa = work.get("open_access", {}) or {}
            oa_status = "🔓 Open Access" if oa.get("is_oa") else "🔒 Closed Access"
            oa_url = oa.get("oa_url", "")

            abstract_inverted = work.get("abstract_inverted_index") or {}
            abstract = ""
            if abstract_inverted and isinstance(abstract_inverted, dict):
                word_positions = []
                for word, positions in abstract_inverted.items():
                    if positions and isinstance(positions, list):
                        for pos in positions:
                            if isinstance(pos, int):
                                word_positions.append((pos, word))
                word_positions.sort()
                abstract = " ".join([w for _, w in word_positions])

            concepts = work.get("concepts", [])[:5]
            topics = [f"`{c.get('display_name', '')}`" for c in concepts if c.get("display_name")]
            referenced_works = work.get("referenced_works", [])

            output = f"# {title}\n\n"
            output += f"**DOI**: https://doi.org/{doi}\n"
            output += f"**Year**: {year} | **Venue**: {venue}\n"
            output += f"**Citations**: {cited_by:,} | {oa_status}\n"
            if oa_url:
                output += f"**PDF**: {oa_url}\n"
            output += "\n"

            output += f"## Authors ({len(authorships)})\n"
            output += "\n".join(authors_list[:10])
            if len(authorships) > 10:
                output += f"\n- ... and {len(authorships) - 10} more\n"
            output += "\n\n"

            if abstract:
                output += f"## Abstract\n{abstract}\n\n"

            if topics:
                output += f"## Topics\n{', '.join(topics)}\n\n"

            output += f"## References\nThis paper cites **{len(referenced_works)}** other works.\n"
            output += f"Use `get_references()` to see them.\n\n"

            output += f"## Cited By\n**{cited_by:,}** papers cite this work.\n"
            output += f"Use `get_citations()` to see them.\n"

            return output

        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to OpenAlex: {str(e)}"
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            return f"Lookup failed: {error_msg}"

    def get_references(
        self,
        paper_title: str,
        max_results: int = 10,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Find papers that a given paper cites (its references/bibliography)

        This is the reverse of get_citations() - shows what sources the paper used.

        Args:
            paper_title: Title of the paper to find references for
            max_results: Maximum number of references to return (default: 10)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            List of papers cited by the specified work
        """

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"📖 Finding references for: {paper_title}...",
                        "done": False,
                    },
                }
            )

        try:
            paper_result = self._make_request("works", {
                "search": paper_title,
                "per_page": 1,
            })

            papers = paper_result.get("results", [])
            if not papers:
                return f"No paper found matching: {paper_title}"

            paper = papers[0]
            paper_title_actual = paper.get("title", paper_title)
            referenced_works = paper.get("referenced_works", [])

            if not referenced_works:
                if __event_emitter__:
                    __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": "⚠️ No references found", "done": True},
                        }
                    )
                return f"# References for: {paper_title_actual}\n\nNo references found in OpenAlex for this paper."

            ref_ids = [r.replace("https://openalex.org/", "") for r in referenced_works[:max_results]]
            ref_filter = "|".join(ref_ids)

            refs_result = self._make_request("works", {
                "filter": f"openalex:{ref_filter}",
                "per_page": min(max_results, 50),
            })

            refs = refs_result.get("results", [])

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {len(referenced_works)} references, showing {len(refs)}",
                            "done": True,
                        },
                    }
                )

            output = f"# References for: {paper_title_actual}\n\n"
            output += f"This paper cites **{len(referenced_works)}** works. Showing top {len(refs)}.\n\n"
            output += "---\n\n"

            if not refs:
                output += "Could not retrieve reference details.\n"
            else:
                for idx, work in enumerate(refs, 1):
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

    def search_by_institution(
        self,
        institution_name: str,
        query: str = "",
        max_results: int = 10,
        year_from: Optional[int] = None,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Search for papers from a specific university or research institution

        Args:
            institution_name: Name of the institution (e.g., "MIT", "Stanford University")
            query: Optional topic to filter by (e.g., "machine learning")
            max_results: Maximum number of results (default: 10)
            year_from: Only include papers from this year onwards (optional)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            Papers from the specified institution
        """

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🏛️ Searching for institution: {institution_name}...",
                        "done": False,
                    },
                }
            )

        try:
            inst_result = self._make_request("institutions", {
                "search": institution_name,
                "per_page": 1,
            })

            institutions = inst_result.get("results", [])
            if not institutions:
                return f"No institution found matching: {institution_name}"

            institution = institutions[0]
            inst_id = institution.get("id", "").replace("https://openalex.org/", "")
            inst_display = institution.get("display_name", institution_name)
            inst_country = institution.get("country_code", "")
            inst_type = institution.get("type", "")
            works_count = institution.get("works_count", 0)
            cited_by = institution.get("cited_by_count", 0)

            filters = [f"institutions.id:{inst_id}"]
            if year_from:
                filters.append(f"publication_year:>{year_from - 1}")

            params = {
                "filter": ",".join(filters),
                "per_page": min(max_results, 50),
                "sort": "cited_by_count:desc",
            }

            if query and query.strip():
                params["search"] = query.strip()

            works_result = self._make_request("works", params)
            works = works_result.get("results", [])
            total_count = works_result.get("meta", {}).get("count", 0)

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {total_count:,} papers from {inst_display}",
                            "done": True,
                        },
                    }
                )

            output = f"# Papers from {inst_display}\n\n"
            if inst_country:
                output += f"**Country**: {inst_country} | **Type**: {inst_type}\n"
            output += f"**Total Works**: {works_count:,} | **Total Citations**: {cited_by:,}\n"
            if query:
                output += f"**Topic Filter**: {query}\n"
            output += f"\nShowing {len(works)} of {total_count:,} matching papers.\n\n"
            output += "---\n\n"

            if not works:
                output += "No papers found matching your criteria.\n"
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

    def get_related_works(
        self,
        paper_title: str,
        max_results: int = 10,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Find papers similar to a given paper based on OpenAlex's related works

        Args:
            paper_title: Title of the paper to find related works for
            max_results: Maximum number of related papers to return (default: 10)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            List of papers related to the specified work
        """

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🔗 Finding related works for: {paper_title}...",
                        "done": False,
                    },
                }
            )

        try:
            paper_result = self._make_request("works", {
                "search": paper_title,
                "per_page": 1,
            })

            papers = paper_result.get("results", [])
            if not papers:
                return f"No paper found matching: {paper_title}"

            paper = papers[0]
            paper_title_actual = paper.get("title", paper_title)
            related_works = paper.get("related_works", [])

            if not related_works:
                if __event_emitter__:
                    __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": "⚠️ No related works found", "done": True},
                        }
                    )
                return f"# Related Works for: {paper_title_actual}\n\nNo related works found in OpenAlex."

            related_ids = [r.replace("https://openalex.org/", "") for r in related_works[:max_results]]
            related_filter = "|".join(related_ids)

            related_result = self._make_request("works", {
                "filter": f"openalex:{related_filter}",
                "per_page": min(max_results, 50),
                "sort": "cited_by_count:desc",
            })

            related = related_result.get("results", [])

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {len(related_works)} related works, showing {len(related)}",
                            "done": True,
                        },
                    }
                )

            output = f"# Related Works for: {paper_title_actual}\n\n"
            output += f"OpenAlex identified **{len(related_works)}** related papers. Showing top {len(related)}.\n\n"
            output += "---\n\n"

            if not related:
                output += "Could not retrieve related work details.\n"
            else:
                for idx, work in enumerate(related, 1):
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

    def search_by_topic(
        self,
        topic: str,
        max_results: int = 10,
        year_from: Optional[int] = None,
        min_citations: int = 0,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Search for papers by OpenAlex concept/topic (more precise than keyword search)

        OpenAlex has a taxonomy of ~65,000 concepts. This searches for papers
        tagged with specific concepts rather than just keyword matching.

        Args:
            topic: The topic/concept to search for (e.g., "Machine Learning", "CRISPR")
            max_results: Maximum number of results (default: 10)
            year_from: Only include papers from this year onwards (optional)
            min_citations: Minimum citation count filter (default: 0)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            Papers tagged with the specified concept
        """

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🏷️ Searching by topic: {topic}...",
                        "done": False,
                    },
                }
            )

        try:
            # First find the concept
            concept_result = self._make_request("concepts", {
                "search": topic,
                "per_page": 1,
            })

            concepts = concept_result.get("results", [])
            if not concepts:
                # Fall back to regular search
                return self.search_papers(topic, max_results, year_from, __user__=__user__, __event_emitter__=__event_emitter__)

            concept = concepts[0]
            concept_id = concept.get("id", "").replace("https://openalex.org/", "")
            concept_name = concept.get("display_name", topic)
            concept_level = concept.get("level", 0)
            works_count = concept.get("works_count", 0)

            filters = [f"concepts.id:{concept_id}"]
            if year_from:
                filters.append(f"publication_year:>{year_from - 1}")
            if min_citations > 0:
                filters.append(f"cited_by_count:>{min_citations - 1}")

            works_result = self._make_request("works", {
                "filter": ",".join(filters),
                "per_page": min(max_results, 50),
                "sort": "cited_by_count:desc",
            })

            works = works_result.get("results", [])
            total_count = works_result.get("meta", {}).get("count", 0)

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {total_count:,} papers on {concept_name}",
                            "done": True,
                        },
                    }
                )

            output = f"# Topic: {concept_name}\n\n"
            output += f"**Concept Level**: {concept_level} (0=broad, 5=specific)\n"
            output += f"**Total Works**: {works_count:,}\n"
            if min_citations > 0:
                output += f"**Min Citations Filter**: {min_citations}+\n"
            output += f"\nShowing {len(works)} of {total_count:,} matching papers.\n\n"
            output += "---\n\n"

            if not works:
                output += "No papers found matching your criteria.\n"
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
