# # app/scene.py
from enum import StrEnum
from PySide6.QtCore import Signal, Qt, QRectF, QPointF
from PySide6.QtGui import QUndoStack, QBrush, QPen, QColor, QCursor, QUndoCommand, QKeyEvent
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QMessageBox,
)

from app.constants import SceneMode
from app.components.background import Background
from app.helpers.scene_align_helper import align_items_helper, distribute_items_helper
from app.helpers.scene_misc_helper import calculate_move_command, calculate_resize_command
from app.components.rectangle_part_item import RectanglePartItem
from app.item_manager import ItemManager, get_ui

from app.constants import WORD_BOUNDARY_ITEM, REF_UNIT_ITEM, CAPTION_ITEM, REF_QUESTION_ITEM, GAP_ITEM, BLOCK_ITEM

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
    saveRequested = Signal()
    toggleToolbarRequested = Signal()
    docNameRequested = Signal(str)

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
        self.setProperty(Prop.undo_stack, QUndoStack(self))
        self.undo_stack.setUndoLimit(100)
        self.temp_rect_item: QGraphicsRectItem | None = None
        self.mode = SceneMode.SELECT
        self.start_point = None
        self.drag_start_positions = {}
        self.setProperty(Prop.mgr, ItemManager())
        # Background Management

#     # --- Properties ---
    @property
    def undo_stack(self):
        undo_stack: QUndoStack = self.property(Prop.undo_stack)
        return undo_stack

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
        background_item_value = None
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
    def recreate_scene(self, old_background: Background | None, new_background: Background | None, ui_items: list[RectanglePartItem]):
        # 1. Clear everything (C++ objects are deleted)
        self.clear()
        self.undo_stack.clear()
        self.temp_rect_item = None
        if old_background and old_background in self.items():
            self.removeItem(old_background)
        if new_background:
            rect = QRectF(new_background.pixmap().rect())
            self.addItem(new_background)
            self.setSceneRect(rect)
        add_items(self, ui_items, signal_clear_dirty=True)

    # --- UPDATED Serialize to include Rect Size ---
    def serialize_scene(self):
        data, exp_data, answers = self.mgr.to_dict()
        self.mgr.stat.signal_clear_dirty()
        return data, exp_data, answers

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
    def keyPressEvent(self, event: QKeyEvent):
        shift_key = event.modifiers() == Qt.KeyboardModifier.ShiftModifier
        if event.key() == Qt.Key.Key_1:
            self.toggleToolbarRequested.emit()
            event.accept()
        elif event.key() == Qt.Key.Key_2:
            self.mgr.show_descendants()
            self.update_scene()
            event.accept()
        elif event.key() == Qt.Key.Key_3:
            self.mgr.show_regions()
            self.update_scene()
            event.accept()                
        elif event.key() == Qt.Key.Key_H:
            self.helpRequested.emit()
            event.accept()
        elif event.key() == Qt.Key.Key_I:
            self.mgr.select_input_type()
            event.accept()
        elif event.key() == Qt.Key.Key_Exclam:
            self.mgr.stat.check_doc_is_ok()
            self.mgr.get_error()
            event.accept()            
        elif event.key() == Qt.Key.Key_O:
            if self.mgr.stat.get_is_dirty():
                reply = QMessageBox.question(None, 'Confirmation', 'Save?',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Abort)
                if reply == QMessageBox.StandardButton.Abort:
                    return            
                elif reply == QMessageBox.StandardButton.Yes:
                    self.saveRequested.emit()
                elif reply == QMessageBox.StandardButton.No:
                    pass
            old_background, new_background, ui_items = self.mgr.open_image(open_last_file=shift_key)
            self.recreate_scene(old_background, new_background, ui_items)
            self.update_doc_title()
            self.mgr.stat.check_doc_is_ok()
            event.accept()
        elif event.key() == Qt.Key.Key_W:
            mode = self.mgr.pre_create_item(WORD_BOUNDARY_ITEM, auto_seq=not shift_key)
            if mode is not None:
                self.mode = mode
            event.accept()
        elif event.key() == Qt.Key.Key_B:
            mode = self.mgr.pre_create_item(BLOCK_ITEM, auto_seq=not shift_key)
            if mode is not None:
                self.mode = mode
            event.accept()            
        elif event.key() == Qt.Key.Key_C:
            mode = self.mgr.pre_create_item(CAPTION_ITEM, auto_seq=not shift_key)
            if mode is not None:
                self.mode = mode
            event.accept()
        elif event.key() == Qt.Key.Key_G:
            mode = self.mgr.pre_create_item(GAP_ITEM, auto_seq=not shift_key)
            if mode is not None:
                self.mode = mode
            event.accept()            
        elif event.key() == Qt.Key.Key_Q:
            mode = self.mgr.pre_create_item(REF_QUESTION_ITEM, auto_seq=not shift_key)
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
            mode, editing_item = self.mgr.request_redraw_rect()
            if mode is not None and editing_item:
                self.undo_stack.push(RemoveItemsCommand(self, [editing_item]))
                self.mode = mode
            event.accept()
        elif event.key() == Qt.Key.Key_0:
            mode = self.mgr.read_item()
            event.accept()            
        elif event.key() == Qt.Key.Key_A and not shift_key:
            mode = self.mgr.pre_create_item()
            if mode is not None:
                self.mode = mode
            event.accept()
        elif event.key() == Qt.Key.Key_A and shift_key:
            mode = self.mgr.pre_create_item(part_type=REF_UNIT_ITEM)
            if mode is not None:
                self.mode = mode
            event.accept()
        elif event.key() == Qt.Key.Key_BracketLeft:
            mode = self.mgr.send_to_back(True)
            event.accept()
        elif event.key() == Qt.Key.Key_BraceLeft:
            mode = self.mgr.send_to_back(False)
            event.accept()
        elif event.key() == Qt.Key.Key_BracketRight:
            mode = self.mgr.bring_to_top(True)
            event.accept()
        elif event.key() == Qt.Key.Key_BraceRight:
            mode = self.mgr.bring_to_top(False)
            event.accept()
        elif event.key() == Qt.Key.Key_Enter:
            mode = self.mgr.edit_item()
            event.accept()                     
        elif event.key() == Qt.Key.Key_Delete:
            items = self.selectedItems()
            if items:
                deleting_items = []
                for obj in items:
                    if isinstance(obj, RectanglePartItem):
                        if self.mgr.stat.remove_item(obj.pre_item.uid):
                            deleting_items.append(obj)
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
                for obj in items:
                    rectangle_part_item: RectanglePartItem = obj
                    drag_start_positions = self.drag_start_positions
                    drag_start_positions[rectangle_part_item.pre_item.uid] = obj.pos()
                    self.drag_start_positions = drag_start_positions
                items_at_pos = self.items(event.scenePos())
                for obj in items_at_pos:
                    if isinstance(obj, RectanglePartItem):
                        self.mgr.activate_item(obj.pre_item.uid)
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
                    for uid, (start, _) in move_data.items():
                        pre_item = self.mgr.stat.get_item(uid)
                        pre_item.ui.setPos(start)
                    self.undo_stack.push(
                        MoveItemsCommand(self, move_data, "Mouse Drag")
                    )
                self.drag_start_positions = {}
        else:
            super().mouseReleaseEvent(event)

    def update_scene(self):
        for obj in self.items():
            if isinstance(obj, RectanglePartItem) and not self.mgr.stat.get_item(obj.pre_item.uid):
                # has been removed before
                self.removeItem(obj)
            
        for pre_item in self.mgr.stat.items:
            if pre_item.is_visible:
                ui = get_ui(pre_item)
                if ui.scene() != self:
                    self.addItem(ui)
            elif not pre_item.is_visible and pre_item.ui.scene() == self:
                self.removeItem(pre_item.ui)

    def update_doc_title(self):
        doc_title = self.mgr.get_doc_title()
        self.docNameRequested.emit(doc_title)



