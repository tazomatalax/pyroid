# AGENTS.md - Development & Agent Architecture Guide

## System Overview
PyRoid is a Python package, CLI tool, and Qt graphical interface for generating, visualizing, and exporting radially symmetrical gyroid structures and converting arbitrary 3D STL geometries into gyroid lattice solids.

## Package Architecture
- `pyroid/core.py`: Pure mathematical engine and mesh generation (`GyroidGenerator`).
- `pyroid/models.py`: Strongly-typed dataclasses for parameters (`GyroidParams`, `STLConversionParams`).
- `pyroid/mesh_utils.py`: Utilities for mesh processing, watertight repair, STL volumetric containment masking, and offscreen rendering.
- `pyroid/cli.py`: Command Line Interface (`pyroid-cli`).
- `pyroid/gui.py`: Desktop PyQt5 GUI with embedded 3D PyVista renderer (`pyroid`).
- `tests/`: Automated unit and integration tests powered by `pytest`.

## Technical Standards & Package Management
- Language: Python >= 3.8
- Package Manager: `uv` (fast Python environment & package manager)
- Dependencies: `numpy`, `pyvista`, `trimesh`, `PyQt5`, `pyvistaqt`, `QDarkStyle`
- Build System: PEP 621 via `pyproject.toml` with `uv.lock`
- Code Style: PEP 8, strict type hints, explicit dataclasses.

## Essential Workflows (with `uv`)
- **Initialize & Sync Environment**: `uv venv` && `uv sync --all-extras`
- **Run GUI**: `uv run main.py` or `uv run pyroid`
- **Run CLI**: `uv run main.py --cli --output model.stl` or `uv run pyroid-cli -o model.stl`
- **Run Tests**: `uv run pytest -v`
- **Convert STL**: `uv run pyroid-cli -i input.stl -o gyroid_output.stl --cell-size 5.0`
