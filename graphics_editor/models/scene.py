from PySide6.QtCore import Qt, QRectF, Signal, QPointF
from PySide6.QtGui import (QBrush, QPen, QColor, QCursor, QFont,
                           QPixmap, QUndoStack)
from PySide6.QtWidgets import (QGraphicsScene, QGraphicsRectItem,
                               QGraphicsEllipseItem, QGraphicsSimpleTextItem,
                               QGraphicsTextItem, QGraphicsItem, QGraphicsPixmapItem,
                               QInputDialog, QMessageBox, QFileDialog, QGraphicsView,
                               QDialog)
from models.serialization import SceneSerializer
from undo_commands import (AddItemsCommand, RemoveItemsCommand, 
                          MoveItemsCommand, SetBackgroundCommand)
from constants import (ALIGN_TOP, ALIGN_BOTTOM, ALIGN_LEFT, ALIGN_RIGHT,
                       MODE_SELECT, COLOR_BACKGROUND, DISTRIBUTE_HORIZONTAL, DISTRIBUTE_VERTICAL,
                       KEY_ID, KEY_TYPE, ITEM_TYPE_CIRCLE, ITEM_TYPE_LABEL, ITEM_TYPE_LABEL2,
                       ITEM_TYPE_RECTANGLE, KEY_RECT_ID, KEY_RECT_TEXT, COLOR_HIGHLIGHT,
                       MODE_ADD_CIRCLE, MODE_ADD_LABEL, MODE_ADD_LABEL2, MODE_DRAWING_RECT,
                       COLOR_LABEL2, COLOR_TRANSPARENT_GREEN, COLOR_TRANSPARENT_RED,
                       CIRCLE_RADIUS, FONT_ARIAL, FONT_SIZE_LARGE, FONT_SIZE_NORMAL, FONT_SIZE_SMALL)
from dialogs import RectInputDialog

