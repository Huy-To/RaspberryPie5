#!/bin/bash

# Raspberry Pi 5 Face Detection System Run Script
# ===============================================

echo "🎬 Starting Raspberry Pi 5 Face Detection System..."
echo "================================================="

# Verify picamera2 is installed (REQUIRED)
echo "🔍 Checking picamera2 installation..."
if ! python3 -c "from picamera2 import Picamera2" 2>/dev/null; then
    echo "❌ picamera2 not found"
    echo "📦 Installing picamera2..."
    python3 -m pip install --no-cache-dir --break-system-packages picamera2
    if python3 -c "from picamera2 import Picamera2" 2>/dev/null; then
        echo "✅ picamera2 installed successfully"
    else
        echo "❌ Failed to install picamera2. Please run setup.sh first."
        exit 1
    fi
else
    echo "✅ picamera2 is installed"
fi

# Check if model file exists
if [ ! -f "yolov12n-face.pt" ]; then
    echo "❌ YOLO model file not found: yolov12n-face.pt"
    echo "   Please ensure the model file is in the current directory."
    exit 1
fi

# Check if main script exists
if [ ! -f "raspberry_pi_face_detection.py" ]; then
    echo "❌ Main script not found: raspberry_pi_face_detection.py"
    exit 1
fi

# Make sure script is executable
chmod +x raspberry_pi_face_detection.py

echo "🚀 Launching face detection system..."
echo ""
echo "📋 Controls:"
echo "   - 'q' or ESC: Quit"
echo "   - 'r': Reset FPS counter"
echo "   - 'f': Toggle FPS display"
echo "   - 'd': Toggle detection info"
echo "   - 's': Toggle performance stats"
echo "   - 'c': Toggle confidence threshold"
echo "   - SPACE: Pause/Resume"
echo ""
echo "⚡ Performance Tips:"
echo "   - Lower camera resolution for better FPS"
echo "   - Increase frame skipping for less CPU usage"
echo "   - Adjust resize factor for speed vs accuracy"
echo ""

# Run the face detection system
python3 raspberry_pi_face_detection.py "$@"

echo ""
echo "👋 Face detection system stopped."

