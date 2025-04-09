"""Service manager module for Pi-PVARR.

This module provides functions to manage services:
- Generate Docker compose files
- Manage service configuration
- Check service health and compatibility
- Generate environment files for services
"""

import os
import json
import platform
import subprocess
import tempfile
from typing import Dict, Any, List, Optional, Tuple

from src.core import config, docker_manager

# Define service types and their descriptions
SERVICE_TYPES = {
    "arr_apps": "Media Management Apps",
    "download_clients": "Download Clients",
    "media_servers": "Media Servers",
    "utilities": "Utility Services"
}

# Service descriptions
SERVICE_DESCRIPTIONS = {
    # Arr Apps
    "sonarr": "TV Series Management",
    "radarr": "Movie Management",
    "lidarr": "Music Management",
    "readarr": "Book & Audiobook Management",
    "prowlarr": "Indexer Management",
    "bazarr": "Subtitle Management",
    
    # Download Clients
    "transmission": "Torrent Client",
    "qbittorrent": "Torrent Client",
    "nzbget": "Usenet Client",
    "sabnzbd": "Usenet Client",
    "jdownloader": "Direct Download Client",
    
    # Media Servers
    "jellyfin": "Media Server",
    "plex": "Media Server",
    "emby": "Media Server",
    
    # Utilities
    "get_iplayer": "BBC Content Downloader",
    "heimdall": "Application Dashboard",
    "overseerr": "Media Requests",
    "tautulli": "Plex Monitoring",
    "portainer": "Docker Management",
    "nginx_proxy_manager": "Reverse Proxy",
    "gluetun": "VPN Client",
    "tailscale": "Secure Network"
}

# Default web UI ports for services
DEFAULT_PORTS = {
    "sonarr": 8989,
    "radarr": 7878,
    "lidarr": 8686,
    "readarr": 8787,
    "prowlarr": 9696,
    "bazarr": 6767,
    "transmission": 9091,
    "qbittorrent": 8080,
    "nzbget": 6789,
    "sabnzbd": 8080,
    "jdownloader": 5800,
    "jellyfin": 8096,
    "plex": 32400,
    "emby": 8096,
    "get_iplayer": 1935,
    "heimdall": 80,
    "overseerr": 5055,
    "tautulli": 8181,
    "portainer": 9000,
    "nginx_proxy_manager": 81
}

# Docker image names by service
DOCKER_IMAGES = {
    "sonarr": "linuxserver/sonarr:latest",
    "radarr": "linuxserver/radarr:latest",
    "lidarr": "linuxserver/lidarr:latest",
    "readarr": "linuxserver/readarr:latest",
    "prowlarr": "linuxserver/prowlarr:latest",
    "bazarr": "linuxserver/bazarr:latest",
    "transmission": "linuxserver/transmission:latest",
    "qbittorrent": "linuxserver/qbittorrent:latest",
    "nzbget": "linuxserver/nzbget:latest",
    "sabnzbd": "linuxserver/sabnzbd:latest",
    "jdownloader": "jlesage/jdownloader-2:latest",
    "jellyfin": "linuxserver/jellyfin:latest",
    "plex": "linuxserver/plex:latest",
    "emby": "linuxserver/emby:latest",
    "get_iplayer": "lsiobase/alpine:3.13",
    "heimdall": "linuxserver/heimdall:latest",
    "overseerr": "linuxserver/overseerr:latest",
    "tautulli": "linuxserver/tautulli:latest",
    "portainer": "portainer/portainer-ce:latest",
    "nginx_proxy_manager": "jc21/nginx-proxy-manager:latest",
    "gluetun": "qmcgaw/gluetun:latest",
    "tailscale": "tailscale/tailscale:latest"
}


