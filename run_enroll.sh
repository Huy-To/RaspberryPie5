#!/bin/bash

# Face Enrollment Run Script - Raspberry Pi 5 Face Detection System
# ================================================================

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "👤 Face Enrollment System"
echo "========================"

# Check if enrollment script exists
ENROLL_SCRIPT="$PROJECT_ROOT/src/enroll_face.py"
if [ ! -f "$ENROLL_SCRIPT" ]; then
    echo "❌ Enrollment script not found: $ENROLL_SCRIPT"
    exit 1
fi

# Make sure script is executable
chmod +x "$ENROLL_SCRIPT"

# Check dependencies
echo "🔍 Checking dependencies..."

# Check face_recognition
if ! python3 -c "import face_recognition" 2>/dev/null; then
    echo "❌ face_recognition not installed"
    echo "   Install with: python3 -m pip install --break-system-packages face_recognition"
    echo "   Or run: ./scripts/setup.sh"
    exit 1
fi

# Check imageio
if ! python3 -c "import imageio" 2>/dev/null; then
    echo "❌ imageio not installed"
    echo "   Install with: python3 -m pip install --break-system-packages imageio imageio-ffmpeg"
    echo "   Or run: ./scripts/setup.sh"
    exit 1
fi

# Check ffmpeg (required for imageio video processing)
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  Warning: ffmpeg not found"
    echo "   Video processing may fail. Install with: sudo apt install -y ffmpeg"
    echo "   Continuing anyway..."
fi

echo "✅ Dependencies OK"
echo ""

# Run the enrollment script
python3 "$ENROLL_SCRIPT" "$@"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✅ Enrollment completed successfully."
else
    echo ""
    echo "❌ Enrollment failed with exit code $EXIT_CODE"
    echo "   Check error messages above for details"
    exit $EXIT_CODE
fi

