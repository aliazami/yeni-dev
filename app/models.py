from abc import abstractmethod
from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QBrush, QPen
from app.constants import KEY_TYPE, KEY_QUESTION_NUMBER, KEY_PART_ID, KEY_IS_ACTIVE, SCOPE_QUESTION, \
    KEY_KWARGS, SCOPE_PART, KEY_STYLE_BORDER_COLOR_ACTIVE, KEY_STYLE_BORDER_COLOR_INACTIVE, \
    KEY_STYLE_BG_COLOR_INACTIVE, KEY_STYLE_BG_COLOR_ACTIVE, KEY_VISIBLE, KEY_STYLE_FONT_COLOR_ACTIVE, \
    KEY_STYLE_FONT_COLOR_INACTIVE, KEY_STYLE_FONT_SIZE_INACTIVE, KEY_STYLE_FONT_SIZE_ACTIVE
from app.helpers.utils import get_next


class PlatFormConfig:
    def __init__(self, serializable, sizable, repeatable, activable, scope):
        self.serializable = serializable
        self.sizable = sizable
        self.repeatable = repeatable
        self.activable = activable
        self.scope = scope


class PlatformState:
    is_repeating = False
    is_active = False
    active_item_uid = ""


class PreItem:
    def __init__(self, part_type, part_id, **kwargs):
        self.part_type = part_type
        self.part_id = part_id
        self.kwargs = kwargs

    @property
    def question_number(self):
        return self.kwargs.get("qn")

    @property
    def uid(self) -> str:
        item_uid = f"{self.part_type}::{self.part_id}"
        if self.question_number > 0:
            item_uid = f"{item_uid}::{self.question_number}"

        return item_uid


class PlatformData:
    pre_item: PreItem | None = None


