import os
import json
import pathlib
from PySide6.QtWidgets import (
    QInputDialog,
    QFileDialog,
    QMessageBox,
)
from app.manager_stat import ManagerStat
from app.components.background import Background
class ManagerIO:

    def __init__(self):
        self._image_folder: str | None = None
        self._image_stem: str | None = None
        self._image_suffix: str | None = None
        self._background: Background | None = None

    @property
    def is_loaded(self):
        return bool(self._image_folder and self._image_stem and self._image_suffix and self._background)

    @property
    def image_name(self):
        if self.is_loaded:
            return self._image_stem + self._image_suffix
        
    @property
    def json_name(self):
        if self.is_loaded:
            return self._image_stem + ".json"        
    
    @property
    def image_path(self):
        if self.is_loaded:
            return os.path.join(self._image_folder, self.image_name)
    
    @property
    def json_path(self):
        return os.path.join(self._image_folder, self.json_name)
    
    @property
    def page_id(self):
        return self._image_stem or "<?>"
    

    
    def open_image(self, file_path=None, image_name=None):
        _file_path = None
        if not file_path and not image_name and self._image_folder:
            image_name, ok = QInputDialog.getText(None, "Enter page number", "Enter page number:")
            if not ok:
                return None, None
        if file_path and os.path.exists(file_path):
            _file_path = file_path
        elif self._image_folder and image_name:
            for ext in [".png", ".jpg", ".jpeg", ".webp"]:
                file_path = os.path.join(self._image_folder, image_name + ext)
                if os.path.exists(file_path):
                    _file_path = file_path
                    break
        else:
            _file_path, _ = QFileDialog.getOpenFileName(
                None, "Open Image", "", "Images (*.png *.jpg *.jpeg *.webp)"
            )
        if _file_path:
            path = pathlib.Path(_file_path)
            self._image_stem = path.stem
            self._image_suffix = path.suffix
            self._image_folder = str(path.parent)
            old_background = self._background
            self._background = Background(_file_path)
            # re-create stat if image is going to change
            return old_background, self._background
    
        return None, None
    
    def load_json(self) -> dict:
        json_path = self.json_path
        if self.is_loaded and os.path.exists(json_path):
            try:
                with open(self.json_path, "r") as f:
                    data = json.load(f)
                print(f"Loaded from {json_path}")
                return data
            except Exception as e:
                QMessageBox.critical(self, "Load Error", str(e))