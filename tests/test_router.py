"""
Test cổng quyết định fallback của router.

Chạy được mà không cần API key hay mạng là nhờ `require_config()` được gọi
lúc BẮT ĐẦU một lượt chạy chứ không phải lúc import — xem docstring của nó
trong extract_vlm.py. `is_acceptable()` là logic thuần, nhưng nó quyết định
có gọi VLM hay không, tức là quyết định cả chi phí lẫn độ đúng của kết quả.
"""

import router
from extraction_types import ExtractionResult, FieldResult
from fields_config import Standard, empty_result
from router import is_acceptable

# Số thật từ báo cáo VNM Q1/2026, trùng bộ dùng trong test_validation.py.
#
# don_vi_tinh phải có mặt: thiếu khai báo đơn vị là một cảnh báo thật sự,
# vì không biết bậc độ lớn thì không kiểm được ca đọc "triệu đồng" thành
# "đồng" — ca mà mọi đẳng thức kế toán đều bó tay.
VNM_Q1_2026 = {
    "tai_san_ngan_han": 29403116984122,
    "hang_ton_kho": 5393002084291,
    "tai_san_dai_han": 18372709942261,
    "tong_tai_san": 47775826926383,
    "no_phai_tra": 16666572149360,
    "von_chu_so_huu": 31109254777023,
    "doanh_thu_thuan": 13217639635987,
    "gia_von_hang_ban": 7278764406353,
    "loi_nhuan_gop": 5938875229634,
    "loi_nhuan_truoc_thue": 2523887147085,
    "loi_nhuan_sau_thue": 2049247209782,
    "don_vi_tinh": "đồng",
}


def test_ket_qua_rong_thi_khong_dat():
    assert is_acceptable(empty_result(), Standard.TT99) is False


def test_bao_cao_that_thi_dat():
    """Đủ field bắt buộc và không warning -> không cần gọi VLM."""
    assert is_acceptable(VNM_Q1_2026, Standard.TT99) is True


def test_thieu_field_bat_buoc_thi_khong_dat():
    thieu = dict(VNM_Q1_2026)
    thieu["tong_tai_san"] = None

    assert is_acceptable(thieu, Standard.TT99) is False


def _vlm_gia(gia_tri: dict) -> ExtractionResult:
    """
    Dựng ExtractionResult như nhánh VLM thật sẽ trả về: đơn vị tính nằm ở
    meta chứ không lẫn vào data.
    """
    return ExtractionResult(
        data={
            khoa: FieldResult.khong_do(v)
            for khoa, v in gia_tri.items()
            if khoa != "don_vi_tinh"
        },
        meta={"don_vi_tinh": gia_tri.get("don_vi_tinh")},
    )


def _lap_pipeline_gia(monkeypatch, ket_qua_vlm: dict):
    """
    Dựng một route_document() chạy được mà không cần mạng, model hay file.

    Thay đúng bốn thứ chạm ra ngoài: kiểm config, nguồn trang, lời gọi VLM,
    và hai chỗ ghi số liệu. Phần logic điều phối — thứ duy nhất đang được
    test — giữ nguyên.
    """
    monkeypatch.setattr(router, "require_config", lambda: None)
    monkeypatch.setattr(router, "iter_table_regions", lambda *a, **k: iter([]))
    monkeypatch.setattr(
        router, "extract_fields_from_regions", lambda *a, **k: _vlm_gia(ket_qua_vlm)
    )
    monkeypatch.setattr(router, "merge_into_totals", lambda run: None)
    monkeypatch.setattr(router.RunMetrics, "save", lambda self, *a, **k: None)


def _dem_lan_goi_is_acceptable(monkeypatch) -> list:
    """Đếm số lần cổng ràng buộc được hỏi ý kiến."""
    lan_goi = []
    that = router.is_acceptable

    def dem(result, standard):
        lan_goi.append(result)
        return that(result, standard)

    monkeypatch.setattr(router, "is_acceptable", dem)
    return lan_goi


def test_tat_cong_rang_buoc_thi_khong_ai_hoi_is_acceptable(monkeypatch):
    """
    Điều kiện để H1 có nghĩa. Chỉ cần MỘT quyết định trong đường đi đọc kết
    quả validate_result() là đầu ra đã bị chính tín hiệu đang được đánh giá
    làm sạch, và con số AUROC thu được không nói lên điều gì.
    """
    _lap_pipeline_gia(monkeypatch, VNM_Q1_2026)
    lan_goi = _dem_lan_goi_is_acceptable(monkeypatch)
    monkeypatch.setattr(router, "DISABLE_CONSTRAINT_GATE", True)

    router.route_document("bao_cao.pdf", save=False)

    assert lan_goi == []


def test_tat_cong_rang_buoc_van_tra_ve_du_ket_qua(monkeypatch):
    """Tắt cổng là bỏ phần LỌC, không phải bỏ phần trích xuất."""
    _lap_pipeline_gia(monkeypatch, VNM_Q1_2026)
    monkeypatch.setattr(router, "DISABLE_CONSTRAINT_GATE", True)

    ket_qua = router.route_document("bao_cao.pdf", save=False)

    assert ket_qua.values()["tong_tai_san"] == VNM_Q1_2026["tong_tai_san"]
    assert ket_qua.meta["don_vi_tinh_he_so"] == 1


def test_bat_cong_rang_buoc_thi_van_hoi_is_acceptable(monkeypatch):
    """Hồi quy: đường phục vụ bình thường không được đổi hành vi."""
    _lap_pipeline_gia(monkeypatch, VNM_Q1_2026)
    lan_goi = _dem_lan_goi_is_acceptable(monkeypatch)
    monkeypatch.setattr(router, "DISABLE_CONSTRAINT_GATE", False)

    router.route_document("bao_cao.pdf", save=False)

    assert lan_goi != []


