#!/bin/bash

# Fix script for libcap-dev installation issues
# =============================================

echo "🔧 Fixing libcap-dev installation for picamera2..."
echo "=================================================="

# Update package list
echo "📦 Updating package list..."
sudo apt update

# Try to install libcap-dev
echo "🔧 Attempting to install libcap-dev..."
LIBCAP_INSTALLED=false

for pkg in libcap-dev libcap2-dev libcap2; do
    echo "   Trying: $pkg"
    if sudo apt install -y "$pkg" 2>&1 | grep -q "Setting up\|is already"; then
        echo "✅ Successfully installed: $pkg"
        LIBCAP_INSTALLED=true
        break
    fi
done

if [ "$LIBCAP_INSTALLED" = false ]; then
    echo ""
    echo "❌ Could not install libcap-dev using standard packages"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check available packages:"
    echo "   apt-cache search libcap"
    echo ""
    echo "2. Try installing build-essential first:"
    echo "   sudo apt install -y build-essential"
    echo "   sudo apt install -y libcap-dev"
    echo ""
    echo "3. Check your Raspberry Pi OS version:"
    echo "   cat /etc/os-release"
    echo ""
    echo "4. You may need to update your system:"
    echo "   sudo apt update && sudo apt upgrade"
    echo ""
    exit 1
fi

# Now try to install picamera2
echo ""
echo "📦 Installing picamera2..."
if [ -d "face_detection_env" ]; then
    source face_detection_env/bin/activate
fi

if pip install --no-cache-dir picamera2; then
    echo "✅ picamera2 installed successfully!"
    echo ""
    echo "You can now run: ./setup.sh (or continue with existing setup)"
else
    echo "❌ picamera2 installation still failed"
    echo "   Check the error messages above"
    exit 1
fi

