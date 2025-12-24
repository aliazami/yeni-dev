from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup

from app.core.models import ACTION, CORRECTION, GAP
from app.ui.role_button import RoleButton

class ButtonRow(QWidget):
    roleChangeRequest = Signal(str)
    def __init__(self):
        super().__init__()

        # 1. Create the Layout
        layout = QHBoxLayout(self)
        layout.setSpacing(0)  # Make buttons touch each other
        layout.setContentsMargins(0, 0, 0, 0)  # Remove outer padding

        # 2. Create the Logic Group
        # This group ensures only one button is 'checked' at a time
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.setProperty("role", GAP)
        # 3. Create Buttons
        roles = {"A": ACTION, "C": CORRECTION, "G": GAP}

        for key, role in roles.items():
            btn = RoleButton(key, role)
            btn.roleButtonRequest.connect(self.role_set)
            # Add to layout and group
            layout.addWidget(btn)
            self.button_group.addButton(btn)



    def role_set(self, role: str):
        self.setProperty("role", role)
        self.roleChangeRequest.emit(role)