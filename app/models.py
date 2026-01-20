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
    def __init__(self):
        # mandatory
        self.part_type: str = "part_type?"
        self.parent_id: str = "parent_id?"
        self.seq: int = -1
        self.active: bool = False
        self.visible: bool = True
        # optional
        self.tag: str | None = None
        self.x: int | None = None
        self.y: int | None = None
        self.width: int | None = None
        self.height: int | None = None
        self.ui: Any | None = None


    def copy(self):
        new = PreItemData()
        new.part_type = self.part_type
        new.parent_id = self.parent_id
        new.seq = self.seq
        new.active = self.active
        new.visible = self.visible
        # optional
        new.tag = self.tag
        new.x = self.x
        new.y = self.y
        new.width = self.width
        new.height = self.height
        new.ui = self.ui
        return new


