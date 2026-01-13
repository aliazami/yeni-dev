from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtCore import QPointF
from PySide6.QtGui import QColor, QBrush, QPen
from app.constants import (
    KEY_PRE_ITEM, KEY_RECT_STYLE, 
)

from app.models import RectStyles
from app.pre_item import PreItem


class RectanglePartItem(QGraphicsRectItem):

    def __init__(self, pre_item: PreItem, pos: QPointF):
        super().__init__(x=pos.x(), y=pos.y(), w=pre_item.width, h=pre_item.height)
        self.setData(KEY_PRE_ITEM, pre_item)
        styles = RectStyles(pre_item.settings)
        self.setData(KEY_RECT_STYLE, styles)

    @property
    def styles(self) -> RectStyles:
        return self.data(KEY_RECT_STYLE)

    @property
    def pre_item(self) -> PreItem:
        return self.data(KEY_PRE_ITEM)

    # ======= item UI =======
    def _refresh_ui(self):
        self.setPen(QPen(QColor(self.styles.border_color_active), 2))

        if self.pre_item.is_active:
            self.setBrush(QBrush(QColor(self.styles.bg_color_active)))
            self.setPen(QPen(QColor(self.styles.border_color_active), 2))
        else:
            self.setBrush(QBrush(QColor(self.styles.bg_color_inactive)))
            self.setPen(QPen(QColor(self.styles.border_color_inactive), 2))
