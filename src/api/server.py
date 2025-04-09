"""
API server module for Pi-PVARR.

This module provides a RESTful API server for the Pi-PVARR application:
- System information
- Configuration management
- Service management
- Docker container control
"""

import os
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from typing import Dict, Any

from src.core import system_info, config, docker_manager, storage_manager, network_manager, service_manager, install_wizard


def create_app(test_config=None):
    """
    Create and configure the Flask application.
    
    Args:
        test_config: Configuration for testing (optional).
    
    Returns:
        Flask: The configured Flask application.
    """
    # Create Flask app
    app = Flask(__name__, instance_relative_config=True)
    
    # Enable CORS
    CORS(app)
    
    # Apply test configuration if provided
    if test_config:
        app.config.update(test_config)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass
    
    # Define API routes
    
    @app.route('/api/system', methods=['GET'])
    def get_system_info():
        """
        Get system information.
        
        Returns:
            JSON: System information.
        """
        return jsonify(system_info.get_system_info())
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """
        Get configuration.
        
        Returns:
            JSON: Configuration settings.
        """
        return jsonify(config.get_config())
    
    @app.route('/api/config', methods=['POST'])
    def update_config():
        """
        Update configuration.
        
        Returns:
            JSON: Status message.
        """
        new_config = request.json
        config.save_config_wrapper(new_config)
        return jsonify({"status": "success"})
    
    @app.route('/api/services', methods=['GET'])
    def get_services():
        """
        Get services configuration.
        
        Returns:
            JSON: Services configuration.
        """
        return jsonify(config.get_services_config())
    
    @app.route('/api/services', methods=['POST'])
    def update_services():
        """
        Update services configuration.
        
        Returns:
            JSON: Status message.
        """
        new_services = request.json
        config.save_services_config(new_services)
        return jsonify({"status": "success"})
    
    @app.route('/api/containers', methods=['GET'])
    def get_containers():
        """
        Get container status for all Docker containers.
        
        Returns:
            JSON: Container status information.
        """
        return jsonify(docker_manager.get_container_status())
    
    @app.route('/api/containers/<container_name>', methods=['GET'])
    def get_container_info(container_name):
        """
        Get detailed information about a specific container.
        
        Args:
            container_name: The name of the container.
        
        Returns:
            JSON: Container information.
        """
        return jsonify(docker_manager.get_container_info(container_name))
    
    @app.route('/api/containers/<container_name>/logs', methods=['GET'])
    def get_container_logs(container_name):
        """
        Get logs for a specific container.
        
        Args:
            container_name: The name of the container.
        
        Returns:
            JSON: Container logs.
        """
        lines = request.args.get('lines', default=100, type=int)
        logs = docker_manager.get_container_logs(container_name, lines)
        return jsonify({"container": container_name, "logs": logs})
    
    @app.route('/api/containers/<container_name>/start', methods=['POST'])
    def start_container(container_name):
        """
        Start a specific container.
        
        Args:
            container_name: The name of the container.
        
        Returns:
            JSON: Status message.
        """
        result = docker_manager.start_container(container_name)
        return jsonify(result)
    
    @app.route('/api/containers/<container_name>/stop', methods=['POST'])
    def stop_container(container_name):
        """
        Stop a specific container.
        
        Args:
            container_name: The name of the container.
        
        Returns:
            JSON: Status message.
        """
        result = docker_manager.stop_container(container_name)
        return jsonify(result)
    
    @app.route('/api/containers/<container_name>/restart', methods=['POST'])
    def restart_container(container_name):
        """
        Restart a specific container.
        
        Args:
            container_name: The name of the container.
        
        Returns:
            JSON: Status message.
        """
        result = docker_manager.restart_container(container_name)
        return jsonify(result)
    
    @app.route('/api/containers/update', methods=['POST'])
    def update_containers():
        """
        Update all containers.
        
        Returns:
            JSON: Status message with details.
        """
        result = docker_manager.update_all_containers()
        return jsonify(result)
    
    # Storage management endpoints
    
    @app.route('/api/storage/drives', methods=['GET'])
    def get_drives():
        """
        Get information about all drives.
        
        Returns:
            JSON: Drive information.
        """
        return jsonify(storage_manager.get_drives_info())
    
    @app.route('/api/storage/mounts', methods=['GET'])
    def get_mounts():
        """
        Get information about mounted drives.
        
        Returns:
            JSON: Mount point information.
        """
        return jsonify(storage_manager.get_mount_points())
    
    @app.route('/api/storage/mount', methods=['POST'])
    def mount_drive():
        """
        Mount a drive.
        
        Returns:
            JSON: Status message.
        """
        data = request.json
        result = storage_manager.mount_drive(
            data.get('device'),
            data.get('mountpoint'),
            data.get('fstype', 'auto')
        )
        return jsonify(result)
    
    @app.route('/api/storage/unmount', methods=['POST'])
    def unmount_drive():
        """
        Unmount a drive.
        
        Returns:
            JSON: Status message.
        """
        data = request.json
        result = storage_manager.unmount_drive(data.get('mountpoint'))
        return jsonify(result)
    
    @app.route('/api/storage/directory', methods=['GET'])
    def get_directory_info():
        """
        Get information about a directory.
        
        Returns:
            JSON: Directory information.
        """
        path = request.args.get('path', '')
        if not path:
            return jsonify({"status": "error", "message": "Path parameter is required"})
        return jsonify(storage_manager.get_directory_info(path))
    
    @app.route('/api/storage/directories', methods=['POST'])
    def get_directories_info():
        """
        Get information about multiple directories.
        
        Returns:
            JSON: Directory information for multiple directories.
        """
        data = request.json
        paths = data.get('paths', [])
        return jsonify(storage_manager.get_directories_info(paths))
    
    @app.route('/api/storage/directory/create', methods=['POST'])
    def create_directory():
        """
        Create a directory.
        
        Returns:
            JSON: Status message.
        """
        data = request.json
        result = storage_manager.create_directory(
            data.get('path'),
            data.get('uid', 1000),
            data.get('gid', 1000),
            data.get('mode', 0o755)
        )
        return jsonify(result)
    
    @app.route('/api/storage/shares', methods=['GET'])
    def get_network_shares():
        """
        Get information about network shares.
        
        Returns:
            JSON: Network share information.
        """
        return jsonify(storage_manager.get_shares())
    
    @app.route('/api/storage/shares/add', methods=['POST'])
    def add_network_share():
        """
        Add a network share.
        
        Returns:
            JSON: Status message.
        """
        data = request.json
        result = storage_manager.add_share(data)
        return jsonify(result)
    
    @app.route('/api/storage/shares/remove', methods=['POST'])
    def remove_network_share():
        """
        Remove a network share.
        
        Returns:
            JSON: Status message.
        """
        data = request.json
        result = storage_manager.remove_share(data.get('name'))
        return jsonify(result)
    
    @app.route('/api/storage/media/create', methods=['POST'])
    def create_media_directories():
        """
        Create standard media directories.
        
        Returns:
            JSON: Status message.
        """
        data = request.json
        result = storage_manager.create_media_directories(
            data.get('base_dir'),
            data.get('uid', 1000),
            data.get('gid', 1000)
        )
        return jsonify(result)
    
    # Network management endpoints
    
    @app.route('/api/network/interfaces', methods=['GET'])
    def get_network_interfaces():
        """
        Get information about network interfaces.
        
        Returns:
            JSON: Network interface information.
        """
        return jsonify(network_manager.get_network_interfaces())
    
    @app.route('/api/network/info', methods=['GET'])
    def get_network_info():
        """
        Get comprehensive network information.
        
        Returns:
            JSON: Network information including interfaces, VPN, and Tailscale.
        """
        return jsonify(network_manager.get_network_info())
    
    @app.route('/api/network/vpn/status', methods=['GET'])
    def get_vpn_status():
        """
        Get VPN connection status.
        
        Returns:
            JSON: VPN status information.
        """
        return jsonify(network_manager.get_vpn_status())
    
    @app.route('/api/network/vpn/configure', methods=['POST'])
    def configure_vpn():
        """
        Configure VPN settings.
        
        Returns:
            JSON: Status message.
        """
        vpn_config = request.json
        result = network_manager.configure_vpn(vpn_config)
        return jsonify(result)
    
    @app.route('/api/network/tailscale/status', methods=['GET'])
    def get_tailscale_status():
        """
        Get Tailscale VPN status.
        
        Returns:
            JSON: Tailscale status information.
        """
        return jsonify(network_manager.get_tailscale_status())
    
    @app.route('/api/network/tailscale/configure', methods=['POST'])
    def configure_tailscale():
        """
        Configure Tailscale VPN.
        
        Returns:
            JSON: Status message.
        """
        tailscale_config = request.json
        result = network_manager.configure_tailscale(tailscale_config)
        return jsonify(result)
    
    # Service management endpoints
    
    @app.route('/api/services/info', methods=['GET'])
    def get_services_info():
        """
        Get comprehensive information about services.
        
        Returns:
            JSON: Service information including status, descriptions, and configuration.
        """
        return jsonify(service_manager.get_service_info())
    
    @app.route('/api/services/toggle', methods=['POST'])
    def toggle_service():
        """
        Enable or disable a service.
        
        Returns:
            JSON: Status message.
        """
        data = request.json
        if 'service_name' not in data or 'enabled' not in data:
            return jsonify({
                "status": "error",
                "message": "Missing required parameters: service_name and enabled"
            })
        
        result = service_manager.toggle_service(data['service_name'], data['enabled'])
        return jsonify(result)
    
    @app.route('/api/services/compatibility', methods=['GET'])
    def get_service_compatibility():
        """
        Get service compatibility information for the current system.
        
        Returns:
            JSON: Service compatibility information.
        """
        return jsonify(service_manager.get_service_compatibility())
    
    @app.route('/api/services/compose', methods=['GET'])
    def generate_docker_compose():
        """
        Generate Docker Compose file based on current service configuration.
        
        Returns:
            JSON: Docker Compose file content.
        """
        result = service_manager.generate_docker_compose()
        return jsonify(result)
    
    @app.route('/api/services/env', methods=['GET'])
    def generate_env_file():
        """
        Generate environment file for Docker Compose.
        
        Returns:
            JSON: Environment file content.
        """
        result = service_manager.generate_env_file()
        return jsonify(result)
    
    @app.route('/api/services/apply', methods=['POST'])
    def apply_service_changes():
        """
        Apply service changes by regenerating Docker Compose files.
        
        Returns:
            JSON: Status message.
        """
        result = service_manager.apply_service_changes()
        return jsonify(result)
    
    @app.route('/api/services/start', methods=['POST'])
    def start_services():
        """
        Start services using Docker Compose.
        
        Returns:
            JSON: Status message.
        """
        result = service_manager.start_services()
        return jsonify(result)
    
    @app.route('/api/services/stop', methods=['POST'])
    def stop_services():
        """
        Stop services using Docker Compose.
        
        Returns:
            JSON: Status message.
        """
        result = service_manager.stop_services()
        return jsonify(result)
    
    @app.route('/api/services/restart', methods=['POST'])
    def restart_services():
        """
        Restart services using Docker Compose.
        
        Returns:
            JSON: Status message.
        """
        result = service_manager.restart_services()
        return jsonify(result)
    
    @app.route('/api/services/status', methods=['GET'])
    def get_installation_status():
        """
        Get the current installation status.
        
        Returns:
            JSON: Installation status information.
        """
        return jsonify(service_manager.get_installation_status())
    
    # Installation wizard endpoints
    
    @app.route('/api/install/status', methods=['GET'])
    def get_wizard_status():
        """
        Get the current installation wizard status.
        
        Returns:
            JSON: Installation wizard status information.
        """
        return jsonify(install_wizard.get_installation_status())
    
    @app.route('/api/install/compatibility', methods=['GET'])
    def check_system_compatibility():
        """
        Check system compatibility for installation.
        
        Returns:
            JSON: System compatibility information.
        """
        return jsonify(install_wizard.check_system_compatibility())
    
    @app.route('/api/install/config', methods=['POST'])
    def setup_basic_configuration():
        """
        Set up basic configuration for installation.
        
        Returns:
            JSON: Configuration setup status.
        """
        user_config = request.json
        return jsonify(install_wizard.setup_basic_configuration(user_config))
    
    @app.route('/api/install/network', methods=['POST'])
    def setup_network_configuration():
        """
        Set up network configuration for installation.
        
        Returns:
            JSON: Network configuration setup status.
        """
        network_config = request.json
        return jsonify(install_wizard.setup_network_configuration(network_config))
    
    @app.route('/api/install/storage', methods=['POST'])
    def setup_storage_configuration():
        """
        Set up storage configuration for installation.
        
        Returns:
            JSON: Storage configuration setup status.
        """
        storage_config = request.json
        return jsonify(install_wizard.setup_storage_configuration(storage_config))
    
    @app.route('/api/install/services', methods=['POST'])
    def setup_service_selection():
        """
        Set up service selection for installation.
        
        Returns:
            JSON: Service selection setup status.
        """
        services_config = request.json
        return jsonify(install_wizard.setup_service_selection(services_config))
    
    @app.route('/api/install/dependencies', methods=['POST'])
    def install_dependencies():
        """
        Install dependencies for Pi-PVARR.
        
        Returns:
            JSON: Dependency installation status.
        """
        return jsonify(install_wizard.install_dependencies())
    
    @app.route('/api/install/docker', methods=['POST'])
    def setup_docker():
        """
        Set up Docker and Docker Compose.
        
        Returns:
            JSON: Docker setup status.
        """
        return jsonify(install_wizard.setup_docker())
    
    @app.route('/api/install/compose', methods=['POST'])
    def generate_compose_files():
        """
        Generate Docker Compose files based on service configuration.
        
        Returns:
            JSON: Docker Compose generation status.
        """
        return jsonify(install_wizard.generate_compose_files())
    
    @app.route('/api/install/containers', methods=['POST'])
    def create_containers():
        """
        Create Docker containers based on generated Docker Compose files.
        
        Returns:
            JSON: Container creation status.
        """
        return jsonify(install_wizard.create_containers())
    
    @app.route('/api/install/post', methods=['POST'])
    def perform_post_installation():
        """
        Perform post-installation tasks.
        
        Returns:
            JSON: Post-installation status.
        """
        return jsonify(install_wizard.perform_post_installation())
    
    @app.route('/api/install/finalize', methods=['POST'])
    def finalize_installation():
        """
        Finalize the installation process.
        
        Returns:
            JSON: Finalization status.
        """
        return jsonify(install_wizard.finalize_installation())
    
    @app.route('/api/install/run', methods=['POST'])
    def run_installation():
        """
        Run the complete installation process.
        
        Returns:
            JSON: Installation status.
        """
        installation_config = request.json
        return jsonify(install_wizard.run_installation(installation_config))
    
    @app.route('/', methods=['GET'])
    def index():
        """
        Serve the main page.
        
        Returns:
            HTML: The main page.
        """
        return send_from_directory('../web/dist', 'index.html')
    
    @app.route('/<path:path>', methods=['GET'])
    def serve_static(path):
        """
        Serve static files.
        
        Args:
            path: The file path.
        
        Returns:
            File: The requested file.
        """
        return send_from_directory('../web/dist', path)
    
    return app


def run_server(host='0.0.0.0', port=8080, debug=False):
    """
    Run the API server.
    
    Args:
        host (str): The host to bind to. Defaults to '0.0.0.0' (all interfaces).
        port (int): The port to bind to. Defaults to 8080.
        debug (bool): Whether to run in debug mode. Defaults to False.
    """
    app = create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server(debug=True)