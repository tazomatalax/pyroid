import os
import numpy as np
import scipy.ndimage as ndi
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

    # Determine voxel resolution per dimension with slight bounding box padding
    # to ensure containment and distance transforms do not clip at the bbox boundary.
    res = params.resolution
    pad = 2.0 * max_dim / res
    grid_min = min_b - pad
    grid_max = max_b + pad
    grid_extent = grid_max - grid_min

    nx = max(12, int(np.round(res * (grid_extent[0] / max_dim))))
    ny = max(12, int(np.round(res * (grid_extent[1] / max_dim))))
    nz = max(12, int(np.round(res * (grid_extent[2] / max_dim))))

    # Create 3D grid across padded bounding box
    x, y, z = np.mgrid[
        grid_min[0]:grid_max[0]:nx * 1j,
        grid_min[1]:grid_max[1]:ny * 1j,
        grid_min[2]:grid_max[2]:nz * 1j
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

    # Mask out points outside the STL geometry
    inside_3d = inside_mask.reshape(x.shape)

    # Preserve outer shell if configured:
    # Instead of voxelizing the outer boundary, we compute the internal gyroid voids
    # (receded by shell_thickness from the boundary) and subtract them from the exact original STL mesh.
    if params.preserve_shell and params.shell_thickness > 0:
        dx = grid_extent[0] / max(nx - 1, 1)
        dy = grid_extent[1] / max(ny - 1, 1)
        dz = grid_extent[2] / max(nz - 1, 1)
        dist_inside = ndi.distance_transform_edt(inside_3d, sampling=(dx, dy, dz))

        # Void exists only where dist_inside > shell_thickness AND |gyroid_val| > t.
        field_void = np.maximum(params.shell_thickness - dist_inside, t - np.abs(gyroid_val))

        grid = pv.StructuredGrid(x, y, z)
        grid["vol"] = field_void.ravel('F')
        void_mesh = grid.contour([0])

        # If no internal void formed (e.g. wall thickness encompasses the entire volume)
        if void_mesh.n_points == 0 or void_mesh.n_cells == 0:
            return pv.wrap(stl_mesh)

        faces = void_mesh.faces.reshape((-1, 4))[:, 1:]
        tri_void = trimesh.Trimesh(vertices=void_mesh.points, faces=faces)
        tri_void.process(validate=True)
        if tri_void.volume < 0:
            tri_void.faces = tri_void.faces[:, ::-1]

        # Prepare clean STL mesh for boolean subtraction
        clean_stl = stl_mesh.copy()
        clean_stl.process(validate=True)
        if not clean_stl.is_watertight:
            clean_stl.fill_holes()
        if clean_stl.volume < 0:
            clean_stl.faces = clean_stl.faces[:, ::-1]

        # Robust boolean subtraction: outer STL minus internal gyroid void.
        # This keeps the exact original STL surface triangles, vertices, and CAD dimensions 100% intact!
        try:
            import manifold3d
            m_outer = manifold3d.Manifold(
                manifold3d.Mesh(
                    vert_properties=np.asarray(clean_stl.vertices, dtype=np.float32),
                    tri_verts=np.asarray(clean_stl.faces, dtype=np.uint32)
                )
            )
            m_void = manifold3d.Manifold(
                manifold3d.Mesh(
                    vert_properties=np.asarray(tri_void.vertices, dtype=np.float32),
                    tri_verts=np.asarray(tri_void.faces, dtype=np.uint32)
                )
            )
            diff = m_outer - m_void
            res_mesh = diff.to_mesh()
            tri_result = trimesh.Trimesh(
                vertices=res_mesh.vert_properties,
                faces=res_mesh.tri_verts,
                process=False
            )
            return pv.wrap(tri_result)
        except Exception:
            # Fallback to trimesh boolean difference
            try:
                tri_result = clean_stl.difference(tri_void, engine='manifold')
                return pv.wrap(tri_result)
            except Exception:
                pass

        # Fallback to marching cubes with shell if boolean operations fail
        shell_mask = inside_3d & (dist_inside <= params.shell_thickness)
        field = np.abs(gyroid_val) - t
        field[shell_mask] = -1.0
        field[~inside_3d] = 1.0
        grid = pv.StructuredGrid(x, y, z)
        grid["vol"] = field.ravel('F')
        return grid.contour([0])

    # No shell preservation: gyroid infill throughout the volume
    field = np.abs(gyroid_val) - t
    field[~inside_3d] = 1.0  # Set outside points high so isosurface doesn't form outside boundary

    # Construct PyVista grid and contour isosurface at 0
    grid = pv.StructuredGrid(x, y, z)
    grid["vol"] = field.ravel('F')
    mesh = grid.contour([0])

    return mesh


def prepare_for_printing(mesh: Union[pv.PolyData, trimesh.Trimesh], flat_cap: bool = False) -> trimesh.Trimesh:
    """Ensure generated mesh is manifold/watertight for 3D printing."""
    if isinstance(mesh, pv.PolyData):
        faces = mesh.faces.reshape((-1, 4))[:, 1:]
        tri = trimesh.Trimesh(vertices=mesh.points, faces=faces)
    else:
        tri = mesh.copy()

    if flat_cap and len(tri.vertices) > 0:
        z_min, z_max = tri.bounds[:, 2]
        # Trim slightly off top/bottom extreme limits if needed
        margin = (z_max - z_min) * 0.01
        if margin > 0.001:
            try:
                tri = trimesh.intersections.slice_mesh_plane(tri, plane_normal=[0, 0, -1], plane_origin=[0, 0, z_max - margin], cap=True)
                tri = trimesh.intersections.slice_mesh_plane(tri, plane_normal=[0, 0, 1], plane_origin=[0, 0, z_min + margin], cap=True)
            except Exception:
                pass

    if not tri.is_watertight:
        tri.fill_holes()

    if tri.volume < 0:
        tri.faces = tri.faces[:, ::-1]

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
