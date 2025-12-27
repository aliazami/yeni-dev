from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help")
        self.resize(300, 320)
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        help_text = (
            "<b>COMMANDS:</b><br>"
            "<b>Ctrl+S</b> : Save<br>"
            "<b>Ctrl+Shift+S</b> : Save As<br>"
            "<b>Ctrl+O</b> : Open<br>"
            "<b>Ctrl+Z</b> : Undo<br>"
            "<b>Ctrl+Shift+Z</b> : Redo<br>"
            "<b>I</b> : Import Background Image<br>"
            "<b>A</b> : Add Circle<br>"
            "<b>R</b> : Add Rectangle<br>"
            "<b>F</b> : Add Label<br>"
            "<b>G</b> : Add Label 2<br>"
            "<b>1</b> : Toggle Alignment Toolbar<br>"
        )
        label = QLabel(help_text)
        label.setTextFormat(Qt.RichText)
        layout.addWidget(label)
        self.setLayout(layout)