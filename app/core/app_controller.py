# core/controller.py
import json
import os
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMessageBox
from app.ui.main_window import MainWindow
from app.ui.label_item import LabelItem
from app.ui.action_item import ActionItem
from app.utils.general import get_first_missing_index
from app.core.models import LabelItemProps, ActionItemProps, OK, ACTION, GAP, CORRECTION


class AppController:
    def __init__(self, main_window: MainWindow):
        self.image_path = None
        self.gaps = []
        self.corrections = []
        self.actions = []
        self.main_window = main_window
        self.main_window.toolbar.loadImageRequested.connect(self.load_image)
        self.main_window.toolbar.exportJsonRequested.connect(self.export_json)
        self.main_window.toolbar.button_row.roleChangeRequest.connect(self.role_change)
        self.main_window.view.sceneShiftLeftClickRequest.connect(self.add_item)
        self.check()

    def load_image(self, path = None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "Select Image",
                "",
                "Images (*.jpg *.jpeg *.png *.webp)",
            )
        if not path:
            return self.check()

        self.image_path = path
        self.main_window.view.load_image(self.image_path)
        page_name = "Page: " + (self.get_page() or "<Nothing>")
        self.main_window.toolbar.page_label.setText(page_name)
        return self.check()

    def add_item(self, x: int, y: int):
        role = self.main_window.toolbar.button_row.property("role")
        if role == ACTION:
            return self.add_action(x, y)
        elif role == GAP or role == CORRECTION:
            return self.add_label(x, y)

    def add_label(self, x: int, y: int):
        props = self.get_label_props_from_toolbar(x, y)
        if not props.tag:
            return self.set_message("No Tag")
        if self.search_label(props.tag, props.index, props.role):
            return self.set_message(f"Another {props.tag}.{props.index} <{props.role}> already exists")
        label = LabelItem(props)
        label.deleteRequest.connect(self.delete_label)
        self.main_window.view.scene().addItem(label)
        label.setFocus()
        if props.role == GAP:
            self.gaps.append(label)
        elif props.role == CORRECTION:
            self.corrections.append(label)
        self.main_window.toolbar.index_edit.setValue(props.index + 1)
        return self.check()

    def add_action(self, x: int, y: int):
        props = self.get_action_props_from_toolbar(x, y)
        if not props.tag:
            return self.set_message("No Tag")
        if self.search_action(props.tag):
            return self.set_message(f"Action {props.tag} already exists")
        action = ActionItem(props)
        action.deleteRequest.connect(self.delete_action)
        self.main_window.view.scene().addItem(action)
        action.setFocus()
        self.actions.append(action)
        return self.check()

    def export_json(self):
        if not self.image_path:
            QMessageBox.warning(self.main_window, "No Image", "Load an image first.")
            return

        data = {"words": []}

        for item in self.gaps:
            if item.scene() is None:
                continue  # deleted

            pos = item.pos()
            data["words"].append(
                {
                    "word": item.toPlainText(),
                    "x": int(pos.x()),
                    "y": int(pos.y()),
                }
            )

        base, _ = os.path.splitext(self.image_path)
        out_path = base + ".json"

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        QMessageBox.information(self.main_window, "Exported", f"Saved:\n{out_path}")
        return self.check()

    def focus_in(self, props: LabelItemProps):
        self.main_window.current_item = props.label_object
        return self.check()

    def focus_out(self):
        self.main_window.current_item = None
        return self.check()

    def get_page(self):
        if self.image_path:
            return Path(self.image_path).stem

    def get_label_props_from_toolbar(self, x: int, y: int):
        t = self.main_window.toolbar
        return LabelItemProps(
            x=x,
            y=y,
            index=t.index_edit.value(),
            place_holder=t.place_holder_edit.text(),
            role=t.button_row.property("role"),
            tag=t.tag_edit.text(),
            font=t.font_edit.value(),
            color=t.color_edit.text(),
        )

    def get_action_props_from_toolbar(self, x: int, y: int):
        t = self.main_window.toolbar
        return ActionItemProps(
            x=x,
            y=y,
            tag=t.tag_edit.text(),
        )

    def check(self) -> bool:
        if not self.get_page():
            return self.set_message("No image")
        for role in [GAP, CORRECTION]:
            tags = self.get_label_tags(role)
            for tag in tags:
                indices = self.get_label_indices(GAP, tag)
                missing_gap_index = get_first_missing_index(indices)
                if missing_gap_index:
                    return self.set_message(f"{role} {tag}.{missing_gap_index} is missing")

        for item in self.gaps:
            gap: LabelItem = item
            gap_props: LabelItemProps = gap.property("props")
            if not self.search_action(gap_props.tag):
                return self.set_message(f"No Action found for gap {gap_props.tag}.{gap_props.index}")
            if not self.search_label(gap_props.tag, gap_props.index, CORRECTION):
                return self.set_message(f"No correction found for gap {gap_props.tag}.{gap_props.index}")

        for item in self.corrections:
            correction: LabelItem = item
            correction_props: LabelItemProps = correction.property("props")
            if not self.search_action(correction_props.tag):
                return self.set_message(f"No Action found for correction {correction_props.tag}.{correction_props.index}")
            if not self.search_label(correction_props.tag, correction_props.index, GAP):
                return self.set_message(f"No gap found for correction {correction_props.tag}.{correction_props.index}")

        for item in self.actions:
            action: ActionItem = item
            action_props: ActionItemProps = action.data(Qt.ItemDataRole.UserRole)
            if not self.search_label(action_props.tag, 1, GAP):
                return self.set_message(f"No gap {action_props.tag}.1 found")


        return self.set_message(OK, False)

    def set_message(self, msg: str, is_error=True):
        lbl = self.main_window.toolbar.error_message_label
        lbl.setText(msg)
        lbl.setStyleSheet("color: #ff0000;" if is_error else "color: #f5f5f5;")
        return is_error

    def search_label(self, tag: str, index: int, role: str) -> LabelItem | None:
        collection = self.corrections if role == CORRECTION else self.gaps
        for item in collection:
            label: LabelItem = item
            if label.scene() is None:
                collection.remove(label)
                continue  # deleted
            props: LabelItemProps = label.property("props")
            if props.tag == tag and props.index == index:
                return label

    def search_action(self, tag: str) -> ActionItem | None:
        for item in self.actions:
            action: ActionItem = item
            if action.scene() is None:
                self.actions.remove(action)
                continue  # deleted
            props: LabelItemProps = action.data(Qt.ItemDataRole.UserRole)
            if props.tag == tag:
                return action

    def delete_label(self, p: LabelItemProps):
        label = self.search_label(p.tag, p.index, p.role)
        if not label:
            return self.set_message(f"No {p.role} {p.tag}.{p.index} was found for delete")
        if p.role == GAP:
            self.gaps.remove(label)
        elif p.role == CORRECTION:
            self.corrections.remove(label)

        return self.check()

    def delete_action(self, p: ActionItemProps):
        action = self.search_action(p.tag)
        if not action:
            return self.set_message(f"No Action {p.tag} was found for delete")

        self.actions.remove(action)
        return self.check()

    def role_change(self, role: str):
        toolbar_prop = self.get_label_props_from_toolbar(0, 0)
        tag = toolbar_prop.tag
        indices = self.get_label_indices(role, tag)
        max_index = max(indices) if indices else 0
        self.main_window.toolbar.index_edit.setValue(max_index + 1)


    def get_label_indices(self, role: str, tag: str):
        indices = []
        collection: list = self.gaps if role == GAP else self.corrections
        for item in collection:
            label: LabelItem = item
            label_props: LabelItemProps = label.property("props")
            if label_props.tag == tag:
                indices.append(label_props.index)
        return indices

    def get_label_tags(self, role: str):
        tags_set = set()
        collection: list = self.gaps if role == GAP else self.corrections
        for item in collection:
            label: LabelItem = item
            label_props: LabelItemProps = label.property("props")
            tags_set.add(label_props.tag)
        return tags_set