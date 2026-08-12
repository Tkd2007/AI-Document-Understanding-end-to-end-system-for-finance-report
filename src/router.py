"""
Document Classifier & Router

Routes between OCR Pipeline (cheap, fast) and VLM Pipeline
(expensive, slower but more reliable) based on whether OCR
extraction found all required fields.
"""
import json
import sys

from pathlib import Path
from ocr_baseline import iter_table_regions, ocr_page_regions
from extract_baseline import extract_all_fields
from extract_vlm import extract_fields_from_regions
from validation import validate_result, has_required_fields

from fields_config import FIELD_MAP


def route_document(file_path: str) -> dict:
    pages_iter = iter_table_regions(file_path)   # generator
    cached_pages = []                             # để VLM dùng lại, không chạy YOLO lần 2
    result = {key: None for key in FIELD_MAP}

    # VÒNG LẶP OCR theo từng trang
    for page in pages_iter:
        cached_pages.append(page)

        ocr_result = ocr_page_regions(page)              # OCR 1 trang
        page_fields = extract_all_fields(ocr_result["text"])   # regex trên text trang đó

        # merge: chỉ lấp field còn None, không ghi đè field đã có
        for key in result:
            if result[key] is None and page_fields.get(key) is not None:
                result[key] = page_fields[key]

        # dừng sớm nếu đủ field VÀ validate không có warning
        if is_acceptable(result):
            break

    # fallback VLM nếu OCR không cho kết quả đáng tin
    if not is_acceptable(result):
        vlm_result = extract_fields_from_regions(cached_pages)
        # merge: giữ field OCR đã có, chỉ lấp chỗ thiếu
        for key in result:
            if result[key] is None and vlm_result.get(key) is not None:
                result[key] = vlm_result[key]

    save_result(file_path, result)
    return result


def save_result(file_path: str, result: dict) -> Path:
    out_path = Path("data/output")/(Path(file_path).stem + "_routed.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return out_path


def is_acceptable(result: dict) -> bool:
    """
    Kết quả có đáng tin để dừng sớm / khỏi cần fallback VLM không?

    Hai điều kiện, cả hai đều phải đạt:
    1. Đủ các field BẮT BUỘC (theo FIELD_RULES). Field bổ sung thiếu vẫn
       chấp nhận được — danh sách chỉ tiêu càng dài thì càng dễ thiếu một
       chỉ tiêu phụ, và nếu bắt đủ hết mới cho qua thì lần nào cũng phải
       fallback sang VLM.
    2. Validate không sinh warning. Chỉ kiểm tra "có giá trị" là chưa đủ,
       vì regex có thể bắt trúng một con số SAI (không phải None) và
       router sẽ tin dùng luôn mà không bao giờ gọi VLM.
    """
    if not has_required_fields(result):
        return False

    return not validate_result(result)["warnings"]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python router.py <file_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    result = route_document(input_path)

    print(result)