def get_service_info() -> Dict[str, Dict[str, Any]]:
    """
    Get comprehensive information about services including status, descriptions, and enabled status.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of service information organized by service types.
    """
    result = {}
    
    # Get current service configuration from config
    services_config = config.get_services_config()
    
    # Get current container status from docker_manager
    container_status = docker_manager.get_container_status()
    
    # Build result dictionary by service type
    for service_type, services in services_config.items():
        result[service_type] = {}
        
        for service_name, enabled in services.items():
            # Find matching container if it exists
            container_info = container_status.get(service_name, None)
            
            # Create service info dictionary
            service_info = {
                "name": service_name,
                "enabled": enabled,
                "description": SERVICE_DESCRIPTIONS.get(service_name, "Unknown service"),
                "default_port": DEFAULT_PORTS.get(service_name),
                "docker_image": DOCKER_IMAGES.get(service_name),
                "status": "not_installed"
            }
            
            # Add container status if available
            if container_info:
                service_info.update({
                    "status": container_info.get("status", "unknown"),
                    "url": container_info.get("url"),
                    "ports": container_info.get("ports", [])
                })
            
            # Add to result
            result[service_type][service_name] = service_info
    
    return result


def toggle_service(service_name: str, enabled: bool) -> Dict[str, Any]:
    """
    Enable or disable a service in the configuration.
    
    Args:
        service_name (str): The name of the service to toggle.
        enabled (bool): Whether the service should be enabled or disabled.
    
    Returns:
        Dict[str, Any]: Dictionary with status and message.
    """
    try:
        # Get current services configuration
        services_config = config.get_services_config()
        
        # Find the service in the configuration
        found = False
        for service_type, services in services_config.items():
            if service_name in services:
                services_config[service_type][service_name] = enabled
                found = True
                break
        
        if not found:
            return {
                "status": "error", 
                "message": f"Service '{service_name}' not found in configuration"
            }
        
        # Save updated configuration
        config.save_services_config(services_config)
        
        return {
            "status": "success",
            "message": f"Service '{service_name}' {'enabled' if enabled else 'disabled'} successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error toggling service: {str(e)}"
        }


