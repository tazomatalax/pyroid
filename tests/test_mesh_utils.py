import os
import tempfile
import pytest
import trimesh
import pyvista as pv

from pyroid.models import STLConversionParams
from pyroid.mesh_utils import load_stl, convert_stl_to_gyroid, prepare_for_printing


def test_stl_gyroid_conversion():
    # Create a temporary primitive cube STL
    cube = trimesh.creation.box(extents=[10, 10, 10])
    
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        cube.export(tmp.name)
        tmp_path = tmp.name

    try:
        # Load STL
        tri_mesh, pv_mesh = load_stl(tmp_path)
        assert len(tri_mesh.vertices) > 0

        # Convert to Gyroid lattice volume
        params = STLConversionParams(
            stl_path=tmp_path,
            resolution=30,
            cell_size=3.0,
            wall_thickness=0.5
        )

        gyroid_mesh = convert_stl_to_gyroid(tri_mesh, params)
        assert isinstance(gyroid_mesh, pv.PolyData)
        assert gyroid_mesh.n_points > 0

        # Test watertight preparation
        tri_printable = prepare_for_printing(gyroid_mesh, flat_cap=False)
        assert isinstance(tri_printable, trimesh.Trimesh)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
