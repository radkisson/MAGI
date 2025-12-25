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
    
    # Add popularity score
    popularity = calculate_popularity_score(model)
    litellm_model['model_info']['popularity_score'] = round(popularity, 1)
    
    # Add cost metadata for filtering
    litellm_model = add_cost_metadata(model, litellm_model)
    
    # Add capability tags for search
    litellm_model = add_capability_tags(model, litellm_model)
    
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


def calculate_popularity_score(model: Dict[str, Any]) -> float:
    """
    Calculate a popularity score for a model based on various metrics
    
    Args:
        model: OpenRouter model dictionary
        
    Returns:
        Popularity score (0-100)
    """
    score = 50.0  # Base score
    
    # Well-known providers get bonus points
    model_id = model.get('id', '').lower()
    if 'openai' in model_id or 'gpt' in model_id:
        score += 20
    elif 'anthropic' in model_id or 'claude' in model_id:
        score += 15
    elif 'meta' in model_id or 'llama' in model_id:
        score += 10
    elif 'google' in model_id or 'gemini' in model_id:
        score += 10
    elif 'mistral' in model_id:
        score += 8
    
    # Models with lower pricing tend to be more popular
    pricing = model.get('pricing', {})
    try:
        prompt_cost = float(pricing.get('prompt', 0))
        if prompt_cost > 0 and prompt_cost < 0.00001:  # Very cheap
            score += 10
        elif prompt_cost < 0.00005:  # Moderately priced
            score += 5
    except (ValueError, TypeError):
        pass
    
    # Models with function calling are more versatile
    arch = model.get('architecture', {})
    if arch.get('supports_function_calling'):
        score += 5
    
    # Vision models are in demand
    if 'vision' in model_id or arch.get('modality') == 'multimodal':
        score += 5
    
    return min(100.0, score)


