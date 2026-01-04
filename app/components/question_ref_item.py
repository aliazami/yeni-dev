
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsSimpleTextItem
from PySide6.QtGui import QPen, QFont
from PySide6.QtCore import Qt, QPointF
from app.constants import SETTINGS, KEY_TYPE, KEY_PART_ID, KEY_QUESTION_NUMBER, QUESTION_REF_ITEM
from app.models import IQuestionItem, TQuestionItem


class QuestionRefItem(QGraphicsRectItem, IQuestionItem):

    def __init__(self, item: TQuestionItem, pos: QPointF):
        w = SETTINGS["question_ref_item"]["width"]
        h = SETTINGS["question_ref_item"]["height"]
        super().__init__(-w, -h / 2, w, h)
        self.setData(KEY_PART_ID, QUESTION_REF_ITEM)
        self.setData(KEY_PART_ID, item.part_id)
        self.setData(KEY_QUESTION_NUMBER, item.qn)
        self.setPos(pos)
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        t = QGraphicsSimpleTextItem(item.part_id, parent=self)
        t.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        br = t.boundingRect()
        t.setPos(-br.width() / 2, -br.height() / 2)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)

    # === IPartItem ===
    @property
    def item_type(self) -> str:
        return self.data(KEY_TYPE)

    @property
    def part_id(self):
        return self.data(KEY_PART_ID)

    @property
    def qn(self):
        return self.data(KEY_QUESTION_NUMBER)

    @classmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        return QuestionRefItem(cls._pre_item, pos) if cls._pre_item else None
