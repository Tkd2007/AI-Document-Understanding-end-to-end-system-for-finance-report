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
    ...