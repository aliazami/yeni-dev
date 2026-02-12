import os
import pathlib
import json
from PySide6.QtWidgets import QMessageBox


IO_SETTINGS_PATH = pathlib.Path(__file__).parent.parent.resolve()
def read_settings():
    data_json = {}

    settings_path = os.path.join(IO_SETTINGS_PATH, "settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                data_json: dict = json.load(f)
        except Exception as e:
            QMessageBox.critical(None, "Load Error", str(e))
    return data_json

def write_settings(data_json: dict):
    settings_path = os.path.join(IO_SETTINGS_PATH, "settings.json")
    try:
        if data_json:
            with open(settings_path, "w") as f:
                json.dump(data_json, f, indent=4)
    except Exception as e:
        QMessageBox.critical(None, "File Write Error", str(e))

def get_settings(key: str):
    data_json = read_settings() 
    return data_json.get(key)

def set_settings(key: str, value):
    data_json = read_settings()
    data_json[key] = value
    write_settings(data_json)