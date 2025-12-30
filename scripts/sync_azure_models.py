#!/usr/bin/env python3
"""
Azure OpenAI Model Synchronization Script
Auto-discovers Azure OpenAI deployments via API and updates the litellm config.

Environment Variables:
  AZURE_OPENAI_API_KEY: Azure OpenAI API key
  AZURE_OPENAI_ENDPOINT: Azure OpenAI endpoint URL
  AZURE_OPENAI_API_VERSION: API version (default: 2024-08-01-preview)
  AZURE_OPENAI_MODELS: (Optional) Comma-separated list of deployment:model pairs
                       If not set, will auto-discover deployments from the API
"""

import os
import sys
import yaml
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Configuration constants
YAML_LINE_WIDTH = 1000
DEFAULT_API_VERSION = "2024-08-01-preview"

# ANSI color codes
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'


def print_header(text: str):
    print(f"\n{BLUE}{'=' * 70}{NC}")
    print(f"{BLUE}{text:^70}{NC}")
    print(f"{BLUE}{'=' * 70}{NC}\n")


def print_success(text: str):
    print(f"{GREEN}✓ {text}{NC}")


def print_error(text: str):
    print(f"{RED}✗ {text}{NC}")


def print_warning(text: str):
    print(f"{YELLOW}⚠ {text}{NC}")


def print_info(text: str):
    print(f"  {text}")


def parse_azure_models_env(models_str: str) -> List[Tuple[str, str]]:
    """
    Parse AZURE_OPENAI_MODELS environment variable.

    Args:
        models_str: Comma-separated list of deployment:model pairs

    Returns:
        List of (deployment_name, model_name) tuples
    """
    models = []
    if not models_str or not models_str.strip():
        return models

    for entry in models_str.split(','):
        entry = entry.strip()
        if not entry:
            continue

        if ':' in entry:
            parts = entry.split(':', 1)
            deployment_name = parts[0].strip()
            model_name = parts[1].strip()
        else:
            # If no model specified, use deployment name as model name
            deployment_name = entry
            model_name = entry

        if deployment_name:
            models.append((deployment_name, model_name))

    return models