def test_metrics_ghi_ro_luot_chay_o_che_do_nao(monkeypatch):
    """
    Một lượt chạy ở chế độ đo và một lượt chạy phục vụ cho ra dữ liệu không
    so được với nhau. Người đọc metrics.jsonl phải phân biệt được bằng một
    khoá có sẵn, đừng bắt họ suy ra từ sự vắng mặt của khoá khác.
    """
    da_ghi = {}
    _lap_pipeline_gia(monkeypatch, VNM_Q1_2026)
    monkeypatch.setattr(router, "DISABLE_CONSTRAINT_GATE", True)
    monkeypatch.setattr(
        router.RunMetrics, "set_info", lambda self, **kwargs: da_ghi.update(kwargs)
    )

    router.route_document("bao_cao.pdf", save=False)

    assert da_ghi["constraint_gate"] is False


def test_co_gia_tri_nhung_sai_thi_van_khong_dat():
    """
    Lớp bảo vệ quan trọng nhất của cổng này: mọi field đều CÓ giá trị,
    nhưng Hàng tồn kho bị đọc nhầm sang dòng "Dự phòng giảm giá hàng tồn
    kho" nên nhỏ hơn giá trị thật khoảng 1000 lần.

    Nếu is_acceptable() chỉ hỏi "đã đủ field chưa" thì con số sai này được
    chấp nhận và VLM không bao giờ được gọi. Đúng loại lỗi tệ nhất — có
    kết quả, trông hợp lệ, và sai âm thầm.
    """
    sai = dict(VNM_Q1_2026)
    sai["hang_ton_kho"] = 5393002084

    assert all(value is not None for value in sai.values())
    assert is_acceptable(sai, Standard.TT99) is False


def _vlm_gia_co_early_stop(gia_tri: dict, early_stop: dict):
    """Như _vlm_gia nhưng meta mang thêm early_stop, giống nhánh VLM thật."""
    ket_qua = _vlm_gia(gia_tri)
    ket_qua.meta["early_stop"] = early_stop
    ket_qua.meta["prompt_hash"] = "bam-gia"
    return ket_qua


def test_route_document_truyen_chuan_xuong_tan_buoc_kiem(monkeypatch):
    """
    Chuẩn do người gọi chỉ định phải đi tới tận validate_result().

    Hồi quy cho lỗi câm: router từng gọi validate_result() không truyền
    chuẩn, nên mọi tài liệu bị kiểm bằng DEFAULT_STANDARD (TT99) bất kể
    thực tế là chuẩn nào, và meta trả ra khai sai chuẩn đã dùng.
    """
    _lap_pipeline_gia(monkeypatch, VNM_Q1_2026)

    ket_qua = router.route_document("bao_cao.pdf", save=False, standard=Standard.TT200)

    assert ket_qua.meta["standard"] == "TT200"


def test_meta_ghi_ro_chuan_den_tu_dau(monkeypatch):
    """
    Biết chuẩn nào được dùng là chưa đủ — phải biết kết luận đó từ đâu ra.

    Một lượt lùi về mặc định và một lượt do người chỉ định cho ra cùng chữ
    "TT99". Gộp chúng lại là xoá mất chế độ lỗi "nhận diện sai chuẩn" khỏi
    mọi phép đo, mà đó đúng là thứ detect_standard() cố ý giữ lại bằng cách
    không bao giờ đoán bừa.
    """
    _lap_pipeline_gia(monkeypatch, VNM_Q1_2026)

    chi_dinh = router.route_document("a.pdf", save=False, standard=Standard.TT99)
    lui_mac_dinh = router.route_document("b.pdf", save=False)

    assert chi_dinh.meta["standard"] == lui_mac_dinh.meta["standard"] == "TT99"
    assert chi_dinh.meta["standard_nguon"] == "tham_so"
    assert lui_mac_dinh.meta["standard_nguon"] == "mac_dinh"


def test_meta_giu_lai_early_stop_cua_nhanh_vlm(monkeypatch):
    """
    early_stop phải sống sót ra tới đầu ra của router.

    Hồi quy: route_document() từng gán meta = meta của validate_result(),
    tức ĐÈ mất mọi thứ nhánh trích xuất biết. Nên trên đường chạy thật —
    API và CLI — không ai thấy được lượt chạy đã dừng ở trang nào và còn
    thiếu field gì. Cờ dừng sớm sinh ra chính để không giấu điều đó, và
    tests/test_early_stop.py không bắt được vì nó gọi thẳng hàm VLM.
    """
    dung_som = {
        "da_dung_som": True,
        "ly_do": "het_bang_de_doc",
        "trang_cuoi": 7,
        "field_con_thieu": ["hang_ton_kho"],
    }
    monkeypatch.setattr(router, "require_config", lambda: None)
    monkeypatch.setattr(router, "iter_table_regions", lambda *a, **k: iter([]))
    monkeypatch.setattr(
        router,
        "extract_fields_from_regions",
        lambda *a, **k: _vlm_gia_co_early_stop(VNM_Q1_2026, dung_som),
    )
    monkeypatch.setattr(router, "merge_into_totals", lambda run: None)
    monkeypatch.setattr(router.RunMetrics, "save", lambda self, *a, **k: None)

    ket_qua = router.route_document("bao_cao.pdf", save=False)

    assert ket_qua.meta["early_stop"] == dung_som
