# app/part_item.py
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont, QBrush, QColor
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSimpleTextItem,
    QInputDialog,
    QMessageBox,
)
from app.constants import SETTINGS, KEY_PART_ID, KEY_TYPE, PART_ITEM, SCOPE_PART
from app.helpers.utils import ignore
from app.models import RectanglePartItem, PreItem, PlatFormConfig


class PartItem(RectanglePartItem):
    platform_config = PlatFormConfig(
        serializable=True,
        sizable=False,
        activable=True,
        repeatable=True,
        scope=SCOPE_PART,
    )
    def __init__(self, part_id: str, pos: QPointF):
        radius = SETTINGS["part_item"]["radius"]
        draw_pos = QPointF(-radius, -radius)
        w = h = 2 * radius
        super().__init__(PART_ITEM, part_id, draw_pos, w=w, h=h)
        self.setData(KEY_PART_ID, part_id)
        self.setData(KEY_TYPE, PART_ITEM)

        self.setPos(pos)
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        t = QGraphicsSimpleTextItem(part_id, parent=self)
        t.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        br = t.boundingRect()
        t.setPos(-br.width() / 2, -br.height() / 2)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._refresh_ui(False)


    @classmethod
    def pre_create(cls, items: list[QGraphicsItem], part_id: str) -> bool:
        text, ok = QInputDialog.getText(None, "Add Part Item", "Enter Unique ID:")
        if ok and text:
            pre_item = PreItem(part_type=PART_ITEM, part_id=text)
            if cls.has_item(items, pre_item):
                QMessageBox.warning(None, "Error", "Exists!")
                return False
            else:
                cls._pre_item = pre_item
                return True

        return False

    @classmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        ignore([w, h])
        pre_item = cls.platform_data.pre_item
        return PartItem(pre_item.part_id, pos) if pre_item else None

    def _refresh_ui(self, active):
        if active:
            self.setBrush(QBrush(QColor("#4488FF")))
            self.setPen(QPen(Qt.GlobalColor.black, 2))
        else:
            self.setBrush(QBrush(Qt.GlobalColor.yellow))
            self.setPen(QPen(Qt.GlobalColor.black, 2))