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
mkdir -p "$BASE_DIR/data"/{open-webui,qdrant,redis,searxng}
mkdir -p "$BASE_DIR/config"/{litellm,searxng}

# Fix Permissions (Critical for Redis/Qdrant on Linux)
chmod 777 "$BASE_DIR/data/redis" "$BASE_DIR/data/qdrant"

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
    LOADED_SEARX_KEY=$(grep SEARXNG_SECRET "$BASE_DIR/.env" | cut -d '=' -f2)
    
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
if [ ! -f /etc/docker/daemon.json ]; then
    echo -e "${BLUE}🔧 Patching Docker DNS...${NC}"
    sudo mkdir -p /etc/docker
    echo '{"dns": ["1.1.1.1", "8.8.8.8"]}' | sudo tee /etc/docker/daemon.json > /dev/null
    sudo systemctl restart docker
    sleep 3 # Wait for Docker to wake up
fi

# --- 7. LAUNCH ---
echo -e "${GREEN}🚀 Igniting the Organism...${NC}"
docker compose up -d --remove-orphans

echo ""
echo -e "${BLUE}✅ RIN IS ALIVE.${NC}"
echo "------------------------------------------------"
echo "🧠 Cortex (UI):   http://localhost:3000"
echo "👁️  SearXNG:      http://localhost:8080"
echo "------------------------------------------------"
echo "👉 NEXT STEP: Edit '.env' to add your OpenAI/Anthropic keys if needed."
echo "              Then restart with './start.sh'"
