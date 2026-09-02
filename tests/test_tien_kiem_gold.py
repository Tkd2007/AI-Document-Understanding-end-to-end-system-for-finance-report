"""
Kiểm `tien_kiem.py` — script mà một phiên mới chạy THAY CHO việc đọc tài liệu.

Vì sao nó đáng có test dù chỉ là công cụ: cả thiết kế của kỹ năng
`chay-tap-gold` đặt cược vào chỗ "chạy lệnh này, xanh thì chạy tiếp". Một
script tiền kiểm bỏ sót vấn đề còn tệ hơn không có script, vì nó biến sự im
lặng thành lời cam đoan rằng tập gold sạch — và cái giá trả sau đó là hàng
giờ OCR trên một tập không chấm được.

Script nằm ngoài `src/` nên không import theo tên module được; nạp bằng
đường dẫn, đúng cách mà người dùng gọi nó.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]
DUONG_DAN_SCRIPT = GOC / ".claude" / "skills" / "chay-tap-gold" / "tien_kiem.py"


@pytest.fixture(scope="module")
def tien_kiem():
    dac_ta = importlib.util.spec_from_file_location("tien_kiem_gold", DUONG_DAN_SCRIPT)
    module = importlib.util.module_from_spec(dac_ta)
    sys.modules["tien_kiem_gold"] = module
    dac_ta.loader.exec_module(module)
    return module


def _ho_so_gold(chuan: str = "TT99", **ghi_de) -> dict:
    """Một hồ sơ gold hợp lệ tối thiểu, đủ mọi khoá bắt buộc."""
    from fields_config import Standard, fields_for

    ho_so = {
        "doc_id": f"AAA_2026Q1_{chuan}",
        "ticker": "AAA",
        "period": "2026Q1",
        "standard": chuan,
        "quy_uoc_dau": "tru",
        "unit_declared": "Đơn vị tính: VND",
        "unit_multiplier": 1,
        "values": {ten: 0 for ten in fields_for(Standard(chuan))},
        "source_url": "https://vi.du/bao-cao.pdf",
        "downloaded_at": "2026-09-02",
        "annotator": "Danh",
        "annotated_at": "2026-09-02T00:00:00+00:00",
    }
    ho_so.update(ghi_de)
    return ho_so


def _dung_tap(tmp_path: Path, cac_ho_so: list[dict], co_pdf: bool = True) -> tuple[Path, Path]:
    thu_muc_gold = tmp_path / "gold"
    thu_muc_pdf = tmp_path / "bctc"
    thu_muc_gold.mkdir()
    thu_muc_pdf.mkdir()
    for ho_so in cac_ho_so:
        (thu_muc_gold / f"{ho_so['doc_id']}.json").write_text(
            json.dumps(ho_so, ensure_ascii=False), encoding="utf-8"
        )
        if co_pdf:
            (thu_muc_pdf / f"{ho_so['doc_id']}.pdf").write_bytes(b"%PDF-1.4\n")
    return thu_muc_gold, thu_muc_pdf


@pytest.fixture
def tro_toi(tien_kiem, monkeypatch):
    def _tro(thu_muc_gold: Path, thu_muc_pdf: Path):
        monkeypatch.setattr(tien_kiem, "THU_MUC_GOLD", thu_muc_gold)
        monkeypatch.setattr(tien_kiem, "THU_MUC_PDF", thu_muc_pdf)
    return _tro


def test_tap_hop_le_thi_khong_bao_van_de(tien_kiem, tro_toi, tmp_path):
    cac_ho_so = [_ho_so_gold("TT99"), _ho_so_gold("TT200", doc_id="BBB_2026Q1_TT200")]
    tro_toi(*_dung_tap(tmp_path, cac_ho_so))
    van_de, thong_ke = tien_kiem.kiem_gold()
    assert van_de == []
    assert thong_ke["so_file"] == 2
    assert thong_ke["theo_chuan"] == {"TT99": 1, "TT200": 1}


def test_thieu_chi_tieu_thi_bao(tien_kiem, tro_toi, tmp_path):
    ho_so = _ho_so_gold()
    ho_so["values"].pop("tong_tai_san")
    tro_toi(*_dung_tap(tmp_path, [ho_so]))
    van_de, _ = tien_kiem.kiem_gold()
    assert len(van_de) == 1
    assert "tong_tai_san" in van_de[0][1]


def test_thieu_quy_uoc_dau_thi_bao(tien_kiem, tro_toi, tmp_path):
    """Đúng chế độ hỏng đã xảy ra thật: file gán nhãn trước 01/09/2026."""
    ho_so = _ho_so_gold()
    del ho_so["quy_uoc_dau"]
    tro_toi(*_dung_tap(tmp_path, [ho_so]))
    van_de, _ = tien_kiem.kiem_gold()
    assert len(van_de) == 1
    assert "quy_uoc_dau" in van_de[0][1]


def test_thieu_pdf_thi_bao(tien_kiem, tro_toi, tmp_path):
    tro_toi(*_dung_tap(tmp_path, [_ho_so_gold()], co_pdf=False))
    van_de, _ = tien_kiem.kiem_gold()
    assert len(van_de) == 1
    assert "PDF" in van_de[0][1]


def test_doc_id_lech_ten_file_thi_bao(tien_kiem, tro_toi, tmp_path):
    """doc_id lệch tên file làm `--chi` và `--tiep-tuc` trỏ nhầm tài liệu."""
    thu_muc_gold, thu_muc_pdf = _dung_tap(tmp_path, [_ho_so_gold()])
    (thu_muc_gold / "AAA_2026Q1_TT99.json").rename(thu_muc_gold / "CCC_2026Q1_TT99.json")
    (thu_muc_pdf / "CCC_2026Q1_TT99.pdf").write_bytes(b"%PDF-1.4\n")
    tro_toi(thu_muc_gold, thu_muc_pdf)
    van_de, _ = tien_kiem.kiem_gold()
    assert any("không khớp tên file" in ly_do for _, ly_do in van_de)


def test_dem_dong_ho_va_quy_uoc_dau(tien_kiem, tro_toi, tmp_path):
    tro_toi(
        *_dung_tap(
            tmp_path,
            [
                _ho_so_gold(trang_thai_dong_ho="da_do"),
                _ho_so_gold(doc_id="BBB_2026Q1_TT99", quy_uoc_dau="tong"),
            ],
        )
    )
    _, thong_ke = tien_kiem.kiem_gold()
    assert thong_ke["so_co_dong_ho"] == 1
    assert thong_ke["theo_quy_uoc_dau"] == {"tru": 1, "tong": 1}


def test_sao_luu_chep_ket_qua_luot_truoc(tien_kiem, monkeypatch, tmp_path):
    """Cạm bẫy 3 của kỹ năng: `--chi` không kèm `--tiep-tuc` ghi đè file kết quả."""
    thu_muc_ra = tmp_path / "output"
    thu_muc_ra.mkdir()
    (thu_muc_ra / "tap_gold_chuan_tu_gold.json").write_text("{}", encoding="utf-8")
    (thu_muc_ra / "tap_gold_chuan_tu_gold_pipeline.log").write_text("log", encoding="utf-8")
    # Mốc so sánh có ngày trong tên đã là bản sao rồi, không chép tiếp.
    (thu_muc_ra / "tap_gold_chuan_tu_gold_2026-08-30.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(tien_kiem, "THU_MUC_RA", thu_muc_ra)
    monkeypatch.setattr(tien_kiem, "THU_MUC_SAO_LUU", thu_muc_ra / "sao_luu_tu_dong")

    da_chep = tien_kiem.sao_luu()

    assert len(da_chep) == 2
    assert all("2026-08-30" not in ten for ten in da_chep)
    assert len(list((thu_muc_ra / "sao_luu_tu_dong").iterdir())) == 2


def test_danh_muc_thieu_thi_canh_bao_nhung_khong_chan(tien_kiem, monkeypatch, tmp_path):
    thu_muc_gold, _ = _dung_tap(tmp_path, [_ho_so_gold(), _ho_so_gold(doc_id="BBB_2026Q1_TT99")])
    danh_muc = tmp_path / "nguon_gold.json"
    danh_muc.write_text(
        json.dumps({"tai_lieu": [{"doc_id": "AAA_2026Q1_TT99"}]}), encoding="utf-8"
    )
    monkeypatch.setattr(tien_kiem, "THU_MUC_GOLD", thu_muc_gold)
    monkeypatch.setattr(tien_kiem, "DANH_MUC_NGUON", danh_muc)

    canh_bao = tien_kiem.kiem_danh_muc(2)

    assert canh_bao is not None
    assert "1/2" in canh_bao
