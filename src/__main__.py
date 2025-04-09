"""
Main entry point for the Pi-PVARR application.
"""

import argparse
import sys
from src.api.server import run_server


def main():
    """
    Main entry point function.
    
    Parses command line arguments and runs the application.
    """
    parser = argparse.ArgumentParser(description="Pi-PVARR Media Server")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # API server command
    api_parser = subparsers.add_parser("api", help="Run the API server")
    api_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    api_parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    api_parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == "api":
        run_server(host=args.host, port=args.port, debug=args.debug)
    else:
        # If no command specified, show help
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()