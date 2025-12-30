from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QPen, QBrush, QColor

class DefaultBackground(QGraphicsRectItem):
    def __init__(self, width: float, height: float):
        super().__init__(0, 0, width, height)
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setBrush(QBrush(QColor("#333")))
        self.setZValue(-1000)