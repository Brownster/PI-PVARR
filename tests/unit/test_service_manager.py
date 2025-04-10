"""
Unit tests for the service_manager module.
"""

import os
import json
import tempfile
import yaml
import pytest
from unittest.mock import patch, MagicMock, mock_open

from src.core import service_manager


@pytest.fixture
def mock_services_config():
    """Fixture providing sample services configuration."""
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
            "nzbget": True,
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
            "get_iplayer": True
        }
    }


@pytest.fixture
def mock_system_config():
    """Fixture providing sample system configuration."""
    return {
        "puid": 1000,
        "pgid": 1000,
        "timezone": "Europe/London",
        "media_dir": "/mnt/media",
        "downloads_dir": "/mnt/downloads",
        "docker_dir": "/home/user/docker",
        "vpn": {
            "enabled": True,
            "provider": "private internet access",
            "username": "testuser",
            "password": "testpass",
            "region": "Netherlands"
        },
        "tailscale": {
            "enabled": False,
            "auth_key": ""
        },
        "installation_status": "not_started"
    }


@pytest.fixture
def mock_container_status():
    """Fixture providing sample container status."""
    return {
        "sonarr": {
            "status": "running",
            "ports": [{"container": "8989", "host": "8989", "protocol": "tcp"}],
            "type": "media",
            "description": "TV Series Management",
            "url": "http://localhost:8989"
        },
        "radarr": {
            "status": "running",
            "ports": [{"container": "7878", "host": "7878", "protocol": "tcp"}],
            "type": "media",
            "description": "Movie Management",
            "url": "http://localhost:7878"
        },
        "prowlarr": {
            "status": "running",
            "ports": [{"container": "9696", "host": "9696", "protocol": "tcp"}],
            "type": "media",
            "description": "Indexer Management",
            "url": "http://localhost:9696"
        },
        "transmission": {
            "status": "running",
            "ports": [{"container": "9091", "host": "9091", "protocol": "tcp"}],
            "type": "download",
            "description": "Torrent Client",
            "url": "http://localhost:9091"
        },
        "nzbget": {
            "status": "stopped",
            "ports": [{"container": "6789", "host": "6789", "protocol": "tcp"}],
            "type": "download",
            "description": "Usenet Client",
            "url": None
        },
        "jellyfin": {
            "status": "running",
            "ports": [{"container": "8096", "host": "8096", "protocol": "tcp"}],
            "type": "media",
            "description": "Media Server",
            "url": "http://localhost:8096"
        },
        "portainer": {
            "status": "running",
            "ports": [{"container": "9000", "host": "9000", "protocol": "tcp"}],
            "type": "utility",
            "description": "Docker Management",
            "url": "http://localhost:9000"
        },
        "get_iplayer": {
            "status": "running",
            "ports": [{"container": "1935", "host": "1935", "protocol": "tcp"}],
            "type": "utility",
            "description": "BBC Content Downloader",
            "url": "http://localhost:1935"
        }
    }


@pytest.fixture
def mock_system_info():
    """Fixture providing sample system information."""
    return {
        "hostname": "raspberry-pi",
        "architecture": "aarch64",
        "memory": {
            "total_gb": 4,
            "available_gb": 2.5
        },
        "raspberry_pi": {
            "is_raspberry_pi": True,
            "model": "Raspberry Pi 4 Model B Rev 1.2"
        },
        "transcoding": {
            "vaapi_available": False,
            "nvdec_available": False,
            "v4l2_available": True,
            "recommended_method": "v4l2"
        }
    }


