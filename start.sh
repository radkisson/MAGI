#!/bin/bash
set -e

# --- 1. VISUAL FEEDBACK ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧠 Rhyzomic Intelligence Node (RIN) - Boot Sequence Initiated${NC}"

# --- 2. DEPENDENCY CHECK ---
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "Docker installed. Please re-login to apply user groups."
    exit 1
fi

# --- 3. INFRASTRUCTURE PREP ---
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "${GREEN}📂 Verifying biological directory structure...${NC}"

# Create all volume paths
mkdir -p "$BASE_DIR/data"/{open-webui,qdrant,redis,searxng,n8n}
mkdir -p "$BASE_DIR/config"/{litellm,searxng}
mkdir -p "$BASE_DIR/workflows"

# Fix Permissions (Critical for Redis/Qdrant on Linux)
# Note: 777 is required for Docker volume permissions on many Linux systems
# where the container UIDs don't match host UIDs. This is a known Docker limitation.
chmod 777 "$BASE_DIR/data/redis" "$BASE_DIR/data/qdrant"

# Fix Permissions for n8n (runs as user 1000 inside container)
chown -R 1000:1000 "$BASE_DIR/data/n8n" 2>/dev/null || chmod 777 "$BASE_DIR/data/n8n"

# --- 4. INTERNAL KEY GENERATION (The Magic Step) ---
# We auto-generate keys if .env doesn't exist. 
# The user only touches this file if they want to add OpenAI/Anthropic keys.

if [ ! -f "$BASE_DIR/.env" ]; then
    echo -e "${GREEN}🔐 Generating internal neural secrets...${NC}"
    
    # Generate random high-entropy strings
    LITELLM_KEY="sk-rin-$(openssl rand -hex 12)"
    SEARXNG_KEY=$(openssl rand -hex 32)
    FIRECRAWL_KEY="fc-$(openssl rand -hex 16)"
    
    cat <<EOF > "$BASE_DIR/.env"
# --- RIN INTERNAL NERVOUS SYSTEM (AUTO-GENERATED) ---
# Do not change these unless you know what you are doing.
LITELLM_MASTER_KEY=${LITELLM_KEY}
SEARXNG_SECRET=${SEARXNG_KEY}
FIRECRAWL_API_KEY=${FIRECRAWL_KEY}

# --- EXTERNAL API KEYS (USER DEFINED) ---
# Replace these with your actual keys to power the brain.
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OPENROUTER_API_KEY=

# --- NETWORK ---
PORT_WEBUI=3000
EOF
    echo "✅ .env created with secure internal keys."
else
    echo "✅ .env already exists. Preserving existing keys."
fi

# --- 5. CONFIGURATION INJECTION ---

# Generate SearXNG Settings (Prevents Crash Loop)
if [ ! -f "$BASE_DIR/config/searxng/settings.yml" ]; then
    # We pull the key back out of .env to populate the config
    LOADED_SEARX_KEY=$(grep "^SEARXNG_SECRET=" "$BASE_DIR/.env" | cut -d '=' -f2 | tr -d ' ')
    
    cat <<EOF > "$BASE_DIR/config/searxng/settings.yml"
use_default_settings: true
server:
  secret_key: "${LOADED_SEARX_KEY}"
  bind_address: "0.0.0.0"
  image_proxy: true
  limiter: false
search:
  formats:
    - html
    - json
EOF
fi

# --- 6. DNS FIX (Azure/Cloud Specific) ---
# Ensures containers can talk to the outside world
# Only applies if Docker daemon config doesn't already have DNS settings
if [ ! -f /etc/docker/daemon.json ] || ! grep -q '"dns"' /etc/docker/daemon.json 2>/dev/null; then
    echo -e "${BLUE}🔧 Patching Docker DNS...${NC}"
    sudo mkdir -p /etc/docker
    # Merge with existing config if present, otherwise create new
    if [ -f /etc/docker/daemon.json ]; then
        echo "⚠️  Existing Docker daemon.json found. Please manually add DNS settings if needed."
    else
        echo '{"dns": ["1.1.1.1", "8.8.8.8"]}' | sudo tee /etc/docker/daemon.json > /dev/null
        sudo systemctl restart docker
        sleep 3 # Wait for Docker to wake up
    fi
fi

# --- 7. LAUNCH ---
echo -e "${GREEN}🚀 Igniting the Organism...${NC}"

# Verify docker-compose.yml exists
if [ ! -f "$BASE_DIR/docker-compose.yml" ]; then
    echo "❌ Error: docker-compose.yml not found in $BASE_DIR"
    exit 1
fi

# Verify Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

docker compose up -d --remove-orphans

echo ""
echo -e "${GREEN}✅ RIN IS ALIVE.${NC}"
echo ""
echo "=== Post-Deployment Verification ==="
echo "Verify the 5 biological subsystems are active:"
echo ""
echo "🧠 Cortex (UI):        http://localhost:3000      (Open WebUI login screen)"
echo "🔄 Reflex (n8n):       http://localhost:5678      (n8n workflow editor)"
echo "👁️  Sensorium:         http://localhost:8080      (SearXNG search bar)"
echo "🔥 Digestion:          http://localhost:3002      (FireCrawl API - returns {\"status\":\"ok\"})"
echo "🚦 Router:             http://localhost:4000/health (LiteLLM health status)"
echo ""
echo "=== Next Steps ==="
echo "1. Add API keys: nano .env (add OPENAI_API_KEY or ANTHROPIC_API_KEY)"
echo "2. Restart to apply: ./start.sh"
echo "3. Activate tools in Cortex: http://localhost:3000 → Workspace → Tools"
echo "4. Import workflows: http://localhost:5678 → Import → workflows/morning_briefing.json"
