from PySide6.QtCore import QRectF
from app.helpers.ocr import ImageReader

def read_gap_caption(caption: QRectF, gaps: list[QRectF], image_path: str):
    if len(gaps) < 1:
        raise Exception("unexpected condition")    
    top = caption.top()
    height = caption.height()
    left1 = caption.left()
    width1 = gaps[0].left() - left1
    rect1 = QRectF(left1, top, width1, height)
    reader = ImageReader()
    text1 = reader.read_image(image_path, rect1)
    if not text1:
        raise Exception("Text1 not recognized")    
    left2 = gaps[0].right()
    width2 = caption.right() - left2
    rect2 = QRectF(left2, top, width2, height)
    if len(gaps) > 1:
        new_caption = rect2
        new_gas = gaps[1:]
        other_texts = read_gap_caption(new_caption, new_gas, image_path)
        return [text1, *other_texts]
    #else:
    text2 = reader.read_image(image_path, rect2)
    if not text2:
        raise Exception("Text2 not recognized")
    
    return [text1, text2]