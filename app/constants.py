# app/constants.py
from PySide6.QtCore import Qt


# --- Constants ---
KEY_PART_ID = Qt.ItemDataRole.UserRole + 0
KEY_PART_TYPE = Qt.ItemDataRole.UserRole + 1
KEY_QUESTION_NUMBER = Qt.ItemDataRole.UserRole + 2
KEY_IS_ACTIVE = Qt.ItemDataRole.UserRole + 3
KEY_KWARGS = Qt.ItemDataRole.UserRole + 4
KEY_VISIBLE = Qt.ItemDataRole.UserRole + 5
KEY_RECT_STYLE = Qt.ItemDataRole.UserRole + 6
KEY_WORD = Qt.ItemDataRole.UserRole + 14

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
