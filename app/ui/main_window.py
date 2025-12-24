# ui/main_window.py
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
)
from app.ui.image_view import ImageView
from app.ui.toolbar import Toolbar

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gap Coordinate Tool (v0)")
        self.resize(1200, 800)
        self.current_item = None
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)

        self.view = ImageView(self)
        self.toolbar = Toolbar()
        layout.addWidget(self.view, 1)
        layout.addWidget(self.toolbar)
