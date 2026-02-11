from app.pre_item import PreItem
from app.constants import (
    REF_QUESTION_ITEM, ALL_PLACE_HOLDER_ITEMS
)

class PreItemRelations:
    def __init__(self, items: list[PreItem] | dict[str, PreItem]):
        self.items: dict[str, PreItem] = {}
        if isinstance(items, dict):
            self.items = items.copy()
        elif isinstance(items, list):
            for obj in items:
                self.items[obj.uid] = obj

    def get_item(self, uid: str):
        return self.items.get(uid)

    def add_item(self, item: PreItem):
        self.items[item.uid] = item
        
    def remove_item(self, item_or_uid: str | PreItem):
        if isinstance(item_or_uid, str):
            item = self.items.get(item_or_uid)
        elif isinstance(item_or_uid, PreItem):
            item = self.items.get(item_or_uid.uid)
        else:
            raise ValueError
        if not item:
            raise ValueError
        for child in self.get_descendants(item):
            self.items.pop(child.uid)
        self.items.pop(item.uid)
    
    def get_ascendants(self, parent_item: PreItem):
        ascendants = [obj for obj in self.items.values() if parent_item.is_my_ascendant(obj)]
        return ascendants
    
    def get_descendants(self, parent_item: PreItem):
        descendants = [obj for obj in self.items.values() if parent_item.is_my_descendant(obj)]
        return descendants
    
    def get_children(self, parent: PreItem):
        children = [obj for obj in self.items.values() if parent.is_my_child(obj)]
        return children
    
    def get_siblings(self, item: PreItem):
        siblings = [other for other in self.items.values() if item.is_my_sibling(other)]
        return siblings
    
    def get_all_by_type(self, part_type: str):
        return [obj for obj in self.items.values() if obj.part_type == part_type]
    
    def get_all_by_types(self, part_types: list[str] | set[str]):
        return [obj for obj in self.items.values() if obj.part_type in part_types]

    def find_first_place_holder_by_question_seq(self, seq: int):
        question_item = next((obj for obj in self.items.values() if obj.seq == seq and obj.part_type == REF_QUESTION_ITEM), None)
        return next((obj for obj in self.items.values() if obj.is_my_parent(question_item) and obj.part_type in ALL_PLACE_HOLDER_ITEMS), None)

    def find_children_by_types(self, parent: PreItem, types: list[str]):
        return [obj for obj in self.items.values() if obj.is_my_parent(parent) and obj.part_type in types]

    def find_child(self, seq: int, types):
        return ((obj for obj in self.items.values() if obj.seq == seq and obj.part_type in types), None)