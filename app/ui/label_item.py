# ui/label_item.py

from PySide6.QtCore import Qt, Signal
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
        self.setDefaultTextColor(Qt.GlobalColor.red)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        props: LabelItemProps = self.property("props")
        self.setDefaultTextColor(props.color)
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

