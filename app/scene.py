# # app/scene.py
from enum import StrEnum
from PySide6.QtCore import Signal, Qt, QRectF, QPointF, QEvent
from PySide6.QtGui import QUndoStack, QBrush, QPen, QColor, QCursor
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
)

from app.constants import SceneMode
from app.commands import (
    AddItemsCommand,
    MoveItemsCommand,
    RemoveItemsCommand,
    ResizeItemsCommand,
    add_items,
)

from app.components.background import Background
from app.helpers.scene_align_helper import align_items_helper, distribute_items_helper
from app.helpers.scene_misc_helper import calculate_move_command, calculate_resize_command
from app.components.rectangle_part_item import RectanglePartItem
from app.item_manager import ItemManager, get_ui

from app.constants import WORD_BOUNDARY_ITEM, REF_UNIT_ITEM

# # ==========================================
# #                THE SCENE
# # ==========================================


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
    docNameRequested = Signal(str)

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(100)
        self.temp_rect_item: QGraphicsRectItem | None = None
        self.mode = SceneMode.SELECT
        self.start_point = None
        self.drag_start_positions = {}
        self.setProperty(Prop.mgr, ItemManager())
        # Background Management
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
        mode_value: SceneMode = self.property(Prop.mode)
        return mode_value
    
    @mode.setter
    def mode(self, value: SceneMode):
        if not isinstance(value, SceneMode):
            raise ValueError

        self.setProperty(Prop.mode, value)
        if not self.views():
            return
        view = self.views()[0]
        if value == SceneMode.SELECT:
            view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            view.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        else:
            view.setDragMode(QGraphicsView.DragMode.NoDrag)
            view.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.clearSelection()
        
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
    def deserialize_scene(self, data: dict):
        # 1. Clear everything (C++ objects are deleted)
        self.clear()
        self.undo_stack.clear()
        self.temp_rect_item = None
        self.setProperty(Prop.mgr, ItemManager())
        
        background_image = data.get("background_image")
        if background_image:
           old_background, new_background = self.mgr.io.open_image(file_path=background_image)
           self.set_background(old_background, new_background)
        # 3. Restore Items
        ui_items = []
        for item_data in data.get("items", []):
            ui_item = self.mgr.create_from_dict(item_data)
            if ui_item:
                ui_items.append(ui_item)
        add_items(self, ui_items)

    # --- UPDATED Serialize to include Rect Size ---
    def serialize_scene(self):
        data = self.mgr.to_dict()
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

    # --- Events ---
    def keyPressEvent(self, event: QEvent):
        shif_key = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        if event.key() == Qt.Key.Key_1:
            self.toggleToolbarRequested.emit()
            event.accept()
        elif event.key() == Qt.Key.Key_H:
            self.helpRequested.emit()
            event.accept()
        elif event.key() == Qt.Key.Key_I:
            old_background, new_background = self.mgr.open_image()
            if old_background and old_background in self.items():
                self.removeItem(old_background)
            if new_background:
                self.docNameRequested.emit(self.mgr.io.image_name)
                self.clear()
                rect = QRectF(new_background.pixmap().rect())
                self.addItem(new_background)
                self.setSceneRect(rect)
            data = self.mgr.io.load_json()
            if data:
                self.deserialize_scene(data)
            event.accept()
        elif event.key() == Qt.Key.Key_B:
            mode = self.mgr.pre_create_item(WORD_BOUNDARY_ITEM)
            if mode is not None:
                self.mode = mode
            event.accept()
        elif event.key() == Qt.Key.Key_N:
            mode = self.mgr.request_next_item()
            if mode is not None:
                self.mode = mode
            event.accept()
        elif event.key() == Qt.Key.Key_D:
            mode = self.mgr.request_deep_copy()
            if mode is not None:
                self.mode = mode
            event.accept()                      
        elif event.key() == Qt.Key.Key_E:
            mode, editing_item = self.mgr.request_edit()
            if mode is not None and editing_item:
                self.undo_stack.push(RemoveItemsCommand(self, [editing_item]))
                self.mode = mode
            event.accept()
        elif event.key() == Qt.Key.Key_A and not shif_key:
            mode = self.mgr.pre_create_item()
            if mode is not None:
                self.mode = mode
            event.accept()
        elif event.key() == Qt.Key.Key_A and shif_key:
            mode = self.mgr.pre_create_item(part_type=REF_UNIT_ITEM)
            if mode is not None:
                self.mode = mode
            event.accept()
            
        elif event.key() == Qt.Key.Key_Delete:
            items = self.selectedItems()
            if items:
                deleting_items = []
                for item in items:
                    if isinstance(item, RectanglePartItem):
                        if self.mgr.stat.remove_item(item.pre_item.uid):
                            deleting_items.append(item)
                self.undo_stack.push(RemoveItemsCommand(self, deleting_items))
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            if self.mode != SceneMode.SELECT:
                if self.temp_rect_item:
                    self.removeItem(self.temp_rect_item)
                    self.temp_rect_item = None
                if self.mgr._editing_item:
                    self.undo_stack.undo()
                self.mgr.escape()
                self.mode = SceneMode.SELECT

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
            if items and event.modifiers() & Qt.KeyboardModifier.AltModifier:
                move_data = calculate_resize_command(items, dx, dy)
                self.undo_stack.push(ResizeItemsCommand(self, move_data, "Arrow Resize"))
                event.accept()
            elif items:
                move_data = calculate_move_command(items, dx, dy)
                self.undo_stack.push(MoveItemsCommand(self, move_data, "Arrow Move"))
                event.accept()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.mode in [SceneMode.DRAWING_RECT, SceneMode.EDIT_RECT]:
                self.start_point = event.scenePos()
                self.temp_rect_item = QGraphicsRectItem()
                self.temp_rect_item.setPen(
                    QPen(Qt.GlobalColor.red, 2, Qt.PenStyle.DashLine)
                )
                self.temp_rect_item.setBrush(QBrush(QColor(255, 0, 0, 50)))
                self.addItem(self.temp_rect_item)
                self.temp_rect_item.setRect(QRectF(self.start_point, self.start_point))
                event.accept()
            elif self.mode == SceneMode.ADD_ITEM:
                pos = event.scenePos()
                new_item = self.mgr.create(pos)
                if new_item:
                    self.undo_stack.push(
                        AddItemsCommand(self, new_item, f"Add {new_item.pre_item.uid}")
                    )
                    if self.mgr.is_repeating:
                        self.mode = self.mgr.request_next_item()
                    else:
                        self.mode = SceneMode.SELECT
                event.accept()
            elif self.mode == SceneMode.DEEP_COPY:
                pos = event.scenePos()
                new_item_list = self.mgr.deep_copy(pos)
                if new_item_list:
                    self.undo_stack.push(
                        AddItemsCommand(self, new_item_list, f"Deep Copy {self.mode}")
                    )
                    self.mode = SceneMode.SELECT
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
                        self.update_scene()


        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.mode in [SceneMode.DRAWING_RECT, SceneMode.EDIT_RECT] and self.temp_rect_item:
            current_point = event.scenePos()
            new_rect = QRectF(self.start_point, current_point).normalized()
            self.temp_rect_item.setRect(new_rect)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if (
            self.mode in [SceneMode.DRAWING_RECT, SceneMode.EDIT_RECT]
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
                new_item = None
                command = ""
                if self.mode == SceneMode.DRAWING_RECT:
                    new_item = self.mgr.create_rect(pos, w, h)
                    command = "Add"
                if self.mode == SceneMode.EDIT_RECT:
                    new_item = self.mgr.edit_rect(pos, w, h)
                    command = "Edit-Add"
                if new_item:
                    self.undo_stack.push(
                        AddItemsCommand(self, new_item, f"{command} {new_item.pre_item.uid}")
                    )

            self.mode = SceneMode.SELECT
            event.accept()

        elif self.mode == SceneMode.SELECT and event.button() == Qt.MouseButton.LeftButton:
            super().mouseReleaseEvent(event)
            if self.drag_start_positions:
                move_data = {}
                moved = False
                for uid, start_pos in self.drag_start_positions.items():
                    pre_item = self.mgr.stat.get_item(uid)
                    end_pos = pre_item.ui.pos()
                    if start_pos != end_pos:
                        moved = True
                        move_data[uid] = (start_pos, end_pos)
                if moved:
                    for uid, (start, end) in move_data.items():
                        pre_item = self.mgr.stat.get_item(uid)
                        pre_item.ui.setPos(start)
                    self.undo_stack.push(
                        MoveItemsCommand(self, move_data, "Mouse Drag")
                    )
                self.drag_start_positions = {}
        else:
            super().mouseReleaseEvent(event)

    def set_background(self, old_background: Background, new_background: Background):
        if old_background and old_background in self.items():
            self.removeItem(old_background)
        if new_background:
            rect = QRectF(new_background.pixmap().rect())
            self.addItem(new_background)
            self.setSceneRect(rect)   

    def update_scene(self):
        for item in self.items():
            if isinstance(item, RectanglePartItem) and not self.mgr.stat.get_item(item.pre_item.uid):
                # has been removed before
                self.removeItem(item)
            
        for pre_item in self.mgr.stat.items:
            if pre_item.is_visible:
                ui = get_ui(pre_item)
                if ui.scene() != self:
                    self.addItem(ui)
            elif not pre_item.is_visible and pre_item.ui.scene() == self:
                self.removeItem(pre_item.ui)



    