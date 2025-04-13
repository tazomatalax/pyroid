import sys
import os
import json
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QFileDialog, QMessageBox, QComboBox, QGroupBox,
                           QCheckBox, QTabWidget, QStatusBar, QAction,
                           QMenuBar, QMenu, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings
from PyQt5.QtGui import QIcon, QFont
from pyvistaqt import QtInteractor
import qdarkstyle

from pyroid.core import GyroidGenerator


class GenerationWorker(QThread):
    """Worker thread for generating gyroid to keep UI responsive."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        try:
            # Update progress
            self.progress.emit(10)
            
            # Create generator and validate
            generator = GyroidGenerator(self.params)
            self.progress.emit(20)
            
            # Generate mesh
            mesh = generator.generate()
            self.progress.emit(90)
            
            # Return the generator with mesh
            self.finished.emit(generator)
            self.progress.emit(100)
        except Exception as e:
            self.error.emit(str(e))


class GyroidGeneratorGUI(QMainWindow):
    """Improved GUI for the Gyroid Generator application."""
    
    def __init__(self):
        super().__init__()
        self.generator = None
        self.config_file = os.path.join(os.path.expanduser("~"), ".pyroid_config.json")
        self.current_preset = "default"
        
        self.init_ui()
        self.load_config()
        self.apply_preset(self.current_preset)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PyRoid - Radially Symmetrical Gyroid Generator")
        self.setGeometry(100, 100, 1200, 700)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Create the control panel (left side)
        self.create_control_panel(main_layout)
        
        # Create the visualization panel (right side)
        self.create_visualization_panel(main_layout)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        # Create progress bar in status bar
        self.progressBar = QProgressBar()
        self.progressBar.setMaximumWidth(200)
        self.progressBar.setVisible(False)
        self.statusBar.addPermanentWidget(self.progressBar)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Apply dark style
        self.apply_theme()

    def create_control_panel(self, main_layout):
        """Create the left panel with controls."""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel, 1)
        
        # Presets section
        preset_box = QGroupBox("Presets")
        preset_layout = QVBoxLayout(preset_box)
        
        preset_combo_layout = QHBoxLayout()
        preset_label = QLabel("Select Preset:")
        self.preset_combo = QComboBox()
        for preset_name in GyroidGenerator.get_presets().keys():
            self.preset_combo.addItem(preset_name)
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        
        preset_combo_layout.addWidget(preset_label)
        preset_combo_layout.addWidget(self.preset_combo)
        preset_layout.addLayout(preset_combo_layout)
        
        preset_buttons_layout = QHBoxLayout()
        self.save_preset_btn = QPushButton("Save Current as Preset")
        self.save_preset_btn.clicked.connect(self.save_current_as_preset)
        preset_buttons_layout.addWidget(self.save_preset_btn)
        preset_layout.addLayout(preset_buttons_layout)
        
        left_layout.addWidget(preset_box)
        
        # Parameters section
        params_box = QGroupBox("Parameters")
        params_layout = QVBoxLayout(params_box)
        
        self.params_widgets = {}
        param_descriptions = GyroidGenerator.get_param_descriptions()
        param_labels = {
            'res': 'Resolution',
            'a': 'X-axis Length',
            'b': 'Y-axis Length',
            'c': 'Z-axis Length',
            'r1': 'Inner Radius',
            'r2': 'Outer Radius',
            'phi_scale': 'Angular Scaling Factor',
            'wall_thickness': 'Wall Thickness',
            'cell_radius': 'Cell Radius',
            'cell_height': 'Cell Height'
        }
        
        for key, label in param_labels.items():
            layout = QHBoxLayout()
            label_widget = QLabel(f"{label}:")
            line_edit = QLineEdit()
            line_edit.setToolTip(param_descriptions.get(key, "No description available"))
            
            layout.addWidget(label_widget)
            layout.addWidget(line_edit)
            
            self.params_widgets[key] = line_edit
            params_layout.addLayout(layout)
        
        left_layout.addWidget(params_box)
        
        # Actions section
        actions_box = QGroupBox("Actions")
        actions_layout = QVBoxLayout(actions_box)
        
        self.generate_btn = QPushButton("Generate Gyroid")
        self.generate_btn.clicked.connect(self.on_generate_clicked)
        self.generate_btn.setStyleSheet("font-weight: bold;")
        actions_layout.addWidget(self.generate_btn)
        
        save_layout = QHBoxLayout()
        self.save_stl_btn = QPushButton("Save as STL")
        self.save_stl_btn.clicked.connect(lambda: self.save_mesh("stl"))
        self.save_obj_btn = QPushButton("Save as OBJ")
        self.save_obj_btn.clicked.connect(lambda: self.save_mesh("obj"))
        
        save_layout.addWidget(self.save_stl_btn)
        save_layout.addWidget(self.save_obj_btn)
        actions_layout.addLayout(save_layout)
        
        left_layout.addWidget(actions_box)
        
        # Stats section
        self.stats_box = QGroupBox("Mesh Statistics")
        stats_layout = QVBoxLayout(self.stats_box)
        
        self.stats_labels = {
            "n_points": QLabel("Points: -"),
            "n_cells": QLabel("Cells: -"),
            "volume": QLabel("Volume: -"),
            "surface_area": QLabel("Surface Area: -")
        }
        
        for label in self.stats_labels.values():
            stats_layout.addWidget(label)
            
        self.stats_box.setVisible(False)
        left_layout.addWidget(self.stats_box)
        
        # Add stretch to push everything up
        left_layout.addStretch()

    def create_visualization_panel(self, main_layout):
        """Create the right panel with 3D visualization."""
        # Create PyVista plotter widget
        self.plotter = QtInteractor(self)
        main_layout.addWidget(self.plotter, 2)

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        export_menu = file_menu.addMenu("&Export")
        
        export_stl = QAction("Export as &STL", self)
        export_stl.triggered.connect(lambda: self.save_mesh("stl"))
        export_menu.addAction(export_stl)
        
        export_obj = QAction("Export as &OBJ", self)
        export_obj.triggered.connect(lambda: self.save_mesh("obj"))
        export_menu.addAction(export_obj)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        theme_menu = view_menu.addMenu("&Theme")
        
        light_theme_action = QAction("&Light", self)
        light_theme_action.triggered.connect(lambda: self.apply_theme("light"))
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("&Dark", self)
        dark_theme_action.triggered.connect(lambda: self.apply_theme("dark"))
        theme_menu.addAction(dark_theme_action)
        
        view_menu.addSeparator()
        
        reset_camera_action = QAction("Reset &Camera", self)
        reset_camera_action.triggered.connect(self.plotter.reset_camera)
        view_menu.addAction(reset_camera_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def on_preset_changed(self, preset_name):
        """Handle preset selection change."""
        self.apply_preset(preset_name)
        self.current_preset = preset_name

    def apply_preset(self, preset_name):
        """Apply the selected preset to the parameters fields."""
        presets = GyroidGenerator.get_presets()
        if preset_name in presets:
            preset = presets[preset_name]
            for key, value in preset.items():
                if key in self.params_widgets:
                    self.params_widgets[key].setText(str(value))

    def save_current_as_preset(self):
        """Save current parameters as a new preset."""
        name, ok = QFileDialog.getSaveFileName(self, "Save Preset", "", "Preset Files (*.json)")
        
        if ok and name:
            params = self.get_params_from_ui()
            
            # If no extension was provided, add .json
            if not name.endswith(".json"):
                name += ".json"
                
            try:
                with open(name, 'w') as f:
                    json.dump(params, f, indent=4)
                QMessageBox.information(self, "Success", f"Preset saved as {name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save preset: {str(e)}")

    def get_params_from_ui(self):
        """Extract parameters from UI input fields."""
        params = {}
        for key, widget in self.params_widgets.items():
            try:
                value = widget.text()
                # Convert to appropriate type
                if key == 'res':
                    params[key] = int(value)
                else:
                    params[key] = float(value)
            except ValueError:
                # Use default if conversion fails
                params[key] = GyroidGenerator.DEFAULT_PARAMS.get(key)
        return params

    def on_generate_clicked(self):
        """Handle generate button click."""
        try:
            params = self.get_params_from_ui()
            
            # Disable UI during generation
            self.generate_btn.setEnabled(False)
            self.statusBar.showMessage("Generating gyroid...")
            self.progressBar.setVisible(True)
            self.progressBar.setValue(0)
            
            # Create and start the worker thread
            self.worker = GenerationWorker(params)
            self.worker.finished.connect(self.on_generation_finished)
            self.worker.error.connect(self.on_generation_error)
            self.worker.progress.connect(self.progressBar.setValue)
            self.worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate gyroid: {str(e)}")
            self.generate_btn.setEnabled(True)
            self.progressBar.setVisible(False)
            self.statusBar.showMessage("Generation failed")

    def on_generation_finished(self, generator):
        """Handle successful gyroid generation."""
        self.generator = generator
        self.statusBar.showMessage("Gyroid generated successfully")
        self.generate_btn.setEnabled(True)
        self.progressBar.setVisible(False)
        
        # Visualize
        self.plotter.clear()
        self.plotter.add_mesh(generator.mesh, scalars=generator.mesh.points[:, -1], show_scalar_bar=False)
        self.plotter.add_bounding_box()
        self.plotter.show_axes()
        self.plotter.reset_camera()
        
        # Update stats
        self.update_stats()
        self.stats_box.setVisible(True)
        
        # Save configuration
        self.save_config()

    def on_generation_error(self, error_msg):
        """Handle error in gyroid generation."""
        QMessageBox.critical(self, "Error", f"Failed to generate gyroid: {error_msg}")
        self.generate_btn.setEnabled(True)
        self.progressBar.setVisible(False)
        self.statusBar.showMessage("Generation failed")

    def update_stats(self):
        """Update mesh statistics display."""
        if self.generator and self.generator.mesh:
            stats = self.generator.get_mesh_stats()
            
            self.stats_labels["n_points"].setText(f"Points: {stats['n_points']:,}")
            self.stats_labels["n_cells"].setText(f"Cells: {stats['n_cells']:,}")
            self.stats_labels["volume"].setText(f"Volume: {stats['volume']:.2f} cubic units")
            self.stats_labels["surface_area"].setText(f"Surface Area: {stats['surface_area']:.2f} square units")

    def save_mesh(self, file_type):
        """Save the mesh to a file."""
        if not self.generator or not self.generator.mesh:
            QMessageBox.warning(self, "Warning", "Please generate a gyroid first")
            return
            
        if file_type == "stl":
            filename, _ = QFileDialog.getSaveFileName(self, "Save as STL", "", "STL Files (*.stl)")
            if filename:
                if not filename.lower().endswith('.stl'):
                    filename += '.stl'
                self.generator.save_stl(filename)
                self.statusBar.showMessage(f"Saved as {filename}")
                
        elif file_type == "obj":
            filename, _ = QFileDialog.getSaveFileName(self, "Save as OBJ", "", "OBJ Files (*.obj)")
            if filename:
                if not filename.lower().endswith('.obj'):
                    filename += '.obj'
                self.generator.save_obj(filename)
                self.statusBar.showMessage(f"Saved as {filename}")

    def new_project(self):
        """Reset project to default state."""
        reply = QMessageBox.question(self, "New Project",
                                    "Are you sure you want to start a new project? All unsaved changes will be lost.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                    
        if reply == QMessageBox.Yes:
            self.apply_preset("default")
            self.plotter.clear()
            self.generator = None
            self.stats_box.setVisible(False)
            self.statusBar.showMessage("New project started")

    def apply_theme(self, theme_name="dark"):
        """Apply the selected theme to the application."""
        if theme_name == "dark":
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            self.setStyleSheet("")  # Reset to default

    def show_about(self):
        """Show about dialog."""
        about_text = """
        <h1>PyRoid - Gyroid Generator</h1>
        <p>A tool for generating radially symmetrical gyroid structures for 3D printing and modeling.</p>
        <p>Version 1.0.0</p>
        """
        QMessageBox.about(self, "About PyRoid", about_text)

    def save_config(self):
        """Save configuration to file."""
        try:
            config = {
                "current_preset": self.current_preset,
                "last_params": self.get_params_from_ui(),
                "window_geometry": {
                    "x": self.x(),
                    "y": self.y(),
                    "width": self.width(),
                    "height": self.height()
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {str(e)}")

    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                # Apply saved preset
                if "current_preset" in config:
                    self.current_preset = config["current_preset"]
                    index = self.preset_combo.findText(self.current_preset)
                    if index >= 0:
                        self.preset_combo.setCurrentIndex(index)
                
                # Apply saved geometry
                if "window_geometry" in config:
                    g = config["window_geometry"]
                    self.setGeometry(g.get("x", 100), g.get("y", 100), 
                                    g.get("width", 1200), g.get("height", 700))
        except Exception as e:
            print(f"Error loading config: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = GyroidGeneratorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()