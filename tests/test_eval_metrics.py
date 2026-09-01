"""
Test các chỉ số đánh giá chất lượng trích xuất.

Test đáng chú ý nhất là nhóm fabrication_rate: nó bảo vệ chỉ số chống bịa,
thứ duy nhất ngăn một hệ ép số cho khớp phương trình đạt điểm tuyệt đối ở
mọi chỉ số còn lại — bảng cân đối cân hoàn hảo, chứng chỉ PASS, và mọi con
số đều sai.
"""

import numpy as np
import pytest

from eval.metrics import (
    document_fully_correct,
    fabrication_rate,
    field_accuracy,
    gop_ty_le,
    khop_so,
    localization_top_k,
    silent_error_rate,
)
from eval.schema import GroundTruthDoc

GOLD = {"a": 100, "b": 200, "c": 300}

# a + b = c, dạng ma trận. Đủ nhỏ để kiểm bằng mắt.
A = np.array([[1.0, 1.0, -1.0]])
THU_TU = ["a", "b", "c"]


# --- So khớp số --------------------------------------------------------------


def test_lech_trong_dung_sai_thi_van_khop():
    """Dung sai chỉ để bỏ qua làm tròn ở đơn vị rút gọn, không hơn."""
    assert khop_so(1_000_000_000, 1_000_000_000 + 50)


def test_lech_ngoai_dung_sai_thi_khong_khop():
    assert not khop_so(1_000_000_000, 1_000_100_000)


def test_none_chi_khop_voi_none():
    assert khop_so(None, None)
    assert not khop_so(None, 100)
    assert not khop_so(100, None)


# --- Độ chính xác mức trường -------------------------------------------------


def test_field_accuracy_tra_ca_tu_va_mau():
    """
    Trả cả tử và mẫu chứ không chỉ tỷ lệ, vì bootstrap theo cụm cần cộng
    dồn qua nhiều tài liệu — trung bình của các tỷ lệ KHÁC tỷ lệ của tổng
    khi các tài liệu có số trường khác nhau.
    """
    ket_qua = field_accuracy({"a": 100, "b": 999, "c": 300}, GOLD)

    assert ket_qua == {"dung": 2, "tong": 3, "ty_le": pytest.approx(2 / 3)}


def test_gop_ty_le_cong_tu_va_mau_chu_khong_lay_trung_binh():
    """
    Hai tài liệu, một cái 1/1 và một cái 0/99. Tỷ lệ đúng là 1/100 = 0,01.
    Trung bình của các tỷ lệ cho 0,5 — sai 50 lần, và sai theo hướng lạc
    quan vì tài liệu nhỏ được cùng trọng số với tài liệu lớn.
    """
    cac_tai_lieu = [{"dung": 1, "tong": 1}, {"dung": 0, "tong": 99}]

    assert gop_ty_le(cac_tai_lieu, "dung", "tong") == pytest.approx(0.01)


# --- Lỗi câm -----------------------------------------------------------------


def test_lo_i_cam_chi_dem_tren_nhung_truong_CO_gia_tri():
    """
    Trả null là lỗi ỒN: hệ biết mình thất bại và có thể fallback hoặc đẩy
    cho người. Nó không được tính vào mẫu số của lỗi câm, vì chỉ số này
    tách riêng loại lỗi nguy hiểm hơn hẳn — có giá trị, trông hợp lệ, và
    sai âm thầm.
    """
    du_doan = {"a": 100, "b": None, "c": 999}

    assert silent_error_rate(du_doan, GOLD) == {
        "sai": 1,
        "co_gia_tri": 2,
        "ty_le": pytest.approx(0.5),
    }


def test_khong_truong_nao_co_gia_tri_thi_ty_le_bang_0():
    """Không trả gì thì không bịa gì. Chia cho 0 ở đây phải là 0, không nổ."""
    ket_qua = silent_error_rate({"a": None, "b": None, "c": None}, GOLD)

    assert ket_qua["ty_le"] == 0.0


def test_document_fully_correct_doi_hoi_dung_HET():
    """
    Chỉ số mà pipeline dữ liệu thật quan tâm: một tài liệu có đúng một
    trường sai thì vẫn phải người kiểm lại toàn bộ.
    """
    assert document_fully_correct(dict(GOLD), GOLD)
    assert not document_fully_correct({**GOLD, "b": 201}, GOLD)


# --- Định vị -----------------------------------------------------------------


def test_top_k_bat_trung_truong_sai():
    assert localization_top_k(["b", "a", "c"], {"a"}, k=3) == 1.0
    assert localization_top_k(["b", "a", "c"], {"a"}, k=1) == 0.0


def test_top_k_tren_tai_lieu_khong_co_loi_tra_0():
    """
    Tài liệu không có lỗi nào KHÔNG thuộc mẫu của H2 và người gọi phải lọc
    bỏ trước. Trả 1.0 ở đây sẽ thổi phồng Top-k bằng những tài liệu mà bài
    toán định vị còn không đặt ra.
    """
    assert localization_top_k(["a", "b"], set(), k=3) == 0.0


