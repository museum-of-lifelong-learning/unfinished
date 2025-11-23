"""
Configuration loader that automatically selects the appropriate config
based on the FIGURINE_ENV environment variable.

Usage:
    from config import config
    
    # Access configuration
    print(config.CAMERA_WIDTH)
    print(config.DEBUG)
"""
import os
import sys

from .base_config import BaseConfig
from .dev_config import DevConfig
from .pi_config import PiConfig


def get_config():
    """
    Load configuration based on FIGURINE_ENV environment variable.
    
    Returns:
        Configuration class instance (DevConfig or PiConfig)
    
    Raises:
        ValueError: If FIGURINE_ENV is set to an invalid value
    """
    env = os.getenv('FIGURINE_ENV', 'dev').lower()
    
    config_map = {
        'dev': DevConfig,
        'development': DevConfig,
        'pi': PiConfig,
        'raspberry': PiConfig,
        'production': PiConfig,
    }
    
    config_class = config_map.get(env)
    
    if config_class is None:
        print(f"Warning: Invalid FIGURINE_ENV '{env}'. Valid options: {', '.join(config_map.keys())}")
        print("Defaulting to DevConfig")
        config_class = DevConfig
    
    return config_class()


# Global configuration instance
config = get_config()

# Print loaded configuration on import (helpful for debugging)
if __name__ != "__main__":
    env_name = os.getenv('FIGURINE_ENV', 'dev')
    print(f"Loaded configuration: {config.__class__.__name__} (FIGURINE_ENV={env_name})")
