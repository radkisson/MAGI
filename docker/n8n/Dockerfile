# Custom n8n Docker Image for MAGI
# Based on official n8n image with customizations for out-of-the-box functionality

FROM n8nio/n8n:latest

# Set to root temporarily for installations
USER root

# Install additional system dependencies if needed
RUN apk add --no-cache \
    python3 \
    py3-pip \
    git \
    curl \
    bash

# Install Python packages that may be useful for n8n workflows
RUN pip3 install --no-cache-dir \
    requests \
    beautifulsoup4 \
    pandas \
    numpy

# Create necessary directories with proper permissions
RUN mkdir -p /home/node/.n8n/nodes \
    && chown -R node:node /home/node/.n8n

# Switch back to node user for security
USER node

# Set working directory
WORKDIR /home/node

# Environment variables for configuration
ENV N8N_PORT=5678
ENV N8N_PROTOCOL=http
ENV N8N_HOST=0.0.0.0
ENV EXECUTIONS_PROCESS=main
ENV N8N_METRICS=false
ENV NODE_ENV=production

# Health check to ensure n8n is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:5678/healthz || exit 1

# Expose the n8n port
EXPOSE 5678

# Use the default n8n entrypoint
ENTRYPOINT ["tini", "--", "/docker-entrypoint.sh"]
CMD ["n8n"]