# ==========================================
#              UNDO COMMANDS
# ==========================================


class AddItemsCommand(QUndoCommand):
    def __init__(self, scene: EditorScene, items: list[RectanglePartItem] | RectanglePartItem, description="Add Items"):
        super().__init__(description)
        self.scene = scene
        self.items = items if isinstance(items, list) else [items]

    def redo(self):
        add_items(self.scene, self.items)

    def undo(self):
        remove_items(self.scene, self.items)

class RemoveItemsCommand(QUndoCommand):
    def __init__(self, scene: EditorScene, items: list[RectanglePartItem] | RectanglePartItem, description="Delete Items"):
        super().__init__(description)
        self.scene = scene
        self.items = items if isinstance(items, list) else [items]

    def redo(self):
        remove_items(self.scene, self.items)

    def undo(self):
        add_items(self.scene, self.items)


class MoveItemsCommand(QUndoCommand):
    def __init__(self, scene: EditorScene, move_data: dict, description="Move Items"):
        super().__init__(description)
        self.scene = scene
        self.move_data = move_data

    def redo(self):
        items = self.move_data.items()
        for uid, (_, end) in items:
            pre_item = self.scene.mgr.stat.get_item(uid)
            if pre_item:
                pre_item.ui.setPos(end)
            else:
                print(f"Warning: {uid} not found")
        self.scene.update_doc_title()

    def undo(self):
        for uid, (start, _) in self.move_data.items():
            pre_item = self.scene.mgr.stat.get_item(uid)
            pre_item.ui.setPos(start)
        self.scene.update_doc_title()            


class ResizeItemsCommand(QUndoCommand):
    def __init__(self, scene: EditorScene, resize_data: dict, description="Move Items"):
        super().__init__(description)
        self.scene = scene
        self.resize_data = resize_data

    def redo(self):
        for uid, (_, end) in self.resize_data.items():
            pre_item = self.scene.mgr.stat.get_item(uid)
            pre_item.set_width(end[0])
            pre_item.set_height(end[1])
        self.scene.update_doc_title()            

    def undo(self):
        for uid, (start, _) in self.resize_data.items():
            pre_item = self.scene.mgr.stat.get_item(uid)
            pre_item.set_width(start[0])
            pre_item.set_height(start[1])
        self.scene.update_doc_title()            


def add_items(scene: EditorScene, items: list[RectanglePartItem], signal_clear_dirty = False):
    update_flag = False
    for obj in items:
        if isinstance(obj, RectanglePartItem) and not scene.mgr.stat.get_item(obj.pre_item.uid):
            scene.mgr.stat.add_item(obj.pre_item)
            update_flag = True
        elif obj.scene() != scene:
            scene.addItem(obj)
    if signal_clear_dirty:
        scene.mgr.stat.signal_clear_dirty()
    if update_flag:
        scene.update_scene()
        scene.update_doc_title()

def remove_items(scene: EditorScene, items: list[RectanglePartItem]):
    update_flag = False
    for obj in items:
        if isinstance(obj, RectanglePartItem) and scene.mgr.stat.get_item(obj.pre_item.uid):
            scene.mgr.stat.remove_item(obj.pre_item.uid)
            update_flag = True
        elif obj.scene() == scene:
            scene.removeItem(obj)
    if update_flag:
        scene.update_scene()
        scene.update_doc_title()