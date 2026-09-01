"""
Quy ước dấu của B02 — một bit đọc từ tờ giấy, ANNOTATION-GUIDELINE.md mục 3.3.

Thay cho `tests/test_chuan_hoa_dau.py` (xoá 01/09/2026 cùng `chuan_hoa_dau()`).
Bộ test này neo vào ca thật: số của `DGC_2025Q2_TT200` cho dạng tổng, và số
trên trang B02 mà người chủ trì đọc ngày 01/09/2026 cho dạng trừ.
"""

import pytest

from fields_config import (
    QuyUocDau,
    Standard,
    identities_for,
    kiem_dau_ma_11,
    quy_uoc_tu_cong_thuc,
    quy_uoc_tu_ma_11,
    xac_dinh_quy_uoc,
)
from validation import validate_result

# Số thật, dạng TRỪ: mã 51 in độ lớn, mã 52 in trong ngoặc (thu nhập thuế
# hoãn lại). `60 = 50 − 51 − 52` khớp tới từng đồng.
B02_DANG_TRU = {
    "loi_nhuan_truoc_thue": 507_896_277_534,
    "thue_tndn_hien_hanh": 68_069_473_287,
    "thue_tndn_hoan_lai": -28_074_849_836,
    "loi_nhuan_sau_thue": 467_901_654_083,
}

# Số thật của DGC, dạng TỔNG: mã 51 in trong ngoặc nên đọc ra số âm.
B02_DANG_TONG = {
    "loi_nhuan_truoc_thue": 628_869_302_528,
    "thue_tndn_hien_hanh": -23_554_373_035,
    "thue_tndn_hoan_lai": 0,
    "loi_nhuan_sau_thue": 605_314_929_493,
}


def _canh_bao_ma_60(gia_tri: dict, quy_uoc: QuyUocDau) -> list[str]:
    bo_so = {**gia_tri, "don_vi_tinh": "VND"}
    return [
        w
        for w in validate_result(bo_so, Standard.TT200, quy_uoc)["warnings"]
        if "Mã 60" in w
    ]


# --- Đọc quy ước từ công thức in trên biểu mẫu ---------------------------

@pytest.mark.parametrize(
    ("van_ban", "mong_doi"),
    [
        ("LỢI NHUẬN SAU THUẾ TNDN (60 = 50 + 51 + 52)", QuyUocDau.TONG),
        ("Lợi nhuận sau thuế (60 = 50 - 51 - 52)", QuyUocDau.TRU),
        # Nguyên văn TT200 Điều 113 mục 3.18, nhiều báo cáo chép y như vậy.
        ("Mã số 60 = Mã số 50 - (Mã số 51 + Mã số 52)", QuyUocDau.TRU),
        ("Lợi nhuận sau thuế TNDN (60=50-51-52)", QuyUocDau.TRU),
        ("bảng không in công thức nào", None),
    ],
)
def test_doc_quy_uoc_tu_cong_thuc_in_tren_bieu_mau(van_ban, mong_doi):
    assert quy_uoc_tu_cong_thuc(van_ban) is mong_doi


def test_trang_in_ca_hai_cong_thuc_thi_khong_ket_luan():
    """
    Cùng nguyên tắc với `nhan_dien_chuan()` khi hai chuẩn hoà điểm: một trang
    nhắc cả hai dạng là trang không nói được gì, và chọn bừa một bên ở đây sẽ
    lật cả hai đẳng thức B02 của tài liệu.
    """
    assert quy_uoc_tu_cong_thuc("(60 = 50 + 51 + 52) ... (60 = 50 - 51 - 52)") is None


# --- Đọc quy ước từ dấu ngoặc của mã 11 ----------------------------------

def test_ma_11_am_la_dang_tong_duong_la_dang_tru():
    assert quy_uoc_tu_ma_11({"gia_von_hang_ban": -107_515_846_476}) is QuyUocDau.TONG
    assert quy_uoc_tu_ma_11({"gia_von_hang_ban": 107_515_846_476}) is QuyUocDau.TRU


def test_ma_11_bang_khong_hay_vang_mat_thi_khong_suy_duoc():
    """
    Giá vốn bằng 0 hợp lệ ở CẢ HAI quy ước nên không mang một bit thông tin
    nào. Đoán bừa từ nó là đoán từ hư không.
    """
    assert quy_uoc_tu_ma_11({"gia_von_hang_ban": 0}) is None
    assert quy_uoc_tu_ma_11({}) is None


# --- Chốt quy ước từ hai nguồn -------------------------------------------

