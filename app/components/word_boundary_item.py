# app/word_boundary_item.py
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont, QBrush, QColor
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsSimpleTextItem
from app.constants import (
    KEY_ID,
    KEY_TYPE,
    KEY_RECT_ID,
    KEY_RECT_TEXT,
    WORD_BOUNDARY_ITEM,
)
from app.models import ISerializable


class WordBoundaryItem(QGraphicsRectItem, ISerializable):

    def __init__(
        self, part_id: str, item_id: str, word: str, pos: QPointF, w: float, h: float
    ):
        super().__init__(0, 0, w, h)
        self.setPos(pos)
        self.setPen(QPen(Qt.GlobalColor.green, 2))
        self.setBrush(QBrush(QColor(0, 255, 0, 100)))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        self.setData(KEY_TYPE, WORD_BOUNDARY_ITEM)
        self.setData(KEY_ID, part_id)
        self.setData(KEY_RECT_ID, item_id)
        self.setData(KEY_RECT_TEXT, word)

        lbl = f"{part_id}.{item_id}.{word}"
        t = QGraphicsSimpleTextItem(lbl, parent=self)
        t.setBrush(QBrush(Qt.GlobalColor.white))
        t.setFont(QFont("Arial", 10))
        t.setPos(0, h + 5)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def to_dict(self) -> dict:
        r = self.rect()
        return {
            "type": WORD_BOUNDARY_ITEM,
            "part_id": self.data(KEY_ID),
            "item_id": self.data(KEY_RECT_ID),
            "word": self.data(KEY_RECT_TEXT),
            "w": r.width(),
            "h": r.height(),
            "x": self.pos().x(),
            "y": self.pos().y(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        pos = QPointF(data["x"], data["y"])
        part_id = data["part_id"]
        item_id = data["item_id"]
        word = data["word"]
        h = data["h"]
        w = data["w"]
        return cls(part_id, item_id, word, pos, w, h)
