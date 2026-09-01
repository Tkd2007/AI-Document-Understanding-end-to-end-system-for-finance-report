"""
Test chuẩn hoá đơn vị tính — mỏ neo tuyệt đối chống sai bậc độ lớn.

Vì sao phần này đáng test kỹ hơn vẻ ngoài của nó: hệ ràng buộc kế toán là
hệ THUẦN NHẤT (Ax = 0), nên nhân mọi giá trị với một hằng số vẫn cho
residual bằng 0. Đọc "triệu đồng" thành "đồng" khiến mọi con số sai gấp một
triệu lần trong khi bảng cân đối vẫn cân hoàn hảo và mọi đẳng thức vẫn khớp
tới từng đồng.

Không có đẳng thức nào bắt được ca đó. Chỉ dòng khai báo đơn vị và biên độ
lớn tuyệt đối bắt được. Nên nếu bộ test này yếu, cả phần đo accuracy trên
nhiều công ty đều đứng trên cát.
"""

import pytest

from fields_config import TOTAL_ASSETS_BOUNDS, QuyUocDau, Standard, parse_unit
from validation import validate_result


@pytest.mark.parametrize(
    "raw, he_so_mong_doi, dang_chuan_mong_doi",
    [
        ("đồng", 1, "đồng"),
        ("nghìn đồng", 1_000, "nghìn đồng"),
        ("triệu đồng", 1_000_000, "triệu đồng"),
        ("tỷ đồng", 1_000_000_000, "tỷ đồng"),
    ],
)
def test_bon_bac_do_lon_co_ban(raw, he_so_mong_doi, dang_chuan_mong_doi):
    assert parse_unit(raw) == (he_so_mong_doi, dang_chuan_mong_doi)


@pytest.mark.parametrize(
    "raw",
    [
        "(Đơn vị tính: Triệu đồng)",
        "Đơn vị tính: triệu đồng",
        "ĐƠN VỊ: TRIỆU ĐỒNG",
        "Don vi tinh: trieu dong",       # OCR nuốt sạch dấu
        "Đơn vị: triệu VNĐ",
    ],
)
def test_chuoi_that_tren_bao_cao_deu_doc_duoc(raw):
    """
    Chuỗi thật rất đa dạng về cách viết, dấu ngoặc, hoa thường, và mức độ
    hỏng dấu do OCR. Liệt kê từng biến thể có dấu là cuộc đuổi bắt không có
    hồi kết, nên parse_unit() bỏ dấu trước khi tra.
    """
    assert parse_unit(raw)[0] == 1_000_000


def test_chi_noi_tien_te_ma_khong_noi_bac_thi_la_dong():
    """VND trần, không kèm bậc độ lớn nào, nghĩa là đơn vị đồng."""
    assert parse_unit("VNĐ") == (1, "đồng")
    assert parse_unit("VND") == (1, "đồng")


@pytest.mark.parametrize("raw", [None, "", "xyz", "Đơn vị tính:", "Tài sản ngắn hạn"])
def test_khong_doc_duoc_thi_tra_none_chu_khong_doan_bua(raw):
    """
    Trả (None, "") chứ tuyệt đối không ngầm coi là "đồng". Mặc định im lặng
    biến một tài liệu CHƯA BIẾT bậc độ lớn thành một tài liệu trông như đã
    biết, và đó đúng là lỗi mà cả mục này sinh ra để chống.

    Ca "Tài sản ngắn hạn" đáng chú ý: bỏ dấu thành "tai san ngan han", có
    chứa "ngan" — từ khoá của bậc nghìn. Nó không lọt được vì parse_unit()
    kiểm dấu hiệu tiền tệ TRƯỚC khi dò bậc độ lớn.
    """
    assert parse_unit(raw) == (None, "")


# Cùng một doanh nghiệp, cùng một bộ số, trình bày ở đơn vị TRIỆU ĐỒNG.
#
# Số tròn có chủ đích: cả ba đẳng thức kế toán phải khớp CHÍNH XÁC sau khi
# quy đổi, nên không dùng được bộ VNM chia cho 1e6 (phép chia làm tròn phá
# vỡ đẳng thức, lệch đúng một đơn vị).
BAO_CAO_TRIEU_DONG = {
    "tai_san_ngan_han": 600_000,
    "hang_ton_kho": 100_000,
    "tai_san_dai_han": 400_000,
    "tong_tai_san": 1_000_000,
    "no_phai_tra": 400_000,
    "von_chu_so_huu": 600_000,
    "doanh_thu_thuan": 500_000,
    "gia_von_hang_ban": 300_000,
    "loi_nhuan_gop": 200_000,
    "loi_nhuan_truoc_thue": 100_000,
    "loi_nhuan_sau_thue": 80_000,
    "don_vi_tinh": "triệu đồng",
}


