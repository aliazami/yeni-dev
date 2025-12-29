
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