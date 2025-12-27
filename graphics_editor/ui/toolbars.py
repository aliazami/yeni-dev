from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction
from utils.icon_utils import create_icon
from constants import (ALIGN_LEFT, ALIGN_RIGHT, ALIGN_TOP, ALIGN_BOTTOM,
                       DISTRIBUTE_HORIZONTAL, DISTRIBUTE_VERTICAL)

def create_alignment_toolbar(parent, scene):
    toolbar = QToolBar("Alignment", parent)
    
    # Alignment actions
    act_left = QAction(create_icon("align_left"), "Left", parent)
    act_left.triggered.connect(lambda: scene.align_items(ALIGN_LEFT))
    
    act_right = QAction(create_icon("align_right"), "Right", parent)
    act_right.triggered.connect(lambda: scene.align_items(ALIGN_RIGHT))
    
    act_top = QAction(create_icon("align_top"), "Top", parent)
    act_top.triggered.connect(lambda: scene.align_items(ALIGN_TOP))
    
    act_btm = QAction(create_icon("align_bottom"), "Bottom", parent)
    act_btm.triggered.connect(lambda: scene.align_items(ALIGN_BOTTOM))
    
    # Distribution actions
    act_d_h = QAction(create_icon("dist_horz"), "Dist H", parent)
    act_d_h.triggered.connect(lambda: scene.distribute_items(DISTRIBUTE_HORIZONTAL))
    
    act_d_v = QAction(create_icon("dist_vert"), "Dist V", parent)
    act_d_v.triggered.connect(lambda: scene.distribute_items(DISTRIBUTE_VERTICAL))
    
    # Add actions to toolbar
    toolbar.addAction(act_left)
    toolbar.addAction(act_right)
    toolbar.addAction(act_top)
    toolbar.addAction(act_btm)
    toolbar.addSeparator()
    toolbar.addAction(act_d_h)
    toolbar.addAction(act_d_v)
    
    return toolbar