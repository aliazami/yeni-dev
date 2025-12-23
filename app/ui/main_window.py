import json
import os

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QMessageBox,
)
from app.ui.image_view import ImageView
from app.ui.toolbar import Toolbar

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gap Coordinate Tool (v0)")
        self.resize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)

        self.view = ImageView(self)
        self.toolbar = Toolbar()
        layout.addWidget(self.view, 1)
        layout.addWidget(self.toolbar)


    def add_label(self, x, y):
        self.counter += 1
        text = f"{self.counter}.<empty>"

        item = LabelItem(text, x, y)
        self.view.scene().addItem(item)
        item.setFocus()

        self.annotations.append(item)

    def export_json(self):
        if not self.image_path:
            QMessageBox.warning(self, "No Image", "Load an image first.")
            return

        data = {"words": []}

        for item in self.annotations:
            if item.scene() is None:
                continue  # deleted

            pos = item.pos()
            data["words"].append(
                {
                    "word": item.toPlainText(),
                    "x": int(pos.x()),
                    "y": int(pos.y()),
                }
            )

        base, _ = os.path.splitext(self.image_path)
        out_path = base + ".json"

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        QMessageBox.information(self, "Exported", f"Saved:\n{out_path}")