"""
Pipeline step 1: Document -> Raw Text (OCR baseline)

Uses EasyOCR (Vietnamese + English) instead of training DBNet/PARSeq
from scratch. The goal at this stage is NOT the best possible OCR
quality, but a working end-to-end "walking skeleton" to build on.

Usage:
    python src/ocr_baseline.py data/samples/report.pdf
    python src/ocr_baseline.py data/samples/report.png
"""

import os
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from PIL import Image

from layout_detection import get_table_regions
from metrics import timer

load_dotenv()


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
    import module này (để dùng load_pages/iter_table_regions), chạy nhánh
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


def iter_table_regions(file_path: str, metrics=None) -> Iterator[dict]:
    """
    Generator: chạy layout detection cho TỪNG trang, yield từng trang một:
        {"page": 1, "regions": [Image, ...]}

    Mỗi trang trả về các vùng bảng tìm được; nếu không tìm thấy bảng nào
    thì trả về nguyên trang gốc (fail open — để không mất dữ liệu ở trang
    mà YOLO nhận nhầm là plain text).

    Dùng generator thay vì trả về list: YOLO chỉ chạy khi người gọi thực
    sự cần tới trang đó. Nếu tìm đủ field ở trang 10 rồi dừng thì 45 trang
    còn lại không hề bị chạy YOLO — đây là phần tiết kiệm lớn nhất, vì
    YOLO là một trong hai việc đắt nhất pipeline (cùng với convert PDF).
    """
    with timer(metrics, "pdf_convert"):
        pages = load_pages(file_path)

    total = len(pages)

    for i, page_img in enumerate(pages, start=1):
        with timer(metrics, "layout"):
            regions = get_table_regions(page_img)

        if not regions:
            print(f"--- Page {i}/{total}: không có bảng, dùng nguyên trang ---")
            yield {"page": i, "regions": [page_img]}
            continue

        print(f"--- Page {i}/{total}: tìm thấy {len(regions)} bảng ---")
        yield {"page": i, "regions": regions}


def ocr_image(image: Image.Image) -> str:
    image_array = np.array(image)
    results = get_reader().readtext(image_array, detail=0)
    return "\n".join(results)


def ocr_page_regions(page: dict) -> dict:
    """
    OCR các vùng bảng của MỘT trang.
    Nhận {"page": 1, "regions": [...]}, trả {"page": 1, "text": "..."}.

    Tách ra khỏi ocr_regions() để router.py gọi được theo từng trang khi
    duyệt generator, thay vì phải gom hết mọi trang lại rồi mới OCR.
    """
    text = "\n".join(ocr_image(region) for region in page["regions"])
    print(f"--- OCR page {page['page']}: {len(text)} characters ---")
    return {"page": page["page"], "text": text}


def ocr_regions(pages: Iterable[dict]) -> list[dict]:
    """
    OCR nhiều trang đã cắt sẵn bởi iter_table_regions().
    Format: [{"page": 1, "text": "..."}, ...]
    """
    return [ocr_page_regions(page) for page in pages]


def ocr_document(file_path: str) -> list[dict]:
    """
    Run layout detection + OCR on the whole document, return results per page.
    Format: [{"page": 1, "text": "..."}, ...]
    """
    return ocr_regions(iter_table_regions(file_path))


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