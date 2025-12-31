# Custom n8n Docker Image for MAGI
# Based on official n8n image - using latest stable version
# This ensures all REST API endpoints (including /rest/credential-types) work correctly

FROM n8nio/n8n:latest

# Environment variables for configuration
ENV N8N_PORT=5678
ENV N8N_PROTOCOL=http
ENV N8N_HOST=0.0.0.0
ENV N8N_METRICS=false
ENV NODE_ENV=production

# Health check to ensure n8n is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:5678/healthz || exit 1

# Expose the n8n port
EXPOSE 5678
