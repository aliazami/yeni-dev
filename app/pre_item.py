
from PySide6.QtCore import QPointF
from app.constants import (
    SETTINGS,
    PART_ITEM, QUESTION_REF_ITEM, WORD_BOUNDARY_PART_ITEM,
    SIZABLE, SERIALIZABLE, REPEATABLE, ACTIVABLE,
    KEY_PRE_ITEM,
)

from app.helpers.utils import points_are_very_near



class PreItem:
    def __init__(self, part_type: str, part_id: str, **kwargs):
        self.part_type = part_type
        self.part_id = part_id
        self._is_active = kwargs.get("active", False)
        self._qn = kwargs.get("qn")
        self._qnn = kwargs.get("qnn")
        self.is_visible = kwargs.get("visible", True)
        size: int = SETTINGS.get(part_type, {}).get("size")
        x = kwargs.get("x")
        y = kwargs.get("y")
        pos = kwargs.get("pos")
        width = kwargs.get("width") 
        height = kwargs.get("height")
        if x is None or y is None:
            if pos and isinstance(pos, QPointF):
                x , y = pos.x(), pos.y()
            elif size:
                x = y = -size / 2
            else:
                x = y = 0
        self._pos = QPointF(x, y)
        self.width = width or size
        self.height = height or size
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
    def pos(self):
        return QPointF(self._pos.x(), self._pos.y())
    
    def set_pos(self, x, y):
        self._pos.setX(x)
        self._pos.setY(y)
        if self.ui:
            if not points_are_very_near(self._pos, self.ui.pos()):
                self.ui.setPos(self._pos)
    @property
    def kwargs(self):
        return {
            "active": self._is_active,
            "visible": self.is_visible,
            "x": self.pos.x(),
            "y": self.pos.y(),
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
    
    @property
    def initial_pos(self):
        pos = QPointF(0, 0)
        if self.part_type in [PART_ITEM, QUESTION_REF_ITEM]:
          pos = QPointF(-1 * self.width / 2, -1 * self.height / 2)
        return pos  
    
    def update_ui_data(self):
        if not self.ui:
            return
        pos = self.ui.pos()
        self.set_pos(pos.x(), pos.y())
        self.width = self.ui.rect().width()
        self.height = self.ui.rect().height()

    def _refresh_ui(self):
        if not self.ui:
            return
        self.ui._refresh_ui()

    # ======= item serialization =======
    def to_dict(self) -> dict | None:
        item_dict = {
            "part_type": self.part_type,
            "x": self.pos.x(),
            "y": self.pos.y(),
            "w": self.width,
            "h": self.height,
            "part_id": self.part_id,
            "visible": self.is_visible,
        }
        if self._qn:
                item_dict["qn"] = self._qn
        if self._qnn:
                item_dict["qnn"] = self._qnn
        return item_dict

    @classmethod
    def from_dict(cls, data: dict):
        part_type = data["part_type"]
        part_id = data["part_id"]
        kwargs = {
            "active": False,
            "visible": part_type == PART_ITEM,
            "x": data.get("x"),
            "y": data.get("y"),
            "width": data.get("w"),
            "height": data.get("h"),
            "qn": data.get("qn"),
            "qnn": data.get("qnn"),
        }
        return cls(part_type, part_id, **kwargs)
    
