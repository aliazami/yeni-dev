# app/word_boundary_part_item.py
from PySide6.QtWidgets import QGraphicsSimpleTextItem
from app.constants import KEY_DEFAULT_TEXT
from app.pre_item import PreItem
from app.components.rectangle_part_item import RectanglePartItem


class WordBoundaryPartItem(RectanglePartItem):

    def __init__(self, pre_item: PreItem):
        super().__init__(pre_item)
        self._refresh_ui()

    def _refresh_ui(self):
        super()._refresh_ui()
        default_text: QGraphicsSimpleTextItem = self.data(KEY_DEFAULT_TEXT)
        br = default_text.boundingRect()
        br_height = br.height()
        default_text.setPos(0, -br_height)