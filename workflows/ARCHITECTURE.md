# RIN n8n Workflow Architecture

## System Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                          RIN Intelligence Node                         │
└────────────────────────────────────────────────────────────────────────┘
                                     │
                  ┌──────────────────┼──────────────────┐
                  │                  │                  │
         ┌────────▼────────┐  ┌─────▼──────┐  ┌───────▼────────┐
         │   Open WebUI    │  │  LiteLLM   │  │    SearXNG     │
         │   (Cortex)      │  │  (Router)  │  │    (Vision)    │
         └────────┬────────┘  └─────┬──────┘  └───────┬────────┘
                  │                  │                  │
                  │                  │                  │
         ┌────────▼──────────────────▼──────────────────▼────────┐
         │              n8n Workflow Automation                   │
         │                  (Reflex Arc)                          │
         └────────┬───────────────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┬─────────────┐
    │             │             │             │             │
┌───▼───┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌───▼────┐
│ Email │   │  Slack  │   │Telegram │   │   RSS   │   │Research│
│  SMTP │   │   API   │   │   Bot   │   │  Feeds  │   │ Agent  │
└───────┘   └─────────┘   └─────────┘   └─────────┘   └────────┘
```

## Workflow Types

### 1. Scheduled Workflows (Autonomous)
```
┌──────────────────────────────────────────────────────────┐
│  Time-based triggers (no user intervention required)     │
└──────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════╗
║  morning_briefing.json                                ║
╠═══════════════════════════════════════════════════════╣
║  Trigger: 8:00 AM Daily                               ║
║  Action: Search news → Summarize → Store              ║
║  Output: 3-bullet tech news summary                   ║
╚═══════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════╗
║  rss_feed_monitor.json                                ║
╠═══════════════════════════════════════════════════════╣
║  Trigger: Every 6 hours                               ║
║  Action: Fetch RSS → Filter → Summarize               ║
║  Output: Top 5 items digest                           ║
╚═══════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════╗
║  daily_report_generator.json                          ║
╠═══════════════════════════════════════════════════════╣
║  Trigger: 6:00 PM Daily                               ║
║  Action: Multi-topic search → Aggregate → Report      ║
║  Output: Comprehensive intelligence report            ║
╚═══════════════════════════════════════════════════════╝
```

### 2. Webhook Workflows (On-Demand)
```
┌──────────────────────────────────────────────────────────┐
│  Triggered by HTTP POST requests from Open WebUI or API  │
└──────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════╗
║  openwebui_webhook_integration.json                   ║
╠═══════════════════════════════════════════════════════╣
║  URL: /webhook/openwebui-action                       ║
║  Purpose: General-purpose webhook router              ║
║  Routes: email, research, notify                      ║
╚═══════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════╗
║  email_integration.json                               ║
╠═══════════════════════════════════════════════════════╣
║  URL: /webhook/send-email                             ║
║  Purpose: Send emails via SMTP                        ║
║  Requires: SMTP credentials                           ║
╚═══════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════╗
║  slack_notification.json                              ║
╠═══════════════════════════════════════════════════════╣
║  URL: /webhook/slack-notify                           ║
║  Purpose: Post to Slack channels                      ║
║  Requires: Slack API token                            ║
╚═══════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════╗
║  telegram_notification.json                           ║
╠═══════════════════════════════════════════════════════╣
║  URL: /webhook/telegram-send                          ║
║  Purpose: Send Telegram messages                      ║
║  Requires: Telegram bot token                         ║
╚═══════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════╗
║  research_agent.json                                  ║
╠═══════════════════════════════════════════════════════╣
║  URL: /webhook/research                               ║
║  Purpose: Autonomous research workflow                ║
║  Flow: Search → Scrape → Synthesize → Report          ║
╚═══════════════════════════════════════════════════════╝
```

## Data Flow Example: Research Agent

```
┌─────────────────┐
│  User Query     │
│  "Research AI"  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  1. Webhook Trigger                             │
│     Receives: {"query": "AI developments"}      │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  2. SearXNG Search                              │
│     http://rin-vision:8080/search?q=AI          │
│     Returns: Top search results                 │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  3. Extract URLs                                │
│     Gets top 3 URLs from results                │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  4. FireCrawl Scraping                          │
│     http://firecrawl:3002/v0/scrape             │
│     Extracts: Clean markdown content            │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  5. LiteLLM Synthesis                           │
│     http://rin-router:4000/chat/completions     │
│     Generates: Comprehensive research report    │
└────────┬────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────┐
│  6. Format & Return                             │
│     Returns: JSON with report + sources         │
└─────────────────────────────────────────────────┘
```

## Integration Patterns

### Pattern 1: Open WebUI → n8n (Synaptic Bridge)

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│             │         │             │         │             │
│  Open WebUI │ ─────▶  │   n8n Tool  │ ─────▶  │  Workflow   │
│   (User)    │  Chat   │ (n8n_reflex)│  HTTP   │  (Action)   │
│             │         │             │         │             │
└─────────────┘         └─────────────┘         └─────────────┘

Example:
User: "Email this report to my team"
↓
n8n_reflex.trigger_workflow("send-email", {...})
↓
Email sent via SMTP
```

