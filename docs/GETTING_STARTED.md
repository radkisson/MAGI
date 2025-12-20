# Getting Started with RIN

## Introduction

Welcome to the Rhyzomic Intelligence Node (RIN)! This guide will help you get started with your sovereign AI agent system.

## What is RIN?

RIN is an autonomous, self-hosted AI agent system that gives you full control over your AI infrastructure. Unlike commercial AI services, RIN:

- Runs entirely on your infrastructure
- Maintains its own memory and knowledge
- Can browse the web and gather information
- Executes autonomous tasks
- Uses commercial AI APIs only as "compute" while keeping control in your hands

## Core Concepts

### The Three Pillars

1. **Sensors (Perception)**
   - Real-time web browsing
   - API integration
   - Data collection and extraction

2. **Memory (Knowledge)**
   - Vector-based storage
   - Semantic search
   - Persistent knowledge across sessions

3. **Reflexes (Action)**
   - Autonomous task execution
   - Workflow automation
   - Decision making

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Optional: Docker for containerized deployment

### Quick Install

```bash
# Clone the repository
git clone https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-.git
cd Rhyzomic-Intelligence-Node-RIN-

# Install dependencies
pip install -r requirements.txt

# Install RIN
pip install -e .
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings:
```bash
# Add your API keys
OPENAI_API_KEY=your_key_here
# Configure other settings as needed
```

3. Verify configuration:
```bash
python -m rin.main
```

## Basic Usage

### Running RIN

```bash
# Run directly
python -m rin.main

# Or if installed
rin
```

### Using RIN in Code

```python
from rin import Agent

# Initialize the agent
agent = Agent()

# Query the agent
response = agent.query("What's the latest in AI research?")
print(response)

# Execute a task
result = agent.execute_task("Monitor HackerNews for Python articles")
print(result)
```

## Docker Deployment

### Build and Run

```bash
# Build the Docker image
docker build -t rin:latest .

# Run the container
docker run -d \
  --name rin \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY=your_key \
  rin:latest
```

### Using Docker Compose

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  rin:
    build: .
    container_name: rin
    volumes:
      - ./data:/app/data
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

## Next Steps

- Read the [Architecture Documentation](ARCHITECTURE.md)
- Explore [Examples](EXAMPLES.md)
- Check out [Advanced Configuration](CONFIGURATION.md)
- Learn about [Custom Sensors](SENSORS.md)
- Understand [Memory Management](MEMORY.md)
- Create [Custom Reflexes](REFLEXES.md)

## Troubleshooting

### Common Issues

**Issue**: Import errors
**Solution**: Make sure you've installed the package: `pip install -e .`

**Issue**: API key errors
**Solution**: Check your `.env` file has valid API keys

**Issue**: Permission errors
**Solution**: Ensure the `data/` directory is writable

## Getting Help

- Check the [FAQ](FAQ.md)
- Read the [Documentation](README.md)
- Open an [Issue](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/issues)
- Join [Discussions](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/discussions)

## Philosophy

Remember: RIN is about **digital sovereignty**. You control:
- Where it runs
- What data it stores
- How it operates
- Which AI providers it uses

Start small, experiment, and expand as you understand the system better.

Welcome to sovereign AI! 🚀
