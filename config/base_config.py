"""
Base configuration settings shared across all environments.
"""
import os


class BaseConfig:
    """Base configuration with sensible defaults"""
    
    # Application
    APP_NAME = "Figurine Shape Recognition"
    VERSION = "0.1.0"
    DEBUG = False
    
    # Camera settings
    CAMERA_INDEX = 0  # Default USB webcam
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Detection settings
    MIN_CONTOUR_AREA = 500  # Minimum area to consider a shape
    MAX_SHAPES = 6  # Maximum shapes in a stack
    
    # Classification settings
    MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'shape_classifier.tflite')
    LABELS_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'labels.txt')
    CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence for classification
    
    # Preprocessing
    BACKGROUND_SUBTRACTION = True
    GAUSSIAN_BLUR_KERNEL = (5, 5)
    CANNY_THRESHOLD1 = 50
    CANNY_THRESHOLD2 = 150
    
    # Stick detection (color range in HSV)
    STICK_COLOR_LOWER = (0, 100, 100)  # Example: red lower bound
    STICK_COLOR_UPPER = (10, 255, 255)  # Example: red upper bound
    
    # Performance
    INFERENCE_THREADS = 2
    FRAME_SKIP = 1  # Process every Nth frame
    
    # Display
    SHOW_DEBUG_WINDOW = False
    SHOW_FPS = True
    WINDOW_NAME = "Figurine Recognition"
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "figurine.log"
    
    @classmethod
    def get_absolute_path(cls, relative_path):
        """Convert relative path to absolute path from project root"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, relative_path)
