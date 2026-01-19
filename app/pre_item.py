
from PySide6.QtCore import QPointF
from app.constants import (
    UI_SETTINGS,
    REF_PART_ITEM, REF_QUESTION_ITEM, Q_WORD_BOUNDARY_PART_ITEM,
    FIXED_SIZE, SERIALIZABLE, REPEATABLE, ACTIVABLE, SQUARE,
    KEY_PRE_ITEM, REF_PAGE_ITEM
)

from app.helpers.utils import points_are_very_near, lengthes_are_very_similar
from app.models import Delta, PreItemData
from app.helpers.utils import resize_rect


class PreItem:
    def __init__(self, d: PreItemData):
        self._part_type = d.part_type
        self._part_id = d.part_id
        self._page_id: str | None = d.page_id
        self._is_active = d.active
        self._qn = d.qn
        self._qnn = d.qnn
        self.is_visible = d.visible
        size: int = UI_SETTINGS.get(d.part_type, {}).get("size")
        x = d.x
        y = d.y
        width = d.width 
        height = d.height
        if x is None or y is None:
            if size:
                x = y = -size / 2
            else:
                x = y = 0
        self._pos = QPointF(x, y)
        self._width = width or size
        self._height = height or size
        self.ui = d.ui
        if self.ui:
            self.ui.setData(KEY_PRE_ITEM, self)

    def copy(self):
        return PreItem(self.data)

    def __str__(self):
        return self.uid
    
    def __repr__(self):
        return f"{self.uid} {id(self)}"

    @property
    def part_type(self):
        return self._part_type
    
    @property
    def part_id(self):
        return self._part_id
    
    @property
    def page_id(self):
        return self._page_id
    
    @property
    def settings(self) -> dict:
        return UI_SETTINGS.get(self.part_type, {})
    
    @property
    def pos(self):
        return QPointF(self._pos.x(), self._pos.y())
    
    @property
    def width(self):
        return self._width
    
    @property
    def height(self):
        return self._height
    
    def move(self, delta: Delta):
        x = self.pos.x() + delta.dx
        y = self.pos.y() + delta.dy
        self.set_pos(x, y)
    
    def set_pos(self, x, y):
        self._pos.setX(x)
        self._pos.setY(y)
        if self.ui:
            if not points_are_very_near(self._pos, self.ui.pos()):
                self.ui.setPos(self._pos)

    def set_width(self, value: float):
        if self.fixed_size:
            return
        self._width = value
        if self.ui:
            if not lengthes_are_very_similar(self._width, self.ui.rect().width()):
                new_rect = resize_rect(self.ui.rect(), w=self._width, h=None)
                self.ui.setRect(new_rect)

    def set_height(self, value: float):
        if self.fixed_size:
            return        
        self._height = value
        if self.ui:
            if not lengthes_are_very_similar(self._height, self.ui.rect().height()):
                new_rect = resize_rect(self.ui.rect(), w=None, h=self._height)
                self.ui.setRect(new_rect)

    @property
    def data(self):
        d = PreItemData(self.part_type, self.part_id)
        d.active = self._is_active
        d.visible = self.is_visible
        d.x = self.pos.x()
        d.y = self.pos.y()
        d.width = self.width
        d.height = self.height
        d.ui = self.ui
        d.qn = self._qn
        d.qnn = self._qnn
        d.page_id = self.page_id
        return d

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
    def fixed_size(self):
        return self.part_type in FIXED_SIZE
    
    @property
    def is_square(self):
        return self.part_type in SQUARE

    @property
    def uid(self) -> str:
        item_uid = f"{self.part_type}::{self.part_id}"
        if self.question_number:
            item_uid = f"{item_uid}::{self.question_number}"
            if self.qnn:
                item_uid = f"{item_uid}::{self.qnn}"
        return item_uid
    
    @property
    def default_text(self) -> str:
        if self.part_type == REF_PAGE_ITEM:
            return self.page_id        
        if self.part_type == REF_PART_ITEM:
            return self.part_id
        if self.part_type == REF_QUESTION_ITEM:
            return str(self.question_number)
        if self.part_type in [Q_WORD_BOUNDARY_PART_ITEM]:
            return str(self.qnn)        
        return "???"
    
    @property
    def initial_pos(self):
        pos = QPointF(0, 0)
        if self.part_type in [REF_PART_ITEM, REF_QUESTION_ITEM]:
          pos = QPointF(-1 * self.width / 2, -1 * self.height / 2)
        return pos  
    
    def update_ui_data(self):
        if not self.ui:
            return
        pos = self.ui.pos()
        self.set_pos(pos.x(), pos.y())
        self.set_width(self.ui.rect().width())
        self.set_height(self.ui.rect().height())

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
            "page_id": self.page_id,
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
        d = PreItemData(part_type, part_id)
        d.active = False
        d.visible = part_type == REF_PART_ITEM
        d.x = data.get("x")
        d.y = data.get("y")
        d.width = data.get("w")
        d.height = data.get("h")
        d.qn = data.get("qn")
        d.qnn = data.get("qnn")
        d.page_id = data.get("page_id")
                
        return cls(d)
    
