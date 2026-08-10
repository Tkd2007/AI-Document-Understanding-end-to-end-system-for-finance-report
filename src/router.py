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
    result = run_ocr_pipeline(file_path)

    if not all(value is not None for value in result.values()):
        result = run_vlm_pipeline(file_path)

    save_result(file_path, result)
    return result


def save_result(file_path: str, result: dict) -> Path:
    out_path = Path("data/output")/(Path(file_path).stem + "_routed.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return out_path