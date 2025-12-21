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

# Check if already imported using hash of workflow filenames instead of count
WORKFLOW_HASH=$(find "$WORKFLOWS_DIR" -name "*.json" -type f -exec basename {} \; 2>/dev/null | sort | md5sum | cut -d' ' -f1)
if [ -f "$IMPORT_MARKER" ]; then
    MARKER_HASH=$(cat "$IMPORT_MARKER" 2>/dev/null || echo "")
    if [ "$MARKER_HASH" = "$WORKFLOW_HASH" ]; then
        echo "ℹ️  Workflows already imported ($WORKFLOW_COUNT workflows). Skipping."
        exit 0
    fi
fi

echo "🔄 Importing $WORKFLOW_COUNT workflows from $WORKFLOWS_DIR..."

# Import all workflows and check exit status
n8n import:workflow --separate --input="$WORKFLOWS_DIR" 2>&1 | grep -v "Could not find workflow" | grep -v "Could not remove webhooks"
IMPORT_EXIT_CODE=${PIPESTATUS[0]}

if [ "$IMPORT_EXIT_CODE" -ne 0 ]; then
    echo "❌ Workflow import failed with exit code $IMPORT_EXIT_CODE."
    exit "$IMPORT_EXIT_CODE"
fi

# Mark as imported with hash
echo "$WORKFLOW_HASH" > "$IMPORT_MARKER"

echo "✅ Workflows imported successfully."

# List imported workflows with robust parsing
echo ""
echo "📋 Available workflows:"
n8n list:workflow 2>/dev/null | while IFS= read -r line; do
    # Skip empty lines and obvious header/separator lines
    [ -z "$line" ] && continue
    case "$line" in
        -*|'='*|ID*Name*|id*name*) continue ;;
    esac

    name=""

    if printf '%s\n' "$line" | grep -q '|'; then
        # Pipe-delimited table format: assume second column is the name
        name=$(printf '%s\n' "$line" | awk -F'|' 'NF>=2 {gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}')
    else
        # Fallback: treat first whitespace-separated field as ID and the rest as name
        name=$(printf '%s\n' "$line" | awk '{ $1=""; sub(/^[ \t]+/, ""); print }')
    fi

    # Only print if we successfully extracted a non-empty name
    [ -n "$name" ] && echo "   - $name"
done