class EditorScene(QGraphicsScene):
    helpRequested = Signal()
    toggleToolbarRequested = Signal()

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(100)

        self.mode = MODE_SELECT
        self.temp_rect_item = None
        self.start_point = None

        self.current_id = None
        self.pending_payload = ""
        self.pending_rect_id = None
        self.pending_rect_text = None
        self.drag_start_positions = {}

        # Background Management
        self.background_item = None
        self.background_path = None
        self.default_w = w
        self.default_h = h

        self.serializer = SceneSerializer(self)
        self.init_default_background()

    def init_default_background(self):
        if self.background_item:
            self.removeItem(self.background_item)
        rect = QGraphicsRectItem(0, 0, self.default_w, self.default_h)
        rect.setPen(QPen(Qt.NoPen))
        rect.setBrush(QBrush(QColor(COLOR_BACKGROUND)))
        rect.setZValue(-1000)
        self.addItem(rect)
        self.background_item = rect
        self.background_path = None
        self.setSceneRect(0, 0, self.default_w, self.default_h)

    # Background Logic
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
            if self.background_item: 
                self.removeItem(self.background_item)
            self.addItem(new_bg)
            self.background_item = new_bg
            self.background_path = file_path
            self.setSceneRect(QRectF(pixmap.rect()))

    def push_background_image(self, file_path):
        self.set_image_background(file_path, record_undo=True)

    # Item Management
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
        if direction == ALIGN_LEFT:
            target = min(item.sceneBoundingRect().left() for item in items)
        elif direction == ALIGN_RIGHT:
            target = max(item.sceneBoundingRect().right() for item in items)
        elif direction == ALIGN_TOP:
            target = min(item.sceneBoundingRect().top() for item in items)
        elif direction == ALIGN_BOTTOM:
            target = max(item.sceneBoundingRect().bottom() for item in items)

        move_data = {}
        for item in items:
            rect = item.sceneBoundingRect()
            start_pos = item.pos()
            dx, dy = 0, 0
            if direction == ALIGN_LEFT:
                dx = target - rect.left()
            elif direction == ALIGN_RIGHT:
                dx = target - rect.right()
            elif direction == ALIGN_TOP:
                dy = target - rect.top()
            elif direction == ALIGN_BOTTOM:
                dy = target - rect.bottom()
            if dx != 0 or dy != 0:
                move_data[item] = (start_pos, QPointF(start_pos.x() + dx, start_pos.y() + dy))
        if move_data: 
            self.undo_stack.push(MoveItemsCommand(self, move_data, f"Align {direction}"))

    def distribute_items(self, orientation):
        items = self.selectedItems()
        if len(items) < 3: return
        move_data = {}
        if orientation == DISTRIBUTE_HORIZONTAL:
            items.sort(key=lambda item: item.sceneBoundingRect().center().x())
            start = items[0].sceneBoundingRect().center().x()
            end = items[-1].sceneBoundingRect().center().x()
            step = (end - start) / (len(items) - 1)
            for i, item in enumerate(items):
                current_center = item.sceneBoundingRect().center().x()
                target_center = start + (i * step)
                dx = target_center - current_center
                if abs(dx) > 0.1: 
                    move_data[item] = (item.pos(), QPointF(item.pos().x() + dx, item.pos().y()))
        elif orientation == DISTRIBUTE_VERTICAL:
            items.sort(key=lambda item: item.sceneBoundingRect().center().y())
            start = items[0].sceneBoundingRect().center().y()
            end = items[-1].sceneBoundingRect().center().y()
            step = (end - start) / (len(items) - 1)
            for i, item in enumerate(items):
                current_center = item.sceneBoundingRect().center().y()
                target_center = start + (i * step)
                dy = target_center - current_center
                if abs(dy) > 0.1: 
                    move_data[item] = (item.pos(), QPointF(item.pos().x(), item.pos().y() + dy))
        if move_data: 
            self.undo_stack.push(MoveItemsCommand(self, move_data, f"Distribute {orientation}"))

    # ID Validation Helpers
    def circle_id_exists(self, target_id):
        for item in self.items():
            if item.data(KEY_TYPE) == ITEM_TYPE_CIRCLE and item.data(KEY_ID) == target_id: 
                return True
        return False

    def label_id_exists(self, full_label):
        for item in self.items():
            if item.data(KEY_TYPE) == ITEM_TYPE_LABEL and item.data(KEY_ID) == full_label: 
                return True
        return False

    def label2_id_exists(self, full_label):
        for item in self.items():
            if item.data(KEY_TYPE) == ITEM_TYPE_LABEL2 and item.data(KEY_ID) == full_label: 
                return True
        return False

    def rect_compound_id_exists(self, compound_id):
        for item in self.items():
            if item.data(KEY_TYPE) == ITEM_TYPE_RECTANGLE:
                existing = f"{item.data(KEY_ID)}.{item.data(KEY_RECT_ID)}.{item.data(KEY_RECT_TEXT)}"
                if existing == compound_id: 
                    return True
        return False

    def get_next_label_int(self):
        if not self.current_id: return 1
        max_val = 0
        prefix = f"{self.current_id}."
        for item in self.items():
            if item.data(KEY_TYPE) == ITEM_TYPE_LABEL:
                lbl = item.data(KEY_ID)
                if lbl.startswith(prefix):
                    try:
                        max_val = max(max_val, int(lbl.split('.')[1]))
                    except:
                        pass
        return max_val + 1

    def get_next_label2_int(self):
        if not self.current_id: return 1
        max_val = 0
        prefix = f"{self.current_id}."
        for item in self.items():
            if item.data(KEY_TYPE) == ITEM_TYPE_LABEL2:
                lbl = item.data(KEY_ID)
                if lbl.startswith(prefix) and lbl.endswith("**"):
                    try:
                        max_val = max(max_val, int(lbl.replace("**", "").split('.')[1]))
                    except:
                        pass
        return max_val + 1

    def refresh_circle_colors(self):
        for item in self.items():
            if item.data(KEY_TYPE) == ITEM_TYPE_CIRCLE:
                item_id = item.data(KEY_ID)
                if item_id == self.current_id:
                    item.setBrush(QBrush(QColor(COLOR_HIGHLIGHT)))
                    item.setPen(QPen(Qt.black, 2))
                else:
                    item.setBrush(QBrush(Qt.yellow))
                    item.setPen(QPen(Qt.black, 2))

    def set_mode(self, mode):
        self.mode = mode
        if not self.views(): return
        view = self.views()[0]
        if mode == MODE_SELECT:
            view.setDragMode(QGraphicsView.RubberBandDrag)
            view.setCursor(QCursor(Qt.ArrowCursor))
        else:
            view.setDragMode(QGraphicsView.NoDrag)
            view.setCursor(QCursor(Qt.CrossCursor))
            self.clearSelection()

    # Events
    def keyPressEvent(self, event):
        key = event.key()
        
        if key == Qt.Key_1:
            self.toggleToolbarRequested.emit()
            event.accept()
        elif key == Qt.Key_H:
            self.helpRequested.emit()
            event.accept()
        elif key == Qt.Key_I:
            file_path, _ = QFileDialog.getOpenFileName(None, "Open Image", "", "Images (*.png *.jpg *.jpeg *.webp)")
            if file_path: 
                self.push_background_image(file_path)
            event.accept()
        elif key == Qt.Key_R:
            self._handle_rectangle_key()
            event.accept()
        elif key == Qt.Key_A:
            self._handle_add_circle_key()
            event.accept()
        elif key == Qt.Key_F:
            self._handle_add_label_key()
            event.accept()
        elif key == Qt.Key_G:
            self._handle_add_label2_key()
            event.accept()
        elif key == Qt.Key_Delete:
            self._handle_delete_key()
            event.accept()
        elif key == Qt.Key_Escape:
            self._handle_escape_key()
            event.accept()
        elif key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            self._handle_arrow_key(event)
        else:
            super().keyPressEvent(event)

    def _handle_rectangle_key(self):
        if not self.current_id: 
            QMessageBox.warning(None, "Error", "No Circle Selected.")
            return
        dialog = RectInputDialog()
        if dialog.exec() == QDialog.Accepted:
            r_id, r_text = dialog.get_data()
            if not r_id.isdigit(): 
                QMessageBox.warning(None, "Error", "ID must be int.")
                return
            if not r_text: 
                QMessageBox.warning(None, "Error", "Text required.")
                return
            if self.rect_compound_id_exists(f"{self.current_id}.{r_id}.{r_text}"):
                QMessageBox.warning(None, "Error", "Exists!")
                return
            self.pending_rect_id = r_id
            self.pending_rect_text = r_text
            self.set_mode(MODE_DRAWING_RECT)

    def _handle_add_circle_key(self):
        text, ok = QInputDialog.getText(None, "Add Circle", "Enter Unique ID:")
        if ok and text:
            if self.circle_id_exists(text):
                QMessageBox.warning(None, "Error", "Exists!")
            else:
                self.pending_payload = text
                self.set_mode(MODE_ADD_CIRCLE)

    def _handle_add_label_key(self):
        if not self.current_id: 
            QMessageBox.warning(None, "Error", "No Circle Selected.")
            return
        default_int = self.get_next_label_int()
        val, ok = QInputDialog.getInt(None, "Add Label", f"Sequence:", value=default_int, minValue=1)
        if ok:
            full = f"{self.current_id}.{val}"
            if self.label_id_exists(full):
                QMessageBox.warning(None, "Error", "Exists!")
            else:
                self.pending_payload = full
                self.set_mode(MODE_ADD_LABEL)

    def _handle_add_label2_key(self):
        if not self.current_id: 
            QMessageBox.warning(None, "Error", "No Circle Selected.")
            return
        default_int = self.get_next_label2_int()
        val, ok = QInputDialog.getInt(None, "Add Label 2", f"Sequence:", value=default_int, minValue=1)
        if ok:
            full = f"{self.current_id}.{val}**"
            if self.label2_id_exists(full):
                QMessageBox.warning(None, "Error", "Exists!")
            else:
                self.pending_payload = full
                self.set_mode(MODE_ADD_LABEL2)

    def _handle_delete_key(self):
        items = self.selectedItems()
        if items:
            for item in items:
                if item.data(KEY_TYPE) == ITEM_TYPE_CIRCLE and item.data(KEY_ID) == self.current_id: 
                    self.current_id = None
            self.undo_stack.push(RemoveItemsCommand(self, items))
            self.refresh_circle_colors()

    def _handle_escape_key(self):
        if self.mode != MODE_SELECT:
            if self.temp_rect_item: 
                self.removeItem(self.temp_rect_item)
                self.temp_rect_item = None
            self.set_mode(MODE_SELECT)
        else:
            self.clearSelection()

    def _handle_arrow_key(self, event):
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.mode == MODE_DRAWING_RECT:
                self._handle_rect_mouse_press(event)
            elif self.mode in [MODE_ADD_CIRCLE, MODE_ADD_LABEL, MODE_ADD_LABEL2]:
                self._handle_add_item_mouse_press(event)
            else:
                super().mousePressEvent(event)
                items = self.selectedItems()
                self.drag_start_positions = {}
                for item in items: 
                    self.drag_start_positions[item] = item.pos()
                self._handle_circle_click(event)
        else:
            super().mousePressEvent(event)

    def _handle_rect_mouse_press(self, event):
        self.start_point = event.scenePos()
        self.temp_rect_item = QGraphicsRectItem()
        self.temp_rect_item.setPen(QPen(Qt.red, 2, Qt.DashLine))
        self.temp_rect_item.setBrush(QBrush(QColor(*COLOR_TRANSPARENT_RED)))
        self.addItem(self.temp_rect_item)
        self.temp_rect_item.setRect(QRectF(self.start_point, self.start_point))
        event.accept()

    def _handle_add_item_mouse_press(self, event):
        pos = event.scenePos()
        new_item = None
        
        if self.mode == MODE_ADD_CIRCLE:
            new_item = self._create_circle_item(pos, self.pending_payload)
            self.current_id = self.pending_payload
        elif self.mode == MODE_ADD_LABEL:
            new_item = self._create_label_item(pos, self.pending_payload)
        elif self.mode == MODE_ADD_LABEL2:
            new_item = self._create_label2_item(pos, self.pending_payload)
        
        if new_item:
            self.undo_stack.push(AddItemsCommand(self, new_item, f"Add {self.mode}"))
            self.refresh_circle_colors()
            self.set_mode(MODE_SELECT)
        event.accept()

    def _handle_circle_click(self, event):
        items_at_pos = self.items(event.scenePos())
        clicked_circle = None
        for item in items_at_pos:
            if item.data(KEY_TYPE) == ITEM_TYPE_CIRCLE: 
                clicked_circle = item
                break
        if clicked_circle:
            self.current_id = clicked_circle.data(KEY_ID)
            self.refresh_circle_colors()

    def _create_circle_item(self, pos, text):
        ellipse = QGraphicsEllipseItem(-CIRCLE_RADIUS, -CIRCLE_RADIUS, 
                                       CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2)
        ellipse.setPos(pos)
        ellipse.setPen(QPen(Qt.black, 2))
        ellipse.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        ellipse.setData(KEY_ID, text)
        ellipse.setData(KEY_TYPE, ITEM_TYPE_CIRCLE)
        
        t = QGraphicsSimpleTextItem(text, parent=ellipse)
        t.setFont(QFont(FONT_ARIAL, FONT_SIZE_NORMAL, QFont.Bold))
        br = t.boundingRect()
        t.setPos(-br.width() / 2, -br.height() / 2)
        t.setAcceptedMouseButtons(Qt.NoButton)
        
        return ellipse

    def _create_label_item(self, pos, text):
        t = QGraphicsTextItem(text)
        t.setDefaultTextColor(Qt.white)
        t.setFont(QFont(FONT_ARIAL, FONT_SIZE_LARGE))
        t.setPos(pos)
        t.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        t.setData(KEY_ID, text)
        t.setData(KEY_TYPE, ITEM_TYPE_LABEL)
        return t

    def _create_label2_item(self, pos, text):
        t = QGraphicsTextItem(text)
        t.setDefaultTextColor(QColor(COLOR_LABEL2))
        t.setFont(QFont(FONT_ARIAL, FONT_SIZE_LARGE, QFont.Bold))
        t.setPos(pos)
        t.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        t.setData(KEY_ID, text)
        t.setData(KEY_TYPE, ITEM_TYPE_LABEL2)
        return t

    def mouseMoveEvent(self, event):
        if self.mode == MODE_DRAWING_RECT and self.temp_rect_item:
            current_point = event.scenePos()
            new_rect = QRectF(self.start_point, current_point).normalized()
            self.temp_rect_item.setRect(new_rect)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.mode == MODE_DRAWING_RECT and event.button() == Qt.LeftButton and self.temp_rect_item:
            self._finalize_rectangle()
            event.accept()
        elif self.mode == MODE_SELECT and event.button() == Qt.LeftButton:
            super().mouseReleaseEvent(event)
            self._finalize_drag()
        else:
            super().mouseReleaseEvent(event)

    def _finalize_rectangle(self):
        geo = self.temp_rect_item.rect()
        self.removeItem(self.temp_rect_item)
        self.temp_rect_item = None

        if geo.width() > 1 and geo.height() > 1:
            final_item = QGraphicsRectItem(0, 0, geo.width(), geo.height())
            final_item.setPos(geo.x(), geo.y())
            final_item.setPen(QPen(Qt.green, 2))
            final_item.setBrush(QBrush(QColor(*COLOR_TRANSPARENT_GREEN)))
            final_item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

            final_item.setData(KEY_TYPE, ITEM_TYPE_RECTANGLE)
            final_item.setData(KEY_ID, self.current_id)
            final_item.setData(KEY_RECT_ID, self.pending_rect_id)
            final_item.setData(KEY_RECT_TEXT, self.pending_rect_text)

            lbl = f"{self.current_id}.{self.pending_rect_id}.{self.pending_rect_text}"
            t = QGraphicsSimpleTextItem(lbl, parent=final_item)
            t.setBrush(QBrush(Qt.white))
            t.setFont(QFont(FONT_ARIAL, FONT_SIZE_SMALL))

            r = final_item.rect()
            t.setPos(r.x(), r.y() + r.height() + 5)
            t.setAcceptedMouseButtons(Qt.NoButton)

            self.addItem(final_item)
            self.undo_stack.push(AddItemsCommand(self, final_item, "Add Rectangle"))

        self.set_mode(MODE_SELECT)

    def _finalize_drag(self):
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
                self.undo_stack.push(MoveItemsCommand(self, move_data, "Mouse Drag"))
            self.drag_start_positions = {}