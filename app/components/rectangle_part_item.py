from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsSimpleTextItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QBrush, QPen, QFont
from app.constants import (
    KEY_PRE_ITEM, KEY_RECT_STYLE, KEY_DEFAULT_TEXT
)

from app.models import RectStyles
from app.pre_item import PreItem


class RectanglePartItem(QGraphicsRectItem):

    def __init__(self, pre_item: PreItem, pos: QPointF):

        super().__init__(pre_item.pos.x(), pre_item.pos.y(), pre_item.width, pre_item.height)
        pre_item.pos = pos
        self.setPos(pos)
        self.setData(KEY_PRE_ITEM, pre_item)
        styles = RectStyles(pre_item.settings)
        self.setData(KEY_RECT_STYLE, styles)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        default_text = QGraphicsSimpleTextItem("", parent=self)
        default_text.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self.setData(KEY_DEFAULT_TEXT, default_text)

    @property
    def pre_item(self) -> PreItem:
        return self.data(KEY_PRE_ITEM)

    # ======= item UI =======
    def _refresh_ui(self):
        styles: RectStyles = self.data(KEY_RECT_STYLE)
        default_text: QGraphicsSimpleTextItem = self.data(KEY_DEFAULT_TEXT)
        default_text.setText(self.pre_item.default_text)
        
        if self.pre_item.is_active:
            self.setBrush(QBrush(QColor(styles.bg_color_active)))
            self.setPen(QPen(QColor(styles.border_color_active), 2))
            default_text.setFont(QFont(styles.font_family, styles.font_size_active, QFont.Weight.Bold))
        else:
            self.setBrush(QBrush(QColor(styles.bg_color_inactive)))
            self.setPen(QPen(QColor(styles.border_color_inactive), 2))
            default_text.setFont(QFont(styles.font_family, styles.font_size_inactive, QFont.Weight.Normal))
