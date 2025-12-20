# RIN Workflows

This directory contains n8n workflow definitions for the Reflex Arc (Autonomy Layer).

## About n8n Integration

n8n is the "Nervous System" that gives RIN the ability to run scheduled tasks and connect to external services (Email, Telegram, Slack) without relying on cloud automation tools.

## Workflow Architecture

### Synaptic Bridges (Webhooks)

**Reflex → Cortex**: n8n sends prompts to Open WebUI API
- **Use Case**: "It is 8:00 AM. Ask RIN to summarize the news."
- **Endpoint**: `http://rin-cortex:8080/api/...`

**Cortex → Reflex**: Open WebUI Tools call n8n webhooks
- **Use Case**: User says "Email this report to my boss." RIN triggers `send_email` webhook
- **Endpoint**: `http://rin-reflex-automation:5678/webhook/...`

## Workflow Examples

### morning_briefing.json ✅ AVAILABLE
**Autonomous morning news summary delivered at 8:00 AM daily.**

This is RIN's first "survival instinct" - the organism wakes up, scans the world, and prepares a briefing without human intervention.

**How it works:**
1. **Trigger**: Cron node fires at 8:00 AM every day
2. **Sensor**: HTTP Request to SearXNG (`http://rin-vision:8080/search?q=top+technology+news+today`)
3. **Cognition**: HTTP Request to LiteLLM (`http://rin-router:4000/chat/completions`) with GPT-4o
4. **Output**: 3-bullet summary of the day's top tech news

**To activate:**
1. Access n8n at http://localhost:5678
2. Import `workflows/morning_briefing.json` via: Menu (⋮) → Import from File
3. Toggle workflow to "Active"

### email_integration.json (Coming Soon)
Webhook endpoint for sending emails from RIN conversations.

## Accessing n8n

After running `./start.sh`, access the n8n editor at:
- **URL**: http://localhost:5678
- **First Run**: You'll be prompted to create an owner account

## Directory Structure

```
workflows/
├── README.md                # This file
├── morning_briefing.json    # ✅ Scheduled news summary (8 AM daily)
└── email_integration.json   # (Future) Email webhook handler
```

## Creating Workflows

1. Access n8n at http://localhost:5678
2. Create workflows visually in the editor
3. Export workflows as JSON files to this directory
4. Workflows are automatically loaded when n8n starts

## Internal Connectivity

n8n can communicate with other RIN services using Docker network names:

- **Open WebUI**: `http://rin-cortex:8080`
- **LiteLLM**: `http://rin-router:4000`
- **SearXNG**: `http://rin-vision:8080`
- **FireCrawl**: `http://rin-digestion:3002`
- **Qdrant**: `http://rin-memory:6333`
- **Redis**: `redis://rin-nervous-system:6379`

## Next Steps

Future workflow implementations will include:
- Scheduled news briefings
- Email/Slack/Telegram integrations
- Data backup automation
- Health monitoring and alerts
