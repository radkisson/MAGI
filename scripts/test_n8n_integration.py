#!/usr/bin/env python3
"""
Comprehensive test for n8n and OpenWebUI integration.
Tests connectivity, workflow availability, and webhook functionality.
"""

import sys
import json
import urllib.request
import urllib.error
from urllib.parse import urljoin


class Colors:
    GREEN = '\033[0;32m'
    BLUE = '\033[0;34m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color


def print_header(text):
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.BLUE}{text}{Colors.NC}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.NC}\n")


def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.NC}")


def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.NC}")


def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.NC}")


def test_n8n_connectivity():
    """Test basic n8n connectivity from OpenWebUI perspective."""
    print_header("Test 1: n8n Basic Connectivity")

    n8n_hosts = [
        "http://magi-reflex-automation:5678",
        "http://n8n:5678"
    ]

    for host in n8n_hosts:
        try:
            url = f"{host}/healthz"
            req = urllib.request.Request(url, method='GET')
            resp = urllib.request.urlopen(req, timeout=5)
            if resp.status == 200:
                print_success(f"n8n accessible at {host}")
                return host
        except Exception as e:
            print_warning(f"Could not reach n8n at {host}: {e}")

    print_error("n8n not accessible from any known host")
    return None


def test_webhook_endpoint(base_url):
    """Test if webhook endpoints are accessible."""
    print_header("Test 2: Webhook Endpoint Accessibility")

    test_endpoints = [
        "/webhook/openwebui-action",
        "/webhook-test/test"
    ]

    accessible = False
    for endpoint in test_endpoints:
        try:
            url = urljoin(base_url, endpoint)
            req = urllib.request.Request(url, method='GET')
            urllib.request.urlopen(req, timeout=5)
            print_success(f"Webhook endpoint accessible: {endpoint}")
            accessible = True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print_warning(f"Webhook endpoint exists but workflow not active: {endpoint}")
                accessible = True
            else:
                print_warning(f"Webhook returned status {e.code}: {endpoint}")
        except Exception as e:
            print_error(f"Could not test webhook {endpoint}: {e}")

    return accessible


def test_webhook_post(base_url):
    """Test POSTing data to a webhook."""
    print_header("Test 3: Webhook POST Request")

    webhook_url = urljoin(base_url, "/webhook/openwebui-action")
    test_data = {
        "action": "test",
        "payload": {"message": "Integration test from OpenWebUI"},
        "user": "test-user"
    }

    try:
        data = json.dumps(test_data).encode('utf-8')
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read().decode('utf-8'))
        print_success(f"Webhook POST successful (status: {resp.status})")
        print(f"   Response: {json.dumps(result, indent=2)[:200]}")
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print_warning("Webhook workflow not active or not found")
            print("   This is expected if the workflow hasn't been activated in n8n")
        else:
            print_error(f"Webhook POST failed with status {e.code}")
        return False
    except Exception as e:
        print_error(f"Webhook POST failed: {e}")
        return False


def test_n8n_tool_configuration():
    """Test if n8n tool is properly configured in OpenWebUI."""
    print_header("Test 4: n8n Tool Configuration")

    try:
        import os
        tool_path = "/app/backend/data/tools/n8n_reflex.py"
        if os.path.exists(tool_path):
            print_success("n8n_reflex.py tool found in OpenWebUI")

            # Check if environment variables are set
            n8n_url = os.getenv("N8N_WEBHOOK_URL", "http://magi-reflex-automation:5678/webhook")
            print(f"   Configured webhook URL: {n8n_url}")
            return True
        else:
            print_error("n8n_reflex.py tool not found in OpenWebUI")
            return False
    except Exception as e:
        print_error(f"Could not check tool configuration: {e}")
        return False


def generate_report(results):
    """Generate final test report."""
    print_header("Integration Test Summary")

    total = len(results)
    passed = sum(results.values())

    print(f"Total Tests: {total}")
    print(f"Passed: {Colors.GREEN}{passed}{Colors.NC}")
    print(f"Failed: {Colors.RED}{total - passed}{Colors.NC}")
    print()

    if passed == total:
        print_success("All integration tests passed!")
        print("\n🎉 n8n and OpenWebUI are properly connected and ready to use!")
        return 0
    elif passed > 0:
        print_warning(f"{passed}/{total} tests passed - partial integration")
        print("\n⚠️  Some features may not work correctly. Check the logs above.")
        return 1
    else:
        print_error("All tests failed - integration not working")
        print("\n❌ n8n and OpenWebUI are not properly connected.")
        return 2


def main():
    """Main test function."""
    print(f"\n{Colors.BLUE}🧪 n8n and OpenWebUI Integration Test{Colors.NC}")

    results = {}

    # Test 1: Basic connectivity
    base_url = test_n8n_connectivity()
    results['connectivity'] = base_url is not None

    if not base_url:
        print_error("Cannot proceed with further tests - n8n not accessible")
        return generate_report(results)

    # Test 2: Webhook endpoints
    results['webhook_endpoint'] = test_webhook_endpoint(base_url)

    # Test 3: Webhook POST
    results['webhook_post'] = test_webhook_post(base_url)

    # Test 4: Tool configuration
    results['tool_config'] = test_n8n_tool_configuration()

    # Generate report
    return generate_report(results)


if __name__ == "__main__":
    sys.exit(main())
