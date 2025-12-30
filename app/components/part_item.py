# app/part_item.py
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont, QBrush, QColor
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsSimpleTextItem,
)
from app.constants import SETTINGS, KEY_ID, KEY_TYPE, PART_ITEM
from app.models import ISerializable


class PartItem(QGraphicsEllipseItem, ISerializable):

    def __init__(self, item_id: str, pos: QPointF):
        radius = SETTINGS["part_item"]["radius"]
        super().__init__(-radius, -radius, 2 * radius, 2 * radius)
        self.setPos(pos)
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        self.setData(KEY_ID, item_id)
        self.setData(KEY_TYPE, PART_ITEM)
        t = QGraphicsSimpleTextItem(item_id, parent=self)
        t.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        br = t.boundingRect()
        t.setPos(-br.width() / 2, -br.height() / 2)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def set_active(self, active: bool):
        if active:
            self.setBrush(QBrush(QColor("#4488FF")))
            self.setPen(QPen(Qt.GlobalColor.black, 2))
        else:
            self.setBrush(QBrush(Qt.GlobalColor.yellow))
            self.setPen(QPen(Qt.GlobalColor.black, 2))

    def to_dict(self) -> dict:
        return {
            "type": PART_ITEM,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "id": self.data(KEY_ID),
        }

    @classmethod
    def from_dict(cls, data: dict):
        pos = QPointF(data["x"], data["y"])
        iid = data["id"]
        return cls(item_id=iid, pos=pos)
