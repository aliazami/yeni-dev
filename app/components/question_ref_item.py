from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QFont, QBrush, QColor
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSimpleTextItem,
    QInputDialog,
    QMessageBox,
)
from app.constants import (
    SETTINGS, QUESTION_REF_ITEM, PART_ITEM, SCOPE_QUESTION, 
    PRE_ITEM, KEY_QUESTION_NUMBER, QUESTION_NUMBER, KEY_QUESTION_REF_ITEM_TEXT
)
from app.helpers.utils import ignore, check_repeat_id
from app.models import RectanglePartItem, PreItem, PlatFormConfig


class QuestionRefItem(RectanglePartItem):
    platform_config = PlatFormConfig(
        serializable=True,
        sizable=False,
        activable=True,
        repeatable=True,
        scope=SCOPE_QUESTION,
    )

    def __init__(self, part_id: str, pos: QPointF, **kwargs):
        setting = SETTINGS[QUESTION_REF_ITEM]
        size = setting["size"]
        draw_pos = QPointF(-size / 2, -size / 2)
        question_number = kwargs[QUESTION_NUMBER]
        super().__init__(QUESTION_REF_ITEM, part_id, draw_pos, size=size, setting=setting, **kwargs)
        self.setData(KEY_QUESTION_NUMBER, question_number)
        self.setPos(pos)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
        question_ref_text = QGraphicsSimpleTextItem(str(question_number), parent=self)
        self.setData(KEY_QUESTION_REF_ITEM_TEXT, question_ref_text)
        self._refresh_ui(False)

    @classmethod
    def pre_create(cls, items: list[QGraphicsItem], **kwrgs) -> bool:
        part_id = kwrgs["part_id"]
        if not part_id:
            QMessageBox.warning(None, "Error", "No Part Item Selected.")
            return False

        default_int = 1
        for item in items:
            if isinstance(item, QuestionRefItem) and item.part_id == part_id:
                default_int = max(default_int, item.question_number)
        qn, ok = QInputDialog.getInt(
            None, "Add Gap Item", "Sequence:", value=default_int, minValue=1
        )
        if ok:
            ir_repeating, qn = check_repeat_id(qn)
            pre_item = PreItem(part_type=PRE_ITEM, part_id=part_id, pos=QPointF(0, 0), qn=qn)
            if cls.has_item(items, pre_item):
                QMessageBox.warning(None, "Error", "Exists!")
                return False

            else:
                cls.platform_state.is_repeating = ir_repeating
                cls.platform_data.pre_item = pre_item
                return True

    @classmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        ignore([w, h])
        pre_item = cls.platform_data.pre_item
        if not pre_item:
            return None
        part_id = pre_item.part_id
        kwargs = {QUESTION_NUMBER: pre_item.question_number}
        return QuestionRefItem(part_id, pos, **kwargs)

    def _refresh_ui(self, active):
        if active:
            self.setBrush(QBrush(QColor("#4488FF")))
            self.setPen(QPen(Qt.GlobalColor.black, 2))
        else:
            self.setBrush(QBrush(Qt.GlobalColor.yellow))
            self.setPen(QPen(Qt.GlobalColor.black, 2))
        t = self.data(KEY_QUESTION_REF_ITEM_TEXT)
        t.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        br = t.boundingRect()
        t.setPos(-br.width() / 2, -br.height() / 2)
        t.setAcceptedMouseButtons(Qt.MouseButton.NoButton)
