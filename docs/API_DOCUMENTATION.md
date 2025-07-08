# Pi-PVARR API Documentation

*Last Updated: August 4, 2025*

## Overview

This document provides comprehensive documentation for the Pi-PVARR RESTful API. The API allows for management of:

- System information
- Configuration settings
- Docker containers
- Storage and file systems
- Network interfaces and VPN
- Service management and deployment
- Installation wizard for setup automation

## Base URL

All API endpoints are relative to:

```
http://<host>:8080/api
```

Where `<host>` is the hostname or IP address of the Pi-PVARR server.

## Authentication

Currently, the API does not require authentication. Future versions may implement authentication mechanisms.

## Endpoints

### System Information

#### Get System Information

```
GET /system
```

Returns comprehensive information about the system, including:
- Hostname
- Operating system details
- Memory usage
- Disk usage
- CPU information
- Temperature
- Raspberry Pi detection
- Docker installation status
- Network information

**Response Example:**

```json
{
  "hostname": "raspberrypi",
  "platform": "linux",
  "platform_version": "5.10.0",
  "os": {
    "name": "linux",
    "release": "5.10.0",
    "version": "#1 SMP Debian 5.10.0-18",
    "pretty_name": "Debian GNU/Linux 11"
  },
  "architecture": "aarch64",
  "memory_total": 4294967296,
  "memory_available": 2147483648,
  "memory_used": 2147483648,
  "memory_percent": 50.0,
  "disk_total": 34359738368,
  "disk_free": 21474836480,
  "disk_used": 12884901888,
  "disk_percent": 37.5,
  "cpu": {
    "model": "ARMv8",
    "cores": 4,
    "percent": 15.5
  },
  "temperature_celsius": 45.2,
  "raspberry_pi": {
    "is_raspberry_pi": true,
    "model": "Raspberry Pi 4 Model B Rev 1.4"
  },
  "docker_installed": true,
  "tailscale_installed": true,
  "network": {
    "interfaces": {
      "eth0": {
        "addresses": [
          {
            "address": "192.168.1.100",
            "netmask": "255.255.255.0",
            "broadcast": "192.168.1.255"
          }
        ],
        "mac": "00:11:22:33:44:55",
        "type": "ethernet"
      }
    }
  }
}
```

### Configuration

#### Get Configuration

```
GET /config
```

Returns the current configuration settings.

**Response Example:**

```json
{
  "puid": 1000,
  "pgid": 1000,
  "timezone": "UTC",
  "media_dir": "/mnt/media",
  "downloads_dir": "/mnt/downloads",
  "docker_dir": "/home/pi/docker",
  "vpn": {
    "enabled": true,
    "provider": "private internet access",
    "username": "user",
    "password": "pass",
    "region": "Netherlands"
  },
  "tailscale": {
    "enabled": false,
    "auth_key": ""
  },
  "installation_status": "not_started"
}
```

#### Update Configuration

```
POST /config
```

Updates the configuration settings.

**Request Body Example:**

```json
{
  "puid": 1000,
  "pgid": 1000,
  "timezone": "Europe/London",
  "media_dir": "/mnt/media",
  "downloads_dir": "/mnt/downloads",
  "docker_dir": "/home/pi/docker",
  "vpn": {
    "enabled": true,
    "provider": "private internet access",
    "username": "user",
    "password": "pass",
    "region": "Netherlands"
  },
  "tailscale": {
    "enabled": false,
    "auth_key": ""
  }
}
```

**Response Example:**

```json
{
  "status": "success"
}
```

#### Get Services Configuration

```
GET /services
```

Returns the current services configuration.

**Response Example:**

```json
{
  "arr_apps": {
    "sonarr": true,
    "radarr": true,
    "prowlarr": true,
    "lidarr": false,
    "readarr": false,
    "bazarr": false
  },
  "download_clients": {
    "transmission": true,
    "qbittorrent": false,
    "nzbget": true,
    "sabnzbd": false,
    "jdownloader": false
  },
  "media_servers": {
    "jellyfin": true,
    "plex": false,
    "emby": false
  },
  "utilities": {
    "heimdall": false,
    "overseerr": false,
    "tautulli": false,
    "portainer": true,
    "nginx_proxy_manager": false,
    "get_iplayer": true
  }
}
```