class RectanglePartItem(QGraphicsRectItem):
    platform_config: PlatFormConfig | None = None
    platform_state = PlatformState()
    platform_data = PlatformData()

    def __init__(self, part_type: str, part_id: str, pos: QPointF, **kwargs):
        w = kwargs.get("w") or kwargs.get("size") or 5
        h = kwargs.get("h") or kwargs.get("size") or 5
        super().__init__(pos.x(), pos.y(), w, h)
        self.setData(KEY_PART_ID, part_id)
        self.setData(KEY_TYPE, part_type)
        self.setData(KEY_KWARGS, kwargs)
        visible = True
        if kwargs.get("visible") is not None:
            visible = kwargs.get("visible")
        self.setData(KEY_VISIBLE, visible)
        setting = kwargs.get("setting")
        if isinstance(setting, dict):
            border_color_active = setting.get("border_color_active", "#00D4FF")
            self.setData(KEY_STYLE_BG_COLOR_ACTIVE, setting.get("bg_color_active", "#00D4FF"))
            self.setData(KEY_STYLE_BG_COLOR_INACTIVE, setting.get("bg_color_inactive", "#B0E9F5"))
            self.setData(KEY_STYLE_BORDER_COLOR_ACTIVE, setting.get("border_color_active", "#00D4FF"))
            self.setData(KEY_STYLE_BORDER_COLOR_INACTIVE, setting.get("border_color_inactive", "#B0E9F5"))
            self.setData(KEY_STYLE_FONT_COLOR_ACTIVE, setting.get("font_color_active", "#000"))
            self.setData(KEY_STYLE_FONT_COLOR_INACTIVE, setting.get("font_color_inactive", "#000"))
            self.setData(KEY_STYLE_FONT_SIZE_ACTIVE, setting.get("font_size_active", 2))
            self.setData(KEY_STYLE_FONT_SIZE_INACTIVE, setting.get("font_size_inactive", 2))
            self.setPen(QPen(Qt.GlobalColor.black, 2))



    # ====== part item identity =======
    @property
    def uid(self) -> str:
        if self.platform_config.scope == SCOPE_QUESTION:
            return f"{self.part_type}::{self.part_id}::{self.question_number}"
        return f"{self.part_type}::{self.part_id}"

    @property
    def part_id(self) -> str:
        return self.data(KEY_PART_ID)

    @property
    def part_type(self) -> str:
        return self.data(KEY_TYPE)

    @property
    def is_visible(self):
        return self.data(KEY_VISIBLE)

    def set_visible(self, visibility: bool):
        if not isinstance(visibility, bool):
            raise Exception("visibility must be bool")
        self.setData(KEY_VISIBLE, visibility)

    def is_me(self, **kwargs) -> bool:
        part_type = kwargs.get("part_type")
        part_id = kwargs.get("part_id")
        if self.part_type != part_type or self.part_id != part_id:
            return False

        if self.platform_config.scope in [SCOPE_PART]:
            return True

        if self.platform_config.scope in [SCOPE_QUESTION]:
            return self.question_number == kwargs.get("qn")

        return False

    @classmethod
    def has_item(cls, items: list[QGraphicsItem], temp_item) -> bool:
        if isinstance(temp_item, PreItem):
            return any(
                isinstance(item, cls) and item.uid == temp_item.uid
                for item in items
            )

        if not isinstance(temp_item, RectanglePartItem):
            return False

        return any(
            isinstance(item, cls) and item.uid == temp_item.uid
            for item in items
        )

    # ====== question items ======
    @property
    def question_number(self) -> int | None:
        if self.platform_config.scope in [SCOPE_QUESTION]:
            return self.data(KEY_QUESTION_NUMBER)
        return None

    @classmethod
    def get_max_question_number(cls, items: list[QGraphicsItem], part_id: str) -> int | None:
        if cls.platform_config.scope in [SCOPE_QUESTION]:
            max_qn = 0
            for item in items:
                if isinstance(item, cls) and item.part_id == part_id:
                    max_qn = max(max_qn, item.question_number)
            return max_qn

        return None

    # ======= item creation =======
    @classmethod
    @abstractmethod
    def pre_create(cls, items: list[QGraphicsItem], part_id: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def create_item(cls, pos: QPointF, w: float, h: float):
        pass

    # ======= item serialization =======
    def to_dict(self) -> dict | None:
        if not self.platform_config.serializable:
            return None
        item_dict = {
            "part_type": self.part_type,
            "x": self.pos().x(),
            "y": self.pos().y(),
            "part_id": self.part_id,
            "visible": self.is_visible,
        }
        if self.platform_config.sizable:
            item_dict["w"] = self.rect().width()
            item_dict["h"] = self.rect().height()
        if self.platform_config.scope in [SCOPE_QUESTION]:
            item_dict["qn"] = self.question_number
        return item_dict

    @classmethod
    def from_dict(cls, data: dict):
        if not cls.platform_config.serializable:
            return
        pos = QPointF(data["x"], data["y"])
        part_type = data["part_type"]
        part_id = data["part_id"]
        visible = data["visible"]

        return cls(part_type, part_id, pos, visible=visible)

    # ======= item repeating =======
    @classmethod
    def is_repeating(cls) -> bool | None:
        if not cls.platform_config.repeatable:
            return None
        return cls.platform_state.is_repeating

    @classmethod
    def cancel_repeating(cls):
        if not cls.platform_config.repeatable:
            return None
        cls.platform_state.is_repeating = False

    @classmethod
    def repeat(cls):
        if not cls.platform_config.repeatable:
            return None
        pre_item: PreItem = cls.platform_data.pre_item
        if not pre_item:
            return

        part_id = pre_item.part_id
        part_type = pre_item.part_type
        kwargs = pre_item.kwargs
        if cls.platform_config.scope in [SCOPE_PART]:
            part_id = get_next(part_id)
        elif cls.platform_config.scope in [SCOPE_QUESTION]:
            last_qn = pre_item.question_number
            qn = int(get_next(str(last_qn)))
            kwargs["qn"] = qn
        cls.platform_data.pre_item = PreItem(part_type, part_id, **kwargs)

    # ======= item UI =======
    def _refresh_ui(self, active):
        if active:
            self.setBrush(QBrush(QColor(self.data(KEY_STYLE_BG_COLOR_ACTIVE))))
            self.setPen(QPen(QColor(self.data(KEY_STYLE_BORDER_COLOR_ACTIVE)), 2))
        else:
            self.setBrush(QBrush(QColor(self.data(KEY_STYLE_BG_COLOR_INACTIVE))))
            self.setPen(QPen(QColor(self.data(KEY_STYLE_BORDER_COLOR_INACTIVE)), 2))

    # ======= item active state =======
    @property
    def is_active(self) -> str | None:
        if not self.platform_config.activable:
            return None
        return self.data(KEY_IS_ACTIVE)

    @classmethod
    def get_active_item_uid(cls) -> str | None:
        if not cls.platform_config.activable:
            return None
        return cls.platform_state.active_item_uid

    @classmethod
    def set_active_item(cls, items: list, **kwargs):
        if not cls.platform_config.activable:
            return None
        part_items: list[RectanglePartItem] = items
        for item in part_items:
            part_id = kwargs["part_id"]
            if item.is_me(**kwargs) and not item.is_active:
                item.setData(KEY_IS_ACTIVE, item.uid)
                cls.platform_state.active_item_uid = item.uid
                item._refresh_ui(True)
            elif item.part_id != part_id and item.is_active:
                item.setData(KEY_IS_ACTIVE, "")
                cls._active_item = ""
                item._refresh_ui(False)
