
from PySide6.QtCore import QPointF
from app.constants import (
    UI_SETTINGS,
    REF_PART_ITEM, REF_QUESTION_ITEM, BEHAVE_FIXED_SIZE,
    KEY_PRE_ITEM, ITEM_SIGN, BEHAVE_INITIAL_VISIBLE, ITEM_SIGN,
    BEHAVE_SQUARE, BEHAVE_HAS_CAPTION,
)

from app.helpers.utils import points_are_very_near, lengthes_are_very_similar, resize_rect
from app.models import Delta, PreItemData, Caption


class PreItem:
    def __init__(self, d: PreItemData):
        self._part_type = d.part_type
        self._parent_id = d.parent_id
        self._seq = d.seq
        self._is_active = d.active
        self.is_visible = d.visible
        self._is_dirty = d.is_dirty
        self._z_order = d.z_order
        size: int = int(UI_SETTINGS.get(d.part_type, {}).get("size", 0))
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
        if d.caption:
            self.caption = d.caption.copy()
        elif d.part_type in BEHAVE_HAS_CAPTION:
            self.caption = Caption("")
        else:
            self.caption = None


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
    
    def __hash__(self):
        return hash(self.uid)

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

    @property
    def is_dirty(self):
        return self._is_dirty
        
    @property
    def z_order(self):
        return self._z_order
    
    @z_order.setter
    def z_order(self, value):
        if not isinstance(value, int):
            raise ValueError
        if value != self.z_order:
            self.set_dirty()
            self._z_order = value
            self._refresh_ui()       
    
    @property
    def data(self):
        d = PreItemData()
        d.part_type = self.part_type
        d.parent_id = self.parent_id
        d.seq = self.seq
        d.active = self._is_active
        d.visible = self.is_visible
        d.is_dirty = self._is_dirty
        d.x = self.pos.x()
        d.y = self.pos.y()
        d.z_order = self.z_order
        d.width = self.width
        d.height = self.height
        d.caption = self.caption
        d.ui = self.ui
        return d

    @property
    def is_active(self):
        return self._is_active
    
    @is_active.setter
    def is_active(self, value: bool):
        if not isinstance(value, bool):
            raise ValueError
        if self._is_active != value:
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
        caption = f" ({self.caption_text})" if self.caption_text else ""
        sign = ITEM_SIGN.get(self.part_type)
        return f"{sign}{self.seq}{caption}" if sign else "???"
    
    @property
    def caption_text(self):
        return self.caption.text if self.caption else None
    
    @property
    def initial_pos(self):
        pos = QPointF(0, 0)
        if self.part_type in [REF_PART_ITEM, REF_QUESTION_ITEM]:
          pos = QPointF(-1 * self.width / 2, -1 * self.height / 2)
        return pos  

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

    def set_dirty(self):
        self._is_dirty = True

    def set_caption(self, text: str):
        if self.caption and self.caption.text != text:
            self.caption.text = text
            self.set_dirty()

    
    def set_pos(self, x, y):
        if x != self._pos.x() or y != self._pos.y():
            self.set_dirty()
        self._pos.setX(x)
        self._pos.setY(y)
        if self.ui:
            if not points_are_very_near(self._pos, self.ui.pos()):
                self.ui.setPos(self._pos)

    def set_width(self, value: float):
        if self.part_type in BEHAVE_FIXED_SIZE:
            return
        if self._width != value:
            self.set_dirty()
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
        if self._height != value:
            self.set_dirty()
        self._height = value
        if self.ui:
            if not lengthes_are_very_similar(self._height, self.ui.rect().height()):
                new_rect = resize_rect(self.ui.rect(), w=None, h=self._height)
                self.ui.setRect(new_rect)
    

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
            "z_order": self.z_order,
            "w": self.width,
            "h": self.height,
            "visible": self.is_visible,
        }
        if self.caption_text:
            item_dict["caption"] = self.caption_text
        self._is_dirty = False
        return item_dict

    @classmethod
    def from_dict(cls, data: dict):
        d = PreItemData()
        d.part_type = data["part_type"]
        d.parent_id = data["parent_id"]
        d.seq = data["seq"]
        d.active = False
        d.visible = d.part_type in BEHAVE_INITIAL_VISIBLE
        d.is_dirty = False
        d.x = data.get("x")
        d.z_order = data.get("z_order", 0)
        d.y = data.get("y")
        d.width = data.get("w")
        d.height = data.get("h")
        caption_text = data.get("caption")
        if caption_text:
            d.caption = Caption(caption_text)
        return cls(d)
    
