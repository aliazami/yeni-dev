import os
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem
from constants import (
    KEY_ID, KEY_RECT_ID, KEY_RECT_TEXT, KEY_TYPE, ITEM_TYPE_RECTANGLE
)

class SceneSerializer:
    def __init__(self, scene):
        self.scene = scene

    def serialize_scene(self):
        data = {
            "background_image": self.scene.background_path,
            "items": []
        }

        for item in self.scene.items():
            # Skip temp items or background
            if item == self.scene.background_item or item == self.scene.temp_rect_item:
                continue

            # Skip child items
            if item.parentItem() is not None:
                continue

            item_type = item.data(KEY_TYPE)
            if not item_type: 
                continue

            item_data = {
                "type": item_type,
                "x": item.pos().x(),
                "y": item.pos().y(),
                "id": item.data(KEY_ID)
            }

            if item_type == ITEM_TYPE_RECTANGLE:
                item_data["rect_id"] = item.data(KEY_RECT_ID)
                item_data["rect_text"] = item.data(KEY_RECT_TEXT)
                # Save Dimensions
                r = item.rect()
                item_data["w"] = r.width()
                item_data["h"] = r.height()

            data["items"].append(item_data)

        return data

    def deserialize_scene(self, data):
        # Clear everything
        self.scene.clear()
        self.scene.undo_stack.clear()
        self.scene.current_id = None

        # Restore Background
        bg_path = data.get("background_image")
        if bg_path and os.path.exists(bg_path):
            self._restore_background(bg_path)
        else:
            self.scene.init_default_background()

        # Restore Items
        for item_data in data.get("items", []):
            self._restore_item(item_data)

        self.scene.refresh_circle_colors()

    def _restore_background(self, bg_path):
        pixmap = QPixmap(bg_path)
        if not pixmap.isNull():
            new_bg = QGraphicsPixmapItem(pixmap)
            new_bg.setZValue(-1000)
            new_bg.set