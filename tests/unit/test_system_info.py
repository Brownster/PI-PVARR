"""
Unit tests for the system_info module.
"""
import os
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock

# The module will be imported here after it's created
from src.core import system_info


@pytest.mark.unit
class TestSystemInfo:
    """Tests for the system_info module."""

    def test_get_hostname(self):
        """Test getting the system hostname."""
        with patch('platform.node', return_value='test-hostname'):
            assert system_info.get_hostname() == 'test-hostname'

    def test_get_os_info(self):
        """Test getting OS information."""
        with patch('platform.system', return_value='Linux'), \
             patch('platform.release', return_value='5.10.0'), \
             patch('platform.version', return_value='#1 SMP Debian 5.10.0-18'), \
             patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='PRETTY_NAME="Debian GNU/Linux 11"\n')):
            
            os_info = system_info.get_os_info()
            
            assert os_info['name'] == 'linux'
            assert os_info['release'] == '5.10.0'
            assert os_info['pretty_name'] == 'Debian GNU/Linux 11'

    def test_get_memory_info(self):
        """Test getting memory information."""
        mock_virtual_memory = MagicMock()
        mock_virtual_memory.total = 4 * 1024 * 1024 * 1024  # 4GB
        mock_virtual_memory.available = 2 * 1024 * 1024 * 1024  # 2GB
        
        with patch('psutil.virtual_memory', return_value=mock_virtual_memory):
            memory_info = system_info.get_memory_info()
            
            assert memory_info['total'] == 4 * 1024 * 1024 * 1024
            assert memory_info['available'] == 2 * 1024 * 1024 * 1024
            assert memory_info['used'] == 2 * 1024 * 1024 * 1024
            assert memory_info['percent'] == 50.0

    def test_get_disk_info(self):
        """Test getting disk information."""
        mock_disk_usage = MagicMock()
        mock_disk_usage.total = 32 * 1024 * 1024 * 1024  # 32GB
        mock_disk_usage.free = 20 * 1024 * 1024 * 1024  # 20GB
        mock_disk_usage.used = 12 * 1024 * 1024 * 1024  # 12GB
        mock_disk_usage.percent = 37.5
        
        with patch('psutil.disk_usage', return_value=mock_disk_usage):
            disk_info = system_info.get_disk_info('/')
            
            assert disk_info['total'] == 32 * 1024 * 1024 * 1024
            assert disk_info['free'] == 20 * 1024 * 1024 * 1024
            assert disk_info['used'] == 12 * 1024 * 1024 * 1024
            assert disk_info['percent'] == 37.5

    def test_get_cpu_info(self):
        """Test getting CPU information."""
        with patch('platform.processor', return_value='ARMv8'), \
             patch('os.cpu_count', return_value=4), \
             patch('psutil.cpu_percent', return_value=15.5):
            
            cpu_info = system_info.get_cpu_info()
            
            assert cpu_info['model'] == 'ARMv8'
            assert cpu_info['cores'] == 4
            assert cpu_info['percent'] == 15.5

    def test_get_temperature(self):
        """Test getting CPU temperature."""
        # Mock for Raspberry Pi temperature
        mock_temp_content = "45200\n"  # 45.2°C in millidegrees
        
        with patch('os.path.exists', side_effect=lambda path: path == '/sys/class/thermal/thermal_zone0/temp'), \
             patch('builtins.open', mock_open(read_data=mock_temp_content)):
            
            temp = system_info.get_temperature()
            assert temp == 45.2

    def test_is_raspberry_pi(self):
        """Test detecting Raspberry Pi."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='Raspberry Pi 4 Model B Rev 1.4\n')):
            
            result = system_info.is_raspberry_pi()
            assert result['is_raspberry_pi'] is True
            assert result['model'] == 'Raspberry Pi 4 Model B Rev 1.4'

    def test_is_docker_installed(self):
        """Test detecting Docker installation."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            assert system_info.is_docker_installed() is True
            
            mock_run.side_effect = Exception("Docker not found")
            assert system_info.is_docker_installed() is False

    def test_get_system_info(self):
        """Test getting complete system information."""
        with patch('src.core.system_info.get_hostname', return_value='raspberrypi'), \
             patch('src.core.system_info.get_os_info', return_value={'name': 'linux', 'release': '5.10.0', 'pretty_name': 'Debian GNU/Linux 11'}), \
             patch('src.core.system_info.get_memory_info', return_value={'total': 4*1024*1024*1024, 'available': 2*1024*1024*1024, 'used': 2*1024*1024*1024, 'percent': 50.0}), \
             patch('src.core.system_info.get_disk_info', return_value={'total': 32*1024*1024*1024, 'free': 20*1024*1024*1024, 'used': 12*1024*1024*1024, 'percent': 37.5}), \
             patch('src.core.system_info.get_cpu_info', return_value={'model': 'ARMv8', 'cores': 4, 'percent': 15.5}), \
             patch('src.core.system_info.get_temperature', return_value=45.2), \
             patch('src.core.system_info.is_raspberry_pi', return_value={'is_raspberry_pi': True, 'model': 'Raspberry Pi 4 Model B Rev 1.4'}), \
             patch('src.core.system_info.is_docker_installed', return_value=True), \
             patch('platform.machine', return_value='aarch64'):
            
            system_info_data = system_info.get_system_info()
            
            assert system_info_data['hostname'] == 'raspberrypi'
            assert system_info_data['architecture'] == 'aarch64'
            assert system_info_data['memory_total'] == 4*1024*1024*1024
            assert system_info_data['temperature_celsius'] == 45.2
            assert system_info_data['docker_installed'] is True
            assert system_info_data['raspberry_pi']['is_raspberry_pi'] is True