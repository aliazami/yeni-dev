# app/part_item.py
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSimpleTextItem,
    QInputDialog,
    QMessageBox,
)
from app.constants import SETTINGS, PART_ITEM, SCOPE_PART, PART_ITEM, KEY_PART_ITEM_TEXT
from app.helpers.utils import ignore, check_repeat_id
from app.models import RectanglePartItem, PreItem, PlatFormConfig


class PartItem(RectanglePartItem):
    platform_config = PlatFormConfig(
        serializable=True,
        sizable=False,
        activable=True,
        repeatable=True,
        scope=SCOPE_PART,
    )

    def __init__(self, part_id: str, pos: QPointF, **kwargs):
        setting = SETTINGS[PART_ITEM]
        size = setting["size"]
        draw_pos = QPointF(-size / 2, -size / 2)
        super().__init__(PART_ITEM, part_id, draw_pos, size=size, setting=setting, **kwargs)
        self.setPos(pos)
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        part_item_text = QGraphicsSimpleTextItem(self.part_id, parent=self)
        self.setData(KEY_PART_ITEM_TEXT, part_item_text) 
        self._refresh_ui(False)

    @classmethod
    def get_active_item(cls) -> str | None:
        uid = cls.platform_state.active_item_uid
        if not uid:
            return None
        return uid.split("::")[1]

    @classmethod
    def pre_create(cls, items: list[QGraphicsItem], **kwargs) -> bool:
        part_id, ok = QInputDialog.getText(None, "Add Part Item", "Enter Unique ID:")
        if ok and part_id:
            is_repeating, part_id = check_repeat_id(part_id)
            pre_item = PreItem(part_type=PART_ITEM, part_id=part_id)
            if cls.has_item(items, pre_item):
                QMessageBox.warning(None, "Error", "Exists!")
                return False
            else:
                cls.platform_state.is_repeating = is_repeating
                cls.platform_data.pre_item = pre_item
                return True

        return False

    @classmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        ignore([w, h])
        pre_item = cls.platform_data.pre_item
        return PartItem(pre_item.part_id, pos) if pre_item else None

    def _refresh_ui(self, active):
        super()._refresh_ui(active)
        t = self.data(KEY_PART_ITEM_TEXT)
        t.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        br = t.boundingRect()
        t.setPos(-br.width() / 2, -br.height() / 2)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)