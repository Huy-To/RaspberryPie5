#!/bin/bash

# API Server Run Script - Raspberry Pi 5 Face Detection System
# ============================================================

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Starting API Server..."
echo "========================"

# Check if API server script exists
API_SCRIPT="$PROJECT_ROOT/src/api_server.py"
if [ ! -f "$API_SCRIPT" ]; then
    echo "❌ API server script not found: $API_SCRIPT"
    exit 1
fi

# Make sure script is executable
chmod +x "$API_SCRIPT"

# Run the API server
python3 "$API_SCRIPT" "$@"

echo ""
echo "👋 API server stopped."

