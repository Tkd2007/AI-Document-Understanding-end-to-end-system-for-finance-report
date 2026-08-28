"""
Tập gán nhãn đôi không được chứa tài liệu đã lộ đáp án cho người gán nhãn.

Quyết định Câu 12 (28/08/2026) loại mọi tài liệu đã chạy pipeline khỏi tập
gán nhãn đôi. Vi phạm nó không làm gì nổ: con số đồng thuận vẫn tính ra, chỉ
là nó đo trí nhớ của người gán nhãn về giá trị máy đoán chứ không đo tính
nhất quán của quy tắc — và không có cách nào phát hiện ngược từ dữ liệu.
Cùng loại nguy hiểm với Luật 1, nên xử lý cùng cách: cưỡng chế bằng test.

Test cuối cùng là test đáng giá nhất — nó chạy trên dữ liệu THẬT của repo và
sẽ đỏ vào đúng ngày ai đó chạy pipeline trên một tài liệu mới mà quên cập
nhật `data/nguon_gold.json`.
"""

import json
from pathlib import Path

from eval.tap_dong_thuan import (
    DU_DIEU_KIEN,
    LOAI_DA_CHAY,
    doc_id_co_dau_ra_pipeline,
    doi_chieu,
    tai_lieu_du_dieu_kien,
    tai_lieu_ngoai_danh_muc,
)

REPO = Path(__file__).resolve().parents[1]


def _lap_thu_muc(tmp_path: Path, tap_gold: list[str], gold: list[str], khac: list[str]):
    """Dựng một cặp thư mục output/gold giả, trả về (output, gold)."""
    thu_muc_out = tmp_path / "output"
    thu_muc_gold = tmp_path / "gold"
    thu_muc_out.mkdir()
    thu_muc_gold.mkdir()

    if tap_gold:
        (thu_muc_out / "tap_gold_chuan_tu_gold.json").write_text(
            json.dumps({"tung_tai_lieu": [{"doc_id": d} for d in tap_gold]}),
            encoding="utf-8",
        )
    for doc_id in gold:
        (thu_muc_gold / f"{doc_id}.json").write_text("{}", encoding="utf-8")
    for ten in khac:
        (thu_muc_out / ten).write_text("{}", encoding="utf-8")

    return thu_muc_out, thu_muc_gold


