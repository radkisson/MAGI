# Jupyter Lab Security Configuration

This document provides security guidance for Jupyter Lab in the MAGI stack.

## Default Configuration (Development)

The default Jupyter configuration is optimized for **local development** and prioritizes convenience:

- ✗ No authentication (JUPYTER_TOKEN is empty)
- ✗ Accepts connections from all origins (CORS = '*')
- ✗ Runs as root with sudo access
- ✓ Binds to all interfaces (0.0.0.0)

**This configuration is NOT suitable for production or network-accessible deployments.**

## Production Security Checklist

Before deploying Jupyter in a production or network-accessible environment, implement these security measures:

### 1. Enable Authentication

Set a secure token in your `.env` file:

```bash
# Generate a secure random token
JUPYTER_TOKEN=$(openssl rand -hex 32)

# Add to .env
echo "JUPYTER_TOKEN=$JUPYTER_TOKEN" >> .env
```

Access Jupyter with: `http://localhost:8888/?token=YOUR_TOKEN_HERE`

### 2. Use a Reverse Proxy

**Do not expose Jupyter directly to the internet.** Use a reverse proxy (nginx, Traefik, Caddy) for:

- SSL/TLS termination
- Rate limiting
- Access control
- IP whitelisting

Example nginx configuration:

```nginx
server {
    listen 443 ssl;
    server_name jupyter.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # IP whitelist (optional)
    allow 192.168.1.0/24;
    deny all;
    
    location / {
        proxy_pass http://localhost:8888;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # WebSocket support for Jupyter
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. Restrict Network Access

**Option A: Bind to localhost only**

Modify `docker-compose.yml`:

```yaml
ports:
  - "127.0.0.1:8888:8888"  # Only accessible from localhost
```

Then access via SSH tunnel or reverse proxy.

**Option B: Use firewall rules**

```bash
# Allow only from specific IP
sudo ufw allow from 192.168.1.0/24 to any port 8888

# Or use Docker network isolation
# Don't expose port in docker-compose.yml, access via internal network only
```

### 4. Remove Root Privileges

For production, pre-install all required packages in a custom Docker image and run as non-root:

**Dockerfile.jupyter** (custom image):

```dockerfile
FROM jupyter/scipy-notebook:latest

USER root
RUN pip install --no-cache-dir pydiode requests openai anthropic litellm
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt || true

# Switch back to jovyan user
USER $NB_UID
```

**docker-compose.yml** modification:

```yaml
jupyter:
  build: 
    context: .
    dockerfile: Dockerfile.jupyter
  # Remove: user: root
  environment:
    # Remove: - GRANT_SUDO=yes
    - JUPYTER_ENABLE_LAB=yes
    ...
```

### 5. Restrict CORS Origins

Modify `docker-compose.yml` to restrict allowed origins:

```yaml
command: >
  bash -c "
  ...
  echo \"c.ServerApp.allow_origin = 'https://yourdomain.com'\" >> /home/jovyan/.jupyter/jupyter_lab_config.py &&
  ...
  "
```

Or for multiple origins:

```python
c.ServerApp.allow_origin = '*'  # Development only
c.ServerApp.allow_origin = 'https://domain1.com,https://domain2.com'  # Production
```

### 6. Enable HTTPS

Set in `.env`:

```bash
ENABLE_HTTPS=true
SSL_CERT_PATH=./config/ssl/cert.pem
SSL_KEY_PATH=./config/ssl/key.pem
```

Generate certificates:

```bash
./scripts/generate-certs.sh
```

### 7. Additional Security Measures

**Container-level isolation:**

```yaml
jupyter:
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - ALL
  cap_add:
    - CHOWN
    - SETGID
    - SETUID
  read_only: true
  tmpfs:
    - /tmp
    - /home/jovyan/.local
```

**Resource limits:**

```yaml
jupyter:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
      reservations:
        cpus: '1'
        memory: 2G
```

**Network isolation:**

```yaml
jupyter:
  networks:
    - internal
    
networks:
  internal:
    internal: true  # No external access
```

## Security Best Practices

1. **Never commit notebooks with credentials** - Use environment variables
2. **Regularly update the Jupyter image** - `docker-compose pull jupyter`
3. **Audit installed packages** - Review notebooks for `!pip install` commands
4. **Monitor container logs** - Watch for suspicious activity
5. **Use secrets management** - Consider HashiCorp Vault or Docker secrets
6. **Implement backup strategy** - Regular backups of `/data/jupyter/notebooks`
7. **Review notebook outputs** - Sensitive data may be stored in outputs
8. **Limit session duration** - Configure session timeouts
9. **Use multi-factor authentication** - Via reverse proxy (OAuth2, etc.)
10. **Regular security audits** - Scan for vulnerabilities

## Attack Vectors to Consider

1. **Remote Code Execution** - Jupyter executes arbitrary Python code
2. **CSRF Attacks** - Mitigated by token authentication + CORS restrictions
3. **XSS** - Jupyter has built-in XSS protections, keep updated
4. **Privilege Escalation** - Running as root increases risk
5. **Network Scanning** - Exposed port 8888 is easily discovered
6. **Credential Theft** - Notebooks may contain or log sensitive data
7. **Container Escape** - Root + sudo increases escape risk

## Monitoring and Logging

Enable logging for security monitoring:

```yaml
jupyter:
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

Monitor for:
- Failed authentication attempts
- Unusual package installations
- High CPU/memory usage (crypto mining)
- Network connections to unexpected hosts
- File system modifications

## Incident Response

If Jupyter is compromised:

1. Immediately stop the container: `docker stop magi-jupyter`
2. Isolate the system from the network
3. Review logs: `docker logs magi-jupyter`
4. Audit all notebooks for malicious code
5. Check for installed packages: `docker exec magi-jupyter pip list`
6. Review network connections: `docker exec magi-jupyter netstat -an`
7. Rotate all API keys and credentials
8. Rebuild container from clean image
9. Review and harden security configuration

## References

- [Jupyter Security Documentation](https://jupyter-notebook.readthedocs.io/en/stable/security.html)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

## Support

For security concerns or questions, please open an issue on GitHub or contact the maintainers.
