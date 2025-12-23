from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QGraphicsTextItem,
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

