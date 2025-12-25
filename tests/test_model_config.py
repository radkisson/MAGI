#!/usr/bin/env python3
"""
Test script for v1.1 Enhanced Model Support
Tests OpenRouter integration, cost tracking, and fallback chains
"""

import os
import sys
import yaml
import json
import time
from pathlib import Path

# Colors for terminal output
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color


def print_header(text):
    """Print a formatted header"""
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}{text:^70}{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")


def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓ {text}{NC}")


def print_error(text):
    """Print error message"""
    print(f"{RED}✗ {text}{NC}")


def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{NC}")


def print_info(text):
    """Print info message"""
    print(f"  {text}")


def test_config_file():
    """Test that the LiteLLM config file exists and is valid"""
    print_header("TEST 1: Configuration File Validation")
    
    config_path = Path(__file__).parent.parent / "config" / "litellm" / "config.yaml"
    
    assert config_path.exists(), f"Config file not found: {config_path}"
    print_success(f"Config file found: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print_success("Config file is valid YAML")
    except Exception as e:
        assert False, f"Config file is invalid YAML: {e}"
    
    # Check required sections
    required_sections = ['model_list', 'router_settings', 'general_settings']
    for section in required_sections:
        if section in config:
            print_success(f"Section '{section}' present")
        else:
            print_error(f"Section '{section}' missing")
            assert False, f"Section '{section}' missing"


def test_model_definitions():
    """Test that all models are properly defined"""
    print_header("TEST 2: Model Definitions")
    
    config_path = Path(__file__).parent.parent / "config" / "litellm" / "config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    models = config.get('model_list', [])
    
    assert models, "No models defined in config"
    print_success(f"Found {len(models)} model definitions")
    
    # Check for OpenRouter models
    openrouter_models = [m for m in models if 'openrouter' in m.get('litellm_params', {}).get('model', '')]
    if openrouter_models:
        print_success(f"OpenRouter integration: {len(openrouter_models)} models")
    else:
        print_warning("No OpenRouter models found")
    
    # Check for required parameters
    models_with_temp = [m for m in models if 'temperature' in m.get('litellm_params', {})]
    models_with_max_tokens = [m for m in models if 'max_tokens' in m.get('litellm_params', {})]
    models_with_top_p = [m for m in models if 'top_p' in m.get('litellm_params', {})]
    
    print_success(f"Models with temperature: {len(models_with_temp)}/{len(models)}")
    print_success(f"Models with max_tokens: {len(models_with_max_tokens)}/{len(models)}")
    print_success(f"Models with top_p: {len(models_with_top_p)}/{len(models)}")
    
    # List model categories
    print_info("\nModel categories:")
    openai_models = [m['model_name'] for m in models if 'openai' in m.get('litellm_params', {}).get('model', '')]
    anthropic_models = [m['model_name'] for m in models if 'anthropic' in m.get('litellm_params', {}).get('model', '')]
    llama_models = [m['model_name'] for m in models if 'llama' in m.get('litellm_params', {}).get('model', '').lower()]
    google_models = [m['model_name'] for m in models if 'google' in m.get('litellm_params', {}).get('model', '').lower() or 'gemini' in m.get('litellm_params', {}).get('model', '').lower()]
    mistral_models = [m['model_name'] for m in models if 'mistral' in m.get('litellm_params', {}).get('model', '').lower()]
    
    if openai_models:
        print_info(f"  OpenAI: {', '.join(openai_models)}")
    if anthropic_models:
        print_info(f"  Anthropic: {', '.join(anthropic_models)}")
    if llama_models:
        print_info(f"  Llama: {', '.join(llama_models)}")
    if google_models:
        print_info(f"  Google: {', '.join(google_models)}")
    if mistral_models:
        print_info(f"  Mistral: {', '.join(mistral_models)}")


def test_cost_tracking():
    """Test that cost tracking is properly configured"""
    print_header("TEST 3: Cost Tracking Configuration")
    
    config_path = Path(__file__).parent.parent / "config" / "litellm" / "config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    general_settings = config.get('general_settings', {})
    
    # Check database URL
    db_url = general_settings.get('database_url')
    assert db_url and 'sqlite' in db_url, "Cost tracking database not configured"
    print_success(f"Cost tracking database configured: {db_url}")
    
    # Check budget settings
    max_budget = general_settings.get('max_budget')
    if max_budget:
        print_success(f"Budget limit set: ${max_budget}")
    else:
        print_warning("No budget limit configured")
    
    budget_duration = general_settings.get('budget_duration')
    if budget_duration:
        print_success(f"Budget duration: {budget_duration}")
    else:
        print_warning("No budget duration configured")
    
    # Check model costs
    model_cost = general_settings.get('model_cost', {})
    if model_cost:
        print_success(f"Custom pricing for {len(model_cost)} models")
        for model, pricing in model_cost.items():
            input_cost = pricing.get('input_cost_per_token', 0) * 1_000_000
            output_cost = pricing.get('output_cost_per_token', 0) * 1_000_000
            print_info(f"  {model}: ${input_cost:.2f}/${output_cost:.2f} per 1M tokens")
    else:
        print_warning("No custom model pricing (will use LiteLLM defaults)")


def test_fallback_chains():
    """Test that fallback chains are properly configured"""
    print_header("TEST 4: Fallback Chain Configuration")
    
    config_path = Path(__file__).parent.parent / "config" / "litellm" / "config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    router_settings = config.get('router_settings', {})
    
    # Check routing strategy
    strategy = router_settings.get('routing_strategy')
    assert strategy, "No routing strategy configured"
    print_success(f"Routing strategy: {strategy}")
    
    # Check retry settings
    num_retries = router_settings.get('num_retries')
    if num_retries:
        print_success(f"Retry attempts: {num_retries}")
    else:
        print_warning("No retry configuration")
    
    timeout = router_settings.get('timeout')
    if timeout:
        print_success(f"Request timeout: {timeout}s")
    else:
        print_warning("No timeout configuration")
    
    # Check fallback chains
    fallbacks = router_settings.get('fallbacks', [])
    if fallbacks:
        print_success(f"Fallback chains configured: {len(fallbacks)} models")
        for fallback in fallbacks:
            for primary, backups in fallback.items():
                print_info(f"  {primary} → {' → '.join(backups)}")
    else:
        print_warning("No fallback chains configured")
    
    # Check cooldown and health settings
    cooldown = router_settings.get('cooldown_time')
    if cooldown:
        print_success(f"Cooldown period: {cooldown}s")
    
    allowed_fails = router_settings.get('allowed_fails')
    if allowed_fails:
        print_success(f"Allowed failures: {allowed_fails}")


def test_docker_compose():
    """Test Docker Compose configuration"""
    print_header("TEST 5: Docker Compose Configuration")
    
    compose_path = Path(__file__).parent.parent / "docker-compose.yml"
    
    assert compose_path.exists(), f"docker-compose.yml not found: {compose_path}"
    print_success(f"docker-compose.yml found: {compose_path}")
    
    with open(compose_path, 'r') as f:
        compose = yaml.safe_load(f)
    
    services = compose.get('services', {})
    
    # Check LiteLLM service
    litellm = services.get('litellm', {})
    assert litellm, "LiteLLM service not defined"
    print_success("LiteLLM service defined")
    
    # Check volumes
    volumes = litellm.get('volumes', [])
    config_volume = any('config.yaml' in v for v in volumes)
    data_volume = any('data/litellm' in v for v in volumes)
    
    assert config_volume, "Config volume not mounted"
    print_success("Config volume mounted")
    
    assert data_volume, "Data volume not mounted"
    print_success("Data volume mounted (for cost tracking database)")
    
    # Check Redis dependency
    depends_on = litellm.get('depends_on', [])
    if 'redis' in depends_on:
        print_success("Redis dependency configured")
    else:
        print_warning("Redis dependency not configured")
    
    # Check environment
    environment = litellm.get('environment', [])
    has_redis_config = any('REDIS' in str(env) for env in environment)
    if has_redis_config:
        print_success("Redis environment configured")


def test_env_file():
    """Test environment file configuration"""
    print_header("TEST 6: Environment Configuration")
    
    env_example_path = Path(__file__).parent.parent / ".env.example"
    
    assert env_example_path.exists(), f".env.example not found: {env_example_path}"
    print_success(f".env.example found: {env_example_path}")
    
    with open(env_example_path, 'r') as f:
        env_content = f.read()
    
    # Check for required API keys
    required_keys = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'OPENROUTER_API_KEY',
        'LITELLM_MASTER_KEY',
        'SEARXNG_SECRET',
        'FIRECRAWL_API_KEY'
    ]
    
    for key in required_keys:
        assert key in env_content, f"{key} missing from .env.example"
        print_success(f"{key} present in .env.example")
    
    # Check for OpenRouter webhook configuration
    webhook_keys = ['OPENROUTER_SITE_URL', 'OPENROUTER_APP_NAME']
    for key in webhook_keys:
        assert key in env_content, f"{key} missing from .env.example"
        print_success(f"{key} present in .env.example (webhook config)")


def test_openrouter_webhook_headers():
    """Test that all OpenRouter models have webhook headers configured"""
    print_header("TEST 7: OpenRouter Webhook Configuration")
    
    config_path = Path(__file__).parent.parent / "config" / "litellm" / "config.yaml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    models = config.get('model_list', [])
    openrouter_models = [m for m in models if m['model_name'].startswith('openrouter/')]
    
    if not openrouter_models:
        print_warning("No OpenRouter models found")
        return True
    
    print_success(f"Found {len(openrouter_models)} OpenRouter models")
    
    missing_headers = []
    for model in openrouter_models:
        model_name = model['model_name']
        extra_headers = model.get('litellm_params', {}).get('extra_headers', {})
        
        if not extra_headers:
            missing_headers.append(model_name)
            print_error(f"{model_name} - Missing extra_headers")
        else:
            has_referer = 'HTTP-Referer' in extra_headers
            has_title = 'X-Title' in extra_headers
            
            if has_referer and has_title:
                referer_value = extra_headers['HTTP-Referer']
                title_value = extra_headers['X-Title']
                
                # Verify they reference environment variables with exact pattern
                expected_referer = 'os.environ/OPENROUTER_SITE_URL'
                expected_title = 'os.environ/OPENROUTER_APP_NAME'
                
                if referer_value == expected_referer and title_value == expected_title:
                    print_success(f"{model_name} - Properly configured with webhook headers")
                else:
                    print_warning(f"{model_name} - Has headers but not using expected environment variable pattern")
                    print_info(f"    Expected: {expected_referer}, Got: {referer_value}")
                    print_info(f"    Expected: {expected_title}, Got: {title_value}")
            else:
                missing = []
                if not has_referer:
                    missing.append("HTTP-Referer")
                if not has_title:
                    missing.append("X-Title")
                print_error(f"{model_name} - Missing: {', '.join(missing)}")
                missing_headers.append(model_name)
    
    if missing_headers:
        print_error(f"{len(missing_headers)} models have incomplete or missing webhook headers")
        assert False, f"OpenRouter models missing webhook configuration: {', '.join(missing_headers)}"
    else:
        print_success(f"All {len(openrouter_models)} OpenRouter models have proper webhook headers!")
    
    # Print explanation
    print_info("\nWebhook headers explanation:")
    print_info("  HTTP-Referer: Identifies the originating site/application")
    print_info("  X-Title: Sets the application's display name in OpenRouter")
    print_info("  These enable proper API attribution and prevent response issues")


def test_start_script():
    """Test start.sh creates required directories"""
    print_header("TEST 8: Start Script Configuration")
    
    start_script_path = Path(__file__).parent.parent / "start.sh"
    
    assert start_script_path.exists(), f"start.sh not found: {start_script_path}"
    print_success(f"start.sh found: {start_script_path}")
    
    with open(start_script_path, 'r') as f:
        start_content = f.read()
    
    # Check for litellm directory creation
    assert 'litellm' in start_content and 'mkdir' in start_content, "start.sh doesn't create litellm data directory"
    print_success("start.sh creates litellm data directory")
    
    # Check for permissions
    if 'chmod' in start_content and 'litellm' in start_content:
        print_success("start.sh sets litellm directory permissions")
    else:
        print_warning("start.sh may not set litellm directory permissions")


def main():
    """Run all tests"""
    print_header("RIN v1.1 Enhanced Model Support - Configuration Tests")
    
    tests = [
        ("Configuration File", test_config_file),
        ("Model Definitions", test_model_definitions),
        ("Cost Tracking", test_cost_tracking),
        ("Fallback Chains", test_fallback_chains),
        ("Docker Compose", test_docker_compose),
        ("Environment File", test_env_file),
        ("OpenRouter Webhook Headers", test_openrouter_webhook_headers),
        ("Start Script", test_start_script),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Test failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        if result:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print_success("\n✅ All tests passed! Configuration is ready.")
        return 0
    else:
        print_error(f"\n❌ {total - passed} test(s) failed. Please review the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
