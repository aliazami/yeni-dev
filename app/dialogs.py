# app/dialogs.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QComboBox
)

# ==========================================
#              GUI COMPONENTS
# ==========================================


class RectInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Rectangle Details")
        self.resize(300, 150)
        layout = QFormLayout(self)
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter Integer ID")
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter Text")
        layout.addRow("Rectangle ID (Int):", self.id_input)
        layout.addRow("Description:", self.text_input)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return self.id_input.text().strip(), self.text_input.text().strip()
    
class PartSelectDialog(QDialog):
    def __init__(self, child_options: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Part Item Type")
        self.resize(300, 150)
        self.child_options = child_options
        layout = QVBoxLayout(self)
        self.combo_box = QComboBox()
        for child_type in self.child_options:
            self.combo_box.addItem(child_type[0])
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter ID:")
        id_str = str(self.child_options[0][1])
        self.id_input.setText(id_str)
        self.combo_box.currentIndexChanged.connect(self.update_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(self.combo_box)
        layout.addWidget(self.id_input)
        layout.addWidget(buttons)
        self.combo_box.setCurrentIndex(0)

    def update_label(self, selected_type):
        id_str = str(self.child_options[selected_type][1])
        self.id_input.setText(id_str)


    def get_data(self):
        return self.combo_box.currentText(), int(self.id_input.text().strip())


class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help")
        self.resize(300, 320)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
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
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)
        self.setLayout(layout)
