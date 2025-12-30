# app/word_boundary_item.py
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont, QBrush, QColor
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsSimpleTextItem
from app.constants import (
    KEY_PART_ID,
    KEY_TYPE,
    WORD_BOUNDARY_ITEM,
)
from app.models import ISerializable, IQuestionItem

_QUESTION_NUMBER = 5
_WORD = 6

class WordBoundaryItem(QGraphicsRectItem, ISerializable, IQuestionItem):

    def __init__(
        self, part_id: str, qn: int, word: str, pos: QPointF, w: float, h: float
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
        self.setData(KEY_PART_ID, part_id)
        self.setData(_QUESTION_NUMBER, qn)
        self.setData(_WORD, word)

        lbl = f"{part_id}.{qn}.{word}"
        t = QGraphicsSimpleTextItem(lbl, parent=self)
        t.setBrush(QBrush(Qt.GlobalColor.white))
        t.setFont(QFont("Arial", 10))
        t.setPos(0, h + 5)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    def to_dict(self) -> dict:
        r = self.rect()
        return {
            "type": WORD_BOUNDARY_ITEM,
            "part_id": self.data(KEY_PART_ID),
            "qn": self.data(_QUESTION_NUMBER),
            "word": self.data(_WORD),
            "w": r.width(),
            "h": r.height(),
            "x": self.pos().x(),
            "y": self.pos().y(),
        }

    def part_id(self) -> str:
        return self.data(KEY_PART_ID)

    def qn(self) -> int:
        return self.data(_QUESTION_NUMBER)

    def word(self):
        return self.data(_WORD)

    def is_me(self, part_id, qn, word):
        return self.is_my_question(part_id, qn) and self.word() == word

    @classmethod
    def from_dict(cls, data: dict):
        pos = QPointF(data["x"], data["y"])
        part_id = data["part_id"]
        qn = data["qn"]
        word = data["word"]
        h = data["h"]
        w = data["w"]
        return cls(part_id, qn, word, pos, w, h)
