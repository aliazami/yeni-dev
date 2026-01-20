from app.constants import (
    REF_PART_ITEM, REF_QUESTION_ITEM, WORD_BOUNDARY_ITEM, 
    ITEM_CHILD_TYPES, REF_ANSWER_ITEM, REF_OPTION_ITEM, REF_UNIT_ITEM, BAHAVE_INITIAL_VISIBLE
)
from app.pre_item import PreItem
from app.models import Delta

class ManagerStat:

    def __init__(self, items: list[PreItem]):
        self.items = items

    def get_item(self, uid: str):
        for item in self.items:
            if item.uid == uid:
                return item
            
    def add_item(self, item: PreItem):
        if self.get_item(item.uid):
            raise Exception(f"Duplicate pre-item")
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
        for child in self.get_decendents(item):
            self.items.remove(child)
        self.items.remove(item)
        return True
    
    def activate_item(self, item: PreItem):
        ascendants = self.get_acendents(item)
        siblings = self.get_siblings(item)
        children = self.get_children(item)
        visible_items = ascendants + siblings + children
        for other in self.items:
            other.is_visible = other.part_type in BAHAVE_INITIAL_VISIBLE or other in visible_items
            other.is_active = False
        item.is_visible = True
        item.is_active = True

    
    def get_acendents(self, parent_item: PreItem):
        acendants = [item for item in self.items if parent_item.is_my_ascendant(item)]
        return acendants
    
    def get_decendents(self, parent_item: PreItem):
        decendants = [item for item in self.items if parent_item.is_my_descendant(item)]
        return decendants
    
    def get_children(self, parent: PreItem):
        children = [item for item in self.items if parent.is_my_child(item)]
        return children
    
    def get_siblings(self, item: PreItem):
        siblings = [other for other in self.items if item.is_my_sibling(other)]
        return siblings
    
    def deep_copy_by_delta(self, item: PreItem, move_delta: Delta) -> list[PreItem]:
        root_item = self.get_next_pre_item(item, move_delta)
        # root_item.move(move_delta)
        item_list = [root_item]
        for decendent in self.get_decendents(item):
            d = decendent.data.copy()
            d.ui = None
            d.parent_id = d.parent_id.replace(item.uid, root_item.uid)
            new_child = PreItem(d)
            new_child.move(move_delta)
            item_list.append(new_child)
        return item_list
    
    def get_next_seq(self, parent_id: str, part_type: str) -> int:
        id_list = [item.seq for item in self.items if item.parent_id == parent_id and item.part_type == part_type]
        return get_next_id(id_list, 1)
    
    def get_next_pre_item(self, item: PreItem, move_delta: Delta = None):
        d = item.data.copy()
        d.ui = None
        d.active = False
        d.visible = True
        d.seq = self.get_next_seq(d.parent_id, d.part_type)
        next_item = PreItem(d)
        if move_delta:
            next_item.move(move_delta)
        return next_item
    
    def get_child_options(self, parent_item: PreItem):
        child_options = []
        for part_type in ITEM_CHILD_TYPES[parent_item.part_type]:
            next_seq = self.get_next_seq(parent_item.uid, part_type)
            option = (part_type, next_seq)
            child_options.append(option)
        return child_options
    
    def get_unique_unit_item(self):
        unit_items = [item for item in self.items if item.part_type == REF_UNIT_ITEM]
        if len(unit_items) == 1:
            return unit_items[0]
        return len(unit_items)


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
