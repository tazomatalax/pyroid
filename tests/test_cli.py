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
