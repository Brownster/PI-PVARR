#!/bin/bash

# Pi-PVARR Web UI server starter

# Exit on error
set -euo pipefail

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start API server in the background
echo "Starting API server in the background..."
python -m src.api.server &
API_PID=$!

# Trap SIGINT and SIGTERM to kill the API server when the script exits
trap "kill $API_PID 2>/dev/null || true" INT TERM EXIT

# Print instructions
echo "Web UI server started at http://localhost:8080"
echo "Press Ctrl+C to stop the server"

# Keep the script running
wait $API_PID