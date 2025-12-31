# Custom n8n Docker Image for MAGI

This directory contains a custom n8n Docker image that provides out-of-the-box functionality for MAGI.

## Features

- Based on the latest official `n8nio/n8n` image
- Includes Python 3 and pip for Python-based workflows
- Pre-installed Python packages: requests, beautifulsoup4, pandas, numpy
- Includes git, curl, and bash for enhanced workflow capabilities
- Properly configured health checks
- Optimized for production use

## Building the Image

The image is automatically built when you run:

```bash
docker-compose build n8n
```

Or to build manually:

```bash
cd docker/n8n
docker build -t magi-n8n:latest .
```

## Configuration

The n8n service is configured in `docker-compose.yml` with the following key features:

- **Backend Port**: 5678 (internal)
- **Proxy Port**: 8081 (external, recommended for access)
- **Data Persistence**: `./data/n8n` mounted to `/home/node/.n8n`
- **Workflows**: `./workflows` mounted as read-only

## Tailscale Configuration

For Tailscale network access, configure the following in your `.env` file:

```bash
# Replace with your Tailscale IP
N8N_HOST=100.75.7.93
N8N_PROTOCOL=http
N8N_EDITOR_BASE_URL=http://100.75.7.93:8081
N8N_WEBHOOK_URL=http://100.75.7.93:8081/
```

## Accessing n8n

- **Via Proxy (Recommended)**: http://localhost:8081 or http://your-tailscale-ip:8081
- **Direct Backend**: http://localhost:5678 (for debugging only)

## Proxy Setup

An nginx proxy (`n8n-proxy` service) is included to:
- Handle WebSocket connections properly
- Provide a stable frontend endpoint
- Separate backend and frontend concerns

## Verifying the Installation

After starting the services, verify that all REST endpoints are working:

```bash
# Check health
curl http://localhost:8081/healthz

# Check credential types endpoint (should return JSON, not 404)
curl http://localhost:8081/rest/credential-types

# Check workflows endpoint
curl http://localhost:8081/rest/workflows
```

## Troubleshooting

### Frontend shows "data.filter is not a function" error

This usually means the backend isn't serving the REST API endpoints properly. Check:

1. Backend is running: `docker logs magi-reflex-automation`
2. Endpoints are accessible: `curl http://localhost:5678/rest/credential-types`
3. Proxy is forwarding correctly: `docker logs magi-n8n-proxy`

### Webhooks not working with Telegram

Ensure `N8N_WEBHOOK_URL` is set to your externally accessible URL:

```bash
N8N_WEBHOOK_URL=http://your-tailscale-ip:8081/
```

## Python Package Management

To add more Python packages for workflows, edit the Dockerfile and rebuild:

```dockerfile
RUN pip3 install --no-cache-dir \
    your-package-here
```

Then rebuild: `docker-compose build n8n`
