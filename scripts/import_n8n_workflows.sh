#!/bin/bash
# Auto-import n8n workflows from /workflows directory
# This script runs inside the n8n container after startup

set -e

WORKFLOWS_DIR="/workflows"
IMPORT_MARKER="/home/node/.n8n/.workflows_imported"

# Check if workflows directory exists and has JSON files
if [ ! -d "$WORKFLOWS_DIR" ]; then
    echo "⚠️  Workflows directory not found: $WORKFLOWS_DIR"
    exit 0
fi

WORKFLOW_COUNT=$(find "$WORKFLOWS_DIR" -name "*.json" -type f 2>/dev/null | wc -l)
if [ "$WORKFLOW_COUNT" -eq 0 ]; then
    echo "⚠️  No workflow JSON files found in $WORKFLOWS_DIR"
    exit 0
fi

# Check if already imported (skip on subsequent starts)
if [ -f "$IMPORT_MARKER" ]; then
    MARKER_COUNT=$(cat "$IMPORT_MARKER" 2>/dev/null || echo "0")
    if [ "$MARKER_COUNT" -eq "$WORKFLOW_COUNT" ]; then
        echo "ℹ️  Workflows already imported ($WORKFLOW_COUNT workflows). Skipping."
        exit 0
    fi
fi

echo "🔄 Importing $WORKFLOW_COUNT workflows from $WORKFLOWS_DIR..."

# Import all workflows
n8n import:workflow --separate --input="$WORKFLOWS_DIR" 2>&1 | grep -v "Could not find workflow" | grep -v "Could not remove webhooks" || true

# Mark as imported
echo "$WORKFLOW_COUNT" > "$IMPORT_MARKER"

echo "✅ Workflows imported successfully."

# List imported workflows
echo ""
echo "📋 Available workflows:"
n8n list:workflow 2>/dev/null | while IFS='|' read -r id name; do
    echo "   - $name"
done
