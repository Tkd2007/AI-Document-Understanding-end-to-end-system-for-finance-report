import easyocr
import numpy as np
from PIL import Image

reader = easyocr.Reader(['vi', 'en'])


def ocr_page(image: Image.Image) -> str:
    image_array = np.array(image)
    results = reader.readtext(image_array, detail=0)
    return "\n".join(results)
