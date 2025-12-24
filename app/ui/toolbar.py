# ui/toolbar.py
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QLineEdit,
    QSpinBox,
)
from app.core.models import CORRECTION, GAP, OK, ACTION
from app.ui.button_row import ButtonRow
from app.utils.ui_tools import clear_layout

class Toolbar(QWidget):
    loadImageRequested = Signal()
    exportJsonRequested = Signal()
    def __init__(self, /):
        super().__init__()
        toolbar_layout = QVBoxLayout(self)
        toolbar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        load_btn = QPushButton("Load Image")
        export_btn = QPushButton("Export JSON")

        load_btn.clicked.connect(self.loadImageRequested.emit)
        export_btn.clicked.connect(self.exportJsonRequested.emit)
        self.error_message_label = QLabel(OK)

        page_widget = QWidget()
        page_widget_layout = QHBoxLayout(page_widget)
        self.page_label = QLabel("<No Page>")
        page_widget_layout.addWidget(self.page_label)

        tag_widget = QWidget()
        tag_widget_layout = QHBoxLayout(tag_widget)
        self.tag_edit = QLineEdit()
        tag_widget_layout.addWidget(QLabel("tag"))
        tag_widget_layout.addWidget(self.tag_edit)

        self.index_edit = None
        self.font_edit = None
        self.color_edit = None
        self.place_holder_edit = None
        self.gap_tools = None

        tag_widget = QWidget()
        tag_widget_layout = QHBoxLayout(tag_widget)
        self.tag_edit = QLineEdit()
        tag_widget_layout.addWidget(QLabel("tag"))
        tag_widget_layout.addWidget(self.tag_edit)

        self.button_row = ButtonRow()
        self.button_row.roleChangeRequest.connect(self.role_changed)
        self.role_tools_layout = QVBoxLayout()


        toolbar_layout.addWidget(load_btn)
        toolbar_layout.addWidget(export_btn)
        toolbar_layout.addWidget(self.error_message_label)
        toolbar_layout.addWidget(page_widget)
        toolbar_layout.addWidget(tag_widget)
        toolbar_layout.addWidget(self.button_row)
        toolbar_layout.addLayout(self.role_tools_layout)
        self.toolbar_layout = toolbar_layout

    def create_gap_tools(self):
        index_widget = QWidget()
        index_widget_layout = QHBoxLayout(index_widget)
        self.index_edit = QSpinBox()
        self.index_edit.setRange(1, 100)
        self.index_edit.setValue(1)
        index_widget_layout.addWidget(QLabel("index"))
        index_widget_layout.addWidget(self.index_edit)

        font_widget = QWidget()
        font_widget_layout = QHBoxLayout(font_widget)
        self.font_edit = QSpinBox()
        self.font_edit.setRange(1, 100)
        self.font_edit.setValue(12)
        font_widget_layout.addWidget(QLabel("font"))
        font_widget_layout.addWidget(self.font_edit)

        color_widget = QWidget()
        color_widget_layout = QHBoxLayout(color_widget)
        self.color_edit = QLineEdit()
        color_widget_layout.addWidget(QLabel("color"))
        color_widget_layout.addWidget(self.color_edit)

        place_holder_widget = QWidget()
        place_holder_widget_layout = QHBoxLayout(place_holder_widget)
        self.place_holder_edit = QLineEdit()
        self.place_holder_edit.setText("<gap>")
        place_holder_widget_layout.addWidget(QLabel("place holder"))
        place_holder_widget_layout.addWidget(self.place_holder_edit)

        self.gap_tools = QWidget()
        gap_tools_layout = QVBoxLayout(self.gap_tools)
        gap_tools_layout.addWidget(index_widget)
        gap_tools_layout.addWidget(font_widget)
        gap_tools_layout.addWidget(color_widget)
        gap_tools_layout.addWidget(place_holder_widget)

    def role_changed(self, role: str):
        clear_layout(self.role_tools_layout)
        if role in [GAP, CORRECTION]:
            self.create_gap_tools()
            self.role_tools_layout.addWidget(self.gap_tools)

