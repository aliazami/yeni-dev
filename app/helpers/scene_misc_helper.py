from typing import List
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QGraphicsItem
from app.components.rectangle_part_item import RectanglePartItem


def calculate_move_command(items: List[RectanglePartItem], dx, dy):
    move_data = {}
    for item in items:
        start_pos = item.pos()
        end_pos = QPointF(start_pos.x() + dx, start_pos.y() + dy)
        move_data[item.pre_item.uid] = (start_pos, end_pos)
    return move_data

def calculate_resize_command(items: List[RectanglePartItem], dx, dy):
    move_data = {}
    for item in items:
        start_size = (item.rect().width(), item.rect().height())
        end_size = (start_size[0] + dx, start_size[1] + dy)
        move_data[item.pre_item.uid] = (start_size, end_size)
    return move_data
