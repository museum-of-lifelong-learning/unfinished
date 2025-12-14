#!/usr/bin/env python3
"""
Figurine Shape Recognition - Main Application
Integrates camera capture, detection, classification, and stacking analysis.
"""
import sys
import time
import cv2
from config import config

# Import our modules
from capture import CameraCapture
from detection import ShapeDetector
from classification import ShapeClassifier
from stacking import StackAnalyzer


class FigurineRecognition:
    """Main application class"""
    
    def __init__(self):
        """Initialize all components"""
        print(f"Initializing {config.APP_NAME} v{config.VERSION}")
        print(f"Configuration: {config.__class__.__name__}")
        print("-" * 50)
        
        self.camera = CameraCapture()
        self.detector = ShapeDetector()
        self.classifier = ShapeClassifier()
        self.analyzer = StackAnalyzer()
        
        self.running = False
        self.frame_count = 0
        self.fps = 0
        self.last_time = time.time()
    
    def start(self):
        """Start the application"""
        print("Starting application...")
        self.camera.start()
        self.running = True
        print("✓ Ready")
        print("\nPress 'q' to quit, 's' to save frame, 'd' to toggle debug\n")
    
    def process_frame(self, frame):
        """
        Process a single frame through the full pipeline
        
        Args:
            frame: Input frame from camera
            
        Returns:
            tuple: (annotated_frame, stack_description)
        """
        # Preprocessing
        processed = self.camera.preprocess_frame(frame)
        
        # Shape detection
        contours = self.detector.find_shape_contours(processed)
        rois = self.detector.extract_rois(frame, contours)
        
        # Classification
        classified = self.classifier.classify_batch(rois)
        
        # Stack analysis
        ordered = self.analyzer.order_by_vertical_position(classified)
        stack = self.analyzer.build_stack_description(ordered)
        
        # Annotate frame
        annotated = self.annotate_frame(frame, stack)
        
        return annotated, stack
    
    def annotate_frame(self, frame, stack):
        """
        Draw bounding boxes and labels on frame
        
        Args:
            frame: Original frame
            stack: Stack description from analyzer
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        # Draw each shape
        for shape in stack['shapes']:
            x, y, w, h = shape['bbox']
            label = shape['label']
            confidence = shape['confidence']
            
            # Choose color based on confidence
            if confidence > 0.8:
                color = (0, 255, 0)  # Green
            elif confidence > 0.6:
                color = (0, 255, 255)  # Yellow
            else:
                color = (0, 0, 255)  # Red
            
            # Draw bounding box
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            text = f"{label} ({confidence:.2f})"
            cv2.putText(
                annotated, text, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
            )
            
            # Draw position number
            pos_text = f"#{shape['position']}"
            cv2.putText(
                annotated, pos_text, (x + w - 30, y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
        
        # Draw stack info
        stack_text = self.analyzer.format_stack_string(stack)
        cv2.putText(
            annotated, stack_text, (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
        )
        
        # Draw FPS if enabled
        if config.SHOW_FPS:
            fps_text = f"FPS: {self.fps:.1f}"
            cv2.putText(
                annotated, fps_text, (10, annotated.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
            )
        
        return annotated
    
    def run(self):
        """Main application loop"""
        self.start()
        
        try:
            while self.running:
                # Read frame
                success, frame = self.camera.read_frame()
                if not success:
                    print("Failed to read frame")
                    break
                
                # Process every Nth frame
                self.frame_count += 1
                if self.frame_count % config.FRAME_SKIP != 0:
                    continue
                
                # Process frame
                annotated, stack = self.process_frame(frame)
                
                # Calculate FPS
                current_time = time.time()
                self.fps = 1.0 / (current_time - self.last_time)
                self.last_time = current_time
                
                # Display if enabled
                if config.SHOW_DEBUG_WINDOW:
                    cv2.imshow(config.WINDOW_NAME, annotated)
                    
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('s'):
                        filename = f"capture_{int(time.time())}.jpg"
                        cv2.imwrite(filename, annotated)
                        print(f"Saved frame to {filename}")
                
                # Log every 30 frames
                if self.frame_count % 30 == 0:
                    print(f"[{self.frame_count}] {self.analyzer.format_stack_string(stack)}")
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the application and cleanup"""
        print("\nStopping application...")
        self.running = False
        self.camera.release()
        cv2.destroyAllWindows()
        print("✓ Cleanup complete")


def main():
    """Entry point"""
    try:
        app = FigurineRecognition()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
