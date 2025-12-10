#!/bin/bash

# Setup Git Hooks for Automatic Permission Fixing
# ===============================================
# This script sets up git hooks to automatically fix permissions after git pull

echo "🔧 Setting up Git hooks for automatic permission fixing..."
echo "=========================================================="

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT" || exit 1

# Check if .git directory exists
if [ ! -d ".git" ]; then
    echo "❌ Error: .git directory not found. Are you in a git repository?"
    exit 1
fi

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Create post-merge hook
cat > .git/hooks/post-merge << 'HOOK_EOF'
#!/bin/bash

# Git Post-Merge Hook
# Automatically fixes script permissions after git pull/merge

# Get project root (parent of .git directory)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 0

# Run fix_permissions.sh if it exists
if [ -f "$PROJECT_ROOT/fix_permissions.sh" ]; then
    echo ""
    echo "🔧 Auto-fixing script permissions after git pull..."
    bash "$PROJECT_ROOT/fix_permissions.sh"
fi

exit 0
HOOK_EOF

# Create post-checkout hook
cat > .git/hooks/post-checkout << 'HOOK_EOF'
#!/bin/bash

# Git Post-Checkout Hook
# Automatically fixes script permissions after git checkout

# Get project root (parent of .git directory)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT" || exit 0

# Run fix_permissions.sh if it exists
if [ -f "$PROJECT_ROOT/fix_permissions.sh" ]; then
    echo ""
    echo "🔧 Auto-fixing script permissions after git checkout..."
    bash "$PROJECT_ROOT/fix_permissions.sh"
fi

exit 0
HOOK_EOF

# Make hooks executable
chmod +x .git/hooks/post-merge
chmod +x .git/hooks/post-checkout

# Make fix_permissions.sh executable
chmod +x fix_permissions.sh

echo ""
echo "✅ Git hooks installed successfully!"
echo ""
echo "📋 What happens now:"
echo "   - After every 'git pull', permissions will be fixed automatically"
echo "   - After every 'git checkout', permissions will be fixed automatically"
echo ""
echo "🧪 Test it:"
echo "   git pull"
echo "   # You should see: '🔧 Auto-fixing script permissions after git pull...'"
echo ""
echo "💡 To disable automatic fixing, remove the hooks:"
echo "   rm .git/hooks/post-merge .git/hooks/post-checkout"

