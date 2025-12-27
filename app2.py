import sys
import json
import os
from PySide6.QtCore import Qt, QRectF, Signal, QPointF
from PySide6.QtGui import (QBrush, QPen, QColor, QPainter, QCursor, QFont,
                           QAction, QIcon, QPixmap, QKeySequence,
                           QUndoStack, QUndoCommand)
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                               QGraphicsScene, QGraphicsRectItem,
                               QGraphicsEllipseItem, QGraphicsSimpleTextItem,
                               QGraphicsTextItem, QGraphicsItem, QGraphicsPixmapItem,
                               QInputDialog, QWidget, QVBoxLayout, QLabel,
                               QMessageBox, QToolBar, QStyle, QDialog,
                               QFormLayout, QLineEdit, QDialogButtonBox,
                               QFileDialog)

# --- Constants ---
KEY_ID = 0
KEY_TYPE = 1
KEY_RECT_ID = 2
KEY_RECT_TEXT = 3


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


# ==========================================
#              GUI COMPONENTS
# ==========================================

def create_icon(icon_type, color=Qt.black):
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setPen(QPen(color, 2))
    painter.setBrush(QBrush(color))
    if icon_type == "align_left":
        painter.drawLine(4, 4, 4, 28);
        painter.drawRect(8, 6, 12, 6);
        painter.drawRect(8, 20, 16, 6)
    elif icon_type == "align_right":
        painter.drawLine(28, 4, 28, 28);
        painter.drawRect(12, 6, 12, 6);
        painter.drawRect(8, 20, 16, 6)
    elif icon_type == "align_top":
        painter.drawLine(4, 4, 28, 4);
        painter.drawRect(6, 8, 6, 12);
        painter.drawRect(20, 8, 6, 16)
    elif icon_type == "align_bottom":
        painter.drawLine(4, 28, 28, 28);
        painter.drawRect(6, 12, 6, 12);
        painter.drawRect(20, 8, 6, 16)
    elif icon_type == "dist_horz":
        painter.drawRect(4, 10, 6, 12);
        painter.drawRect(13, 10, 6, 12);
        painter.drawRect(22, 10, 6, 12)
        painter.drawLine(4, 6, 28, 6);
        painter.drawLine(4, 4, 4, 8);
        painter.drawLine(28, 4, 28, 8)
    elif icon_type == "dist_vert":
        painter.drawRect(10, 4, 12, 6);
        painter.drawRect(10, 13, 12, 6);
        painter.drawRect(10, 22, 12, 6)
        painter.drawLine(6, 4, 6, 28);
        painter.drawLine(4, 4, 8, 4);
        painter.drawLine(4, 28, 8, 28)
    painter.end()
    return QIcon(pixmap)


class RectInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Rectangle Details")
        self.resize(300, 150)
        layout = QFormLayout(self)
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter Integer ID")
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter Text")
        layout.addRow("Rectangle ID (Int):", self.id_input)
        layout.addRow("Description:", self.text_input)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return self.id_input.text().strip(), self.text_input.text().strip()


