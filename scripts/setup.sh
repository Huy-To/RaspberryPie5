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
    python3-dev \
    python3-tk \
    python3-pil.imagetk

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

# Try to install dlib dependencies (for face_recognition)
echo "🔧 Installing dlib dependencies (REQUIRED for face_recognition)..."
echo "   Installing: cmake, libdlib-dev, libopenblas-dev, liblapack-dev"
set +e  # Don't exit on error for individual packages
CMake_INSTALLED=false
for pkg in cmake libdlib-dev libopenblas-dev liblapack-dev; do
    if sudo apt install -y "$pkg" 2>&1 | grep -q "Setting up\|is already"; then
        echo "✅ Installed: $pkg"
        if [ "$pkg" = "cmake" ]; then
            CMake_INSTALLED=true
        fi
    else
        echo "⚠️  Failed to install: $pkg"
        if [ "$pkg" = "cmake" ]; then
            echo "   ⚠️  WARNING: cmake is REQUIRED for building dlib!"
            echo "   Try manually: sudo apt update && sudo apt install -y cmake"
        fi
    fi
done

# Verify cmake is installed
if command -v cmake &> /dev/null; then
    CMAKE_VERSION=$(cmake --version | head -n1)
    echo "✅ cmake verified: $CMAKE_VERSION"
    CMake_INSTALLED=true
else
    echo "❌ cmake is NOT installed or not in PATH"
    echo "   This will cause dlib build to fail!"
    echo "   Install with: sudo apt install -y cmake"
    CMake_INSTALLED=false
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

# Add ~/.local/bin to PATH if not already there
echo "🔧 Configuring PATH..."
LOCAL_BIN="$HOME/.local/bin"
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
    export PATH="$LOCAL_BIN:$PATH"
    echo "   Added $LOCAL_BIN to PATH for this session"
    
    # Add to .bashrc for persistence (if it exists and not already added)
    if [ -f "$HOME/.bashrc" ] && ! grep -q "$LOCAL_BIN" "$HOME/.bashrc"; then
        echo "" >> "$HOME/.bashrc"
        echo "# Added by Raspberry Pi Face Detection setup" >> "$HOME/.bashrc"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.bashrc"
        echo "   Added $LOCAL_BIN to ~/.bashrc for future sessions"
    fi
    
    # Also add to .profile if it exists (for login shells)
    if [ -f "$HOME/.profile" ] && ! grep -q "$LOCAL_BIN" "$HOME/.profile"; then
        echo "" >> "$HOME/.profile"
        echo "# Added by Raspberry Pi Face Detection setup" >> "$HOME/.profile"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.profile"
        echo "   Added $LOCAL_BIN to ~/.profile for login shells"
    fi
else
    echo "   $LOCAL_BIN is already in PATH"
fi

# Upgrade pip (using system Python)
echo "⬆️  Upgrading pip..."
echo "   Note: Using --break-system-packages flag (required on newer Raspberry Pi OS)"
python3 -m pip install --upgrade pip setuptools wheel --break-system-packages --no-warn-script-location

# Install Python dependencies
echo "📚 Installing Python dependencies..."
echo "   This may take several minutes on Raspberry Pi..."

# Install core dependencies first (these don't need libcap-dev)
echo "   Installing core packages (ultralytics, numpy, Pillow)..."
echo "   Note: Using system numpy if available to avoid version conflicts with picamera2"

# Check if system numpy is available and compatible
if python3 -c "import numpy; print(numpy.__version__)" 2>/dev/null | grep -q "."; then
    SYSTEM_NUMPY_VERSION=$(python3 -c "import numpy; print(numpy.__version__)" 2>/dev/null)
    echo "   System numpy version: $SYSTEM_NUMPY_VERSION"
    echo "   Will use system numpy to avoid conflicts with system picamera2"
    # Install ultralytics and Pillow, but let numpy use system version
    python3 -m pip install --no-cache-dir --break-system-packages --no-warn-script-location ultralytics Pillow
else
    # No system numpy, install via pip
    python3 -m pip install --no-cache-dir --break-system-packages --no-warn-script-location ultralytics numpy Pillow
fi

# Install picamera2 separately (requires libcap-dev)
echo "   Installing picamera2 (requires libcap-dev)..."
if [ "$LIBCAP_INSTALLED" = false ]; then
    echo "   ⚠️  WARNING: libcap-dev not installed. picamera2 installation may fail."
    echo "   If it fails, install libcap-dev manually and run: python3 -m pip install --break-system-packages picamera2"
fi

set +e  # Don't exit on error for picamera2
if python3 -m pip install --no-cache-dir --break-system-packages --no-warn-script-location picamera2 2>&1 | tee /tmp/picamera2_install.log; then
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
        echo "   Then run: python3 -m pip install --break-system-packages picamera2"
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

# Install face_recognition (for facial recognition features)
echo "   Installing face_recognition (this may take a while - requires dlib)..."
echo "   Note: face_recognition requires dlib, which can take 10-30 minutes to build on Raspberry Pi"

