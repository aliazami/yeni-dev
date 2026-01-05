from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont, QBrush, QColor
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSimpleTextItem,
    QInputDialog,
    QMessageBox,
)
from app.constants import SETTINGS, KEY_PART_ID, KEY_TYPE, PART_ITEM, SCOPE_PART, SCOPE_QUESTION, PRE_ITEM
from app.helpers.utils import ignore
from app.models import RectanglePartItem, PreItem, PlatFormConfig


class QuestionRefItem(RectanglePartItem):
    platform_config = PlatFormConfig(
        serializable=True,
        sizable=False,
        activable=True,
        repeatable=True,
        scope=SCOPE_PART,
    )

    def __init__(self, part_id: str, pos: QPointF):
        setting = SETTINGS["question_ref_item"]
        size = setting["size"]
        draw_pos = QPointF(-size / 2, -size / 2)
        super().__init__(PART_ITEM, part_id, draw_pos, size=size, setting=setting)
        self.setPos(pos)
        self.setPen(QPen(Qt.GlobalColor.black, 2))
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        t = QGraphicsSimpleTextItem(part_id, parent=self)
        t.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        br = t.boundingRect()
        t.setPos(-br.width() / 2, -br.height() / 2)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
        self._refresh_ui(False)

    @classmethod
    def pre_create(cls, items: list[QGraphicsItem], part_id: str) -> bool:

        # ======= question items =======
        if cls.platform_config.scope in [SCOPE_QUESTION]:
            if not part_id:
                QMessageBox.warning(None, "Error", "No Part Item Selected.")
                return False
            default_int = cls.get_max_question_number(items, part_id) + 1
            qn, ok = QInputDialog.getInt(
                None, "Add Gap Item", "Sequence:", value=default_int, minValue=1
            )
            if ok:
                if qn > 999 and qn % 1000 == 0:
                    cls.platform_state.is_repeating = True
                    qn = qn / 1000

                pre_item = PreItem(part_type=PRE_ITEM, part_id=part_id, pos=QPointF(0, 0), qn=qn)
                if cls.has_item(items, pre_item):
                    QMessageBox.warning(None, "Error", "Exists!")
                    return False

                else:
                    cls.platform_data.pre_item = pre_item
                    return True

        return False

    @classmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        ignore([w, h])
        pre_item = cls.platform_data.pre_item
        return QuestionRefItem(pre_item.part_id, pos) if pre_item else None

    def _refresh_ui(self, active):
        if active:
            self.setBrush(QBrush(QColor("#4488FF")))
            self.setPen(QPen(Qt.GlobalColor.black, 2))
        else:
            self.setBrush(QBrush(Qt.GlobalColor.yellow))
            self.setPen(QPen(Qt.GlobalColor.black, 2))
