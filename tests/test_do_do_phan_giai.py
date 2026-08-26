"""
Test phép đo độ phân giải bản quét.

Con số này là trục phân nhóm Stress thứ ba của tập gold kể từ tu chính
26/08/2026 (`ANNOTATION-GUIDELINE.md` mục 7), nên một phép đo sai ở đây không
làm gì nổ — nó chỉ lặng lẽ xếp nhầm tài liệu vào nhóm và làm hỏng đúng phép
so sánh mà nhóm ấy sinh ra để đo.
"""

import math
from types import SimpleNamespace

from do_do_phan_giai import dpi_hai_chieu


def _anh(rong_px: int, cao_px: int, ma_tran: tuple[float, float, float, float]):
    """
    Giả lập một `PdfImage`: chỉ cần `get_metadata()` và `get_matrix()`.

    Dựng giả thay vì mở PDF thật vì `data/bctc/` KHÔNG vào git — test đọc file
    thật ở đó sẽ xanh trên máy này và đỏ trên mọi máy khác.
    """
    a, b, c, d = ma_tran
    return SimpleNamespace(
        get_metadata=lambda: SimpleNamespace(width=rong_px, height=cao_px),
        get_matrix=lambda: SimpleNamespace(a=a, b=b, c=c, d=d),
    )


def test_trang_khong_xoay_tinh_theo_duong_cheo_ma_tran():
    """Ca thường: ảnh dọc đặt thẳng lên trang A4 dọc, 200 dpi đều hai chiều."""
    ngang, doc = dpi_hai_chieu(_anh(1654, 2340, (595.4, 0.0, 0.0, 842.4)))
    assert math.isclose(ngang, 200.0, abs_tol=0.5)
    assert math.isclose(doc, 200.0, abs_tol=0.5)


def test_trang_dat_xoay_90_do_van_ra_dung_do_phan_giai():
    """
    Hồi quy trên ca `SBT_2025Q2_TT200`, và là lý do hàm này không dùng
    `horizontal_dpi`/`vertical_dpi` của pdfium.

    Ảnh 1052×743 đặt xoay 90° lên trang 595,2×841,9 điểm. Hai trường dpi của
    pdfium chỉ chia cho phần đường chéo của ma trận, mà ma trận xoay có đường
    chéo bằng 0 và giá trị nằm ở b với c — nên chúng chia nhầm cạnh và trả
    127,3 với 63,5, tức báo một bản quét bị kéo dãn gấp đôi theo một chiều.
    Sự thật là 90 dpi đều cả hai chiều, chỉ thấp chứ không méo.

    Nhầm lẫn ấy không vô hại: 127,3 sẽ xếp SBT vào giữa dải thay vì vào đúng
    đầu thấp nhất, và đầu thấp của dải chính là chỗ nhóm Stress cần nhất.
    """
    ngang, doc = dpi_hai_chieu(_anh(1052, 743, (0.0, 841.9, -595.2, 0.0)))
    assert math.isclose(ngang, 90.0, abs_tol=0.5)
    assert math.isclose(doc, 90.0, abs_tol=0.5)


def test_anh_dat_suy_bien_tra_None_chu_khong_tra_khong():
    """
    Cạnh dài 0 điểm thì không chia được. Trả 0 ở đây sẽ lọt vào trung vị dưới
    dạng "bản quét 0 dpi" — tức một tài liệu bình thường tự nhiên thành ca
    tệ nhất của tập, và không dấu hiệu nào cho biết vì sao.
    """
    assert dpi_hai_chieu(_anh(1000, 1000, (0.0, 0.0, 0.0, 842.0))) is None
