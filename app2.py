import sys
from PySide6.QtCore import Qt, QRectF, Signal, QPointF
from PySide6.QtGui import (QBrush, QPen, QColor, QPainter, QCursor, QFont,
                           QAction, QIcon, QPixmap)
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                               QGraphicsScene, QGraphicsRectItem,
                               QGraphicsEllipseItem, QGraphicsSimpleTextItem,
                               QGraphicsTextItem, QGraphicsItem, QGraphicsPixmapItem,
                               QInputDialog, QWidget, QVBoxLayout, QLabel,
                               QMessageBox, QToolBar, QStyle, QDialog,
                               QFormLayout, QLineEdit, QDialogButtonBox,
                               QFileDialog)  # Added QFileDialog

# --- Constants for Item Data Keys ---
KEY_ID = 0
KEY_TYPE = 1
KEY_RECT_ID = 2
KEY_RECT_TEXT = 3


# --- Helper to Create Icons (Unchanged) ---
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


# --- Custom Dialog for Rectangle Inputs (Unchanged) ---
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


# --- Help Window ---
class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help")
        self.resize(300, 300)
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        help_text = (
            "<b>COMMANDS:</b><br>"
            "<b>I</b> : Import Background Image<br>"
            "<b>A</b> : Add Circle (Set Current ID)<br>"
            "<b>R</b> : Add Rectangle (Linked to Current ID)<br>"
            "<b>F</b> : Add Label (Linked to Current ID)<br>"
            "<b>G</b> : Add Label 2 (Linked to Current ID)<br>"
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


# --- The Scene ---
class EditorScene(QGraphicsScene):
    helpRequested = Signal()
    toggleToolbarRequested = Signal()

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)
        self.mode = 'SELECT'
        self.temp_rect_item = None
        self.start_point = None

        self.current_id = None
        self.pending_payload = ""
        self.pending_rect_id = None
        self.pending_rect_text = None

        # Track background item
        self.background_item = None

        # Create initial default background (Gray Rect)
        self.set_default_background(w, h)

    def set_default_background(self, w, h):
        """Sets the initial gray background."""
        if self.background_item:
            self.removeItem(self.background_item)

        # Add gray rect
        rect = QGraphicsRectItem(0, 0, w, h)
        rect.setPen(QPen(Qt.NoPen))
        rect.setBrush(QBrush(QColor("#333")))
        rect.setZValue(-1000)  # Ensure it is behind everything
        self.addItem(rect)
        self.background_item = rect
        self.setSceneRect(0, 0, w, h)

    def set_image_background(self, file_path):
        """Loads and sets the image background."""
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.warning(None, "Error", "Failed to load image.")
            return

        # Remove old background
        if self.background_item:
            self.removeItem(self.background_item)

        # Create new Pixmap item
        pix_item = QGraphicsPixmapItem(pixmap)
        pix_item.setZValue(-1000)  # Keep it at the bottom
        pix_item.setPos(0, 0)

        # Requirement 6: No interactions
        pix_item.setAcceptedMouseButtons(Qt.NoButton)

        self.addItem(pix_item)
        self.background_item = pix_item

        # Requirement 4 & 8: Update Scene Rect to match Image size
        # This forces scrollbars to appear if image > view
        self.setSceneRect(QRectF(pixmap.rect()))

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
                stored_circle_id = item.data(KEY_ID)
                stored_rect_id = item.data(KEY_RECT_ID)
                stored_text = item.data(KEY_RECT_TEXT)
                existing_compound = f"{stored_circle_id}.{stored_rect_id}.{stored_text}"
                if existing_compound == compound_id: return True
        return False

    def get_next_label_int(self):
        if not self.current_id: return 1
        max_val = 0
        prefix = f"{self.current_id}."
        for item in self.items():
            if item.data(KEY_TYPE) == "LABEL":
                lbl_text = item.data(KEY_ID)
                if lbl_text.startswith(prefix):
                    try:
                        suffix = int(lbl_text.split('.')[1])
                        if suffix > max_val: max_val = suffix
                    except ValueError:
                        pass
        return max_val + 1

    def get_next_label2_int(self):
        if not self.current_id: return 1
        max_val = 0
        prefix = f"{self.current_id}."
        for item in self.items():
            if item.data(KEY_TYPE) == "LABEL2":
                lbl_text = item.data(KEY_ID)
                if lbl_text.startswith(prefix) and lbl_text.endswith("**"):
                    try:
                        clean_text = lbl_text.replace("**", "")
                        suffix = int(clean_text.split('.')[1])
                        if suffix > max_val: max_val = suffix
                    except ValueError:
                        pass
        return max_val + 1

    def refresh_circle_colors(self):
        for item in self.items():
            if item.data(KEY_TYPE) == "CIRCLE":
                item_id = item.data(KEY_ID)
                if item_id == self.current_id:
                    item.setBrush(QBrush(QColor("#4488FF")))
                    item.setPen(QPen(Qt.black, 2))
                else:
                    item.setBrush(QBrush(Qt.yellow))
                    item.setPen(QPen(Qt.black, 2))

    def set_mode(self, mode):
        self.mode = mode
        if not self.views(): return
        view = self.views()[0]
        if mode == 'SELECT':
            view.setDragMode(QGraphicsView.RubberBandDrag)
            view.setCursor(QCursor(Qt.ArrowCursor))
        else:
            view.setDragMode(QGraphicsView.NoDrag)
            view.setCursor(QCursor(Qt.CrossCursor))
            self.clearSelection()

    # --- Alignment Logic (Unchanged) ---
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
        for item in items:
            rect = item.sceneBoundingRect()
            if direction == 'left':
                item.moveBy(target - rect.left(), 0)
            elif direction == 'right':
                item.moveBy(target - rect.right(), 0)
            elif direction == 'top':
                item.moveBy(0, target - rect.top())
            elif direction == 'bottom':
                item.moveBy(0, target - rect.bottom())

    def distribute_items(self, orientation):
        items = self.selectedItems()
        if len(items) < 3: return
        if orientation == 'horz':
            items.sort(key=lambda item: item.sceneBoundingRect().center().x())
            start = items[0].sceneBoundingRect().center().x();
            end = items[-1].sceneBoundingRect().center().x()
            step = (end - start) / (len(items) - 1)
            for i, item in enumerate(items):
                current_center = item.sceneBoundingRect().center().x();
                target_center = start + (i * step)
                item.moveBy(target_center - current_center, 0)
        elif orientation == 'vert':
            items.sort(key=lambda item: item.sceneBoundingRect().center().y())
            start = items[0].sceneBoundingRect().center().y();
            end = items[-1].sceneBoundingRect().center().y()
            step = (end - start) / (len(items) - 1)
            for i, item in enumerate(items):
                current_center = item.sceneBoundingRect().center().y();
                target_center = start + (i * step)
                item.moveBy(0, target_center - current_center)

    # --- Event Handling ---
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_1:
            self.toggleToolbarRequested.emit()
            event.accept()

        elif event.key() == Qt.Key_H:
            self.helpRequested.emit()
            event.accept()

        # --- I: Import Background ---
        elif event.key() == Qt.Key_I:
            file_path, _ = QFileDialog.getOpenFileName(None, "Open Image", "", "Images (*.png *.jpg *.jpeg *.webp)")
            if file_path:
                self.set_image_background(file_path)
            event.accept()

        elif event.key() == Qt.Key_R:
            if not self.current_id:
                QMessageBox.warning(None, "Error", "No Circle Selected.")
                event.accept();
                return
            dialog = RectInputDialog()
            if dialog.exec() == QDialog.Accepted:
                r_id, r_text = dialog.get_data()
                if not r_id.isdigit():
                    QMessageBox.warning(None, "Error", "ID must be int.");
                    event.accept();
                    return
                if not r_text:
                    QMessageBox.warning(None, "Error", "Text required.");
                    event.accept();
                    return
                compound_id = f"{self.current_id}.{r_id}.{r_text}"
                if self.rect_compound_id_exists(compound_id):
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
            val, ok = QInputDialog.getInt(None, "Add Label", f"ID: {self.current_id}\nSequence:", value=default_int,
                                          minValue=1)
            if ok:
                full_label = f"{self.current_id}.{val}"
                if self.label_id_exists(full_label):
                    QMessageBox.warning(None, "Error", "Exists!")
                else:
                    self.pending_payload = full_label; self.set_mode('ADD_LABEL')
            event.accept()

        elif event.key() == Qt.Key_G:
            if not self.current_id: QMessageBox.warning(None, "Error", "No Circle Selected."); event.accept(); return
            default_int = self.get_next_label2_int()
            val, ok = QInputDialog.getInt(None, "Add Label 2", f"ID: {self.current_id}\nSequence:", value=default_int,
                                          minValue=1)
            if ok:
                full_label = f"{self.current_id}.{val}**"
                if self.label2_id_exists(full_label):
                    QMessageBox.warning(None, "Error", "Exists!")
                else:
                    self.pending_payload = full_label; self.set_mode('ADD_LABEL2')
            event.accept()

        elif event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                if item.data(KEY_TYPE) == "CIRCLE" and item.data(KEY_ID) == self.current_id:
                    self.current_id = None
                self.removeItem(item)
            self.refresh_circle_colors()

        elif event.key() == Qt.Key_Escape:
            if self.mode != 'SELECT':
                if self.temp_rect_item: self.removeItem(self.temp_rect_item); self.temp_rect_item = None
                self.set_mode('SELECT')
            else:
                self.clearSelection()

        elif event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            dx, dy = 0, 0
            if event.modifiers() & Qt.ShiftModifier:
                step = 1
            else:
                step = 10
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
                for item in items: item.moveBy(dx, dy)
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

            elif self.mode == 'ADD_CIRCLE':
                pos = event.scenePos()
                radius = 25
                ellipse = QGraphicsEllipseItem(-radius, -radius, radius * 2, radius * 2)
                ellipse.setPos(pos)
                ellipse.setPen(QPen(Qt.black, 2))
                ellipse.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
                ellipse.setData(KEY_ID, self.pending_payload)
                ellipse.setData(KEY_TYPE, "CIRCLE")

                text_item = QGraphicsSimpleTextItem(self.pending_payload, parent=ellipse)
                font = QFont("Arial", 12, QFont.Bold)
                text_item.setFont(font)
                br = text_item.boundingRect()
                text_item.setPos(-br.width() / 2, -br.height() / 2)
                text_item.setAcceptedMouseButtons(Qt.NoButton)

                self.addItem(ellipse)
                self.current_id = self.pending_payload
                self.refresh_circle_colors()
                self.set_mode('SELECT')
                event.accept()

            elif self.mode == 'ADD_LABEL':
                pos = event.scenePos()
                text_item = QGraphicsTextItem(self.pending_payload)
                text_item.setDefaultTextColor(Qt.white)
                text_item.setFont(QFont("Arial", 14))
                text_item.setPos(pos)
                text_item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
                text_item.setData(KEY_ID, self.pending_payload)
                text_item.setData(KEY_TYPE, "LABEL")
                self.addItem(text_item)
                self.set_mode('SELECT')
                event.accept()

            elif self.mode == 'ADD_LABEL2':
                pos = event.scenePos()
                text_item = QGraphicsTextItem(self.pending_payload)
                text_item.setDefaultTextColor(QColor("#00FFFF"))
                text_item.setFont(QFont("Arial", 14, QFont.Bold))
                text_item.setPos(pos)
                text_item.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
                text_item.setData(KEY_ID, self.pending_payload)
                text_item.setData(KEY_TYPE, "LABEL2")
                self.addItem(text_item)
                self.set_mode('SELECT')
                event.accept()

            else:
                items_at_pos = self.items(event.scenePos())
                clicked_circle = None
                for item in items_at_pos:
                    if item.data(KEY_TYPE) == "CIRCLE":
                        clicked_circle = item
                        break
                if clicked_circle:
                    self.current_id = clicked_circle.data(KEY_ID)
                    self.refresh_circle_colors()
                super().mousePressEvent(event)
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

                label_text = f"{self.current_id}.{self.pending_rect_id}.{self.pending_rect_text}"
                text_item = QGraphicsSimpleTextItem(label_text, parent=final_item)
                text_item.setBrush(QBrush(Qt.white))
                text_item.setFont(QFont("Arial", 10))

                rect = final_item.rect()
                text_item.setPos(rect.x(), rect.y() + rect.height() + 5)
                text_item.setAcceptedMouseButtons(Qt.NoButton)

                self.addItem(final_item)
            self.set_mode('SELECT')
            event.accept()
        else:
            super().mouseReleaseEvent(event)


