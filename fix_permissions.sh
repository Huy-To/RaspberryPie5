#!/bin/bash

# Fix Script Permissions
# ======================
# Makes all scripts executable after pulling from GitHub
# Git doesn't preserve executable permissions, so run this after every pull

echo "🔧 Fixing script permissions..."
echo "================================"

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT" || exit 1

# Counter for files fixed
FIXED_COUNT=0

# Make all .sh files executable (recursive)
echo "📝 Making all .sh files executable..."
while IFS= read -r -d '' file; do
    if [ ! -x "$file" ]; then
        chmod +x "$file"
        echo "   ✅ Made executable: $file"
        ((FIXED_COUNT++))
    fi
done < <(find . -type f -name "*.sh" -not -path "./.git/*" -print0)

# Make all .py files executable (recursive)
echo "🐍 Making all .py files executable..."
while IFS= read -r -d '' file; do
    if [ ! -x "$file" ]; then
        chmod +x "$file"
        echo "   ✅ Made executable: $file"
        ((FIXED_COUNT++))
    fi
done < <(find . -type f -name "*.py" -not -path "./.git/*" -not -path "./__pycache__/*" -print0)

# Make this script itself executable
chmod +x "$0" 2>/dev/null || true

echo ""
echo "✅ Fixed permissions for $FIXED_COUNT file(s)"
echo ""
echo "📋 You can now run:"
echo "  ./run.sh          - Start face detection"
echo "  ./run_api.sh      - Start API server"
echo "  ./run_enroll.sh   - Enroll faces"
echo "  ./fix_permissions.sh - Fix permissions (this script)"
echo ""
echo "💡 Tip: Run this script after every 'git pull'"

