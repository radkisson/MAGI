#!/usr/bin/env python3
"""
OpenRouter Model Synchronization Script
Fetches the latest models from OpenRouter API and updates the litellm config.
"""

import os
import sys
import json
import yaml
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configuration constants
YAML_LINE_WIDTH = 1000  # Width for YAML output formatting

# ANSI color codes for terminal output
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}{text:^70}{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✓ {text}{NC}")


def print_error(text: str):
    """Print error message"""
    print(f"{RED}✗ {text}{NC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{NC}")


def print_info(text: str):
    """Print info message"""
    print(f"  {text}")


def fetch_openrouter_models(api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch available models from OpenRouter API
    
    Args:
        api_key: OpenRouter API key (optional, fetches public info without it)
        
    Returns:
        List of model dictionaries
    """
    url = "https://openrouter.ai/api/v1/models"
    headers = {}
    
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        print_info("Fetching models from OpenRouter API...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        models = data.get('data', [])
        
        print_success(f"Fetched {len(models)} models from OpenRouter")
        return models
        
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to fetch models from OpenRouter: {e}")
        return []


def convert_openrouter_model_to_litellm(model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert OpenRouter model format to LiteLLM config format
    
    Args:
        model: OpenRouter model dictionary
        
    Returns:
        LiteLLM model configuration dictionary
    """
    model_id = model.get('id', '')
    model_name = model.get('name', model_id)
    context_length = model.get('context_length', 4096)
    
    # Determine reasonable max_tokens (typically half of context length)
    max_tokens = min(8192, context_length // 2)
    
    # Check for capabilities
    architecture = model.get('architecture', {})
    supports_function_calling = architecture.get('supports_function_calling', False)
    supports_vision = 'vision' in model_id.lower() or architecture.get('modality', '').lower() in ['multimodal', 'vision']
    
    # Create friendly model name for RIN
    # Format: openrouter/{simplified-name}
    simple_name = model_id.replace('/', '-').replace(':', '-')
    
    litellm_model = {
        'model_name': f"openrouter/{simple_name}",
        'litellm_params': {
            'model': f"openrouter/{model_id}",
            'api_key': 'os.environ/OPENROUTER_API_KEY',
            'temperature': 0.7,
            'max_tokens': max_tokens,
            'top_p': 1.0
        },
        'model_info': {
            'mode': 'chat'
        }
    }
    
    # Add optional capabilities
    if supports_function_calling:
        litellm_model['model_info']['supports_function_calling'] = True
    if supports_vision:
        litellm_model['model_info']['supports_vision'] = True
    
    # Add metadata as comments (stored in description)
    if 'description' in model:
        litellm_model['model_info']['description'] = model['description']
    
    return litellm_model


def filter_models_by_criteria(models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter models based on criteria (active, available, etc.)
    
    Args:
        models: List of OpenRouter models
        
    Returns:
        Filtered list of models
    """
    # Extended context variants that should be included despite general filtering
    ALLOWED_EXTENDED_KEYWORDS = ['128k-online', 'sonar']
    
    # Extended context patterns to exclude (unless in allowed list)
    EXCLUDED_EXTENDED_PATTERNS = [':extended', '-extended', '32k', '64k', '128k']
    
    filtered = []
    
    for model in models:
        model_id = model.get('id', '')
        
        # Skip models that are marked as deprecated or unavailable
        if model.get('deprecated', False):
            continue
            
        # Only include models that have pricing info (means they're available)
        if not model.get('pricing'):
            continue
        
        # Skip extended context variants unless explicitly allowed
        model_id_lower = model_id.lower()
        is_extended = any(pattern in model_id_lower for pattern in EXCLUDED_EXTENDED_PATTERNS)
        is_allowed_extended = any(keyword in model_id_lower for keyword in ALLOWED_EXTENDED_KEYWORDS)
        
        if is_extended and not is_allowed_extended:
            continue
        
        filtered.append(model)
    
    return filtered


def update_litellm_config(
    config_path: Path,
    openrouter_models: List[Dict[str, Any]],
    backup: bool = True
) -> bool:
    """
    Update the LiteLLM config file with OpenRouter models
    
    Args:
        config_path: Path to litellm config.yaml
        openrouter_models: List of models to add
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
        
        # Separate OpenRouter models from other models
        non_openrouter_models = [
            m for m in existing_models 
            if not m.get('litellm_params', {}).get('model', '').startswith('openrouter/')
        ]
        
        # Convert OpenRouter models to LiteLLM format
        new_openrouter_models = [
            convert_openrouter_model_to_litellm(model) 
            for model in openrouter_models
        ]
        
        # Combine: keep non-OpenRouter models, add new OpenRouter models
        updated_models = non_openrouter_models + new_openrouter_models
        
        # Update config
        config['model_list'] = updated_models
        
        # Write updated config
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False, width=YAML_LINE_WIDTH)
        
        print_success(f"Updated config with {len(new_openrouter_models)} OpenRouter models")
        print_info(f"Total models in config: {len(updated_models)}")
        print_info(f"- Non-OpenRouter models: {len(non_openrouter_models)}")
        print_info(f"- OpenRouter models: {len(new_openrouter_models)}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to update config: {e}")
        return False


def main():
    """Main execution function"""
    print_header("OpenRouter Model Synchronization")
    
    # Get paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    config_path = repo_root / "config" / "litellm" / "config.yaml"
    
    # Check if config exists
    if not config_path.exists():
        print_error(f"Config file not found: {config_path}")
        return 1
    
    print_success(f"Found config file: {config_path}")
    
    # Get OpenRouter API key (optional)
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if api_key:
        print_success("Using OPENROUTER_API_KEY from environment")
    else:
        print_warning("No OPENROUTER_API_KEY found - fetching public model info")
        print_info("Set OPENROUTER_API_KEY in .env to use OpenRouter models")
    
    # Fetch models from OpenRouter
    all_models = fetch_openrouter_models(api_key)
    
    if not all_models:
        print_error("Could not fetch models from OpenRouter API")
        print_warning("This is normal if:")
        print_info("  - You haven't set OPENROUTER_API_KEY yet")
        print_info("  - Network is unavailable")
        print_info("  - OpenRouter API is temporarily down")
        print_info("")
        print_warning("Using existing static configuration")
        print_info("Run this script again later when you have:")
        print_info("  1. Set OPENROUTER_API_KEY in .env")
        print_info("  2. Network connectivity")
        return 0  # Exit successfully, not an error condition
    
    # Filter models
    print_info("Filtering models by availability criteria...")
    filtered_models = filter_models_by_criteria(all_models)
    
    if not filtered_models:
        print_warning("No models passed the availability filter")
        print_warning("Keeping existing config unchanged")
        return 0
    
    print_success(f"Filtered to {len(filtered_models)} available models")
    
    # Show some examples
    print_info("\nExample models that will be added:")
    for i, model in enumerate(filtered_models[:5]):
        model_id = model.get('id', '')
        model_name = model.get('name', '')
        print_info(f"  {i+1}. {model_name} ({model_id})")
    if len(filtered_models) > 5:
        print_info(f"  ... and {len(filtered_models) - 5} more")
    
    # Update config
    print_info("\nUpdating LiteLLM configuration...")
    success = update_litellm_config(config_path, filtered_models, backup=True)
    
    if success:
        print_success("\n✅ Configuration updated successfully!")
        print_info("Restart LiteLLM to apply changes:")
        print_info("  docker-compose restart litellm")
        return 0
    else:
        print_error("\n❌ Failed to update configuration")
        return 1


if __name__ == "__main__":
    sys.exit(main())
