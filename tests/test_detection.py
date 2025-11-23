"""
Tests for shape detection module
"""
import pytest
import numpy as np
import cv2
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from detection import ShapeDetector


class TestShapeDetector:
    """Test cases for ShapeDetector class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.detector = ShapeDetector()
    
    def test_detector_initialization(self):
        """Test that detector initializes correctly"""
        assert self.detector is not None
    
    def test_analyze_shape_geometry_circle(self):
        """Test geometric analysis of a circular contour"""
        # Create a circular contour
        radius = 50
        center = (100, 100)
        contour = np.array([
            [center[0] + int(radius * np.cos(theta)), 
             center[1] + int(radius * np.sin(theta))]
            for theta in np.linspace(0, 2 * np.pi, 100)
        ]).reshape(-1, 1, 2).astype(np.int32)
        
        features = self.detector.analyze_shape_geometry(contour)
        
        # Circle should have high circularity (close to 1.0)
        assert features['circularity'] > 0.8
        assert features['area'] > 0
        assert features['perimeter'] > 0
    
    def test_analyze_shape_geometry_square(self):
        """Test geometric analysis of a square contour"""
        # Create a square contour
        size = 50
        contour = np.array([
            [0, 0], [size, 0], [size, size], [0, size]
        ]).reshape(-1, 1, 2).astype(np.int32)
        
        features = self.detector.analyze_shape_geometry(contour)
        
        # Square should have 4 corners
        assert features['corners'] == 4
        # Aspect ratio should be close to 1.0
        assert 0.9 < features['aspect_ratio'] < 1.1
    
    def test_extract_rois_sorting(self):
        """Test that ROIs are sorted by vertical position"""
        # Create dummy frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create contours at different Y positions
        contour1 = np.array([[100, 100], [150, 100], [150, 150], [100, 150]]).reshape(-1, 1, 2)
        contour2 = np.array([[100, 200], [150, 200], [150, 250], [100, 250]]).reshape(-1, 1, 2)
        contour3 = np.array([[100, 300], [150, 300], [150, 350], [100, 350]]).reshape(-1, 1, 2)
        
        contours = [contour1, contour2, contour3]
        
        rois = self.detector.extract_rois(frame, contours)
        
        # Should be sorted by Y position (top to bottom)
        assert len(rois) == 3
        assert rois[0]['center'][1] < rois[1]['center'][1] < rois[2]['center'][1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
