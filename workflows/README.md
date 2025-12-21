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

### 1. morning_briefing.json ✅ AVAILABLE
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

### 2. openwebui_webhook_integration.json ✅ AVAILABLE
**General-purpose webhook receiver for Open WebUI integration.**

Creates the synaptic bridge between Open WebUI (Cortex) and n8n (Reflex Arc), allowing the brain to trigger autonomous workflows.

**Webhook URL**: `http://localhost:5678/webhook/openwebui-action`

**How to use from Open WebUI:**
Use the n8n_reflex.py tool to trigger this workflow:
```
trigger_workflow("openwebui-action", '{"action": "email", "payload": "..."}')
```

**To activate:**
1. Import `workflows/openwebui_webhook_integration.json`
2. Toggle to "Active"
3. Use the webhook URL in your Open WebUI tools or custom integrations

### 3. email_integration.json ✅ AVAILABLE
**Send emails from RIN conversations via webhook.**

Allows RIN to send emails through SMTP (Gmail, custom server, etc.) when triggered from Open WebUI or other workflows.

**Webhook URL**: `http://localhost:5678/webhook/send-email`

**Prerequisites:**
- Configure SMTP credentials in n8n (Settings > Credentials > SMTP)
- For Gmail: Use an app-specific password

**Example payload:**
```json
{
  "to": "recipient@example.com",
  "subject": "Report from RIN",
  "body": "Here is your requested report...",
  "from": "RIN Intelligence Node <rin@yourdomain.com>"
}
```

**To activate:**
1. Import `workflows/email_integration.json`
2. Configure SMTP credentials in n8n
3. Edit the "Send Email" node to select your SMTP credential
4. Toggle to "Active"

### 4. slack_notification.json ✅ AVAILABLE
**Send notifications to Slack channels.**

Enables RIN to post messages to Slack channels for alerts, reports, or general notifications.

**Webhook URL**: `http://localhost:5678/webhook/slack-notify`

**Prerequisites:**
- Create a Slack App and get an OAuth token
- Configure Slack API credentials in n8n (Settings > Credentials > Slack API)
- Required scopes: `chat:write`, `channels:read`

**Example payload:**
```json
{
  "channel": "#general",
  "message": "Daily report from RIN is ready!",
  "username": "RIN Intelligence Node",
  "icon_emoji": ":brain:"
}
```

**To activate:**
1. Import `workflows/slack_notification.json`
2. Configure Slack API credentials in n8n
3. Edit the "Send to Slack" node to select your Slack credential
4. Toggle to "Active"

### 5. telegram_notification.json ✅ AVAILABLE
**Send messages via Telegram bot.**

Allows RIN to send notifications through Telegram, perfect for mobile alerts and updates.

**Webhook URL**: `http://localhost:5678/webhook/telegram-send`

**Prerequisites:**
- Create a Telegram bot with @BotFather
- Get the bot token from BotFather
- Configure Telegram API credentials in n8n (Settings > Credentials > Telegram API)
- Get your chat ID (message your bot and use the Telegram API to find it)

**Example payload:**
```json
{
  "chatId": "123456789",
  "message": "**Alert from RIN**: Your daily briefing is ready!",
  "parseMode": "Markdown"
}
```

**To activate:**
1. Import `workflows/telegram_notification.json`
2. Configure Telegram API credentials in n8n
3. Edit the "Send to Telegram" node to select your Telegram credential
4. Toggle to "Active"

### 6. rss_feed_monitor.json ✅ AVAILABLE
**Monitor and summarize RSS feeds automatically.**

Periodically checks an RSS feed and generates AI-powered summaries of new items. Runs every 6 hours by default.

**How it works:**
1. **Trigger**: Runs every 6 hours (configurable cron schedule)
2. **Fetch**: Retrieves RSS feed items (default: Hacker News)
3. **Filter**: Selects top 5 items
4. **Summarize**: Uses LiteLLM to generate a digest
5. **Store**: Formatted summary is available for downstream actions

**Customization:**
- Edit the "Fetch RSS Feed" node to change the RSS URL
- Modify the cron expression in "Schedule" node to change frequency
- Add downstream nodes to email/Slack the summary

