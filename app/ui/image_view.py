# ui/image_view.py
from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPixmap, QWheelEvent, QBrush, QColor, QPen
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsPixmapItem,
)


class ImageView(QGraphicsView):
    sceneShiftLeftClickRequest = Signal(int, int)
    sceneLeftClickRequest = Signal()
    sceneSelectionRequest = Signal(QRectF)

    def __init__(self, main_window):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        # self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        self.image_item = None
        # Internal state
        self._start_point = None
        self._current_rect_item = None

        # Styles
        self.border_color = QColor("violet")
        self.background_color = QColor(238, 130, 238, 80)  # Pale violet with alpha (80/255)
        self.pen = QPen(self.border_color, 1.5)  # Narrow border

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
        elif event.button() == Qt.MouseButton.LeftButton:
            # Map the click position to the scene coordinates
            self._start_point = self.mapToScene(event.pos())
            self.sceneLeftClickRequest.emit()
            # Create a temporary rectangle item for visual feedback during drag
            self._current_rect_item = QGraphicsRectItem()
            self._current_rect_item.setPen(self.pen)
            self._current_rect_item.setBrush(QBrush(self.background_color))

            # Add it to the scene immediately so we see it while dragging
            self.scene().addItem(self._current_rect_item)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._current_rect_item is not None:
            # Current mouse position in scene coordinates
            current_point = self.mapToScene(event.pos())

            # Calculate the rectangle dimensions
            # .normalized() ensures the rect is valid even if dragging top-left
            rect = QRectF(self._start_point, current_point).normalized()

            # Update the visual item
            self._current_rect_item.setRect(rect)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # finalize the drawing
            self.sceneSelectionRequest.emit(self._current_rect_item.rect())
            self.scene().removeItem(self._current_rect_item)
            self._current_rect_item = None
            self._start_point = None
