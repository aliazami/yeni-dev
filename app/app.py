# app.py
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.core.app_controller import AppController
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
)

class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.main_window = MainWindow()
        self.controller = AppController(self.main_window)
        current_folder = Path(__file__).resolve().parent.parent.resolve()
        test_file = current_folder / "test.webp"
        self.controller.load_image(test_file)
    def start(self):
        self.main_window.show()

def run():
    app = App(sys.argv)
    app.start()
    sys.exit(app.exec())