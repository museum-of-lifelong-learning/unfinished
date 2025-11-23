"""
Development configuration for Linux notebook.
Optimized for testing and debugging.
"""
from .base_config import BaseConfig


class DevConfig(BaseConfig):
    """Development environment configuration"""
    
    # Override for development
    DEBUG = True
    
    # Higher resolution for development
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    CAMERA_FPS = 30
    
    # More verbose debugging
    SHOW_DEBUG_WINDOW = True
    SHOW_FPS = True
    LOG_LEVEL = "DEBUG"
    
    # Development can handle more threads
    INFERENCE_THREADS = 4
    FRAME_SKIP = 1  # Process every frame
    
    # Relaxed thresholds for testing
    CONFIDENCE_THRESHOLD = 0.5
    MIN_CONTOUR_AREA = 300
