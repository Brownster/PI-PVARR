# Pi-PVARR Media Server

A comprehensive Docker-based media server solution designed for Raspberry Pi and other Linux systems. Pi-PVARR provides an intuitive web interface to manage media services, downloads, storage, and network settings.

## Features

- **System Health Monitoring**: CPU, RAM, disk space, and temperature monitoring
- **Docker Management**: Start, stop, restart, and update containers
- **Storage Management**: Configure media directories and network shares
- **Network Management**: Configure VPN and Tailscale for secure remote access
- **Media Services**: Sonarr, Radarr, Prowlarr, Jellyfin, and more
- **First-time Setup Wizard**: Guided installation for new users

## Requirements

- Raspberry Pi 4/5 or any Linux-based system (4GB+ RAM recommended)
- Docker and Docker Compose (installed automatically)
- External storage for media files
- Internet connection

## Quick Start

To install Pi-PVARR, run:

```bash
sudo apt update
sudo apt install git -y
git clone https://github.com/username/Pi-PVARR.git
cd Pi-PVARR
./install.sh
```

After installation, access the web UI at `http://<your-ip>:8080`

## Documentation

See the [docs](./docs) directory for detailed documentation:

- [Installation Guide](./docs/INSTALLATION.md)
- [User Guide](./docs/USER_GUIDE.md)
- [Developer Guide](./docs/DEVELOPER_GUIDE.md)
- [API Documentation](./docs/API.md)

## Development

For development instructions, see [CONTRIBUTING.md](./docs/CONTRIBUTING.md).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
