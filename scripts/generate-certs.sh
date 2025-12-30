#!/bin/bash
# Script to generate self-signed SSL certificates for RIN services
# For production use, replace these with proper CA-signed certificates

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SSL_DIR="$BASE_DIR/config/ssl"

echo -e "${BLUE}🔒 RIN SSL Certificate Generator${NC}"
echo ""

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Check if certificates already exist
if [ -f "$SSL_DIR/cert.pem" ] && [ -f "$SSL_DIR/key.pem" ]; then
    echo -e "${YELLOW}⚠️  SSL certificates already exist in $SSL_DIR${NC}"
    read -r -p "Do you want to regenerate them? This will overwrite existing certificates [y/N]: " REGENERATE
    REGENERATE=${REGENERATE:-N}
    
    if [[ ! "$REGENERATE" =~ ^[Yy]$ ]]; then
        echo "Keeping existing certificates."
        exit 0
    fi
    
    echo "Regenerating certificates..."
fi

echo -e "${GREEN}📝 Generating self-signed SSL certificates...${NC}"
echo ""

# Generate private key
echo "Generating private key..."
openssl genrsa -out "$SSL_DIR/key.pem" 2048

# Generate certificate signing request (CSR)
echo "Generating certificate signing request..."
openssl req -new -key "$SSL_DIR/key.pem" -out "$SSL_DIR/csr.pem" \
    -subj "/C=US/ST=State/L=City/O=RIN/OU=Rhyzomic Intelligence Node/CN=localhost"

# Generate self-signed certificate (valid for 365 days)
echo "Generating self-signed certificate (valid for 1 year)..."
openssl x509 -req -days 365 -in "$SSL_DIR/csr.pem" \
    -signkey "$SSL_DIR/key.pem" -out "$SSL_DIR/cert.pem" \
    -extfile <(printf "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1,IP:0.0.0.0")

# Generate CA certificate (self-signed root CA)
echo "Generating self-signed CA certificate..."
cp "$SSL_DIR/cert.pem" "$SSL_DIR/ca.pem"

# Clean up CSR
rm "$SSL_DIR/csr.pem"

# Set appropriate permissions
chmod 644 "$SSL_DIR/cert.pem"
chmod 600 "$SSL_DIR/key.pem"
chmod 644 "$SSL_DIR/ca.pem"

echo ""
echo -e "${GREEN}✅ SSL certificates generated successfully!${NC}"
echo ""
echo "Generated files:"
echo "  - Certificate: $SSL_DIR/cert.pem"
echo "  - Private Key: $SSL_DIR/key.pem"
echo "  - CA Certificate: $SSL_DIR/ca.pem"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: These are self-signed certificates for development/testing.${NC}"
echo -e "${YELLOW}   Your browser will show security warnings. This is expected.${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "   1. Set ENABLE_HTTPS=true in your .env file"
echo "   2. Run ./start.sh or ./magi start to restart services with HTTPS"
echo "   3. Access services using https:// instead of http://"
echo ""
echo -e "${BLUE}🔐 For production:${NC}"
echo "   Replace these self-signed certificates with proper CA-signed certificates"
echo "   from Let's Encrypt, Cloudflare, or your certificate authority."
echo ""
