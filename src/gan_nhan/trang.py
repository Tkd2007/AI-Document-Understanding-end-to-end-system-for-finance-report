"""
Dựng ảnh từng trang PDF cho công cụ gán nhãn xem.

Dùng `pypdfium2` chứ không dùng `pdf2image` dù cả hai đều có trong máy:
`pdf2image` gọi nhị phân Poppler ở ngoài, mà máy đang chạy KHÔNG có
`pdftoppm` (kiểm 25/08/2026 — chỉ có `pdftotext`). Nên `pdf2image` sẽ nổ lúc
chạy chứ không phải lúc cài, tức hỏng vào đúng lúc người gán nhãn đang mở
tài liệu đầu tiên. `pypdfium2` là wheel thuần, không phụ thuộc nhị phân
ngoài.

Ảnh dựng ra được NHỚ trong bộ nhớ tiến trình vì người gán nhãn lật đi lật
lại giữa ba biểu mẫu của cùng một tài liệu hàng chục lần, và dựng lại mỗi
lần ở độ phóng đủ để đọc số thì mỗi lần tốn hàng trăm mili giây.
"""

import io
from functools import lru_cache
from pathlib import Path

import pypdfium2 as pdfium

# Độ phóng mặc định. 2.0 cho ra khoảng 150 dpi trên trang A4, đủ đọc chữ số
# trên bản scan mà chưa làm ảnh nặng tới mức lật trang bị khựng. Người gán
# nhãn phóng to thêm được ở từng trang khi gặp bản scan xấu.
PHONG_MAC_DINH = 2.0

# Trần độ phóng. Chặn để một tham số truyền từ trình duyệt không dựng nổi
# một ảnh vài trăm megabyte và làm chết tiến trình.
PHONG_TOI_DA = 5.0

# Số ảnh giữ lại. Một tài liệu có tới vài chục trang nhưng người chỉ lật
# quanh ba biểu mẫu, nên bộ nhớ đệm nhỏ vẫn trúng gần như mọi lần.
SO_ANH_NHO = 24


def so_trang(duong_dan: str | Path) -> int:
    """Số trang của một PDF."""
    tai_lieu = pdfium.PdfDocument(str(duong_dan))
    try:
        return len(tai_lieu)
    finally:
        tai_lieu.close()


@lru_cache(maxsize=SO_ANH_NHO)
def _dung_anh(duong_dan: str, chi_so: int, phong: float) -> bytes:
    tai_lieu = pdfium.PdfDocument(duong_dan)
    try:
        anh = tai_lieu[chi_so].render(scale=phong).to_pil()
    finally:
        tai_lieu.close()

    dem = io.BytesIO()
    anh.save(dem, format="PNG")
    return dem.getvalue()


def anh_trang(duong_dan: str | Path, chi_so: int, phong: float = PHONG_MAC_DINH) -> bytes:
    """
    Ảnh PNG của một trang, đánh số từ 0.

    Ném IndexError khi vượt số trang thay vì trả trang cuối: người gán nhãn
    gõ nhầm số trang mà nhận được một trang khác trông hợp lệ là cách chắc
    chắn để đọc số của sai biểu mẫu.
    """
    tong = so_trang(duong_dan)
    if not 0 <= chi_so < tong:
        raise IndexError(f"Trang {chi_so} nằm ngoài tài liệu {tong} trang")

    return _dung_anh(str(duong_dan), chi_so, min(float(phong), PHONG_TOI_DA))
