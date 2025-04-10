"""
Installation wizard module for Pi-PVARR.

This module provides a step-by-step installation wizard for setting up the Pi-PVARR system:
- System compatibility checking
- Configuration collection
- Storage setup
- Service selection and configuration
- Installation process execution and tracking
"""

import os
import time
import logging
import subprocess
import platform
from typing import Dict, Any, List

from src.core import config, docker_manager, storage_manager, network_manager, service_manager, system_info

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
log_file = os.path.join(log_dir, 'install_wizard.log')

# Create logs directory if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Installation stages
INSTALLATION_STAGES = {
    "pre_check": "System Compatibility Check",
    "config_setup": "Basic Configuration Setup",
    "network_setup": "Network Configuration",
    "storage_setup": "Storage Configuration",
    "service_selection": "Service Selection",
    "dependency_install": "Installing Dependencies",
    "docker_setup": "Setting up Docker",
    "compose_generation": "Generating Docker Compose Files",
    "container_creation": "Creating Containers",
    "service_start": "Starting Services",
    "post_install": "Post-Installation Configuration",
    "finalization": "Finalizing Installation"
}

# Installation status tracking
class InstallationStatus:
    def __init__(self):
        self.current_stage = "pre_check"
        self.stage_progress = 0  # 0-100 for each stage
        self.overall_progress = 0  # 0-100 for overall installation
        self.status = "not_started"  # not_started, in_progress, completed, failed
        self.logs = []
        self.errors = []
        self.start_time = None
        self.end_time = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert installation status to a dictionary."""
        return {
            "current_stage": self.current_stage,
            "current_stage_name": INSTALLATION_STAGES.get(self.current_stage, "Unknown Stage"),
            "stage_progress": self.stage_progress,
            "overall_progress": self.overall_progress,
            "status": self.status,
            "logs": self.logs,
            "errors": self.errors,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "elapsed_time": (self.end_time - self.start_time) if (self.start_time and self.end_time) else None
        }
    
    def add_log(self, message: str) -> None:
        """Add a log message."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        logger.info(message)
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        error_entry = f"[{timestamp}] ERROR: {error}"
        self.errors.append(error_entry)
        self.logs.append(error_entry)
        logger.error(error)
    
    def update_progress(self, stage: str, progress: int) -> None:
        """Update progress for a specific stage."""
        self.current_stage = stage
        self.stage_progress = progress
        
        # Calculate overall progress based on stages
        stage_weights = {
            "pre_check": 5,
            "config_setup": 5,
            "network_setup": 10,
            "storage_setup": 10,
            "service_selection": 5,
            "dependency_install": 10,
            "docker_setup": 15,
            "compose_generation": 10,
            "container_creation": 15,
            "service_start": 10,
            "post_install": 5,
            "finalization": 0
        }
        
        # Calculate stage index and weight
        stages = list(stage_weights.keys())
        if stage in stages:
            stage_index = stages.index(stage)
            stages_completed = sum(stage_weights[s] for s in stages[:stage_index])
            current_stage_contribution = (stage_weights[stage] * progress) / 100
            self.overall_progress = int(stages_completed + current_stage_contribution)
        
        # Ensure progress is between 0 and 100
        self.overall_progress = max(0, min(100, self.overall_progress))


# Global installation status
_installation_status = InstallationStatus()


def get_installation_status() -> Dict[str, Any]:
    """
    Get the current installation status.
    
    Returns:
        Dict[str, Any]: Dictionary with installation status information.
    """
    return _installation_status.to_dict()


def check_system_compatibility() -> Dict[str, Any]:
    """
    Check system compatibility for installation.
    
    Returns:
        Dict[str, Any]: Dictionary with compatibility information.
    """
    _installation_status.update_progress("pre_check", 10)
    _installation_status.add_log("Starting system compatibility check")
    
    try:
        # Get system information
        _installation_status.update_progress("pre_check", 30)
        sys_info = system_info.get_system_info()
        
        # Memory check (minimum 2GB recommended)
        memory_gb = sys_info.get("memory", {}).get("total_gb", 0)
        memory_compatible = memory_gb >= 2
        
        _installation_status.update_progress("pre_check", 50)
        
        # Disk space check (minimum 10GB free space recommended)
        disk_free_gb = sys_info.get("disk", {}).get("free_gb", 0)
        disk_compatible = disk_free_gb >= 10
        
        _installation_status.update_progress("pre_check", 70)
        
        # Docker check
        docker_installed = sys_info.get("docker_installed", False)
        
        _installation_status.update_progress("pre_check", 90)
        
        # Overall compatibility
        compatible = memory_compatible and disk_compatible
        
        compatibility_info = {
            "status": "success",
            "compatible": compatible,
            "system_info": sys_info,
            "checks": {
                "memory": {
                    "value": memory_gb,
                    "unit": "GB",
                    "compatible": memory_compatible,
                    "recommended": 2,
                    "message": f"Memory: {memory_gb}GB" + (" (Recommended: ≥2GB)" if not memory_compatible else "")
                },
                "disk_space": {
                    "value": disk_free_gb,
                    "unit": "GB",
                    "compatible": disk_compatible,
                    "recommended": 10,
                    "message": f"Free Disk Space: {disk_free_gb}GB" + (" (Recommended: ≥10GB)" if not disk_compatible else "")
                },
                "docker": {
                    "installed": docker_installed,
                    "message": "Docker: " + ("Installed" if docker_installed else "Not installed (will be installed during setup)")
                }
            }
        }
        
        # Log results
        _installation_status.add_log(f"System compatibility check completed: {'Compatible' if compatible else 'Not fully compatible'}")
        for check_type, check_info in compatibility_info["checks"].items():
            if "message" in check_info:
                _installation_status.add_log(check_info["message"])
        
        _installation_status.update_progress("pre_check", 100)
        return compatibility_info
    
    except Exception as e:
        error_msg = f"Error during system compatibility check: {str(e)}"
        _installation_status.add_error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


