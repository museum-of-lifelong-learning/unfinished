"""
Raspberry Pi 5 configuration.
Optimized for performance and resource efficiency.
"""
from .base_config import BaseConfig


class PiConfig(BaseConfig):
    """Raspberry Pi 5 deployment configuration"""
    
    # Keep debug off for production
    DEBUG = False
    
    # Lower resolution for better performance
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 15  # Lower FPS to reduce CPU load
    
    # Minimal UI for headless operation
    SHOW_DEBUG_WINDOW = False
    SHOW_FPS = False
    LOG_LEVEL = "INFO"
    
    # Optimize for Pi's CPU
    INFERENCE_THREADS = 2
    FRAME_SKIP = 2  # Process every other frame to reduce load
    
    # Stricter thresholds to reduce false positives
    CONFIDENCE_THRESHOLD = 0.7
    MIN_CONTOUR_AREA = 600
    
    # Smaller blur kernel for faster processing
    GAUSSIAN_BLUR_KERNEL = (3, 3)
