# Rhyzomic Intelligence Node (RIN)

**Version**: 1.3.0 (Stable)  
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
- **Dynamic Model Loading**: Automatically sync latest models from OpenRouter API (100+ models)
- **OpenRouter Integration**: Access 100+ models from one unified API (GPT-4, Claude, Llama, Gemini, Mistral, and more)
- **Model Intelligence**: Popularity rankings, cost metadata, and automatic recommendations
- **Cost Tracking**: Monitor spending across all models with built-in budgeting
- **Fallback Chains**: Automatic failover to backup models for 99.9% reliability
- **Persistent Memory**: RAG-enabled recall via Qdrant vector storage
- **Asynchronous Coordination**: Redis-powered task queuing and execution
- **Biological Design**: Five subsystems working as a unified organism
- **Comprehensive CLI**: Complete system management via `./rin` command
- **Auto-Registration**: Tools auto-authenticate and appear instantly in UI
- **MCP Bridge**: Model Context Protocol tools for advanced reasoning
- **Workflow Automation**: 8 pre-configured n8n workflows for autonomous operations

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
chmod +x rin start.sh
./rin start
```

Or use the classic method:
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
- Run `./rin start` or `./start.sh` again to apply

Then open http://localhost:3000 to access the Cortex.

### Included Tools (Auto-Registered)

RIN comes with 5 pre-configured tools that are automatically registered on startup:

| Tool | Functions | Purpose |
|------|-----------|---------|
| 🔥 **FireCrawl Scraper** | `scrape_webpage`, `crawl_website` | Web scraping with headless browser |
| 🔍 **Tavily Search** | `web_search`, `quick_search`, `deep_search` | AI-optimized web search |
| 👁️ **SearXNG Search** | `web_search` | Anonymous metasearch |
| 💾 **Qdrant Memory** | `store_memory`, `recall_memory` | Long-term RAG memory |
| ⚡ **n8n Reflex** | `trigger_workflow`, `list_workflows` | Workflow automation |

View and configure tools: **Workspace → Tools** in the UI.

### CLI Management

RIN includes a comprehensive CLI tool (`./rin`) for managing the entire system:

```bash
./rin start      # Start all services
./rin stop       # Stop all services
./rin status     # Check system health
./rin logs       # View logs
./rin update     # Pull latest images
./rin upgrade    # Upgrade RIN
./rin backup     # Backup your data
./rin help       # Show all commands
```

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
- `PORT_MCP_BRIDGE=9000` - MCP Bridge (Sequential Thinking) - Model Context Protocol bridge
- `PORT_YOUTUBE_MCP=9001` - YouTube MCP (YouTube Transcript) - Video subtitle extraction

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
- **MCP Bridge (Sequential Thinking)**: http://localhost:9000
- **YouTube MCP (YouTube Transcript)**: http://localhost:9001
- **Redis**: localhost:6379

### Synaptic Wiring (Tool Definitions)

RIN includes **tool definitions** that connect the Cortex (Open WebUI) to the other subsystems. These act as "nerve endings" allowing the brain to control the body:

**Available Tools:**
- 🔍 **SearXNG Search** - Anonymous web search via the Sensorium's Vision
- 🔍 **Tavily Search** - AI-optimized web search (premium alternative/complement to SearXNG)
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

### MCP Bridge (Model Context Protocol)

RIN includes an **MCP Bridge** that connects Model Context Protocol (MCP) tools to Open WebUI. The bridge translates MCP tools into OpenAPI format that Open WebUI can understand.

For detailed setup instructions, troubleshooting, and advanced usage, see the **[MCP Tools Guide](docs/MCP_TOOLS.md)**.

**Available MCP Tools:**

#### 1. Sequential Thinking Tool

The Sequential Thinking tool is included by default. It forces the AI to use a "Chain of Thought" approach, resulting in deeper, more methodical reasoning for complex queries.

**How it works:**
1. The AI calls the tool with `thoughtNumber: 1` ("First, we need to solve transport...")
2. The tool replies "Ack"
3. The AI calls the tool again with `thoughtNumber: 2` ("Next, we need life support...")
4. This creates a "Chain of Thought" loop that results in much smarter, deeper answers

**Connecting to Open WebUI:**

1. Go to **Settings → Tool Servers** (Admin Settings)
2. In the URL field, type: `http://mcp-bridge:9000/openapi.json`
   - Use `mcp-bridge` as the hostname (same Docker network)
   - If that fails, try: `http://host.docker.internal:9000/openapi.json`
   - On Linux, you may need to use: `http://localhost:9000/openapi.json`
