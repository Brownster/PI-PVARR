# Pi-PVARR Installation Wizard Documentation

This document provides comprehensive documentation for the Pi-PVARR Installation Wizard, including both backend API endpoints and the frontend user interface.

## Overview

The Pi-PVARR Installation Wizard provides a streamlined, step-by-step process for setting up your Pi-PVARR media server. The wizard covers:

1. System compatibility checking
2. Basic configuration setup
3. Network configuration (including VPN and Tailscale)
4. Storage configuration
5. Service selection
6. Installation and deployment

The wizard is designed to work across a variety of hardware platforms, with special optimizations for Raspberry Pi.

## Installation Wizard API Endpoints

All installation wizard API endpoints are available under the `/api/install/` path. These endpoints facilitate the step-by-step installation process.

### Get Installation Status

```
GET /api/install/status
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

### Check System Compatibility

```
GET /api/install/compatibility
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

### Setup Basic Configuration

```
POST /api/install/config
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

### Setup Network Configuration

```
POST /api/install/network
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

### Setup Storage Configuration

```
POST /api/install/storage
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

### Setup Service Selection

```
POST /api/install/services
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

### Install Dependencies

```
POST /api/install/dependencies
```

Installs system dependencies required for Pi-PVARR.

**Response Example:**

```json
{
  "status": "success",
  "message": "Dependency installation completed"
}
```

### Setup Docker

```
POST /api/install/docker
```

Sets up Docker and Docker Compose.

**Response Example:**

```json
{
  "status": "success",
  "message": "Docker setup completed successfully"
}
```

### Generate Docker Compose Files

```
POST /api/install/compose
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

### Create Containers

```
POST /api/install/containers
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

### Perform Post-Installation Tasks

```
POST /api/install/post
```

Performs post-installation tasks such as setting up permissions and initializing services.

**Response Example:**

```json
{
  "status": "success",
  "message": "Post-installation tasks completed"
}
```

### Finalize Installation

```
POST /api/install/finalize
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

### Run Complete Installation

```
POST /api/install/run
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

## Frontend User Interface

The Installation Wizard UI is built as a step-by-step process with a clear progress indicator and intuitive form controls.

### Accessing the Wizard

The Installation Wizard is automatically shown on first run of Pi-PVARR. You can also access it at any time by visiting:

```
http://<your-pi-ip>:8080/install
```

### Wizard Steps

The Installation Wizard consists of the following steps:

1. **System Compatibility Check**: Verifies that your system meets the requirements
2. **Basic Configuration**: Sets up user IDs, timezone, and base directories
3. **Network Configuration**: Configures VPN and Tailscale for secure access
4. **Storage Configuration**: Sets up storage drives and file sharing
5. **Service Selection**: Choose which services to install
6. **Installation**: Review and start the installation process

### UI Components

The Installation Wizard UI provides the following components:

- **Progress Bar**: Shows overall installation progress
- **Step Indicators**: Shows the current step and completed steps
- **Form Controls**: Input fields, toggle switches, and dropdowns for configuration
- **Validation**: Real-time validation of inputs
- **Installation Log**: Live updates during the installation process
- **Service Summary**: Overview of installed services and their access URLs

### JavaScript API Client

The Installation Wizard uses a JavaScript API client (`api-client.js`) to communicate with the backend. This client provides methods for all installation wizard endpoints:

```javascript
// Initialize the API client
const api = new ApiClient();

// Check system compatibility
const compatibilityCheck = await api.checkSystemCompatibility();

// Save basic configuration
const basicConfig = {
  puid: 1000,
  pgid: 1000,
  timezone: 'Europe/London',
  media_dir: '/mnt/media',
  downloads_dir: '/mnt/downloads'
};
const configResult = await api.saveBasicConfig(basicConfig);

// Start the complete installation
const installationConfig = {
  user_config: basicConfig,
  network_config: { ... },
  storage_config: { ... },
  services_config: { ... }
};
const installationResult = await api.startInstallation(installationConfig);
```

## Error Handling

The Installation Wizard includes robust error handling:

1. **Backend Validation**: Each configuration step validates inputs and returns clear error messages
2. **Frontend Validation**: The UI validates inputs before submitting to the API
3. **Installation Recovery**: The installation process can recover from certain errors
4. **Detailed Logs**: Comprehensive logs help diagnose and resolve issues

## Testing

The Installation Wizard includes comprehensive testing:

1. **Backend Unit Tests**: Tests for all installation wizard functions
2. **API Tests**: Tests for all API endpoints
3. **Frontend Tests**: Tests for UI components and API client
4. **Integration Tests**: Tests for the complete installation flow

## Customization

The Installation Wizard can be customized through:

1. **Configuration Files**: Default settings in `config.json`
2. **Service Definitions**: Service configurations in `services.json`
3. **UI Themes**: Light and dark mode supported
4. **Custom Validations**: Additional validation rules can be added

## Troubleshooting

If you encounter issues with the Installation Wizard:

1. **Check Logs**: Review the installation logs at `/api/install/status`
2. **System Requirements**: Ensure your system meets the minimum requirements
3. **Network Issues**: Verify network connectivity for downloading Docker images
4. **Storage Issues**: Ensure sufficient disk space and proper permissions
5. **Docker Issues**: Check Docker installation and service status

## Integration with Pi-PVARR

The Installation Wizard integrates with other Pi-PVARR components:

1. **Dashboard**: Accessible after installation
2. **Service Manager**: Manages services installed via the wizard
3. **Update Manager**: Updates services installed via the wizard
4. **Health Monitoring**: Monitors the health of installed services

## Security Considerations

The Installation Wizard implements several security measures:

1. **Password Security**: Passwords are not stored in plain text
2. **Input Validation**: All inputs are validated to prevent injection attacks
3. **Secure Defaults**: Default configurations prioritize security
4. **Permission Handling**: Proper file and directory permissions are set

## Future Enhancements

Planned enhancements for the Installation Wizard include:

1. **Resumable Installations**: Resume interrupted installations
2. **Migration Tools**: Migrate from other media server platforms
3. **Backup Integration**: Built-in backup configuration
4. **Advanced Networking**: More network configuration options5. **Custom Service Configurations**: More granular service configuration
