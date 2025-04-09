#!/bin/bash

# Pi-PVARR API server starter

# Exit on error
set -euo pipefail

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the API server
python -m src.api.server