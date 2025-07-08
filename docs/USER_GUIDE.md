# Pi-PVARR User Guide

This guide helps you get the most out of your Pi-PVARR Media Server.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Dashboard Overview](#dashboard-overview)
3. [Managing Docker Services](#managing-docker-services)
4. [Storage Management](#storage-management)
5. [Network Configuration](#network-configuration)
6. [Settings](#settings)

## Getting Started

### First-Time Setup

When you first launch Pi-PVARR, you'll be guided through a setup wizard that helps you configure:

1. System settings (user/group IDs, timezone)
2. Storage locations (media and downloads directories)
3. Network settings (VPN and Tailscale configuration)
4. Services selection (media management, download clients, media servers)

### Accessing the Web UI

After installation, access the web UI at:

```
http://your-server-ip:8080
```

## Dashboard Overview

The Pi-PVARR dashboard is divided into three main sections:

### System Health Panel (Top Left)

This panel displays:
- Basic system information (hostname, OS, architecture, IP)
- CPU usage
- RAM usage
- Disk usage
- System temperature

### Storage & Shares Panel (Bottom Left)

This panel has two tabs:
- **Drives**: Shows mounted drives and their usage
- **Shares**: Shows configured network shares

### Main Content Area (Right)

This area has multiple tabs:
- **Services**: Manage Docker containers
- **Media Folders**: View and manage media directories
- **Network**: Configure network settings
- **Logs**: View system logs

## Managing Docker Services

The Services tab in the main content area allows you to manage all your Docker containers.

### Service Categories

Services are categorized into:
- **All**: All available services
- **Media Management**: Sonarr, Radarr, Prowlarr, etc.
- **Download Clients**: Transmission, NZBGet, etc.
- **Media Servers**: Jellyfin, Plex, Emby
- **Utilities**: Portainer, Heimdall, etc.

### Service Actions

For each service, you can:
- **Start**: Start a stopped service
- **Stop**: Stop a running service
- **Restart**: Restart a running service
- **Open**: Open the service's web UI (if it's running)

### Batch Actions

You can also perform batch operations:
- **Start All**: Start all services
- **Stop All**: Stop all services
- **Restart All**: Restart all running services
- **Update All**: Update all services to their latest versions

## Storage Management

### Drives Tab

The Drives tab shows all mounted drives, including:
- Device name
- Mount point
- Size
- Used space
- Available space

You can also:
- Add a new drive
- Unmount a drive

### Shares Tab

The Shares tab shows configured network shares, including:
- Share name
- Path
- Share type
- Access controls

You can also:
- Add a new share
- Edit an existing share
- Remove a share

## Media Folders

The Media Folders tab in the main content area shows your media directories, including:
- Movies
- TV Shows
- Music
- Books
- Downloads

For each directory, you can:
- View size and file count
- Scan for new content
- Browse the directory
- Edit the directory configuration

## Network Configuration

The Network tab in the main content area allows you to manage:

### Network Information

- IP address
- Gateway
- DNS servers
- MAC address

### VPN Configuration

- VPN provider settings
- Connection status
- External IP address

### Tailscale Configuration

- Tailscale status
- Tailscale IP address
- Connected peers

## Settings

The Settings tab allows you to configure:

### General Settings

- User/group IDs
- Timezone
- Language
- Theme

### Services Settings

- Auto-update settings
- Restart policies
- Update channels

### Network Settings

- Port ranges
- VPN kill switch
- Proxy settings

### Security Settings

- Web UI password protection
- HTTPS configuration

### Advanced Settings

- Debug mode
- Hardware acceleration- Resource limits
