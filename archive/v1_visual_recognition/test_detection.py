#!/usr/bin/env python3
"""
Test script to analyze figurine images and detect individual shapes.
"""
import sys
import os
sys.path.insert(0, '/app')

import cv2
import numpy as np
from src.detection import ShapeDetector
from src.capture import CameraCapture


def test_image_detection(image_path):
    """Test shape detection on a single image"""
    print(f"\n{'='*60}")
    print(f"Testing: {image_path}")
    print(f"{'='*60}")
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"ERROR: Could not load image {image_path}")
        return
    
    print(f"✓ Image loaded: {img.shape} (H x W x C)")
    
    # Preprocess
    camera = CameraCapture()
    processed = camera.preprocess_frame(img)
    print(f"✓ Preprocessing complete: {len(processed)} outputs generated")
    
    # Detect shapes
    detector = ShapeDetector()
    contours = detector.find_shape_contours(processed)
    print(f"✓ Found {len(contours)} contours")
    
    # Extract ROIs
    rois = detector.extract_rois(img, contours)
    print(f"✓ Extracted {len(rois)} potential shapes")
    
    # Analyze each shape
    for i, roi_data in enumerate(rois):
        features = detector.analyze_shape_geometry(roi_data['contour'])
        print(f"\nShape #{i+1}:")
        print(f"  Position: {roi_data['center']}")
        print(f"  BBox: {roi_data['bbox']}")
        print(f"  Area: {features['area']:.0f} pixels")
        print(f"  Circularity: {features['circularity']:.2f} (1.0 = perfect circle)")
        print(f"  Aspect Ratio: {features['aspect_ratio']:.2f}")
        print(f"  Corners: {features['corners']}")
        
        # Simple shape guess based on geometry
        if features['circularity'] > 0.8:
            guess = "sphere/ball"
        elif features['corners'] == 4 and 0.9 < features['aspect_ratio'] < 1.1:
            guess = "cube/square"
        elif features['corners'] == 4:
            guess = "rectangle/cylinder"
        elif features['corners'] == 3:
            guess = "triangle/pyramid"
        else:
            guess = "unknown"
        print(f"  Geometric guess: {guess}")
    
    # Save annotated image
    output_img = img.copy()
    for i, roi_data in enumerate(rois):
        x, y, w, h = roi_data['bbox']
        cv2.rectangle(output_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(output_img, f"#{i+1}", (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    output_path = image_path.replace('.jpeg', '_detected.jpeg').replace('.jpg', '_detected.jpg')
    cv2.imwrite(output_path, output_img)
    print(f"\n✓ Annotated image saved to: {output_path}")


def main():
    """Test all images in assets folder"""
    assets_dir = '/app/assets'
    
    if not os.path.exists(assets_dir):
        print(f"ERROR: Assets directory not found: {assets_dir}")
        return 1
    
    # Find all image files
    image_files = [f for f in os.listdir(assets_dir) 
                   if f.endswith(('.jpeg', '.jpg', '.png'))]
    
    if not image_files:
        print(f"No images found in {assets_dir}")
        return 1
    
    print(f"Found {len(image_files)} images to process")
    
    # Process each image
    for img_file in sorted(image_files):
        if '_detected' not in img_file:  # Skip already processed images
            img_path = os.path.join(assets_dir, img_file)
            try:
                test_image_detection(img_path)
            except Exception as e:
                print(f"ERROR processing {img_file}: {e}")
                import traceback
                traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("Processing complete!")
    print("Check assets/ folder for *_detected.jpeg files")
    print(f"{'='*60}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
