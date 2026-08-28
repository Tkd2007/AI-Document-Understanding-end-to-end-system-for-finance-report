"""
Bộ đếm kiên nhẫn của nhánh OCR.

VÌ SAO BỘ ĐẾM NÀY TỒN TẠI, và vì sao nó phải được chốt bằng test. Trước nó,
`run_ocr_first()` chỉ dừng khi `is_acceptable()` đúng — mà điều kiện ấy đòi
regex khớp TÊN chỉ tiêu tiếng Việt có dấu, đúng chỗ EasyOCR đọc hỏng. Đo trên
tập gold 27/08/2026: **0/9 lần dừng sớm**, quét 100% số trang của mọi tài
liệu, OCR chiếm 77% tổng thời gian chạy.

Một vòng lặp không có trần và một vòng lặp dừng đúng lúc cho ra CÙNG kết quả
trích xuất — khác biệt chỉ nằm ở số trang đã đọc. Nên thứ phải chốt là số
trang, không phải giá trị đi ra.

Chạy được không cần EasyOCR và không cần model: hàm OCR bị thay bằng hàm giả
đếm số trang nó được gọi.
"""

import router
from extraction_types import FieldResult


def _trang(so: int) -> dict:
    """Một 'trang' đủ dùng cho vòng lặp — nó chỉ đọc khoá `page`."""
    return {"page": so, "regions": []}


def _lap_ocr_gia(monkeypatch, theo_trang: dict) -> list:
    """
    Thay `_ocr_mot_trang` bằng hàm giả và trả về sổ ghi các trang đã đọc.

    theo_trang: {số trang: {tên chỉ tiêu: giá trị}} — những gì regex "đọc ra"
    ở trang đó. Trang không có trong dict là trang không trích được gì.
    """
    da_doc = []

    def gia(page, bo_nho_text, metrics=None):
        da_doc.append(page["page"])
        return {
            khoa: FieldResult.khong_do(gt)
            for khoa, gt in theo_trang.get(page["page"], {}).items()
        }

    monkeypatch.setattr(router, "_ocr_mot_trang", gia)
    # Cổng hợp lệ luôn trả False: đây đúng là hiện trạng đo được trên tài liệu
    # thật (0/9 lần đạt), và nó cô lập bộ đếm kiên nhẫn khỏi điều kiện dừng kia.
    monkeypatch.setattr(router, "is_acceptable", lambda *a, **k: False)
    return da_doc


def _khung(standard=None):
    return router.khung_rong(standard or router.DEFAULT_STANDARD)


def test_dung_sau_dung_PATIENCE_trang_khong_co_chi_tieu_moi(monkeypatch):
    da_doc = _lap_ocr_gia(monkeypatch, {1: {"tong_tai_san": 100.0}})
    monkeypatch.setattr(router, "PATIENCE_PAGES_OCR", 3)

    _, dung_som = router.run_ocr_first(
        (_trang(i) for i in range(1, 51)),
        [],
        _khung(),
        router.DEFAULT_STANDARD,
        {},
    )

    # Trang 1 có chỉ tiêu mới; trang 2, 3, 4 thì không -> dừng ở trang 4.
    assert da_doc == [1, 2, 3, 4]
    assert dung_som["da_dung_som"] is True
    assert dung_som["ly_do"] == "het_bang_de_doc"
    assert dung_som["trang_cuoi"] == 4


def test_bo_dem_dat_lai_khi_gap_chi_tieu_moi(monkeypatch):
    """
    Đếm trang LIÊN TIẾP, không đếm dồn. Giữa B01 và B02 có thể chen vài trang
    chữ ký hoặc trang YOLO cắt nhầm; đếm dồn thì dừng ngay trước bảng thứ hai.
    """
    da_doc = _lap_ocr_gia(
        monkeypatch,
        {1: {"tong_tai_san": 100.0}, 4: {"doanh_thu_thuan": 200.0}},
    )
    monkeypatch.setattr(router, "PATIENCE_PAGES_OCR", 3)

    _, dung_som = router.run_ocr_first(
        (_trang(i) for i in range(1, 51)), [], _khung(), router.DEFAULT_STANDARD, {}
    )

    # 1 mới, 2-3 không, 4 mới (đặt lại), 5-6-7 không -> dừng ở 7.
    assert da_doc == [1, 2, 3, 4, 5, 6, 7]
    assert dung_som["trang_cuoi"] == 7


def test_khong_gac_sau_has_required_fields(monkeypatch):
    """
    Điều kiện dừng KHÔNG được gác sau `has_required_fields()` như nhánh VLM.

    Ở nhánh VLM cái gác đó hợp lý vì VLM thường lấp đủ field bắt buộc. Ở nhánh
    regex nó gần như không bao giờ đúng — đây là ca không đọc được gì cả — nên
    gác vào là dựng lại đúng vòng lặp không có trần mà bộ đếm sinh ra để cắt.
    """
    da_doc = _lap_ocr_gia(monkeypatch, {})
    monkeypatch.setattr(router, "PATIENCE_PAGES_OCR", 3)

    _, dung_som = router.run_ocr_first(
        (_trang(i) for i in range(1, 63)), [], _khung(), router.DEFAULT_STANDARD, {}
    )

    assert da_doc == [1, 2, 3]
    assert dung_som["ly_do"] == "het_bang_de_doc"


