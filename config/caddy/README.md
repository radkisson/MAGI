# Automatic HTTPS with Let's Encrypt

This directory contains the configuration for automatic HTTPS using Caddy and Let's Encrypt.

## Overview

MAGI can automatically obtain and renew SSL certificates from Let's Encrypt using Caddy as a reverse proxy. No manual certificate management is required!

## Features

- ✅ **Zero Configuration**: Just provide your domain and email
- ✅ **Automatic Certificate Issuance**: Caddy obtains certificates from Let's Encrypt
- ✅ **Automatic Renewal**: Certificates renew before expiration (60 days before)
- ✅ **No Manual Management**: Everything is handled automatically
- ✅ **Multiple Subdomains**: Supports main domain and service subdomains
- ✅ **HTTP/3 Support**: Includes HTTP/3 (QUIC) support

## Files

- `Caddyfile.template`: Template for Caddy configuration with placeholders
- `Caddyfile`: Generated configuration (created by setup script)

## Quick Setup

1. **Run the setup script:**
   ```bash
   ./rin setup-https
   ```

2. **Provide your information:**
   - Domain name (e.g., `magi.example.com`)
   - Email address (for Let's Encrypt notifications)
   - Choose production or staging environment

3. **Configure DNS:**
   Ensure your domain and subdomains point to your server:
   ```
   magi.example.com     → YOUR_SERVER_IP
   n8n.magi.example.com → YOUR_SERVER_IP
   search.magi.example.com → YOUR_SERVER_IP
   api.magi.example.com → YOUR_SERVER_IP
   ```

4. **Start MAGI:**
   ```bash
   ./rin start
   ```

Caddy will automatically obtain SSL certificates on first access!

## Supported Services

The automatic HTTPS setup configures reverse proxy for:

- **Main Domain**: Open WebUI (Cortex)
- **n8n.domain**: n8n (Reflex)
- **search.domain**: SearXNG (Vision)
- **api.domain**: LiteLLM (Router)

## Port Requirements

Ensure these ports are open and accessible from the internet:

- **Port 80**: Required for ACME HTTP-01 challenge
- **Port 443**: HTTPS traffic
- **Port 443 UDP**: HTTP/3 (optional but recommended)

## Testing with Staging

Let's Encrypt has rate limits (50 certificates per domain per week). For testing, use the staging environment:

```bash
./rin setup-https
# Answer 'y' to "Use Let's Encrypt STAGING for testing?"
```

⚠️ **Note**: Staging certificates are not trusted by browsers.

## Switching to Production

To switch from staging to production certificates:

1. Edit `config/caddy/Caddyfile`
2. Comment the staging line and uncomment the production line:
   ```
   # Production (uncomment this)
   acme_ca https://acme-v02.api.letsencrypt.org/directory
   
   # Staging (comment this)
   # acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
   ```
3. Restart: `./rin restart`

## Certificate Storage

Certificates are stored in:
- `data/caddy/data/`: Certificate data
- `data/caddy/config/`: Caddy configuration

These directories are persistent across restarts.

## Troubleshooting

### Certificate Obtainment Fails

**Problem**: Caddy cannot obtain certificates

**Solutions**:
1. Verify DNS points to your server: `dig magi.example.com`
2. Check ports 80 and 443 are open: `netstat -tuln | grep -E ':(80|443)'`
3. Ensure domain is accessible: `curl -I http://magi.example.com`
4. Check Caddy logs: `./rin logs caddy`

### Rate Limit Errors

**Problem**: "too many certificates already issued"

**Solution**: Use staging environment for testing, or wait for rate limit to reset (usually 1 week)

### DNS Not Resolving

**Problem**: Domain doesn't resolve to server

**Solution**: 
1. Check DNS propagation: `dig magi.example.com`
2. Wait for DNS propagation (can take up to 48 hours)
3. Verify DNS records are correct in your domain registrar

## Manual Configuration

If you need to customize the Caddyfile:

1. Edit `config/caddy/Caddyfile.template` for permanent changes
2. Or edit `config/caddy/Caddyfile` for one-time changes
3. Restart: `./rin restart`

## Security Notes

- Certificates are renewed automatically 60 days before expiration
- Email notifications are sent if renewal fails
- Private keys are stored securely in `data/caddy/data/`
- All HTTP traffic is automatically redirected to HTTPS

## See Also

- [HTTPS Configuration Guide](../../docs/HTTPS_CONFIGURATION.md)
- [Caddy Documentation](https://caddyserver.com/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
