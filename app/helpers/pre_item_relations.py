from app.pre_item import PreItem

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
