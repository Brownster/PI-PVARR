# PI-PVARR API Documentation

This document provides reference information for the PI-PVARR API endpoints.

## Base URL

All API endpoints are relative to the base URL of your PI-PVARR installation:

```
http://<your-pi-ip>:8080/api
```

## Authentication

Currently, the API does not require authentication. This will be added in a future update.

## Error Handling

All API endpoints return standard HTTP status codes:

- `200 OK`: The request was successful
- `400 Bad Request`: The request was invalid
- `404 Not Found`: The requested resource was not found
- `500 Internal Server Error`: An error occurred on the server

Error responses include a JSON body with error details:

```json
{
  "error": "Error message",
  "details": "Detailed error information (if available)"
}
```

## API Endpoints

### System Information

#### Get System Information

```
GET /system
```

Returns detailed information about the system.

**Response Example:**

```json
{
  "hostname": "pi-pvr",
  "os": {
    "name": "Debian",
    "version": "12",
    "pretty_name": "Debian GNU/Linux 12 (bookworm)",
    "id": "debian"
  },
  "architecture": "aarch64",
  "memory_total": 4294967296,
  "memory_available": 2147483648,
  "disk_total": 107374182400,
  "disk_free": 53687091200,
  "cpu_usage": 15,
  "docker_installed": true,
  "docker_version": "24.0.5",
  "tailscale_installed": true,
  "tailscale_ip": "100.100.100.100",
  "ip_address": "192.168.1.100",
  "installation_status": "completed"
}
```

### Configuration

#### Get Configuration

```
GET /config
```

Returns the current system configuration.

