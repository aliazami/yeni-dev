# app/main_window.py
import json
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow,
    QGraphicsView,
    QMessageBox,
    QToolBar,
    QFileDialog,
)
from app.helpers.utils import create_icon
from app.scene import EditorScene
from app.dialogs import HelpWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 800)
        self.setWindowTitle("No page")

        self.scene = EditorScene(0, 0, 1000, 800)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setCentralWidget(self.view)
        self.align_toolbar = None
        self.help_window = HelpWindow()
        self.scene.helpRequested.connect(self.show_help_window)
        self.scene.saveRequested.connect(self.save_file)
        self.scene.toggleToolbarRequested.connect(self.toggle_align_toolbar)
        self.scene.docNameRequested.connect(self.doc_name_request)

        self.create_alignment_toolbar()
        self.create_actions()

    def create_actions(self):
        # File Menu Actions
        save_act = QAction("Save", self)
        save_act.setShortcut(QKeySequence.StandardKey.Save)  # Ctrl+S
        save_act.triggered.connect(self.save_file)
        self.addAction(save_act)

        save_as_act = QAction("Save As...", self)
        # Ctrl+Shift+S is standard for Save As
        save_as_act.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_act.triggered.connect(self.save_file_as)
        self.addAction(save_as_act)


        # Undo/Redo
        undo_act = self.scene.undo_stack.createUndoAction(self, "Undo")
        undo_act.setShortcut(QKeySequence.StandardKey.Undo)
        self.addAction(undo_act)

        redo_act = self.scene.undo_stack.createRedoAction(self, "Redo")
        redo_act.setShortcut(QKeySequence.StandardKey.Redo)
        self.addAction(redo_act)

    def create_alignment_toolbar(self):
        self.align_toolbar = QToolBar("Alignment")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.align_toolbar)
        self.align_toolbar.setHidden(True)

        act_left = QAction(create_icon("align_left"), "Left", self)
        act_left.triggered.connect(lambda: self.scene.align_items("left"))
        act_right = QAction(create_icon("align_right"), "Right", self)
        act_right.triggered.connect(lambda: self.scene.align_items("right"))
        act_top = QAction(create_icon("align_top"), "Top", self)
        act_top.triggered.connect(lambda: self.scene.align_items("top"))
        act_btm = QAction(create_icon("align_bottom"), "Bottom", self)
        act_btm.triggered.connect(lambda: self.scene.align_items("bottom"))
        act_d_h = QAction(create_icon("dist_horz"), "Dist H", self)
        act_d_h.triggered.connect(lambda: self.scene.distribute_items("horz"))
        act_d_v = QAction(create_icon("dist_vert"), "Dist V", self)
        act_d_v.triggered.connect(lambda: self.scene.distribute_items("vert"))

        self.align_toolbar.addAction(act_left)
        self.align_toolbar.addAction(act_right)
        self.align_toolbar.addAction(act_top)
        self.align_toolbar.addAction(act_btm)
        self.align_toolbar.addSeparator()
        self.align_toolbar.addAction(act_d_h)
        self.align_toolbar.addAction(act_d_v)

    def toggle_align_toolbar(self):
        self.align_toolbar.setVisible(not self.align_toolbar.isVisible())

    def show_help_window(self):
        self.help_window.show()
        self.help_window.raise_()
        self.help_window.activateWindow()

    # --- File IO Logic ---

    def save_file(self):
        data_path = self.scene.mgr.io.json_path
        exp_data_path = self.scene.mgr.io.exp_json_path
        answers_path = self.scene.mgr.io.answers_json_path
        if data_path and answers_path:
            self._write_to_file(data_path, exp_data_path, answers_path)
        else:
            QMessageBox.warning(None, "Error", "No image is loaded")

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Scene", "", "JSON Files (*.json)"
        )
        if file_path:
            self._write_to_file(file_path)

    def _write_to_file(self, data_path, exp_data_path, answers_path):
        try:
            data, exp_data, answers = self.scene.serialize_scene()
            if data:
                with open(data_path, "w") as f:
                    json.dump(data, f, indent=4)
                print(f"Data Saved to {data_path}")
            if exp_data_path:
                with open(exp_data_path, "w") as f:
                    json.dump(exp_data, f, indent=4)
                print(f"Exported Data Saved to {exp_data_path}")                
            if answers:
                with open(answers_path, "w") as f:
                    json.dump(answers, f, indent=4)
                print(f"Answer Saved to {answers_path}") 
            self.scene.update_doc_title()
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def doc_name_request(self, docname: str):
        self.setWindowTitle(docname)