# Check if cmake is available before attempting installation
if [ "$CMake_INSTALLED" = false ]; then
    echo ""
    echo "❌ SKIPPING face_recognition installation - cmake is not installed!"
    echo ""
    echo "   SOLUTION: Install cmake first:"
    echo "   sudo apt update"
    echo "   sudo apt install -y cmake libdlib-dev libopenblas-dev liblapack-dev"
    echo ""
    echo "   Then re-run this script or install manually:"
    echo "   python3 -m pip install --break-system-packages face_recognition"
    echo ""
    FACE_RECOGNITION_INSTALLED=false
else
    set +e  # Don't exit on error for face_recognition (it's optional)
    if python3 -m pip install --no-cache-dir --break-system-packages --no-warn-script-location face_recognition 2>&1 | tee /tmp/face_recognition_install.log; then
        echo "✅ face_recognition installed successfully"
        FACE_RECOGNITION_INSTALLED=true
    else
        echo ""
        echo "⚠️  face_recognition installation failed"
        echo ""
        if grep -qi "CMake\|cmake" /tmp/face_recognition_install.log 2>/dev/null; then
            echo "   Error: CMake is not installed or not working"
            echo ""
            echo "   SOLUTION:"
            echo "   1. Verify cmake: cmake --version"
            echo "   2. If not installed: sudo apt install -y cmake"
            echo "   3. If installed but not found: which cmake"
            echo "   4. Install all dependencies: sudo apt install -y cmake libdlib-dev libopenblas-dev liblapack-dev"
            echo "   5. Then retry: python3 -m pip install --break-system-packages face_recognition"
            echo ""
        elif grep -qi "dlib" /tmp/face_recognition_install.log 2>/dev/null; then
            echo "   Error: dlib build failed"
            echo ""
            echo "   SOLUTION: Install all dlib dependencies:"
            echo "   sudo apt install -y cmake libdlib-dev libopenblas-dev liblapack-dev"
            echo "   Then try: python3 -m pip install --break-system-packages face_recognition"
            echo ""
        else
            echo "   Troubleshooting:"
            echo "   1. Install dependencies: sudo apt install -y cmake libdlib-dev libopenblas-dev liblapack-dev"
            echo "   2. Try installing dlib separately: python3 -m pip install --break-system-packages dlib"
            echo "   3. Then install face_recognition: python3 -m pip install --break-system-packages face_recognition"
        fi
        echo "   Full error log saved to: /tmp/face_recognition_install.log"
        echo "   ⚠️  Face recognition features will be disabled until face_recognition is installed"
        FACE_RECOGNITION_INSTALLED=false
    fi
    set -e  # Re-enable exit on error
fi

# Install imageio and imageio-ffmpeg (for video processing in enrollment)
echo "   Installing imageio and imageio-ffmpeg (for video processing)..."
set +e  # Don't exit on error for imageio (it's optional)
if python3 -m pip install --no-cache-dir --break-system-packages --no-warn-script-location imageio imageio-ffmpeg 2>&1 | tee /tmp/imageio_install.log; then
    echo "✅ imageio installed successfully"
    IMAGEIO_INSTALLED=true
else
    echo ""
    echo "⚠️  imageio installation failed"
    echo "   Video-based enrollment will not work until imageio is installed"
    echo "   Try manually: python3 -m pip install --break-system-packages imageio imageio-ffmpeg"
    IMAGEIO_INSTALLED=false
fi
set -e  # Re-enable exit on error

# Install FastAPI and dependencies (for n8n API integration)
echo "   Installing FastAPI and dependencies (for n8n integration)..."
set +e  # Don't exit on error for FastAPI (it's optional)
if python3 -m pip install --no-cache-dir --break-system-packages --no-warn-script-location fastapi uvicorn httpx pydantic python-multipart 2>&1 | tee /tmp/fastapi_install.log; then
    echo "✅ FastAPI installed successfully"
    FASTAPI_INSTALLED=true
else
    echo ""
    echo "⚠️  FastAPI installation failed"
    echo "   n8n API integration will not work until FastAPI is installed"
    echo "   Try manually: python3 -m pip install --break-system-packages fastapi uvicorn httpx pydantic python-multipart"
    FASTAPI_INSTALLED=false
fi
set -e  # Re-enable exit on error

# Make all scripts executable using fix_permissions.sh
echo "🔧 Making scripts executable..."
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

