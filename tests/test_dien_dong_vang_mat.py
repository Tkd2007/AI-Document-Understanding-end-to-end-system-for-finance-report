"""
Test bước điền 0 cho dòng vắng mặt, và hệ quả của nó lên bước kiểm đẳng thức.

Đây là phần trả lời câu hỏi treo ở `HANDOFF.md` mục 12. Bước kiểm đẳng thức
bỏ qua CẢ đẳng thức nếu bất kỳ thành phần nào là `None`. Với đẳng thức phân
rã tài sản ngắn hạn — 5 thành phần ở TT200, 6 ở TT99 — chỉ cần một dòng
vắng mặt là đẳng thức đắt nhất mà Mốc 1 mua về im lặng không chạy.

Ranh giới phải giữ bằng mọi giá: chỉ điền 0 khi oracle KHẲNG ĐỊNH dòng vắng
mặt trên biểu mẫu. Điền 0 cho ca "chưa biết" là bịa ra một con số, và sai
lệch sinh ra sẽ bị quy cho nhầm chỉ tiêu ở bước sinh ứng viên sửa lỗi.
"""

import os

os.environ.setdefault("OPENROUTER_API_KEY", "khoa-gia-cho-test")
os.environ.setdefault("OPENROUTER_MODEL", "model-gia-cho-test")

import router  # noqa: E402
from extract_baseline import DauVetDong  # noqa: E402
from fields_config import Standard  # noqa: E402
from validation import validate_result  # noqa: E402

VANG_MAT = DauVetDong(None, "khong_thay_dong")
DOC_HONG = DauVetDong(None, "thay_dong_khong_ra_so")
KHONG_BIET = DauVetDong(None, "khong_thay_mau_bieu")


def test_dong_vang_mat_duoc_dien_0_va_ghi_ro_ly_do():
    gia_tri, trang_thai = router.dien_dong_vang_mat(
        {"tai_san_sinh_hoc_ngan_han": None, "hang_ton_kho": 5},
        {"tai_san_sinh_hoc_ngan_han": VANG_MAT},
    )

    assert gia_tri["tai_san_sinh_hoc_ngan_han"] == 0
    assert trang_thai["tai_san_sinh_hoc_ngan_han"] == "vang_mat"
    assert trang_thai["hang_ton_kho"] == "co_gia_tri"


def test_dong_DOC_HONG_giu_None_chu_khong_bi_dien_0():
    """
    Ranh giới quan trọng nhất của cả phương án.

    Dòng có trên giấy nên giá trị thật gần như chắc chắn khác 0. Gán 0 cho
    nó sẽ làm đẳng thức lệch đúng bằng giá trị bị mất, và bước sinh ứng
    viên sửa lỗi đi tìm cho nhầm chỉ tiêu — cảnh báo đúng hướng nhưng quy
    trách nhiệm sai chỗ.
    """
    gia_tri, trang_thai = router.dien_dong_vang_mat(
        {"phai_thu_ngan_han": None}, {"phai_thu_ngan_han": DOC_HONG}
    )

    assert gia_tri["phai_thu_ngan_han"] is None
    assert trang_thai["phai_thu_ngan_han"] == "khong_doc_duoc"


def test_probe_khong_ket_luan_duoc_thi_KHONG_dien_0():
    """Không kết luận được phải xử như chưa biết, không xử như vắng mặt."""
    gia_tri, trang_thai = router.dien_dong_vang_mat(
        {"phai_thu_ngan_han": None}, {"phai_thu_ngan_han": KHONG_BIET}
    )

    assert gia_tri["phai_thu_ngan_han"] is None
    assert trang_thai["phai_thu_ngan_han"] == "khong_doc_duoc"


def test_khong_co_dau_vet_nao_thi_khong_dien_gi():
    """
    Probe tắt (DISABLE_LINE_PROBE) hoặc chưa chạy -> dấu vết rỗng.

    Mặc định phải là an toàn: mất tính năng chứ không sinh số sai.
    """
    gia_tri, trang_thai = router.dien_dong_vang_mat({"hang_ton_kho": None}, {})

    assert gia_tri["hang_ton_kho"] is None
    assert trang_thai["hang_ton_kho"] == "khong_doc_duoc"


