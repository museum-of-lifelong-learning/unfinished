"""
Stacking analysis module.
Determines vertical ordering and relationships between detected shapes.
"""
import numpy as np
from config import config


class StackAnalyzer:
    """Analyzes stacking order and relationships of detected shapes"""
    
    def __init__(self):
        """Initialize stack analyzer"""
        self.stick_reference = None
    
    def set_stick_reference(self, stick_bbox):
        """
        Set the stick position as reference for vertical alignment
        
        Args:
            stick_bbox: (x, y, w, h) bounding box of the detected stick
        """
        self.stick_reference = stick_bbox
    
    def order_by_vertical_position(self, classified_shapes):
        """
        Order shapes from bottom to top based on Y-coordinate
        
        Args:
            classified_shapes: List of classification results from classifier
            
        Returns:
            list: Shapes ordered from bottom (index 0) to top
        """
        # Sort by Y-coordinate (higher Y = lower on screen = bottom of stack)
        sorted_shapes = sorted(
            classified_shapes,
            key=lambda s: s['center'][1],
            reverse=True  # Bottom to top
        )
        
        # Limit to maximum allowed shapes
        return sorted_shapes[:config.MAX_SHAPES]
    
    def calculate_spacing(self, ordered_shapes):
        """
        Calculate spacing between consecutive shapes
        
        Args:
            ordered_shapes: List of shapes ordered bottom to top
            
        Returns:
            list: Spacing values (in pixels) between each pair
        """
        if len(ordered_shapes) < 2:
            return []
        
        spacings = []
        for i in range(len(ordered_shapes) - 1):
            y1 = ordered_shapes[i]['center'][1]
            y2 = ordered_shapes[i + 1]['center'][1]
            spacing = abs(y1 - y2)
            spacings.append(spacing)
        
        return spacings
    
    def verify_alignment(self, ordered_shapes, tolerance=50):
        """
        Verify that shapes are vertically aligned (on the stick)
        
        Args:
            ordered_shapes: List of shapes ordered bottom to top
            tolerance: Maximum horizontal deviation allowed (pixels)
            
        Returns:
            dict: Alignment verification results
        """
        if len(ordered_shapes) < 2:
            return {'aligned': True, 'deviations': []}
        
        # Calculate average X position
        x_positions = [s['center'][0] for s in ordered_shapes]
        mean_x = np.mean(x_positions)
        
        # Calculate deviations
        deviations = [abs(x - mean_x) for x in x_positions]
        max_deviation = max(deviations)
        
        aligned = max_deviation <= tolerance
        
        return {
            'aligned': aligned,
            'mean_x': mean_x,
            'max_deviation': max_deviation,
            'deviations': deviations
        }
    
    def build_stack_description(self, ordered_shapes):
        """
        Build a human-readable description of the stack
        
        Args:
            ordered_shapes: List of shapes ordered bottom to top
            
        Returns:
            dict: Complete stack description
        """
        stack = {
            'count': len(ordered_shapes),
            'shapes': [],
            'spacings': self.calculate_spacing(ordered_shapes),
            'alignment': self.verify_alignment(ordered_shapes)
        }
        
        for i, shape in enumerate(ordered_shapes):
            stack['shapes'].append({
                'position': i + 1,  # 1-indexed for human readability
                'label': shape['label'],
                'confidence': shape['confidence'],
                'center': shape['center'],
                'bbox': shape['bbox']
            })
        
        return stack
    
    def format_stack_string(self, stack_description):
        """
        Format stack as a simple string for logging/display
        
        Args:
            stack_description: Output from build_stack_description()
            
        Returns:
            str: Formatted string like "Bottom→Top: cube, sphere, cylinder"
        """
        if stack_description['count'] == 0:
            return "No shapes detected"
        
        labels = [s['label'] for s in stack_description['shapes']]
        return f"Bottom→Top: {', '.join(labels)}"


def test_stack_analyzer():
    """Test function for stack analyzer"""
    print("Testing StackAnalyzer...")
    
    # Mock data
    mock_shapes = [
        {'label': 'cube', 'confidence': 0.9, 'center': (100, 300), 'bbox': (80, 280, 40, 40)},
        {'label': 'sphere', 'confidence': 0.85, 'center': (105, 200), 'bbox': (85, 180, 40, 40)},
        {'label': 'cylinder', 'confidence': 0.92, 'center': (98, 100), 'bbox': (78, 80, 40, 40)},
    ]
    
    analyzer = StackAnalyzer()
    ordered = analyzer.order_by_vertical_position(mock_shapes)
    stack = analyzer.build_stack_description(ordered)
    
    print(f"✓ Stack count: {stack['count']}")
    print(f"✓ Stack order: {analyzer.format_stack_string(stack)}")
    print(f"✓ Alignment: {stack['alignment']['aligned']}")


if __name__ == "__main__":
    test_stack_analyzer()
