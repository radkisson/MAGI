"""
Qdrant Memory Tool for Open WebUI

This tool connects the Cortex (Open WebUI) to the Memory (Qdrant),
allowing MAGI to store and retrieve information with RAG capabilities.
"""

import os
import requests
from typing import Callable, Any
import json
import uuid
import time
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel, Field

try:
    from .utils import get_service_url
except ImportError:
    from utils import get_service_url


class Valves(BaseModel):
    """Configuration valves for Qdrant Memory integration"""

    QDRANT_URL: str = Field(
        default="",
        description="Qdrant instance URL (leave empty to auto-detect from Docker)"
    )
    COLLECTION_NAME: str = Field(
        default="rin_memory",
        description="Name of the Qdrant collection for storing memories"
    )
    EMBEDDING_MODEL: str = Field(
        default="all-mpnet-base-v2",
        description="Sentence-transformers model for local embeddings (ignored if using Azure)"
    )
    EMBEDDING_DIM: int = Field(
        default=768,
        description="Embedding vector dimension (768 for local all-mpnet-base-v2, 1536 for Azure ada-002)"
    )
    EMBEDDING_TYPE: str = Field(
        default="local",
        description="Embedding type: 'local' (sentence-transformers) or 'azure' (Azure OpenAI)"
    )
    AZURE_EMBEDDING_ENDPOINT: str = Field(
        default="",
        description="Azure OpenAI embedding endpoint (leave empty to use env var)"
    )
    AZURE_EMBEDDING_API_KEY: str = Field(
        default="",
        description="Azure OpenAI embedding API key (leave empty to use env var)"
    )
    AZURE_EMBEDDING_DEPLOYMENT: str = Field(
        default="text-embedding-ada-002",
        description="Azure OpenAI embedding deployment name"
    )
    REQUEST_TIMEOUT: int = Field(
        default=10,
        description="Timeout in seconds for API requests"
    )
    DEFAULT_RECALL_LIMIT: int = Field(
        default=5,
        description="Default number of memories to recall"
    )
    MAX_CONTENT_PREVIEW: int = Field(
        default=200,
        description="Maximum characters to show in content preview"
    )
    ENABLE_RERANKING: bool = Field(
        default=False,
        description="Enable reranking for more accurate results"
    )
    RERANKER_TYPE: str = Field(
        default="azure_cohere",
        description="Reranker type: 'azure_cohere' (API) or 'local' (cross-encoder model)"
    )
    AZURE_COHERE_RERANK_ENDPOINT: str = Field(
        default="",
        description="Azure Cohere Rerank API endpoint (leave empty to use env var)"
    )
    AZURE_COHERE_RERANK_API_KEY: str = Field(
        default="",
        description="Azure Cohere Rerank API key (leave empty to use env var)"
    )
    AZURE_COHERE_RERANK_MODEL: str = Field(
        default="Cohere-rerank-v4.0-fast",
        description="Azure Cohere Rerank model deployment name"
    )
    LOCAL_RERANKER_MODEL: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        description="Local cross-encoder model for reranking (only if RERANKER_TYPE='local')"
    )
    RECENCY_WEIGHT: float = Field(
        default=0.0,
        description="Weight for recency boost (0.0=disabled, 0.1-0.3=subtle, 0.5+=strong)"
    )
    RERANK_TOP_K: int = Field(
        default=20,
        description="Number of candidates to retrieve before reranking (should be > limit)"
    )


