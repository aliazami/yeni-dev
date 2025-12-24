from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton


class RoleButton(QPushButton):
    roleButtonRequest = Signal(str)
    def __init__(self, key: str, role: str):
        super().__init__(key)
        self.setProperty("role", role)
        self.setCheckable(True)  # Crucial: Allows the button to stay pressed
        self.setFixedSize(30, 30)  # Make them "tiny"
        self.clicked.connect(self.role_set)

        # 4. Apply Styles (CSS)
        # We use the :checked pseudo-state to handle the blue color
        self.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #bdc3c7;
                font-weight: bold;
                color: black;
            }
            /* Style for when the button is active/selected */
            QPushButton:checked {
                background-color: #3498db; /* Blue */
                color: white;
                border: 1px solid #2980b9;
            }
            /* Optional: Hover effect */
            QPushButton:hover:!checked {
                background-color: #dcdcdc;
            }
        """)

    def role_set(self):
        self.roleButtonRequest.emit(self.property("role"))