#### Update Services Configuration

```
POST /services
```

Updates the services configuration.

**Request Body Example:**

```json
{
  "arr_apps": {
    "sonarr": true,
    "radarr": true,
    "prowlarr": true,
    "lidarr": true,
    "readarr": false,
    "bazarr": true
  },
  "download_clients": {
    "transmission": true,
    "qbittorrent": false,
    "nzbget": true,
    "sabnzbd": false,
    "jdownloader": false
  },
  "media_servers": {
    "jellyfin": true,
    "plex": false,
    "emby": false
  },
  "utilities": {
    "heimdall": true,
    "overseerr": true,
    "tautulli": false,
    "portainer": true,
    "nginx_proxy_manager": false,
    "get_iplayer": true
  }
}
```

**Response Example:**

```json
{
  "status": "success"
}
```

### Docker Containers

#### Get Container Status

```
GET /containers
```

Returns the status of all Docker containers.

**Response Example:**

```json
{
  "sonarr": {
    "status": "running",
    "ports": [
      {
        "container": "8989",
        "host": "8989",
        "protocol": "tcp"
      }
    ],
    "type": "media",
    "description": "TV Series Management",
    "url": "http://localhost:8989"
  },
  "radarr": {
    "status": "running",
    "ports": [
      {
        "container": "7878",
        "host": "7878",
        "protocol": "tcp"
      }
    ],
    "type": "media",
    "description": "Movie Management",
    "url": "http://localhost:7878"
  }
}
```

#### Get Container Information

```
GET /containers/{container_name}
```

Returns detailed information about a specific container.

**Response Example:**

```json
{
  "name": "sonarr",
  "status": "running",
  "image": "linuxserver/sonarr:latest",
  "created": "2023-01-01T00:00:00.000000000Z",
  "ports": [
    {
      "container": "8989",
      "host": "8989",
      "protocol": "tcp"
    }
  ],
  "volumes": [
    "/home/pi/docker/sonarr/config:/config",
    "/mnt/media:/media"
  ],
  "environment": [
    "PUID=1000",
    "PGID=1000",
    "TZ=Europe/London"
  ],
  "labels": {
    "maintainer": "linuxserver.io"
  }
}
```

#### Get Container Logs

```
GET /containers/{container_name}/logs?lines=100
```

Returns logs for a specific container.

**Query Parameters:**

- `lines` (optional): Number of log lines to retrieve. Default is 100.

**Response Example:**

```json
{
  "container": "sonarr",
  "logs": "Log line 1\nLog line 2\nLog line 3"
}
```

#### Start Container

```
POST /containers/{container_name}/start
```

Starts a specific container.

**Response Example:**

```json
{
  "status": "success",
  "message": "Container sonarr started successfully"
}
```

#### Stop Container

```
POST /containers/{container_name}/stop
```

Stops a specific container.

**Response Example:**

```json
{
  "status": "success",
  "message": "Container sonarr stopped successfully"
}
```

#### Restart Container

```
POST /containers/{container_name}/restart
```

Restarts a specific container.

**Response Example:**

```json
{
  "status": "success",
  "message": "Container sonarr restarted successfully"
}
```

#### Update All Containers

```
POST /containers/update
```

Updates all containers by pulling their images and recreating them.

**Response Example:**

```json
{
  "status": "success",
  "message": "Update process completed",
  "details": [
    {
      "container": "sonarr",
      "status": "updated",
      "message": "Image pulled and container restarted"
    },
    {
      "container": "radarr",
      "status": "updated",
      "message": "Image pulled and container restarted"
    }
  ]
}
```

### Storage Management

#### Get Drives Information

```
GET /storage/drives
```

Returns information about all drives.

**Response Example:**

