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

# Run the enrollment script
python3 "$ENROLL_SCRIPT" "$@"

echo ""
echo "👋 Enrollment completed."

