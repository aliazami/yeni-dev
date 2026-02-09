from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QGraphicsItem
from app.components.rectangle_part_item import RectanglePartItem

def align_items_helper(items:  list[RectanglePartItem], direction):
    if len(items) < 2:
        return
    target = 0.0
    if direction == "left":
        target = min(obj.sceneBoundingRect().left() for obj in items)
    elif direction == "right":
        target = max(obj.sceneBoundingRect().right() for obj in items)
    elif direction == "top":
        target = min(obj.sceneBoundingRect().top() for obj in items)
    elif direction == "bottom":
        target = max(obj.sceneBoundingRect().bottom() for obj in items)

    move_data = {}
    for obj in items:
        rect = obj.sceneBoundingRect()
        start_pos = obj.pos()
        dx, dy = 0, 0
        if direction == "left":
            dx = target - rect.left()
        elif direction == "right":
            dx = target - rect.right()
        elif direction == "top":
            dy = target - rect.top()
        elif direction == "bottom":
            dy = target - rect.bottom()
        if dx != 0 or dy != 0:
            move_data[obj.pre_item.uid] = (
                start_pos,
                QPointF(start_pos.x() + dx, start_pos.y() + dy),
            )

    return move_data



def distribute_items_helper(items: list[RectanglePartItem], orientation):
    if len(items) < 3:
        return
    move_data = {}
    if orientation == "horz":
        items.sort(key=lambda this_item: this_item.sceneBoundingRect().center().x())
        start = items[0].sceneBoundingRect().center().x()
        end = items[-1].sceneBoundingRect().center().x()
        step = (end - start) / (len(items) - 1)
        for i, item in enumerate(items):
            current_center = item.sceneBoundingRect().center().x()
            target_center = start + (i * step)
            dx = target_center - current_center
            if abs(dx) > 0.1:
                move_data[item.pre_item.uid] = (
                    item.pos(),
                    QPointF(item.pos().x() + dx, item.pos().y()),
                )
    elif orientation == "vert":
        items.sort(key=lambda this_item: this_item.sceneBoundingRect().center().y())
        start = items[0].sceneBoundingRect().center().y()
        end = items[-1].sceneBoundingRect().center().y()
        step = (end - start) / (len(items) - 1)
        for i, item in enumerate(items):
            current_center = item.sceneBoundingRect().center().y()
            target_center = start + (i * step)
            dy = target_center - current_center
            if abs(dy) > 0.1:
                move_data[item.pre_item.uid] = (
                    item.pos(),
                    QPointF(item.pos().x(), item.pos().y() + dy),
                )

    return move_data