def test_khoa_don_vi_tinh_khong_bi_gan_trang_thai():
    """don_vi_tinh là chuỗi mô tả cách đọc bảng, không phải một chỉ tiêu."""
    _, trang_thai = router.dien_dong_vang_mat({"don_vi_tinh": "đồng"}, {})

    assert "don_vi_tinh" not in trang_thai


# --- Hệ quả thật: đẳng thức phân rã nay CHẠY ĐƯỢC -------------------------

# Bộ số kiểu VNM: doanh nghiệp không có tài sản sinh học nên biểu mẫu bỏ hẳn
# mã 150. Hàng tồn kho bị đọc nhầm sang dòng "Dự phòng giảm giá hàng tồn
# kho" — lỗi có thật đã quan sát được, và là ví dụ mở đầu của proposal.
_TY = 1_000_000_000
BAO_CAO_VNM_SAI_HANG_TON_KHO = {
    "don_vi_tinh": "đồng",
    "tai_san_ngan_han": 5_000 * _TY,
    "tien_va_tuong_duong_tien": 1_000 * _TY,
    "dau_tu_tc_ngan_han": 1_000 * _TY,
    "phai_thu_ngan_han": 1_000 * _TY,
    "hang_ton_kho": 1 * _TY,          # thật là 1.500 tỷ, đọc nhầm còn 1 tỷ
    "tai_san_sinh_hoc_ngan_han": None,  # dòng KHÔNG có trên biểu mẫu
    "tsnh_khac": 500 * _TY,
}


def _co_canh_bao_phan_ra(gia_tri: dict) -> bool:
    warnings = validate_result(gia_tri, Standard.TT99)["warnings"]
    return any("thành phần tài sản ngắn hạn" in w for w in warnings)


def test_truoc_khi_dien_thi_loi_hang_ton_kho_di_qua_im_lang():
    """
    Chốt lại HIỆN TRẠNG CŨ để thấy rõ bước điền mua được cái gì.

    Dòng tài sản sinh học vắng mặt -> None -> cả đẳng thức bị bỏ qua, nên
    lỗi hàng tồn kho 1.499 tỷ không sinh một cảnh báo nào. Đây chính là lý
    do proposal chọn kịch bản D mà vẫn chưa thu được lợi ích của nó.
    """
    assert not _co_canh_bao_phan_ra(BAO_CAO_VNM_SAI_HANG_TON_KHO)


def test_sau_khi_dien_thi_dung_loi_do_bi_bat():
    """
    Cùng bộ số, sau khi oracle khẳng định mã 150 vắng mặt và bước điền gán 0.

    Đây là toàn bộ giá trị của phương án C, gói trong một phép so sánh: một
    lỗi đọc có thật, trên tài liệu mẫu có thật, đi từ IM LẶNG thành BẮT ĐƯỢC.
    """
    da_dien, trang_thai = router.dien_dong_vang_mat(
        BAO_CAO_VNM_SAI_HANG_TON_KHO,
        {"tai_san_sinh_hoc_ngan_han": VANG_MAT},
    )

    assert trang_thai["tai_san_sinh_hoc_ngan_han"] == "vang_mat"
    assert _co_canh_bao_phan_ra(da_dien)


def test_dong_doc_hong_thi_dang_thuc_van_im_lang_va_do_la_dung():
    """
    Chiều ngược lại: khi thật sự CHƯA BIẾT thì im lặng mới là hành vi đúng.

    Báo cáo cảnh báo ở đây sẽ là báo oan — độ lệch bằng đúng giá trị chưa
    đọc được, không nói lên điều gì về việc có lỗi đọc hay không.
    """
    chua_biet = dict(BAO_CAO_VNM_SAI_HANG_TON_KHO)
    da_dien, _ = router.dien_dong_vang_mat(
        chua_biet, {"tai_san_sinh_hoc_ngan_han": DOC_HONG}
    )

    assert da_dien["tai_san_sinh_hoc_ngan_han"] is None
    assert not _co_canh_bao_phan_ra(da_dien)


# --- Đầu-cuối qua route_document ------------------------------------------

