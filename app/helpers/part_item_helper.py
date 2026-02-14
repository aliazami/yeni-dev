from app.pre_item import PreItem
from app.models import Input
from app.constants import (
    REF_PART_ITEM, REF_QUESTION_ITEM, REF_GROUP_ITEM,
    INPUT_TRUE_FALSE, WORD_BOUNDARY_ITEM, INPUT_NUMBERS, INPUT_BOUNDARY_MULTI, INPUT_BOUNDARY_SINGLE,
    INPUT_SELECT_WORDS_NON_SHARED, INPUT_SELECT_WORDS_SHARED,
    BOX_ITEM, GAP_ITEM, TAIL_ITEM, CAPTION_ITEM, PART_REGION_ITEM, BEHAVE_READABLE
)
from app.helpers.utils import get_answer_from_line, get_answer_lines
from app.helpers.pre_item_relations import PreItemRelations
from app.helpers.pre_item_children import PreItemChildrenTypes

def check_part_item(part_item: PreItem, descendants: list[PreItem]):
    pir = PreItemRelations(descendants)
    if part_item.part_type != REF_PART_ITEM:
        raise Exception("required a part_item")
    pict = PreItemChildrenTypes(part_item, descendants)
    if not part_region_checker(pict) or not caption_checker(pict):
        return
      
    if part_item.input:
        if not ref_part_input_general_checker(pict):
            return

        if part_item.input.input_type in [INPUT_BOUNDARY_MULTI, INPUT_BOUNDARY_SINGLE]:
            if not ref_part_input_boundary_words_checker(pict):
                return
        else:
            correct_answers = part_item.input.stripped_correct_answer
            if not pict.desc_place_holders:
                part_item.input.error = f"No place_holders. ({part_item.uid})"
                return
            if len(correct_answers) != len(pict.desc_place_holders):
                part_item.input.error = f"Mismatch place_holders number and correct answers ({part_item.uid})"
                return
            if part_item.input.input_type == INPUT_TRUE_FALSE:  
                if any([answer.upper() not in ["T", "F"] for answer in correct_answers]):
                    part_item.input.error = f"At least one answer is not either T or F ({part_item.uid})"
                    return
            if part_item.input.input_type in [INPUT_NUMBERS] and any([not answer.isdigit() for answer in correct_answers]):
                part_item.input.error = f"At least one answer is not a digit in INPUT_NUMBERS ({part_item.uid})"
                return
            
            if part_item.input.input_type in [INPUT_SELECT_WORDS_NON_SHARED, INPUT_SELECT_WORDS_SHARED]:
                pass

        for i in range(len(correct_answers)):
            place_holder = pir.find_first_place_holder_by_question_seq(i + 1)
            place_holder.input = Input(part_item.input.input_type)
            place_holder.input.correct_answer = correct_answers[i]
            place_holder.input.options = part_item.input.options
            place_holder.refresh_ui()


        part_item.input.error = ""
        return

def add_error(pict: PreItemChildrenTypes, error: str):
    pict.parent_item.input.error = f"{error} ({pict.parent_item.uid})"
    return False

def part_region_checker(pict: PreItemChildrenTypes):
    child_part_regions = pict.child_part_regions
    if not child_part_regions:
        return add_error(pict, "No part region.")
    elif len(child_part_regions) != 1:
        return add_error(pict, "more than one part_region exists")
    return True

def ref_part_input_general_checker(pict: PreItemChildrenTypes):
    child_questions = pict.child_questions
    correct_answers = pict.parent_item.input.stripped_correct_answer
    if not correct_answers:
        return add_error(pict, "No correct answers.")   
    if not child_questions:
        return add_error(pict, "No questions.")
    if len(correct_answers) != len(child_questions):
        return add_error(pict, "Mismatch question number and correct answers")   
    return True

def ref_part_input_boundary_words_checker(pict: PreItemChildrenTypes):
    part_input = pict.parent_item.input
    correct_answers_lines = get_answer_lines(part_input.correct_answer)
    correct_answers = [get_answer_from_line(answer) for answer in correct_answers_lines]    
    for question_item in pict.child_questions:
        correct_answer = correct_answers[question_item.seq - 1]
        pir = PreItemRelations(pict.descendants)
        caption_items = pir.find_children_by_types(question_item, [CAPTION_ITEM])
        if not caption_items or len(caption_items) != 1:
            return add_error(pict, "There shold be only one caption item")
        caption_item = caption_items[0]
        if not caption_item.caption_text :
            return add_error(pict, "No caption text found")
        word_boundary_items = pir.find_children_by_types(question_item, [WORD_BOUNDARY_ITEM])
        if not word_boundary_items:
            return add_error(pict, "No boundary items found")
            
        if any(not obj.caption_text for obj in word_boundary_items):
            return add_error(pict, "At least one boundary item without caption found")
        word_boundary_texts = [obj.caption_text for obj in word_boundary_items if obj.caption_text]            
        for correct_answer_item in correct_answer.split(";"):
            if correct_answer_item not in word_boundary_texts:
                return add_error(pict, "The answer `{correct_answer_item}` was not found word boundaries")
        for word_boundary in word_boundary_texts:
            if word_boundary not in caption_item.caption_text:
                return add_error(pict, "The word boundary `{word_boundary}` was not found in caption `{caption_item.caption_text}`")
        return True 

def caption_checker(pict: PreItemChildrenTypes):
    for obj in pict.descendants:
        if obj.part_type in BEHAVE_READABLE and not obj.caption_text:
            return add_error(pict, f"No caption for {obj.uid}")
    return True


# def group_checker(pict: PreItemChildrenTypes):
#     group_items = pict.child_groups
#     if not group_items:
#         return True
#     for group_item in group_items:

#     question_items = pir.find_children_by_types(REF_QUESTION_ITEM)
#     caption_items = pir.find_children_by_types(CAPTION_ITEM)
#     gap_items = pir.find_children_by_types(GAP_ITEM)
#     tail_items = pir.find_children_by_types(TAIL_ITEM)
#     word_boundary_items = pir.find_children_by_types(WORD_BOUNDARY_ITEM)
    

            
            


            
