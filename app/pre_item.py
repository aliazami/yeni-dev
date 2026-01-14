
from PySide6.QtCore import QPointF
from app.constants import (
    SETTINGS,
    PART_ITEM, QUESTION_REF_ITEM, WORD_BOUNDARY_PART_ITEM,
    SIZABLE, SERIALIZABLE, REPEATABLE, ACTIVABLE,
    KEY_PRE_ITEM,
)



class PreItem:
    def __init__(self, part_type: str, part_id: str, **kwargs):
        self.part_type = part_type
        self.part_id = part_id
        self._is_active = kwargs.get("active", False)
        self._qn = kwargs.get("qn")
        self._qnn = kwargs.get("qnn")
        self.is_visible = kwargs.get("visible", True)
        size: int = SETTINGS.get(part_type, {}).get("size")
        self.pos = QPointF(-size / 2, -size / 2) if size else kwargs.get("pos", QPointF(0, 0))
        self.width = size or kwargs.get("width", 30) 
        self.height = size or kwargs.get("height", 10) 
        self.ui = kwargs.get("ui")
        if self.ui:
            self.ui.setData(KEY_PRE_ITEM, self)

    def copy(self):
        part_id= str(self.part_id)
        part_type = str(self.part_type)
        return PreItem(part_type, part_id, **self.kwargs)

    def __str__(self):
        return self.uid

    @property
    def settings(self) -> dict:
        return SETTINGS.get(self.part_type, {})

    @property
    def kwargs(self):
        return {
            "active": self._is_active,
            "visible": self.is_visible,
            "pos": self.pos,
            "width": self.width,
            "height": self.height,
            "ui": self.ui,
            "qn": self._qn,
            "qnn": self._qnn,
        }

    @property
    def is_active(self):
        return self._is_active
    
    @is_active.setter
    def is_active(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError
        self._is_active = value
        self._refresh_ui()

    @property
    def question_number(self):
        return self._qn
    
    @property
    def qnn(self):
        return self._qnn
    
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
    
    @property
    def default_text(self) -> str:
        if self.part_type == PART_ITEM:
            return self.part_id
        if self.part_type == QUESTION_REF_ITEM:
            return str(self.question_number)
        return "???"
    
    def update_ui_data(self):
        if not self.ui:
            return
        self.pos = self.ui.pos()
        self.width = self.ui.rect().width()
        self.height = self.ui.rect().height()

    def _refresh_ui(self):
        if not self.ui:
            return
        self.ui._refresh_ui()

    # ======= item serialization =======
    def to_dict(self) -> dict | None:
        if not self.serializable:
            return None
        if not self.ui:
            return
        self.update_ui_data()

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
        if self.part_type in [WORD_BOUNDARY_PART_ITEM]:
            item_dict["qn"] = self.question_number
            item_dict["qnn"] = self.qnn
        return item_dict

    def from_dict(self, data: dict):
        pos = QPointF(data["x"], data["y"])
        part_type = data["part_type"]
        part_id = data["part_id"]
        visible = data["visible"]
        kwargs = {"visible": visible, "pos": pos}
        return PreItem(part_type, part_id, **kwargs)
    
