"""
Pipeline step: FastAPI Gateway

Wraps the VLM extraction pipeline into an HTTP endpoint so real
users (not just terminal commands) can use it.
"""

from pathlib import Path

from fastapi import FastAPI, UploadFile, File

from extract_vlm import extract_fields_from_document

app = FastAPI()

UPLOAD_DIR = Path("data/samples")


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    save_path = UPLOAD_DIR / file.filename
    contents = file.file.read()
    with open(save_path, "wb") as f:
        f.write(contents)

    result = extract_fields_from_document(str(save_path))
    return result


def validate_result(result: dict) -> dict:
    warnings = []

    for key, value in result.items():
        if value is not None and value < 0:
            warnings.append(f"{key} có giá trị âm: {value}")

    doanh_thu = result.get("doanh_thu_thuan")
    tong_tai_san = result.get("tong_tai_san")

    if doanh_thu is not None and tong_tai_san is not None and float(doanh_thu) > float(tong_tai_san)*10:
        warnings.append("Doanh thu thuần lớn bất thường so với Tổng tài sản")

    return {"data": result, "warnings": warnings}