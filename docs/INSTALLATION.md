# Pi-PVARR Installation Guide

This guide provides detailed instructions for installing the Pi-PVARR Media Server.

## System Requirements

- **Supported Platforms**:
  - Raspberry Pi 4 (2GB RAM minimum, 4GB+ recommended)
  - Raspberry Pi 5
  - Any Linux-based system (Debian/Ubuntu recommended)

- **Hardware Requirements**:
  - 2GB RAM minimum (4GB+ recommended)
  - 16GB storage for the system (SSD recommended)
  - External storage for media files
  - Internet connection

- **Software Requirements**:
  - Python 3.8 or newer
  - Docker and Docker Compose (installed automatically)

## Installation Methods

### Method 1: Automatic Installation

The easiest way to install Pi-PVARR is to use the automatic installation script:

```bash
# Clone the repository
git clone https://github.com/username/Pi-PVARR.git
cd Pi-PVARR

# Make the installation script executable
chmod +x install.sh

# Run the installation script
./install.sh
```

The script will:
1. Check system requirements
2. Install Python dependencies
3. Install Docker if not already installed
4. Set up initial configuration
5. Create startup scripts

### Method 2: Manual Installation

If you prefer a manual installation, follow these steps:

#### 1. Clone the Repository

```bash
git clone https://github.com/username/Pi-PVARR.git
cd Pi-PVARR
```

#### 2. Create a Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Install Docker (if not already installed)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
```

#### 5. Set Up Initial Configuration

```bash
python -c "from src.core.config import get_config, save_config_wrapper, get_services_config, save_services_config; save_config_wrapper(get_config()); save_services_config(get_services_config())"
```

#### 6. Make Startup Scripts Executable

```bash
chmod +x start-api.sh start-web.sh
```

## Post-Installation

### Start the Web UI

```bash
./start-web.sh
```

Access the web UI at:

```
http://your-server-ip:8080
```

### First-Time Setup

When you first access the web UI, you'll be guided through a setup wizard that will help you configure:

1. System settings (user/group IDs, timezone)
2. Storage locations (media and downloads directories)
3. Network settings (VPN and Tailscale configuration)
4. Services selection (media management, download clients, media servers)

## Installation on a Raspberry Pi

### Recommended Raspbian Setup

1. Start with a fresh install of Raspberry Pi OS (64-bit recommended)
2. Perform system updates:

```bash
sudo apt update
sudo apt upgrade -y
```

3. Install required packages:

```bash
sudo apt install -y python3-venv git
```

4. Follow the automatic or manual installation method above

### USB Boot Considerations

For better performance, consider:
- Booting from a USB SSD rather than SD card
- Storing your media on external USB drives formatted with ext4

## Docker Configuration

The Pi-PVARR installation automatically manages Docker, but if you want to customize the Docker configuration:

### Container Storage Location

By default, Docker container data is stored in:

```
~/docker
```

You can modify this location in the configuration settings.

### Default Container Networks

Pi-PVARR creates the following Docker networks:
- `vpn_network`: For containers that should route through the VPN
- `host_network`: For containers that should use the host network directly

## Troubleshooting

### Installation Issues

If the installation fails:

1. Check the logs:

```bash
cat install.log
```

2. Verify Python version:

```bash
python3 --version
```

3. Check Docker installation:

```bash
docker --version
docker-compose --version
```

### Web UI Access Issues

If you can't access the web UI:

1. Verify the server is running:

```bash
ps aux | grep python
```

2. Check for any port conflicts:

```bash
netstat -tuln | grep 8080
```

3. Check firewall settings:

```bash
sudo ufw status
```

### Docker Issues

If containers fail to start:

1. Check Docker status:

```bash
systemctl status docker
```

2. Verify Docker permissions:

```bash
groups $USER
```

3. Restart Docker:

```bash
sudo systemctl restart docker
```