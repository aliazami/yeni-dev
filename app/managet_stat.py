from app.constants import PART_ITEM, QUESTION_REF_ITEM, Q_WORD_BOUNDARY_PART_ITEM
from app.pre_item import PreItem

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

    def remove_item(self, uid: str):
        item = self.get_item(uid)
        if not item:
            raise Exception(f"item {uid} not found")
        if item.part_type == PART_ITEM:
            for qri in self.question_ref_items:
                if qri.part_id == item.part_id:
                    return False

            self.items.remove(item)
            return True

        elif item.part_type == QUESTION_REF_ITEM:
            for qnn in self.question_child_items:
                if qnn.question_number == item.question_number:
                    return False
            self.items.remove(item)
            return True
        
        elif item.part_type in [Q_WORD_BOUNDARY_PART_ITEM]:
            self.items.remove(item)
            return True
        else:
            print("Warning no type detected to delete")
                    

    @property
    def part_items(self):
        return [item for item in self.items if item.part_type == PART_ITEM]
    
    @property
    def active_part_item(self):
        for pi in self.part_items:
            if pi.is_active:
                return pi
    
    @property
    def question_ref_items(self):
        return [item for item in self.items if item.part_type == QUESTION_REF_ITEM]

    @property
    def question_child_items(self):
        return [item for item in self.items if item.qnn]

    def get_next_part_id(self) -> str:
        id_list = [item.part_id for item in self.part_items]
        return get_next_id(id_list, "1")
    
    def get_next_question_number(self, part_id: str) -> int:
        id_list = [item.question_number for item in self.question_ref_items if item.part_id == part_id]
        return get_next_id(id_list, 1)
    
    def get_next_qnn(self, part_id: str, question_number: int, part_type: str) -> int:
        id_list = [item.qnn for item in self.items if item.part_id == part_id and item.question_number == question_number and item.part_type == part_type and item.qnn is not None]
        return get_next_id(id_list, 1)



def get_next_id(id_list: list[str] | list[int], default: int | str = 1):
    for the_id in id_list:
        next_id = get_next(the_id)
        if next_id not in id_list:
            return next_id

    return default

def get_next(value: str | int):
    if isinstance(value, int):
        return value + 1
    if isinstance(value, str):
        return get_next_str(value)
    raise ValueError

def get_next_str(value: str) -> str:
    """Return next integer or alphabet character."""
    if len(value) == 1 and value.isalpha():
        return chr(ord(value) + 1 - 26 * (value in 'zZ'))

    if value.isdigit():
        return str(int(value) + 1)

    raise ValueError(f"Invalid: '{value}'")                