```json
{
  "drives": [
    {
      "device": "/dev/sda1",
      "mountpoint": "/mnt/media",
      "size": "2000G",
      "used": "500.0 GB",
      "available": "1.5 TB",
      "percent": 25,
      "fstype": "ext4",
      "is_usb": true,
      "label": "External Drive",
      "model": "SanDisk"
    },
    {
      "device": "/dev/sdb1",
      "mountpoint": "/mnt/downloads",
      "size": "1000G",
      "used": "300.0 GB",
      "available": "700.0 GB",
      "percent": 30,
      "fstype": "ext4",
      "is_usb": false,
      "label": "Internal Drive",
      "model": "WD"
    }
  ]
}
```

#### Get Media Paths

```
GET /storage/media/paths
```

Returns information about configured media paths.

**Response Example:**

```json
{
  "paths": {
    "movies": {
      "path": "/mnt/media/Movies",
      "exists": true
    },
    "tv": {
      "path": "/mnt/media/TV",
      "exists": true
    },
    "music": {
      "path": "/mnt/media/Music",
      "exists": false
    },
    "downloads": {
      "path": "/mnt/downloads",
      "exists": true
    },
    "completed": {
      "path": "/mnt/downloads/completed",
      "exists": true
    },
    "incomplete": {
      "path": "/mnt/downloads/incomplete",
      "exists": true
    }
  }
}
```

#### Get Mount Points

```
GET /storage/mounts
```

Returns information about mounted filesystems.

**Response Example:**

```json
[
  {
    "device": "/dev/sda1",
    "mountpoint": "/mnt/media",
    "fstype": "ext4"
  },
  {
    "device": "/dev/sdb1",
    "mountpoint": "/mnt/downloads",
    "fstype": "ext4"
  }
]
```

#### Mount Drive

```
POST /storage/mount
```

Mounts a drive.

**Request Body Example:**

```json
{
  "device": "/dev/sda1",
  "mountpoint": "/mnt/media",
  "fstype": "ext4"
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Device /dev/sda1 mounted to /mnt/media"
}
```

#### Unmount Drive

```
POST /storage/unmount
```

Unmounts a drive.

**Request Body Example:**

```json
{
  "mountpoint": "/mnt/media"
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Device unmounted from /mnt/media"
}
```

#### Get Directory Information

```
GET /storage/directory?path=/mnt/media/Movies
```

Returns information about a directory.

**Query Parameters:**

- `path`: The directory path.

**Response Example:**

```json
{
  "path": "/mnt/media/Movies",
  "size": "300.0 GB",
  "files": 150,
  "directories": 5,
  "usage": 30
}
```

#### Get Directories Information

```
POST /storage/directories
```

Returns information about multiple directories.

**Request Body Example:**

```json
{
  "paths": [
    "/mnt/media/Movies",
    "/mnt/media/TVShows",
    "/mnt/downloads"
  ]
}
```

**Response Example:**

```json
[
  {
    "path": "/mnt/media/Movies",
    "size": "300.0 GB",
    "files": 150,
    "directories": 5,
    "usage": 15
  },
  {
    "path": "/mnt/media/TVShows",
    "size": "200.0 GB",
    "files": 500,
    "directories": 20,
    "usage": 10
  },
  {
    "path": "/mnt/downloads",
    "size": "100.0 GB",
    "files": 25,
    "directories": 3,
    "usage": 5
  }
]
```

#### Create Directory

```
POST /storage/directory/create
```

Creates a directory.

**Request Body Example:**

```json
{
  "path": "/mnt/media/Movies/Action",
  "uid": 1000,
  "gid": 1000,
  "mode": 493
}
```

Note: `mode` is an octal value represented as decimal (e.g., 0o755 = 493).

**Response Example:**

```json
{
  "status": "success",
  "message": "Directory /mnt/media/Movies/Action created successfully"
}
```

#### Create Media Directories

```
POST /storage/media/create
```

Creates standard media directories (Movies, TVShows, Music, Books, Photos).

**Request Body Example:**

