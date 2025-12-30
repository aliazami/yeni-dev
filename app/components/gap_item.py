from PySide6.QtWidgets import QGraphicsTextItem

from app.models import ISerializable, IQuestionItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsItem
from app.constants import KEY_PART_ID, KEY_TYPE, GAP_ITEM

_QUESTION_NUMBER = 5

class GapItem(QGraphicsTextItem, ISerializable, IQuestionItem):
    def __init__(self, part_id: str, question_number: int, pos: QPointF):
        tag = f"{part_id}.{question_number}"
        super().__init__(tag)
        self.setDefaultTextColor(Qt.GlobalColor.white)
        self.setFont(QFont("Arial", 14))
        self.setPos(pos)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        self.setData(KEY_PART_ID, part_id)
        self.setData(_QUESTION_NUMBER, question_number)
        self.setData(KEY_TYPE, "LABEL")

    def to_dict(self) -> dict:
        return {
            "type": GAP_ITEM,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "part_id": self.data(KEY_PART_ID),
            "qn": self.data(_QUESTION_NUMBER),
        }

    def part_id(self) -> str:
        return self.data(KEY_PART_ID)

    def qn(self) -> int:
        return self.data(_QUESTION_NUMBER)

    @classmethod
    def from_dict(cls, data: dict):
        pos = QPointF(data["x"], data["y"])
        part_id = data["part_id"]
        gap_id = data["qn"]
        return cls(part_id, gap_id, pos)