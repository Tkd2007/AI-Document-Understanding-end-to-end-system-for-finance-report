"""
Pipeline step: FastAPI Gateway

Wraps the VLM extraction pipeline into an HTTP endpoint so real
users (not just terminal commands) can use it.
"""

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from validation import validate_result

from router import route_document

app = FastAPI(title="AI Document Understanding — Financial Reports")

UPLOAD_DIR = Path("data/samples")
ALLOWED_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg"}


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Request thiếu tên file")

    # Chỉ giữ phần tên, bỏ mọi thành phần thư mục. Dùng thẳng
    # file.filename thì client gửi tên "../../../x.pdf" sẽ ghi được file
    # ra ngoài thư mục dự án (path traversal) — tên file là dữ liệu do
    # client kiểm soát, không bao giờ được tin.
    safe_name = Path(file.filename).name
    suffix = Path(safe_name).suffix.lower()

    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng {suffix or '(không có)'} không được hỗ trợ. "
                   f"Chấp nhận: {', '.join(sorted(ALLOWED_SUFFIXES))}",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_DIR / safe_name
    save_path.write_bytes(await file.read())

    # route_document() chạy OCR/YOLO/VLM, mất từ vài chục giây tới vài
    # phút. Gọi thẳng trong endpoint async sẽ chặn event loop và treo mọi
    # request khác, nên đẩy sang threadpool.
    result = await run_in_threadpool(route_document, str(save_path))
    return validate_result(result)