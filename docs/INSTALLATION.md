# Installation Guide

## Prerequisites

- Docker (automatically installed by start.sh if missing)
- API keys for LLM providers (OpenAI, Anthropic, OpenRouter) - Optional, can be added later

## Quick Start (3 Steps)

### 1. Clone

```bash
git clone https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-.git
cd Rhyzomic-Intelligence-Node-RIN-
```

### 2. Start

```bash
chmod +x rin start.sh
./magi start
```

This automatically:
- Generates all secure internal keys
- Creates the required directory structure
- Fixes permissions for Redis/Qdrant
- Configures Docker DNS for cloud environments
- Starts all containers
- Prompts for initial admin account setup

### 3. Access

Open http://localhost:3000 to access MAGI.

## Initial Account Setup

On first startup, MAGI prompts you to create admin accounts for:
- **OpenWebUI** (main interface)
- **n8n** (workflow automation)

You can:
- Pre-configure in `.env` as `MAGI_ADMIN_EMAIL` and `MAGI_ADMIN_PASSWORD`
- Enter interactively during startup
- Reset later using `./magi reset-password <service>`

## Adding API Keys

Edit `.env` and add your keys:

```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
OPENROUTER_API_KEY=your_openrouter_key
```

Then restart: `./magi restart`

## Service Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Open WebUI | http://localhost:3000 | Main interface |
| n8n | http://localhost:5678 | Workflow automation |
| LiteLLM | http://localhost:4000 | API router |
| SearXNG | http://localhost:8080 | Search engine |
| Qdrant | http://localhost:6333 | Vector database |
| MCP Bridge | http://localhost:9000 | Sequential Thinking |
| YouTube MCP | http://localhost:9001 | Video transcripts |

## Troubleshooting

### Port Already Allocated

Edit `.env` and change the conflicting port:

```bash
PORT_WEBUI=3001  # Change from 3000
```

Available port settings:
- `PORT_WEBUI`, `PORT_LITELLM`, `PORT_SEARXNG`, `PORT_FIRECRAWL`
- `PORT_N8N`, `PORT_QDRANT`, `PORT_MCP_BRIDGE`, `PORT_YOUTUBE_MCP`

### n8n Secure Cookie Warning

Expected for local HTTP. For production, see [HTTPS_CONFIGURATION.md](HTTPS_CONFIGURATION.md).

## HTTPS/TLS

For production deployments with HTTPS:

```bash
# Generate certificates
./scripts/generate-certs.sh

# Enable HTTPS in .env
ENABLE_HTTPS=true

# Restart
./magi restart
```

See [HTTPS_CONFIGURATION.md](HTTPS_CONFIGURATION.md) for reverse proxy setup (nginx, Traefik, Caddy).