**Response Example:**

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
    "region": "Netherlands"
  },
  "tailscale": {
    "enabled": false
  },
  "installation_status": "completed"
}
```

#### Update Configuration

```
POST /config
```

Updates the system configuration.

**Request Body Example:**

```json
{
  "puid": 1000,
  "pgid": 1000,
  "timezone": "Europe/Paris"
}
```

**Response Example:**

```json
{
  "status": "success"
}
```

### Services

#### Get All Services

```
GET /services
```

Returns information about all services.

**Response Example:**

```json
{
  "services": [
    {
      "name": "sonarr",
      "type": "media",
      "status": "running",
      "port": 8989,
      "url": "http://192.168.1.100:8989",
      "description": "TV show management"
    },
    {
      "name": "radarr",
      "type": "media",
      "status": "running",
      "port": 7878,
      "url": "http://192.168.1.100:7878",
      "description": "Movie management"
    },
    // Additional services...
  ]
}
```

#### Start Service

```
POST /start/:container
```

Starts a specific container.

**Path Parameters:**

- `container`: The name of the container to start

**Response Example:**

```json
{
  "status": "success"
}
```

#### Stop Service

```
POST /stop/:container
```

Stops a specific container.

**Path Parameters:**

- `container`: The name of the container to stop

**Response Example:**

```json
{
  "status": "success"
}
```

#### Restart Service

```
POST /restart/:container
```

Restarts a specific container.

**Path Parameters:**

- `container`: The name of the container to restart

**Response Example:**

```json
{
  "status": "success"
}
```

#### Restart All Services

```
POST /restart
```

Restarts all containers.

**Response Example:**

```json
{
  "status": "success"
}
```

### Storage

#### Get Drives

```
GET /storage/drives
```

Returns information about connected drives.

**Response Example:**

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

### Update Management

#### Start Image Update

```
POST /update/images
```

Starts the process of updating all Docker images.

**Response Example:**

```json
{
  "status": "success",
  "message": "Image update process started"
}
```

#### Get Update Status

```
GET /update/status
```

Returns the status of the image update process.

**Response Example:**

```json
{
  "status": "in_progress",
  "logs": "Starting Docker image updates...\nPulling image sonarr:latest...\nPulling image radarr:latest..."
}
```

### Logs

#### Get Installation Logs

```
GET /logs
```

Returns the installation logs.

**Response Example:**

```json
{
  "logs": "Installation started...\nInstalling Docker...\nDocker installed successfully...\n"
}
```

#### Get System Logs

```
GET /logs/system
```

Returns system logs.

**Query Parameters:**

- `source`: Log source (system, installer, vpn, docker)
- `level`: Log level (all, info, warning, error)
- `lines`: Number of lines to return (default: 100)

**Response Example:**

```json
{
  "content": "2025-04-02 10:00:05 [INFO] System startup\n2025-04-02 10:00:10 [INFO] Loading configuration\n...",
  "source": "system",
  "level": "all",
  "lines": 100
}
```

#### Get Service Logs

```
GET /logs/:service
```

Returns logs for a specific service.

**Path Parameters:**

- `service`: The name of the service to get logs for

**Query Parameters:**

- `lines`: Number of lines to return (default: 100)

**Response Example:**

```json
{
  "content": "Starting Sonarr...\nSonarr started successfully...\n",
  "service": "sonarr",
  "lines": 100
}
```

### Installation Wizard

The Installation Wizard API provides endpoints for setting up your Pi-PVARR installation.

#### Get Installation Status

```
GET /install/status
```

Returns the current status of the installation process.

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

Checks if the system meets the requirements for Pi-PVARR installation.

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

Sets up the basic configuration parameters.

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

Sets up network configuration including VPN and Tailscale.

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

Sets up storage configuration including mounting drives and configuring file sharing.

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
        "valid_users": "user1"
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

Sets up service selection for the Pi-PVARR installation.

**Request Body Example:**

```json
{
  "arr_apps": {
    "sonarr": true,
    "radarr": true,
    "prowlarr": true,
    "lidarr": false,
    "readarr": false
  },
  "download_clients": {
    "transmission": true,
    "qbittorrent": false,
    "nzbget": false
  },
  "media_servers": {
    "jellyfin": true,
    "plex": false,
    "emby": false
  },
  "utilities": {
    "heimdall": true,
    "overseerr": false,
    "portainer": true
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

Installs system dependencies required for Pi-PVARR.

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

Sets up Docker and Docker Compose.

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

Generates Docker Compose configuration files.

**Response Example:**

```json
{
  "status": "success",
  "message": "Docker Compose configuration completed",
  "docker_compose_path": "/home/pi/docker/docker-compose.yml",
  "env_path": "/home/pi/docker/.env"
}
```

#### Create Containers

```
POST /install/containers
```

Creates Docker containers based on the service selection.

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

Performs post-installation tasks such as setting up permissions and initializing services.

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

Finalizes the installation process.

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

Runs the complete installation process from start to finish.

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
    }
  },
  "storage_config": {
    "media_directory": "/mnt/media",
    "downloads_directory": "/mnt/downloads"
  },
  "services_config": {
    "arr_apps": {
      "sonarr": true,
      "radarr": true
    },
    "media_servers": {
      "jellyfin": true
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

## JavaScript API Client

For frontend developers, PI-PVARR provides a JavaScript API client that centralizes all API calls. This client is available in `web-ui/js/api-client.js` and can be imported in your JavaScript modules:

```javascript
import { systemApi, servicesApi, storageApi, networkApi, updateApi, configApi, logsApi, installApi } from './api-client.js';

// Example: Get system information
const systemInfo = await systemApi.getSystemInfo();

// Example: Start a service
await servicesApi.startService('sonarr');

// Example: Get logs
const logs = await logsApi.getSystemLogs('system', 'all', 100);

// Example: Check system compatibility
const compatibility = await installApi.checkSystemCompatibility();
```

The API client handles error reporting and provides a consistent interface for all API endpoints.

## WebSocket API

The WebSocket API provides real-time updates without polling. This enables:

- Real-time resource usage monitoring
- Instant service status updates
- Live log streaming
- Installation progress events

### WebSocket Connection

Connect to the WebSocket endpoint at:

```
ws://<host>:8080/ws
```

### Message Types

The WebSocket API supports the following event types:

- `installation_status`: Updates on installation progress
- `installation_complete`: Notification when installation completes
- `service_update`: Updates when service status changes
- `system_update`: Real-time system resource updates
- `logs`: Live log streaming

## API Versioning

The current API is v1 (implicit). Future versions will be explicitly versioned in the URL path (e.g., `/api/v2/system`).

## Rate Limiting

Currently, there are no rate limits on the API. However, excessive requests may impact system performance.

## Future Enhancements

Planned API enhancements include:

- Authentication and authorization
- Pagination for list endpoints
- Filtering and sorting options
- WebSocket support for real-time updates
- Comprehensive error codes
- API versioning- Rate limiting
