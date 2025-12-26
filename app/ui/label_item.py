# ui/label_item.py

from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QKeyEvent, QFont, QColor
from PySide6.QtWidgets import (
    QGraphicsTextItem,
)
from app.core.models import LabelItemProps, CORRECTION, GAP, ACTION


class LabelItem(QGraphicsTextItem):
    focusInRequest = Signal(LabelItemProps)
    focusOutRequest = Signal()
    deleteRequest = Signal(LabelItemProps)

    def __init__(self, props: LabelItemProps):
        props.label_object = self

        if props.role == GAP:
            label = f"{props.tag}.{props.index}.{props.place_holder}"
        elif props.role == CORRECTION:
            label = f"{props.tag}.{props.index}.{props.place_holder}**"
        else:
            label = ""

        super().__init__(label)
        self.setPos(int(props.x), int(props.y))
        self.setFont(QFont("Arial", props.font))
        the_color = QColor(props.color)
        self.setDefaultTextColor(the_color)
        self.setProperty("props", props)

        self.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsFocusable, True)

    def focusInEvent(self, event):
        self.set_selected(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.set_selected(False)
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
                self.deleteRequest.emit(self.property("props"))
                scene.removeItem(self)
            return

        if dx or dy:
            pos = self.pos()
            self.setPos(int(pos.x() + dx), int(pos.y() + dy))
            return

        super().keyPressEvent(event)

    def set_selected(self, selected: bool):
        props: LabelItemProps = self.property("props")
        if props.selected == selected:
            return 
        props.selected = selected
        color = Qt.GlobalColor.red if selected else props.color
        self.setDefaultTextColor(color)

    def set_selected_by_rect(self, rect: QRectF):
        props: LabelItemProps = self.property("props")

        if rect.contains(QPointF(props.x, props.y)):
            self.set_selected(True)


    def get_selected(self):
        props: LabelItemProps = self.property("props")
        return props.selected