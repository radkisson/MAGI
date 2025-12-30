#!/bin/bash
# Script to set up automatic HTTPS via Tailscale Serve
# This provides zero-config HTTPS for Tailscale users with path-based routing

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}🔒 MAGI Tailscale HTTPS Setup${NC}"
echo ""
echo "This script configures Tailscale Serve to provide automatic HTTPS"
echo "for all MAGI services with path-based routing. No certificates needed!"
echo ""

# Check if Tailscale is installed
if ! command -v tailscale &> /dev/null; then
    echo -e "${RED}❌ Error: Tailscale is not installed${NC}"
    echo "Install Tailscale: https://tailscale.com/download"
    exit 1
fi

# Check if python3 is available (needed for JSON parsing)
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 is required but not installed${NC}"
    exit 1
fi

# Check if Tailscale is connected
if ! tailscale status &> /dev/null; then
    echo -e "${RED}❌ Error: Tailscale is not connected${NC}"
    echo "Run: sudo tailscale up"
    exit 1
fi

# Get Tailscale hostname and domain
TS_STATUS=$(tailscale status --json 2>/dev/null) || {
    echo -e "${RED}❌ Error: Could not get Tailscale status${NC}"
    exit 1
}

TS_HOSTNAME=$(echo "$TS_STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('Self',{}).get('HostName',''))" 2>/dev/null)
if [ -z "$TS_HOSTNAME" ]; then
    TS_HOSTNAME=$(hostname)
fi

TS_DOMAIN=$(echo "$TS_STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('MagicDNSSuffix',''))" 2>/dev/null)

if [ -z "$TS_DOMAIN" ]; then
    echo -e "${RED}❌ Error: Could not determine Tailscale domain${NC}"
    echo "Make sure Tailscale MagicDNS is enabled in your admin console"
    exit 1
fi

FULL_DOMAIN="${TS_HOSTNAME}.${TS_DOMAIN}"

echo -e "${GREEN}Tailscale Configuration Detected:${NC}"
echo "  Hostname: $TS_HOSTNAME"
echo "  Domain:   $TS_DOMAIN"
echo "  Full URL: https://$FULL_DOMAIN"
echo ""