# --- Main Window (Unchanged) ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 800)
        self.setWindowTitle("Interactive Graphics Editor")

        # Scene init handles default background now
        self.scene = EditorScene(0, 0, 1000, 800)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCentralWidget(self.view)

        self.help_window = HelpWindow()
        self.scene.helpRequested.connect(self.show_help_window)
        self.scene.toggleToolbarRequested.connect(self.toggle_align_toolbar)

        self.create_alignment_toolbar()

    def create_alignment_toolbar(self):
        self.align_toolbar = QToolBar("Alignment")
        self.addToolBar(Qt.TopToolBarArea, self.align_toolbar)
        self.align_toolbar.setHidden(True)

        act_align_left = QAction(create_icon("align_left"), "Align Left", self)
        act_align_left.triggered.connect(lambda: self.scene.align_items('left'))
        act_align_right = QAction(create_icon("align_right"), "Align Right", self)
        act_align_right.triggered.connect(lambda: self.scene.align_items('right'))
        act_align_top = QAction(create_icon("align_top"), "Align Top", self)
        act_align_top.triggered.connect(lambda: self.scene.align_items('top'))
        act_align_bottom = QAction(create_icon("align_bottom"), "Align Bottom", self)
        act_align_bottom.triggered.connect(lambda: self.scene.align_items('bottom'))
        act_dist_horz = QAction(create_icon("dist_horz"), "Distribute Horizontally", self)
        act_dist_horz.triggered.connect(lambda: self.scene.distribute_items('horz'))
        act_dist_vert = QAction(create_icon("dist_vert"), "Distribute Vertically", self)
        act_dist_vert.triggered.connect(lambda: self.scene.distribute_items('vert'))

        self.align_toolbar.addAction(act_align_left)
        self.align_toolbar.addAction(act_align_right)
        self.align_toolbar.addAction(act_align_top)
        self.align_toolbar.addAction(act_align_bottom)
        self.align_toolbar.addSeparator()
        self.align_toolbar.addAction(act_dist_horz)
        self.align_toolbar.addAction(act_dist_vert)

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