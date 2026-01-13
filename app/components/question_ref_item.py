from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont, QBrush, QColor
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSimpleTextItem,
)
from app.constants import (
    KEY_QUESTION_REF_ITEM_TEXT
)

from app.models import RectanglePartItem, PreItem


class QuestionRefItem(RectanglePartItem):

    def __init__(self, pre_item: PreItem, pos: QPointF):
        super().__init__(pre_item, pos)
        self.setPos(pos)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        question_ref_text = QGraphicsSimpleTextItem(str(pre_item.question_number), parent=self)
        self.setData(KEY_QUESTION_REF_ITEM_TEXT, question_ref_text)
        self._refresh_ui(False)

    def _refresh_ui(self):
        super()._refresh_ui()
        if self.pre_item.is_active:
            self.setBrush(QBrush(QColor("#4488FF")))
            self.setPen(QPen(Qt.GlobalColor.black, 2))
        else:
            self.setBrush(QBrush(Qt.GlobalColor.yellow))
            self.setPen(QPen(Qt.GlobalColor.black, 2))

        t: QGraphicsSimpleTextItem = self.data(KEY_QUESTION_REF_ITEM_TEXT)
        t.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        br = t.boundingRect()
        t.setPos(-br.width() / 2, -br.height() / 2)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
