"""
Document Classifier & Router

Routes between OCR Pipeline (cheap, fast) and VLM Pipeline
(expensive, slower but more reliable) based on whether OCR
extraction found all required fields.
"""
import json

from pathlib import Path
from ocr_baseline import ocr_document
from extract_baseline import extract_all_fields
from extract_vlm import extract_fields_from_document


def run_ocr_pipeline(file_path: str) -> dict:
    pages = ocr_document(file_path)
    full_text = "\n".join(page["text"] for page in pages)
    return extract_all_fields(full_text)


def run_vlm_pipeline(file_path: str) -> dict:
    return extract_fields_from_document(file_path)
    


def route_document(file_path: str) -> dict:
    # Gọi run_ocr_pipeline() trước — rẻ, nhanh, thử trước
    result = run_ocr_pipeline(file_path)

    # Kiểm tra kết quả OCR có đủ tất cả field chưa
    if all(value is not None for value in result.values()):

        # Nếu đủ rồi → return kết quả OCR luôn, không cần gọi VLM (tiết kiệm chi phí)
        return result

    # Nếu thiếu → gọi run_vlm_pipeline(), return kết quả đó thay thế
    result = run_vlm_pipeline(file_path)
    return result


def save_result(file_path: str, result: dict) -> Path:
    ...


def route_document(file_path: str) -> dict:
    ocr_result = run_ocr_pipeline(file_path)

    if all(value is not None for value in ocr_result.values()):
        result = ocr_result
    else:
        result = run_vlm_pipeline(file_path)

    save_result(file_path, result)
    return result