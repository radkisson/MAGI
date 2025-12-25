#!/bin/bash
# Convenience script to sync OpenRouter models
# Usage: ./scripts/sync_models.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔄 Syncing OpenRouter models..."
echo ""

# Make sure we have python3 and requirements
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found. Please install Python 3."
    exit 1
fi

# Check if requests and pyyaml are available
python3 -c "import requests, yaml" 2>/dev/null || {
    echo "📦 Installing required Python packages..."
    pip3 install requests pyyaml || {
        echo "❌ Failed to install Python requirements"
        echo "   Please install manually: pip3 install requests pyyaml"
        exit 1
    }
}

# Load environment variables if .env exists
if [ -f "$BASE_DIR/.env" ]; then
    export $(grep -E '^OPENROUTER_API_KEY=' "$BASE_DIR/.env" | xargs)
fi

# Run the sync script
python3 "$SCRIPT_DIR/sync_openrouter_models.py"
SYNC_EXIT=$?

if [ $SYNC_EXIT -eq 0 ]; then
    echo ""
    echo "✅ Model sync complete!"
    echo ""
    echo "To apply changes, restart LiteLLM:"
    echo "  docker-compose restart litellm"
    echo ""
    echo "Or restart all services:"
    echo "  docker-compose down && docker-compose up -d"
else
    echo ""
    echo "⚠️  Model sync did not complete successfully"
    echo "   Check the output above for details"
fi

exit $SYNC_EXIT
