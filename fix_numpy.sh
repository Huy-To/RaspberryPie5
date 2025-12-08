#!/bin/bash

# Fix script for numpy version incompatibility with picamera2
# ============================================================

echo "🔧 Fixing numpy version incompatibility with picamera2..."
echo "========================================================="

echo "📊 Checking current numpy installation..."
if python3 -c "import numpy; print(f'Current numpy: {numpy.__version__}')" 2>/dev/null; then
    NUMPY_VERSION=$(python3 -c "import numpy; print(numpy.__version__)" 2>/dev/null)
    echo "   Found numpy: $NUMPY_VERSION"
else
    echo "   No numpy found"
fi

echo ""
echo "🔍 Testing picamera2 import..."
if python3 -c "import numpy; import picamera2; print('✅ Compatible')" 2>/dev/null; then
    echo "✅ numpy and picamera2 are compatible!"
    echo "   No fix needed."
    exit 0
else
    echo "❌ Incompatibility detected!"
    echo ""
    echo "🔧 Attempting to fix..."
    echo ""
    
    # Check if system numpy exists
    if python3 -c "import sys; sys.path.insert(0, '/usr/lib/python3/dist-packages'); import numpy" 2>/dev/null; then
        echo "   Found system numpy - will use that instead"
    fi
    
    # Uninstall pip-installed numpy
    echo "   1. Uninstalling pip-installed numpy..."
    python3 -m pip uninstall -y numpy 2>/dev/null || echo "   (numpy not installed via pip)"
    
    # Test if system numpy works
    echo "   2. Testing system numpy..."
    if python3 -c "import numpy; import picamera2; print('✅ Fixed!')" 2>/dev/null; then
        echo "✅ Fixed! Now using system numpy"
        echo ""
        echo "You can now run: ./run.sh"
        exit 0
    else
        echo "❌ Still incompatible. Trying alternative fix..."
        echo ""
        echo "   3. Reinstalling compatible numpy version..."
        # Install a compatible numpy version
        python3 -m pip install --break-system-packages --no-warn-script-location "numpy<2.0" 2>/dev/null
        
        if python3 -c "import numpy; import picamera2; print('✅ Fixed!')" 2>/dev/null; then
            echo "✅ Fixed! Using numpy < 2.0"
            exit 0
        else
            echo "❌ Could not automatically fix"
            echo ""
            echo "Manual solutions:"
            echo "  1. Use system packages: sudo apt install -y python3-numpy python3-picamera2"
            echo "  2. Or downgrade numpy: python3 -m pip install --break-system-packages 'numpy<2.0'"
            exit 1
        fi
    fi
fi

