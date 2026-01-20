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


REF_UNIT_ITEM = "REF_UNIT_ITEM"
REF_PART_ITEM = "REF_PART_ITEM"
REF_GROUP_ITEM = "REF_GROUP_ITEM"
REF_QUESTION_ITEM = "REF_QUESTION_ITEM"
REF_OPTION_ITEM = "REF_OPTION_ITEM"
REF_ANSWER_ITEM = "REF_ANSWER_ITEM"
WORD_BOUNDARY_ITEM = "WORD_BOUNDARY_ITEM"
BOX_ITEM = "BOX_ITEM"
GAP_ITEM = "GAP_ITEM"
CAPTION_ITEM = "CAPTION_ITEM"

ITEM_SIGN = {
    REF_UNIT_ITEM: "U",
    REF_PART_ITEM: "P",
    REF_GROUP_ITEM: "G",
    REF_QUESTION_ITEM: "Q",
    REF_OPTION_ITEM: "O",
    REF_ANSWER_ITEM: "A",
    WORD_BOUNDARY_ITEM: "[W]",
    BOX_ITEM: "[X]",
    GAP_ITEM: "<G>",
    CAPTION_ITEM: "c"
}

ITEM_CHILD_TYPES = {
    REF_UNIT_ITEM: [REF_PART_ITEM, REF_ANSWER_ITEM],
    REF_PART_ITEM: [REF_QUESTION_ITEM, REF_OPTION_ITEM, REF_GROUP_ITEM, CAPTION_ITEM],
    REF_QUESTION_ITEM: [WORD_BOUNDARY_ITEM, GAP_ITEM, BOX_ITEM, CAPTION_ITEM],
    REF_OPTION_ITEM: [WORD_BOUNDARY_ITEM, GAP_ITEM, BOX_ITEM, CAPTION_ITEM],
    REF_GROUP_ITEM: [WORD_BOUNDARY_ITEM, GAP_ITEM, BOX_ITEM, CAPTION_ITEM],
}

BAHAVE_INITIAL_VISIBLE = [REF_UNIT_ITEM, REF_PART_ITEM]
BEHAVE_RECTANGLE = [WORD_BOUNDARY_ITEM, GAP_ITEM, CAPTION_ITEM]
BAHAVE_REPEATABLE_INSERT = [REF_PART_ITEM, REF_QUESTION_ITEM]
BEHAVE_HAS_NO_PARENT = [REF_UNIT_ITEM]
BEHAVE_FIXED_SIZE = [REF_PART_ITEM, REF_QUESTION_ITEM]
BEHAVE_SQUARE = [BOX_ITEM]

ITEM_Z_ORDER = {
    CAPTION_ITEM: 1
}

UI_SETTINGS = {
    "colors": {
        "icon": Qt.GlobalColor.black,
    },
    REF_QUESTION_ITEM: {
        "size": 30,
        "bg_color_active": "#00D4FF",
        "bg_color_inactive": "#B0E9F5",
        "border_color_active": "#00D4FF",
        "border_color_inactive": "#B0E9F5",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },
    REF_PART_ITEM: {
        "size": 30,
        "bg_color_active": "#FF7A59",
        "bg_color_inactive": "#FFC7B3",
        "border_color_active": "#FF7A59",
        "border_color_inactive": "#FFC7B3",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },
    REF_UNIT_ITEM: {
        "size": 50,
        "bg_color_active": "#7D2EA8",
        "bg_color_inactive": "#C69FDA",
        "border_color_active": "#7D2EA8",
        "border_color_inactive": "#C69FDA",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },
    CAPTION_ITEM: {
        "size": 50,
        "bg_color_active": "#A50D3080",
        "bg_color_inactive": "#A8737F80",
        "border_color_active": "#A50D30",
        "border_color_inactive": "#A8737F",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },       
    BOX_ITEM: {
        "size": 20,
        "bg_color_active": "#000000ff",
        "bg_color_inactive": "#000000ff",
        "border_color_active": "#FF59E9",
        "border_color_inactive": "#F8BDF0",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },
    GAP_ITEM: {
        "width": 50,
        "height": 20,
        "bg_color_active": "#2A741480",
        "bg_color_inactive": "#88FA8480",
        "border_color_active": "#2A741480",
        "border_color_inactive": "#88FA8480",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },    
    WORD_BOUNDARY_ITEM: {
        "bg_color_active": "#6F59FF80",
        "bg_color_inactive": "#A4AFFB80",
        "border_color_active": "#6F59FF80",
        "border_color_inactive": "#A4AFFB80",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    }
}

Z_ORDER_BACKGROUND = -1000
