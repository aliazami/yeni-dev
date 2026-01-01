# app/part_item.py
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont, QBrush, QColor
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsSimpleTextItem,
    QInputDialog,
    QMessageBox,
)
from app.constants import SETTINGS, KEY_PART_ID, KEY_TYPE, PART_ITEM
from app.models import ISerializable, IPartItem, TPartItem
from app.helpers.utils import ignore

class PartItem(QGraphicsEllipseItem, ISerializable, IPartItem):

    def __init__(self, item: TPartItem, pos: QPointF):
        radius = SETTINGS["part_item"]["radius"]
        super().__init__(-radius, -radius, 2 * radius, 2 * radius)
        self.setData(KEY_PART_ID, item.part_id)
        self.setData(KEY_TYPE, PART_ITEM)

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

    @property
    def item_type(self) -> str:
        return self.data(KEY_TYPE)

    @property
    def part_id(self) -> str:
        return self.data(KEY_PART_ID)

    @property
    def uid(self) -> str:
        return f"{self.item_type}::{self.part_id}"

    def to_dict(self) -> dict:
        return {
            "type": PART_ITEM,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "id": self.data(KEY_PART_ID),
        }


    @classmethod
    def from_dict(cls, data: dict):
        pos = QPointF(data["x"], data["y"])
        part_id = data["part_id"]
        item = TPartItem(PART_ITEM, part_id)
        return cls(item, pos)

    @classmethod
    def pre_create(cls, items: list[QGraphicsItem], part_id: str, **kwargs) -> bool:
        ignore([part_id, kwargs])
        text, ok = QInputDialog.getText(None, "Add Part Item", "Enter Unique ID:")
        if ok and text:
            pre_item = TPartItem(PART_ITEM, text)
            if cls.has_item(items, pre_item):
                QMessageBox.warning(None, "Error", "Exists!")
                return False
            else:
                cls._pre_item = pre_item
                return True

        return False

    @classmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        return PartItem(cls._pre_item, pos) if cls._pre_item else None

    def set_active(self, active: bool):
        if active:
            self.setBrush(QBrush(QColor("#4488FF")))
            self.setPen(QPen(Qt.GlobalColor.black, 2))
        else:
            self.setBrush(QBrush(Qt.GlobalColor.yellow))
            self.setPen(QPen(Qt.GlobalColor.black, 2))

