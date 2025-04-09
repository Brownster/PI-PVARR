"""
Unit tests for the Docker manager module.
"""
import pytest
from unittest.mock import patch, MagicMock

from src.core import docker_manager


@pytest.mark.unit
class TestDockerManager:
    """Tests for the docker_manager module."""

    def test_get_container_status(self):
        """Test getting container status."""
        # Create mock container objects
        mock_container1 = MagicMock()
        mock_container1.name = 'test1'
        mock_container1.status = 'running'
        mock_container1.ports = {'8080/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '8080'}]}
        
        mock_container2 = MagicMock()
        mock_container2.name = 'test2'
        mock_container2.status = 'exited'
        mock_container2.ports = {}
        
        # Mock docker client
        mock_client = MagicMock()
        mock_client.containers.list.return_value = [mock_container1, mock_container2]
        
        with patch('docker.from_env', return_value=mock_client):
            container_status = docker_manager.get_container_status()
            
            assert len(container_status) == 2
            assert container_status['test1']['status'] == 'running'
            assert container_status['test1']['ports'][0]['host'] == '8080'
            assert container_status['test2']['status'] == 'exited'
            assert container_status['test2']['ports'] == []

    def test_get_container_status_with_error(self):
        """Test handling errors when getting container status."""
        with patch('docker.from_env', side_effect=Exception("Test error")):
            container_status = docker_manager.get_container_status()
            
            assert 'error' in container_status
            assert container_status['error']['status'] == 'error'
            assert "Test error" in container_status['error']['message']

    def test_get_container_logs(self):
        """Test getting container logs."""
        # Mock container
        mock_container = MagicMock()
        mock_container.logs.return_value = b"Test log\nAnother line"
        
        # Mock docker client
        mock_client = MagicMock()
        mock_client.containers.get.return_value = mock_container
        
        with patch('docker.from_env', return_value=mock_client):
            logs = docker_manager.get_container_logs('test', 10)
            
            assert logs == "Test log\nAnother line"
            mock_container.logs.assert_called_once_with(tail=10)

    def test_get_container_logs_with_error(self):
        """Test handling errors when getting container logs."""
        # Mock docker client
        mock_client = MagicMock()
        mock_client.containers.get.side_effect = Exception("Container not found")
        
        with patch('docker.from_env', return_value=mock_client):
            logs = docker_manager.get_container_logs('test', 10)
            
            assert "Error getting logs" in logs
            assert "Container not found" in logs

    def test_start_container(self):
        """Test starting a container."""
        # Mock container
        mock_container = MagicMock()
        
        # Mock docker client
        mock_client = MagicMock()
        mock_client.containers.get.return_value = mock_container
        
        with patch('docker.from_env', return_value=mock_client):
            result = docker_manager.start_container('test')
            
            assert result['status'] == 'success'
            mock_container.start.assert_called_once()

    def test_start_container_with_error(self):
        """Test handling errors when starting a container."""
        # Mock docker client
        mock_client = MagicMock()
        mock_client.containers.get.return_value = MagicMock()
        mock_client.containers.get.return_value.start.side_effect = Exception("Test error")
        
        with patch('docker.from_env', return_value=mock_client):
            result = docker_manager.start_container('test')
            
            assert result['status'] == 'error'
            assert "Test error" in result['message']

    def test_stop_container(self):
        """Test stopping a container."""
        # Mock container
        mock_container = MagicMock()
        
        # Mock docker client
        mock_client = MagicMock()
        mock_client.containers.get.return_value = mock_container
        
        with patch('docker.from_env', return_value=mock_client):
            result = docker_manager.stop_container('test')
            
            assert result['status'] == 'success'
            mock_container.stop.assert_called_once()

    def test_restart_container(self):
        """Test restarting a container."""
        # Mock container
        mock_container = MagicMock()
        
        # Mock docker client
        mock_client = MagicMock()
        mock_client.containers.get.return_value = mock_container
        
        with patch('docker.from_env', return_value=mock_client):
            result = docker_manager.restart_container('test')
            
            assert result['status'] == 'success'
            mock_container.restart.assert_called_once()

    def test_get_container_info(self):
        """Test getting container information."""
        # Mock container
        mock_container = MagicMock()
        mock_container.name = 'test'
        mock_container.status = 'running'
        mock_container.attrs = {
            'Config': {
                'Image': 'test/image:latest',
                'Labels': {'test.label': 'value'}
            },
            'NetworkSettings': {
                'Ports': {
                    '8080/tcp': [{'HostIp': '0.0.0.0', 'HostPort': '8080'}]
                }
            }
        }
        
        # Mock docker client
        mock_client = MagicMock()
        mock_client.containers.get.return_value = mock_container
        
        with patch('docker.from_env', return_value=mock_client):
            info = docker_manager.get_container_info('test')
            
            assert info['name'] == 'test'
            assert info['status'] == 'running'
            assert info['image'] == 'test/image:latest'
            assert info['ports'][0]['host'] == '8080'
            assert info['ports'][0]['container'] == '8080'
            
    def test_get_container_info_with_error(self):
        """Test handling errors when getting container info."""
        mock_client = MagicMock()
        mock_client.containers.get.side_effect = Exception("Container not found")
        
        with patch('docker.from_env', return_value=mock_client):
            info = docker_manager.get_container_info('test')
            
            assert info['status'] == 'error'
            assert 'Container not found' in info['message']
            
    def test_pull_image(self):
        """Test pulling a Docker image."""
        mock_client = MagicMock()
        mock_client.images.pull.return_value = MagicMock()
        
        with patch('docker.from_env', return_value=mock_client):
            result = docker_manager.pull_image('test/image:latest')
            
            assert result['status'] == 'success'
            assert 'pulled successfully' in result['message']
            mock_client.images.pull.assert_called_once_with('test/image:latest')
            
    def test_pull_image_with_error(self):
        """Test handling errors when pulling an image."""
        mock_client = MagicMock()
        mock_client.images.pull.side_effect = Exception("Image not found")
        
        with patch('docker.from_env', return_value=mock_client):
            result = docker_manager.pull_image('test/image:latest')
            
            assert result['status'] == 'error'
            assert 'Image not found' in result['message']
            
    def test_update_all_containers(self):
        """Test updating all containers."""
        # Mock containers
        mock_container1 = MagicMock()
        mock_container1.name = 'test1'
        mock_container1.status = 'running'
        
        mock_container2 = MagicMock()
        mock_container2.name = 'test2'
        mock_container2.status = 'exited'
        
        mock_client = MagicMock()
        mock_client.containers.list.return_value = [mock_container1, mock_container2]
        
        with patch('docker.from_env', return_value=mock_client), \
             patch('src.core.docker_manager.get_container_info') as mock_get_info, \
             patch('src.core.docker_manager.pull_image') as mock_pull:
            
            # Mock container info and pull results
            mock_get_info.side_effect = lambda name: {
                'test1': {'image': 'test/image1:latest'},
                'test2': {'image': 'test/image2:latest'}
            }[name]
            
            mock_pull.side_effect = lambda image: {
                'test/image1:latest': {'status': 'success', 'message': 'Pulled image1'},
                'test/image2:latest': {'status': 'success', 'message': 'Pulled image2'}
            }[image]
            
            result = docker_manager.update_all_containers()
            
            assert result['status'] == 'success'
            assert len(result['details']) == 2
            assert result['details'][0]['container'] == 'test1'
            assert result['details'][0]['status'] == 'updated'
            assert result['details'][1]['container'] == 'test2'
            assert result['details'][1]['status'] == 'updated'
            
            # Verify that container1 was restarted (was running)
            mock_container1.restart.assert_called_once()
            # Verify that container2 was not restarted (was exited)
            mock_container2.restart.assert_not_called()
            
    def test_update_all_containers_with_error(self):
        """Test handling errors when updating containers."""
        # Test global error
        with patch('docker.from_env', side_effect=Exception("Docker error")):
            result = docker_manager.update_all_containers()
            
            assert result['status'] == 'error'
            assert 'Docker error' in result['message']
            
        # Test partial success with some container errors
        mock_container1 = MagicMock()
        mock_container1.name = 'test1'
        mock_container1.status = 'running'
        
        mock_container2 = MagicMock()
        mock_container2.name = 'test2'
        mock_container2.status = 'running'
        
        mock_client = MagicMock()
        mock_client.containers.list.return_value = [mock_container1, mock_container2]
        
        with patch('docker.from_env', return_value=mock_client), \
             patch('src.core.docker_manager.get_container_info') as mock_get_info, \
             patch('src.core.docker_manager.pull_image') as mock_pull:
            
            # Mock container info and pull results - one succeeds, one fails
            mock_get_info.side_effect = lambda name: {
                'test1': {'image': 'test/image1:latest'},
                'test2': {'image': 'test/image2:latest'}
            }[name]
            
            mock_pull.side_effect = lambda image: {
                'test/image1:latest': {'status': 'success', 'message': 'Pulled image1'},
                'test/image2:latest': {'status': 'error', 'message': 'Image2 not found'}
            }[image]
            
            result = docker_manager.update_all_containers()
            
            assert result['status'] == 'partial'
            assert '1 of 2 updates failed' in result['message']
            assert len(result['details']) == 2
            assert result['details'][0]['status'] == 'updated'
            assert result['details'][1]['status'] == 'error'