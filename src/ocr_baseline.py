"""
Pipeline step 1: Document -> Raw Text (OCR baseline)

Uses Tesseract OCR (with the Vietnamese language pack) instead of
training DBNet/PARSeq from scratch. The goal at this stage is NOT
the best possible OCR quality, but a working end-to-end "walking
skeleton" to build on.

Usage:
    python src/ocr_baseline.py data/samples/report.pdf
    python src/ocr_baseline.py data/samples/report.png
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_PATH")

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
        # dpi=300 for better OCR quality (slower than the default dpi)
        return convert_from_path(str(path), dpi=300, poppler_path=os.getenv("POPPLER_PATH"))
    else:
        return [Image.open(path)]


def ocr_page(image: Image.Image, lang: str = "vie+eng") -> str:
    """Run Tesseract on a single image, return the raw text."""
    return pytesseract.image_to_string(image, lang=lang)


def ocr_document(file_path: str, lang: str = "vie+eng") -> list[dict]:
    """
    Run OCR on the whole document, return results per page.
    Format: [{"page": 1, "text": "..."}, ...]
    This list-of-pages format matters: the later Information
    Extraction step will need to know which page each piece of
    text came from.
    """
    pages = load_pages(file_path)
    results = []
    for i, page_img in enumerate(pages, start=1):
        text = ocr_page(page_img, lang=lang)
        results.append({"page": i, "text": text})
        print(f"--- Page {i}/{len(pages)}: {len(text)} characters ---")
    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ocr_baseline.py <file_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output = ocr_document(input_path)

    # Save the raw text so the next step (extraction) can use it
    out_path = Path("data/output") / (Path(input_path).stem + "_raw.txt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for page in output:
            f.write(f"===== PAGE {page['page']} =====\n")
            f.write(page["text"])
            f.write("\n\n")

    print(f"\nOCR result saved to: {out_path}")
