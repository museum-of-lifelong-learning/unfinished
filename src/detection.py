"""
Shape detection module using OpenCV.
Identifies regions of interest (ROIs) containing potential shapes.
"""
import cv2
import numpy as np
from config import config


class ShapeDetector:
    """Detects shapes in preprocessed frames using contour analysis"""
    
    def __init__(self):
        """Initialize shape detector"""
        pass
    
    def detect_stick(self, frame):
        """
        Detect the vertical stick in the frame using color segmentation
        
        Args:
            frame: BGR image frame
            
        Returns:
            tuple: (x, y, w, h) bounding box of the stick, or None if not found
        """
        # Convert to HSV for color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create mask for stick color
        lower = np.array(config.STICK_COLOR_LOWER)
        upper = np.array(config.STICK_COLOR_UPPER)
        mask = cv2.inRange(hsv, lower, upper)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Find the largest vertical contour (likely the stick)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Verify it's reasonably vertical (height > width)
        if h > w * 2:
            return (x, y, w, h)
        
        return None
    
    def find_shape_contours(self, processed_frames):
        """
        Find contours that likely represent shapes
        
        Args:
            processed_frames: Dictionary from capture.preprocess_frame()
            
        Returns:
            list: List of contours representing potential shapes
        """
        edges = processed_frames['edges']
        
        # Find all contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area
        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area >= config.MIN_CONTOUR_AREA:
                valid_contours.append(contour)
        
        return valid_contours
    
    def extract_rois(self, frame, contours, max_shapes=None):
        """
        Extract regions of interest (ROIs) from detected contours
        
        Args:
            frame: Original frame
            contours: List of contours
            max_shapes: Maximum number of shapes to extract
            
        Returns:
            list: List of dictionaries with 'roi', 'bbox', 'center' for each shape
        """
        if max_shapes is None:
            max_shapes = config.MAX_SHAPES
        
        # Sort contours by area (largest first)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:max_shapes]
        
        rois = []
        for contour in contours:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Extract ROI
            roi = frame[y:y+h, x:x+w]
            
            # Calculate center
            M = cv2.moments(contour)
            if M['m00'] != 0:
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
            else:
                cx, cy = x + w // 2, y + h // 2
            
            rois.append({
                'roi': roi,
                'bbox': (x, y, w, h),
                'center': (cx, cy),
                'contour': contour
            })
        
        # Sort by vertical position (top to bottom)
        rois.sort(key=lambda r: r['center'][1])
        
        return rois
    
    def analyze_shape_geometry(self, contour):
        """
        Analyze geometric properties of a contour
        
        Args:
            contour: OpenCV contour
            
        Returns:
            dict: Geometric features (circularity, aspect_ratio, corners, etc.)
        """
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        # Circularity (1.0 = perfect circle)
        circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
        
        # Bounding box aspect ratio
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h if h > 0 else 0
        
        # Approximate polygon to count corners
        epsilon = 0.04 * perimeter
        approx = cv2.approxPolyDP(contour, epsilon, True)
        corners = len(approx)
        
        return {
            'area': area,
            'perimeter': perimeter,
            'circularity': circularity,
            'aspect_ratio': aspect_ratio,
            'corners': corners
        }


if __name__ == "__main__":
    print("ShapeDetector module loaded")
    print("Use from main.py to run full detection pipeline")
