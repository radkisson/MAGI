"""
MAGI Memory Review Tool

Human-in-the-loop memory curation. Review AI-extracted memories before
they're permanently stored.

Flow:
1. n8n extracts potential memories → stores in pending queue
2. User calls review_pending_memories() to see queue
3. User approves/rejects each memory
4. Approved memories → permanent storage (rin_memory)
"""

import os
import requests
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Tools:
    class Valves(BaseModel):
        QDRANT_URL: str = Field(
            default="",
            description="Qdrant URL (set via QDRANT_URL env var)"
        )
        AZURE_EMBEDDING_ENDPOINT: str = Field(
            default="",
            description="Azure embedding endpoint (set via AZURE_EMBEDDING_ENDPOINT env var)"
        )
        AZURE_EMBEDDING_API_KEY: str = Field(
            default="",
            description="Azure embedding API key (set via AZURE_EMBEDDING_API_KEY env var)"
        )
        PENDING_COLLECTION: str = Field(
            default="rin_pending_memories",
            description="Collection for pending memories awaiting review"
        )
        APPROVED_COLLECTION: str = Field(
            default="rin_memory",
            description="Collection for approved memories"
        )

    def __init__(self):
        self.valves = self.Valves(
            QDRANT_URL=os.getenv("QDRANT_URL", "http://localhost:6333"),
            AZURE_EMBEDDING_ENDPOINT=os.getenv("AZURE_EMBEDDING_ENDPOINT", ""),
            AZURE_EMBEDDING_API_KEY=os.getenv("AZURE_EMBEDDING_API_KEY", ""),
        )

    def _get_qdrant_url(self) -> str:
        return self.valves.QDRANT_URL or os.getenv("QDRANT_URL", "http://localhost:6333")

    def review_pending_memories(
        self,
        limit: int = 10,
        __user__: dict = None
    ) -> str:
        """
        Review pending memories waiting for your approval.
        
        Shows AI-extracted memories that need human review before being
        permanently stored. Use approve_memory() or reject_memory() to act on them.

        Args:
            limit: Maximum number of pending memories to show (default: 10)

        Returns:
            List of pending memories with their IDs for review
        """
        user_id = __user__.get("id", "") if __user__ else ""
        
        try:
            # Fetch pending memories
            scroll_payload = {
                "limit": limit,
                "with_payload": True,
                "with_vector": False
            }
            
            # Filter by user if available
            if user_id:
                scroll_payload["filter"] = {
                    "must": [
                        {"key": "metadata.user_id", "match": {"value": user_id}}
                    ]
                }
            
            response = requests.post(
                f"{self._get_qdrant_url()}/collections/{self.valves.PENDING_COLLECTION}/points/scroll",
                json=scroll_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                return f"❌ Failed to fetch pending memories: {response.text}"
            
            data = response.json()
            points = data.get("result", {}).get("points", [])
            
            if not points:
                return "✅ No pending memories to review! Your queue is empty."
            
            # Format for display
            lines = [f"📋 **{len(points)} Pending Memories for Review**\n"]
            lines.append("Use `approve_memory(id)` or `reject_memory(id)` to act on each.\n")
            lines.append("---\n")
            
            for i, point in enumerate(points, 1):
                memory_id = point.get("id", "unknown")
                payload = point.get("payload", {})
                content = payload.get("content", "No content")
                metadata = payload.get("metadata", {})
                category = metadata.get("category", "general")
                source = metadata.get("source", "unknown")
                timestamp = metadata.get("timestamp", 0)
                
                # Format timestamp
                if timestamp:
                    dt = datetime.fromtimestamp(timestamp)
                    time_str = dt.strftime("%Y-%m-%d %H:%M")
                else:
                    time_str = "Unknown time"
                
                lines.append(f"**{i}. [{category.upper()}]** {content}")
                lines.append(f"   - ID: `{memory_id}`")
                lines.append(f"   - Source: {source} | {time_str}")
                lines.append("")
            
            lines.append("---")
            lines.append("💡 **Quick actions:**")
            lines.append("- `approve_memory('ID')` - Save to permanent memory")
            lines.append("- `reject_memory('ID')` - Discard this memory")
            lines.append("- `approve_all_pending()` - Approve all shown memories")
            lines.append("- `reject_all_pending()` - Clear the queue")
            
            return "\n".join(lines)
            
        except Exception as e:
            return f"❌ Error reviewing memories: {str(e)}"

    def approve_memory(
        self,
        memory_id: str,
        __user__: dict = None
    ) -> str:
        """
        Approve a pending memory and move it to permanent storage.

        Args:
            memory_id: The ID of the pending memory to approve

        Returns:
            Confirmation message
        """
        user_id = __user__.get("id", "") if __user__ else ""
        
        try:
            # 1. Fetch the pending memory with its vector
            response = requests.post(
                f"{self._get_qdrant_url()}/collections/{self.valves.PENDING_COLLECTION}/points/scroll",
                json={
                    "filter": {
                        "must": [{"has_id": [memory_id]}]
                    },
                    "with_payload": True,
                    "with_vector": True,
                    "limit": 1
                },
                timeout=10
            )
            
            if response.status_code != 200:
                return f"❌ Failed to fetch memory: {response.text}"
            
            points = response.json().get("result", {}).get("points", [])
            if not points:
                return f"❌ Memory ID `{memory_id}` not found in pending queue"
            
            point = points[0]
            vector = point.get("vector", [])
            payload = point.get("payload", {})
            
            # Update metadata
            if "metadata" not in payload:
                payload["metadata"] = {}
            payload["metadata"]["approved_at"] = datetime.now().timestamp()
            payload["metadata"]["approved_by"] = user_id
            
            # 2. Store in approved collection
            store_response = requests.put(
                f"{self._get_qdrant_url()}/collections/{self.valves.APPROVED_COLLECTION}/points",
                json={
                    "points": [{
                        "id": memory_id,
                        "vector": vector,
                        "payload": payload
                    }]
                },
                timeout=10
            )
            
            if store_response.status_code not in [200, 201]:
                return f"❌ Failed to store approved memory: {store_response.text}"
            
            # 3. Delete from pending
            delete_response = requests.post(
                f"{self._get_qdrant_url()}/collections/{self.valves.PENDING_COLLECTION}/points/delete",
                json={"points": [memory_id]},
                timeout=10
            )
            
            content_preview = payload.get("content", "")[:50]
            return f"✅ Memory approved and stored: \"{content_preview}...\""
            
        except Exception as e:
            return f"❌ Error approving memory: {str(e)}"

    def reject_memory(
        self,
        memory_id: str,
        __user__: dict = None
    ) -> str:
        """
        Reject and delete a pending memory.

        Args:
            memory_id: The ID of the pending memory to reject

        Returns:
            Confirmation message
        """
        try:
            response = requests.post(
                f"{self._get_qdrant_url()}/collections/{self.valves.PENDING_COLLECTION}/points/delete",
                json={"points": [memory_id]},
                timeout=10
            )
            
            if response.status_code != 200:
                return f"❌ Failed to reject memory: {response.text}"
            
            return f"🗑️ Memory `{memory_id}` rejected and removed from queue"
            
        except Exception as e:
            return f"❌ Error rejecting memory: {str(e)}"

    def approve_all_pending(
        self,
        __user__: dict = None
    ) -> str:
        """
        Approve all pending memories at once.

        Returns:
            Summary of approved memories
        """
        user_id = __user__.get("id", "") if __user__ else ""
        
        try:
            # Fetch all pending
            scroll_payload = {
                "limit": 100,
                "with_payload": True,
                "with_vector": True
            }
            
            if user_id:
                scroll_payload["filter"] = {
                    "must": [
                        {"key": "metadata.user_id", "match": {"value": user_id}}
                    ]
                }
            
            response = requests.post(
                f"{self._get_qdrant_url()}/collections/{self.valves.PENDING_COLLECTION}/points/scroll",
                json=scroll_payload,
                timeout=15
            )
            
            if response.status_code != 200:
                return f"❌ Failed to fetch pending memories: {response.text}"
            
            points = response.json().get("result", {}).get("points", [])
            
            if not points:
                return "✅ No pending memories to approve"
            
            # Prepare for batch insert
            approved_points = []
            point_ids = []
            
            for point in points:
                memory_id = point.get("id")
                vector = point.get("vector", [])
                payload = point.get("payload", {})
                
                if "metadata" not in payload:
                    payload["metadata"] = {}
                payload["metadata"]["approved_at"] = datetime.now().timestamp()
                payload["metadata"]["approved_by"] = user_id
                payload["metadata"]["batch_approved"] = True
                
                approved_points.append({
                    "id": memory_id,
                    "vector": vector,
                    "payload": payload
                })
                point_ids.append(memory_id)
            
            # Batch insert to approved
            store_response = requests.put(
                f"{self._get_qdrant_url()}/collections/{self.valves.APPROVED_COLLECTION}/points",
                json={"points": approved_points},
                timeout=30
            )
            
            if store_response.status_code not in [200, 201]:
                return f"❌ Failed to store memories: {store_response.text}"
            
            # Batch delete from pending
            requests.post(
                f"{self._get_qdrant_url()}/collections/{self.valves.PENDING_COLLECTION}/points/delete",
                json={"points": point_ids},
                timeout=15
            )
            
            return f"✅ Approved and stored {len(approved_points)} memories"
            
        except Exception as e:
            return f"❌ Error in batch approval: {str(e)}"

    def reject_all_pending(
        self,
        __user__: dict = None
    ) -> str:
        """
        Reject and clear all pending memories.

        Returns:
            Confirmation message
        """
        user_id = __user__.get("id", "") if __user__ else ""
        
        try:
            # Get IDs to delete
            scroll_payload = {
                "limit": 100,
                "with_payload": False,
                "with_vector": False
            }
            
            if user_id:
                scroll_payload["filter"] = {
                    "must": [
                        {"key": "metadata.user_id", "match": {"value": user_id}}
                    ]
                }
            
            response = requests.post(
                f"{self._get_qdrant_url()}/collections/{self.valves.PENDING_COLLECTION}/points/scroll",
                json=scroll_payload,
                timeout=10
            )
            
            if response.status_code != 200:
                return f"❌ Failed to fetch pending memories: {response.text}"
            
            points = response.json().get("result", {}).get("points", [])
            
            if not points:
                return "✅ No pending memories to reject"
            
            point_ids = [p.get("id") for p in points]
            
            # Delete all
            delete_response = requests.post(
                f"{self._get_qdrant_url()}/collections/{self.valves.PENDING_COLLECTION}/points/delete",
                json={"points": point_ids},
                timeout=15
            )
            
            if delete_response.status_code != 200:
                return f"❌ Failed to clear queue: {delete_response.text}"
            
            return f"🗑️ Cleared {len(point_ids)} pending memories from queue"
            
        except Exception as e:
            return f"❌ Error clearing queue: {str(e)}"
