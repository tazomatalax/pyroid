import sys
import os
import json
from typing import Optional
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QFileDialog, QMessageBox, QComboBox, QGroupBox,
                           QCheckBox, QTabWidget, QStatusBar, QAction,
                           QProgressBar)
from PyQt5.QtCore import QThread, pyqtSignal, QEvent
from pyvistaqt import QtInteractor
import qdarkstyle

from pyroid.core import GyroidGenerator
from pyroid.models import GyroidParams, STLConversionParams


class ParametricWorker(QThread):
    """Worker thread for parametric gyroid generation."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, params: GyroidParams):
        super().__init__()
        self.params = params

    def run(self):
        try:
            self.progress.emit(20)
            generator = GyroidGenerator(self.params)
            self.progress.emit(50)
            generator.generate()
            self.progress.emit(90)
            self.finished.emit(generator)
            self.progress.emit(100)
        except Exception as e:
            self.error.emit(str(e))


class STLConversionWorker(QThread):
    """Worker thread for converting an STL volume to a gyroid lattice."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)

    def __init__(self, stl_params: STLConversionParams):
        super().__init__()
        self.stl_params = stl_params

    def run(self):
        try:
            self.progress.emit(20)
            generator = GyroidGenerator()
            self.progress.emit(40)
            generator.convert_from_stl(self.stl_params)
            self.progress.emit(90)
            self.finished.emit(generator)
            self.progress.emit(100)
        except Exception as e:
            self.error.emit(str(e))


