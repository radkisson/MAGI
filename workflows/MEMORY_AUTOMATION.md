# MAGI Memory Automation Workflow

This n8n workflow automates memory storage and management for MAGI's long-term memory system.

## Features

### 1. Direct Memory Storage Webhook
**Endpoint:** `POST /webhook/memory-store`

Store memories directly via API:

```bash
curl -X POST http://localhost:5678/webhook/memory-store \
  -H "Content-Type: application/json" \
  -d '{
    "content": "User prefers dark mode interfaces",
    "user_id": "user-123",
    "user_name": "John",
    "category": "preferences"
  }'
```

### 2. Conversation Summary Webhook
**Endpoint:** `POST /webhook/conversation-summary`

Send a conversation to extract and store key memories automatically:

```bash
curl -X POST http://localhost:5678/webhook/conversation-summary \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "user_name": "John",
    "messages": [
      {"role": "user", "content": "I prefer Python for backend development"},
      {"role": "assistant", "content": "Great choice! Python is excellent for backends."},
      {"role": "user", "content": "Yes, and I always use FastAPI for APIs"},
      {"role": "assistant", "content": "FastAPI is a fantastic modern framework."}
    ]
  }'
```

The workflow uses GPT-4o-mini to extract important facts and stores them automatically.

### 3. Daily Memory Consolidation
**Schedule:** Every 24 hours

Automatically:
- Reviews all stored memories
- Identifies duplicates and near-duplicates
- Merges related memories
- Removes outdated contradictory information

## Installation

### 1. Import the Workflow

1. Open n8n (http://localhost:5678 or your n8n URL)
2. Go to **Workflows** → **Import from File**
3. Select `workflows/memory_automation.json`
4. Click **Import**

### 2. Configure Environment Variables

The workflow uses these environment variables (already in your `.env`):

```bash
AZURE_EMBEDDING_ENDPOINT=https://rizzai-02.cognitiveservices.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15
AZURE_EMBEDDING_API_KEY=your-key
LITELLM_MASTER_KEY=your-litellm-key
```

### 3. Set Up n8n Environment Variables

In n8n:
1. Go to **Settings** → **Variables**
2. Add:
   - `AZURE_EMBEDDING_ENDPOINT` 
   - `AZURE_EMBEDDING_API_KEY`
   - `LITELLM_MASTER_KEY`

Or use the n8n credentials system.

### 4. Activate the Workflow

1. Open the imported workflow
2. Click **Active** toggle to enable
3. Test with a sample request

## Integration with Open WebUI

### Option A: Post-Conversation Hook (Recommended)

Create an Open WebUI **Pipeline** that calls the conversation-summary webhook after each chat:

```python
# In Open WebUI Pipelines
import requests

class ConversationMemoryPipeline:
    def __init__(self):
        self.n8n_url = "http://magi-reflex-automation:5678/webhook/conversation-summary"
    
    async def on_chat_end(self, messages, user):
        try:
            requests.post(self.n8n_url, json={
                "user_id": user.get("id"),
                "user_name": user.get("name"),
                "messages": messages[-10:]  # Last 10 messages
            }, timeout=5)
        except:
            pass  # Don't block on failure
```

### Option B: Manual Trigger via Tool

Add a tool that triggers memory summarization:

```python
def summarize_conversation(messages: list, __user__: dict = {}):
    """Summarize and store memories from current conversation"""
    requests.post("http://magi-reflex-automation:5678/webhook/conversation-summary", json={
        "user_id": __user__.get("id"),
        "user_name": __user__.get("name"),
        "messages": messages
    })
    return "Conversation memories have been extracted and stored."
```

## Memory Categories

The system uses these categories for organization:

| Category | Description | Examples |
|----------|-------------|----------|
| `preferences` | User preferences and likes | "Prefers dark mode", "Likes Python" |
| `facts` | Factual information about user | "Works at Company X", "Lives in City Y" |
| `decisions` | Decisions made in conversations | "Chose React for frontend" |
| `context` | Background context | "Working on Project Z" |
| `goals` | User goals and objectives | "Learning machine learning" |

## API Reference

### Store Memory

```http
POST /webhook/memory-store
Content-Type: application/json

{
  "content": "string (required) - The memory content",
  "user_id": "string (required) - User identifier",
  "user_name": "string (optional) - User display name",
  "category": "string (optional) - Memory category"
}
```

**Response:**
```json
{
  "status": "success",
  "memory_id": "uuid",
  "message": "Memory stored successfully"
}
```

### Conversation Summary

```http
POST /webhook/conversation-summary
Content-Type: application/json

{
  "user_id": "string (required)",
  "user_name": "string (optional)",
  "messages": [
    {"role": "user|assistant", "content": "string"}
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "memories_stored": 3,
  "message": "Conversation memories extracted and stored"
}
```

## Troubleshooting

### Webhook not responding
- Check n8n is running: `docker ps | grep n8n`
- Verify workflow is active
- Check n8n logs: `docker logs magi-reflex-automation`

### Embeddings failing
- Verify Azure API key is correct
- Check endpoint URL format
- Test embedding manually:
  ```bash
  curl -X POST "https://rizzai-02.cognitiveservices.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15" \
    -H "api-key: YOUR_KEY" \
    -H "Content-Type: application/json" \
    -d '{"input": "test"}'
  ```

### Qdrant storage failing
- Check Qdrant is running: `docker ps | grep qdrant`
- Verify collection exists: `curl http://localhost:6333/collections/rin_memory`
- Check vector dimensions match (1536 for ada-002)

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Open WebUI    │────▶│      n8n        │────▶│     Qdrant      │
│  (Conversations)│     │  (Automation)   │     │    (Memory)     │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Azure OpenAI  │
                        │  (Embeddings +  │
                        │   Extraction)   │
                        └─────────────────┘
```