def _danh_muc(tmp_path: Path, muc: dict[str, str]) -> Path:
    duong_dan = tmp_path / "nguon_gold.json"
    duong_dan.write_text(
        json.dumps(
            {"tai_lieu": [{"doc_id": d, "gan_nhan_doi": k} for d, k in muc.items()]},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return duong_dan


def test_bat_duoc_doc_id_trong_file_ket_qua_tap_gold(tmp_path):
    out, gold = _lap_thu_muc(tmp_path, ["AAA_2026Q1_TT99"], [], [])

    assert doc_id_co_dau_ra_pipeline(out, gold) == {
        "AAA_2026Q1_TT99": ["tap_gold_chuan_tu_gold.json"]
    }


def test_bat_duoc_file_dat_ten_theo_pdf_qua_ma_chung_khoan(tmp_path):
    """
    File `*_routed.json` đặt tên theo PDF nên không có `doc_id` để tra. Bỏ
    qua chúng là bỏ sót đúng ca VNM: có nhãn gold, có đầu ra pipeline, mà
    không nằm trong danh mục nguồn.
    """
    out, gold = _lap_thu_muc(
        tmp_path, [], ["VNM_2026Q1_TT99"], ["20260429_VNM_BCTC_Q1_abc_routed.json"]
    )

    assert doc_id_co_dau_ra_pipeline(out, gold) == {
        "VNM_2026Q1_TT99": ["20260429_VNM_BCTC_Q1_abc_routed.json"]
    }


def test_khong_nham_ma_chung_khoan_voi_chu_khac_trong_ten_file(tmp_path):
    """Chỉ khớp khi mã đứng thành một đoạn riêng, không khớp chuỗi con."""
    out, gold = _lap_thu_muc(
        tmp_path, [], ["VNM_2026Q1_TT99"], ["20260429_HPGVNMX_BCTC_routed.json"]
    )

    assert doc_id_co_dau_ra_pipeline(out, gold) == {}


def test_khai_du_dieu_kien_ma_co_dau_ra_pipeline_thi_lech_so_sach(tmp_path):
    out, gold = _lap_thu_muc(tmp_path, ["AAA_2026Q1_TT99"], [], [])
    danh_muc = _danh_muc(tmp_path, {"AAA_2026Q1_TT99": DU_DIEU_KIEN})

    trang_thai = doi_chieu(out, danh_muc, gold)

    assert trang_thai["AAA_2026Q1_TT99"]["khop"] is False


def test_khai_loai_va_co_dau_ra_pipeline_thi_khop(tmp_path):
    out, gold = _lap_thu_muc(tmp_path, ["AAA_2026Q1_TT99"], [], [])
    danh_muc = _danh_muc(tmp_path, {"AAA_2026Q1_TT99": LOAI_DA_CHAY})

    assert doi_chieu(out, danh_muc, gold)["AAA_2026Q1_TT99"]["khop"] is True


def test_khai_loai_ma_khong_con_file_van_khop(tmp_path):
    """
    Xoá `data/output/` không trả lại quyền vào tập gán nhãn đôi: việc người
    ấy đã nhìn thấy máy đoán gì thì đã xảy ra rồi. Nên chiều này KHÔNG phải
    lệch sổ sách, và tài liệu vẫn bị loại.
    """
    out, gold = _lap_thu_muc(tmp_path, [], [], [])
    danh_muc = _danh_muc(tmp_path, {"AAA_2026Q1_TT99": LOAI_DA_CHAY})

    assert doi_chieu(out, danh_muc, gold)["AAA_2026Q1_TT99"]["khop"] is True
    assert tai_lieu_du_dieu_kien(out, danh_muc, gold) == []


def test_du_dieu_kien_doi_ca_hai_dieu_kien(tmp_path):
    out, gold = _lap_thu_muc(tmp_path, ["AAA_2026Q1_TT99"], [], [])
    danh_muc = _danh_muc(
        tmp_path,
        {
            "AAA_2026Q1_TT99": DU_DIEU_KIEN,   # khai được nhưng đã chạy pipeline
            "BBB_2026Q1_TT99": DU_DIEU_KIEN,   # khai được và chưa chạy
            "CCC_2026Q1_TT99": LOAI_DA_CHAY,
        },
    )

    assert tai_lieu_du_dieu_kien(out, danh_muc, gold) == ["BBB_2026Q1_TT99"]


def test_tai_lieu_co_nhan_gold_ma_khong_trong_danh_muc_van_bi_neu_ten(tmp_path):
    out, gold = _lap_thu_muc(
        tmp_path, [], ["VNM_2026Q1_TT99"], ["20260429_VNM_BCTC_Q1_abc_routed.json"]
    )
    danh_muc = _danh_muc(tmp_path, {"AAA_2026Q1_TT99": LOAI_DA_CHAY})

    assert list(tai_lieu_ngoai_danh_muc(out, danh_muc, gold)) == ["VNM_2026Q1_TT99"]


def test_danh_muc_that_cua_repo_khop_voi_hien_trang_data_output():
    """
    Hồi quy trên dữ liệu THẬT: mọi tài liệu đã chạy pipeline đều đã được
    đánh dấu loại trong `data/nguon_gold.json`.

    Test này đỏ đúng vào ngày có người chạy pipeline trên một tài liệu mới
    mà quên cập nhật danh mục — thời điểm duy nhất sửa được, vì sau đó tài
    liệu ấy có thể đã nằm trong lượt gán nhãn đôi.
    """
    trang_thai = doi_chieu(
        REPO / "data" / "output", REPO / "data" / "nguon_gold.json", REPO / "data" / "gold"
    )
    lech = [doc_id for doc_id, muc in trang_thai.items() if not muc["khop"]]

    assert lech == [], (
        f"{lech} có đầu ra pipeline trong data/output/ nhưng data/nguon_gold.json "
        f"chưa đánh dấu {LOAI_DA_CHAY!r} — xem ANNOTATION-GUIDELINE.md mục 5"
    )
