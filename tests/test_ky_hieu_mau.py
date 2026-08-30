"""
Lan ký hiệu mẫu biểu — bộ báo cáo hợp nhất hay riêng.

Ký hiệu `B01a-DN/HN` nằm phía trên bảng và không phải bảng nào cũng đọc được:
trang xoay 90 độ thì nó nằm ở cạnh bên, ngoài vùng cắt. Cơ chế ở đây đọc chỗ
nào đọc được rồi lan sang chỗ không đọc được — nhưng CHỈ lan phần hậu tố, và
không được im lặng ở bất kỳ chỗ nào nó không chắc.
"""

from ky_hieu_mau import doc_hau_to, lan_ky_hieu

# ---------------------------------------------------------------------------
# Đọc một ký hiệu
# ---------------------------------------------------------------------------


def test_co_hau_to_HN_la_bo_hop_nhat():
    assert doc_hau_to("Mẫu số B 01a - DN/HN") == "HN"


def test_khong_co_hau_to_la_bo_rieng():
    assert doc_hau_to("Mẫu số B01a-DN") == "DN"


def test_doc_duoc_qua_nhieu_OCR_hong_chu_so():
    """
    EasyOCR đọc "Mẫu B 01a - DN" ra "Mâu B Ola" — số 0 thành chữ O, số 1 thành
    chữ l thường. Cùng chế độ hỏng mà `fields_config.FORM_MARKERS` đã phải chịu.
    """
    assert doc_hau_to("Mâu B Ola - DN/HN") == "HN"
    assert doc_hau_to("MAU SO B 0la- dn|hn") == "HN"


def test_hau_to_doc_duoc_o_MOI_mau_bieu():
    """
    Hậu tố nói bộ báo cáo, không nói bảng nào, nên nó phải đọc được như nhau ở
    B01, B02, B03 — đó chính là lý do lan nó đi được.
    """
    assert doc_hau_to("Mẫu số B 02a - DN/HN") == "HN"
    assert doc_hau_to("B03a-DN") == "DN"


def test_dan_chieu_B01_trong_cau_van_KHONG_phai_ky_hieu_mau():
    """
    Thuyết minh và dẫn chiếu chéo nhắc "B01" suốt mà không kèm gì. Nhận chúng
    là ký hiệu mẫu thì mọi tài liệu đều thành "bộ riêng" — một kết luận bịa ra,
    và tệ hơn là nó được lan đi khắp tài liệu.
    """
    assert doc_hau_to("xem thuyết minh B01 mã số 100") is None


def test_hai_ky_hieu_mau_thuan_trong_CUNG_mot_vung_thi_khong_ket_luan():
    """Đoạn đó không cho một kết luận, và kết luận nửa vời ở đây sẽ bị lan đi."""
    assert doc_hau_to("Mẫu B01a-DN/HN và B01a-DN") is None


# ---------------------------------------------------------------------------
# Lan qua các vùng
# ---------------------------------------------------------------------------


def test_vung_khong_doc_duoc_thua_huong_vung_TRUOC():
    """
    Ca thật: bảng kết quả kinh doanh xoay ngang, ký hiệu nằm ngoài vùng cắt.
    """
    kq = lan_ky_hieu(
        [
            (5, 0, "Mẫu số B 01a - DN/HN"),
            (8, 0, "bảng xoay ngang, không có ký hiệu"),
        ]
    )

    assert kq["loai"] == "hop_nhat"
    assert kq["nguon"] == "doc_duoc"
    assert kq["theo_vung"] == {"5-0": ("hop_nhat", "doc_duoc"), "8-0": ("hop_nhat", "lan")}


def test_KHONG_lan_nguoc_len_vung_truoc_do():
    """
    Phép lan có hướng. Vùng đứng trước vùng đọc được đầu tiên thì vắng mặt khỏi
    `theo_vung` chứ không được gán bừa: lúc duyệt qua nó, chưa có gì để lan.
    """
    kq = lan_ky_hieu([(3, 0, "không có ký hiệu"), (5, 0, "Mẫu số B 01a - DN/HN")])

    assert "3-0" not in kq["theo_vung"]
    assert kq["theo_vung"]["5-0"] == ("hop_nhat", "doc_duoc")


def test_mau_thuan_duoc_GHI_LAI_chu_khong_de_len_ket_luan():
    """
    Vùng sau đọc ra hậu tố khác là tín hiệu: hoặc file đóng gói cả hai bộ, hoặc
    khâu cắt/đọc hỏng. Giữ giá trị cuối cùng là xoá đúng tín hiệu đáng giá nhất
    mà cơ chế này thu được.
    """
    kq = lan_ky_hieu([(5, 0, "B01a-DN/HN"), (9, 0, "B02a-DN")])

    assert kq["loai"] == "hop_nhat"
    assert kq["mau_thuan"] == [
        {"trang": 9, "vung": 0, "da_chot": "hop_nhat", "doc_duoc": "rieng"}
    ]
    # theo_vung mô tả TỜ GIẤY, nên nó ghi thứ đọc được tại chỗ.
    assert kq["theo_vung"]["9-0"] == ("rieng", "doc_duoc")


def test_khong_doc_duoc_o_dau_ca_thi_KHONG_doan():
    """Nguyên tắc detect_standard() đang giữ: không đủ dấu hiệu thì trả None."""
    kq = lan_ky_hieu([(3, 0, "bảng trống"), (4, 0, "cũng không có gì")])

    assert kq["loai"] is None
    assert kq["nguon"] == "khong_doc_duoc"
    assert kq["theo_vung"] == {}


def test_tai_lieu_rong_khong_lam_no():
    assert lan_ky_hieu([])["loai"] is None


def test_nhieu_vung_trong_MOT_trang_lan_theo_dung_thu_tu():
    kq = lan_ky_hieu([(5, 0, "không rõ"), (5, 1, "B01a-DN"), (5, 2, "không rõ")])

    assert kq["theo_vung"] == {"5-1": ("rieng", "doc_duoc"), "5-2": ("rieng", "lan")}
