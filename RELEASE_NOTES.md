# RIN v1.3: "Intelligence" Release

**"Tools that think before you ask."**

We have eliminated the last layer of manual configuration. RIN v1.3 introduces **Auto-Registration**, ensuring that your biological sensors (Search, Scraping, Memory) are wired to the brain immediately upon boot.

---

## 🌟 New Features

### 1. Auto-Registered Tooling

- **Problem**: In v1.2, tools were mounted but invisible until manually imported via the UI.
- **Solution**: The new `register_tools.py` injector scans your `tools/` directory and hot-wires them directly into the Cortex's synapse database.
- **Result**: Tavily Search, FireCrawl, SearXNG, Qdrant Memory, and n8n Reflex appear in your chat interface **instantly on first launch**.

### 2. Environment-Driven Configuration ("Smart Valves")

- **Security**: API keys for tools (e.g., `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`) are now injected from your `.env` file directly into the tool's logic via Pydantic Valves.
- **Zero-Touch**: No more copying and pasting keys into the UI. If the environment variable exists, the tool is authenticated.

### 3. Expanded Sensorium

- **Tavily Search**: Added as a native "Premium" alternative to SearXNG for users requiring higher-reliability citations and AI-optimized results.
- **Smart Fallbacks**: Tools now gracefully degrade (providing helpful error messages) if keys are missing, rather than crashing the conversation.

---

## 🐛 Bug Fixes

- **INC-009**: Fixed LiteLLM crash loop caused by phantom PostgreSQL configuration (`database_url` in config.yaml).
- **Tool Visibility**: Fixed tools not appearing in Open WebUI despite correct volume mounts.
- **n8n Permissions**: Fixed permission errors on fresh Linux deployments.

---

## ⚡ Upgrade Instructions (from v1.2)

```bash
# 1. Pull latest code
git pull origin main

# 2. Update your .env (Add Tavily if desired)
nano .env
# Add: TAVILY_API_KEY=tvly-your-key-here

# 3. Re-Ignite (Triggers the new registration script)
./start.sh
```

Your tools will be automatically registered and ready to use.

---

## 🔧 Technical Notes

### SQLite Constraint (Technical Debt)

The `register_tools.py` script currently uses direct SQLite injection to bypass the API authentication requirement. This is intentional for the Zero-Config architecture.

**Future Migration Path (v1.4 Enterprise)**:
- When scaling to 20+ users with PostgreSQL, this script will need refactoring.
- Planned: Check for `DATABASE_URL` and use SQLAlchemy/Prisma instead of raw `sqlite3` calls.

---

## 📦 What's Included

### Auto-Registered Tools (5 Total)

| Tool | Functions | Purpose |
|------|-----------|---------|
| **FireCrawl Scraper** | `scrape_webpage`, `crawl_website` | Web scraping with headless browser |
| **Tavily Search** | `web_search`, `quick_search`, `deep_search` | AI-optimized premium search |
| **SearXNG Search** | `web_search` | Anonymous metasearch |
| **Qdrant Memory** | `store_memory`, `recall_memory` | Long-term RAG memory |
| **n8n Reflex** | `trigger_workflow`, `list_workflows` | Workflow automation triggers |

---

## 🎯 Version History

| Version | Codename | Focus |
|---------|----------|-------|
| v1.0 | Genesis | Initial release, biological architecture |
| v1.1 | Expansion | OpenRouter integration, model marketplace |
| v1.2 | Zero-Config | Atomic deployment, infrastructure automation |
| **v1.3** | **Intelligence** | **Auto-registration, smart tooling** |

---

**RIN v1.3 "Intelligence"** - The sovereign AI organism is now fully autonomous. Zero-config. Zero-friction. Complete control. 🧠⚡

---
---

# RIN v1.0: "Genesis" Release

**"The Intelligence of GPT-4. The Privacy of a Faraday Cage."**

We are proud to announce the first stable release of the Rhyzomic Intelligence Node (RIN). This release marks the transition from experimental framework to a fully autonomous, self-hosted AI agent system.

## 🌟 Top Features

### 1. Zero-Config "Atomic" Deployment

Forget manual configuration. RIN v1.0 features a Self-Generating Nervous System.

- **Auto-Cryptography**: The `start.sh` bootloader automatically generates high-entropy internal secrets for SearXNG, FireCrawl, and LiteLLM.
- **Infrastructure Repair**: Automatically fixes Docker DNS issues (Azure/Cloud) and volume permissions (Linux) on boot.
- **Command**: `git clone ... && ./start.sh`. That's it.

### 2. The Biological Architecture

RIN is not a chatbot; it is an organism composed of five specialized subsystems:

- **🧠 Cortex (Open WebUI + LiteLLM)**: A unified interface that routes "thoughts" to the best model (GPT-4o, Claude 3.5, Local Llama 3) based on cost and capability.
- **👁️ Sensorium (SearXNG + FireCrawl)**: Anonymous, privacy-respecting web search and a headless browser that digests complex JavaScript sites into clean Markdown.
- **💾 Memory (Qdrant)**: A Vector Database enabling RAG (Retrieval Augmented Generation). RIN remembers facts, summaries, and context from months ago.
- **⚡ Nervous System (Redis)**: A high-speed message bus coordinating the sensorium's asynchronous tasks.
- **🔄 Reflex (n8n)**: An automation engine that allows RIN to wake up on a schedule (Cron), check the world, and trigger actions without human input.