def get_service_compatibility() -> Dict[str, Any]:
    """
    Check system compatibility with various services.
    
    Returns:
        Dict[str, Any]: Dictionary with compatibility information.
    """
    # Get system information to check compatibility
    try:
        import psutil
        from src.core import system_info
        
        # Get system information
        sys_info = system_info.get_system_info()
        
        # Get memory information
        memory_gb = sys_info.get("memory", {}).get("total_gb", 0)
        
        # Check CPU architecture
        architecture = sys_info.get("architecture", "")
        is_arm = "arm" in architecture.lower()
        is_arm64 = "aarch64" in architecture.lower() or "arm64" in architecture.lower()
        is_x86 = "x86" in architecture.lower()
        is_x86_64 = "x86_64" in architecture.lower() or "amd64" in architecture.lower()
        
        # Check for Raspberry Pi specific information
        is_raspberry_pi = sys_info.get("raspberry_pi", {}).get("is_raspberry_pi", False)
        pi_model = sys_info.get("raspberry_pi", {}).get("model", "Unknown")
        
        # Transcoding capabilities
        transcoding = sys_info.get("transcoding", {})
        has_hw_transcoding = any([
            transcoding.get("vaapi_available", False),
            transcoding.get("nvdec_available", False),
            transcoding.get("v4l2_available", False)
        ])
        
        # Calculate service compatibility based on system specifications
        # These are general guidelines and can be adjusted
        compatibility = {
            "media_servers": {
                "jellyfin": {
                    "compatible": True,  # Jellyfin works on all platforms
                    "recommended": True,
                    "notes": "Recommended for ARM platforms" if is_arm else "Full compatibility"
                },
                "plex": {
                    "compatible": is_x86_64 or is_arm64,  # Plex needs ARM64 or x86_64
                    "recommended": is_x86_64 and memory_gb >= 4 and has_hw_transcoding,
                    "notes": "Limited transcoding on ARM platforms" if is_arm else "Full compatibility"
                },
                "emby": {
                    "compatible": is_x86_64 or is_arm64,
                    "recommended": is_x86_64 and memory_gb >= 4,
                    "notes": "Limited transcoding on ARM platforms" if is_arm else "Full compatibility"
                }
            },
            "arr_apps": {
                "sonarr": {"compatible": True, "recommended": True, "notes": "Core service"},
                "radarr": {"compatible": True, "recommended": True, "notes": "Core service"},
                "prowlarr": {"compatible": True, "recommended": True, "notes": "Core service"},
                "lidarr": {
                    "compatible": True,
                    "recommended": memory_gb >= 2,
                    "notes": "May be memory-intensive"
                },
                "readarr": {
                    "compatible": True,
                    "recommended": memory_gb >= 2,
                    "notes": "May be memory-intensive"
                },
                "bazarr": {
                    "compatible": True,
                    "recommended": memory_gb >= 2,
                    "notes": "CPU intensive during subtitle extraction"
                }
            },
            "download_clients": {
                "transmission": {"compatible": True, "recommended": True, "notes": "Lightweight and efficient"},
                "qbittorrent": {
                    "compatible": True,
                    "recommended": memory_gb >= 2,
                    "notes": "More features but higher resource usage than Transmission"
                },
                "nzbget": {"compatible": True, "recommended": True, "notes": "Lightweight Usenet client"},
                "sabnzbd": {
                    "compatible": True,
                    "recommended": memory_gb >= 2,
                    "notes": "More features but higher resource usage than NZBGet"
                },
                "jdownloader": {
                    "compatible": is_x86_64 or is_arm64,
                    "recommended": memory_gb >= 2,
                    "notes": "Java-based, higher memory usage"
                }
            },
            "utilities": {
                "portainer": {"compatible": True, "recommended": True, "notes": "Lightweight Docker management"},
                "heimdall": {"compatible": True, "recommended": True, "notes": "Lightweight dashboard"},
                "overseerr": {
                    "compatible": is_x86_64 or is_arm64,
                    "recommended": memory_gb >= 2,
                    "notes": "Media request management"
                },
                "tautulli": {
                    "compatible": True,
                    "recommended": memory_gb >= 1,
                    "notes": "Plex monitoring and statistics"
                },
                "nginx_proxy_manager": {
                    "compatible": True,
                    "recommended": True,
                    "notes": "Web proxy and SSL management"
                },
                "get_iplayer": {
                    "compatible": True,
                    "recommended": True,
                    "notes": "BBC content downloader"
                }
            }
        }
        
        return {
            "status": "success",
            "system_info": {
                "architecture": architecture,
                "memory_gb": memory_gb,
                "is_raspberry_pi": is_raspberry_pi,
                "pi_model": pi_model if is_raspberry_pi else None,
                "has_hw_transcoding": has_hw_transcoding
            },
            "compatibility": compatibility
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error checking service compatibility: {str(e)}"
        }


