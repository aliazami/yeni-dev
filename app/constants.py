# app/constants.py
from PySide6.QtCore import Qt
from enum import Enum, auto

class SceneMode(Enum):
    SELECT = auto()
    ADD_ITEM = auto()
    DRAWING_RECT = auto()
    EDIT_RECT = auto()
    DEEP_COPY = auto()

INPUT_TRUE_FALSE = "INPUT_TRUE_FALSE"
INPUT_KEYBOARD = "INPUT_KEYBOARD"
INPUT_SELECT_WORDS = "INPUT_SELECT_WORDS"
INPUT_NUMBERS = "INPUT_NUMBERS"

ALL_INPUT_TYPES = {
    INPUT_TRUE_FALSE,
    INPUT_KEYBOARD,
    INPUT_SELECT_WORDS,
    INPUT_NUMBERS,
}

# --- Constants ---
KEY_PRE_ITEM = Qt.ItemDataRole.UserRole + 1
KEY_RECT_STYLE = Qt.ItemDataRole.UserRole + 2
KEY_DEFAULT_TEXT = Qt.ItemDataRole.UserRole + 3


REF_UNIT_ITEM = "REF_UNIT_ITEM"
REF_PART_ITEM = "REF_PART_ITEM"
REF_GROUP_ITEM = "REF_GROUP_ITEM"
REF_QUESTION_ITEM = "REF_QUESTION_ITEM"
REF_QUESTION_SAMPLE_ITEM = "REF_QUESTION_SAMPLE_ITEM"
REF_OPTION_ITEM = "REF_OPTION_ITEM"
REF_ANSWER_PART_ITEM = "REF_ANSWER_PART_ITEM"
REF_ANSWER_QUESTION_ITEM = "REF_ANSWER_QUESTION_ITEM"
BLOCK_ITEM = "BLOCK_ITEM"
WORD_BOUNDARY_ITEM = "WORD_BOUNDARY_ITEM"
BOX_ITEM = "BOX_ITEM"
GAP_ITEM = "GAP_ITEM"
GAP_SAMPLE_ITEM = "GAP_SAMPLE_ITEM"
BOX_SAMPLE_ITEM = "BOX_SAMPLE_ITEM"
CAPTION_ITEM = "CAPTION_ITEM"

ALL_ITEMS = {
    REF_UNIT_ITEM,
    REF_PART_ITEM,
    REF_GROUP_ITEM,
    REF_QUESTION_ITEM,
    REF_QUESTION_SAMPLE_ITEM,
    REF_OPTION_ITEM,
    REF_ANSWER_PART_ITEM,
    REF_ANSWER_QUESTION_ITEM,
    BLOCK_ITEM,
    WORD_BOUNDARY_ITEM,
    BOX_ITEM,
    GAP_ITEM,
    GAP_SAMPLE_ITEM,
    CAPTION_ITEM,
}

ITEM_SIGN = {
    REF_UNIT_ITEM: "U",
    REF_PART_ITEM: "P",
    REF_GROUP_ITEM: "G",
    REF_QUESTION_ITEM: "Q",
    REF_QUESTION_SAMPLE_ITEM: "QS",
    REF_OPTION_ITEM: "O",
    REF_ANSWER_PART_ITEM: "A",
    REF_ANSWER_QUESTION_ITEM: "AQ",
    WORD_BOUNDARY_ITEM: "[W]",
    BOX_ITEM: "[X]",
    BOX_SAMPLE_ITEM: "[XS]",
    GAP_ITEM: "<G>",
    GAP_SAMPLE_ITEM: "<GS>",
    CAPTION_ITEM: "c",
    BLOCK_ITEM: "b",
}

