from app.constants import (
    ITEM_CHILD_TYPES, REF_UNIT_ITEM, BEHAVE_INITIAL_VISIBLE, REF_ANSWER_PART_ITEM,
    BEHAVE_HAS_NO_PARENT, REF_PART_ITEM, REF_QUESTION_ITEM, CAPTION_ITEM
)
from app.pre_item import PreItem
from app.models import Delta
from app.helpers.part_item_helper import check_part_item
from app.helpers.utils import get_answer_from_line, get_answer_lines

class ManagerStat:

    def __init__(self):
        self.items: list[PreItem] = []
        self.answer_items: dict[str, PreItem] = {}
        self._is_dirty = False

    def get_item(self, uid: str):
        for obj in self.items:
            if obj.uid == uid:
                return obj
        return None

    def add_item(self, item: PreItem):
        if self.get_item(item.uid):
            raise Exception("Duplicate pre-item")
        self._is_dirty = True
        self.items.append(item.copy())

    def remove_item(self, item: str | PreItem):
        if isinstance(item, PreItem):
            uid = item.uid
        elif isinstance(item, str):
            uid = item
        else:
            raise ValueError
        item = self.get_item(uid)
        if not item:
            raise Exception(f"item {uid} not found")
        for child in self.get_descendants(item):
            self.items.remove(child)
        self.items.remove(item)
        self._is_dirty = True
        return True
    
    def activate_item(self, item: PreItem):
        ascendants = self.get_ascendants(item)
        siblings = self.get_siblings(item)
        children = self.get_children(item)
        visible_items = ascendants + siblings + children
        for other in self.items:
            other.is_visible = other.part_type in BEHAVE_INITIAL_VISIBLE or other in visible_items
            other.is_active = False
        item.is_visible = True
        item.is_active = True

    def show_descendants(self, item: PreItem):
        descendants = self.get_descendants(item)
        for other in self.items:
            other.is_visible = other.part_type in BEHAVE_INITIAL_VISIBLE or other in descendants
            other.is_active = False
        item.is_visible = True
        item.is_active = True    


    def get_ascendants(self, parent_item: PreItem):
        ascendants = [obj for obj in self.items if parent_item.is_my_ascendant(obj)]
        return ascendants
    
    def get_descendants(self, parent_item: PreItem):
        descendants = [obj for obj in self.items if parent_item.is_my_descendant(obj)]
        return descendants
    
    def get_children(self, parent: PreItem):
        children = [obj for obj in self.items if parent.is_my_child(obj)]
        return children
    
    def get_siblings(self, item: PreItem):
        siblings = [other for other in self.items if item.is_my_sibling(other)]
        return siblings
    
    def deep_copy_by_delta(self, item: PreItem, move_delta: Delta) -> list[PreItem]:
        root_item = self.get_next_pre_item(item, move_delta)
        # root_item.move(move_delta)
        item_list = [root_item]
        for descendant in self.get_descendants(item):
            d = descendant.data.copy()
            d.ui = None
            d.parent_id = d.parent_id.replace(item.uid, root_item.uid)
            new_child = PreItem(d)
            new_child.move(move_delta)
            item_list.append(new_child)
        return item_list
    
    def get_next_seq(self, parent_id: str, part_type: str) -> int:
        id_list = [obj.seq for obj in self.items if obj.parent_id == parent_id and obj.part_type == part_type]
        return get_next_id(id_list, 1)
    
    def get_next_pre_item(self, item: PreItem, move_delta: Delta = None):
        d = item.data.copy()
        d.ui = None
        d.active = False
        d.visible = True
        d.caption = None
        d.seq = self.get_next_seq(d.parent_id, d.part_type)
        next_item = PreItem(d)
        if move_delta:
            next_item.move(move_delta)
        return next_item
    
    def get_parent_ref_item(self, child_item: PreItem):
        for obj in self.items:
            if obj.part_type in [REF_PART_ITEM, REF_QUESTION_ITEM] and child_item.is_my_parent(obj):
                return obj
        
        return None
    
    def get_child_options(self, parent_item: PreItem):
        child_options = []
        for part_type in ITEM_CHILD_TYPES[parent_item.part_type]:
            next_seq = self.get_next_seq(parent_item.uid, part_type)
            option = (part_type, next_seq)
            child_options.append(option)
        return child_options
    
    def check_doc_is_ok(self):
        root_items = [obj for obj in self.items if obj.part_type in BEHAVE_HAS_NO_PARENT]
        for root_item in root_items:
            root_item_error = ""
            part_items = [obj for obj in self.get_children(root_item) if obj.part_type == REF_PART_ITEM]
            for part_item in part_items:
                descendants = self.get_descendants(part_item)
                check_part_item(part_item, descendants)
                part_item.refresh_ui()
                root_item_error = root_item_error or part_item.error
            root_item.child_error = root_item_error
            root_item.refresh_ui()

    def get_unique_unit_item(self):
        unit_items = [obj for obj in self.items if obj.part_type == REF_UNIT_ITEM]
        if len(unit_items) == 1:
            return unit_items[0]
        return len(unit_items)
    
    def bring_to_top(self, item: PreItem, one_step: bool):
        max_z_order = max([obj.z_order for obj in self.items])
        most_top_items = [obj for obj in self.items if obj.z_order == max_z_order]
        if len(most_top_items) == 1 and most_top_items[0] == item:
            return
        if one_step and item.z_order <= max_z_order:
            item.z_order += 1
        else:
            item.z_order = max_z_order + 1       
        
    def send_to_back(self, item: PreItem, one_step: bool):
        if one_step and item.z_order >= 0:
            item.z_order -= 1
        else:
            item.z_order = -1
        if item.z_order < 0: 
            min_z_order = min([obj.z_order for obj in self.items])
            for obj in self.items:
                obj.z_order = obj.z_order - min_z_order

    def get_is_dirty(self):
        return self._is_dirty or any([obj.is_dirty for obj in self.items])
    
    def signal_clear_dirty(self):
        self._is_dirty = False
    
    def get_has_answers(self):
        return any([obj.part_type == REF_ANSWER_PART_ITEM for obj in self.items])
    
    def is_gap_in_caption(self, item: PreItem):
        if item.part_type != CAPTION_ITEM:
            return False
        
    def get_part_answers(self, part_item: PreItem):
        def get_uid(seq):
            uid = f"{part_item.parent_id}::A{part_item.seq}::b{seq}"
            return uid
        if part_item.part_type != REF_PART_ITEM:
            raise Exception(f"{part_item} is not a part item")
        seq = 1
        items = []
        while block_item := self.answer_items.get(get_uid(seq)):
            if not block_item.caption_text:
                return items
            answer_lines = get_answer_lines(block_item.caption_text)
            items.extend((get_answer_from_line(line) for line in answer_lines))
            seq += 1
        return items


        
        

def get_next_str(value: str) -> str:
    """Return next integer or alphabet character."""
    if len(value) == 1 and value.isalpha():
        return chr(ord(value) + 1 - 26 * (value in 'zZ'))

    if value.isdigit():
        return str(int(value) + 1)

    raise ValueError(f"Invalid: '{value}'")

def get_next(value: str | int):
    if isinstance(value, int):
        return value + 1
    if isinstance(value, str):
        return get_next_str(value)
    raise ValueError

def get_next_id(id_list: list[str] | list[int], default: int | str = 1):
    for the_id in id_list:
        next_id = get_next(the_id)
        if next_id not in id_list:
            return next_id

    return default