3. Click the **Download/Load** button (Cloud icon)
4. **Activate** the tool (toggle the switch)

**Usage Example:**
```
User: "Use the sequential thinking tool to analyze exactly how we could colonize Mars, step by step."
RIN: [Calls Sequential Thinking tool iteratively]
     [Generates step-by-step breakdown]
     [Provides comprehensive, well-reasoned answer]
```

**Note:** The bridge uses the official `@modelcontextprotocol/server-sequential-thinking` package maintained by the protocol creators for maximum stability.

#### 2. YouTube Transcript Tool

The YouTube Transcript tool allows the AI to "watch" videos by reading their subtitle/caption data. This enables video analysis and summarization without actually playing the video.

**How it works:**
- The tool extracts subtitle/transcript data from YouTube videos
- The AI can then analyze, summarize, or search the content
- Works with any YouTube video that has captions (automatic or manual)

**Connecting to Open WebUI:**

1. Go to **Settings → Tool Servers** (Admin Settings)
2. In the URL field, type: `http://youtube-mcp:9001/openapi.json`
   - Use `youtube-mcp` as the hostname (same Docker network)
   - If that fails, try: `http://host.docker.internal:9001/openapi.json`
   - On Linux, you may need to use: `http://localhost:9001/openapi.json`
3. Click the **Download/Load** button (Cloud icon)
4. **Activate** the tool (toggle the switch)

**Usage Examples:**
```
User: "Summarize this video for me: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
RIN: [Retrieves video transcript]
     [Analyzes content]
     [Provides comprehensive summary]

User: "Find the exact timestamp in this video where they talk about 'Docker': https://www.youtube.com/watch?v=..."
RIN: [Searches transcript for keyword]
     [Identifies relevant timestamps]
     [Provides specific time markers with context]
```

**Technical Note:** This service uses a Python base image with Node.js installed to run the NPM-based `@sinco-lab/mcp-youtube-transcript` tool via the mcpo bridge.

### Autonomous Workflows (n8n)

RIN includes **8 pre-configured workflow templates** that enable autonomous operations and external integrations. These workflows give RIN the ability to send emails, post to Slack/Telegram, monitor RSS feeds, conduct research, and generate daily reports.

#### Available Workflow Templates

1. **Morning Briefing** - Daily news summary at 8 AM
2. **OpenWebUI Integration** - General-purpose webhook receiver for Open WebUI
3. **Email Integration** - Send emails via SMTP (Gmail, custom servers)
4. **Slack Notifications** - Post messages to Slack channels
5. **Telegram Notifications** - Send messages via Telegram bot
6. **RSS Feed Monitor** - Monitor and summarize RSS feeds every 6 hours
7. **Research Agent** - Autonomous research with search, scraping, and synthesis
8. **Daily Report Generator** - Comprehensive intelligence reports at 6 PM daily

#### Quick Start

1. **Access n8n**: After running `./start.sh`, open http://localhost:5678
2. **Create Account**: First-time setup will prompt you to create an owner account
3. **Import Workflows**:
   - Click "Add workflow" (+ button)
   - Click the three dots menu (⋮) → "Import from File"
   - Select any workflow from `workflows/` directory (e.g., `morning_briefing.json`)
4. **Configure Credentials** (for email/Slack/Telegram workflows):
   - Settings → Credentials → Create New
   - Add SMTP, Slack API, or Telegram API credentials as needed
5. **Activate**: Toggle the workflow to "Active" in the top-right corner

#### Using Workflows from Open WebUI

Once workflows are activated, you can trigger them naturally in conversation:

```
You: "Send an email to team@company.com with today's briefing"
You: "Post a message to Slack saying 'Deployment complete'"
You: "Research quantum computing and send me a comprehensive report"
```

RIN will automatically use the n8n_reflex tool to trigger the appropriate workflows.

#### Documentation

For detailed setup instructions, see:
- [`workflows/INSTALLATION_GUIDE.md`](workflows/INSTALLATION_GUIDE.md) - Step-by-step setup for each workflow
- [`workflows/USAGE_GUIDE.md`](workflows/USAGE_GUIDE.md) - How to trigger workflows from Open WebUI
- [`workflows/README.md`](workflows/README.md) - Technical architecture and workflow descriptions

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

RIN now includes a comprehensive CLI management tool for easier lifecycle management:

