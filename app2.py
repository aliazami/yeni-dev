import sys
from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QBrush, QPen, QColor, QPainter, QCursor, QFont
from PySide6.QtWidgets import (QApplication, QMainWindow, QGraphicsView,
                               QGraphicsScene, QGraphicsRectItem,
                               QGraphicsEllipseItem, QGraphicsSimpleTextItem,
                               QGraphicsTextItem, QGraphicsItem,
                               QInputDialog, QWidget, QVBoxLayout, QLabel, QMessageBox)

# --- Constants for Item Data Keys ---
KEY_ID = 0  # Stores the ID string (e.g., "1" or "1.1")
KEY_TYPE = 1  # Stores type string ("CIRCLE" or "LABEL")


# --- 1. Help Window (Unchanged) ---
class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help")
        self.resize(220, 180)
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        help_text = (
            "<b>COMMANDS:</b><br><br>"
            "<b>R</b> : Draw Rectangle<br>"
            "<b>A</b> : Add Circle (Set Current ID)<br>"
            "<b>F</b> : Add Label (Child of Current ID)<br>"
            "<b>H</b> : Show Help<br>"
            "<b>Click Circle</b> : Select ID<br>"
            "<b>Arrows</b> : Move Item<br>"
            "<b>Del</b> : Delete Item<br>"
            "<b>Esc</b> : Cancel / Deselect"
        )
        label = QLabel(help_text)
        label.setTextFormat(Qt.RichText)
        layout.addWidget(label)
        self.setLayout(layout)


# --- 2. The Scene ---
class EditorScene(QGraphicsScene):
    helpRequested = Signal()

    def __init__(self, x, y, w, h, parent=None):
        super().__init__(x, y, w, h, parent)

        self.mode = 'SELECT'
        self.temp_rect_item = None
        self.start_point = None

        self.current_id = None
        self.pending_payload = ""

        # --- Helpers ---

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

    def refresh_circle_colors(self):
        # We iterate through all items and update their brush based on current_id
        for item in self.items():
            if item.data(KEY_TYPE) == "CIRCLE":
                item_id = item.data(KEY_ID)
                if item_id == self.current_id:
                    item.setBrush(QBrush(QColor("#4488FF")))  # Blue for Active
                    item.setPen(QPen(Qt.black, 2))  # Ensure pen is visible
                else:
                    item.setBrush(QBrush(Qt.yellow))  # Yellow for Inactive
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

    # --- Event Handling ---
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_H:
            self.helpRequested.emit()
            event.accept()

        elif event.key() == Qt.Key_R:
            if self.mode != 'DRAWING_RECT': self.set_mode('DRAWING_RECT')
            event.accept()

        elif event.key() == Qt.Key_A:
            text, ok = QInputDialog.getText(None, "Add Circle", "Enter Unique ID (e.g. '1'):")
            if ok and text:
                if self.circle_id_exists(text):
                    QMessageBox.warning(None, "Error", f"Circle ID '{text}' already exists!")
                else:
                    self.pending_payload = text
                    self.set_mode('ADD_CIRCLE')
            event.accept()

        elif event.key() == Qt.Key_F:
            if not self.current_id:
                QMessageBox.warning(None, "Error", "No Circle Selected (No Current ID).")
                event.accept()
                return

            default_int = self.get_next_label_int()
            val, ok = QInputDialog.getInt(None, "Add Label",
                                          f"Current ID is {self.current_id}.\nEnter sequence number:",
                                          value=default_int, minValue=1)
            if ok:
                full_label = f"{self.current_id}.{val}"
                if self.label_id_exists(full_label):
                    QMessageBox.warning(None, "Error", f"Label '{full_label}' already exists!")
                else:
                    self.pending_payload = full_label
                    self.set_mode('ADD_LABEL')
            event.accept()

        elif event.key() == Qt.Key_Delete:
            for item in self.selectedItems():
                if item.data(KEY_TYPE) == "CIRCLE" and item.data(KEY_ID) == self.current_id:
                    self.current_id = None
                self.removeItem(item)
            self.refresh_circle_colors()

        elif event.key() == Qt.Key_Escape:
            if self.mode != 'SELECT':
                if self.temp_rect_item:
                    self.removeItem(self.temp_rect_item)
                    self.temp_rect_item = None
                self.set_mode('SELECT')
            else:
                self.clearSelection()

        elif event.key() in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            dx, dy = 0, 0
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

            # --- 1. Mode: Drawing Rectangle ---
            if self.mode == 'DRAWING_RECT':
                self.start_point = event.scenePos()
                self.temp_rect_item = QGraphicsRectItem()
                self.temp_rect_item.setPen(QPen(Qt.red, 2, Qt.DashLine))
                self.temp_rect_item.setBrush(QBrush(QColor(255, 0, 0, 50)))
                self.addItem(self.temp_rect_item)
                self.temp_rect_item.setRect(QRectF(self.start_point, self.start_point))
                event.accept()

            # --- 2. Mode: Add Circle ---
            elif self.mode == 'ADD_CIRCLE':
                pos = event.scenePos()
                radius = 25

                # Create the Circle
                ellipse = QGraphicsEllipseItem(-radius, -radius, radius * 2, radius * 2)
                ellipse.setPos(pos)
                ellipse.setPen(QPen(Qt.black, 2))
                ellipse.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

                # Metadata
                ellipse.setData(KEY_ID, self.pending_payload)
                ellipse.setData(KEY_TYPE, "CIRCLE")

                # Create the Text
                text_item = QGraphicsSimpleTextItem(self.pending_payload, parent=ellipse)
                font = QFont("Arial", 12, QFont.Bold)
                text_item.setFont(font)
                br = text_item.boundingRect()
                text_item.setPos(-br.width() / 2, -br.height() / 2)

                # !!! CRITICAL FIX: Make text transparent to mouse clicks !!!
                # This ensures the click passes through the text to the Circle
                text_item.setAcceptedMouseButtons(Qt.NoButton)

                self.addItem(ellipse)

                # Logic
                self.current_id = self.pending_payload
                self.refresh_circle_colors()

                self.set_mode('SELECT')
                event.accept()

            # --- 3. Mode: Add Label ---
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

            # --- 4. Mode: Select (Default) ---
            else:
                # Use scenePos to find items. The top item is first.
                items_at_pos = self.items(event.scenePos())

                clicked_circle = None

                # Find if we clicked a circle
                for item in items_at_pos:
                    if item.data(KEY_TYPE) == "CIRCLE":
                        clicked_circle = item
                        break

                # If we found a circle, update logic BEFORE calling super
                if clicked_circle:
                    self.current_id = clicked_circle.data(KEY_ID)
                    self.refresh_circle_colors()

                # Pass to base class to handle actual Selection/Dragging
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
                self.addItem(final_item)

            self.set_mode('SELECT')
            event.accept()
        else:
            super().mouseReleaseEvent(event)


# --- 3. The Main Window ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 800)
        self.setWindowTitle("Interactive Graphics Editor")

        self.scene = EditorScene(0, 0, 1000, 800)
        self.scene.addRect(0, 0, 1000, 800, QPen(Qt.NoPen), QBrush(QColor("#333"))).setZValue(-100)

        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCentralWidget(self.view)

        self.help_window = HelpWindow()
        self.scene.helpRequested.connect(self.show_help_window)

    def show_help_window(self):
        self.help_window.show()
        self.help_window.raise_()
        self.help_window.activateWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())