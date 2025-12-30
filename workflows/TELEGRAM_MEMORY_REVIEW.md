# Telegram Memory Review Bot

Review and approve/reject AI-extracted memories directly from Telegram.

## Setup

### 1. Create Telegram Bot

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow prompts
3. Copy the bot token (looks like `123456789:ABCdefGHI...`)

### 2. Add to Environment

Add to your `.env`:

```bash
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
```

Add to n8n environment variables:
1. Go to n8n → **Settings** → **Variables**
2. Add `TELEGRAM_BOT_TOKEN`

### 3. Import Workflow

1. Open n8n: http://localhost:5678
2. **Workflows** → **Import from File**
3. Select `workflows/telegram_memory_review.json`
4. **Activate** the workflow

### 4. Configure Telegram Credentials in n8n

1. Open the imported workflow
2. Click on **Telegram Trigger** node
3. Click **Create New Credential**
4. Paste your bot token
5. Save

## Usage

### Commands

| Command | Action |
|---------|--------|
| `/review` | Show pending memories with approve/reject buttons |

### Inline Buttons

After sending `/review`, you'll see buttons:

- **✅ Approve [id]** - Move memory to permanent storage
- **❌ Reject [id]** - Delete memory
- **✅ Approve All** - Batch approve all pending
- **❌ Reject All** - Clear the queue

## Flow

```
You: /review
Bot: 📋 5 Pending Memories

     [PREFERENCE] User prefers dark mode...
     ID: abc12345
     [✅ Approve] [❌ Reject]

     [FACT] User works at Acme Corp...
     ID: def67890
     [✅ Approve] [❌ Reject]

     [✅ Approve All] [❌ Reject All]

You: *taps ✅ Approve on first one*
Bot: ✅ Memory approved: User prefers dark...
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | Yes |
| `QDRANT_URL` | Qdrant endpoint (default: `http://magi-memory:6333`) | No |

## Troubleshooting

### Bot not responding

1. Check workflow is **Active** in n8n
2. Verify bot token is correct
3. Check n8n logs: `docker logs magi-reflex-automation`

### Buttons not working

1. Ensure `callback_query` is in Telegram Trigger updates
2. Check n8n execution logs for errors

### Memories not moving

1. Verify Qdrant is running: `docker ps | grep qdrant`
2. Check collections exist:
   ```bash
   curl http://localhost:6333/collections/rin_pending_memories
   curl http://localhost:6333/collections/rin_memory
   ```
