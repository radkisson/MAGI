#!/bin/bash
# Script to set up automatic HTTPS with Let's Encrypt via Caddy
# This makes HTTPS completely automatic - user just provides domain and email

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CADDY_CONFIG_DIR="$BASE_DIR/config/caddy"
CADDY_TEMPLATE="$CADDY_CONFIG_DIR/Caddyfile.template"
CADDYFILE="$CADDY_CONFIG_DIR/Caddyfile"

echo -e "${BLUE}🔒 MAGI Automatic HTTPS Setup with Let's Encrypt${NC}"
echo ""
echo "This script configures Caddy to automatically obtain and manage"
echo "SSL certificates from Let's Encrypt. No manual certificate management needed!"
echo ""

# Check if .env exists
if [ ! -f "$BASE_DIR/.env" ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo "Please run ./start.sh first to initialize the system"
    exit 1
fi

# Function to validate domain
validate_domain() {
    local domain="$1"
    # Basic domain validation - must have at least one dot and valid characters
    if [[ "$domain" =~ ^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to validate email
validate_email() {
    local email="$1"
    if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Check if automatic HTTPS is already configured
if [ -f "$CADDYFILE" ]; then
    echo -e "${YELLOW}⚠️  Automatic HTTPS is already configured${NC}"
    read -r -p "Do you want to reconfigure it? [y/N]: " RECONFIGURE
    RECONFIGURE=${RECONFIGURE:-N}
    
    if [[ ! "$RECONFIGURE" =~ ^[Yy]$ ]]; then
        echo "Keeping existing configuration."
        exit 0
    fi
fi

# Prompt for domain
echo -e "${GREEN}Domain Configuration${NC}"
echo ""
echo "Enter your domain name (e.g., magi.example.com)"
echo "This domain must:"
echo "  • Point to this server's public IP address (DNS A record)"
echo "  • Be accessible from the internet on ports 80 and 443"
echo ""

while true; do
    read -r -p "Domain name: " DOMAIN
    
    if [ -z "$DOMAIN" ]; then
        echo -e "${RED}Domain cannot be empty${NC}"
        continue
    fi
    
    if ! validate_domain "$DOMAIN"; then
        echo -e "${RED}Invalid domain format. Please enter a valid domain (e.g., magi.example.com)${NC}"
        continue
    fi
    
    # Confirm domain
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANT: Make sure your DNS is configured correctly${NC}"
    echo "   $DOMAIN → $(curl -s ifconfig.me 2>/dev/null || echo "your-server-ip")"
    echo ""
    read -r -p "Is this correct? [y/N]: " CONFIRM
    CONFIRM=${CONFIRM:-N}
    
    if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
        break
    fi
done

# Prompt for email
echo ""
echo -e "${GREEN}Administrator Email${NC}"
echo ""
echo "Enter your email address for Let's Encrypt notifications"
echo "You'll receive alerts before certificate expiration (though auto-renewal should handle it)"
echo ""

while true; do
    read -r -p "Email address: " EMAIL
    
    if [ -z "$EMAIL" ]; then
        echo -e "${RED}Email cannot be empty${NC}"
        continue
    fi
    
    if ! validate_email "$EMAIL"; then
        echo -e "${RED}Invalid email format${NC}"
        continue
    fi
    
    break
done

# Optional: Use Let's Encrypt staging for testing
echo ""
echo -e "${YELLOW}Certificate Authority Selection${NC}"
echo ""
echo "Let's Encrypt has rate limits (50 certs per domain per week)"
echo "For testing, you can use the staging environment (unlimited but not trusted by browsers)"
echo ""
read -r -p "Use Let's Encrypt STAGING for testing? [y/N]: " USE_STAGING
USE_STAGING=${USE_STAGING:-N}

# Create Caddyfile from template
echo ""
echo -e "${BLUE}📝 Generating Caddy configuration...${NC}"

if [ ! -f "$CADDY_TEMPLATE" ]; then
    echo -e "${RED}❌ Error: Caddyfile template not found at $CADDY_TEMPLATE${NC}"
    exit 1
fi

# Replace placeholders in template
sed -e "s/{DOMAIN}/$DOMAIN/g" \
    -e "s/{ADMIN_EMAIL}/$EMAIL/g" \
    "$CADDY_TEMPLATE" > "$CADDYFILE"

# If using staging, update ACME CA
if [[ "$USE_STAGING" =~ ^[Yy]$ ]]; then
    # Uncomment staging CA line and comment production line
    sed -i.bak \
        -e 's|acme_ca https://acme-v02.api.letsencrypt.org/directory|# acme_ca https://acme-v02.api.letsencrypt.org/directory|' \
        -e 's|# acme_ca https://acme-staging-v02.api.letsencrypt.org/directory|acme_ca https://acme-staging-v02.api.letsencrypt.org/directory|' \
        "$CADDYFILE" && rm -f "$CADDYFILE.bak"
    
    echo -e "${YELLOW}⚠️  Using Let's Encrypt STAGING environment${NC}"
    echo "   Certificates will not be trusted by browsers!"
fi

# Update .env file with domain and email
if grep -q "^MAGI_DOMAIN=" "$BASE_DIR/.env"; then
    # Update existing value
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s|^MAGI_DOMAIN=.*|MAGI_DOMAIN=$DOMAIN|" "$BASE_DIR/.env"
        sed -i '' "s|^MAGI_ADMIN_EMAIL=.*|MAGI_ADMIN_EMAIL=$EMAIL|" "$BASE_DIR/.env"
        sed -i '' "s|^ENABLE_AUTO_HTTPS=.*|ENABLE_AUTO_HTTPS=true|" "$BASE_DIR/.env"
    else
        sed -i "s|^MAGI_DOMAIN=.*|MAGI_DOMAIN=$DOMAIN|" "$BASE_DIR/.env"
        sed -i "s|^MAGI_ADMIN_EMAIL=.*|MAGI_ADMIN_EMAIL=$EMAIL|" "$BASE_DIR/.env"
        sed -i "s|^ENABLE_AUTO_HTTPS=.*|ENABLE_AUTO_HTTPS=true|" "$BASE_DIR/.env"
    fi
else
    # Add new values
    cat >> "$BASE_DIR/.env" <<EOF

# --- AUTOMATIC HTTPS CONFIGURATION ---
# Caddy will automatically obtain and renew Let's Encrypt certificates
MAGI_DOMAIN=$DOMAIN
MAGI_ADMIN_EMAIL=$EMAIL
ENABLE_AUTO_HTTPS=true
EOF
fi

# Create data directories for Caddy
mkdir -p "$BASE_DIR/data/caddy/data"
mkdir -p "$BASE_DIR/data/caddy/config"

echo -e "${GREEN}✅ Configuration complete!${NC}"
echo ""
echo "Generated files:"
echo "  - $CADDYFILE"
echo "  - Updated $BASE_DIR/.env"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo ""
echo "1. Ensure your DNS is configured:"
echo "   $DOMAIN → $(curl -s ifconfig.me 2>/dev/null || echo "your-server-ip")"
echo "   n8n.$DOMAIN → $(curl -s ifconfig.me 2>/dev/null || echo "your-server-ip")"
echo "   search.$DOMAIN → $(curl -s ifconfig.me 2>/dev/null || echo "your-server-ip")"
echo "   api.$DOMAIN → $(curl -s ifconfig.me 2>/dev/null || echo "your-server-ip")"
echo ""
echo "2. Ensure ports 80 and 443 are open in your firewall"
echo ""
echo "3. Start MAGI with automatic HTTPS:"
echo "   ./magi start"
echo ""
echo "4. Access your services:"
echo "   🧠 Cortex:  https://$DOMAIN"
echo "   🔄 Reflex:  https://n8n.$DOMAIN"
echo "   🔍 Vision:  https://search.$DOMAIN"
echo "   🚦 API:     https://api.$DOMAIN"
echo ""
echo -e "${GREEN}Caddy will automatically obtain SSL certificates from Let's Encrypt!${NC}"
echo ""
if [[ "$USE_STAGING" =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}⚠️  REMINDER: You're using staging certificates${NC}"
    echo "   To switch to production, edit $CADDYFILE"
    echo "   and restart: ./magi restart"
    echo ""
fi
