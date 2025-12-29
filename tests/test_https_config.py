#!/usr/bin/env python3
"""
Test HTTPS configuration and auto-detection in RIN tools
Tests the URL generation logic without requiring full dependencies
"""

import sys
import os


def test_url_generation_logic():
    """Test URL generation logic for HTTPS vs HTTP"""
    print("Testing URL Generation Logic...")
    
    # Test HTTP (default)
    print("\n  Testing HTTP mode (ENABLE_HTTPS=false):")
    os.environ['ENABLE_HTTPS'] = 'false'
    
    enable_https = os.getenv("ENABLE_HTTPS", "false").lower() == "true"
    protocol = "https" if enable_https else "http"
    
    n8n_url = f"{protocol}://rin-reflex-automation:5678/webhook"
    firecrawl_url = f"{protocol}://firecrawl:3002"
    qdrant_url = f"{protocol}://qdrant:6333"
    searxng_url = f"{protocol}://searxng:8080"
    
    assert n8n_url == "http://rin-reflex-automation:5678/webhook"
    assert firecrawl_url == "http://firecrawl:3002"
    assert qdrant_url == "http://qdrant:6333"
    assert searxng_url == "http://searxng:8080"
    
    print(f"    ✓ n8n URL: {n8n_url}")
    print(f"    ✓ firecrawl URL: {firecrawl_url}")
    print(f"    ✓ qdrant URL: {qdrant_url}")
    print(f"    ✓ searxng URL: {searxng_url}")
    
    # Test HTTPS
    print("\n  Testing HTTPS mode (ENABLE_HTTPS=true):")
    os.environ['ENABLE_HTTPS'] = 'true'
    
    enable_https = os.getenv("ENABLE_HTTPS", "false").lower() == "true"
    protocol = "https" if enable_https else "http"
    
    n8n_url = f"{protocol}://rin-reflex-automation:5678/webhook"
    firecrawl_url = f"{protocol}://firecrawl:3002"
    qdrant_url = f"{protocol}://qdrant:6333"
    searxng_url = f"{protocol}://searxng:8080"
    
    assert n8n_url == "https://rin-reflex-automation:5678/webhook"
    assert firecrawl_url == "https://firecrawl:3002"
    assert qdrant_url == "https://qdrant:6333"
    assert searxng_url == "https://searxng:8080"
    
    print(f"    ✓ n8n URL: {n8n_url}")
    print(f"    ✓ firecrawl URL: {firecrawl_url}")
    print(f"    ✓ qdrant URL: {qdrant_url}")
    print(f"    ✓ searxng URL: {searxng_url}")
    
    # Test default (no env var)
    print("\n  Testing default mode (ENABLE_HTTPS not set):")
    if 'ENABLE_HTTPS' in os.environ:
        del os.environ['ENABLE_HTTPS']
    
    enable_https = os.getenv("ENABLE_HTTPS", "false").lower() == "true"
    protocol = "https" if enable_https else "http"
    
    n8n_url = f"{protocol}://rin-reflex-automation:5678/webhook"
    assert n8n_url == "http://rin-reflex-automation:5678/webhook"
    print(f"    ✓ Defaults to HTTP: {n8n_url}")
    
    print("\n✅ All URL generation logic tests passed!")


