# # app/scene.py
from enum import Enum, auto, StrEnum
from PySide6.QtCore import Signal, Qt, QRectF, QPointF, QEvent
from PySide6.QtGui import QUndoStack, QBrush, QPen, QColor, QCursor
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QFileDialog,
)

from app.constants import PART_ITEM
from app.commands import (
    AddItemsCommand,
    MoveItemsCommand,
    RemoveItemsCommand,
)

from app.components.part_item import PartItem
from app.components.background import Background
# from app.components.word_boundary_part_item import WordBoundaryPartItem
from app.helpers.scene_align_helper import align_items_helper, distribute_items_helper
from app.helpers.scene_misc_helper import calculate_move_command
from app.components.rectangle_part_item import RectanglePartItem
from app.item_manager import ItemManager, get_ui

# # ==========================================
# #                THE SCENE
# # ==========================================

class Mode(Enum):
    SELECT = auto()
    ADD_ITEM = auto()
    DRAWING_RECT = auto()


class Prop(StrEnum):
    undo_stack = "undo_stack"
    mode = "mode"
    temp_rect_item = "temp_rect_item"
    start_point = "start_point"
    drag_start_positions = "drag_start_positions"
    background_item = "background_item"
    mgr = "mgr"

class EditorScene(QGraphicsScene):
    helpRequested = Signal()
    toggleToolbarRequested = Signal()

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(100)
        self.mode = Mode.SELECT
        self.temp_rect_item = None
        self.start_point = None
        self.drag_start_positions = {}
        self.setProperty(Prop.mgr, ItemManager())
        self.setProperty("background_item", 12)
        # Background Management
        self.background_item = Background()
        # self.set_background()

