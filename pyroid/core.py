import numpy as np
import pyvista as pv
import trimesh
from typing import Dict, Any, Tuple, Optional


class GyroidGenerator:
    """Core class for generating gyroid structures with various parameters."""
    
    DEFAULT_PARAMS = {
        'res': 80,
        'a': 24,
        'b': 24,
        'c': 10,
        'r1': 12,
        'r2': 0,
        'phi_scale': 8,
        'wall_thickness': 11.5,
        'cell_radius': 2,
        'cell_height': 3
    }
    
    def __init__(self, params: Optional[Dict[str, float]] = None):
        """
        Initialize the gyroid generator with parameters.
        
        Args:
            params: Dictionary of parameters to override defaults
        """
        self.params = self.DEFAULT_PARAMS.copy()
        if params:
            self.params.update(params)
        self.mesh = None
        
    def validate_params(self) -> Tuple[bool, str]:
        """
        Validate parameters to ensure they have appropriate values.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Ensure res is a positive integer
            if not isinstance(self.params['res'], int) or self.params['res'] <= 0:
                return False, "Resolution must be a positive integer"
                
            # Ensure dimensions are positive
            for dim in ['a', 'b', 'c']:
                if self.params[dim] <= 0:
                    return False, f"Dimension {dim} must be positive"
                    
            # Ensure radiuses make sense
            if self.params['r1'] < 0:
                return False, "Inner radius must be non-negative"
            
            if self.params['wall_thickness'] <= 0:
                return False, "Wall thickness must be positive"
                
            # All checks passed
            return True, ""
            
        except KeyError as e:
            return False, f"Missing parameter: {str(e)}"
        except Exception as e:
            return False, f"Parameter validation failed: {str(e)}"
    
    def generate(self) -> pv.PolyData:
        """
        Generate the gyroid mesh using the configured parameters.
        
        Returns:
            The generated mesh as a PyVista PolyData object
        
        Raises:
            ValueError: If parameters are invalid
        """
        # Validate parameters
        is_valid, error = self.validate_params()
        if not is_valid:
            raise ValueError(error)
        
        # Extract parameters for easier reference
        params = self.params
        
        # Generate gyroid
        kx, ky, kz = [2 * np.pi / params[p] for p in ('a', 'b', 'c')]
        r_aux, phi, z = np.mgrid[0:params['a']:int(params['res']) * 1j, 
                                 0:params['b']:int(params['res']) * 1j, 
                                 0:params['c']:int(params['res']) * 1j]

        r = (params['r2'] - params['r1']) / params['a'] * r_aux + params['r1']

        # Calculate gyroid function values
        scale_x = 2 * np.pi * params['cell_radius'] / params['a']
        scale_y = 2 * np.pi * params['cell_radius'] / params['b']
        scale_z = 2 * np.pi * params['cell_height'] / params['c']
        
        fun_values = (np.cos(r_aux * scale_x) * np.sin(phi * params['phi_scale'] * scale_y) + 
                     np.cos(phi * params['phi_scale'] * scale_y) * np.sin(z * scale_z) + 
                     np.cos(z * scale_z) * np.sin(r_aux * scale_x))

        # Apply mask
        mask = (r >= (params['r1'] - params['wall_thickness'])) & (r <= params['r1'])
        fun_values[~mask] = 1

        # Convert to cartesian coordinates
        x = r * np.cos(phi * ky)
        y = r * np.sin(phi * ky)
        
        # Create grid and extract isosurface
        grid = pv.StructuredGrid(x, y, z)
        grid["vol"] = fun_values.ravel('F')
        self.mesh = grid.contour([0])
        
        return self.mesh
    
    def save_stl(self, filename: str) -> None:
        """Save the generated mesh as an STL file."""
        if self.mesh is None:
            raise ValueError("No mesh has been generated yet")
        self.mesh.save(filename)
    
    def save_obj(self, filename: str) -> None:
        """Save the generated mesh as an OBJ file."""
        if self.mesh is None:
            raise ValueError("No mesh has been generated yet")
        # Convert PyVista mesh to Trimesh format
        mesh = trimesh.Trimesh(vertices=self.mesh.points, 
                              faces=self.mesh.faces.reshape((-1, 4))[:, 1:])
        mesh.export(filename)
    
    def get_mesh_stats(self) -> Dict[str, Any]:
        """Return statistics about the generated mesh."""
        if self.mesh is None:
            raise ValueError("No mesh has been generated yet")
        
        return {
            "n_points": self.mesh.n_points,
            "n_cells": self.mesh.n_cells,
            "volume": self.mesh.volume,
            "surface_area": self.mesh.area,
            "has_normals": self.mesh.face_normals is not None,
        }
    
    @classmethod
    def get_param_descriptions(cls) -> Dict[str, str]:
        """Return descriptions of each parameter."""
        return {
            'res': 'Resolution of the grid in each dimension. Higher values create more detailed structures but increase computation time.',
            'a': 'Dimension length along the X-axis. Affects the overall width of the gyroid.',
            'b': 'Dimension length along the Y-axis. Affects the overall depth of the gyroid.',
            'c': 'Dimension length along the Z-axis. Affects the overall height of the gyroid.',
            'r1': 'Inner radius of the gyroid structure. Determines the size of the central void.',
            'r2': 'Outer radius of the gyroid structure. Determines the overall thickness of the structure.',
            'phi_scale': 'Scaling factor for the angular coordinate. Affects the number of twists in the structure.',
            'wall_thickness': 'Thickness of the gyroid walls. Higher values create thicker, more robust structures.',
            'cell_radius': 'Radius of the cells in the gyroid structure. Affects the size of individual "pores" in the structure.',
            'cell_height': 'Height of the cells in the gyroid structure. Affects the vertical spacing of features.'
        }
    
    @classmethod
    def get_presets(cls) -> Dict[str, Dict[str, float]]:
        """Return predefined parameter presets."""
        return {
            "default": cls.DEFAULT_PARAMS,
            "fine_detail": {
                'res': 120, 'a': 24, 'b': 24, 'c': 10, 'r1': 12, 'r2': 0,
                'phi_scale': 8, 'wall_thickness': 11.5, 'cell_radius': 1.5, 'cell_height': 2.5
            },
            "thick_walls": {
                'res': 80, 'a': 24, 'b': 24, 'c': 10, 'r1': 12, 'r2': 0,
                'phi_scale': 8, 'wall_thickness': 15.0, 'cell_radius': 2, 'cell_height': 3
            },
            "dense_pattern": {
                'res': 100, 'a': 24, 'b': 24, 'c': 10, 'r1': 12, 'r2': 0,
                'phi_scale': 12, 'wall_thickness': 11.5, 'cell_radius': 1.2, 'cell_height': 1.8
            }
        }