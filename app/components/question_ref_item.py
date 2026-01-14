from PySide6.QtCore import Qt, QPointF
from PySide6.QtWidgets import QGraphicsSimpleTextItem
from app.constants import KEY_DEFAULT_TEXT

from app.components.rectangle_part_item import RectanglePartItem
from app.pre_item import PreItem


class QuestionRefItem(RectanglePartItem):

    def __init__(self, pre_item: PreItem):
        super().__init__(pre_item)
        self._refresh_ui()

    def _refresh_ui(self):
        super()._refresh_ui()
        default_text: QGraphicsSimpleTextItem = self.data(KEY_DEFAULT_TEXT)
        br = default_text.boundingRect()
        default_text.setPos(-br.width() / 2, -br.height() / 2)
        default_text.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
