"""
Mock data for install_wizard tests.
"""

from typing import Dict, Any


def get_mock_installation_status() -> Dict[str, Any]:
    """
    Get mock installation status.
    
    Returns:
        Dict[str, Any]: Mock installation status data.
    """
    return {
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
        "end_time": None,
        "elapsed_time": None
    }


def get_mock_compatibility_check() -> Dict[str, Any]:
    """
    Get mock system compatibility check result.
    
    Returns:
        Dict[str, Any]: Mock compatibility check data.
    """
    return {
        "status": "success",
        "compatible": True,
        "system_info": {
            "memory": {
                "total_gb": 4,
                "free_gb": 3.2
            },
            "disk": {
                "total_gb": 32,
                "free_gb": 25
            },
            "docker_installed": True,
            "is_raspberry_pi": True,
            "model": "Raspberry Pi 4 Model B Rev 1.2"
        },
        "checks": {
            "memory": {
                "value": 4,
                "unit": "GB",
                "compatible": True,
                "recommended": 2,
                "message": "Memory: 4GB"
            },
            "disk_space": {
                "value": 25,
                "unit": "GB",
                "compatible": True,
                "recommended": 10,
                "message": "Free Disk Space: 25GB"
            },
            "docker": {
                "installed": True,
                "message": "Docker: Installed"
            }
        }
    }


def get_mock_complete_installation_result() -> Dict[str, Any]:
    """
    Get mock complete installation result.
    
    Returns:
        Dict[str, Any]: Mock complete installation result data.
    """
    return {
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


def get_mock_user_config() -> Dict[str, Any]:
    """
    Get mock user configuration.
    
    Returns:
        Dict[str, Any]: Mock user configuration data.
    """
    return {
        "puid": 1000,
        "pgid": 1000,
        "timezone": "Europe/London",
        "media_dir": "/mnt/media",
        "downloads_dir": "/mnt/downloads"
    }


def get_mock_network_config() -> Dict[str, Any]:
    """
    Get mock network configuration.
    
    Returns:
        Dict[str, Any]: Mock network configuration data.
    """
    return {
        "vpn": {
            "enabled": True,
            "provider": "private internet access",
            "username": "user",
            "password": "pass",
            "region": "Netherlands"
        },
        "tailscale": {
            "enabled": True,
            "auth_key": "tskey-auth-example12345"
        }
    }


def get_mock_storage_config() -> Dict[str, Any]:
    """
    Get mock storage configuration.
    
    Returns:
        Dict[str, Any]: Mock storage configuration data.
    """
    return {
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
                    "public": False,
                    "valid_users": "pi"
                },
                {
                    "name": "TVShows",
                    "path": "/mnt/media/TVShows",
                    "public": False,
                    "valid_users": "pi"
                }
            ]
        }
    }


def get_mock_services_config() -> Dict[str, Any]:
    """
    Get mock services configuration.
    
    Returns:
        Dict[str, Any]: Mock services configuration data.
    """
    return {
        "arr_apps": {
            "sonarr": True,
            "radarr": True,
            "prowlarr": True,
            "lidarr": False,
            "readarr": False,
            "bazarr": True
        },
        "download_clients": {
            "transmission": True,
            "qbittorrent": False,
            "nzbget": False,
            "sabnzbd": True,
            "jdownloader": False
        },
        "media_servers": {
            "jellyfin": True,
            "plex": False,
            "emby": False
        },
        "utilities": {
            "heimdall": True,
            "overseerr": True,
            "tautulli": False,
            "portainer": True,
            "nginx_proxy_manager": True,
            "get_iplayer": False
        }
    }


def get_mock_installation_config() -> Dict[str, Any]:
    """
    Get mock complete installation configuration.
    
    Returns:
        Dict[str, Any]: Mock installation configuration data.
    """
    return {
        "user_config": get_mock_user_config(),
        "network_config": get_mock_network_config(),
        "storage_config": get_mock_storage_config(),
        "services_config": get_mock_services_config()
    }