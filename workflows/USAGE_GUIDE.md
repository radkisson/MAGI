# Using n8n Workflows from Open WebUI

This guide shows you how to trigger n8n workflows directly from Open WebUI using the `n8n_reflex.py` tool.

## Prerequisites

1. n8n workflows must be imported and activated (see `workflows/INSTALLATION_GUIDE.md`)
2. The `n8n_reflex.py` tool must be installed in Open WebUI (it's pre-mounted via docker-compose)

## How to Trigger Workflows

### Method 1: Natural Language (Recommended)

Simply ask RIN to perform actions in natural language. RIN will automatically use the appropriate tool:

```
You: "Send an email to john@example.com with the subject 'Meeting Notes' and body 'Here are the notes from today's meeting'"

RIN will use the n8n_reflex tool to trigger the email workflow
```

### Method 2: Direct Tool Call

You can explicitly ask RIN to use the n8n_reflex tool:

```
You: "Use the n8n reflex tool to trigger the research workflow for 'quantum computing'"

RIN will call trigger_workflow("research", '{"query": "quantum computing"}')
```

## Workflow Examples

### 1. Send Email

**Natural Language**:
```
You: "Email the morning report to team@company.com"
```

**Direct Call**:
```
You: "Trigger the send-email workflow with:
- to: team@company.com
- subject: Morning Report
- body: Here is today's report..."
```

### 2. Send Slack Notification

**Natural Language**:
```
You: "Post a message to the #engineering Slack channel saying 'Deployment complete!'"
```

**Direct Call**:
```
You: "Trigger the slack-notify workflow with:
- channel: #engineering
- message: Deployment complete!"
```

### 3. Send Telegram Message

**Natural Language**:
```
You: "Send me a Telegram message with today's summary"
```

**Direct Call**:
```
You: "Trigger the telegram-send workflow with my chat ID and today's summary"
```

### 4. Run Research Agent

**Natural Language**:
```
You: "Research the latest AI developments and create a comprehensive report"
```

**Direct Call**:
```
You: "Trigger the research workflow for 'AI developments 2024'"
```

### 5. Custom Webhook Trigger

For any webhook-based workflow:

```
You: "Trigger the workflow 'my-custom-workflow' with data: {key: 'value'}"
```

## Workflow URLs Reference

All workflows are accessible via webhook URLs. Use these for direct HTTP calls:

| Workflow | Webhook URL | Payload Example |
|----------|-------------|-----------------|
| OpenWebUI Integration | `http://localhost:5678/webhook/openwebui-action` | `{"action": "email", "payload": "data"}` |
| Email Integration | `http://localhost:5678/webhook/send-email` | `{"to": "user@example.com", "subject": "Hi", "body": "Hello"}` |
| Slack Notification | `http://localhost:5678/webhook/slack-notify` | `{"channel": "#general", "message": "Update"}` |
| Telegram Notification | `http://localhost:5678/webhook/telegram-send` | `{"chatId": "123456", "message": "Alert"}` |
| Research Agent | `http://localhost:5678/webhook/research` | `{"query": "topic", "depth": "standard"}` |

## Advanced Usage

### Chaining Actions

You can ask RIN to perform multiple actions in sequence:

```
You: "Research quantum computing, then email the report to my team, and post a summary to Slack"

RIN will:
1. Trigger the research workflow
2. Wait for results
3. Trigger the email workflow with the report
4. Trigger the slack-notify workflow with the summary
```

### Conditional Workflows

Ask RIN to make decisions:

```
You: "If the morning briefing mentions 'breaking news', send me a Telegram notification"

RIN will:
1. Check the morning briefing
2. Decide if criteria is met
3. Trigger telegram-send if needed
```

### Scheduled Reminders

While scheduled workflows run automatically, you can ask RIN to set up reminders:

```
You: "Remind me via Telegram every day at 9 AM to review the morning briefing"

(This would require creating a new scheduled workflow in n8n)
```

## Testing Workflows

### Test from Command Line

You can test any workflow directly with curl:

```bash
# Test email workflow
curl -X POST http://localhost:5678/webhook/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "test@example.com",
    "subject": "Test",
    "body": "This is a test"
  }'

# Test research workflow
curl -X POST http://localhost:5678/webhook/research \
  -H "Content-Type: application/json" \
  -d '{
    "query": "AI safety",
    "depth": "standard"
  }'
```

### Test from Open WebUI

In Open WebUI, you can directly test the tool:

```
You: "List available n8n workflows"

RIN will show you the available workflows and their webhook IDs
```

## Creating Custom Workflows

To add your own workflows:

1. **Create in n8n**:
   - Open http://localhost:5678
   - Create a new workflow
   - Add a Webhook trigger node
   - Set a unique webhook path (e.g., `my-custom-action`)
   - Build your workflow logic
   - Activate the workflow

2. **Use from Open WebUI**:
   ```
   You: "Trigger the my-custom-action workflow with {data: 'value'}"
   ```

3. **Document it**:
   - Export the workflow as JSON
   - Save to `workflows/my_custom_workflow.json`
   - Add documentation to `workflows/README.md`

## Troubleshooting

### Workflow Not Triggering

**Problem**: "Cannot reach n8n" error

**Solutions**:
1. Check n8n is running: `docker ps | grep n8n`
2. Verify workflow is activated in n8n
3. Check webhook URL is correct
4. Restart n8n: `docker-compose restart n8n`

### Wrong Data Format

**Problem**: Workflow triggers but doesn't process data correctly

**Solutions**:
1. Check the payload format in the workflow's Code node
2. Ensure JSON is properly formatted
3. Review workflow execution logs in n8n (Executions tab)

### Permission Errors

**Problem**: SMTP/Slack/Telegram node fails

**Solutions**:
1. Verify credentials are configured in n8n
2. Check credential is linked to the node
3. Test credential in n8n settings
4. For Gmail: Use app-specific passwords
5. For Slack: Ensure bot has correct scopes
6. For Telegram: Verify bot token is correct

## Best Practices

### 1. Use Descriptive Payloads

Instead of:
```json
{"d": "value"}
```

Use:
```json
{"description": "value", "timestamp": "2024-01-01"}
```

### 2. Handle Errors Gracefully

Add error handling nodes in your workflows to catch and report failures.

### 3. Log Important Events

Use the "Store in Qdrant" pattern to save workflow results for future reference.

### 4. Test Before Activating

Always test workflows manually before activating them for scheduled execution.

### 5. Monitor Executions

Regularly check the Executions tab in n8n to ensure workflows are running correctly.

## Integration Examples

### Example 1: Daily Digest via Email

```
You: "Every morning at 8 AM, send me an email with the morning briefing"
```

This would combine the `morning_briefing.json` workflow with the `email_integration.json` workflow.

### Example 2: Emergency Alerts

```
You: "If the research agent finds any breaking news about cybersecurity, immediately send me a Telegram message"
```

This would add conditional logic to the `research_agent.json` workflow.

### Example 3: Team Updates

```
You: "When the daily report is generated at 6 PM, post a summary to our #updates Slack channel"
```

This would connect the `daily_report_generator.json` to the `slack_notification.json` workflow.

## Support

- **Workflow Documentation**: See `workflows/README.md`
- **Installation Guide**: See `workflows/INSTALLATION_GUIDE.md`
- **RIN CLI**: Use `./rin logs n8n` for n8n logs
- **n8n Documentation**: https://docs.n8n.io/

---

**Ready to automate!** Use these workflows to give RIN autonomous capabilities. 🧠⚡
