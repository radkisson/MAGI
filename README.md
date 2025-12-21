# Rhyzomic Intelligence Node (RIN)

**Version**: 1.2.0 (Stable)  
**Status**: Active Development  
**Classification**: Sovereign AI Infrastructure

## Overview

Commercial AI models (ChatGPT, Claude) are "Brains in a Jar"—intelligent but disconnected, censored, and reliant on their creators for input. RIN is a sovereign, self-hosted entity. It treats commercial APIs merely as "compute," while retaining its own memory, eyes, and agency on your infrastructure.

Rhyzomic Intelligence Node (RIN) is an autonomous, self-hosted AI agent system designed to operate independently of centralized commercial control. It is not merely a chatbot, but a **sovereign organism** composed of biological subsystems:

- 🧠 **The Cortex** (cognition) - Open WebUI + LiteLLM
- 👁️ **The Sensorium** (perception) - SearXNG + FireCrawl
- 💾 **The Memory** (recall) - Qdrant Vector Database
- ⚡ **The Nervous System** (reflex) - Redis Message Bus
- 🔄 **The Reflex Arc** (autonomy) - n8n Workflow Automation

## System Architecture

RIN functions as a single organism via Docker orchestration, with each subsystem playing a vital role:

### The Cortex (Cognition)
- **Open WebUI**: Unified interface for human-agent interaction
- **LiteLLM**: Intelligent API router for multi-model orchestration (GPT-4o, Claude 3.5, Llama 3)

### The Sensorium (Perception)
- **SearXNG**: Privacy-respecting metasearch engine for anonymous web vision
- **FireCrawl**: Specialized scraping array for complex JavaScript sites

### The Memory (Recall)
- **Qdrant**: Vector database enabling RAG for long-term semantic recall

### The Nervous System (Reflex)
- **Redis**: High-speed message bus coordinating asynchronous tasks

### The Reflex Arc (Autonomy)
- **n8n**: Workflow automation enabling scheduled tasks and external integrations
- **Capabilities**: Email, Telegram, Slack integration without cloud dependencies
- **Synaptic Bridges**: Webhooks connecting Cortex ↔ Reflex for autonomous actions

## Key Features

- **Sovereign Architecture**: Complete control over your AI infrastructure
- **Privacy-First**: Anonymous web search via SearXNG, no data leakage
- **Multi-Model Intelligence**: Route tasks to optimal LLM providers via LiteLLM
- **OpenRouter Integration**: Access 20+ models from one unified API (GPT-4, Claude, Llama, Gemini, Mistral, and more)
- **Cost Tracking**: Monitor spending across all models with built-in budgeting
- **Fallback Chains**: Automatic failover to backup models for 99.9% reliability
- **Persistent Memory**: RAG-enabled recall via Qdrant vector storage
- **Asynchronous Coordination**: Redis-powered task queuing and execution
- **Biological Design**: Five subsystems working as a unified organism

## Quick Start

### Prerequisites

- Docker (automatically installed by start.sh if missing)
- API keys for LLM providers (OpenAI, Anthropic) - Optional, can be added later

### Installation (3 Steps)

**1. Clone the Organism**
```bash
git clone https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-.git
cd Rhyzomic-Intelligence-Node-RIN-
```

**2. Ignite**
```bash
chmod +x start.sh
./start.sh
```

This automatically:
- Generates all secure internal keys (you never need to see these)
- Creates the required directory structure
- Fixes permissions for Redis/Qdrant (critical on Linux/Azure)
- Configures Docker DNS for cloud environments
- Starts all containers

**3. Connect (Optional)**

If you have an OpenAI/Anthropic API key:
- Open `.env` and add your keys
- Run `./start.sh` again to apply

Then open http://localhost:3000 to access the Cortex.

### Troubleshooting

#### Port Already Allocated Error

If you encounter an error like `"Bind for 0.0.0.0:3000 failed: port is already allocated"`, this means one of the default ports is already in use on your system.

**Solution**: Edit the `.env` file and change the conflicting port(s):

```bash
nano .env
```

Available port configurations:
- `PORT_WEBUI=3000` - Open WebUI (Cortex) - Main interface
- `PORT_LITELLM=4000` - LiteLLM (Router) - AI model routing
- `PORT_SEARXNG=8080` - SearXNG (Vision) - Search engine
- `PORT_FIRECRAWL=3002` - FireCrawl (Digestion) - Web scraping
- `PORT_N8N=5678` - n8n (Reflex) - Workflow automation
- `PORT_QDRANT=6333` - Qdrant (Memory) - Vector database

For example, if port 3000 is in use, change `PORT_WEBUI=3000` to `PORT_WEBUI=3001`.

After making changes, restart RIN:
```bash
./start.sh
```

The start script will display the actual ports being used.

#### n8n Secure Cookie Warning

If you see a warning about n8n's secure cookie configuration when accessing http://localhost:5678, this is expected for local development over HTTP.

**Already Fixed**: The `docker-compose.yml` is configured with `N8N_SECURE_COOKIE=false` to disable this security feature for local HTTP development.

**Note**: If deploying to production with HTTPS/TLS, you should remove this setting to enable secure cookies for better security.

