from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QBrush, QPen
from app.constants import (
    KEY_PRE_ITEM, KEY_RECT_STYLE, 
    QUESTION_REF_ITEM, SETTINGS,
    SIZABLE, SERIALIZABLE, REPEATABLE, ACTIVABLE
)


class RectStyles:
    def __init__(self, styles: dict):
        self.bg_color_active = styles.get("bg_color_active", "#00D4FF")
        self.bg_color_inactive = styles.get("bg_color_inactive", "#B0E9F5")
        self.border_color_active = styles.get("border_color_active", "#00D4FF")
        self.border_color_inactive = styles.get("border_color_inactive", "#B0E9F5")
        self.font_color_active = styles.get("font_color_active", "#000")
        self.font_color_inactive = styles.get("font_color_inactive", "#000")
        self.font_size_active = styles.get("font_size_active", 2)
        self.font_size_inactive = styles.get("font_size_inactive", 2)


class PreItem:
    def __init__(self, part_type, part_id, **kwargs):
        self.part_type = part_type
        self.part_id = part_id
        self.kwargs = kwargs
        self.is_active = kwargs.get("active", False)
        self.is_visible = kwargs.get("visible", True)
        size: int = SETTINGS.get(part_type, {}).get("size")
        self.pos = QPointF(-size / 2, -size / 2) if size else kwargs.get("pos", QPointF(0, 0))
        self.width = kwargs.get("width", 30) 
        self.height = kwargs.get("height", 10) 
        self.ui: RectanglePartItem | None = None

    @property
    def question_number(self):
        return self.kwargs.get("qn")
    
    @property
    def serializable(self):
        return self.part_type in SERIALIZABLE
    
    @property
    def activable(self):
        return self.part_type in ACTIVABLE
    
    @property
    def repeatable(self):
        return self.part_type in REPEATABLE

    @property
    def sizable(self):
        return self.part_type in SIZABLE      

    @property
    def uid(self) -> str:
        item_uid = f"{self.part_type}::{self.part_id}"
        if self.question_number:
            item_uid = f"{item_uid}::{self.question_number}"

        return item_uid
    
    def update_ui(self):
        if not self.ui:
            return
        self.pos = self.ui.pos()
        self.width = self.ui.rect().width()
        self.height = self.ui.rect().height()

    # ======= item serialization =======
    def to_dict(self) -> dict | None:
        if not self.serializable:
            return None
        if not self.ui:
            return
        self.update_ui()

        item_dict = {
            "part_type": self.part_type,
            "x": self.pos.x(),
            "y": self.pos.y(),
            "part_id": self.part_id,
            "visible": self.is_visible,
        }
        if self.sizable:
            item_dict["w"] = self.width
            item_dict["h"] = self.height
        if self.part_type in [QUESTION_REF_ITEM]:
            item_dict["qn"] = self.question_number
        return item_dict

    @classmethod
    def from_dict(cls, data: dict):
        pos = QPointF(data["x"], data["y"])
        part_type = data["part_type"]
        part_id = data["part_id"]
        visible = data["visible"]
        return PreItem(part_type, part_id, visible=visible)
        return cls(pre_item, pos)



class RectanglePartItem(QGraphicsRectItem):

    def __init__(self, pre_item: PreItem, pos: QPointF):
        kwargs = pre_item.kwargs
        w = kwargs.get("w") or kwargs.get("size") or 5
        h = kwargs.get("h") or kwargs.get("size") or 5
        super().__init__(pos.x(), pos.y(), w, h)
        self.setData(KEY_PRE_ITEM, pre_item)
        styles = kwargs.get("setting")
        if isinstance(styles, dict):
            self.setData(KEY_RECT_STYLE, RectStyles(styles))
            self.setPen(QPen(QColor(self.styles.border_color_active), 2))

    @property
    def styles(self) -> RectStyles:
        return self.data(KEY_RECT_STYLE)

    @property
    def pre_item(self) -> PreItem:
        return self.data(KEY_PRE_ITEM)

    # ======= item UI =======
    def _refresh_ui(self):
        if self.pre_item.is_active:
            self.setBrush(QBrush(QColor(self.styles.bg_color_active)))
            self.setPen(QPen(QColor(self.styles.border_color_active), 2))
        else:
            self.setBrush(QBrush(QColor(self.styles.bg_color_inactive)))
            self.setPen(QPen(QColor(self.styles.border_color_inactive), 2))
