from app.pre_item import PreItem
from app.constants import (
    REF_ANSWER_PART_ITEM, REF_ANSWER_QUESTION_ITEM, REF_GROUP_ITEM, REF_OPTION_ITEM,
    REF_PART_ITEM, REF_QUESTION_ITEM, REF_QUESTION_SAMPLE_ITEM, 
    BLOCK_ITEM, WORD_BOUNDARY_ITEM, BOX_ITEM, GAP_ITEM, GAP_SAMPLE_ITEM, TAIL_ITEM,
    TAIL_SAMPLE_ITEM, CAPTION_ITEM, GROUP_REGION_ITEM, PART_REGION_ITEM,
)


class PreItemChildrenTypes:
    def __init__(self, parent_item: PreItem, items: list[PreItem]):
        self._parent_item = parent_item
        self._items = items

    @property
    def descendants(self):
        return (obj for obj in self._items if self._parent_item.is_my_descendant(obj))
    
    @property
    def children(self):    
        return (obj for obj in self.descendants if self._parent_item.is_my_child(obj))

    @property
    def child_answer_parts(self):
        return [obj for obj in self.children if obj.part_type == REF_ANSWER_PART_ITEM]
        
    @property
    def child_answer_questions(self):
        return [obj for obj in self.children if obj.part_type == REF_ANSWER_QUESTION_ITEM]
        
    @property
    def child_groups(self):
        return [obj for obj in self.children if obj.part_type == REF_GROUP_ITEM]
        
    @property
    def child_options(self):
        return [obj for obj in self.children if obj.part_type == REF_OPTION_ITEM]
        
    @property
    def child_parts(self):
        return [obj for obj in self.children if obj.part_type == REF_PART_ITEM]
        
    @property
    def child_questions(self):
        return [obj for obj in self.children if obj.part_type == REF_QUESTION_ITEM]
        
    @property
    def child_question_samples(self):
        return [obj for obj in self.children if obj.part_type == REF_QUESTION_SAMPLE_ITEM]

    @property
    def child_blocks(self):
        return [obj for obj in self.children if obj.part_type == BLOCK_ITEM]

    @property
    def child_word_boundaries(self):
        return [obj for obj in self.children if obj.part_type == WORD_BOUNDARY_ITEM]

    @property
    def child_boxes(self):
        return [obj for obj in self.children if obj.part_type == BOX_ITEM]

    @property
    def child_gaps(self):
        return [obj for obj in self.children if obj.part_type == GAP_ITEM]

    @property
    def child_gap_samples(self):
        return [obj for obj in self.children if obj.part_type == GAP_SAMPLE_ITEM]

    @property
    def child_tails(self):
        return [obj for obj in self.children if obj.part_type == TAIL_ITEM]

    @property
    def child_tail_samples(self):
        return [obj for obj in self.children if obj.part_type == TAIL_SAMPLE_ITEM]

    @property
    def child_captions(self):
        return [obj for obj in self.children if obj.part_type == CAPTION_ITEM]

    @property
    def child_group_regions(self):
        return [obj for obj in self.children if obj.part_type == GROUP_REGION_ITEM]

    @property
    def child_part_regions(self):
        return [obj for obj in self.children if obj.part_type == PART_REGION_ITEM]

    # descendants
    @property
    def desc_answer_parts(self):
        return [obj for obj in self.descendants if obj.part_type == REF_ANSWER_PART_ITEM]
        
    @property
    def desc_answer_questions(self):
        return [obj for obj in self.descendants if obj.part_type == REF_ANSWER_QUESTION_ITEM]
        
    @property
    def desc_groups(self):
        return [obj for obj in self.descendants if obj.part_type == REF_GROUP_ITEM]
        
    @property
    def desc_options(self):
        return [obj for obj in self.descendants if obj.part_type == REF_OPTION_ITEM]
        
    @property
    def desc_parts(self):
        return [obj for obj in self.descendants if obj.part_type == REF_PART_ITEM]
        
    @property
    def desc_questions(self):
        return [obj for obj in self.descendants if obj.part_type == REF_QUESTION_ITEM]
        
    @property
    def desc_question_samples(self):
        return [obj for obj in self.descendants if obj.part_type == REF_QUESTION_SAMPLE_ITEM]

    @property
    def desc_blocks(self):
        return [obj for obj in self.descendants if obj.part_type == BLOCK_ITEM]

    @property
    def desc_word_boundaries(self):
        return [obj for obj in self.descendants if obj.part_type == WORD_BOUNDARY_ITEM]

    @property
    def desc_boxes(self):
        return [obj for obj in self.descendants if obj.part_type == BOX_ITEM]

    @property
    def desc_gaps(self):
        return [obj for obj in self.descendants if obj.part_type == GAP_ITEM]

    @property
    def desc_gap_samples(self):
        return [obj for obj in self.descendants if obj.part_type == GAP_SAMPLE_ITEM]

    @property
    def desc_tails(self):
        return [obj for obj in self.descendants if obj.part_type == TAIL_ITEM]

    @property
    def desc_tail_samples(self):
        return [obj for obj in self.descendants if obj.part_type == TAIL_SAMPLE_ITEM]

    @property
    def desc_captions(self):
        return [obj for obj in self.descendants if obj.part_type == CAPTION_ITEM]

    @property
    def desc_group_regions(self):
        return [obj for obj in self.descendants if obj.part_type == GROUP_REGION_ITEM]

    @property
    def desc_part_regions(self):
        return [obj for obj in self.descendants if obj.part_type == PART_REGION_ITEM]