def test_quy_doi_ra_dong_dung_tung_dong():
    """
    Test then chốt của cả module: sau quy đổi, mọi giá trị phải bằng đúng
    con số VND, không sai một đồng. Đây là điều kiện để accuracy đo trên
    nhiều công ty khác đơn vị có nghĩa gì.
    """
    ket_qua = validate_result(BAO_CAO_TRIEU_DONG, Standard.TT99, QuyUocDau.TRU)

    for key, gia_tri_trieu in BAO_CAO_TRIEU_DONG.items():
        if key == "don_vi_tinh":
            continue
        assert ket_qua["data"][key] == gia_tri_trieu * 1_000_000


def test_bao_cao_ghi_trieu_dong_khong_sinh_warning():
    """Quy đổi đúng thì mọi check phía sau phải sạch."""
    assert validate_result(BAO_CAO_TRIEU_DONG, Standard.TT99, QuyUocDau.TRU)["warnings"] == []


def test_meta_ghi_lai_don_vi_da_doc_duoc():
    """
    Đơn vị phải đi ra ngoài ở tầng meta, không lẫn vào data. Đây là dữ liệu
    về CÁCH ĐỌC cả bảng, và bước đọc lại ở giai đoạn C cần nó.
    """
    meta = validate_result(BAO_CAO_TRIEU_DONG, Standard.TT99, QuyUocDau.TRU)["meta"]

    assert meta["don_vi_tinh_raw"] == "triệu đồng"
    assert meta["don_vi_tinh_chuan"] == "triệu đồng"
    assert meta["don_vi_tinh_he_so"] == 1_000_000


def test_don_vi_tinh_khong_lan_vao_data():
    """
    don_vi_tinh cố ý không nằm trong FIELD_MAP. Nếu nó lọt vào vòng ép kiểu
    số thì chuỗi "triệu đồng" thành None kèm cảnh báo "không đọc được thành
    số" — một cảnh báo hoàn toàn sai về một dữ liệu hoàn toàn đúng.
    """
    ket_qua = validate_result(BAO_CAO_TRIEU_DONG, Standard.TT99, QuyUocDau.TRU)
    assert "don_vi_tinh" not in ket_qua["data"]


def test_doc_nham_trieu_dong_thanh_dong_bi_mo_neo_bat():
    """
    TEST QUAN TRỌNG NHẤT CỦA A4.

    Cùng bộ số ở trên, nhưng dòng đơn vị bị đọc nhầm thành "đồng". Kết quả:
    tổng tài sản thành 1 triệu đồng thay vì 1 nghìn tỷ — sai gấp một triệu
    lần.

    MỌI đẳng thức kế toán vẫn khớp hoàn hảo trong ca này, vì hệ ràng buộc
    thuần nhất nên bất biến với phép nhân vô hướng. Chỉ biên độ lớn tuyệt
    đối bắt được. Test này chứng minh mỏ neo hoạt động ở đúng chỗ đẳng thức
    bất lực.
    """
    doc_nham = dict(BAO_CAO_TRIEU_DONG)
    doc_nham["don_vi_tinh"] = "đồng"

    ket_qua = validate_result(doc_nham, Standard.TT99, QuyUocDau.TRU)
    canh_bao_dang_thuc = [w for w in ket_qua["warnings"] if "phải bằng" in w]
    canh_bao_don_vi = [w for w in ket_qua["warnings"] if "đơn vị tính" in w]

    assert canh_bao_dang_thuc == [], "đẳng thức lẽ ra vẫn khớp hoàn hảo"
    assert canh_bao_don_vi != [], "mỏ neo phải bắt được ca này"


def test_khong_khai_don_vi_thi_canh_bao_va_bo_qua_bien():
    """
    Thiếu khai báo đơn vị phải cảnh báo, nhưng KHÔNG được báo kèm chuyện
    vi phạm biên độ lớn: một biên tuyệt đối áp lên con số chưa biết bậc độ
    lớn thì không phân biệt được "doanh nghiệp nhỏ" với "đọc nhầm đơn vị",
    nên báo ra sẽ là phỏng đoán khoác áo kết luận.
    """
    thieu_don_vi = {k: v for k, v in BAO_CAO_TRIEU_DONG.items() if k != "don_vi_tinh"}

    warnings = validate_result(thieu_don_vi, Standard.TT99, QuyUocDau.TRU)["warnings"]

    assert [w for w in warnings if "Không có khai báo đơn vị tính" in w]
    assert [w for w in warnings if "ngoài biên hợp lý" in w] == []


def test_khong_quy_doi_khi_chua_biet_he_so():
    """Chưa biết hệ số thì giữ nguyên số thô, không nhân bừa với 1."""
    thieu_don_vi = {k: v for k, v in BAO_CAO_TRIEU_DONG.items() if k != "don_vi_tinh"}

    ket_qua = validate_result(thieu_don_vi, Standard.TT99, QuyUocDau.TRU)

    assert ket_qua["data"]["tong_tai_san"] == 1_000_000
    assert ket_qua["meta"]["don_vi_tinh_he_so"] is None


