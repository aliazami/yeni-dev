from PySide6.QtCore import QPointF
from easyocr import Reader
from PySide6.QtWidgets import (
    QInputDialog,
    QMessageBox,
    QDialog,
)
from app.pre_item import PreItem
from app.constants import (
    REF_PART_ITEM, SceneMode, REF_UNIT_ITEM,
    BEHAVE_REPEATABLE_INSERT, BEHAVE_RECTANGLE, ITEM_CHILD_TYPES,
    BEHAVE_HAS_NO_PARENT, BEHAVE_HAS_CAPTION, BEHAVE_READABLE,
    BEHAVE_CENTER_NUMBER, BEHAVE_TOP_LEFT_CAPTION, BEHAVE_ANSWER_ITEMS, ALL_INPUT_TYPES,
    INPUT_CHILD_TYPES
)
from app.components.reference_part_item import ReferencePartItem
from app.components.rectangle_part_item import RectanglePartItem
from app.components.word_boundary_part_item import WordBoundaryPartItem
from app.dialogs import PartSelectDialog, CaptionEditDialog, InputSelectDialog
from app.models import Delta, PreItemData, Input
from app.manager_stat import ManagerStat
from app.manager_io import ManagerIO
from app.helpers.ocr import ImageReader


class ItemManager:
    def __init__(self):
        self._stat = ManagerStat()
        self.io = ManagerIO()
        self.is_repeating = False
        self._pre_item: PreItem | None = None
        self._current_item: PreItem | None = None
        self._editing_item: PreItem | None = None
        self._deep_copy_item: PreItem | None = None
        self.image_reader = ImageReader()

    def escape(self):
        self.is_repeating = False
        self._editing_item = None
        self._deep_copy_item = None

    def _clear(self):
        # self.io = ManagerIO()   <preserved>
        # self.image_reader = ImageReader() <preserved>
        self._stat = ManagerStat()
        self._pre_item = None
        self._current_item = None
        self.escape()

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
        new_uis: list[RectanglePartItem] = []
        for new_item in new_items:
            self._pre_item = new_item
            new_uis.append(self.create())
        return new_uis 

    def select_input_type(self):
        item = self._current_item
        if not item:
            return
        input_types: set[str] = set()
        for input_type in ALL_INPUT_TYPES:
            if item.part_type in INPUT_CHILD_TYPES[input_type]:
                input_types.add(input_type)
        if len(input_types) < 1:
            return
        dialog = InputSelectDialog(input_types, None)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            input_type = dialog.get_data()
            item.input = Input(input_type)
            self.stat.check_doc_is_ok()

    def pre_create_item(self, part_type: str | None = None, parent_item: PreItem | None = None, auto_seq = False):
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
                return None
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
            next_seq = self.stat.get_next_seq(parent_item.uid, part_type)
            if auto_seq:
                seq, ok = next_seq, True
            else:
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
                self.is_repeating = part_type in BEHAVE_REPEATABLE_INSERT
                self._pre_item = pre_item
                return get_scene_mode(pre_item)
        return None

    def activate_item(self, uid: str):
        item = self.stat.get_item(uid)
        if not item:
            raise Exception(f"item {uid} not found")
        self._current_item = item
        self.stat.activate_item(item)
    
    def request_redraw_rect(self):
        if self._current_item and self._current_item.part_type in BEHAVE_RECTANGLE:
            self._editing_item = self._current_item.copy()
            ui: RectanglePartItem = self._current_item.ui
            if not self.stat.remove_item(self._current_item):
                raise Exception("unexpected condition")
            return SceneMode.EDIT_RECT, ui
        return None

    def request_next_item(self):
        if self._current_item and self._current_item.part_type in BEHAVE_REPEATABLE_INSERT:
            pre_item = self.stat.get_next_pre_item(self._current_item)
            self._pre_item = pre_item
            return get_scene_mode(pre_item)
        return SceneMode.SELECT
        
    def request_deep_copy(self):
        if self._current_item:
            self._deep_copy_item = self._current_item
            return SceneMode.DEEP_COPY
        return None

    def bring_to_top(self, one_step: bool):
        item = self._current_item
        if not item:
            return
        max_z_order = max([obj.z_order for obj in self.stat.items])
        most_top_items = [obj for obj in self.stat.items if obj.z_order == max_z_order]
        if len(most_top_items) == 1 and most_top_items[0] == item:
            return
        if one_step and item.z_order <= max_z_order:
            item.z_order += 1
        else:
            item.z_order = max_z_order + 1       
        
    def send_to_back(self, one_step: bool):
        item = self._current_item
        if not item:
            return        
        if one_step and item.z_order >= 0:
            item.z_order -= 1
        else:
            item.z_order = -1
        if item.z_order < 0: 
            min_z_order = min([obj.z_order for obj in self.stat.items])
            for obj in self.stat.items:
                obj.z_order = obj.z_order - min_z_order
    
    def edit_item(self):
        if self._current_item and self._current_item.part_type in BEHAVE_HAS_CAPTION:
            md_text = self._current_item.caption.text if self._current_item.caption else ""
            dialog = CaptionEditDialog(md_text)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self._current_item.set_caption(dialog.get_mark_down())

    def debug_print(self):
        print("============================")
        for obj in self.stat.items:
            print(obj)
        print(f"self._pre_item: {self._pre_item}")

    def to_dict(self):
        items = []
        answer_items = []
        contains_answer = self.stat.get_has_answers()
        for pre_item in self.stat.items:
            if contains_answer and pre_item.part_type in BEHAVE_ANSWER_ITEMS:
                answer_items.append(pre_item)
            items.append(pre_item.to_dict())
        return {
            "background_image": self.io.image_path,
            "page": self.io.page_id,
            "items": items,
        }        

    def open_image(self):
        old_background, new_background, data_json, answer_json = self.io.open_image()
        ui_items = []
        if new_background:
            self._clear()
            if data_json:
                for item_data in data_json.get("items", []):
                    ui_item = self.create_from_dict(item_data)
                    if ui_item:
                        ui_items.append(ui_item)
                if isinstance(answer_json, dict):
                    self.stat.answer_items.update(answer_json)
        return old_background, new_background, ui_items
    
    def read_item(self):
        item = self._current_item
        if not item:
            return None
        success = 0
        failed = 0
        result = self.read_content(item, self.io.image_path)
        if isinstance(result, bool) and result == True:
            success += 1
        elif result == False:
            failed += 1
        for obj in self.stat.get_descendants(item):
            result = self.read_content(obj, self.io.image_path)
            if isinstance(result, bool) and result == True:
                success += 1
            elif result == False:
                failed += 1
        QMessageBox.information(None, "Completed", f"Success: {success}, Failed: {failed}")
        return None

    def get_doc_title(self):
        doc_title = "No page"
        is_dirty = self.stat.get_is_dirty()
        if self.io.image_name:
            star = "*" if is_dirty else ""
            doc_title = self.io.image_name + star
        return doc_title

    def read_all_items(self):
        for obj in self.stat.items:
            if obj.part_type in BEHAVE_READABLE and not obj.caption_text:
                self.read_content(obj, self.io.image_path)

    def read_content(self, item:PreItem, image_path: str):
        
        if item.part_type not in BEHAVE_READABLE:
            return None
        
        if not item.pos or not item.width or not item.height:
            return False
        x1 = int(item.pos.x())
        y1 = int(item.pos.y())
        x2 = int(x1 + item.width)
        y2 = int(y1 + item.height)
        rect = (x1, y1, x2, y2)
        result = False
        if rect and image_path:
            item.refresh_ui()
            text = self.image_reader.read_image(image_path, rect)
            if text:
                item.set_caption(text)
                result = True
            item.refresh_ui()
        return result                    


def get_ui(item: PreItem) -> RectanglePartItem:
    current_ui: RectanglePartItem | None = item.ui
    if current_ui:
        return current_ui
    if item.part_type in BEHAVE_CENTER_NUMBER:
        current_ui = ReferencePartItem(item)
    elif item.part_type in BEHAVE_TOP_LEFT_CAPTION:
        current_ui = WordBoundaryPartItem(item)    
    else:
        current_ui = None
        QMessageBox.warning(None, "Error", f"Warning: No {item.part_type} in get_ui()")
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