class Tools:
    """Open WebUI Tool: Long-Term Memory via Qdrant Vector Database"""

    def __init__(self):
        self.valves = Valves()
        self.embedding_model = None
        self.local_reranker = None

    def _get_qdrant_url(self) -> str:
        """Get Qdrant URL from valves or auto-detect."""
        if self.valves.QDRANT_URL:
            return self.valves.QDRANT_URL
        return get_service_url("qdrant", 6333)

    def _get_embedding_model(self):
        """
        Lazily initialize and return the local embedding model.
        Uses sentence-transformers with the configured model.
        """
        if self.embedding_model is None:
            try:
                self.embedding_model = SentenceTransformer(self.valves.EMBEDDING_MODEL)
            except Exception as e:
                raise Exception(f"Failed to load embedding model: {str(e)}")
        return self.embedding_model

    def _get_azure_embedding(self, text: str) -> list:
        """
        Get embedding from Azure OpenAI embedding endpoint.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        endpoint = self.valves.AZURE_EMBEDDING_ENDPOINT or os.getenv("AZURE_EMBEDDING_ENDPOINT", "")
        api_key = self.valves.AZURE_EMBEDDING_API_KEY or os.getenv("AZURE_EMBEDDING_API_KEY", "")
        deployment = self.valves.AZURE_EMBEDDING_DEPLOYMENT or os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
        
        if not endpoint or not api_key:
            raise Exception("Azure embedding credentials not configured. Set AZURE_EMBEDDING_ENDPOINT and AZURE_EMBEDDING_API_KEY.")
        
        # Azure OpenAI embedding API format
        payload = {
            "input": text
        }
        
        headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        
        # Build URL - handle both full URL and base endpoint
        if "/deployments/" in endpoint:
            url = endpoint
        else:
            url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/embeddings?api-version=2024-02-01"
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=self.valves.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"Azure embedding failed: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["data"][0]["embedding"]

    def _get_embedding(self, text: str) -> list:
        """
        Get embedding using configured method (local or Azure).
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        if self.valves.EMBEDDING_TYPE == "azure":
            return self._get_azure_embedding(text)
        else:
            model = self._get_embedding_model()
            return model.encode(text).tolist()

    def _get_local_reranker(self):
        """Lazily initialize local cross-encoder reranker."""
        if self.local_reranker is None:
            try:
                from sentence_transformers import CrossEncoder
                self.local_reranker = CrossEncoder(self.valves.LOCAL_RERANKER_MODEL)
            except Exception as e:
                raise Exception(f"Failed to load local reranker: {str(e)}")
        return self.local_reranker

    def _rerank_with_azure_cohere(self, query: str, documents: list) -> list:
        """
        Rerank documents using Azure Cohere Rerank API.
        
        Args:
            query: The search query
            documents: List of dicts with 'content' and original result data
            
        Returns:
            Reranked list of documents with updated scores
        """
        # Get credentials from valves or environment
        endpoint = self.valves.AZURE_COHERE_RERANK_ENDPOINT or os.getenv("AZURE_COHERE_RERANK_ENDPOINT", "")
        api_key = self.valves.AZURE_COHERE_RERANK_API_KEY or os.getenv("AZURE_COHERE_RERANK_API_KEY", "")
        model = self.valves.AZURE_COHERE_RERANK_MODEL or os.getenv("AZURE_COHERE_RERANK_MODEL", "Cohere-rerank-v4.0-fast")
        
        if not endpoint or not api_key:
            raise Exception("Azure Cohere Rerank credentials not configured. Set AZURE_COHERE_RERANK_ENDPOINT and AZURE_COHERE_RERANK_API_KEY.")
        
        # Prepare documents for Cohere API
        doc_texts = [doc.get("payload", {}).get("content", "") for doc in documents]
        
        payload = {
            "model": model,
            "query": query,
            "documents": doc_texts,
            "top_n": len(documents)
        }
        
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=self.valves.REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            raise Exception(f"Azure Cohere Rerank failed: {response.status_code} - {response.text}")
        
        result = response.json()
        reranked_results = result.get("results", [])
        
        # Rebuild document list with new scores
        reranked_docs = []
        for item in reranked_results:
            idx = item.get("index", 0)
            relevance_score = item.get("relevance_score", 0)
            original_doc = documents[idx].copy()
            original_doc["score"] = relevance_score
            original_doc["original_score"] = documents[idx].get("score", 0)
            reranked_docs.append(original_doc)
        
        return reranked_docs

    def _rerank_with_local_model(self, query: str, documents: list) -> list:
        """
        Rerank documents using local cross-encoder model.
        
        Args:
            query: The search query
            documents: List of dicts with 'content' and original result data
            
        Returns:
            Reranked list of documents with updated scores
        """
        reranker = self._get_local_reranker()
        
        # Prepare query-document pairs
        pairs = [(query, doc.get("payload", {}).get("content", "")) for doc in documents]
        
        # Get reranking scores
        scores = reranker.predict(pairs)
        
        # Rebuild document list with new scores
        reranked_docs = []
        for idx, score in enumerate(scores):
            original_doc = documents[idx].copy()
            original_doc["original_score"] = documents[idx].get("score", 0)
            original_doc["score"] = float(score)
            reranked_docs.append(original_doc)
        
        # Sort by new score descending
        reranked_docs.sort(key=lambda x: x["score"], reverse=True)
        return reranked_docs

    def _apply_recency_boost(self, documents: list) -> list:
        """
        Apply recency weighting to document scores.
        
        Args:
            documents: List of scored documents
            
        Returns:
            Documents with recency-boosted scores
        """
        if self.valves.RECENCY_WEIGHT <= 0:
            return documents
        
        current_time = time.time()
        max_age = 30 * 24 * 3600  # 30 days in seconds
        
        for doc in documents:
            metadata = doc.get("payload", {}).get("metadata", {})
            timestamp = metadata.get("timestamp", current_time)
            age = current_time - timestamp
            
            # Recency factor: 1.0 for new, decaying to 0.0 for old
            recency_factor = max(0, 1 - (age / max_age))
            
            # Blend original score with recency
            original_score = doc.get("score", 0)
            boosted_score = (1 - self.valves.RECENCY_WEIGHT) * original_score + self.valves.RECENCY_WEIGHT * recency_factor
            doc["score"] = boosted_score
        
        # Re-sort by boosted score
        documents.sort(key=lambda x: x["score"], reverse=True)
        return documents

    def _rerank_results(self, query: str, results: list, limit: int) -> list:
        """
        Apply reranking pipeline to search results.
        
        Args:
            query: The search query
            results: Raw vector search results from Qdrant
            limit: Final number of results to return
            
        Returns:
            Reranked and limited results
        """
        if not self.valves.ENABLE_RERANKING or not results:
            return results[:limit]
        
        # Apply semantic reranking
        if self.valves.RERANKER_TYPE == "azure_cohere":
            reranked = self._rerank_with_azure_cohere(query, results)
        elif self.valves.RERANKER_TYPE == "local":
            reranked = self._rerank_with_local_model(query, results)
        else:
            reranked = results
        
        # Apply recency boost if configured
        if self.valves.RECENCY_WEIGHT > 0:
            reranked = self._apply_recency_boost(reranked)
        
        return reranked[:limit]

    def store_memory(
        self,
        content: str,
        metadata: dict = None,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Store information in MAGI's long-term memory (Qdrant Vector Database)

        This tool allows MAGI to remember facts, conversations, and documents
        for future recall using RAG (Retrieval Augmented Generation).

        Security: Requires valid user authentication. Each memory is tagged
        with the user's ID to ensure proper isolation.

        Args:
            content: The text content to store in memory
            metadata: Optional metadata (tags, source, timestamp, etc.)
            __user__: User context (provided by Open WebUI) - REQUIRED
            __event_emitter__: Event emitter for streaming results (provided by Open WebUI)

        Returns:
            Confirmation message with memory ID, or error if no user context
        """

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "💾 Storing in long-term memory...",
                        "done": False,
                    },
                }
            )

        try:
            # Require valid user context for security (check FIRST before any operations)
            user_id = __user__.get("id") if __user__ else None
            if not user_id:
                error_msg = "User authentication required to store memories"
                if __event_emitter__:
                    __event_emitter__(
                        {
                            "type": "status",
                            "data": {"description": f"❌ {error_msg}", "done": True},
                        }
                    )
                return f"Memory storage failed: {error_msg}"

            # First, ensure collection exists
            self._ensure_collection_exists()

            # Generate embedding using configured method (local or Azure)
            embedding = self._get_embedding(content)

            # Generate unique ID using UUID to avoid collisions
            memory_id = str(uuid.uuid4())

            # Prepare metadata (create a new dict to avoid modifying the input)
            prepared_metadata = dict(metadata) if metadata else {}

            # Add user context to metadata
            prepared_metadata["user_id"] = user_id
            prepared_metadata["user_name"] = __user__.get("name", "unknown")

            # Add timestamp
            prepared_metadata["timestamp"] = time.time()

            # Store in Qdrant using upsert
            upsert_payload = {
                "points": [
                    {
                        "id": memory_id,
                        "vector": embedding,
                        "payload": {
                            "content": content,
                            "metadata": prepared_metadata
                        }
                    }
                ]
            }

            qdrant_url = self._get_qdrant_url()
            response = requests.put(
                f"{qdrant_url}/collections/{self.valves.COLLECTION_NAME}/points",
                json=upsert_payload,
                timeout=self.valves.REQUEST_TIMEOUT,
            )

            if response.status_code not in [200, 201]:
                raise Exception(
                    f"Failed to store in Qdrant: {response.status_code} - {response.text}"
                )

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "✅ Memory stored successfully",
                            "done": True,
                        },
                    }
                )

            return (
                f"✅ Stored in MAGI's long-term memory\n\n"
                f"**Memory ID**: {memory_id}\n"
                f"**Content**: {content[:self.valves.MAX_CONTENT_PREVIEW]}{'...' if len(content) > self.valves.MAX_CONTENT_PREVIEW else ''}\n\n"
                f"This information can now be recalled using semantic search."
            )

        except Exception as e:
            error_msg = f"Error storing memory: {str(e)}"

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )

            return f"Memory storage failed: {error_msg}"

    def recall_memory(
        self,
        query: str,
        limit: int = 5,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Recall information from MAGI's long-term memory using semantic search

        This tool performs RAG (Retrieval Augmented Generation) by searching
        the vector database for semantically similar content to the query.
        This prevents hallucination by providing factual context.

        Memory isolation: Each user can only access their own memories.
        Results are automatically filtered by user_id to ensure privacy.

        Args:
            query: What to search for in memory
            limit: Maximum number of results to return (default: 5)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results (provided by Open WebUI)

        Returns:
            Relevant memories from the vector database (user-filtered)
        """

        if __event_emitter__:
            __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": "🧠 Searching long-term memory...",
                        "done": False,
                    },
                }
            )

        try:
            # Generate query embedding using configured method
            query_embedding = self._get_embedding(query)

            # When reranking is enabled, fetch more candidates
            fetch_limit = self.valves.RERANK_TOP_K if self.valves.ENABLE_RERANKING else limit

            # Build search payload with user filtering
            search_payload = {
                "vector": query_embedding,
                "limit": fetch_limit,
                "with_payload": True
            }

            # Add user-specific filter to ensure memory isolation
            # Only return memories that belong to the current user
            user_id = __user__.get("id") if __user__ else None
            if user_id:
                search_payload["filter"] = {
                    "must": [
                        {
                            "key": "metadata.user_id",
                            "match": {
                                "value": user_id
                            }
                        }
                    ]
                }
            else:
                # No user context - return empty results for privacy
                # This prevents accidental exposure of all users' memories
                if __event_emitter__:
                    __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": "⚠️ No user context - privacy protected",
                                "done": True,
                            },
                        }
                    )
                return (
                    f"# Memory Recall: '{query}'\n\n"
                    f"⚠️ No user context available. Unable to search memories.\n"
                    f"This is a privacy protection to prevent unauthorized access."
                )

            qdrant_url = self._get_qdrant_url()
            response = requests.post(
                f"{qdrant_url}/collections/{self.valves.COLLECTION_NAME}/points/search",
                json=search_payload,
                timeout=self.valves.REQUEST_TIMEOUT,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Failed to search Qdrant: {response.status_code} - {response.text}"
                )

            # Parse response and check for empty result
            try:
                response_json = response.json()
            except json.JSONDecodeError:
                raise Exception(
                    f"Qdrant returned invalid JSON response: {response.text[:200]}"
                )

            # Check if response is empty or malformed
            if not response_json or response_json == {}:
                if __event_emitter__:
                    __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": "⚠️ Received empty response from Qdrant",
                                "done": True,
                            },
                        }
                    )
                return (
                    f"⚠️ Qdrant returned an empty response for query: '{query}'\n\n"
                    f"This may indicate:\n"
                    f"1. The Qdrant service is not properly configured\n"
                    f"2. The collection may be empty or not initialized\n"
                    f"3. The query format may be incorrect\n\n"
                    f"Try:\n"
                    f"- Verify Qdrant is running: `docker ps | grep qdrant`\n"
                    f"- Check Qdrant logs: `docker logs rin-qdrant`\n"
                    f"- Store some memories first using `store_memory()`"
                )

            results = response_json.get("result", [])

            # Apply reranking if enabled
            if self.valves.ENABLE_RERANKING and results:
                if __event_emitter__:
                    __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": f"🔄 Reranking with {self.valves.RERANKER_TYPE}...",
                                "done": False,
                            },
                        }
                    )
                results = self._rerank_results(query, results, limit)

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": "✅ Memory search completed",
                            "done": True,
                        },
                    }
                )

            # Format results
            if not results:
                return (
                    f"# Memory Recall: '{query}'\n\n"
                    f"No memories found matching this query.\n"
                    f"Store memories using the `store_memory` tool."
                )

            # Build response with results
            rerank_note = " (reranked)" if self.valves.ENABLE_RERANKING else ""
            response_text = f"# Memory Recall: '{query}'\n\n"
            response_text += f"Found {len(results)} relevant memories{rerank_note}:\n\n"

            for idx, result in enumerate(results, 1):
                score = result.get("score", 0)
                payload = result.get("payload", {})
                content = payload.get("content", "")
                metadata = payload.get("metadata", {})

                response_text += f"## Memory {idx} (Similarity: {score:.3f})\n"
                response_text += f"{content}\n"

                if metadata:
                    response_text += f"\n*Metadata: {json.dumps(metadata, indent=2)}*\n"

                response_text += "\n---\n\n"

            return response_text

        except Exception as e:
            error_msg = f"Error recalling memory: {str(e)}"

            if __event_emitter__:
                __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"❌ {error_msg}", "done": True},
                    }
                )

            return f"Memory recall failed: {error_msg}"

    def _ensure_collection_exists(self):
        """
        Ensure the Qdrant collection exists, create if needed.

        This is critical on first deployment - without this check, the memory
        tool will crash when trying to upsert data into a non-existent collection.
        """
        try:
            qdrant_url = self._get_qdrant_url()
            # Check if collection exists
            response = requests.get(
                f"{qdrant_url}/collections/{self.valves.COLLECTION_NAME}",
                timeout=self.valves.REQUEST_TIMEOUT,
            )

            if response.status_code == 404:
                # Collection doesn't exist - create it
                create_response = requests.put(
                    f"{qdrant_url}/collections/{self.valves.COLLECTION_NAME}",
                    json={
                        "vectors": {
                            "size": self.valves.EMBEDDING_DIM,
                            "distance": "Cosine",
                        }
                    },
                    timeout=self.valves.REQUEST_TIMEOUT,
                )

                if create_response.status_code not in [200, 201]:
                    raise Exception(
                        f"Failed to create collection: {create_response.status_code}"
                    )

            elif response.status_code != 200:
                raise Exception(
                    f"Failed to check collection status: {response.status_code}"
                )

        except requests.exceptions.ConnectionError:
            raise Exception(
                "Cannot connect to Qdrant. Ensure service is running (docker-compose up -d)"
            )
        except requests.exceptions.Timeout:
            raise Exception(
                "Qdrant connection timeout. Service may be starting up or overloaded"
            )
        except Exception as e:
            if "Failed" in str(e) or "Cannot connect" in str(e):
                raise  # Re-raise our custom exceptions
            # For other exceptions, provide generic error
            raise Exception(f"Qdrant initialization failed: {str(e)}")
