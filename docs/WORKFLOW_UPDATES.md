# Workflow Updates for OpenRouter Integration

## Overview

All n8n workflows have been updated to use OpenRouter models by default, ensuring they work out-of-the-box with the new webhook configuration.

## Changes Made

### 1. Workflow Model Updates

The following workflows have been updated to use OpenRouter models:

| Workflow | Old Model | New Model |
|----------|-----------|-----------|
| `morning_briefing.json` | `gpt-4o` | `openrouter/gpt-4o` |
| `research_agent.json` | `gpt-4o` | `openrouter/gpt-4o` |
| `daily_report_generator.json` | `gpt-4o` | `openrouter/gpt-4o` |
| `rss_feed_monitor.json` | `gpt-4o-mini` | `openrouter/gpt-4o-mini` |
| `telegram_research_assistant.json` | `$env.OPENWEBUI_DEFAULT_MODEL \|\| 'gpt-4o'` | `$env.OPENWEBUI_DEFAULT_MODEL \|\| 'openrouter/gpt-4o'` |

### 2. Environment Configuration

#### `.env.example` Updates:
```bash
# Updated to use OpenRouter model by default
OPENWEBUI_DEFAULT_MODEL=openrouter/gpt-4o
```

#### `start.sh` Updates:
The start script now automatically generates OpenRouter webhook configuration:
```bash
OPENROUTER_SITE_URL=http://localhost:3000
OPENROUTER_APP_NAME=RIN - Rhyzomic Intelligence Node
OPENWEBUI_DEFAULT_MODEL=openrouter/gpt-4o
```

## Benefits

### ✅ Works Out-of-the-Box
- Workflows now use OpenRouter models by default
- Webhook headers are automatically added by LiteLLM
- No manual configuration needed for OpenRouter attribution

### ✅ Machine-Independent Configuration
- `OPENROUTER_SITE_URL` can be customized per deployment
- `OPENROUTER_APP_NAME` can be customized for different instances
- Configuration is environment-based, not hardcoded

### ✅ Backward Compatible
- If you have existing API keys for OpenAI/Anthropic, you can still use direct models
- Simply change the model in the workflow JSON or environment variable
- The system supports both OpenRouter and direct API models

## Usage

### For New Installations

1. Run `./start.sh` - webhook configuration is automatically generated
2. Add your OpenRouter API key:
   ```bash
   echo "OPENROUTER_API_KEY=sk-or-v1-your-key" >> .env
   ```
3. Start the system:
   ```bash
   docker-compose up -d
   ```
4. Workflows will automatically use OpenRouter models with proper headers

### For Existing Installations

1. Update your `.env` file with OpenRouter webhook config:
   ```bash
   OPENROUTER_SITE_URL=http://localhost:3000  # or your public URL
   OPENROUTER_APP_NAME=RIN - Rhyzomic Intelligence Node
   OPENWEBUI_DEFAULT_MODEL=openrouter/gpt-4o
   ```

2. Restart LiteLLM to load new configuration:
   ```bash
   docker-compose restart litellm
   ```

3. Import updated workflows (optional - existing ones will work but use old model names):
   ```bash
   ./rin import-workflows
   ```

### Customizing for Production

For production deployments with a public URL:

```bash
# In .env
OPENROUTER_SITE_URL=https://your-domain.com
OPENROUTER_APP_NAME=My Production Instance
OPENROUTER_API_KEY=sk-or-v1-production-key
```

Restart services:
```bash
docker-compose restart litellm
```

## Technical Details

### How It Works

1. **Workflow → LiteLLM**: Workflows call `http://rin-router:4000/chat/completions` with model name `openrouter/gpt-4o`

2. **LiteLLM → OpenRouter**: LiteLLM routes to OpenRouter and automatically adds headers:
   ```
   HTTP-Referer: http://localhost:3000  (from OPENROUTER_SITE_URL)
   X-Title: RIN - Rhyzomic Intelligence Node  (from OPENROUTER_APP_NAME)
   ```

3. **OpenRouter → Response**: OpenRouter receives properly attributed request and returns response

### Header Flow
```
n8n Workflow
    ↓
    model: "openrouter/gpt-4o"
    ↓
LiteLLM (rin-router:4000)
    ↓ (adds headers from env vars)
    HTTP-Referer: OPENROUTER_SITE_URL
    X-Title: OPENROUTER_APP_NAME
    ↓
OpenRouter API
    ↓
✅ Proper attribution & tracking
```

## Verification

Run the integration tests to verify everything works:
```bash
python3 tests/test_integration_openrouter.py
```

Expected output:
```
✅ All integration tests passed! (8/8)
```

Check workflow configurations:
```bash
# View model configuration in a workflow
grep -A 3 '"name": "model"' workflows/morning_briefing.json
```

Expected output:
```json
"name": "model",
"value": "openrouter/gpt-4o"
```

## Troubleshooting

### Workflows not using OpenRouter models

**Issue**: Workflows still use old model names like `gpt-4o`

**Solution**: 
1. Check if workflows were updated: `git status workflows/`
2. Reimport workflows: `./rin import-workflows`
3. Or manually update workflow JSON files

### Headers not being sent

**Issue**: OpenRouter dashboard doesn't show attribution

**Solution**:
1. Verify env vars are set: `cat .env | grep OPENROUTER`
2. Restart LiteLLM: `docker-compose restart litellm`
3. Check LiteLLM logs: `docker-compose logs litellm | grep -i openrouter`

### Different URL per machine

**Issue**: Need different `OPENROUTER_SITE_URL` for dev vs production

**Solution**: This is expected! Update `.env` on each machine:
```bash
# Development
OPENROUTER_SITE_URL=http://localhost:3000

# Production
OPENROUTER_SITE_URL=https://your-domain.com
```

## Migration Guide

### From Direct API to OpenRouter

If you were using direct API models and want to switch to OpenRouter:

1. Get OpenRouter API key from https://openrouter.ai/
2. Add to `.env`: `OPENROUTER_API_KEY=sk-or-v1-your-key`
3. Models are already updated in workflows (this PR)
4. Restart: `docker-compose restart litellm`

### From OpenRouter without Headers to OpenRouter with Headers

If you were already using OpenRouter but without webhook headers:

1. Webhook configuration is already in `.env.example` (from this PR)
2. Add to your `.env`:
   ```bash
   OPENROUTER_SITE_URL=http://localhost:3000
   OPENROUTER_APP_NAME=RIN - Rhyzomic Intelligence Node
   ```
3. Restart: `docker-compose restart litellm`
4. Headers will now be sent automatically

## See Also

- [OpenRouter Webhook Setup Guide](./OPENROUTER_WEBHOOK_SETUP.md)
- [OpenRouter Integration Verification](./OPENROUTER_INTEGRATION_VERIFICATION.md)
- [Model Configuration Guide](./MODEL_CONFIGURATION.md)

---

**Status**: ✅ Complete  
**Updated Workflows**: 5  
**Configuration Files**: 2 (.env.example, start.sh)  
**Backward Compatible**: Yes  
**Breaking Changes**: None
