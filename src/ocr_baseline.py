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

import numpy as np
from PIL import Image

from layout_detection import get_table_regions

LANGUAGES = ["vi", "en"]
PDF_DPI = 300

_reader = None

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None


def get_reader():
    """
    Khởi tạo EasyOCR ở lần gọi đầu tiên rồi tái sử dụng.

    Trước đây reader được tạo ngay lúc import. Vì extract_vlm.py cũng
    import module này (để dùng load_pages/load_table_regions), chạy nhánh
    VLM thuần vẫn phải chờ nạp xong model OCR không dùng tới.
    """
    global _reader
    if _reader is None:
        import easyocr

        _reader = easyocr.Reader(LANGUAGES)
    return _reader


def load_pages(file_path: str) -> list[Image.Image]:
    """Return a list of page images (one image per page). A multi-page
    PDF becomes multiple images."""
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        if convert_from_path is None:
            raise RuntimeError("pdf2image is not installed")
        return convert_from_path(
            str(path), dpi=PDF_DPI, poppler_path=os.getenv("POPPLER_PATH")
        )
    else:
        return [Image.open(path)]


def load_table_regions(file_path: str) -> list[dict]:
    """
    Load document, chạy layout detection, trả về các vùng bảng theo trang:
        [{"page": 1, "regions": [Image, ...]}, ...]
    mỗi trang trả về các vùng bảng tìm được; nếu không tìm thấy bảng nào 
    thì trả về nguyên trang gốc (fail open — để không mất dữ liệu ở trang 
    mà YOLO nhận nhầm).

    Tách riêng khỏi ocr_document() để router.py tính MỘT LẦN rồi dùng
    chung cho cả nhánh OCR lẫn nhánh VLM. Convert PDF ở 300 DPI và chạy
    YOLO là hai việc đắt nhất trong pipeline; trước đây mỗi nhánh tự làm
    lại từ đầu nên báo cáo 54 trang bị xử lý hai lượt.
    """
    pages = load_pages(file_path)
    total = len(pages)
    results = []

    for i, page_img in enumerate(pages, start=1):
        regions = get_table_regions(page_img)

        if not regions:
            print(f"--- Page {i}/{total}: không có bảng, dùng nguyên trang ---")
            results.append({"page": i, "regions": [page_img]})
            continue

        results.append({"page": i, "regions": regions})
        print(f"--- Page {i}/{total}: tìm thấy {len(regions)} bảng ---")

    return results


def ocr_image(image: Image.Image) -> str:
    image_array = np.array(image)
    results = get_reader().readtext(image_array, detail=0)
    return "\n".join(results)


def ocr_regions(pages: list[dict]) -> list[dict]:
    """
    OCR các vùng bảng đã cắt sẵn bởi load_table_regions().
    Format: [{"page": 1, "text": "..."}, ...]
    """
    results = []

    for page in pages:
        text = "\n".join(ocr_image(region) for region in page["regions"])
        results.append({"page": page["page"], "text": text})
        print(f"--- OCR page {page['page']}: {len(text)} characters ---")

    return results


def ocr_document(file_path: str) -> list[dict]:
    """
    Run layout detection + OCR on the whole document, return results per page.
    Format: [{"page": 1, "text": "..."}, ...]
    """
    return ocr_regions(load_table_regions(file_path))


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
