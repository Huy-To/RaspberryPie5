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

# Check for webhook URL in environment or config
if [ -z "$N8N_WEBHOOK_URL" ]; then
    echo "ℹ️  Tip: Set N8N_WEBHOOK_URL environment variable or use --webhook-url argument"
    echo "   Example: N8N_WEBHOOK_URL='http://n8n.local:5678/webhook/id' ./run_api.sh"
    echo "   Or: ./run_api.sh --webhook-url 'http://n8n.local:5678/webhook/id'"
    echo ""
fi

# Run the API server
python3 "$API_SCRIPT" "$@"

echo ""
echo "👋 API server stopped."

