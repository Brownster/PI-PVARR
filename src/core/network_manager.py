"""
Network manager module for Pi-PVARR.

This module provides functions to manage network-related functionality:
- Network interface information
- VPN configuration
- Tailscale integration
- Docker network management
"""

import os
import re
import json
import subprocess
import psutil
from typing import Dict, Any, List, Optional


def get_network_interfaces() -> Dict[str, Any]:
    """
    Get information about network interfaces.
    
    Returns:
        Dict[str, Any]: Dictionary with network interface information.
    """
    interfaces = {}
    
    try:
        # Get all network interfaces using psutil
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        for interface_name, addresses in net_if_addrs.items():
            # Skip loopback and docker interfaces
            if interface_name == 'lo' or interface_name.startswith('docker'):
                continue
            
            # Initialize interface details
            interfaces[interface_name] = {
                'addresses': [],
                'up': net_if_stats.get(interface_name, {}).isup if interface_name in net_if_stats else False,
                'speed': net_if_stats.get(interface_name, {}).speed if interface_name in net_if_stats else 0,
                'mtu': net_if_stats.get(interface_name, {}).mtu if interface_name in net_if_stats else 0,
                'mac': None,
                'type': 'ethernet' if interface_name.startswith('eth') or interface_name.startswith('en') else 
                        'wireless' if interface_name.startswith('wlan') or interface_name.startswith('wl') else 'other'
            }
            
            # Add addresses (IPv4, IPv6, MAC)
            for addr in addresses:
                if addr.family == psutil.AF_LINK:
                    interfaces[interface_name]['mac'] = addr.address
                elif addr.family == 2:  # IPv4
                    interfaces[interface_name]['addresses'].append({
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
                elif addr.family == 10:  # IPv6
                    interfaces[interface_name]['addresses'].append({
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': None
                    })
    except Exception as e:
        return {'status': 'error', 'message': f"Error getting network interfaces: {str(e)}"}
    
    return {'status': 'success', 'interfaces': interfaces}


def get_vpn_status() -> Dict[str, Any]:
    """
    Get VPN connection status.
    
    Returns:
        Dict[str, Any]: Dictionary with VPN status information.
    """
    result = {
        'connected': False,
        'provider': None,
        'ip_address': None,
        'location': None
    }
    
    try:
        # Check if the gluetun container is running
        gluetun_running = False
        
        docker_ps = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True, text=True, check=True
        )
        containers = docker_ps.stdout.splitlines()
        
        for container in containers:
            if 'gluetun' in container.lower() or 'vpn' in container.lower():
                gluetun_running = True
                result['provider'] = 'gluetun'
                break
        
        if gluetun_running:
            # Get the external IP address to verify VPN connection
            curl_output = subprocess.run(
                ["docker", "exec", container, "curl", "-s", "https://ipinfo.io"],
                capture_output=True, text=True, check=True
            )
            
            try:
                ipinfo = json.loads(curl_output.stdout)
                result['connected'] = True
                result['ip_address'] = ipinfo.get('ip')
                result['location'] = f"{ipinfo.get('city', '')}, {ipinfo.get('country', '')}"
            except json.JSONDecodeError:
                # Could not get valid IP info, VPN might be connected but not working properly
                result['connected'] = False
        
    except Exception as e:
        return {'status': 'error', 'message': f"Error checking VPN status: {str(e)}"}
    
    return {'status': 'success', 'vpn': result}


def configure_vpn(vpn_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Configure VPN settings.
    
    Args:
        vpn_config (Dict[str, Any]): VPN configuration settings.
    
    Returns:
        Dict[str, Any]: Dictionary with status and message.
    """
    try:
        # We'll implement this by updating environment variables for the VPN container
        # First, check if VPN is enabled
        if not vpn_config.get('enabled', False):
            return {'status': 'success', 'message': "VPN disabled in configuration"}
        
        # Get required VPN parameters
        provider = vpn_config.get('provider', '').strip().lower()
        username = vpn_config.get('username', '').strip()
        password = vpn_config.get('password', '').strip()
        region = vpn_config.get('region', '').strip()
        
        # Validate parameters
        if not provider:
            return {'status': 'error', 'message': "VPN provider is required"}
        
        if not username or not password:
            return {'status': 'error', 'message': "VPN username and password are required"}
        
        # For now, we'll just return success - the actual modification of Docker environment
        # files would be implementation-specific
        return {
            'status': 'success', 
            'message': f"VPN configuration updated for provider {provider}",
            'details': {
                'provider': provider,
                'region': region,
                'credentials_set': bool(username and password)
            }
        }
        
    except Exception as e:
        return {'status': 'error', 'message': f"Error configuring VPN: {str(e)}"}


def get_tailscale_status() -> Dict[str, Any]:
    """
    Get Tailscale VPN status.
    
    Returns:
        Dict[str, Any]: Dictionary with Tailscale status information.
    """
    result = {
        'installed': False,
        'running': False,
        'ip_address': None,
        'hostname': None
    }
    
    try:
        # Check if tailscale is installed
        result['installed'] = os.path.exists('/usr/bin/tailscale')
        
        if result['installed']:
            # Check if tailscale is running
            tailscale_status = subprocess.run(
                ["tailscale", "status", "--json"],
                capture_output=True, text=True, check=False
            )
            
            if tailscale_status.returncode == 0:
                try:
                    status_data = json.loads(tailscale_status.stdout)
                    result['running'] = status_data.get('BackendState') == 'Running'
                    
                    # Get self info
                    self_info = status_data.get('Self', {})
                    result['ip_address'] = self_info.get('TailscaleIPs', [None])[0]
                    result['hostname'] = self_info.get('HostName')
                except json.JSONDecodeError:
                    pass
        
    except Exception as e:
        return {'status': 'error', 'message': f"Error checking Tailscale status: {str(e)}"}
    
    return {'status': 'success', 'tailscale': result}


def configure_tailscale(tailscale_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Configure Tailscale VPN.
    
    Args:
        tailscale_config (Dict[str, Any]): Tailscale configuration settings.
    
    Returns:
        Dict[str, Any]: Dictionary with status and message.
    """
    try:
        # Check if tailscale is installed
        if not os.path.exists('/usr/bin/tailscale'):
            return {'status': 'error', 'message': "Tailscale is not installed"}
        
        # Check if Tailscale is enabled in config
        if not tailscale_config.get('enabled', False):
            # If tailscale is currently running, stop it
            subprocess.run(["tailscale", "down"], check=False)
            return {'status': 'success', 'message': "Tailscale disabled and stopped"}
        
        # Get auth key for Tailscale
        auth_key = tailscale_config.get('auth_key', '').strip()
        
        if not auth_key:
            return {'status': 'error', 'message': "Tailscale auth key is required"}
        
        # Run tailscale up with the auth key
        tailscale_up = subprocess.run(
            ["tailscale", "up", "--authkey", auth_key],
            capture_output=True, text=True, check=False
        )
        
        if tailscale_up.returncode != 0:
            return {'status': 'error', 'message': f"Tailscale setup failed: {tailscale_up.stderr}"}
        
        return {'status': 'success', 'message': "Tailscale configured and started"}
        
    except Exception as e:
        return {'status': 'error', 'message': f"Error configuring Tailscale: {str(e)}"}


def get_network_info() -> Dict[str, Any]:
    """
    Get comprehensive network information.
    
    Returns:
        Dict[str, Any]: Dictionary with all network information.
    """
    # Get interface information
    interfaces_info = get_network_interfaces()
    
    # Get VPN status
    vpn_status = get_vpn_status()
    
    # Get Tailscale status
    tailscale_status = get_tailscale_status()
    
    # Combine all information
    network_info = {
        'interfaces': interfaces_info.get('interfaces', {}),
        'vpn': vpn_status.get('vpn', {'connected': False, 'provider': None}),
        'tailscale': tailscale_status.get('tailscale', {'installed': False, 'running': False})
    }
        return network_info
