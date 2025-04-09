"""
Unit tests for the network API endpoints.
"""
import pytest
import json
from unittest.mock import patch, MagicMock

from src.api.server import create_app


@pytest.mark.unit
class TestNetworkAPI:
    """Tests for the network API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Flask test client fixture."""
        app = create_app({'TESTING': True})
        with app.test_client() as client:
            yield client
    
    def test_get_network_interfaces(self, client):
        """Test getting network interface information."""
        mock_interfaces = {
            'status': 'success',
            'interfaces': {
                'eth0': {
                    'mac': '00:11:22:33:44:55',
                    'up': True,
                    'type': 'ethernet',
                    'addresses': [
                        {'address': '192.168.1.100', 'netmask': '255.255.255.0', 'broadcast': '192.168.1.255'}
                    ]
                }
            }
        }
        
        with patch('src.core.network_manager.get_network_interfaces', return_value=mock_interfaces):
            response = client.get('/api/network/interfaces')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'success'
            assert 'interfaces' in data
            assert 'eth0' in data['interfaces']
    
    def test_get_network_info(self, client):
        """Test getting comprehensive network information."""
        mock_info = {
            'interfaces': {'eth0': {'type': 'ethernet'}},
            'vpn': {'connected': True, 'provider': 'gluetun'},
            'tailscale': {'installed': True, 'running': True}
        }
        
        with patch('src.core.network_manager.get_network_info', return_value=mock_info):
            response = client.get('/api/network/info')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert 'interfaces' in data
            assert 'vpn' in data
            assert 'tailscale' in data
    
    def test_get_vpn_status(self, client):
        """Test getting VPN status."""
        mock_status = {
            'status': 'success',
            'vpn': {
                'connected': True,
                'provider': 'gluetun',
                'ip_address': '123.45.67.89',
                'location': 'Amsterdam, NL'
            }
        }
        
        with patch('src.core.network_manager.get_vpn_status', return_value=mock_status):
            response = client.get('/api/network/vpn/status')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'success'
            assert 'vpn' in data
            assert data['vpn']['connected'] is True
            assert data['vpn']['provider'] == 'gluetun'
    
    def test_configure_vpn(self, client):
        """Test configuring VPN."""
        mock_result = {
            'status': 'success',
            'message': 'VPN configuration updated for provider private internet access',
            'details': {
                'provider': 'private internet access',
                'region': 'Netherlands',
                'credentials_set': True
            }
        }
        
        vpn_config = {
            'enabled': True,
            'provider': 'private internet access',
            'username': 'test_user',
            'password': 'test_pass',
            'region': 'Netherlands'
        }
        
        with patch('src.core.network_manager.configure_vpn', return_value=mock_result):
            response = client.post('/api/network/vpn/configure', json=vpn_config)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'success'
            assert 'VPN configuration updated' in data['message']
    
    def test_get_tailscale_status(self, client):
        """Test getting Tailscale status."""
        mock_status = {
            'status': 'success',
            'tailscale': {
                'installed': True,
                'running': True,
                'ip_address': '100.100.100.100',
                'hostname': 'test-host'
            }
        }
        
        with patch('src.core.network_manager.get_tailscale_status', return_value=mock_status):
            response = client.get('/api/network/tailscale/status')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'success'
            assert 'tailscale' in data
            assert data['tailscale']['installed'] is True
            assert data['tailscale']['running'] is True
    
    def test_configure_tailscale(self, client):
        """Test configuring Tailscale."""
        mock_result = {
            'status': 'success',
            'message': 'Tailscale configured and started'
        }
        
        tailscale_config = {
            'enabled': True,
            'auth_key': 'tskey-abcdef123456'
        }
        
        with patch('src.core.network_manager.configure_tailscale', return_value=mock_result):
            response = client.post('/api/network/tailscale/configure', json=tailscale_config)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['status'] == 'success'
            assert 'Tailscale configured and started' in data['message']