```json
{
  "base_dir": "/mnt/media",
  "uid": 1000,
  "gid": 1000
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Media directories created successfully",
  "details": [
    {
      "directory": "Movies",
      "status": "success",
      "message": "Directory Movies created"
    },
    {
      "directory": "TVShows",
      "status": "success",
      "message": "Directory TVShows created"
    }
  ]
}
```

#### Get Network Shares

```
GET /storage/shares
```

Returns information about network shares.

**Response Example:**

```json
[
  {
    "name": "Movies",
    "path": "/mnt/media/Movies",
    "public": false,
    "read_only": false,
    "valid_users": "user1"
  },
  {
    "name": "TVShows",
    "path": "/mnt/media/TVShows",
    "public": false,
    "read_only": false,
    "valid_users": "user1, user2"
  }
]
```

#### Add Network Share

```
POST /storage/shares/add
```

Adds a network share.

**Request Body Example:**

```json
{
  "name": "Music",
  "path": "/mnt/media/Music",
  "public": false,
  "read_only": false,
  "valid_users": "user1, user2"
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Share Music added successfully"
}
```

#### Remove Network Share

```
POST /storage/shares/remove
```

Removes a network share.

**Request Body Example:**

```json
{
  "name": "Music"
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Share Music removed successfully"
}
```

### Network Management

#### Get Network Interfaces

```
GET /network/interfaces
```

Returns information about network interfaces.

**Response Example:**

```json
{
  "status": "success",
  "interfaces": {
    "eth0": {
      "mac": "00:11:22:33:44:55",
      "up": true,
      "speed": 1000,
      "mtu": 1500,
      "type": "ethernet",
      "addresses": [
        {
          "address": "192.168.1.100",
          "netmask": "255.255.255.0",
          "broadcast": "192.168.1.255"
        }
      ]
    },
    "wlan0": {
      "mac": "AA:BB:CC:DD:EE:FF",
      "up": true,
      "speed": 100,
      "mtu": 1500,
      "type": "wireless",
      "addresses": [
        {
          "address": "192.168.1.101",
          "netmask": "255.255.255.0",
          "broadcast": "192.168.1.255"
        }
      ]
    }
  }
}
```

#### Get Network Information

```
GET /network/info
```

Returns comprehensive network information.

**Response Example:**

```json
{
  "interfaces": {
    "eth0": {
      "mac": "00:11:22:33:44:55",
      "up": true,
      "type": "ethernet",
      "addresses": [
        {
          "address": "192.168.1.100",
          "netmask": "255.255.255.0",
          "broadcast": "192.168.1.255"
        }
      ]
    }
  },
  "vpn": {
    "connected": true,
    "provider": "gluetun",
    "ip_address": "123.45.67.89",
    "location": "Amsterdam, NL"
  },
  "tailscale": {
    "installed": true,
    "running": true,
    "ip_address": "100.100.100.100",
    "hostname": "raspberrypi"
  }
}
```

#### Get VPN Status

```
GET /network/vpn/status
```

Returns VPN connection status.

**Response Example:**

```json
{
  "status": "success",
  "vpn": {
    "connected": true,
    "provider": "gluetun",
    "ip_address": "123.45.67.89",
    "location": "Amsterdam, NL"
  }
}
```

#### Configure VPN

```
POST /network/vpn/configure
```

Configures VPN settings.

**Request Body Example:**

```json
{
  "enabled": true,
  "provider": "private internet access",
  "username": "user",
  "password": "pass",
  "region": "Netherlands"
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "VPN configuration updated for provider private internet access",
  "details": {
    "provider": "private internet access",
    "region": "Netherlands",
    "credentials_set": true
  }
}
```

#### Get Tailscale Status

```
GET /network/tailscale/status
```

Returns Tailscale VPN status.

**Response Example:**

```json
{
  "status": "success",
  "tailscale": {
    "installed": true,
    "running": true,
    "ip_address": "100.100.100.100",
    "hostname": "raspberrypi"
  }
}
```

#### Configure Tailscale

```
POST /network/tailscale/configure
```

