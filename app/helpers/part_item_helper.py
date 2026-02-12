from app.pre_item import PreItem
from app.models import Input
from app.constants import (
    REF_PART_ITEM, REF_QUESTION_ITEM,
    INPUT_TRUE_FALSE, WORD_BOUNDARY_ITEM, INPUT_NUMBERS, INPUT_BOUNDARY_MULTI, INPUT_BOUNDARY_SINGLE,
    INPUT_SELECT_WORDS_NON_SHARED, INPUT_SELECT_WORDS_SHARED,
    BOX_ITEM, GAP_ITEM, TAIL_ITEM, CAPTION_ITEM, PART_REGION_ITEM, BEHAVE_READABLE
)
from app.helpers.utils import get_answer_from_line, get_answer_lines
from app.helpers.pre_item_relations import PreItemRelations

def check_part_item(part_item: PreItem, descendants: list[PreItem]):
    pir = PreItemRelations(descendants)
    if part_item.part_type != REF_PART_ITEM:
        raise Exception("required a part_item")
    if not pir.find_children_by_types(part_item, PART_REGION_ITEM):
        part_item.input.error = f"No part region. ({part_item.uid})"
        return
    for obj in pir.get_descendants(part_item):
        if obj.part_type in BEHAVE_READABLE and not obj.caption_text:
            part_item.input.error = f"No caption ({obj.uid})"
            return        
    if part_item.input:
        questions = pir.get_all_by_type(REF_QUESTION_ITEM)
        boxes = pir.get_all_by_type(BOX_ITEM)
        gaps = pir.get_all_by_type(GAP_ITEM)
        tails = pir.get_all_by_type(TAIL_ITEM)
        place_holders = boxes or gaps or tails
        correct_answers_lines = get_answer_lines(part_item.input.correct_answer)
        correct_answers = [get_answer_from_line(answer) for answer in correct_answers_lines]
        if not correct_answers:
            part_item.input.error = f"No correct answers. ({part_item.uid})"
            return    
        if not questions:
            part_item.input.error = f"No questions. ({part_item.uid})"
            return
        if len(correct_answers) != len(questions):
            part_item.input.error = f"Mismatch question number and correct answers ({part_item.uid})"
            return
        if part_item.input.input_type in [INPUT_BOUNDARY_MULTI, INPUT_BOUNDARY_SINGLE]:
            for question_item in questions:
                correct_answer = correct_answers[question_item.seq - 1]

                caption_items = pir.find_children_by_types(question_item, [CAPTION_ITEM])
                if not caption_items or len(caption_items) != 1:
                    part_item.input.error = f"There shold be only one caption item for ({question_item.uid})"
                    return
                caption_item = caption_items[0]
                if not caption_item.caption_text :
                    part_item.input.error = f"No caption text found for ({question_item.uid})"
                    return
                word_boundary_items = pir.find_children_by_types(question_item, [WORD_BOUNDARY_ITEM])
                if not word_boundary_items:
                    part_item.input.error = f"No boundary items found for ({question_item.uid})"
                    return
                if any(not obj.caption_text for obj in word_boundary_items):
                    part_item.input.error = f"At least one boundary item without caption found for ({question_item.uid})"
                    return
                word_boundary_texts = [obj.caption_text for obj in word_boundary_items if obj.caption_text]            
                for correct_answer_item in correct_answer.split(";"):
                    if correct_answer_item not in word_boundary_texts:
                        part_item.input.error = f"The answer `{correct_answer_item}` was not found word boundaries for ({question_item.uid})"
                        return
                for word_boundary in word_boundary_texts:
                    if word_boundary not in caption_item.caption_text:
                        part_item.input.error = f"The word boundary `{word_boundary}` was not found in caption `{caption_item.caption_text}` for ({question_item.uid})"
                        return
                part_item.input.error = ""
                return
        else:
            if not place_holders:
                part_item.input.error = f"No place_holders. ({part_item.uid})"
                return
            if len(correct_answers) != len(place_holders):
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
    

            
            


            
