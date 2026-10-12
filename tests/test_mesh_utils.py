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


def test_stl_gyroid_conversion_with_preserved_shell():
    # Create a temporary primitive cube STL
    cube = trimesh.creation.box(extents=[12, 12, 12])
    
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        cube.export(tmp.name)
        tmp_path = tmp.name

    try:
        tri_mesh, _ = load_stl(tmp_path)
        params = STLConversionParams(
            stl_path=tmp_path,
            resolution=30,
            cell_size=3.0,
            wall_thickness=0.5,
            preserve_shell=True,
            shell_thickness=1.0
        )

        gyroid_mesh = convert_stl_to_gyroid(tri_mesh, params)
        assert isinstance(gyroid_mesh, pv.PolyData)
        assert gyroid_mesh.n_points > 0

        tri_printable = prepare_for_printing(gyroid_mesh, flat_cap=False)
        assert isinstance(tri_printable, trimesh.Trimesh)
        assert tri_printable.is_watertight

        # Verify that the original outer boundary geometry was exactly preserved
        import numpy as np
        np.testing.assert_allclose(tri_printable.bounds, cube.bounds, atol=1e-3)
        diffs = np.min(np.linalg.norm(tri_printable.vertices[:, None, :] - cube.vertices[None, :, :], axis=2), axis=0)
        assert (diffs < 1e-4).all()

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