#     # --- Properties ---
    @property
    def undo_stack(self):
        undo_stack: QUndoStack = self.property(Prop.undo_stack)
        return undo_stack

    @undo_stack.setter
    def undo_stack(self, value):
        self.setProperty(Prop.undo_stack, value)

    
    @property
    def mode(self):
        mode_value: Mode = self.property(Prop.mode)
        return mode_value
    
    @mode.setter
    def mode(self, value: Mode):
        if not isinstance(value, Mode):
            raise ValueError
        self.setProperty(Prop.mode, value)
        if not self.views():
            return
        view = self.views()[0]
        if value == Mode.SELECT:
            view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            view.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        else:
            view.setDragMode(QGraphicsView.DragMode.NoDrag)
            view.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.clearSelection()
        
    @property
    def temp_rect_item(self):
        temp_rect_item_value: QGraphicsRectItem | None = self.property(Prop.temp_rect_item)
        return temp_rect_item_value
    
    @temp_rect_item.setter
    def temp_rect_item(self, value: QGraphicsRectItem | None):
        self.setProperty(Prop.temp_rect_item, value)
        
    @property
    def drag_start_positions(self):
        drag_start_positions_value: dict | None = self.property(Prop.drag_start_positions)
        return drag_start_positions_value
    
    @drag_start_positions.setter
    def drag_start_positions(self, value: dict | None):
        self.setProperty(Prop.drag_start_positions, value)
    
    @property
    def background_item(self):
        prop = str(Prop.background_item)
        try:
            background_item_value: Background | None = self.property(prop)
        except Exception as e:
            print(e)
        return background_item_value
    
    @property
    def mgr(self) -> ItemManager:
        return self.property(Prop.mgr)

    @background_item.setter
    def background_item(self, value: Background | None):
        self.setProperty(Prop.background_item, value)

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
            itype = item_data["item-type"]

            if itype == PART_ITEM:
                part_item = PartItem.from_dict(item_data)
                self.addItem(part_item)
            # elif itype == GAP_I:
            #     gap_item = GapItem.from_dict(item_data)
            #     self.addItem(gap_item)
            # elif itype == "WORD_BOUNDARY_ITEM":
            #     word_boundary_item = WordBoundaryItem.from_dict(item_data)
            #     self.addItem(word_boundary_item)

    # --- UPDATED Serialize to include Rect Size ---
    def serialize_scene(self):
        background_path = (
            self.background_item.file_path() if self.background_item else None
        )
        data = {"background_image": background_path, "items": []}
        for item in self.items():
            if isinstance(item, RectanglePartItem) and item.platform_config.serializable:
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
        if mode == Mode.SELECT:
            view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            view.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        else:
            view.setDragMode(QGraphicsView.DragMode.NoDrag)
            view.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.clearSelection()

    # --- Events ---
    def keyPressEvent(self, event: QEvent):
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
        # elif event.key() == Qt.Key.Key_R:
        #     if WordBoundaryItem.pre_create(self.items(), PartItem.get_active_item()):
        #         self.set_mode("DRAWING_RECT")
        #     event.accept()
        elif event.key() == Qt.Key.Key_A:
            if self.mgr.pre_create_part_item():
                self.mode = Mode.ADD_ITEM
            event.accept()
        elif event.key() == Qt.Key.Key_Q:
            if self.mgr.pre_create_question_ref_item():
                self.mode = Mode.ADD_ITEM
            event.accept()
        elif event.key() == Qt.Key.Key_Delete:
            items = self.selectedItems()
            if items:
                deleting_items = []
                for item in items:
                    if isinstance(item, RectanglePartItem):
                        if self.mgr.remove_item(item.pre_item.uid):
                            deleting_items.append(item)
                self.undo_stack.push(RemoveItemsCommand(self, deleting_items))
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            if self.mode != Mode.SELECT:
                if self.temp_rect_item:
                    self.removeItem(self.temp_rect_item)
                    self.temp_rect_item = None
                self.mgr.is_repeating = False
                self.mode = Mode.SELECT
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
            if self.mode == Mode.DRAWING_RECT:
                self.start_point = event.scenePos()
                self.temp_rect_item = QGraphicsRectItem()
                self.temp_rect_item.setPen(
                    QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DashLine)
                )
                self.temp_rect_item.setBrush(QBrush(QColor(255, 0, 0, 50)))
                self.addItem(self.temp_rect_item)
                self.temp_rect_item.setRect(QRectF(self.start_point, self.start_point))
                event.accept()
            elif self.mode == Mode.ADD_ITEM:
                pos = event.scenePos()
                new_item = self.mgr.create(pos)
                if new_item:
                    self.undo_stack.push(
                        AddItemsCommand(self, new_item, f"Add {self.mode}")
                    )
                    if self.mgr.is_repeating:
                        self.mgr.repeat()
                    else:
                        self.mode = Mode.SELECT

                event.accept()
            else:
                super().mousePressEvent(event)
                items = self.selectedItems()
                self.drag_start_positions = {}
                for item in items:
                    rectangle_part_item: RectanglePartItem = item
                    drag_start_positions = self.drag_start_positions
                    drag_start_positions[rectangle_part_item.pre_item.uid] = item.pos()
                    self.drag_start_positions = drag_start_positions
                items_at_pos = self.items(event.scenePos())
                for item in items_at_pos:
                    if isinstance(item, RectanglePartItem):
                        self.mgr.activate_item(item.pre_item.uid)


        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.mode == Mode.DRAWING_RECT and self.temp_rect_item:
            current_point = event.scenePos()
            new_rect = QRectF(self.start_point, current_point).normalized()
            self.temp_rect_item.setRect(new_rect)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if (
            self.mode == Mode.DRAWING_RECT
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
                # final_item = WordBoundaryPartItem.create_item(pos, w, h)
                # self.addItem(final_item)
                # self.undo_stack.push(AddItemsCommand(self, final_item, "Add Rectangle"))

            self.mode = Mode.SELECT
            event.accept()

        elif self.mode == Mode.SELECT and event.button() == Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            if self.drag_start_positions:
                move_data = {}
                moved = False
                for uid, start_pos in self.drag_start_positions.items():
                    pre_item = self.mgr.get_item(uid)
                    end_pos = pre_item.ui.pos()
                    if start_pos != end_pos:
                        moved = True
                        move_data[uid] = (start_pos, end_pos)
                if moved:
                    for uid, (start, end) in move_data.items():
                        pre_item = self.mgr.get_item(uid)
                        pre_item.ui.setPos(start)
                    self.undo_stack.push(
                        MoveItemsCommand(self, move_data, "Mouse Drag")
                    )
                self.drag_start_positions = {}
        else:
            super().mouseReleaseEvent(event)

    def set_background(self, file_path=None):
        if self.background_item and self.background_item in self.items():
            self.removeItem(self.background_item)
        # self.background_item = Background(file_path)
        # rect = QRectF(self.background_item.pixmap().rect())
        # self.addItem(self.background_item)
        # self.setSceneRect(rect)

    def update_scene(self):
        for item in self.items():
            if isinstance(item, RectanglePartItem) and not self.mgr.get_item(item.pre_item.uid):
                # has been removed before
                self.removeItem(item)
            
        for pre_item in self.mgr.items:
            if pre_item.is_visible:
                ui = get_ui(pre_item)
                if ui.scene() != self:
                    self.addItem(ui)
            elif not pre_item.is_visible and pre_item.ui == self:
                self.removeItem(pre_item.ui)



    