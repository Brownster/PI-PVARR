#!/bin/bash

# Pi-PVARR installation script
# This script installs the Pi-PVARR media server stack

# Exit on error
set -euo pipefail

# Define colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log file
LOG_FILE="./install.log"

# Functions
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} - $1" | tee -a "${LOG_FILE}"
}

log_info() {
    log "${BLUE}INFO${NC} - $1"
}

log_success() {
    log "${GREEN}SUCCESS${NC} - $1"
}

log_warning() {
    log "${YELLOW}WARNING${NC} - $1"
}

log_error() {
    log "${RED}ERROR${NC} - $1"
}

# Check if script is run as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
}

# Check system requirements
check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_info "Python version: ${PYTHON_VERSION}"
        
        if [[ $(echo "${PYTHON_VERSION}" | cut -d'.' -f1) -lt 3 ]] || [[ $(echo "${PYTHON_VERSION}" | cut -d'.' -f2) -lt 8 ]]; then
            log_error "Python 3.8 or higher is required"
            exit 1
        fi
    else
        log_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check if Docker is installed
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | tr -d ',')
        log_info "Docker version: ${DOCKER_VERSION}"
    else
        log_warning "Docker is not installed, will be installed during setup"
    fi
    
    # Check if Docker Compose is installed
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | tr -d ',')
        log_info "Docker Compose version: ${DOCKER_COMPOSE_VERSION}"
    else
        log_warning "Docker Compose is not installed, will be installed during setup"
    fi
    
    log_success "System requirements check completed"
}

# Create a Python virtual environment
create_virtualenv() {
    log_info "Creating Python virtual environment..."
    
    if ! command -v python3 -m venv &> /dev/null; then
        log_warning "Python venv not installed, trying to install..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y python3-venv python3-dev gcc
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-venv python3-devel gcc
        else
            log_error "Cannot install python3-venv, please install it manually"
            exit 1
        fi
    else
        # Ensure Python dev headers are installed for module compilation
        if command -v apt-get &> /dev/null; then
            log_info "Installing Python development headers required for some modules..."
            sudo apt-get update
            sudo apt-get install -y python3-dev gcc
        elif command -v yum &> /dev/null; then
            log_info "Installing Python development headers required for some modules..."
            sudo yum install -y python3-devel gcc
        fi
    fi
    
    # Create virtual environment
    python3 -m venv venv
    log_success "Virtual environment created"
}

# Install Python dependencies
install_python_dependencies() {
    log_info "Installing Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_success "Python dependencies installed"
}

# Install Docker if not already installed
install_docker() {
    if ! command -v docker &> /dev/null; then
        log_info "Installing Docker..."
        
        # Download Docker installation script
        curl -fsSL https://get.docker.com -o get-docker.sh
        
        # Run the Docker installation script
        chmod +x get-docker.sh
        sh get-docker.sh
        
        # Add current user to the Docker group
        sudo usermod -aG docker "$(whoami)"
        
        # Clean up
        rm get-docker.sh
        
        log_success "Docker installed"
        log_warning "You may need to log out and log back in for the Docker group changes to take effect"
    else
        log_info "Docker is already installed"
    fi
}

# Setup initial configuration
setup_configuration() {
    log_info "Setting up initial configuration..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run initial setup
    python -c "from src.core.config import get_config, save_config_wrapper, get_services_config, save_services_config; save_config_wrapper(get_config()); save_services_config(get_services_config())"
    
    log_success "Initial configuration set up"
}

# Create startup scripts
create_startup_scripts() {
    log_info "Creating startup scripts..."
    
    # Create start.sh script
    cat > start.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Activate virtual environment
source venv/bin/activate

# Start the Pi-PVARR API server
python -m src.api.server
EOF
    
    # Make it executable
    chmod +x start.sh
    
    log_success "Startup scripts created"
}

# Main installation process
main() {
    echo -e "${GREEN}Pi-PVARR Installation${NC}"
    echo "==============================="
    
    # Start clean log file
    > "${LOG_FILE}"
    
    # Check requirements
    check_root
    check_system_requirements
    
    # Create virtual environment
    create_virtualenv
    
    # Install dependencies
    install_python_dependencies
    
    # Install Docker if needed
    install_docker
    
    # Setup configuration
    setup_configuration
    
    # Create startup scripts
    create_startup_scripts
    
    echo -e "${GREEN}Installation completed successfully!${NC}"
    echo "To start Pi-PVARR, run: ./start.sh"
    log_success "Installation completed"
}

# Run the main function
main