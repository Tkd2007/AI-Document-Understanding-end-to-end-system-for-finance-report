"""
Khởi động công cụ gán nhãn tập gold.

VÌ SAO CÓ FILE NÀY thay vì gọi thẳng uvicorn: lệnh gọi thẳng cần đặt hai
biến môi trường, mà cú pháp đặt biến khác nhau giữa các shell —
`VAR=x lệnh` chạy trên bash nhưng là LỖI CÚ PHÁP trên PowerShell, và
PowerShell là shell chính của máy đang dùng. Người gán nhãn sẽ gõ lệnh này
cả trăm lần trong vài tuần tới; bắt họ nhớ đúng biến thể cho đúng shell là
cách chắc chắn để mất thời gian vào một lỗi không liên quan gì tới nghiên
cứu. Đã xảy ra một lần ngày 25/08/2026.

Chạy, giống hệt nhau ở mọi shell:

    python chay_gan_nhan.py
    python chay_gan_nhan.py --pdf-dir D:\\bctc --port 8200
"""

import argparse
import os
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent


def main() -> int:
    bo_phan_tich = argparse.ArgumentParser(
        description="Máy chủ cục bộ để gán nhãn tập gold ViFinKIE.",
    )
    bo_phan_tich.add_argument(
        "--pdf-dir",
        default="data/samples",
        help="Thư mục chứa PDF cần gán nhãn (mặc định: data/samples)",
    )
    bo_phan_tich.add_argument("--port", type=int, default=8100)
    tham_so = bo_phan_tich.parse_args()

    thu_muc = Path(tham_so.pdf_dir)
    if not thu_muc.is_dir():
        print(f"Không có thư mục {thu_muc}", file=sys.stderr)
        return 1

    so_pdf = len(list(thu_muc.glob("*.pdf")))
    if so_pdf == 0:
        print(f"Thư mục {thu_muc} không có file .pdf nào", file=sys.stderr)
        return 1

    # Đặt biến TRƯỚC khi uvicorn import gan_nhan.app, vì THU_MUC_PDF được đọc
    # ở mức module. Truyền chuỗi "gan_nhan.app:app" chứ không import sẵn đối
    # tượng app chính là để giữ đúng thứ tự đó.
    os.environ["GAN_NHAN_PDF_DIR"] = str(thu_muc)
    sys.path.insert(0, str(GOC / "src"))

    import uvicorn

    print(f"{so_pdf} tài liệu trong {thu_muc}")
    print(f"Mở http://127.0.0.1:{tham_so.port} — Ctrl+C để dừng")
    uvicorn.run("gan_nhan.app:app", host="127.0.0.1", port=tham_so.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