def discover_azure_deployments(endpoint: str, api_key: str, api_version: str) -> List[Tuple[str, str]]:
    """
    Auto-discover Azure OpenAI deployments via the API.

    Args:
        endpoint: Azure OpenAI endpoint URL
        api_key: Azure OpenAI API key
        api_version: API version

    Returns:
        List of (deployment_name, model_name) tuples
    """
    deployments = []
    
    # Clean endpoint URL
    endpoint = endpoint.rstrip('/')
    
    # Azure OpenAI deployments API
    url = f"{endpoint}/openai/deployments?api-version={api_version}"
    
    headers = {
        'api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    try:
        print_info(f"Fetching deployments from Azure OpenAI API...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            deployment_list = data.get('data', [])
            
            for deployment in deployment_list:
                deployment_name = deployment.get('id', '')
                model_name = deployment.get('model', deployment_name)
                status = deployment.get('status', 'unknown')
                
                # Only include succeeded deployments
                if status.lower() == 'succeeded' and deployment_name:
                    deployments.append((deployment_name, model_name))
                    
            print_success(f"Discovered {len(deployments)} active deployments")
            
        elif response.status_code == 404:
            print_warning("Deployments API not available - use AZURE_OPENAI_MODELS env var instead")
        else:
            print_warning(f"API returned status {response.status_code}: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print_warning("API request timed out - use AZURE_OPENAI_MODELS env var instead")
    except requests.exceptions.RequestException as e:
        print_warning(f"Failed to fetch deployments: {e}")
    except json.JSONDecodeError:
        print_warning("Invalid JSON response from API")
    
    return deployments


def get_model_capabilities(model_name: str) -> Dict[str, Any]:
    """
    Determine model capabilities based on model name.

    Args:
        model_name: The Azure OpenAI model name

    Returns:
        Dictionary of capabilities
    """
    model_lower = model_name.lower()

    capabilities = {
        'mode': 'chat',
        'supports_function_calling': False,
        'supports_vision': False,
    }

    # Embedding models
    if 'embedding' in model_lower or 'ada' in model_lower:
        capabilities['mode'] = 'embedding'
        return capabilities

    # Reranking models (Cohere)
    if 'rerank' in model_lower:
        capabilities['mode'] = 'rerank'
        return capabilities

    # Whisper (audio transcription)
    if 'whisper' in model_lower:
        capabilities['mode'] = 'audio_transcription'
        return capabilities

    # Sora (video generation)
    if 'sora' in model_lower:
        capabilities['mode'] = 'video_generation'
        return capabilities

    # Image generation models (DALL-E, Flux, etc.)
    if any(x in model_lower for x in ['dall-e', 'dalle', 'flux', 'image-gen', 'stable-diffusion']):
        capabilities['mode'] = 'image_generation'
        return capabilities

    # Model router
    if 'model-router' in model_lower or 'router' in model_lower:
        capabilities['supports_function_calling'] = True
        capabilities['supports_vision'] = True
        return capabilities

    # GPT-5.x, GPT-4o, GPT-4 Turbo support vision and function calling
    if any(x in model_lower for x in ['gpt-5', 'gpt-4o', 'gpt-4-turbo']):
        capabilities['supports_function_calling'] = True
        capabilities['supports_vision'] = True
    elif 'gpt-4.1' in model_lower:
        capabilities['supports_function_calling'] = True
        capabilities['supports_vision'] = True
    elif 'gpt-4' in model_lower:
        capabilities['supports_function_calling'] = True
    elif 'gpt-3.5' in model_lower or 'gpt-35' in model_lower:
        capabilities['supports_function_calling'] = True

    # o1/o3/o4 reasoning models
    if any(x in model_lower for x in ['o1', 'o3', 'o4']):
        capabilities['supports_function_calling'] = True

    # Grok models
    if 'grok' in model_lower:
        capabilities['supports_function_calling'] = True
        if 'reasoning' in model_lower:
            capabilities['supports_reasoning'] = True

    # DeepSeek models
    if 'deepseek' in model_lower:
        capabilities['supports_function_calling'] = True

    return capabilities


def get_model_max_tokens(model_name: str) -> int:
    """
    Get appropriate max_tokens for a model.

    Args:
        model_name: The Azure OpenAI model name

    Returns:
        Max tokens value
    """
    model_lower = model_name.lower()

    # Skip max_tokens for non-chat models
    if any(x in model_lower for x in ['embedding', 'ada-002', 'rerank', 'whisper', 'sora', 'flux', 'dall-e', 'dalle', 'image-gen']):
        return 0

    # Reasoning models can output more tokens
    if any(x in model_lower for x in ['o1', 'o3', 'o4']):
        return 16384

    # GPT-5.x models
    if 'gpt-5' in model_lower:
        return 8192

    # GPT-4o models
    if 'gpt-4o' in model_lower:
        return 4096

    # GPT-4.1 models
    if 'gpt-4.1' in model_lower:
        return 4096

    # GPT-4 Turbo
    if 'gpt-4-turbo' in model_lower:
        return 4096

    # GPT-4
    if 'gpt-4' in model_lower:
        return 8192

    # GPT-3.5
    if 'gpt-3.5' in model_lower or 'gpt-35' in model_lower:
        return 4096

    # DeepSeek
    if 'deepseek' in model_lower:
        return 8192

    # Grok
    if 'grok' in model_lower:
        return 8192

    # Default
    return 4096


def convert_azure_model_to_litellm(
    deployment_name: str,
    model_name: str,
    endpoint: str,
    api_version: str
) -> Dict[str, Any]:
    """
    Convert Azure OpenAI deployment to LiteLLM config format.

    Args:
        deployment_name: Azure deployment name
        model_name: The underlying model name
        endpoint: Azure OpenAI endpoint URL
        api_version: API version

    Returns:
        LiteLLM model configuration dictionary
    """
    capabilities = get_model_capabilities(model_name)
    max_tokens = get_model_max_tokens(model_name)
    model_lower = model_name.lower()

    litellm_model = {
        'model_name': f"azure/{deployment_name}",
        'litellm_params': {
            'model': f"azure/{deployment_name}",
            'api_key': 'os.environ/AZURE_OPENAI_API_KEY',
            'api_base': 'os.environ/AZURE_OPENAI_ENDPOINT',
            'api_version': api_version,
        },
        'model_info': capabilities.copy()
    }

    # Add chat-specific params for chat models
    mode = capabilities.get('mode', 'chat')
    if mode == 'chat':
        litellm_model['litellm_params']['temperature'] = 0.7
        litellm_model['litellm_params']['top_p'] = 1.0
        if max_tokens > 0:
            litellm_model['litellm_params']['max_tokens'] = max_tokens

    # Add description
    litellm_model['model_info']['description'] = (
        f"Azure OpenAI deployment '{deployment_name}' running {model_name}"
    )

    # Add tags based on model type
    tags = ['azure', 'enterprise']
    
    if 'gpt-5' in model_lower:
        tags.append('gpt-5')
    if 'gpt-4' in model_lower:
        tags.append('gpt-4')
    if 'gpt-3.5' in model_lower or 'gpt-35' in model_lower:
        tags.append('gpt-3.5')
    if any(x in model_lower for x in ['o1', 'o3', 'o4']):
        tags.append('reasoning')
    if 'deepseek' in model_lower:
        tags.append('deepseek')
    if 'grok' in model_lower:
        tags.append('grok')
    if 'cohere' in model_lower:
        tags.append('cohere')
    if 'rerank' in model_lower:
        tags.append('rerank')
    if 'embedding' in model_lower or 'ada' in model_lower:
        tags.append('embedding')
    if 'whisper' in model_lower:
        tags.append('audio')
    if 'sora' in model_lower:
        tags.append('video')
    if 'router' in model_lower:
        tags.append('router')
    if any(x in model_lower for x in ['flux', 'dall-e', 'dalle', 'image-gen', 'stable-diffusion']):
        tags.append('image-generation')

    litellm_model['model_info']['tags'] = tags

    return litellm_model


def update_litellm_config(
    config_path: Path,
    azure_models: List[Dict[str, Any]],
    backup: bool = True
) -> bool:
    """
    Update the LiteLLM config file with Azure OpenAI models.

    Args:
        config_path: Path to litellm config.yaml
        azure_models: List of Azure models to add
        backup: Whether to backup existing config

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read existing config
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Backup if requested
        if backup:
            backup_path = config_path.with_suffix('.yaml.backup')
            with open(backup_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            print_info(f"Backed up config to {backup_path}")

        # Get existing model list
        existing_models = config.get('model_list', [])

        # Remove existing Azure models (to avoid duplicates)
        non_azure_models = [
            m for m in existing_models
            if not m.get('model_name', '').startswith('azure/')
        ]

        # Combine: keep non-Azure models, add new Azure models
        updated_models = non_azure_models + azure_models

        # Update config
        config['model_list'] = updated_models

        # Write updated config
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, width=YAML_LINE_WIDTH)

        print_success(f"Updated config with {len(azure_models)} Azure OpenAI models")
        print_info(f"Total models in config: {len(updated_models)}")
        print_info(f"- Non-Azure models: {len(non_azure_models)}")
        print_info(f"- Azure models: {len(azure_models)}")

        return True

    except Exception as e:
        print_error(f"Failed to update config: {e}")
        return False


def main():
    """Main execution function"""
    print_header("Azure OpenAI Model Synchronization")

    # Get paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    config_path = repo_root / "config" / "litellm" / "config.yaml"

    # Check if config exists
    if not config_path.exists():
        print_error(f"Config file not found: {config_path}")
        return 1

    print_success(f"Found config file: {config_path}")

    # Get Azure OpenAI configuration from environment
    api_key = os.environ.get('AZURE_OPENAI_API_KEY', '').strip()
    endpoint = os.environ.get('AZURE_OPENAI_ENDPOINT', '').strip()
    api_version = os.environ.get('AZURE_OPENAI_API_VERSION', DEFAULT_API_VERSION).strip()
    models_str = os.environ.get('AZURE_OPENAI_MODELS', '').strip()

    # Check if Azure OpenAI is configured
    if not api_key:
        print_warning("AZURE_OPENAI_API_KEY not set - skipping Azure OpenAI sync")
        print_info("Set AZURE_OPENAI_API_KEY in .env to enable Azure OpenAI models")
        return 0

    if not endpoint:
        print_warning("AZURE_OPENAI_ENDPOINT not set - skipping Azure OpenAI sync")
        print_info("Set AZURE_OPENAI_ENDPOINT in .env (e.g., https://your-resource.openai.azure.com)")
        return 0

    print_success("Azure OpenAI configuration found")
    print_info(f"Endpoint: {endpoint}")
    print_info(f"API Version: {api_version}")

    # Try to get models - first from env var, then auto-discover
    model_pairs = []
    
    if models_str:
        # Use explicitly configured models
        print_info("Using models from AZURE_OPENAI_MODELS environment variable")
        model_pairs = parse_azure_models_env(models_str)
    else:
        # Try auto-discovery via API
        print_info("AZURE_OPENAI_MODELS not set - attempting auto-discovery...")
        model_pairs = discover_azure_deployments(endpoint, api_key, api_version)

    if not model_pairs:
        print_warning("No Azure OpenAI deployments found")
        print_info("Set AZURE_OPENAI_MODELS in .env with your deployment:model pairs")
        print_info("Example: AZURE_OPENAI_MODELS=gpt-4o:gpt-4o,gpt-4o-mini:gpt-4o-mini")
        return 0

    print_success(f"Found {len(model_pairs)} Azure OpenAI deployments")

    # Convert to LiteLLM format
    azure_models = []
    for deployment_name, model_name in model_pairs:
        print_info(f"  - {deployment_name} ({model_name})")
        litellm_model = convert_azure_model_to_litellm(
            deployment_name=deployment_name,
            model_name=model_name,
            endpoint=endpoint,
            api_version=api_version
        )
        azure_models.append(litellm_model)

    # Update config
    print_info("\nUpdating LiteLLM configuration...")
    success = update_litellm_config(config_path, azure_models, backup=True)

    if success:
        print_success("\n✅ Azure OpenAI configuration updated successfully!")
        print_info("Restart LiteLLM to apply changes:")
        print_info("  docker-compose restart litellm")
        return 0
    else:
        print_error("\n❌ Failed to update configuration")
        return 1


if __name__ == "__main__":
    sys.exit(main())
