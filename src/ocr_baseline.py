"""
Pipeline step 1: Document -> Raw Text (OCR baseline)

Uses EasyOCR (Vietnamese + English) instead of training DBNet/PARSeq
from scratch. The goal at this stage is NOT the best possible OCR
quality, but a working end-to-end "walking skeleton" to build on.

Usage:
    python src/ocr_baseline.py data/samples/report.pdf
    python src/ocr_baseline.py data/samples/report.png
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import easyocr
import numpy as np
from PIL import Image

reader = easyocr.Reader(['vi', 'en'])

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None


def load_pages(file_path: str) -> list[Image.Image]:
    """Return a list of page images (one image per page). A multi-page
    PDF becomes multiple images."""
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        if convert_from_path is None:
            raise RuntimeError("pdf2image is not installed")
        return convert_from_path(str(path), dpi=300, poppler_path=os.getenv("POPPLER_PATH"))
    else:
        return [Image.open(path)]


def ocr_page(image: Image.Image) -> str:
    image_array = np.array(image)
    results = reader.readtext(image_array, detail=0)
    return "\n".join(results)


def ocr_document(file_path: str) -> list[dict]:
    """
    Run OCR on the whole document, return results per page.
    Format: [{"page": 1, "text": "..."}, ...]
    """
    pages = load_pages(file_path)
    results = []
    for i, page_img in enumerate(pages, start=1):
        text = ocr_page(page_img)
        results.append({"page": i, "text": text})
        print(f"--- Page {i}/{len(pages)}: {len(text)} characters ---")
    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ocr_baseline.py <file_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output = ocr_document(input_path)

    out_path = Path("data/output") / (Path(input_path).stem + "_raw.txt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for page in output:
            f.write(f"===== PAGE {page['page']} =====\n")
            f.write(page["text"])
            f.write("\n\n")

    print(f"\nOCR result saved to: {out_path}")