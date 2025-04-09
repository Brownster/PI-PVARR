"""
Docker manager module for Pi-PVARR.

This module provides functions to manage Docker containers:
- Get container status
- Start, stop, and restart containers
- Get container logs
- Get container information
"""

import re
from typing import Dict, Any, List, Optional

# Conditionally import Docker client
try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


def get_container_status() -> Dict[str, Dict[str, Any]]:
    """
    Get the status of all Docker containers.
    
    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of container information indexed by container name.
    """
    containers = {}
    
    if not DOCKER_AVAILABLE:
        containers['error'] = {
            'status': 'error',
            'message': "Docker Python SDK is not installed. Docker functionality is unavailable.",
            'type': 'other',
            'description': 'Docker Python SDK missing'
        }
        return containers
    
    try:
        # Connect to Docker
        client = docker.from_env()
        
        # Get list of all containers
        for container in client.containers.list(all=True):
            # Extract port mappings
            ports = []
            if hasattr(container, 'ports') and container.ports:
                for container_port, host_mappings in container.ports.items():
                    # container_port is like '8080/tcp'
                    if host_mappings:
                        for mapping in host_mappings:
                            ports.append({
                                'container': container_port.split('/')[0],
                                'host': mapping['HostPort'],
                                'protocol': container_port.split('/')[1] if '/' in container_port else 'tcp'
                            })
            
            # Determine container type and description
            container_name = container.name
            container_type = 'other'
            description = 'Docker container'
            
            # Try to determine container type and description from name
            if any(x in container_name.lower() for x in ['sonarr', 'radarr', 'lidarr', 'readarr', 'prowlarr', 'bazarr']):
                container_type = 'media'
                if 'sonarr' in container_name.lower():
                    description = 'TV Series Management'
                elif 'radarr' in container_name.lower():
                    description = 'Movie Management'
                elif 'lidarr' in container_name.lower():
                    description = 'Music Management'
                elif 'readarr' in container_name.lower():
                    description = 'Book Management'
                elif 'prowlarr' in container_name.lower():
                    description = 'Indexer Management'
                elif 'bazarr' in container_name.lower():
                    description = 'Subtitle Management'
            elif any(x in container_name.lower() for x in ['transmission', 'qbittorrent', 'nzbget', 'sabnzbd', 'jdownloader']):
                container_type = 'download'
                if 'transmission' in container_name.lower():
                    description = 'Torrent Client'
                elif 'qbittorrent' in container_name.lower():
                    description = 'Torrent Client'
                elif 'nzbget' in container_name.lower():
                    description = 'Usenet Client'
                elif 'sabnzbd' in container_name.lower():
                    description = 'Usenet Client'
                elif 'jdownloader' in container_name.lower():
                    description = 'Direct Download Client'
            elif any(x in container_name.lower() for x in ['jellyfin', 'plex', 'emby']):
                container_type = 'media'
                description = 'Media Server'
            elif any(x in container_name.lower() for x in ['portainer', 'heimdall', 'overseerr', 'tautulli', 'nginx']):
                container_type = 'utility'
                if 'portainer' in container_name.lower():
                    description = 'Docker Management'
                elif 'heimdall' in container_name.lower():
                    description = 'Application Dashboard'
                elif 'overseerr' in container_name.lower():
                    description = 'Media Requests'
                elif 'tautulli' in container_name.lower():
                    description = 'Plex Monitoring'
                elif 'nginx' in container_name.lower():
                    description = 'Reverse Proxy'
            
            # Determine URL based on port mappings
            url = None
            if container.status == 'running' and ports:
                web_ports = ['80', '8080', '8096', '9090', '9091', '7878', '8989', '8686', '8787', '9696', '6767', '6789', '5055', '8181']
                for port_info in ports:
                    if port_info['container'] in web_ports:
                        url = f"http://localhost:{port_info['host']}"
                        break
            
            # Create container info
            containers[container.name] = {
                'status': container.status,
                'ports': ports,
                'type': container_type,
                'description': description,
                'url': url
            }
    except Exception as e:
        # Handle errors
        containers['error'] = {
            'status': 'error',
            'message': f"Error getting container status: {str(e)}",
            'type': 'other',
            'description': 'Error checking Docker status'
        }
    
    return containers


def get_container_logs(container_name: str, lines: int = 100) -> str:
    """
    Get logs from a Docker container.
    
    Args:
        container_name (str): The name of the container.
        lines (int, optional): Number of log lines to retrieve. Defaults to 100.
    
    Returns:
        str: Container logs.
    """
    if not DOCKER_AVAILABLE:
        return "Docker Python SDK is not installed. Cannot fetch container logs."
    
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        logs = container.logs(tail=lines)
        return logs.decode('utf-8')
    except Exception as e:
        return f"Error getting logs for container {container_name}: {str(e)}"


def start_container(container_name: str) -> Dict[str, str]:
    """
    Start a Docker container.
    
    Args:
        container_name (str): The name of the container to start.
    
    Returns:
        Dict[str, str]: Dictionary with status and message.
    """
    if not DOCKER_AVAILABLE:
        return {'status': 'error', 'message': "Docker Python SDK is not installed. Docker functionality is unavailable."}
    
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        container.start()
        return {'status': 'success', 'message': f"Container {container_name} started successfully"}
    except Exception as e:
        return {'status': 'error', 'message': f"Error starting container {container_name}: {str(e)}"}


