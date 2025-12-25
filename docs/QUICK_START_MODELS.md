# Quick Start: Dynamic Model Loading

## What Changed?

RIN now automatically fetches the latest models from OpenRouter instead of using a static list.

## For New Users

**Nothing changes!** Just run:

```bash
./start.sh
```

If you have an `OPENROUTER_API_KEY` in your `.env`, RIN will automatically load all available models.

## For Existing Users

### To Get New Models

Run this anytime to sync the latest OpenRouter models:

```bash
./scripts/sync_models.sh
docker-compose restart litellm
```

### How Often Should I Sync?

- **Weekly**: To stay current with new models
- **Monthly**: If you don't need cutting-edge models
- **On-demand**: When you hear about a new model you want to try

### Manual Sync

```bash
# Quick way
./scripts/sync_models.sh

# Or directly
python3 scripts/sync_openrouter_models.py

# Then restart
docker-compose restart litellm
```

## Troubleshooting

### Models Not Showing Up

```bash
# 1. Check if sync worked
./scripts/sync_models.sh

# 2. Verify LiteLLM restarted
docker-compose logs litellm | tail -20

# 3. Check model endpoint
curl http://localhost:4000/models
```

### Sync Fails

**Most Common**: No `OPENROUTER_API_KEY` set

```bash
# Check your .env
grep OPENROUTER_API_KEY .env

# Add if missing
echo "OPENROUTER_API_KEY=your_key_here" >> .env
```

### Too Many Models

Edit filtering in `scripts/sync_openrouter_models.py`:

```python
# Example: Only OpenAI and Anthropic
if not any(x in model_id for x in ['openai', 'anthropic']):
    continue
```

## Features

- ✅ Automatic sync on startup
- ✅ Manual sync anytime
- ✅ Preserves custom models
- ✅ Backup before changes
- ✅ Graceful fallback
- ✅ Works without API key (uses static config)

## More Info

- [Complete Guide](DYNAMIC_MODELS.md)
- [Model Configuration](MODEL_CONFIGURATION.md)
- [OpenRouter Website](https://openrouter.ai/)

---

**TL;DR**: Models sync automatically. Run `./scripts/sync_models.sh` for updates. 🚀