def setup_basic_configuration(user_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set up basic configuration based on user input.
    
    Args:
        user_config (Dict[str, Any]): User-provided configuration.
    
    Returns:
        Dict[str, Any]: Dictionary with setup status.
    """
    _installation_status.update_progress("config_setup", 10)
    _installation_status.add_log("Setting up basic configuration")
    
    try:
        # Get default configuration
        default_config = config.get_default_config()
        
        # Merge user configuration with defaults
        merged_config = {**default_config, **user_config}
        
        # Validate configuration
        required_fields = ["puid", "pgid", "timezone", "media_dir", "downloads_dir"]
        missing_fields = [field for field in required_fields if field not in merged_config]
        
        if missing_fields:
            error_msg = f"Missing required configuration fields: {', '.join(missing_fields)}"
            _installation_status.add_error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
        
        _installation_status.update_progress("config_setup", 50)
        
        # Save configuration
        config.save_config_wrapper(merged_config)
        
        _installation_status.update_progress("config_setup", 100)
        _installation_status.add_log("Basic configuration setup completed")
        
        return {
            "status": "success",
            "message": "Basic configuration setup completed",
            "config": merged_config
        }
    
    except Exception as e:
        error_msg = f"Error during basic configuration setup: {str(e)}"
        _installation_status.add_error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


def setup_network_configuration(network_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set up network configuration based on user input.
    
    Args:
        network_config (Dict[str, Any]): User-provided network configuration.
    
    Returns:
        Dict[str, Any]: Dictionary with setup status.
    """
    _installation_status.update_progress("network_setup", 10)
    _installation_status.add_log("Setting up network configuration")
    
    try:
        # Get current configuration
        current_config = config.get_config()
        
        # Update VPN configuration if provided
        if "vpn" in network_config:
            _installation_status.update_progress("network_setup", 30)
            _installation_status.add_log("Configuring VPN settings")
            
            vpn_config = network_config.get("vpn", {})
            current_config["vpn"] = {
                "enabled": vpn_config.get("enabled", False),
                "provider": vpn_config.get("provider", ""),
                "username": vpn_config.get("username", ""),
                "password": vpn_config.get("password", ""),
                "region": vpn_config.get("region", "")
            }
            
            if current_config["vpn"]["enabled"]:
                required_vpn_fields = ["provider", "username", "password", "region"]
                missing_vpn_fields = [field for field in required_vpn_fields if not current_config["vpn"][field]]
                
                if missing_vpn_fields:
                    warning_msg = f"VPN enabled but missing fields: {', '.join(missing_vpn_fields)}"
                    _installation_status.add_log(f"WARNING: {warning_msg}")
        
        # Update Tailscale configuration if provided
        if "tailscale" in network_config:
            _installation_status.update_progress("network_setup", 60)
            _installation_status.add_log("Configuring Tailscale settings")
            
            tailscale_config = network_config.get("tailscale", {})
            current_config["tailscale"] = {
                "enabled": tailscale_config.get("enabled", False),
                "auth_key": tailscale_config.get("auth_key", "")
            }
            
            if current_config["tailscale"]["enabled"] and not current_config["tailscale"]["auth_key"]:
                _installation_status.add_log("WARNING: Tailscale enabled but no auth key provided")
        
        # Configure VPN through network manager if VPN is enabled
        if current_config["vpn"]["enabled"]:
            _installation_status.update_progress("network_setup", 80)
            _installation_status.add_log(f"Configuring VPN through network manager: {current_config['vpn']['provider']}")
            network_manager.configure_vpn(current_config["vpn"])
        
        # Configure Tailscale through network manager if Tailscale is enabled
        if current_config["tailscale"]["enabled"]:
            _installation_status.update_progress("network_setup", 90)
            _installation_status.add_log("Configuring Tailscale through network manager")
            network_manager.configure_tailscale(current_config["tailscale"])
        
        # Save updated configuration
        config.save_config_wrapper(current_config)
        
        _installation_status.update_progress("network_setup", 100)
        _installation_status.add_log("Network configuration setup completed")
        
        return {
            "status": "success",
            "message": "Network configuration setup completed",
            "config": current_config
        }
    
    except Exception as e:
        error_msg = f"Error during network configuration setup: {str(e)}"
        _installation_status.add_error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


def setup_storage_configuration(storage_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set up storage configuration based on user input.
    
    Args:
        storage_config (Dict[str, Any]): User-provided storage configuration.
    
    Returns:
        Dict[str, Any]: Dictionary with setup status.
    """
    _installation_status.update_progress("storage_setup", 10)
    _installation_status.add_log("Setting up storage configuration")
    
    try:
        # Get current configuration
        current_config = config.get_config()
        
        # Process mount points configuration
        if "mount_points" in storage_config:
            _installation_status.update_progress("storage_setup", 30)
            _installation_status.add_log("Configuring mount points")
            
            mount_points = storage_config.get("mount_points", [])
            critical_mount_failures = []
            
            for mount_point in mount_points:
                device = mount_point.get("device")
                mount_path = mount_point.get("path")
                fs_type = mount_point.get("fs_type", "auto")
                mount_options = mount_point.get("mount_options")
                add_to_fstab_flag = mount_point.get("add_to_fstab", True)
                is_critical = mount_point.get("is_critical", False)
                
                if device and mount_path:
                    _installation_status.add_log(f"Mounting {device} to {mount_path}")
                    
                    # First validate the device
                    validation_result = storage_manager.validate_device(device, fs_type)
                    if validation_result["status"] == "error":
                        error_msg = f"Device validation failed for {device}: {validation_result.get('message')}"
                        _installation_status.add_error(error_msg)
                        if is_critical:
                            critical_mount_failures.append(error_msg)
                        continue
                    elif validation_result["status"] == "warning":
                        _installation_status.add_log(f"WARNING: {validation_result.get('message')}")
                    
                    # Attempt mounting with our enhanced mount_drive function
                    mount_result = storage_manager.mount_drive(
                        device, 
                        mount_path, 
                        fs_type, 
                        mount_options, 
                        add_to_fstab_flag
                    )
                    
                    if mount_result["status"] != "success":
                        error_msg = f"Failed to mount {device}: {mount_result.get('message')}"
                        _installation_status.add_error(error_msg)
                        if is_critical:
                            critical_mount_failures.append(error_msg)
                        continue
                    
                    # Verify the mount if successful
                    verify_result = storage_manager.verify_mount(
                        mount_path,
                        uid=current_config.get("puid", 1000),
                        gid=current_config.get("pgid", 1000)
                    )
                    
                    if verify_result["status"] == "error":
                        error_msg = f"Mount verification failed for {mount_path}: {verify_result.get('message')}"
                        _installation_status.add_error(error_msg)
                        if is_critical:
                            critical_mount_failures.append(error_msg)
                            
                        # Unmount failed mount to prevent partial configuration
                        _installation_status.add_log(f"Unmounting {mount_path} due to verification failure")
                        storage_manager.unmount_drive(mount_path)
                    elif verify_result["status"] == "warning":
                        _installation_status.add_log(f"WARNING: {verify_result.get('message')}")
                else:
                    _installation_status.add_log(f"WARNING: Skipping mount point with missing device or path")
            
            # Block installation if critical mounts failed
            if critical_mount_failures:
                return {
                    "status": "error",
                    "message": "Critical storage mounts failed, cannot continue installation",
                    "details": critical_mount_failures
                }
            
            # Store critical mount paths in configuration for boot script
            current_config["critical_mounts"] = [
                mount_point["path"] for mount_point in mount_points 
                if mount_point.get("is_critical", False) and mount_point.get("path")
            ]
        
        # Process media directories configuration
        if "media_directory" in storage_config:
            _installation_status.update_progress("storage_setup", 60)
            _installation_status.add_log("Configuring media directories")
            
            media_dir = storage_config.get("media_directory")
            
            if media_dir:
                current_config["media_dir"] = media_dir
                
                # Create media subdirectories
                _installation_status.add_log(f"Creating media subdirectories in {media_dir}")
                media_dir_result = storage_manager.create_media_directories(
                    media_dir,
                    uid=current_config.get("puid", 1000),
                    gid=current_config.get("pgid", 1000)
                )
                
                if media_dir_result["status"] != "success":
                    error_msg = f"Failed to create media directories: {media_dir_result.get('message')}"
                    _installation_status.add_error(error_msg)
                    
                    # This is critical for most services, so we should fail here
                    if storage_config.get("require_media_directory", True):
                        return {
                            "status": "error",
                            "message": error_msg
                        }
        
        # Process downloads directory configuration
        if "downloads_directory" in storage_config:
            _installation_status.update_progress("storage_setup", 80)
            _installation_status.add_log("Configuring downloads directory")
            
            downloads_dir = storage_config.get("downloads_directory")
            
            if downloads_dir:
                current_config["downloads_dir"] = downloads_dir
                
                # Create downloads directory if it doesn't exist
                if not os.path.exists(downloads_dir):
                    _installation_status.add_log(f"Creating downloads directory: {downloads_dir}")
                    try:
                        os.makedirs(downloads_dir, exist_ok=True)
                        os.chown(downloads_dir, current_config.get("puid", 1000), current_config.get("pgid", 1000))
                    except Exception as e:
                        error_msg = f"Failed to create downloads directory: {str(e)}"
                        _installation_status.add_error(error_msg)
                        
                        # This is critical for download clients, so fail if required
                        if storage_config.get("require_downloads_directory", True):
                            return {
                                "status": "error",
                                "message": error_msg
                            }
        
        # Process file sharing configuration (Samba/NFS)
        if "file_sharing" in storage_config:
            _installation_status.update_progress("storage_setup", 90)
            _installation_status.add_log("Configuring file sharing")
            
            file_sharing = storage_config.get("file_sharing", {})
            share_type = file_sharing.get("type", "samba")
            shares = file_sharing.get("shares", [])
            
            if share_type == "samba" and shares:
                _installation_status.add_log("Setting up Samba shares")
                
                # Configure Samba
                for share in shares:
                    share_name = share.get("name")
                    share_path = share.get("path")
                    share_public = share.get("public", False)
                    
                    if share_name and share_path:
                        _installation_status.add_log(f"Adding Samba share: {share_name} ({share_path})")
                        share_result = storage_manager.add_share({
                            "name": share_name,
                            "path": share_path,
                            "public": share_public,
                            "read_only": share.get("read_only", False),
                            "valid_users": share.get("valid_users", "")
                        })
                        
                        if share_result["status"] != "success":
                            _installation_status.add_error(f"Failed to add Samba share {share_name}: {share_result.get('message')}")
            
            # Add support for NFS shares if requested
            elif share_type == "nfs" and shares:
                _installation_status.add_log("Setting up NFS exports")
                # Would need to implement NFS export configuration
                _installation_status.add_log("WARNING: NFS export configuration not yet implemented")
        
        # Save updated configuration
        config.save_config_wrapper(current_config)
        
        _installation_status.update_progress("storage_setup", 100)
        _installation_status.add_log("Storage configuration setup completed")
        
        return {
            "status": "success",
            "message": "Storage configuration setup completed",
            "config": current_config
        }
    
    except Exception as e:
        error_msg = f"Error during storage configuration setup: {str(e)}"
        _installation_status.add_error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


def setup_service_selection(services_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set up service selection based on user input.
    
    Args:
        services_config (Dict[str, Any]): User-provided services configuration.
    
    Returns:
        Dict[str, Any]: Dictionary with setup status.
    """
    _installation_status.update_progress("service_selection", 10)
    _installation_status.add_log("Setting up service selection")
    
    try:
        # Get default services
        default_services = config.get_default_services()
        
        # Merge user services with defaults
        merged_services = default_services.copy()
        
        # Update each service category if provided
        for category in ["arr_apps", "download_clients", "media_servers", "utilities"]:
            if category in services_config:
                _installation_status.add_log(f"Configuring {category}")
                
                user_category = services_config.get(category, {})
                
                if not isinstance(user_category, dict):
                    _installation_status.add_error(f"Invalid {category} configuration: must be a dictionary")
                    continue
                
                # Update each service in the category
                for service_name, enabled in user_category.items():
                    if service_name in merged_services[category]:
                        merged_services[category][service_name] = bool(enabled)
                        _installation_status.add_log(f"Service {service_name}: {'Enabled' if enabled else 'Disabled'}")
        
        _installation_status.update_progress("service_selection", 50)
        
        # Validate service selection
        # At least one download client should be enabled
        has_download_client = any(merged_services["download_clients"].values())
        
        # At least one media server should be enabled
        has_media_server = any(merged_services["media_servers"].values())
        
        if not has_download_client:
            _installation_status.add_log("WARNING: No download client selected")
        
        if not has_media_server:
            _installation_status.add_log("WARNING: No media server selected")
        
        # Save services configuration
        config.save_services_config(merged_services)
        
        _installation_status.update_progress("service_selection", 100)
        _installation_status.add_log("Service selection setup completed")
        
        return {
            "status": "success",
            "message": "Service selection setup completed",
            "services": merged_services
        }
    
    except Exception as e:
        error_msg = f"Error during service selection setup: {str(e)}"
        _installation_status.add_error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


def install_dependencies() -> Dict[str, Any]:
    """
    Install required dependencies for Pi-PVARR.
    
    Returns:
        Dict[str, Any]: Dictionary with installation status.
    """
    _installation_status.update_progress("dependency_install", 10)
    _installation_status.add_log("Installing dependencies")
    
    try:
        # Check if we're running as root or have sudo privileges
        has_sudo = os.geteuid() == 0 if hasattr(os, "geteuid") else False
        
        if not has_sudo:
            # Check if sudo command is available
            try:
                subprocess.run(["sudo", "-n", "true"], check=True, capture_output=True)
                has_sudo = True
            except (subprocess.SubprocessError, FileNotFoundError):
                has_sudo = False
        
        if not has_sudo:
            warning_msg = "Not running as root and no sudo privileges. Some dependency installations may fail."
            _installation_status.add_log(f"WARNING: {warning_msg}")
        
        _installation_status.update_progress("dependency_install", 30)
        
        # Function to run system commands with or without sudo
        def run_system_command(command: List[str], description: str) -> bool:
            cmd = ["sudo"] + command if has_sudo and command[0] not in ["pip", "pip3"] else command
            _installation_status.add_log(f"Running: {' '.join(cmd)}")
            
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                _installation_status.add_log(f"{description} successful")
                return True
            except subprocess.SubprocessError as e:
                _installation_status.add_error(f"{description} failed: {e}")
                if hasattr(e, "stderr") and e.stderr:
                    _installation_status.add_error(f"Error output: {e.stderr}")
                return False
        
        # Install system packages based on the detected platform
        system_packages = []
        package_manager = ""
        install_command = []
        
        # Detect Linux distribution
        if platform.system() == "Linux":
            if os.path.exists("/etc/debian_version"):
                # Debian/Ubuntu
                package_manager = "apt"
                install_command = ["apt", "install", "-y"]
                system_packages = ["python3-pip", "docker.io", "docker-compose"]
            elif os.path.exists("/etc/fedora-release"):
                # Fedora
                package_manager = "dnf"
                install_command = ["dnf", "install", "-y"]
                system_packages = ["python3-pip", "docker", "docker-compose"]
            elif os.path.exists("/etc/arch-release"):
                # Arch Linux
                package_manager = "pacman"
                install_command = ["pacman", "-S", "--noconfirm"]
                system_packages = ["python-pip", "docker", "docker-compose"]
            else:
                # Generic Linux
                _installation_status.add_log("Unable to determine Linux distribution. Skipping system package installation.")
        
        _installation_status.update_progress("dependency_install", 50)
        
        # Update package lists if using apt
        if package_manager == "apt":
            run_system_command(["apt", "update"], "Package list update")
        
        # Install system packages
        if system_packages and install_command:
            _installation_status.add_log(f"Installing system packages: {', '.join(system_packages)}")
            run_system_command(install_command + system_packages, "System package installation")
        
        _installation_status.update_progress("dependency_install", 80)
        
        # Install Python packages
        _installation_status.add_log("Installing required Python packages")
        python_packages = ["docker", "flask", "flask-cors", "PyYAML", "psutil", "requests", "pytest", "pytest-cov"]
        run_system_command(["pip3", "install", "--user"] + python_packages, "Python package installation")
        
        _installation_status.update_progress("dependency_install", 100)
        _installation_status.add_log("Dependency installation completed")
        
        return {
            "status": "success",
            "message": "Dependency installation completed"
        }
    
    except Exception as e:
        error_msg = f"Error during dependency installation: {str(e)}"
        _installation_status.add_error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


def setup_docker() -> Dict[str, Any]:
    """
    Set up Docker and Docker Compose.
    
    Returns:
        Dict[str, Any]: Dictionary with setup status.
    """
    _installation_status.update_progress("docker_setup", 10)
    _installation_status.add_log("Setting up Docker")
    
    try:
        # Check if Docker is already installed
        docker_installed = system_info.is_docker_installed()
        
        if docker_installed:
            _installation_status.add_log("Docker is already installed")
        else:
            _installation_status.add_log("Docker not installed. Installing Docker...")
            
            # Install Docker using the official script
            _installation_status.update_progress("docker_setup", 30)
            
            # Download the Docker installation script
            docker_script_path = "/tmp/get-docker.sh"
            download_cmd = [
                "curl", "-fsSL", "https://get.docker.com", "-o", docker_script_path
            ]
            
            try:
                subprocess.run(download_cmd, check=True, capture_output=True)
                _installation_status.add_log("Docker installation script downloaded")
                
                # Make the script executable and run it
                os.chmod(docker_script_path, 0o755)
                
                install_cmd = ["sh", docker_script_path]
                
                # Use sudo if available and needed
                if os.geteuid() != 0:
                    try:
                        subprocess.run(["sudo", "-n", "true"], check=True, capture_output=True)
                        install_cmd = ["sudo"] + install_cmd
                    except (subprocess.SubprocessError, FileNotFoundError):
                        _installation_status.add_error("Insufficient permissions to install Docker")
                        return {
                            "status": "error",
                            "message": "Insufficient permissions to install Docker"
                        }
                
                _installation_status.add_log("Running Docker installation script")
                subprocess.run(install_cmd, check=True, capture_output=True)
                
                # Clean up the script
                if os.path.exists(docker_script_path):
                    os.remove(docker_script_path)
                
                _installation_status.add_log("Docker installed successfully")
                docker_installed = True
            
            except Exception as e:
                _installation_status.add_error(f"Failed to install Docker: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Failed to install Docker: {str(e)}"
                }
        
        _installation_status.update_progress("docker_setup", 60)
        
        # Configure Docker for the current user
        if docker_installed:
            _installation_status.add_log("Configuring Docker for current user")
            
            try:
                # Check if the current user is already in the docker group
                user = os.environ.get("USER", "")
                
                if user:
                    # Check if the docker group exists
                    docker_group_exists = False
                    try:
                        with open("/etc/group", "r") as f:
                            docker_group_exists = any(line.startswith("docker:") for line in f)
                    except:
                        pass
                    
                    if docker_group_exists:
                        # Check if the user is already in the docker group
                        in_docker_group = False
                        try:
                            process = subprocess.run(["groups", user], check=True, capture_output=True, text=True)
                            in_docker_group = "docker" in process.stdout
                        except:
                            pass
                        
                        if not in_docker_group:
                            _installation_status.add_log(f"Adding user {user} to the docker group")
                            
                            # Add user to docker group
                            try:
                                usermod_cmd = ["usermod", "-aG", "docker", user]
                                
                                # Use sudo if available and needed
                                if os.geteuid() != 0:
                                    try:
                                        subprocess.run(["sudo", "-n", "true"], check=True, capture_output=True)
                                        usermod_cmd = ["sudo"] + usermod_cmd
                                    except (subprocess.SubprocessError, FileNotFoundError):
                                        _installation_status.add_log("WARNING: Unable to add user to docker group. You may need to run Docker commands with sudo.")
                                        return {
                                            "status": "warning",
                                            "message": "Docker installed but user not added to docker group"
                                        }
                                
                                subprocess.run(usermod_cmd, check=True, capture_output=True)
                                _installation_status.add_log(f"User {user} added to docker group")
                                _installation_status.add_log("NOTE: You may need to log out and back in for this change to take effect")
                            
                            except Exception as e:
                                _installation_status.add_log(f"WARNING: Failed to add user to docker group: {str(e)}")
                                return {
                                    "status": "warning",
                                    "message": f"Docker installed but failed to add user to docker group: {str(e)}"
                                }
            
            except Exception as e:
                _installation_status.add_log(f"WARNING: Error during Docker group configuration: {str(e)}")
        
        _installation_status.update_progress("docker_setup", 90)
        
        # Check Docker service status and ensure it's running
        try:
            # Check if Docker service is running
            systemctl_cmd = ["systemctl", "is-active", "docker"]
            
            # Use sudo if available and needed
            if os.geteuid() != 0:
                try:
                    subprocess.run(["sudo", "-n", "true"], check=True, capture_output=True)
                    systemctl_cmd = ["sudo"] + systemctl_cmd
                except (subprocess.SubprocessError, FileNotFoundError):
                    pass
            
            process = subprocess.run(systemctl_cmd, capture_output=True, text=True)
            
            if process.stdout.strip() != "active":
                _installation_status.add_log("Docker service is not active. Starting Docker service...")
                
                # Start Docker service
                start_cmd = ["systemctl", "start", "docker"]
                
                # Use sudo if available and needed
                if os.geteuid() != 0:
                    try:
                        subprocess.run(["sudo", "-n", "true"], check=True, capture_output=True)
                        start_cmd = ["sudo"] + start_cmd
                    except (subprocess.SubprocessError, FileNotFoundError):
                        _installation_status.add_log("WARNING: Unable to start Docker service. Please start it manually.")
                        return {
                            "status": "warning",
                            "message": "Docker installed but service not started"
                        }
                
                subprocess.run(start_cmd, check=True, capture_output=True)
                _installation_status.add_log("Docker service started")
        
        except Exception as e:
            _installation_status.add_log(f"WARNING: Error checking/starting Docker service: {str(e)}")
        
        _installation_status.update_progress("docker_setup", 100)
        _installation_status.add_log("Docker setup completed")
        
        return {
            "status": "success",
            "message": "Docker setup completed successfully"
        }
    
    except Exception as e:
        error_msg = f"Error during Docker setup: {str(e)}"
        _installation_status.add_error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


def generate_compose_files() -> Dict[str, Any]:
    """
    Generate Docker Compose files based on service configuration.
    
    Returns:
        Dict[str, Any]: Dictionary with generation status.
    """
    _installation_status.update_progress("compose_generation", 10)
    _installation_status.add_log("Generating Docker Compose files")
    
    try:
        # Get service manager to generate Docker Compose file
        _installation_status.update_progress("compose_generation", 40)
        compose_result = service_manager.generate_docker_compose()
        
        if compose_result["status"] != "success":
            error_msg = f"Failed to generate Docker Compose file: {compose_result.get('message')}"
            _installation_status.add_error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
        
        _installation_status.add_log("Docker Compose file generated successfully")
        
        # Get service manager to generate environment file
        _installation_status.update_progress("compose_generation", 70)
        env_result = service_manager.generate_env_file()
        
        if env_result["status"] != "success":
            error_msg = f"Failed to generate environment file: {env_result.get('message')}"
            _installation_status.add_error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
        
        _installation_status.add_log("Environment file generated successfully")
        
        # Apply service changes
        _installation_status.update_progress("compose_generation", 90)
        apply_result = service_manager.apply_service_changes()
        
        if apply_result["status"] != "success":
            error_msg = f"Failed to apply service changes: {apply_result.get('message')}"
            _installation_status.add_error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
        
        _installation_status.update_progress("compose_generation", 100)
        _installation_status.add_log("Docker Compose configuration completed")
        
        return {
            "status": "success",
            "message": "Docker Compose configuration completed",
            "docker_compose_path": apply_result.get("docker_compose_path"),
            "env_path": apply_result.get("env_path")
        }
    
    except Exception as e:
        error_msg = f"Error during Docker Compose generation: {str(e)}"
        _installation_status.add_error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


def create_containers() -> Dict[str, Any]:
    """
    Create Docker containers based on generated Docker Compose files.
    
    Returns:
        Dict[str, Any]: Dictionary with creation status.
    """
    _installation_status.update_progress("container_creation", 10)
    _installation_status.add_log("Creating Docker containers")
    
    try:
        # Start services using service manager
        _installation_status.update_progress("container_creation", 50)
        start_result = service_manager.start_services()
        
        if start_result["status"] != "success":
            error_msg = f"Failed to create containers: {start_result.get('message')}"
            _installation_status.add_error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
        
        _installation_status.update_progress("container_creation", 100)
        _installation_status.add_log("Docker containers created successfully")
        
        return {
            "status": "success",
            "message": "Docker containers created successfully",
            "output": start_result.get("output")
        }
    
    except Exception as e:
        error_msg = f"Error during container creation: {str(e)}"
        _installation_status.add_error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


def perform_post_installation() -> Dict[str, Any]:
    """
    Perform post-installation tasks.
    
    Returns:
        Dict[str, Any]: Dictionary with post-installation status.
    """
    _installation_status.update_progress("post_install", 10)
    _installation_status.add_log("Performing post-installation tasks")
    
    try:
        # Get services configuration
        _installation_status.update_progress("post_install", 30)
        # Note: services_config not used in this function yet, but keeping for future use
        config.get_services_config()
        
        # Get system configuration
        system_config = config.get_config()
        
        # Check if there are critical mount points and set up the wait-for-mounts script
        if "critical_mounts" in system_config and system_config["critical_mounts"]:
            _installation_status.add_log("Setting up mount point monitoring for critical storage")
            
            # Ensure the config directory exists
            config_dir = "/opt/pi-pvarr/config"
            os.makedirs(config_dir, exist_ok=True)
            
            # Create the critical mounts configuration file
            with open(os.path.join(config_dir, "critical-mounts.conf"), "w") as f:
                for mount in system_config["critical_mounts"]:
                    f.write(f"{mount}\n")
            
            # Copy the wait-for-mounts script to the proper location
            script_src = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                      "scripts", "wait-for-mounts.sh")
            script_dst = "/opt/pi-pvarr/bin/wait-for-mounts.sh"
            
            # Create bin directory
            os.makedirs(os.path.dirname(script_dst), exist_ok=True)
            
            # Copy script and make it executable
            import shutil
            shutil.copy2(script_src, script_dst)
            os.chmod(script_dst, 0o755)
            
            # Set up systemd service
            systemd_dir = "/etc/systemd/system"
            if os.path.exists(systemd_dir):
                service_file = os.path.join(systemd_dir, "pi-pvarr-mounts.service")
                
                service_content = """[Unit]
Description=Pi-PVARR Mount Wait Service
Before=docker.service
After=network.target

[Service]
Type=oneshot
ExecStart=/opt/pi-pvarr/bin/wait-for-mounts.sh
TimeoutSec=600
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
"""
                # Write the service file
                try:
                    with open(service_file, "w") as f:
                        f.write(service_content)
                    
                    # Enable and start the service
                    subprocess.run(["systemctl", "daemon-reload"], check=True)
                    subprocess.run(["systemctl", "enable", "pi-pvarr-mounts.service"], check=True)
                    _installation_status.add_log("Mount wait service installed and enabled")
                except Exception as e:
                    _installation_status.add_log(f"WARNING: Could not create systemd service: {str(e)}")
            else:
                _installation_status.add_log("WARNING: systemd not detected, mount wait service not installed")
                
                # Create a cron job as alternative
                crontab_cmd = f"@reboot /opt/pi-pvarr/bin/wait-for-mounts.sh >> /var/log/pi-pvarr/mount-check.log 2>&1"
                try:
                    # Get current crontab
                    process = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
                    current_crontab = process.stdout if process.returncode == 0 else ""
                    
                    # Add our command if it's not already there
                    if crontab_cmd not in current_crontab:
                        new_crontab = current_crontab + "\n" + crontab_cmd + "\n"
                        
                        # Write to a temporary file
                        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
                            temp.write(new_crontab)
                            temp_name = temp.name
                        
                        # Install new crontab
                        subprocess.run(["crontab", temp_name], check=True)
                        os.unlink(temp_name)
                        _installation_status.add_log("Mount wait script added to crontab")
                except Exception as e:
                    _installation_status.add_log(f"WARNING: Could not update crontab: {str(e)}")
        
        # Add any customizations for specific services here
        # For example, if Jellyfin is enabled and some specific configuration is needed
        
        # Update installation status in configuration
        _installation_status.update_progress("post_install", 70)
        system_config["installation_status"] = "completed"
        config.save_config_wrapper(system_config)
        
        _installation_status.update_progress("post_install", 100)
        _installation_status.add_log("Post-installation tasks completed")
        
        return {
            "status": "success",
            "message": "Post-installation tasks completed"
        }
    
    except Exception as e:
        error_msg = f"Error during post-installation: {str(e)}"
        _installation_status.add_error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


def finalize_installation() -> Dict[str, Any]:
    """
    Finalize the installation process.
    
    Returns:
        Dict[str, Any]: Dictionary with finalization status.
    """
    _installation_status.update_progress("finalization", 50)
    _installation_status.add_log("Finalizing installation")
    
    try:
        # Get container status
        containers = docker_manager.get_container_status()
        
        # Prepare summary information
        container_summary = {
            "total": len(containers),
            "running": sum(1 for _, info in containers.items() if info.get("status") == "running"),
            "stopped": sum(1 for _, info in containers.items() if info.get("status") == "stopped")
        }
        
        # Get service information (for future, currently unused)
        service_manager.get_service_info()
        
        # Create container URL list for easy access
        container_urls = {}
        for container_name, info in containers.items():
            if info.get("url"):
                container_urls[container_name] = info["url"]
        
        # Mark installation as completed
        _installation_status.status = "completed"
        _installation_status.end_time = time.time()
        
        _installation_status.update_progress("finalization", 100)
        _installation_status.add_log("Installation completed successfully")
        
        return {
            "status": "success",
            "message": "Installation completed successfully",
            "container_summary": container_summary,
            "container_urls": container_urls,
            "installation_time": _installation_status.end_time - _installation_status.start_time if _installation_status.start_time else None
        }
    
    except Exception as e:
        error_msg = f"Error during finalization: {str(e)}"
        _installation_status.add_error(error_msg)
        return {
            "status": "error",
            "message": error_msg
        }


def run_installation(installation_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run the complete installation process.
    
    Args:
        installation_config (Dict[str, Any]): Installation configuration.
    
    Returns:
        Dict[str, Any]: Dictionary with installation status.
    """
    # Reset installation status
    global _installation_status
    _installation_status = InstallationStatus()
    _installation_status.status = "in_progress"
    _installation_status.start_time = time.time()
    
    _installation_status.add_log("Starting installation process")
    
    try:
        # Step 1: System compatibility check
        _installation_status.add_log("Step 1: System compatibility check")
        compatibility_result = check_system_compatibility()
        
        if compatibility_result.get("status") == "error":
            _installation_status.status = "failed"
            return get_installation_status()
        
        if not compatibility_result.get("compatible", True):
            _installation_status.add_log("WARNING: System may not be fully compatible. Continuing anyway.")
        
        # Step 2: Basic configuration setup
        _installation_status.add_log("Step 2: Basic configuration setup")
        user_config = installation_config.get("user_config", {})
        config_result = setup_basic_configuration(user_config)
        
        if config_result.get("status") == "error":
            _installation_status.status = "failed"
            return get_installation_status()
        
        # Step 3: Network configuration setup
        _installation_status.add_log("Step 3: Network configuration setup")
        network_config = installation_config.get("network_config", {})
        network_result = setup_network_configuration(network_config)
        
        if network_result.get("status") == "error":
            _installation_status.status = "failed"
            return get_installation_status()
        
        # Step 4: Storage configuration setup
        _installation_status.add_log("Step 4: Storage configuration setup")
        storage_config = installation_config.get("storage_config", {})
        storage_result = setup_storage_configuration(storage_config)
        
        if storage_result.get("status") == "error":
            _installation_status.status = "failed"
            return get_installation_status()
        
        # Step 5: Service selection setup
        _installation_status.add_log("Step 5: Service selection setup")
        services_config = installation_config.get("services_config", {})
        services_result = setup_service_selection(services_config)
        
        if services_result.get("status") == "error":
            _installation_status.status = "failed"
            return get_installation_status()
        
        # Step 6: Install dependencies
        _installation_status.add_log("Step 6: Installing dependencies")
        dependencies_result = install_dependencies()
        
        if dependencies_result.get("status") == "error":
            _installation_status.status = "failed"
            return get_installation_status()
        
        # Step 7: Docker setup
        _installation_status.add_log("Step 7: Setting up Docker")
        docker_result = setup_docker()
        
        if docker_result.get("status") == "error":
            _installation_status.status = "failed"
            return get_installation_status()
        
        # Step 8: Generate Docker Compose files
        _installation_status.add_log("Step 8: Generating Docker Compose files")
        compose_result = generate_compose_files()
        
        if compose_result.get("status") == "error":
            _installation_status.status = "failed"
            return get_installation_status()
        
        # Step 9: Create Docker containers
        _installation_status.add_log("Step 9: Creating Docker containers")
        container_result = create_containers()
        
        if container_result.get("status") == "error":
            _installation_status.status = "failed"
            return get_installation_status()
        
        # Step 10: Post-installation configuration
        _installation_status.add_log("Step 10: Post-installation configuration")
        post_result = perform_post_installation()
        
        if post_result.get("status") == "error":
            _installation_status.status = "failed"
            return get_installation_status()
        
        # Step 11: Finalize installation
        _installation_status.add_log("Step 11: Finalizing installation")
        final_result = finalize_installation()
        
        if final_result.get("status") == "error":
            _installation_status.status = "failed"
            return get_installation_status()
        
        # Installation completed successfully
        _installation_status.status = "completed"
        _installation_status.add_log("Installation process completed successfully")
        
        return get_installation_status()
    
    except Exception as e:
        error_msg = f"Unexpected error during installation: {str(e)}"
        _installation_status.add_error(error_msg)
        _installation_status.status = "failed"
        return get_installation_status()