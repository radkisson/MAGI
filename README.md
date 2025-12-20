# Rhyzomic Intelligence Node (RIN)

**Version**: 1.2.0 (Stable)  
**Status**: Active Development  
**Classification**: Sovereign AI Infrastructure

## Overview

Commercial AI models (ChatGPT, Claude) are "Brains in a Jar"—intelligent but disconnected, censored, and reliant on their creators for input. RIN is a sovereign, self-hosted entity. It treats commercial APIs merely as "compute," while retaining its own memory, eyes, and agency on your infrastructure.

Rhyzomic Intelligence Node (RIN) is an autonomous, self-hosted AI agent system designed to operate independently of centralized commercial control. It is not merely a chatbot, but a **sovereign organism** composed of five biological subsystems:

- 🧠 **The Cortex** (cognition) - Open WebUI + LiteLLM
- 👁️ **The Sensorium** (perception) - SearXNG + FireCrawl
- 💾 **The Memory** (recall) - Qdrant Vector Database
- ⚡ **The Nervous System** (reflex) - Redis Message Bus

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

## Key Features

- **Sovereign Architecture**: Complete control over your AI infrastructure
- **Privacy-First**: Anonymous web search via SearXNG, no data leakage
- **Multi-Model Intelligence**: Route tasks to optimal LLM providers via LiteLLM
- **Persistent Memory**: RAG-enabled recall via Qdrant vector storage
- **Asynchronous Coordination**: Redis-powered task queuing and execution
- **Biological Design**: Five subsystems working as a unified organism

## Quick Start

### Prerequisites

- Docker and Docker Compose
- API keys for LLM providers (OpenAI, Anthropic) or local Ollama installation

### Installation

```bash
# Clone the repository
git clone https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-.git
cd Rhyzomic-Intelligence-Node-RIN-

# Configure your environment
cp .env.example .env
# Edit .env with your API keys

# Launch the entire organism
docker-compose up -d

# Access the Cortex (Open WebUI)
open http://localhost:3000
```

### Service Access Points

Once deployed, access the various subsystems:

- **Open WebUI (Cortex)**: http://localhost:3000
- **LiteLLM API**: http://localhost:4000
- **SearXNG (Search)**: http://localhost:8080
- **FireCrawl API**: http://localhost:3002
- **Qdrant (Vector DB)**: http://localhost:6333
- **Redis**: localhost:6379

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

- [x] v1.0: Foundation and architecture design
- [ ] v1.1: The Cortex (Open WebUI + LiteLLM integration)
- [ ] v1.2: The Sensorium (SearXNG + FireCrawl deployment) - Current
- [ ] v1.3: The Memory (Qdrant RAG implementation)
- [ ] v1.4: The Nervous System (Redis coordination)
- [ ] v2.0: Full organism integration and optimization

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
