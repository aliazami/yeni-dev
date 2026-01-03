import easyocr
from pathlib import Path


# ==========================================
#              MAIN WINDOW
# ==========================================


if __name__ == "__main__":
    file_path = Path(__file__).parent / "test.jpg"
    print(Path(file_path).exists())
    path_string = str(file_path)
    print(path_string)
    print(type(path_string))
    reader = easyocr.Reader(["en"], gpu=False)
    result = reader.readtext(path_string)
    print(result)