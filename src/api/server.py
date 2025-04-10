"""
API server module for Pi-PVARR.

This module provides a RESTful API server for the Pi-PVARR application:
- System information
- Configuration management
- Service management
- Docker container control
"""

import os
import datetime
from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS

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
    
    # Enable CORS with specific settings
    CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})
    
    # Determine the absolute path to the web directory
    # First check if we're running in the installed directory structure
    installed_web_dir = os.path.join(os.path.expanduser('~'), 'Pi-PVARR', 'src', 'web')
    
    if os.path.exists(installed_web_dir):
        web_dir = installed_web_dir
    else:
        # Fall back to the development path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        web_dir = os.path.join(parent_dir, 'web')
    
    # Log the web directory path for debugging
    app.logger.info(f"Web directory path: {web_dir}")
    if os.path.exists(web_dir):
        app.logger.info(f"Files in web directory: {os.listdir(web_dir)}")
        
        # Check for key web assets
        css_dir = os.path.join(web_dir, 'css')
        js_dir = os.path.join(web_dir, 'js')
        index_file = os.path.join(web_dir, 'index.html')
        
        app.logger.info(f"CSS directory exists: {os.path.exists(css_dir)}")
        if os.path.exists(css_dir):
            app.logger.info(f"CSS files: {os.listdir(css_dir)}")
            
        app.logger.info(f"JS directory exists: {os.path.exists(js_dir)}")
        if os.path.exists(js_dir):
            app.logger.info(f"JS files: {os.listdir(js_dir)}")
            
        app.logger.info(f"index.html exists: {os.path.exists(index_file)}")
    else:
        app.logger.error(f"Web directory not found: {web_dir}")
    
    # Set the web directory as an app config
    app.config['WEB_DIR'] = web_dir
    
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
        Mount a drive or network share.
        
        Returns:
            JSON: Status message.
        """
        data = request.json
        
        # Check for required parameters
        if not data.get('device') or not data.get('mountpoint'):
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameters: device and mountpoint'
            })
        
        # Get optional parameters with defaults
        fstype = data.get('fstype', 'auto')
        mount_options = data.get('mount_options')
        add_to_fstab = data.get('add_to_fstab', False)
        
        # First validate the device
        if data.get('validate', True):
            validation_result = storage_manager.validate_device(data.get('device'), fstype)
            if validation_result['status'] == 'error':
                return jsonify(validation_result)
        
        # Mount the drive
        result = storage_manager.mount_drive(
            data.get('device'),
            data.get('mountpoint'),
            fstype,
            mount_options,
            add_to_fstab
        )
        
        # If successful and verification requested, verify the mount
        if result['status'] == 'success' and data.get('verify', False):
            verify_result = storage_manager.verify_mount(
                data.get('mountpoint'),
                data.get('uid', 1000),
                data.get('gid', 1000)
            )
            
            # If verification failed, unmount and return error
            if verify_result['status'] == 'error':
                storage_manager.unmount_drive(data.get('mountpoint'))
                return jsonify(verify_result)
            
            # If verification has warnings, include them in the result
            if verify_result['status'] == 'warning':
                result['warning'] = verify_result['message']
        
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
    
    @app.route('/debug', methods=['GET'])
    def debug():
        """Debug route to verify server is working."""
        client_ip = request.remote_addr
        hostname = request.host
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        app.logger.info(f"Debug route accessed from IP: {client_ip}, Host: {hostname}, User-Agent: {user_agent}")
        
        return jsonify({
            "status": "ok", 
            "message": "Server is running",
            "client_ip": client_ip,
            "hostname": hostname,
            "user_agent": user_agent,
            "server_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    @app.route('/', methods=['GET'])
    def index():
        """
        Serve the main page.
        
        Returns:
            HTML: The main page or redirects to installation wizard if needed.
        """
        try:
            # Use the absolute path from the app config
            web_dir = app.config['WEB_DIR']
            app.logger.info(f"Serving index.html from {web_dir}")
            
            # Add status information to help debug
            if request.args.get('status') == 'debug':
                return jsonify({
                    "status": "ok",
                    "web_dir": web_dir,
                    "files": os.listdir(web_dir) if os.path.exists(web_dir) else "Directory not found",
                    "index_exists": os.path.exists(os.path.join(web_dir, 'index.html'))
                })
            
            # Check if installation is required
            install_status = install_wizard.get_installation_status()
            app.logger.info(f"Installation status: {install_status.get('status', 'unknown')}")
            
            # Redirect to installation wizard if not completed
            if install_status.get('status') in ['not_started', 'in_progress', 'failed']:
                return redirect('/install')
            
            response = send_from_directory(web_dir, 'index.html')
            app.logger.info(f"Response headers: {dict(response.headers)}")
            return response
        except Exception as e:
            app.logger.error(f"Error serving index.html: {str(e)}")
            return jsonify({"error": str(e), "web_dir": app.config.get('WEB_DIR', 'Not set')}), 500
    
    @app.route('/install', methods=['GET'])
    def install_wizard_page():
        """
        Serve the installation wizard page.
        
        Returns:
            HTML: The installation wizard page.
        """
        try:
            web_dir = app.config['WEB_DIR']
            app.logger.info(f"Serving install.html from {web_dir}")
            
            install_html_path = os.path.join(web_dir, 'install.html')
            if os.path.exists(install_html_path):
                response = send_from_directory(web_dir, 'install.html')
                app.logger.info(f"Response headers: {dict(response.headers)}")
                return response
            else:
                app.logger.error(f"install.html not found at {install_html_path}")
                return jsonify({"error": "Installation page not found"}), 404
        except Exception as e:
            app.logger.error(f"Error serving install.html: {str(e)}")
            return jsonify({"error": str(e)}), 500
            
    @app.route('/favicon.ico')
    def favicon():
        """Handle browser requests for favicon."""
        app.logger.info("Favicon requested")
        web_dir = app.config['WEB_DIR']
        favicon_path = os.path.join(web_dir, 'favicon.ico')
        
        if os.path.exists(favicon_path):
            return send_from_directory(web_dir, 'favicon.ico')
        else:
            return '', 204  # No content response
    
    @app.route('/<path:path>', methods=['GET'])
    def serve_static(path):
        """
        Serve static files.
        
        Args:
            path: The file path.
        
        Returns:
            File: The requested file.
        """
        try:
            # Use the absolute path from the app config
            web_dir = app.config['WEB_DIR']
            app.logger.info(f"Serving static file: {path} from {web_dir}")
            
            # Add status information for debugging
            if request.args.get('status') == 'debug':
                full_path = os.path.join(web_dir, path)
                return jsonify({
                    "path_requested": path,
                    "full_path": full_path,
                    "file_exists": os.path.exists(full_path),
                    "is_file": os.path.isfile(full_path) if os.path.exists(full_path) else False,
                    "parent_dir_exists": os.path.exists(os.path.dirname(full_path)) if '/' in path else True
                })
            
            # Add validation to make sure the file exists
            file_path = os.path.join(web_dir, path)
            if not os.path.exists(file_path):
                app.logger.error(f"File not found: {file_path}")
                return jsonify({"error": f"File not found: {path}"}), 404
                
            # For CSS and JS files, make sure content type is set correctly
            if path.endswith('.css'):
                response = send_from_directory(web_dir, path)
                response.headers['Content-Type'] = 'text/css'
                app.logger.info(f"Served CSS file {path} with content type {response.content_type}")
                return response
            elif path.endswith('.js'):
                response = send_from_directory(web_dir, path)
                response.headers['Content-Type'] = 'application/javascript'
                app.logger.info(f"Served JS file {path} with content type {response.content_type}")
                return response
            else:
                response = send_from_directory(web_dir, path)
                app.logger.info(f"Successfully served {path} with content type {response.content_type}")
                return response
        except Exception as e:
            app.logger.error(f"Error serving {path}: {str(e)}")
            return jsonify({"error": str(e), "web_dir": app.config.get('WEB_DIR', 'Not set')}), 500
    
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