def test_generator_khong_bi_tieu_thu_qua_cho_da_dung(monkeypatch):
    """
    Nhánh VLM đọc tiếp từ đúng chỗ nhánh OCR dừng. Nếu vòng lặp nuốt thêm
    trang khỏi generator sau khi break thì YOLO đã chạy cho những trang đó mà
    không ai dùng, và `cached_pages` khai nhiều hơn số trang thật sự được xử lý.
    """
    _lap_ocr_gia(monkeypatch, {})
    monkeypatch.setattr(router, "PATIENCE_PAGES_OCR", 3)
    cached: list = []
    gen = (_trang(i) for i in range(1, 21))

    router.run_ocr_first(gen, cached, _khung(), router.DEFAULT_STANDARD, {})

    assert [p["page"] for p in cached] == [1, 2, 3]
    assert next(gen)["page"] == 4


def test_het_trang_truoc_khi_het_kien_nhan_thi_noi_ra(monkeypatch):
    """
    Tài liệu ngắn hơn ngưỡng kiên nhẫn: `da_dung_som` phải là False. Một lượt
    dừng vì kiên nhẫn và một lượt quét trọn tài liệu 2 trang cho ra cùng con số
    trang, mà hai chuyện đó khác hẳn nhau khi đối chiếu chi phí.
    """
    _lap_ocr_gia(monkeypatch, {})
    monkeypatch.setattr(router, "PATIENCE_PAGES_OCR", 3)

    _, dung_som = router.run_ocr_first(
        (_trang(i) for i in range(1, 3)), [], _khung(), router.DEFAULT_STANDARD, {}
    )

    assert dung_som["da_dung_som"] is False
    assert dung_som["ly_do"] == "het_trang"
    assert dung_som["trang_cuoi"] == 2


def test_cong_hop_le_van_dung_som_duoc(monkeypatch):
    """Điều kiện dừng cũ không bị bộ đếm mới thay thế — hai cái chạy song song."""
    da_doc = _lap_ocr_gia(monkeypatch, {1: {"tong_tai_san": 100.0}})
    monkeypatch.setattr(router, "is_acceptable", lambda *a, **k: True)
    monkeypatch.setattr(router, "PATIENCE_PAGES_OCR", 3)

    _, dung_som = router.run_ocr_first(
        (_trang(i) for i in range(1, 51)), [], _khung(), router.DEFAULT_STANDARD, {}
    )

    assert da_doc == [1]
    assert dung_som["ly_do"] == "du_va_hop_le"


def test_khong_chay_nhanh_ocr_thi_trang_thai_van_tuong_minh():
    """
    Một lượt không bật nhánh OCR phải phân biệt được với một lượt bật mà quét
    hết tài liệu. Để khoá này vắng mặt ở ca đầu thì người đọc `metrics.jsonl`
    phải suy từ `ocr_first`, và suy thì sai.
    """
    import inspect

    nguon = inspect.getsource(router.route_document)
    assert '"ly_do": "khong_chay"' in nguon


def test_nguong_du_rong_de_vuot_qua_phan_mo_dau_tai_lieu():
    """
    Ngưỡng mặc định phải đủ lớn để vượt phần mở đầu báo cáo.

    Đây KHÔNG phải tham số tinh chỉnh tốc độ mà là điều kiện để nhánh OCR còn
    chạy: bộ đếm không được gác sau `has_required_fields()` nên nó chạy ngay từ
    trang 1, mà trang đầu báo cáo niêm yết là bìa, trang ký, mục lục, phần giới
    thiệu. Ngưỡng nhỏ hơn số trang mở đầu thì vòng lặp dừng TRƯỚC khi tới bảng
    nào, và nhánh OCR thành vô dụng một cách IM LẶNG — không gì nổ, chỉ là regex
    không bao giờ được đưa cho xem một trang có số.

    Trên tập gold, bảng B01 sớm nhất ở trang 4 và muộn nhất ở trang 5.
    """
    assert router.PATIENCE_PAGES_OCR >= 10


def test_khong_dung_truoc_khi_toi_bang_dau_tien(monkeypatch):
    """
    Ca hồi quy cho đúng cái bẫy trên: tám trang mở đầu không trích được gì, bảng
    bắt đầu ở trang 9. Với ngưỡng mặc định, vòng lặp phải đi qua được phần đầu
    và đọc tới bảng.
    """
    da_doc = _lap_ocr_gia(monkeypatch, {9: {"tong_tai_san": 100.0}})

    _, dung_som = router.run_ocr_first(
        (_trang(i) for i in range(1, 63)), [], _khung(), router.DEFAULT_STANDARD, {}
    )

    assert 9 in da_doc, "dừng trước khi tới bảng đầu tiên"
    # Bộ đếm đặt lại ở trang 9, nên dừng ở 9 + PATIENCE.
    assert dung_som["trang_cuoi"] == 9 + router.PATIENCE_PAGES_OCR
