# Rhyzomic Intelligence Node (RIN)

**Version**: 1.2.0 (Stable)  
**Status**: Active Development  
**Classification**: Sovereign AI Infrastructure

## Overview

Commercial AI models (ChatGPT, Claude) are "Brains in a Jar"—intelligent but disconnected, censored, and reliant on their creators for input. RIN is a sovereign, self-hosted entity. It treats commercial APIs merely as "compute," while retaining its own memory, eyes, and agency on your infrastructure.

Rhyzomic Intelligence Node (RIN) is an autonomous, self-hosted AI agent system designed to operate independently of centralized commercial control. It is not merely a chatbot, but a sovereign organism equipped with:

- 🔭 **Sensors** (real-time browsing)
- 🧠 **Memory** (vectorized recall)
- ⚡ **Reflexes** (automation)

## Key Features

- **Sovereign Architecture**: Run entirely on your infrastructure
- **Real-Time Perception**: Browse the web and gather information
- **Persistent Memory**: Vector-based knowledge storage and retrieval
- **Autonomous Actions**: Automated task execution and decision-making
- **API Independence**: Use any LLM provider as compute
- **Privacy-First**: Your data never leaves your control

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Docker (optional, for containerized deployment)
- API keys for LLM providers (OpenAI, Anthropic, or local models)

### Installation

```bash
# Clone the repository
git clone https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-.git
cd Rhyzomic-Intelligence-Node-RIN-

# Install dependencies
pip install -r requirements.txt

# Configure your environment
cp .env.example .env
# Edit .env with your API keys and settings

# Run RIN
python -m rin.main
```

### Docker Deployment

```bash
# Build the Docker image
docker build -t rin:latest .

# Run the container
docker run -d \
  --name rin \
  -v $(pwd)/data:/app/data \
  -p 8000:8000 \
  --env-file .env \
  rin:latest
```

## Architecture

RIN is built on three core pillars:

### 1. Sensors (Real-Time Browsing)
- Web scraping and content extraction
- API integration for external data sources
- Real-time information gathering

### 2. Memory (Vectorized Recall)
- Vector database for semantic search
- Persistent knowledge storage
- Context-aware retrieval

### 3. Reflexes (Automation)
- Autonomous task execution
- Decision-making framework
- Tool integration and orchestration

See [DESIGN.md](DESIGN.md) for detailed architecture documentation.

## Project Structure

```
rin/
├── src/rin/                    # Source code
│   ├── sensors/                # Real-time browsing and data collection
│   ├── memory/                 # Vector storage and retrieval
│   ├── reflexes/               # Automation and action execution
│   ├── core/                   # Agent orchestration
│   └── utils/                  # Shared utilities
├── tests/                      # Test suite
├── docs/                       # Documentation
├── examples/                   # Usage examples
├── config/                     # Configuration files
└── data/                       # Local data storage (gitignored)
```

## Configuration

RIN is configured via environment variables and configuration files:

- `.env` - API keys and sensitive settings
- `config/config.yaml` - System configuration
- `config/memory_config.yaml` - Memory system settings
- `config/sensors_config.yaml` - Sensors configuration

## Usage Examples

### Basic Agent Interaction

```python
from rin import Agent

# Initialize the agent
agent = Agent()

# Send a query
response = agent.query("What are the latest developments in AI?")
print(response)

# The agent will:
# 1. Use sensors to browse relevant sources
# 2. Store findings in memory
# 3. Generate a response using its reflexes
```

### Autonomous Task Execution

```python
from rin import Agent

agent = Agent()

# Assign a task
agent.execute_task(
    "Monitor HackerNews for articles about Python and summarize them daily"
)

# The agent will autonomously:
# 1. Browse HackerNews regularly
# 2. Filter relevant articles
# 3. Store summaries in memory
# 4. Generate daily reports
```

## Development

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
- New sensor implementations
- Memory optimization
- Reflex automation patterns
- Documentation improvements
- Testing coverage

## Roadmap

- [x] v1.0: Foundation and core agent loop
- [x] v1.1: Basic sensors implementation
- [ ] v1.2: Memory system with vector storage (Current)
- [ ] v1.3: Advanced reflexes and automation
- [ ] v2.0: Multi-agent coordination

## Philosophy

RIN embodies digital sovereignty. It's not about replacing commercial AI—it's about reclaiming agency. By hosting your own intelligence node, you maintain:

- **Control**: Over your data and operations
- **Privacy**: No data sent to third parties
- **Flexibility**: Use any LLM as compute
- **Transparency**: Full visibility into operations
- **Independence**: Not reliant on any single provider

## License

See [LICENSE](LICENSE) for details.

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/issues)
- **Discussions**: [GitHub Discussions](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/discussions)

---

**Built for digital sovereignty. Run by you, for you.**