# Load port configuration from .env
if [ -f "$BASE_DIR/.env" ]; then
    # shellcheck disable=SC1090
    set -a
    while IFS='=' read -r key value; do
        [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
        if [[ "$key" =~ ^PORT_ ]]; then
            export "$key=$value"
        fi
    done < <(grep -E '^PORT_' "$BASE_DIR/.env" 2>/dev/null || true)
    set +a
fi

# Use loaded values or defaults
PORT_WEBUI=${PORT_WEBUI:-3000}
PORT_N8N=${PORT_N8N:-5678}
PORT_LITELLM=${PORT_LITELLM:-4000}
PORT_JUPYTER=${PORT_JUPYTER:-8888}
PORT_SEARXNG=${PORT_SEARXNG:-8080}

echo -e "${BLUE}📝 Configuring Tailscale Serve...${NC}"
echo ""

# Reset existing serve configuration
echo "  Resetting existing configuration..."
tailscale serve reset 2>/dev/null || true

# Configure path-based routing
echo "  Setting up path-based routing..."

# Main service - OpenWebUI at root
if tailscale serve --bg --set-path / "http://localhost:${PORT_WEBUI}" 2>/dev/null; then
    echo "  ✓ / → OpenWebUI (port $PORT_WEBUI)"
else
    echo -e "${RED}  ✗ Failed to configure / path${NC}"
fi

# n8n workflow automation
if tailscale serve --bg --set-path /n8n "http://localhost:${PORT_N8N}" 2>/dev/null; then
    echo "  ✓ /n8n → n8n (port $PORT_N8N)"
else
    echo -e "${RED}  ✗ Failed to configure /n8n path${NC}"
fi

# LiteLLM API
if tailscale serve --bg --set-path /api "http://localhost:${PORT_LITELLM}" 2>/dev/null; then
    echo "  ✓ /api → LiteLLM API (port $PORT_LITELLM)"
else
    echo -e "${RED}  ✗ Failed to configure /api path${NC}"
fi

# Jupyter notebooks
if tailscale serve --bg --set-path /jupyter "http://localhost:${PORT_JUPYTER}" 2>/dev/null; then
    echo "  ✓ /jupyter → Jupyter (port $PORT_JUPYTER)"
else
    echo -e "${RED}  ✗ Failed to configure /jupyter path${NC}"
fi

# SearXNG search (optional - may conflict with OpenWebUI paths)
# Uncomment if needed:
# tailscale serve --bg --set-path /search http://localhost:${PORT_SEARXNG} 2>/dev/null
# echo "  ✓ /search → SearXNG (port $PORT_SEARXNG)"

echo ""

# Update .env with Tailscale configuration
if [ ! -f "$BASE_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Run ./start.sh first to initialize.${NC}"
    echo "   Tailscale Serve is configured but settings won't persist in .env"
elif grep -q "^ENABLE_TAILSCALE_HTTPS=" "$BASE_DIR/.env" 2>/dev/null; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^ENABLE_TAILSCALE_HTTPS=.*|ENABLE_TAILSCALE_HTTPS=true|" "$BASE_DIR/.env"
        # Update or add TAILSCALE_DOMAIN
        if grep -q "^TAILSCALE_DOMAIN=" "$BASE_DIR/.env" 2>/dev/null; then
            sed -i '' "s|^TAILSCALE_DOMAIN=.*|TAILSCALE_DOMAIN=$FULL_DOMAIN|" "$BASE_DIR/.env"
        else
            echo "TAILSCALE_DOMAIN=$FULL_DOMAIN" >> "$BASE_DIR/.env"
        fi
        # Configure path-based routing for services
        if grep -q "^N8N_PATH=" "$BASE_DIR/.env" 2>/dev/null; then
            sed -i '' "s|^N8N_PATH=.*|N8N_PATH=/n8n|" "$BASE_DIR/.env"
        else
            echo "N8N_PATH=/n8n" >> "$BASE_DIR/.env"
        fi
        if grep -q "^N8N_EDITOR_BASE_URL=" "$BASE_DIR/.env" 2>/dev/null; then
            sed -i '' "s|^N8N_EDITOR_BASE_URL=.*|N8N_EDITOR_BASE_URL=https://$FULL_DOMAIN/n8n/|" "$BASE_DIR/.env"
        else
            echo "N8N_EDITOR_BASE_URL=https://$FULL_DOMAIN/n8n/" >> "$BASE_DIR/.env"
        fi
        if grep -q "^JUPYTER_BASE_URL=" "$BASE_DIR/.env" 2>/dev/null; then
            sed -i '' "s|^JUPYTER_BASE_URL=.*|JUPYTER_BASE_URL=/jupyter|" "$BASE_DIR/.env"
        else
            echo "JUPYTER_BASE_URL=/jupyter" >> "$BASE_DIR/.env"
        fi
        # Configure OpenWebUI base URL and disable persistent config
        if grep -q "^WEBUI_URL=" "$BASE_DIR/.env" 2>/dev/null; then
            sed -i '' "s|^WEBUI_URL=.*|WEBUI_URL=https://$FULL_DOMAIN|" "$BASE_DIR/.env"
        else
            echo "WEBUI_URL=https://$FULL_DOMAIN" >> "$BASE_DIR/.env"
        fi
        if grep -q "^ENABLE_PERSISTENT_CONFIG=" "$BASE_DIR/.env" 2>/dev/null; then
            sed -i '' "s|^ENABLE_PERSISTENT_CONFIG=.*|ENABLE_PERSISTENT_CONFIG=false|" "$BASE_DIR/.env"
        else
            echo "ENABLE_PERSISTENT_CONFIG=false" >> "$BASE_DIR/.env"
        fi
    else
        sed -i "s|^ENABLE_TAILSCALE_HTTPS=.*|ENABLE_TAILSCALE_HTTPS=true|" "$BASE_DIR/.env"
        # Update or add TAILSCALE_DOMAIN
        if grep -q "^TAILSCALE_DOMAIN=" "$BASE_DIR/.env" 2>/dev/null; then
            sed -i "s|^TAILSCALE_DOMAIN=.*|TAILSCALE_DOMAIN=$FULL_DOMAIN|" "$BASE_DIR/.env"
        else
            echo "TAILSCALE_DOMAIN=$FULL_DOMAIN" >> "$BASE_DIR/.env"
        fi
        # Configure path-based routing for services
        if grep -q "^N8N_PATH=" "$BASE_DIR/.env" 2>/dev/null; then
            sed -i "s|^N8N_PATH=.*|N8N_PATH=/n8n|" "$BASE_DIR/.env"
        else
            echo "N8N_PATH=/n8n" >> "$BASE_DIR/.env"
        fi
        if grep -q "^N8N_EDITOR_BASE_URL=" "$BASE_DIR/.env" 2>/dev/null; then
            sed -i "s|^N8N_EDITOR_BASE_URL=.*|N8N_EDITOR_BASE_URL=https://$FULL_DOMAIN/n8n/|" "$BASE_DIR/.env"
        else
            echo "N8N_EDITOR_BASE_URL=https://$FULL_DOMAIN/n8n/" >> "$BASE_DIR/.env"
        fi
        if grep -q "^JUPYTER_BASE_URL=" "$BASE_DIR/.env" 2>/dev/null; then
            sed -i "s|^JUPYTER_BASE_URL=.*|JUPYTER_BASE_URL=/jupyter|" "$BASE_DIR/.env"
        else
            echo "JUPYTER_BASE_URL=/jupyter" >> "$BASE_DIR/.env"
        fi
        # Configure OpenWebUI base URL and disable persistent config
        if grep -q "^WEBUI_URL=" "$BASE_DIR/.env" 2>/dev/null; then
            sed -i "s|^WEBUI_URL=.*|WEBUI_URL=https://$FULL_DOMAIN|" "$BASE_DIR/.env"
        else
            echo "WEBUI_URL=https://$FULL_DOMAIN" >> "$BASE_DIR/.env"
        fi
        if grep -q "^ENABLE_PERSISTENT_CONFIG=" "$BASE_DIR/.env" 2>/dev/null; then
            sed -i "s|^ENABLE_PERSISTENT_CONFIG=.*|ENABLE_PERSISTENT_CONFIG=false|" "$BASE_DIR/.env"
        else
            echo "ENABLE_PERSISTENT_CONFIG=false" >> "$BASE_DIR/.env"
        fi
    fi
else
    cat >> "$BASE_DIR/.env" <<EOF

# --- TAILSCALE HTTPS CONFIGURATION ---
# Tailscale Serve provides automatic HTTPS with path-based routing
ENABLE_TAILSCALE_HTTPS=true
TAILSCALE_DOMAIN=$FULL_DOMAIN

# Path-based routing configuration for services
N8N_PATH=/n8n
N8N_EDITOR_BASE_URL=https://$FULL_DOMAIN/n8n/
JUPYTER_BASE_URL=/jupyter

# OpenWebUI base URL configuration (for frontend-backend communication)
WEBUI_URL=https://$FULL_DOMAIN
ENABLE_PERSISTENT_CONFIG=false
EOF
fi

# Show final configuration
echo -e "${GREEN}✅ Tailscale HTTPS configuration complete!${NC}"
echo ""
tailscale serve status
echo ""
echo -e "${BLUE}📋 Your MAGI services are now available at:${NC}"
echo ""
echo "  🧠 OpenWebUI:  https://$FULL_DOMAIN/"
echo "  🔄 n8n:        https://$FULL_DOMAIN/n8n"
echo "  🚦 LiteLLM:    https://$FULL_DOMAIN/api"
echo "  📓 Jupyter:    https://$FULL_DOMAIN/jupyter"
echo ""
echo -e "${GREEN}All services use automatic HTTPS via Tailscale!${NC}"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Restart MAGI services to apply path-based routing:${NC}"
echo "   ./rin restart"
echo ""
echo "Note: These URLs only work from devices on your Tailscale network."
echo ""
