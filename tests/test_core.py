import pytest
import pyvista as pv
from pyroid.core import GyroidGenerator
from pyroid.models import GyroidParams


def test_gyroid_params_validation():
    params = GyroidParams(res=50, a=20.0, b=20.0, c=10.0)
    valid, err = params.validate()
    assert valid
    assert err == ""

    invalid_params = GyroidParams(res=-5)
    valid, err = invalid_params.validate()
    assert not valid
    assert "Resolution" in err


def test_default_gyroid_generation():
    # Fast resolution for testing
    params = GyroidParams(res=30)
    generator = GyroidGenerator(params)
    mesh = generator.generate()

    assert isinstance(mesh, pv.PolyData)
    assert mesh.n_points > 0
    assert mesh.n_cells > 0


def test_mesh_statistics():
    params = GyroidParams(res=25)
    generator = GyroidGenerator(params)
    generator.generate()
    stats = generator.get_mesh_stats()

    assert "n_points" in stats
    assert "n_cells" in stats
    assert "volume" in stats
    assert "surface_area" in stats
    assert stats["n_points"] > 0
