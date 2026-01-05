# app/constants.py
from PySide6.QtCore import Qt


# --- Constants ---
KEY_PART_ID = 0
KEY_TYPE = 1
KEY_QUESTION_NUMBER = 2
KEY_IS_ACTIVE = 3
KEY_KWARGS = 4
KEY_VISIBLE = 5
KEY_STYLE_BG_COLOR_ACTIVE = 6
KEY_STYLE_BG_COLOR_INACTIVE = 7
KEY_STYLE_BORDER_COLOR_ACTIVE = 8
KEY_STYLE_BORDER_COLOR_INACTIVE = 9
KEY_STYLE_FONT_COLOR_ACTIVE = 10
KEY_STYLE_FONT_COLOR_INACTIVE = 11
KEY_STYLE_FONT_SIZE_ACTIVE = 12
KEY_STYLE_FONT_SIZE_INACTIVE = 13
KEY_WORD = 14

SCOPE_PART = "SCOPE_PART"
SCOPE_QUESTION = "SCOPE_QUESTION"
SCOPE_ANSWER = "SCOPE_ANSWER"
SCOPE_PART_CHOICE = "SCOPE_PART_CHOICE"
SCOPE_QUESTION_CHOICE = "SCOPE_QUESTION_CHOICE"

PRE_ITEM = "PRE_ITEM"
PART_ITEM = "PART_ITEM"
WORD_BOUNDARY_PART_ITEM = "WORD_BOUNDARY_PART_ITEM"
GAP_ITEM = "GAP_ITEM"
QUESTION_REF_ITEM = "QUESTION_REF_ITEM"

SETTINGS = {
    "colors": {
        "icon": Qt.GlobalColor.black,
    },
    "question_ref_item": {
        "size": 30,
        "bg_color_active": "#00D4FF",
        "bg_color_inactive": "#B0E9F5",
        "border_color_active": "#00D4FF",
        "border_color_inactive": "#B0E9F5",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },
    "part_item": {
        "size": 30,
        "bg_color_active": "#FF7A59",
        "bg_color_inactive": "#FFC7B3",
        "border_color_active": "#FF7A59",
        "border_color_inactive": "#FFC7B3",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    },
    "word_boundary_part_item": {
        "bg_color_active": "#FF7A59",
        "bg_color_inactive": "#FFC7B3",
        "border_color_active": "#FF7A59",
        "border_color_inactive": "#FFC7B3",
        "font_color_active": "#000",
        "font_color_inactive": "#000",
    }
}

Z_ORDER_BACKGROUND = -1000
