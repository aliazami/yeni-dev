from typing import List
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QGraphicsItem


def calculate_move_command(items: List[QGraphicsItem], dx, dy):
    move_data = {}
    for item in items:
        start_pos = item.pos()
        end_pos = QPointF(start_pos.x() + dx, start_pos.y() + dy)
        move_data[item] = (start_pos, end_pos)
    return move_data
