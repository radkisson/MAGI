#!/usr/bin/env python3
"""
Model Search Tool
Search and filter OpenRouter models by capabilities, cost, and other criteria
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# ANSI color codes for terminal output
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color


def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✓ {text}{NC}")


def print_error(text: str):
    """Print error message"""
    print(f"{RED}✗ {text}{NC}")


def print_info(text: str):
    """Print info message"""
    print(f"  {text}")


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load LiteLLM configuration"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def search_models(
    models: List[Dict[str, Any]],
    tags: Optional[List[str]] = None,
    cost_tier: Optional[str] = None,
    min_popularity: Optional[float] = None,
    capabilities: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Search models by various criteria
    
    Args:
        models: List of model configurations
        tags: Filter by tags (e.g., 'openai', 'vision', 'function-calling')
        cost_tier: Filter by cost tier ('budget', 'standard', 'premium')
        min_popularity: Minimum popularity score (0-100)
        capabilities: Required capabilities
        
    Returns:
        Filtered list of models
    """
    results = []
    
    for model in models:
        model_info = model.get('model_info', {})
        
        # Skip non-OpenRouter models
        if not model.get('litellm_params', {}).get('model', '').startswith('openrouter/'):
            continue
        
        # Filter by tags
        if tags:
            model_tags = model_info.get('tags', [])
            if not any(tag in model_tags for tag in tags):
                continue
        
        # Filter by cost tier
        if cost_tier:
            model_cost = model_info.get('cost', {})
            if model_cost.get('tier') != cost_tier:
                continue
        
        # Filter by popularity
        if min_popularity is not None:
            model_popularity = model_info.get('popularity_score', 0)
            if model_popularity < min_popularity:
                continue
        
        # Filter by capabilities
        if capabilities:
            if 'function_calling' in capabilities:
                if not model_info.get('supports_function_calling'):
                    continue
            if 'vision' in capabilities:
                if not model_info.get('supports_vision'):
                    continue
        
        results.append(model)
    
    return results


def display_results(models: List[Dict[str, Any]], limit: int = 10):
    """Display search results"""
    if not models:
        print_error("No models found matching criteria")
        return
    
    print_success(f"Found {len(models)} models\n")
    
    for i, model in enumerate(models[:limit], 1):
        model_name = model.get('model_name', '')
        model_info = model.get('model_info', {})
        
        # Get basic info
        popularity = model_info.get('popularity_score', 0)
        cost = model_info.get('cost', {})
        tags = model_info.get('tags', [])
        
        # Display model
        print(f"{BLUE}{i}. {model_name}{NC}")
        print_info(f"   Popularity: {popularity:.1f}/100")
        
        if cost.get('tier'):
            tier = cost.get('tier', 'unknown')
            input_cost = cost.get('input_per_1m_tokens', 0)
            output_cost = cost.get('output_per_1m_tokens', 0)
            print_info(f"   Cost: {tier} (${input_cost:.2f}/${output_cost:.2f} per 1M tokens)")
        
        if tags:
            print_info(f"   Tags: {', '.join(tags)}")
        
        # Show capabilities
        caps = []
        if model_info.get('supports_function_calling'):
            caps.append('Function Calling')
        if model_info.get('supports_vision'):
            caps.append('Vision')
        if caps:
            print_info(f"   Capabilities: {', '.join(caps)}")
        
        print()
    
    if len(models) > limit:
        print_info(f"... and {len(models) - limit} more models")


def main():
    """Main execution function"""
    # Get paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    config_path = repo_root / "config" / "litellm" / "config.yaml"
    
    # Check if config exists
    if not config_path.exists():
        print_error(f"Config file not found: {config_path}")
        print_info("Run ./scripts/sync_models.sh first to sync models")
        return 1
    
    # Load config
    try:
        config = load_config(config_path)
        models = config.get('model_list', [])
    except Exception as e:
        print_error(f"Failed to load config: {e}")
        return 1
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print(f"{BLUE}Model Search Tool{NC}")
        print("\nUsage:")
        print("  python3 scripts/search_models.py <search_type> [options]")
        print("\nSearch types:")
        print("  --tag <tag>              Search by tag (openai, anthropic, vision, etc.)")
        print("  --cost <tier>            Search by cost tier (budget, standard, premium)")
        print("  --popular <score>        Search by minimum popularity score (0-100)")
        print("  --capability <cap>       Search by capability (function_calling, vision)")
        print("  --best-value             Show best value models")
        print("  --coding                 Show models good for coding")
        print("  --vision                 Show models with vision support")
        print("\nExamples:")
        print("  python3 scripts/search_models.py --tag vision")
        print("  python3 scripts/search_models.py --cost budget")
        print("  python3 scripts/search_models.py --popular 70")
        print("  python3 scripts/search_models.py --best-value")
        return 0
    
    # Process search criteria
    search_type = sys.argv[1]
    
    if search_type == '--tag' and len(sys.argv) > 2:
        tag = sys.argv[2]
        print(f"{BLUE}Searching for models with tag: {tag}{NC}\n")
        results = search_models(models, tags=[tag])
        display_results(results)
        
    elif search_type == '--cost' and len(sys.argv) > 2:
        tier = sys.argv[2]
        print(f"{BLUE}Searching for {tier} tier models{NC}\n")
        results = search_models(models, cost_tier=tier)
        display_results(results)
        
    elif search_type == '--popular' and len(sys.argv) > 2:
        min_score = float(sys.argv[2])
        print(f"{BLUE}Searching for models with popularity >= {min_score}{NC}\n")
        results = search_models(models, min_popularity=min_score)
        display_results(results)
        
    elif search_type == '--capability' and len(sys.argv) > 2:
        cap = sys.argv[2]
        print(f"{BLUE}Searching for models with {cap} capability{NC}\n")
        results = search_models(models, capabilities=[cap])
        display_results(results)
        
    elif search_type == '--best-value':
        print(f"{BLUE}Best Value Models{NC}\n")
        results = search_models(models, cost_tier='budget', min_popularity=60)
        if not results:
            results = search_models(models, cost_tier='standard', min_popularity=60)
        display_results(results, limit=5)
        
    elif search_type == '--coding':
        print(f"{BLUE}Models Recommended for Coding{NC}\n")
        results = search_models(models, tags=['anthropic'])
        if not results:
            results = search_models(models, tags=['openai'])
        display_results(results, limit=5)
        
    elif search_type == '--vision':
        print(f"{BLUE}Models with Vision Support{NC}\n")
        results = search_models(models, tags=['vision'])
        display_results(results, limit=5)
        
    else:
        print_error(f"Unknown search type: {search_type}")
        print_info("Run without arguments to see usage")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
