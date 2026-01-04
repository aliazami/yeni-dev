# app/constants.py
from PySide6.QtCore import Qt


# --- Constants ---
KEY_PART_ID = 0
KEY_TYPE = 1
KEY_QUESTION_NUMBER = 2
KEY_IS_ACTIVE = 3
KEY_KWARGS = 4

SCOPE_PART = "SCOPE_PART"
SCOPE_QUESTION = "SCOPE_QUESTION"
SCOPE_ANSWER = "SCOPE_ANSWER"
SCOPE_PART_CHOICE = "SCOPE_PART_CHOICE"
SCOPE_QUESTION_CHOICE = "SCOPE_QUESTION_CHOICE"


PRE_ITEM = "PRE_ITEM"
PART_ITEM = "PART_ITEM"
WORD_BOUNDARY_ITEM = "WORD_BOUNDARY_ITEM"
GAP_ITEM = "GAP_ITEM"
QUESTION_REF_ITEM = "QUESTION_REF_ITEM"
T_QUESTION_ITEM = "T_QUESTION_ITEM"

SETTINGS = {
    "colors": {
        "icon": Qt.GlobalColor.black,
    },
    "part_item": {"radius": 25.0},
    "question_ref_item": {
        "width": 40,
        "height": 20,
    }
}

Z_ORDER_BACKGROUND = -1000