def generate_docker_compose() -> Dict[str, Any]:
    """
    Generate Docker Compose file based on selected services.
    
    Returns:
        Dict[str, Any]: Dictionary with status, message, and compose file content.
    """
    try:
        # Get services and system configuration
        services_config = config.get_services_config()
        system_config = config.get_config()
        
        # Generate docker-compose content
        compose = {
            "version": "3.7",
            "services": {},
            "networks": {
                "container_network": {
                    "driver": "bridge"
                }
            },
            "volumes": {}
        }
        
        # Define common environment variables
        common_env = {
            "PUID": str(system_config.get("puid", 1000)),
            "PGID": str(system_config.get("pgid", 1000)),
            "TZ": system_config.get("timezone", "UTC")
        }
        
        # Define common volume mappings
        media_dir = system_config.get("media_dir", "/mnt/media")
        downloads_dir = system_config.get("downloads_dir", "/mnt/downloads")
        docker_dir = system_config.get("docker_dir", os.path.expanduser("~/docker"))
        
        # Add volumes for persistent data
        compose["volumes"]["config"] = {"driver": "local"}
        
        # Process VPN container first if enabled
        vpn_config = system_config.get("vpn", {})
        if vpn_config.get("enabled", False):
            compose["services"]["gluetun"] = {
                "container_name": "gluetun",
                "image": DOCKER_IMAGES["gluetun"],
                "cap_add": ["NET_ADMIN"],
                "devices": ["net/tun"],
                "ports": [], # Will be filled with ports from download clients
                "environment": {
                    **common_env,
                    "VPN_SERVICE_PROVIDER": vpn_config.get("provider", "private internet access"),
                    "OPENVPN_USER": vpn_config.get("username", ""),
                    "OPENVPN_PASSWORD": vpn_config.get("password", ""),
                    "SERVER_REGIONS": vpn_config.get("region", "Netherlands")
                },
                "volumes": [
                    "config:/gluetun"
                ],
                "restart": "unless-stopped",
                "networks": ["container_network"]
            }
        
        # Process Download Clients
        for client_name, enabled in services_config["download_clients"].items():
            if enabled and client_name in DOCKER_IMAGES:
                service_config = {
                    "container_name": client_name,
                    "image": DOCKER_IMAGES[client_name],
                    "environment": common_env.copy(),
                    "volumes": [
                        f"{docker_dir}/{client_name}:/config",
                        f"{downloads_dir}:/downloads"
                    ],
                    "restart": "unless-stopped",
                    "networks": ["container_network"]
                }
                
                # Set appropriate ports
                if client_name in DEFAULT_PORTS:
                    host_port = DEFAULT_PORTS[client_name]
                    
                    # If VPN is enabled, expose port through VPN container
                    if vpn_config.get("enabled", False):
                        # Add port to VPN container
                        vpn_port_mapping = f"{host_port}:{host_port}"
                        if vpn_port_mapping not in compose["services"]["gluetun"].get("ports", []):
                            compose["services"]["gluetun"]["ports"].append(vpn_port_mapping)
                        
                        # Set this container to use the VPN network
                        service_config["network_mode"] = "service:gluetun"
                        # Remove the normal networks since we're using network_mode
                        if "networks" in service_config:
                            del service_config["networks"]
                    else:
                        # Normal port exposure
                        service_config["ports"] = [f"{host_port}:{host_port}"]                
                
                # Add service to compose file
                compose["services"][client_name] = service_config
        
        # Process Media Servers
        for server_name, enabled in services_config["media_servers"].items():
            if enabled and server_name in DOCKER_IMAGES:
                service_config = {
                    "container_name": server_name,
                    "image": DOCKER_IMAGES[server_name],
                    "environment": common_env.copy(),
                    "volumes": [
                        f"{docker_dir}/{server_name}:/config",
                        f"{media_dir}:/media"
                    ],
                    "restart": "unless-stopped",
                    "networks": ["container_network"]
                }
                
                # Add ports
                if server_name in DEFAULT_PORTS:
                    service_config["ports"] = [f"{DEFAULT_PORTS[server_name]}:{DEFAULT_PORTS[server_name]}"]                
                
                # Add any special configurations for specific servers
                if server_name == "jellyfin":
                    # Add devices for hardware acceleration if available
                    from src.core import system_info
                    sys_info = system_info.get_system_info()
                    transcoding = sys_info.get("transcoding", {})
                    
                    if transcoding.get("vaapi_available", False):
                        service_config["devices"] = ["/dev/dri:/dev/dri"]
                    elif transcoding.get("v4l2_available", False):
                        service_config["devices"] = ["/dev/video10:/dev/video10"]
                    elif transcoding.get("nvdec_available", False):
                        service_config["runtime"] = "nvidia"
                        service_config["environment"]["NVIDIA_VISIBLE_DEVICES"] = "all"
                
                # Add service to compose file
                compose["services"][server_name] = service_config
        
        # Process Arr Apps
        for app_name, enabled in services_config["arr_apps"].items():
            if enabled and app_name in DOCKER_IMAGES:
                service_config = {
                    "container_name": app_name,
                    "image": DOCKER_IMAGES[app_name],
                    "environment": common_env.copy(),
                    "volumes": [
                        f"{docker_dir}/{app_name}:/config",
                        f"{media_dir}:/media",
                        f"{downloads_dir}:/downloads"
                    ],
                    "restart": "unless-stopped",
                    "networks": ["container_network"]
                }
                
                # Add ports
                if app_name in DEFAULT_PORTS:
                    service_config["ports"] = [f"{DEFAULT_PORTS[app_name]}:{DEFAULT_PORTS[app_name]}"]                
                
                # Add service to compose file
                compose["services"][app_name] = service_config
        
        # Process Utilities
        for util_name, enabled in services_config["utilities"].items():
            if enabled and util_name in DOCKER_IMAGES:
                service_config = {
                    "container_name": util_name,
                    "image": DOCKER_IMAGES[util_name],
                    "environment": common_env.copy(),
                    "volumes": [f"{docker_dir}/{util_name}:/config"],
                    "restart": "unless-stopped",
                    "networks": ["container_network"]
                }
                
                # Add ports
                if util_name in DEFAULT_PORTS:
                    service_config["ports"] = [f"{DEFAULT_PORTS[util_name]}:{DEFAULT_PORTS[util_name]}"]                
                
                # Specific configurations for utilities
                if util_name == "portainer":
                    service_config["volumes"].append("/var/run/docker.sock:/var/run/docker.sock")
                elif util_name == "nginx_proxy_manager":
                    service_config["volumes"].extend([
                        "./data:/data",
                        "./letsencrypt:/etc/letsencrypt"
                    ])
                
                # Add service to compose file
                compose["services"][util_name] = service_config
        
        # Process Tailscale if enabled
        tailscale_config = system_config.get("tailscale", {})
        if tailscale_config.get("enabled", False):
            compose["services"]["tailscale"] = {
                "container_name": "tailscale",
                "image": DOCKER_IMAGES["tailscale"],
                "cap_add": ["NET_ADMIN"],
                "environment": {
                    **common_env,
                    "TS_AUTH_KEY": tailscale_config.get("auth_key", "")
                },
                "volumes": [
                    "./tailscale:/var/lib/tailscale"
                ],
                "restart": "unless-stopped",
                "network_mode": "host"
            }
        
        # Convert to YAML
        import yaml
        
        # Custom dumper to avoid unwanted anchors and aliases
        class NoAliasDumper(yaml.SafeDumper):
            def ignore_aliases(self, data):
                return True
        
        compose_yaml = yaml.dump(compose, default_flow_style=False, sort_keys=False, Dumper=NoAliasDumper)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.yml') as tmp_file:
            tmp_file.write(compose_yaml)
            tmp_path = tmp_file.name
        
        # Return success with the compose file content
        return {
            "status": "success",
            "message": "Docker Compose file generated successfully",
            "compose_file": compose_yaml,
            "temp_file_path": tmp_path
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating Docker Compose file: {str(e)}"
        }


