# n8n Workflow Installation Guide

This guide provides step-by-step instructions for installing and configuring all RIN n8n workflows.

## Prerequisites

1. RIN must be running: `./start.sh` or `./magi start`
2. All services must be healthy: `./magi status`
3. n8n must be accessible at http://localhost:5678

## Python Support

RIN's n8n instance includes **full Python 3.12 support** in addition to JavaScript. This means you can:

- Write Python code directly in Code nodes
- Use Python's standard library
- Install external packages with pip (via Execute Command node)
- Use data science libraries like pandas, numpy, scikit-learn

See [`PYTHON_EXAMPLES.md`](PYTHON_EXAMPLES.md) for detailed examples and usage guide.

## Initial n8n Setup

### First-Time Access

1. Open http://localhost:5678 in your browser
2. Create an owner account (first-time setup)
   - Enter your email address
   - Set a strong password
   - Click "Continue"
3. You'll be taken to the n8n dashboard

### Importing Workflows

All workflows are located in the `workflows/` directory. To import any workflow:

1. In n8n, click the "Add workflow" button (+ icon)
2. Click the three-dot menu (⋮) in the top-right
3. Select "Import from File"
4. Navigate to the `workflows/` directory
5. Select the workflow JSON file
6. Click "Import"

**Tip**: You can import multiple workflows by repeating these steps.

## Workflow-by-Workflow Setup

### 1. Morning Briefing (No Configuration Required)

**File**: `morning_briefing.json`

**Setup**:
1. Import the workflow
2. Click "Activate" toggle in top-right
3. Done! It will run automatically at 8:00 AM daily

**Customization** (optional):
- Change the time: Edit "Circadian Rhythm" node → Change cron expression
- Change search query: Edit "Sensor: SearXNG" node → Change query parameter
- Change AI model: Edit "Cortex: LiteLLM" node → Change model parameter

### 2. OpenWebUI Webhook Integration (No Configuration Required)

**File**: `openwebui_webhook_integration.json`

**Setup**:
1. Import the workflow
2. Click "Activate" toggle
3. Note the webhook URL: `http://localhost:5678/webhook/openwebui-action`

**Usage from Open WebUI**:
```python
# Use the n8n_reflex.py tool
trigger_workflow("openwebui-action", '{"action": "email", "payload": "data"}')
```

### 3. Email Integration (Requires SMTP Configuration)

**File**: `email_integration.json`

**Setup**:

#### A. Configure SMTP Credentials

1. In n8n, go to Settings (gear icon) → Credentials
2. Click "Create New Credential"
3. Search for "SMTP" and select it
4. Fill in your SMTP details:

