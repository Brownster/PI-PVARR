# Pi-PVARR API Documentation

This document describes the REST API endpoints available in the Pi-PVARR Media Server.

## Base URL

All API endpoints are accessible under the `/api` path.

## Authentication

Currently, the API does not require authentication.

## Response Format

All responses are in JSON format. Successful responses typically include a `status` field with the value `success`.

## System Information

### Get System Information

```
GET /api/system
```

Returns information about the system, including:
- Hostname
- Operating system details
- Hardware information
- Memory usage
- Disk usage
- CPU usage
- Temperature
- Network interfaces

#### Response Example

```json
{
  "hostname": "raspberrypi",
  "platform": "linux",
  "platform_version": "5.10.103-v8+",
  "os": {
    "name": "raspbian",
    "release": "11",
    "pretty_name": "Raspbian GNU/Linux 11 (bullseye)"
  },
  "architecture": "aarch64",
  "memory_total": 4294967296,
  "memory_available": 2147483648,
  "memory_used": 2147483648,
  "memory_percent": 50,
  "disk_total": 34359738368,
  "disk_free": 21474836480,
  "disk_used": 12884901888,
  "disk_percent": 37.5,
  "cpu": {
    "model": "ARMv8",
    "cores": 4,
    "percent": 15.5
  },
  "cpu_usage_percent": 15.5,
  "temperature_celsius": 45.2,
  "raspberry_pi": {
    "is_raspberry_pi": true,
    "model": "Raspberry Pi 4 Model B Rev 1.4"
  },
  "docker_installed": true,
  "tailscale_installed": false,
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
        "mac": "dc:a6:32:12:34:56"
      }
    }
  }
}
```

## Configuration

### Get Configuration

```
GET /api/config
```

Returns the current configuration settings.

#### Response Example

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
    "username": "xxx",
    "password": "xxx",
    "region": "Netherlands"
  },
  "tailscale": {
    "enabled": false,
    "auth_key": ""
  },
  "installation_status": "completed"
}
```

### Update Configuration

```
POST /api/config
```

Updates the configuration settings.

#### Request Body

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
    "username": "new_username",
    "password": "new_password",
    "region": "Netherlands"
  },
  "tailscale": {
    "enabled": true,
    "auth_key": "tskey-xxxx"
  }
}
```

#### Response Example

```json
{
  "status": "success"
}
```

### Get Services Configuration

```
GET /api/services
```

Returns the current services configuration.

#### Response Example

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

### Update Services Configuration

```
POST /api/services
```

Updates the services configuration.

#### Request Body

```json
{
  "arr_apps": {
    "sonarr": true,
    "radarr": true,
    "prowlarr": true,
    "lidarr": true,
    "readarr": true,
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

#### Response Example

```json
{
  "status": "success"
}
```

## Docker Containers

### Get All Containers

```
GET /api/containers
```

Returns information about all Docker containers.

#### Response Example

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

### Get Container Information

```
GET /api/containers/{container_name}
```

Returns detailed information about a specific container.

#### Response Example

```json
{
  "name": "sonarr",
  "status": "running",
  "image": "linuxserver/sonarr:latest",
  "created": "2023-04-01T12:34:56.789Z",
  "ports": [
    {
      "container": "8989",
      "host": "8989",
      "protocol": "tcp"
    }
  ],
  "volumes": [
    "/home/pi/docker/sonarr:/config",
    "/mnt/media:/media"
  ],
  "environment": [
    "PUID=1000",
    "PGID=1000",
    "TZ=Europe/London"
  ],
  "labels": {
    "maintainer": "LinuxServer.io"
  }
}
```

### Get Container Logs

```
GET /api/containers/{container_name}/logs?lines=100
```

Returns logs from a specific container.

#### Parameters

- `lines` (optional): Number of log lines to retrieve (default: 100)

#### Response Example

```json
{
  "container": "sonarr",
  "logs": "[2023-04-02 10:00:05] INFO - Starting Sonarr\n[2023-04-02 10:00:10] INFO - Sonarr started successfully"
}
```

### Start Container

```
POST /api/containers/{container_name}/start
```

Starts a specific container.

#### Response Example

```json
{
  "status": "success",
  "message": "Container sonarr started successfully"
}
```

### Stop Container

```
POST /api/containers/{container_name}/stop
```

Stops a specific container.

#### Response Example

```json
{
  "status": "success",
  "message": "Container sonarr stopped successfully"
}
```

### Restart Container

```
POST /api/containers/{container_name}/restart
```

Restarts a specific container.

#### Response Example

```json
{
  "status": "success",
  "message": "Container sonarr restarted successfully"
}
```

### Update All Containers

```
POST /api/containers/update
```

Updates all containers by pulling the latest images.

#### Response Example

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

## Storage API

### Get Drives

```
GET /api/storage/drives
```

Returns information about connected drives.

#### Response Example

```json
{
  "drives": [
    {
      "device": "/dev/sda1",
      "size": "500G",
      "fstype": "ext4",
      "mountpoint": "/mnt/media",
      "used": "100GB",
      "available": "400GB",
      "percent": 20,
      "is_usb": true,
      "label": "External Drive", 
      "model": "SanDisk"
    },
    {
      "device": "/dev/sdb1",
      "size": "1T",
      "fstype": "ext4",
      "mountpoint": "/mnt/backup",
      "used": "200GB",
      "available": "800GB",
      "percent": 20,
      "is_usb": false,
      "label": "Internal Drive",
      "model": "WD"
    }
  ]
}
```

### Get Media Paths

```
GET /api/storage/media/paths
```

Returns information about configured media paths.

#### Response Example

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

### Mount Drive

```
POST /api/storage/mount
```

Mounts a drive.

#### Request Body

```json
{
  "device": "/dev/sda1",
  "mountpoint": "/mnt/media",
  "fstype": "ext4",
  "mount_options": "defaults",
  "add_to_fstab": true,
  "verify": true
}
```

#### Response Example

```json
{
  "status": "success",
  "message": "Device /dev/sda1 mounted to /mnt/media"
}
```

## Network API

The following endpoints are available for network management:

### Get Network Information

```
GET /api/network/info
```

Returns comprehensive network information including interface details and VPN status.

#### Response Example

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

### Get Network Interfaces

```
GET /api/network/interfaces
```

Returns information about network interfaces.

#### Response Example

```json
{
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

### Get VPN Status

```
GET /api/network/vpn/status
```

Returns VPN connection status.

#### Response Example

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

### Configure VPN

```
POST /api/network/vpn/configure
```

Configures VPN settings.

#### Request Body Example

```json
{
  "enabled": true,
  "provider": "private internet access",
  "username": "user",
  "password": "pass",
  "region": "Netherlands"
}
```

#### Response Example

```json
{
  "status": "success",
  "message": "VPN configuration updated for provider private internet access"
}
```

### Get Tailscale Status

```
GET /api/network/tailscale/status
```

Returns Tailscale VPN status.

#### Response Example

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

### Configure Tailscale

```
POST /api/network/tailscale/configure
```

Configures Tailscale VPN.

#### Request Body Example

```json
{
  "enabled": true,
  "auth_key": "tskey-abcdef123456"
}
```

#### Response Example

```json
{
  "status": "success",
  "message": "Tailscale configured and started"
}
```