def test_bien_tong_tai_san_phu_duoc_doanh_nghiep_niem_yet_that():
    """
    Chốt rằng biên để đủ rộng. Biên hẹp sẽ báo oan hàng loạt, và một luật
    báo oan thường xuyên thì người dùng sẽ tắt — lúc đó mỏ neo mất tác dụng
    đúng vào khi cần nó nhất.
    """
    can_duoi, can_tren = TOTAL_ASSETS_BOUNDS

    assert can_duoi <= 47_775_826_926_383 <= can_tren   # VNM, cỡ vừa
    assert can_duoi <= 50_000_000_000 <= can_tren       # niêm yết nhỏ, 50 tỷ

    # Nhưng vẫn phải chặn được lệch cả bậc độ lớn ở hai đầu.
    assert 1_000_000 < can_duoi                         # 1 triệu đồng: đọc nhầm đơn vị
    assert 2_000_000_000_000_000 > can_tren             # 2 triệu tỷ: không doanh nghiệp nào


# ---------------------------------------------------------------------------
# ĐƠN VỊ BUỘC THEO BẢNG
#
# Vì sao cả nhóm test này tồn tại, đo được trên `HNG_2025H1_TT200`: trang 1 của
# hồ sơ là công văn giải trình gửi HNX, khai `ĐVT: tỷ đồng`, và pipeline đọc
# `loi_nhuan_sau_thue` ra từ đúng bảng hai dòng ấy. 25 chỉ tiêu còn lại đọc từ
# các bảng BCTC khai `nghìn đồng`. Với một hệ số duy nhất cho cả tài liệu thì
# KHÔNG lựa chọn nào đúng: tỷ đồng làm 24 ô sai gấp 1e6, nghìn đồng làm ô kia
# sai gấp 1e6 theo chiều ngược lại. Lượt chạy 30/08 chọn tỷ đồng và HNG được
# 2/26 — hai ô đúng là hai ô bằng 0, tức hai ô bất biến với phép nhân.
# ---------------------------------------------------------------------------

from extract_vlm import _don_vi_tai_lieu, _he_so_vung  # noqa: E402
from extraction_types import FieldResult  # noqa: E402


def _doc_ra(raw, confidence=1.0):
    """Kết quả bỏ phiếu đơn vị của một vùng, như _bo_phieu() trả về."""
    return FieldResult(value=raw, confidence=confidence)


def test_vung_tu_khai_don_vi_thi_de_don_vi_dang_ke_thua():
    """
    Đây là chỗ đảo ngược hành vi cũ, và là chỗ ca HNG được cứu. Bản trước đối
    xử với đơn vị như một chỉ tiêu bình thường nên vùng ĐẦU TIÊN đọc được sẽ
    chốt cho cả tài liệu; công văn trang 1 vì thế thắng bảng cân đối trang 5.
    """
    assert _he_so_vung(_doc_ra("nghìn đồng"), 1_000_000_000) == (1_000, "doc_duoc")


def test_vung_khong_khai_thi_ke_thua_vung_truoc():
    """Phần lan của cơ chế: trang tiếp nối của một bảng không in lại dòng đơn vị."""
    assert _he_so_vung(_doc_ra(None), 1_000) == (1_000, "ke_thua")


def test_chua_vung_nao_doc_duoc_thi_khong_doan_bua():
    """
    Không có gì để kế thừa thì trả None, KHÔNG lùi về "đồng" — cùng nguyên tắc
    parse_unit() giữ. Một tài liệu chưa biết bậc độ lớn mà bị đối xử như đã
    biết thì mọi con số accuracy đo trên nó đều vô nghĩa.
    """
    assert _he_so_vung(_doc_ra(None), None) == (None, "chua_biet")


def test_chuoi_khong_ra_don_vi_thi_ke_thua_chu_khong_pha_don_vi_dang_co():
    """
    Vùng đọc ra một chuỗi rác vẫn phải kế thừa, không được coi là "đã khai".
    Nếu không thì mỗi bảng có tiêu đề lạ là một lần đơn vị đang đúng bị xoá.
    """
    assert _he_so_vung(_doc_ra("Tài sản ngắn hạn"), 1_000) == (1_000, "ke_thua")


def test_phieu_yeu_khong_duoc_ghi_de_don_vi_dang_ke_thua():
    """
    Buộc đơn vị theo bảng mở ra một chế độ lỗi mới: một đơn vị BỊA trên trang
    tiếp nối làm hỏng mọi chỉ tiêu của bảng đó, và không đẳng thức nào bắt
    được vì hệ ràng buộc thuần nhất. Ngưỡng quá bán là cái chặn nó.
    """
    assert _he_so_vung(_doc_ra("tỷ đồng", confidence=0.2), 1_000) == (1_000, "ke_thua")


