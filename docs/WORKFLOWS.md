# Workflow Automation

MAGI includes n8n for workflow automation with 8 pre-configured templates.

## Available Workflows

1. **Morning Briefing** - Daily news summary at 8 AM
2. **OpenWebUI Integration** - Webhook receiver for Open WebUI
3. **Email Integration** - Send emails via SMTP
4. **Slack Notifications** - Post to Slack channels
5. **Telegram Notifications** - Send via Telegram bot
6. **RSS Feed Monitor** - Monitor feeds every 6 hours
7. **Research Agent** - Autonomous research with synthesis
8. **Daily Report Generator** - Intelligence reports at 6 PM

## Quick Start

1. Access n8n: http://localhost:5678
2. Import workflow: **Add workflow → Import from File**
3. Select from `workflows/` directory
4. Configure credentials (SMTP, Slack, Telegram)
5. Activate the workflow

## Triggering from Open WebUI

```
"Send an email to team@company.com with today's briefing"
"Post to Slack saying 'Deployment complete'"
"Research quantum computing and send me a report"
```

## Python Support

n8n includes Python 3.12 support in Code nodes:

```python
items = _input.all()
results = []
for item in items:
    data = item['json']
    processed = {'text': str(data.get('text', '')).upper()}
    results.append({'json': processed})
return results
```

**Installing packages:**
```bash
pip install requests pandas
```

Note: Packages may not persist across restarts. For production, build a custom image.

## More Documentation

- [workflows/INSTALLATION_GUIDE.md](../workflows/INSTALLATION_GUIDE.md)
- [workflows/USAGE_GUIDE.md](../workflows/USAGE_GUIDE.md)
- [workflows/README.md](../workflows/README.md)
