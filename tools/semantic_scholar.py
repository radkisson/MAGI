"""
Semantic Scholar Academic Search Tool for Open WebUI

This tool connects the Cortex (Open WebUI) to Semantic Scholar, an AI-powered
research tool that indexes over 200 million academic papers with advanced
citation analysis and paper recommendations.

Features:
- Free API (API key optional for higher rate limits)
- Advanced citation graph analysis
- AI-generated paper summaries (TLDR)
- Influential citation detection
- Paper recommendations

Complements OpenAlex by providing deeper citation analysis and AI features.
"""

import time
import requests
from typing import Callable, Any, Optional, List
from pydantic import BaseModel, Field


class Valves(BaseModel):
    """Configuration valves for Semantic Scholar integration"""

    S2_API_URL: str = Field(
        default="https://api.semanticscholar.org/graph/v1",
        description="Semantic Scholar API base URL"
    )
    S2_API_KEY: str = Field(
        default="",
        description="Semantic Scholar API key (optional, increases rate limits)"
    )
    REQUEST_TIMEOUT: int = Field(
        default=15,
        description="Timeout in seconds for API requests"
    )
    MAX_RETRIES: int = Field(
        default=2,
        description="Number of retries on rate limit errors"
    )
    MAX_OUTPUT_LENGTH: int = Field(
        default=15000,
        description="Maximum characters in output to prevent context overflow"
    )