def stop_container(container_name: str) -> Dict[str, str]:
    """
    Stop a Docker container.
    
    Args:
        container_name (str): The name of the container to stop.
    
    Returns:
        Dict[str, str]: Dictionary with status and message.
    """
    if not DOCKER_AVAILABLE:
        return {'status': 'error', 'message': "Docker Python SDK is not installed. Docker functionality is unavailable."}
    
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        container.stop()
        return {'status': 'success', 'message': f"Container {container_name} stopped successfully"}
    except Exception as e:
        return {'status': 'error', 'message': f"Error stopping container {container_name}: {str(e)}"}


def restart_container(container_name: str) -> Dict[str, str]:
    """
    Restart a Docker container.
    
    Args:
        container_name (str): The name of the container to restart.
    
    Returns:
        Dict[str, str]: Dictionary with status and message.
    """
    if not DOCKER_AVAILABLE:
        return {'status': 'error', 'message': "Docker Python SDK is not installed. Docker functionality is unavailable."}
    
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        container.restart()
        return {'status': 'success', 'message': f"Container {container_name} restarted successfully"}
    except Exception as e:
        return {'status': 'error', 'message': f"Error restarting container {container_name}: {str(e)}"}


def get_container_info(container_name: str) -> Dict[str, Any]:
    """
    Get detailed information about a Docker container.
    
    Args:
        container_name (str): The name of the container.
    
    Returns:
        Dict[str, Any]: Dictionary with container information.
    """
    if not DOCKER_AVAILABLE:
        return {'status': 'error', 'message': "Docker Python SDK is not installed. Docker functionality is unavailable."}
    
    try:
        client = docker.from_env()
        container = client.containers.get(container_name)
        
        # Extract port mappings
        ports = []
        # Check for the NetworkSettings.Ports in container attributes
        network_settings = container.attrs.get('NetworkSettings', {})
        container_ports = network_settings.get('Ports', {})
        
        for container_port, host_mappings in container_ports.items():
            if host_mappings:
                for mapping in host_mappings:
                    container_port_number = container_port.split('/')[0]
                    host_port = mapping.get('HostPort', '')
                    protocol = container_port.split('/')[1] if '/' in container_port else 'tcp'
                    
                    ports.append({
                        'container': container_port_number,
                        'host': host_port,
                        'protocol': protocol
                    })
        
        # Get config settings safely
        config = container.attrs.get('Config', {})
        
        # Create container info
        return {
            'name': container.name,
            'status': container.status,
            'image': config.get('Image', ''),
            'created': container.attrs.get('Created', ''),
            'ports': ports,
            'volumes': list(config.get('Volumes', {}).keys()) if config.get('Volumes') else [],
            'environment': config.get('Env', []),
            'labels': config.get('Labels', {})
        }
    except Exception as e:
        return {'status': 'error', 'message': f"Error getting container info: {str(e)}"}


def pull_image(image_name: str) -> Dict[str, str]:
    """
    Pull a Docker image.
    
    Args:
        image_name (str): The name of the image to pull.
    
    Returns:
        Dict[str, str]: Dictionary with status and message.
    """
    if not DOCKER_AVAILABLE:
        return {'status': 'error', 'message': "Docker Python SDK is not installed. Docker functionality is unavailable."}
    
    try:
        client = docker.from_env()
        client.images.pull(image_name)
        return {'status': 'success', 'message': f"Image {image_name} pulled successfully"}
    except Exception as e:
        return {'status': 'error', 'message': f"Error pulling image {image_name}: {str(e)}"}


def update_all_containers() -> Dict[str, Any]:
    """
    Update all containers by pulling their images and recreating them.
    
    Returns:
        Dict[str, Any]: Dictionary with status and details.
    """
    if not DOCKER_AVAILABLE:
        return {'status': 'error', 'message': "Docker Python SDK is not installed. Docker functionality is unavailable."}
    
    results = {
        'status': 'success',
        'message': "Update process completed",
        'details': []
    }
    
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        
        for container in containers:
            try:
                # Get current container information
                container_info = get_container_info(container.name)
                
                # Pull the latest image
                image_name = container_info.get('image', '')
                if image_name:
                    pull_result = pull_image(image_name)
                else:
                    pull_result = {'status': 'error', 'message': 'Image name not found'}
                
                if pull_result['status'] == 'success':
                    # Restart the container to use the new image
                    if container.status == 'running':
                        container.restart()
                        results['details'].append({
                            'container': container.name,
                            'status': 'updated',
                            'message': "Image pulled and container restarted"
                        })
                    else:
                        results['details'].append({
                            'container': container.name,
                            'status': 'updated',
                            'message': "Image pulled, container not running"
                        })
                else:
                    results['details'].append({
                        'container': container.name,
                        'status': 'error',
                        'message': pull_result['message']
                    })
            except Exception as e:
                results['details'].append({
                    'container': container.name,
                    'status': 'error',
                    'message': str(e)
                })
        
        # Check if any updates failed
        failed_updates = [detail for detail in results['details'] if detail['status'] == 'error']
        if failed_updates:
            results['status'] = 'partial'
            results['message'] = f"{len(failed_updates)} of {len(containers)} updates failed"
    except Exception as e:
        results['status'] = 'error'
        results['message'] = f"Error updating containers: {str(e)}"
    
    return results