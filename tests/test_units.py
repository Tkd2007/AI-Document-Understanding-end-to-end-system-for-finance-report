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

from fields_config import TOTAL_ASSETS_BOUNDS, Standard, parse_unit
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
    ket_qua = validate_result(BAO_CAO_TRIEU_DONG, Standard.TT99)

    for key, gia_tri_trieu in BAO_CAO_TRIEU_DONG.items():
        if key == "don_vi_tinh":
            continue
        assert ket_qua["data"][key] == gia_tri_trieu * 1_000_000


def test_bao_cao_ghi_trieu_dong_khong_sinh_warning():
    """Quy đổi đúng thì mọi check phía sau phải sạch."""
    assert validate_result(BAO_CAO_TRIEU_DONG, Standard.TT99)["warnings"] == []


def test_meta_ghi_lai_don_vi_da_doc_duoc():
    """
    Đơn vị phải đi ra ngoài ở tầng meta, không lẫn vào data. Đây là dữ liệu
    về CÁCH ĐỌC cả bảng, và bước đọc lại ở giai đoạn C cần nó.
    """
    meta = validate_result(BAO_CAO_TRIEU_DONG, Standard.TT99)["meta"]

    assert meta["don_vi_tinh_raw"] == "triệu đồng"
    assert meta["don_vi_tinh_chuan"] == "triệu đồng"
    assert meta["don_vi_tinh_he_so"] == 1_000_000


def test_don_vi_tinh_khong_lan_vao_data():
    """
    don_vi_tinh cố ý không nằm trong FIELD_MAP. Nếu nó lọt vào vòng ép kiểu
    số thì chuỗi "triệu đồng" thành None kèm cảnh báo "không đọc được thành
    số" — một cảnh báo hoàn toàn sai về một dữ liệu hoàn toàn đúng.
    """
    assert "don_vi_tinh" not in validate_result(BAO_CAO_TRIEU_DONG, Standard.TT99)["data"]


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

    ket_qua = validate_result(doc_nham, Standard.TT99)
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

    warnings = validate_result(thieu_don_vi, Standard.TT99)["warnings"]

    assert [w for w in warnings if "Không có khai báo đơn vị tính" in w]
    assert [w for w in warnings if "ngoài biên hợp lý" in w] == []


def test_khong_quy_doi_khi_chua_biet_he_so():
    """Chưa biết hệ số thì giữ nguyên số thô, không nhân bừa với 1."""
    thieu_don_vi = {k: v for k, v in BAO_CAO_TRIEU_DONG.items() if k != "don_vi_tinh"}

    ket_qua = validate_result(thieu_don_vi, Standard.TT99)

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