Configures Tailscale VPN.

**Request Body Example:**

```json
{
  "enabled": true,
  "auth_key": "tskey-abcdef123456"
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Tailscale configured and started"
}
```

### Service Management

#### Get Services Information

```
GET /services/info
```

Returns comprehensive information about all available services, including status, descriptions, and configuration.

**Response Example:**

```json
{
  "arr_apps": {
    "sonarr": {
      "name": "sonarr",
      "enabled": true,
      "description": "TV Series Management",
      "default_port": 8989,
      "docker_image": "linuxserver/sonarr:latest",
      "status": "running",
      "url": "http://localhost:8989",
      "ports": [
        {
          "container": "8989",
          "host": "8989",
          "protocol": "tcp"
        }
      ]
    },
    "radarr": {
      "name": "radarr",
      "enabled": true,
      "description": "Movie Management",
      "default_port": 7878,
      "docker_image": "linuxserver/radarr:latest",
      "status": "running",
      "url": "http://localhost:7878",
      "ports": [
        {
          "container": "7878",
          "host": "7878",
          "protocol": "tcp"
        }
      ]
    }
  },
  "download_clients": {
    "transmission": {
      "name": "transmission",
      "enabled": true,
      "description": "Torrent Client",
      "default_port": 9091,
      "docker_image": "linuxserver/transmission:latest",
      "status": "running",
      "url": "http://localhost:9091",
      "ports": [
        {
          "container": "9091",
          "host": "9091",
          "protocol": "tcp"
        }
      ]
    }
  },
  "media_servers": {
    "jellyfin": {
      "name": "jellyfin",
      "enabled": true,
      "description": "Media Server",
      "default_port": 8096,
      "docker_image": "linuxserver/jellyfin:latest",
      "status": "running",
      "url": "http://localhost:8096",
      "ports": [
        {
          "container": "8096",
          "host": "8096",
          "protocol": "tcp"
        }
      ]
    }
  }
}
```

#### Toggle Service Enabled State

```
POST /services/toggle
```

Enable or disable a specific service in the configuration.

**Request Body Example:**

```json
{
  "service_name": "lidarr",
  "enabled": true
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Service 'lidarr' enabled successfully"
}
```

#### Get Service Compatibility

```
GET /services/compatibility
```

Get service compatibility information for the current system.

**Response Example:**

```json
{
  "status": "success",
  "system_info": {
    "architecture": "aarch64",
    "memory_gb": 4,
    "is_raspberry_pi": true,
    "pi_model": "Raspberry Pi 4 Model B Rev 1.2",
    "has_hw_transcoding": true
  },
  "compatibility": {
    "media_servers": {
      "jellyfin": {
        "compatible": true,
        "recommended": true,
        "notes": "Recommended for ARM platforms"
      },
      "plex": {
        "compatible": true,
        "recommended": false,
        "notes": "Limited transcoding on ARM platforms"
      }
    },
    "arr_apps": {
      "sonarr": {"compatible": true, "recommended": true, "notes": "Core service"},
      "radarr": {"compatible": true, "recommended": true, "notes": "Core service"}
    }
  }
}
```

#### Generate Docker Compose File

```
GET /services/compose
```

Generate a Docker Compose file based on the current service configuration.

**Response Example:**

```json
{
  "status": "success",
  "message": "Docker Compose file generated successfully",
  "compose_file": "version: '3.7'\nservices:\n  sonarr:\n    image: linuxserver/sonarr:latest\n    container_name: sonarr\n    environment:\n      - PUID=1000\n      - PGID=1000\n      - TZ=UTC\n    volumes:\n      - /home/pi/docker/sonarr:/config\n      - /mnt/media:/media\n    ports:\n      - 8989:8989\n    restart: unless-stopped\n    networks:\n      - container_network\n",
  "temp_file_path": "/tmp/docker-compose-12345.yml"
}
```

#### Generate Environment File

```
GET /services/env
```

Generate an environment file for Docker Compose.

**Response Example:**

