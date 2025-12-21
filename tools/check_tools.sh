#!/bin/bash
# RIN Tool Diagnostic Script
# Usage: ./tools/check_tools.sh

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 RIN Tool Diagnostic Report"
echo "=============================="
echo ""

# 1. Check if tools directory exists on host
echo "1. Host Tools Directory:"
if [ -d "./tools" ]; then
    TOOLS=$(ls ./tools/*.py 2>/dev/null | wc -l)
    echo -e "   ${GREEN}✅ Found $TOOLS .py files${NC}"
    ls ./tools/*.py 2>/dev/null | sed 's|.*/||' | while read f; do
        echo "      - $f"
    done
else
    echo -e "   ${RED}❌ ./tools directory not found${NC}"
fi

# 2. Check container mount
echo ""
echo "2. Container Mount:"
if ! docker ps --format '{{.Names}}' | grep -q "rin-cortex"; then
    echo -e "   ${RED}❌ rin-cortex container not running${NC}"
    echo "   Run: ./rin start"
    exit 1
fi

CONTAINER_TOOLS=$(docker exec rin-cortex ls /app/backend/data/tools/*.py 2>/dev/null | wc -l)
if [ "$CONTAINER_TOOLS" -gt 0 ]; then
    echo -e "   ${GREEN}✅ $CONTAINER_TOOLS tool(s) mounted in container${NC}"
    docker exec rin-cortex ls /app/backend/data/tools/*.py 2>/dev/null | sed 's|.*/||' | while read f; do
        echo "      - $f"
    done
else
    echo -e "   ${RED}❌ No tools found in container${NC}"
    echo "   Check docker-compose.yml volume mount"
fi

# 3. Check Python syntax
echo ""
echo "3. Python Syntax Validation:"
for tool in ./tools/*.py; do
    [ -f "$tool" ] || continue
    if python3 -m py_compile "$tool" 2>/dev/null; then
        echo -e "   ${GREEN}✅ $(basename $tool)${NC}"
    else
        echo -e "   ${RED}❌ $(basename $tool) - SYNTAX ERROR${NC}"
        python3 -m py_compile "$tool" 2>&1 | head -3
    fi
done

# 4. Check if tools have Tools class
echo ""
echo "4. Tools Class Validation:"
docker exec rin-cortex python3 -c "
import sys
sys.path.insert(0, '/app/backend/data/tools')
import os
for f in sorted(os.listdir('/app/backend/data/tools')):
    if f.endswith('.py') and not f.startswith('_'):
        mod_name = f[:-3]
        try:
            mod = __import__(mod_name)
            if hasattr(mod, 'Tools'):
                print(f'   ✅ {f}: Tools class found')
            else:
                print(f'   ⚠️  {f}: No Tools class')
        except Exception as e:
            print(f'   ❌ {f}: Import error - {e}')
" 2>/dev/null

# 5. Check __pycache__
echo ""
echo "5. Compilation Status:"
PYC_EXISTS=$(docker exec rin-cortex ls /app/backend/data/tools/__pycache__/*.pyc 2>/dev/null | head -1)
if [ -n "$PYC_EXISTS" ]; then
    PYC_COUNT=$(docker exec rin-cortex ls /app/backend/data/tools/__pycache__/*.pyc 2>/dev/null | wc -l)
    echo -e "   ${GREEN}✅ $PYC_COUNT compiled .pyc files found${NC}"
    echo "   (Tools have been imported at least once)"
else
    echo -e "   ${YELLOW}⚠️  No .pyc files yet${NC}"
    echo "   (Tools not yet imported via Open WebUI)"
fi

# 6. Check API endpoint
echo ""
echo "6. Open WebUI API Status:"
PORT_WEBUI=${PORT_WEBUI:-3000}
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${PORT_WEBUI}/api/v1/tools/" 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "   ${GREEN}✅ API responding (HTTP $HTTP_CODE)${NC}"
elif [ "$HTTP_CODE" = "401" ]; then
    echo -e "   ${YELLOW}⚠️  API requires auth (HTTP 401) - this is normal${NC}"
else
    echo -e "   ${RED}❌ API error (HTTP $HTTP_CODE)${NC}"
fi

echo ""
echo "=============================="
echo "📝 Summary & Next Steps:"
echo ""
if [ "$CONTAINER_TOOLS" -gt 0 ]; then
    echo -e "${GREEN}Tools are mounted correctly.${NC}"
    echo ""
    echo "→ Import tools via Open WebUI:"
    echo "  1. Open http://localhost:${PORT_WEBUI}"
    echo "  2. Go to: Workspace → Tools"
    echo "  3. Click '+' or 'Import Tool'"
    echo "  4. Toggle each tool ON"
else
    echo -e "${RED}Tools are NOT mounted correctly.${NC}"
    echo ""
    echo "→ Check docker-compose.yml has:"
    echo "  volumes:"
    echo "    - ./tools:/app/backend/data/tools"
    echo ""
    echo "→ Then restart: ./rin restart"
fi
echo ""
