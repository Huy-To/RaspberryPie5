#!/bin/bash

# Main Run Script - Raspberry Pi 5 Face Detection System
# ======================================================
# This script runs the face detection system from the project root

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the main script
exec "$PROJECT_ROOT/scripts/run.sh" "$@"

