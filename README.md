# Figurine Shape Recognition

Real-time computer vision system for detecting and classifying stacked geometric shapes (figurines) using a webcam.

## Project Overview

This project enables recognition of up to 6 basic geometric shapes (sphere, cube, cylinder, etc.) stacked vertically on a stick. The system uses computer vision and lightweight machine learning to identify each shape and its position in the stack.

**Target Platforms:**

- Development: Linux notebook (for testing and iteration)
- Deployment: Raspberry Pi 5 with USB webcam

## Architecture

### Hardware Requirements

- Raspberry Pi 5 (4GB+ RAM recommended) or Linux development machine
- USB Webcam (720p or higher)
- Figurine shapes and stick assembly
- Optional: Controlled lighting setup

### Software Stack

- **Python 3.9+**
- **OpenCV**: Video capture, preprocessing, geometric analysis
- **TensorFlow Lite**: Lightweight inference for shape classification
- **NumPy**: Numerical operations
- **Git**: Version control with platform-specific configurations

## Technical Approach

### Phase 1: Classical CV + Lightweight ML (Hybrid Approach)

**Pipeline:**

```text
Webcam → OpenCV Capture → Preprocessing → Shape Detection → Classification → Stacking Analysis
```

**Key Components:**

1. **Frame Preprocessing** (OpenCV)
   - Background subtraction
   - Color-based segmentation
   - Noise reduction and filtering

2. **Shape Detection** (OpenCV)
   - Contour detection along the vertical stick
   - Region of Interest (ROI) extraction per shape
   - Geometric feature analysis (circularity, corners, aspect ratio)

3. **Classification** (TensorFlow Lite)
   - Lightweight CNN (MobileNetV3-small backbone)
   - Per-shape classification from ROI
   - Confidence scoring

4. **Stacking Logic** (Python)
   - Y-coordinate tracking for vertical ordering
   - Stick detection as reference line
   - Output: Ordered list of shapes from bottom to top

### Design Decisions

- **Hybrid approach**: Leverage OpenCV's efficiency for detection, ML only for classification
- **Color coding**: Optional colored markers between shapes to aid segmentation
- **Fixed camera**: Simplifies calibration and improves reliability
- **Target performance**: 10-15 FPS on Raspberry Pi 5

## Configuration Strategy

The project uses environment-based configuration to seamlessly switch between development and production environments:

- **`config/dev_config.py`**: Linux notebook settings (higher resolution, debug mode)
- **`config/pi_config.py`**: Raspberry Pi 5 optimized settings (lower resolution, optimized inference)
- **Environment variable `FIGURINE_ENV`**: Set to `dev` or `pi` to load appropriate config
- **Git tracked**: All configurations version controlled for reproducibility

## Project Structure

```text
figurine/
├── README.md
├── requirements.txt           # Common dependencies
├── requirements-dev.txt       # Development-only dependencies
├── requirements-pi.txt        # Raspberry Pi specific dependencies
├── config/
│   ├── __init__.py
│   ├── base_config.py        # Shared configuration
│   ├── dev_config.py         # Development overrides
│   └── pi_config.py          # Raspberry Pi overrides
├── src/
│   ├── __init__.py
│   ├── capture.py            # Webcam capture and preprocessing
│   ├── detection.py          # Shape detection (OpenCV)
│   ├── classification.py     # ML-based classification (TFLite)
│   ├── stacking.py           # Vertical ordering logic
│   └── main.py               # Main application entry point
├── models/
│   ├── shape_classifier.tflite
│   └── labels.txt
├── data/
│   ├── training/             # Training images
│   └── test/                 # Test images
├── notebooks/
│   └── exploration.ipynb     # Data exploration and model training
└── tests/
    └── test_detection.py
```

## Getting Started

### Quick Start with Docker (Recommended)

**Development Mode (Linux Notebook):**

```bash
# Build and run in Docker with webcam access
./docker-run-dev.sh
```

**Raspberry Pi Mode:**

```bash
# Build and run optimized for Pi
./docker-run-pi.sh
```

Or use Docker Compose:

```bash
docker-compose up -d
docker-compose exec figurine-dev /bin/bash
```

### Alternative: Manual Installation

**On Linux Development Machine:**

```bash
# Clone the repository
git clone <repository-url>
cd figurine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set environment
export FIGURINE_ENV=dev
```

**On Raspberry Pi 5:**

```bash
# Clone the repository
git clone <repository-url>
cd figurine

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (optimized for Pi)
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-pi.txt

# Set environment
export FIGURINE_ENV=pi
```

### Running the Application

**With Docker:**

```bash
# Development mode
./docker-run-dev.sh

# Inside container
python src/main.py
```

**Without Docker:**

```bash
# Ensure environment is set
export FIGURINE_ENV=dev  # or 'pi'

# Run the main application
python src/main.py
```

## Development Workflow

1. **Develop on Linux**: Fast iteration with full debugging tools
2. **Test changes**: Verify functionality locally
3. **Commit to Git**: Push changes to repository
4. **Deploy to Pi**: Pull latest code and run with Pi configuration
5. **Iterate**: Refine based on real-world performance

## Roadmap

- [ ] Phase 1: Setup project structure and configuration system
- [ ] Phase 2: Implement OpenCV capture and preprocessing
- [ ] Phase 3: Develop shape detection with contour analysis
- [ ] Phase 4: Create and train TFLite classification model
- [ ] Phase 5: Implement stacking logic and ordering
- [ ] Phase 6: Optimize performance for Raspberry Pi 5
- [ ] Phase 7: Add visualization and debugging UI

## Future Enhancements

- Web interface for remote monitoring
- Data logging and analytics
- Support for custom shape definitions
- Multi-camera support for 3D reconstruction
- Edge-case handling (missing shapes, tilted stacks)

## License

MIT License
