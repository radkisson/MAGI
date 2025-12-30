# RIN Synaptic Wiring: Tool Definitions

This directory contains the **"nerve endings"** that connect the Cortex (Open WebUI) to the other biological subsystems of RIN. These tools enable Open WebUI to control and utilize the Sensorium, Memory, and Nervous System.

## ✅ Auto-Registration

**Tools are automatically registered** when you run `./start.sh` or `./magi start`. No manual setup required.

### Included Tools

| Tool | Functions | Purpose |
|------|-----------|---------|
| **FireCrawl Scraper** | `scrape_webpage()`, `crawl_website()` | Web scraping with headless browser |
| **Tavily Search** | `web_search()`, `quick_search()`, `deep_search()` | AI-optimized search |
| **SearXNG Search** | `web_search()` | Anonymous metasearch |
| **Qdrant Memory** | `store_memory()`, `recall_memory()` | Long-term RAG memory |
| **n8n Reflex** | `trigger_workflow()`, `list_workflows()` | Workflow automation |

### Verification

After starting RIN, verify tools are registered:

```bash
# Check tools in database
docker exec rin-cortex python3 -c "
import sqlite3
conn = sqlite3.connect('/app/backend/data/webui.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM tool')
for row in cursor.fetchall():
    print(f'  ✅ {row[0]}')
conn.close()
"
```

Or view them in the UI: **Workspace → Tools**

### Manual Registration (If Needed)

If tools don't appear, re-run the registration script:

```bash
docker exec rin-cortex python3 /app/backend/data/tools/register_tools.py
docker restart rin-cortex
```

## 🧠 Architecture: Brain-to-Body Connection

```
┌─────────────────┐
│   Open WebUI    │  The Cortex (Brain)
│   (Cortex)      │
└────────┬────────┘
         │
         │ Tool Definitions (Synaptic Wiring)
         │
    ┌────┴────┬────────┬────────────┐
    │         │        │            │
┌───▼──┐  ┌──▼───┐ ┌──▼─────┐  ┌──▼────┐
│SearXNG│ │FireCrawl│Qdrant│  │ Redis │
│(Vision)│(Digestion)│(Memory)│ │(Reflex)│
└───────┘  └──────┘ └────────┘  └───────┘
   The Sensorium      Memory    Nervous System
```

## 📦 Available Tools

