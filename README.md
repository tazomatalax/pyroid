# Radially Symmetrical Gyroid Generator

## 🚧 Work in Progress 🚧

This project is currently under active development. Features and functionality may change, and there might be bugs or incomplete aspects.


## Description

The Radially Symmetrical Gyroid Generator is a Python-based application that allows users to create and visualize customizable gyroid structures. It provides a graphical user interface for adjusting various parameters to generate unique, radially symmetrical gyroid models.
<img width="731" alt="image" src="https://github.com/user-attachments/assets/741ab68a-3688-4f59-9f43-9f8c42e98ab8">

## Current Features

- Interactive GUI for parameter input
- Real-time 3D visualization of the generated gyroid
- Customizable gyroid properties (dimensions, cell sizes, wall thickness, etc.)
- Dual-color visualization
- STL/OBJ export functionality for 3D printing

## Installation

### Prerequisites

- Python 3.7+
- PyQt5
- PyVista
- NumPy
- trimesh

### Steps

1. Clone this repository:
   ```
   git clone https://github.com/tazomatalax/pyroid.git
   ```
   NOTE: If you dont have "git" installed in windows, do that first. Otherwise, skip this step and just [download the repo as a .zip](https://github.com/tazomatalax/pyroid/archive/refs/heads/main.zip).
   Save file to Downloads, and extract to Downloads, then open cmd.exe and type:
   ```
   cd Downloads\pyroid-main\pyroid-main
   ```
   Skip to step 3.
    
3. Navigate to the project directory:
   ```
   cd pyroid
   ```
4. Create Virtual Environment (optional but reccomended):
   ```
   python -m venv venv
   ```
   And activate it with (Windows):
   ```
   venv\Scripts\activate
   ```
   On Linux use:
   ```
   source venv/bin/activate
   ```
6. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
   OR
   ```
   pip install numpy pyvista trimesh PyQt5 pyvistaqt
   ```





## Usage

1. Navigate to the project directory:
   ```
   cd pyroid
   ```

2. Create a Virtual Environment (optional but recommended):
   ```
   python -m venv venv
   ```
   
   And activate it:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Navigate to the `gygui` folder:
   ```
   cd gygui
   ```

5. Run the application by executing:
   ```
   python main.py
   ```

Use the GUI to adjust parameters and generate your custom gyroid structure. Click "Generate Gyroid" to create the model and "Save STL" to export it.

Note: If you encounter any issues with PyVista, ensure that you have a compatible graphics driver installed and updated.

After export, the walls of the inner structure may need thickening. This can be accomplished using Blender:

1. Open Blender and delete the default cube.
2. File > Import > STL (.stl)
3. Apply wireframe to better visualize the mesh.
4. Apply a Solidify modifier, with 0 offset, to a thickness of your choice to the model.
5. Apply a Remesh modifier to smooth things out.
6. File > Export > STL (.stl)
   
<img width="1918" alt="image" src="https://github.com/user-attachments/assets/64ee483d-05cf-4275-b4be-437bbdcf94c6">

7. I found that I needed to "Cut" the model at the top (save bottom object), and the bottom (save top object) in order to have flat surfaces to print
8. Slice and print!

<img width="1280" alt="image" src="https://github.com/user-attachments/assets/dd770983-72bc-4c1c-b885-cee5cee44684">


## Known Issues

- Performance may degrade with very high resolution settings
- Some parameter combinations may produce unexpected results

## Planned Features

- [ ] Improved error handling and user feedback
- [ ] Additional gyroid types and variations
- [ ] Performance optimizations for handling higher resolutions
- [ ] More export options (e.g., OBJ, STEP formats)
- [ ] Undo/Redo functionality
- [ ] Importing .STL or other bodies to use as an implicit body to apply gyroid latticing

## Contributing

As this project is still in development, contributions are welcome! Please feel free to submit issues or pull requests.

## License

[MIT License](LICENSE)

## Disclaimer

This software is provided "as is", without warranty of any kind. Use at your own risk.
