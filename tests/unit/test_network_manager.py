"""
Unit tests for the network manager module.
"""
import pytest
from unittest.mock import patch, MagicMock
import json
import os
import psutil

from src.core import network_manager


@pytest.mark.unit
class TestNetworkManager:
    """Tests for the network_manager module."""
    
    def test_get_network_interfaces(self):
        """Test getting network interface information."""
        # Mock psutil network functions
        mock_if_addrs = {
            'eth0': [
                MagicMock(family=psutil.AF_LINK, address='00:11:22:33:44:55'),
                MagicMock(family=2, address='192.168.1.100', netmask='255.255.255.0', broadcast='192.168.1.255')
            ],
            'wlan0': [
                MagicMock(family=psutil.AF_LINK, address='AA:BB:CC:DD:EE:FF'),
                MagicMock(family=2, address='192.168.1.101', netmask='255.255.255.0', broadcast='192.168.1.255')
            ],
            'lo': [
                MagicMock(family=2, address='127.0.0.1', netmask='255.0.0.0', broadcast=None)
            ]
        }
        
        mock_if_stats = {
            'eth0': MagicMock(isup=True, speed=1000, mtu=1500),
            'wlan0': MagicMock(isup=True, speed=100, mtu=1500),
            'lo': MagicMock(isup=True, speed=0, mtu=65536)
        }
        
        with patch('psutil.net_if_addrs', return_value=mock_if_addrs), \
             patch('psutil.net_if_stats', return_value=mock_if_stats):
            
            result = network_manager.get_network_interfaces()
            
            assert result['status'] == 'success'
            assert 'interfaces' in result
            assert 'eth0' in result['interfaces']
            assert 'wlan0' in result['interfaces']
            assert 'lo' not in result['interfaces']
            
            # Check eth0 details
            eth0 = result['interfaces']['eth0']
            assert eth0['mac'] == '00:11:22:33:44:55'
            assert eth0['up'] is True
            assert eth0['speed'] == 1000
            assert eth0['type'] == 'ethernet'
            assert len(eth0['addresses']) == 1
            assert eth0['addresses'][0]['address'] == '192.168.1.100'
            
            # Check wlan0 details
            wlan0 = result['interfaces']['wlan0']
            assert wlan0['mac'] == 'AA:BB:CC:DD:EE:FF'
            assert wlan0['type'] == 'wireless'
    
    def test_get_network_interfaces_with_error(self):
        """Test handling errors when getting network interfaces."""
        with patch('psutil.net_if_addrs', side_effect=Exception("Test error")):
            result = network_manager.get_network_interfaces()
            
            assert result['status'] == 'error'
            assert 'Error getting network interfaces' in result['message']
    
    def test_get_vpn_status(self):
        """Test getting VPN status."""
        with patch('subprocess.run') as mock_run:
            # Mock docker ps command
            mock_docker_ps = MagicMock()
            mock_docker_ps.stdout = "container1\ngluetun\ncontainer3"
            mock_docker_ps.returncode = 0
            
            # Mock curl command for IP info
            mock_curl = MagicMock()
            mock_curl.stdout = json.dumps({
                'ip': '123.45.67.89',
                'city': 'Amsterdam',
                'country': 'NL'
            })
            mock_curl.returncode = 0
            
            # Configure mock to return different values for different commands
            mock_run.side_effect = [mock_docker_ps, mock_curl]
            
            result = network_manager.get_vpn_status()
            
            assert result['status'] == 'success'
            assert 'vpn' in result
            assert result['vpn']['connected'] is True
            assert result['vpn']['provider'] == 'gluetun'
            assert result['vpn']['ip_address'] == '123.45.67.89'
            assert result['vpn']['location'] == 'Amsterdam, NL'
    
    def test_get_vpn_status_not_connected(self):
        """Test getting VPN status when not connected."""
        with patch('subprocess.run') as mock_run:
            # Mock docker ps command with no VPN container
            mock_docker_ps = MagicMock()
            mock_docker_ps.stdout = "container1\ncontainer2\ncontainer3"
            mock_docker_ps.returncode = 0
            
            mock_run.return_value = mock_docker_ps
            
            result = network_manager.get_vpn_status()
            
            assert result['status'] == 'success'
            assert 'vpn' in result
            assert result['vpn']['connected'] is False
            assert result['vpn']['provider'] is None
    
    def test_get_vpn_status_with_error(self):
        """Test handling errors when getting VPN status."""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            result = network_manager.get_vpn_status()
            
            assert result['status'] == 'error'
            assert 'Error checking VPN status' in result['message']
    
    def test_configure_vpn(self):
        """Test configuring VPN."""
        vpn_config = {
            'enabled': True,
            'provider': 'private internet access',
            'username': 'test_user',
            'password': 'test_pass',
            'region': 'Netherlands'
        }
        
        result = network_manager.configure_vpn(vpn_config)
        
        assert result['status'] == 'success'
        assert 'VPN configuration updated' in result['message']
        assert result['details']['provider'] == 'private internet access'
        assert result['details']['region'] == 'Netherlands'
        assert result['details']['credentials_set'] is True
    
    def test_configure_vpn_disabled(self):
        """Test configuring VPN when disabled."""
        vpn_config = {'enabled': False}
        
        result = network_manager.configure_vpn(vpn_config)
        
        assert result['status'] == 'success'
        assert 'VPN disabled' in result['message']
    
    def test_configure_vpn_missing_params(self):
        """Test configuring VPN with missing parameters."""
        # Missing provider
        vpn_config = {
            'enabled': True,
            'username': 'test_user',
            'password': 'test_pass'
        }
        
        result = network_manager.configure_vpn(vpn_config)
        
        assert result['status'] == 'error'
        assert 'provider is required' in result['message']
        
        # Missing credentials
        vpn_config = {
            'enabled': True,
            'provider': 'private internet access'
        }
        
        result = network_manager.configure_vpn(vpn_config)
        
        assert result['status'] == 'error'
        assert 'username and password are required' in result['message']
    
    def test_get_tailscale_status(self):
        """Test getting Tailscale status."""
        mock_status_json = json.dumps({
            'BackendState': 'Running',
            'Self': {
                'HostName': 'test-host',
                'TailscaleIPs': ['100.100.100.100']
            }
        })
        
        with patch('os.path.exists', return_value=True), \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = mock_status_json
            
            result = network_manager.get_tailscale_status()
            
            assert result['status'] == 'success'
            assert 'tailscale' in result
            assert result['tailscale']['installed'] is True
            assert result['tailscale']['running'] is True
            assert result['tailscale']['ip_address'] == '100.100.100.100'
            assert result['tailscale']['hostname'] == 'test-host'
    
    def test_get_tailscale_status_not_installed(self):
        """Test getting Tailscale status when not installed."""
        with patch('os.path.exists', return_value=False):
            result = network_manager.get_tailscale_status()
            
            assert result['status'] == 'success'
            assert 'tailscale' in result
            assert result['tailscale']['installed'] is False
            assert result['tailscale']['running'] is False
    
    def test_configure_tailscale(self):
        """Test configuring Tailscale."""
        tailscale_config = {
            'enabled': True,
            'auth_key': 'tskey-abcdef123456'
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 0
            
            result = network_manager.configure_tailscale(tailscale_config)
            
            assert result['status'] == 'success'
            assert 'Tailscale configured and started' in result['message']
    
    def test_configure_tailscale_not_installed(self):
        """Test configuring Tailscale when not installed."""
        tailscale_config = {
            'enabled': True,
            'auth_key': 'tskey-abcdef123456'
        }
        
        with patch('os.path.exists', return_value=False):
            result = network_manager.configure_tailscale(tailscale_config)
            
            assert result['status'] == 'error'
            assert 'not installed' in result['message']
    
    def test_configure_tailscale_missing_key(self):
        """Test configuring Tailscale with missing auth key."""
        tailscale_config = {
            'enabled': True,
            'auth_key': ''
        }
        
        with patch('os.path.exists', return_value=True):
            result = network_manager.configure_tailscale(tailscale_config)
            
            assert result['status'] == 'error'
            assert 'auth key is required' in result['message']
    
    def test_get_network_info(self):
        """Test getting comprehensive network information."""
        interfaces_result = {
            'status': 'success',
            'interfaces': {
                'eth0': {'type': 'ethernet', 'addresses': []}
            }
        }
        
        vpn_result = {
            'status': 'success',
            'vpn': {
                'connected': True,
                'provider': 'gluetun'
            }
        }
        
        tailscale_result = {
            'status': 'success',
            'tailscale': {
                'installed': True,
                'running': True
            }
        }
        
        with patch('src.core.network_manager.get_network_interfaces', return_value=interfaces_result), \
             patch('src.core.network_manager.get_vpn_status', return_value=vpn_result), \
             patch('src.core.network_manager.get_tailscale_status', return_value=tailscale_result):
            
            result = network_manager.get_network_info()
            
            assert 'interfaces' in result
            assert 'vpn' in result
            assert 'tailscale' in result
            assert result['interfaces'] == interfaces_result['interfaces']
            assert result['vpn'] == vpn_result['vpn']
            assert result['tailscale'] == tailscale_result['tailscale']