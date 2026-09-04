"""
Xoay lại vùng khi OCR không bóc được ô số nào.

VÌ SAO CHỐT NHỮNG THỨ DƯỚI ĐÂY. Đo ngày 04/09/2026 trên 10 tài liệu đầu của
lượt chấm hai phe: một phần trang kết quả kinh doanh được quét nằm ngang, và
trên chúng EasyOCR bóc được 0 ô số. Không ô số thì không neo được chỉ tiêu vào
toạ độ nào, tập ứng viên rỗng, và tầng sửa lỗi bỏ cuộc — đúng ba tài liệu mang
lỗi câm của lượt chấm. Xoay 270° kéo cả ba lên 51–86 ô số.

Ba chốt mà test này canh, cả ba đều là chỗ đã suýt làm sai:

  * tiêu chí phải là SỐ Ô SỐ chứ không phải số ký tự;
  * 270° phải được thử TRƯỚC 90°;
  * ảnh xoay phải thay luôn `region.image`, không chỉ dùng riêng cho OCR,
    vì nhánh VLM đọc chính thuộc tính ấy.
"""

import pytest

import ocr_baseline
from layout_detection import TableRegion


class AnhGia:
    """Ảnh giả chỉ nhớ nó đã bị xoay bao nhiêu độ."""

    def __init__(self, goc: int = 0):
        self.goc = goc

    def rotate(self, goc: int, expand: bool = False):
        return AnhGia(goc)


def _vung() -> TableRegion:
    return TableRegion(image=AnhGia(), bbox=(0, 0, 100, 100), confidence=1.0)


def _o_so(n: int) -> list:
    """`n` ô khớp MAU_O_GIA_TRI."""
    return [(f"{i + 1}.234.567", (0, 0, 10, 10)) for i in range(n)]


def _o_chu(n: int) -> list:
    """`n` ô chữ — nhiều ký tự nhưng không ô nào là giá trị."""
    return [("Doanh thu bán hàng và cung cấp dịch vụ", (0, 0, 10, 10))] * n


def _gia_lap(monkeypatch, theo_goc: dict):
    """Cho `ocr_image_chi_tiet` trả kết quả khác nhau theo góc đã xoay."""
    da_goi = []

    def gia(anh):
        da_goi.append(anh.goc)
        return theo_goc.get(anh.goc, [])

    monkeypatch.setattr(ocr_baseline, "ocr_image_chi_tiet", gia)
    return da_goi


def test_doc_duoc_ngay_thi_KHONG_xoay(monkeypatch):
    """Vùng đọc tốt mà vẫn bị xoay là làm hỏng một vùng đang chạy được."""
    da_goi = _gia_lap(monkeypatch, {0: _o_so(50)})
    vung = _vung()
    anh_cu = vung.image

    kq = ocr_baseline._ocr_mot_vung(vung, 0, 7)

    assert len(kq["o_so"]) == 50
    assert kq["goc_xoay"] == 0
    assert vung.image is anh_cu
    assert da_goi == [0], "đọc được rồi thì không được gọi OCR thêm lần nào"


def test_khong_o_so_thi_xoay_270_va_THAY_LUON_anh_cua_vung(monkeypatch):
    """
    Thay `region.image` chứ không dùng ảnh xoay cho riêng OCR.

    Nhánh VLM đọc chính thuộc tính ấy. Sáu trong mười một lỗi câm của lượt
    chấm là mất dấu âm trên đúng các trang nằm ngang này, nên để VLM tiếp tục
    nhận ảnh xoay là bỏ mất nửa lợi ích của cả phép sửa.
    """
    _gia_lap(monkeypatch, {0: [], 270: _o_so(55)})
    vung = _vung()

    kq = ocr_baseline._ocr_mot_vung(vung, 0, 7)

    assert len(kq["o_so"]) == 55
    assert kq["goc_xoay"] == 270
    assert vung.goc_xoay == 270
    assert vung.image.goc == 270


def test_thu_270_TRUOC_90(monkeypatch):
    """
    Cả ba trang cứu được ngày 04/09/2026 đều cứu ở 270°. Thử 90° trước thì
    những ca chỉ 270° mới đúng vẫn cứu được, nhưng ca nào cả hai góc cùng cho
    ô số sẽ chốt nhầm hướng — và một trang xoay ngược 180° vẫn ra ô số, chỉ là
    ô của dòng khác.
    """
    da_goi = _gia_lap(monkeypatch, {0: [], 270: _o_so(55), 90: _o_so(80)})
    vung = _vung()

    kq = ocr_baseline._ocr_mot_vung(vung, 0, 7)

    assert kq["goc_xoay"] == 270
    assert da_goi == [0, 270], "chốt được ở 270° rồi thì không thử 90° nữa"


def test_tieu_chi_la_O_SO_chu_khong_phai_ky_tu(monkeypatch):
    """
    Chỗ trực giác sai, đã đo trên `DGC_2025Q2` trang 7: góc 90° cho 1808 ký
    tự và góc 270° cho 1821 ký tự — chênh 13 — nhưng 0 ô số so với 55. Chữ
    xoay sai chiều vẫn ra hộp text dài tương đương, chỉ có điều không chuỗi
    nào parse thành số.
    """
    _gia_lap(monkeypatch, {0: [], 270: _o_chu(200), 90: _o_so(40)})
    vung = _vung()

    kq = ocr_baseline._ocr_mot_vung(vung, 0, 7)

    # 270° cho RẤT nhiều ký tự nhưng không ô giá trị nào, nên phải bỏ nó.
    assert kq["goc_xoay"] == 90
    assert len(kq["o_so"]) == 40


def test_khong_goc_nao_cuu_duoc_thi_tra_ve_nhu_cu(monkeypatch):
    """
    Ca `DPM_2022Q3`: trang khổ ngang thật, không góc nào bóc được ô số. Vùng
    phải trở về nguyên trạng chứ không giữ lại một ảnh đã xoay vô ích — nhánh
    VLM sau đó sẽ đọc đúng cái ảnh ấy.
    """
    da_goi = _gia_lap(monkeypatch, {0: _o_chu(3)})
    vung = _vung()
    anh_cu = vung.image

    kq = ocr_baseline._ocr_mot_vung(vung, 0, 6)

    assert kq["o_so"] == []
    assert kq["goc_xoay"] == 0
    assert vung.image is anh_cu
    assert da_goi == [0, 270, 90], "phải thử đủ cả hai góc rồi mới chịu thua"


def test_goc_xoay_luon_co_mat_trong_ket_qua(monkeypatch):
    """
    Quy ước trạng thái tường minh của dự án: không để người đọc bảng điểm suy
    ra "vùng này không cần xoay" từ sự vắng mặt của khoá.
    """
    _gia_lap(monkeypatch, {0: _o_so(10)})

    kq = ocr_baseline._ocr_mot_vung(_vung(), 2, 9)

    assert "goc_xoay" in kq
    assert kq["region_index"] == 2


def test_truong_goc_xoay_mac_dinh_bang_0():
    assert TableRegion(image=AnhGia(), bbox=(0, 0, 1, 1), confidence=0.5).goc_xoay == 0


@pytest.mark.parametrize("goc", ocr_baseline.GOC_THU_LAI)
def test_khong_thu_180(goc):
    """
    180° chưa từng giúp: ở cả bốn trang đo được, nó cho số ký tự xấp xỉ 0° và
    vẫn 0 ô số. Thêm nó vào chỉ tốn một lượt OCR cho mỗi vùng hỏng.
    """
    assert goc != 180
    assert ocr_baseline.GOC_THU_LAI == (270, 90)
