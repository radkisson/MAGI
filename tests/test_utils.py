#!/usr/bin/env python3
"""
Test the shared utility module
"""

import sys
import os

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from utils import get_service_url


def test_get_service_url():
    """Test the shared get_service_url utility function"""
    print("Testing get_service_url utility...")
    
    # Test HTTP mode (default)
    os.environ['ENABLE_HTTPS'] = 'false'
    url = get_service_url("testservice", 1234)
    assert url == "http://testservice:1234", f"Expected http://testservice:1234, got {url}"
    print("  ✓ HTTP mode works")
    
    # Test HTTPS mode
    os.environ['ENABLE_HTTPS'] = 'true'
    url = get_service_url("testservice", 1234)
    assert url == "https://testservice:1234", f"Expected https://testservice:1234, got {url}"
    print("  ✓ HTTPS mode works")
    
    # Test environment variable override
    os.environ['TEST_URL'] = 'https://custom.example.com:5678'
    url = get_service_url("testservice", 1234, check_env_var="TEST_URL")
    assert url == "https://custom.example.com:5678", f"Expected custom URL, got {url}"
    print("  ✓ Environment variable override works")
    
    # Clean up
    del os.environ['TEST_URL']
    
    # Test default (no ENABLE_HTTPS set)
    if 'ENABLE_HTTPS' in os.environ:
        del os.environ['ENABLE_HTTPS']
    url = get_service_url("testservice", 1234)
    assert url == "http://testservice:1234", f"Expected http://testservice:1234, got {url}"
    print("  ✓ Defaults to HTTP when ENABLE_HTTPS not set")
    
    print("\n✅ All get_service_url tests passed!")


if __name__ == '__main__':
    try:
        test_get_service_url()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
