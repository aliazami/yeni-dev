import os
from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtCore import Qt
from app.constants import Z_ORDER_BACKGROUND

BACKGROUND_FILE_KEY = 5
EMPTY = "empty"
WIDTH = 1000
HEIGHT = 800

class Background(QGraphicsPixmapItem):

    def __init__(self, file_path = None):
        file_path = file_path or EMPTY
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            pixmap = QPixmap(WIDTH, HEIGHT)
            pixmap.fill(QColor("#333"))
            file_path = EMPTY
        super().__init__(pixmap)
        self.setZValue(Z_ORDER_BACKGROUND)
        self.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.setData(BACKGROUND_FILE_KEY, file_path)

    def file_path(self) -> dict:
        return self.data(BACKGROUND_FILE_KEY)

    @classmethod
    def set_file_path(cls, file_path: str):
        return cls(file_path)

    def is_empty(self):
        return self.data(BACKGROUND_FILE_KEY) == EMPTY
