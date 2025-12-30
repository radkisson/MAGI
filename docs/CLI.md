# CLI Reference

MAGI includes a comprehensive CLI tool (`./magi`) for system management.

## Basic Commands

```bash
./magi start              # Start all services
./magi stop               # Stop all services
./magi restart            # Restart all services
./magi status             # Check system health
./magi logs               # View logs (all services)
./magi logs <service> -f  # Follow specific service logs
./magi ps                 # List running containers
./magi help               # Show all commands
```

## Updates & Upgrades

```bash
./magi update             # Pull latest Docker images
./magi upgrade            # Upgrade MAGI to latest version
./magi version            # Show version information
```

## Backup & Restore

```bash
./magi backup             # Backup all data
./magi restore <path>     # Restore from backup
```

## Model Management

```bash
./magi models sync        # Sync latest models from OpenRouter
./magi models list [N]    # List available models
./magi models top [N]     # Show top N models by popularity
./magi models search <q>  # Search models
./magi models recommend   # Show curated recommendations
```

## Password Management

```bash
./magi reset-password openwebui  # Reset OpenWebUI password
./magi reset-password n8n        # Reset n8n password
./magi reset-password all        # Reset all passwords
./magi setup-accounts            # Run initial account setup
```

## Advanced

```bash
./magi exec <container> <cmd>  # Execute command in container
./magi clean                   # Clean up containers and images
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
