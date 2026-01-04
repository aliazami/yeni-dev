# app/word_boundary_item.py
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont, QBrush, QColor
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsSimpleTextItem
from app.constants import (
    KEY_PART_ID,
    KEY_TYPE, KEY_QUESTION_NUMBER,
    WORD_BOUNDARY_ITEM,
)
from app.models import RectanglePartItem

KEY_WORD = 6


class WordBoundaryItem(RectanglePartItem):

    def __init__(
        self, item: part_id: str, pos: QPointF, w: float, h: float
    ):
        super().__init__(0, 0, w, h)
        word = item.kwargs["word"]
        self.setData(KEY_TYPE, WORD_BOUNDARY_ITEM)
        self.setData(KEY_PART_ID, item.part_id)
        self.setData(KEY_QUESTION_NUMBER, item.qn)
        self.setData(KEY_WORD, word)

        self.setPos(pos)
        self.setPen(QPen(Qt.GlobalColor.green, 2))
        self.setBrush(QBrush(QColor(0, 255, 0, 100)))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

        lbl = f"{item.part_id}.{item.qn}.{word}"
        t = QGraphicsSimpleTextItem(lbl, parent=self)
        t.setBrush(QBrush(Qt.GlobalColor.white))
        t.setFont(QFont("Arial", 10))
        t.setPos(0, h + 5)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    @property
    def item_type(self) -> str:
        return self.data(KEY_TYPE)

    @property
    def part_id(self) -> str:
        return self.data(KEY_PART_ID)

    @property
    def qn(self) -> int:
        return self.data(KEY_QUESTION_NUMBER)

    def to_dict(self) -> dict:
        r = self.rect()
        return {
            "type": WORD_BOUNDARY_ITEM,
            "part_id": self.part_id,
            "qn": self.qn,
            "word": self.word,
            "w": r.width(),
            "h": r.height(),
            "x": self.pos().x(),
            "y": self.pos().y(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        pos = QPointF(data["x"], data["y"])
        part_id = data["part_id"]
        qn = data["qn"]
        word = data["word"]
        h = data["h"]
        w = data["w"]
        item = TQuestionItem(WORD_BOUNDARY_ITEM, part_id, qn, word=word)
        return cls(item, pos, w, h)

    @property
    def word(self):
        return self.data(KEY_WORD)

    @classmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        return WordBoundaryItem(cls._pre_item, pos, w, h) if cls._pre_item else None