# Trang bảng cân đối TT99 kiểu OCR trả về. Có mã 140 (hàng tồn kho) nên
# oracle khẳng định dòng đó TỒN TẠI; không có mã 150 nên oracle khẳng định
# tài sản sinh học VẮNG MẶT.
TRANG_OCR_TT99 = """
BÁO CÁO TÌNH HÌNH TÀI CHÍNH
Mẫu số B 01a - DN
TÀI SẢN NGẮN HẠN                                      100
    5.000.000.000.000
Tiền và các khoản tương đương tiền                     110
    1.000.000.000.000
Đầu tư tài chính ngắn hạn                              120
    1.000.000.000.000
Các khoản phải thu ngắn hạn                            130
    1.000.000.000.000
Hàng tồn kho                                           140
    1.500.000.000.000
Tài sản ngắn hạn khác                                  160
    500.000.000.000
"""


def _lap_pipeline_co_ocr(monkeypatch, gia_tri_vlm: dict, text_ocr: str):
    """route_document() chạy được không cần mạng, model, file hay EasyOCR."""
    from extraction_types import ExtractionResult, FieldResult

    def vlm_gia(pages, *a, **k):
        # PHẢI duyệt hết generator, đúng như nhánh VLM thật: cached_pages
        # được bồi vào trong lúc duyệt, và probe chỉ đọc những trang nằm
        # trong đó. Hàm giả không duyệt thì cached_pages rỗng và probe
        # không có gì để dò — test sẽ đỏ vì lý do chẳng liên quan.
        list(pages)

        return ExtractionResult(
            data={
                khoa: FieldResult.khong_do(v)
                for khoa, v in gia_tri_vlm.items()
                if khoa != "don_vi_tinh"
            },
            meta={"don_vi_tinh": gia_tri_vlm.get("don_vi_tinh")},
        )

    monkeypatch.setattr(router, "require_config", lambda: None)
    monkeypatch.setattr(
        router, "iter_table_regions", lambda *a, **k: iter([{"page": 1, "regions": []}])
    )
    monkeypatch.setattr(
        router, "ocr_page_regions", lambda page: {"page": page["page"], "text": text_ocr}
    )
    monkeypatch.setattr(router, "extract_fields_from_regions", vlm_gia)
    monkeypatch.setattr(router, "merge_into_totals", lambda run: None)
    monkeypatch.setattr(router.RunMetrics, "save", lambda self, *a, **k: None)


def test_route_document_dien_0_cho_dong_vang_mat(monkeypatch):
    """
    Đường đầy đủ: VLM trả null cho mã 150, probe khẳng định dòng đó không có
    trên biểu mẫu, bước điền gán 0, và đẳng thức phân rã chạy được.
    """
    tu_vlm = dict(BAO_CAO_VNM_SAI_HANG_TON_KHO)
    _lap_pipeline_co_ocr(monkeypatch, tu_vlm, TRANG_OCR_TT99)

    ket_qua = router.route_document("bao_cao.pdf", save=False, standard=Standard.TT99)

    assert ket_qua.values()["tai_san_sinh_hoc_ngan_han"] == 0
    assert ket_qua.meta["trang_thai_chi_tieu"]["tai_san_sinh_hoc_ngan_han"] == "vang_mat"
    assert ket_qua.meta["line_probe"] is True
    assert any("thành phần tài sản ngắn hạn" in w for w in ket_qua.warnings), (
        "Đẳng thức phân rã phải chạy được sau khi điền, và phải bắt lỗi hàng tồn kho"
    )


def test_tat_probe_thi_khong_ai_bi_dien_0(monkeypatch):
    """
    Tắt probe là mất tính năng, KHÔNG phải sinh số sai.

    Ghi `line_probe` thành khoá tường minh trong meta: một lượt chạy có
    probe và một lượt không có cho ra dữ liệu khác nhau về chất, nên người
    đọc kết quả phải phân biệt được mà không phải suy đoán.
    """
    _lap_pipeline_co_ocr(monkeypatch, dict(BAO_CAO_VNM_SAI_HANG_TON_KHO), TRANG_OCR_TT99)
    monkeypatch.setattr(router, "DISABLE_LINE_PROBE", True)

    ket_qua = router.route_document("bao_cao.pdf", save=False, standard=Standard.TT99)

    assert ket_qua.values()["tai_san_sinh_hoc_ngan_han"] is None
    assert ket_qua.meta["trang_thai_chi_tieu"]["tai_san_sinh_hoc_ngan_han"] == (
        "khong_doc_duoc"
    )
    assert ket_qua.meta["line_probe"] is False
