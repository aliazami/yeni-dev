
from PySide6.QtCore import QPointF
from app.constants import (
    QUESTION_REF_ITEM, SETTINGS,
    SIZABLE, SERIALIZABLE, REPEATABLE, ACTIVABLE,
)



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
        self.ui = None

    @property
    def settings(self) -> dict:
        return SETTINGS.get(self.part_type, {})

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

    def from_dict(self, data: dict):
        pos = QPointF(data["x"], data["y"])
        part_type = data["part_type"]
        part_id = data["part_id"]
        visible = data["visible"]
        return PreItem(part_type, part_id, visible=visible, pos=pos)