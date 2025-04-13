import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QFileDialog, QMessageBox, QColorDialog, QFormLayout,
                             QFrame, QComboBox)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from pyvistaqt import QtInteractor

class GyroidGeneratorGUI(QMainWindow):
    def __init__(self, gyroid_generator, visualization):
        super().__init__()
        self.gyroid_generator = gyroid_generator
        self.visualization = visualization
        self.setWindowTitle("Gyroid Generator")
        self.setGeometry(100, 100, 1000, 600)
        
        # Set the icon
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Warning: Icon file not found at {icon_path}")
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # Initialize shape_params and current_shape
        self.shape_params = {
            'radial': ['res', 'a', 'b', 'c', 'r1', 'r2', 'phi_scale', 'cell_radius', 'cell_height'],
            'cartesian': ['res', 'a', 'b', 'c', 'density'],
            'diamond': ['res', 'a', 'b', 'c', 'density']
        }
        self.current_shape = 'radial'

        # Setup the left panel for parameters and buttons
        self.setup_left_panel(main_layout)

        # Right panel for visualization
        self.plotter = QtInteractor(self)
        main_layout.addWidget(self.plotter, 2)

        self.gyroid_mesh = None
        self.gyroid_colors = [[1, 1, 1], [0, 0, 0]]  # Default colors: white and black

    def setup_left_panel(self, main_layout):
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel.setFrameShadow(QFrame.Raised)
        left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel, 1)
        
        # Add shape selection dropdown
        shape_layout = QHBoxLayout()
        shape_label = QLabel("Shape:")
        self.shape_combo = QComboBox()
        self.shape_combo.addItems(['radial', 'cartesian', 'diamond'])
        self.shape_combo.currentTextChanged.connect(self.on_shape_changed)
        shape_layout.addWidget(shape_label)
        shape_layout.addWidget(self.shape_combo)
        left_layout.addLayout(shape_layout)
        
        # Parameter inputs and buttons
        self.form_layout = QFormLayout()
        self.params = self.create_param_inputs(self.form_layout)
        left_layout.addLayout(self.form_layout)
        self.create_buttons(left_layout)

    def create_param_inputs(self, layout):
        default_params = {
            'res': 80, 'a': 24, 'b': 24, 'c': 10, 'r1': 12, 'r2': 0,
            'phi_scale': 8, 'cell_radius': 2, 'cell_height': 3, 'density': 1
        }
        param_descriptions = {
            'res': 'Resolution of the grid in each dimension.',
            'a': 'Dimension length along the X-axis.',
            'b': 'Dimension length along the Y-axis.',
            'c': 'Dimension length along the Z-axis.',
            'r1': 'Inner radius of the gyroid structure.',
            'r2': 'Outer radius of the gyroid structure.',
            'phi_scale': 'Scaling factor for the angular coordinate.',
            'cell_radius': 'Radius of the cells in the gyroid structure.',
            'cell_height': 'Height of the cells in the gyroid structure.',
            'density': 'Density factor for Cartesian and Diamond gyroids.'
        }
        param_labels = {
            'res': 'Resolution', 'a': 'X-axis Length', 'b': 'Y-axis Length',
            'c': 'Z-axis Length', 'r1': 'Inner Radius', 'r2': 'Outer Radius',
            'phi_scale': 'Angular Scaling Factor', 'cell_radius': 'Cell Radius',
            'cell_height': 'Cell Height', 'density': 'Density'
        }
        params = {}
        for key in self.shape_params[self.current_shape]:
            label, line_edit = self.create_param_input(key, default_params[key], param_labels[key], param_descriptions[key])
            layout.addRow(label, line_edit)
            params[key] = line_edit
        return params

    def on_shape_changed(self, shape):
        self.current_shape = shape
        self.update_param_inputs()

    def update_param_inputs(self):
        # Clear existing inputs
        for i in reversed(range(self.form_layout.rowCount())):
            self.form_layout.removeRow(i)
        
        # Create new inputs based on the selected shape
        self.params = self.create_param_inputs(self.form_layout)

    def create_param_input(self, key, default_value, label_text, description):
        label = QLabel(f"{label_text}:")
        label.setFont(QFont("Arial", 10))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        line_edit = QLineEdit(str(default_value))
        line_edit.setToolTip(description)
        line_edit.setFixedWidth(100)
        line_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #555;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        
        return label, line_edit

    def create_buttons(self, layout):
        button_layout = QHBoxLayout()
        
        generate_button = QPushButton("Generate Gyroid")
        generate_button.clicked.connect(self.generate_gyroid)
        generate_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(generate_button)

        save_button = QPushButton("Save STL/OBJ")
        save_button.clicked.connect(self.save_mesh)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #008CBA;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #007B9A;
            }
        """)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)

    def generate_gyroid(self):
        try:
            params = {k: float(v.text()) for k, v in self.params.items()}
            params['res'] = int(params['res'])
            params['shape'] = self.current_shape

            if self.current_shape in ['cartesian', 'diamond']:
                # Add default values for parameters not used by these shapes
                params['r1'] = 0
                params['r2'] = 0
                params['phi_scale'] = 1
                params['cell_radius'] = 1
                params['cell_height'] = 1
                # Ensure density is included
                if 'density' not in params:
                    params['density'] = 1

            self.gyroid_mesh = self.gyroid_generator.generate(params)

            # Visualize
            self.visualization.render(self.plotter, self.gyroid_mesh, self.gyroid_colors)

            QMessageBox.information(self, "Success", "Gyroid generated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate gyroid: {str(e)}")

    def save_mesh(self):
        if self.gyroid_mesh is None:
            QMessageBox.warning(self, "Warning", "Please generate a gyroid first.")
            return

        options = "STL Files (*.stl);;OBJ Files (*.obj)"
        filename, filetype = QFileDialog.getSaveFileName(self, "Save STL/OBJ", "", options)

        if filename:
            try:
                if filetype == "OBJ Files (*.obj)":
                    self.gyroid_generator.save_obj(self.gyroid_mesh, filename)
                else:
                    self.gyroid_generator.save_stl(self.gyroid_mesh, filename)
                QMessageBox.information(self, "Success", f"Mesh saved as {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save mesh: {str(e)}")

    def choose_color(self, color_index):
        color = QColorDialog.getColor()
        if color.isValid():
            self.gyroid_colors[color_index - 1] = [color.red() / 255, color.green() / 255, color.blue() / 255]
            if self.gyroid_mesh:
                self.visualization.render(self.plotter, self.gyroid_mesh, self.gyroid_colors)