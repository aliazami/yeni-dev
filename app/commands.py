# app/commands.py
from PySide6.QtGui import QUndoCommand
from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QGraphicsPixmapItem

# ==========================================
#              UNDO COMMANDS
# ==========================================


class AddItemsCommand(QUndoCommand):
    def __init__(self, scene, items, description="Add Items"):
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
    def __init__(self, scene, items, description="Delete Items"):
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
    def __init__(self, scene, move_data, description="Move Items"):
        super().__init__(description)
        self.scene = scene
        self.move_data = move_data

    def redo(self):
        for item, (start, end) in self.move_data.items():
            item.setPos(end)

    def undo(self):
        for item, (start, end) in self.move_data.items():
            item.setPos(start)

