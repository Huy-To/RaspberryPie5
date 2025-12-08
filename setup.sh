#!/bin/bash

# Raspberry Pi 5 Face Detection System Setup Script
# =================================================

set -e  # Exit on error

echo "🚀 Setting up Raspberry Pi 5 Face Detection System..."
echo "=================================================="
echo ""
echo "ℹ️  Note: Some optional system packages may not be available."
echo "   This is OK - we'll use pip-installed packages instead."
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi. Continuing anyway..."
fi

# Check Python version
echo "🐍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
python3 --version

# Update package list (but don't upgrade everything - takes too long)
echo "📦 Updating package list..."
sudo apt update

# Install essential system dependencies (only packages that are definitely available)
echo "🔧 Installing essential system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-venv \
    python3-dev

# Try to install optional packages (continue if they fail)
echo "🔧 Installing optional system dependencies (if available)..."
set +e  # Don't exit on error for optional packages

# Try to install OpenCV system package (optional - we'll use pip version)
if sudo apt install -y python3-opencv 2>/dev/null; then
    echo "✅ System OpenCV installed"
else
    echo "⚠️  System OpenCV not available, will use pip-installed version"
fi

# Try to install libcap-dev (required for picamera2/python-prctl)
# Try multiple package names as they vary by OS version
LIBCAP_INSTALLED=false
for pkg in libcap-dev libcap2-dev; do
    if sudo apt install -y "$pkg" 2>/dev/null; then
        echo "✅ Installed: $pkg (required for picamera2)"
        LIBCAP_INSTALLED=true
        break
    fi
done

if [ "$LIBCAP_INSTALLED" = false ]; then
    echo "⚠️  libcap-dev not available (tried libcap-dev and libcap2-dev)"
    echo "   This may cause picamera2 installation to fail, but OpenCV/USB cameras will still work"
    echo "   If you need picamera2, you may need to build libcap from source or use a different OS version"
fi

# Try to install other optional packages
for pkg in libopencv-dev libatlas-base-dev libhdf5-dev libhdf5-serial-dev; do
    if sudo apt install -y "$pkg" 2>/dev/null; then
        echo "✅ Installed: $pkg"
    else
        echo "⚠️  Package not available: $pkg (skipping - not critical)"
    fi
done

set -e  # Re-enable exit on error

# Create virtual environment
echo "🏠 Creating Python virtual environment..."
if [ -d "face_detection_env" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf face_detection_env
fi
python3 -m venv face_detection_env
source face_detection_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📚 Installing Python dependencies..."
echo "   This may take several minutes on Raspberry Pi..."

# Install core dependencies first (these should always work)
echo "   Installing core packages (ultralytics, opencv-python, numpy)..."
pip install --no-cache-dir ultralytics opencv-python numpy

# Try to install picamera2 separately (it may fail if libcap-dev is missing)
echo "   Attempting to install picamera2 (for Raspberry Pi Camera Module)..."
set +e  # Don't exit on error for picamera2
PICAMERA2_INSTALLED=false
if pip install --no-cache-dir picamera2 2>/dev/null; then
    echo "✅ picamera2 installed successfully"
    PICAMERA2_INSTALLED=true
else
    echo "⚠️  picamera2 installation failed (likely due to missing libcap-dev)"
    echo "   This is OK if you're using USB webcam instead of Pi Camera Module"
    echo "   You can use: --camera-type opencv for USB webcams"
fi
set -e  # Re-enable exit on error

# Verify installations
echo "🔍 Verifying installations..."
if python3 -c "import cv2; print(f'✅ OpenCV {cv2.__version__} installed successfully')" 2>/dev/null; then
    echo "✅ OpenCV is ready to use"
else
    echo "❌ OpenCV installation failed. Trying to fix..."
    pip install --upgrade --no-cache-dir opencv-python
    if python3 -c "import cv2" 2>/dev/null; then
        echo "✅ OpenCV fixed"
    else
        echo "⚠️  OpenCV verification failed, but continuing..."
    fi
fi

# Verify picamera2 installation
if python3 -c "from picamera2 import Picamera2; print('✅ picamera2 installed successfully')" 2>/dev/null; then
    echo "✅ picamera2 is ready to use (for Raspberry Pi Camera Module)"
else
    echo "⚠️  picamera2 not available"
    if [ "$LIBCAP_INSTALLED" = false ]; then
        echo "   Reason: libcap-dev package not found in repositories"
        echo "   Solution: Use USB webcam with --camera-type opencv"
    else
        echo "   Installation may have failed for another reason"
        echo "   You can still use USB webcam with --camera-type opencv"
    fi
fi

# Check if model file exists
echo "🤖 Checking for YOLO model..."
if [ -f "yolov12n-face.pt" ]; then
    echo "✅ YOLO model found: yolov12n-face.pt"
else
    echo "❌ YOLO model not found. Please ensure yolov12n-face.pt is in the current directory."
    echo "   You can download it from: https://github.com/ultralytics/assets/releases"
    exit 1
fi

# Test camera access (non-blocking - just a warning if it fails)
echo "📹 Testing camera access..."
set +e  # Temporarily disable exit on error for camera test
if python3 -c "import cv2; cap = cv2.VideoCapture(0); result = cap.isOpened(); cap.release(); exit(0 if result else 1)" 2>/dev/null; then
    echo "✅ Camera accessible"
else
    echo "⚠️  Camera not accessible right now. This is OK if camera is not connected."
    echo "   You can test it later when running the application."
fi
set -e  # Re-enable exit on error

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x setup.sh
chmod +x run.sh
chmod +x raspberry_pi_face_detection.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Quick Start:"
echo "   Run: ./run.sh"
echo ""
echo "   Or manually:"
echo "   1. source face_detection_env/bin/activate"
echo "   2. python3 raspberry_pi_face_detection.py"
echo ""
echo "🎮 Runtime Controls:"
echo "   - 'q' or ESC: Quit"
echo "   - 'f': Toggle FPS display"
echo "   - 'd': Toggle detection info"
echo "   - 'c': Toggle confidence threshold"
echo "   - SPACE: Pause/Resume"
echo ""
echo "💡 Performance Tips:"
echo "   - Use --width 480 --height 360 for better FPS"
echo "   - Use --resize 0.5 for faster processing"
echo "   - Use --skip-frames 3 to reduce CPU load"
echo ""

