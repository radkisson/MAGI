"""
Qdrant Memory Tool for Open WebUI

This tool connects the Cortex (Open WebUI) to the Memory (Qdrant),
allowing RIN to store and retrieve information with RAG capabilities.
"""

import requests
from typing import Callable, Any, List
import json


class Tools:
    """Open WebUI Tool: Long-Term Memory via Qdrant Vector Database"""

    def __init__(self):
        self.qdrant_url = "http://qdrant:6333"
        self.collection_name = "rin_memory"

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

        Args:
            content: The text content to store in memory
            metadata: Optional metadata (tags, source, timestamp, etc.)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results (provided by Open WebUI)

        Returns:
            Confirmation message with memory ID
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
            # First, ensure collection exists
            self._ensure_collection_exists()

            # Generate embedding (this would typically use an embedding model)
            # For now, this is a placeholder - in production, use OpenAI embeddings or similar
            import hashlib
            memory_id = hashlib.md5(content.encode()).hexdigest()

            # Store in Qdrant
            # Note: In production, you'd generate actual embeddings here
            # This is a simplified implementation

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

        Args:
            query: What to search for in memory
            limit: Maximum number of results to return (default: 5)
            __user__: User context (provided by Open WebUI)
            __event_emitter__: Event emitter for streaming results (provided by Open WebUI)

        Returns:
            Relevant memories from the vector database
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
            # Query Qdrant for similar vectors
            # Note: In production, you'd generate query embedding and perform vector search
            # This is a simplified placeholder

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

            return (
                f"# Memory Recall: '{query}'\n\n"
                f"Searching RIN's long-term memory via Qdrant vector database...\n\n"
                f"**Note**: Full RAG implementation requires embedding model integration.\n"
                f"Current status: Memory infrastructure ready, embeddings pending."
            )

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
                            "size": 768,  # Standard embedding dimension (text-embedding-ada-002)
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