def test_cong_thuc_duoc_uu_tien_va_nguon_duoc_khai_ra():
    quy_uoc, nguon = xac_dinh_quy_uoc(
        "(60 = 50 + 51 + 52)", {"gia_von_hang_ban": -5}
    )
    assert (quy_uoc, nguon) == (QuyUocDau.TONG, "cong_thuc")


def test_khong_co_cong_thuc_thi_lui_ve_ma_11():
    quy_uoc, nguon = xac_dinh_quy_uoc("", {"gia_von_hang_ban": 5})
    assert (quy_uoc, nguon) == (QuyUocDau.TRU, "ma_11")


def test_hai_nguon_mau_thuan_thi_KHONG_chon_ben_nao():
    """
    Mâu thuẫn nghĩa là một trong hai nguồn đã bị đọc sai mà ta không biết cái
    nào. Chạy đẳng thức theo bên đoán sai sẽ BỊA ra một lỗi lệch đúng gấp đôi
    các dòng khấu trừ — tệ hơn hẳn việc bỏ qua hai đẳng thức ấy.
    """
    quy_uoc, nguon = xac_dinh_quy_uoc("(60 = 50 + 51 + 52)", {"gia_von_hang_ban": 5})
    assert (quy_uoc, nguon) == (QuyUocDau.KHONG_XAC_DINH, "mau_thuan")


def test_khong_nguon_nao_doc_duoc():
    assert xac_dinh_quy_uoc("", {}) == (QuyUocDau.KHONG_XAC_DINH, "khong_doc_duoc")


# --- Bộ đẳng thức đổi theo quy ước ---------------------------------------

def test_cung_bo_so_cho_hai_ket_luan_nguoc_nhau_tuy_quy_uoc():
    """
    Đây là mệnh đề trung tâm của cả thay đổi ngày 01/09/2026.

    Cùng một bộ số phải CÂN dưới quy ước của chính tài liệu nó, và VỠ dưới
    quy ước kia. Trước ngày đó hai dạng bị buộc vào CHUẨN, nên tài liệu TT200
    in dạng trừ luôn bị chấm bằng dạng tổng và sinh dương tính giả.
    """
    assert _canh_bao_ma_60(B02_DANG_TRU, QuyUocDau.TRU) == []
    assert _canh_bao_ma_60(B02_DANG_TRU, QuyUocDau.TONG) != []

    assert _canh_bao_ma_60(B02_DANG_TONG, QuyUocDau.TONG) == []
    assert _canh_bao_ma_60(B02_DANG_TONG, QuyUocDau.TRU) != []


def test_dung_quy_uoc_sai_thi_lech_dung_gap_doi_hai_dong_thue():
    """
    Chữ ký của lỗi này là "lệch đúng gấp đôi", và nó đo được chứ không phải
    lời khuyên: `2×(51+52)` chính là khoảng cách giữa hai vế.
    """
    canh_bao = _canh_bao_ma_60(B02_DANG_TRU, QuyUocDau.TONG)
    gap_doi = 2 * (
        B02_DANG_TRU["thue_tndn_hien_hanh"] + B02_DANG_TRU["thue_tndn_hoan_lai"]
    )
    assert f"{gap_doi:,}" in canh_bao[0]


def test_khong_xac_dinh_bo_dung_hai_dang_thuc_B02():
    """
    Bỏ QUA, không phải đoán. Hai đẳng thức bị bỏ là mã 20 và mã 60; mọi đẳng
    thức khác vẫn chạy vì chúng không phụ thuộc cách in.
    """
    for chuan in Standard:
        du = identities_for(chuan, QuyUocDau.TONG)
        thieu = identities_for(chuan, QuyUocDau.KHONG_XAC_DINH)
        assert len(du) - len(thieu) == 2  # noqa: PLR2004
        assert _canh_bao_ma_60(B02_DANG_TRU, QuyUocDau.KHONG_XAC_DINH) == []


# --- Kiểm dấu mã 11, thay cho luật "giá vốn luôn dương" -------------------

def test_ma_11_sai_dau_so_voi_quy_uoc_thi_bi_canh_bao():
    assert kiem_dau_ma_11({"gia_von_hang_ban": 107_515_846_476}, QuyUocDau.TONG)
    assert kiem_dau_ma_11({"gia_von_hang_ban": -107_515_846_476}, QuyUocDau.TRU)


def test_ma_11_dung_dau_thi_im_lang():
    assert kiem_dau_ma_11({"gia_von_hang_ban": -107_515_846_476}, QuyUocDau.TONG) is None
    assert kiem_dau_ma_11({"gia_von_hang_ban": 107_515_846_476}, QuyUocDau.TRU) is None
    assert kiem_dau_ma_11({"gia_von_hang_ban": 0}, QuyUocDau.TONG) is None
    assert kiem_dau_ma_11({}, QuyUocDau.TRU) is None