class TestServiceManager:
    """Tests for service_manager module."""

    def test_get_service_info(self, mock_services_config, mock_container_status):
        """Test get_service_info function."""
        with patch('src.core.config.get_services_config', return_value=mock_services_config), \
             patch('src.core.docker_manager.get_container_status', return_value=mock_container_status):
            result = service_manager.get_service_info()
            
            # Check structure
            assert isinstance(result, dict)
            assert set(result.keys()) == set(["arr_apps", "download_clients", "media_servers", "utilities"])
            
            # Check that the result contains all services from the configuration
            assert "sonarr" in result["arr_apps"]
            assert "transmission" in result["download_clients"]
            assert "jellyfin" in result["media_servers"]
            assert "portainer" in result["utilities"]
            
            # Check that container status is integrated
            assert result["arr_apps"]["sonarr"]["status"] == "running"
            assert result["arr_apps"]["sonarr"]["url"] == "http://localhost:8989"
            assert result["download_clients"]["nzbget"]["status"] == "stopped"
            
            # Check that non-running containers still have basic info
            assert result["arr_apps"]["lidarr"]["enabled"] is False
            assert result["arr_apps"]["lidarr"]["status"] == "not_installed"
            assert "url" not in result["arr_apps"]["lidarr"]
    
    def test_toggle_service_enable(self, mock_services_config):
        """Test toggle_service function to enable a service."""
        with patch('src.core.config.get_services_config', return_value=mock_services_config), \
             patch('src.core.config.save_services_config') as mock_save:
            # Toggle service from False to True
            result = service_manager.toggle_service("lidarr", True)
            
            assert result["status"] == "success"
            assert "lidarr" in result["message"]
            assert "enabled" in result["message"]
            
            # Verify save was called with updated config
            updated_config = mock_services_config.copy()
            updated_config["arr_apps"]["lidarr"] = True
            mock_save.assert_called_once()
            assert mock_save.call_args[0][0]["arr_apps"]["lidarr"] is True
    
    def test_toggle_service_disable(self, mock_services_config):
        """Test toggle_service function to disable a service."""
        with patch('src.core.config.get_services_config', return_value=mock_services_config), \
             patch('src.core.config.save_services_config') as mock_save:
            # Toggle service from True to False
            result = service_manager.toggle_service("sonarr", False)
            
            assert result["status"] == "success"
            assert "sonarr" in result["message"]
            assert "disabled" in result["message"]
            
            # Verify save was called with updated config
            mock_save.assert_called_once()
            assert mock_save.call_args[0][0]["arr_apps"]["sonarr"] is False
    
    def test_toggle_service_not_found(self, mock_services_config):
        """Test toggle_service function with a non-existent service."""
        with patch('src.core.config.get_services_config', return_value=mock_services_config):
            result = service_manager.toggle_service("non_existent_service", True)
            
            assert result["status"] == "error"
            assert "not found" in result["message"]
    
    def test_get_service_compatibility(self, mock_system_info):
        """Test get_service_compatibility function."""
        with patch('src.core.system_info.get_system_info', return_value=mock_system_info):
            result = service_manager.get_service_compatibility()
            
            assert result["status"] == "success"
            assert "system_info" in result
            assert "compatibility" in result
            assert "is_raspberry_pi" in result["system_info"]
            assert result["system_info"]["is_raspberry_pi"] is True
            
            # Check that compatibility info is present for services
            assert "media_servers" in result["compatibility"]
            assert "arr_apps" in result["compatibility"]
            assert "download_clients" in result["compatibility"]
            assert "utilities" in result["compatibility"]
            
            # Check compatibility for specific services
            assert result["compatibility"]["media_servers"]["jellyfin"]["compatible"] is True
            assert result["compatibility"]["media_servers"]["jellyfin"]["recommended"] is True
            
            # Plex is not ideal for Pi but should be compatible on ARM64
            assert result["compatibility"]["media_servers"]["plex"]["compatible"] is True
            # But not recommended without more memory and transcoding
            assert result["compatibility"]["media_servers"]["plex"]["recommended"] is False
            
            # Core services should always be compatible
            assert result["compatibility"]["arr_apps"]["sonarr"]["compatible"] is True
            assert result["compatibility"]["download_clients"]["transmission"]["compatible"] is True
    
    def test_generate_docker_compose(self, mock_services_config, mock_system_config):
        """Test generate_docker_compose function."""
        with patch('src.core.config.get_services_config', return_value=mock_services_config), \
             patch('src.core.config.get_config', return_value=mock_system_config), \
             patch('tempfile.NamedTemporaryFile') as mock_tempfile, \
             patch('yaml.dump', return_value="dummy yaml content"):
            
            # Setup mock temporary file
            mock_file = MagicMock()
            mock_file.name = "/tmp/test-docker-compose.yml"
            mock_tempfile.return_value.__enter__.return_value = mock_file
            
            result = service_manager.generate_docker_compose()
            
            assert result["status"] == "success"
            assert result["message"] == "Docker Compose file generated successfully"
            assert "compose_file" in result
            assert result["temp_file_path"] == "/tmp/test-docker-compose.yml"
            
            # Verify file was written
            mock_file.write.assert_called_once()
    
    def test_generate_env_file(self, mock_system_config):
        """Test generate_env_file function."""
        with patch('src.core.config.get_config', return_value=mock_system_config), \
             patch('tempfile.NamedTemporaryFile') as mock_tempfile:
            
            # Setup mock temporary file
            mock_file = MagicMock()
            mock_file.name = "/tmp/test.env"
            mock_tempfile.return_value.__enter__.return_value = mock_file
            
            result = service_manager.generate_env_file()
            
            assert result["status"] == "success"
            assert result["message"] == ".env file generated successfully"
            assert "env_file" in result
            assert result["temp_file_path"] == "/tmp/test.env"
            
            # Verify env file contains expected variables
            env_content = result["env_file"]
            assert "PUID=1000" in env_content
            assert "PGID=1000" in env_content
            assert "TIMEZONE=Europe/London" in env_content
            assert "MEDIA_DIR=/mnt/media" in env_content
            assert "DOWNLOADS_DIR=/mnt/downloads" in env_content
            
            # VPN config should be included since it's enabled
            assert "VPN_CONTAINER=gluetun" in env_content
            assert "OPENVPN_USER=testuser" in env_content
            
            # Tailscale should not be included since it's disabled
            assert "TAILSCALE_AUTH_KEY=" not in env_content
    
    def test_apply_service_changes(self, mock_services_config, mock_system_config):
        """Test apply_service_changes function."""
        compose_file_path = "/tmp/test-docker-compose.yml"
        env_file_path = "/tmp/test.env"
        config_dir = "/home/user/.config/pi-pvarr"
        
        with patch('src.core.service_manager.generate_docker_compose') as mock_generate_compose, \
             patch('src.core.service_manager.generate_env_file') as mock_generate_env, \
             patch('src.core.config.get_config_dir', return_value=config_dir), \
             patch('os.makedirs') as mock_makedirs, \
             patch('shutil.copy') as mock_copy, \
             patch('os.unlink') as mock_unlink, \
             patch('src.core.config.get_config', return_value=mock_system_config), \
             patch('src.core.config.save_config_wrapper') as mock_save:
            
            # Setup mock returns
            mock_generate_compose.return_value = {
                "status": "success",
                "message": "Docker Compose file generated successfully",
                "compose_file": "dummy yaml content",
                "temp_file_path": compose_file_path
            }
            
            mock_generate_env.return_value = {
                "status": "success", 
                "message": ".env file generated successfully",
                "env_file": "dummy env content",
                "temp_file_path": env_file_path
            }
            
            result = service_manager.apply_service_changes()
            
            assert result["status"] == "success"
            assert result["message"] == "Service changes applied successfully"
            assert "docker_compose_path" in result
            assert "env_path" in result
            
            # Verify directories were created
            mock_makedirs.assert_called_with(os.path.join(config_dir, "docker-compose"), exist_ok=True)
            
            # Verify files were copied and cleaned up
            assert mock_copy.call_count == 2
            assert mock_unlink.call_count == 2
            
            # Verify config was updated
            mock_save.assert_called_once()
            updated_config = mock_system_config.copy()
            updated_config["installation_status"] = "configured"
            assert mock_save.call_args[0][0]["installation_status"] == "configured"
    
    def test_get_docker_compose_cmd_builtin(self):
        """Test get_docker_compose_cmd with built-in Docker Compose."""
        with patch('subprocess.run') as mock_run:
            # Mock successful 'docker compose' command
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_run.return_value = mock_process
            
            cmd = service_manager.get_docker_compose_cmd()
            assert cmd == "docker compose"
            
            # Verify 'docker compose' was checked
            mock_run.assert_called_with(
                ["docker", "compose", "version"],
                stdout=-1,
                stderr=-1,
                check=False
            )
    
    def test_get_docker_compose_cmd_standalone(self):
        """Test get_docker_compose_cmd with standalone docker-compose."""
        with patch('subprocess.run') as mock_run:
            # Mock failure of 'docker compose' but success of 'docker-compose'
            mock_run.side_effect = [
                # First call fails (docker compose)
                MagicMock(returncode=1),
                # Second call succeeds (docker-compose)
                MagicMock(returncode=0)
            ]
            
            cmd = service_manager.get_docker_compose_cmd()
            assert cmd == "docker-compose"
            
            # Verify both commands were checked
            assert mock_run.call_count == 2
            mock_run.assert_any_call(
                ["docker", "compose", "version"],
                stdout=-1,
                stderr=-1,
                check=False
            )
            mock_run.assert_any_call(
                ["docker-compose", "--version"],
                stdout=-1,
                stderr=-1,
                check=False
            )
    
    def test_start_services_success(self):
        """Test start_services function with successful execution."""
        docker_compose_file = "/home/user/.config/pi-pvarr/docker-compose/docker-compose.yml"
        
        with patch('os.path.exists', return_value=True), \
             patch('src.core.config.get_config_dir', return_value="/home/user/.config/pi-pvarr"), \
             patch('src.core.service_manager.get_docker_compose_cmd', return_value="docker compose"), \
             patch('subprocess.Popen') as mock_popen, \
             patch('src.core.config.get_config', return_value={"installation_status": "configured"}), \
             patch('src.core.config.save_config_wrapper') as mock_save:
            
            # Mock successful process execution
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = ("Services started", "")
            mock_popen.return_value = mock_process
            
            result = service_manager.start_services()
            
            assert result["status"] == "success"
            assert result["message"] == "Services started successfully"
            assert result["output"] == "Services started"
            
            # Verify command was executed with correct parameters
            mock_popen.assert_called_with(
                f"docker compose -f {docker_compose_file} up -d",
                shell=True,
                stdout=-1,
                stderr=-1,
                text=True
            )
            
            # Verify status was updated
            mock_save.assert_called_once()
            assert mock_save.call_args[0][0]["installation_status"] == "running"
    
    def test_start_services_error(self):
        """Test start_services function with execution error."""
        # Unused but kept for context
        # docker_compose_file = "/home/user/.config/pi-pvarr/docker-compose/docker-compose.yml"
        
        with patch('os.path.exists', return_value=True), \
             patch('src.core.config.get_config_dir', return_value="/home/user/.config/pi-pvarr"), \
             patch('src.core.service_manager.get_docker_compose_cmd', return_value="docker compose"), \
             patch('subprocess.Popen') as mock_popen:
            
            # Mock failed process execution
            mock_process = MagicMock()
            mock_process.returncode = 1
            mock_process.communicate.return_value = ("", "Error starting services")
            mock_popen.return_value = mock_process
            
            result = service_manager.start_services()
            
            assert result["status"] == "error"
            assert "Error starting services" in result["message"]
            assert result["output"] == "Error starting services"
    
    def test_stop_services_success(self):
        """Test stop_services function with successful execution."""
        docker_compose_file = "/home/user/.config/pi-pvarr/docker-compose/docker-compose.yml"
        
        with patch('os.path.exists', return_value=True), \
             patch('src.core.config.get_config_dir', return_value="/home/user/.config/pi-pvarr"), \
             patch('src.core.service_manager.get_docker_compose_cmd', return_value="docker compose"), \
             patch('subprocess.Popen') as mock_popen, \
             patch('src.core.config.get_config', return_value={"installation_status": "running"}), \
             patch('src.core.config.save_config_wrapper') as mock_save:
            
            # Mock successful process execution
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = ("Services stopped", "")
            mock_popen.return_value = mock_process
            
            result = service_manager.stop_services()
            
            assert result["status"] == "success"
            assert result["message"] == "Services stopped successfully"
            assert result["output"] == "Services stopped"
            
            # Verify command was executed with correct parameters
            mock_popen.assert_called_with(
                f"docker compose -f {docker_compose_file} down",
                shell=True,
                stdout=-1,
                stderr=-1,
                text=True
            )
            
            # Verify status was updated
            mock_save.assert_called_once()
            assert mock_save.call_args[0][0]["installation_status"] == "configured"
    
    def test_restart_services_success(self):
        """Test restart_services function with successful execution."""
        docker_compose_file = "/home/user/.config/pi-pvarr/docker-compose/docker-compose.yml"
        
        with patch('os.path.exists', return_value=True), \
             patch('src.core.config.get_config_dir', return_value="/home/user/.config/pi-pvarr"), \
             patch('src.core.service_manager.get_docker_compose_cmd', return_value="docker compose"), \
             patch('subprocess.Popen') as mock_popen:
            
            # Mock successful process execution
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = ("Services restarted", "")
            mock_popen.return_value = mock_process
            
            result = service_manager.restart_services()
            
            assert result["status"] == "success"
            assert result["message"] == "Services restarted successfully"
            assert result["output"] == "Services restarted"
            
            # Verify command was executed with correct parameters
            mock_popen.assert_called_with(
                f"docker compose -f {docker_compose_file} restart",
                shell=True,
                stdout=-1,
                stderr=-1,
                text=True
            )
    
    def test_get_installation_status_fixed(self):
        """Test get_installation_status function with a simplified approach."""
        
        # Mock configuration
        mock_config = {"installation_status": "running"}
        
        # Create a direct mock for get_service_info outside the patch
        service_info_mock = {
            "arr_apps": {
                "sonarr": {"enabled": True, "status": "running"},
                "radarr": {"enabled": True, "status": "running"}
            },
            "download_clients": {
                "transmission": {"enabled": True, "status": "running"},
                "nzbget": {"enabled": True, "status": "stopped"}
            },
            "media_servers": {
                "jellyfin": {"enabled": True, "status": "running"}
            },
            "utilities": {
                "portainer": {"enabled": True, "status": "running"}
            }
        }
        
        # Create patches
        with patch('src.core.config.get_config', return_value=mock_config), \
             patch('src.core.config.get_config_dir', return_value="/home/user/.config/pi-pvarr"), \
             patch('os.path.exists', return_value=True), \
             patch('src.core.service_manager.get_service_info', return_value=service_info_mock):
            
            # Get the actual result
            result = service_manager.get_installation_status()
            
            # Test the basic result structure
            assert result["status"] == "success"
            assert result["installation_status"] == "running"
            assert result["compose_file_exists"] is True