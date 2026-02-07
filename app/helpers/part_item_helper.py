from app.pre_item import PreItem
from app.constants import (
    REF_PART_ITEM, REF_QUESTION_ITEM,
    INPUT_TRUE_FALSE, INPUT_KEYBOARD, INPUT_NUMBERS,
    BOX_ITEM, GAP_ITEM,
)

def check_part_item(part_item: PreItem, descendants: list[PreItem]):
    if part_item.part_type != REF_PART_ITEM:
        raise Exception("required a part_item")
    if part_item.input:
        questions = [obj for obj in descendants if obj.part_type == REF_QUESTION_ITEM]
        boxes = [obj for obj in descendants if obj.part_type == BOX_ITEM]
        gaps = [obj for obj in descendants if obj.part_type == GAP_ITEM]
        place_holders = boxes or gaps
        correct_answers = part_item.input.correct_answer.split("\n\n")

        if part_item.input.input_type == INPUT_TRUE_FALSE:
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
            
            if any([answer.upper() not in ["T", "F"] for answer in correct_answers]):
                part_item.input.error = f"At least one answer is not either T or F ({part_item.uid})"
                return
        
        if part_item.input.input_type in [INPUT_KEYBOARD, INPUT_NUMBERS]:
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

            if part_item.input.input_type in [INPUT_NUMBERS] and any([not answer.isdigit() for answer in correct_answers]):
                part_item.input.error = f"At least one answer is not a digit in INPUT_NUMBERS ({part_item.uid})"
                return                         
        
        part_item.input.error = ""
        return
            
            


            
