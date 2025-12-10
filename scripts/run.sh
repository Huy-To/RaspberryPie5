#!/bin/bash

# Raspberry Pi 5 Face Detection System Run Script
# ===============================================
# Updated for organized folder structure

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "🎬 Starting Raspberry Pi 5 Face Detection System..."
echo "================================================="

# Verify picamera2 is installed (REQUIRED)
echo "🔍 Checking picamera2 installation..."
if python3 -c "from picamera2 import Picamera2" 2>/dev/null; then
    echo "✅ picamera2 is installed and working"
elif python3 -c "import picamera2" 2>/dev/null; then
    echo "✅ picamera2 is available (system package)"
elif python3 -m pip show picamera2 &>/dev/null || dpkg -l | grep -q python3-picamera2; then
    echo "✅ picamera2 is installed (detected via package manager)"
    echo "   Continuing - import will be tested when script runs"
else
    echo "⚠️  picamera2 not detected via standard checks"
    echo "   If it works in other programs (like Geany), it should work here"
    echo "   Continuing anyway - the script will test import on startup"
fi

# Check if model file exists
MODEL_PATH="$PROJECT_ROOT/models/yolov12n-face.pt"
if [ ! -f "$MODEL_PATH" ]; then
    echo "❌ YOLO model file not found: $MODEL_PATH"
    echo "   Please ensure the model file is in the models/ directory."
    exit 1
fi

# Check if main script exists
MAIN_SCRIPT="$PROJECT_ROOT/src/raspberry_pi_face_detection.py"
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo "❌ Main script not found: $MAIN_SCRIPT"
    exit 1
fi

# Make sure script is executable
chmod +x "$MAIN_SCRIPT"

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
python3 "$MAIN_SCRIPT" "$@"

echo ""
echo "👋 Face detection system stopped."