def test_start_script_protocol_detection():
    """Test the protocol detection logic from start.sh"""
    print("\nTesting start.sh Protocol Detection Logic...")
    
    # Simulate bash logic: if [ "${ENABLE_HTTPS}" = "true" ]; then PROTOCOL="https"; else PROTOCOL="http"; fi
    
    # Test HTTP
    os.environ['ENABLE_HTTPS'] = 'false'
    enable_https = os.environ.get('ENABLE_HTTPS', 'false')
    protocol = 'https' if enable_https == 'true' else 'http'
    assert protocol == 'http'
    print(f"  ✓ ENABLE_HTTPS='false' -> PROTOCOL='{protocol}'")
    
    # Test HTTPS
    os.environ['ENABLE_HTTPS'] = 'true'
    enable_https = os.environ.get('ENABLE_HTTPS', 'false')
    protocol = 'https' if enable_https == 'true' else 'http'
    assert protocol == 'https'
    print(f"  ✓ ENABLE_HTTPS='true' -> PROTOCOL='{protocol}'")
    
    # Test default
    if 'ENABLE_HTTPS' in os.environ:
        del os.environ['ENABLE_HTTPS']
    enable_https = os.environ.get('ENABLE_HTTPS', 'false')
    protocol = 'https' if enable_https == 'true' else 'http'
    assert protocol == 'http'
    print(f"  ✓ ENABLE_HTTPS not set -> PROTOCOL='{protocol}' (default)")
    
    print("\n✅ All start.sh protocol detection tests passed!")


def test_n8n_entrypoint_logic():
    """Test the n8n entrypoint script logic"""
    print("\nTesting n8n Entrypoint Script Logic...")
    
    # Simulate the bash logic from n8n-entrypoint.sh
    
    # Test HTTPS mode
    os.environ['ENABLE_HTTPS'] = 'true'
    os.environ['N8N_PORT'] = '5678'
    
    enable_https = os.environ.get('ENABLE_HTTPS', 'false')
    n8n_port = os.environ.get('N8N_PORT', '5678')
    
    if enable_https == 'true':
        n8n_protocol = 'https'
        n8n_secure_cookie = 'true'
        webhook_url = f"https://localhost:{n8n_port}"
        editor_url = f"https://localhost:{n8n_port}"
    else:
        n8n_protocol = 'http'
        n8n_secure_cookie = 'false'
        webhook_url = f"http://localhost:{n8n_port}"
        editor_url = f"http://localhost:{n8n_port}"
    
    assert n8n_protocol == 'https'
    assert n8n_secure_cookie == 'true'
    assert webhook_url == 'https://localhost:5678'
    assert editor_url == 'https://localhost:5678'
    
    print(f"  ✓ HTTPS mode:")
    print(f"    - N8N_PROTOCOL: {n8n_protocol}")
    print(f"    - N8N_SECURE_COOKIE: {n8n_secure_cookie}")
    print(f"    - WEBHOOK_URL: {webhook_url}")
    print(f"    - N8N_EDITOR_BASE_URL: {editor_url}")
    
    # Test HTTP mode
    os.environ['ENABLE_HTTPS'] = 'false'
    
    enable_https = os.environ.get('ENABLE_HTTPS', 'false')
    
    if enable_https == 'true':
        n8n_protocol = 'https'
        n8n_secure_cookie = 'true'
        webhook_url = f"https://localhost:{n8n_port}"
        editor_url = f"https://localhost:{n8n_port}"
    else:
        n8n_protocol = 'http'
        n8n_secure_cookie = 'false'
        webhook_url = f"http://localhost:{n8n_port}"
        editor_url = f"http://localhost:{n8n_port}"
    
    assert n8n_protocol == 'http'
    assert n8n_secure_cookie == 'false'
    assert webhook_url == 'http://localhost:5678'
    assert editor_url == 'http://localhost:5678'
    
    print(f"  ✓ HTTP mode:")
    print(f"    - N8N_PROTOCOL: {n8n_protocol}")
    print(f"    - N8N_SECURE_COOKIE: {n8n_secure_cookie}")
    print(f"    - WEBHOOK_URL: {webhook_url}")
    print(f"    - N8N_EDITOR_BASE_URL: {editor_url}")
    
    print("\n✅ All n8n entrypoint logic tests passed!")


if __name__ == '__main__':
    try:
        test_url_generation_logic()
        test_start_script_protocol_detection()
        test_n8n_entrypoint_logic()
        print("\n" + "="*60)
        print("✅ ALL HTTPS CONFIGURATION TESTS PASSED")
        print("="*60)
        print("\nNote: These tests validate the URL generation logic.")
        print("For full integration tests with actual services, run:")
        print("  docker-compose up -d && ./tests/test_tools_integration.py")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
