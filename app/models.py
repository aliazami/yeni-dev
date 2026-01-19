from typing import Any


class RectStyles:
    def __init__(self, styles: dict):
        self.bg_color_active = styles.get("bg_color_active", "#00D4FF")
        self.bg_color_inactive = styles.get("bg_color_inactive", "#B0E9F5")
        self.border_color_active = styles.get("border_color_active", "#00D4FF")
        self.border_color_inactive = styles.get("border_color_inactive", "#B0E9F5")
        self.font_color_active = styles.get("font_color_active", "#000")
        self.font_color_inactive = styles.get("font_color_inactive", "#000")
        self.font_family = styles.get("font_family", "Arial")
        self.font_size_active = styles.get("font_size_active", 12)
        self.font_size_inactive = styles.get("font_size_inactive", 12)

class Delta:
    def __init__(self, dx: int, dy:int):
        self._dx = dx
        self._dy = dy

    @property
    def dx(self):
        return self._dx
    
    @property
    def dy(self):
        return self._dy
    

class PreItemData:
    def __init__(self, part_type: str, part_id: str):
        # mandatory
        self._part_type: str = part_type
        self._part_id: str = part_id
        self.active: bool = False
        self.visible: bool = True
        # optional
        self.page_id: str | None = None
        self.qn: int | None = None
        self.qnn: int | None = None
        self.x: int | None = None
        self.y: int | None = None
        self.width: int | None = None
        self.height: int | None = None
        self.ui: Any | None = None

    @property
    def part_type(self):
        return self._part_type
    
    @property
    def part_id(self):
        return self._part_id
    
    def set_part_id(self, part_id: str):
        self._part_id = part_id

    def set_part_type(self, part_type: str):
        self._part_type = part_type 

    def copy(self):
        new = PreItemData(self.part_type, self.part_id)
        new.active = self.active
        new.visible = self.visible
        # optional
        new.page_id = self.page_id
        new.qn = self.qn
        new.qnn = self.qnn
        new.x = self.x
        new.y = self.y
        new.width = self.width
        new.height = self.height
        new.ui = self.ui
        return new


