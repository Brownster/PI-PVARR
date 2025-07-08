#!/bin/bash
# wait-for-mounts.sh - Script to wait for critical mounts before starting Docker
# This script is installed by the Pi-PVARR installer when critical storage is configured

# Load mount points from configuration file
CONFIG_FILE="/opt/pi-pvarr/config/critical-mounts.conf"
TIMEOUT=300  # 5 minutes timeout
LOG_FILE="/var/log/pi-pvarr/mount-check.log"
WEB_UI_PATH="/opt/pi-pvarr/web-ui"
API_PATH="/opt/pi-pvarr/api"
PID_DIR="/var/run/pi-pvarr"

# Make sure log directory exists
mkdir -p "$(dirname $LOG_FILE)"
mkdir -p "$PID_DIR"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log "Starting mount check script"

# Start the Pi-PVARR Web UI first for monitoring
start_web_ui() {
    log "Starting Pi-PVARR Web UI for monitoring"
    if [ -f "$WEB_UI_PATH/server.js" ]; then
        if [ -f "$PID_DIR/web-ui.pid" ]; then
            local old_pid=$(cat "$PID_DIR/web-ui.pid")
            if kill -0 $old_pid 2>/dev/null; then
                log "Web UI is already running (PID: $old_pid)"
                return
            else
                log "Removing stale PID file"
                rm -f "$PID_DIR/web-ui.pid"
            fi
        fi
        
        cd "$WEB_UI_PATH"
        if command -v node &>/dev/null; then
            nohup node server.js > /var/log/pi-pvarr/web-ui.log 2>&1 &
            echo $! > "$PID_DIR/web-ui.pid"
            log "Started Pi-PVARR Web UI (PID: $!)"
        else
            log "Node.js not found, can't start Web UI"
        fi
    else
        log "Web UI not found at $WEB_UI_PATH/server.js"
    fi
}

# Start the Pi-PVARR API for status information
start_api() {
    log "Starting Pi-PVARR API for monitoring"
    if [ -f "$API_PATH/server.py" ]; then
        if [ -f "$PID_DIR/api.pid" ]; then
            local old_pid=$(cat "$PID_DIR/api.pid")
            if kill -0 $old_pid 2>/dev/null; then
                log "API is already running (PID: $old_pid)"
                return
            else
                log "Removing stale PID file"
                rm -f "$PID_DIR/api.pid"
            fi
        fi
        
        cd "$API_PATH"
        if command -v python3 &>/dev/null; then
            nohup python3 server.py > /var/log/pi-pvarr/api.log 2>&1 &
            echo $! > "$PID_DIR/api.pid"
            log "Started Pi-PVARR API (PID: $!)"
        else
            log "Python3 not found, can't start API"
        fi
    else
        log "API not found at $API_PATH/server.py"
    fi
}

# Start monitoring services first
start_web_ui
start_api

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    log "No critical mounts configuration found. Exiting."
    exit 0
fi

# Read mount points from config file
readarray -t MOUNT_POINTS < "$CONFIG_FILE"

