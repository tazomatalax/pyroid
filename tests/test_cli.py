import os
import tempfile
import trimesh
from pyroid.cli import parse_args, main


def test_cli_parametric_generation(monkeypatch):
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        out_path = tmp.name

    try:
        test_args = ["pyroid-cli", "--output", out_path, "--res", "25", "--print-stats"]
        monkeypatch.setattr("sys.argv", test_args)

        exit_code = main()
        assert exit_code == 0
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
    finally:
        if os.path.exists(out_path):
            os.remove(out_path)


def test_cli_stl_conversion(monkeypatch):
    # Create input STL
    cube = trimesh.creation.box(extents=[8, 8, 8])
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as in_tmp:
        cube.export(in_tmp.name)
        in_path = in_tmp.name

    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as out_tmp:
        out_path = out_tmp.name

    try:
        test_args = [
            "pyroid-cli",
            "--input-stl", in_path,
            "--output", out_path,
            "--res", "25",
            "--cell-size", "2.5"
        ]
        monkeypatch.setattr("sys.argv", test_args)

        exit_code = main()
        assert exit_code == 0
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0
    finally:
        for p in [in_path, out_path]:
            if os.path.exists(p):
                os.remove(p)


def test_cli_stl_conversion_with_shell(monkeypatch):
    cube = trimesh.creation.box(extents=[10, 10, 10])
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as in_tmp:
        cube.export(in_tmp.name)
        in_path = in_tmp.name

    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as out_tmp:
        out_path = out_tmp.name

    try:
        test_args = [
            "pyroid-cli",
            "--input-stl", in_path,
            "--output", out_path,
            "--res", "25",
            "--cell-size", "2.5",
            "--preserve-shell",
            "--shell-thickness", "1.0"
        ]
        monkeypatch.setattr("sys.argv", test_args)

        exit_code = main()
        assert exit_code == 0
        assert os.path.exists(out_path)
        assert os.path.getsize(out_path) > 0

        # Verify exported STL has exact bounds and original outer vertices preserved
        out_mesh = trimesh.load(out_path, force='mesh')
        assert out_mesh.is_watertight
        import numpy as np
        np.testing.assert_allclose(out_mesh.bounds, cube.bounds, atol=1e-3)
        diffs = np.min(np.linalg.norm(out_mesh.vertices[:, None, :] - cube.vertices[None, :, :], axis=2), axis=0)
        assert (diffs < 1e-4).all()
    finally:
        for p in [in_path, out_path]:
            if os.path.exists(p):
                os.remove(p)