```json
{
  "status": "success",
  "message": ".env file generated successfully",
  "env_file": "# Generated by Pi-PVARR\n# Base Configuration\nPUID=1000\nPGID=1000\nTIMEZONE=UTC\nIMAGE_RELEASE=latest\nDOCKER_DIR=/home/pi/docker\n\n# Media and Download Directories\nMEDIA_DIR=/mnt/media\nDOWNLOADS_DIR=/mnt/downloads\nWATCH_DIR=/mnt/downloads/watch\n\n# VPN Configuration\nVPN_CONTAINER=gluetun\nVPN_IMAGE=qmcgaw/gluetun\nVPN_SERVICE_PROVIDER=private internet access\nOPENVPN_USER=user\nOPENVPN_PASSWORD=pass\nSERVER_REGIONS=Netherlands\n\n# Network Configuration\nCONTAINER_NETWORK=container_network\n",
  "temp_file_path": "/tmp/env-12345"
}
```

#### Apply Service Changes

```
POST /services/apply
```

Apply service configuration changes by generating Docker Compose files and saving them to the configuration directory.

**Response Example:**

```json
{
  "status": "success",
  "message": "Service changes applied successfully",
  "docker_compose_path": "/home/user/.config/pi-pvarr/docker-compose/docker-compose.yml",
  "env_path": "/home/user/.config/pi-pvarr/.env"
}
```

#### Start Services

```
POST /services/start
```

Start services using Docker Compose.

**Response Example:**

```json
{
  "status": "success",
  "message": "Services started successfully",
  "output": "Creating network container_network\nCreating container sonarr\nCreating container radarr\nCreating container jellyfin\n"
}
```

#### Stop Services

```
POST /services/stop
```

Stop services using Docker Compose.

**Response Example:**

```json
{
  "status": "success",
  "message": "Services stopped successfully",
  "output": "Stopping container sonarr\nStopping container radarr\nStopping container jellyfin\nRemoving network container_network\n"
}
```

#### Restart Services

```
POST /services/restart
```

Restart services using Docker Compose.

**Response Example:**

```json
{
  "status": "success",
  "message": "Services restarted successfully",
  "output": "Restarting sonarr\nRestarting radarr\nRestarting jellyfin\n"
}
```

#### Get Installation Status

```
GET /services/status
```

Get the current installation status including active and enabled services.

**Response Example:**

```json
{
  "status": "success",
  "installation_status": "running",
  "compose_file_exists": true,
  "active_services": 5,
  "enabled_services": 6,
  "service_info": {
    "arr_apps": {
      "sonarr": {
        "name": "sonarr",
        "enabled": true,
        "status": "running"
      },
      "radarr": {
        "name": "radarr",
        "enabled": true,
        "status": "running"
      }
    },
    "download_clients": {
      "transmission": {
        "name": "transmission",
        "enabled": true,
        "status": "running"
      }
    }
  }
}
```

## Error Handling

All API endpoints return proper HTTP status codes and error messages in case of failures. Common error responses:

```json
{
  "status": "error",
  "message": "Error message describing the issue"
}
```

### Installation Wizard

#### Get Installation Status

```
GET /install/status
```

Get the current status of the installation wizard.

**Response Example:**

```json
{
  "current_stage": "pre_check",
  "current_stage_name": "System Compatibility Check",
  "stage_progress": 100,
  "overall_progress": 5,
  "status": "in_progress",
  "logs": [
    "[2023-08-04 12:30:45] Starting system compatibility check",
    "[2023-08-04 12:30:46] System compatibility check completed: Compatible"
  ],
  "errors": [],
  "start_time": 1691157045.123456,
  "end_time": null,
  "elapsed_time": null
}
```

#### Check System Compatibility

```
GET /install/compatibility
```

Check if the system is compatible with Pi-PVARR installation.

**Response Example:**

