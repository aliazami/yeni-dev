# ui/label_item.py

from PySide6.QtCore import Qt, Signal, QRect, QObject, QRectF, QPointF
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
)
from PySide6.QtGui import QPen, QBrush, QColor, QFont, QPainter
from app.core.models import ActionItemProps, CORRECTION, GAP, ACTION, ACTION_SIZE


class ActionItem(QObject, QGraphicsEllipseItem):
    deleteRequest = Signal(ActionItemProps)

    def __init__(self, props: ActionItemProps):
        QObject.__init__(self)
        rect = QRect(0, 0, ACTION_SIZE, ACTION_SIZE)
        QGraphicsEllipseItem.__init__(self, rect)

        props.action_object = self
        self.setPos(int(props.x), int(props.y))
        self.setData(Qt.ItemDataRole.UserRole, props)

        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsEllipseItem.GraphicsItemFlag.ItemIsFocusable, True)

        # 2. Border (Optional - remove if you want CSS border: none)
        self.setPen(Qt.PenStyle.NoPen)

        # 3. Font settings
        self.font = QFont("Arial", 10)
        self.font.setBold(True)
        self.update_props()

    def update_props(self):
        my_props: ActionItemProps = self.data(Qt.ItemDataRole.UserRole)
        # Pre-calculate colors to keep the paint method fast
        bg_color = QColor("red") if my_props.selected else QColor("blue")
        self.setBrush(QBrush(bg_color))

        # Schedule the repaint
        self.update()

    def paint(self, painter, option, widget=None):
        # First, let the standard paint method draw the ellipse/background
        super().paint(painter, option, widget)

        props: ActionItemProps = self.data(Qt.ItemDataRole.UserRole)
        painter.setFont(self.font)
        painter.setPen(QColor("white"))

        # This one line handles the CSS flex centering logic:
        # It draws text inside the ellipse's rectangle, aligned to center.
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, props.tag)

    def focusInEvent(self, event):
        print("focusInEvent")
        # self.set_selected(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        print("focusOutEvent")
        # self.set_selected(False)
        super().focusOutEvent(event)

    def keyPressEvent(self, event: QKeyEvent):
        dx, dy = 0, 0

        if event.key() == Qt.Key.Key_Left:
            dx = -1
        elif event.key() == Qt.Key.Key_Right:
            dx = 1
        elif event.key() == Qt.Key.Key_Up:
            dy = -1
        elif event.key() == Qt.Key.Key_Down:
            dy = 1
        elif event.key() == Qt.Key.Key_Delete:
            scene = self.scene()
            if scene:
                self.deleteRequest.emit(self.data(Qt.ItemDataRole.UserRole))
                scene.removeItem(self)
            return

        if dx or dy:
            pos = self.pos()
            self.setPos(int(pos.x() + dx), int(pos.y() + dy))
            return

        super().keyPressEvent(event)

    def set_selected(self, selected: bool):
        props: ActionItemProps = self.data(Qt.ItemDataRole.UserRole)
        if props.selected == selected:
            return 
        props.selected = selected
        self.update_props()

    def set_selected_by_rect(self, rect: QRectF):
        props: ActionItemProps = self.data(Qt.ItemDataRole.UserRole)

        if rect.contains(QPointF(props.x, props.y)):
            self.set_selected(True)


    def get_selected(self):
        props: ActionItemProps = self.data(Qt.ItemDataRole.UserRole)
        return props.selected
