"""
Unit tests for the installation wizard API endpoints.
"""

import json
import pytest
from unittest.mock import patch, MagicMock

from src.api.server import create_app


@pytest.fixture
def client():
    """Test client fixture."""
    app = create_app({"TESTING": True})
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_installation_status():
    """Fixture with mock installation status."""
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


@pytest.fixture
def mock_compatibility_check():
    """Fixture with mock system compatibility check result."""
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


@pytest.fixture
def mock_basic_config_result():
    """Fixture with mock basic configuration setup result."""
    return {
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


@pytest.fixture
def mock_network_config_result():
    """Fixture with mock network configuration setup result."""
    return {
        "status": "success",
        "message": "Network configuration setup completed",
        "config": {
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
    }


@pytest.fixture
def mock_storage_config_result():
    """Fixture with mock storage configuration setup result."""
    return {
        "status": "success",
        "message": "Storage configuration setup completed",
        "config": {
            "media_dir": "/mnt/media",
            "downloads_dir": "/mnt/downloads"
        }
    }


@pytest.fixture
def mock_service_selection_result():
    """Fixture with mock service selection setup result."""
    return {
        "status": "success",
        "message": "Service selection setup completed",
        "services": {
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
    }


@pytest.fixture
def mock_dependencies_result():
    """Fixture with mock dependencies installation result."""
    return {
        "status": "success",
        "message": "Dependency installation completed"
    }


@pytest.fixture
def mock_docker_setup_result():
    """Fixture with mock Docker setup result."""
    return {
        "status": "success",
        "message": "Docker setup completed successfully"
    }


@pytest.fixture
def mock_compose_files_result():
    """Fixture with mock Docker Compose files generation result."""
    return {
        "status": "success",
        "message": "Docker Compose configuration completed",
        "docker_compose_path": "/home/pi/docker/docker-compose.yml",
        "env_path": "/home/pi/docker/.env"
    }


@pytest.fixture
def mock_containers_result():
    """Fixture with mock containers creation result."""
    return {
        "status": "success",
        "message": "Docker containers created successfully",
        "output": "Creating network container_network\nCreating container sonarr\nCreating container radarr\nCreating container jellyfin\n"
    }


@pytest.fixture
def mock_post_install_result():
    """Fixture with mock post-installation result."""
    return {
        "status": "success",
        "message": "Post-installation tasks completed"
    }


@pytest.fixture
def mock_finalize_result():
    """Fixture with mock finalization result."""
    return {
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


@pytest.fixture
def mock_run_installation_result():
    """Fixture with mock complete installation result."""
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


class TestInstallationWizardAPI:
    """Tests for installation wizard API endpoints."""

    def test_get_wizard_status(self, client, mock_installation_status):
        """Test getting installation wizard status."""
        with patch('src.core.install_wizard.get_installation_status', return_value=mock_installation_status):
            response = client.get('/api/install/status')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["current_stage"] == "pre_check"
            assert data["current_stage_name"] == "System Compatibility Check"
            assert data["stage_progress"] == 100
            assert data["overall_progress"] == 5
            assert data["status"] == "in_progress"
            assert len(data["logs"]) == 2
            assert len(data["errors"]) == 0

    def test_check_system_compatibility(self, client, mock_compatibility_check):
        """Test checking system compatibility."""
        with patch('src.core.install_wizard.check_system_compatibility', return_value=mock_compatibility_check):
            response = client.get('/api/install/compatibility')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["compatible"] is True
            assert "system_info" in data
            assert "checks" in data
            assert data["checks"]["memory"]["compatible"] is True
            assert data["checks"]["disk_space"]["compatible"] is True
            assert data["checks"]["docker"]["installed"] is True

    def test_setup_basic_configuration(self, client, mock_basic_config_result):
        """Test setting up basic configuration."""
        with patch('src.core.install_wizard.setup_basic_configuration', return_value=mock_basic_config_result):
            config_data = {
                "puid": 1000,
                "pgid": 1000,
                "timezone": "Europe/London",
                "media_dir": "/mnt/media",
                "downloads_dir": "/mnt/downloads"
            }
            response = client.post(
                '/api/install/config',
                json=config_data,
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["message"] == "Basic configuration setup completed"
            assert "config" in data
            assert data["config"]["puid"] == 1000
            assert data["config"]["timezone"] == "Europe/London"
            assert data["config"]["media_dir"] == "/mnt/media"

    def test_setup_network_configuration(self, client, mock_network_config_result):
        """Test setting up network configuration."""
        with patch('src.core.install_wizard.setup_network_configuration', return_value=mock_network_config_result):
            network_data = {
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
            response = client.post(
                '/api/install/network',
                json=network_data,
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["message"] == "Network configuration setup completed"
            assert "config" in data
            assert data["config"]["vpn"]["enabled"] is True
            assert data["config"]["vpn"]["provider"] == "private internet access"
            assert data["config"]["tailscale"]["enabled"] is True

    def test_setup_storage_configuration(self, client, mock_storage_config_result):
        """Test setting up storage configuration."""
        with patch('src.core.install_wizard.setup_storage_configuration', return_value=mock_storage_config_result):
            storage_data = {
                "mount_points": [
                    {
                        "device": "/dev/sda1",
                        "path": "/mnt/media",
                        "fs_type": "ext4"
                    }
                ],
                "media_directory": "/mnt/media",
                "downloads_directory": "/mnt/downloads"
            }
            response = client.post(
                '/api/install/storage',
                json=storage_data,
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["message"] == "Storage configuration setup completed"
            assert "config" in data
            assert data["config"]["media_dir"] == "/mnt/media"
            assert data["config"]["downloads_dir"] == "/mnt/downloads"

    def test_setup_service_selection(self, client, mock_service_selection_result):
        """Test setting up service selection."""
        with patch('src.core.install_wizard.setup_service_selection', return_value=mock_service_selection_result):
            services_data = {
                "arr_apps": {
                    "sonarr": True,
                    "radarr": True,
                    "prowlarr": True
                },
                "download_clients": {
                    "transmission": True
                },
                "media_servers": {
                    "jellyfin": True
                }
            }
            response = client.post(
                '/api/install/services',
                json=services_data,
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["message"] == "Service selection setup completed"
            assert "services" in data
            assert data["services"]["arr_apps"]["sonarr"] is True
            assert data["services"]["media_servers"]["jellyfin"] is True

    def test_install_dependencies(self, client, mock_dependencies_result):
        """Test installing dependencies."""
        with patch('src.core.install_wizard.install_dependencies', return_value=mock_dependencies_result):
            response = client.post('/api/install/dependencies')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["message"] == "Dependency installation completed"

    def test_setup_docker(self, client, mock_docker_setup_result):
        """Test setting up Docker."""
        with patch('src.core.install_wizard.setup_docker', return_value=mock_docker_setup_result):
            response = client.post('/api/install/docker')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["message"] == "Docker setup completed successfully"

    def test_generate_compose_files(self, client, mock_compose_files_result):
        """Test generating Docker Compose files."""
        with patch('src.core.install_wizard.generate_compose_files', return_value=mock_compose_files_result):
            response = client.post('/api/install/compose')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["message"] == "Docker Compose configuration completed"
            assert "docker_compose_path" in data
            assert "env_path" in data

    def test_create_containers(self, client, mock_containers_result):
        """Test creating Docker containers."""
        with patch('src.core.install_wizard.create_containers', return_value=mock_containers_result):
            response = client.post('/api/install/containers')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["message"] == "Docker containers created successfully"
            assert "output" in data
            assert "Creating container sonarr" in data["output"]

    def test_perform_post_installation(self, client, mock_post_install_result):
        """Test performing post-installation tasks."""
        with patch('src.core.install_wizard.perform_post_installation', return_value=mock_post_install_result):
            response = client.post('/api/install/post')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["message"] == "Post-installation tasks completed"

    def test_finalize_installation(self, client, mock_finalize_result):
        """Test finalizing installation."""
        with patch('src.core.install_wizard.finalize_installation', return_value=mock_finalize_result):
            response = client.post('/api/install/finalize')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert data["message"] == "Installation completed successfully"
            assert "container_summary" in data
            assert data["container_summary"]["total"] == 6
            assert data["container_summary"]["running"] == 6
            assert "container_urls" in data
            assert "sonarr" in data["container_urls"]
            assert "installation_time" in data

    def test_run_installation(self, client, mock_run_installation_result):
        """Test running complete installation."""
        with patch('src.core.install_wizard.run_installation', return_value=mock_run_installation_result):
            installation_data = {
                "user_config": {
                    "puid": 1000,
                    "pgid": 1000,
                    "timezone": "Europe/London",
                    "media_dir": "/mnt/media",
                    "downloads_dir": "/mnt/downloads"
                },
                "network_config": {
                    "vpn": {
                        "enabled": True,
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
                        "sonarr": True,
                        "radarr": True
                    },
                    "media_servers": {
                        "jellyfin": True
                    }
                }
            }
            response = client.post(
                '/api/install/run',
                json=installation_data,
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "completed"
            assert data["current_stage"] == "finalization"
            assert data["overall_progress"] == 100
            assert len(data["logs"]) > 0
            assert data["start_time"] is not None
            assert data["end_time"] is not None
            assert data["elapsed_time"] is not None