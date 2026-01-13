
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

