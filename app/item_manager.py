from PySide6.QtCore import QPointF
from PySide6.QtWidgets import (
    QInputDialog,
    QMessageBox,
    QDialog,
)
from app.pre_item import PreItem
from app.constants import (
    REF_PART_ITEM, REF_QUESTION_ITEM, SceneMode, WORD_BOUNDARY_ITEM,
    CAPTION_ITEM, BOX_ITEM, REF_UNIT_ITEM,
    BAHAVE_REPEATABLE_INSERT, BEHAVE_RECTANGLE, ITEM_CHILD_TYPES,
    BEHAVE_HAS_NO_PARENT
)
from app.components.reference_part_item import ReferencePartItem
from app.components.rectangle_part_item import RectanglePartItem
from app.components.word_boundary_part_item import WordBoundaryPartItem
from app.dialogs import PartSelectDialog
from app.models import Delta, PreItemData
from app.manager_stat import ManagerStat, get_next_str
from app.manager_io import ManagerIO
class ItemManager:
    def __init__(self):
        self._items: list[PreItem] = []
        self._stat = ManagerStat(self._items)
        self.io = ManagerIO()
        self.is_repeating = False
        self._pre_item: PreItem | None = None
        self._current_item: PreItem | None = None
        self._editing_item: PreItem | None = None
        self._deep_copy_item: PreItem | None = None

    # @property
    # def current_file_path(self):

    @property
    def stat(self):
        return self._stat

    
    def create(self, pos: QPointF | None = None) -> RectanglePartItem | None:
        item = self._pre_item.copy()
        if not self.is_repeating:
            self._pre_item = None
        if not item:
            raise Exception(f"No pre-item exists in create phase")
        if pos:
            item.set_pos(pos.x(), pos.y())
        item.ui = get_ui(item)
        # self.activate_item(item.uid)
        return item.ui
    
    def create_from_dict(self, item_data: dict)-> RectanglePartItem | None:
        self._pre_item = PreItem.from_dict(item_data)
        return self.create()
    
    def create_rect(self, pos: QPointF, w: float, h: float):
        if not self._pre_item:
            return
        if self._pre_item.part_type not in BEHAVE_RECTANGLE:
            raise Exception(f"{self._pre_item.part_type} is not a rectangular")
        d = self._pre_item.data.copy()
        d.x = pos.x()
        d.y = pos.y()
        d.width = w
        d.height = h
        pre_item = PreItem(d)
        self._pre_item = pre_item
        return self.create()
    
    def edit_rect(self, pos: QPointF, w: float, h: float):
        pre_item = self._editing_item.copy()
        pre_item.ui = None
        self._editing_item = None
        pre_item.set_pos(pos.x(), pos.y())
        pre_item.set_width(w)
        pre_item.set_height(h)
        self._pre_item = pre_item
        return self.create()
    
    def deep_copy(self, pos: QPointF):
        item = self._deep_copy_item
        if not item:
            return
        dx = pos.x() - item.pos.x()
        dy = pos.y() - item.pos.y()
        move_delta = Delta(dx, dy)
        new_items = self.stat.deep_copy_by_delta(item, move_delta)
        if not new_items:
            return
        new_uis = []
        for new_item in new_items:
            self._pre_item = new_item
            new_uis.append(self.create())
        return new_uis 
    
    def pre_create_item(self, part_type: str | None = None, parent_item: PreItem | None = None):
        seq = ok = None
        if parent_item is None and self._current_item:
            parent_item = self._current_item

        if parent_item is None and part_type in BEHAVE_HAS_NO_PARENT:
            seq, ok = QInputDialog.getInt(None, f"Add {part_type}", f"{part_type}:", value=1)
        elif parent_item is None and part_type not in BEHAVE_HAS_NO_PARENT:
            unique_unit_item = self.stat.get_unique_unit_item()
            if isinstance(unique_unit_item, int) and unique_unit_item == 0:
                part_type = REF_UNIT_ITEM
                seq, ok = QInputDialog.getInt(None, f"Add {part_type}", f"{part_type}:", value=1)
            elif isinstance(unique_unit_item, int) and unique_unit_item > 1:
                QMessageBox.warning(None, "Error", "More Than 1 UNIT exists, select one of them")
                return
            elif isinstance(unique_unit_item, PreItem):
                # default to add the next REF_PART_ITEM
                part_type = REF_PART_ITEM
                seq, ok = self.stat.get_next_seq(unique_unit_item.uid, part_type), True
                parent_item = unique_unit_item
            else:
                raise Exception("unexpected condition")
        elif parent_item and part_type and part_type not in ITEM_CHILD_TYPES[parent_item.part_type]:
            raise Exception(f"{part_type} is not a child of {parent_item.part_type}")
        elif parent_item and part_type and part_type in ITEM_CHILD_TYPES[parent_item.part_type]:
            next_seq = self.stat.get_next_seq(parent_item.id, part_type)
            seq, ok = QInputDialog.getInt(None, f"Add {part_type}", f"{part_type}:", value=next_seq)
        elif parent_item and not part_type:
            child_options = self.stat.get_child_options(parent_item)
            dialog = PartSelectDialog(child_options)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                part_type, seq = dialog.get_data()
                ok = True
        else:
            raise Exception("unpredicted condition")
        if ok and seq:
            d = PreItemData()
            d.part_type = part_type
            d.parent_id = parent_item.uid if parent_item else None
            d.seq = seq
            pre_item = PreItem(d)
            if self.stat.get_item(pre_item.uid):
                QMessageBox.warning(None, "Error", "Exists!")
            else:
                self.is_repeating = part_type in BAHAVE_REPEATABLE_INSERT
                self._pre_item = pre_item
                return get_scene_mode(pre_item)        
    
    def activate_item(self, uid: str):
        item = self.stat.get_item(uid)
        if not item:
            raise Exception(f"item {uid} not found")
        self._current_item = item
        self.stat.activate_item(item)
    
    def request_edit(self):
        if self._current_item and self._current_item.part_type in BEHAVE_RECTANGLE:
            self._editing_item = self._current_item.copy()
            ui: RectanglePartItem = self._current_item.ui
            if not self.stat.remove_item(self._current_item):
                raise Exception("unexpected condition")
            return SceneMode.EDIT_RECT, ui

    def request_next_item(self):
        if self._current_item and self._current_item.part_type in BAHAVE_REPEATABLE_INSERT:
            pre_item = self.stat.get_next_pre_item(self._current_item)
            self._pre_item = pre_item
            return get_scene_mode(pre_item)
        return SceneMode.SELECT
        
    def request_deep_copy(self):
        if self._current_item:
            self._deep_copy_item = self._current_item
            return SceneMode.DEEP_COPY

    def debug_print(self):
        print("============================")
        for item in self.stat.items:
            print(item)
        print(f"self._pre_item: {self._pre_item}")

    def to_dict(self):
        items = []
        for per_item in self.stat.items:
            items.append(per_item.to_dict())
        return {
            "background_image": self.io.image_path,
            "page": self.io.page_id,
            "items": items,
        }        

    def escape(self):
        self.is_repeating = False
        self._editing_item = None
        self._deep_copy_item = None

    def open_image(self):
        old_background, new_background = self.io.open_image()
        if new_background:
            self._items: list[PreItem] = []
            self._stat = ManagerStat(self._items)
            self.is_repeating = False
            self._pre_item: PreItem | None = None
            self._current_item: PreItem | None = None
            self._editing_item: PreItem | None = None
            self._deep_copy_item: PreItem | None = None
        return old_background, new_background

def get_ui(item: PreItem) -> RectanglePartItem:
    current_ui: RectanglePartItem | None = item.ui
    if current_ui:
        return current_ui
    if item.part_type in [REF_PART_ITEM, REF_QUESTION_ITEM, REF_UNIT_ITEM]:
        current_ui = ReferencePartItem(item)
    elif item.part_type in [WORD_BOUNDARY_ITEM, BOX_ITEM, CAPTION_ITEM]:
        current_ui = WordBoundaryPartItem(item)    
    else:
        print("Warning: No current_ui in get_ui()")
    return current_ui

def get_scene_mode(item_or_type: PreItem | str):
    part_type = None
    if isinstance(item_or_type, PreItem):
        part_type = item_or_type.part_type
    elif isinstance(item_or_type, str):
        part_type = item_or_type
    else:
        raise ValueError
    return SceneMode.DRAWING_RECT if part_type in BEHAVE_RECTANGLE else SceneMode.ADD_ITEM