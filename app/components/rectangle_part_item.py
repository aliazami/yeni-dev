from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem, QGraphicsSimpleTextItem
from PySide6.QtCore import Qt, QPointF, QPoint
from PySide6.QtGui import QColor, QBrush, QPen, QFont, QPainterPath
from app.constants import (
    KEY_PRE_ITEM,
    KEY_RECT_STYLE,
    KEY_DEFAULT_TEXT,
    ITEM_Z_ORDER,
    BEHAVE_INPUT_ITEMS,
    BEHAVE_SAMPLE_INPUT_ITEMS,
    CAPTION_ITEM,
)

from app.models import RectStyles
from app.pre_item import PreItem
from app.helpers.utils import points_are_very_near


class RectanglePartItem(QGraphicsRectItem):
    def __init__(self, pre_item: PreItem):
        initial_pos = pre_item.initial_pos
        super().__init__(
            initial_pos.x(), initial_pos.y(), pre_item.width, pre_item.height
        )
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
        if (
            self.pre_item.part_type in [*BEHAVE_INPUT_ITEMS, *BEHAVE_SAMPLE_INPUT_ITEMS]
            and self.pre_item.input
            and self.pre_item.input.correct_answer
        ):
            default_text.setText("")       
        else:
            default_text.setText(self.pre_item.default_text)
        if self.pre_item.z_order is not None:
            self.setZValue(self.pre_item.z_order)

        center_text = self.pre_item.center_text
        if center_text:
            center_obj = QGraphicsSimpleTextItem(center_text, self)
            r_rect = self.rect()  # The QRectF(0, 0, 300, 100)
            t_rect = center_obj.boundingRect()  # The size of the "hello" string

            # Calculate center: (ParentCenter - ChildHalfSize)
            x = r_rect.center().x() - t_rect.width() / 2
            y = r_rect.center().y() - t_rect.height() / 2
            center_obj.setPos(x, y)

        if self.pre_item.is_active:
            self.setBrush(QBrush(QColor(styles.bg_color_active)))
            self.setPen(QPen(QColor(styles.border_color_active), 2))
            default_text.setFont(
                QFont(styles.font_family, styles.font_size_active, QFont.Weight.Bold)
            )
        else:
            self.setBrush(QBrush(QColor(styles.bg_color_inactive)))
            self.setPen(QPen(QColor(styles.border_color_inactive), 2))
            default_text.setFont(
                QFont(
                    styles.font_family, styles.font_size_inactive, QFont.Weight.Normal
                )
            )

    def setPos(self, *args):
        if len(args) == 2 and all(isinstance(arg, (int, float)) for arg in args):
            x, y = args
            # Handle x, y case
            self.setPos(QPoint(x, y))
        elif len(args) == 1:
            pos = args[0]
            # Handle QPoint/QPointF/Element case
            super().setPos(pos)
            if self.pre_item and not points_are_very_near(pos, self.pre_item.pos):
                self.pre_item.set_pos(pos.x(), pos.y())
        else:
            raise TypeError("setPos() takes 1 or 2 positional arguments")