**For Gmail**:
- User: `your-email@gmail.com`
- Password: Use an [App Password](https://support.google.com/accounts/answer/185833)
- Host: `smtp.gmail.com`
- Port: `587`
- SSL/TLS: Enable

**For Custom SMTP**:
- User: Your SMTP username
- Password: Your SMTP password
- Host: Your SMTP server address
- Port: Usually 587 (TLS) or 465 (SSL)

5. Click "Save"

#### B. Link Credential to Workflow

1. Import the `email_integration.json` workflow
2. Click the "Send Email" node
3. In the "Credentials" section, select your SMTP credential
4. Click "Activate" toggle

**Test**:
```bash
curl -X POST http://localhost:5678/webhook/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Test from RIN",
    "body": "This is a test email from RIN!"
  }'
```

### 4. Slack Notification (Requires Slack App)

**File**: `slack_notification.json`

**Setup**:

#### A. Create Slack App

1. Go to https://api.slack.com/apps
2. Click "Create New App" → "From scratch"
3. Name: "RIN Intelligence Node"
4. Select your workspace
5. Click "Create App"

#### B. Add Bot Permissions

1. Go to "OAuth & Permissions" in sidebar
2. Scroll to "Scopes" → "Bot Token Scopes"
3. Add these scopes:
   - `chat:write`
   - `channels:read`
4. Scroll up and click "Install to Workspace"
5. Copy the "Bot User OAuth Token" (starts with `xoxb-`)

#### C. Configure n8n Credentials

1. In n8n: Settings → Credentials → Create New
2. Search for "Slack API" and select it
3. Paste your Bot OAuth Token
4. Click "Save"

#### D. Import and Activate

1. Import `slack_notification.json`
2. Click "Send to Slack" node
3. Select your Slack credential
4. Click "Activate" toggle

**Test**:
```bash
curl -X POST http://localhost:5678/webhook/slack-notify \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "#general",
    "message": "Hello from RIN! 🧠"
  }'
```

### 5. Telegram Notification (Requires Telegram Bot)

**File**: `telegram_notification.json`

**Setup**:

#### A. Create Telegram Bot

1. Open Telegram and search for @BotFather
2. Send `/newbot`
3. Follow prompts to name your bot
4. Copy the bot token (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### B. Get Your Chat ID

1. Message your bot with `/start`
2. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find the "chat" object and note the "id" value
4. This is your chat ID (e.g., `123456789`)

#### C. Configure n8n Credentials

1. In n8n: Settings → Credentials → Create New
2. Search for "Telegram API" and select it
3. Paste your bot token
4. Click "Save"

#### D. Import and Activate

1. Import `telegram_notification.json`
2. Click "Send to Telegram" node
3. Select your Telegram credential
4. Click "Activate" toggle

**Test**:
```bash
curl -X POST http://localhost:5678/webhook/telegram-send \
  -H "Content-Type: application/json" \
  -d '{
    "chatId": "YOUR_CHAT_ID",
    "message": "**Hello from RIN!** 🧠\nYour autonomous AI is online."
  }'
```

### 6. RSS Feed Monitor (No Configuration Required)

**File**: `rss_feed_monitor.json`

**Setup**:
1. Import the workflow
2. (Optional) Edit "Fetch RSS Feed" node to change the RSS URL
3. Click "Activate" toggle
4. It will run every 6 hours automatically

**Customization**:
- Change frequency: Edit "Schedule" node → Modify cron expression
- Change feed: Edit "Fetch RSS Feed" node → Change URL
- Add email output: Add "Send Email" node after "Format Summary"

### 7. Research Agent (No Configuration Required)

**File**: `research_agent.json`

**Setup**:
1. Import the workflow
2. Click "Activate" toggle
3. Webhook URL: `http://localhost:5678/webhook/research`

**Usage**:
```bash
# Via curl
curl -X POST http://localhost:5678/webhook/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "latest quantum computing breakthroughs",
    "depth": "comprehensive"
  }'

# Via Open WebUI n8n_reflex.py tool
trigger_workflow("research", '{"query": "AI developments 2024"}')
```

**Note**: This workflow uses FireCrawl for web scraping. Ensure the FireCrawl service is running.

### 8. Daily Report Generator (No Configuration Required)

**File**: `daily_report_generator.json`

**Setup**:
1. Import the workflow
2. (Optional) Edit "Generate Topics" node to customize topics
3. Click "Activate" toggle
4. Runs daily at 6:00 PM automatically

**Customization**:
- Change time: Edit "Schedule" node → Modify cron expression (default: `0 18 * * *`)
- Change topics: Edit "Generate Topics" node → Modify topics array
- Add delivery: Add email/Slack/Telegram node after "Format Report"

## Testing All Workflows

### Quick Health Check

After importing all workflows, verify they're working:

```bash
# Test webhook-based workflows
curl -X POST http://localhost:5678/webhook/openwebui-action \
  -H "Content-Type: application/json" \
  -d '{"action": "test", "payload": "hello"}'

# Check scheduled workflows
# View in n8n: Workflows → Click workflow → Executions tab
```

### Common Issues and Solutions

#### Issue: "Workflow not found" error
**Solution**: Ensure workflow is activated (toggle in top-right)

#### Issue: Webhook returns 404
**Solution**: 
1. Check workflow is active
2. Verify webhook path matches the URL
3. Restart n8n if needed: `docker-compose restart n8n`

#### Issue: SMTP/Slack/Telegram nodes failing
**Solution**:
1. Verify credentials are configured correctly
2. Check credential is selected in the node
3. Test credential: Click "Test" button in credential settings

#### Issue: FireCrawl scraping fails
**Solution**:
1. Ensure FireCrawl service is running: `docker ps | grep firecrawl`
2. Check FireCrawl logs: `docker-compose logs firecrawl`
3. Verify FIRECRAWL_API_KEY is set in `.env`

#### Issue: LiteLLM requests fail
**Solution**:
1. Ensure LITELLM_MASTER_KEY is set in `.env`
2. Verify you have API keys for OpenAI/Anthropic/OpenRouter
3. Check LiteLLM logs: `docker-compose logs litellm`

## Advanced Configuration

### Chaining Workflows

You can call one workflow from another:

```javascript
// In a Code node within a workflow
const response = await fetch('http://localhost:5678/webhook/research', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'topic' })
});
```

### Adding Qdrant Storage

To store workflow outputs in long-term memory:

1. Add an HTTP Request node after your data processing
2. Configure:
   - Method: POST
   - URL: `http://rin-memory:6333/collections/rin_workflows/points`
   - Body: Your data with vector embedding
3. Use the Qdrant Memory tool to retrieve later

### Environment Variables

Workflows can access environment variables using `{{ $env.VARIABLE_NAME }}`:

- `$env.LITELLM_MASTER_KEY` - LiteLLM API key
- `$env.FIRECRAWL_API_KEY` - FireCrawl API key
- `$env.OPENAI_API_KEY` - OpenAI API key (if needed directly)

## Maintenance

### Backing Up Workflows

Workflows are automatically persisted in `/data/n8n` directory.

To backup manually:
```bash
./magi backup
# Or
tar -czf n8n-backup.tar.gz data/n8n/
```

### Updating Workflows

1. Export updated workflow: Workflow menu (⋮) → Download
2. Save to `workflows/` directory
3. Commit to git for version control

### Monitoring Executions

1. In n8n, click any workflow
2. Go to "Executions" tab
3. View success/failure status and detailed logs

## Support

- **Documentation**: See `workflows/README.md` for workflow descriptions
- **RIN CLI**: Use `./magi logs n8n` to view n8n logs
- **n8n Docs**: https://docs.n8n.io/
- **Issues**: Report at GitHub Issues

---

**You're all set!** Your RIN autonomous organism now has full workflow capabilities. 🧠⚡