def generate_env_file() -> Dict[str, Any]:
    """
    Generate environment file for Docker Compose based on configuration.
    
    Returns:
        Dict[str, Any]: Dictionary with status, message, and env file content.
    """
    try:
        # Get system configuration
        system_config = config.get_config()
        
        # Generate .env file content
        env_content = f"""# Generated by Pi-PVARR
# Base Configuration
PUID={system_config.get('puid', 1000)}
PGID={system_config.get('pgid', 1000)}
TIMEZONE={system_config.get('timezone', 'UTC')}
IMAGE_RELEASE=latest
DOCKER_DIR={system_config.get('docker_dir', os.path.expanduser('~/docker'))}

# Media and Download Directories
MEDIA_DIR={system_config.get('media_dir', '/mnt/media')}
DOWNLOADS_DIR={system_config.get('downloads_dir', '/mnt/downloads')}
WATCH_DIR={system_config.get('downloads_dir', '/mnt/downloads')}/watch

# VPN Configuration
"""
        
        # Add VPN configuration if enabled
        vpn_config = system_config.get("vpn", {})
        if vpn_config.get("enabled", False):
            env_content += f"""VPN_CONTAINER=gluetun
VPN_IMAGE=qmcgaw/gluetun
VPN_SERVICE_PROVIDER={vpn_config.get('provider', 'private internet access')}
OPENVPN_USER={vpn_config.get('username', '')}
OPENVPN_PASSWORD={vpn_config.get('password', '')}
SERVER_REGIONS={vpn_config.get('region', 'Netherlands')}

"""
        
        # Add Tailscale configuration if enabled
        tailscale_config = system_config.get("tailscale", {})
        if tailscale_config.get("enabled", False):
            env_content += f"""# Tailscale
TAILSCALE_AUTH_KEY={tailscale_config.get('auth_key', '')}

"""
        
        # Add network configuration
        env_content += """# Network Configuration
CONTAINER_NETWORK=container_network
"""
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmp_file:
            tmp_file.write(env_content)
            tmp_path = tmp_file.name
        
        # Return success with the env file content
        return {
            "status": "success",
            "message": ".env file generated successfully",
            "env_file": env_content,
            "temp_file_path": tmp_path
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating .env file: {str(e)}"
        }


