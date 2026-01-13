from PySide6.QtCore import QPointF
from PySide6.QtWidgets import (
    QInputDialog,
    QMessageBox,
)
from app.pre_item import PreItem
from app.constants import (
    PART_ITEM, QUESTION_REF_ITEM, PRE_ITEM,
)
from app.manager_helper import check_repeat_id, get_next
from app.components.part_item import PartItem
from app.components.question_ref_item import QuestionRefItem
from app.components.rectangle_part_item import RectanglePartItem


class ItemManager:
    def __init__(self):
        self.items: list[PreItem] = []
        self.is_repeating = False
        self._pre_item: PreItem | None = None

    def get_item(self, uid: str):
        for item in self.items:
            if item.uid == uid:
                return item
            
    def add_item(self, item: PreItem):
        if self.get_item(item.uid):
            raise Exception(f"Duplicate pre-item")
        self.items.append(item.copy())

    
    def create(self, pos) -> RectanglePartItem | None:
        item = self._pre_item.copy()
        if not self.is_repeating:
            self._pre_item = None
        if not item:
            raise Exception(f"No pre-item exists in create phase")
        item.ui = get_ui(item, pos)
        # self.activate_item(item.uid)
        return item.ui

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
            self.items.remove(item)
            return True
            

    def activate_item(self, uid: str):
        item = self.get_item(uid)
        if not item:
            raise Exception(f"item {uid} not found")
        if item.part_type == QUESTION_REF_ITEM:
            for qri in self.question_ref_items:
                qri.is_active = (qri.uid == item.uid)
        elif item.part_type == PART_ITEM:
            for pi in self.part_items:
                pi.is_active = (pi.uid == item.uid)
            for qri in self.question_ref_items:
                qri.is_visible = (qri.part_id == item.part_id)
                qri.is_active = False

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


    def pre_create_part_item(self) -> bool:
        part_id, ok = QInputDialog.getText(None, "Add Part Item", "Enter Unique ID:")
        if ok and part_id:
            is_repeating, part_id = check_repeat_id(part_id)
            kwargs = {}
            pre_item = PreItem(PART_ITEM, part_id, **kwargs)
            if self.get_item(pre_item.uid):
                QMessageBox.warning(None, "Error", "Exists!")
                return False
            else:
                self.is_repeating = is_repeating
                self._pre_item = pre_item
                return True

        return False
    
    def pre_create_question_ref_item(self) -> bool:
        part_id = self.active_part_item.part_id if self.active_part_item else None
        if not part_id:
            QMessageBox.warning(None, "Error", "No Part Item Selected.")
            return False

        default_int = 1
        for item in self.question_ref_items:
            if item.part_id == part_id:
                default_int = max(default_int, item.question_number)
        qn, ok = QInputDialog.getInt(
            None, "Add Gap Item", "Sequence:", value=default_int, minValue=1
        )
        if ok:
            ir_repeating, qn = check_repeat_id(qn)
            kwargs = {"qn": qn}
            pre_item = PreItem(QUESTION_REF_ITEM, part_id, **kwargs)
            if self.get_item(pre_item.uid):
                QMessageBox.warning(None, "Error", "Exists!")
                return False

            else:
                self.is_repeating = ir_repeating
                self._pre_item = pre_item
                return True
            
        return False
            
    def repeat(self):

        if not self._pre_item or not self._pre_item.repeatable:
            raise Exception(f"No pre-item exists in repeat phase")

        part_id = self._pre_item.part_id
        part_type = self._pre_item.part_type
        kwargs = self._pre_item.kwargs
        if part_type in [PART_ITEM]:
            part_id = get_next(part_id)
        elif part_type in [QUESTION_REF_ITEM]:
            last_qn = self._pre_item.question_number
            qn = int(get_next(str(last_qn)))
            kwargs["qn"] = qn
        self._pre_item = PreItem(part_type, part_id, **kwargs)
       

    def debug_print(self):
        print("============================")
        for item in self.items:
            print(item)
        print(f"self._pre_item: {self._pre_item}")


def get_ui(item: PreItem, pos: QPointF=None) -> RectanglePartItem:
    current_ui: RectanglePartItem | None = item.ui
    if current_ui:
        return current_ui
    if pos is None:
        pos = item.pos
    if item.part_type == PART_ITEM:
        current_ui = PartItem(item, pos)
    elif item.part_type == QUESTION_REF_ITEM:
        current_ui = QuestionRefItem(item, pos)
    return current_ui