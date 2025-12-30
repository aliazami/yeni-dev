# app/constants.py
from PySide6.QtCore import Qt


# --- Constants ---
KEY_PART_ID = 0
KEY_TYPE = 1
KEY_RECT_ID = 2
KEY_RECT_TEXT = 3

PART_ITEM = "CIRCLE"
WORD_BOUNDARY_ITEM = "RECTANGLE"
GAP_ITEM = "LABEL"


SETTINGS = {
    "colors": {
        "icon": Qt.GlobalColor.black,
    },
    "part_item": {"radius": 25.0},
}

Z_ORDER_BACKGROUND = -1000