"""
Document Classifier & Router

Routes between OCR Pipeline (cheap, fast) and VLM Pipeline
(expensive, slower but more reliable) based on whether OCR
extraction found all required fields.
"""
import json

from pathlib import Path
from ocr_baseline import load_table_regions, ocr_regions
from extract_baseline import extract_all_fields
from extract_vlm import extract_fields_from_regions


def run_ocr_pipeline(pages: list[dict]) -> dict:
    ocr_results = ocr_regions(pages)
    full_text = "\n".join(page["text"] for page in ocr_results)
    return extract_all_fields(full_text)


def run_vlm_pipeline(pages: list[dict]) -> dict:
    return extract_fields_from_regions(pages)


def route_document(file_path: str) -> dict:
    """
    Chạy nhánh OCR trước, thiếu field nào thì mới chuyển sang nhánh VLM.

    Convert PDF sang ảnh 300 DPI và chạy YOLO là hai việc đắt nhất trong
    pipeline, nên load_table_regions() được gọi đúng MỘT LẦN ở đây rồi
    truyền chung cho cả hai nhánh. Trước đây mỗi nhánh tự gọi lại từ file
    gốc, nên báo cáo 54 trang phải convert và chạy YOLO hai lượt.
    """
    pages = load_table_regions(file_path)

    result = run_ocr_pipeline(pages)

    missing = [key for key, value in result.items() if value is None]
    if missing:
        print(f"--- OCR không tìm được {missing}, chuyển sang nhánh VLM ---")
        result = run_vlm_pipeline(pages)

    save_result(file_path, result)
    return result


def save_result(file_path: str, result: dict) -> Path:
    out_path = Path("data/output")/(Path(file_path).stem + "_routed.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return out_path
