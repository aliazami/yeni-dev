from PySide6.QtWidgets import QGraphicsPixmapItem
from PySide6.QtGui import QUndoCommand
from PySide6.QtCore import QRectF

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


class SetBackgroundCommand(QUndoCommand):
    def __init__(self, scene, new_bg_item, old_bg_item, path, description="Change Background"):
        super().__init__(description)
        self.scene = scene
        self.new_bg = new_bg_item
        self.old_bg = old_bg_item
        self.new_path = path
        self.old_path = scene.background_path

    def redo(self):
        if self.old_bg and self.old_bg.scene() == self.scene:
            self.scene.removeItem(self.old_bg)
        if self.new_bg and self.new_bg.scene() != self.scene:
            self.scene.addItem(self.new_bg)
            self.scene.background_item = self.new_bg
            self.scene.background_path = self.new_path
            if isinstance(self.new_bg, QGraphicsPixmapItem):
                self.scene.setSceneRect(QRectF(self.new_bg.pixmap().rect()))

    def undo(self):
        if self.new_bg and self.new_bg.scene() == self.scene:
            self.scene.removeItem(self.new_bg)
        if self.old_bg and self.old_bg.scene() != self.scene:
            self.scene.addItem(self.old_bg)
            self.scene.background_item = self.old_bg
            self.scene.background_path = self.old_path
            if isinstance(self.old_bg, QGraphicsPixmapItem):
                self.scene.setSceneRect(QRectF(self.old_bg.pixmap().rect()))
            else:
                self.scene.setSceneRect(0, 0, 1000, 800)