# app/commands.py
from PySide6.QtGui import QUndoCommand
from PySide6.QtWidgets import QGraphicsItem, QGraphicsScene
from app.components.rectangle_part_item import RectanglePartItem

# ==========================================
#              UNDO COMMANDS
# ==========================================


class AddItemsCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, items: list[QGraphicsItem] | QGraphicsItem, description="Add Items"):
        super().__init__(description)
        self.scene = scene
        self.items = items if isinstance(items, list) else [items]

    def redo(self):
        add_items(self.scene, self.items)

    def undo(self):
        remove_items(self.scene, self.items)

class RemoveItemsCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, items: list[QGraphicsItem] | QGraphicsItem, description="Delete Items"):
        super().__init__(description)
        self.scene = scene
        self.items = items if isinstance(items, list) else [items]

    def redo(self):
        remove_items(self.scene, self.items)

    def undo(self):
        add_items(self.scene, self.items)


class MoveItemsCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, move_data, description="Move Items"):
        super().__init__(description)
        self.scene = scene
        self.move_data = move_data

    def redo(self):
        for uid, (_, end) in self.move_data.items():
            pre_item = self.scene.mgr.stat.get_item(uid)
            pre_item.ui.setPos(end)

    def undo(self):
        for uid, (start, _) in self.move_data.items():
            pre_item = self.scene.mgr.stat.get_item(uid)
            pre_item.ui.setPos(start)


class ResizeItemsCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, resize_data, description="Move Items"):
        super().__init__(description)
        self.scene = scene
        self.resize_data = resize_data

    def redo(self):
        for uid, (_, end) in self.resize_data.items():
            pre_item = self.scene.mgr.stat.get_item(uid)
            pre_item.set_width(end[0])
            pre_item.set_height(end[1])

    def undo(self):
        for uid, (start, _) in self.resize_data.items():
            pre_item = self.scene.mgr.stat.get_item(uid)
            pre_item.set_width(start[0])
            pre_item.set_height(start[1])


def add_items(scene: QGraphicsScene, items: list[QGraphicsItem]):
    update_flag = False
    for item in items:
        if isinstance(item, RectanglePartItem) and not scene.mgr.stat.get_item(item.pre_item.uid):
            scene.mgr.stat.add_item(item.pre_item)
            update_flag = True
        elif item.scene() != scene:
            scene.addItem(item)
    if update_flag:
        scene.update_scene()

def remove_items(scene: QGraphicsScene, items: list[QGraphicsItem]):
    update_flag = False
    for item in items:
        if isinstance(item, RectanglePartItem) and scene.mgr.stat.get_item(item.pre_item.uid):
            scene.mgr.stat.remove_item(item.pre_item.uid)
            update_flag = True
        elif item.scene() == scene:
            scene.removeItem(item)
    if update_flag:
        scene.update_scene()

