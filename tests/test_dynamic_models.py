#!/usr/bin/env python3
"""
Test script for dynamic OpenRouter model synchronization
"""

import os
import sys
import json
import yaml
import traceback
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

# Colors for terminal output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'


def print_test(name):
    print(f"\n{'='*70}")
    print(f"TEST: {name}")
    print(f"{'='*70}")


def print_pass(msg):
    print(f"{GREEN}✓ PASS: {msg}{NC}")


def print_fail(msg):
    print(f"{RED}✗ FAIL: {msg}{NC}")


def print_skip(msg):
    print(f"{YELLOW}⊘ SKIP: {msg}{NC}")


def test_script_exists():
    """Test that the sync script exists"""
    print_test("Script Existence")
    
    script_path = Path(__file__).parent.parent / 'scripts' / 'sync_openrouter_models.py'
    
    if script_path.exists():
        print_pass(f"Script exists at {script_path}")
        return True
    else:
        print_fail(f"Script not found at {script_path}")
        return False


def test_config_backup():
    """Test that config backup works"""
    print_test("Config Backup")
    
    config_path = Path(__file__).parent.parent / 'config' / 'litellm' / 'config.yaml'
    
    if not config_path.exists():
        print_skip("Config file doesn't exist, skipping backup test")
        return True
    
    # Import the sync module
    try:
        from sync_openrouter_models import update_litellm_config
        
        # Create a test model
        test_models = [{
            'id': 'test/model',
            'name': 'Test Model',
            'context_length': 4096,
            'pricing': {'prompt': '0.0001', 'completion': '0.0002'},
            'architecture': {}
        }]
        
        # Try to update config (this should create a backup)
        # We'll pass empty list to avoid actual changes
        backup_path = config_path.with_suffix('.yaml.backup')
        
        # Clean up any existing backup
        if backup_path.exists():
            backup_path.unlink()
        
        # Run update with backup=True and empty models (no actual changes)
        result = update_litellm_config(config_path, [], backup=True)
        
        if backup_path.exists():
            print_pass("Backup file created successfully")
            # Clean up
            backup_path.unlink()
            return True
        else:
            print_fail("Backup file not created")
            return False
            
    except Exception as e:
        print_fail(f"Backup test failed with error: {e}")
        return False


def test_model_conversion():
    """Test OpenRouter model to LiteLLM conversion"""
    print_test("Model Conversion")
    
    try:
        from sync_openrouter_models import convert_openrouter_model_to_litellm
        
        # Test model data
        test_model = {
            'id': 'openai/gpt-4o',
            'name': 'GPT-4o',
            'context_length': 128000,
            'pricing': {'prompt': '0.0000025', 'completion': '0.00001'},
            'architecture': {
                'supports_function_calling': True,
                'modality': 'multimodal'
            }
        }
        
        # Convert
        result = convert_openrouter_model_to_litellm(test_model)
        
        # Validate structure
        checks = [
            ('model_name' in result, "Has model_name field"),
            ('litellm_params' in result, "Has litellm_params field"),
            ('model_info' in result, "Has model_info field"),
            (result['model_name'].startswith('openrouter/'), "Model name has correct prefix"),
            (result['litellm_params']['model'] == 'openrouter/openai/gpt-4o', "Model ID correct"),
            (result['litellm_params']['temperature'] == 0.7, "Default temperature set"),
            (result['model_info'].get('supports_function_calling') == True, "Function calling detected"),
        ]
        
        all_passed = True
        for check, msg in checks:
            if check:
                print_pass(msg)
            else:
                print_fail(msg)
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_fail(f"Conversion test failed with error: {e}")
        traceback.print_exc()
        return False


def test_model_filtering():
    """Test model filtering logic"""
    print_test("Model Filtering")
    
    try:
        from sync_openrouter_models import filter_models_by_criteria
        
        # Test models with various properties
        test_models = [
            # Should be included
            {
                'id': 'openai/gpt-4o',
                'name': 'GPT-4o',
                'pricing': {'prompt': '0.0000025'},
                'deprecated': False
            },
            # Should be excluded - deprecated
            {
                'id': 'old/model',
                'name': 'Old Model',
                'pricing': {'prompt': '0.0001'},
                'deprecated': True
            },
            # Should be excluded - no pricing
            {
                'id': 'unavailable/model',
                'name': 'Unavailable Model',
                'deprecated': False
            },
            # Should be excluded - extended variant
            {
                'id': 'test/model-32k-extended',
                'name': 'Extended Model',
                'pricing': {'prompt': '0.0001'},
                'deprecated': False
            },
            # Should be included - allowed extended variant
            {
                'id': 'perplexity/sonar-128k-online',
                'name': 'Sonar Online',
                'pricing': {'prompt': '0.0001'},
                'deprecated': False
            }
        ]
        
        filtered = filter_models_by_criteria(test_models)
        
        checks = [
            (len(filtered) == 2, f"Filtered to 2 models (got {len(filtered)})"),
            (any(m['id'] == 'openai/gpt-4o' for m in filtered), "Includes valid model"),
            (not any(m['id'] == 'old/model' for m in filtered), "Excludes deprecated"),
            (not any(m['id'] == 'unavailable/model' for m in filtered), "Excludes unpriceable"),
            (not any(m['id'] == 'test/model-32k-extended' for m in filtered), "Excludes extended variants"),
            (any(m['id'] == 'perplexity/sonar-128k-online' for m in filtered), "Includes allowed extended")
        ]
        
        all_passed = True
        for check, msg in checks:
            if check:
                print_pass(msg)
            else:
                print_fail(msg)
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print_fail(f"Filtering test failed with error: {e}")
        traceback.print_exc()
        return False


def test_script_imports():
    """Test that script can be imported"""
    print_test("Script Imports")
    
    try:
        import sync_openrouter_models
        
        # Check required functions exist
        required_functions = [
            'fetch_openrouter_models',
            'convert_openrouter_model_to_litellm',
            'filter_models_by_criteria',
            'update_litellm_config'
        ]
        
        all_exist = True
        for func_name in required_functions:
            if hasattr(sync_openrouter_models, func_name):
                print_pass(f"Function {func_name} exists")
            else:
                print_fail(f"Function {func_name} missing")
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        print_fail(f"Import test failed with error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print(f"\n{'='*70}")
    print("Dynamic OpenRouter Model Sync - Test Suite")
    print(f"{'='*70}\n")
    
    tests = [
        ("Script Exists", test_script_exists),
        ("Script Imports", test_script_imports),
        ("Model Conversion", test_model_conversion),
        ("Model Filtering", test_model_filtering),
        ("Config Backup", test_config_backup),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_fail(f"{name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print(f"{'='*70}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{GREEN}PASS{NC}" if result else f"{RED}FAIL{NC}"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print(f"{GREEN}✅ All tests passed!{NC}\n")
        return 0
    else:
        print(f"{RED}❌ Some tests failed{NC}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
