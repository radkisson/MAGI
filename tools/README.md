# RIN Synaptic Wiring: Tool Definitions

This directory contains the **"nerve endings"** that connect the Cortex (Open WebUI) to the other biological subsystems of RIN. These tools enable Open WebUI to control and utilize the Sensorium, Memory, and Nervous System.

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

### 2. FireCrawl Scraper (`firecrawl_scraper.py`)
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

### 3. Qdrant Memory (`qdrant_memory.py`)
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

## 🔌 Installation in Open WebUI

### Method 1: Manual Installation

1. Copy the tool files to Open WebUI's tools directory:
   ```bash
   docker cp tools/searxng_search.py rin-cortex-ui:/app/backend/data/tools/
   docker cp tools/firecrawl_scraper.py rin-cortex-ui:/app/backend/data/tools/
   docker cp tools/qdrant_memory.py rin-cortex-ui:/app/backend/data/tools/
   ```

2. Restart Open WebUI:
   ```bash
   docker-compose restart open-webui
   ```

3. Tools will appear in Open WebUI's Tools section

### Method 2: Volume Mount (Recommended)

Update `docker-compose.yml` to mount the tools directory:

```yaml
open-webui:
  image: ghcr.io/open-webui/open-webui:latest
  volumes:
    - open-webui-data:/app/backend/data
    - ./tools:/app/backend/data/tools  # Add this line
```

Then restart:
```bash
docker-compose down && docker-compose up -d
```

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
