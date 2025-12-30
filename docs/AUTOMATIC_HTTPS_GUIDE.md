# Automatic HTTPS Setup Guide

This guide walks through setting up automatic HTTPS for MAGI using Let's Encrypt and Caddy.

## What You Get

✅ **Fully Automatic SSL Certificates** - Caddy obtains certificates from Let's Encrypt  
✅ **Zero Manual Management** - Certificates renew automatically before expiration  
✅ **Production-Ready Security** - TLS 1.3, HTTP/2, HTTP/3 support  
✅ **Multiple Services** - Main domain + subdomains for all services  
✅ **One Command Setup** - Just run `./magi setup-https` and answer prompts  

## Before You Begin

### Requirements

1. **Domain Name**: You must own a domain (e.g., `magi.example.com`)
2. **Server with Public IP**: Your server must be accessible from the internet
3. **DNS Configuration**: Domain must point to your server's IP
4. **Open Firewall Ports**: Ports 80 and 443 must be accessible

### DNS Setup

Configure these DNS A records to point to your server's IP:

```
magi.example.com     → YOUR_SERVER_IP
n8n.magi.example.com → YOUR_SERVER_IP
search.magi.example.com → YOUR_SERVER_IP
api.magi.example.com → YOUR_SERVER_IP
```

Replace `YOUR_SERVER_IP` with your actual server IP address.

To find your server's public IP:
```bash
curl ifconfig.me
```

### Firewall Configuration

Ensure these ports are open:
- **Port 80** (HTTP) - Required for Let's Encrypt ACME challenge
- **Port 443** (HTTPS) - For secure traffic
- **Port 443 UDP** (optional) - For HTTP/3 support

For UFW (Ubuntu):
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 443/udp
```

For firewalld (RHEL/CentOS):
```bash
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## Setup Methods

### Method 1: During Initial Installation (Recommended)

Run the start script:
```bash
./magi start
```

When prompted for HTTPS configuration, select option 1:
```
🔒 HTTPS/TLS Configuration

Choose your HTTPS setup:
1. Automatic HTTPS with Let's Encrypt (RECOMMENDED for production)
2. Manual HTTPS setup (for custom reverse proxy)
3. HTTP only (for local development)

Select option [1/2/3]: 1
```

Follow the prompts to enter your domain and email.

### Method 2: After Installation

If MAGI is already installed, run:
```bash
./magi setup-https
```

