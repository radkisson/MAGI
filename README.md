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
| 🔄 **n8n** | Workflow automation (custom build with latest stable n8n 2.1.4) |
| 📓 **Jupyter Lab** | Code execution and data analysis |

> **Note**: n8n uses a custom Docker image built on the official n8nio/n8n:latest base, with an nginx proxy for improved frontend/backend separation. See [docker/n8n/SETUP.md](docker/n8n/SETUP.md) for configuration details.

## Quick Start

```bash
git clone https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-.git
cd Rhyzomic-Intelligence-Node-RIN-
./magi start
```

Open http://localhost:3000

For n8n automation, open http://localhost:8081 (recommended proxy) or http://localhost:5678 (direct backend)

For Jupyter Lab, open http://localhost:8888

Add API keys to `.env` and restart:
```bash
OPENROUTER_API_KEY=your_key
./magi restart
```

## Production Setup (HTTPS)

**Option 1: Let's Encrypt (Public Domain)**

```bash
./magi setup-https
# Enter your domain and email
./magi start
```

Caddy automatically obtains and renews SSL certificates.

**Option 2: Tailscale (Private Network)**

```bash
./magi setup-tailscale-https
```

Access via `https://your-machine.ts.net/` — no public ports required.

> **Port Note:** Let's Encrypt defaults to ports 8880/8443. Customize via `PORT_HTTP` and `PORT_HTTPS` in `.env`.

## CLI

```bash
./magi start        # Start all services
./magi stop         # Stop all services
./magi status       # Health check
./magi logs         # View logs
./magi setup-https  # Configure automatic HTTPS
./magi backup       # Backup data
./magi help         # All commands
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