def test_don_vi_muc_tai_lieu_lay_theo_da_so_chi_tieu():
    """
    Đúng hình dạng của HNG: một chỉ tiêu đọc từ bảng tỷ đồng, 25 chỉ tiêu đọc
    từ bảng nghìn đồng. Kết luận mức tài liệu phải là nghìn đồng — khớp
    `unit_multiplier` của gold. Lấy vùng đọc được đầu tiên sẽ trả về tỷ đồng,
    và bảng chấm điểm báo sai đơn vị trong khi 25/26 con số đã quy đổi đúng.
    """
    he_so_theo_truong = {"loi_nhuan_sau_thue": 1_000_000_000}
    he_so_theo_truong.update({f"chi_tieu_{i}": 1_000 for i in range(25)})

    raw, he_so = _don_vi_tai_lieu(
        he_so_theo_truong, [(1_000_000_000, "tỷ đồng"), (1_000, "nghìn đồng")]
    )

    assert (raw, he_so) == ("nghìn đồng", 1_000)


def test_hoa_thi_lay_don_vi_doc_duoc_som_nhat_cho_tat_dinh():
    """
    Điều kiện phá hoà không mang ý nghĩa nghiệp vụ, nó chỉ để cùng đầu vào
    cho cùng đầu ra — không có nó thì lượt chạy không tái lập được.
    """
    raw, he_so = _don_vi_tai_lieu(
        {"a": 1_000, "b": 1_000_000},
        [(1_000_000, "triệu đồng"), (1_000, "nghìn đồng")],
    )

    assert (raw, he_so) == ("triệu đồng", 1_000_000)


def test_khong_vung_nao_doc_duoc_thi_don_vi_tai_lieu_la_none():
    assert _don_vi_tai_lieu({}, []) == (None, None)


def test_quy_doi_tung_o_theo_he_so_cua_bang_da_sinh_ra_no():
    """
    TEST TRUNG TÂM CỦA CƠ CHẾ, dựng lại đúng ca HNG ở quy mô nhỏ.

    `loi_nhuan_sau_thue` đọc từ bảng tỷ đồng, mọi ô còn lại từ bảng nghìn
    đồng. Cả hai phải ra đúng con số VND cùng lúc — điều mà không hệ số toàn
    cục nào làm được.
    """
    tron_don_vi = dict(BAO_CAO_TRIEU_DONG)
    tron_don_vi["don_vi_tinh"] = "nghìn đồng"
    tron_don_vi["loi_nhuan_sau_thue"] = 80

    ket_qua = validate_result(
        tron_don_vi, Standard.TT99, QuyUocDau.TRU, {"loi_nhuan_sau_thue": 1_000_000_000}
    )

    assert ket_qua["data"]["loi_nhuan_sau_thue"] == 80_000_000_000
    assert ket_qua["data"]["tong_tai_san"] == 1_000_000_000
    assert ket_qua["meta"]["he_so_don_vi_theo_truong"]["loi_nhuan_sau_thue"] == 1_000_000_000
    assert ket_qua["meta"]["he_so_don_vi_theo_truong"]["tong_tai_san"] == 1_000


def test_o_khong_co_trong_anh_xa_thi_lui_ve_he_so_muc_tai_lieu():
    """
    Ô do nhánh OCR điền không có xuất xứ vùng, nên phải lùi về hệ số mức tài
    liệu chứ không phải bị bỏ quên không quy đổi.
    """
    ket_qua = validate_result(
        BAO_CAO_TRIEU_DONG, Standard.TT99, QuyUocDau.TRU, {"tong_tai_san": 1_000}
    )

    assert ket_qua["data"]["tong_tai_san"] == 1_000_000_000
    assert ket_qua["data"]["hang_ton_kho"] == 100_000 * 1_000_000


def test_mo_neo_bien_do_lon_gac_theo_he_so_cua_chinh_tong_tai_san():
    """
    Mỏ neo phải đọc hệ số ĐÃ DÙNG CHO tong_tai_san, không phải hệ số mức tài
    liệu. Ở đây tài liệu khai triệu đồng nhưng riêng ô tổng tài sản đọc từ
    một bảng khai đồng — con số quy đổi ra 1 triệu đồng, ngoài biên, và mỏ
    neo là thứ duy nhất bắt được vì mọi đẳng thức vẫn khớp.
    """
    ket_qua = validate_result(BAO_CAO_TRIEU_DONG, Standard.TT99, QuyUocDau.TRU, {"tong_tai_san": 1})

    assert [w for w in ket_qua["warnings"] if "ngoài biên hợp lý" in w]
