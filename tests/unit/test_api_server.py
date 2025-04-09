"""
Unit tests for the API server module.
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from src.api import server


@pytest.mark.unit
class TestAPIServer:
    """Tests for the API server module."""

    def test_create_app(self):
        """Test creating the Flask application."""
        app = server.create_app()
        assert app.name == 'src.api.server'
        
    def test_system_info_endpoint(self):
        """Test the system info endpoint."""
        app = server.create_app()
        
        with patch('src.core.system_info.get_system_info') as mock_get_system_info:
            mock_get_system_info.return_value = {'hostname': 'test'}
            
            client = app.test_client()
            response = client.get('/api/system')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['hostname'] == 'test'
            
    def test_config_endpoint(self):
        """Test the configuration endpoint."""
        app = server.create_app()
        
        with patch('src.core.config.get_config') as mock_get_config:
            mock_get_config.return_value = {'test': 'config'}
            
            client = app.test_client()
            response = client.get('/api/config')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['test'] == 'config'
            
    def test_services_endpoint(self):
        """Test the services endpoint."""
        app = server.create_app()
        
        with patch('src.core.config.get_services_config') as mock_get_services:
            mock_get_services.return_value = {'test': 'services'}
            
            client = app.test_client()
            response = client.get('/api/services')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['test'] == 'services'
            
    def test_update_config(self):
        """Test updating configuration."""
        app = server.create_app()
        
        with patch('src.core.config.save_config_wrapper') as mock_save_config:
            client = app.test_client()
            response = client.post(
                '/api/config',
                data=json.dumps({'test': 'updated_config'}),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            mock_save_config.assert_called_once_with({'test': 'updated_config'})
            
    def test_update_services(self):
        """Test updating services configuration."""
        app = server.create_app()
        
        with patch('src.core.config.save_services_config') as mock_save_services:
            client = app.test_client()
            response = client.post(
                '/api/services',
                data=json.dumps({'test': 'updated_services'}),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            mock_save_services.assert_called_once_with({'test': 'updated_services'})