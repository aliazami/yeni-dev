
from PySide6.QtCore import QPointF
from app.constants import (
    UI_SETTINGS,
    REF_PART_ITEM, REF_QUESTION_ITEM, BEHAVE_FIXED_SIZE,
    KEY_PRE_ITEM, ITEM_SIGN, BAHAVE_INITIAL_VISIBLE, ITEM_SIGN,
    BEHAVE_SQUARE
)

from app.helpers.utils import points_are_very_near, lengthes_are_very_similar
from app.models import Delta, PreItemData
from app.helpers.utils import resize_rect


class PreItem:
    def __init__(self, d: PreItemData):
        self._part_type = d.part_type
        self._parent_id = d.parent_id
        self._seq = d.seq
        self._is_active = d.active
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
        self.tag = d.tag
        if self.ui:
            self.ui.setData(KEY_PRE_ITEM, self)

    def copy(self):
        return PreItem(self.data)

    def __str__(self):
        return self.uid
    
    def __repr__(self):
        return f"{self.uid} {id(self)}"
    
    def __eq__(self, value):
        if isinstance(value, PreItem):
            return self.uid == value.uid
        return False
    
    def __ne__(self, value):
        if isinstance(value, PreItem):
            return self.uid != value.uid
        return True

    @property
    def part_type(self):
        return self._part_type
    
    @property
    def parent_id(self):
        return self._parent_id
    
    @property
    def seq(self):
        return self._seq
    
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
    
    def is_my_ascendant(self, other):
        if isinstance(other, PreItem):
            return self.uid.startswith(other.uid) and self != other
        raise ValueError
    
    def is_my_descendant(self, other):
        if isinstance(other, PreItem):
            return other.is_my_ascendant(self)
        raise ValueError
    
    def is_my_parent(self, other):
        if isinstance(other, PreItem):
            return self.is_my_ascendant(other) and self.depth == other.depth + 1
        raise ValueError
    
    def is_my_child(self, other):
        if isinstance(other, PreItem):
            return other.is_my_parent(self)
        raise ValueError     

    def is_my_sibling(self, other):
        if isinstance(other, PreItem):
            return self.parent_id == other.parent_id and self != other
        raise ValueError   

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
        if self.part_type in BEHAVE_FIXED_SIZE:
            return
        self._width = value
        if self.ui:
            if not lengthes_are_very_similar(self._width, self.ui.rect().width()):
                new_rect = resize_rect(self.ui.rect(), w=self._width, h=None)
                self.ui.setRect(new_rect)
        if self.part_type in BEHAVE_SQUARE:
            self._set_height(value)

    def set_height(self, value: float):
        if self.part_type in BEHAVE_SQUARE:
            return        
        self._set_height(value)

    def _set_height(self, value: float):      
        if self.part_type in BEHAVE_FIXED_SIZE:
            return        
        self._height = value
        if self.ui:
            if not lengthes_are_very_similar(self._height, self.ui.rect().height()):
                new_rect = resize_rect(self.ui.rect(), w=None, h=self._height)
                self.ui.setRect(new_rect)

    

    @property
    def data(self):
        d = PreItemData()
        d.part_type = self.part_type
        d.parent_id = self.parent_id
        d.seq = self.seq
        d.active = self._is_active
        d.visible = self.is_visible
        d.x = self.pos.x()
        d.y = self.pos.y()
        d.width = self.width
        d.height = self.height
        d.ui = self.ui
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
    def seq(self):
        return self._seq

    @property
    def uid(self) -> str:
        parent_part = f"{self.parent_id}::" if self.parent_id else ""
        return f"{parent_part}{self.default_text}"
    
    @property
    def depth(self):
        return self.uid.count("::")
    
    @property
    def default_text(self) -> str:
        sign = ITEM_SIGN.get(self.part_type)
        return f"{sign}{self.seq}" if sign else "???"
    
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
            "parent_id": self.parent_id,
            "seq": self.seq,
            "x": self.pos.x(),
            "y": self.pos.y(),
            "w": self.width,
            "h": self.height,
            "visible": self.is_visible,
        }

        return item_dict

    @classmethod
    def from_dict(cls, data: dict):
        d = PreItemData()
        d.part_type = data["part_type"]
        d.parent_id = data["parent_id"]
        d.seq = data["seq"]
        d.active = False
        d.visible = d.part_type in BAHAVE_INITIAL_VISIBLE
        d.x = data.get("x")
        d.y = data.get("y")
        d.width = data.get("w")
        d.height = data.get("h")
                
        return cls(d)
    
