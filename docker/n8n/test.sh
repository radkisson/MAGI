#!/bin/bash
# Test script to verify n8n installation and endpoints

set -e

echo "========================================"
echo "Testing n8n Installation"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if n8n container is running
echo -n "1. Checking if n8n container is running... "
if docker ps | grep -q "magi-reflex-automation"; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   n8n container is not running"
    exit 1
fi

# Test 2: Check if n8n-proxy container is running
echo -n "2. Checking if n8n-proxy container is running... "
if docker ps | grep -q "magi-n8n-proxy"; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   n8n-proxy container is not running"
    exit 1
fi

# Test 3: Check n8n backend health endpoint
echo -n "3. Testing n8n backend health endpoint (localhost:5678/healthz)... "
if curl -sf http://localhost:5678/healthz | grep -q "ok"; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   Backend health check failed"
    exit 1
fi

# Test 4: Check n8n proxy health endpoint
echo -n "4. Testing n8n proxy health endpoint (localhost:8081/healthz)... "
if curl -sf http://localhost:8081/healthz | grep -q "ok"; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   Proxy health check failed"
    exit 1
fi

# Test 5: Check if n8n UI is accessible through backend
echo -n "5. Testing n8n UI access through backend (localhost:5678)... "
if curl -sf http://localhost:5678/ | grep -q "n8n"; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   Backend UI not accessible"
    exit 1
fi

# Test 6: Check if n8n UI is accessible through proxy
echo -n "6. Testing n8n UI access through proxy (localhost:8081)... "
if curl -sf http://localhost:8081/ | grep -q "n8n"; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    echo "   Proxy UI not accessible"
    exit 1
fi

# Test 7: Check n8n version
echo -n "7. Checking n8n version... "
VERSION=$(docker exec magi-reflex-automation n8n --version 2>&1)
echo -e "${GREEN}✓ PASSED${NC} (Version: $VERSION)"

# Test 8: Check container health status
echo -n "8. Checking n8n container health status... "
HEALTH=$(docker inspect --format='{{.State.Health.Status}}' magi-reflex-automation 2>/dev/null || echo "no-health")
if [ "$HEALTH" == "healthy" ]; then
    echo -e "${GREEN}✓ PASSED${NC}"
else
    echo -e "${YELLOW}⚠ WARNING${NC} (Status: $HEALTH)"
    echo "   Container may still be initializing"
fi

echo ""
echo "========================================"
echo -e "${GREEN}All Tests Passed!${NC}"
echo "========================================"
echo ""
echo "n8n is ready and accessible at:"
echo "  - Backend:  http://localhost:5678"
echo "  - Proxy:    http://localhost:8081 (recommended)"
echo ""
echo "For Tailscale access, configure in .env:"
echo "  N8N_HOST=<your-tailscale-ip>"
echo "  N8N_PROTOCOL=http"
echo "  N8N_EDITOR_BASE_URL=http://<your-tailscale-ip>:8081"
echo "  N8N_WEBHOOK_URL=http://<your-tailscale-ip>:8081/"
echo ""
