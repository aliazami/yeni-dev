# app/dialogs.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QComboBox,
    QTextEdit,
)
from PySide6.QtGui import QKeySequence, QShortcut, QFont
from app.models import Input
from app.constants import (
    ALL_INPUT_STYLES,
    INPUT_SELECT_WORDS_SHARED,
    INPUT_SELECT_WORDS_NON_SHARED,
)


# ==========================================
#              GUI COMPONENTS
# ==========================================

EMPTY = "<none>"
COPY_ANSWERS = "COPY_ANSWERS"



class RectInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Rectangle Details")
        self.resize(300, 150)
        layout = QFormLayout(self)
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter Integer ID")
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Enter Text")
        layout.addRow("Rectangle ID (Int):", self.id_input)
        layout.addRow("Description:", self.text_input)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self):
        return self.id_input.text().strip(), self.text_input.text().strip()
    
class PartSelectDialog(QDialog):
    def __init__(self, child_options: list[tuple[str, str]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Part Item Type")
        self.resize(300, 150)
        self.child_options = child_options
        layout = QVBoxLayout(self)
        self.combo_box = QComboBox()
        for child_type in self.child_options:
            self.combo_box.addItem(child_type[0])
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter ID:")
        id_str = str(self.child_options[0][1])
        self.id_input.setText(id_str)
        self.combo_box.currentIndexChanged.connect(self.update_label)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(self.combo_box)
        layout.addWidget(self.id_input)
        layout.addWidget(buttons)
        self.combo_box.setCurrentIndex(0)

    def update_label(self, selected_type):
        id_str = str(self.child_options[selected_type][1])
        self.id_input.setText(id_str)


    def get_data(self):
        return self.combo_box.currentText(), int(self.id_input.text().strip())


class InputSelectDialog(QDialog):
    def __init__(self, input_types: set[str], input_obj: Input = None, answers: dict[str, str] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Input Type")
        self.resize(300, 150)
        self.buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
            )
        self.ok_button = self.buttons.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        layout = QVBoxLayout(self)
        self.answers = answers
        self.text_correct_answer = MyTextEdit()
        self.combo_input_type = QComboBox()
        self.combo_input_type.addItem(EMPTY)
        self.combo_input_type.currentTextChanged.connect(self.combo_input_type_change)
        self.combo_answers = QComboBox()
        self.combo_answers.addItem(EMPTY)
        self.combo_input_style = QComboBox()
        self.combo_input_style.addItem(EMPTY)
        self.combo_input_style.setEnabled(False)        
        self.combo_options = QComboBox()
        self.combo_options.addItem(EMPTY)
        self.combo_options.addItem(COPY_ANSWERS)
        self.combo_options.currentTextChanged.connect(self.combo_options_change)

        for input_type in input_types:
            self.combo_input_type.addItem(input_type)
        if answers:
            for key in answers.keys():
                self.combo_answers.addItem(key)
                self.combo_options.addItem(key)
            self.combo_answers.setEnabled(True)
            self.combo_answers.currentTextChanged.connect(self.combo_answers_change)
            self.combo_answers.setCurrentIndex(0)
            self.combo_answers_change(selected_key=next(iter(answers)))

        self.text_correct_answer.setup()

        self.text_options = MyTextEdit()
        self.text_options.setup()
   
        if input_obj:
            self.combo_input_type.setCurrentText(input_obj.input_type)
            self.text_correct_answer.setMarkdown(input_obj.correct_answer)
            self.text_options.setMarkdown(input_obj.options)
            if input_obj.style:
                self.combo_input_style.setCurrentText(input_obj.style)
        else:
            self.combo_input_type.setCurrentIndex(0)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(QLabel("input type"))
        layout.addWidget(self.combo_input_type)
        layout.addWidget(QLabel("answer type"))
        layout.addWidget(self.combo_answers)        
        layout.addWidget(QLabel("correct answer"))
        layout.addWidget(self.text_correct_answer)
        layout.addWidget(QLabel("option type"))
        layout.addWidget(self.combo_options)         
        layout.addWidget(QLabel("options"))
        layout.addWidget(self.text_options)
        layout.addWidget(QLabel("input style"))
        layout.addWidget(self.combo_input_style)                
        layout.addWidget(self.buttons)

    def check_form(self):
        check = True
        if self.combo_input_type.currentText() == EMPTY or self.combo_answers.currentText() == EMPTY:
            check = False
        self.ok_button.setEnabled(check)

    def combo_options_change(self, selected_key):
        if selected_key == COPY_ANSWERS:
            self.text_options.setMarkdown(self.text_correct_answer.get_mark_down())
        elif ans_value := self.answers.get(selected_key):
            self.text_options.setMarkdown(ans_value)
        
        self.check_form()

    def combo_answers_change(self, selected_key):
        if not self.answers.get(selected_key):
            return
        self.text_correct_answer.setMarkdown(self.answers[selected_key])
        self.check_form()

    def combo_input_type_change(self, selected_key):
        if selected_key in [INPUT_SELECT_WORDS_SHARED, INPUT_SELECT_WORDS_NON_SHARED]:
            self.combo_options.setEnabled(True)
            self.text_options.setEnabled(True)           
        else:
            self.combo_options.setCurrentText(EMPTY)
            self.text_options.setText("")
            self.combo_options.setEnabled(False)
            self.text_options.setEnabled(False)               
        self.combo_input_style.clear()
        self.combo_input_style.addItem(EMPTY)
        if style_options := ALL_INPUT_STYLES.get(selected_key):
            self.combo_input_style.addItems(style_options)
            self.combo_input_style.setEnabled(True)
        else:
            self.combo_input_style.setEnabled(False)               
        self.check_form()

    def get_data(self):
        input_type = self.combo_input_type.currentText()
        correct_answer = self.text_correct_answer.get_mark_down()
        options = self.text_options.get_mark_down()
        combo_input_style = self.combo_input_style.currentText()
        input_style = combo_input_style if combo_input_style != EMPTY else ""
        return input_type, correct_answer, options, input_style 


class MyTextEdit(QTextEdit):
    def __init_subclass__(cls):
        return super().__init_subclass__()
    
    def setup(self):
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextEditorInteraction |  # Basic editing
            Qt.TextInteractionFlag.TextSelectableByMouse |  # Select with mouse
            Qt.TextInteractionFlag.TextSelectableByKeyboard # Select with keyboard
        )    
        self.setup_shortcuts()        

    def setup_shortcuts(self):
        """Explicitly set up formatting shortcuts"""
        
        # Bold - Ctrl+B
        bold_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        bold_shortcut.activated.connect(self.toggle_bold)
        
        # Italic - Ctrl+I
        italic_shortcut = QShortcut(QKeySequence("Ctrl+I"), self)
        italic_shortcut.activated.connect(self.toggle_italic)
        
        # Underline - Ctrl+U
        underline_shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
        underline_shortcut.activated.connect(self.toggle_underline)
        
        # Strikethrough - Ctrl+S (not standard, but useful)
        strike_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        strike_shortcut.activated.connect(self.toggle_strikethrough)
        
    def toggle_bold(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            fmt = cursor.charFormat()
            weight = QFont.Weight.Bold if fmt.fontWeight() != QFont.Weight.Bold else QFont.Weight.Normal
            new_fmt = cursor.charFormat()
            new_fmt.setFontWeight(weight)
            cursor.mergeCharFormat(new_fmt)
            
    def toggle_italic(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            fmt = cursor.charFormat()
            italic = not fmt.fontItalic()
            new_fmt = cursor.charFormat()
            new_fmt.setFontItalic(italic)
            cursor.mergeCharFormat(new_fmt)
            
    def toggle_underline(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            fmt = cursor.charFormat()
            underline = not fmt.fontUnderline()
            new_fmt = cursor.charFormat()
            new_fmt.setFontUnderline(underline)
            cursor.mergeCharFormat(new_fmt)
            
    def toggle_strikethrough(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            fmt = cursor.charFormat()
            strikeout = not fmt.fontStrikeOut()
            new_fmt = cursor.charFormat()
            new_fmt.setFontStrikeOut(strikeout)
            cursor.mergeCharFormat(new_fmt)

    def get_html(self):
        return self.toHtml()
    
    def get_mark_down(self):
        return self.toMarkdown().strip()
    
    def get_plain_text(self):
        return self.toPlainText()


class CaptionEditDialog(QDialog):
    def __init__(self, md_text: str = ""):
        super().__init__(None)
        self.setWindowTitle("Edit Caption")
        self.resize(300, 150)
        layout = QVBoxLayout(self)
        self.text_edit = MyTextEdit()
        self.text_edit.setup()
        self.text_edit.setMarkdown(md_text)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)        
        layout.addWidget(self.text_edit)
        layout.addWidget(buttons)

    def get_data(self):
        return self.text_edit.get_mark_down()


class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help")
        self.resize(300, 320)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        layout = QVBoxLayout()
        help_text = (
            "<b>COMMANDS:</b><br>"
            "<b>Ctrl+S</b> : Save<br>"
            "<b>Ctrl+Shift+S</b> : Save As<br>"
            "<b>Ctrl+O</b> : Open<br>"
            "<b>Ctrl+Z</b> : Undo<br>"
            "<b>Ctrl+Shift+Z</b> : Redo<br>"
            "<b>I</b> : Import Background Image<br>"
            "<b>A</b> : Add Circle<br>"
            "<b>R</b> : Add Rectangle<br>"
            "<b>F</b> : Add Label<br>"
            "<b>G</b> : Add Label 2<br>"
            "<b>1</b> : Toggle Alignment Toolbar<br>"
        )
        label = QLabel(help_text)
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)
        self.setLayout(layout)
