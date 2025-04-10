"""
PyTest configuration file for Pi-PVARR tests.

This module contains shared fixtures and configuration for all tests.
"""

import pytest
import os
import sys

# Add the root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))


# Add shared fixtures here
@pytest.fixture
def temp_dir(tmpdir):
    """Create a temporary directory for test files."""
    return tmpdir


@pytest.fixture
def mock_config():
    """Return a mock configuration for testing."""
    return {
        "puid": 1000,
        "pgid": 1000,
        "timezone": "Europe/London",
        "docker_dir": "/home/pi/docker",
        "media_dir": "/mnt/media",
        "downloads_dir": "/mnt/downloads",
        "vpn": {
            "enabled": True,
            "provider": "private internet access",
            "username": "test_user",
            "password": "test_password",
            "region": "Netherlands"
        },
        "tailscale": {
            "enabled": False
        }
    }
