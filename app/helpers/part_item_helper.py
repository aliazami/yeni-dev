import re
from app.pre_item import PreItem
from app.models import Input
from app.constants import (
    REF_PART_ITEM, REF_QUESTION_ITEM,
    INPUT_TRUE_FALSE, INPUT_KEYBOARD, INPUT_NUMBERS,
    BOX_ITEM, GAP_ITEM,
)
from app.helpers.utils import get_answer_from_line

def find_place_holder(stack: list[PreItem], seq: int):
    question_item = next((obj for obj in stack if obj.seq == seq and obj.part_type == REF_QUESTION_ITEM), None)
    return next((obj for obj in stack if obj.is_my_parent(question_item) and obj.part_type in [GAP_ITEM, BOX_ITEM]), None)

def check_part_item(part_item: PreItem, descendants: list[PreItem]):
    if part_item.part_type != REF_PART_ITEM:
        raise Exception("required a part_item")
    if part_item.input:
        questions = [obj for obj in descendants if obj.part_type == REF_QUESTION_ITEM]
        boxes = [obj for obj in descendants if obj.part_type == BOX_ITEM]
        gaps = [obj for obj in descendants if obj.part_type == GAP_ITEM]
        place_holders = boxes or gaps
        correct_answers_lines = part_item.input.correct_answer.split("\n\n")
        correct_answers = [get_answer_from_line(answer) for answer in correct_answers_lines]
        if not correct_answers:
            part_item.input.error = f"No correct answers. ({part_item.uid})"
            return    

        if not place_holders:
            part_item.input.error = f"No place_holders. ({part_item.uid})"
            return
                
        if not questions:
            part_item.input.error = f"No questions. ({part_item.uid})"
            return
                
        if len(correct_answers) != len(questions):
            part_item.input.error = f"Mismatch question number and correct answers ({part_item.uid})"
            return
        
        if len(correct_answers) != len(place_holders):
            part_item.input.error = f"Mismatch place_holders number and correct answers ({part_item.uid})"
            return
        
        if part_item.input.input_type == INPUT_TRUE_FALSE:  
            if any([answer.upper() not in ["T", "F"] for answer in correct_answers]):
                part_item.input.error = f"At least one answer is not either T or F ({part_item.uid})"
                return

        if part_item.input.input_type in [INPUT_KEYBOARD, INPUT_NUMBERS]:
            if part_item.input.input_type in [INPUT_NUMBERS] and any([not answer.isdigit() for answer in correct_answers]):
                part_item.input.error = f"At least one answer is not a digit in INPUT_NUMBERS ({part_item.uid})"
                return                         
        
        for i in range(len(correct_answers)):
            place_holder = find_place_holder(descendants, i + 1)
            place_holder.input = Input(part_item.input.input_type)
            place_holder.input.correct_answer = correct_answers[i]
            place_holder.input.options = part_item.input.options
            place_holder.refresh_ui()


        part_item.input.error = ""
        return
    

            
            


            
