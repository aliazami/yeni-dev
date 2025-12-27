import sys
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
    """Handles Arrows, Dragging, Alignment, and Distribution"""

    def __init__(self, scene, move_data, description="Move Items"):
        # move_data is a dict: { item: (start_pos, end_pos) }
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
    def __init__(self, scene, new_bg_item, old_bg_item, description="Change Background"):
        super().__init__(description)
        self.scene = scene
        self.new_bg = new_bg_item
        self.old_bg = old_bg_item

    def redo(self):
        if self.old_bg and self.old_bg.scene() == self.scene:
            self.scene.removeItem(self.old_bg)

        if self.new_bg and self.new_bg.scene() != self.scene:
            self.scene.addItem(self.new_bg)
            # Update background reference in scene so other logic works
            self.scene.background_item = self.new_bg
            # Update scene rect if it's an image
            if isinstance(self.new_bg, QGraphicsPixmapItem):
                self.scene.setSceneRect(QRectF(self.new_bg.pixmap().rect()))

    def undo(self):
        if self.new_bg and self.new_bg.scene() == self.scene:
            self.scene.removeItem(self.new_bg)

        if self.old_bg and self.old_bg.scene() != self.scene:
            self.scene.addItem(self.old_bg)
            self.scene.background_item = self.old_bg
            # Restore rect logic?
            # Ideally we'd store the old SceneRect too, but for now assuming
            # if old was rect, standard size, if pixmap, pixmap size.
            if isinstance(self.old_bg, QGraphicsPixmapItem):
                self.scene.setSceneRect(QRectF(self.old_bg.pixmap().rect()))
            else:
                # Default size assumption (or store it in constructor)
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
            "<b>Ctrl+Z</b> : Undo<br>"
            "<b>Ctrl+Shift+Z</b> : Redo<br>"
            "<b>I</b> : Import Background Image<br>"
            "<b>A</b> : Add Circle<br>"
            "<b>R</b> : Add Rectangle<br>"
            "<b>F</b> : Add Label<br>"
            "<b>G</b> : Add Label 2<br>"
            "<b>1</b> : Toggle Alignment Toolbar<br>"
            "<b>H</b> : Show Help<br>"
            "<b>Arrows</b> : Move (Step=10)<br>"
            "<b>Shift+Arrows</b> : Move (Step=1)<br>"
            "<b>Del</b> : Delete Item"
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

        # --- UNDO STACK ---
        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(100)

        self.mode = 'SELECT'
        self.temp_rect_item = None
        self.start_point = None

        self.current_id = None
        self.pending_payload = ""
        self.pending_rect_id = None
        self.pending_rect_text = None

        # Dragging state
        self.drag_start_positions = {}

        # Background
        self.background_item = None
        # Init default background
        self.init_default_background(w, h)

    def init_default_background(self, w, h):
        """Creates the initial gray background directly."""
        rect = QGraphicsRectItem(0, 0, w, h)
        rect.setPen(QPen(Qt.NoPen))
        rect.setBrush(QBrush(QColor("#333")))
        rect.setZValue(-1000)
        self.addItem(rect)
        self.background_item = rect

    # --- Commands Logic ---

    def push_background_image(self, file_path):
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.warning(None, "Error", "Failed to load image.")
            return

        new_bg = QGraphicsPixmapItem(pixmap)
        new_bg.setZValue(-1000)
        new_bg.setAcceptedMouseButtons(Qt.NoButton)

        cmd = SetBackgroundCommand(self, new_bg, self.background_item, "Import Image")
        self.undo_stack.push(cmd)

    def calculate_move_command(self, items, dx, dy):
        """Prepares data for MoveItemsCommand based on simple delta."""
        move_data = {}
        for item in items:
            start_pos = item.pos()
            end_pos = QPointF(start_pos.x() + dx, start_pos.y() + dy)
            move_data[item] = (start_pos, end_pos)
        return move_data

    # --- Alignment Logic with Undo ---
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
                end_pos = QPointF(start_pos.x() + dx, start_pos.y() + dy)
                move_data[item] = (start_pos, end_pos)

        if move_data:
            self.undo_stack.push(MoveItemsCommand(self, move_data, f"Align {direction}"))

    def distribute_items(self, orientation):
        items = self.selectedItems()
        if len(items) < 3: return

        move_data = {}
        if orientation == 'horz':
            items.sort(key=lambda item: item.sceneBoundingRect().center().x())
            start = items[0].sceneBoundingRect().center().x()
            end = items[-1].sceneBoundingRect().center().x()
            step = (end - start) / (len(items) - 1)
            for i, item in enumerate(items):
                current_center = item.sceneBoundingRect().center().x()
                target_center = start + (i * step)
                dx = target_center - current_center
                if abs(dx) > 0.1:
                    start_pos = item.pos()
                    move_data[item] = (start_pos, QPointF(start_pos.x() + dx, start_pos.y()))

        elif orientation == 'vert':
            items.sort(key=lambda item: item.sceneBoundingRect().center().y())
            start = items[0].sceneBoundingRect().center().y()
            end = items[-1].sceneBoundingRect().center().y()
            step = (end - start) / (len(items) - 1)
            for i, item in enumerate(items):
                current_center = item.sceneBoundingRect().center().y()
                target_center = start + (i * step)
                dy = target_center - current_center
                if abs(dy) > 0.1:
                    start_pos = item.pos()
                    move_data[item] = (start_pos, QPointF(start_pos.x(), start_pos.y() + dy))

        if move_data:
            self.undo_stack.push(MoveItemsCommand(self, move_data, f"Distribute {orientation}"))

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

    # --- Key Events ---
    def keyPressEvent(self, event):
        # Tools and shortcuts that DON'T modify state directly
        if event.key() == Qt.Key_1:
            self.toggleToolbarRequested.emit(); event.accept()
        elif event.key() == Qt.Key_H:
            self.helpRequested.emit(); event.accept()

        # Undo/Redo are handled by MainWindow actions, but if we needed to manual:
        # if event.matches(QKeySequence.Undo): self.undo_stack.undo() ...

        # Image Import
        elif event.key() == Qt.Key_I:
            file_path, _ = QFileDialog.getOpenFileName(None, "Open Image", "", "Images (*.png *.jpg *.jpeg *.webp)")
            if file_path: self.push_background_image(file_path)
            event.accept()

        # Tools (Dialogs)
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

        # --- Deletion with Undo ---
        elif event.key() == Qt.Key_Delete:
            items = self.selectedItems()
            if items:
                # Check if deleting current circle
                for item in items:
                    if item.data(KEY_TYPE) == "CIRCLE" and item.data(KEY_ID) == self.current_id:
                        self.current_id = None
                self.undo_stack.push(RemoveItemsCommand(self, items))
                self.refresh_circle_colors()
            event.accept()

        elif event.key() == Qt.Key_Escape:
            if self.mode != 'SELECT':
                if self.temp_rect_item: self.removeItem(self.temp_rect_item); self.temp_rect_item = None
                self.set_mode('SELECT')
            else:
                self.clearSelection()

        # --- Arrow Movement with Undo ---
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

    # --- Mouse Events ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:

            # --- Drawing Logic (Standard) ---
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
                    ellipse.setPos(pos)
                    ellipse.setPen(QPen(Qt.black, 2))
                    ellipse.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
                    ellipse.setData(KEY_ID, self.pending_payload);
                    ellipse.setData(KEY_TYPE, "CIRCLE")

                    text = QGraphicsSimpleTextItem(self.pending_payload, parent=ellipse)
                    text.setFont(QFont("Arial", 12, QFont.Bold))
                    br = text.boundingRect()
                    text.setPos(-br.width() / 2, -br.height() / 2)
                    text.setAcceptedMouseButtons(Qt.NoButton)
                    new_item = ellipse
                    self.current_id = self.pending_payload

                elif self.mode == 'ADD_LABEL':
                    text = QGraphicsTextItem(self.pending_payload)
                    text.setDefaultTextColor(Qt.white);
                    text.setFont(QFont("Arial", 14))
                    text.setPos(pos)
                    text.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
                    text.setData(KEY_ID, self.pending_payload);
                    text.setData(KEY_TYPE, "LABEL")
                    new_item = text

                elif self.mode == 'ADD_LABEL2':
                    text = QGraphicsTextItem(self.pending_payload)
                    text.setDefaultTextColor(QColor("#00FFFF"));
                    text.setFont(QFont("Arial", 14, QFont.Bold))
                    text.setPos(pos)
                    text.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
                    text.setData(KEY_ID, self.pending_payload);
                    text.setData(KEY_TYPE, "LABEL2")
                    new_item = text

                # Push Undo Command
                if new_item:
                    self.undo_stack.push(AddItemsCommand(self, new_item, f"Add {self.mode}"))
                    self.refresh_circle_colors()
                    self.set_mode('SELECT')
                event.accept()

            # --- Select / Drag Start ---
            else:
                super().mousePressEvent(event)  # This selects items

                # Capture drag start positions of ALL selected items
                items = self.selectedItems()
                self.drag_start_positions = {}
                for item in items:
                    self.drag_start_positions[item] = item.pos()

                # Handle Click Selection Logic for Circles
                # (We do this after super() so selection is updated)
                items_at_pos = self.items(event.scenePos())
                clicked_circle = None
                for item in items_at_pos:
                    if item.data(KEY_TYPE) == "CIRCLE": clicked_circle = item; break
                if clicked_circle:
                    self.current_id = clicked_circle.data(KEY_ID)
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
            final_rect_geometry = self.temp_rect_item.rect()
            self.removeItem(self.temp_rect_item)
            self.temp_rect_item = None

            if final_rect_geometry.width() > 1 and final_rect_geometry.height() > 1:
                final_item = QGraphicsRectItem(final_rect_geometry)
                final_item.setPen(QPen(Qt.green, 2))
                final_item.setBrush(QBrush(QColor(0, 255, 0, 100)))
                final_item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
                final_item.setData(KEY_TYPE, "RECTANGLE")
                final_item.setData(KEY_ID, self.current_id)
                final_item.setData(KEY_RECT_ID, self.pending_rect_id)
                final_item.setData(KEY_RECT_TEXT, self.pending_rect_text)

                lbl = f"{self.current_id}.{self.pending_rect_id}.{self.pending_rect_text}"
                t = QGraphicsSimpleTextItem(lbl, parent=final_item)
                t.setBrush(QBrush(Qt.white));
                t.setFont(QFont("Arial", 10))
                r = final_item.rect()
                t.setPos(r.x(), r.y() + r.height() + 5)
                t.setAcceptedMouseButtons(Qt.NoButton)

                # Push Add Command
                self.undo_stack.push(AddItemsCommand(self, final_item, "Add Rectangle"))

            self.set_mode('SELECT')
            event.accept()

        elif self.mode == 'SELECT' and event.button() == Qt.LeftButton:
            # Handle Drag Finish
            super().mouseReleaseEvent(event)

            if self.drag_start_positions:
                move_data = {}
                moved = False

                for item, start_pos in self.drag_start_positions.items():
                    # Item might have been deselected during drag (rare but safe to check)
                    # or deleted, but item object still exists
                    end_pos = item.pos()
                    if start_pos != end_pos:
                        moved = True
                        move_data[item] = (start_pos, end_pos)

                if moved:
                    # IMPORTANT: The items are ALREADY at end_pos visually.
                    # We must move them BACK to start_pos before pushing the command,
                    # because pushing the command triggers 'redo', which moves them to end_pos.
                    # If we don't move them back, the stack logic is fine, but it's cleaner to reset.
                    for item, (start, end) in move_data.items():
                        item.setPos(start)

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
        self.setWindowTitle("Interactive Graphics Editor (Undo/Redo)")

        self.scene = EditorScene(0, 0, 1000, 800)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCentralWidget(self.view)

        self.help_window = HelpWindow()
        self.scene.helpRequested.connect(self.show_help_window)
        self.scene.toggleToolbarRequested.connect(self.toggle_align_toolbar)

        self.create_alignment_toolbar()
        self.create_undo_actions()

    def create_undo_actions(self):
        # Undo Action
        self.undo_action = self.scene.undo_stack.createUndoAction(self, "Undo")
        self.undo_action.setShortcuts(QKeySequence.Undo)
        self.addAction(self.undo_action)

        # Redo Action
        self.redo_action = self.scene.undo_stack.createRedoAction(self, "Redo")
        self.redo_action.setShortcuts(QKeySequence.Redo)
        self.addAction(self.redo_action)

    def create_alignment_toolbar(self):
        self.align_toolbar = QToolBar("Alignment")
        self.addToolBar(Qt.TopToolBarArea, self.align_toolbar)
        self.align_toolbar.setHidden(True)

        # We wrap lambda calls to use scene methods which now trigger commands
        act_left = QAction(create_icon("align_left"), "Left", self)
        act_left.triggered.connect(lambda: self.scene.align_items('left'))

        act_right = QAction(create_icon("align_right"), "Right", self)
        act_right.triggered.connect(lambda: self.scene.align_items('right'))

        act_top = QAction(create_icon("align_top"), "Top", self)
        act_top.triggered.connect(lambda: self.scene.align_items('top'))

        act_btm = QAction(create_icon("align_bottom"), "Bottom", self)
        act_btm.triggered.connect(lambda: self.scene.align_items('bottom'))

        act_d_h = QAction(create_icon("dist_horz"), "Dist H", self)
        act_d_h.triggered.connect(lambda: self.scene.distribute_items('horz'))

        act_d_v = QAction(create_icon("dist_vert"), "Dist V", self)
        act_d_v.triggered.connect(lambda: self.scene.distribute_items('vert'))

        self.align_toolbar.addAction(act_left)
        self.align_toolbar.addAction(act_right)
        self.align_toolbar.addAction(act_top)
        self.align_toolbar.addAction(act_btm)
        self.align_toolbar.addSeparator()
        self.align_toolbar.addAction(act_d_h)
        self.align_toolbar.addAction(act_d_v)

    def toggle_align_toolbar(self):
        self.align_toolbar.setVisible(not self.align_toolbar.isVisible())

    def show_help_window(self):
        self.help_window.show()
        self.help_window.raise_()
        self.help_window.activateWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())