class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help")
        self.resize(300, 320)
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        help_text = (
            "<b>COMMANDS:</b><br>"
            "<b>Ctrl+S</b> : Save<br>"
            "<b>Ctrl+Shift+S</b> : Save As<br>"
            "<b>Ctrl+O</b> : Open<br>"
            "<b>Ctrl+Z</b> : Undo<br>"
            "<b>Ctrl+Shift+Z</b> : Redo<br>"
            "<b>I</b> : Import Background Image<br>"
            "<b>A</b> : Add Circle<br>"
            "<b>R</b> : Add Rectangle<br>"
            "<b>F</b> : Add Label<br>"
            "<b>G</b> : Add Label 2<br>"
            "<b>1</b> : Toggle Alignment Toolbar<br>"
        )
        label = QLabel(help_text)
        label.setTextFormat(Qt.RichText)
        layout.addWidget(label)
        self.setLayout(layout)


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

        self.mode = 'SELECT'
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
        rect = QGraphicsRectItem(0, 0, self.default_w, self.default_h)
        rect.setPen(QPen(Qt.NoPen))
        rect.setBrush(QBrush(QColor("#333")))
        rect.setZValue(-1000)
        self.addItem(rect)
        self.background_item = rect
        self.background_path = None
        self.setSceneRect(0, 0, self.default_w, self.default_h)

    # --- Serialization Logic ---
    def serialize_scene(self):
        data = {
            "background_image": self.background_path,
            "items": []
        }

        for item in self.items():
            # Skip temp items or background
            if item == self.background_item or item == self.temp_rect_item:
                continue

            # Skip child items (Text inside shapes), we rebuild them from parents
            if item.parentItem() is not None:
                continue

            item_type = item.data(KEY_TYPE)
            if not item_type: continue

            item_data = {
                "type": item_type,
                "x": item.pos().x(),
                "y": item.pos().y(),
                "id": item.data(KEY_ID)
            }

            if item_type == "RECTANGLE":
                item_data["rect_id"] = item.data(KEY_RECT_ID)
                item_data["rect_text"] = item.data(KEY_RECT_TEXT)

            data["items"].append(item_data)

        return data

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
                new_bg.setAcceptedMouseButtons(Qt.NoButton)
                self.addItem(new_bg)

                # Update State
                self.background_item = new_bg
                self.background_path = bg_path
                self.setSceneRect(QRectF(pixmap.rect()))
                loaded_bg = True

        if not loaded_bg:
            # Create Default Rect Background
            rect = QGraphicsRectItem(0, 0, self.default_w, self.default_h)
            rect.setPen(QPen(Qt.NoPen))
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
            iid = item_data["id"]

            if itype == "CIRCLE":
                self.restore_circle(pos, iid)
            elif itype == "LABEL":
                self.restore_label(pos, iid)
            elif itype == "LABEL2":
                self.restore_label2(pos, iid)
            elif itype == "RECTANGLE":
                w = item_data.get("w", 100)
                h = item_data.get("h", 50)
                self.restore_rectangle_with_size(pos, iid, item_data["rect_id"], item_data["rect_text"], w, h)

        self.refresh_circle_colors()

    # --- Restoration Helpers ---
    def restore_circle(self, pos, text):
        radius = 25
        ellipse = QGraphicsEllipseItem(-radius, -radius, radius * 2, radius * 2)
        ellipse.setPos(pos)
        ellipse.setPen(QPen(Qt.black, 2))
        ellipse.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        ellipse.setData(KEY_ID, text)
        ellipse.setData(KEY_TYPE, "CIRCLE")

        t = QGraphicsSimpleTextItem(text, parent=ellipse)
        t.setFont(QFont("Arial", 12, QFont.Bold))
        br = t.boundingRect()
        t.setPos(-br.width() / 2, -br.height() / 2)
        t.setAcceptedMouseButtons(Qt.NoButton)
        self.addItem(ellipse)

    def restore_label(self, pos, text):
        t = QGraphicsTextItem(text)
        t.setDefaultTextColor(Qt.white);
        t.setFont(QFont("Arial", 14))
        t.setPos(pos)
        t.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        t.setData(KEY_ID, text);
        t.setData(KEY_TYPE, "LABEL")
        self.addItem(t)

    def restore_label2(self, pos, text):
        t = QGraphicsTextItem(text)
        t.setDefaultTextColor(QColor("#00FFFF"));
        t.setFont(QFont("Arial", 14, QFont.Bold))
        t.setPos(pos)
        t.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        t.setData(KEY_ID, text);
        t.setData(KEY_TYPE, "LABEL2")
        self.addItem(t)

    def restore_rectangle(self, pos, circle_id, rect_id, rect_text):
        # We need to recreate the geometry. Since we don't save width/height in requirement,
        # we can assume standard size or we should have saved it.
        # Requirement 6 says: "finished drawing a rectangle".
        # To strictly follow "restore state", we *should* save width/height.
        # However, for this demo, I will default to a 100x100 rect if w/h isn't saved.
        # *Self-correction*: The rect geometry defines pos.
        # QGraphicsRectItem geometry is (x, y, w, h).
        # When user draws, they define a Rect.
        # In `serialize`, I only saved x,y (pos). I missed width/height.
        # FIX: Let's update `serialize_scene` to save width/height for rectangles.
        pass  # Logic handled in updated serialize_scene below

    def restore_rectangle_with_size(self, pos, circle_id, rect_id, rect_text, w, h):
        rect_item = QGraphicsRectItem(0, 0, w, h)
        rect_item.setPos(pos)
        rect_item.setPen(QPen(Qt.green, 2))
        rect_item.setBrush(QBrush(QColor(0, 255, 0, 100)))
        rect_item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        rect_item.setData(KEY_TYPE, "RECTANGLE")
        rect_item.setData(KEY_ID, circle_id)
        rect_item.setData(KEY_RECT_ID, rect_id)
        rect_item.setData(KEY_RECT_TEXT, rect_text)

        lbl = f"{circle_id}.{rect_id}.{rect_text}"
        t = QGraphicsSimpleTextItem(lbl, parent=rect_item)
        t.setBrush(QBrush(Qt.white));
        t.setFont(QFont("Arial", 10))
        t.setPos(0, h + 5)
        t.setAcceptedMouseButtons(Qt.NoButton)
        self.addItem(rect_item)

    # --- UPDATED Serialize to include Rect Size ---
    def serialize_scene(self):
        data = {"background_image": self.background_path, "items": []}
        for item in self.items():
            if item == self.background_item or item == self.temp_rect_item or item.parentItem(): continue
            item_type = item.data(KEY_TYPE)
            if not item_type: continue

            item_data = {
                "type": item_type,
                "x": item.pos().x(),
                "y": item.pos().y(),
                "id": item.data(KEY_ID)
            }
            if item_type == "RECTANGLE":
                item_data["rect_id"] = item.data(KEY_RECT_ID)
                item_data["rect_text"] = item.data(KEY_RECT_TEXT)
                # Save Dimensions
                r = item.rect()
                item_data["w"] = r.width()
                item_data["h"] = r.height()

            data["items"].append(item_data)
        return data

    def deserialize_scene(self, data):
        self.clear();
        self.undo_stack.clear();
        self.current_id = None

        bg_path = data.get("background_image")
        if bg_path and os.path.exists(bg_path):
            self.set_image_background(bg_path, record_undo=False)
        else:
            self.init_default_background()

        for item_data in data.get("items", []):
            itype = item_data["type"]
            pos = QPointF(item_data["x"], item_data["y"])
            iid = item_data["id"]
            if itype == "CIRCLE":
                self.restore_circle(pos, iid)
            elif itype == "LABEL":
                self.restore_label(pos, iid)
            elif itype == "LABEL2":
                self.restore_label2(pos, iid)
            elif itype == "RECTANGLE":
                self.restore_rectangle_with_size(pos, iid, item_data["rect_id"], item_data["rect_text"],
                                                 item_data.get("w", 100), item_data.get("h", 100))
        self.refresh_circle_colors()

    # --- Background Logic ---
    def set_image_background(self, file_path, record_undo=True):
        pixmap = QPixmap(file_path)
        if pixmap.isNull(): return
        new_bg = QGraphicsPixmapItem(pixmap)
        new_bg.setZValue(-1000)
        new_bg.setAcceptedMouseButtons(Qt.NoButton)
        if record_undo:
            cmd = SetBackgroundCommand(self, new_bg, self.background_item, file_path, "Import Image")
            self.undo_stack.push(cmd)
        else:
            if self.background_item: self.removeItem(self.background_item)
            self.addItem(new_bg)
            self.background_item = new_bg
            self.background_path = file_path
            self.setSceneRect(QRectF(pixmap.rect()))

    # --- Commands Logic (Move, Align, etc - same as before) ---
    def push_background_image(self, file_path):
        self.set_image_background(file_path, record_undo=True)

    def calculate_move_command(self, items, dx, dy):
        move_data = {}
        for item in items:
            start_pos = item.pos()
            end_pos = QPointF(start_pos.x() + dx, start_pos.y() + dy)
            move_data[item] = (start_pos, end_pos)
        return move_data

    def align_items(self, direction):
        items = self.selectedItems()
        if len(items) < 2: return
        target = 0.0
        if direction == 'left':
            target = min(item.sceneBoundingRect().left() for item in items)
        elif direction == 'right':
            target = max(item.sceneBoundingRect().right() for item in items)
        elif direction == 'top':
            target = min(item.sceneBoundingRect().top() for item in items)
        elif direction == 'bottom':
            target = max(item.sceneBoundingRect().bottom() for item in items)

        move_data = {}
        for item in items:
            rect = item.sceneBoundingRect()
            start_pos = item.pos()
            dx, dy = 0, 0
            if direction == 'left':
                dx = target - rect.left()
            elif direction == 'right':
                dx = target - rect.right()
            elif direction == 'top':
                dy = target - rect.top()
            elif direction == 'bottom':
                dy = target - rect.bottom()
            if dx != 0 or dy != 0:
                move_data[item] = (start_pos, QPointF(start_pos.x() + dx, start_pos.y() + dy))
        if move_data: self.undo_stack.push(MoveItemsCommand(self, move_data, f"Align {direction}"))

    def distribute_items(self, orientation):
        items = self.selectedItems()
        if len(items) < 3: return
        move_data = {}
        if orientation == 'horz':
            items.sort(key=lambda item: item.sceneBoundingRect().center().x())
            start = items[0].sceneBoundingRect().center().x();
            end = items[-1].sceneBoundingRect().center().x()
            step = (end - start) / (len(items) - 1)
            for i, item in enumerate(items):
                current_center = item.sceneBoundingRect().center().x();
                target_center = start + (i * step)
                dx = target_center - current_center
                if abs(dx) > 0.1: move_data[item] = (item.pos(), QPointF(item.pos().x() + dx, item.pos().y()))
        elif orientation == 'vert':
            items.sort(key=lambda item: item.sceneBoundingRect().center().y())
            start = items[0].sceneBoundingRect().center().y();
            end = items[-1].sceneBoundingRect().center().y()
            step = (end - start) / (len(items) - 1)
            for i, item in enumerate(items):
                current_center = item.sceneBoundingRect().center().y();
                target_center = start + (i * step)
                dy = target_center - current_center
                if abs(dy) > 0.1: move_data[item] = (item.pos(), QPointF(item.pos().x(), item.pos().y() + dy))
        if move_data: self.undo_stack.push(MoveItemsCommand(self, move_data, f"Distribute {orientation}"))

    # --- Helpers (Unchanged) ---
    def circle_id_exists(self, target_id):
        for item in self.items():
            if item.data(KEY_TYPE) == "CIRCLE" and item.data(KEY_ID) == target_id: return True
        return False

    def label_id_exists(self, full_label):
        for item in self.items():
            if item.data(KEY_TYPE) == "LABEL" and item.data(KEY_ID) == full_label: return True
        return False

    def label2_id_exists(self, full_label):
        for item in self.items():
            if item.data(KEY_TYPE) == "LABEL2" and item.data(KEY_ID) == full_label: return True
        return False

    def rect_compound_id_exists(self, compound_id):
        for item in self.items():
            if item.data(KEY_TYPE) == "RECTANGLE":
                existing = f"{item.data(KEY_ID)}.{item.data(KEY_RECT_ID)}.{item.data(KEY_RECT_TEXT)}"
                if existing == compound_id: return True
        return False

    def get_next_label_int(self):
        if not self.current_id: return 1
        max_val = 0;
        prefix = f"{self.current_id}."
        for item in self.items():
            if item.data(KEY_TYPE) == "LABEL":
                lbl = item.data(KEY_ID)
                if lbl.startswith(prefix):
                    try:
                        max_val = max(max_val, int(lbl.split('.')[1]))
                    except:
                        pass
        return max_val + 1

    def get_next_label2_int(self):
        if not self.current_id: return 1
        max_val = 0;
        prefix = f"{self.current_id}."
        for item in self.items():
            if item.data(KEY_TYPE) == "LABEL2":
                lbl = item.data(KEY_ID)
                if lbl.startswith(prefix) and lbl.endswith("**"):
                    try:
                        max_val = max(max_val, int(lbl.replace("**", "").split('.')[1]))
                    except:
                        pass
        return max_val + 1

    def refresh_circle_colors(self):
        for item in self.items():
            if item.data(KEY_TYPE) == "CIRCLE":
                item_id = item.data(KEY_ID)
                if item_id == self.current_id:
                    item.setBrush(QBrush(QColor("#4488FF")));
                    item.setPen(QPen(Qt.black, 2))
                else:
                    item.setBrush(QBrush(Qt.yellow));
                    item.setPen(QPen(Qt.black, 2))

    def set_mode(self, mode):
        self.mode = mode
        if not self.views(): return
        view = self.views()[0]
        if mode == 'SELECT':
            view.setDragMode(QGraphicsView.RubberBandDrag);
            view.setCursor(QCursor(Qt.ArrowCursor))
        else:
            view.setDragMode(QGraphicsView.NoDrag);
            view.setCursor(QCursor(Qt.CrossCursor))
            self.clearSelection()

    # --- Events ---
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_1:
            self.toggleToolbarRequested.emit(); event.accept()
        elif event.key() == Qt.Key_H:
            self.helpRequested.emit(); event.accept()
        elif event.key() == Qt.Key_I:
            file_path, _ = QFileDialog.getOpenFileName(None, "Open Image", "", "Images (*.png *.jpg *.jpeg *.webp)")
            if file_path: self.push_background_image(file_path)
            event.accept()
        elif event.key() == Qt.Key_R:
            if not self.current_id: QMessageBox.warning(None, "Error", "No Circle Selected."); event.accept(); return
            dialog = RectInputDialog()
            if dialog.exec() == QDialog.Accepted:
                r_id, r_text = dialog.get_data()
                if not r_id.isdigit(): QMessageBox.warning(None, "Error", "ID must be int."); event.accept(); return
                if not r_text: QMessageBox.warning(None, "Error", "Text required."); event.accept(); return
                if self.rect_compound_id_exists(f"{self.current_id}.{r_id}.{r_text}"):
                    QMessageBox.warning(None, "Error", "Exists!");
                    event.accept();
                    return
                self.pending_rect_id = r_id;
                self.pending_rect_text = r_text
                self.set_mode('DRAWING_RECT')
            event.accept()
        elif event.key() == Qt.Key_A:
            text, ok = QInputDialog.getText(None, "Add Circle", "Enter Unique ID:")
            if ok and text:
                if self.circle_id_exists(text):
                    QMessageBox.warning(None, "Error", "Exists!")
                else:
                    self.pending_payload = text; self.set_mode('ADD_CIRCLE')
            event.accept()
        elif event.key() == Qt.Key_F:
            if not self.current_id: QMessageBox.warning(None, "Error", "No Circle Selected."); event.accept(); return
            default_int = self.get_next_label_int()
            val, ok = QInputDialog.getInt(None, "Add Label", f"Sequence:", value=default_int, minValue=1)
            if ok:
                full = f"{self.current_id}.{val}"
                if self.label_id_exists(full):
                    QMessageBox.warning(None, "Error", "Exists!")
                else:
                    self.pending_payload = full; self.set_mode('ADD_LABEL')
            event.accept()
        elif event.key() == Qt.Key_G:
            if not self.current_id: QMessageBox.warning(None, "Error", "No Circle Selected."); event.accept(); return
            default_int = self.get_next_label2_int()
            val, ok = QInputDialog.getInt(None, "Add Label 2", f"Sequence:", value=default_int, minValue=1)
            if ok:
                full = f"{self.current_id}.{val}**"
                if self.label2_id_exists(full):
                    QMessageBox.warning(None, "Error", "Exists!")
                else:
                    self.pending_payload = full; self.set_mode('ADD_LABEL2')
            event.accept()
        elif event.key() == Qt.Key_Delete:
            items = self.selectedItems()
            if items:
                for item in items:
                    if item.data(KEY_TYPE) == "CIRCLE" and item.data(KEY_ID) == self.current_id: self.current_id = None
                self.undo_stack.push(RemoveItemsCommand(self, items))
                self.refresh_circle_colors()
            event.accept()
        elif event.key() == Qt.Key_Escape:
            if self.mode != 'SELECT':
                if self.temp_rect_item: self.removeItem(self.temp_rect_item); self.temp_rect_item = None
                self.set_mode('SELECT')
            else:
                self.clearSelection()
        elif event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            step = 1 if event.modifiers() & Qt.ShiftModifier else 10
            dx, dy = 0, 0
            if event.key() == Qt.Key_Left:
                dx = -step
            elif event.key() == Qt.Key_Right:
                dx = step
            elif event.key() == Qt.Key_Up:
                dy = -step
            elif event.key() == Qt.Key_Down:
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
        if event.button() == Qt.LeftButton:
            if self.mode == 'DRAWING_RECT':
                self.start_point = event.scenePos()
                self.temp_rect_item = QGraphicsRectItem()
                self.temp_rect_item.setPen(QPen(Qt.red, 2, Qt.DashLine))
                self.temp_rect_item.setBrush(QBrush(QColor(255, 0, 0, 50)))
                self.addItem(self.temp_rect_item)
                self.temp_rect_item.setRect(QRectF(self.start_point, self.start_point))
                event.accept()
            elif self.mode in ['ADD_CIRCLE', 'ADD_LABEL', 'ADD_LABEL2']:
                pos = event.scenePos()
                new_item = None
                if self.mode == 'ADD_CIRCLE':
                    radius = 25
                    ellipse = QGraphicsEllipseItem(-radius, -radius, radius * 2, radius * 2)
                    ellipse.setPos(pos);
                    ellipse.setPen(QPen(Qt.black, 2))
                    ellipse.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
                    ellipse.setData(KEY_ID, self.pending_payload);
                    ellipse.setData(KEY_TYPE, "CIRCLE")
                    text = QGraphicsSimpleTextItem(self.pending_payload, parent=ellipse)
                    text.setFont(QFont("Arial", 12, QFont.Bold))
                    br = text.boundingRect();
                    text.setPos(-br.width() / 2, -br.height() / 2)
                    text.setAcceptedMouseButtons(Qt.NoButton)
                    new_item = ellipse;
                    self.current_id = self.pending_payload
                elif self.mode == 'ADD_LABEL':
                    text = QGraphicsTextItem(self.pending_payload)
                    text.setDefaultTextColor(Qt.white);
                    text.setFont(QFont("Arial", 14))
                    text.setPos(pos);
                    text.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
                    text.setData(KEY_ID, self.pending_payload);
                    text.setData(KEY_TYPE, "LABEL")
                    new_item = text
                elif self.mode == 'ADD_LABEL2':
                    text = QGraphicsTextItem(self.pending_payload)
                    text.setDefaultTextColor(QColor("#00FFFF"));
                    text.setFont(QFont("Arial", 14, QFont.Bold))
                    text.setPos(pos);
                    text.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
                    text.setData(KEY_ID, self.pending_payload);
                    text.setData(KEY_TYPE, "LABEL2")
                    new_item = text
                if new_item:
                    self.undo_stack.push(AddItemsCommand(self, new_item, f"Add {self.mode}"))
                    self.refresh_circle_colors();
                    self.set_mode('SELECT')
                event.accept()
            else:
                super().mousePressEvent(event)
                items = self.selectedItems()
                self.drag_start_positions = {}
                for item in items: self.drag_start_positions[item] = item.pos()
                items_at_pos = self.items(event.scenePos())
                clicked_circle = None
                for item in items_at_pos:
                    if item.data(KEY_TYPE) == "CIRCLE": clicked_circle = item; break
                if clicked_circle:
                    self.current_id = clicked_circle.data(KEY_ID);
                    self.refresh_circle_colors()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.mode == 'DRAWING_RECT' and self.temp_rect_item:
            current_point = event.scenePos()
            new_rect = QRectF(self.start_point, current_point).normalized()
            self.temp_rect_item.setRect(new_rect)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.mode == 'DRAWING_RECT' and event.button() == Qt.LeftButton and self.temp_rect_item:
            # 1. Get the geometry of the drawn dashed rectangle
            geo = self.temp_rect_item.rect()

            # Remove the temporary dashed item
            self.removeItem(self.temp_rect_item)
            self.temp_rect_item = None

            if geo.width() > 1 and geo.height() > 1:
                # --- FIX START ---
                # Instead of QGraphicsRectItem(geo), we create it at 0,0 with the correct size...
                final_item = QGraphicsRectItem(0, 0, geo.width(), geo.height())

                # ...and then Move the item itself to the coordinates.
                # This ensures item.pos() returns the real X/Y, not 0.0
                final_item.setPos(geo.x(), geo.y())
                # --- FIX END ---

                final_item.setPen(QPen(Qt.green, 2))
                final_item.setBrush(QBrush(QColor(0, 255, 0, 100)))
                final_item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

                final_item.setData(KEY_TYPE, "RECTANGLE")
                final_item.setData(KEY_ID, self.current_id)
                final_item.setData(KEY_RECT_ID, self.pending_rect_id)
                final_item.setData(KEY_RECT_TEXT, self.pending_rect_text)

                lbl = f"{self.current_id}.{self.pending_rect_id}.{self.pending_rect_text}"
                t = QGraphicsSimpleTextItem(lbl, parent=final_item)
                t.setBrush(QBrush(Qt.white))
                t.setFont(QFont("Arial", 10))

                # Position text relative to the new (0,0) based rect
                r = final_item.rect()
                t.setPos(r.x(), r.y() + r.height() + 5)
                t.setAcceptedMouseButtons(Qt.NoButton)

                self.addItem(final_item)
                self.undo_stack.push(AddItemsCommand(self, final_item, "Add Rectangle"))

            self.set_mode('SELECT')
            event.accept()

        elif self.mode == 'SELECT' and event.button() == Qt.LeftButton:
            super().mouseReleaseEvent(event)
            if self.drag_start_positions:
                move_data = {}
                moved = False
                for item, start_pos in self.drag_start_positions.items():
                    end_pos = item.pos()
                    if start_pos != end_pos: moved = True; move_data[item] = (start_pos, end_pos)
                if moved:
                    for item, (start, end) in move_data.items(): item.setPos(start)
                    self.undo_stack.push(MoveItemsCommand(self, move_data, "Mouse Drag"))
                self.drag_start_positions = {}
        else:
            super().mouseReleaseEvent(event)