```json
{
  "status": "success",
  "compatible": true,
  "system_info": {
    "memory": {
      "total_gb": 4,
      "free_gb": 3.2
    },
    "disk": {
      "total_gb": 32,
      "free_gb": 25
    },
    "docker_installed": true,
    "is_raspberry_pi": true,
    "model": "Raspberry Pi 4 Model B Rev 1.2"
  },
  "checks": {
    "memory": {
      "value": 4,
      "unit": "GB",
      "compatible": true,
      "recommended": 2,
      "message": "Memory: 4GB"
    },
    "disk_space": {
      "value": 25,
      "unit": "GB",
      "compatible": true,
      "recommended": 10,
      "message": "Free Disk Space: 25GB"
    },
    "docker": {
      "installed": true,
      "message": "Docker: Installed"
    }
  }
}
```

#### Setup Basic Configuration

```
POST /install/config
```

Set up basic configuration for the installation.

**Request Body Example:**

```json
{
  "puid": 1000,
  "pgid": 1000,
  "timezone": "Europe/London",
  "media_dir": "/mnt/media",
  "downloads_dir": "/mnt/downloads"
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Basic configuration setup completed",
  "config": {
    "puid": 1000,
    "pgid": 1000,
    "timezone": "Europe/London",
    "media_dir": "/mnt/media",
    "downloads_dir": "/mnt/downloads",
    "docker_dir": "/home/pi/docker"
  }
}
```

#### Setup Network Configuration

```
POST /install/network
```

Set up network configuration for the installation.

**Request Body Example:**

```json
{
  "vpn": {
    "enabled": true,
    "provider": "private internet access",
    "username": "user",
    "password": "pass",
    "region": "Netherlands"
  },
  "tailscale": {
    "enabled": true,
    "auth_key": "tskey-auth-example12345"
  }
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Network configuration setup completed",
  "config": {
    "vpn": {
      "enabled": true,
      "provider": "private internet access",
      "username": "user",
      "password": "pass",
      "region": "Netherlands"
    },
    "tailscale": {
      "enabled": true,
      "auth_key": "tskey-auth-example12345"
    }
  }
}
```

#### Setup Storage Configuration

```
POST /install/storage
```

Set up storage configuration for the installation.

**Request Body Example:**

```json
{
  "mount_points": [
    {
      "device": "/dev/sda1",
      "path": "/mnt/media",
      "fs_type": "ext4"
    }
  ],
  "media_directory": "/mnt/media",
  "downloads_directory": "/mnt/downloads",
  "file_sharing": {
    "type": "samba",
    "shares": [
      {
        "name": "Movies",
        "path": "/mnt/media/Movies",
        "public": false,
        "valid_users": "pi"
      },
      {
        "name": "TVShows",
        "path": "/mnt/media/TVShows",
        "public": false,
        "valid_users": "pi"
      }
    ]
  }
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Storage configuration setup completed",
  "config": {
    "media_dir": "/mnt/media",
    "downloads_dir": "/mnt/downloads"
  }
}
```

#### Setup Service Selection

```
POST /install/services
```

Set up service selection for the installation.

**Request Body Example:**

```json
{
  "arr_apps": {
    "sonarr": true,
    "radarr": true,
    "prowlarr": true,
    "lidarr": false,
    "readarr": false,
    "bazarr": true
  },
  "download_clients": {
    "transmission": true,
    "qbittorrent": false,
    "nzbget": false,
    "sabnzbd": true,
    "jdownloader": false
  },
  "media_servers": {
    "jellyfin": true,
    "plex": false,
    "emby": false
  },
  "utilities": {
    "heimdall": true,
    "overseerr": true,
    "tautulli": false,
    "portainer": true,
    "nginx_proxy_manager": true,
    "get_iplayer": false
  }
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Service selection setup completed",
  "services": {
    "arr_apps": {
      "sonarr": true,
      "radarr": true,
      "prowlarr": true,
      "lidarr": false,
      "readarr": false,
      "bazarr": true
    },
    "download_clients": {
      "transmission": true,
      "qbittorrent": false,
      "nzbget": false,
      "sabnzbd": true,
      "jdownloader": false
    },
    "media_servers": {
      "jellyfin": true,
      "plex": false,
      "emby": false
    },
    "utilities": {
      "heimdall": true,
      "overseerr": true,
      "tautulli": false,
      "portainer": true,
      "nginx_proxy_manager": true,
      "get_iplayer": false
    }
  }
}
```

