#!/usr/bin/env python3
import sys
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="PyRoid - Radially Symmetrical Gyroid Generator & STL Volume Infill Tool"
    )
    parser.add_argument("--cli", action="store_true", 
                      help="Run in command line interface mode")
    return parser.parse_known_args()


def main():
    args, remaining = parse_args()
    
    if args.cli:
        from pyroid.cli import main as cli_main
        return cli_main()
    else:
        from pyroid.gui import main as gui_main
        return gui_main()


if __name__ == "__main__":
    sys.exit(main())