def test_khong_ap_luat_dau_cho_ma_51_va_52():
    """
    Hàng rào cho Câu 13 (28/08/2026): thu nhập thuế hoãn lại đi cùng chi phí
    thuế hiện hành là trạng thái kế toán CÓ THẬT, nên cả hai dấu đều hợp lệ ở
    cả hai quy ước. Áp luật dấu cho chúng là đẻ ra lỗi câm mới — gold của HNG,
    MWG và VRE rơi đúng vào đó và cả ba đều cân đẳng thức tới từng đồng.
    """
    for quy_uoc in (QuyUocDau.TONG, QuyUocDau.TRU):
        for dau in (1, -1):
            bo_so = {"thue_tndn_hien_hanh": dau * 150, "thue_tndn_hoan_lai": -dau * 50}
            assert kiem_dau_ma_11(bo_so, quy_uoc) is None


def test_gia_von_am_khong_con_bi_bao_la_bat_thuong():
    """
    Luật `allow_negative` của mã 11 đã mở ra ngày 01/09/2026: tài liệu in mã
    11 trong ngoặc thì giá trị đọc nguyên văn PHẢI âm, và cảnh báo "âm bất
    thường" ở đó là báo oan trên số liệu hoàn toàn đúng.
    """
    da_kiem = validate_result(
        {"gia_von_hang_ban": -107_515_846_476, "don_vi_tinh": "VND"},
        Standard.TT200,
        QuyUocDau.TONG,
    )
    assert not any("âm bất thường" in w for w in da_kiem["warnings"])


def test_gia_tri_chuoi_van_duoc_ep_kieu_truoc_khi_kiem_dau():
    """
    Ca hồi quy giữ lại từ `test_chuan_hoa_dau.py`: VLM đôi khi trả số dưới
    dạng CHUỖI. Phép kiểm dấu chạy trên chuỗi sẽ lặng lẽ không làm gì — hỏng
    đúng kiểu không ai thấy — nên nó phải nằm SAU bước ép kiểu.
    """
    da_kiem = validate_result(
        {"gia_von_hang_ban": "(107.515.846.476)", "don_vi_tinh": "VND"},
        Standard.TT200,
        QuyUocDau.TRU,
    )
    assert da_kiem["data"]["gia_von_hang_ban"] == -107_515_846_476
    assert any("ngược quy ước" in w for w in da_kiem["warnings"])


# --- Tính chất phải giữ: KHÔNG giải đẳng thức ra dấu ----------------------

def test_tang_trich_xuat_KHONG_lat_dau_de_lam_can_dang_thuc():
    """
    Tính chất sống còn của H1, giữ nguyên từ bộ test cũ.

    `chuan_hoa_dau()` từng lật dấu mã 51 theo suy luận. Nay không còn bước lật
    nào: quy ước được ĐỌC từ tài liệu, còn độ lớn sai thì đẳng thức phải VỠ.
    Nếu tầng trích xuất giải đẳng thức ra dấu thì mọi kết quả đều thoả ràng
    buộc, và phép đo H1 — so vi phạm ràng buộc với confidence của model — mất
    sạch tín hiệu vì tín hiệu bị chính bước trích xuất làm phẳng.
    """
    do_lon_sai = {**B02_DANG_TONG, "thue_tndn_hien_hanh": -999_999_999_999}
    da_kiem = validate_result(
        {**do_lon_sai, "don_vi_tinh": "VND"}, Standard.TT200, QuyUocDau.TONG
    )
    # Giá trị đi ra ĐÚNG như đã đọc, không bị sửa cho cân.
    assert da_kiem["data"]["thue_tndn_hien_hanh"] == -999_999_999_999
    assert [w for w in da_kiem["warnings"] if "Mã 60" in w]


def test_meta_luon_khai_quy_uoc_da_dung():
    """
    Trạng thái tường minh: một lượt chạy 7 đẳng thức phải phân biệt được với
    một lượt chạy đủ 9, nếu không thì residual bằng 0 của hai lượt trông giống
    hệt nhau trong khi chúng nói hai chuyện khác hẳn.
    """
    for quy_uoc in QuyUocDau:
        meta = validate_result(
            {"don_vi_tinh": "VND"}, Standard.TT99, quy_uoc
        )["meta"]
        assert meta["quy_uoc_dau"] == quy_uoc.value
