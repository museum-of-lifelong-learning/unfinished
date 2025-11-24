#!/usr/bin/env python3
"""
Data Capture Tool for Figurine Shape Training
Captures images from webcam and saves them organized by shape and color.
"""
import sys
import os
sys.path.insert(0, '/app')

import cv2
import time
from datetime import datetime
from config import config
from src.capture import CameraCapture


# Define your 36 shape types
SHAPE_CLASSES = [
    'sphere', 'cube', 'cylinder', 'cone', 'pyramid', 'prism',
    'hexagon', 'octagon', 'torus', 'ellipsoid', 'cuboid', 'tetrahedron',
    'dodecahedron', 'icosahedron', 'star', 'heart', 'cross', 'ring',
    'disc', 'rod', 'block', 'wedge', 'arch', 'dome',
    'spiral', 'wave', 'zigzag', 'ball', 'box', 'tube',
    'cap', 'base', 'joint', 'connector', 'adapter', 'terminal'
]

# Define color categories
COLOR_CLASSES = [
    'red', 'blue', 'green', 'yellow', 'orange', 'purple',
    'pink', 'cyan', 'magenta', 'brown', 'black', 'white',
    'gray', 'lime', 'navy', 'teal', 'maroon', 'olive'
]


class DataCaptureApp:
    """Interactive data capture application"""
    
    def __init__(self):
        """Initialize the capture application"""
        self.camera = CameraCapture()
        self.current_shape = None
        self.current_color = None
        self.capture_count = 0
        self.output_dir = '/app/data/training'
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("=" * 70)
        print("FIGURINE DATA CAPTURE TOOL")
        print("=" * 70)
        print("\nAvailable shapes:")
        for i, shape in enumerate(SHAPE_CLASSES, 1):
            print(f"  {i:2d}. {shape}")
        
        print("\nAvailable colors:")
        for i, color in enumerate(COLOR_CLASSES, 1):
            print(f"  {i:2d}. {color}")
        
        print("\n" + "=" * 70)
        print("CONTROLS:")
        print("=" * 70)
        print("  's' - Select shape and color")
        print("  SPACE - Capture image")
        print("  'n' - Next shape/color")
        print("  'i' - Show info")
        print("  'q' - Quit")
        print("=" * 70 + "\n")
    
    def select_shape_and_color(self):
        """Interactively select shape and color"""
        print("\n" + "=" * 70)
        
        # Select shape
        while True:
            print("\nEnter shape number (1-{}):".format(len(SHAPE_CLASSES)), end=" ")
            try:
                shape_num = int(input().strip())
                if 1 <= shape_num <= len(SHAPE_CLASSES):
                    self.current_shape = SHAPE_CLASSES[shape_num - 1]
                    break
                else:
                    print(f"Invalid! Enter 1-{len(SHAPE_CLASSES)}")
            except ValueError:
                print("Invalid input! Enter a number")
        
        # Select color
        while True:
            print("Enter color number (1-{}):".format(len(COLOR_CLASSES)), end=" ")
            try:
                color_num = int(input().strip())
                if 1 <= color_num <= len(COLOR_CLASSES):
                    self.current_color = COLOR_CLASSES[color_num - 1]
                    break
                else:
                    print(f"Invalid! Enter 1-{len(COLOR_CLASSES)}")
            except ValueError:
                print("Invalid input! Enter a number")
        
        # Create directory for this combination
        self.capture_count = 0
        combo_dir = os.path.join(self.output_dir, f"{self.current_shape}_{self.current_color}")
        os.makedirs(combo_dir, exist_ok=True)
        
        # Count existing images
        existing = len([f for f in os.listdir(combo_dir) if f.endswith('.jpg')])
        
        print("\n" + "=" * 70)
        print(f"✓ Selected: {self.current_shape.upper()} - {self.current_color.upper()}")
        print(f"  Save directory: {combo_dir}")
        print(f"  Existing images: {existing}")
        print("=" * 70)
        print("Position the shape in frame and press SPACE to capture")
        print("=" * 70 + "\n")
    
    def capture_image(self, frame):
        """Save current frame to disk"""
        if self.current_shape is None or self.current_color is None:
            print("⚠ Please select shape and color first (press 's')")
            return
        
        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        combo_dir = os.path.join(self.output_dir, f"{self.current_shape}_{self.current_color}")
        filename = os.path.join(combo_dir, f"{timestamp}.jpg")
        
        # Save image
        cv2.imwrite(filename, frame)
        self.capture_count += 1
        
        print(f"✓ Captured: {filename} (#{self.capture_count})")
    
    def show_info(self):
        """Display current session info"""
        print("\n" + "=" * 70)
        print("CURRENT SESSION INFO")
        print("=" * 70)
        if self.current_shape and self.current_color:
            print(f"Shape: {self.current_shape}")
            print(f"Color: {self.current_color}")
            print(f"Images captured this session: {self.capture_count}")
            
            combo_dir = os.path.join(self.output_dir, f"{self.current_shape}_{self.current_color}")
            total = len([f for f in os.listdir(combo_dir) if f.endswith('.jpg')])
            print(f"Total images in folder: {total}")
        else:
            print("No shape/color selected yet")
        print("=" * 70 + "\n")
    
    def draw_overlay(self, frame):
        """Draw information overlay on frame"""
        overlay = frame.copy()
        h, w = frame.shape[:2]
        
        # Semi-transparent background
        cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
        
        # Current selection
        if self.current_shape and self.current_color:
            text = f"Shape: {self.current_shape.upper()}  |  Color: {self.current_color.upper()}"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            count_text = f"Captured: {self.capture_count}"
            cv2.putText(frame, count_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            text = "Press 'S' to select shape and color"
            cv2.putText(frame, text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        # Crosshair for centering
        center_x, center_y = w // 2, h // 2
        cv2.line(frame, (center_x - 30, center_y), (center_x + 30, center_y), (0, 255, 0), 2)
        cv2.line(frame, (center_x, center_y - 30), (center_x, center_y + 30), (0, 255, 0), 2)
        cv2.circle(frame, (center_x, center_y), 100, (0, 255, 0), 2)
        
        return frame
    
    def run(self):
        """Main application loop"""
        try:
            self.camera.start()
            
            print("Camera ready! Press 's' to begin...")
            
            while True:
                # Read frame
                success, frame = self.camera.read_frame()
                if not success:
                    print("Failed to read frame")
                    break
                
                # Draw overlay
                display_frame = self.draw_overlay(frame)
                
                # Show frame
                cv2.imshow('Figurine Data Capture', display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\nQuitting...")
                    break
                elif key == ord('s'):
                    self.select_shape_and_color()
                elif key == ord(' '):
                    self.capture_image(frame)
                elif key == ord('n'):
                    print("\nMoving to next shape/color...")
                    self.select_shape_and_color()
                elif key == ord('i'):
                    self.show_info()
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self.camera.release()
            cv2.destroyAllWindows()
            self.print_summary()
    
    def print_summary(self):
        """Print capture session summary"""
        print("\n" + "=" * 70)
        print("CAPTURE SESSION SUMMARY")
        print("=" * 70)
        
        # Count all captured images
        total_images = 0
        combo_count = 0
        
        if os.path.exists(self.output_dir):
            for combo_dir in os.listdir(self.output_dir):
                combo_path = os.path.join(self.output_dir, combo_dir)
                if os.path.isdir(combo_path):
                    images = len([f for f in os.listdir(combo_path) if f.endswith('.jpg')])
                    if images > 0:
                        print(f"  {combo_dir}: {images} images")
                        total_images += images
                        combo_count += 1
        
        print("=" * 70)
        print(f"Total combinations: {combo_count}")
        print(f"Total images: {total_images}")
        print(f"Data saved to: {self.output_dir}")
        print("=" * 70 + "\n")


def main():
    """Entry point"""
    app = DataCaptureApp()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