### Service Access Points

Once deployed, access the various subsystems:

- **Open WebUI (Cortex)**: http://localhost:3000
- **n8n (Reflex/Automation)**: http://localhost:5678
- **LiteLLM API**: http://localhost:4000
- **SearXNG (Search)**: http://localhost:8080
- **FireCrawl API**: http://localhost:3002
- **Qdrant (Vector DB)**: http://localhost:6333
- **Redis**: localhost:6379

### Synaptic Wiring (Tool Definitions)

RIN includes **tool definitions** that connect the Cortex (Open WebUI) to the other subsystems. These act as "nerve endings" allowing the brain to control the body:

**Available Tools:**
- 🔍 **SearXNG Search** - Anonymous web search via the Sensorium's Vision
- 🔥 **FireCrawl Scraper** - Extract content from JavaScript-heavy websites
- 💾 **Qdrant Memory** - Store and recall information with RAG
- 🔄 **n8n Reflex** - Trigger autonomous workflows and external integrations

The tools are automatically mounted into Open WebUI and appear in the Tools section. See [`tools/README.md`](tools/README.md) for detailed documentation.

**Usage Example:**
```
User: "Search for the latest AI research papers and summarize them"
RIN: [Uses SearXNG tool to search anonymously]
     [Uses FireCrawl tool to scrape paper pages]
     [Stores summaries in Qdrant memory]
     [Generates comprehensive answer]
```

### Autonomous Workflows (n8n)

RIN comes with a **pre-configured Morning Briefing workflow** that runs autonomously at 8 AM daily. This is RIN's first "survival instinct" - waking up and checking the world without human intervention.

#### Importing the Morning Briefing Workflow

1. **Access n8n**: After running `./start.sh`, open http://localhost:5678
2. **Create Account**: First-time setup will prompt you to create an owner account
3. **Import Workflow**:
   - Click "Add workflow" (+ button)
   - Click the three dots menu (⋮) → "Import from File"
   - Select `workflows/morning_briefing.json`
4. **Activate**: Toggle the workflow to "Active" in the top-right corner

The workflow will now:
- Trigger at 8:00 AM daily
- Query SearXNG for "top technology news today"
- Send results to LiteLLM for summarization
- Generate a 3-bullet morning briefing

#### Creating Custom Workflows

You can create your own workflows in the n8n visual editor:

1. Use **Webhook** triggers to allow Open WebUI to trigger workflows
2. Use **HTTP Request** nodes to connect to RIN services:
   - `http://rin-cortex:8080` - Open WebUI API
   - `http://rin-router:4000` - LiteLLM for AI processing
   - `http://rin-vision:8080` - SearXNG for web search
   - `http://rin-memory:6333` - Qdrant for vector storage
3. Export your workflows as JSON to the `workflows/` directory

See [`workflows/README.md`](workflows/README.md) for detailed architecture and examples.

### Managing the Organism

```bash
# Start all subsystems
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all subsystems
docker-compose down

# Restart a specific subsystem
docker-compose restart open-webui

# Check health status
docker-compose ps
```

## Architecture

RIN functions as a biological organism with specialized subsystems:

### The Cortex (Cognition)
- **Open WebUI**: Human-agent interaction interface
- **LiteLLM**: Multi-model routing (GPT-4o for logic, Claude for coding, Llama for privacy)

### The Sensorium (Perception)
- **SearXNG**: Privacy-preserving metasearch for anonymous web vision
- **FireCrawl**: Headless browser for complex JavaScript site scraping

### The Memory (Recall)
- **Qdrant**: Vector database for RAG-enabled long-term semantic recall

### The Nervous System (Reflex)
- **Redis**: Asynchronous task coordination and message bus

See [DESIGN.md](DESIGN.md) for detailed architecture documentation.

## Project Structure

```
rin/
├── docker-compose.yml          # Orchestration of all subsystems
├── .env.example                # Environment configuration template
├── DESIGN.md                   # Detailed architecture documentation
├── src/rin/                    # Python integration code (legacy framework)
│   ├── core/                   # Agent orchestration
│   ├── sensors/                # Sensor framework
│   ├── memory/                 # Memory framework
│   ├── reflexes/               # Reflex framework
│   └── utils/                  # Shared utilities
├── tests/                      # Test suite
├── docs/                       # Documentation
└── examples/                   # Usage examples
```

## Configuration

RIN is configured via environment variables in `.env`:

```bash
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Optional: Local Ollama
OLLAMA_API_BASE=http://host.docker.internal:11434

# LiteLLM Configuration
LITELLM_MASTER_KEY=your_secure_key

# SearXNG Configuration
SEARXNG_SECRET=your_secret_key

# FireCrawl Configuration
FIRECRAWL_API_KEY=your_firecrawl_key

# Web UI Authentication (optional)
WEBUI_AUTH=false
```

## Usage Examples

### Interacting with RIN

1. **Access Open WebUI** at http://localhost:3000
2. **Start a conversation** with the Cortex
3. **Ask questions** - RIN will use SearXNG to search privately
4. **Request detailed information** - FireCrawl will scrape and extract content
5. **Build context** - Qdrant stores all interactions for future recall
6. **Switch models** - LiteLLM routes to the best model for your task

