# app/word_boundary_part_item.py
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont, QBrush, QColor
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSimpleTextItem,
    QInputDialog,
    QMessageBox,
)
from app.constants import SETTINGS, WORD_BOUNDARY_PART_ITEM, SCOPE_PART, KEY_WORD
from app.helpers.utils import ignore
from app.models import RectanglePartItem, PreItem, PlatFormConfig


class WordBoundaryPartItem(RectanglePartItem):
    platform_config = PlatFormConfig(
        serializable=True,
        sizable=True,
        activable=False,
        repeatable=True,
        scope=SCOPE_PART,
    )
    
    def __init__(self, part_id: str, pos: QPointF, **kwargs):
        kwargs["setting"] = SETTINGS["word_boundary_part_item"]
        super().__init__(WORD_BOUNDARY_PART_ITEM, part_id, pos, **kwargs)
        word = kwargs["word"]
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
        pre_item = cls.platform_data.pre_item
        return WordBoundaryPartItem(pre_item.part_id, pos, w=w, h=h) if pre_item else None

    def _refresh_ui(self, active):
        super()._refresh_ui(active)
        self.scene().clear()
        lbl = f"{self.part_id}.{self.qn}.{word}"
        t = QGraphicsSimpleTextItem(lbl, parent=self)
        t.setBrush(QBrush(Qt.GlobalColor.white))
        t.setFont(QFont("Arial", 10))
        t.setPos(0, h + 5)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
