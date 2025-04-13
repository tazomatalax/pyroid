#!/usr/bin/env python3
import argparse
import sys
import os
import json
from typing import Dict, Any

from pyroid.core import GyroidGenerator


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PyRoid - Command line tool for generating gyroid structures",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Main arguments
    parser.add_argument("--output", "-o", type=str, required=True,
                        help="Output file path (with .stl or .obj extension)")
    
    # Parameter groups
    param_group = parser.add_argument_group("Gyroid Parameters")
    param_group.add_argument("--res", type=int, default=80,
                           help="Resolution of the grid in each dimension")
    param_group.add_argument("--a", type=float, default=24,
                           help="X-axis length")
    param_group.add_argument("--b", type=float, default=24,
                           help="Y-axis length")
    param_group.add_argument("--c", type=float, default=10,
                           help="Z-axis length")
    param_group.add_argument("--r1", type=float, default=12,
                           help="Inner radius")
    param_group.add_argument("--r2", type=float, default=0,
                           help="Outer radius")
    param_group.add_argument("--phi-scale", type=float, default=8,
                           help="Angular scaling factor")
    param_group.add_argument("--wall-thickness", type=float, default=11.5,
                           help="Wall thickness")
    param_group.add_argument("--cell-radius", type=float, default=2,
                           help="Cell radius")
    param_group.add_argument("--cell-height", type=float, default=3,
                           help="Cell height")
    
    # Preset handling
    preset_group = parser.add_argument_group("Preset Management")
    preset_group.add_argument("--preset", type=str,
                            help="Use a named preset (default, fine_detail, thick_walls, dense_pattern)")
    preset_group.add_argument("--load-preset", type=str, 
                            help="Load parameters from a preset JSON file")
    preset_group.add_argument("--save-preset", type=str,
                            help="Save current parameters to a preset JSON file")
    
    # Stats options
    parser.add_argument("--print-stats", action="store_true",
                      help="Print statistics about the generated mesh")
    
    return parser.parse_args()


def collect_params_from_args(args) -> Dict[str, Any]:
    """Convert command line args to parameter dictionary."""
    return {
        'res': args.res,
        'a': args.a,
        'b': args.b,
        'c': args.c,
        'r1': args.r1,
        'r2': args.r2,
        'phi_scale': args.phi_scale,
        'wall_thickness': args.wall_thickness,
        'cell_radius': args.cell_radius,
        'cell_height': args.cell_height
    }


def main():
    """Main function for the CLI application."""
    args = parse_args()
    
    # Parameter handling
    params = {}
    
    # Load from preset if specified
    if args.preset:
        presets = GyroidGenerator.get_presets()
        if args.preset in presets:
            params = presets[args.preset]
        else:
            print(f"Error: Preset '{args.preset}' not found. Available presets: {', '.join(presets.keys())}")
            return 1
    
    # Load from preset file if specified
    if args.load_preset:
        try:
            with open(args.load_preset, 'r') as f:
                file_params = json.load(f)
                params.update(file_params)
        except Exception as e:
            print(f"Error loading preset file: {e}")
            return 1
    
    # Override with any parameters specified in command line
    cmd_params = collect_params_from_args(args)
    # Only update params that were explicitly set (not using default values)
    for k, v in vars(args).items():
        if k in cmd_params and k in ['res', 'a', 'b', 'c', 'r1', 'r2', 'phi_scale', 'wall_thickness', 'cell_radius', 'cell_height']:
            params[k] = v
    
    # Save preset if specified
    if args.save_preset:
        try:
            with open(args.save_preset, 'w') as f:
                json.dump(params, f, indent=4)
            print(f"Preset saved to {args.save_preset}")
        except Exception as e:
            print(f"Error saving preset file: {e}")
            return 1
    
    # Generate the gyroid
    try:
        print("Generating gyroid structure...")
        generator = GyroidGenerator(params)
        generator.generate()
        
        # Save the output file
        extension = os.path.splitext(args.output)[1].lower()
        if extension == '.obj':
            generator.save_obj(args.output)
        else:
            generator.save_stl(args.output)
        print(f"Gyroid saved to {args.output}")
        
        # Print stats if requested
        if args.print_stats:
            stats = generator.get_mesh_stats()
            print("\nMesh Statistics:")
            print(f"Points: {stats['n_points']:,}")
            print(f"Cells: {stats['n_cells']:,}")
            print(f"Volume: {stats['volume']:.2f} cubic units")
            print(f"Surface Area: {stats['surface_area']:.2f} square units")
        
        return 0
    
    except Exception as e:
        print(f"Error generating gyroid: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())