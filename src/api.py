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

# api.py là entrypoint của service, nên đây ĐÚNG là chỗ để fail fast: thiếu
# key thì container chết ngay lúc khởi động, thay vì lên "healthy" rồi trả
# 500 ở từng request. Các module thư viện thì không kiểm ở mức import —
# xem docstring của require_config().
require_config()

app = FastAPI(title="AI Document Understanding — Financial Reports")

UPLOAD_DIR = Path("data/samples")
ALLOWED_SUFFIXES = {".pdf", ".png", ".jpg", ".jpeg"}
PREFIX = "doc_ai_"

# Trần kích thước một file upload. Hằng số này KHÔNG nằm ở fields_config.py
# dù quy ước chung của repo là gom hằng số về đó: fields_config giữ hằng số
# MIỀN (tên chỉ tiêu, mã số dòng, biên giá trị hợp lệ), còn đây là giới hạn
# của tầng vận chuyển HTTP, không có ý nghĩa gì với phần nghiên cứu.
#
# 50 MB chọn theo tài liệu thật: báo cáo VNM Q1/2026 là bản scan 55 trang
# nặng khoảng 9 MB, nên trần này còn dư chỗ cho báo cáo hợp nhất dày hơn
# nhiều mà vẫn chặn được thứ rõ ràng không phải BCTC.
MAX_UPLOAD_BYTES = 50 * 1024 * 1024

# Đọc theo khối thay vì đọc một phát cả file. Con số không quan trọng lắm,
# chỉ cần đủ lớn để không gọi read() hàng chục nghìn lần.
CHUNK_BYTES = 1024 * 1024


async def luu_upload_co_tran(file: UploadFile, dest: Path, max_bytes: int) -> int:
    """
    Ghi nội dung upload ra `dest`, huỷ giữa chừng nếu vượt `max_bytes`.

    Trả về số byte đã ghi. Ném HTTPException 413 khi vượt trần, và xoá
    luôn phần đã ghi dở — để lại nửa file trong data/samples/ thì lần chạy
    sau sẽ gặp một PDF cụt và báo lỗi parse ở tận trong pdf2image, cách xa
    nguyên nhân thật.

    Vì sao phải đọc theo khối chứ không kiểm `file.size` rồi `read()`:
    bản cũ gọi `await file.read()` nạp TRỌN file vào RAM rồi mới ghi, nên
    một upload 4 GB là 4 GB thường trú trong tiến trình. Container có giới
    hạn bộ nhớ sẽ bị OOM-kill — cả service chết, không riêng request đó.

    Giới hạn cần nói thẳng: hàm này chạy SAU khi Starlette đã nhận xong
    toàn bộ body và đệm nó vào SpooledTemporaryFile, nên nó không hề ngăn
    được việc truyền dữ liệu lên. Nó chỉ chặn phần ta tự làm mình chết —
    nạp hết vào RAM và ghi hết ra đĩa. Chặn ngay ở lúc truyền là việc của
    reverse proxy (`client_max_body_size` của nginx), tầng mà repo này
    chưa có.
    """
    da_ghi = 0

    try:
        with open(dest, "wb") as f:
            while chunk := await file.read(CHUNK_BYTES):
                da_ghi += len(chunk)

                if da_ghi > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File vượt quá giới hạn "
                               f"{max_bytes // (1024 * 1024)} MB",
                    )

                f.write(chunk)
    except BaseException:
        # BaseException chứ không phải Exception: xoá file dở phải xảy ra
        # cả khi request bị huỷ (asyncio.CancelledError kế thừa
        # BaseException), vốn đúng là thứ hay xảy ra với upload lớn.
        dest.unlink(missing_ok=True)
        raise

    return da_ghi


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
    await luu_upload_co_tran(file, save_path, MAX_UPLOAD_BYTES)

    try:
        # route_document() chạy OCR/YOLO/VLM, mất từ vài chục giây tới vài
        # phút. Gọi thẳng trong endpoint async sẽ chặn event loop và treo mọi
        # request khác, nên đẩy sang threadpool.
        #
        # save=False: đường API không ghi data/output/<stem>_routed.json.
        # Dữ liệu đã có ở hai chỗ khác — response HTTP ngay bên dưới, và
        # metrics.jsonl (chỗ này còn ghi được cả lượt chạy THẤT BẠI, vì
        # metrics.save() nằm trong finally còn save_result() thì không).
        # File thứ ba chỉ để lại rác: mỗi request một file không ai dọn,
        # tên mang hậu tố ngẫu nhiên của request
        # (report_a3f2b1c9_routed.json) nên upload cùng một báo cáo ba lần
        # ra ba file giống hệt nhau mà không tra cứu theo tên được.
        #
        # Đường CLI vẫn để mặc định save=True, vì ở đó file kia CHÍNH LÀ
        # output của lệnh.
        extraction = await run_in_threadpool(route_document, str(save_path), save=False)
    finally:
        # Xoá file tạm kể cả khi pipeline ném lỗi. Không có bước này thì
        # data/samples/ phình vô hạn theo số request — mỗi lượt upload để
        # lại một PDF vài chục MB không ai dọn.
        save_path.unlink(missing_ok=True)

    # KHÔNG gọi lại validate_result ở đây. route_document() đã chạy nó và
    # trả về cả data đã ép kiểu lẫn warnings, nên gọi lần hai vừa thừa vừa
    # nguy hiểm: nó chạy trên dữ liệu ĐÃ QUY ĐỔI về đồng nhưng lại không
    # còn khoá đơn vị tính, nên sẽ nhân thêm lần nữa hoặc báo thiếu đơn vị
    # một cách vô cớ.
    return {
        "data": extraction.values(),
        "meta": extraction.meta,
        "confidence": extraction.confidences(),
        "warnings": extraction.warnings,
    }


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    lines = []
    for name, value in get_totals().items():
        metric = PREFIX + name
        lines.append(f"# TYPE {metric} counter")
        lines.append(f"{metric} {value}")
    return "\n".join(lines) + "\n"
