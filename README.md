# PyRoid - Radially Symmetrical Gyroid Generator

A powerful application for generating, visualizing, and exporting customizable radially symmetrical gyroid structures for 3D printing and modeling.

## Features

- **Interactive GUI**: Intuitive graphical interface for real-time parameter adjustment and visualization
- **Command Line Interface**: Generate gyroids programmatically or in scripts
- **Parameter Presets**: Save and load parameter configurations for reproducible designs
- **Export Options**: Export models as STL or OBJ files for 3D printing or further modeling
- **Customizable Parameters**: Fine-tune every aspect of the gyroid structure
- **Mesh Statistics**: View detailed statistics about your generated mesh

## Installation

### Prerequisites

- Python 3.7+
- Required Python packages (installed automatically):
  - numpy
  - pyvista
  - trimesh
  - PyQt5
  - pyvistaqt
  - QDarkStyle

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/tazomatalax/pyroid.git
   ```
   NOTE: If you dont have "git" installed in windows, do that first. Otherwise, skip this step and just [download the repo as a .zip](https://github.com/tazomatalax/pyroid/archive/refs/heads/main.zip).
   Save file to Downloads, and extract to Downloads, then open cmd.exe and type:
   ```
   cd Downloads\pyroid
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

## Usage

### Graphical User Interface

Run the GUI with:

```
python main.py
```


### Command Line Interface

Generate a gyroid from the command line:

```
python main.py --cli --output my_gyroid.stl
```


## Parameters Explained

- **Resolution**: Higher values create more detailed structures but increase computation time
- **X/Y/Z-axis Length**: Dimensions of the gyroid structure
- **Inner Radius**: Size of the central void
- **Outer Radius**: Overall thickness of the structure
- **Angular Scaling Factor**: Affects the number of twists in the structure
- **Wall Thickness**: Thickness of the gyroid walls
- **Cell Radius/Height**: Affects the size and spacing of the gyroid's features

## Example Presets

- **Default**: Balanced parameters for general purpose use
- **Fine Detail**: Higher resolution and smaller cells for more intricate designs
- **Thick Walls**: Sturdier structure with thicker walls for easier printing
- **Dense Pattern**: More tightly packed patterns for a denser structure

## Prepping the model for Printing

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

### Project Structure

- `pyroid/core.py`: Core gyroid generation logic
- `pyroid/gui.py`: Graphical user interface
- `pyroid/cli.py`: Command line interface
- `tests/`: Test suite

## License

This project is licensed under the MIT License - see the LICENSE file for details.
