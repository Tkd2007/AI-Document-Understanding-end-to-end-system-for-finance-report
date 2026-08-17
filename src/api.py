"""
Pipeline step: FastAPI Gateway

Wraps the VLM extraction pipeline into an HTTP endpoint so real
users (not just terminal commands) can use it.
"""

import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import PlainTextResponse

from extract_vlm import require_config
from metrics import get_totals
from router import route_document
from validation import validate_result

# api.py là entrypoint của service, nên đây ĐÚNG là chỗ để fail fast: thiếu
# key thì container chết ngay lúc khởi động, thay vì lên "healthy" rồi trả
# 500 ở từng request. Các module thư viện thì không kiểm ở mức import —
# xem docstring của require_config().
require_config()

app = FastAPI(title="AI Document Understanding — Financial Reports")

UPLOAD_DIR = Path("data/samples")
ALLOWED_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg"}
PREFIX = "doc_ai_"


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

    # Tên lưu phải DUY NHẤT cho mỗi request, không được dùng lại tên client
    # gửi lên. Hai người cùng upload "report.pdf" thì request đến sau ghi
    # đè file của request đang chạy — và vì load_page() mở lại file cho
    # TỪNG trang, request đầu sẽ đọc tiếp sang nội dung của tài liệu kia
    # rồi trả về số của một báo cáo khác. Hậu tố ngẫu nhiên cũng tách luôn
    # file <stem>_routed.json ở data/output, vốn cũng bị ghi đè y hệt.
    stem = Path(safe_name).stem
    save_path = UPLOAD_DIR / f"{stem}_{uuid.uuid4().hex[:8]}{suffix}"
    save_path.write_bytes(await file.read())

    try:
        # route_document() chạy OCR/YOLO/VLM, mất từ vài chục giây tới vài
        # phút. Gọi thẳng trong endpoint async sẽ chặn event loop và treo mọi
        # request khác, nên đẩy sang threadpool.
        result = await run_in_threadpool(route_document, str(save_path))
    finally:
        # Xoá file tạm kể cả khi pipeline ném lỗi. Không có bước này thì
        # data/samples/ phình vô hạn theo số request — mỗi lượt upload để
        # lại một PDF vài chục MB không ai dọn.
        save_path.unlink(missing_ok=True)

    return validate_result(result)


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    lines = []
    for name, value in get_totals().items():
        metric = PREFIX + name
        lines.append(f"# TYPE {metric} counter")
        lines.append(f"{metric} {value}")
    return "\n".join(lines) + "\n"
