#!/bin/bash

# Fix Script Permissions
# ======================
# Makes all scripts executable

echo "🔧 Fixing script permissions..."

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT" || exit 1

# Make all scripts executable
chmod +x run.sh run_api.sh run_enroll.sh
chmod +x scripts/*.sh
chmod +x src/*.py

echo "✅ All scripts are now executable"
echo ""
echo "You can now run:"
echo "  ./run.sh          - Start face detection"
echo "  ./run_api.sh      - Start API server"
echo "  ./run_enroll.sh   - Enroll faces"