if [ ${#MOUNT_POINTS[@]} -eq 0 ]; then
    log "No critical mount points specified. Exiting."
    exit 0
fi

log "Waiting for ${#MOUNT_POINTS[@]} critical mount points..."

# Function to check if all mount points are available
check_mounts() {
    local all_mounted=true
    local mounted_count=0
    
    for mount in "${MOUNT_POINTS[@]}"; do
        if mountpoint -q "$mount"; then
            mounted_count=$((mounted_count + 1))
            log "$mount is mounted"
        else
            all_mounted=false
            log "$mount is NOT mounted"
        fi
    done
    
    log "$mounted_count/${#MOUNT_POINTS[@]} mount points are ready"
    
    if $all_mounted; then
        return 0
    else
        return 1
    fi
}

# Try to mount from fstab in case some mounts aren't ready
mount -a
log "Executed 'mount -a' to ensure all fstab entries are mounted"

# Create a status file for the web UI to read
STATUS_FILE="/var/run/pi-pvarr/mount-status.json"

update_status_file() {
    local status="$1"
    local message="$2"
    local progress="$3"
    local elapsed="$4"
    
    cat > "$STATUS_FILE" <<EOF
{
    "status": "$status",
    "message": "$message",
    "progress": $progress,
    "elapsed": $elapsed,
    "timestamp": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF
    log "Updated status file: $status - $message"
}

# Initial status
update_status_file "checking" "Checking for critical mounts..." 0 0

# Wait for all mount points to be available with timeout
start_time=$(date +%s)
while ! check_mounts; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))
    
    # Calculate progress percentage (0-100)
    progress=$((elapsed * 100 / TIMEOUT))
    if [ $progress -gt 100 ]; then
        progress=100
    fi
    
    # Update status file for web UI
    update_status_file "waiting" "Waiting for mount points..." $progress $elapsed
    
    if [ $elapsed -gt $TIMEOUT ]; then
        log "Timeout waiting for mount points after $TIMEOUT seconds"
        log "WARNING: Starting services with missing mounts may cause issues!"
        
        # Update status file with warning for web UI
        update_status_file "warning" "Mount timeout! Services may not function correctly." 100 $elapsed
        
        # Alert user via system notification if possible
        if command -v notify-send &> /dev/null; then
            notify-send -u critical "Pi-PVARR Mount Warning" "Some critical storage mounts are not available. Services may not function correctly."
        fi
        
        # Give user a choice if this is an interactive session
        if tty -s; then
            read -p "Continue anyway? (y/n): " choice
            if [[ "$choice" != "y" && "$choice" != "Y" ]]; then
                log "User aborted startup due to missing mounts"
                update_status_file "error" "User aborted startup due to missing mounts" 100 $elapsed
                exit 1
            fi
        fi
        
        break
    fi
    
    log "Waiting for mount points... ($elapsed seconds elapsed, timeout: $TIMEOUT)"
    sleep 5
done

# Update status file with success
update_status_file "success" "All critical mounts are available" 100 $elapsed

# Start Docker if it's not already running
if ! systemctl is-active --quiet docker; then
    log "Starting Docker service..."
    update_status_file "starting" "Starting Docker service..." 0 0
    systemctl start docker
    
    # Wait for Docker to be up
    DOCKER_TIMEOUT=60
    docker_start_time=$(date +%s)
    while ! docker info &>/dev/null; do
        docker_current_time=$(date +%s)
        docker_elapsed=$((docker_current_time - docker_start_time))
        
        # Calculate progress
        docker_progress=$((docker_elapsed * 100 / DOCKER_TIMEOUT))
        if [ $docker_progress -gt 100 ]; then
            docker_progress=100
        fi
        
        update_status_file "starting_docker" "Starting Docker service..." $docker_progress $docker_elapsed
        
        if [ $docker_elapsed -gt $DOCKER_TIMEOUT ]; then
            log "Timeout waiting for Docker to start"
            update_status_file "error" "Timeout waiting for Docker to start" 100 $docker_elapsed
            exit 1
        fi
        
        log "Waiting for Docker to start... ($docker_elapsed seconds elapsed)"
        sleep 2
    done
    
    log "Docker service started successfully"
    update_status_file "docker_ready" "Docker service started successfully" 100 $docker_elapsed
fi

# Start Pi-PVARR services
log "Starting Pi-PVARR services..."
update_status_file "starting_services" "Starting Pi-PVARR services..." 0 0

if [ -f "/opt/pi-pvarr/docker/docker-compose.yml" ]; then
    cd /opt/pi-pvarr/docker
    
    # Determine whether to use docker-compose or docker compose
    if docker compose version &>/dev/null; then
        docker compose up -d
        startup_result=$?
    elif command -v docker-compose &>/dev/null; then
        docker-compose up -d
        startup_result=$?
    else
        log "Error: Neither docker compose nor docker-compose is available"
        update_status_file "error" "Docker Compose not available" 100 0
        exit 1
    fi
    
    if [ $startup_result -eq 0 ]; then
        log "Pi-PVARR services started successfully"
        update_status_file "services_running" "All services started successfully" 100 0
    else
        log "Error starting Pi-PVARR services"
        update_status_file "error" "Error starting Pi-PVARR services" 100 0
    fi
else
    log "Warning: Docker compose file not found at /opt/pi-pvarr/docker/docker-compose.yml"
    update_status_file "warning" "Docker compose file not found" 100 0
fi

# Create a system status file for the dashboard
SYSTEM_STATUS_FILE="/var/run/pi-pvarr/system-status.json"
cat > "$SYSTEM_STATUS_FILE" <<EOF
{
    "status": "running",
    "last_boot": "$(date '+%Y-%m-%d %H:%M:%S')",
    "boot_count": "$(cat /var/run/pi-pvarr/boot-count 2>/dev/null || echo 1)",
    "mount_status": "$(cat $STATUS_FILE | grep status | cut -d'"' -f4)",
    "docker_status": "$(systemctl is-active docker || echo 'inactive')",
    "containers_running": "$(docker ps -q 2>/dev/null | wc -l)",
    "timestamp": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF

# Increment boot count
boot_count=$(cat /var/run/pi-pvarr/boot-count 2>/dev/null || echo 0)
echo $((boot_count + 1)) > /var/run/pi-pvarr/boot-count

log "Mount check script completed"
update_status_file "completed" "System startup complete" 100 0exit 0
