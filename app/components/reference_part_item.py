# app/part_item.py
from PySide6.QtWidgets import QGraphicsSimpleTextItem
from app.constants import KEY_DEFAULT_TEXT
from app.pre_item import PreItem
from app.components.rectangle_part_item import RectanglePartItem


class ReferencePartItem(RectanglePartItem):

    def __init__(self, pre_item: PreItem):
        super().__init__(pre_item)
        self._refresh_ui()

    def _refresh_ui(self):
        super()._refresh_ui()
        default_text: QGraphicsSimpleTextItem = self.data(KEY_DEFAULT_TEXT)
        r_rect = self.rect()                # The QRectF(0, 0, 300, 100)
        t_rect = default_text.boundingRect()  # The size of the "hello" string
        
        # Calculate center: (ParentCenter - ChildHalfSize)
        x = r_rect.center().x() - t_rect.width() / 2
        y = r_rect.center().y() - t_rect.height() / 2
        default_text.setPos(x, y)
