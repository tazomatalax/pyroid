import numpy as np
import pyvista as pv

class GyroidVisualization:
    def render(self, plotter, gyroid_mesh, gyroid_colors):
        plotter.clear()
        
        # Add the gyroid mesh with improved appearance
        plotter.add_mesh(gyroid_mesh, 
                         scalars=gyroid_mesh.points[:, -1], 
                         show_scalar_bar=False,
                         smooth_shading=True,
                         specular=0.5,
                         cmap='viridis')
        
        # Add a semi-transparent bounding box
        bounds = gyroid_mesh.bounds
        box = pv.Box(bounds)
        plotter.add_mesh(box, style='wireframe', color='gray', opacity=0.5)
        
        # Add axes with labels
        plotter.add_axes(xlabel='X', ylabel='Y', zlabel='Z', line_width=2)
        
        # Add text displaying mesh information
        info = f"Vertices: {gyroid_mesh.n_points}\nFaces: {gyroid_mesh.n_cells}"
        plotter.add_text(info, position='upper_left', font_size=10)
        
        # Set camera position for a good initial view
        plotter.camera_position = 'iso'
        plotter.reset_camera()
        
        # Enable shadows for better depth perception
        plotter.enable_shadows()
        
        # Add a simple ground plane
        center = gyroid_mesh.center
        normal = [0, 0, 1]
        origin = [center[0], center[1], bounds[4]]  # Use the bottom of the bounding box for Z
        plotter.add_mesh(pv.Plane(center=origin, direction=normal, i_size=bounds[1]-bounds[0], j_size=bounds[3]-bounds[2]),
                         color='lightgray', opacity=0.5)

    def update_colors(self, plotter, gyroid_mesh, new_colors):
        # Method to update colors without regenerating the entire visualization
        plotter.update_scalars(new_colors, mesh=gyroid_mesh)