if [ -f "$PROJECT_ROOT/fix_permissions.sh" ]; then
    chmod +x "$PROJECT_ROOT/fix_permissions.sh" 2>/dev/null || true
    bash "$PROJECT_ROOT/fix_permissions.sh" 2>/dev/null || {
        # Fallback if fix_permissions.sh fails
        chmod +x run.sh run_api.sh run_enroll.sh 2>/dev/null || true
        chmod +x scripts/*.sh 2>/dev/null || true
        chmod +x src/*.py 2>/dev/null || true
    }
else
    # Fallback if fix_permissions.sh doesn't exist
    chmod +x run.sh run_api.sh run_enroll.sh 2>/dev/null || true
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod +x src/*.py 2>/dev/null || true
fi
echo "✅ Scripts made executable"

# Verify installations
echo "🔍 Verifying installations..."

# Verify picamera2 (REQUIRED)
# Check if picamera2 is available (either from pip install or system package)
if python3 -c "from picamera2 import Picamera2; print('OK')" 2>&1 | grep -q "OK"; then
    echo "✅ picamera2 is ready to use (REQUIRED for Raspberry Pi Camera Module)"
elif python3 -c "import picamera2" 2>/dev/null; then
    echo "✅ picamera2 is available (system package)"
elif [ "$PICAMERA2_INSTALLED" = true ]; then
    echo "✅ picamera2 was installed via pip"
else
    echo "⚠️  picamera2 verification failed, but checking if system package exists..."
    if python3 -c "import sys; sys.path.insert(0, '/usr/lib/python3/dist-packages'); from picamera2 import Picamera2" 2>/dev/null; then
        echo "✅ picamera2 is available as system package"
    else
        echo "❌ picamera2 is not available!"
        echo "   This system requires picamera2 to work."
        echo "   Please fix the libcap-dev issue and re-run setup.sh"
        echo "   Or install system package: sudo apt install -y python3-picamera2"
        exit 1
    fi
fi

# Verify numpy compatibility
echo "🔍 Checking numpy compatibility with picamera2..."
if python3 -c "import numpy; import picamera2; print('✅ numpy and picamera2 are compatible')" 2>/dev/null; then
    NUMPY_VERSION=$(python3 -c "import numpy; print(numpy.__version__)" 2>/dev/null)
    echo "✅ numpy $NUMPY_VERSION is compatible with picamera2"
else
    echo "⚠️  numpy version conflict detected!"
    echo "   System picamera2 may be incompatible with pip-installed numpy"
    echo "   Attempting to fix by using system numpy..."
    # Try to uninstall pip numpy and use system version
    python3 -m pip uninstall -y numpy 2>/dev/null || true
    if python3 -c "import numpy; import picamera2; print('OK')" 2>/dev/null; then
        echo "✅ Fixed: Now using system numpy"
    else
        echo "⚠️  Warning: numpy compatibility issue may persist"
        echo "   You may need to reinstall picamera2 or use system packages"
    fi
fi

# Verify Pillow
if python3 -c "from PIL import Image; print(f'✅ Pillow {Image.__version__} installed')" 2>/dev/null; then
    echo "✅ Pillow is ready to use"
else
    echo "❌ Pillow installation failed. Trying to fix..."
    python3 -m pip install --upgrade --no-cache-dir --break-system-packages --no-warn-script-location Pillow
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
cd "$PROJECT_ROOT" || exit 1
if [ -f "models/yolov12n-face.pt" ]; then
    echo "✅ YOLO model found: models/yolov12n-face.pt"
else
    echo "❌ YOLO model not found. Please ensure yolov12n-face.pt is in models/ directory."
    echo "   Expected: $PROJECT_ROOT/models/yolov12n-face.pt"
    echo "   You can download it from: https://github.com/ultralytics/assets/releases"
    exit 1
fi

# Test camera access (non-blocking - just a warning if it fails)
echo "📹 Testing camera access..."
set +e  # Temporarily disable exit on error for camera test
cd "$PROJECT_ROOT" || exit 1
if python3 src/test_camera.py 2>/dev/null; then
    echo "✅ Camera test passed - everything is working!"
else
    echo "⚠️  Camera test failed, but this is OK if:"
    echo "   - Camera is not connected right now"
    echo "   - You want to test later"
    echo ""
    echo "   To test manually:"
    echo "   - System test: rpicam-hello"
    echo "   - Python test: python3 src/test_camera.py"
fi
set -e  # Re-enable exit on error

# Make scripts executable (already done earlier, but ensure it's done)
echo "🔐 Ensuring scripts are executable..."
cd "$PROJECT_ROOT" || exit 1

if [ -f "$PROJECT_ROOT/fix_permissions.sh" ]; then
    chmod +x "$PROJECT_ROOT/fix_permissions.sh" 2>/dev/null || true
    bash "$PROJECT_ROOT/fix_permissions.sh" 2>/dev/null || {
        # Fallback if fix_permissions.sh fails
        chmod +x run.sh run_api.sh run_enroll.sh 2>/dev/null || true
        chmod +x scripts/*.sh 2>/dev/null || true
        chmod +x src/*.py 2>/dev/null || true
    }
else
    # Fallback if fix_permissions.sh doesn't exist
    chmod +x run.sh run_api.sh run_enroll.sh 2>/dev/null || true
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod +x src/*.py 2>/dev/null || true
fi
echo "✅ All scripts are executable"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Quick Start:"
echo "   Run: ./run.sh"
echo ""
echo "   Or directly:"
echo "   python3 src/raspberry_pi_face_detection.py"
echo ""
echo "📝 PATH Configuration:"
echo "   ~/.local/bin has been added to your PATH"
echo "   If you open a new terminal, run: source ~/.bashrc"
echo "   Or restart your terminal session"
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

