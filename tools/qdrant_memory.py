"""
Qdrant Memory Tool for Open WebUI

This tool connects the Cortex (Open WebUI) to the Memory (Qdrant),
allowing RIN to store and retrieve information with RAG capabilities.
"""

import requests
from typing import Callable, Any, List
import json
import uuid
import time
from sentence_transformers import SentenceTransformer


class Tools:
    """Open WebUI Tool: Long-Term Memory via Qdrant Vector Database"""

    def __init__(self):
        self.qdrant_url = "http://qdrant:6333"
        self.collection_name = "rin_memory"
        self.embedding_model = None
        self.embedding_dim = 768  # Standard dimension for many models

    def _get_embedding_model(self):
        """
        Lazily initialize and return the embedding model.
        Uses sentence-transformers with a 768-dimensional model.
        """
        if self.embedding_model is None:
            try:
                # Using all-mpnet-base-v2: 768 dimensions, good quality, reasonable speed
                self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
            except Exception as e:
                raise Exception(f"Failed to load embedding model: {str(e)}")
        return self.embedding_model

    def store_memory(
        self,
        content: str,
        metadata: dict = None,
        __user__: dict = {},
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Store information in RIN's long-term memory (Qdrant Vector Database)

        This tool allows RIN to remember facts, conversations, and documents
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

            # Generate embedding using sentence-transformers
            model = self._get_embedding_model()
            embedding = model.encode(content).tolist()

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

            response = requests.put(
                f"{self.qdrant_url}/collections/{self.collection_name}/points",
                json=upsert_payload,
                timeout=10,
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
                f"✅ Stored in RIN's long-term memory\n\n"
                f"**Memory ID**: {memory_id}\n"
                f"**Content**: {content[:200]}{'...' if len(content) > 200 else ''}\n\n"
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
        Recall information from RIN's long-term memory using semantic search

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
            # Generate query embedding
            model = self._get_embedding_model()
            query_embedding = model.encode(query).tolist()

            # Build search payload with user filtering
            search_payload = {
                "vector": query_embedding,
                "limit": limit,
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

            response = requests.post(
                f"{self.qdrant_url}/collections/{self.collection_name}/points/search",
                json=search_payload,
                timeout=10,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Failed to search Qdrant: {response.status_code} - {response.text}"
                )

            results = response.json().get("result", [])

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
            response_text = f"# Memory Recall: '{query}'\n\n"
            response_text += f"Found {len(results)} relevant memories:\n\n"
            
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
            # Check if collection exists
            response = requests.get(
                f"{self.qdrant_url}/collections/{self.collection_name}",
                timeout=5,
            )

            if response.status_code == 404:
                # Collection doesn't exist - create it
                create_response = requests.put(
                    f"{self.qdrant_url}/collections/{self.collection_name}",
                    json={
                        "vectors": {
                            "size": 768,  # Dimension for all-mpnet-base-v2 model
                            "distance": "Cosine",  # Cosine similarity for semantic search
                        }
                    },
                    timeout=5,
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
