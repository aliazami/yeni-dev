from PySide6.QtCore import QPointF
from PySide6.QtWidgets import (
    QInputDialog,
    QMessageBox,
    QDialog,
)
from app.pre_item import PreItem
from app.constants import (
    PART_ITEM, QUESTION_REF_ITEM, SceneMode, Q_WORD_BOUNDARY_PART_ITEM,
    OPTION_REF_ITEM
)
from app.components.part_item import PartItem
from app.components.question_ref_item import QuestionRefItem
from app.components.rectangle_part_item import RectanglePartItem
from app.components.word_boundary_part_item import WordBoundary
from app.dialogs import PartSelectDialog
from app.managet_stat import ManagerStat, get_next_str

class ItemManager:
    def __init__(self):
        self._items: list[PreItem] = []
        self.stat = ManagerStat(self._items)
        self.is_repeating = False
        self._pre_item: PreItem | None = None
        self._current_item: PreItem | None = None
        self._editing_item: PreItem | None = None
    
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
        part_id = self.stat.active_part_item.part_id if self.stat.active_part_item else None
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
            next_qnn = self.stat.get_next_qnn(part_id, qn, part_type)
            kwargs.update({"qn": qn, "qnn": next_qnn}) 
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
    




    def pre_create_part_item(self):
        next_part_id = self.stat.get_next_part_id()
        part_id, ok = QInputDialog.getText(None, "Add Part Item", "Enter Unique ID:", text=next_part_id)
        if ok and part_id:
            kwargs = {}
            pre_item = PreItem(PART_ITEM, part_id, **kwargs)
            if self.stat.get_item(pre_item.uid):
                QMessageBox.warning(None, "Error", "Exists!")
            else:
                self.is_repeating = True
                self._pre_item = pre_item
                return SceneMode.ADD_ITEM
    
    def activate_item(self, uid: str):
        item = self.stat.get_item(uid)
        if not item:
            raise Exception(f"item {uid} not found")
        self._current_item = item
        if item.part_type in [Q_WORD_BOUNDARY_PART_ITEM]:
            for qnn in  self.stat.question_child_items:
                qnn.is_active = (qnn.uid == item.uid)
        elif item.part_type == QUESTION_REF_ITEM:
            for qri in self.stat.question_ref_items:
                qri.is_active = (qri.uid == item.uid)

            for qnn in self.stat.question_child_items:
                qnn.is_visible = (qnn.part_id == item.part_id and qnn.question_number == item.question_number)
                qnn.is_active = False
        elif item.part_type == PART_ITEM:
            for pi in self.stat.part_items:
                pi.is_active = (pi.uid == item.uid)

            for qri in self.stat.question_ref_items:
                qri.is_visible = (qri.part_id == item.part_id)
                qri.is_active = False
            for qnn in  self.stat.question_child_items:
                qnn.is_visible = (qnn.part_id == item.part_id and qnn.question_number == item.question_number)
                qnn.is_active = False
    
    def pre_create_part_child_item(self):
        part_id = self.stat.active_part_item.part_id if self.stat.active_part_item else None
        kwargs = None
        child_options = None
        if not part_id:
            if len(self.stat.part_items) == 0:
                return self.pre_create_part_item()
            else:
                QMessageBox.warning(None, "Error", "No Part Item Selected.")
                return
        part_type = self._current_item.part_type
        part_id = self._current_item.part_id
        question_number = self._current_item.question_number
        if part_type == PART_ITEM:
            next_question_number = self.stat.get_next_question_number(part_id)
            next_question_option = "b"
            child_options = [
                (QUESTION_REF_ITEM, next_question_number),
                (OPTION_REF_ITEM, next_question_option),
            ]
        elif part_type == QUESTION_REF_ITEM:
            next_q_word_boundary = self.stat.get_next_qnn(part_id, question_number, part_type)
            child_options = [
                (Q_WORD_BOUNDARY_PART_ITEM, next_q_word_boundary),
            ]


        if not child_options:
            raise Exception("expected child_options")

        dialog = PartSelectDialog(child_options)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            r_part_type, r_id = dialog.get_data()
            if r_part_type == QUESTION_REF_ITEM:
                qn = int(r_id)
                kwargs = {"qn": qn}
            # other types are added bellow #
            # other types are added bellow #
            # other types are added bellow #
            if kwargs:
                kwargs = {"qn": qn}
                pre_item = PreItem(QUESTION_REF_ITEM, part_id, **kwargs)
                if self.stat.get_item(pre_item.uid):
                    QMessageBox.warning(None, "Error", "Exists!")
                else:
                    self.is_repeating = True
                    self._pre_item = pre_item
                    return SceneMode.ADD_ITEM
    
    def pre_create_boundary(self):
        if not self.stat.active_part_item:
            QMessageBox.warning(None, "Error", "Part?")
            return 
        if not self._current_item:
            QMessageBox.warning(None, "Error", "No Active Item")
            return
        if self._current_item.part_type != QUESTION_REF_ITEM:
            QMessageBox.warning(None, "Error", "Question?")
            return
        return SceneMode.DRAWING_RECT
    
    def request_edit(self):
        if self._current_item and self._current_item.part_type in [Q_WORD_BOUNDARY_PART_ITEM]:
            self._editing_item = self._current_item.copy()
            ui: RectanglePartItem = self._current_item.ui
            if not self.stat.remove_item(self._current_item):
                raise Exception("unexpected condition")
            return SceneMode.DRAWING_RECT, ui


            
    def repeat(self):

        if not self._pre_item or not self._pre_item.repeatable:
            raise Exception(f"No pre-item exists in repeat phase")

        part_id = self._pre_item.part_id
        part_type = self._pre_item.part_type
        kwargs = self._pre_item.kwargs
        if part_type in [PART_ITEM]:
            part_id = get_next_str(part_id)
        elif part_type in [QUESTION_REF_ITEM]:
            last_qn = self._pre_item.question_number
            qn = int(get_next_str(str(last_qn)))
            kwargs["qn"] = qn
        self._pre_item = PreItem(part_type, part_id, **kwargs)
       

    def debug_print(self):
        print("============================")
        for item in self.stat.items:
            print(item)
        print(f"self._pre_item: {self._pre_item}")

    def to_dict(self):
        output = []
        for per_item in self.stat.items:
            output.append(per_item.to_dict())
        return output
    





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