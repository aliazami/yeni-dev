import json
from PySide6.QtWidgets import (QMainWindow, QGraphicsView, 
                               QFileDialog, QMessageBox)
from PySide6.QtGui import QKeySequence, QAction, QPainter
from PySide6.QtCore import Qt

from models.scene import EditorScene
from widgets import HelpWindow
from ui.toolbars import create_alignment_toolbar
from constants import DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT)
        self.setWindowTitle("Interactive Graphics Editor (Save/Load)")
        self.current_file_path = None  # State for file handling

        self.scene = EditorScene(0, 0, DEFAULT_SCENE_WIDTH, DEFAULT_SCENE_HEIGHT)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCentralWidget(self.view)

        self.help_window = HelpWindow()
        self.scene.helpRequested.connect(self.show_help_window)
        self.scene.toggleToolbarRequested.connect(self.toggle_align_toolbar)

        self.align_toolbar = create_alignment_toolbar(self, self.scene)
        self.addToolBar(Qt.TopToolBarArea, self.align_toolbar)
        self.align_toolbar.setHidden(True)

        self.create_actions()

    def create_actions(self):
        # File Menu Actions
        save_act = QAction("Save", self)
        save_act.setShortcut(QKeySequence.Save)  # Ctrl+S
        save_act.triggered.connect(self.save_file)
        self.addAction(save_act)

        save_as_act = QAction("Save As...", self)
        save_as_act.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_act.triggered.connect(self.save_file_as)
        self.addAction(save_as_act)

        open_act = QAction("Open", self)
        open_act.setShortcut(QKeySequence.Open)  # Ctrl+O
        open_act.triggered.connect(self.open_file)
        self.addAction(open_act)

        # Undo/Redo
        undo_act = self.scene.undo_stack.createUndoAction(self, "Undo")
        undo_act.setShortcut(QKeySequence.Undo)
        self.addAction(undo_act)

        redo_act = self.scene.undo_stack.createRedoAction(self, "Redo")
        redo_act.setShortcut(QKeySequence.Redo)
        self.addAction(redo_act)

    def toggle_align_toolbar(self):
        self.align_toolbar.setVisible(not self.align_toolbar.isVisible())

    def show_help_window(self):
        self.help_window.show()
        self.help_window.raise_()
        self.help_window.activateWindow()

    # --- File IO Logic ---
    def save_file(self):
        if self.current_file_path:
            self._write_to_file(self.current_file_path)
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Scene", "", "JSON Files (*.json)")
        if file_path:
            self.current_file_path = file_path
            self._write_to_file(file_path)

    def _write_to_file(self, path):
        try:
            data = self.scene.serializer.serialize_scene()
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Saved to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Scene", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                self.scene.serializer.deserialize_scene(data)
                self.current_file_path = file_path
                print(f"Loaded from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Load Error", str(e))