CORRECTION = "correction"
ACTION = "action"
GAP = "gap"
OK = "<OK>"
ACTION_SIZE = 50


class LabelItemProps:
    def __init__(self, x: int, y: int, index: int, place_holder: str, role: str, tag: str, font: int, color: str):
        self.x = x
        self.y = y
        self.index = index
        self.place_holder = place_holder
        self.role = role
        self.tag = tag
        self.font = font
        self.color = color
        self.label_object = None
        self.selected = False


class ActionItemProps:
    def __init__(self, x: int, y: int, tag: str):
        self.x = x
        self.y = y
        self.tag = tag
        self.selected = False
        self.action_object = None

