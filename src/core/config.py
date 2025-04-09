"""
Configuration module for Pi-PVARR.

This module provides functions to manage configuration settings:
- Load and save configuration
- Default configuration values
- Configuration file paths
"""

import os
import json
import platform
from typing import Dict, Any, Optional


def get_config_dir() -> str:
    """
    Get the configuration directory path.
    
    Returns:
        str: Path to the configuration directory.
    """
    if platform.system() == 'Windows':
        # Windows config path
        base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
        return os.path.join(base_dir, 'Pi-PVARR')
    else:
        # Unix-like systems config path
        base_dir = os.environ.get('XDG_CONFIG_HOME', os.path.join(os.environ.get('HOME', '/'), '.config'))
        return os.path.join(base_dir, 'pi-pvarr')


def ensure_config_dir_exists(config_dir: str) -> None:
    """
    Ensure the configuration directory exists.
    
    Args:
        config_dir (str): The configuration directory path.
    """
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)


def get_default_config() -> Dict[str, Any]:
    """
    Get the default configuration values.
    
    Returns:
        Dict[str, Any]: Dictionary containing default configuration values.
    """
    home_dir = os.environ.get('HOME', '/home/pi')
    docker_dir = os.path.join(home_dir, 'docker')
    
    return {
        "puid": 1000,
        "pgid": 1000,
        "timezone": "UTC",
        "media_dir": "/mnt/media",
        "downloads_dir": "/mnt/downloads",
        "docker_dir": docker_dir,
        "vpn": {
            "enabled": True,
            "provider": "private internet access",
            "username": "",
            "password": "",
            "region": "Netherlands"
        },
        "tailscale": {
            "enabled": False,
            "auth_key": ""
        },
        "installation_status": "not_started"
    }


def get_default_services() -> Dict[str, Any]:
    """
    Get the default services configuration.
    
    Returns:
        Dict[str, Any]: Dictionary containing default services configuration.
    """
    return {
        "arr_apps": {
            "sonarr": True,
            "radarr": True,
            "prowlarr": True,
            "lidarr": False,
            "readarr": False,
            "bazarr": False
        },
        "download_clients": {
            "transmission": True,
            "qbittorrent": False,
            "nzbget": False,
            "sabnzbd": False,
            "jdownloader": False
        },
        "media_servers": {
            "jellyfin": True,
            "plex": False,
            "emby": False
        },
        "utilities": {
            "heimdall": False,
            "overseerr": False,
            "tautulli": False,
            "portainer": True,
            "nginx_proxy_manager": False,
            "get_iplayer": False
        }
    }


def load_config(config_file: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_file (str): Path to the configuration file.
    
    Returns:
        Dict[str, Any]: Dictionary containing configuration values.
    """
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # If there's an error reading the file, return default config
            pass
    
    # If file doesn't exist or there was an error reading it, return default config
    if config_file.endswith('services.json'):
        return get_default_services()
    else:
        return get_default_config()


def save_config(config: Dict[str, Any], config_file: str) -> None:
    """
    Save configuration to a JSON file.
    
    Args:
        config (Dict[str, Any]): The configuration to save.
        config_file (str): Path to the configuration file.
    """
    with open(config_file, 'w') as f:
        json_str = json.dumps(config, indent=2)
        f.write(json_str)


def get_config(filename: str = 'config.json') -> Dict[str, Any]:
    """
    Get the configuration.
    
    Args:
        filename (str, optional): Name of the configuration file. Defaults to 'config.json'.
    
    Returns:
        Dict[str, Any]: Dictionary containing configuration values.
    """
    config_dir = get_config_dir()
    ensure_config_dir_exists(config_dir)
    config_file = os.path.join(config_dir, filename)
    return load_config(config_file)


def save_config_wrapper(config: Dict[str, Any], filename: str = 'config.json') -> None:
    """
    Save the configuration to the appropriate file.
    
    Args:
        config (Dict[str, Any]): The configuration to save.
        filename (str, optional): Name of the configuration file. Defaults to 'config.json'.
    """
    config_dir = get_config_dir()
    ensure_config_dir_exists(config_dir)
    config_file = os.path.join(config_dir, filename)
    save_config(config, config_file)


def get_services_config() -> Dict[str, Any]:
    """
    Get the services configuration.
    
    Returns:
        Dict[str, Any]: Dictionary containing services configuration.
    """
    return get_config('services.json')


def save_services_config(services_config: Dict[str, Any]) -> None:
    """
    Save the services configuration.
    
    Args:
        services_config (Dict[str, Any]): The services configuration to save.
    """
    save_config_wrapper(services_config, 'services.json')