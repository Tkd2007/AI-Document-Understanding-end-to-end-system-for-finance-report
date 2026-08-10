import easyocr
import numpy as np

reader = easyocr.Reader(['vi', 'en'])


def ocr_page(image: Image.Image) -> str:
    ...