**To activate:**
1. Import `workflows/rss_feed_monitor.json`
2. Customize the RSS feed URL if desired
3. Toggle to "Active"

### 7. research_agent.json ✅ AVAILABLE
**Autonomous research agent that searches, scrapes, and synthesizes information.**

A comprehensive research workflow that uses SearXNG for search, FireCrawl for content extraction, and LiteLLM for synthesis.

**Webhook URL**: `http://localhost:5678/webhook/research`

**How it works:**
1. **Input**: Receives a research query via webhook
2. **Search**: Queries SearXNG for relevant results
3. **Extract**: Gets top 3 URLs from search results
4. **Scrape**: Uses FireCrawl to extract content from each URL
5. **Synthesize**: LiteLLM generates a comprehensive research report
6. **Output**: Returns structured research report with sources

**Example payload:**
```json
{
  "query": "latest developments in quantum computing",
  "depth": "comprehensive",
  "sources": 5
}
```

**Usage from Open WebUI:**
```
trigger_workflow("research", '{"query": "quantum computing breakthroughs 2024"}')
```

**To activate:**
1. Import `workflows/research_agent.json`
2. Toggle to "Active"
3. Trigger via webhook or n8n_reflex.py tool

### 8. daily_report_generator.json ✅ AVAILABLE
**Automated daily intelligence reports on multiple topics.**

Generates comprehensive daily reports covering multiple topics (AI, technology, cybersecurity). Runs at 6 PM daily.

**How it works:**
1. **Trigger**: Scheduled daily at 6:00 PM
2. **Topics**: Searches multiple predefined topics
3. **Aggregate**: Combines search results from all topics
4. **Generate**: LiteLLM creates a structured intelligence report
5. **Store**: Saves report to Qdrant for long-term memory (optional)

**Customization:**
- Edit "Generate Topics" node to add/change topics
- Modify cron schedule to change report time
- Add downstream nodes to email/Slack the report
- Configure Qdrant storage in the last node

**To activate:**
1. Import `workflows/daily_report_generator.json`
2. Customize topics and schedule if desired
3. Toggle to "Active"

## Accessing n8n

After running `./start.sh`, access the n8n editor at:
- **URL**: http://localhost:5678
- **First Run**: You'll be prompted to create an owner account

## Directory Structure

```
workflows/
├── README.md                           # This file
├── morning_briefing.json               # ✅ Scheduled news summary (8 AM daily)
├── openwebui_webhook_integration.json  # ✅ General OpenWebUI webhook receiver
├── email_integration.json              # ✅ Email sending via SMTP
├── slack_notification.json             # ✅ Slack channel notifications
├── telegram_notification.json          # ✅ Telegram bot messaging
├── rss_feed_monitor.json               # ✅ RSS feed monitoring & summarization
├── research_agent.json                 # ✅ Autonomous research workflow
└── daily_report_generator.json         # ✅ Daily intelligence reports
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

All core workflow templates are now available! These workflows enable:
- **Scheduled automation**: Morning briefings, RSS monitoring, daily reports
- **External integrations**: Email, Slack, Telegram notifications
- **Autonomous research**: Web search, scraping, and synthesis
- **Webhook connectivity**: Direct integration with Open WebUI and external services

### Quick Start Guide

1. **Start RIN**: `./start.sh` or `./rin start`
2. **Access n8n**: Open http://localhost:5678
3. **Create account**: First-time setup prompts for owner account
4. **Import workflows**: Menu (⋮) → Import from File → Select workflow JSON
5. **Configure credentials**: Settings > Credentials (for SMTP, Slack, Telegram)
6. **Activate workflows**: Toggle each workflow to "Active"
7. **Test**: Use webhook URLs or the n8n_reflex.py tool from Open WebUI

### Advanced Customization

- **Change schedules**: Edit cron expressions in Schedule Trigger nodes
- **Add topics**: Modify the code nodes to include your topics of interest
- **Chain workflows**: Connect workflows by calling webhooks from other workflows
- **Store results**: Add Qdrant storage nodes to persist findings in long-term memory
- **Notifications**: Add email/Slack/Telegram nodes to any workflow for alerts
