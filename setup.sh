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

# Try to install libcap-dev (REQUIRED for picamera2/python-prctl)
# Try multiple package names as they vary by OS version
echo "🔧 Installing libcap-dev (REQUIRED for picamera2)..."
LIBCAP_INSTALLED=false
LIBCAP_PKG=""

# First, try installing build-essential (sometimes needed for libcap-dev)
echo "   Installing build-essential (may be needed for libcap-dev)..."
sudo apt install -y build-essential 2>/dev/null || true

# Try different package names
for pkg in libcap-dev libcap2-dev libcap2; do
    echo "   Trying: $pkg"
    if sudo apt install -y "$pkg" 2>&1 | grep -q "Setting up\|is already\|0 upgraded"; then
        # Verify it's actually installed
        if dpkg -l | grep -q "^ii.*libcap"; then
            echo "✅ Installed: $pkg (required for picamera2)"
            LIBCAP_INSTALLED=true
            LIBCAP_PKG="$pkg"
            break
        fi
    fi
done

if [ "$LIBCAP_INSTALLED" = false ]; then
    echo ""
    echo "❌ libcap-dev not available (tried: libcap-dev, libcap2-dev, libcap2)"
    echo ""
    echo "⚠️  CRITICAL: picamera2 requires libcap development headers!"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check available packages: apt-cache search libcap"
    echo "  2. Try: sudo apt install -y libcap-dev"
    echo "  3. Or run the fix script: chmod +x fix_libcap.sh && ./fix_libcap.sh"
    echo "  4. You may need to update: sudo apt update && sudo apt upgrade"
    echo ""
    echo "Attempting to continue anyway, but picamera2 installation will likely fail..."
    echo ""
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

# Install core dependencies first (these don't need libcap-dev)
echo "   Installing core packages (ultralytics, numpy, Pillow)..."
pip install --no-cache-dir ultralytics numpy Pillow

# Install picamera2 separately (requires libcap-dev)
echo "   Installing picamera2 (requires libcap-dev)..."
if [ "$LIBCAP_INSTALLED" = false ]; then
    echo "   ⚠️  WARNING: libcap-dev not installed. picamera2 installation may fail."
    echo "   If it fails, install libcap-dev manually and run: pip install picamera2"
fi

set +e  # Don't exit on error for picamera2
if pip install --no-cache-dir picamera2 2>&1 | tee /tmp/picamera2_install.log; then
    echo "✅ picamera2 installed successfully"
    PICAMERA2_INSTALLED=true
else
    echo ""
    echo "❌ picamera2 installation failed!"
    echo ""
    if grep -q "libcap" /tmp/picamera2_install.log 2>/dev/null; then
        echo "   Error: Missing libcap development headers"
        echo ""
        echo "   SOLUTION: Install libcap-dev first:"
        echo "   sudo apt install -y libcap-dev"
        echo "   Then run: pip install picamera2"
        echo ""
        echo "   Or try alternative package names:"
        echo "   sudo apt install -y libcap2-dev"
        echo "   sudo apt install -y libcap2"
    fi
    echo "   Full error log saved to: /tmp/picamera2_install.log"
    PICAMERA2_INSTALLED=false
    exit 1  # Exit on failure since picamera2 is required
fi
set -e  # Re-enable exit on error

# Verify installations
echo "🔍 Verifying installations..."

# Verify picamera2 (REQUIRED)
if [ "$PICAMERA2_INSTALLED" = true ]; then
    if python3 -c "from picamera2 import Picamera2; print('✅ picamera2 installed successfully')" 2>/dev/null; then
        echo "✅ picamera2 is ready to use (REQUIRED for Raspberry Pi Camera Module)"
    else
        echo "⚠️  picamera2 installed but import failed. This may indicate a compatibility issue."
    fi
else
    echo "❌ picamera2 installation failed!"
    echo "   This system requires picamera2 to work."
    echo "   Please fix the libcap-dev issue and re-run setup.sh"
    exit 1
fi

# Verify Pillow
if python3 -c "from PIL import Image; print(f'✅ Pillow {Image.__version__} installed')" 2>/dev/null; then
    echo "✅ Pillow is ready to use"
else
    echo "❌ Pillow installation failed. Trying to fix..."
    pip install --upgrade --no-cache-dir Pillow
    if python3 -c "from PIL import Image" 2>/dev/null; then
        echo "✅ Pillow fixed"
    else
        echo "❌ Pillow installation failed!"
        exit 1
    fi
fi

# Verify ultralytics
if python3 -c "from ultralytics import YOLO; print('✅ ultralytics installed')" 2>/dev/null; then
    echo "✅ ultralytics is ready to use"
else
    echo "❌ ultralytics installation failed!"
    exit 1
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
if python3 test_camera.py 2>/dev/null; then
    echo "✅ Camera test passed - everything is working!"
else
    echo "⚠️  Camera test failed, but this is OK if:"
    echo "   - Camera is not connected right now"
    echo "   - You want to test later"
    echo ""
    echo "   To test manually:"
    echo "   - System test: rpicam-hello"
    echo "   - Python test: python3 test_camera.py"
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

