# RIN CLI Reference Guide

Quick reference for the Rhyzomic Intelligence Node (RIN) CLI management tool.

## Overview

The `rin` CLI provides comprehensive lifecycle management for your RIN instance, including start/stop operations, monitoring, updates, backups, and more.

## Quick Start

```bash
# Make executable (first time only)
chmod +x rin

# Start RIN
./rin start

# Check status
./rin status

# View logs
./rin logs
```

## Command Reference

### Basic Operations

#### `./rin start`
Starts all RIN services. This is equivalent to running `./start.sh`.

- Auto-generates secure internal keys if `.env` doesn't exist
- Creates required directory structure
- Fixes permissions for Redis/Qdrant
- Configures Docker DNS
- Starts all containers

**Example:**
```bash
./rin start
```

#### `./rin stop`
Gracefully stops all RIN services.

**Example:**
```bash
./rin stop
```

#### `./rin restart`
Restarts all RIN services (stop + start).

**Example:**
```bash
./rin restart
```

### Monitoring & Diagnostics

#### `./rin status`
Shows comprehensive system status including:
- Container status for all services
- Health checks for all endpoints
- Quick access URLs

**Example:**
```bash
./rin status
```

**Output:**
```
Container Status:
NAME                  STATUS    PORTS
rin-cortex           running   0.0.0.0:3000->8080/tcp
rin-router           running   0.0.0.0:4000->4000/tcp
...

Service Health:
✓ Open WebUI (Cortex): http://localhost:3000
✓ LiteLLM (Router): http://localhost:4000/health
...
```

#### `./rin logs [service] [-f]`
View logs for all services or a specific service.

**Examples:**
```bash
# View all logs (last 50 lines)
./rin logs

# View specific service logs
./rin logs open-webui

# Follow logs in real-time
./rin logs -f

# Follow specific service logs
./rin logs open-webui -f
```

**Available services:**
- `open-webui` - Open WebUI (Cortex)
- `litellm` - LiteLLM (Router)
- `searxng` - SearXNG (Vision)
- `firecrawl` - FireCrawl (Digestion)
- `n8n` - n8n (Reflex)
- `qdrant` - Qdrant (Memory)
- `redis` - Redis (Nervous System)
- `playwright` - Playwright (Browser)

#### `./rin ps`
Lists all running RIN containers with their status.

**Example:**
```bash
./rin ps
```

### Updates & Upgrades

#### `./rin update`
Pulls the latest Docker images for all services without upgrading the RIN codebase.

**Example:**
```bash
./rin update
# Then restart to apply:
./rin restart
```

#### `./rin upgrade`
Upgrades RIN to the latest version by:
1. Fetching latest changes from git
2. Pulling the latest code
3. Updating Docker images

**Example:**
```bash
./rin upgrade
```

**Note:** Requires RIN to be in a git repository. Creates automatic backup before upgrading.

### Backup & Restore

#### `./rin backup [directory]`
Creates a complete backup of RIN data including:
- All data directories (Open WebUI, Qdrant, Redis, etc.)
- Environment configuration (`.env`)
- Service configurations
- n8n workflows

**Examples:**
```bash
# Automatic backup with timestamp
./rin backup

# Backup to specific directory
./rin backup /path/to/backup
```

**Backup location:** `backups/YYYYMMDD_HHMMSS/`

**Backup contents:**
- `data/` - All service data
- `.env` - Environment configuration
- `config/` - Service configurations
- `workflows/` - n8n workflows
- `backup_manifest.txt` - Backup metadata

#### `./rin restore <directory>`
Restores RIN from a previous backup.

**Example:**
```bash
./rin restore backups/20231221_120000
```

**Warning:** This will overwrite current data. A confirmation prompt will appear.

### Advanced Operations

#### `./rin exec <service> [command]`
Execute commands inside a service container.

**Examples:**
```bash
# Interactive shell in redis
./rin exec redis /bin/sh

# Run redis-cli
./rin exec redis redis-cli

# Check Open WebUI database
./rin exec open-webui ls -la /app/backend/data
```

#### `./rin clean`
Removes all RIN containers, volumes, and images. 

**Warning:** This is destructive! Your data in the `data/` directory is preserved, but containers and images will be removed.

**Example:**
```bash
./rin clean
```

### Information

#### `./rin version`
Shows version information including:
- RIN version
- CLI tool version
- Git branch and commit (if in repository)

**Example:**
```bash
./rin version
```

#### `./rin help`
Displays comprehensive help with all available commands and examples.

**Example:**
```bash
./rin help
```

## Common Workflows

### Fresh Installation
```bash
git clone https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-.git
cd Rhyzomic-Intelligence-Node-RIN-
chmod +x rin
./rin start
```

### Daily Monitoring
```bash
# Check system status
./rin status

# View recent logs
./rin logs

# Follow logs in real-time
./rin logs -f
```

### Updating RIN
```bash
# Pull latest Docker images
./rin update
./rin restart

# Or upgrade everything
./rin upgrade
```

### Backup Before Changes
```bash
# Create backup
./rin backup

# Make your changes...

# Restore if needed
./rin restore backups/20231221_120000
```

### Troubleshooting
```bash
# Check status
./rin status

# View logs for problematic service
./rin logs open-webui -f

# Restart services
./rin restart

# Access container for debugging
./rin exec open-webui /bin/sh
```

### Port Conflicts
If you encounter port conflicts:

1. Edit `.env` to change conflicting ports:
```bash
nano .env
# Change PORT_WEBUI=3000 to PORT_WEBUI=3001
```

2. Restart:
```bash
./rin restart
```

### Complete Reset
```bash
# Backup first (optional but recommended)
./rin backup

# Stop and clean everything
./rin stop
./rin clean

# Start fresh
./rin start
```

## Environment Variables

RIN configuration is stored in `.env`. Common variables:

```bash
# Service Ports
PORT_WEBUI=3000      # Open WebUI
PORT_LITELLM=4000    # LiteLLM
PORT_SEARXNG=8080    # SearXNG
PORT_FIRECRAWL=3002  # FireCrawl
PORT_N8N=5678        # n8n
PORT_QDRANT=6333     # Qdrant

# API Keys (External)
OPENAI_API_KEY=      # OpenAI API key
ANTHROPIC_API_KEY=   # Anthropic API key
OPENROUTER_API_KEY=  # OpenRouter API key

# Internal Keys (Auto-generated)
LITELLM_MASTER_KEY=  # Auto-generated
SEARXNG_SECRET=      # Auto-generated
FIRECRAWL_API_KEY=   # Auto-generated
```

## Service URLs

Once RIN is running:

- **Open WebUI (Cortex)**: http://localhost:3000
- **n8n (Reflex)**: http://localhost:5678
- **LiteLLM API**: http://localhost:4000
- **SearXNG (Search)**: http://localhost:8080
- **FireCrawl API**: http://localhost:3002
- **Qdrant (Vector DB)**: http://localhost:6333
- **Redis**: localhost:6379

## Backward Compatibility

The original `./start.sh` script continues to work as before. The `./rin` CLI is a wrapper that adds management capabilities on top of the existing infrastructure.

## Getting Help

```bash
# Show all commands
./rin help

# Check version
./rin version

# View system status
./rin status
```

For more information:
- **Repository**: https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-
- **Issues**: https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/issues
- **Documentation**: See `docs/` directory
