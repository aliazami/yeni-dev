from typing import Any

from app.constants import (
    INPUT_TRUE_FALSE, INPUT_NUMBERS, INPUT_SELECT_WORDS, ALL_INPUT_TYPES, INPUT_KEYBOARD
)



def can_build(parts: list[str], target: str) -> bool:
    n = len(target)
    dp = [False] * (n + 1)
    dp[0] = True  # empty string is always buildable

    for i in range(1, n + 1):
        for word in parts:
            if i >= len(word) and dp[i - len(word)]:
                if target[i - len(word):i] == word:
                    dp[i] = True
                    break

    return dp[n]

def trim(text: str):
    return (text.strip().lower().replace(" ", "").replace("\n", "")
            .replace("-", "").replace("_", ""))


class RectStyles:
    def __init__(self, styles: dict):
        self.bg_color_active = styles.get("bg_color_active", "#00D4FF")
        self.bg_color_inactive = styles.get("bg_color_inactive", "#B0E9F5")
        self.border_color_active = styles.get("border_color_active", "#00D4FF")
        self.border_color_inactive = styles.get("border_color_inactive", "#B0E9F5")
        self.font_color_active = styles.get("font_color_active", "#000")
        self.font_color_inactive = styles.get("font_color_inactive", "#000")
        self.font_family = styles.get("font_family", "Arial")
        self.font_size_active = styles.get("font_size_active", 12)
        self.font_size_inactive = styles.get("font_size_inactive", 12)


class Delta:
    def __init__(self, dx: int, dy:int):
        self._dx = dx
        self._dy = dy

    @property
    def dx(self):
        return self._dx
    
    @property
    def dy(self):
        return self._dy

class Caption:
    def __init__(self, text: str):
        self._text: str = str(text)

    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        self._text = value

    def copy(self):
        return Caption(self.text)


class Input:
    def __init__(self, input_type: str):
        if not isinstance(input_type, str) or input_type not in ALL_INPUT_TYPES:
            raise ValueError(f"Invalid input type: {input_type}")
        self._input_type: str = input_type
        self.correct_answer = ""
        self.word_options: list[str] = []

    @property
    def input_type(self):
        return self._input_type

    def copy(self):
        new = Input(self.input_type)
        new.correct_answer = str(self.correct_answer)
        new.word_options = self.word_options
        return new

    @property
    def is_ok(self):
        if not self.correct_answer or not isinstance(self.correct_answer, str):
            return False
        if self._input_type == INPUT_KEYBOARD:
            return True
        if self._input_type == INPUT_TRUE_FALSE:
            return self.correct_answer.upper() in {"T", "F"}
        if self._input_type == INPUT_NUMBERS:
            return self.correct_answer.isdigit()
        if self._input_type == INPUT_SELECT_WORDS:
            target = trim(self.correct_answer)
            parts = [trim(part) for part in self.word_options]
            return can_build(parts, target)
        raise ValueError


class PreItemData:
    def __init__(self):
        # mandatory
        self.part_type: str = "part_type?"
        self.parent_id: str = "parent_id?"
        self.seq: int = -1
        self.z_order: int = 1
        self.active: bool = False
        self.visible: bool = True
        self.is_dirty: bool = True
        # optional
        self.tag: str | None = None
        self.x: int | None = None
        self.y: int | None = None
        self.width: int | None = None
        self.height: int | None = None
        self.ui: Any | None = None
        self.caption: Caption | None = None
        self.input: Input | None = None


    def copy(self):
        new = PreItemData()
        new.part_type = self.part_type
        new.parent_id = self.parent_id
        new.seq = self.seq
        new.active = self.active
        new.visible = self.visible
        new.is_dirty = self.is_dirty
        # optional
        new.tag = self.tag
        new.x = self.x
        new.z_order = self.z_order
        new.y = self.y
        new.width = self.width
        new.height = self.height
        new.ui = self.ui
        new.caption = self.caption.copy() if self.caption else None
        new.input = self.input.copy() if self.input else None
        return new


