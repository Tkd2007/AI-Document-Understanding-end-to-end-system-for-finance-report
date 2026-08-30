"""
Tầng repair trên đường chạy tài liệu Việt Nam.

Ba thứ phải khoá, và cả ba đều là điều kiện để con số của dự án còn nghĩa:

1. **Mặc định TẮT.** Tầng này sửa giá trị cho tới khi residual về 0, tức làm
   phẳng đúng tín hiệu mà H1 đem đi so với confidence. Bật nó mặc định là hỏng
   phép đo theo kiểu không nhìn thấy được từ bảng kết quả.
2. **Không chạy ở chế độ đo**, kể cả khi cờ bật.
3. **Certificate luôn có mặt.** Một con số đã bị sửa mà người đọc kết quả
   không thấy dấu vết thì đúng bằng một con số bịa.
"""

import router
from extraction_types import FieldResult, Provenance
from fields_config import Standard


def _bo_so_can():
    """Bốn dòng của đẳng thức mã 60, đã cân: 750 + 300 + (−50) = 1000."""
    return {
        "loi_nhuan_truoc_thue": 1_000.0,
        "thue_tndn_hien_hanh": 300.0,
        "thue_tndn_hoan_lai": -50.0,
        "loi_nhuan_sau_thue": 750.0,
    }


def _ket_qua(gia_tri: dict) -> dict:
    return {k: FieldResult.khong_do(v) for k, v in gia_tri.items()}


def test_mac_dinh_tat():
    """
    Cờ mặc định phải là TẮT. Đây không phải sở thích cấu hình: bật mặc định
    thì mọi lượt chạy phục vụ đều cho ra đầu ra đã được ràng buộc làm sạch, và
    không còn lượt nào dùng được cho H1.
    """
    assert router.BAT_TANG_REPAIR is False


def test_sua_duoc_loi_dau_va_khai_ra_nguon_dinh_vi():
    gia_tri = {**_bo_so_can(), "thue_tndn_hoan_lai": 50.0}

    sau, cc = router.chay_tang_repair(gia_tri, _ket_qua(gia_tri), Standard.TT200)

    assert cc["verdict"] == "REPAIRED"
    assert cc["nguon_dinh_vi"] == "luat_dau"
    assert sau["thue_tndn_hoan_lai"] == -50.0


def test_certificate_ghi_ca_gia_tri_truoc_va_sau():
    """
    Chỉ ghi tên chỉ tiêu bị đổi thì về sau không dựng lại được đầu ra CHƯA sửa,
    mà đó chính là bộ số H1 cần. Certificate phải đủ để đảo ngược phép sửa.
    """
    gia_tri = {**_bo_so_can(), "thue_tndn_hoan_lai": 50.0}

    _, cc = router.chay_tang_repair(gia_tri, _ket_qua(gia_tri), Standard.TT200)

    doi = cc["da_doi"]["thue_tndn_hoan_lai"]
    assert doi["truoc"] == 50.0
    assert doi["sau"] == -50.0
    assert doi["nguon_ung_vien"] == "sign"


def test_bo_so_da_can_thi_khong_doi_gi():
    gia_tri = _bo_so_can()

    sau, cc = router.chay_tang_repair(gia_tri, _ket_qua(gia_tri), Standard.TT200)

    assert cc["verdict"] == "VERIFIED"
    assert cc["da_doi"] == {}
    assert sau == gia_tri


def test_abstain_thi_KHONG_dong_vao_gia_tri():
    """
    ABSTAIN là câu trả lời đúng, không phải thất bại cần chữa. Sửa một phần
    rồi trả về là tệ hơn cả không sửa: bảng vẫn không cân mà dấu vết đọc gốc
    thì đã mất.
    """
    # Lệch không phải vì dấu: không tổ hợp ứng viên nào đưa residual về 0.
    gia_tri = {**_bo_so_can(), "loi_nhuan_sau_thue": 123.0}

    sau, cc = router.chay_tang_repair(gia_tri, _ket_qua(gia_tri), Standard.TT200)

    assert cc["verdict"] == "ABSTAIN"
    assert sau == gia_tri


def test_certificate_khai_rang_o_lan_can_dang_TAT():
    """
    Không truyền vùng bảng đã OCR thì nguồn ứng viên giá trị nhất tắt. Một lượt
    chạy thiếu nó phải TỰ KHAI là thiếu — không thì kết quả của nó bị đọc như
    kết quả của phiên bản đầy đủ.
    """
    gia_tri = _bo_so_can()

    _, cc = router.chay_tang_repair(gia_tri, _ket_qua(gia_tri), Standard.TT200)

    assert cc["o_lan_can"] is False


