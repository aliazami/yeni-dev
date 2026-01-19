from app.constants import (
    PART_ITEM, QUESTION_REF_ITEM, Q_WORD_BOUNDARY_PART_ITEM, 
    CHILD_TYPES, ANSWER_PART_ITEM, OPTION_REF_ITEM, PAGE_REF_ITEM
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
        if item.part_type == PART_ITEM:
            for qri in self.question_ref_items:
                if qri.part_id == item.part_id:
                    return False

            self.items.remove(item)
            return True

        elif item.part_type == QUESTION_REF_ITEM:
            for qnn in self.all_question_child_items:
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
    def answer_part_items(self):
        return [item for item in self.items if item.part_type == ANSWER_PART_ITEM]    
    
    @property
    def active_part_item(self):
        for pi in self.part_items:
            if pi.is_active:
                return pi

    @property
    def question_ref_items(self):
        return [item for item in self.items if item.part_type == QUESTION_REF_ITEM]

    def part_child_items(self, parent_item: PreItem):
        return [item for item in self.items if item.part_type in CHILD_TYPES[PART_ITEM] and item.part_id == parent_item.part_id]
    

    def get_decendents(self, parent_item: PreItem):
        part_type = parent_item.part_type
        if not CHILD_TYPES[part_type]:
            return []
        part_id = parent_item.part_id
        question_number = parent_item.question_number
        screen1 = [item for item in self.items if item.part_id == part_id and item.part_type != PART_ITEM]
        if part_type == PART_ITEM:
            return screen1
        screen2 = [item for item in screen1 if \
                   question_number and item.question_number == question_number \
                   and item.part_type != QUESTION_REF_ITEM
                   ]
        if part_type == QUESTION_REF_ITEM:
            return screen2
        
        raise Exception(f"not implemented for {part_type}")
        
    @property
    def all_question_child_items(self):
        return [item for item in self.items if item.part_type in CHILD_TYPES[QUESTION_REF_ITEM]]
    
    def deep_copy_by_delta(self, item: PreItem, move_delta: Delta) -> list[PreItem]:
        root_item = self.get_next_pre_item(item, move_delta)
        # root_item.move(move_delta)
        item_list = [root_item]
        for decendent in self.get_decendents(item):
            part_id = root_item.part_id
            part_type = decendent.part_type
            kwargs = decendent.kwargs.copy()
            kwargs["ui"] = None
            if root_item.question_number:
                kwargs["qn"] = root_item.question_number
            if root_item.qnn:
                kwargs["qnn"] = root_item.qnn
            new_child = PreItem(part_type, part_id, **kwargs)
            new_child.move(move_delta)
            item_list.append(new_child)
        return item_list

    def get_next_part_id(self) -> str:
        id_list = [item.part_id for item in self.part_items]
        return get_next_id(id_list, "1")
    
    def get_next_answer_part_id(self, page_id: str | None) -> str:
        if page_id:
            id_list = [item.part_id for item in self.answer_part_items if item.page_id == page_id]
        else:
            id_list = [item.part_id for item in self.answer_part_items]
        return get_next_id(id_list, "001")

    def get_next_question_number(self, part_id: str) -> int:
        id_list = [item.question_number for item in self.question_ref_items if item.part_id == part_id]
        return get_next_id(id_list, 1)

    def get_next_qnn(self, part_id: str, question_number: int, part_type: str) -> int:
        id_list = [item.qnn for item in self.items if item.part_id == part_id and item.question_number == question_number and item.part_type == part_type and item.qnn is not None]
        return get_next_id(id_list, 1)
    
    def get_next_pre_item(self, item: PreItem, move_delta: Delta = None):
        kwargs = item.kwargs.copy()
        kwargs["ui"] = None
        kwargs["active"] = False
        kwargs["visible"] = True
        part_type = item.part_type
        part_id = item.part_id
        question_number = item.question_number
        if part_type == PART_ITEM:
            part_id = self.get_next_part_id()
        elif part_type == QUESTION_REF_ITEM:
            kwargs["qn"] = self.get_next_question_number(part_id)
        elif part_type in CHILD_TYPES[QUESTION_REF_ITEM]:
            kwargs["qnn"] = self.get_next_qnn(part_id, question_number, part_type)
        else:
            raise Exception("unexpected type")
        next_item = PreItem(part_type, part_id, **kwargs)
        if move_delta:
            next_item.move(move_delta)
        return next_item
    
    def get_child_options(self, item: PreItem):
        page_id = item.page_id
        part_type = item.part_type
        part_id = item.part_id
        question_number = item.question_number
        if part_type == PART_ITEM:
            next_question_number = self.get_next_question_number(part_id)
            next_question_option = "b"
            child_options = [
                (QUESTION_REF_ITEM, next_question_number),
                (OPTION_REF_ITEM, next_question_option),
            ]
        elif part_type == PAGE_REF_ITEM:
            next_answer_part_id = self.stat.get_next_answer_part_id(page_id)
            child_options = [
                (ANSWER_PART_ITEM, next_answer_part_id),
            ]            
        elif part_type == QUESTION_REF_ITEM:
            next_q_word_boundary = self.stat.get_next_qnn(part_id, question_number, Q_WORD_BOUNDARY_PART_ITEM)
            child_options = [
                (Q_WORD_BOUNDARY_PART_ITEM, next_q_word_boundary),
            ]


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



