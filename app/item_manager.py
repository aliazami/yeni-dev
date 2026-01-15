from PySide6.QtCore import QPointF
from PySide6.QtWidgets import (
    QInputDialog,
    QMessageBox,
)
from app.pre_item import PreItem
from app.constants import (
    PART_ITEM, QUESTION_REF_ITEM, PRE_ITEM, Q_WORD_BOUNDARY_PART_ITEM
)
from app.manager_helper import get_next
from app.components.part_item import PartItem
from app.components.question_ref_item import QuestionRefItem
from app.components.rectangle_part_item import RectanglePartItem
from app.components.word_boundary_part_item import WordBoundary


class ItemManager:
    def __init__(self):
        self.items: list[PreItem] = []
        self.is_repeating = False
        self._pre_item: PreItem | None = None
        self._current_item: PreItem | None = None
        self._editing_item: PreItem | None = None

    def get_item(self, uid: str):
        for item in self.items:
            if item.uid == uid:
                return item
            
    def add_item(self, item: PreItem):
        if self.get_item(item.uid):
            raise Exception(f"Duplicate pre-item")
        self.items.append(item.copy())

    
    def create(self, pos=None) -> RectanglePartItem | None:
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
        part_id = self.active_part_item.part_id if self.active_part_item else None
        if not self._current_item or not part_id:
            return
        kwargs = {
            "x": pos.x(),
            "y": pos.y(),
            "width": w,
            "height": h,
        }
        if self._current_item.part_type == QUESTION_REF_ITEM:
            part_type = Q_WORD_BOUNDARY_PART_ITEM
            qn = self._current_item.question_number
            max_qnn = self.get_max_qnn(part_id, qn, part_type)
            kwargs.update({"qn": qn, "qnn": max_qnn + 1}) 
        else:
            return
        pre_item = PreItem(part_type, part_id, **kwargs)
        self._pre_item = pre_item
        return self.create()
    
    def edit_rect(self, pos: QPointF, w: float, h: float):
        pre_item = self._editing_item
        pre_item.set_pos(pos.x(), pos.y())
        pre_item.width = w
        pre_item.height = h
        self._pre_item = pre_item
        return self.create()
    
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
            

    def activate_item(self, uid: str):
        item = self.get_item(uid)
        if not item:
            raise Exception(f"item {uid} not found")
        self._current_item = item
        if item.part_type in [Q_WORD_BOUNDARY_PART_ITEM]:
            for qnn in  self.question_child_items:
                qnn.is_active = (qnn.uid == item.uid)
        elif item.part_type == QUESTION_REF_ITEM:
            for qri in self.question_ref_items:
                qri.is_active = (qri.uid == item.uid)

            for qnn in  self.question_child_items:
                qnn.is_visible = (qnn.part_id == item.part_id and qnn.question_number == item.question_number)
                qnn.is_active = False
        elif item.part_type == PART_ITEM:
            for pi in self.part_items:
                pi.is_active = (pi.uid == item.uid)

            for qri in self.question_ref_items:
                qri.is_visible = (qri.part_id == item.part_id)
                qri.is_active = False
            for qnn in  self.question_child_items:
                qnn.is_visible = (qnn.part_id == item.part_id and qnn.question_number == item.question_number)
                qnn.is_active = False

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


    def pre_create_part_item(self) -> bool:
        part_id, ok = QInputDialog.getText(None, "Add Part Item", "Enter Unique ID:")
        if ok and part_id:
            kwargs = {}
            pre_item = PreItem(PART_ITEM, part_id, **kwargs)
            if self.get_item(pre_item.uid):
                QMessageBox.warning(None, "Error", "Exists!")
                return False
            else:
                self.is_repeating = True
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
            kwargs = {"qn": qn}
            pre_item = PreItem(QUESTION_REF_ITEM, part_id, **kwargs)
            if self.get_item(pre_item.uid):
                QMessageBox.warning(None, "Error", "Exists!")
                return False

            else:
                self.is_repeating = True
                self._pre_item = pre_item
                return True
            
        return False
    
    def pre_create_boundary(self):
        if not self.active_part_item:
            QMessageBox.warning(None, "Error", "Part?")
            return False
        if not self._current_item:
            QMessageBox.warning(None, "Error", "No Active Item")
            return False
        if self._current_item.part_type != QUESTION_REF_ITEM:
            QMessageBox.warning(None, "Error", "Question?")
            return False
        return True
    
    def request_edit(self):
        if self._current_item and self._current_item.part_type in [Q_WORD_BOUNDARY_PART_ITEM]:
            self._editing_item = self._current_item.copy()
            return "edit-rect", self._current_item
        
        return None,None

            
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

    def to_dict(self):
        output = []
        for per_item in self.items:
            output.append(per_item.to_dict())
        return output
    
    def get_max_qnn(self, part_id: str, qn: int, part_type: str):
        max_qnn = 0
        for qri in self.question_child_items:
            if qri.part_id == part_id and qri.question_number == qn and qri.part_type == part_type:
                max_qnn = max(max_qnn, qri.qnn)
        return max_qnn




def get_ui(item: PreItem) -> RectanglePartItem:
    current_ui: RectanglePartItem | None = item.ui
    if current_ui:
        return current_ui
    if item.part_type == PART_ITEM:
        current_ui = PartItem(item)
    elif item.part_type == QUESTION_REF_ITEM:
        current_ui = QuestionRefItem(item)
    elif item.part_type == Q_WORD_BOUNDARY_PART_ITEM:
        current_ui = WordBoundary(item)        
    else:
        print("Warning: No current_ui in get_ui()")
    return current_ui