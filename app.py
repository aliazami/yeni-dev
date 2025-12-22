import json
import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QWheelEvent, QKeyEvent
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsTextItem,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
)


class LabelItem(QGraphicsTextItem):
    def __init__(self, text, x, y):
        super().__init__(text)
        self.setPos(int(x), int(y))

        self.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsFocusable, True)

        self.setDefaultTextColor(Qt.GlobalColor.black)

    def focusInEvent(self, event):
        self.setDefaultTextColor(Qt.GlobalColor.red)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.setDefaultTextColor(Qt.GlobalColor.black)
        super().focusOutEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        dx, dy = 0, 0

        if event.key() == Qt.Key.Key_Left:
            dx = -1
        elif event.key() == Qt.Key.Key_Right:
            dx = 1
        elif event.key() == Qt.Key.Key_Up:
            dy = -1
        elif event.key() == Qt.Key.Key_Down:
            dy = 1
        elif event.key() == Qt.Key.Key_Delete:
            scene = self.scene()
            if scene:
                scene.removeItem(self)
            return

        if dx or dy:
            pos = self.pos()
            self.setPos(int(pos.x() + dx), int(pos.y() + dy))
            return

        super().keyPressEvent(event)


class ImageView(QGraphicsView):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.setScene(QGraphicsScene(self))
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        self.image_item = None

    def load_image(self, image_path):
        self.scene().clear()

        pixmap = QPixmap(image_path)
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.image_item.setPos(0, 0)

        self.scene().addItem(self.image_item)
        self.scene().setSceneRect(self.image_item.boundingRect())

        self.resetTransform()

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
            self.scale(factor, factor)
            return

        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            bar = self.horizontalScrollBar()
            bar.setValue(bar.value() - event.angleDelta().y())
            return

        super().wheelEvent(event)

    def mousePressEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and event.modifiers() & Qt.KeyboardModifier.ShiftModifier
            and self.image_item
        ):
            scene_pos = self.mapToScene(event.pos())
            x, y = int(scene_pos.x()), int(scene_pos.y())
            self.main_window.add_label(x, y)
            return

        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gap Coordinate Tool (v0)")
        self.resize(1200, 800)

        self.image_path = None
        self.counter = 0
        self.annotations = []

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)

        self.view = ImageView(self)
        layout.addWidget(self.view, 1)

        toolbar = QWidget()
        toolbar_layout = QVBoxLayout(toolbar)
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        load_btn = QPushButton("Load Image")
        export_btn = QPushButton("Export JSON")

        load_btn.clicked.connect(self.load_image)
        export_btn.clicked.connect(self.export_json)

        toolbar_layout.addWidget(load_btn)
        toolbar_layout.addWidget(export_btn)

        layout.addWidget(toolbar)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.jpg *.jpeg *.png *.webp)"
        )
        if not path:
            return

        self.image_path = path
        self.counter = 0
        self.annotations.clear()
        self.view.load_image(path)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
