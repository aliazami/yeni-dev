from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsSimpleTextItem
from PySide6.QtCore import Qt, QPointF, QPoint
from PySide6.QtGui import QColor, QBrush, QPen, QFont, QPainterPath
from app.constants import (
    KEY_PRE_ITEM, KEY_RECT_STYLE, KEY_DEFAULT_TEXT, ITEM_Z_ORDER
)

from app.models import RectStyles
from app.pre_item import PreItem
from app.helpers.utils import points_are_very_near


class RectanglePartItem(QGraphicsRectItem):

    def __init__(self, pre_item: PreItem):
        initial_pos = pre_item.initial_pos
        super().__init__(initial_pos.x(), initial_pos.y(), pre_item.width, pre_item.height)
        self.setPos(pre_item.pos)
        self.setData(KEY_PRE_ITEM, pre_item)
        styles = RectStyles(pre_item.settings)
        self.setData(KEY_RECT_STYLE, styles)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        z_order = ITEM_Z_ORDER.get(pre_item.part_type)
        if isinstance(z_order, int):
            self.setZValue(z_order)
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

    def setPos(self, x: float, y: float, /):
        self.setPos(QPoint(x, y))

    def setPos(self, pos: QPointF | QPoint | QPainterPath.Element, /):
        super().setPos(pos)
        if self.pre_item and not points_are_very_near(pos, self.pre_item.pos):
            self.pre_item.set_pos(pos.x(), pos.y())
