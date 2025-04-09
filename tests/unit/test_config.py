"""
Unit tests for the configuration module.
"""
import os
import json
import pytest
from unittest.mock import patch, mock_open

from src.core import config


@pytest.mark.unit
class TestConfig:
    """Tests for the config module."""

    def test_get_config_dir(self):
        """Test getting the config directory."""
        with patch.dict(os.environ, {'HOME': '/home/testuser'}):
            assert config.get_config_dir() == '/home/testuser/.config/pi-pvarr'

    def test_ensure_config_dir_exists(self):
        """Test ensuring config directory exists."""
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs') as mock_makedirs:
            
            config.ensure_config_dir_exists('/test/config/dir')
            mock_makedirs.assert_called_once_with('/test/config/dir', exist_ok=True)

    def test_get_default_config(self):
        """Test getting default configuration."""
        with patch.dict(os.environ, {'HOME': '/home/testuser'}):
            default_config = config.get_default_config()
            
            assert default_config['puid'] == 1000
            assert default_config['pgid'] == 1000
            assert default_config['timezone'] == 'UTC'
            assert default_config['docker_dir'] == '/home/testuser/docker'
            assert default_config['vpn']['enabled'] is True
            assert default_config['tailscale']['enabled'] is False

    def test_load_config_file_exists(self, mock_config):
        """Test loading config when file exists."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(mock_config))):
            
            loaded_config = config.load_config('/test/config/file.json')
            
            assert loaded_config == mock_config

    def test_load_config_file_not_exists(self):
        """Test loading config when file does not exist."""
        with patch('os.path.exists', return_value=False), \
             patch('src.core.config.get_default_config', return_value={'test': 'config'}):
            
            loaded_config = config.load_config('/test/config/file.json')
            
            assert loaded_config == {'test': 'config'}

    def test_save_config(self):
        """Test saving configuration to file."""
        test_config = {'test': 'config'}
        mock_file = mock_open()
        
        with patch('builtins.open', mock_file):
            config.save_config(test_config, '/test/config/file.json')
            
        mock_file.assert_called_once_with('/test/config/file.json', 'w')
        mock_file().write.assert_called_once_with(json.dumps(test_config, indent=2))

    def test_get_config_no_args(self):
        """Test get_config with no arguments."""
        with patch('src.core.config.get_config_dir', return_value='/test/config'), \
             patch('src.core.config.ensure_config_dir_exists') as mock_ensure, \
             patch('src.core.config.load_config', return_value={'test': 'config'}) as mock_load:
            
            result = config.get_config()
            
            mock_ensure.assert_called_once_with('/test/config')
            mock_load.assert_called_once_with('/test/config/config.json')
            assert result == {'test': 'config'}

    def test_get_config_with_filename(self):
        """Test get_config with specific filename."""
        with patch('src.core.config.get_config_dir', return_value='/test/config'), \
             patch('src.core.config.ensure_config_dir_exists') as mock_ensure, \
             patch('src.core.config.load_config', return_value={'test': 'services'}) as mock_load:
            
            result = config.get_config('services.json')
            
            mock_ensure.assert_called_once_with('/test/config')
            mock_load.assert_called_once_with('/test/config/services.json')
            assert result == {'test': 'services'}

    def test_save_config_wrapper(self):
        """Test save_config wrapper function."""
        test_config = {'test': 'config'}
        
        with patch('src.core.config.get_config_dir', return_value='/test/config'), \
             patch('src.core.config.ensure_config_dir_exists') as mock_ensure, \
             patch('src.core.config.save_config') as mock_save:
            
            config.save_config_wrapper(test_config)
            
            mock_ensure.assert_called_once_with('/test/config')
            mock_save.assert_called_once_with(test_config, '/test/config/config.json')

    def test_save_config_wrapper_with_filename(self):
        """Test save_config wrapper function with specific filename."""
        test_config = {'test': 'services'}
        
        with patch('src.core.config.get_config_dir', return_value='/test/config'), \
             patch('src.core.config.ensure_config_dir_exists') as mock_ensure, \
             patch('src.core.config.save_config') as mock_save:
            
            config.save_config_wrapper(test_config, 'services.json')
            
            mock_ensure.assert_called_once_with('/test/config')
            mock_save.assert_called_once_with(test_config, '/test/config/services.json')