The script will guide you through:
1. Domain name configuration
2. Administrator email (for Let's Encrypt notifications)
3. Production vs staging environment selection

## Step-by-Step Walkthrough

### 1. Run Setup Script

```bash
./magi setup-https
```

### 2. Enter Domain Name

```
Domain name: magi.example.com
```

Enter your fully qualified domain name (FQDN).

### 3. Verify DNS

The script will show your server's IP and ask for confirmation:

```
⚠️  IMPORTANT: Make sure your DNS is configured correctly
   magi.example.com → 203.0.113.45

Is this correct? [y/N]: y
```

Verify your DNS is pointing to the correct IP before proceeding.

### 4. Enter Email

```
Email address: admin@example.com
```

This email receives Let's Encrypt notifications (rarely needed - mainly for renewal failures).

### 5. Choose Environment

```
Use Let's Encrypt STAGING for testing? [y/N]: n
```

- **Production** (default): Real certificates trusted by browsers
- **Staging**: For testing, avoids rate limits but not trusted by browsers

Choose staging first if you're testing the setup.

### 6. Review Configuration

The script generates:
- `config/caddy/Caddyfile` - Caddy configuration
- Updates `.env` with domain and email

### 7. Start MAGI

```bash
./magi start
```

Caddy will automatically obtain SSL certificates when you first access your domain!

## Accessing Your Services

After setup, access your services via HTTPS:

- **🧠 Cortex (Open WebUI)**: `https://magi.example.com`
- **🔄 Reflex (n8n)**: `https://n8n.magi.example.com`
- **🔍 Vision (SearXNG)**: `https://search.magi.example.com`
- **🚦 Router (LiteLLM)**: `https://api.magi.example.com`

## Certificate Management

### Automatic Renewal

Caddy automatically renews certificates 60 days before expiration. No action required!

### Check Certificate Status

View Caddy logs to see certificate activity:
```bash
./magi logs caddy
```

### Force Certificate Renewal

Normally not needed, but if you want to force renewal:
```bash
docker exec magi-caddy caddy reload --config /etc/caddy/Caddyfile
```

## Troubleshooting

### Problem: DNS Not Resolving

**Symptoms**: Cannot obtain certificate, "DNS problem: NXDOMAIN" error

**Solution**:
1. Verify DNS with: `dig magi.example.com`
2. Wait for DNS propagation (up to 48 hours)
3. Check your domain registrar's DNS settings

### Problem: Port 80/443 Not Accessible

**Symptoms**: "connection refused" or timeout errors

**Solution**:
1. Check firewall: `sudo ufw status`
2. Verify ports are open: `netstat -tuln | grep -E ':(80|443)'`
3. Check cloud provider security groups (AWS, GCP, Azure)

### Problem: Rate Limit Errors

**Symptoms**: "too many certificates already issued"

**Solution**:
- Use staging environment: `./magi setup-https` and answer 'y' to staging
- Wait for rate limit reset (7 days for most limits)
- See [Let's Encrypt Rate Limits](https://letsencrypt.org/docs/rate-limits/)

### Problem: Certificate Not Trusted

**Symptoms**: Browser shows "Not Secure" or certificate error

**Solution**:
1. Verify you're using production (not staging) certificates
2. Check certificate with: `curl -vI https://magi.example.com`
3. Ensure domain matches certificate CN

### Problem: Subdomain Not Working

**Symptoms**: Main domain works but subdomains don't

**Solution**:
1. Verify DNS records for all subdomains
2. Check Caddyfile includes subdomain configuration
3. Restart Caddy: `./magi restart`

## Switching Between Staging and Production

### From Staging to Production

1. Edit `config/caddy/Caddyfile`:
   ```bash
   nano config/caddy/Caddyfile
   ```

2. Comment staging line, uncomment production line:
   ```
   # Production
   acme_ca https://acme-v02.api.letsencrypt.org/directory
   
   # Staging (for testing)
   # acme_ca https://acme-staging-v02.api.letsencrypt.org/directory
   ```

3. Delete old certificates:
   ```bash
   rm -rf data/caddy/data/caddy/certificates/acme.zerossl.com-*
   rm -rf data/caddy/data/caddy/certificates/acme-staging*
   ```

4. Restart:
   ```bash
   ./magi restart
   ```

### From Production to Staging

Same steps, but reverse the comments in the Caddyfile.

## Advanced Configuration

### Custom Subdomains

To add more subdomains, edit `config/caddy/Caddyfile.template`:

```
# Custom subdomain
custom.{DOMAIN} {
    reverse_proxy custom-service:8080 {
        header_up Host {host}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}
```

Then regenerate: `./magi setup-https`

### Custom SSL Settings

Edit the global options in `config/caddy/Caddyfile`:

```
{
    # Add custom TLS options
    tls {
        protocols tls1.3
        ciphers TLS_AES_256_GCM_SHA384
    }
}
```

### HTTP to HTTPS Redirect

Caddy automatically redirects HTTP to HTTPS. No configuration needed!

## Security Best Practices

1. **Keep Software Updated**: Regularly update MAGI and Caddy
2. **Monitor Logs**: Check `./magi logs caddy` for suspicious activity
3. **Use Strong Passwords**: Secure Open WebUI and n8n accounts
4. **Backup Certificates**: Include `data/caddy/` in backups
5. **Email Monitoring**: Watch for Let's Encrypt expiration emails

## Performance

### HTTP/3 (QUIC)

Caddy enables HTTP/3 by default on port 443 UDP. This provides:
- Faster connection establishment
- Better performance on poor networks
- Multiplexed streams without head-of-line blocking

### Connection Pooling

Caddy maintains connection pools to backend services for optimal performance.

### Caching

For production deployments, consider adding caching headers in Caddyfile:

```
header {
    Cache-Control "public, max-age=3600"
}
```

## Disabling Automatic HTTPS

To switch back to HTTP:

1. Edit `.env`:
   ```bash
   ENABLE_AUTO_HTTPS=false
   ```

2. Restart:
   ```bash
   ./magi restart
   ```

The Caddy container will not start when `ENABLE_AUTO_HTTPS=false`.

## Getting Help

### Check Logs
```bash
./magi logs caddy
./magi logs caddy -f  # Follow logs
```

### View Status
```bash
./magi status
```

### Test Certificate
```bash
curl -vI https://magi.example.com
```

### Community Support
- [GitHub Issues](https://github.com/radkisson/MAGI/issues)
- [GitHub Discussions](https://github.com/radkisson/MAGI/discussions)

## Resources

- [Caddy Documentation](https://caddyserver.com/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [HTTPS Configuration Guide](../docs/HTTPS_CONFIGURATION.md)
- [Caddy Configuration README](../config/caddy/README.md)

---

**That's it!** With automatic HTTPS, you get enterprise-grade security with zero manual certificate management. 🔒✨