class Tools:
    """Open WebUI Tool: Academic Search via Semantic Scholar"""

    def __init__(self):
        self.valves = Valves()
        # Standard fields to request for papers
        self.paper_fields = "paperId,title,abstract,year,citationCount,influentialCitationCount,isOpenAccess,openAccessPdf,authors,venue,publicationTypes,tldr,fieldsOfStudy,externalIds"
        self.author_fields = "authorId,name,affiliations,paperCount,citationCount,hIndex"

    def _normalize_paper_id(self, paper_id: str) -> str:
        """Normalize paper ID to handle DOI, arXiv, and URL formats."""
        paper_id = paper_id.strip()
        
        if not paper_id:
            return ""
        
        # Handle URLs
        if paper_id.startswith("http"):
            if "semanticscholar.org" in paper_id:
                paper_id = paper_id.split("/")[-1]
            elif "doi.org" in paper_id:
                paper_id = paper_id.replace("https://doi.org/", "").replace("http://doi.org/", "")
            elif "arxiv.org" in paper_id:
                paper_id = "arXiv:" + paper_id.split("/")[-1].replace(".pdf", "")
        
        # Add DOI prefix if it looks like a DOI
        if paper_id.startswith("10.") and "/" in paper_id:
            paper_id = f"DOI:{paper_id}"
        
        return paper_id

    def _make_request(self, endpoint: str, params: dict = None, method: str = "GET", json_data: dict = None) -> dict:
        """Make a request to the Semantic Scholar API with retry logic."""
        headers = {}
        if self.valves.S2_API_KEY:
            headers["x-api-key"] = self.valves.S2_API_KEY

        url = f"{self.valves.S2_API_URL}/{endpoint}"
        
        last_error = None
        for attempt in range(self.valves.MAX_RETRIES + 1):
            try:
                if method == "GET":
                    response = requests.get(url, params=params, headers=headers, timeout=self.valves.REQUEST_TIMEOUT)
                else:
                    response = requests.post(url, params=params, json=json_data, headers=headers, timeout=self.valves.REQUEST_TIMEOUT)
                
                # Handle rate limiting with backoff
                if response.status_code == 429:
                    if attempt < self.valves.MAX_RETRIES:
                        time.sleep(2 ** attempt)
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
        
        truncated = output[:limit]
        last_separator = truncated.rfind("\n---\n")
        if last_separator > limit // 2:
            truncated = truncated[:last_separator + 5]
        
        return truncated + "\n\n> ⚠️ **Output truncated** to fit context limits.\n"

    def _format_paper(self, paper: dict, idx: int) -> str:
        """Format a single paper for display."""
        title = paper.get("title", "No title")
        year = paper.get("year", "N/A")
        
        # Authors
        authors = paper.get("authors", [])
        author_names = [a.get("name", "Unknown") for a in authors[:3]]
        if len(authors) > 3:
            author_names.append(f"et al. (+{len(authors) - 3})")
        authors_str = ", ".join(author_names) if author_names else "Unknown authors"
        
        # Venue
        venue = paper.get("venue", "") or "Unknown venue"
        
        # Citations (handle None values)
        citations = paper.get("citationCount") or 0
        influential = paper.get("influentialCitationCount") or 0
        
        # Open access
        is_oa = paper.get("isOpenAccess", False)
        oa_status = "🔓 Open Access" if is_oa else "🔒 Closed"
        oa_pdf = paper.get("openAccessPdf", {})
        pdf_url = oa_pdf.get("url", "") if oa_pdf else ""
        
        # TLDR (AI summary)
        tldr = paper.get("tldr", {})
        tldr_text = tldr.get("text", "") if tldr else ""
        
        # Abstract - show full, output truncation handles overall length
        abstract = paper.get("abstract", "") or ""
        
        # External IDs
        external_ids = paper.get("externalIds", {}) or {}
        doi = external_ids.get("DOI", "")
        arxiv = external_ids.get("ArXiv", "")
        
        # Fields of study
        fields = paper.get("fieldsOfStudy", []) or []
        fields_str = ", ".join([f"`{f}`" for f in fields[:3]]) if fields else ""
        
        # Build output
        output = f"### {idx}. {title}\n"
        output += f"**Authors**: {authors_str}\n"
        output += f"**Year**: {year} | **Venue**: {venue}\n"
        output += f"**Citations**: {citations:,} ({influential} influential) | {oa_status}\n"
        
        if tldr_text:
            output += f"\n**TLDR**: {tldr_text}\n"
        elif abstract:
            output += f"\n> {abstract}\n"
        
        if fields_str:
            output += f"\n**Fields**: {fields_str}\n"
        
        if doi:
            output += f"**DOI**: https://doi.org/{doi}\n"
        if arxiv:
            output += f"**arXiv**: https://arxiv.org/abs/{arxiv}\n"
        if pdf_url:
            output += f"**PDF**: {pdf_url}\n"
        
        paper_id = paper.get("paperId", "")
        if paper_id:
            output += f"**S2**: https://www.semanticscholar.org/paper/{paper_id}\n"
        
        return output

    def search_papers(
        self,
        query: str,
        max_results: int = 10,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        open_access_only: bool = False,
        fields_of_study: Optional[List[str]] = None,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Search for academic papers using Semantic Scholar

        Semantic Scholar provides AI-powered search with TLDRs and citation analysis.
        Free to use, with optional API key for higher rate limits.

        Args:
            query: Search query (searches title and abstract)
            max_results: Maximum number of results (default: 10, max: 100)
            year_from: Filter papers from this year onwards (optional)
            year_to: Filter papers up to this year (optional)
            open_access_only: Only return open access papers (default: False)
            fields_of_study: Filter by fields like ["Computer Science", "Medicine"]
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            Formatted list of academic papers with AI summaries
        """
        if not query or not query.strip():
            return "❌ Please provide a search query."
        
        query = query.strip()

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🔬 Searching Semantic Scholar for: {query}...",
                        "done": False,
                    },
                }
            )

        try:
            params = {
                "query": query,
                "limit": min(max_results, 100),
                "fields": self.paper_fields,
            }

            # Add year filter
            if year_from or year_to:
                year_range = f"{year_from or ''}-{year_to or ''}"
                params["year"] = year_range

            # Add open access filter
            if open_access_only:
                params["openAccessPdf"] = ""

            # Add fields of study filter
            if fields_of_study:
                params["fieldsOfStudy"] = ",".join(fields_of_study)

            result = self._make_request("paper/search", params)

            if not result or "data" not in result:
                if __event_emitter__:
                    __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": "⚠️ No results from Semantic Scholar", "done": True},
                        }
                    )
                return f"No results found for: {query}"

            papers = result.get("data", [])
            total = result.get("total", len(papers))

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {total:,} papers, showing {len(papers)}",
                            "done": True,
                        },
                    }
                )

            if not papers:
                return f"No papers found matching: {query}"

            output = f"# Semantic Scholar Search: {query}\n\n"
            output += f"Found **{total:,}** papers. Showing top {len(papers)} results.\n\n"
            output += "---\n\n"

            for idx, paper in enumerate(papers, 1):
                output += self._format_paper(paper, idx)
                output += "\n---\n\n"

            return self._truncate_output(output)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Semantic Scholar: {str(e)}"
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            return f"Search failed: {error_msg}"

    def get_paper(
        self,
        paper_id: str,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Get detailed information about a specific paper

        Args:
            paper_id: Semantic Scholar paper ID, DOI, arXiv ID, or URL
                     Examples: "649def34f8be52c8b66281af98ae884c09aef38b"
                              "10.1038/nature12373"
                              "arXiv:2106.15928"
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            Detailed paper information with abstract, citations, and references
        """
        paper_id = self._normalize_paper_id(paper_id)
        if not paper_id:
            return "❌ Please provide a paper ID, DOI, or arXiv ID."

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🔍 Looking up paper: {paper_id[:50]}...",
                        "done": False,
                    },
                }
            )

        try:
            # Get paper with extended fields
            fields = self.paper_fields + ",references.paperId,references.title,references.year,citations.paperId,citations.title,citations.year"
            result = self._make_request(f"paper/{paper_id}", {"fields": fields})

            if not result:
                return f"No paper found with ID: {paper_id}"

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "✅ Paper found", "done": True},
                    }
                )

            title = result.get("title", "No title")
            year = result.get("year", "N/A")
            
            # Authors with affiliations
            authors = result.get("authors", [])
            authors_list = [f"- {a.get('name', 'Unknown')}" for a in authors]
            
            venue = result.get("venue", "") or "Unknown venue"
            citations = result.get("citationCount", 0)
            influential = result.get("influentialCitationCount", 0)
            
            is_oa = result.get("isOpenAccess", False)
            oa_status = "🔓 Open Access" if is_oa else "🔒 Closed Access"
            oa_pdf = result.get("openAccessPdf", {})
            pdf_url = oa_pdf.get("url", "") if oa_pdf else ""
            
            # Full abstract
            abstract = result.get("abstract", "")
            
            # TLDR
            tldr = result.get("tldr", {})
            tldr_text = tldr.get("text", "") if tldr else ""
            
            # External IDs
            external_ids = result.get("externalIds", {}) or {}
            doi = external_ids.get("DOI", "")
            arxiv = external_ids.get("ArXiv", "")
            
            # Fields
            fields_list = result.get("fieldsOfStudy", []) or []
            
            # References and citations
            references = result.get("references", []) or []
            citing_papers = result.get("citations", []) or []
            
            # Build output
            output = f"# {title}\n\n"
            output += f"**Year**: {year} | **Venue**: {venue}\n"
            output += f"**Citations**: {citations:,} ({influential} influential) | {oa_status}\n"
            
            if doi:
                output += f"**DOI**: https://doi.org/{doi}\n"
            if arxiv:
                output += f"**arXiv**: https://arxiv.org/abs/{arxiv}\n"
            if pdf_url:
                output += f"**PDF**: {pdf_url}\n"
            
            output += "\n"
            
            output += f"## Authors ({len(authors)})\n"
            output += "\n".join(authors_list[:10])
            if len(authors) > 10:
                output += f"\n- ... and {len(authors) - 10} more"
            output += "\n\n"
            
            if tldr_text:
                output += f"## TLDR (AI Summary)\n{tldr_text}\n\n"
            
            if abstract:
                output += f"## Abstract\n{abstract}\n\n"
            
            if fields_list:
                output += f"## Fields of Study\n{', '.join([f'`{f}`' for f in fields_list])}\n\n"
            
            # Top references
            if references:
                output += f"## References ({len(references)} total)\n"
                for ref in references[:5]:
                    ref_title = ref.get("title", "Unknown")
                    ref_year = ref.get("year", "")
                    output += f"- {ref_title} ({ref_year})\n"
                if len(references) > 5:
                    output += f"- ... and {len(references) - 5} more\n"
                output += "\n"
            
            # Top citing papers
            if citing_papers:
                output += f"## Cited By ({len(citing_papers)} shown, {citations:,} total)\n"
                for cite in citing_papers[:5]:
                    cite_title = cite.get("title", "Unknown")
                    cite_year = cite.get("year", "")
                    output += f"- {cite_title} ({cite_year})\n"
                if len(citing_papers) > 5:
                    output += f"- ... and more\n"

            return output

        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Semantic Scholar: {str(e)}"
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            return f"Lookup failed: {error_msg}"

    def get_author(
        self,
        author_name: str,
        max_papers: int = 10,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Search for an author and get their profile with top papers

        Args:
            author_name: Name of the author to search for
            max_papers: Maximum number of papers to show (default: 10)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            Author profile with h-index, affiliations, and top papers
        """
        if not author_name or not author_name.strip():
            return "❌ Please provide an author name."
        
        author_name = author_name.strip()
        max_papers = max(1, min(max_papers, 100))

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
            # Search for author
            result = self._make_request("author/search", {
                "query": author_name,
                "limit": 1,
                "fields": self.author_fields,
            })

            authors = result.get("data", [])
            if not authors:
                return f"No author found matching: {author_name}"

            author = authors[0]
            author_id = author.get("authorId", "")
            name = author.get("name", author_name)
            affiliations = author.get("affiliations", []) or []
            paper_count = author.get("paperCount", 0)
            citation_count = author.get("citationCount", 0)
            h_index = author.get("hIndex", 0)

            # Get author's papers
            papers_result = self._make_request(f"author/{author_id}/papers", {
                "fields": self.paper_fields,
                "limit": min(max_papers, 100),
            })

            papers = papers_result.get("data", [])

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {name} with {paper_count:,} papers",
                            "done": True,
                        },
                    }
                )

            # Build output
            output = f"# {name}\n\n"
            
            if affiliations:
                output += f"**Affiliations**: {', '.join(affiliations)}\n"
            
            output += f"**Papers**: {paper_count:,} | **Citations**: {citation_count:,} | **h-index**: {h_index}\n"
            output += f"**S2 Profile**: https://www.semanticscholar.org/author/{author_id}\n\n"
            output += "---\n\n"
            
            output += f"## Top Papers (showing {len(papers)} of {paper_count:,})\n\n"

            for idx, paper in enumerate(papers, 1):
                output += self._format_paper(paper, idx)
                output += "\n---\n\n"

            return self._truncate_output(output)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Semantic Scholar: {str(e)}"
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            return f"Search failed: {error_msg}"

    def get_recommendations(
        self,
        paper_id: str,
        max_results: int = 10,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Get paper recommendations based on a given paper

        Args:
            paper_id: Semantic Scholar paper ID, DOI, or arXiv ID
            max_results: Number of recommendations to return (default: 10)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            List of recommended papers similar to the input
        """
        paper_id = self._normalize_paper_id(paper_id)
        if not paper_id:
            return "❌ Please provide a paper ID, DOI, or arXiv ID."
        
        max_results = max(1, min(max_results, 100))

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🎯 Getting recommendations for paper...",
                        "done": False,
                    },
                }
            )

        try:
            # Use recommendations API (different base URL)
            rec_url = "https://api.semanticscholar.org/recommendations/v1/papers"
            
            headers = {}
            if self.valves.S2_API_KEY:
                headers["x-api-key"] = self.valves.S2_API_KEY

            last_error = None
            for attempt in range(self.valves.MAX_RETRIES + 1):
                try:
                    response = requests.post(
                        rec_url,
                        json={"positivePaperIds": [paper_id]},
                        params={"fields": self.paper_fields, "limit": max_results},
                        headers=headers,
                        timeout=self.valves.REQUEST_TIMEOUT,
                    )
                    
                    if response.status_code == 429:
                        if attempt < self.valves.MAX_RETRIES:
                            time.sleep(2 ** attempt)
                            continue
                    
                    response.raise_for_status()
                    
                    try:
                        result = response.json()
                    except ValueError as e:
                        raise requests.exceptions.RequestException(f"Invalid JSON: {e}")
                    
                    break
                except requests.exceptions.RequestException as e:
                    last_error = e
                    if attempt < self.valves.MAX_RETRIES:
                        time.sleep(1)
                        continue
                    raise
            
            if last_error and not result:
                raise last_error

            papers = result.get("recommendedPapers", [])

            if not papers:
                return f"No recommendations found for paper: {paper_id}"

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {len(papers)} recommendations",
                            "done": True,
                        },
                    }
                )

            output = f"# Paper Recommendations\n\n"
            output += f"Based on paper ID: `{paper_id}`\n\n"
            output += "---\n\n"

            for idx, paper in enumerate(papers, 1):
                output += self._format_paper(paper, idx)
                output += "\n---\n\n"

            return self._truncate_output(output)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error getting recommendations: {str(e)}"
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            return f"Recommendations failed: {error_msg}"

    def get_citations(
        self,
        paper_id: str,
        max_results: int = 10,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Get papers that cite a given paper

        Args:
            paper_id: Semantic Scholar paper ID, DOI, or arXiv ID
            max_results: Maximum number of citing papers (default: 10)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            List of papers that cite the specified work
        """
        paper_id = self._normalize_paper_id(paper_id)
        if not paper_id:
            return "❌ Please provide a paper ID, DOI, or arXiv ID."
        
        max_results = max(1, min(max_results, 100))

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"🔗 Finding citations...",
                        "done": False,
                    },
                }
            )

        try:
            result = self._make_request(f"paper/{paper_id}/citations", {
                "fields": "citingPaper." + self.paper_fields,
                "limit": min(max_results, 100),
            })

            citations = result.get("data", [])

            if not citations:
                return f"No citations found for paper: {paper_id}"

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {len(citations)} citing papers",
                            "done": True,
                        },
                    }
                )

            output = f"# Papers Citing: {paper_id}\n\n"
            output += f"Showing {len(citations)} citing papers.\n\n"
            output += "---\n\n"

            for idx, citation in enumerate(citations, 1):
                paper = citation.get("citingPaper", {})
                if paper:
                    output += self._format_paper(paper, idx)
                    output += "\n---\n\n"

            return self._truncate_output(output)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error getting citations: {str(e)}"
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            return f"Citations lookup failed: {error_msg}"

    def get_references(
        self,
        paper_id: str,
        max_results: int = 10,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Get papers that a given paper cites (its bibliography)

        Args:
            paper_id: Semantic Scholar paper ID, DOI, or arXiv ID
            max_results: Maximum number of references (default: 10)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results

        Returns:
            List of papers cited by the specified work
        """
        paper_id = self._normalize_paper_id(paper_id)
        if not paper_id:
            return "❌ Please provide a paper ID, DOI, or arXiv ID."
        
        max_results = max(1, min(max_results, 100))

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": f"📖 Finding references...",
                        "done": False,
                    },
                }
            )

        try:
            result = self._make_request(f"paper/{paper_id}/references", {
                "fields": "citedPaper." + self.paper_fields,
                "limit": min(max_results, 100),
            })

            references = result.get("data", [])

            if not references:
                return f"No references found for paper: {paper_id}"

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"✅ Found {len(references)} references",
                            "done": True,
                        },
                    }
                )

            output = f"# References in: {paper_id}\n\n"
            output += f"Showing {len(references)} referenced papers.\n\n"
            output += "---\n\n"

            for idx, ref in enumerate(references, 1):
                paper = ref.get("citedPaper", {})
                if paper:
                    output += self._format_paper(paper, idx)
                    output += "\n---\n\n"

            return self._truncate_output(output)

        except requests.exceptions.RequestException as e:
            error_msg = f"Error getting references: {str(e)}"
            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )
            return f"References lookup failed: {error_msg}"
