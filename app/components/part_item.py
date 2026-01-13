# app/part_item.py
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSimpleTextItem,
)
from app.constants import SETTINGS, PART_ITEM, PART_ITEM, KEY_PART_ITEM_TEXT
from app.models import RectanglePartItem


class PartItem(RectanglePartItem):

    def __init__(self, part_id: str, pos: QPointF, **kwargs):
        setting = SETTINGS[PART_ITEM]
        size = setting["size"]
        draw_pos = QPointF(-size / 2, -size / 2)
        super().__init__(PART_ITEM, part_id, draw_pos, size=size, setting=setting, **kwargs)
        self.setPos(pos)
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        part_item_text = QGraphicsSimpleTextItem(self.part_id, parent=self)
        self.setData(KEY_PART_ITEM_TEXT, part_item_text) 
        self._refresh_ui(False)


    def _refresh_ui(self):
        super()._refresh_ui()
        t: QGraphicsSimpleTextItem = self.data(KEY_PART_ITEM_TEXT)
        t.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        br = t.boundingRect()
        t.setPos(-br.width() / 2, -br.height() / 2)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)