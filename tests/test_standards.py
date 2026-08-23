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
    line_codes_for,
    marker_for_form,
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
    thieu = sorted(
        {form for form, _ in line_codes_for(standard).values() if marker_for_form(form) is None}
    )

    assert thieu == [], f"{standard} có mã trỏ tới mẫu biểu không marker: {thieu}"


def test_hai_chuan_khac_nhau_o_ma_tong_tai_san():
    """
    Chốt lại chỗ lệch đã biết giữa hai chuẩn. Nếu test này đỏ thì hoặc ai
    đó vừa sửa bảng mã, hoặc việc đối chiếu Phụ lục IV cho kết quả khác —
    cả hai trường hợp đều cần người xem lại, không được sửa test cho xanh.
    """
    assert line_codes_for(Standard.TT200)["tong_tai_san"][1] == "270"
    assert line_codes_for(Standard.TT99)["tong_tai_san"][1] == "280"


@pytest.mark.parametrize(
    "ky_hieu",
    ["Mẫu số B 01 - DN", "Mẫu số B01a-DN", "Mẫu số B01b-DN", "Mẫu số B 01a - DN"],
)
def test_marker_b01_khop_moi_bien_the_ky_bao_cao(ky_hieu):
    r"""
    Hậu tố "a"/"b" phân biệt KỲ BÁO CÁO, không phân biệt Thông tư — đã đối
    chiếu Công báo 289+290 của TT200, nguyên văn: "Bảng cân đối kế toán
    giữa niên độ (dạng đầy đủ) — Mẫu số B01a-DN". Cả ba biến thể đều là
    cùng một biểu mẫu và TT200 nói rõ chúng dùng CÙNG bộ mã số.

    Bản trước cài (?!\s*a) để chặn hậu tố "a", tưởng đó là dấu hiệu của
    TT99. Hậu quả là marker trượt mọi báo cáo QUÝ theo TT200 — đúng loại
    tài liệu dự án xử lý, gồm cả báo cáo VNM Q1/2026 dùng làm mẫu — và khi
    trượt thì đường dự phòng theo mã số tắt hẳn mà không cảnh báo.
    """
    assert re.search(marker_for_form("B01"), ky_hieu, flags=re.IGNORECASE)


def test_marker_khong_lan_giua_cac_bieu_mau():
    """
    Việc marker phải làm là phân biệt B01 với B02 với B03 — trong một chuẩn
    ĐÃ BIẾT. Lẫn giữa hai biểu mẫu là nguồn sai âm thầm thật sự, vì "10" là
    Doanh thu thuần ở B02 nhưng là Biến động hàng tồn kho ở B03.
    """
    assert not re.search(marker_for_form("B02"), "Mẫu số B01a-DN", flags=re.IGNORECASE)
    assert not re.search(marker_for_form("B03"), "Mẫu số B01a-DN", flags=re.IGNORECASE)
    assert not re.search(marker_for_form("B01"), "Mẫu số B02a-DN", flags=re.IGNORECASE)


def test_marker_khong_biet_mau_bieu_thi_tra_none():
    """Trả None chứ không ném lỗi: người gọi đã có nhánh xử lý cho ca đó."""
    assert marker_for_form("B09") is None


def test_marker_van_chiu_duoc_bien_the_ocr():
    """
    EasyOCR đọc "Mẫu B 01a" thành "Mâu B Ola" — số 0 thành chữ O, số 1
    thành chữ l thường. Đây là quan sát thật trên báo cáo VNM, không phải
    ca giả định.
    """
    assert re.search(marker_for_form("B01"), "Mâu B Ola", flags=re.IGNORECASE)


def test_hai_chuan_deu_co_mat_trong_bang_ma():
    """Bảng mã phải phủ mọi chuẩn khai báo trong enum, không thiếu chuẩn nào."""
    assert set(FIELD_LINE_CODES) == set(Standard)
