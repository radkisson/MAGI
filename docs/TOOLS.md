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
| 📓 **Jupyter Lab** | Code execution, data analysis | Interactive Python notebooks with AI integration |

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

### Jupyter Lab

Interactive Python notebooks for code execution, data analysis, and AI model interaction.

**Access:**
- Open `http://localhost:8888` in your browser (or port configured via `PORT_JUPYTER`)
- No authentication required by default (can be configured)
- HTTPS supported when enabled

**Features:**
- Full scipy stack (NumPy, Pandas, Matplotlib, SciPy)
- OpenRouter integration via `OPENROUTER_API_KEY` environment variable
- Direct LiteLLM access at `http://litellm:4000`
- pydiode for AI-assisted code execution
- Pre-installed example notebook: `Welcome_to_MAGI.ipynb`

**Usage:**
```python
# In a Jupyter notebook
import os
import requests

# Use OpenRouter
api_key = os.environ.get('OPENROUTER_API_KEY')
response = requests.post(
    'https://openrouter.ai/api/v1/chat/completions',
    headers={'Authorization': f'Bearer {api_key}'},
    json={'model': 'openai/gpt-4o', 'messages': [{'role': 'user', 'content': 'Hello!'}]}
)
```

## Tool Configuration

Tools auto-authenticate via environment variables in `.env`:

```bash
TAVILY_API_KEY=tvly-your-key
FIRECRAWL_API_KEY=fc-your-key  # Auto-generated for self-hosted
```

After adding keys, restart: `./rin restart`
