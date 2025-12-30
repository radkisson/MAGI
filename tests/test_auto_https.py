#!/usr/bin/env python3
"""
Test automatic HTTPS configuration with Let's Encrypt and Caddy
Tests the configuration generation and environment setup
"""

import sys
import os
import tempfile
import shutil


def test_caddyfile_template_exists():
    """Test that Caddyfile template exists"""
    print("Testing Caddyfile template existence...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(base_dir, "config", "caddy", "Caddyfile.template")
    
    assert os.path.exists(template_path), f"Caddyfile template not found at {template_path}"
    
    # Read template and verify structure
    with open(template_path, 'r') as f:
        content = f.read()
    
    # Check for required placeholders
    assert "{DOMAIN}" in content, "Template missing {DOMAIN} placeholder"
    assert "{ADMIN_EMAIL}" in content, "Template missing {ADMIN_EMAIL} placeholder"
    
    # Check for Let's Encrypt configuration
    assert "acme_ca" in content, "Template missing ACME CA configuration"
    assert "letsencrypt.org" in content, "Template missing Let's Encrypt URL"
    
    # Check for service reverse proxy configurations
    assert "reverse_proxy open-webui:8080" in content, "Missing Open WebUI proxy"
    assert "reverse_proxy n8n:5678" in content, "Missing n8n proxy"
    assert "reverse_proxy searxng:8080" in content, "Missing SearXNG proxy"
    assert "reverse_proxy litellm:4000" in content, "Missing LiteLLM proxy"
    
    print("  ✓ Caddyfile template structure is valid")


def test_setup_script_exists():
    """Test that auto-HTTPS setup script exists and is executable"""
    print("\nTesting setup script...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(base_dir, "scripts", "setup-auto-https.sh")
    
    assert os.path.exists(script_path), f"Setup script not found at {script_path}"
    assert os.access(script_path, os.X_OK), "Setup script is not executable"
    
    # Read script and verify structure
    with open(script_path, 'r') as f:
        content = f.read()
    
    # Check for validation functions
    assert "validate_domain" in content, "Script missing domain validation"
    assert "validate_email" in content, "Script missing email validation"
    
    # Check for Let's Encrypt staging option
    assert "staging" in content.lower(), "Script missing staging environment option"
    
    print("  ✓ Setup script exists and has proper structure")


def test_docker_compose_caddy_service():
    """Test that docker-compose.yml includes Caddy service"""
    print("\nTesting docker-compose.yml Caddy configuration...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    compose_path = os.path.join(base_dir, "docker-compose.yml")
    
    assert os.path.exists(compose_path), f"docker-compose.yml not found at {compose_path}"
    
    with open(compose_path, 'r') as f:
        content = f.read()
    
    # Check for Caddy service
    assert "caddy:" in content, "docker-compose.yml missing Caddy service"
    assert "magi-caddy" in content, "Caddy container not named correctly"
    assert "caddy:2-alpine" in content or "caddy:" in content, "Missing Caddy image"
    
    # Check for auto-https profile
    assert "auto-https" in content, "Missing auto-https profile"
    
    # Check for port mappings
    assert '"80:80"' in content or "'80:80'" in content, "Missing port 80 mapping"
    assert '"443:443"' in content or "'443:443'" in content, "Missing port 443 mapping"
    
    # Check for volume mounts
    assert "config/caddy/Caddyfile" in content, "Missing Caddyfile mount"
    assert "data/caddy" in content, "Missing Caddy data volume"
    
    # Check for environment variables
    assert "MAGI_DOMAIN" in content or "DOMAIN" in content, "Missing domain environment variable"
    
    print("  ✓ docker-compose.yml has valid Caddy configuration")


def test_env_example_updated():
    """Test that .env.example includes automatic HTTPS variables"""
    print("\nTesting .env.example for automatic HTTPS variables...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_example_path = os.path.join(base_dir, ".env.example")
    
    assert os.path.exists(env_example_path), f".env.example not found at {env_example_path}"
    
    with open(env_example_path, 'r') as f:
        content = f.read()
    
    # Check for automatic HTTPS variables
    assert "ENABLE_AUTO_HTTPS" in content, "Missing ENABLE_AUTO_HTTPS variable"
    assert "MAGI_DOMAIN" in content, "Missing MAGI_DOMAIN variable"
    assert "MAGI_ADMIN_EMAIL" in content, "Missing MAGI_ADMIN_EMAIL variable"
    
    # Check for documentation
    assert "Let's Encrypt" in content or "automatic" in content.lower(), "Missing Let's Encrypt documentation"
    
    print("  ✓ .env.example includes automatic HTTPS configuration")


def test_start_script_integration():
    """Test that start.sh integrates automatic HTTPS option"""
    print("\nTesting start.sh integration...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    start_script_path = os.path.join(base_dir, "start.sh")
    
    assert os.path.exists(start_script_path), f"start.sh not found at {start_script_path}"
    
    with open(start_script_path, 'r') as f:
        content = f.read()
    
    # Check for automatic HTTPS option in menu
    assert "Automatic HTTPS" in content or "automatic" in content.lower(), "Missing automatic HTTPS option"
    assert "Let's Encrypt" in content, "Missing Let's Encrypt mention"
    
    # Check for setup script invocation
    assert "setup-auto-https.sh" in content, "Missing setup script invocation"
    
    # Check for auto-https profile usage
    assert "auto-https" in content, "Missing auto-https profile handling"
    assert "ENABLE_AUTO_HTTPS" in content, "Missing ENABLE_AUTO_HTTPS variable"
    
    print("  ✓ start.sh properly integrates automatic HTTPS")


def test_rin_cli_command():
    """Test that rin CLI includes setup-https command"""
    print("\nTesting rin CLI integration...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rin_path = os.path.join(base_dir, "rin")
    
    assert os.path.exists(rin_path), f"rin CLI not found at {rin_path}"
    
    with open(rin_path, 'r') as f:
        content = f.read()
    
    # Check for setup-https command
    assert "setup-https" in content, "Missing setup-https command"
    assert "cmd_setup_https" in content, "Missing setup-https function"
    
    # Check for help text
    assert "Automatic HTTPS" in content or "Let's Encrypt" in content, "Missing HTTPS documentation in help"
    
    print("  ✓ rin CLI includes setup-https command")


def test_caddyfile_generation():
    """Test Caddyfile generation from template"""
    print("\nTesting Caddyfile generation logic...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(base_dir, "config", "caddy", "Caddyfile.template")
    
    # Read template
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Simulate generation
    test_domain = "magi.example.com"
    test_email = "admin@example.com"
    
    generated = template.replace("{DOMAIN}", test_domain)
    generated = generated.replace("{ADMIN_EMAIL}", test_email)
    
    # Verify generated content
    assert test_domain in generated, "Domain not properly substituted"
    assert test_email in generated, "Email not properly substituted"
    assert "{DOMAIN}" not in generated, "Template placeholders not replaced"
    assert "{ADMIN_EMAIL}" not in generated, "Template placeholders not replaced"
    
    # Check subdomain generation
    assert f"n8n.{test_domain}" in generated, "n8n subdomain not generated"
    assert f"search.{test_domain}" in generated, "search subdomain not generated"
    assert f"api.{test_domain}" in generated, "api subdomain not generated"
    
    print("  ✓ Caddyfile generation works correctly")


def test_documentation_updated():
    """Test that HTTPS documentation includes automatic setup"""
    print("\nTesting HTTPS documentation...")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_path = os.path.join(base_dir, "docs", "HTTPS_CONFIGURATION.md")
    
    assert os.path.exists(docs_path), f"HTTPS docs not found at {docs_path}"
    
    with open(docs_path, 'r') as f:
        content = f.read()
    
    # Check for automatic HTTPS section
    assert "Automatic HTTPS" in content, "Missing automatic HTTPS section"
    assert "Let's Encrypt" in content, "Missing Let's Encrypt mention"
    assert "Caddy" in content, "Missing Caddy mention"
    
    # Check for setup instructions
    assert "./magi setup-https" in content or "setup-https" in content, "Missing setup command"
    assert "Zero Configuration" in content or "automatic" in content.lower(), "Missing automation benefits"
    
    # Check for DNS requirements
    assert "DNS" in content, "Missing DNS configuration instructions"
    
    print("  ✓ HTTPS documentation includes automatic setup")


if __name__ == '__main__':
    try:
        test_caddyfile_template_exists()
        test_setup_script_exists()
        test_docker_compose_caddy_service()
        test_env_example_updated()
        test_start_script_integration()
        test_rin_cli_command()
        test_caddyfile_generation()
        test_documentation_updated()
        
        print("\n" + "="*60)
        print("✅ ALL AUTOMATIC HTTPS TESTS PASSED")
        print("="*60)
        print("\nAutomatic HTTPS with Let's Encrypt is properly configured!")
        print("\nTo use automatic HTTPS:")
        print("  1. Ensure your domain points to this server")
        print("  2. Run: ./magi setup-https")
        print("  3. Follow the prompts to configure your domain")
        print("  4. Start MAGI: ./magi start")
        print("\nCaddy will automatically obtain SSL certificates from Let's Encrypt!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
