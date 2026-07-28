# PyRoid - Radially Symmetrical Gyroid Generator & STL Infill Tool

A powerful, high-performance Python application and library for generating, visualizing, and exporting customizable radially symmetrical gyroid structures and converting arbitrary 3D STL volumes into gyroid lattices for 3D printing and industrial design.

![PyRoid GUI](https://github.com/user-attachments/assets/64ee483d-05cf-4275-b4be-437bbdcf94c6)

## Features

- **Interactive GUI**: Intuitive dual-mode graphical interface (Parametric Gyroid & STL Volume Infill) with real-time PyVista 3D viewport.
- **STL Volume Gyroidization**: Import any closed 3D STL model and convert its internal volume into a porous gyroid lattice structure.
- **Command Line Interface (`pyroid-cli`)**: Scriptable CLI supporting parametric generation, STL conversion, preset loading, offscreen rendering, and mesh stats.
- **Powered by `uv`**: Ultra-fast dependency resolution, environment isolation, and project execution using `uv`.
- **Type-Safe Data Models**: Powered by strongly-typed `GyroidParams` and `STLConversionParams` dataclasses.
- **Automated Mesh Repair**: Watertight validation, hole filling, and optional planar surface trimming/capping ready for direct slicing and 3D printing.
- **Export Options**: Export high-quality STL or OBJ meshes.

---

## Installation & Setup (with `uv`)

### Prerequisites

- [uv](https://github.com/astral-sh/uv) (install via `pip install uv` or `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`)

### Setup Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/tazomatalax/pyroid.git
   cd pyroid
   ```

2. **Sync Virtual Environment**:
   ```bash
   uv venv
   uv sync --all-extras
   ```

---

## Usage

### Graphical User Interface (GUI)

Launch the dual-tab GUI using `uv`:

```bash
uv run main.py
# Or using entry point:
uv run pyroid
```

- **Tab 1 (Parametric Gyroid)**: Adjust dimensions ($a, b, c$), inner/outer radii, wall thickness, cell scaling, and preset configurations.
- **Tab 2 (STL to Gyroid Volume)**: Select an external STL file, configure unit cell pitch (mm) and wall thickness, and convert its volume into a gyroid lattice structure.

### Command Line Interface (CLI)

#### 1. Generate Parametric Gyroid
```bash
uv run pyroid-cli --output my_gyroid.stl --preset thick_walls --res 100
```

#### 2. Convert 3D STL Model Volume into a Gyroid Structure
```bash
uv run pyroid-cli --input-stl model.stl --output gyroid_model.stl --cell-size 5.0 --wall-thickness 0.5
```

#### 3. Offscreen Thumbnail Rendering & Stats
```bash
uv run pyroid-cli --input-stl input.stl --output out.stl --render screenshot.png --print-stats
```

---

## Technical Architecture

```gfm
pyroid/
├── pyroid/
│   ├── core.py         # Main GyroidGenerator class & math pipeline
│   ├── models.py       # GyroidParams & STLConversionParams dataclasses
│   ├── mesh_utils.py   # STL loading, volumetric ray containment, watertight repair
│   ├── cli.py          # Command Line Interface (pyroid-cli)
│   └── gui.py          # PyQt5 dual-mode GUI & PyVistaQt interactor
├── tests/              # Automated pytest test suite
├── AGENTS.md           # Developer & AI Agent contribution guide
├── pyproject.toml      # Modern PEP 621 package metadata & uv overrides
├── uv.lock             # Deterministic uv lockfile
└── main.py             # Entry point launcher
```

---

## Running Tests

Run the test suite using `uv`:

```bash
uv run pytest -v
```

---

## License

Licensed under the MIT License - see [LICENSE](LICENSE) for details.
