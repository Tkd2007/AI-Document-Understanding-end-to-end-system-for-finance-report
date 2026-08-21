"""
Test cổng quyết định fallback của router.

Chạy được mà không cần API key hay mạng là nhờ `require_config()` được gọi
lúc BẮT ĐẦU một lượt chạy chứ không phải lúc import — xem docstring của nó
trong extract_vlm.py. `is_acceptable()` là logic thuần, nhưng nó quyết định
có gọi VLM hay không, tức là quyết định cả chi phí lẫn độ đúng của kết quả.
"""

import router
from fields_config import empty_result
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
    assert is_acceptable(empty_result()) is False


def test_bao_cao_that_thi_dat():
    """Đủ field bắt buộc và không warning -> không cần gọi VLM."""
    assert is_acceptable(VNM_Q1_2026) is True


def test_thieu_field_bat_buoc_thi_khong_dat():
    thieu = dict(VNM_Q1_2026)
    thieu["tong_tai_san"] = None

    assert is_acceptable(thieu) is False


def _lap_pipeline_gia(monkeypatch, ket_qua_vlm: dict):
    """
    Dựng một route_document() chạy được mà không cần mạng, model hay file.

    Thay đúng bốn thứ chạm ra ngoài: kiểm config, nguồn trang, lời gọi VLM,
    và hai chỗ ghi số liệu. Phần logic điều phối — thứ duy nhất đang được
    test — giữ nguyên.
    """
    monkeypatch.setattr(router, "require_config", lambda: None)
    monkeypatch.setattr(router, "iter_table_regions", lambda *a, **k: iter([]))
    monkeypatch.setattr(router, "extract_fields_from_regions", lambda *a, **k: ket_qua_vlm)
    monkeypatch.setattr(router, "merge_into_totals", lambda run: None)
    monkeypatch.setattr(router.RunMetrics, "save", lambda self, *a, **k: None)


def _dem_lan_goi_is_acceptable(monkeypatch) -> list:
    """Đếm số lần cổng ràng buộc được hỏi ý kiến."""
    lan_goi = []
    that = router.is_acceptable

    def dem(result):
        lan_goi.append(result)
        return that(result)

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

    data = router.route_document("bao_cao.pdf", save=False)

    assert data["tong_tai_san"] == VNM_Q1_2026["tong_tai_san"]


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
    assert is_acceptable(sai) is False
