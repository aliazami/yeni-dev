from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QGraphicsItem

def align_items_helper(items:  list[QGraphicsItem], direction):
    if len(items) < 2:
        return
    target = 0.0
    if direction == "left":
        target = min(item.sceneBoundingRect().left() for item in items)
    elif direction == "right":
        target = max(item.sceneBoundingRect().right() for item in items)
    elif direction == "top":
        target = min(item.sceneBoundingRect().top() for item in items)
    elif direction == "bottom":
        target = max(item.sceneBoundingRect().bottom() for item in items)

    move_data = {}
    for item in items:
        rect = item.sceneBoundingRect()
        start_pos = item.pos()
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
            move_data[item] = (
                start_pos,
                QPointF(start_pos.x() + dx, start_pos.y() + dy),
            )

    return move_data



def distribute_items_helper(items: list[QGraphicsItem], orientation):
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
                move_data[item] = (
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
                move_data[item] = (
                    item.pos(),
                    QPointF(item.pos().x(), item.pos().y() + dy),
                )

    return move_data
