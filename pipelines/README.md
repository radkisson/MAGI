# MAGI Pipelines

This directory contains Open WebUI pipelines for MAGI's extended functionality.

## Available Pipelines

### memory_auto_rag.py - Auto-RAG Memory Pipeline

A filter pipeline that automatically injects relevant memories into every conversation.

**Features:**
- **Inlet (Pre-processing):** Recalls relevant memories and injects them into the user's message context
- **Outlet (Post-processing):** Optionally extracts and stores important info from responses via n8n

**How it works:**
```
User Message → [Recall Memories] → [Inject Context] → LLM → Response → [Optional: Extract & Store]
```

## Installation

### Option 1: Via Open WebUI UI (Recommended)

1. Go to Open WebUI → **Workspace** → **Functions**
2. Click **+ Add Function**
3. Select **Filter** type
4. Copy the content of `memory_auto_rag.py`
5. Save and enable

### Option 2: Via Pipelines Server

If running the pipelines server separately:

1. Copy files to your pipelines directory:
   ```bash
   cp pipelines/*.py /path/to/pipelines/server/pipelines/
   ```

2. Restart the pipelines server

3. Connect in Open WebUI → Admin → Pipelines

## Configuration (Valves)

| Valve | Default | Description |
|-------|---------|-------------|
| `pipelines` | `["*"]` | Target models (use `*` for all) |
| `QDRANT_URL` | `http://magi-memory:6333` | Qdrant instance URL |
| `COLLECTION_NAME` | `rin_memory` | Memory collection name |
| `AZURE_EMBEDDING_ENDPOINT` | (env) | Azure embedding API endpoint |
| `AZURE_EMBEDDING_API_KEY` | (env) | Azure embedding API key |
| `RECALL_LIMIT` | `3` | Max memories to inject |
| `MIN_SIMILARITY` | `0.7` | Minimum similarity threshold |
| `ENABLE_AUTO_STORE` | `False` | Auto-extract info from responses |
| `N8N_WEBHOOK_URL` | `http://magi-reflex-automation:5678/webhook/conversation-summary` | n8n webhook for extraction |

## Usage Examples

### Basic Auto-RAG (Memory Recall Only)

Default configuration - just enable the pipeline:
- Memories are recalled on every user message
- Relevant context is injected before sending to LLM
- No automatic storage

### Full Auto-RAG (Recall + Store)

Set `ENABLE_AUTO_STORE=True`:
- Memories recalled and injected
- Every 5 messages, conversation is sent to n8n for extraction
- Important facts automatically stored in Qdrant

## How Memory Injection Looks

When you send a message like "What framework should I use?", and you have stored memories about your preferences, the pipeline modifies your message to:

```
What framework should I use?

---
**Relevant memories:**
1. User prefers Python for backend development (relevance: 0.89)
2. User always uses FastAPI for APIs (relevance: 0.82)
3. User is working on Project Alpha (relevance: 0.75)
```

The LLM then sees this augmented context and can provide personalized responses.

## Troubleshooting

### Memories not being recalled
1. Check Qdrant is running: `docker ps | grep qdrant`
2. Verify collection exists: `curl http://localhost:6333/collections/rin_memory`
3. Ensure Azure embedding credentials are set
4. Check minimum similarity threshold isn't too high

### Pipeline not activating
1. Verify pipeline is enabled in Open WebUI Functions
2. Check `pipelines` valve includes your model
3. Look at Open WebUI logs for errors

### Auto-store not working
1. Set `ENABLE_AUTO_STORE=True`
2. Verify n8n is running and workflow is active
3. Check n8n logs for webhook errors