```bash
# Start RIN (same as ./start.sh)
./rin start

# Stop all services
./rin stop

# Restart all services
./rin restart

# Check system status and health
./rin status

# View logs (all services)
./rin logs

# View logs for specific service (with follow)
./rin logs open-webui -f

# Update Docker images
./rin update

# Upgrade RIN to latest version
./rin upgrade

# Backup all data
./rin backup

# Restore from backup
./rin restore backups/20231221_120000

# List running containers
./rin ps

# Execute command in container
./rin exec redis redis-cli

# Clean up containers and images
./rin clean

# Show version information
./rin version

# Show help
./rin help
```

**Backward Compatibility**: The original `./start.sh` script still works as before. The new `./rin` CLI is a comprehensive wrapper that provides additional management commands.

**Advanced Docker Management** (if you prefer direct docker-compose):

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

### The Reflex Arc (Autonomy)
- **n8n**: Workflow automation enabling scheduled tasks and external integrations

See [DESIGN.md](DESIGN.md) for detailed architecture documentation.

**Future Vision**: See [ARCHITECTURAL_VISION.md](ARCHITECTURAL_VISION.md) for the granular roadmap through v3.0, focusing on production readiness, observability, backups, multi-user support, and enterprise features.

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

### Zero-Config Philosophy

RIN follows the **"Sovereign Appliance"** philosophy: configure once in `.env`, and everything auto-wires on boot. No manual UI configuration needed.

#### The Pre-Wired Pipeline

```
Host (.env) → start.sh → Docker Compose → Containers → Tools (Auto-Authenticated)
```

RIN is configured via environment variables in `.env`:

```bash
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
OPENROUTER_API_KEY=your_openrouter_key

# OpenRouter Configuration (Optional but recommended)
OPENROUTER_SITE_URL=http://localhost:3000           # Your WebUI public URL
OPENROUTER_APP_NAME=RIN - Rhyzomic Intelligence Node  # Your app name for attribution

# Optional: Local Ollama
OLLAMA_API_BASE=http://host.docker.internal:11434

# External Senses: Tool API Keys (Auto-Configured)
# Set these in .env and tools will auto-authenticate in Open WebUI
TAVILY_API_KEY=tvly-your-key-here        # Get from https://tavily.com
FIRECRAWL_API_KEY=fc-auto-generated-key  # Auto-generated by start.sh (self-hosted)

# Internal Nervous System (Auto-Generated by start.sh)
LITELLM_MASTER_KEY=sk-rin-auto-generated
SEARXNG_SECRET=auto-generated-secret

# Web UI Authentication (optional)
WEBUI_AUTH=false
```

### Tool Configuration (Zero-Friction)

**New in v1.3**: Tools auto-authenticate using the Smart Valve pattern.

✅ **How it works**:
1. Add API key to `.env` file
2. Run `./start.sh`
3. Open WebUI → Tools are pre-authenticated

❌ **Old way (deprecated)**: Manually copying keys into the Tools settings UI

**Verification**: Open WebUI → Workspace → Tools → [Tool Name] → Valves - API keys should be pre-filled.

### Firecrawl Configuration Options

RIN supports two modes for Firecrawl:

**1. Cloud API (Recommended)**
- Use Firecrawl's managed cloud service
- Most reliable option for all environments
- Requires API key from https://firecrawl.dev
- Add to `.env`:
  ```bash
  FIRECRAWL_API_URL=https://api.firecrawl.dev
  FIRECRAWL_API_KEY=fc-your-api-key-here
  ```
- Restart services: `./start.sh`

**2. Self-Hosted (Advanced)**
- Firecrawl runs as a Docker container locally
- No external API key needed
- Complete privacy and control
- API key is auto-generated by `start.sh`
- **Note**: Requires PostgreSQL and RabbitMQ. In some environments (e.g., containers), self-hosted FireCrawl may not work due to Docker-in-Docker limitations.

**Troubleshooting Self-Hosted FireCrawl**:

If FireCrawl is restarting continuously with errors about PostgreSQL or RabbitMQ:
1. Use the Firecrawl Cloud API instead (recommended)
2. Or use Tavily Search as an alternative for web scraping
3. Or disable FireCrawl by setting `ENABLE_FIRECRAWL=N` in `.env`

Self-hosted FireCrawl requires external PostgreSQL and RabbitMQ services, which may not be available in all deployment environments.

### Tavily Search Configuration

Tavily provides AI-optimized search as a premium alternative or complement to the self-hosted SearXNG.

**Setup**:
1. Get API key from https://tavily.com
2. Add to `.env`:
   ```bash
   TAVILY_API_KEY=tvly-your-key-here
   ```
3. Restart: `./start.sh`
4. Tool is immediately ready in Open WebUI (pre-authenticated)

