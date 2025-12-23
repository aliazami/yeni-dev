import sys
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.core.project_manager import ProjectManager
from app.core.app_controller import AppController

class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.main_window = MainWindow()
        self.project_manager = ProjectManager()
        self.controller = AppController(self.project_manager, self.main_window)


    def start(self):
        self.main_window.show()

def run():
    app = App(sys.argv)
    app.start()
    sys.exit(app.exec())