class GyroidGeneratorGUI(QMainWindow):
    """Modern GUI for PyRoid with Parametric and STL Conversion tabs."""
    
    def __init__(self):
        super().__init__()
        self.generator: Optional[GyroidGenerator] = None
        self.config_file = os.path.join(os.path.expanduser("~"), ".pyroid_config.json")
        self.current_preset = "default"
        
        self.init_ui()
        self.load_config()
        self.apply_preset(self.current_preset)

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("PyRoid - Radially Symmetrical Gyroid Generator & STL Volume Infill")
        self.setGeometry(100, 100, 1280, 750)
        self.setAcceptDrops(True)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Left Panel (Tabbed Controls & Actions)
        self.create_control_panel(main_layout)
        
        # Right Panel (3D PyVista Visualization)
        self.create_visualization_panel(main_layout)
        
        # Status Bar & Progress Bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
        self.progressBar = QProgressBar()
        self.progressBar.setMaximumWidth(200)
        self.progressBar.setVisible(False)
        self.statusBar.addPermanentWidget(self.progressBar)
        
        self.create_menu_bar()
        self.apply_theme("dark")

    def create_control_panel(self, main_layout):
        """Create left side control panel with QTabWidget."""
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        main_layout.addWidget(left_panel, 1)
        
        # Tab Widget
        self.tabs = QTabWidget()
        left_layout.addWidget(self.tabs)
        
        # TAB 1: Parametric Gyroid Generator
        tab_parametric = QWidget()
        param_tab_layout = QVBoxLayout(tab_parametric)
        
        # Presets Section
        preset_box = QGroupBox("Presets")
        preset_layout = QVBoxLayout(preset_box)
        preset_combo_layout = QHBoxLayout()
        preset_combo_layout.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        for p in GyroidGenerator.get_presets().keys():
            self.preset_combo.addItem(p)
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        preset_combo_layout.addWidget(self.preset_combo)
        preset_layout.addLayout(preset_combo_layout)
        
        self.save_preset_btn = QPushButton("Save Preset...")
        self.save_preset_btn.clicked.connect(self.save_current_as_preset)
        preset_layout.addWidget(self.save_preset_btn)
        param_tab_layout.addWidget(preset_box)
        
        # Parameters Section
        params_box = QGroupBox("Parameters")
        params_layout = QVBoxLayout(params_box)
        self.params_widgets = {}
        param_descriptions = GyroidGenerator.get_param_descriptions()
        param_labels = {
            'res': 'Resolution', 'a': 'X-axis Length', 'b': 'Y-axis Length', 'c': 'Z-axis Length',
            'r1': 'Inner Radius', 'r2': 'Outer Radius', 'phi_scale': 'Angular Scaling',
            'wall_thickness': 'Wall Thickness', 'cell_radius': 'Cell Radius', 'cell_height': 'Cell Height'
        }
        for k, label in param_labels.items():
            row = QHBoxLayout()
            row.addWidget(QLabel(f"{label}:"))
            line_edit = QLineEdit()
            line_edit.setToolTip(param_descriptions.get(k, ""))
            row.addWidget(line_edit)
            self.params_widgets[k] = line_edit
            params_layout.addLayout(row)
        param_tab_layout.addWidget(params_box)
        
        self.generate_btn = QPushButton("Generate Gyroid")
        self.generate_btn.setStyleSheet("font-weight: bold; padding: 6px;")
        self.generate_btn.clicked.connect(self.on_generate_clicked)
        param_tab_layout.addWidget(self.generate_btn)
        
        self.tabs.addTab(tab_parametric, "Parametric Gyroid")
        
        # TAB 2: STL Volume Conversion
        tab_stl = QWidget()
        stl_tab_layout = QVBoxLayout(tab_stl)
        
        stl_file_box = QGroupBox("Input Mesh (STL)")
        stl_file_layout = QVBoxLayout(stl_file_box)
        self.stl_path_edit = QLineEdit()
        self.stl_path_edit.setPlaceholderText("Select STL file...")
        stl_browse_btn = QPushButton("Browse...")
        stl_browse_btn.clicked.connect(self.on_browse_stl)
        
        file_row = QHBoxLayout()
        file_row.addWidget(self.stl_path_edit)
        file_row.addWidget(stl_browse_btn)
        stl_file_layout.addLayout(file_row)
        stl_tab_layout.addWidget(stl_file_box)
        
        stl_params_box = QGroupBox("Conversion Settings")
        stl_params_layout = QVBoxLayout(stl_params_box)
        
        # Resolution
        res_row = QHBoxLayout()
        res_row.addWidget(QLabel("Voxel Resolution:"))
        self.stl_res_edit = QLineEdit("80")
        res_row.addWidget(self.stl_res_edit)
        stl_params_layout.addLayout(res_row)
        
        # Cell Size
        cell_row = QHBoxLayout()
        cell_row.addWidget(QLabel("Cell Size (mm):"))
        self.stl_cell_edit = QLineEdit("5.0")
        cell_row.addWidget(self.stl_cell_edit)
        stl_params_layout.addLayout(cell_row)

        # Wall Thickness
        wall_row = QHBoxLayout()
        wall_row.addWidget(QLabel("Wall Thickness:"))
        self.stl_wall_edit = QLineEdit("0.5")
        wall_row.addWidget(self.stl_wall_edit)
        stl_params_layout.addLayout(wall_row)

        # Flat Capping
        self.stl_cap_check = QCheckBox("Planar slice & cap surfaces for 3D printing")
        self.stl_cap_check.setChecked(False)
        stl_params_layout.addWidget(self.stl_cap_check)

        # Preserve Shell
        self.stl_shell_check = QCheckBox("Preserve original STL outer shell")
        self.stl_shell_check.setChecked(False)
        self.stl_shell_check.toggled.connect(self.on_shell_check_toggled)
        stl_params_layout.addWidget(self.stl_shell_check)

        shell_thick_row = QHBoxLayout()
        self.stl_shell_label = QLabel("Shell Thickness (mm):")
        self.stl_shell_edit = QLineEdit("1.0")
        self.stl_shell_label.setEnabled(False)
        self.stl_shell_edit.setEnabled(False)
        shell_thick_row.addWidget(self.stl_shell_label)
        shell_thick_row.addWidget(self.stl_shell_edit)
        stl_params_layout.addLayout(shell_thick_row)

        stl_tab_layout.addWidget(stl_params_box)
        
        self.convert_stl_btn = QPushButton("Convert STL Volume to Gyroid")
        self.convert_stl_btn.setStyleSheet("font-weight: bold; padding: 6px;")
        self.convert_stl_btn.clicked.connect(self.on_convert_stl_clicked)
        stl_tab_layout.addWidget(self.convert_stl_btn)
        stl_tab_layout.addStretch()

        self.tabs.addTab(tab_stl, "STL to Gyroid Volume")
        
        # Shared Export Actions Section
        actions_box = QGroupBox("Export Options")
        actions_layout = QHBoxLayout(actions_box)
        
        self.save_stl_btn = QPushButton("Export STL")
        self.save_stl_btn.clicked.connect(lambda: self.save_mesh("stl"))
        self.save_obj_btn = QPushButton("Export OBJ")
        self.save_obj_btn.clicked.connect(lambda: self.save_mesh("obj"))
        
        actions_layout.addWidget(self.save_stl_btn)
        actions_layout.addWidget(self.save_obj_btn)
        left_layout.addWidget(actions_box)

        # View Options Section
        view_box = QGroupBox("View Options")
        view_layout = QVBoxLayout(view_box)
        self.cutaway_check = QCheckBox("Show Cross-Section (Cutaway)")
        self.cutaway_check.setToolTip("Slice mesh along X-axis to inspect internal gyroid infill")
        self.cutaway_check.toggled.connect(self.on_view_mode_changed)
        view_layout.addWidget(self.cutaway_check)
        left_layout.addWidget(view_box)
        
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

    def create_visualization_panel(self, main_layout):
        """Create 3D visualization panel with PyVistaQt."""
        self.plotter = QtInteractor(self)
        self.plotter.installEventFilter(self)
        main_layout.addWidget(self.plotter, 2)

    def create_menu_bar(self):
        """Create top menu bar."""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Project", self)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        open_stl_action = QAction("Open &STL...", self)
        open_stl_action.triggered.connect(self.on_browse_stl)
        file_menu.addAction(open_stl_action)
        
        export_stl = QAction("Export as &STL", self)
        export_stl.triggered.connect(lambda: self.save_mesh("stl"))
        file_menu.addAction(export_stl)
        
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        view_menu = menubar.addMenu("&View")
        reset_camera_action = QAction("Reset &Camera", self)
        reset_camera_action.triggered.connect(self.plotter.reset_camera)
        view_menu.addAction(reset_camera_action)

    def on_preset_changed(self, preset_name):
        self.apply_preset(preset_name)
        self.current_preset = preset_name

    def apply_preset(self, preset_name):
        presets = GyroidGenerator.get_presets()
        if preset_name in presets:
            for k, v in presets[preset_name].items():
                if k in self.params_widgets:
                    self.params_widgets[k].setText(str(v))

    def save_current_as_preset(self):
        name, ok = QFileDialog.getSaveFileName(self, "Save Preset", "", "Preset Files (*.json)")
        if ok and name:
            if not name.endswith(".json"):
                name += ".json"
            try:
                params = self.get_params_from_ui()
                with open(name, 'w') as f:
                    json.dump(params.to_dict(), f, indent=4)
                QMessageBox.information(self, "Success", f"Preset saved as {name}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save preset: {str(e)}")

    def get_params_from_ui(self) -> GyroidParams:
        raw_dict = {}
        for k, widget in self.params_widgets.items():
            val = widget.text()
            raw_dict[k] = int(val) if k == 'res' else float(val or 0.0)
        return GyroidParams.from_dict(raw_dict)

    def eventFilter(self, watched, event):
        """Intercept drag and drop events on child widgets (e.g. 3D plotter viewport)."""
        if watched == getattr(self, "plotter", None):
            if event.type() == QEvent.DragEnter:
                self.dragEnterEvent(event)
                return True
            elif event.type() == QEvent.DragMove:
                self.dragMoveEvent(event)
                return True
            elif event.type() == QEvent.Drop:
                self.dropEvent(event)
                return True
        return super().eventFilter(watched, event)

    def dragEnterEvent(self, event):
        """Accept drag event if it contains supported file types (.stl or .json)."""
        if self.progressBar.isVisible():
            event.ignore()
            return

        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path and path.lower().endswith(('.stl', '.json')):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dragMoveEvent(self, event):
        """Accept drag movement over valid drop areas."""
        if self.progressBar.isVisible():
            event.ignore()
            return

        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path and path.lower().endswith(('.stl', '.json')):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        """Handle dropped files (.stl or .json)."""
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        handled = False
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if not file_path or not os.path.isfile(file_path):
                continue

            lower_path = file_path.lower()
            if lower_path.endswith('.stl'):
                self.load_stl_file(file_path)
                handled = True
                break
            elif lower_path.endswith('.json'):
                self.load_preset_file(file_path)
                handled = True
                break

        if handled:
            event.acceptProposedAction()
        else:
            event.ignore()

    def load_stl_file(self, file_path: str):
        """Load an STL file, switch to STL conversion tab, and preview in 3D."""
        if not file_path or not os.path.isfile(file_path):
            QMessageBox.warning(self, "File Not Found", f"STL file does not exist:\n{file_path}")
            return

        self.stl_path_edit.setText(file_path)
        self.tabs.setCurrentIndex(1)
        self.statusBar.showMessage(f"Loaded STL: {os.path.basename(file_path)}")

        try:
            import pyvista as pv
            mesh = pv.read(file_path)
            if mesh is not None and getattr(mesh, "n_points", 0) > 0:
                self.plotter.clear()
                self.plotter.add_mesh(mesh, color="#5dade2", show_edges=True)
                self.plotter.add_bounding_box()
                self.plotter.show_axes()
                self.plotter.reset_camera()
                self.generator = None
                self.stats_box.setVisible(False)
        except Exception:
            pass

    def load_preset_file(self, file_path: str):
        """Load parameter preset from a JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                preset_data = json.load(f)
            if not isinstance(preset_data, dict):
                raise ValueError("Preset file must contain a JSON object.")
            for k, v in preset_data.items():
                if k in self.params_widgets:
                    self.params_widgets[k].setText(str(v))
            self.tabs.setCurrentIndex(0)
            self.statusBar.showMessage(f"Loaded preset: {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.warning(self, "Invalid Preset", f"Failed to load preset: {str(e)}")

    def on_browse_stl(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Input STL File", "", "STL Files (*.stl)")
        if filename:
            self.load_stl_file(filename)

    def on_generate_clicked(self):
        try:
            params = self.get_params_from_ui()
            valid, err = params.validate()
            if not valid:
                QMessageBox.warning(self, "Validation Error", err)
                return
                
            self.generate_btn.setEnabled(False)
            self.statusBar.showMessage("Generating parametric gyroid...")
            self.progressBar.setVisible(True)
            self.progressBar.setValue(10)
            
            self.worker = ParametricWorker(params)
            self.worker.finished.connect(self.on_generation_finished)
            self.worker.error.connect(self.on_generation_error)
            self.worker.progress.connect(self.progressBar.setValue)
            self.worker.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.generate_btn.setEnabled(True)

    def on_convert_stl_clicked(self):
        stl_path = self.stl_path_edit.text().strip()
        if not stl_path or not os.path.exists(stl_path):
            QMessageBox.warning(self, "Warning", "Please select a valid existing STL file.")
            return

        try:
            res = int(self.stl_res_edit.text())
            cell_size = float(self.stl_cell_edit.text())
            wall_thick = float(self.stl_wall_edit.text())
            flat_cap = self.stl_cap_check.isChecked()
            preserve_shell = self.stl_shell_check.isChecked()
            shell_thick = float(self.stl_shell_edit.text()) if preserve_shell else 1.0

            stl_params = STLConversionParams(
                stl_path=stl_path,
                resolution=res,
                cell_size=cell_size,
                wall_thickness=wall_thick,
                flat_cap=flat_cap,
                preserve_shell=preserve_shell,
                shell_thickness=shell_thick
            )
            
            self.convert_stl_btn.setEnabled(False)
            self.statusBar.showMessage("Converting STL volume to Gyroid lattice...")
            self.progressBar.setVisible(True)
            
            self.stl_worker = STLConversionWorker(stl_params)
            self.stl_worker.finished.connect(self.on_generation_finished)
            self.stl_worker.error.connect(self.on_generation_error)
            self.stl_worker.progress.connect(self.progressBar.setValue)
            self.stl_worker.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Invalid parameters: {str(e)}")

    def on_shell_check_toggled(self, checked: bool):
        self.stl_shell_label.setEnabled(checked)
        self.stl_shell_edit.setEnabled(checked)

    def on_view_mode_changed(self):
        if self.generator and self.generator.mesh:
            self.render_current_mesh()

    def render_current_mesh(self):
        self.plotter.clear()
        if self.generator is None or self.generator.mesh is None:
            return

        if self.generator.mesh.n_points == 0:
            QMessageBox.warning(self, "Empty Mesh", "Generated mesh contains 0 points. Check cell size or wall thickness.")
            return

        mesh_to_show = self.generator.mesh
        if self.cutaway_check.isChecked():
            try:
                mesh_to_show = mesh_to_show.clip(normal='x', origin=mesh_to_show.center)
            except Exception:
                mesh_to_show = self.generator.mesh

        if mesh_to_show.n_points > 0:
            self.plotter.add_mesh(mesh_to_show, scalars=mesh_to_show.points[:, -1], show_scalar_bar=False)
        self.plotter.add_bounding_box()
        self.plotter.show_axes()
        self.plotter.reset_camera()
        self.update_stats()
        self.stats_box.setVisible(True)

    def on_generation_finished(self, generator: GyroidGenerator):
        self.generator = generator
        self.statusBar.showMessage("Mesh generated successfully!")
        self.generate_btn.setEnabled(True)
        self.convert_stl_btn.setEnabled(True)
        self.progressBar.setVisible(False)
        self.render_current_mesh()

    def on_generation_error(self, error_msg):
        QMessageBox.critical(self, "Generation Failed", error_msg)
        self.generate_btn.setEnabled(True)
        self.convert_stl_btn.setEnabled(True)
        self.progressBar.setVisible(False)
        self.statusBar.showMessage("Operation failed")

    def update_stats(self):
        if self.generator and self.generator.mesh:
            stats = self.generator.get_mesh_stats()
            self.stats_labels["n_points"].setText(f"Points: {stats['n_points']:,}")
            self.stats_labels["n_cells"].setText(f"Cells: {stats['n_cells']:,}")
            self.stats_labels["volume"].setText(f"Volume: {stats['volume']:.2f} cubic units")
            self.stats_labels["surface_area"].setText(f"Surface Area: {stats['surface_area']:.2f} square units")

    def save_mesh(self, file_type):
        if not self.generator or not self.generator.mesh:
            QMessageBox.warning(self, "Warning", "Please generate a mesh first")
            return
            
        ext_filter = "STL Files (*.stl)" if file_type == "stl" else "OBJ Files (*.obj)"
        filename, _ = QFileDialog.getSaveFileName(self, f"Save as {file_type.upper()}", "", ext_filter)
        if filename:
            if not filename.lower().endswith(f".{file_type}"):
                filename += f".{file_type}"
            if file_type == "stl":
                is_stl_tab = self.tabs.currentIndex() == 1
                flat_cap = self.stl_cap_check.isChecked() if is_stl_tab else True
                self.generator.save_stl(filename, prepare_manifold=True, flat_cap=flat_cap)
            else:
                self.generator.save_obj(filename)
            self.statusBar.showMessage(f"Saved to {filename}")

    def new_project(self):
        self.generator = None
        self.stats_box.setVisible(False)
        self.apply_preset("default")
        self.stl_shell_check.setChecked(False)
        self.cutaway_check.setChecked(False)
        self.plotter.clear()
        self.statusBar.showMessage("New project started")

    def apply_theme(self, theme_name="dark"):
        if theme_name == "dark":
            self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        else:
            self.setStyleSheet("")

    def save_config(self):
        pass

    def load_config(self):
        pass


def main():
    app = QApplication(sys.argv)
    window = GyroidGeneratorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()