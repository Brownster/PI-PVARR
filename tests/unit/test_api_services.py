"""
Unit tests for the service API endpoints.
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
def mock_service_info():
    """Fixture with mock service information."""
    return {
        "arr_apps": {
            "sonarr": {
                "name": "sonarr",
                "enabled": True,
                "description": "TV Series Management",
                "default_port": 8989,
                "docker_image": "linuxserver/sonarr:latest",
                "status": "running",
                "url": "http://localhost:8989",
                "ports": [{"container": "8989", "host": "8989", "protocol": "tcp"}]
            },
            "radarr": {
                "name": "radarr",
                "enabled": True,
                "description": "Movie Management",
                "default_port": 7878,
                "docker_image": "linuxserver/radarr:latest",
                "status": "running",
                "url": "http://localhost:7878",
                "ports": [{"container": "7878", "host": "7878", "protocol": "tcp"}]
            }
        },
        "download_clients": {
            "transmission": {
                "name": "transmission",
                "enabled": True,
                "description": "Torrent Client",
                "default_port": 9091,
                "docker_image": "linuxserver/transmission:latest",
                "status": "running",
                "url": "http://localhost:9091",
                "ports": [{"container": "9091", "host": "9091", "protocol": "tcp"}]
            }
        },
        "media_servers": {
            "jellyfin": {
                "name": "jellyfin",
                "enabled": True,
                "description": "Media Server",
                "default_port": 8096,
                "docker_image": "linuxserver/jellyfin:latest",
                "status": "running",
                "url": "http://localhost:8096",
                "ports": [{"container": "8096", "host": "8096", "protocol": "tcp"}]
            }
        },
        "utilities": {
            "portainer": {
                "name": "portainer",
                "enabled": True,
                "description": "Docker Management",
                "default_port": 9000,
                "docker_image": "portainer/portainer-ce:latest",
                "status": "running",
                "url": "http://localhost:9000",
                "ports": [{"container": "9000", "host": "9000", "protocol": "tcp"}]
            }
        }
    }


@pytest.fixture
def mock_compatibility_info():
    """Fixture with mock compatibility information."""
    return {
        "status": "success",
        "system_info": {
            "architecture": "aarch64",
            "memory_gb": 4,
            "is_raspberry_pi": True,
            "pi_model": "Raspberry Pi 4 Model B Rev 1.2",
            "has_hw_transcoding": True
        },
        "compatibility": {
            "media_servers": {
                "jellyfin": {
                    "compatible": True,
                    "recommended": True,
                    "notes": "Recommended for ARM platforms"
                },
                "plex": {
                    "compatible": True,
                    "recommended": False,
                    "notes": "Limited transcoding on ARM platforms"
                }
            },
            "arr_apps": {
                "sonarr": {"compatible": True, "recommended": True, "notes": "Core service"},
                "radarr": {"compatible": True, "recommended": True, "notes": "Core service"}
            }
        }
    }


@pytest.fixture
def mock_docker_compose_result():
    """Fixture with mock Docker Compose generation result."""
    return {
        "status": "success",
        "message": "Docker Compose file generated successfully",
        "compose_file": "version: '3.7'\nservices:\n  sonarr:\n    image: linuxserver/sonarr:latest\n",
        "temp_file_path": "/tmp/docker-compose-12345.yml"
    }


@pytest.fixture
def mock_installation_status():
    """Fixture with mock installation status."""
    return {
        "status": "success",
        "installation_status": "running",
        "compose_file_exists": True,
        "active_services": 5,
        "enabled_services": 6,
        "service_info": {}  # This would contain the full service info, omitted for brevity
    }


class TestServicesAPI:
    """Tests for service API endpoints."""

    def test_get_services_info(self, client, mock_service_info):
        """Test getting comprehensive service information."""
        with patch('src.core.service_manager.get_service_info', return_value=mock_service_info):
            response = client.get('/api/services/info')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == mock_service_info
            assert "arr_apps" in data
            assert "sonarr" in data["arr_apps"]
            assert data["arr_apps"]["sonarr"]["enabled"] is True
            assert data["arr_apps"]["sonarr"]["status"] == "running"

    def test_toggle_service(self, client):
        """Test toggling service enabled status."""
        toggle_result = {"status": "success", "message": "Service 'sonarr' enabled successfully"}
        with patch('src.core.service_manager.toggle_service', return_value=toggle_result):
            response = client.post(
                '/api/services/toggle',
                json={"service_name": "sonarr", "enabled": True},
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "sonarr" in data["message"]

    def test_toggle_service_missing_params(self, client):
        """Test toggling service with missing parameters."""
        response = client.post(
            '/api/services/toggle',
            json={"service_name": "sonarr"},  # Missing 'enabled' parameter
            content_type='application/json'
        )
        assert response.status_code == 200  # Flask still returns 200 for JSON responses
        data = json.loads(response.data)
        assert data["status"] == "error"
        assert "Missing required parameters" in data["message"]

    def test_get_service_compatibility(self, client, mock_compatibility_info):
        """Test getting service compatibility information."""
        with patch('src.core.service_manager.get_service_compatibility', return_value=mock_compatibility_info):
            response = client.get('/api/services/compatibility')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "system_info" in data
            assert "compatibility" in data
            assert data["system_info"]["is_raspberry_pi"] is True
            assert "jellyfin" in data["compatibility"]["media_servers"]
            assert data["compatibility"]["media_servers"]["jellyfin"]["compatible"] is True

    def test_generate_docker_compose(self, client, mock_docker_compose_result):
        """Test generating Docker Compose file."""
        with patch('src.core.service_manager.generate_docker_compose', return_value=mock_docker_compose_result):
            response = client.get('/api/services/compose')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "compose_file" in data
            assert "version: '3.7'" in data["compose_file"]

    def test_generate_env_file(self, client):
        """Test generating environment file."""
        env_result = {
            "status": "success",
            "message": ".env file generated successfully",
            "env_file": "PUID=1000\nPGID=1000\nTIMEZONE=UTC\n",
            "temp_file_path": "/tmp/env-12345"
        }
        with patch('src.core.service_manager.generate_env_file', return_value=env_result):
            response = client.get('/api/services/env')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "env_file" in data
            assert "PUID=1000" in data["env_file"]

    def test_apply_service_changes(self, client):
        """Test applying service changes."""
        apply_result = {
            "status": "success",
            "message": "Service changes applied successfully",
            "docker_compose_path": "/home/user/.config/pi-pvarr/docker-compose/docker-compose.yml",
            "env_path": "/home/user/.config/pi-pvarr/.env"
        }
        with patch('src.core.service_manager.apply_service_changes', return_value=apply_result):
            response = client.post('/api/services/apply')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "docker_compose_path" in data
            assert "env_path" in data

    def test_start_services(self, client):
        """Test starting services."""
        start_result = {
            "status": "success",
            "message": "Services started successfully",
            "output": "Creating network container_network\nCreating container sonarr\n"
        }
        with patch('src.core.service_manager.start_services', return_value=start_result):
            response = client.post('/api/services/start')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "output" in data
            assert "Creating" in data["output"]

    def test_stop_services(self, client):
        """Test stopping services."""
        stop_result = {
            "status": "success",
            "message": "Services stopped successfully",
            "output": "Stopping container sonarr\nRemoving network container_network\n"
        }
        with patch('src.core.service_manager.stop_services', return_value=stop_result):
            response = client.post('/api/services/stop')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "output" in data
            assert "Stopping" in data["output"]

    def test_restart_services(self, client):
        """Test restarting services."""
        restart_result = {
            "status": "success",
            "message": "Services restarted successfully",
            "output": "Restarting sonarr\nRestarting radarr\n"
        }
        with patch('src.core.service_manager.restart_services', return_value=restart_result):
            response = client.post('/api/services/restart')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "output" in data
            assert "Restarting" in data["output"]

    def test_get_installation_status(self, client, mock_installation_status):
        """Test getting installation status."""
        with patch('src.core.service_manager.get_installation_status', return_value=mock_installation_status):
            response = client.get('/api/services/status')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data["status"] == "success"
            assert "installation_status" in data
            assert data["installation_status"] == "running"
            assert data["active_services"] == 5
            assert data["enabled_services"] == 6