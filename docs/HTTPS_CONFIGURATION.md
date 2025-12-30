# HTTPS/TLS Configuration Guide for RIN

This guide explains how to enable HTTPS/TLS encryption for all RIN services.

## Overview

RIN provides multiple options for HTTPS/TLS encryption:

1. **Automatic HTTPS with Let's Encrypt** (RECOMMENDED) - Zero configuration, fully automated
2. **Manual HTTPS Setup** - Use your own reverse proxy and certificates
3. **HTTP Only** - For local development

HTTPS is especially important for:
- Production deployments
- Accessing RIN over the internet
- Compliance requirements
- Preventing man-in-the-middle attacks

## Automatic HTTPS with Let's Encrypt (RECOMMENDED)

### Overview

The easiest way to enable HTTPS is using the built-in automatic HTTPS feature powered by Caddy and Let's Encrypt. This provides:

✅ **Zero Configuration** - Just provide your domain and email
✅ **Automatic Certificate Issuance** - Caddy obtains certificates from Let's Encrypt
✅ **Automatic Renewal** - Certificates renew before expiration
✅ **No Manual Management** - Everything is handled automatically

### Requirements

Before enabling automatic HTTPS, ensure:

1. **Domain Name**: You own a domain name (e.g., `magi.example.com`)
2. **DNS Configuration**: Your domain points to your server's public IP
3. **Open Ports**: Ports 80 and 443 are accessible from the internet
4. **Valid Email**: For Let's Encrypt notifications

### Quick Setup

**Option 1: During Initial Setup**

When running `./rin start` for the first time, select option 1 for automatic HTTPS:

```bash
./rin start

# When prompted:
🔒 HTTPS/TLS Configuration

Choose your HTTPS setup:
1. Automatic HTTPS with Let's Encrypt (RECOMMENDED for production)
2. Manual HTTPS setup (for custom reverse proxy)
3. HTTP only (for local development)

Select option [1/2/3]: 1
```

**Option 2: Setup After Installation**

Run the automatic HTTPS setup script:

```bash
./rin setup-https
```

