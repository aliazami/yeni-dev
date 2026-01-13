# app/part_item.py
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSimpleTextItem,
)
from app.constants import KEY_PART_ITEM_TEXT
from app.pre_item import PreItem
from app.components.rectangle_part_item import RectanglePartItem


class PartItem(RectanglePartItem):

    def __init__(self, pre_item: PreItem, pos: QPointF):
        super().__init__(pre_item, pos)
        self.setPos(pos)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        part_item_text = QGraphicsSimpleTextItem(self.pre_item.part_id, parent=self)
        self.setData(KEY_PART_ITEM_TEXT, part_item_text) 
        self._refresh_ui(False)

    def _refresh_ui(self):
        super()._refresh_ui()
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        t: QGraphicsSimpleTextItem = self.data(KEY_PART_ITEM_TEXT)
        t.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        br = t.boundingRect()
        t.setPos(-br.width() / 2, -br.height() / 2)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)