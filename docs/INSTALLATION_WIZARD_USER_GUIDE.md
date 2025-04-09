# Pi-PVARR Installation Wizard: User Guide

This guide walks you through using the Pi-PVARR Installation Wizard to set up your media server.

## Table of Contents

1. [Introduction](#introduction)
2. [Before You Begin](#before-you-begin)
3. [Step 1: System Compatibility Check](#step-1-system-compatibility-check)
4. [Step 2: Basic Configuration](#step-2-basic-configuration)
5. [Step 3: Network Configuration](#step-3-network-configuration)
6. [Step 4: Storage Configuration](#step-4-storage-configuration)
7. [Step 5: Service Selection](#step-5-service-selection)
8. [Step 6: Installation](#step-6-installation)
9. [After Installation](#after-installation)
10. [Troubleshooting](#troubleshooting)

## Introduction

The Pi-PVARR Installation Wizard provides a simple, step-by-step approach to set up a complete media server on your Raspberry Pi or other compatible Linux system. The wizard will guide you through:

- Checking your system's compatibility
- Configuring basic system settings
- Setting up networking, including VPN options
- Configuring storage for your media
- Selecting which media services to install
- Installing and configuring all selected components

## Before You Begin

Before starting the Installation Wizard, make sure you have:

1. **Hardware Requirements**:
   - Raspberry Pi 4 (2GB+ RAM recommended) or other compatible Linux system
   - 16GB+ microSD card for the operating system
   - External storage device for media (highly recommended)
   - Ethernet connection (recommended) or Wi-Fi

2. **Software Requirements**:
   - Fresh installation of Raspberry Pi OS (Debian-based) or other compatible Linux distribution
   - Basic system setup completed (user accounts, network connectivity)

3. **Information to Have Ready**:
   - Your user account details (for file permissions)
   - VPN credentials (if you plan to use a VPN)
   - Desired folder structure for your media

## Step 1: System Compatibility Check

**Purpose**: Verify that your system meets the requirements for Pi-PVARR.

1. Access the Pi-PVARR Installation Wizard by opening a web browser and navigating to:
   ```
   http://<your-pi-ip>:8080
   ```

2. Click the "Run Compatibility Check" button to start the system check.

3. The wizard will check:
   - Available memory (2GB+ recommended)
   - Available disk space (10GB+ recommended)
   - Docker installation status
   - Processor architecture
   - Operating system compatibility

4. Review the results:
   - ✅ Green checkmarks indicate passed checks
   - ⚠️ Yellow warnings indicate potential issues that may affect performance
   - ❌ Red errors indicate critical issues that need to be resolved

5. If your system passes all critical checks, click "Next" to continue.

> **Note**: Even if your system doesn't meet all recommended specifications, you may still proceed, but performance might be affected.

## Step 2: Basic Configuration

**Purpose**: Configure essential system parameters.

1. Complete the form with your configuration details:

   - **PUID/PGID**: User and group IDs for file permissions (typically 1000 for the first user)
   - **Timezone**: Your local timezone for correct scheduling
   - **Media Directory**: Where your media files will be stored
   - **Downloads Directory**: Where downloaded files will be temporarily stored

2. For most users, the default values will work well. If you're unsure about any setting, hover over the (?) icons for additional information.

3. Click "Next" to save your basic configuration.

> **Tip**: Use absolute paths for your directories (e.g., `/mnt/media` rather than relative paths).

## Step 3: Network Configuration

**Purpose**: Configure network settings, including optional VPN for download privacy.

1. **VPN Configuration** (Optional):
   - Toggle "Enable VPN for Download Clients" if you want to use a VPN
   - Select your VPN provider from the dropdown
   - Enter your VPN username and password
   - Select a VPN region (typically choose one closest to your location for best performance)

2. **Tailscale Configuration** (Optional):
   - Toggle "Enable Tailscale" if you want secure remote access to your server
   - If you have a Tailscale auth key, enter it (or you can authenticate later)

3. Click "Next" to save your network configuration.

> **Security Tip**: Using a VPN for downloads is highly recommended to enhance your privacy and security.

## Step 4: Storage Configuration

**Purpose**: Configure storage drives and file sharing options.

1. **Available Drives** section shows detected storage devices:
   - Review the list of available drives
   - Click "Select" on the drive you want to use for media storage

2. **Directory Configuration**:
   - Confirm or adjust the media and downloads directories
   - These should typically be on your largest storage device

3. **File Sharing** (Optional):
   - Select a share method (Samba for Windows/Mac/Linux compatibility, NFS for Linux/Mac)
   - Configure shares for your media
   - Set visibility options (public or authenticated access)
   - Click "Add Another Share" if you want to create multiple shares

4. Click "Next" to save your storage configuration.

> **Important**: If you're using a removable drive, ensure it's properly mounted and has appropriate permissions.

## Step 5: Service Selection

**Purpose**: Choose which services to install on your Pi-PVARR server.

The services are organized into four categories:

1. **Media Management**:
   - **Sonarr**: TV series management
   - **Radarr**: Movie management
   - **Prowlarr**: Indexer management
   - **Lidarr**: Music management
   - **Readarr**: Book management
   - **Bazarr**: Subtitle management

2. **Download Clients**:
   - **Transmission**: Torrent downloader
   - **qBittorrent**: Alternative torrent client
   - **NZBGet**: Usenet downloader
   - **SABnzbd**: Alternative usenet client
   - **JDownloader**: Direct download manager

3. **Media Servers**:
   - **Jellyfin**: Open source media server
   - **Plex**: Popular media server
   - **Emby**: Alternative media server

4. **Utilities**:
   - **Heimdall**: Application dashboard
   - **Overseerr**: Media request manager
   - **Tautulli**: Plex monitoring tool
   - **Portainer**: Docker UI manager
   - **Get iPlayer**: BBC content downloader

Toggle the switches for the services you want to install. The defaults are appropriate for most users.

> **Performance Tip**: On Raspberry Pi with limited resources, select fewer services for better performance.

Click "Next" to save your service selection.

## Step 6: Installation

**Purpose**: Review your choices and start the installation process.

1. **Installation Summary**:
   - Review your configuration choices
   - Check that your selected services are correct
   - Make any necessary adjustments by clicking "Previous"

2. **Before You Begin**:
   - Read the installation notes
   - Be aware that the installation process may take several minutes
   - Ensure your system won't be interrupted during installation

3. Click "Start Installation" to begin the process.

4. **Installation Progress**:
   - Watch the progress bar and status updates
   - The installation log shows detailed information about each step
   - The process includes:
     - Installing dependencies
     - Setting up Docker
     - Generating configuration files
     - Downloading Docker images
     - Creating and starting containers
     - Configuring services

5. Wait for the installation to complete. This may take 10-30 minutes depending on your internet speed and system performance.

## After Installation

Once the installation is complete, you'll see the "Installation Complete" screen with:

1. **Service Access Links**:
   - Direct links to all your installed services
   - Bookmark these for easy access later

2. **Getting Started Steps**:
   - Instructions for setting up each service
   - Recommendations for next steps

3. Click "Go to Dashboard" to access your Pi-PVARR dashboard.

The dashboard gives you a complete overview of your media server system, with options to:
- Monitor system resources
- Check service status
- Access all installed applications
- Update your services
- View logs
- Change settings

## Troubleshooting

If you encounter issues during installation:

1. **Check the Installation Log**:
   - The log will often indicate the specific problem

2. **Common Issues**:
   - **Docker Issues**: Verify Docker is installed and running
   - **Network Issues**: Check your internet connection
   - **Storage Issues**: Ensure storage devices are properly mounted
   - **Permission Issues**: Verify PUID/PGID settings

3. **Retry Installation**:
   - You can retry the installation by refreshing the page and starting again
   - Previously entered settings will be preserved

4. **System Requirements**:
   - If your system is struggling, try selecting fewer services

5. **Get Help**:
   - Check the documentation at [Pi-PVARR Documentation](https://github.com/Pi-PVARR/docs)
   - Ask for help in the community forums
   - Check GitHub issues for known problems

---

Congratulations! You've successfully set up Pi-PVARR with the Installation Wizard. Enjoy your new media server system!