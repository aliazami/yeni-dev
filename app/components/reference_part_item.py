# app/part_item.py
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QGraphicsSimpleTextItem
from app.constants import KEY_DEFAULT_TEXT, REF_PAGE_ITEM
from app.pre_item import PreItem
from app.components.rectangle_part_item import RectanglePartItem


class ReferencePartItem(RectanglePartItem):

    def __init__(self, pre_item: PreItem):
        super().__init__(pre_item)
        self._refresh_ui()

    def _refresh_ui(self):
        super()._refresh_ui()
        default_text: QGraphicsSimpleTextItem = self.data(KEY_DEFAULT_TEXT)

        if self.pre_item.part_type == REF_PAGE_ITEM:
            default_text.setPos(17, 17)
        else:
            br = default_text.boundingRect()
            br_width = br.width()
            br_height = br.height()
            default_text.setPos(-br_width / 2, -br_height / 2)