### 3. "Day 1" Autonomy

RIN v1.0 ships with survival instincts pre-installed.

- **Morning Briefing Protocol**: A pre-configured n8n workflow that wakes up at 8:00 AM, searches for global tech news, synthesizes a briefing using GPT-4o, and delivers it to the user.
- **Synaptic Bridges**: Python tools (`tools/n8n_reflex.py`) allow the Chat Interface to trigger complex automation workflows via Webhooks.

## 🔒 Sovereignty & Privacy

- **Zero-Trust Networking**: All services bind strictly to 127.0.0.1. No ports are exposed to the public internet. Access is designed for Tailscale or SSH Tunnels.
- **Data Ownership**: All chat history, vector memory, and scraping logs are stored in `./data` on your local disk.
- **Anonymous Vision**: Web searches are proxied through SearXNG, stripping your IP address and tracking cookies before they reach Google/Bing.

## 📦 Installation

```bash
# 1. Clone
git clone https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-.git
cd Rhyzomic-Intelligence-Node-RIN-

# 2. Ignite (Auto-configures keys, DNS, and containers)
chmod +x start.sh
./start.sh

# 3. Access
# Cortex: http://localhost:3000
# Reflex: http://localhost:5678
```

## 🎯 What's Included

### Pre-configured Services
- **Open WebUI** (Port 3000) - Unified AI interface
- **n8n** (Port 5678) - Workflow automation
- **SearXNG** (Port 8080) - Privacy-respecting search
- **LiteLLM** (Port 4000) - Multi-model API gateway
- **FireCrawl** (Port 3002) - Web scraping engine
- **Qdrant** (Port 6333) - Vector database
- **Redis** (Port 6379) - Message bus

### Pre-configured Tools
- **SearXNG Search** - Anonymous web search
- **FireCrawl Scraper** - JavaScript-heavy site extraction
- **Qdrant Memory** - RAG-enabled recall
- **n8n Reflex** - Autonomous workflow triggering

### Pre-configured Workflows
- **Morning Briefing** - Daily 8 AM tech news summary

## 🚀 Quick Start Guide

1. **Deploy**: Run `./start.sh` to launch all services
2. **Configure** (Optional): Edit `.env` to add your OpenAI/Anthropic API keys
3. **Import Workflow**: Access n8n at http://localhost:5678, import `workflows/morning_briefing.json`
4. **Start Using**: Open http://localhost:3000 to interact with RIN

## 📚 Documentation

- **README.md** - Complete system overview and usage guide
- **DESIGN.md** - Architectural deep-dive
- **workflows/README.md** - Workflow automation guide
- **tools/README.md** - Tool development guide

## 🔧 System Requirements

- **Docker** - Automatically installed by `start.sh` if missing
- **8GB RAM** minimum (16GB recommended)
- **10GB disk space** for containers and data
- **Linux/macOS/Windows** (WSL2)

## 🎓 Key Concepts

### Atomic Deployment
RIN deploys as a single unit. One command (`./start.sh`) generates all secrets, configures all services, and launches the entire organism.

### Biological Design
Each subsystem has a specialized role (Cortex, Sensorium, Memory, Nervous System, Reflex), working together as a unified organism.

### Sovereign Architecture
All data stays on your infrastructure. No cloud dependencies. No tracking. Complete control.

### Zero-Config Philosophy
The system "knows" how to configure itself. Users only provide optional API keys for external LLM providers.

## 🐛 Known Limitations

- **Manual workflow import**: The Morning Briefing workflow requires manual import into n8n (one-time setup).
- **Local-only access**: All services bind to localhost. Remote access requires SSH tunneling or VPN (Tailscale recommended).

## 🔮 What's Next (v1.1+)

- **OpenRouter Integration**: Extended LiteLLM configuration with model selection, temperature control, and cost optimization
- **Automated Workflow Loading**: Pre-load workflows into n8n on first boot
- **Health Dashboard**: Real-time monitoring of all subsystems
- **SQLite Cost Tracking**: Lightweight logging for LiteLLM usage and costs
- **Additional Workflows**: Email integration, RSS monitoring, GitHub notifications

## 🙏 Credits

RIN integrates the following open-source projects:
- **Open WebUI** - Unified AI interface
- **n8n** - Workflow automation
- **SearXNG** - Privacy-respecting metasearch
- **LiteLLM** - Multi-model API gateway
- **FireCrawl** - Web scraping
- **Qdrant** - Vector database
- **Redis** - Message bus

## 📄 License

See [LICENSE](LICENSE) for details.

---

**RIN v1.0 "Genesis"** - The first sovereign AI organism. Built for digital sovereignty. Run by you, for you. 🧠🔄👁️
