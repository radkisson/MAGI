# CLI Reference

MAGI includes a comprehensive CLI tool (`./rin`) for system management.

## Basic Commands

```bash
./rin start              # Start all services
./rin stop               # Stop all services
./rin restart            # Restart all services
./rin status             # Check system health
./rin logs               # View logs (all services)
./rin logs <service> -f  # Follow specific service logs
./rin ps                 # List running containers
./rin help               # Show all commands
```

## Updates & Upgrades

```bash
./rin update             # Pull latest Docker images
./rin upgrade            # Upgrade MAGI to latest version
./rin version            # Show version information
```

## Backup & Restore

```bash
./rin backup             # Backup all data
./rin restore <path>     # Restore from backup
```

## Model Management

```bash
./rin models sync        # Sync latest models from OpenRouter
./rin models list [N]    # List available models
./rin models top [N]     # Show top N models by popularity
./rin models search <q>  # Search models
./rin models recommend   # Show curated recommendations
```

## Password Management

```bash
./rin reset-password openwebui  # Reset OpenWebUI password
./rin reset-password n8n        # Reset n8n password
./rin reset-password all        # Reset all passwords
./rin setup-accounts            # Run initial account setup
```

## Advanced

```bash
./rin exec <container> <cmd>  # Execute command in container
./rin clean                   # Clean up containers and images
```

## Direct Docker Access

If you prefer docker-compose directly:

```bash
docker-compose up -d          # Start
docker-compose logs -f        # View logs
docker-compose down           # Stop
docker-compose restart <svc>  # Restart service
docker-compose ps             # Check status
```
