#!/usr/bin/env python3
"""
RIN Model List Helper
Safely parses and displays models from LiteLLM config
"""

import sys
import yaml
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("Usage: list_models_helper.py <config_path> <limit> [filter]", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    try:
        limit = int(sys.argv[2])
    except ValueError:
        print(f"Error: Invalid limit value: {sys.argv[2]}", file=sys.stderr)
        sys.exit(1)

    filter_type = sys.argv[3] if len(sys.argv) > 3 else 'all'

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        models = config.get('model_list', [])

        # Filter models
        if filter_type != 'all':
            filtered = []
            for model in models:
                model_info = model.get('model_info', {})
                tags = model_info.get('tags', [])

                if filter_type == 'openrouter':
                    if model.get('litellm_params', {}).get('model', '').startswith('openrouter/'):
                        filtered.append(model)
                elif filter_type == 'popular':
                    if model_info.get('popularity_score', 0) >= 70:
                        filtered.append(model)
                elif filter_type == 'budget':
                    cost = model_info.get('cost', {})
                    if cost.get('tier') == 'budget':
                        filtered.append(model)
                elif filter_type in tags:
                    filtered.append(model)
                # Don't append all models if filter doesn't match

            models = filtered

        # Sort by popularity if available
        models_sorted = sorted(
            models,
            key=lambda m: m.get('model_info', {}).get('popularity_score', 0),
            reverse=True
        )

        # Limit results
        limit_value = min(limit, len(models_sorted))

        print(f"Showing {limit_value} of {len(models_sorted)} total models")
        if filter_type != 'all':
            print(f"Filter: {filter_type}")
        print()

        for i, model in enumerate(models_sorted[:limit_value], 1):
            model_name = model.get('model_name', 'unknown')
            model_info = model.get('model_info', {})

            # Get metadata
            popularity = model_info.get('popularity_score', 0)
            cost = model_info.get('cost', {})
            tier = cost.get('tier', 'unknown')
            tags = model_info.get('tags', [])

            # Display
            print(f"{i}. {model_name}")
            if popularity > 0:
                print(f"   Popularity: {popularity}/100")
            if tier != 'unknown':
                print(f"   Cost Tier: {tier}")
            if tags:
                print(f"   Tags: {', '.join(tags[:5])}")

            # Capabilities
            caps = []
            if model_info.get('supports_function_calling'):
                caps.append('function-calling')
            if model_info.get('supports_vision'):
                caps.append('vision')
            if caps:
                print(f"   Capabilities: {', '.join(caps)}")
            print()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