### 1. SearXNG Search (`searxng_search.py`)
**Purpose**: Anonymous web search (The Sensorium's Vision)

**Function**: `web_search(query: str)`

Searches the web anonymously without revealing IP addresses or tracking data. Aggregates results from Google, Bing, and other search engines through SearXNG.

**Example Usage in Open WebUI**:
```
"Search for the latest AI research papers"
```

### 2. Tavily Search (`tavily_search.py`)
**Purpose**: AI-optimized web search (Premium Alternative to SearXNG)

**Functions**:
- `web_search(query: str, search_depth: str, max_results: int)` - Flexible search with options
- `quick_search(query: str)` - Fast search with basic depth (3 results)
- `deep_search(query: str)` - Comprehensive search with advanced depth (10 results)

Tavily is a premium AI-native search engine designed specifically for LLM applications. It provides:
- AI-generated summaries for quick understanding
- Source citations with relevance scoring
- Structured data optimized for LLM consumption
- Real-time information gathering

**Example Usage in Open WebUI**:
```
"Search Tavily for the latest developments in quantum computing"
"Do a deep search on climate change solutions"
```

**Configuration**: Requires TAVILY_API_KEY in .env (get from https://tavily.com)

### 3. FireCrawl Scraper (`firecrawl_scraper.py`)
**Purpose**: Web scraping and content extraction (The Sensorium's Digestion)

**Functions**:
- `scrape_webpage(url: str)` - Extract content from a single page
- `crawl_website(url: str, max_pages: int)` - Crawl multiple pages

Uses headless browsers to handle JavaScript-heavy sites and converts content to clean Markdown optimized for LLM consumption.

**Example Usage in Open WebUI**:
```
"Scrape the content from https://example.com and summarize it"
"Crawl https://docs.python.org and extract the tutorial pages"
```

**Configuration**: 
- Self-hosted mode (default): Uses Docker service, FIRECRAWL_API_KEY auto-generated
- Cloud mode: Set FIRECRAWL_API_URL=https://api.firecrawl.dev and provide your API key

### 4. Qdrant Memory (`qdrant_memory.py`)
**Purpose**: Long-term memory with RAG (The Memory)

**Functions**:
- `store_memory(content: str, metadata: dict)` - Store information
- `recall_memory(query: str, limit: int)` - Retrieve relevant memories

Enables RIN to remember facts and conversations for months, preventing hallucination through retrieval-augmented generation.

**Example Usage in Open WebUI**:
```
"Remember that the user prefers Python over JavaScript"
"What did we discuss about quantum computing last week?"
```

## 🔌 How Tools Are Installed

### Automatic Registration (Default)

When you run `./start.sh`, the script:
1. Mounts `./tools` to `/app/backend/data/tools/` in the container
2. Waits for Open WebUI to initialize
3. Runs `register_tools.py` to insert tools into the database
4. Tools are immediately available in the UI

### Manual Registration (Fallback)

If tools don't appear automatically:

```bash
# Re-run the registration script
docker exec rin-cortex python3 /app/backend/data/tools/register_tools.py

# Restart to pick up changes
docker restart rin-cortex
```

### Adding New Tools

1. Create a new `.py` file in `tools/` directory
2. Follow the structure below (must have `Tools` class)
3. Run registration: `docker exec rin-cortex python3 /app/backend/data/tools/register_tools.py`
4. Restart: `docker restart rin-cortex`

## 🧪 Testing the Synaptic Connections

### Test SearXNG Connection:
```bash
curl "http://localhost:8080/search?q=test&format=json"
```

### Test FireCrawl Connection:
```bash
curl -X POST http://localhost:3002/v0/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "formats": ["markdown"]}'
```

### Test Qdrant Connection:
```bash
curl http://localhost:6333/collections
```

## 🔧 Configuration

### Zero-Config Philosophy: Environment-Driven Auto-Configuration

RIN follows a **"Sovereign Appliance"** philosophy - if an API key exists in your `.env` file, the corresponding tool is immediately live, authenticated, and ready to use. **No manual UI configuration required.**

#### How It Works: The "Pre-Wired" Pipeline

```
Host (.env) → start.sh (Bootloader) → docker-compose.yml → open-webui container → Tool Valves
```

1. **Set API keys in `.env`**:
   ```bash
   FIRECRAWL_API_KEY=fc-your-key-here
   TAVILY_API_KEY=tvly-your-key-here
   ```

2. **Start/Restart RIN**:
   ```bash
   ./start.sh
   ```

3. **Tools are ready**: Open WebUI (http://localhost:3000) → Tools will have API keys pre-filled

#### Smart Valve Pattern

All tools use Pydantic `Valves` classes that automatically pull default values from environment variables:

- **Default behavior**: Keys are auto-loaded from `.env` file
- **Override available**: Users can manually change keys in the Open WebUI Tools settings
- **Graceful fallback**: If a key is missing, tools return clear error messages (not crashes)

### API Key Configuration

#### FireCrawl (Web Scraping)

**Self-hosted mode (default)**:
- `FIRECRAWL_API_KEY` is auto-generated by `start.sh` (starts with `fc-`)
- No manual configuration needed
- Uses Docker service at `http://firecrawl:3002`

**Cloud mode (optional)**:
```bash
# In .env
FIRECRAWL_API_URL=https://api.firecrawl.dev
FIRECRAWL_API_KEY=fc-your-cloud-key-here  # Get from https://firecrawl.dev
```

#### Tavily (AI-Optimized Search)

**External API (requires signup)**:
```bash
# In .env
TAVILY_API_KEY=tvly-your-key-here  # Get from https://tavily.com
```

**Verification**: After restarting, open Open WebUI → Workspace → Tools → Tavily Search → Valves tab - the API key should be pre-populated.

### Troubleshooting Configuration

#### Verify Environment Variables Reached the Container

```bash
# Check if keys are injected into open-webui container
docker exec rin-cortex env | grep -E "FIRECRAWL_API_KEY|TAVILY_API_KEY"
```

You should see your keys displayed. If not:
1. Check your `.env` file has the keys defined
2. Restart the container: `docker compose restart open-webui`
3. Check docker-compose.yml has the environment variables mapped

#### Check Tool Valves in UI

1. Open WebUI: http://localhost:3000
2. Navigate to: Workspace → Tools → [Tool Name] → Valves
3. API Key field should show your key from `.env`
4. If empty, the environment variable didn't reach the container

### Legacy Configuration (Deprecated)

❌ **Old way**: Copy API keys into the Tools settings UI manually after every deployment

✅ **New way**: Set keys in `.env` once, tools auto-authenticate on every boot

All tools use Docker service names for internal networking:
- SearXNG: `http://searxng:8080`
- FireCrawl: `http://firecrawl:3002`
- Qdrant: `http://qdrant:6333`
- Redis: `redis:6379`

These are resolved automatically within the `rin-network` Docker network.

## 🚀 Usage Flow

1. **User asks a question** in Open WebUI
2. **Open WebUI** (Cortex) decides which tool to use
3. **Tool executes** on the appropriate service (SearXNG/FireCrawl/Qdrant)
4. **Results stream back** to the user via event emitters
5. **LLM synthesizes** the final answer using the tool outputs

## 📝 Development Notes

### Critical: Qdrant Collection Initialization

⚠️ **Edge Case Alert**: On first deployment, the Qdrant collection doesn't exist yet.

The `qdrant_memory.py` tool includes automatic collection initialization via `_ensure_collection_exists()`:
- Checks if collection exists on each memory operation
- Creates collection automatically if missing
- Uses 768-dimension vectors (compatible with text-embedding-ada-002)
- Configures Cosine distance for semantic similarity

**What happens without this check:**
```python
# BAD - Will crash on fresh deployment
client.upsert(collection_name="rin_memory", points=[...])
# Error: Collection 'rin_memory' not found
```

**Proper implementation (already in code):**
```python
# GOOD - Safe for fresh deployment
def store_memory(self, content, ...):
    self._ensure_collection_exists()  # Creates if missing
    # Now safe to upsert data
```

### Adding New Tools

1. Create a new `.py` file in this directory
2. Implement a `Tools` class with methods
3. Use the Open WebUI function signature:
   ```python
   def my_tool(
       self,
       param: str,
       __user__: dict = {},
       __event_emitter__: Callable[[dict], Any] = None,
   ) -> str:
   ```
4. Add docstrings (shown in UI)
5. Use `__event_emitter__` for status updates

### Event Emitter Pattern

```python
if __event_emitter__:
    __event_emitter__({
        "type": "status",
        "data": {
            "description": "Processing...",
            "done": False,
        },
    })
```

## 🔐 Security Notes

- Tools run within the Docker network (isolated)
- No external network access from tools (only internal services)
- FireCrawl API key managed via environment variables
- Qdrant has no authentication by default (internal network only)

## 🐛 Troubleshooting

**Qdrant collection errors on first use:**
- The collection is auto-created on first memory operation
- If you see "Collection not found" errors, check Qdrant service health
- Verify Qdrant is accessible: `curl http://localhost:6333/collections`
- Check logs: `docker-compose logs qdrant`

**Tool not appearing in Open WebUI:**
- Check that file is in `/app/backend/data/tools/` inside container
- Verify Python syntax (no errors)
- Restart Open WebUI container

**Connection errors:**
- Ensure all services are running: `docker-compose ps`
- Check service health: `docker-compose logs [service-name]`
- Verify services are on `rin-network`: `docker network inspect rin-network`

**Tool execution fails:**
- Check container logs: `docker-compose logs open-webui`
- Verify service URLs are correct (use service names, not localhost)
- Test service connectivity: `docker exec rin-cortex-ui ping searxng`

## 📚 References

- [Open WebUI Tools Documentation](https://docs.openwebui.com/)
- [SearXNG API](https://docs.searxng.org/)
- [FireCrawl Documentation](https://docs.firecrawl.dev/)
- [Qdrant API Reference](https://qdrant.tech/documentation/)

---

**Status**: Synaptic wiring complete. The Cortex can now control the organism's limbs. 🧠⚡
