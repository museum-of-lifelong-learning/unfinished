"""
Webcam capture and frame preprocessing module.
Handles video input and prepares frames for shape detection.
"""
import cv2
import numpy as np
from config import config


class CameraCapture:
    """Handles webcam capture and frame preprocessing"""
    
    def __init__(self):
        """Initialize camera capture"""
        self.cap = None
        self.background_subtractor = None
        
        if config.BACKGROUND_SUBTRACTION:
            self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=500, varThreshold=16, detectShadows=True
            )
    
    def start(self):
        """Start the camera capture"""
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera at index {config.CAMERA_INDEX}")
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
        
        # Fixed camera settings for consistency
        # Disable auto-exposure
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # 0.25 = manual mode, 0.75 = auto
        
        # Set manual exposure (range: 0-255, adjust based on lighting)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -6)  # Negative values = shorter exposure
        
        # Disable auto white balance
        self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)
        
        # Set white balance temperature (range varies by camera, typically 2800-6500K)
        self.cap.set(cv2.CAP_PROP_WB_TEMPERATURE, 4600)
        
        # Set gain/ISO (lower = less noise, needs more light)
        self.cap.set(cv2.CAP_PROP_GAIN, 50)  # Range: 0-255
        
        # Disable autofocus if available
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        
        # Set focus manually if needed (range varies by camera)
        # self.cap.set(cv2.CAP_PROP_FOCUS, 50)
        
        print(f"Camera started: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.CAMERA_FPS}fps")
        print(f"Manual settings: Exposure={self.cap.get(cv2.CAP_PROP_EXPOSURE)}, "
              f"Gain={self.cap.get(cv2.CAP_PROP_GAIN)}, "
              f"WB={self.cap.get(cv2.CAP_PROP_WB_TEMPERATURE)}")
    
    def read_frame(self):
        """
        Read a frame from the camera
        
        Returns:
            tuple: (success, frame) where success is bool and frame is numpy array
        """
        if self.cap is None:
            raise RuntimeError("Camera not started. Call start() first.")
        
        return self.cap.read()
    
    def preprocess_frame(self, frame):
        """
        Preprocess frame for shape detection
        
        Args:
            frame: Input frame from camera
            
        Returns:
            dict: Dictionary containing processed frames:
                - 'original': Original frame
                - 'blurred': Gaussian blurred frame
                - 'gray': Grayscale frame
                - 'edges': Canny edge detection
                - 'fg_mask': Foreground mask (if background subtraction enabled)
        """
        processed = {'original': frame}
        
        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(frame, config.GAUSSIAN_BLUR_KERNEL, 0)
        processed['blurred'] = blurred
        
        # Convert to grayscale
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        processed['gray'] = gray
        
        # Edge detection
        edges = cv2.Canny(gray, config.CANNY_THRESHOLD1, config.CANNY_THRESHOLD2)
        processed['edges'] = edges
        
        # Background subtraction (if enabled)
        if self.background_subtractor is not None:
            fg_mask = self.background_subtractor.apply(frame)
            processed['fg_mask'] = fg_mask
        
        return processed
    
    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            print("Camera released")


def test_camera():
    """Test function to verify camera setup"""
    print("Testing camera capture...")
    
    camera = CameraCapture()
    camera.start()
    
    try:
        success, frame = camera.read_frame()
        if success:
            print(f"✓ Successfully captured frame: {frame.shape}")
            
            # Test preprocessing
            processed = camera.preprocess_frame(frame)
            print(f"✓ Preprocessing successful, generated {len(processed)} outputs")
        else:
            print("✗ Failed to capture frame")
    
    finally:
        camera.release()


if __name__ == "__main__":
    test_camera()
