import os
import numpy as np
import pyvista as pv
import trimesh
from typing import Tuple, Optional, Union
from pyroid.models import STLConversionParams


def load_stl(filepath: str) -> Tuple[trimesh.Trimesh, pv.PolyData]:
    """Load an STL file into both Trimesh and PyVista objects."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"STL file not found: {filepath}")

    tri_mesh = trimesh.load(filepath, force='mesh')
    pv_mesh = pv.read(filepath)
    return tri_mesh, pv_mesh


def convert_stl_to_gyroid(stl_mesh: trimesh.Trimesh, params: STLConversionParams) -> pv.PolyData:
    """
    Convert an input STL 3D mesh volume into a gyroid lattice structure.
    
    Args:
        stl_mesh: Input Trimesh object (should be a manifold/closed surface)
        params: STLConversionParams configuration
        
    Returns:
        PyVista PolyData object representing the generated gyroid mesh within the STL boundary.
    """
    # Get bounding box
    min_b, max_b = stl_mesh.bounds
    extent = max_b - min_b
    max_dim = max(extent)

    if max_dim <= 0:
        raise ValueError("Invalid STL mesh with zero extent")

    # Determine voxel resolution per dimension
    res = params.resolution
    nx = max(10, int(np.round(res * (extent[0] / max_dim))))
    ny = max(10, int(np.round(res * (extent[1] / max_dim))))
    nz = max(10, int(np.round(res * (extent[2] / max_dim))))

    # Create 3D grid across bounding box
    x, y, z = np.mgrid[
        min_b[0]:max_b[0]:nx * 1j,
        min_b[1]:max_b[1]:ny * 1j,
        min_b[2]:max_b[2]:nz * 1j
    ]

    # Reshape grid points for query
    pts = np.vstack([x.ravel(), y.ravel(), z.ravel()]).T

    # Evaluate interior containment using trimesh ray containment with PyVista fallback
    try:
        inside_mask = stl_mesh.contains(pts)
    except Exception:
        pts_cloud = pv.PolyData(pts)
        pv_stl = pv.wrap(stl_mesh)
        enclosed = pts_cloud.select_enclosed_points(pv_stl, tolerance=1e-5)
        inside_mask = enclosed["SelectedPoints"].astype(bool)

    # Gyroid 3D scalar equation: sin(kx*x)*cos(ky*y) + sin(ky*y)*cos(kz*z) + sin(kz*z)*cos(kx*x)
    k = 2.0 * np.pi / max(params.cell_size, 0.001)
    gyroid_val = (
        np.sin(k * x) * np.cos(k * y) +
        np.sin(k * y) * np.cos(k * z) +
        np.sin(k * z) * np.cos(k * x)
    )

    # Thickness threshold (relative scaling)
    t = np.clip(params.wall_thickness / params.cell_size, 0.05, 1.5)
    field = np.abs(gyroid_val) - t

    # Mask out points outside the STL geometry
    inside_3d = inside_mask.reshape(x.shape)
    field[~inside_3d] = 1.0  # Set outside points high so isosurface doesn't form outside boundary

    # Construct PyVista grid and contour isosurface at 0
    grid = pv.StructuredGrid(x, y, z)
    grid["vol"] = field.ravel('F')
    mesh = grid.contour([0])

    return mesh


def prepare_for_printing(mesh: Union[pv.PolyData, trimesh.Trimesh], flat_cap: bool = True) -> trimesh.Trimesh:
    """Ensure generated mesh is manifold/watertight for 3D printing."""
    if isinstance(mesh, pv.PolyData):
        faces = mesh.faces.reshape((-1, 4))[:, 1:]
        tri = trimesh.Trimesh(vertices=mesh.points, faces=faces)
    else:
        tri = mesh.copy()

    if not tri.is_watertight:
        tri.fill_holes()

    if flat_cap and len(tri.vertices) > 0:
        z_min, z_max = tri.bounds[:, 2]
        # Trim slightly off top/bottom extreme limits if needed
        margin = (z_max - z_min) * 0.01
        if margin > 0.001:
            try:
                tri = trimesh.intersections.slice_mesh_plane(tri, plane_normal=[0, 0, -1], plane_origin=[0, 0, z_max - margin])
                tri = trimesh.intersections.slice_mesh_plane(tri, plane_normal=[0, 0, 1], plane_origin=[0, 0, z_min + margin])
            except Exception:
                pass

    return tri


def render_offscreen(mesh: pv.PolyData, output_image_path: str, window_size=(800, 600)):
    """Render a thumbnail image of the mesh headlessly."""
    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(mesh, color="lightblue", show_edges=True)
    plotter.add_bounding_box()
    plotter.show_axes()
    plotter.reset_camera()
    plotter.screenshot(output_image_path, window_size=window_size)
    plotter.close()
