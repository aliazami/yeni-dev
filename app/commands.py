# app/commands.py
from PySide6.QtGui import QUndoCommand
from PySide6.QtWidgets import QGraphicsScene
from app.components.rectangle_part_item import RectanglePartItem
# ==========================================
#              UNDO COMMANDS
# ==========================================


class AddItemsCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, items: list[RectanglePartItem], description="Add Items"):
        super().__init__(description)
        self.scene = scene
        self.items = items if isinstance(items, list) else [items]

    def redo(self):
        for item in self.items:
            if item.scene() != self.scene:
                self.scene.addItem(item)

    def undo(self):
        for item in self.items:
            if item.scene() == self.scene:
                self.scene.removeItem(item)


class RemoveItemsCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, items: list[RectanglePartItem], description="Delete Items"):
        super().__init__(description)
        self.scene = scene
        self.items = items if isinstance(items, list) else [items]

    def redo(self):
        for item in self.items:
            if item.scene() == self.scene:
                self.scene.removeItem(item)

    def undo(self):
        for item in self.items:
            if item.scene() != self.scene:
                self.scene.addItem(item)


class MoveItemsCommand(QUndoCommand):
    def __init__(self, scene: QGraphicsScene, move_data, description="Move Items"):
        super().__init__(description)
        self.scene = scene
        self.move_data = move_data

    def redo(self):
        for item, (start, end) in self.move_data.items():
            set_pos(item, end)

    def undo(self):
        for item, (start, end) in self.move_data.items():
            set_pos(item, start)


def set_pos(item: RectanglePartItem, pos):
    if isinstance(item, RectanglePartItem):
        item.setPos(pos)
        item.pre_item.update_ui()
