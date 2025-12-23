from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QWheelEvent
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
)


class ImageView(QGraphicsView):
    sceneShiftLeftClickRequest = Signal(int, int) # ?
    def __init__(self, main_window):
        super().__init__()
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
            self.sceneShiftLeftClickRequest.emit(x, y)
            return

        super().mousePressEvent(event)

