#!/bin/sh
# n8n entrypoint wrapper to configure HTTPS/HTTP dynamically
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

# Execute the original n8n entrypoint
exec /docker-entrypoint.sh "$@"