def test_co_vung_thi_NEO_khai_theo_tung_chi_tieu():
    """
    `o_lan_can` bật mới là nửa câu chuyện. Nửa còn lại là neo: không neo được
    thì mọi ô trong vùng cùng cost và trần cắt bằng bốc thăm, tức nguồn bật mà
    vô dụng. Hai ca đó phải phân biệt được từ certificate, nên neo khai theo
    TỪNG chỉ tiêu chứ không gộp thành một cờ.
    """
    gia_tri = _bo_so_can()
    o_so = [
        (750, (1200, 900, 1600, 940)),      # đúng giá trị loi_nhuan_sau_thue
        (1_000, (1200, 700, 1600, 740)),
    ]
    vung = {"region_index": 0, "text": "", "o": [], "o_so": o_so}

    result = {
        k: FieldResult(
            value=v,
            confidence=0.0,
            provenance=Provenance(page=5, region_index=0, bbox=(100, 200, 2000, 1800)),
        )
        for k, v in gia_tri.items()
    }

    _, cc = router.chay_tang_repair(gia_tri, result, Standard.TT200, {(5, 0): vung})

    assert cc["o_lan_can"] is True
    assert cc["neo"]["loi_nhuan_sau_thue"] == "khop_gia_tri"
    # Giá trị không có trên giấy và cũng không dò được mã số: khai thẳng là
    # không neo, thay vì lặng lẽ lấy bbox vùng làm tâm như bản trước.
    assert cc["neo"]["thue_tndn_hoan_lai"] == "khong_neo"


def test_chi_tieu_o_VUNG_KHAC_thi_khong_lay_duoc_o_lan_can():
    """Ô của bảng khác không phải lân cận theo bất kỳ nghĩa nào."""
    gia_tri = _bo_so_can()
    result = {
        k: FieldResult(
            value=v,
            confidence=0.0,
            provenance=Provenance(page=5, region_index=1, bbox=(0, 0, 10, 10)),
        )
        for k, v in gia_tri.items()
    }

    _, cc = router.chay_tang_repair(
        gia_tri, result, Standard.TT200, {(5, 0): {"o": [], "o_so": [(750, (0, 0, 1, 1))]}}
    )

    assert set(cc["neo"].values()) == {"khong_co_vung"}


def test_certificate_khai_ca_khi_luat_dau_im_lang():
    gia_tri = {**_bo_so_can(), "loi_nhuan_sau_thue": 123.0}

    _, cc = router.chay_tang_repair(gia_tri, _ket_qua(gia_tri), Standard.TT200)

    assert cc["luat_dau"]["trang_thai"] == "im_lang"


def test_khong_dung_duoc_dang_thuc_nao_thi_noi_ra():
    """
    Không dựng được đẳng thức nào thì tầng này chưa từng chạy phép chẩn đoán.
    Trả `thieu_gia_tri` chứ không trả VERIFIED — VERIFIED nghĩa là "đã kiểm và
    đạt", và ở đây không có gì được kiểm cả.
    """
    _, cc = router.chay_tang_repair(
        {"hang_ton_kho": 1.0}, _ket_qua({"hang_ton_kho": 1.0}), Standard.TT200
    )

    assert cc["verdict"] == "ABSTAIN"
    assert cc["ma_ly_do"] == "thieu_gia_tri"


def test_khong_chay_o_che_do_do_du_co_bat_co(monkeypatch):
    """
    `DISABLE_CONSTRAINT_GATE` bật nghĩa là lượt chạy đang phục vụ phép đo H1.
    Ở đó mọi thứ đọc ràng buộc đều phải im, kể cả khi người dùng lỡ bật cờ
    repair — hai cờ này gặp nhau thì cờ ĐO phải thắng.
    """
    import inspect

    nguon = inspect.getsource(router.route_document)
    assert "BAT_TANG_REPAIR and not DISABLE_CONSTRAINT_GATE" in nguon


def test_chay_sau_validate_result_chu_khong_truoc():
    """
    Thứ tự này là điều kiện để H1 còn đo được: `warnings` phải ghi lại tình
    trạng vi phạm ràng buộc của đầu ra CHƯA sửa. Đảo thứ tự thì cột warnings
    gần như phẳng và phép so với confidence mất nghĩa.
    """
    import inspect

    nguon = inspect.getsource(router.route_document)
    assert nguon.index("da_kiem = validate_result(") < nguon.index("chay_tang_repair(")
