from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
)

class Toolbar(QWidget):
    loadImageRequested = Signal()
    exportJsonRequested = Signal()
    def __init__(self, /):
        super().__init__()
        toolbar_layout = QVBoxLayout(self)
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        load_btn = QPushButton("Load Image")
        export_btn = QPushButton("Export JSON")

        load_btn.clicked.connect(self.loadImageRequested.emit)
        export_btn.clicked.connect(self.exportJsonRequested.emit)

        toolbar_layout.addWidget(load_btn)
        toolbar_layout.addWidget(export_btn)