"""
Test nhận diện chuẩn mẫu biểu và tính đầy đủ của hai bảng mã số dòng.

Chạy được mà không cần mạng hay model: mọi thứ ở đây là so khớp chuỗi và
tra bảng.

Điều đáng test nhất không phải "nhận đúng khi rõ ràng", mà là hai chỗ thất
bại im lặng: (1) khi không đủ dấu hiệu thì hàm có chịu trả None thay vì
đoán bừa không, và (2) marker của chuẩn này có vô tình khớp mẫu biểu của
chuẩn kia không. Cả hai đều không làm gì nổ — chúng chỉ khiến pipeline dùng
sai bảng mã rồi trả về sai dòng.
"""

import re

import pytest

from fields_config import (
    FIELD_LINE_CODES,
    FIELD_MAP,
    Standard,
    detect_standard,
    form_markers_for,
    line_codes_for,
)


def test_bao_cao_tinh_hinh_tai_chinh_la_tt99():
    chuan, do_tin_cay = detect_standard("BÁO CÁO TÌNH HÌNH TÀI CHÍNH")

    assert chuan is Standard.TT99
    assert do_tin_cay > 0


def test_bang_can_doi_ke_toan_la_tt200():
    chuan, do_tin_cay = detect_standard("BẢNG CÂN ĐỐI KẾ TOÁN")

    assert chuan is Standard.TT200
    assert do_tin_cay > 0


def test_so_hieu_thong_tu_cung_la_dau_hieu():
    """Số hiệu thông tư chắc chắn hơn tên báo cáo, nhưng chỉ có ở trang đầu."""
    assert detect_standard("Ban hành theo Thông tư số 99/2025/TT-BTC")[0] is Standard.TT99
    assert detect_standard("Ban hành theo Thông tư số 200/2014/TT-BTC")[0] is Standard.TT200


def test_khong_co_dau_hieu_thi_tra_none():
    """
    Không đoán bừa. Nhận diện sai chuẩn là một chế độ lỗi riêng cần đo
    được, nên phải trả None để nơi gọi ghi lại, chứ không được lặng lẽ
    chọn mặc định.
    """
    assert detect_standard("Thuyết minh báo cáo tài chính") == (None, 0.0)


def test_trang_nhac_ca_hai_chuan_thi_khong_ket_luan(capsys):
    """
    Trang mục lục nhắc tên cả hai loại báo cáo là ca có thật. Hoà thì trả
    None và kêu ra log — chọn đại một bên ở đây là cách chắc chắn nhất để
    dùng nhầm bảng mã.
    """
    text = "Mục lục: Bảng cân đối kế toán ... Báo cáo tình hình tài chính"
    chuan, do_tin_cay = detect_standard(text)

    assert chuan is None
    assert do_tin_cay < 0.5
    assert "STANDARD" in capsys.readouterr().out


def test_dan_dau_nhung_van_co_dau_hieu_chuan_kia_thi_tin_cay_bi_ha():
    """
    Hai dấu hiệu TT99 và một dấu hiệu TT200 thì vẫn kết luận TT99, nhưng
    độ tin cậy phải thấp hơn hẳn ca sạch — trang này có tranh chấp.
    """
    text = "Thông tư 99/2025 — Báo cáo tình hình tài chính (trước đây: Bảng cân đối kế toán)"
    chuan, do_tin_cay = detect_standard(text)

    sach = detect_standard("Báo cáo tình hình tài chính")[1]

    assert chuan is Standard.TT99
    assert do_tin_cay < sach


def test_ocr_lam_hong_dau_van_nhan_dien_duoc():
    """
    OCR làm hỏng dấu tiếng Việt một cách có hệ thống, nên nhận diện phải
    bỏ dấu trước khi so. Liệt kê từng biến thể có dấu là cuộc đuổi bắt
    không có hồi kết.
    """
    assert detect_standard("BAO CAO TINH HINH TAI CHINH")[0] is Standard.TT99
    assert detect_standard("Báo cào tình hính tài chinh")[0] is Standard.TT99


