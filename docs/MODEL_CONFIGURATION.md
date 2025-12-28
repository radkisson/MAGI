# Model Configuration Guide - RIN v1.1

This guide explains the enhanced model support features introduced in RIN v1.1 "Expansion".

## 🆕 Dynamic Model Loading

**NEW**: RIN now automatically fetches the latest models from OpenRouter!

Models are synchronized automatically on startup and can be manually updated at any time. This ensures you always have access to the newest models without manual configuration.

📖 **See [Dynamic Models Guide](DYNAMIC_MODELS.md) for complete documentation**

Quick start:
```bash
# Set your OpenRouter API key
echo "OPENROUTER_API_KEY=your_key" >> .env

# Sync models
./scripts/sync_models.sh

# Restart to apply
docker-compose restart litellm
```

## Table of Contents

1. [Overview](#overview)
2. [OpenRouter Integration](#openrouter-integration)
3. [Advanced Model Parameters](#advanced-model-parameters)
4. [Model Selection in Open WebUI](#model-selection-in-open-webui)
5. [Cost Tracking and Budgeting](#cost-tracking-and-budgeting)
6. [Fallback Model Chains](#fallback-model-chains)
7. [Configuration Examples](#configuration-examples)

## Related Guides

- **[OpenRouter Webhook Setup Guide](./OPENROUTER_WEBHOOK_SETUP.md)** - Detailed guide for configuring OpenRouter webhooks and HTTP headers

## Overview

RIN v1.1 introduces comprehensive multi-model support with the following capabilities:

- **OpenRouter Integration**: Access to 20+ models from multiple providers
- **Advanced Parameters**: Fine-tune model behavior with temperature, top_p, and max_tokens
- **Cost Tracking**: Monitor and control spending across all models
- **Fallback Chains**: Automatic failover to alternative models for reliability
- **Flexible Configuration**: Easy YAML-based configuration for all models

## OpenRouter Integration

OpenRouter provides access to a marketplace of AI models through a single API. RIN now supports OpenRouter alongside direct API access to OpenAI and Anthropic.

### Supported OpenRouter Models

The default configuration includes:

**OpenAI Models:**
- `openrouter/gpt-4o` - Latest GPT-4 optimized model
- `openrouter/gpt-4-turbo` - Fast GPT-4 variant

**Anthropic Models:**
- `openrouter/claude-3-5-sonnet` - Latest Claude 3.5 Sonnet
- `openrouter/claude-3-opus` - Most capable Claude model

**Meta Llama Models:**
- `openrouter/llama-3.1-405b` - Largest Llama model
- `openrouter/llama-3.1-70b` - High-performance Llama

**Google Models:**
- `openrouter/gemini-pro` - Gemini Pro 1.5
- `openrouter/gemini-flash` - Fast Gemini variant

**Mistral Models:**
- `openrouter/mistral-large` - Largest Mistral model
- `openrouter/mixtral-8x7b` - Mixture of Experts model

**Other Models:**
- `openrouter/command-r-plus` - Cohere's command model
- `openrouter/perplexity-online` - Perplexity with web search

### Setting Up OpenRouter

1. Get your API key from [OpenRouter](https://openrouter.ai/)
2. Add it to your `.env` file:
   ```bash
   OPENROUTER_API_KEY=your_key_here
   ```
3. **Configure webhook parameters (optional but recommended):**
   ```bash
   # The public URL of your WebUI (for production deployments)
   OPENROUTER_SITE_URL=https://your-domain.com
   
   # Your application name (for OpenRouter attribution and rankings)
   OPENROUTER_APP_NAME=RIN - Rhyzomic Intelligence Node
   ```
   
   These parameters enable proper attribution of API calls to your application in OpenRouter's dashboard and rankings. For local development, the default values (`http://localhost:3000` and `RIN - Rhyzomic Intelligence Node`) work fine.
   
4. Restart RIN:
   ```bash
   docker-compose restart litellm
   ```

All OpenRouter models will now be available in Open WebUI's model selector.

#### OpenRouter Webhook Configuration Details

OpenRouter uses two HTTP headers for API attribution:
- **HTTP-Referer** (from `OPENROUTER_SITE_URL`): Identifies the originating site/application
- **X-Title** (from `OPENROUTER_APP_NAME`): Sets your application's display name

These headers help OpenRouter:
- Track and rank your application in their ecosystem
- Ensure proper API request attribution for billing and analytics
- Enable leaderboard rankings and visibility for your application

**Important:** For production deployments with public-facing URLs, always configure these parameters to ensure your API calls are properly attributed and to avoid potential issues with API responses.

**📖 For detailed webhook setup instructions, troubleshooting, and advanced configuration, see the [OpenRouter Webhook Setup Guide](./OPENROUTER_WEBHOOK_SETUP.md).**

## Advanced Model Parameters

Each model in RIN can be configured with advanced parameters to control its behavior:

### Temperature (0.0 - 2.0)
Controls randomness in responses:
- **0.0**: Deterministic, focused responses
- **0.7**: Balanced creativity and consistency (default)
- **1.5+**: Highly creative, more random

### Top P (0.0 - 1.0)
Controls diversity via nucleus sampling:
- **0.1**: Very focused on likely tokens
- **1.0**: Full distribution (default)

### Max Tokens (1 - model_max)
Controls maximum response length:
- GPT-4o: 4096 default (max 128k)
- Claude 3.5: 8192 default (max 200k)
- Adjust based on use case

### Example Configuration

```yaml
model_list:
  - model_name: gpt-4o-creative
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
      temperature: 1.2
      max_tokens: 8192
      top_p: 0.95
    model_info:
      mode: chat
      supports_function_calling: true

  - model_name: claude-precise
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY
      temperature: 0.3
      max_tokens: 4096
      top_p: 0.9
```

## Model Selection in Open WebUI

Once configured, all models appear in Open WebUI's model selector:

1. Open http://localhost:3000
2. Click the model dropdown in the chat interface
3. Select any configured model:
   - Direct API models (gpt-4o, claude-3-5-sonnet, etc.)
   - OpenRouter models (openrouter/gpt-4o, etc.)
4. Start chatting with your selected model

Models are automatically organized and labeled with their capabilities (vision support, function calling, etc.).

## Cost Tracking and Budgeting

RIN v1.1 includes comprehensive cost tracking powered by LiteLLM and SQLite.

### Features

- **Per-Model Cost Tracking**: Track spending for each model separately
- **Real-time Monitoring**: View costs as they accrue
- **Budget Limits**: Set monthly spending limits
- **Cost Database**: Persistent SQLite storage at `data/litellm/litellm_cost_tracking.db`

### Configuration

The cost tracking is automatically enabled with these settings in `config/litellm/config.yaml`:

```yaml
general_settings:
  # Cost tracking database
  database_url: "sqlite:////app/data/litellm_cost_tracking.db"
  
  # Budget settings
  max_budget: 100  # USD per month
  budget_duration: "30d"
  
  # Model-specific pricing (per 1M tokens)
  model_cost:
    gpt-4o:
      input_cost_per_token: 0.0000025
      output_cost_per_token: 0.00001
    claude-3-5-sonnet:
      input_cost_per_token: 0.000003
      output_cost_per_token: 0.000015
```

### Viewing Cost Data

Access the cost tracking database:

```bash
# Connect to the database
sqlite3 data/litellm/litellm_cost_tracking.db

# View total spending
SELECT model, SUM(cost) as total_cost 
FROM spend_log 
GROUP BY model;

# View recent requests
SELECT * FROM spend_log 
ORDER BY created_at DESC 
LIMIT 10;
```

### Budget Alerts

When spending exceeds 80% of your budget, LiteLLM will:
1. Log warnings in the console
2. Continue operating (won't block requests)
3. Track overage in the database

To enforce hard limits, modify the `general_settings` in `config.yaml`:

```yaml
general_settings:
  max_budget: 100
  budget_duration: "30d"
  enforce_budget: true  # Reject requests over budget
```

## Fallback Model Chains

RIN implements intelligent fallback chains for reliability. If a primary model fails, requests automatically retry with backup models.

### How It Works

```yaml
router_settings:
  routing_strategy: usage-based-routing-v2
  num_retries: 2
  timeout: 300
  allowed_fails: 3
  cooldown_time: 60
  
  fallbacks:
    # GPT-4 with fallbacks
    - gpt-4o:
      - openrouter/gpt-4o      # Try OpenRouter first
      - claude-3-5-sonnet       # Fall back to Claude
      - openrouter/llama-3.1-405b  # Final fallback
```

### Fallback Scenarios

**Scenario 1: API Outage**
```
User requests gpt-4o
→ OpenAI API is down
→ Automatically tries openrouter/gpt-4o
→ Request succeeds
```

**Scenario 2: Rate Limiting**
```
User requests claude-3-5-sonnet
→ Anthropic rate limit exceeded
→ Tries openrouter/claude-3-5-sonnet
→ Fails (same underlying API)
→ Falls back to gpt-4o
→ Request succeeds
```

**Scenario 3: Budget Exhaustion**
```
User requests gpt-4o
→ OpenAI budget exceeded
→ Falls back to openrouter/llama-3.1-405b (cheaper)
→ Request succeeds at lower cost
```

### Configuring Custom Fallback Chains

Add your own fallback chains in `config/litellm/config.yaml`:

```yaml
router_settings:
  fallbacks:
    # Custom chain for cost optimization
    - my-smart-model:
      - gpt-4o-mini              # Try cheap model first
      - claude-3-5-haiku         # Cheaper fallback
      - openrouter/mixtral-8x7b  # Open source fallback
    
    # Custom chain for vision tasks
    - vision-model:
      - gpt-4o                   # Best vision support
      - openrouter/gemini-pro    # Google vision
      - claude-3-opus            # Claude vision
```

## Configuration Examples

### Example 1: Cost-Optimized Setup

Prioritize cheaper models with expensive fallbacks:

```yaml
model_list:
  - model_name: smart-cheap
    litellm_params:
      model: openai/gpt-4o-mini
      api_key: os.environ/OPENAI_API_KEY
      temperature: 0.7
      max_tokens: 4096

router_settings:
  fallbacks:
    - smart-cheap:
      - gpt-4o-mini
      - claude-3-5-haiku
      - openrouter/mixtral-8x7b
      - gpt-4o  # Only if needed
```

### Example 2: Maximum Reliability

Use multiple providers for redundancy:

```yaml
router_settings:
  fallbacks:
    - reliable-model:
      - gpt-4o                      # Primary (OpenAI direct)
      - openrouter/gpt-4o          # Backup (OpenRouter)
      - claude-3-5-sonnet          # Different provider
      - openrouter/llama-3.1-405b  # Open source fallback
```

### Example 3: Specialized Models

Configure models for specific tasks:

```yaml
model_list:
  # Code generation
  - model_name: code-expert
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY
      temperature: 0.3
      max_tokens: 8192
  
  # Creative writing
  - model_name: creative-writer
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
      temperature: 1.2
      max_tokens: 4096
  
  # Research with web search
  - model_name: researcher
    litellm_params:
      model: openrouter/perplexity/llama-3.1-sonar-large-128k-online
      api_key: os.environ/OPENROUTER_API_KEY
      temperature: 0.7
      max_tokens: 4096
      extra_headers:
        HTTP-Referer: os.environ/OPENROUTER_SITE_URL
        X-Title: os.environ/OPENROUTER_APP_NAME
```

### Example 4: OpenRouter Models with Webhook Configuration

When adding OpenRouter models, always include the webhook headers:

```yaml
model_list:
  - model_name: openrouter/my-model
    litellm_params:
      model: openrouter/provider/model-name
      api_key: os.environ/OPENROUTER_API_KEY
      temperature: 0.7
      max_tokens: 4096
      extra_headers:
        HTTP-Referer: os.environ/OPENROUTER_SITE_URL
        X-Title: os.environ/OPENROUTER_APP_NAME
    model_info:
      mode: chat
```

These headers ensure proper attribution and prevent potential API response issues.

## Adding New Models

### Option 1: Automatic Sync (Recommended)

The easiest way to get new OpenRouter models:

```bash
# Sync all available models from OpenRouter
./scripts/sync_models.sh

# Restart LiteLLM
docker-compose restart litellm
```

This automatically adds all available OpenRouter models to your configuration.

See [Dynamic Models Guide](DYNAMIC_MODELS.md) for full details.

### Option 2: Manual Configuration

To manually add models from OpenRouter or other providers:

1. Browse available models at [OpenRouter](https://openrouter.ai/models)
2. Add to `config/litellm/config.yaml`:

```yaml
model_list:
  - model_name: my-new-model
    litellm_params:
      model: openrouter/provider/model-name
      api_key: os.environ/OPENROUTER_API_KEY
      temperature: 0.7
      max_tokens: 4096
      extra_headers:
        HTTP-Referer: os.environ/OPENROUTER_SITE_URL
        X-Title: os.environ/OPENROUTER_APP_NAME
    model_info:
      mode: chat
      supports_function_calling: false
```

**Note:** Always include `extra_headers` for OpenRouter models to ensure proper attribution and avoid API response issues.

3. Restart LiteLLM:
```bash
docker-compose restart litellm
```

4. Model appears in Open WebUI immediately

## Troubleshooting

### Models Not Appearing in Open WebUI

1. Check LiteLLM logs:
   ```bash
   docker-compose logs litellm
   ```

2. Verify API keys in `.env`:
   ```bash
   cat .env | grep API_KEY
   ```

3. Test LiteLLM directly:
   ```bash
   curl http://localhost:4000/models
   ```

### Cost Tracking Not Working

1. Verify database volume is mounted:
   ```bash
   ls -la data/litellm/
   ```

2. Check database connection:
   ```bash
   docker-compose logs litellm | grep database
   ```

3. Query the database directly:
   ```bash
   sqlite3 data/litellm/litellm_cost_tracking.db "SELECT COUNT(*) FROM spend_log;"
   ```

### Fallback Chain Not Triggering

1. Check router settings in `config.yaml`
2. Verify `num_retries` is set (default: 2)
3. Review LiteLLM logs for retry attempts:
   ```bash
   docker-compose logs litellm | grep -i "retry\|fallback"
   ```

## Best Practices

1. **Start with conservative budgets** - Set max_budget to a comfortable amount
2. **Use fallback chains** - Always configure fallbacks for critical applications
3. **Monitor costs regularly** - Check the database weekly
4. **Test new models** - Try models with low temperature/max_tokens first
5. **Cache responses** - LiteLLM's Redis cache reduces costs for repeated queries
6. **Use appropriate models** - Don't use GPT-4o for simple tasks when GPT-4o-mini works

## Next Steps

- Read about [RIN Architecture](../DESIGN.md)
- Learn about [Tool Integration](../tools/README.md)
- Explore [Workflow Automation](../workflows/README.md)
- Check [Release Notes](../RELEASE_NOTES.md) for latest updates

---

**Enhanced Model Support** - Making RIN more powerful, flexible, and reliable. 🧠🚀
