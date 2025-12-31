# n8n Setup Guide for MAGI

This guide will help you set up n8n with the custom MAGI Docker image, including Tailscale configuration.

## Quick Start

### 1. Build and Start Services

```bash
# Build the custom n8n image
docker compose build n8n

# Start n8n and the proxy
docker compose up -d n8n n8n-proxy

# Check status
docker compose ps
```

### 2. Access n8n

**Local Access:**
- Via Proxy (recommended): http://localhost:8081
- Direct Backend: http://localhost:5678

**Tailscale Access:**
- Via Proxy: http://YOUR-TAILSCALE-IP:8081

## Tailscale Configuration

If you're using Tailscale, configure the following in your `.env` file:

```bash
# Replace 100.75.7.93 with your actual Tailscale IP
N8N_HOST=100.75.7.93
N8N_PROTOCOL=http
N8N_EDITOR_BASE_URL=http://100.75.7.93:8081
N8N_WEBHOOK_URL=http://100.75.7.93:8081/
```

After updating `.env`, restart the services:

```bash
docker compose restart n8n n8n-proxy
```

## Port Configuration

By default, the following ports are used:

- **5678**: n8n backend (internal API)
- **8081**: n8n proxy (frontend access)

You can change these in your `.env` file:

```bash
PORT_N8N=5678          # Backend port
PORT_N8N_PROXY=8081    # Proxy port
```

## Architecture

```
User Browser
    ↓
Port 8081 (nginx proxy)
    ↓
Port 5678 (n8n backend)
```

The nginx proxy provides:
- WebSocket support for real-time updates
- Buffer management for large API responses
- Separation of concerns between frontend and backend

## First-Time Setup

1. **Access the UI** via http://localhost:8081 (or your Tailscale IP)
2. **Create an admin account** when prompted
3. **Configure credentials** for your integrations
4. **Import workflows** from the `/workflows` directory (if any)

## Verifying the Installation

Run the automated test script:

```bash
./docker/n8n/test.sh
```

This will verify:
- ✓ Containers are running
- ✓ Health endpoints are responding
- ✓ UI is accessible
- ✓ Proxy is working correctly

## Troubleshooting

### Issue: n8n container keeps restarting

**Solution**: Check permissions on the data directory:

```bash
sudo chown -R 1000:1000 data/n8n
docker compose restart n8n
```

### Issue: Cannot access n8n UI

**Solution**: Check if the services are running:

```bash
docker compose ps
docker logs magi-reflex-automation
docker logs magi-n8n-proxy
```

### Issue: Webhooks not working with Telegram

**Solution**: Ensure `N8N_WEBHOOK_URL` is set to your externally accessible URL:

```bash
# In .env file
N8N_WEBHOOK_URL=http://your-tailscale-ip:8081/
```

### Issue: "Cannot GET /rest/credential-types" error

This is **expected behavior** before logging in. The REST API endpoints require authentication. Once you:
1. Access the UI at http://localhost:8081
2. Create an admin account
3. Log in

The REST API endpoints will work correctly with proper authentication headers.

## Updating n8n

To update to the latest version of n8n:

```bash
# Pull latest image
docker pull n8nio/n8n:latest

# Rebuild custom image
docker compose build n8n

# Restart services
docker compose up -d n8n n8n-proxy
```

## Data Persistence

n8n data is stored in `./data/n8n/` directory:
- Workflows
- Credentials
- Execution history
- Settings

**Important**: Back up this directory regularly to prevent data loss.

## Security Considerations

### Production Deployment

For production use:

1. **Use HTTPS**: Configure SSL/TLS certificates
2. **Set Strong Passwords**: Use complex admin passwords
3. **Limit Access**: Use firewall rules to restrict access
4. **Regular Backups**: Automate backups of the data directory
5. **Update Regularly**: Keep n8n updated to latest stable version

### Tailscale Security

When using Tailscale:
- Your n8n instance is only accessible within your Tailscale network
- No public ports need to be opened
- End-to-end encryption provided by Tailscale

## Additional Resources

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community Forum](https://community.n8n.io/)
- [MAGI Documentation](../../docs/)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Run the test script: `./docker/n8n/test.sh`
3. Check logs: `docker logs magi-reflex-automation`
4. Review the README: `docker/n8n/README.md`
