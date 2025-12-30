# Dynamic Model Loading

## Overview

Starting with this release, RIN automatically fetches and updates the list of available models from multiple providers. This ensures you always have access to the latest models without manual configuration updates.

## Supported Providers

- **OpenRouter** - Access to 100+ models from multiple providers
- **Azure OpenAI** - Enterprise Azure-hosted OpenAI models
- **OpenAI** (Direct) - Direct OpenAI API access
- **Anthropic** (Direct) - Direct Anthropic API access

## How It Works

### Automatic Sync on Startup

When you run `./start.sh`, RIN automatically:
1. Connects to provider APIs (OpenRouter, Azure OpenAI)
2. Fetches available models and deployments
3. Filters models based on availability and quality criteria
4. Updates the LiteLLM configuration with fresh model entries
5. Preserves your existing direct API models (OpenAI, Anthropic)

### Manual Sync

You can manually sync models at any time:

```bash
# Sync all providers (OpenRouter + Azure OpenAI)
./magi models sync

# Or run directly
./scripts/sync_models.sh

# Sync with custom limit for OpenRouter
./magi models sync 25
```

After syncing, restart LiteLLM to apply changes:

```bash
./magi restart litellm
# Or
docker-compose restart litellm
```

## Azure OpenAI Configuration

### Prerequisites

1. **Azure OpenAI Resource** - Create one in the Azure portal
2. **Deploy Models** - Deploy models to your resource
3. **Get API Key and Endpoint** - From your Azure OpenAI resource

### Environment Variables

Add to your `.env` file:

```bash
# Azure OpenAI API key
AZURE_OPENAI_API_KEY=your-api-key-here

# Azure OpenAI endpoint (e.g., https://your-resource.openai.azure.com)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com

# API version (optional, defaults to 2024-08-01-preview)
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Your deployed models - comma-separated list of deployment:model pairs
# Format: deployment_name:model_name,deployment2:model2
AZURE_OPENAI_MODELS=my-gpt4o:gpt-4o,my-gpt4o-mini:gpt-4o-mini,my-o1:o1-preview
```

### Model Naming

Azure models are automatically named using the pattern:
- **Format**: `azure/{deployment_name}`
- **Example**: `azure/my-gpt4o`

### Capability Detection

The sync script automatically detects model capabilities based on the model name:
- **Vision Support**: gpt-4o, gpt-4-turbo
- **Function Calling**: gpt-4o, gpt-4, gpt-3.5-turbo, o1, o3
- **Extended Tokens**: o1, o3 reasoning models

### Example Azure Configuration

```bash
# .env file
AZURE_OPENAI_API_KEY=abc123...
AZURE_OPENAI_ENDPOINT=https://mycompany-openai.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_MODELS=prod-gpt4o:gpt-4o,prod-gpt4o-mini:gpt-4o-mini,prod-o1:o1-preview

# After setting these, run:
./scripts/sync_models.sh
docker-compose restart litellm
```

Models will appear in Open WebUI as:
- `azure/prod-gpt4o`
- `azure/prod-gpt4o-mini`
- `azure/prod-o1`

## OpenRouter Configuration

### Prerequisites

