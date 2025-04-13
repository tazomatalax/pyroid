#!/usr/bin/env python3
"""
PyRoid - Radially Symmetrical Gyroid Generator

Main entry point for the PyRoid application.
"""
import sys
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="PyRoid - Radially Symmetrical Gyroid Generator"
    )
    parser.add_argument("--cli", action="store_true", 
                      help="Run in command line interface mode")
    return parser.parse_args()

def main():
    args = parse_args()
    
    if args.cli:
        # Import and run the CLI interface
        from pyroid.cli import main as cli_main
        return cli_main()
    else:
        # Import and run the GUI interface
        from pyroid.gui import main as gui_main
        return gui_main()

if __name__ == "__main__":
    sys.exit(main())