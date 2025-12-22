#!/bin/bash
# generate_api_key.sh - Generate Open WebUI API key for n8n integration
# Run this AFTER you've created your first admin user in Open WebUI

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🔑 Open WebUI API Key Generator${NC}"
echo ""
echo "This script will help you generate an API key for n8n integration."
echo "Prerequisites:"
echo "  1. RIN must be running (./start.sh)"
echo "  2. You must have created your admin account in Open WebUI"
echo ""

# Check if RIN is running
if ! docker ps | grep -q rin-cortex; then
    echo -e "${RED}❌ RIN is not running. Please run ./start.sh first.${NC}"
    exit 1
fi

# Load port from .env
if [ -f "$BASE_DIR/../.env" ]; then
    export $(grep -v '^#' "$BASE_DIR/../.env" | grep 'PORT_WEBUI' | xargs) 2>/dev/null || true
fi
PORT_WEBUI=${PORT_WEBUI:-3000}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To generate an API key:"
echo ""
echo "1. Open your browser to: http://localhost:${PORT_WEBUI}"
echo "2. Log in with your admin account"
echo "3. Click your profile icon (top right) → Settings"
echo "4. Go to 'Account' tab"
echo "5. Scroll to 'API Keys' section"
echo "6. Click 'Create new secret key'"
echo "7. Copy the generated key"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Paste your API key here: " API_KEY

if [ -z "$API_KEY" ]; then
    echo -e "${RED}❌ No API key provided. Exiting.${NC}"
    exit 1
fi

# Update .env file
if grep -q "^OPENWEBUI_API_KEY=" "$BASE_DIR/../.env" 2>/dev/null; then
    # Update existing value
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^OPENWEBUI_API_KEY=.*|OPENWEBUI_API_KEY=${API_KEY}|" "$BASE_DIR/../.env"
    else
        sed -i "s|^OPENWEBUI_API_KEY=.*|OPENWEBUI_API_KEY=${API_KEY}|" "$BASE_DIR/../.env"
    fi
else
    # Add new value
    echo "" >> "$BASE_DIR/../.env"
    echo "# --- OPEN WEBUI API KEY ---" >> "$BASE_DIR/../.env"
    echo "OPENWEBUI_API_KEY=${API_KEY}" >> "$BASE_DIR/../.env"
fi

echo ""
echo -e "${GREEN}✅ API key saved to .env${NC}"
echo ""
echo "Next steps:"
echo "1. Restart RIN to apply: ./start.sh"
echo "2. Import the Telegram Research Assistant workflow in n8n"
echo "3. Configure Telegram credentials in n8n"
echo "4. Start chatting with your bot!"
echo ""
echo "The following workflows can now use Open WebUI as an API:"
echo "  - telegram_research_assistant.json"
echo "  - Any custom workflow using the Open WebUI API"