@pytest.mark.parametrize("standard", list(Standard))
def test_moi_chuan_co_du_ma_cho_moi_field(standard):
    """
    Thiếu một mã là lỗi im lặng: field vẫn được trích bằng alias nhưng mất
    hẳn đường dự phòng theo mã số — đúng đường mà OCR cần khi nó làm hỏng
    tên chỉ tiêu tiếng Việt.
    """
    codes = line_codes_for(standard)

    thieu = [key for key in FIELD_MAP if key not in codes]

    assert thieu == [], f"{standard} thiếu mã cho: {thieu}"


@pytest.mark.parametrize("standard", list(Standard))
def test_moi_ma_deu_tro_toi_mau_bieu_co_marker(standard):
    """
    Mã số chỉ được dùng khi trang đúng mẫu biểu. Nếu một field trỏ tới mẫu
    không có marker thì extract_field_by_code() lặng lẽ trả None mãi mãi.
    """
    markers = form_markers_for(standard)

    thieu = sorted({form for form, _ in line_codes_for(standard).values() if form not in markers})

    assert thieu == [], f"{standard} có mã trỏ tới mẫu biểu không marker: {thieu}"


def test_hai_chuan_khac_nhau_o_ma_tong_tai_san():
    """
    Chốt lại chỗ lệch đã biết giữa hai chuẩn. Nếu test này đỏ thì hoặc ai
    đó vừa sửa bảng mã, hoặc việc đối chiếu Phụ lục IV cho kết quả khác —
    cả hai trường hợp đều cần người xem lại, không được sửa test cho xanh.
    """
    assert line_codes_for(Standard.TT200)["tong_tai_san"][1] == "270"
    assert line_codes_for(Standard.TT99)["tong_tai_san"][1] == "280"


def test_marker_tt200_khong_khop_mau_bieu_cua_tt99():
    """
    Bẫy tinh vi nhất của việc tách hai chuẩn: chuỗi "B 01" nằm gọn bên
    trong "B 01a", nên marker TT200 sẽ khớp luôn trang TT99 nếu không
    chặn. Hậu quả là bảng mã TT200 được đem dùng trên báo cáo TT99 và mã
    270 tra trên trang mà tổng tài sản mang mã 280 — sai dòng, không lỗi.
    """
    trang_tt99 = "Mẫu số B 01a - DN"

    marker_tt200 = form_markers_for(Standard.TT200)["B01"]
    marker_tt99 = form_markers_for(Standard.TT99)["B01a"]

    assert re.search(marker_tt99, trang_tt99, flags=re.IGNORECASE)
    assert not re.search(marker_tt200, trang_tt99, flags=re.IGNORECASE)


def test_marker_tt99_khong_khop_mau_bieu_cua_tt200():
    """Chiều ngược lại: "B 01a" không nằm trong "B 01" nên phải trượt."""
    trang_tt200 = "Mẫu số B 01 - DN"

    assert re.search(form_markers_for(Standard.TT200)["B01"], trang_tt200, flags=re.IGNORECASE)
    assert not re.search(form_markers_for(Standard.TT99)["B01a"], trang_tt200, flags=re.IGNORECASE)


def test_marker_van_chiu_duoc_bien_the_ocr():
    """
    EasyOCR đọc "Mẫu B 01a" thành "Mâu B Ola" — số 0 thành chữ O, số 1
    thành chữ l thường. Đây là quan sát thật trên báo cáo VNM, không phải
    ca giả định.
    """
    assert re.search(form_markers_for(Standard.TT99)["B01a"], "Mâu B Ola", flags=re.IGNORECASE)


def test_hai_chuan_deu_co_mat_trong_bang_ma():
    """Bảng mã phải phủ mọi chuẩn khai báo trong enum, không thiếu chuẩn nào."""
    assert set(FIELD_LINE_CODES) == set(Standard)