### Pattern 2: Scheduled → Action → Notification

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│             │         │             │         │             │
│  Schedule   │ ─────▶  │   Action    │ ─────▶  │   Notify    │
│   (Cron)    │  Time   │  (Process)  │  Result │ (Optional)  │
│             │         │             │         │             │
└─────────────┘         └─────────────┘         └─────────────┘

Example:
8:00 AM
↓
Search news + Summarize
↓
Store in Qdrant OR Email report
```

### Pattern 3: Webhook Chain (Composite Actions)

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│             │         │             │         │             │
│  Webhook 1  │ ─────▶  │  Webhook 2  │ ─────▶  │  Webhook 3  │
│ (Research)  │  Data   │   (Email)   │  Status │   (Slack)   │
│             │         │             │         │             │
└─────────────┘         └─────────────┘         └─────────────┘

Example:
Research topic
↓
Email detailed report
↓
Post summary to Slack
```

## Service Connectivity Map

```
All workflows can connect to these RIN internal services:

┌────────────────────────────────────────────────────────┐
│  Internal Docker Network (rin-network)                 │
├────────────────────────────────────────────────────────┤
│                                                        │
│  rin-cortex:8080        → Open WebUI API              │
│  rin-router:4000        → LiteLLM (AI models)         │
│  rin-vision:8080        → SearXNG (web search)        │
│  firecrawl:3002         → FireCrawl (scraping)        │
│  rin-memory:6333        → Qdrant (vector DB)          │
│  rin-nervous-system:6379→ Redis (message bus)         │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## Customization Guide

### Adding a New Workflow

```
1. Create in n8n UI
   ├─ Add Webhook Trigger (for on-demand)
   │  OR Schedule Trigger (for autonomous)
   │
   ├─ Add processing nodes
   │  ├─ HTTP Request (call RIN services)
   │  ├─ Code (JavaScript logic)
   │  └─ Set/Filter (data transformation)
   │
   ├─ Add output nodes
   │  ├─ Respond to Webhook (for webhooks)
   │  └─ Email/Slack/Telegram (for notifications)
   │
   └─ Test & Activate

2. Export as JSON
   ├─ Menu (⋮) → Download
   └─ Save to workflows/ directory

3. Document
   ├─ Add to workflows/README.md
   ├─ Update QUICK_REFERENCE.md
   └─ Add examples to USAGE_GUIDE.md
```

### Chaining Workflows

```javascript
// Inside a Code node in Workflow A:
const response = await fetch('http://localhost:5678/webhook/workflow-b', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ data: 'from-workflow-a' })
});

const result = await response.json();
return { json: result };
```

## Security Considerations

```
┌────────────────────────────────────────────────┐
│  Secure by Default                             │
├────────────────────────────────────────────────┤
│                                                │
│  ✓ All services run in isolated Docker network│
│  ✓ Credentials stored encrypted in n8n        │
│  ✓ Webhook URLs only accessible internally    │
│  ✓ Environment variables for sensitive data   │
│  ✗ No external network access from workflows  │
│                                                │
└────────────────────────────────────────────────┘

For production deployment:
- Enable HTTPS/TLS
- Use secrets management (Vault, etc.)
- Implement authentication on webhooks
- Set up firewall rules
- Enable n8n secure cookies
```

## Monitoring & Debugging

```
View logs:           ./rin logs n8n
Check executions:    n8n UI → Workflow → Executions tab
Test webhook:        curl -X POST http://localhost:5678/webhook/...
Check connectivity:  docker exec rin-reflex-automation ping rin-router
Restart service:     docker-compose restart n8n
```

## Version Information

- **n8n Version**: Latest (from Docker)
- **Workflow Format**: n8n JSON v1
- **RIN Compatibility**: v1.2+ (Intelligence)
- **Last Updated**: 2024-12-21

---

**For detailed setup instructions**, see `INSTALLATION_GUIDE.md`  
**For usage examples**, see `USAGE_GUIDE.md`  
**For quick commands**, see `QUICK_REFERENCE.md`
