# MAGI

**Multi-Agent General Intelligence** — A self-hosted AI agent stack.

MAGI combines Open WebUI, LiteLLM, SearXNG, Qdrant, and n8n into a unified system. It routes queries to any LLM provider, searches the web, stores long-term memory, and automates workflows—all on your infrastructure. The goal: a fully autonomous AI agent that can observe, reason, act, and learn without human intervention.

## Stack

| Component | Purpose |
|-----------|---------|
| 🧠 **Open WebUI** | Chat interface |
| 🔀 **LiteLLM** | Multi-model router (OpenRouter, OpenAI, Anthropic, local) |
| 🔍 **SearXNG** | Private web search |
| 🔥 **FireCrawl** | Web scraping |
| 💾 **Qdrant** | Vector memory (RAG) |
| ⚡ **Redis** | Message bus |
| 🔄 **n8n** | Workflow automation |
| 📓 **Jupyter Lab** | Code execution and data analysis |

## Quick Start

```bash
git clone https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-.git
cd Rhyzomic-Intelligence-Node-RIN-
./rin start
```

Open http://localhost:3000

For Jupyter Lab, open http://localhost:8888

Add API keys to `.env` and restart:
```bash
OPENROUTER_API_KEY=your_key
./rin restart
```

## Production Setup (HTTPS)

Enable automatic HTTPS with Let's Encrypt:

```bash
./rin setup-https
# Enter your domain and email
./rin start
```

Caddy automatically obtains and renews SSL certificates. No manual certificate management!

> **Port Note:** HTTPS defaults to ports 8880/8443 to avoid conflicts. Customize via `PORT_HTTP` and `PORT_HTTPS` in `.env`.

## CLI

```bash
./rin start        # Start all services
./rin stop         # Stop all services
./rin status       # Health check
./rin logs         # View logs
./rin setup-https  # Configure automatic HTTPS
./rin backup       # Backup data
./rin help         # All commands
```

## Tools (Auto-Registered)

| Tool | Purpose |
|------|---------|
| 🔍 Tavily/SearXNG | Web search |
| 🔥 FireCrawl | Web scraping |
| 💾 Qdrant | Long-term memory |
| ⚡ n8n | Workflow triggers |
| 🧠 Sequential Thinking | Chain-of-thought reasoning |
| 📺 YouTube Transcript | Video analysis |
| 📓 Jupyter Lab | Code execution with OpenRouter/pydiode integration |

## Documentation

- **[Installation](docs/INSTALLATION.md)** — Setup, prerequisites, troubleshooting
- **[CLI Reference](docs/CLI.md)** — All commands
- **[Configuration](docs/CONFIGURATION.md)** — Environment variables, service selection
- **[Tools](docs/TOOLS.md)** — Auto-registered tools, MCP Bridge
- **[Workflows](docs/WORKFLOWS.md)** — n8n automation, Python support
- **[Model Config](docs/MODEL_CONFIGURATION.md)** — LLM provider setup
- **[HTTPS Setup](docs/HTTPS_CONFIGURATION.md)** — Production TLS
- **[Jupyter Security](docs/JUPYTER_SECURITY.md)** — Production security for Jupyter Lab
- **[Architecture](docs/ARCHITECTURE.md)** — System design
- **[Roadmap](docs/ROADMAP.md)** — Future plans through v3.0

## Roadmap

- ✅ **v1.0-1.3**: Core stack, 100+ models, CLI, MCP tools, auto-registration
- 🔲 **v1.4**: Observability & monitoring
- 🔲 **v1.5**: Automated backups
- 🔲 **v1.6**: Fault tolerance
- 🔲 **v2.0**: Production dashboard
- 🔲 **v3.0**: Enterprise features

## License

See [LICENSE](LICENSE).

---

**Self-hosted AI. Your infrastructure. Your rules.** 🧠
