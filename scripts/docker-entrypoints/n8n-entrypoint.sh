#!/bin/sh
# n8n entrypoint wrapper to configure HTTPS/HTTP dynamically and auto-import workflows
set -e

# Determine protocol based on ENABLE_HTTPS environment variable
if [ "${ENABLE_HTTPS}" = "true" ]; then
    export N8N_PROTOCOL="https"
    export N8N_SECURE_COOKIE="true"
    
    # Set webhook and editor URLs based on port
    N8N_PORT=${N8N_PORT:-5678}
    export WEBHOOK_URL="https://localhost:${N8N_PORT}"
    export N8N_EDITOR_BASE_URL="https://localhost:${N8N_PORT}"
    
    echo "n8n starting with HTTPS enabled"
    echo "   SSL Certificate: ${N8N_SSL_CERT}"
    echo "   SSL Key: ${N8N_SSL_KEY}"
else
    export N8N_PROTOCOL="http"
    export N8N_SECURE_COOKIE="false"
    
    # Set webhook and editor URLs based on port
    N8N_PORT=${N8N_PORT:-5678}
    export WEBHOOK_URL="http://localhost:${N8N_PORT}"
    export N8N_EDITOR_BASE_URL="http://localhost:${N8N_PORT}"
    
    echo "n8n starting with HTTP (development mode)"
fi

# Auto-import workflows from /workflows directory on first run
WORKFLOWS_DIR="/workflows"
IMPORT_MARKER="/home/node/.n8n/.workflows_imported"

if [ -d "$WORKFLOWS_DIR" ] && [ ! -f "$IMPORT_MARKER" ]; then
    echo "Importing MAGI workflows from $WORKFLOWS_DIR..."
    
    # Wait for n8n database to be ready (run import after n8n starts)
    # We'll use a background process that waits and imports
    (
        # Wait for n8n to be ready
        sleep 30
        
        # Import all workflow JSON files
        for workflow in "$WORKFLOWS_DIR"/*.json; do
            if [ -f "$workflow" ]; then
                echo "Importing workflow: $(basename "$workflow")"
                n8n import:workflow --input="$workflow" 2>/dev/null || echo "  (may already exist)"
            fi
        done
        
        # Mark as imported (activation must be done manually in n8n UI)
        touch "$IMPORT_MARKER"
        echo "MAGI workflows imported successfully"
        echo "NOTE: Activate workflows in n8n UI: http://localhost:5678"
    ) &
fi

# Execute the original n8n entrypoint
exec /docker-entrypoint.sh "$@"
