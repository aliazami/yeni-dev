from abc import abstractmethod


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


class IPartItem:
    @abstractmethod
    def part_id(self) -> str:
        """Returns the dictionary representation of the item."""
        pass

    def is_my_part(self, part_id: str):
        return self.part_id() == part_id

class IQuestionItem(IPartItem):
    @abstractmethod
    def qn(self) -> int:
        """Returns the dictionary representation of the item."""
        pass

    def is_my_question(self, part_id: str, qn: int):
        return self.is_my_part(part_id) and self.qn() == qn


class Payload:

    def __init__(self):
        self.part_id = ""
        self.gap_id = 0

    def clear(self):
        self.part_id = ""
        self.gap_id = 0