**Features**:
- AI-generated summaries for queries
- Source citations with relevance scoring
- Optimized for LLM consumption
- Includes raw content for maximum context

### Service Selection

RIN allows you to selectively enable or disable optional services to reduce resource usage or when using alternatives.

**Interactive Mode (First Run)**

When you run `./start.sh` for the first time, you'll be prompted to select which services to enable:

```
🎛️  Service Selection
Choose which services to enable:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 FireCrawl (Web Scraping Engine)
   Self-hosted service for extracting content from websites
   Alternative: Use Tavily API or other scraping tools via OpenWebUI

   Enable FireCrawl? [Y/n]:
```

**Manual Configuration**

You can also manually configure services in `.env`:

```bash
# Service Selection
ENABLE_FIRECRAWL=Y     # Set to N to disable FireCrawl
```

**When to Disable FireCrawl:**
- You prefer using Tavily API for web scraping
- You want to reduce memory/CPU usage
- You're using other OpenWebUI scraping tools
- You don't need web content extraction

After changing service selection, restart RIN:
```bash
./start.sh
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

- [x] **v1.2 "Intelligence"**: Advanced Automation ✅
  - [x] Comprehensive n8n workflow template library (8 workflows)
  - [x] Email integration workflow (Gmail, SMTP)
  - [x] RSS feed monitoring and summarization
  - [x] Slack/Telegram bot integration workflows
  - [x] Autonomous research agent workflow
  - [x] Daily report generator workflow
  - [x] Detailed workflow installation and usage guides
  - [x] FireCrawl API configuration fixes
  - [x] Comprehensive CLI Management Tool (`./rin`)
  - [x] Backup and restore functionality
  - [x] Enhanced service monitoring and logs

- [x] **v1.3 "Dynamic Intelligence"**: Dynamic Model Management & CLI Enhancement ✅
  - [x] Dynamic OpenRouter model loading (100+ models)
  - [x] Automatic model sync on startup
  - [x] Model intelligence features (popularity rankings, cost metadata)
  - [x] RIN CLI model management commands
  - [x] Model search and filtering capabilities
  - [x] Automatic model recommendations
  - [x] MCP Bridge for Model Context Protocol tools
  - [x] Sequential Thinking tool integration
  - [x] YouTube Transcript tool integration
  - [x] Auto-registration tooling for tools
  - [x] Smart Valves pattern for API key management

### Planned

- [ ] **v1.4 "Observability Core"**: Basic Monitoring (Q1 2026)
  - [ ] Health check system and status reporting
  - [ ] Basic cost tracking and usage reports
  - [ ] Enhanced log viewing with filtering
  - [ ] Simple HTML status dashboard
  
- [ ] **v1.5 "Backup Foundation"**: Data Safety (Q2 2026)
  - [ ] Automated scheduled backups (local filesystem)
  - [ ] Simple restore functionality
  - [ ] Backup verification and integrity checks
  - [ ] Container health checks and auto-restart
  
- [ ] **v1.6 "Resilience Basics"**: Fault Tolerance (Q3 2026)
  - [ ] Graceful degradation when services fail
  - [ ] Circuit breakers for external API protection
  - [ ] Basic rate limiting and quota management
  - [ ] Automatic error recovery
  
- [ ] **v1.7 "Multi-User Foundation"**: User Management (Q4 2026)
  - [ ] Basic user account management via CLI
  - [ ] Two-role system (Admin/User)
  - [ ] Per-user chat history and quotas
  - [ ] Simple authentication and session management
  
- [ ] **v2.0 "Advanced Monitoring"**: Production Observability (Q1 2027)
  - [ ] Web-based real-time monitoring dashboard
  - [ ] Metrics collection with 30-day retention
  - [ ] Email/webhook alerting system
  - [ ] Centralized log search and aggregation
  
- [ ] **v2.5 "Cloud Backup"**: Remote Storage (Q2 2027)
  - [ ] S3-compatible backup storage integration
  - [ ] Encrypted backups with client-side encryption
  - [ ] Incremental cloud sync
  - [ ] Remote restore capability
  
- [ ] **v3.0 "Production Ready"**: Enterprise Features (Q3 2027)
  - [ ] High availability mode (optional service redundancy)
  - [ ] Advanced RBAC with custom roles
  - [ ] Point-in-time recovery
  - [ ] SLA monitoring and reporting
  - [ ] Security audit compliance

For detailed feature descriptions and technical specifications, see [ARCHITECTURAL_VISION.md](ARCHITECTURAL_VISION.md).

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