#### Install Dependencies

```
POST /install/dependencies
```

Install required dependencies for Pi-PVARR.

**Response Example:**

```json
{
  "status": "success",
  "message": "Dependency installation completed"
}
```

#### Setup Docker

```
POST /install/docker
```

Set up Docker and Docker Compose.

**Response Example:**

```json
{
  "status": "success",
  "message": "Docker setup completed successfully"
}
```

#### Generate Docker Compose Files

```
POST /install/compose
```

Generate Docker Compose files based on service configuration.

**Response Example:**

```json
{
  "status": "success",
  "message": "Docker Compose configuration completed",
  "docker_compose_path": "/home/pi/docker/docker-compose.yml",
  "env_path": "/home/pi/docker/.env"
}
```

#### Create Docker Containers

```
POST /install/containers
```

Create Docker containers based on generated Docker Compose files.

**Response Example:**

```json
{
  "status": "success",
  "message": "Docker containers created successfully",
  "output": "Creating network container_network\nCreating container sonarr\nCreating container radarr\nCreating container jellyfin\n"
}
```

#### Perform Post-Installation Tasks

```
POST /install/post
```

Perform post-installation tasks.

**Response Example:**

```json
{
  "status": "success",
  "message": "Post-installation tasks completed"
}
```

#### Finalize Installation

```
POST /install/finalize
```

Finalize the installation process.

**Response Example:**

```json
{
  "status": "success",
  "message": "Installation completed successfully",
  "container_summary": {
    "total": 6,
    "running": 6,
    "stopped": 0
  },
  "container_urls": {
    "sonarr": "http://localhost:8989",
    "radarr": "http://localhost:7878",
    "jellyfin": "http://localhost:8096",
    "prowlarr": "http://localhost:9696",
    "transmission": "http://localhost:9091",
    "overseerr": "http://localhost:5055"
  },
  "installation_time": 183.45
}
```

#### Run Complete Installation

```
POST /install/run
```

Run the complete installation process from beginning to end.

**Request Body Example:**

```json
{
  "user_config": {
    "puid": 1000,
    "pgid": 1000,
    "timezone": "Europe/London",
    "media_dir": "/mnt/media",
    "downloads_dir": "/mnt/downloads"
  },
  "network_config": {
    "vpn": {
      "enabled": true,
      "provider": "private internet access",
      "username": "user",
      "password": "pass",
      "region": "Netherlands"
    },
    "tailscale": {
      "enabled": false
    }
  },
  "storage_config": {
    "mount_points": [
      {
        "device": "/dev/sda1",
        "path": "/mnt/media",
        "fs_type": "ext4"
      }
    ],
    "media_directory": "/mnt/media",
    "downloads_directory": "/mnt/downloads"
  },
  "services_config": {
    "arr_apps": {
      "sonarr": true,
      "radarr": true,
      "prowlarr": true
    },
    "download_clients": {
      "transmission": true
    },
    "media_servers": {
      "jellyfin": true
    },
    "utilities": {
      "portainer": true
    }
  }
}
```

**Response Example:**

```json
{
  "current_stage": "finalization",
  "current_stage_name": "Finalizing Installation",
  "stage_progress": 100,
  "overall_progress": 100,
  "status": "completed",
  "logs": [
    "[2023-08-04 12:30:45] Starting installation process",
    "[2023-08-04 12:30:46] Step 1: System compatibility check",
    "[2023-08-04 12:31:15] Step 2: Basic configuration setup",
    "[2023-08-04 12:32:05] Installation process completed successfully"
  ],
  "errors": [],
  "start_time": 1691157045.123456,
  "end_time": 1691157228.654321,
  "elapsed_time": 183.530865
}
```

## Rate Limiting
Currently, there are no rate limits enforced on the API. This may change in future versions.
