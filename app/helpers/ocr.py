import cv2
from easyocr import Reader
from PySide6.QtCore import QRectF


class ImageReader:
    def __init__(self):
        self._reader: Reader | None = None

    @property
    def reader(self):
        if self._reader is None:
            self._reader = Reader(["en"], gpu=False)
        return self._reader

    def read_image(self, image_path: str, target_rect):
        big_image = cv2.imread(image_path)

        # Define crop rectangle (x, y, width, height) or (y1:y2, x1:x2)
        x1, y1, x2, y2 = target_rect
        cropped_image = big_image[y1:y2, x1:x2]
        cv2.imwrite("/home/azami/Downloads/cropped.jpg", cropped_image)
        print("writen: /home/azami/Downloads/cropped.jpg ")

        # Use EasyOCR on the cropped image
        result = self.reader.readtext(cropped_image, paragraph=True)  # Pass numpy array directly
        if result:
            return result[0][1]