# --- Chống bịa ---------------------------------------------------------------


def test_thoa_rang_buoc_nhung_sai_su_that_thi_bi_dem_la_bia():
    """
    TEST BẢO VỆ LUẬN ĐIỂM CỐT LÕI.

    Dự đoán (10, 20, 30) thoả hoàn hảo đẳng thức a + b = c, nhưng sự thật
    là (15, 15, 30). Đây đúng là thứ mà một hệ ép số cho khớp phương trình
    sẽ sinh ra: bảng cân hoàn hảo, chứng chỉ PASS, và hai trên ba con số
    sai. Không có chỉ số này thì hệ đó đạt điểm tuyệt đối ở mọi chỗ khác.
    """
    ket_qua = fabrication_rate({"a": 10, "b": 20, "c": 30}, {"a": 15, "b": 15, "c": 30}, A, THU_TU)

    assert ket_qua["thoa_rang_buoc"] is True
    assert ket_qua["bia"] == 2
    assert ket_qua["ty_le"] == pytest.approx(2 / 3)


def test_con_vi_pham_rang_buoc_thi_chua_tinh_la_bia():
    """
    Ràng buộc còn bị vi phạm nghĩa là hệ chưa "khớp" nên chưa bịa xong. Ca
    đó là lỗi thường và đã được các chỉ số khác đếm — đếm thêm ở đây sẽ
    tính hai lần.
    """
    ket_qua = fabrication_rate({"a": 10, "b": 20, "c": 31}, {"a": 15, "b": 15, "c": 30}, A, THU_TU)

    assert ket_qua["thoa_rang_buoc"] is False
    assert ket_qua["bia"] == 0


def test_dung_het_thi_khong_co_gi_bi_dem_la_bia():
    ket_qua = fabrication_rate({"a": 100, "b": 200, "c": 300}, GOLD, A, THU_TU)

    assert ket_qua["thoa_rang_buoc"] is True
    assert ket_qua["bia"] == 0


def test_thieu_truong_thi_khong_dung_duoc_vector_de_kiem():
    ket_qua = fabrication_rate({"a": 10, "b": None, "c": 30}, GOLD, A, THU_TU)

    assert ket_qua["thoa_rang_buoc"] is False
    assert ket_qua["bia"] == 0


def test_bat_bien_scale_van_thoa_rang_buoc_nhung_sai_het():
    """
    Nhân mọi giá trị với một triệu — đúng ca đọc "triệu đồng" thành "đồng".
    Đẳng thức vẫn khớp tuyệt đối vì hệ ràng buộc là thuần nhất, nên CẢ BA
    trường bị đếm là bịa. Đây chính là lý do mỏ neo đơn vị tính là bắt
    buộc: ràng buộc không bao giờ bắt được ca này.
    """
    ket_qua = fabrication_rate(
        {"a": 100 * 10**6, "b": 200 * 10**6, "c": 300 * 10**6}, GOLD, A, THU_TU
    )

    assert ket_qua["thoa_rang_buoc"] is True
    assert ket_qua["bia"] == 3


# --- Schema ------------------------------------------------------------------


def _gold_hop_le(**ghi_de) -> dict:
    mac_dinh = {
        "doc_id": "VNM_2026Q1_TT99",
        "ticker": "VNM",
        "period": "2026Q1",
        "standard": "TT99",
        "quy_uoc_dau": "tru",
        "unit_declared": "đồng",
        "unit_multiplier": 1,
        "values": dict(GOLD),
        "source_url": "https://example.test/vnm.pdf",
        "downloaded_at": "2026-08-22",
        "annotator": "tkd",
        "annotated_at": "2026-08-22",
    }
    return {**mac_dinh, **ghi_de}


@pytest.mark.parametrize(
    "thieu", ["doc_id", "source_url", "downloaded_at", "annotator", "annotated_at"]
)
def test_thieu_truong_bat_buoc_thi_bao_loi_ngay(thieu):
    """
    source_url và downloaded_at bắt buộc vì bản PDF gốc vẫn có bản quyền
    trình bày, nên phương án phát hành an toàn là phát hành annotation kèm
    URL nguồn và script tải. Thiếu chúng thì không phát hành dataset được,
    mà dataset là một trong bốn kết quả dự kiến của cả nghiên cứu.

    annotator và annotated_at bắt buộc vì quy trình gán nhãn cam kết rằng
    người gán nhãn mù với đầu ra pipeline và gán nhãn xong mới chạy
    pipeline — chỉ dấu thời gian mới kiểm chứng được điều đó.
    """
    with pytest.raises(ValueError, match=thieu):
        GroundTruthDoc(**_gold_hop_le(**{thieu: ""}))


def test_ghi_va_doc_lai_ground_truth(tmp_path):
    goc = GroundTruthDoc(**_gold_hop_le())

    duong_dan = goc.save(tmp_path)
    doc_lai = GroundTruthDoc.load(duong_dan)

    assert doc_lai == goc
    assert duong_dan.name == "VNM_2026Q1_TT99.json"
