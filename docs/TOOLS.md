# Tools Reference

MAGI includes pre-configured tools that auto-register on startup.

## Auto-Registered Tools

| Tool | Functions | Purpose |
|------|-----------|---------|
| 🔥 **FireCrawl** | `scrape_webpage`, `crawl_website` | Web scraping with headless browser |
| 🔍 **Tavily** | `web_search`, `quick_search`, `deep_search` | AI-optimized web search |
| 👁️ **SearXNG** | `web_search` | Anonymous metasearch |
| 💾 **Qdrant** | `store_memory`, `recall_memory` | Long-term RAG memory |
| ⚡ **n8n** | `trigger_workflow`, `list_workflows` | Workflow automation |

View tools: **Workspace → Tools** in Open WebUI.

## MCP Bridge Tools

### Sequential Thinking

Forces chain-of-thought reasoning for complex queries.

**Connect to Open WebUI:**
1. Go to **Settings → Tool Servers**
2. Add URL: `http://mcp-bridge:9000/openapi.json`
3. Click Load, then Activate

**Usage:**
```
"Use sequential thinking to analyze how we could colonize Mars step by step."
```

### YouTube Transcript

Extracts and analyzes video transcripts.

**Connect:**
1. Go to **Settings → Tool Servers**
2. Add URL: `http://youtube-mcp:9001/openapi.json`
3. Click Load, then Activate

**Usage:**
```
"Summarize this video: https://www.youtube.com/watch?v=..."
```

## Tool Configuration

Tools auto-authenticate via environment variables in `.env`:

```bash
TAVILY_API_KEY=tvly-your-key
FIRECRAWL_API_KEY=fc-your-key  # Auto-generated for self-hosted
```

After adding keys, restart: `./rin restart`
