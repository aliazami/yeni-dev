from app.pre_item import PreItem
from app.helpers.pre_item_relations import PreItemRelations
from app.constants import (
    REF_PART_ITEM, REF_UNIT_ITEM
)

def export_doc(items: list[PreItem], page: str):
    parts = []
    pir = PreItemRelations(items)
    part_items = pir.get_all_by_type(REF_PART_ITEM)
    unit_items = pir.get_all_by_type(REF_UNIT_ITEM)
    for part_item in part_items:
        doc = get_descendant_dict(part_item, items)
        parts.append(doc)
    return {
        "page": page,
        "unit": unit_items[0].seq,
        "parts": parts
    }


def filtered_item_doc(item: PreItem):
    doc = item.to_dict()

    return doc

def get_descendant_dict(parent_item: PreItem, all_items: list[PreItem]):
    if parent_item not in all_items:
        raise ValueError("parent_item must exist in all_items")

    # Get direct children
    children = [
        item for item in all_items
        if parent_item.is_my_child(item)
    ]

    # Build current node dict
    node_dict = filtered_item_doc(parent_item)

    # Recursively build children tree
    node_dict["children"] = [
        get_descendant_dict(child, all_items)
        for child in children
    ]

    return node_dict