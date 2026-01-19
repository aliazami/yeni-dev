# app/constants.py
from PySide6.QtCore import Qt
from enum import Enum, auto

class SceneMode(Enum):
    SELECT = auto()
    ADD_ITEM = auto()
    DRAWING_RECT = auto()
    EDIT_RECT = auto()
    DEEP_COPY = auto()

# --- Constants ---
KEY_PART_ID = Qt.ItemDataRole.UserRole + 0
KEY_PART_TYPE = Qt.ItemDataRole.UserRole + 1
KEY_QUESTION_NUMBER = Qt.ItemDataRole.UserRole + 2
KEY_PRE_ITEM = Qt.ItemDataRole.UserRole + 3
KEY_KWARGS = Qt.ItemDataRole.UserRole + 4
KEY_VISIBLE = Qt.ItemDataRole.UserRole + 5
KEY_RECT_STYLE = Qt.ItemDataRole.UserRole + 6
KEY_DEFAULT_TEXT = Qt.ItemDataRole.UserRole + 7
KEY_QUESTION_REF_ITEM_TEXT = Qt.ItemDataRole.UserRole + 8
KEY_WORD = Qt.ItemDataRole.UserRole + 14

SCOPE_PART = "SCOPE_PART"
SCOPE_QUESTION = "SCOPE_QUESTION"
SCOPE_ANSWER = "SCOPE_ANSWER"
SCOPE_PART_CHOICE = "SCOPE_PART_CHOICE"
SCOPE_QUESTION_CHOICE = "SCOPE_QUESTION_CHOICE"

QUESTION_NUMBER = "QUESTION_NUMBER"

PRE_ITEM = "PRE_ITEM"
PART_ITEM = "PART_ITEM"
ANSWER_PART_ITEM = "ANSWER_PART_ITEM"
Q_WORD_BOUNDARY_PART_ITEM = "Q_WORD_BOUNDARY_PART_ITEM"
Q_BOX_PART_ITEM = "Q_BOX_PART_ITEM"
GAP_ITEM = "GAP_ITEM"
Q_GAP_ITEM = "Q_GAP_ITEM"
QUESTION_REF_ITEM = "QUESTION_REF_ITEM"
PAGE_REF_ITEM = "PAGE_REF_ITEM"
OPTION_REF_ITEM = "OPTION_REF_ITEM"


REPEATABLE = [PART_ITEM, QUESTION_REF_ITEM]
SERIALIZABLE = [PART_ITEM, QUESTION_REF_ITEM]
FIXED_SIZE = [PART_ITEM, QUESTION_REF_ITEM]
SQUARE = [Q_BOX_PART_ITEM]
ACTIVABLE =[ PART_ITEM, QUESTION_REF_ITEM]
CHILD_TYPES = {
    PART_ITEM: [QUESTION_REF_ITEM, OPTION_REF_ITEM],
    QUESTION_REF_ITEM: [Q_WORD_BOUNDARY_PART_ITEM, Q_GAP_ITEM]
}
SETTINGS = {
    "colors": {
        "icon": Qt.GlobalColor.black,
    },
    QUESTION_REF_ITEM: {
        "size": 30,
        "bg_color_active": "#00D4FF",
        "bg_color_inactive": "#B0E9F5",
        "border_color_active": "#00D4FF",
        "border_color_inactive": "#B0E9F5",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },
    PART_ITEM: {
        "size": 30,
        "bg_color_active": "#FF7A59",
        "bg_color_inactive": "#FFC7B3",
        "border_color_active": "#FF7A59",
        "border_color_inactive": "#FFC7B3",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },
    PAGE_REF_ITEM: {
        "size": 50,
        "bg_color_active": "#7D2EA8",
        "bg_color_inactive": "#C69FDA",
        "border_color_active": "#7D2EA8",
        "border_color_inactive": "#C69FDA",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },    
    Q_BOX_PART_ITEM: {
        "size": 20,
        "bg_color_active": "#000000ff",
        "bg_color_inactive": "#000000ff",
        "border_color_active": "#FF59E9",
        "border_color_inactive": "#F8BDF0",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },
    Q_GAP_ITEM: {
        "width": 50,
        "height": 20,
        "bg_color_active": "#2A741480",
        "bg_color_inactive": "#88FA8480",
        "border_color_active": "#2A741480",
        "border_color_inactive": "#88FA8480",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },    
    Q_WORD_BOUNDARY_PART_ITEM: {
        "bg_color_active": "#6F59FF80",
        "bg_color_inactive": "#A4AFFB80",
        "border_color_active": "#6F59FF80",
        "border_color_inactive": "#A4AFFB80",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    }
}

Z_ORDER_BACKGROUND = -1000