def apply_service_changes() -> Dict[str, Any]:
    """
    Apply service changes by regenerating Docker Compose files and restarting services if needed.
    
    Returns:
        Dict[str, Any]: Dictionary with status and message.
    """
    try:
        # Generate Docker Compose file
        compose_result = generate_docker_compose()
        if compose_result["status"] != "success":
            return compose_result
        
        compose_file_path = compose_result["temp_file_path"]
        
        # Generate .env file
        env_result = generate_env_file()
        if env_result["status"] != "success":
            # Cleanup compose file
            if os.path.exists(compose_file_path):
                os.unlink(compose_file_path)
            return env_result
        
        env_file_path = env_result["temp_file_path"]
        
        # Get config directory
        config_dir = config.get_config_dir()
        
        # Create docker-compose directory if it doesn't exist
        docker_compose_dir = os.path.join(config_dir, "docker-compose")
        os.makedirs(docker_compose_dir, exist_ok=True)
        
        # Copy files to their destinations
        import shutil
        final_compose_path = os.path.join(docker_compose_dir, "docker-compose.yml")
        final_env_path = os.path.join(config_dir, ".env")
        
        shutil.copy(compose_file_path, final_compose_path)
        shutil.copy(env_file_path, final_env_path)
        
        # Cleanup temporary files
        os.unlink(compose_file_path)
        os.unlink(env_file_path)
        
        # Update system configuration with installation status
        system_config = config.get_config()
        system_config["installation_status"] = "configured"
        config.save_config_wrapper(system_config)
        
        return {
            "status": "success",
            "message": "Service changes applied successfully",
            "docker_compose_path": final_compose_path,
            "env_path": final_env_path
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error applying service changes: {str(e)}"
        }


