"""
MAGI Auto-RAG Memory Pipeline

This filter pipeline automatically:
1. Recalls relevant memories on every user message (inlet)
2. Injects memories into the context for the LLM
3. Optionally extracts and stores important info after responses (outlet)

Install: Copy to Open WebUI → Admin → Functions → Add Function → Filter
"""

import os
import hashlib
import requests
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Pipeline:
    """Auto-RAG Filter Pipeline for MAGI Memory System"""

    class Valves(BaseModel):
        """Configuration for the memory pipeline"""
        pipelines: List[str] = Field(
            default=["*"],
            description="Target model pipelines to apply this filter to"
        )
        priority: int = Field(
            default=0,
            description="Pipeline priority (lower = runs first on inlet, last on outlet)"
        )
        QDRANT_URL: str = Field(
            default="http://magi-memory:6333",
            description="Qdrant vector database URL"
        )
        COLLECTION_NAME: str = Field(
            default="rin_memory",
            description="Qdrant collection name for memories"
        )
        AZURE_EMBEDDING_ENDPOINT: str = Field(
            default="",
            description="Azure OpenAI embedding endpoint (or use env var)"
        )
        AZURE_EMBEDDING_API_KEY: str = Field(
            default="",
            description="Azure OpenAI embedding API key (or use env var)"
        )
        RECALL_LIMIT: int = Field(
            default=3,
            description="Max memories to inject into context"
        )
        MIN_SIMILARITY: float = Field(
            default=0.7,
            description="Minimum similarity score to include memory"
        )
        ENABLE_AUTO_STORE: bool = Field(
            default=False,
            description="Auto-extract and store important info from responses"
        )
        N8N_WEBHOOK_URL: str = Field(
            default="http://magi-reflex-automation:5678/webhook/conversation-summary",
            description="n8n webhook for conversation summarization"
        )
        MEMORY_INJECTION_PREFIX: str = Field(
            default="\n\n---\n**Relevant memories:**\n",
            description="Prefix for injected memories"
        )

    def __init__(self):
        self.type = "filter"
        self.name = "MAGI Auto-RAG Memory"
        self.valves = self.Valves()

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from Azure OpenAI"""
        endpoint = self.valves.AZURE_EMBEDDING_ENDPOINT or os.getenv("AZURE_EMBEDDING_ENDPOINT", "")
        api_key = self.valves.AZURE_EMBEDDING_API_KEY or os.getenv("AZURE_EMBEDDING_API_KEY", "")
        
        if not endpoint or not api_key:
            return None
        
        try:
            response = requests.post(
                endpoint,
                json={"input": text},
                headers={"api-key": api_key, "Content-Type": "application/json"},
                timeout=15
            )
            if response.status_code == 200:
                return response.json()["data"][0]["embedding"]
            else:
                print(f"[MAGI Memory] Embedding API error: {response.status_code} - {response.text[:200]}")
        except Exception as e:
            print(f"[MAGI Memory] Embedding request failed: {e}")
        return None

    def _recall_memories(self, query: str, user_id: str) -> List[Dict[str, Any]]:
        """Recall relevant memories from Qdrant"""
        embedding = self._get_embedding(query)
        if not embedding:
            return []
        
        try:
            search_payload = {
                "vector": embedding,
                "limit": self.valves.RECALL_LIMIT * 2,  # Fetch extra for filtering
                "with_payload": True,
                "filter": {
                    "must": [
                        {"key": "metadata.user_id", "match": {"value": user_id}}
                    ]
                }
            }
            
            response = requests.post(
                f"{self.valves.QDRANT_URL}/collections/{self.valves.COLLECTION_NAME}/points/search",
                json=search_payload,
                timeout=15
            )
            
            if response.status_code == 200:
                results = response.json().get("result", [])
                filtered = [
                    r for r in results 
                    if r.get("score", 0) >= self.valves.MIN_SIMILARITY
                ]
                return filtered[:self.valves.RECALL_LIMIT]
            else:
                print(f"[MAGI Memory] Qdrant search error: {response.status_code}")
        except Exception as e:
            print(f"[MAGI Memory] Recall failed: {e}")
        return []

    def _format_memories(self, memories: List[Dict[str, Any]]) -> str:
        """Format memories for injection into context"""
        if not memories:
            return ""
        
        lines = [self.valves.MEMORY_INJECTION_PREFIX]
        for i, mem in enumerate(memories, 1):
            content = mem.get("payload", {}).get("content", "")
            score = mem.get("score", 0)
            lines.append(f"{i}. {content} (relevance: {score:.2f})")
        
        return "\n".join(lines)

    def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Pre-process incoming message: recall and inject relevant memories.
        
        This runs BEFORE the message is sent to the LLM, allowing us to
        augment the context with relevant historical information.
        """
        if not user:
            return body
        
        user_id = user.get("id", "")
        if not user_id:
            return body
        
        messages = body.get("messages", [])
        if not messages:
            return body
        
        # Get the latest user message
        last_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_message = msg
                break
        
        if not last_message:
            return body
        
        user_query = last_message.get("content", "")
        if not user_query or len(user_query) < 10:
            return body
        
        # Recall relevant memories
        memories = self._recall_memories(user_query, user_id)
        
        if memories:
            # Inject memories into the last user message (copy to avoid side effects)
            memory_context = self._format_memories(memories)
            augmented_content = user_query + memory_context
            # Find and update the message in the list
            for i, msg in enumerate(messages):
                if msg is last_message:
                    body["messages"][i] = {**msg, "content": augmented_content}
                    break
        
        return body

    def outlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """
        Post-process outgoing response: optionally trigger memory extraction.
        
        This runs AFTER the LLM responds, allowing us to extract and store
        important information from the conversation.
        """
        if not self.valves.ENABLE_AUTO_STORE:
            return body
        
        if not user:
            return body
        
        user_id = user.get("id", "")
        user_name = user.get("name", "unknown")
        
        # Get conversation messages
        messages = body.get("messages", [])
        if len(messages) < 2:
            return body
        
        # Trigger async memory extraction via n8n webhook (non-blocking)
        # Use content hash to avoid duplicate processing
        try:
            content_hash = hashlib.md5(
                str(messages[-1].get("content", "")).encode()
            ).hexdigest()[:8]
            
            # Only process if conversation has meaningful content (>100 chars in last msg)
            last_content = messages[-1].get("content", "")
            if len(last_content) > 100:
                requests.post(
                    self.valves.N8N_WEBHOOK_URL,
                    json={
                        "user_id": user_id,
                        "user_name": user_name,
                        "messages": messages[-10:],
                        "content_hash": content_hash
                    },
                    timeout=2
                )
        except Exception as e:
            print(f"[MAGI Memory] Auto-store webhook failed: {e}")
        
        return body
