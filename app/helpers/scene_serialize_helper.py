from app.scene import EditorScene
from app.components.part_item import PartItem
from app.components.gap_item import GapItem
from app.components.word_boundary_item import WordBoundaryItem
from app.models import ISerializable


# --- Serialization Logic ---
def deserialize_scene_helper(scene: EditorScene, data):
    # 1. Clear everything (C++ objects are deleted)
    scene.clear()
    scene.undo_stack.clear()

    # Reset Python references to avoid accessing deleted C++ objects
    scene.temp_rect_item = None
    scene.current_part = None

    # 2. Restore Background EXPLICITLY
    # We manually create the background here instead of calling helper methods
    # like set_image_background() or init_default_background().
    # This avoids calling removeItem() on a deleted object.

    bg_path = data.get("background_image")
    scene.set_background(bg_path)

    # 3. Restore Items
    for item_data in data.get("items", []):
        itype = item_data["type"]

        if itype == "CIRCLE":
            part_item = PartItem.from_dict(item_data)
            scene.addItem(part_item)
        elif itype == "LABEL":
            gap_item = GapItem.from_dict(item_data)
            scene.addItem(gap_item)
        elif itype == "RECTANGLE":
            word_boundary_item = WordBoundaryItem.from_dict(item_data)
            scene.addItem(word_boundary_item)

    scene.refresh_active_items()


# --- UPDATED Serialize to include Rect Size ---
def serialize_scene_helper(scene: EditorScene):
    background_path = (
        scene.background_item.file_path() if scene.background_item else None
    )
    data = {"background_image": background_path, "items": []}
    for item in scene.items():
        if isinstance(item, ISerializable):
            serializable = item
            item_data = serializable.to_dict()
            data["items"].append(item_data)

    return data