ITEM_CHILD_TYPES = {
    REF_UNIT_ITEM: {REF_PART_ITEM, REF_ANSWER_PART_ITEM},
    REF_PART_ITEM: {REF_QUESTION_ITEM, REF_QUESTION_SAMPLE_ITEM, REF_OPTION_ITEM, REF_GROUP_ITEM, CAPTION_ITEM},
    REF_QUESTION_ITEM: {WORD_BOUNDARY_ITEM, GAP_ITEM, BOX_ITEM, CAPTION_ITEM},
    REF_QUESTION_SAMPLE_ITEM: {WORD_BOUNDARY_ITEM, GAP_SAMPLE_ITEM, BOX_SAMPLE_ITEM, CAPTION_ITEM},
    REF_OPTION_ITEM: {WORD_BOUNDARY_ITEM, GAP_ITEM, BOX_ITEM, CAPTION_ITEM},
    REF_GROUP_ITEM: {WORD_BOUNDARY_ITEM, GAP_ITEM, BOX_ITEM, CAPTION_ITEM},
    REF_ANSWER_PART_ITEM: {BLOCK_ITEM, REF_ANSWER_QUESTION_ITEM},
    REF_ANSWER_QUESTION_ITEM: {CAPTION_ITEM}
}

INPUT_CHILD_TYPES = {
    INPUT_TRUE_FALSE: {REF_PART_ITEM, REF_QUESTION_ITEM, BOX_ITEM},
    INPUT_KEYBOARD: {REF_PART_ITEM, REF_QUESTION_ITEM, GAP_ITEM},
    INPUT_SELECT_WORDS: {REF_PART_ITEM, REF_QUESTION_ITEM, GAP_ITEM},
    INPUT_NUMBERS: {REF_PART_ITEM, REF_QUESTION_ITEM, GAP_ITEM, BOX_ITEM},
}

BEHAVE_INITIAL_VISIBLE = {REF_UNIT_ITEM, REF_PART_ITEM, REF_ANSWER_PART_ITEM}
BEHAVE_RECTANGLE = {WORD_BOUNDARY_ITEM, GAP_ITEM, GAP_SAMPLE_ITEM, CAPTION_ITEM, BLOCK_ITEM}
BEHAVE_CENTER_NUMBER = {REF_PART_ITEM, REF_QUESTION_ITEM, REF_QUESTION_SAMPLE_ITEM, REF_UNIT_ITEM, REF_ANSWER_PART_ITEM, REF_ANSWER_QUESTION_ITEM}
BEHAVE_TOP_LEFT_CAPTION = {WORD_BOUNDARY_ITEM, BOX_ITEM, BOX_SAMPLE_ITEM, CAPTION_ITEM, GAP_ITEM, GAP_SAMPLE_ITEM, BLOCK_ITEM}
BEHAVE_REPEATABLE_INSERT = ALL_ITEMS
BEHAVE_HAS_NO_PARENT = {REF_UNIT_ITEM}
BEHAVE_FIXED_SIZE = {REF_PART_ITEM, REF_QUESTION_ITEM, REF_QUESTION_SAMPLE_ITEM, REF_ANSWER_PART_ITEM, REF_ANSWER_QUESTION_ITEM}
BEHAVE_SQUARE = {BOX_ITEM, BOX_SAMPLE_ITEM}
BEHAVE_HAS_CAPTION = {CAPTION_ITEM, BLOCK_ITEM}
BEHAVE_READABLE = {CAPTION_ITEM, BLOCK_ITEM}
BEHAVE_ANSWER_ITEMS = {REF_ANSWER_PART_ITEM, REF_ANSWER_QUESTION_ITEM, BLOCK_ITEM, CAPTION_ITEM}
BEHAVE_INPUT_ITEMS = {GAP_ITEM, BOX_ITEM}

ITEM_Z_ORDER = {
    CAPTION_ITEM: 1
}

UI_SETTINGS = {
    "colors": {
        "icon": Qt.GlobalColor.black,
    },
    REF_ANSWER_QUESTION_ITEM: {
        "size": 30,
        "bg_color_active": "#00D4FF",
        "bg_color_inactive": "#B0E9F5",
        "border_color_active": "#00D4FF",
        "border_color_inactive": "#B0E9F5",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
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
    REF_QUESTION_SAMPLE_ITEM: {
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
    REF_ANSWER_PART_ITEM: {
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
    BLOCK_ITEM: {
        "bg_color_active": "#2A741480",
        "bg_color_inactive": "#88FA8480",
        "border_color_active": "#2A741480",
        "border_color_inactive": "#88FA8480",
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
    GAP_SAMPLE_ITEM: {
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

Z_ORDER_BACKGROUND = -10
