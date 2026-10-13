import os
import json
import pytest
import trimesh
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QMimeData, QUrl, QPoint, Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from pyroid.gui import GyroidGeneratorGUI


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def gui_window(qapp):
    win = GyroidGeneratorGUI()
    yield win
    win.close()


def test_drag_and_drop_stl(gui_window, tmp_path):
    stl_path = str(tmp_path / "test_cube.stl")
    cube = trimesh.creation.box(extents=[10, 10, 10])
    cube.export(stl_path)

    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(stl_path)])

    # Test dragEnterEvent accepts STL
    enter_event = QDragEnterEvent(QPoint(0, 0), Qt.CopyAction, mime, Qt.NoButton, Qt.NoModifier)
    gui_window.dragEnterEvent(enter_event)
    assert enter_event.isAccepted()

    # Test dropEvent processes STL
    drop_event = QDropEvent(QPoint(0, 0), Qt.CopyAction, mime, Qt.NoButton, Qt.NoModifier)
    gui_window.dropEvent(drop_event)
    assert drop_event.isAccepted()
    assert os.path.samefile(gui_window.stl_path_edit.text(), stl_path)
    assert gui_window.tabs.currentIndex() == 1  # Switched to STL Conversion tab


def test_drag_and_drop_plotter_event_filter(gui_window, tmp_path):
    stl_path = str(tmp_path / "test_plotter_cube.stl")
    cube = trimesh.creation.box(extents=[10, 10, 10])
    cube.export(stl_path)

    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(stl_path)])

    enter_event = QDragEnterEvent(QPoint(0, 0), Qt.CopyAction, mime, Qt.NoButton, Qt.NoModifier)
    drop_event = QDropEvent(QPoint(0, 0), Qt.CopyAction, mime, Qt.NoButton, Qt.NoModifier)

    # Deliver directly to plotter child widget
    QApplication.sendEvent(gui_window.plotter, enter_event)
    QApplication.sendEvent(gui_window.plotter, drop_event)

    assert drop_event.isAccepted()
    assert os.path.samefile(gui_window.stl_path_edit.text(), stl_path)
    assert gui_window.tabs.currentIndex() == 1


def test_drag_and_drop_preset_json(gui_window, tmp_path):
    preset_path = str(tmp_path / "custom_preset.json")
    preset_content = {"res": 55, "a": 18.5, "wall_thickness": 0.4}
    with open(preset_path, "w", encoding="utf-8") as f:
        json.dump(preset_content, f)

    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(preset_path)])

    enter_event = QDragEnterEvent(QPoint(0, 0), Qt.CopyAction, mime, Qt.NoButton, Qt.NoModifier)
    gui_window.dragEnterEvent(enter_event)
    assert enter_event.isAccepted()

    drop_event = QDropEvent(QPoint(0, 0), Qt.CopyAction, mime, Qt.NoButton, Qt.NoModifier)
    gui_window.dropEvent(drop_event)
    assert drop_event.isAccepted()

    assert gui_window.tabs.currentIndex() == 0  # Switched to Parametric tab
    assert gui_window.params_widgets["res"].text() == "55"
    assert gui_window.params_widgets["a"].text() == "18.5"
    assert gui_window.params_widgets["wall_thickness"].text() == "0.4"


def test_drag_and_drop_reject_unsupported(gui_window, tmp_path):
    txt_path = str(tmp_path / "readme.txt")
    with open(txt_path, "w") as f:
        f.write("unsupported file")

    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(txt_path)])

    enter_event = QDragEnterEvent(QPoint(0, 0), Qt.CopyAction, mime, Qt.NoButton, Qt.NoModifier)
    gui_window.dragEnterEvent(enter_event)
    assert not enter_event.isAccepted()

    drop_event = QDropEvent(QPoint(0, 0), Qt.CopyAction, mime, Qt.NoButton, Qt.NoModifier)
    gui_window.dropEvent(drop_event)
    assert not drop_event.isAccepted()
