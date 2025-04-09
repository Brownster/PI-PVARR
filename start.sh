#!/bin/bash

# Pi-PVARR Main Starter Script

# Exit on error
set -euo pipefail

# Define colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${GREEN}Pi-PVARR Media Server${NC}"
echo "========================="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found.${NC}"
    echo "Would you like to set up Pi-PVARR now? (y/n)"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        # Run the installation script
        if [ -f "install.sh" ]; then
            echo "Running installation script..."
            ./install.sh
        else
            echo -e "${RED}Error: Installation script not found.${NC}"
            exit 1
        fi
    else
        echo "Installation aborted."
        exit 0
    fi
fi

# Activation virtual environment
source venv/bin/activate

# Display menu
echo "Please select an option:"
echo "1. Start the web UI"
echo "2. Start the API server only"
echo "3. Start the setup wizard"
echo "4. Update Pi-PVARR"
echo "5. Exit"
echo
echo -n "Enter your choice [1-5]: "
read -r choice

case $choice in
    1)
        echo -e "${GREEN}Starting the web UI...${NC}"
        ./start-web.sh
        ;;
    2)
        echo -e "${GREEN}Starting the API server...${NC}"
        ./start-api.sh
        ;;
    3)
        echo -e "${GREEN}Starting the setup wizard...${NC}"
        python -m src.setup
        ;;
    4)
        echo -e "${GREEN}Updating Pi-PVARR...${NC}"
        git pull
        pip install -r requirements.txt
        echo -e "${GREEN}Update completed.${NC}"
        ;;
    5)
        echo "Exiting."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option. Please try again.${NC}"
        exit 1
        ;;
esac