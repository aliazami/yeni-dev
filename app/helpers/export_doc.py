from app.pre_item import PreItem
from app.helpers.pre_item_relations import PreItemRelations
from app.constants import (
    REF_PART_ITEM, REF_QUESTION_ITEM, REF_GROUP_ITEM, CAPTION_ITEM
)

def export_doc(items: list[PreItem], page: str):
    parts = []
    pir = PreItemRelations(items)
    ref_part_items = pir.get_all_by_type(REF_PART_ITEM)
    for ref_part_item in ref_part_items:
        ref_parent_unit = pir.get_item(ref_part_item.parent_id)
        ref_question_items = pir.find_children_by_types(ref_part_item, [REF_QUESTION_ITEM])
        ref_group_items = pir.find_children_by_types(ref_part_item, [REF_GROUP_ITEM])
        part_captions = pir.find_children_by_types(ref_part_item, [CAPTION_ITEM])
        part = {
            "page": page,
            "parent_unit_seq": ref_parent_unit.seq,
            "seq": ref_part_item.seq,
            "input_type": ref_part_item.input.input_type if ref_part_item.input else None,
            "captions"


        }
        decendants = pir.get_descendants(ref_part_item)