# ==========================================
#              MAIN WINDOW
# ==========================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 800)
        self.setWindowTitle("Interactive Graphics Editor (Save/Load)")
        self.current_file_path = None  # State for file handling

        self.scene = EditorScene(0, 0, 1000, 800)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCentralWidget(self.view)

        self.help_window = HelpWindow()
        self.scene.helpRequested.connect(self.show_help_window)
        self.scene.toggleToolbarRequested.connect(self.toggle_align_toolbar)

        self.create_alignment_toolbar()
        self.create_actions()

    def create_actions(self):
        # File Menu Actions
        save_act = QAction("Save", self)
        save_act.setShortcut(QKeySequence.Save)  # Ctrl+S
        save_act.triggered.connect(self.save_file)
        self.addAction(save_act)

        save_as_act = QAction("Save As...", self)
        # Ctrl+Shift+S is standard for Save As
        save_as_act.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_act.triggered.connect(self.save_file_as)
        self.addAction(save_as_act)

        open_act = QAction("Open", self)
        open_act.setShortcut(QKeySequence.Open)  # Ctrl+O
        open_act.triggered.connect(self.open_file)
        self.addAction(open_act)

        # Undo/Redo
        undo_act = self.scene.undo_stack.createUndoAction(self, "Undo")
        undo_act.setShortcut(QKeySequence.Undo)
        self.addAction(undo_act)

        redo_act = self.scene.undo_stack.createRedoAction(self, "Redo")
        redo_act.setShortcut(QKeySequence.Redo)
        self.addAction(redo_act)

    def create_alignment_toolbar(self):
        self.align_toolbar = QToolBar("Alignment")
        self.addToolBar(Qt.TopToolBarArea, self.align_toolbar)
        self.align_toolbar.setHidden(True)

        act_left = QAction(create_icon("align_left"), "Left", self);
        act_left.triggered.connect(lambda: self.scene.align_items('left'))
        act_right = QAction(create_icon("align_right"), "Right", self);
        act_right.triggered.connect(lambda: self.scene.align_items('right'))
        act_top = QAction(create_icon("align_top"), "Top", self);
        act_top.triggered.connect(lambda: self.scene.align_items('top'))
        act_btm = QAction(create_icon("align_bottom"), "Bottom", self);
        act_btm.triggered.connect(lambda: self.scene.align_items('bottom'))
        act_d_h = QAction(create_icon("dist_horz"), "Dist H", self);
        act_d_h.triggered.connect(lambda: self.scene.distribute_items('horz'))
        act_d_v = QAction(create_icon("dist_vert"), "Dist V", self);
        act_d_v.triggered.connect(lambda: self.scene.distribute_items('vert'))

        self.align_toolbar.addAction(act_left);
        self.align_toolbar.addAction(act_right)
        self.align_toolbar.addAction(act_top);
        self.align_toolbar.addAction(act_btm)
        self.align_toolbar.addSeparator()
        self.align_toolbar.addAction(act_d_h);
        self.align_toolbar.addAction(act_d_v)

    def toggle_align_toolbar(self):
        self.align_toolbar.setVisible(not self.align_toolbar.isVisible())

    def show_help_window(self):
        self.help_window.show();
        self.help_window.raise_();
        self.help_window.activateWindow()

    # --- File IO Logic ---

    def save_file(self):
        if self.current_file_path:
            self._write_to_file(self.current_file_path)
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Scene", "", "JSON Files (*.json)")
        if file_path:
            self.current_file_path = file_path
            self._write_to_file(file_path)

    def _write_to_file(self, path):
        try:
            data = self.scene.serialize_scene()
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Saved to {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Scene", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                self.scene.deserialize_scene(data)
                self.current_file_path = file_path
                print(f"Loaded from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Load Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())