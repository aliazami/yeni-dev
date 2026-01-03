from abc import abstractmethod
from PySide6.QtWidgets import QGraphicsItem, QMessageBox, QInputDialog, QGraphicsRectItem
from PySide6.QtCore import QPointF
from app.constants import T_QUESTION_ITEM, KEY_TYPE, KEY_QN, KEY_PART_ID, KEY_IS_ACTIVE
from app.helpers.utils import get_next


class ISerializable:
    """Mixin for items that can be saved/loaded."""

    @abstractmethod
    def to_dict(self) -> dict:
        """Returns the dictionary representation of the item."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict):
        """Creates an instance of the class from a dictionary."""
        pass


class IRepeatable:
    _is_repeating = False

    @property
    def is_repeating(self) -> bool:
        return self._is_repeating
    
    @classmethod
    def cancel_repeating(cls):
        cls._is_repeating = False

    @classmethod
    @abstractmethod
    def repeat(cls):
        pass


class IPartItem(QGraphicsRectItem):
    _pre_item = None

    @property
    def uid(self) -> str:
        return f"{self.item_type}::{self.part_id}"

    @property
    def part_id(self) -> str:
        return self.data(KEY_PART_ID)

    @property
    def item_type(self) -> str:
        return self.data(KEY_TYPE)

    @classmethod
    def has_item(cls, items: list[QGraphicsItem], temp_item) -> bool:
        if not isinstance(temp_item, IPartItem):
            return False

        return any(
            isinstance(item, cls) and item.uid == temp_item.uid
            for item in items
        )

    @classmethod
    def pre_create(cls, items: list[QGraphicsItem], part_id: str, **kwargs) -> bool:
        return False

    @classmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        pass


class IActivePartItem(IPartItem):
    _active_item = None

    @classmethod
    def get_active_item(cls):
        return cls._active_item

    @classmethod
    @abstractmethod
    def set_active_item(cls, items: list, **kwargs):
        pass

    @property
    def is_active(self) -> str:
        return self.data(KEY_IS_ACTIVE)


class IQuestionItem(IPartItem):

    def uid(self) -> str:
        return f"{self.item_type}::{self.part_id}::{self.qn}"

    @property
    def qn(self) -> int:
        return self.data(KEY_QN)

    @classmethod
    def get_max_qn(cls, items: list[QGraphicsItem], part_id: str) -> int:
        max_qn = 0
        for item in items:
            if isinstance(item, cls) and item.part_id == part_id:
                max_qn = max(max_qn, item.qn)
        return max_qn

    @classmethod
    def pre_create(cls, items: list[QGraphicsItem], part_id: str, **kwargs) -> bool:
        if not part_id:
            QMessageBox.warning(None, "Error", "No Circle Selected.")
            return False
        default_int = cls.get_max_qn(items, part_id) + 1
        qn, ok = QInputDialog.getInt(
            None, "Add Gap Item", "Sequence:", value=default_int, minValue=1
        )
        if ok:
            if qn > 999 and qn % 1000 == 0:
                cls._is_repeating = True
                qn = qn / 1000
            pre_item = TQuestionItem(T_QUESTION_ITEM, part_id, qn)
            if cls.has_item(items, pre_item):
                QMessageBox.warning(None, "Error", "Exists!")
                return False

            else:
                cls._pre_item = pre_item
                return True

        return False


class IRepeatableQuestionItem(IRepeatable, IQuestionItem):

    @property
    def part_id(self) -> str:
        return ""

    @property
    def item_type(self) -> str:
        return ""

    @property
    def qn(self) -> int:
        return 0

    @classmethod
    def repeat(cls):
        index = cls._pre_item.qn
        part_id = cls._pre_item.part_id
        qn = int(get_next(str(index)))
        next_pre_item = TQuestionItem(T_QUESTION_ITEM, part_id, qn)
        cls._pre_item = next_pre_item


class TPartItem(IPartItem):

    def __init__(self, item_type: str, part_id: str):
        self._part_id = part_id
        self._item_type = item_type

    @property
    def item_type(self) -> str:
        return self._item_type

    @property
    def part_id(self) -> str:
        return self._part_id

    @property
    def uid(self) -> str:
        return f"{self._item_type}::{self._part_id}"

    @classmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        return cls._pre_item


class TQuestionItem(IQuestionItem):

    def __init__(self, item_type: str, part_id: str, qn: int, **kwargs):
        self._part_id = part_id
        self._qn = qn
        self._item_type = item_type
        self._kwargs = kwargs

    @property
    def part_id(self) -> str:
        return self._part_id

    @property
    def item_type(self) -> str:
        return self._item_type

    @property
    def qn(self) -> int:
        return int(self._qn)

    @classmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        return cls._pre_item

    @property
    def kwargs(self):
        return self._kwargs