def get_docker_compose_cmd() -> str:
    """
    Get the appropriate Docker Compose command for the system.
    
    Returns:
        str: Docker Compose command ('docker compose' or 'docker-compose').
    """
    try:
        # Check if 'docker compose' is available (Docker with built-in compose)
        result = subprocess.run(
            ["docker", "compose", "version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        
        if result.returncode == 0:
            return "docker compose"
        
        # Check if 'docker-compose' is available (standalone compose)
        result = subprocess.run(
            ["docker-compose", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        
        if result.returncode == 0:
            return "docker-compose"
        
        # Default to 'docker compose'
        return "docker compose"
    except Exception:
        # Default to 'docker compose'
        return "docker compose"


def start_services() -> Dict[str, Any]:
    """
    Start services using Docker Compose.
    
    Returns:
        Dict[str, Any]: Dictionary with status and message.
    """
    try:
        # Get configuration directory
        config_dir = config.get_config_dir()
        
        # Check if docker-compose.yml exists
        docker_compose_file = os.path.join(config_dir, "docker-compose", "docker-compose.yml")
        if not os.path.exists(docker_compose_file):
            # Try to generate it first
            apply_result = apply_service_changes()
            if apply_result["status"] != "success":
                return apply_result
            docker_compose_file = apply_result["docker_compose_path"]
        
        # Get Docker Compose command
        compose_cmd = get_docker_compose_cmd()
        
        # Build command
        cmd = f"{compose_cmd} -f {docker_compose_file} up -d"
        
        # Run the command
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            # Update system configuration with installation status
            system_config = config.get_config()
            system_config["installation_status"] = "running"
            config.save_config_wrapper(system_config)
            
            return {
                "status": "success",
                "message": "Services started successfully",
                "output": stdout
            }
        else:
            return {
                "status": "error",
                "message": f"Error starting services: {stderr}",
                "output": stderr
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error starting services: {str(e)}"
        }


def stop_services() -> Dict[str, Any]:
    """
    Stop services using Docker Compose.
    
    Returns:
        Dict[str, Any]: Dictionary with status and message.
    """
    try:
        # Get configuration directory
        config_dir = config.get_config_dir()
        
        # Check if docker-compose.yml exists
        docker_compose_file = os.path.join(config_dir, "docker-compose", "docker-compose.yml")
        if not os.path.exists(docker_compose_file):
            return {
                "status": "error",
                "message": "Docker Compose file not found"
            }
        
        # Get Docker Compose command
        compose_cmd = get_docker_compose_cmd()
        
        # Build command
        cmd = f"{compose_cmd} -f {docker_compose_file} down"
        
        # Run the command
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            # Update system configuration with installation status
            system_config = config.get_config()
            system_config["installation_status"] = "configured"
            config.save_config_wrapper(system_config)
            
            return {
                "status": "success",
                "message": "Services stopped successfully",
                "output": stdout
            }
        else:
            return {
                "status": "error",
                "message": f"Error stopping services: {stderr}",
                "output": stderr
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error stopping services: {str(e)}"
        }


def restart_services() -> Dict[str, Any]:
    """
    Restart services using Docker Compose.
    
    Returns:
        Dict[str, Any]: Dictionary with status and message.
    """
    try:
        # Get configuration directory
        config_dir = config.get_config_dir()
        
        # Check if docker-compose.yml exists
        docker_compose_file = os.path.join(config_dir, "docker-compose", "docker-compose.yml")
        if not os.path.exists(docker_compose_file):
            # Try to generate it first
            apply_result = apply_service_changes()
            if apply_result["status"] != "success":
                return apply_result
            docker_compose_file = apply_result["docker_compose_path"]
        
        # Get Docker Compose command
        compose_cmd = get_docker_compose_cmd()
        
        # Build command
        cmd = f"{compose_cmd} -f {docker_compose_file} restart"
        
        # Run the command
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            return {
                "status": "success",
                "message": "Services restarted successfully",
                "output": stdout
            }
        else:
            return {
                "status": "error",
                "message": f"Error restarting services: {stderr}",
                "output": stderr
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error restarting services: {str(e)}"
        }


def get_installation_status() -> Dict[str, Any]:
    """
    Get the current installation status.
    
    Returns:
        Dict[str, Any]: Dictionary with installation status information.
    """
    try:
        # Get system configuration
        system_config = config.get_config()
        
        # Get current status
        status = system_config.get("installation_status", "not_started")
        
        # Get docker-compose file path
        config_dir = config.get_config_dir()
        docker_compose_file = os.path.join(config_dir, "docker-compose", "docker-compose.yml")
        compose_exists = os.path.exists(docker_compose_file)
        
        # Get service information
        service_info = get_service_info()
        
        # Get active services count
        active_services = 0
        for service_type, services in service_info.items():
            for service_name, info in services.items():
                if info.get("status") == "running":
                    active_services += 1
        
        # Get total enabled services count
        enabled_services = 0
        for service_type, services in service_info.items():
            for service_name, info in services.items():
                if info.get("enabled", False):
                    enabled_services += 1
        
        return {
            "status": "success",
            "installation_status": status,
            "compose_file_exists": compose_exists,
            "active_services": active_services,
            "enabled_services": enabled_services,
            "service_info": service_info
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error getting installation status: {str(e)}"
        }