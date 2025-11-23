"""
Shape classification module using TensorFlow Lite.
Classifies detected shapes using a trained neural network.
"""
import os
import numpy as np
from config import config

# Try to import TensorFlow Lite
try:
    import tflite_runtime.interpreter as tflite
    TFLITE_AVAILABLE = True
except ImportError:
    try:
        import tensorflow.lite as tflite
        TFLITE_AVAILABLE = True
    except ImportError:
        TFLITE_AVAILABLE = False
        print("Warning: TensorFlow Lite not available. Classification will be disabled.")


class ShapeClassifier:
    """Classifies shapes using TensorFlow Lite model"""
    
    def __init__(self):
        """Initialize the classifier"""
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.labels = []
        self.model_loaded = False
        
        if TFLITE_AVAILABLE:
            self._load_model()
            self._load_labels()
    
    def _load_model(self):
        """Load the TensorFlow Lite model"""
        model_path = config.MODEL_PATH
        
        if not os.path.exists(model_path):
            print(f"Warning: Model not found at {model_path}")
            print("Classification will return 'unknown' until model is trained and placed in models/")
            return
        
        try:
            self.interpreter = tflite.Interpreter(
                model_path=model_path,
                num_threads=config.INFERENCE_THREADS
            )
            self.interpreter.allocate_tensors()
            
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            self.model_loaded = True
            print(f"✓ Model loaded from {model_path}")
            print(f"  Input shape: {self.input_details[0]['shape']}")
            print(f"  Output shape: {self.output_details[0]['shape']}")
            
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def _load_labels(self):
        """Load class labels"""
        labels_path = config.LABELS_PATH
        
        if not os.path.exists(labels_path):
            print(f"Warning: Labels file not found at {labels_path}")
            self.labels = ['sphere', 'cube', 'cylinder', 'pyramid', 'cone', 'unknown']
            return
        
        try:
            with open(labels_path, 'r') as f:
                self.labels = [line.strip() for line in f.readlines()]
            print(f"✓ Loaded {len(self.labels)} labels")
        except Exception as e:
            print(f"Error loading labels: {e}")
            self.labels = ['unknown']
    
    def preprocess_roi(self, roi):
        """
        Preprocess ROI for model input
        
        Args:
            roi: Region of interest (numpy array)
            
        Returns:
            numpy array: Preprocessed image ready for inference
        """
        if not self.model_loaded:
            return None
        
        # Get expected input shape
        input_shape = self.input_details[0]['shape']
        height, width = input_shape[1], input_shape[2]
        
        # Resize to model input size
        import cv2
        resized = cv2.resize(roi, (width, height))
        
        # Normalize to [0, 1] or [-1, 1] depending on model
        preprocessed = resized.astype(np.float32) / 255.0
        
        # Add batch dimension
        preprocessed = np.expand_dims(preprocessed, axis=0)
        
        return preprocessed
    
    def classify(self, roi):
        """
        Classify a single shape ROI
        
        Args:
            roi: Region of interest containing a shape
            
        Returns:
            dict: {'label': str, 'confidence': float, 'all_scores': dict}
        """
        if not self.model_loaded or roi is None or roi.size == 0:
            return {
                'label': 'unknown',
                'confidence': 0.0,
                'all_scores': {}
            }
        
        try:
            # Preprocess
            input_data = self.preprocess_roi(roi)
            if input_data is None:
                return {'label': 'unknown', 'confidence': 0.0, 'all_scores': {}}
            
            # Run inference
            self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
            self.interpreter.invoke()
            
            # Get output
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            scores = output_data[0]
            
            # Get top prediction
            top_idx = np.argmax(scores)
            confidence = float(scores[top_idx])
            label = self.labels[top_idx] if top_idx < len(self.labels) else 'unknown'
            
            # Create scores dictionary
            all_scores = {
                self.labels[i]: float(scores[i]) 
                for i in range(min(len(scores), len(self.labels)))
            }
            
            # Check confidence threshold
            if confidence < config.CONFIDENCE_THRESHOLD:
                label = 'unknown'
            
            return {
                'label': label,
                'confidence': confidence,
                'all_scores': all_scores
            }
            
        except Exception as e:
            print(f"Error during classification: {e}")
            return {'label': 'unknown', 'confidence': 0.0, 'all_scores': {}}
    
    def classify_batch(self, rois):
        """
        Classify multiple ROIs
        
        Args:
            rois: List of ROI dictionaries from detection module
            
        Returns:
            list: List of classification results
        """
        results = []
        for roi_dict in rois:
            result = self.classify(roi_dict['roi'])
            result['bbox'] = roi_dict['bbox']
            result['center'] = roi_dict['center']
            results.append(result)
        
        return results


if __name__ == "__main__":
    print("ShapeClassifier module loaded")
    classifier = ShapeClassifier()
    print(f"Model loaded: {classifier.model_loaded}")
    print(f"Available labels: {classifier.labels}")
