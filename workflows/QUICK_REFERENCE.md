# RIN n8n Workflow Quick Reference

## 📦 Available Workflows

| Workflow | Type | Trigger | Description |
|----------|------|---------|-------------|
| **morning_briefing** | Scheduled | 8:00 AM Daily | Autonomous news summary |
| **openwebui_webhook_integration** | Webhook | `/webhook/openwebui-action` | General-purpose OpenWebUI integration |
| **email_integration** | Webhook | `/webhook/send-email` | Send emails via SMTP |
| **slack_notification** | Webhook | `/webhook/slack-notify` | Post to Slack channels |
| **telegram_notification** | Webhook | `/webhook/telegram-send` | Send Telegram messages |
| **rss_feed_monitor** | Scheduled | Every 6 hours | Monitor and summarize RSS feeds |
| **research_agent** | Webhook | `/webhook/research` | Autonomous research with search + scraping |
| **daily_report_generator** | Scheduled | 6:00 PM Daily | Multi-topic intelligence reports |

## 🚀 Quick Start

### Import a Workflow
```
1. Open http://localhost:5678
2. Click "+ Add workflow"
3. Menu (⋮) → "Import from File"
4. Select workflow from workflows/ directory
5. Click "Activate" toggle
```

### Trigger from Open WebUI
```
"Send an email to team@company.com with today's report"
"Post to Slack: Deployment complete!"
"Research quantum computing breakthroughs"
```

### Trigger via curl
```bash
curl -X POST http://localhost:5678/webhook/research \
  -H "Content-Type: application/json" \
  -d '{"query": "AI developments 2024"}'
```

## 🔧 Configuration Requirements

| Workflow | Requires Configuration? | What to Configure |
|----------|------------------------|-------------------|
| morning_briefing | ❌ No | Ready to use |
| openwebui_webhook_integration | ❌ No | Ready to use |
| email_integration | ✅ Yes | SMTP credentials |
| slack_notification | ✅ Yes | Slack API token |
| telegram_notification | ✅ Yes | Telegram bot token |
| rss_feed_monitor | ❌ No | Ready to use (customizable) |
| research_agent | ❌ No | Ready to use |
| daily_report_generator | ❌ No | Ready to use (customizable) |

## 📝 Webhook Payload Examples

### Email
```json
{
  "to": "recipient@example.com",
  "subject": "Subject",
  "body": "Message content"
}
```

### Slack
```json
{
  "channel": "#general",
  "message": "Your message here"
}
```

### Telegram
```json
{
  "chatId": "123456789",
  "message": "Your message here"
}
```

### Research
```json
{
  "query": "research topic",
  "depth": "comprehensive"
}
```

## 🔗 Internal Service URLs

Use these URLs within n8n workflows to connect to RIN services:

| Service | Internal URL | Purpose |
|---------|-------------|---------|
| Open WebUI | `http://rin-cortex:8080` | UI API |
| LiteLLM | `http://rin-router:4000` | AI model routing |
| SearXNG | `http://rin-vision:8080` | Web search |
| FireCrawl | `http://firecrawl:3002` | Web scraping |
| Qdrant | `http://rin-memory:6333` | Vector storage |
| Redis | `redis://rin-nervous-system:6379` | Message queue |

## 🎯 Common Use Cases

### Daily Automation
```
morning_briefing → 8 AM news summary
daily_report_generator → 6 PM intelligence reports
rss_feed_monitor → Every 6 hours feed updates
```

### On-Demand Actions
```
email_integration → Send reports, alerts
slack_notification → Team updates
telegram_notification → Personal notifications
research_agent → Deep research on any topic
```

### Custom Integrations
```
openwebui_webhook_integration → Custom actions from Open WebUI
```

## 📚 Documentation

- **Setup**: `workflows/INSTALLATION_GUIDE.md`
- **Usage**: `workflows/USAGE_GUIDE.md`
- **Details**: `workflows/README.md`

## 🆘 Troubleshooting

### Workflow not triggering?
```bash
# Check n8n is running
docker ps | grep n8n

# View logs
docker-compose logs n8n

# Restart n8n
docker-compose restart n8n
```

### Webhook returns 404?
- Ensure workflow is activated (toggle in top-right)
- Check webhook path matches URL
- Verify workflow was saved after editing

### SMTP/Slack/Telegram failing?
- Configure credentials: Settings → Credentials
- Select credential in the node
- Test credential connection

## ⚡ Pro Tips

1. **Chain workflows**: Call webhooks from within workflows
2. **Store results**: Add Qdrant nodes to save outputs
3. **Add notifications**: Append email/Slack nodes to any workflow
4. **Custom schedules**: Edit cron expressions in Schedule nodes
5. **Monitor executions**: Check "Executions" tab for each workflow

---

**Quick access**: http://localhost:5678 | **Help**: `./rin logs n8n`
