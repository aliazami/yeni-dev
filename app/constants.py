# app/constants.py
from PySide6.QtCore import Qt


# --- Constants ---
KEY_PART_ID = 0
KEY_TYPE = 1
KEY_QN = 2
KEY_IS_ACTIVE = 3


PART_ITEM = "CIRCLE"
WORD_BOUNDARY_ITEM = "RECTANGLE"
GAP_ITEM = "LABEL"
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