### Example Workflows

**Privacy-Preserving Research:**
```
You: "Search for recent developments in quantum computing"
RIN: [Uses SearXNG to search anonymously]
     [Scrapes relevant pages with FireCrawl]
     [Stores findings in Qdrant]
     [Synthesizes comprehensive answer]
```

**Multi-Model Reasoning:**
```
You: "Write a Python script to analyze this data, then explain the logic"
RIN: [Routes coding to Claude 3.5]
     [Routes explanation to GPT-4o]
     [Stores script in Qdrant for future reference]
```

**Long-Term Memory:**
```
You: "Remember we discussed quantum computing last week"
RIN: [Queries Qdrant vector database]
     [Retrieves semantic context via RAG]
     [Responds with relevant past context]
```

## Development

### Python Framework (Legacy)

The `src/rin/` directory contains a Python framework that can be used for custom integrations:

```python
from rin import Agent

# Initialize the agent (uses local framework)
agent = Agent()

# Send a query
response = agent.query("What are the latest developments in AI?")
print(response)
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/test_sensors.py

# Run with coverage
pytest --cov=rin tests/
```

### Code Style

```bash
# Format code
black src/rin

# Lint code
flake8 src/rin
pylint src/rin
```

## Contributing

Contributions are welcome! Please read our contributing guidelines and submit pull requests.

Areas of focus:
- Docker Compose orchestration improvements
- Custom Open WebUI tools and plugins
- LiteLLM routing configurations
- Qdrant schema optimization
- SearXNG and FireCrawl integrations
- Documentation and examples
- Testing coverage

## Roadmap

### Completed
- [x] **v1.0 "Genesis"**: Foundation and architecture design ✅
  - [x] Zero-config atomic deployment with `start.sh`
  - [x] Auto-generated internal secrets (LITELLM, SEARXNG, FIRECRAWL)
  - [x] Docker Compose orchestration with bind mounts
  - [x] The Cortex (Open WebUI + LiteLLM integration)
  - [x] The Sensorium (SearXNG + FireCrawl deployment)
  - [x] The Memory (Qdrant RAG implementation)
  - [x] The Nervous System (Redis coordination)
  - [x] The Reflex Arc (n8n automation)
  - [x] Pre-configured Morning Briefing workflow
  - [x] Synaptic bridge tools (n8n_reflex.py)

- [x] **v1.1 "Expansion"**: Enhanced Model Support ✅
  - [x] OpenRouter integration with full model marketplace access (20+ models)
  - [x] Advanced LiteLLM configuration (temperature, top_p, max_tokens)
  - [x] Model selection UI in Open WebUI (automatic model discovery)
  - [x] Per-model cost tracking and budgeting (SQLite database)
  - [x] Fallback model chains for reliability (multi-provider redundancy)
  - [x] Comprehensive [Model Configuration Guide](docs/MODEL_CONFIGURATION.md)

### Planned
- [ ] **v1.2 "Intelligence"**: Advanced Automation
  - [ ] Auto-load workflows into n8n on first boot
  - [ ] Email integration workflow (Gmail, SMTP)
  - [ ] RSS feed monitoring and summarization
  - [ ] GitHub notifications and PR summaries
  - [ ] Slack/Telegram bot integration
  
- [ ] **v1.3 "Observability"**: Monitoring & Logging
  - [ ] Real-time health dashboard
  - [ ] Usage analytics and insights
  - [ ] Performance metrics (latency, token usage)
  - [ ] Workflow execution history in n8n
  - [ ] Advanced cost analytics and reporting
  
- [ ] **v1.4 "Resilience"**: Production Hardening
  - [ ] Automated backups for vector database and chat history
  - [ ] Health checks and auto-restart for failed services
  - [ ] Rate limiting and quota management
  - [ ] Multi-user authentication and access control
  
- [ ] **v2.0 "Evolution"**: Advanced Capabilities
  - [ ] Voice interface (Whisper integration)
  - [ ] Image generation (Stable Diffusion)
  - [ ] Code execution sandbox
  - [ ] Multi-agent orchestration
  - [ ] Custom model fine-tuning pipeline

## Philosophy

RIN embodies digital sovereignty as a **biological organism**. It's not about replacing commercial AI—it's about reclaiming agency. By hosting your own intelligence node, you maintain:

- **Control**: Over the entire organism and its data
- **Privacy**: Anonymous perception via SearXNG, no external tracking
- **Flexibility**: Multi-model routing via LiteLLM (GPT-4o, Claude, Llama)
- **Memory**: Long-term RAG-enabled recall via Qdrant
- **Transparency**: Full visibility into all subsystems
- **Independence**: Not reliant on any single provider
- **Coordination**: Asynchronous task execution via Redis

RIN is a complete organism, not just a tool. Each subsystem plays a vital role in creating sovereign AI infrastructure.

## License

See [LICENSE](LICENSE) for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/issues)
- **Discussions**: [GitHub Discussions](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/discussions)

---

**Built for digital sovereignty. A living organism, run by you, for you.** 🧠👁️💾⚡
