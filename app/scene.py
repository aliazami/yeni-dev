# app/scene.py
from PySide6.QtCore import Qt, QRectF, Signal, QPointF
from PySide6.QtGui import QBrush, QPen, QColor, QCursor, QUndoStack
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QFileDialog,
)

from app.components.gap_item import GapItem
from app.commands import (
    AddItemsCommand,
    MoveItemsCommand,
    RemoveItemsCommand,
)

from app.models import ISerializable, IRepeatable
from app.components.part_item import PartItem
from app.components.background import Background
from app.components.word_boundary_item import WordBoundaryItem
from app.helpers.scene_align_helper import align_items_helper, distribute_items_helper
from app.helpers.scene_misc_helper import calculate_move_command


# ==========================================
#                THE SCENE
# ==========================================


class EditorScene(QGraphicsScene):
    helpRequested = Signal()
    toggleToolbarRequested = Signal()

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(100)

        self.mode = "SELECT"
        self.temp_rect_item = None
        self.start_point = None
        self.drag_start_positions = {}

        # self.current_part = None

        # Background Management
        self.background_item = Background()
        self.set_background()

    # --- Serialization Logic ---
    def deserialize_scene(self, data):
        # 1. Clear everything (C++ objects are deleted)
        self.clear()
        self.undo_stack.clear()

        # Reset Python references to avoid accessing deleted C++ objects
        self.temp_rect_item = None
        # self.current_part = None

        # 2. Restore Background EXPLICITLY
        # We manually create the background here instead of calling helper methods
        # like set_image_background() or init_default_background().
        # This avoids calling removeItem() on a deleted object.

        bg_path = data.get("background_image")
        self.set_background(bg_path)

        # 3. Restore Items
        for item_data in data.get("items", []):
            itype = item_data["type"]

            if itype == "CIRCLE":
                part_item = PartItem.from_dict(item_data)
                self.addItem(part_item)
            elif itype == "LABEL":
                gap_item = GapItem.from_dict(item_data)
                self.addItem(gap_item)
            elif itype == "RECTANGLE":
                word_boundary_item = WordBoundaryItem.from_dict(item_data)
                self.addItem(word_boundary_item)

    # --- UPDATED Serialize to include Rect Size ---
    def serialize_scene(self):
        background_path = (
            self.background_item.file_path() if self.background_item else None
        )
        data = {"background_image": background_path, "items": []}
        for item in self.items():
            if isinstance(item, ISerializable):
                serializable = item
                item_data = serializable.to_dict()
                data["items"].append(item_data)

        return data

    def align_items(self, direction):
        move_data = align_items_helper(self.selectedItems(), direction)
        if move_data:
            self.undo_stack.push(MoveItemsCommand(self, move_data, f"Align {direction}"))

    def distribute_items(self, orientation):
        move_data = distribute_items_helper(self.selectedItems(), orientation)
        if move_data:
            self.undo_stack.push(
                MoveItemsCommand(self, move_data, f"Distribute {orientation}")
            )

    def set_mode(self, mode):
        self.mode = mode
        if not self.views():
            return
        view = self.views()[0]
        if mode == "SELECT":
            view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            view.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        else:
            view.setDragMode(QGraphicsView.DragMode.NoDrag)
            view.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.clearSelection()

    # --- Events ---
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_1:
            self.toggleToolbarRequested.emit()
            event.accept()
        elif event.key() == Qt.Key.Key_H:
            self.helpRequested.emit()
            event.accept()
        elif event.key() == Qt.Key.Key_I:
            file_path, _ = QFileDialog.getOpenFileName(
                None, "Open Image", "", "Images (*.png *.jpg *.jpeg *.webp)"
            )
            if file_path:
                self.set_background(file_path)
            event.accept()
        elif event.key() == Qt.Key.Key_R:
            if WordBoundaryItem.pre_create(self.items(), PartItem.get_active_item()):
                self.set_mode("DRAWING_RECT")
            event.accept()
        elif event.key() == Qt.Key.Key_A:
            if PartItem.pre_create(self.items(), ""):
                self.set_mode("ADD_CIRCLE")
            event.accept()
        elif event.key() == Qt.Key.Key_F:
            if GapItem.pre_create(self.items(), PartItem.get_active_item()):
                self.set_mode("ADD_LABEL")
            event.accept()
        elif event.key() == Qt.Key.Key_Delete:
            items = self.selectedItems()
            if items:
                for item in items:
                    if (
                        isinstance(item, PartItem)
                        and item.part_id == PartItem.get_active_item()
                    ):
                        PartItem.set_active_item(self.part_items, part_id="")
                self.undo_stack.push(RemoveItemsCommand(self, items))
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            if self.mode != "SELECT":
                if self.temp_rect_item:
                    self.removeItem(self.temp_rect_item)
                    self.temp_rect_item = None

                for item in self.items():
                    if isinstance(item, IRepeatable):
                        item.cancel_repeating()
                self.set_mode("SELECT")
            else:
                self.clearSelection()
        elif event.key() in (
            Qt.Key.Key_Left,
            Qt.Key.Key_Right,
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
        ):
            step = 1 if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else 10
            dx, dy = 0, 0
            if event.key() == Qt.Key.Key_Left:
                dx = -step
            elif event.key() == Qt.Key.Key_Right:
                dx = step
            elif event.key() == Qt.Key.Key_Up:
                dy = -step
            elif event.key() == Qt.Key.Key_Down:
                dy = step
            items = self.selectedItems()
            if items:
                move_data = calculate_move_command(items, dx, dy)
                self.undo_stack.push(MoveItemsCommand(self, move_data, "Arrow Move"))
                event.accept()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode == "DRAWING_RECT":
                self.start_point = event.scenePos()
                self.temp_rect_item = QGraphicsRectItem()
                self.temp_rect_item.setPen(
                    QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DashLine)
                )
                self.temp_rect_item.setBrush(QBrush(QColor(255, 0, 0, 50)))
                self.addItem(self.temp_rect_item)
                self.temp_rect_item.setRect(QRectF(self.start_point, self.start_point))
                event.accept()
            elif self.mode in ["ADD_CIRCLE", "ADD_LABEL"]:
                pos = event.scenePos()
                new_item = None
                if self.mode == "ADD_CIRCLE":
                    new_item = PartItem.create_item(pos, 0, 0)
                    PartItem.set_active_item(self.part_items, part_id=new_item.part_id)

                elif self.mode == "ADD_LABEL":
                    new_item = GapItem.create_item(pos, 0, 0)
                if new_item:
                    self.undo_stack.push(
                        AddItemsCommand(self, new_item, f"Add {self.mode}")
                    )
                    if isinstance(new_item, IRepeatable):
                        if new_item.is_repeating:
                            new_item.repeat()
                        else:
                            self.set_mode("SELECT")
                    else:
                        self.set_mode("SELECT")
                event.accept()
            else:
                super().mousePressEvent(event)
                items = self.selectedItems()
                self.drag_start_positions = {}
                for item in items:
                    self.drag_start_positions[item] = item.pos()
                items_at_pos = self.items(event.scenePos())
                for item in items_at_pos:
                    if isinstance(item, PartItem):
                        PartItem.set_active_item(self.part_items, part_id=item.part_id)
                        break

        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.mode == "DRAWING_RECT" and self.temp_rect_item:
            current_point = event.scenePos()
            new_rect = QRectF(self.start_point, current_point).normalized()
            self.temp_rect_item.setRect(new_rect)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if (
            self.mode == "DRAWING_RECT"
            and event.button() == Qt.MouseButton.LeftButton
            and self.temp_rect_item
        ):
            # 1. Get the geometry of the drawn dashed rectangle
            geo = self.temp_rect_item.rect()

            # Remove the temporary dashed item
            self.removeItem(self.temp_rect_item)
            self.temp_rect_item = None

            if geo.width() > 1 and geo.height() > 1:
                pos = QPointF(geo.x(), geo.y())
                w = geo.width()
                h = geo.height()
                final_item = WordBoundaryItem.create_item(pos, w, h)
                self.addItem(final_item)
                self.undo_stack.push(AddItemsCommand(self, final_item, "Add Rectangle"))

            self.set_mode("SELECT")
            event.accept()

        elif self.mode == "SELECT" and event.button() == Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            if self.drag_start_positions:
                move_data = {}
                moved = False
                for item, start_pos in self.drag_start_positions.items():
                    end_pos = item.pos()
                    if start_pos != end_pos:
                        moved = True
                        move_data[item] = (start_pos, end_pos)
                if moved:
                    for item, (start, end) in move_data.items():
                        item.setPos(start)
                    self.undo_stack.push(
                        MoveItemsCommand(self, move_data, "Mouse Drag")
                    )
                self.drag_start_positions = {}
        else:
            super().mouseReleaseEvent(event)

    def set_background(self, file_path=None):
        if self.background_item and self.background_item in self.items():
            self.removeItem(self.background_item)
        self.background_item = Background(file_path)
        rect = QRectF(self.background_item.pixmap().rect())
        self.addItem(self.background_item)
        self.setSceneRect(rect)

    @property
    def part_items(self):
        return [item for item in self.items() if isinstance(item, PartItem)]