1. **OpenRouter API Key** (Required for model access):
   - Get your key from [OpenRouter](https://openrouter.ai/)
   - Add to `.env`:
     ```bash
     OPENROUTER_API_KEY=your_key_here
     ```

2. **Model Limit Configuration** (Optional):
   - Control the number of models synced and displayed
   - Add to `.env`:
     ```bash
     OPENROUTER_MODEL_LIMIT=50  # Default: 50
     ```
   - Recommended values: 10, 25, 50, 75
   - Set to 0 for unlimited models. If not set, defaults to 50.

3. **Python Requirements** (Installed automatically):
   - `requests` - For API calls
   - `pyyaml` - For config file handling

### Model Filtering

The sync script automatically filters models to include only:

- **Active models** - Not deprecated or removed
- **Available models** - Have pricing information (indicates availability)
- **Base variants** - Excludes extended context variants to reduce clutter
  - Exception: Keeps useful variants like `128k-online` and `sonar` models

## Model Naming

Models are automatically named using a consistent pattern:

- **Format**: `openrouter/{provider}-{model}`
- **Example**: `openrouter/openai-gpt-4o`
- **Original ID preserved** in the `litellm_params.model` field

## Features

### Automatic Capability Detection

The sync script automatically detects and tags models with:

- **Function Calling** - Models that support tool/function calling
- **Vision Support** - Models that can process images
- **Context Length** - Automatically configures max_tokens based on model context

### Fallback to Static Config

If the sync fails (no API key, network issues, etc.), RIN gracefully falls back to:
- Your existing configuration
- Default models in the config file
- No disruption to service

This ensures RIN works even without OpenRouter API access.

## Usage Examples

### CLI Model Management

RIN includes a comprehensive CLI for model management:

```bash
# View all available commands
./magi models help

# Sync models with default limit
./magi models sync

# Sync top 10, 25, 50, or 75 models
./magi models sync 10
./magi models sync 25
./magi models sync 50
./magi models sync 75

# List models with default limit (from OPENROUTER_MODEL_LIMIT)
./magi models list

# List specific number of models
./magi models list 10
./magi models list 25
./magi models list 50

# Show top N models by popularity
./magi models top 10
./magi models top 25

# Filter models by type
./magi models filter vision 20      # Show 20 vision models
./magi models filter budget 30      # Show 30 budget models
./magi models filter openai 15      # Show 15 OpenAI models

# Search models by criteria
./magi models search --tag vision
./magi models search --cost budget
./magi models search --popular 70

# Show model recommendations
./magi models recommend
```

### Example 1: First Time Setup

```bash
# 1. Add your OpenRouter API key and set model limit
nano .env
# Add: 
#   OPENROUTER_API_KEY=sk-or-v1-...
#   OPENROUTER_MODEL_LIMIT=25

# 2. Start RIN (auto-syncs models)
./magi start

# 3. Models are now available in Open WebUI
```

### Example 2: Optimizing for Performance

For faster model listing and better performance, limit the number of models:

```bash
# 1. Set a reasonable limit in .env
echo "OPENROUTER_MODEL_LIMIT=25" >> .env

# 2. Sync with the limit
./magi models sync 25

# 3. Restart LiteLLM
./magi restart litellm

# 4. Verify models are limited
./magi models list
```

### Example 3: Adding New Models

OpenRouter frequently adds new models. To get them:

```bash
# 1. Sync models
./magi models sync

# 2. Restart LiteLLM
./magi restart litellm

# 3. New models appear in Open WebUI immediately
```

### Example 4: Scheduled Sync

Add to crontab for daily model updates:

```bash
# Sync models daily at 3 AM (limit to top 50)
0 3 * * * cd /path/to/RIN && ./magi models sync 50 && ./magi restart litellm
```

## Troubleshooting

### Models Not Appearing

**Problem**: Models don't show up in Open WebUI

**Solutions**:
1. Check if sync succeeded:
   ```bash
   ./scripts/sync_models.sh
   ```

2. Verify LiteLLM restarted:
   ```bash
   docker-compose logs litellm | tail -20
   ```

3. Check model list endpoint:
   ```bash
   curl http://localhost:4000/models
   ```

### Sync Fails

**Problem**: `sync_openrouter_models.py` fails with errors

**Common causes**:

1. **No API key**:
   ```bash
   # Check .env has OPENROUTER_API_KEY
   grep OPENROUTER_API_KEY .env
   ```

2. **Network issues**:
   ```bash
   # Test connectivity
   curl https://openrouter.ai/api/v1/models
   ```

3. **Python dependencies**:
   ```bash
   # Install requirements
   pip3 install requests pyyaml
   ```

### Too Many Models

**Problem**: Model list in Open WebUI is overwhelming

**Solution 1**: Use the `OPENROUTER_MODEL_LIMIT` environment variable to limit the number of models:

```bash
# Edit .env file
nano .env

# Add or update this line:
OPENROUTER_MODEL_LIMIT=25  # Only sync top 25 models

# Re-sync models
./magi models sync

# Restart LiteLLM
./magi restart litellm
```

**Solution 2**: Use the CLI with a limit argument:

```bash
# Sync only top 10 models
./magi models sync 10

# List only top 10 models
./magi models list 10

# Show top 25 models by popularity
./magi models top 25
```

**Solution 3**: Edit the filter criteria in `scripts/sync_openrouter_models.py`:

```python
def filter_models_by_criteria(models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Custom filtering logic"""
    filtered = []
    
    for model in models:
        model_id = model.get('id', '')
        
        # Add your custom filters here
        # Example: Only include OpenAI and Anthropic
        if not any(x in model_id for x in ['openai', 'anthropic']):
            continue
        
        # Example: Exclude expensive models
        pricing = model.get('pricing', {})
        if float(pricing.get('prompt', 0)) > 0.00005:
            continue
        
        filtered.append(model)
    
    return filtered
```

## Advanced Configuration

### Custom Model Parameters

After sync, you can customize individual models in `config/litellm/config.yaml`:

```yaml
model_list:
  # Auto-generated by sync
  - model_name: openrouter/openai-gpt-4o
    litellm_params:
      model: openrouter/openai/gpt-4o
      api_key: os.environ/OPENROUTER_API_KEY
      temperature: 0.7  # Customize this
      max_tokens: 4096  # Customize this
      top_p: 1.0
    model_info:
      mode: chat
      supports_function_calling: true
```

### Preserve Custom Models

The sync script automatically preserves:
- Direct API models (OpenAI, Anthropic)
- Custom model configurations you've added

Only OpenRouter models are updated during sync.

### Disable Auto-Sync

To disable automatic sync on startup:

1. Comment out the sync section in `start.sh`:
   ```bash
   # --- 5.1 SYNC OPENROUTER MODELS ---
   # echo -e "${BLUE}🔄 Synchronizing OpenRouter models...${NC}"
   # if [ -f "$BASE_DIR/scripts/sync_openrouter_models.py" ]; then
   #     python3 "$BASE_DIR/scripts/sync_openrouter_models.py" 2>/dev/null || {
   #         echo "⚠️  Could not fetch latest models"
   #     }
   # fi
   ```

2. You can still manually sync:
   ```bash
   ./scripts/sync_models.sh
   ```

## Architecture

### Sync Flow

```
┌─────────────────┐
│  OpenRouter API │
│  /api/v1/models │
└────────┬────────┘
         │
         ▼
┌────────────────────────┐
│ sync_openrouter_models │
│   - Fetch models       │
│   - Filter by criteria│
│   - Convert to LiteLLM │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│ config/litellm/       │
│ config.yaml           │
│   - Preserve existing │
│   - Add OpenRouter    │
│   - Backup old config │
└────────┬───────────────┘
         │
         ▼
┌────────────────────────┐
│   LiteLLM Service     │
│   Reload config       │
│   Serve models        │
└───────────────────────┘
```

### File Structure

```
scripts/
├── sync_openrouter_models.py  # Core sync logic
└── sync_models.sh             # Convenience wrapper

config/litellm/
├── config.yaml                # Active config
└── config.yaml.backup         # Auto-backup
```

## API Reference

### OpenRouter Models Endpoint

- **URL**: `https://openrouter.ai/api/v1/models`
- **Method**: `GET`
- **Auth**: Bearer token (optional, public data available without auth)
- **Response**: JSON with model list

### Response Format

```json
{
  "data": [
    {
      "id": "openai/gpt-4o",
      "name": "GPT-4o",
      "pricing": {
        "prompt": "0.0000025",
        "completion": "0.00001"
      },
      "context_length": 128000,
      "architecture": {
        "modality": "text+image->text",
        "tokenizer": "GPT",
        "instruct_type": "none"
      },
      "supported_parameters": ["temperature", "top_p", "max_tokens"],
      "description": "..."
    }
  ]
}
```

## Best Practices

1. **Set a Reasonable Model Limit**: Start with 25-50 models for better performance
2. **Sync Regularly**: Run sync weekly or when you need new models
3. **Use Top Models**: The popularity ranking ensures you get the best models first
4. **Review Config**: Check `config.yaml.backup` if something goes wrong
5. **Test New Models**: Try new models with simple queries first
6. **Monitor Costs**: New models may have different pricing
7. **Keep Fallbacks**: Maintain direct API models for reliability

### Performance Optimization

Limiting the number of models improves:
- **WebUI Load Time**: Faster model dropdown rendering
- **API Response Time**: Quicker model listing endpoints
- **Memory Usage**: Reduced LiteLLM memory footprint
- **Configuration Size**: Smaller, more manageable config files

**Recommended Limits by Use Case:**
- **Personal Use**: 10-25 models (quick access to best models)
- **Team Use**: 25-50 models (good variety without overwhelming choice)
- **Production**: 50-75 models (comprehensive options for diverse needs)
- **Enterprise**: 75+ or unlimited (full model catalog)

## Security Notes

- API keys are stored in `.env` (not committed to git)
- Sync script never exposes keys in logs
- Backup files may contain sensitive config (excluded via `.gitignore`)

## Future Enhancements

~~Planned improvements:~~  
**✅ IMPLEMENTED:**
- [x] **Model popularity rankings** - Models are now ranked by popularity score (0-100)
- [x] **Cost-based filtering** - Models tagged with cost tiers (budget, standard, premium)
- [x] **Model capability search** - New `search_models.py` script for filtering by capabilities
- [x] **Automatic model recommendations** - Generates recommendations for different use cases
- [x] **Performance benchmarking integration** - Popularity scores based on multiple factors

### New Features

#### 1. Model Search Tool

Search and filter models by capabilities:

```bash
# Search by tag
python3 scripts/search_models.py --tag vision

# Search by cost tier
python3 scripts/search_models.py --cost budget

# Search by popularity
python3 scripts/search_models.py --popular 70

# Get recommendations
python3 scripts/search_models.py --best-value
python3 scripts/search_models.py --coding
python3 scripts/search_models.py --vision
```

#### 2. Popularity Scoring

Models are automatically ranked by popularity (0-100) based on:
- Provider reputation (OpenAI, Anthropic, etc.)
- Pricing competitiveness
- Capability features (function calling, vision)
- Model specialization

#### 3. Cost Metadata

All models include cost information:
- Cost per 1M tokens (input/output)
- Cost tier classification (budget/standard/premium)
- Enables cost-based filtering

#### 4. Capability Tags

Models are tagged for easy searching:
- Provider tags: `openai`, `anthropic`, `meta`, `google`, `mistral`
- Capability tags: `function-calling`, `vision`, `web-search`, `long-context`
- Size tags: `large`, `small`

#### 5. Automatic Recommendations

The sync script generates recommendations for:
- 💎 **Best Value** - Good performance at reasonable cost
- 🚀 **Most Capable** - Premium flagship models
- ⚡ **Fastest** - Optimized for speed
- 💰 **Budget Friendly** - Most cost-effective
- 👁️ **Vision Tasks** - Image/multimodal support
- 💻 **Coding** - Best for programming tasks

Recommendations are saved to `data/model_recommendations.json`

## Support

For issues or questions:
- GitHub Issues: [Report a bug](https://github.com/radkisson/Rhyzomic-Intelligence-Node-RIN-/issues)
- Documentation: [Full docs](../README.md)

---

**Dynamic Models** - Always up-to-date, always ready. 🚀
