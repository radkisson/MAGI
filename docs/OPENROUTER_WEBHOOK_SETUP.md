# OpenRouter Webhook Configuration Guide

This guide explains how to configure OpenRouter webhooks in RIN for proper API attribution and functionality.

## What are OpenRouter Webhooks?

OpenRouter uses HTTP headers to track and attribute API requests to your application. These headers are:

- **HTTP-Referer**: Identifies your application's URL (site URL)
- **X-Title**: Sets your application's display name

These headers enable:
- Proper attribution of API calls in OpenRouter's dashboard
- Application rankings and discoverability in OpenRouter's ecosystem
- Prevention of potential API response issues with non-localhost keys
- Billing and analytics tracking

## Quick Setup

### 1. Get Your OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up or log in
3. Navigate to Keys section
4. Create a new API key

### 2. Configure Environment Variables

Edit your `.env` file (or create it from `.env.example`):

```bash
# Required: Your OpenRouter API key
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY_HERE

# Recommended: Webhook configuration
OPENROUTER_SITE_URL=http://localhost:3000
OPENROUTER_APP_NAME=RIN - Rhyzomic Intelligence Node
```

### 3. Customize for Production (Optional)

For production deployments with a public URL:

```bash
# Use your actual public domain
OPENROUTER_SITE_URL=https://your-domain.com

# Customize your app name for OpenRouter rankings
OPENROUTER_APP_NAME=My Custom RIN Instance
```

### 4. Restart the Services

```bash
docker-compose restart litellm
```

## Configuration Details

### Default Values

If you don't set these variables, RIN uses sensible defaults:

- `OPENROUTER_SITE_URL`: `http://localhost:3000` (your local WebUI)
- `OPENROUTER_APP_NAME`: `RIN - Rhyzomic Intelligence Node`

### How It Works

The configuration in `config/litellm/config.yaml` automatically includes these headers for all OpenRouter models:

```yaml
- model_name: openrouter/gpt-4o
  litellm_params:
    model: openrouter/openai/gpt-4o
    api_key: os.environ/OPENROUTER_API_KEY
    extra_headers:
      HTTP-Referer: os.environ/OPENROUTER_SITE_URL
      X-Title: os.environ/OPENROUTER_APP_NAME
```

LiteLLM reads the environment variables and includes them as HTTP headers in every request to OpenRouter.

## Verification

### Check Configuration

Run the test suite to verify your configuration:

```bash
python3 tests/test_model_config.py
```

Look for:
```
======================================================================
               TEST 7: OpenRouter Webhook Configuration               
======================================================================

✓ Found 12 OpenRouter models
✓ openrouter/gpt-4o - Properly configured with webhook headers
...
✓ All 12 OpenRouter models have proper webhook headers!
```

### Test API Calls

1. Start RIN:
   ```bash
   ./start.sh
   ```

2. Open WebUI at `http://localhost:3000`

3. Select an OpenRouter model (e.g., `openrouter/gpt-4o`)

4. Send a test message

5. Check OpenRouter dashboard to see attributed usage

## Troubleshooting

### Issue: API responses are empty or incomplete

**Cause**: Missing or incorrect webhook headers for non-localhost keys

**Solution**: 
1. Verify `OPENROUTER_SITE_URL` and `OPENROUTER_APP_NAME` are set in `.env`
2. Restart LiteLLM: `docker-compose restart litellm`
3. Check logs: `docker-compose logs litellm | grep -i openrouter`

### Issue: Usage not showing in OpenRouter dashboard

**Cause**: Headers not properly configured or using localhost key

**Solution**:
1. Ensure you're using a production API key (not a localhost key)
2. Set `OPENROUTER_SITE_URL` to your actual public URL (not localhost)
3. Verify headers are being sent (check LiteLLM logs with `set_verbose: true`)

### Issue: Models not appearing in Open WebUI

**Cause**: Unrelated to webhook configuration; likely API key or LiteLLM issue

**Solution**:
1. Verify `OPENROUTER_API_KEY` is set correctly in `.env`
2. Check LiteLLM service is running: `docker-compose ps litellm`
3. Check LiteLLM logs: `docker-compose logs litellm`
4. Test API directly: `curl http://localhost:4000/models`

## Advanced Configuration

### Custom Headers per Model

If you need different headers for specific models, edit `config/litellm/config.yaml`:

```yaml
- model_name: my-custom-openrouter-model
  litellm_params:
    model: openrouter/provider/model-name
    api_key: os.environ/OPENROUTER_API_KEY
    extra_headers:
      HTTP-Referer: https://my-specific-url.com
      X-Title: My Specific App Name
```

### Using Multiple OpenRouter Accounts

If you have multiple OpenRouter accounts with different keys:

```yaml
- model_name: openrouter-account-1/gpt-4o
  litellm_params:
    model: openrouter/openai/gpt-4o
    api_key: os.environ/OPENROUTER_API_KEY_1
    extra_headers:
      HTTP-Referer: os.environ/OPENROUTER_SITE_URL_1
      X-Title: os.environ/OPENROUTER_APP_NAME_1

- model_name: openrouter-account-2/gpt-4o
  litellm_params:
    model: openrouter/openai/gpt-4o
    api_key: os.environ/OPENROUTER_API_KEY_2
    extra_headers:
      HTTP-Referer: os.environ/OPENROUTER_SITE_URL_2
      X-Title: os.environ/OPENROUTER_APP_NAME_2
```

Then set the corresponding environment variables in `.env`.

## Best Practices

1. **Always set webhook headers** - Even for local development, to ensure consistent behavior
2. **Use meaningful app names** - This helps identify usage in OpenRouter dashboard
3. **Use production URLs for production** - Replace localhost with your actual domain
4. **Test after changes** - Run the test suite after modifying configuration
5. **Monitor usage** - Check OpenRouter dashboard to verify attribution is working

## Additional Resources

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenRouter API Reference](https://openrouter.ai/docs/api/reference/overview)
- [RIN Model Configuration Guide](./MODEL_CONFIGURATION.md)
- [LiteLLM Documentation](https://docs.litellm.ai/)

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review RIN logs: `docker-compose logs -f`
3. Test configuration: `python3 tests/test_model_config.py`
4. Open an issue on GitHub with logs and configuration details

---

**Note**: OpenRouter webhooks are configured automatically in RIN v1.1+. This setup requires no manual configuration in the OpenRouter UI - everything is handled through environment variables and the LiteLLM configuration.
