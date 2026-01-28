# app/utils.py
from PySide6.QtCore import Qt, QPointF, QPoint, QRect
from PySide6.QtGui import QPixmap, QPainter, QPen, QBrush, QIcon
from app.constants import UI_SETTINGS


def create_icon(icon_type, color=UI_SETTINGS["colors"]["icon"]):
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setPen(QPen(color, 2))
    painter.setBrush(QBrush(color))
    if icon_type == "align_left":
        painter.drawLine(4, 4, 4, 28)
        painter.drawRect(8, 6, 12, 6)
        painter.drawRect(8, 20, 16, 6)
    elif icon_type == "align_right":
        painter.drawLine(28, 4, 28, 28)
        painter.drawRect(12, 6, 12, 6)
        painter.drawRect(8, 20, 16, 6)
    elif icon_type == "align_top":
        painter.drawLine(4, 4, 28, 4)
        painter.drawRect(6, 8, 6, 12)
        painter.drawRect(20, 8, 6, 16)
    elif icon_type == "align_bottom":
        painter.drawLine(4, 28, 28, 28)
        painter.drawRect(6, 12, 6, 12)
        painter.drawRect(20, 8, 6, 16)
    elif icon_type == "dist_horz":
        painter.drawRect(4, 10, 6, 12)
        painter.drawRect(13, 10, 6, 12)
        painter.drawRect(22, 10, 6, 12)
        painter.drawLine(4, 6, 28, 6)
        painter.drawLine(4, 4, 4, 8)
        painter.drawLine(28, 4, 28, 8)
    elif icon_type == "dist_vert":
        painter.drawRect(10, 4, 12, 6)
        painter.drawRect(10, 13, 12, 6)
        painter.drawRect(10, 22, 12, 6)
        painter.drawLine(6, 4, 6, 28)
        painter.drawLine(4, 4, 8, 4)
        painter.drawLine(4, 28, 8, 28)
    painter.end()
    return QIcon(pixmap)


def ignore(var):
    if var:
        pass

def lengths_are_very_similar(length1: float, length2: float):
    return abs(length1 - length2) < 1

def points_are_very_near(pnt1: QPoint | QPointF, pnt2: QPoint | QPointF):
    if abs(pnt1.x() - pnt2.x()) > 1: 
        return False
    if abs(pnt1.y() - pnt2.y()) > 1:
        return False
    return True

def resize_rect(rect: QRect, w: int | None, h: int | None):
    x = rect.x()
    y = rect.y()
    width = w if w is not None else rect.width()
    height = h if h is not None else rect.height()
    return QRect(x, y, width, height)