def add_cost_metadata(model: Dict[str, Any], litellm_model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add cost information to model metadata for filtering
    
    Args:
        model: OpenRouter model dictionary
        litellm_model: LiteLLM model configuration
        
    Returns:
        Updated LiteLLM model with cost metadata
    """
    pricing = model.get('pricing', {})
    
    try:
        prompt_cost = float(pricing.get('prompt', 0))
        completion_cost = float(pricing.get('completion', 0))
        
        # Calculate cost per 1M tokens
        cost_per_1m_input = prompt_cost * 1_000_000
        cost_per_1m_output = completion_cost * 1_000_000
        
        # Categorize cost
        if cost_per_1m_input < 0.5:
            cost_tier = 'budget'
        elif cost_per_1m_input < 5.0:
            cost_tier = 'standard'
        else:
            cost_tier = 'premium'
        
        litellm_model['model_info']['cost'] = {
            'input_per_1m_tokens': round(cost_per_1m_input, 2),
            'output_per_1m_tokens': round(cost_per_1m_output, 2),
            'tier': cost_tier
        }
    except (ValueError, TypeError, KeyError):
        # If pricing info is missing or invalid, mark as unknown
        litellm_model['model_info']['cost'] = {
            'tier': 'unknown'
        }
    
    return litellm_model


def add_capability_tags(model: Dict[str, Any], litellm_model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add searchable capability tags to model
    
    Args:
        model: OpenRouter model dictionary
        litellm_model: LiteLLM model configuration
        
    Returns:
        Updated LiteLLM model with capability tags
    """
    tags = []
    model_id = model.get('id', '').lower()
    arch = model.get('architecture', {})
    
    # Add provider tags
    if 'openai' in model_id:
        tags.append('openai')
    if 'anthropic' in model_id:
        tags.append('anthropic')
    if 'meta' in model_id or 'llama' in model_id:
        tags.append('meta')
    if 'google' in model_id or 'gemini' in model_id:
        tags.append('google')
    if 'mistral' in model_id:
        tags.append('mistral')
    
    # Add capability tags
    if arch.get('supports_function_calling'):
        tags.append('function-calling')
    if 'vision' in model_id or arch.get('modality') == 'multimodal':
        tags.append('vision')
    if 'online' in model_id or 'search' in model_id:
        tags.append('web-search')
    
    # Add context size tags
    context_length = model.get('context_length', 0)
    if context_length >= 100000:
        tags.append('long-context')
    
    # Add model size tags (if available in name)
    if any(size in model_id for size in ['405b', '70b', '8x7b', '8x22b']):
        tags.append('large')
    elif any(size in model_id for size in ['7b', '8b', '13b']):
        tags.append('small')
    
    litellm_model['model_info']['tags'] = tags
    
    return litellm_model


def rank_models_by_popularity(models: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank models by popularity score
    
    Args:
        models: List of OpenRouter models
        
    Returns:
        Sorted list of models with popularity scores
    """
    # Calculate popularity scores
    for model in models:
        model['_popularity_score'] = calculate_popularity_score(model)
    
    # Sort by popularity (descending)
    sorted_models = sorted(models, key=lambda m: m.get('_popularity_score', 0), reverse=True)
    
    return sorted_models


def generate_model_recommendations(models: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Generate model recommendations for different use cases
    
    Args:
        models: List of OpenRouter models with metadata
        
    Returns:
        Dictionary of recommendations by category
    """
    recommendations = {
        'best_value': [],
        'most_capable': [],
        'fastest': [],
        'budget_friendly': [],
        'vision_tasks': [],
        'coding': []
    }
    
    # Sort models by different criteria
    models_by_cost = sorted(models, key=lambda m: float(m.get('pricing', {}).get('prompt', 999)))
    models_by_popularity = sorted(models, key=lambda m: m.get('_popularity_score', 0), reverse=True)
    
    # Best value (good performance, reasonable cost)
    for model in models_by_popularity[:10]:
        model_id = model.get('id', '')
        pricing = model.get('pricing', {})
        prompt_cost = float(pricing.get('prompt', 0))
        if prompt_cost < 0.00005:  # Reasonable cost
            recommendations['best_value'].append(model_id)
            if len(recommendations['best_value']) >= 3:
                break
    
    # Most capable (premium models)
    premium_models = ['openai/gpt-4o', 'anthropic/claude-3.5-sonnet', 'anthropic/claude-3-opus']
    for model in models:
        model_id = model.get('id', '')
        if model_id in premium_models:
            recommendations['most_capable'].append(model_id)
    
    # Fastest (small, optimized models)
    for model in models:
        model_id = model.get('id', '')
        if any(x in model_id.lower() for x in ['mini', 'flash', 'haiku', 'turbo']):
            recommendations['fastest'].append(model_id)
            if len(recommendations['fastest']) >= 3:
                break
    
    # Budget friendly (cheapest models)
    for model in models_by_cost[:5]:
        pricing = model.get('pricing', {})
        if pricing and float(pricing.get('prompt', 999)) < 0.000005:
            recommendations['budget_friendly'].append(model.get('id', ''))
    
    # Vision tasks
    for model in models:
        arch = model.get('architecture', {})
        model_id = model.get('id', '')
        if 'vision' in model_id.lower() or arch.get('modality') == 'multimodal':
            recommendations['vision_tasks'].append(model_id)
            if len(recommendations['vision_tasks']) >= 3:
                break
    
    # Coding (models known for coding)
    for model in models:
        model_id = model.get('id', '')
        if any(x in model_id.lower() for x in ['claude', 'gpt-4', 'codellama', 'deepseek']):
            recommendations['coding'].append(model_id)
            if len(recommendations['coding']) >= 3:
                break
    
    return recommendations


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
    
    # Rank models by popularity
    print_info("\nRanking models by popularity...")
    ranked_models = rank_models_by_popularity(filtered_models)
    print_success("Models ranked successfully")
    
    # Generate recommendations
    print_info("\nGenerating model recommendations...")
    recommendations = generate_model_recommendations(ranked_models)
    
    # Display top recommendations
    print_info("\n📊 Top Model Recommendations:")
    if recommendations['best_value']:
        print_info(f"  💎 Best Value: {', '.join(recommendations['best_value'][:3])}")
    if recommendations['most_capable']:
        print_info(f"  🚀 Most Capable: {', '.join(recommendations['most_capable'][:3])}")
    if recommendations['fastest']:
        print_info(f"  ⚡ Fastest: {', '.join(recommendations['fastest'][:3])}")
    if recommendations['budget_friendly']:
        print_info(f"  💰 Budget Friendly: {', '.join(recommendations['budget_friendly'][:3])}")
    if recommendations['vision_tasks']:
        print_info(f"  👁️  Vision Tasks: {', '.join(recommendations['vision_tasks'][:3])}")
    if recommendations['coding']:
        print_info(f"  💻 Coding: {', '.join(recommendations['coding'][:3])}")
    
    # Show top-ranked models
    print_info("\n⭐ Top 5 Models by Popularity Score:")
    for i, model in enumerate(ranked_models[:5], 1):
        model_id = model.get('id', '')
        model_name = model.get('name', '')
        score = model.get('_popularity_score', 0)
        print_info(f"  {i}. {model_name} ({model_id}) - Score: {score:.1f}")
    if len(ranked_models) > 5:
        print_info(f"  ... and {len(ranked_models) - 5} more")
    
    # Save recommendations to a file
    recommendations_path = repo_root / "data" / "model_recommendations.json"
    recommendations_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(recommendations_path, 'w') as f:
            json.dump(recommendations, f, indent=2)
        print_success(f"\n💾 Recommendations saved to: {recommendations_path}")
    except Exception as e:
        print_warning(f"Could not save recommendations: {e}")
    
    # Update config
    print_info("\nUpdating LiteLLM configuration...")
    success = update_litellm_config(config_path, ranked_models, backup=True)
    
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
