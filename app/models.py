from abc import abstractmethod
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtCore import QPointF


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


class IActive:
    _active_item = None

    @classmethod
    def get_active_item(cls):
        return cls._active_item

    @classmethod
    @abstractmethod
    def set_active_item(cls, items: list, **kwargs):
        pass

    @property
    @abstractmethod
    def is_active(self) -> str:
        pass


class IPartItem:
    _pre_item = None

    @property
    @abstractmethod
    def part_id(self) -> str:
        """Returns the dictionary representation of the item."""
        pass

    @property
    @abstractmethod
    def item_type(self) -> str:
        """Returns the dictionary representation of the item."""
        pass

    @property
    @abstractmethod
    def uid(self) -> str:
        pass

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
    @abstractmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        pass


class IQuestionItem(IPartItem):

    @property
    @abstractmethod
    def qn(self) -> int:
        """Returns the dictionary representation of the item."""
        pass

    @classmethod
    def get_max_qn(cls, items: list[QGraphicsItem], part_id: str) -> int:
        max_qn = 0
        for item in items:
            if isinstance(item, cls) and item.part_id == part_id:
                max_qn = max(max_qn, item.qn)
        return max_qn


class TPartItem(IPartItem):

    def __init__(self, item_type: str, part_id: str):
        self._part_id = part_id
        self._item_type = item_type

    @property
    def part_id(self) -> str:
        return self._part_id

    @property
    def item_type(self) -> str:
        return self._item_type

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

    @property
    def uid(self) -> str:
        return f"{self._item_type}::{self._part_id}::{self._qn}"

    @classmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        return cls._pre_item

    @property
    def kwargs(self):
        return self._kwargs
