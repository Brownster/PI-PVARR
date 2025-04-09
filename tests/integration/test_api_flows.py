"""
Integration tests for API flow scenarios.

These tests verify the complete end-to-end flow of key API operations.
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


class TestDashboardFlow:
    """Tests for dashboard data loading flow."""

    def test_load_dashboard_data(self, client):
        """Test loading all dashboard data."""
        # Mock responses for dashboard data sources
        system_info = {
            "hostname": "raspberrypi",
            "platform": "linux",
            "memory": {"total_gb": 4, "available_gb": 2, "percent": 50},
            "cpu": {"cores": 4, "percent": 15},
            "temperature_celsius": 45,
            "is_raspberry_pi": True
        }
        
        container_info = {
            "sonarr": {"status": "running", "description": "TV Series Management"},
            "radarr": {"status": "running", "description": "Movie Management"},
            "jellyfin": {"status": "running", "description": "Media Server"}
        }
        
        drives_info = [
            {"device": "/dev/sda1", "mountpoint": "/mnt/media", "percent": 25},
            {"device": "/dev/sdb1", "mountpoint": "/mnt/downloads", "percent": 30}
        ]
        
        network_info = {
            "interfaces": {
                "eth0": {"addresses": [{"address": "192.168.1.100"}]},
                "wlan0": {"addresses": [{"address": "192.168.1.101"}]}
            }
        }
        
        # Set up mocks
        with patch('src.core.system_info.get_system_info', return_value=system_info), \
             patch('src.core.docker_manager.get_container_status', return_value=container_info), \
             patch('src.core.storage_manager.get_drives_info', return_value=drives_info), \
             patch('src.core.network_manager.get_network_info', return_value=network_info):
            
            # Step 1: Get system information
            response = client.get('/api/system')
            assert response.status_code == 200
            system_data = json.loads(response.data)
            assert system_data["hostname"] == "raspberrypi"
            assert system_data["is_raspberry_pi"] is True
            
            # Step 2: Get container statuses
            response = client.get('/api/containers')
            assert response.status_code == 200
            container_data = json.loads(response.data)
            assert "sonarr" in container_data
            assert container_data["sonarr"]["status"] == "running"
            
            # Step 3: Get storage information
            response = client.get('/api/storage/drives')
            assert response.status_code == 200
            drives_data = json.loads(response.data)
            assert len(drives_data) == 2
            assert drives_data[0]["device"] == "/dev/sda1"
            
            # Step 4: Get network information
            response = client.get('/api/network/info')
            assert response.status_code == 200
            network_data = json.loads(response.data)
            assert "interfaces" in network_data
            assert "eth0" in network_data["interfaces"]


class TestInstallWizardFlow:
    """Tests for installation wizard flow."""

    def test_complete_installation_flow(self, client):
        """Test the complete installation wizard flow."""
        # Mock responses for installation steps
        compatibility_check = {
            "status": "success",
            "compatible": True,
            "checks": {
                "memory": {"compatible": True},
                "disk_space": {"compatible": True},
                "docker": {"installed": False}
            }
        }
        
        config_result = {
            "status": "success",
            "message": "Basic configuration setup completed"
        }
        
        network_result = {
            "status": "success",
            "message": "Network configuration setup completed"
        }
        
        storage_result = {
            "status": "success",
            "message": "Storage configuration setup completed"
        }
        
        services_result = {
            "status": "success",
            "message": "Service selection setup completed"
        }
        
        dependencies_result = {
            "status": "success",
            "message": "Dependencies installed successfully"
        }
        
        docker_result = {
            "status": "success",
            "message": "Docker setup completed successfully"
        }
        
        compose_result = {
            "status": "success",
            "message": "Docker Compose files generated successfully"
        }
        
        containers_result = {
            "status": "success",
            "message": "Containers created successfully"
        }
        
        status_updates = [
            {"current_stage": "pre_check", "overall_progress": 5, "status": "in_progress"},
            {"current_stage": "config_setup", "overall_progress": 10, "status": "in_progress"},
            {"current_stage": "network_setup", "overall_progress": 15, "status": "in_progress"},
            {"current_stage": "storage_setup", "overall_progress": 25, "status": "in_progress"},
            {"current_stage": "service_selection", "overall_progress": 30, "status": "in_progress"},
            {"current_stage": "dependency_install", "overall_progress": 40, "status": "in_progress"},
            {"current_stage": "docker_setup", "overall_progress": 55, "status": "in_progress"},
            {"current_stage": "compose_generation", "overall_progress": 65, "status": "in_progress"},
            {"current_stage": "container_creation", "overall_progress": 80, "status": "in_progress"},
            {"current_stage": "post_install", "overall_progress": 90, "status": "in_progress"},
            {"current_stage": "finalization", "overall_progress": 100, "status": "completed"}
        ]
        
        # Set up mocks for individual steps
        with patch('src.core.install_wizard.check_system_compatibility', return_value=compatibility_check), \
             patch('src.core.install_wizard.setup_basic_configuration', return_value=config_result), \
             patch('src.core.install_wizard.setup_network_configuration', return_value=network_result), \
             patch('src.core.install_wizard.setup_storage_configuration', return_value=storage_result), \
             patch('src.core.install_wizard.setup_service_selection', return_value=services_result), \
             patch('src.core.install_wizard.install_dependencies', return_value=dependencies_result), \
             patch('src.core.install_wizard.setup_docker', return_value=docker_result), \
             patch('src.core.install_wizard.generate_compose_files', return_value=compose_result), \
             patch('src.core.install_wizard.create_containers', return_value=containers_result):
            
            # Step 1: Check system compatibility
            response = client.get('/api/install/compatibility')
            assert response.status_code == 200
            compatibility_data = json.loads(response.data)
            assert compatibility_data["status"] == "success"
            assert compatibility_data["compatible"] is True
            
            # Step 2: Configure basic settings
            config_data = {
                "puid": 1000,
                "pgid": 1000,
                "timezone": "Europe/London",
                "media_dir": "/mnt/media",
                "downloads_dir": "/mnt/downloads"
            }
            response = client.post('/api/install/config', json=config_data)
            assert response.status_code == 200
            assert json.loads(response.data)["status"] == "success"
            
            # Step 3: Configure network
            network_data = {
                "vpn": {
                    "enabled": True,
                    "provider": "private internet access",
                    "username": "user",
                    "password": "pass"
                }
            }
            response = client.post('/api/install/network', json=network_data)
            assert response.status_code == 200
            assert json.loads(response.data)["status"] == "success"
            
            # Step 4: Configure storage
            storage_data = {
                "media_directory": "/mnt/media",
                "downloads_directory": "/mnt/downloads"
            }
            response = client.post('/api/install/storage', json=storage_data)
            assert response.status_code == 200
            assert json.loads(response.data)["status"] == "success"
            
            # Step 5: Configure services
            services_data = {
                "arr_apps": {"sonarr": True, "radarr": True},
                "media_servers": {"jellyfin": True},
                "download_clients": {"transmission": True}
            }
            response = client.post('/api/install/services', json=services_data)
            assert response.status_code == 200
            assert json.loads(response.data)["status"] == "success"
            
            # Step 6: Install dependencies
            response = client.post('/api/install/dependencies')
            assert response.status_code == 200
            assert json.loads(response.data)["status"] == "success"
            
            # Step 7: Setup Docker
            response = client.post('/api/install/docker')
            assert response.status_code == 200
            assert json.loads(response.data)["status"] == "success"
            
            # Step 8: Generate Docker Compose files
            response = client.post('/api/install/compose')
            assert response.status_code == 200
            assert json.loads(response.data)["status"] == "success"
            
            # Step 9: Create containers
            response = client.post('/api/install/containers')
            assert response.status_code == 200
            assert json.loads(response.data)["status"] == "success"
            
            # Mock installation status progress updates for polling
            status_index = 0
            
            def mock_get_status():
                nonlocal status_index
                if status_index < len(status_updates):
                    status = status_updates[status_index]
                    status_index += 1
                    return status
                return status_updates[-1]
            
            with patch('src.core.install_wizard.get_installation_status', side_effect=mock_get_status):
                # Step 10: Poll for installation status updates
                for _ in range(5):  # Simulate polling multiple times
                    response = client.get('/api/install/status')
                    assert response.status_code == 200
                    status_data = json.loads(response.data)
                    assert "current_stage" in status_data
                    assert "overall_progress" in status_data
                    
                    # If installation is completed, break the polling loop
                    if status_data.get("status") == "completed":
                        assert status_data["overall_progress"] == 100
                        break

    def test_installation_run_endpoint(self, client):
        """Test the single API endpoint for running the entire installation."""
        # Mock result for the complete installation process
        installation_result = {
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
        
        with patch('src.core.install_wizard.run_installation', return_value=installation_result):
            # Run the complete installation with a single API call
            installation_config = {
                "user_config": {
                    "puid": 1000,
                    "pgid": 1000,
                    "timezone": "UTC",
                    "media_dir": "/mnt/media",
                    "downloads_dir": "/mnt/downloads"
                },
                "network_config": {
                    "vpn": {"enabled": False},
                    "tailscale": {"enabled": False}
                },
                "storage_config": {
                    "media_directory": "/mnt/media",
                    "downloads_directory": "/mnt/downloads"
                },
                "services_config": {
                    "arr_apps": {"sonarr": True, "radarr": True},
                    "download_clients": {"transmission": True},
                    "media_servers": {"jellyfin": True}
                }
            }
            
            response = client.post('/api/install/run', json=installation_config)
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data["status"] == "completed"
            assert data["overall_progress"] == 100
            assert data["current_stage"] == "finalization"
            assert len(data["logs"]) > 0
            assert data["elapsed_time"] > 0


class TestServiceManagementFlow:
    """Tests for service management flow."""

    def test_service_control_flow(self, client):
        """Test the service control flow (start, restart, stop)."""
        # Mock responses for service operations
        service_info = {
            "arr_apps": {
                "sonarr": {"name": "sonarr", "enabled": True, "status": "running"}
            },
            "media_servers": {
                "jellyfin": {"name": "jellyfin", "enabled": True, "status": "stopped"}
            }
        }
        
        start_result = {"status": "success", "message": "Services started successfully"}
        restart_result = {"status": "success", "message": "Services restarted successfully"}
        stop_result = {"status": "success", "message": "Services stopped successfully"}
        
        with patch('src.core.service_manager.get_service_info', return_value=service_info), \
             patch('src.core.service_manager.start_services', return_value=start_result), \
             patch('src.core.service_manager.restart_services', return_value=restart_result), \
             patch('src.core.service_manager.stop_services', return_value=stop_result):
            
            # Step 1: Get current service status
            response = client.get('/api/services/info')
            assert response.status_code == 200
            info_data = json.loads(response.data)
            assert "arr_apps" in info_data
            assert "sonarr" in info_data["arr_apps"]
            assert info_data["arr_apps"]["sonarr"]["status"] == "running"
            assert info_data["media_servers"]["jellyfin"]["status"] == "stopped"
            
            # Step 2: Start services
            response = client.post('/api/services/start')
            assert response.status_code == 200
            start_data = json.loads(response.data)
            assert start_data["status"] == "success"
            
            # Step 3: Restart services
            response = client.post('/api/services/restart')
            assert response.status_code == 200
            restart_data = json.loads(response.data)
            assert restart_data["status"] == "success"
            
            # Step 4: Stop services
            response = client.post('/api/services/stop')
            assert response.status_code == 200
            stop_data = json.loads(response.data)
            assert stop_data["status"] == "success"