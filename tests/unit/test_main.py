"""
Unit tests for the main module.
"""
import sys
import pytest
from unittest.mock import patch, MagicMock

from src import __main__


@pytest.mark.unit
class TestMain:
    """Tests for the __main__ module."""
    
    @pytest.mark.skip(reason="Skipping due to Flask app initialization issues in tests")
    def test_main_api_command(self):
        """Test main function with 'api' command."""
        test_args = ["program", "api", "--host", "127.0.0.1", "--port", "8081", "--debug"]
        
        # We need to patch argparse to prevent issues with sys.argv
        mock_args = MagicMock()
        mock_args.command = "api"
        mock_args.host = "127.0.0.1"
        mock_args.port = 8081
        mock_args.debug = True
        
        with patch('argparse.ArgumentParser.parse_args', return_value=mock_args), \
             patch('src.api.server.run_server') as mock_run_server:
            
            __main__.main()
            
            mock_run_server.assert_called_once_with(host="127.0.0.1", port=8081, debug=True)
    
    def test_main_no_command(self):
        """Test main function with no command."""
        # Mock args with no command
        mock_args = MagicMock()
        mock_args.command = None
        
        with patch('argparse.ArgumentParser.parse_args', return_value=mock_args), \
             patch('argparse.ArgumentParser.print_help') as mock_print_help, \
             patch('sys.exit') as mock_exit:
            
            __main__.main()
            
            mock_print_help.assert_called_once()
            mock_exit.assert_called_once_with(1)