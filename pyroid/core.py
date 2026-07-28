import numpy as np
import pyvista as pv
import trimesh
from typing import Dict, Any, Tuple, Optional, Union

from pyroid.models import GyroidParams, STLConversionParams
from pyroid.mesh_utils import load_stl, convert_stl_to_gyroid, prepare_for_printing, render_offscreen


class GyroidGenerator:
    """Core class for generating parametric gyroid structures and converting STL meshes."""
    
    DEFAULT_PARAMS = GyroidParams().to_dict()

    def __init__(self, params: Optional[Union[GyroidParams, Dict[str, Any]]] = None):
        """
        Initialize the gyroid generator with parameters.
        
        Args:
            params: GyroidParams instance or dictionary of parameter overrides.
        """
        if isinstance(params, GyroidParams):
            self.params = params
        elif isinstance(params, dict):
            self.params = GyroidParams.from_dict(params)
        else:
            self.params = GyroidParams()

        self.mesh: Optional[pv.PolyData] = None

    def validate_params(self) -> Tuple[bool, str]:
        """Validate parameters using the GyroidParams data model."""
        return self.params.validate()

    def generate(self) -> pv.PolyData:
        """
        Generate the radially symmetrical gyroid mesh using current parameters.
        
        Returns:
            PyVista PolyData mesh object.
            
        Raises:
            ValueError: If parameters are invalid.
        """
        is_valid, error = self.validate_params()
        if not is_valid:
            raise ValueError(error)

        p = self.params
        res = int(p.res)

        # Generate cylindrical/radial grid domain
        kx, ky, kz = [2.0 * np.pi / getattr(p, dim) for dim in ('a', 'b', 'c')]
        r_aux, phi, z = np.mgrid[
            0:p.a:res * 1j, 
            0:p.b:res * 1j, 
            0:p.c:res * 1j
        ]

        r = (p.r2 - p.r1) / p.a * r_aux + p.r1

        # Calculate radial gyroid function values
        scale_x = 2.0 * np.pi * p.cell_radius / p.a
        scale_y = 2.0 * np.pi * p.cell_radius / p.b
        scale_z = 2.0 * np.pi * p.cell_height / p.c
        
        phi_scaled = phi * p.phi_scale
        fun_values = (
            np.cos(r_aux * scale_x) * np.sin(phi_scaled * scale_y) +
            np.cos(phi_scaled * scale_y) * np.sin(z * scale_z) +
            np.cos(z * scale_z) * np.sin(r_aux * scale_x)
        )

        # Apply radial mask
        mask = (r >= (p.r1 - p.wall_thickness)) & (r <= p.r1)
        fun_values[~mask] = 1.0

        # Convert coordinates to Cartesian
        x = r * np.cos(phi * ky)
        y = r * np.sin(phi * ky)
        
        # Build PyVista StructuredGrid and extract isosurface
        grid = pv.StructuredGrid(x, y, z)
        grid["vol"] = fun_values.ravel('F')
        self.mesh = grid.contour([0])
        
        return self.mesh

    def convert_from_stl(self, stl_params: STLConversionParams) -> pv.PolyData:
        """
        Import an STL file and convert its 3D volume into a gyroid lattice.
        
        Args:
            stl_params: STLConversionParams configuration object.
            
        Returns:
            PyVista PolyData mesh of the gyroidized STL volume.
        """
        is_valid, err = stl_params.validate()
        if not is_valid:
            raise ValueError(err)

        tri_mesh, _ = load_stl(stl_params.stl_path)
        self.mesh = convert_stl_to_gyroid(tri_mesh, stl_params)
        return self.mesh

    def save_stl(self, filename: str, prepare_manifold: bool = False) -> None:
        """Save the generated mesh as an STL file."""
        if self.mesh is None:
            raise ValueError("No mesh has been generated yet")
            
        if prepare_manifold:
            tri = prepare_for_printing(self.mesh)
            tri.export(filename)
        else:
            self.mesh.save(filename)

    def save_obj(self, filename: str) -> None:
        """Save the generated mesh as an OBJ file."""
        if self.mesh is None:
            raise ValueError("No mesh has been generated yet")
            
        tri = trimesh.Trimesh(
            vertices=self.mesh.points, 
            faces=self.mesh.faces.reshape((-1, 4))[:, 1:]
        )
        tri.export(filename)

    def save_screenshot(self, filename: str) -> None:
        """Save a rendered PNG thumbnail of the mesh."""
        if self.mesh is None:
            raise ValueError("No mesh has been generated yet")
        render_offscreen(self.mesh, filename)

    def get_mesh_stats(self) -> Dict[str, Any]:
        """Return quantitative mesh metrics."""
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
        """Return parameter descriptions."""
        return {
            'res': 'Resolution of the grid in each dimension.',
            'a': 'Dimension length along X-axis.',
            'b': 'Dimension length along Y-axis.',
            'c': 'Dimension length along Z-axis.',
            'r1': 'Inner radius of gyroid structure (central void).',
            'r2': 'Outer radius of gyroid structure.',
            'phi_scale': 'Angular scaling factor (twists).',
            'wall_thickness': 'Wall thickness of gyroid.',
            'cell_radius': 'Cell pore radius.',
            'cell_height': 'Cell vertical height.'
        }

    @classmethod
    def get_presets(cls) -> Dict[str, Dict[str, Any]]:
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