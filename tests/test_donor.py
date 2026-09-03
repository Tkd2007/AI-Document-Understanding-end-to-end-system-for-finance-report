"""
Bảng donor cho baseline 9 — đối chứng quyết định của H3.

THỨ PHẢI CHỐT KHÔNG PHẢI "DONOR CÓ GIÁ TRỊ", MÀ LÀ "DONOR KHÔNG PHẢI ĐÁP ÁN".
Tầng XBRL đã hỏng đúng chỗ này hai lần, và cả hai lần đều làm lợi cho baseline
9: bản 1 gộp cả hồ sơ đang xét nên 32% chỉ tiêu có donor trùng khít giá trị
thật, bản 2 loại hồ sơ nhưng vẫn lấy từ kỳ liền kề của chính công ty ấy. Một
baseline được đưa sẵn đáp án làm cả thí nghiệm H3 mất giá trị, nên phần lớn
test dưới đây là test chống rò.
"""

import pytest

from eval.donor import KHOA_QUY_MO, bang_donor, do_ro_ri, ma_cong_ty


def _tl(doc_id: str, **gt) -> dict:
    return {"doc_id": doc_id, "values": gt}


# Ba công ty, trong đó HPG có HAI kỳ — đúng hình dạng của tập gold thật.
TAP = [
    _tl("HPG_2022Q2_TT200", tong_tai_san=200, hang_ton_kho=100, no_phai_tra=80),
    _tl("HPG_2026Q2_TT99", tong_tai_san=220, hang_ton_kho=110, no_phai_tra=88),
    _tl("VNM_2023Q2_TT200", tong_tai_san=50, hang_ton_kho=10, no_phai_tra=20),
    _tl("SAB_2020Q2_TT200", tong_tai_san=100, hang_ton_kho=30, no_phai_tra=40),
]


def test_loai_ca_CONG_TY_chu_khong_chi_loai_tai_lieu():
    """
    Bài học đắt nhất của tầng XBRL, chốt lại ở đây.

    `HPG_2022Q2` không được mượn của `HPG_2026Q2`. Tổng tài sản một doanh
    nghiệp lệch vài phần trăm giữa hai kỳ, nên donor cùng công ty là donor gần
    đáp án hơn thực tế rất nhiều — và baseline 9 khi ấy thắng vì được mách,
    không phải vì phương pháp của nó tốt.
    """
    d = bang_donor(TAP, "HPG_2022Q2_TT200", "tho")

    # Trung vị của VNM(10) và SAB(30) là 20. Nếu lọt kỳ kia của HPG (110) thì
    # trung vị nhảy lên 30 — con số này bắt được đúng chỗ rò ấy.
    assert d["hang_ton_kho"] == 20


def test_khong_tai_lieu_nao_muon_cua_chinh_no():
    d = bang_donor(TAP, "VNM_2023Q2_TT200", "tho")
    # Trung vị của HPG(100), HPG(110), SAB(30) là 100, không phải 10 của VNM.
    assert d["hang_ton_kho"] == 100


def test_ty_trong_KHONG_trao_dap_an_o_chi_tieu_lam_mau_so():
    """
    Chỗ rò mà `do_ro_ri()` bắt được ngay lần chạy đầu, 04/09/2026.

    Tỷ trọng của `tong_tai_san` với chính nó luôn bằng 1 ở mọi tài liệu, nên
    trung vị bằng 1, nhân lại quy mô ra ĐÚNG giá trị thật — tức trao thẳng đáp
    án cho baseline 9 ở đúng chỉ tiêu quan trọng nhất. Nó phải lùi về trung vị
    thô cho riêng chỉ tiêu ấy.
    """
    d = bang_donor(TAP, "VNM_2023Q2_TT200", "ty_trong")
    that = 50

    assert d[KHOA_QUY_MO] != that
    # Trung vị thô của HPG(200), HPG(220), SAB(100) là 200.
    assert d[KHOA_QUY_MO] == 200


def test_ty_trong_dung_bac_do_lon():
    """
    Lý do biến thể này tồn tại: donor thô lệch hàng chục lần thì đối thủ là
    bù nhìn, và thắng bù nhìn thì kết luận cũng chẳng đáng tin.
    """
    d = bang_donor(TAP, "VNM_2023Q2_TT200", "ty_trong")
    tho = bang_donor(TAP, "VNM_2023Q2_TT200", "tho")

    # VNM nhỏ (tổng tài sản 50); tỷ trọng tồn kho của công ty khác quanh 0,5
    # nên donor theo tỷ trọng phải quanh 25, còn donor thô là 100.
    assert d["hang_ton_kho"] == pytest.approx(25.0)
    assert tho["hang_ton_kho"] == 100


def test_bien_the_la_thi_no_ngay():
    """Gõ nhầm tên biến thể mà lặng lẽ lùi về mặc định là đổi cả đối chứng."""
    with pytest.raises(ValueError, match="donor"):
        bang_donor(TAP, "VNM_2023Q2_TT200", "trung_binh")


def test_do_ro_ri_bat_duoc_donor_la_dap_an():
    """
    Phép kiểm chống oracle phải thật sự kêu khi donor CHÍNH LÀ đáp án.

    Không có test này thì `do_ro_ri()` có thể trả 0 ở mọi ca và không ai biết
    nó hỏng — mà nó là thứ duy nhất canh chừng chỗ tầng XBRL đã ngã hai lần.
    """
    doi = [_tl(f"C{i}_2020Q1_TT200", hang_ton_kho=100) for i in range(4)]
    r = do_ro_ri(doi, "tho")

    assert r["so_o"] == 4
    assert r["ty_le_lech_duoi_1_phan_tram"] == 1.0


def test_ma_cong_ty_tach_dung():
    assert ma_cong_ty("HPG_2022Q2_TT200") == "HPG"
    assert ma_cong_ty("S12_2016Q1_TT200") == "S12"