You'll be prompted for:
- Your domain name (e.g., `magi.example.com`)
- Your email address (for Let's Encrypt notifications)
- Whether to use staging (for testing)

### DNS Configuration

Before running setup, configure DNS A records pointing to your server's public IP:

```
magi.example.com     → YOUR_SERVER_IP
n8n.magi.example.com → YOUR_SERVER_IP
search.magi.example.com → YOUR_SERVER_IP
api.magi.example.com → YOUR_SERVER_IP
```

### Testing with Let's Encrypt Staging

To avoid rate limits while testing (50 certificates per domain per week), use the staging environment:

```bash
./rin setup-https
# When prompted, answer 'y' to "Use Let's Encrypt STAGING for testing?"
```

⚠️ **Note**: Staging certificates are not trusted by browsers. Switch to production once testing is complete.

### Access Your Services

After setup completes and services start, access via HTTPS:

```
🧠 Cortex (Open WebUI):  https://magi.example.com
🔄 Reflex (n8n):         https://n8n.magi.example.com
🔍 Vision (SearXNG):     https://search.magi.example.com
🚦 API (LiteLLM):        https://api.magi.example.com
```

Certificates are obtained automatically on first access!

## Manual HTTPS Setup

For advanced users who want to use their own reverse proxy configuration.

### Architecture

```
Internet → [Reverse Proxy with SSL] → [RIN Services over HTTP]
          (nginx/Traefik/Caddy)        (Docker containers)
```

### 1. Generate SSL Certificates

For development and testing, generate self-signed certificates:

```bash
./scripts/generate-certs.sh
```

This creates:
- `config/ssl/cert.pem` - SSL certificate
- `config/ssl/key.pem` - Private key
- `config/ssl/ca.pem` - Certificate Authority (self-signed)

**Note:** Self-signed certificates will trigger browser security warnings. This is expected and safe for development.

### 2. Set Up Reverse Proxy (Required)

**HTTPS requires a reverse proxy for SSL termination.** Choose one:

**Option A: nginx (Recommended for production)**

Create `/etc/nginx/sites-available/rin`:

```nginx
server {
    listen 443 ssl http2;
    server_name localhost;  # Change to your domain for production

    ssl_certificate /path/to/rin/config/ssl/cert.pem;
    ssl_certificate_key /path/to/rin/config/ssl/key.pem;

    # Open WebUI
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart nginx:
```bash
sudo ln -s /etc/nginx/sites-available/rin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Option B: Traefik (Easier for Docker)**

Add to `docker-compose.yml`:
```yaml
  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker=true"
      - "--entrypoints.websecure.address=:443"
    ports:
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./config/ssl:/certs:ro
```

**Option C: Caddy (Automatic HTTPS)**

Create `Caddyfile`:
```
localhost {
    reverse_proxy localhost:3000
    tls /path/to/rin/config/ssl/cert.pem /path/to/rin/config/ssl/key.pem
}
```

See the "Reverse Proxy Setup" section below for complete examples.

### 3. Enable HTTPS Mode in RIN

Edit your `.env` file:

```bash
nano .env
```

Set `ENABLE_HTTPS` to `true`:

```bash
ENABLE_HTTPS=true
```

This configures RIN's internal tools to generate HTTPS URLs when communicating with the reverse proxy.

### 4. Restart RIN

```bash
./rin restart
# or
./start.sh
```

### 5. Access Services via Reverse Proxy

With your reverse proxy configured, access services through HTTPS:

- **Open WebUI (Cortex)**: https://localhost (via reverse proxy)
- **Direct service access**: http://localhost:3000 (still HTTP, behind proxy)
- **MCP Bridge**: https://localhost:9000
- **YouTube MCP**: https://localhost:9001

## Production Setup

### Using Let's Encrypt Certificates

For production deployments, use proper CA-signed certificates from Let's Encrypt:

1. **Install Certbot:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install certbot

# macOS
brew install certbot
```

2. **Generate Certificates:**

```bash
sudo certbot certonly --standalone -d yourdomain.com
```

3. **Copy Certificates to RIN:**

```bash
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./config/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./config/ssl/key.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/chain.pem ./config/ssl/ca.pem
sudo chown $USER:$USER ./config/ssl/*.pem
```

4. **Set Up Auto-Renewal:**

```bash
# Add to crontab
0 0 * * 0 certbot renew --quiet && ./rin restart
```

### Using Custom Certificates

If you have certificates from another Certificate Authority:

1. Place your certificate files in `config/ssl/`:
   - `cert.pem` - Your domain certificate
   - `key.pem` - Your private key
   - `ca.pem` - CA certificate chain

2. Update `.env` if using different paths:

```bash
SSL_CERT_PATH=./config/ssl/custom-cert.pem
SSL_KEY_PATH=./config/ssl/custom-key.pem
SSL_CA_PATH=./config/ssl/custom-ca.pem
```

3. Restart RIN:

```bash
./rin restart
```

## Configuration Options

### Environment Variables

Add these to your `.env` file:

```bash
# Enable/Disable HTTPS
ENABLE_HTTPS=true                      # Set to 'true' or 'false'

# SSL Certificate Paths (relative to project root)
SSL_CERT_PATH=./config/ssl/cert.pem    # Path to SSL certificate
SSL_KEY_PATH=./config/ssl/key.pem      # Path to private key
SSL_CA_PATH=./config/ssl/ca.pem        # Path to CA certificate

# HTTPS Ports (optional, defaults shown)
PORT_WEBUI_HTTPS=3443                  # Open WebUI HTTPS port
PORT_LITELLM_HTTPS=4443                # LiteLLM HTTPS port
PORT_SEARXNG_HTTPS=8443                # SearXNG HTTPS port
PORT_FIRECRAWL_HTTPS=3003              # FireCrawl HTTPS port
PORT_N8N_HTTPS=5679                    # n8n HTTPS port
PORT_QDRANT_HTTPS=6334                 # Qdrant HTTPS port
PORT_MCP_BRIDGE_HTTPS=9443             # MCP Bridge HTTPS port
PORT_YOUTUBE_MCP_HTTPS=9444            # YouTube MCP HTTPS port
```

### Interactive Setup

When running `./start.sh` for the first time, you'll be prompted:

```
🔒 HTTPS/TLS Configuration
   Enable HTTPS for secure communication (requires SSL certificates)
   Use HTTP for local development, HTTPS for production

   Enable HTTPS? [y/N]:
```

Answer `y` to enable HTTPS. If certificates don't exist, they'll be generated automatically.

## Service-Specific Configuration

### n8n (Workflow Automation)

n8n uses a custom entrypoint script (`scripts/docker-entrypoints/n8n-entrypoint.sh`) that automatically configures:

- `N8N_PROTOCOL` - Set to `https` or `http`
- `N8N_SECURE_COOKIE` - Enabled for HTTPS, disabled for HTTP
- `WEBHOOK_URL` - Webhook base URL with correct protocol
- `N8N_EDITOR_BASE_URL` - Editor URL with correct protocol

These are configured automatically based on `ENABLE_HTTPS`.

### LiteLLM (API Router)

LiteLLM reads SSL certificate paths from environment variables and automatically enables HTTPS when `ENABLE_HTTPS=true`.

### Qdrant (Vector Database)

Qdrant supports TLS natively and will use the mounted certificates when HTTPS is enabled.

### Open WebUI

Open WebUI can serve content over HTTPS when certificates are provided, though it typically runs behind a reverse proxy in production.

## Tool Integration

All RIN tools automatically detect and use HTTPS when enabled:

- **n8n_reflex.py** - Auto-detects protocol for webhook URLs
- **firecrawl_scraper.py** - Auto-detects protocol for API requests
- **qdrant_memory.py** - Auto-detects protocol for vector DB connections
- **searxng_search.py** - Auto-detects protocol for search queries

No manual configuration is needed - tools read `ENABLE_HTTPS` from the environment.

## Troubleshooting

### Browser Security Warnings

**Symptom:** Browser shows "Your connection is not private" or similar warning.

**Solution:** This is expected with self-signed certificates. You can:

1. **Development:** Click "Advanced" → "Proceed to localhost" (safe for local development)
2. **Production:** Use proper CA-signed certificates from Let's Encrypt or another CA

### Certificate Permission Errors

**Symptom:** Docker containers can't read certificate files.

**Solution:** Ensure correct permissions:

```bash
chmod 644 ./config/ssl/cert.pem
chmod 644 ./config/ssl/ca.pem
chmod 600 ./config/ssl/key.pem  # Keep private key secure
```

### Service Not Starting

**Symptom:** Service fails to start after enabling HTTPS.

**Solution:**

1. Check certificate paths are correct in `.env`
2. Verify certificates exist: `ls -la config/ssl/`
3. Check Docker logs: `docker logs rin-cortex` (or other service name)
4. Regenerate certificates: `./scripts/generate-certs.sh`

### Mixed Content Warnings

**Symptom:** Some resources fail to load with "mixed content" errors.

**Solution:** Ensure all internal service URLs use the same protocol. Tools should auto-detect, but you can verify by checking tool configurations in Open WebUI → Workspace → Tools.

## Reverse Proxy Setup

For production, it's recommended to use a reverse proxy (nginx, Traefik, Caddy) in front of RIN:

### Example: Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Open WebUI
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # n8n
    location /n8n/ {
        proxy_pass http://localhost:5678/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

In this setup, RIN can run with HTTP internally, and nginx handles SSL termination.

## Security Best Practices

1. **Use Strong Certificates:** For production, always use CA-signed certificates (Let's Encrypt is free and automated)

2. **Keep Certificates Updated:** Set up auto-renewal for Let's Encrypt certificates

3. **Restrict Private Key Access:** Keep `key.pem` permissions at 600 (read/write for owner only)

4. **Use HTTPS in Production:** Never expose RIN to the internet over HTTP

5. **Regular Updates:** Keep RIN and all services updated for security patches

6. **Firewall Configuration:** Use firewall rules to restrict access to RIN services

7. **Strong Passwords:** Use strong passwords for Open WebUI and n8n accounts

8. **API Key Security:** Never commit API keys to version control

## Performance Considerations

Enabling HTTPS adds a small overhead for TLS encryption/decryption. For most use cases, this is negligible. However:

- **Local Development:** HTTP is faster and simpler
- **Production:** HTTPS is essential for security
- **Internal Services:** Consider using HTTP for internal service-to-service communication within Docker network, and HTTPS only for external-facing endpoints

## Disabling HTTPS

To switch back to HTTP:

1. Edit `.env`:

```bash
ENABLE_HTTPS=false
```

2. Restart RIN:

```bash
./rin restart
```

All services will return to using HTTP.

## Support

For issues or questions about HTTPS configuration:

- Check logs: `./rin logs [service-name]`
- Review documentation: [README.md](../README.md)
- Report issues: [GitHub Issues](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/issues)
- Discuss: [GitHub Discussions](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/discussions)

---

**Remember:** HTTPS is strongly recommended for any production deployment or when accessing RIN over the internet.
