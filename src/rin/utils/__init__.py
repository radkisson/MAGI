"""Utility functions for RIN"""

import logging
from typing import Dict, Any


def setup_logging(level: str = "INFO") -> None:
    """
    Setup logging configuration for RIN
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    import yaml
    import json
    from pathlib import Path
    
    path = Path(config_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    if path.suffix == '.yaml' or path.suffix == '.yml':
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    elif path.suffix == '.json':
        with open(path, 'r') as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported config format: {path.suffix}")


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to file
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration
    """
    import yaml
    import json
    from pathlib import Path
    
    path = Path(config_path)
    
    if path.suffix == '.yaml' or path.suffix == '.yml':
        with open(path, 'w') as f:
            yaml.safe_dump(config, f, default_flow_style=False)
    elif path.suffix == '.json':
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)
    else:
        raise ValueError(f"Unsupported config format: {path.suffix}")
