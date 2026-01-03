from PySide6.QtWidgets import QGraphicsTextItem

from app.models import ISerializable, TQuestionItem, IRepeatableQuestionItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGraphicsItem
from app.constants import KEY_PART_ID, KEY_TYPE, GAP_ITEM, KEY_QN
from app.helpers.utils import get_next


class GapItem(QGraphicsTextItem, ISerializable, IRepeatableQuestionItem):

    def __init__(self, item: TQuestionItem, pos: QPointF):
        tag = f"{item.part_id}.{item.qn}"
        super().__init__(tag)
        self.setData(KEY_PART_ID, item.part_id)
        self.setData(KEY_QN, item.qn)
        self.setData(KEY_TYPE, GAP_ITEM)

        self.setDefaultTextColor(Qt.GlobalColor.black)
        self.setHtml(f"<div style=\"background-color: lightblue;\">{tag}</div>")
        self.setFont(QFont("Arial", 14))
        self.setPos(pos)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )

    @property
    def item_type(self) -> str:
        return self.data(KEY_TYPE)

    @property
    def part_id(self) -> str:
        return self.data(KEY_PART_ID)

    @property
    def qn(self) -> int:
        return self.data(KEY_QN)

    def to_dict(self) -> dict:
        return {
            "type": GAP_ITEM,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "part_id": self.data(KEY_PART_ID),
            "qn": self.data(KEY_QN),
        }

    @classmethod
    def from_dict(cls, data: dict):
        pos = QPointF(data["x"], data["y"])
        part_id = data["part_id"]
        qn = data["qn"]
        item = TQuestionItem(GAP_ITEM, part_id, qn)
        return cls(item, pos)

    @classmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        return GapItem(cls._pre_item, pos) if cls._pre_item else None

