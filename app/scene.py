# app/scene.py
import os
from PySide6.QtCore import Qt, QRectF, Signal, QPointF
from PySide6.QtGui import QBrush, QPen, QColor, QCursor, QFont, QPixmap, QUndoStack
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QGraphicsTextItem,
    QGraphicsItem,
    QGraphicsPixmapItem,
    QInputDialog,
    QMessageBox,
    QDialog,
    QFileDialog,
)

from app.constants import KEY_ID, KEY_RECT_ID, KEY_RECT_TEXT, KEY_TYPE
from app.commands import (
    AddItemsCommand,
    MoveItemsCommand,
    RemoveItemsCommand,
    SetBackgroundCommand,
)
from app.dialogs import RectInputDialog
from app.components.part_item import PartItem
from app.components.default_background import DefaultBackground
from app.components.word_boundary_item import WordBoundaryItem


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

        self.current_id = None
        self.pending_payload = ""
        self.pending_rect_id = None
        self.pending_rect_text = None
        self.drag_start_positions = {}

        # Background Management
        self.background_item = None
        self.background_path = None  # Store path for JSON saving
        self.default_w = w
        self.default_h = h

        self.init_default_background()

    def init_default_background(self):
        if self.background_item:
            self.removeItem(self.background_item)
        background = DefaultBackground(self.default_w, self.default_h)
        self.background_item = background
        self.background_path = None
        self.setSceneRect(0, 0, self.default_w, self.default_h)

    # --- Serialization Logic ---
    def deserialize_scene(self, data):
        # 1. Clear everything (C++ objects are deleted)
        self.clear()
        self.undo_stack.clear()

        # Reset Python references to avoid accessing deleted C++ objects
        self.background_item = None
        self.temp_rect_item = None
        self.current_id = None

        # 2. Restore Background EXPLICITLY
        # We manually create the background here instead of calling helper methods
        # like set_image_background() or init_default_background().
        # This avoids calling removeItem() on a deleted object.

        bg_path = data.get("background_image")
        loaded_bg = False

        if bg_path and os.path.exists(bg_path):
            pixmap = QPixmap(bg_path)
            if not pixmap.isNull():
                # Create Pixmap Background
                new_bg = QGraphicsPixmapItem(pixmap)
                new_bg.setZValue(-1000)
                new_bg.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
                self.addItem(new_bg)

                # Update State
                self.background_item = new_bg
                self.background_path = bg_path
                self.setSceneRect(QRectF(pixmap.rect()))
                loaded_bg = True

        if not loaded_bg:
            # Create Default Rect Background
            rect = QGraphicsRectItem(0, 0, self.default_w, self.default_h)
            rect.setPen(QPen(Qt.PenStyle.NoPen))
            rect.setBrush(QBrush(QColor("#333")))
            rect.setZValue(-1000)
            self.addItem(rect)

            # Update State
            self.background_item = rect
            self.background_path = None
            self.setSceneRect(0, 0, self.default_w, self.default_h)

        # 3. Restore Items
        for item_data in data.get("items", []):
            itype = item_data["type"]
            pos = QPointF(item_data["x"], item_data["y"])
            iid = item_data.get("id")

            if itype == "CIRCLE":
                part_item = PartItem.from_dict(item_data)
                self.addItem(part_item)
            elif itype == "LABEL":
                self.restore_label(pos, iid)
            elif itype == "LABEL2":
                self.restore_label2(pos, iid)
            elif itype == "RECTANGLE":
                word_boundary_item = WordBoundaryItem.from_dict(item_data)
                self.addItem(word_boundary_item)

        self.refresh_circle_colors()

    # --- Restoration Helpers ---

    def restore_label(self, pos, text):
        t = QGraphicsTextItem(text)
        t.setDefaultTextColor(Qt.GlobalColor.white)
        t.setFont(QFont("Arial", 14))
        t.setPos(pos)
        t.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        t.setData(KEY_ID, text)
        t.setData(KEY_TYPE, "LABEL")
        self.addItem(t)

    def restore_label2(self, pos, text):
        t = QGraphicsTextItem(text)
        t.setDefaultTextColor(QColor("#00FFFF"))
        t.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        t.setPos(pos)
        t.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        t.setData(KEY_ID, text)
        t.setData(KEY_TYPE, "LABEL2")
        self.addItem(t)

    # --- UPDATED Serialize to include Rect Size ---
    def serialize_scene(self):
        data = {"background_image": self.background_path, "items": []}
        for item in self.items():
            if (
                item == self.background_item
                or item == self.temp_rect_item
                or item.parentItem()
            ):
                continue

            item_type = item.data(KEY_TYPE)
            if not item_type:
                continue
            item_data = {
                "type": item_type,
                "x": item.pos().x(),
                "y": item.pos().y(),
                "id": item.data(KEY_ID),
            }
            if isinstance(item, WordBoundaryItem):
                item_data = item.to_dict()
            if isinstance(item, PartItem):
                item_data = item.to_dict()
            data["items"].append(item_data)
        return data

    # --- Background Logic ---
    def set_image_background(self, file_path, record_undo=True):
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            return
        new_bg = QGraphicsPixmapItem(pixmap)
        new_bg.setZValue(-1000)
        new_bg.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        if record_undo:
            cmd = SetBackgroundCommand(
                self, new_bg, self.background_item, file_path, "Import Image"
            )
            self.undo_stack.push(cmd)
        else:
            if self.background_item:
                self.removeItem(self.background_item)
            self.addItem(new_bg)
            self.background_item = new_bg
            self.background_path = file_path
            self.setSceneRect(QRectF(pixmap.rect()))

    # --- Commands Logic (Move, Align, etc. - same as before) ---
    def push_background_image(self, file_path):
        self.set_image_background(file_path, record_undo=True)

    def calculate_move_command(self, items, dx, dy):
        if self:
            pass
        move_data = {}
        for item in items:
            start_pos = item.pos()
            end_pos = QPointF(start_pos.x() + dx, start_pos.y() + dy)
            move_data[item] = (start_pos, end_pos)
        return move_data

    def align_items(self, direction):
        items = self.selectedItems()
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
        if move_data:
            self.undo_stack.push(
                MoveItemsCommand(self, move_data, f"Align {direction}")
            )

    def distribute_items(self, orientation):
        items = self.selectedItems()
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
        if move_data:
            self.undo_stack.push(
                MoveItemsCommand(self, move_data, f"Distribute {orientation}")
            )

    # --- Helpers (Unchanged) ---
    def circle_id_exists(self, target_id):
        for item in self.items():
            if item.data(KEY_TYPE) == "CIRCLE" and item.data(KEY_ID) == target_id:
                return True
        return False

    def label_id_exists(self, full_label):
        for item in self.items():
            if item.data(KEY_TYPE) == "LABEL" and item.data(KEY_ID) == full_label:
                return True
        return False

    def label2_id_exists(self, full_label):
        for item in self.items():
            if item.data(KEY_TYPE) == "LABEL2" and item.data(KEY_ID) == full_label:
                return True
        return False

    def rect_compound_id_exists(self, compound_id):
        for item in self.items():
            if item.data(KEY_TYPE) == "RECTANGLE":
                existing = f"{item.data(KEY_ID)}.{item.data(KEY_RECT_ID)}.{item.data(KEY_RECT_TEXT)}"
                if existing == compound_id:
                    return True
        return False

    def get_next_label_int(self):
        if not self.current_id:
            return 1
        max_val = 0
        prefix = f"{self.current_id}."
        for item in self.items():
            if item.data(KEY_TYPE) == "LABEL":
                lbl = item.data(KEY_ID)
                if lbl.startswith(prefix):
                    try:
                        max_val = max(max_val, int(lbl.split(".")[1]))
                    except Exception:
                        pass
        return max_val + 1

    def get_next_label2_int(self):
        if not self.current_id:
            return 1
        max_val = 0
        prefix = f"{self.current_id}."
        for item in self.items():
            if item.data(KEY_TYPE) == "LABEL2":
                lbl = item.data(KEY_ID)
                if lbl.startswith(prefix) and lbl.endswith("**"):
                    try:
                        max_val = max(max_val, int(lbl.replace("**", "").split(".")[1]))
                    except Exception:
                        pass
        return max_val + 1

    def refresh_circle_colors(self):
        for item in self.items():
            if isinstance(item, PartItem):
                item_id = item.data(KEY_ID)
                is_active = item_id == self.current_id
                item.set_active(is_active)

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
                self.push_background_image(file_path)
            event.accept()
        elif event.key() == Qt.Key.Key_R:
            if not self.current_id:
                QMessageBox.warning(None, "Error", "No Circle Selected.")
                event.accept()
                return
            dialog = RectInputDialog()
            if dialog.exec() == QDialog.DialogCode.Accepted:
                r_id, r_text = dialog.get_data()
                if not r_id.isdigit():
                    QMessageBox.warning(None, "Error", "ID must be int.")
                    event.accept()
                    return
                if not r_text:
                    QMessageBox.warning(None, "Error", "Text required.")
                    event.accept()
                    return
                if self.rect_compound_id_exists(f"{self.current_id}.{r_id}.{r_text}"):
                    QMessageBox.warning(None, "Error", "Exists!")
                    event.accept()
                    return
                self.pending_rect_id = r_id
                self.pending_rect_text = r_text
                self.set_mode("DRAWING_RECT")
            event.accept()
        elif event.key() == Qt.Key.Key_A:
            text, ok = QInputDialog.getText(None, "Add Circle", "Enter Unique ID:")
            if ok and text:
                if self.circle_id_exists(text):
                    QMessageBox.warning(None, "Error", "Exists!")
                else:
                    self.pending_payload = text
                    self.set_mode("ADD_CIRCLE")
            event.accept()
        elif event.key() == Qt.Key.Key_F:
            if not self.current_id:
                QMessageBox.warning(None, "Error", "No Circle Selected.")
                event.accept()
                return
            default_int = self.get_next_label_int()
            val, ok = QInputDialog.getInt(
                None, "Add Label", "Sequence:", value=default_int, minValue=1
            )
            if ok:
                full = f"{self.current_id}.{val}"
                if self.label_id_exists(full):
                    QMessageBox.warning(None, "Error", "Exists!")
                else:
                    self.pending_payload = full
                    self.set_mode("ADD_LABEL")
            event.accept()
        elif event.key() == Qt.Key.Key_G:
            if not self.current_id:
                QMessageBox.warning(None, "Error", "No Circle Selected.")
                event.accept()
                return
            default_int = self.get_next_label2_int()
            val, ok = QInputDialog.getInt(
                None, "Add Label 2", "Sequence:", value=default_int, minValue=1
            )
            if ok:
                full = f"{self.current_id}.{val}**"
                if self.label2_id_exists(full):
                    QMessageBox.warning(None, "Error", "Exists!")
                else:
                    self.pending_payload = full
                    self.set_mode("ADD_LABEL2")
            event.accept()
        elif event.key() == Qt.Key.Key_Delete:
            items = self.selectedItems()
            if items:
                for item in items:
                    if (
                        item.data(KEY_TYPE) == "CIRCLE"
                        and item.data(KEY_ID) == self.current_id
                    ):
                        self.current_id = None
                self.undo_stack.push(RemoveItemsCommand(self, items))
                self.refresh_circle_colors()
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            if self.mode != "SELECT":
                if self.temp_rect_item:
                    self.removeItem(self.temp_rect_item)
                    self.temp_rect_item = None
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
                move_data = self.calculate_move_command(items, dx, dy)
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
            elif self.mode in ["ADD_CIRCLE", "ADD_LABEL", "ADD_LABEL2"]:
                pos = event.scenePos()
                new_item = None
                if self.mode == "ADD_CIRCLE":
                    new_item = PartItem(item_id=self.pending_payload, pos=pos)
                    self.current_id = self.pending_payload
                elif self.mode == "ADD_LABEL":
                    text = QGraphicsTextItem(self.pending_payload)
                    text.setDefaultTextColor(Qt.GlobalColor.white)
                    text.setFont(QFont("Arial", 14))
                    text.setPos(pos)
                    text.setFlags(
                        QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable
                    )
                    text.setData(KEY_ID, self.pending_payload)
                    text.setData(KEY_TYPE, "LABEL")
                    new_item = text
                elif self.mode == "ADD_LABEL2":
                    text = QGraphicsTextItem(self.pending_payload)
                    text.setDefaultTextColor(QColor("#00FFFF"))
                    text.setFont(QFont("Arial", 14, QFont.Weight.Bold))
                    text.setPos(pos)
                    text.setFlags(
                        QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable
                    )
                    text.setData(KEY_ID, self.pending_payload)
                    text.setData(KEY_TYPE, "LABEL2")
                    new_item = text
                if new_item:
                    self.undo_stack.push(
                        AddItemsCommand(self, new_item, f"Add {self.mode}")
                    )
                    self.refresh_circle_colors()
                    self.set_mode("SELECT")
                event.accept()
            else:
                super().mousePressEvent(event)
                items = self.selectedItems()
                self.drag_start_positions = {}
                for item in items:
                    self.drag_start_positions[item] = item.pos()
                items_at_pos = self.items(event.scenePos())
                clicked_circle = None
                for item in items_at_pos:
                    if item.data(KEY_TYPE) == "CIRCLE":
                        clicked_circle = item
                        break
                if clicked_circle:
                    self.current_id = clicked_circle.data(KEY_ID)
                    self.refresh_circle_colors()
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
                final_item = WordBoundaryItem(
                    part_id=self.current_id,
                    item_id=self.pending_rect_id,
                    word=self.pending_rect_text,
                    pos=QPointF(geo.x(), geo.y()),
                    w=geo.width(),
                    h=geo.height(),
                )
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
