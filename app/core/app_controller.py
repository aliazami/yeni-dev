# core/controller.py
from PySide6.QtWidgets import QFileDialog
from app.core.project_manager import ProjectManager
from app.ui.main_window import MainWindow
from app.ui.gap import LabelItem
class AppController:
    def __init__(self, project_manager: ProjectManager, main_window: MainWindow):
        self.project_manager = project_manager
        self.project = project_manager.current
        self.main_window = main_window
        self.main_window.toolbar.loadImageRequested.connect(self.load_image)
        self.main_window.view.sceneShiftLeftClickRequest.connect(self.add_label)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "Select Image",
            "",
            "Images (*.jpg *.jpeg *.png *.webp)",
        )
        if not path:
            return

        self.project.image_path = path
        self.project.counter = 0
        self.project.annotations.clear()
        self.main_window.view.load_image(self.project.image_path)


    def add_label(self, x: int, y: int):
        self.project.counter += 1
        text = f"{self.project.counter}.<empty>"

        item = LabelItem(text, x, y)
        self.main_window.view.scene().addItem(item)
        item.setFocus()

        self.project.annotations.append(item)