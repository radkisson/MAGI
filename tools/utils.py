"""
Shared utility functions for RIN tools
"""

import os


def get_service_url(service_name: str, default_port: int, check_env_var: str = None) -> str:
    """
    Get service URL, auto-detecting HTTP or HTTPS based on configuration.
    
    Args:
        service_name: The Docker service name (e.g., 'qdrant', 'searxng')
        default_port: The default port for the service
        check_env_var: Optional environment variable to check first for explicit URL override
        
    Returns:
        Full URL with protocol, host, and port (e.g., 'http://qdrant:6333')
    """
    # Check for explicit URL override first
    if check_env_var:
        env_url = os.getenv(check_env_var)
        if env_url:
            return env_url
    
    # Auto-detect protocol based on ENABLE_HTTPS
    enable_https = os.getenv("ENABLE_HTTPS", "false").lower() == "true"
    protocol = "https" if enable_https else "http"
    
    return f"{protocol}://{service_name}:{default_port}"
