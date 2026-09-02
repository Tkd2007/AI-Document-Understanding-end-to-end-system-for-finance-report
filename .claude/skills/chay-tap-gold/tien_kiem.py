"""
Tiền kiểm tập gold và sao lưu kết quả cũ — chạy TRƯỚC mọi lượt chấm.

Vì sao script này tồn tại thay vì để mỗi phiên tự dò lại: phiên ngày
02/09/2026 tiêu gần hai chục lượt gọi công cụ chỉ để trả lời ba câu mà lượt
chạy nào cũng phải hỏi — file gold có đọc được không, có đủ PDF không, và
kết quả cũ đã sao lưu chưa. Cả ba đều kiểm được bằng máy trong vài giây, nên
để người đọc tài liệu rồi tự làm là trả cùng một cái giá mỗi phiên.

Nó KHÔNG chấm điểm và KHÔNG gọi API. Chạy xong thì in ra đúng lệnh kế tiếp.

Ba việc, theo thứ tự:

  1. Sao lưu `data/output/tap_gold_*.json` và `*_pipeline.log` sang
     `data/output/sao_luu_tu_dong/` kèm dấu thời gian. Đây là cạm bẫy 3 của
     kỹ năng: `--chi BMP SBT` mà quên `--tiep-tuc` sẽ ghi đè file kết quả
     bằng đúng hai tài liệu, xoá sạch lượt chạy trọn bộ. Thư mục riêng chứ
     không đặt cạnh các mốc so sánh, vì `tap_gold_chuan_tu_gold_<ngày>.json`
     là tên dành cho mốc do người chọn giữ lại, không phải cho bản sao máy.
  2. Nạp mọi file gold qua `GroundTruthDoc.load()` — đúng đường mà
     `chay_tap_gold.py` sẽ đi, nên thiếu khoá bắt buộc thì lộ ra ở đây chứ
     không lộ ra sau bốn tiếng chạy OCR.
  3. Đối chiếu bộ chỉ tiêu với `fields_for(chuẩn)`, và đối chiếu doc_id với
     PDF trong `data/bctc/`.

Số liệu hiện trạng do script IN RA chứ không chép vào tài liệu: tập gold đổi
mỗi đợt gán nhãn, và một con số chép tay trong file MD là một con số sẽ cũ đi
mà không ai biết.

Chạy:
    python .claude/skills/chay-tap-gold/tien_kiem.py
"""

import json
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

GOC = Path(__file__).resolve().parents[3]
THU_MUC_GOLD = GOC / "data" / "gold"
THU_MUC_PDF = GOC / "data" / "bctc"
THU_MUC_RA = GOC / "data" / "output"
THU_MUC_SAO_LUU = THU_MUC_RA / "sao_luu_tu_dong"
DANH_MUC_NGUON = GOC / "data" / "nguon_gold.json"

# Script này nằm ngoài src/ nên không hưởng `pythonpath = src` của pytest.ini.
# Tự chèn để người chạy không phải nhớ đặt PYTHONPATH — quên nó là lỗi
# ModuleNotFoundError ngay dòng import, và đó đúng là loại ma sát mà script
# này sinh ra để xoá.
sys.path.insert(0, str(GOC / "src"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from eval.schema import GroundTruthDoc  # noqa: E402
from fields_config import Standard, fields_for  # noqa: E402


def sao_luu() -> list[str]:
    """Chép kết quả và log của lượt trước sang thư mục sao lưu tự động."""
    can_chep = sorted(THU_MUC_RA.glob("tap_gold_*.json")) + sorted(
        THU_MUC_RA.glob("tap_gold_*_pipeline.log")
    )
    # Chỉ chép file lượt chạy HIỆN HÀNH. Các mốc so sánh có ngày trong tên đã
    # là bản sao rồi, chép tiếp chỉ làm phình thư mục.
    can_chep = [d for d in can_chep if d.stem in ("tap_gold_chuan_tu_gold",
                                                  "tap_gold_dau_cuoi",
                                                  "tap_gold_chuan_tu_gold_pipeline",
                                                  "tap_gold_dau_cuoi_pipeline")]
    if not can_chep:
        return []

    dau_thoi_gian = datetime.now().strftime("%Y-%m-%d-%H%M")
    THU_MUC_SAO_LUU.mkdir(parents=True, exist_ok=True)
    da_chep = []
    for duong_dan in can_chep:
        dich = THU_MUC_SAO_LUU / f"{duong_dan.stem}_{dau_thoi_gian}{duong_dan.suffix}"
        if dich.exists():
            continue
        shutil.copy2(duong_dan, dich)
        da_chep.append(dich.name)
    return da_chep


def kiem_gold() -> tuple[list[tuple[str, str]], dict]:
    """Trả (danh sách vấn đề, thống kê). Vấn đề rỗng nghĩa là chạy được."""
    van_de: list[tuple[str, str]] = []
    dem_chuan: Counter = Counter()
    dem_quy_uoc: Counter = Counter()
    so_co_dong_ho = 0
    cac_file = sorted(THU_MUC_GOLD.glob("*.json"))

    for duong_dan in cac_file:
        try:
            gold = GroundTruthDoc.load(duong_dan)
        except Exception as loi:  # noqa: BLE001
            van_de.append((duong_dan.name, f"không nạp được — {type(loi).__name__}: {loi}"))
            continue

        if gold.doc_id != duong_dan.stem:
            van_de.append((duong_dan.name, f"doc_id `{gold.doc_id}` không khớp tên file"))
        try:
            chuan = Standard(gold.standard)
        except ValueError:
            van_de.append((duong_dan.name, f"standard không hợp lệ: {gold.standard!r}"))
            continue

        dem_chuan[gold.standard] += 1
        dem_quy_uoc[gold.quy_uoc_dau] += 1
        if gold.trang_thai_dong_ho == "da_do":
            so_co_dong_ho += 1

        mong_doi = set(fields_for(chuan))
        thieu = mong_doi - set(gold.values)
        thua = set(gold.values) - mong_doi
        if thieu:
            van_de.append((duong_dan.name, f"thiếu {len(thieu)} chỉ tiêu: {sorted(thieu)}"))
        if thua:
            van_de.append((duong_dan.name, f"thừa khoá: {sorted(thua)}"))
        if not (THU_MUC_PDF / f"{gold.doc_id}.pdf").exists():
            van_de.append((duong_dan.name, "không có PDF trong data/bctc/"))
        if not isinstance(gold.unit_multiplier, int) or gold.unit_multiplier <= 0:
            van_de.append((duong_dan.name, f"unit_multiplier = {gold.unit_multiplier!r}"))

    return van_de, {
        "so_file": len(cac_file),
        "theo_chuan": dict(dem_chuan),
        "theo_quy_uoc_dau": dict(dem_quy_uoc),
        "so_co_dong_ho": so_co_dong_ho,
    }


def kiem_danh_muc(so_file_gold: int) -> str | None:
    """
    Đối chiếu tập gold với `data/nguon_gold.json`.

    Danh mục thiếu KHÔNG chặn lượt chấm — `chay_tap_gold.py` chỉ đọc
    `data/gold/`. Nhưng nó chặn việc phát hành dataset và làm
    `tap_dong_thuan.py` đếm sai tập gán nhãn đôi, nên phải nói ra chứ không
    để im.
    """
    if not DANH_MUC_NGUON.exists():
        return "không tìm thấy data/nguon_gold.json"
    danh_muc = json.loads(DANH_MUC_NGUON.read_text(encoding="utf-8"))
    khai_bao = {muc.get("doc_id") for muc in danh_muc.get("tai_lieu", [])}
    co_nhan = {d.stem for d in THU_MUC_GOLD.glob("*.json")}
    thieu = co_nhan - khai_bao
    if thieu:
        return f"{len(thieu)}/{so_file_gold} tài liệu có nhãn nhưng chưa khai trong nguon_gold.json"
    return None


def main() -> int:
    da_chep = sao_luu()
    van_de, thong_ke = kiem_gold()
    canh_bao_danh_muc = kiem_danh_muc(thong_ke["so_file"])

    print("SAO LƯU")
    if da_chep:
        print(f"  {len(da_chep)} file → data/output/sao_luu_tu_dong/")
        for ten in da_chep:
            print(f"    {ten}")
    else:
        print("  không có kết quả lượt trước để chép")

    print("\nTIỀN KIỂM TẬP GOLD")
    print(f"  File gold           : {thong_ke['so_file']}")
    print(f"  Theo chuẩn          : {thong_ke['theo_chuan']}")
    print(f"  Theo quy ước dấu    : {thong_ke['theo_quy_uoc_dau']}")
    print(f"  Có đồng hồ chạy thật: {thong_ke['so_co_dong_ho']}")

    if canh_bao_danh_muc:
        print(f"\nDANH MỤC NGUỒN — {canh_bao_danh_muc}")
        print("  Không chặn lượt chấm; chặn phát hành dataset và tập gán nhãn đôi.")

    if van_de:
        print(f"\nCHƯA CHẠY ĐƯỢC — {len(van_de)} vấn đề:")
        for ten, ly_do in van_de:
            print(f"  {ten}: {ly_do}")
        return 1

    print("\nTẬP GOLD SẴN SÀNG. Lệnh kế tiếp:")
    print("  PYTHONIOENCODING=utf-8 PYTHONPATH=src \\")
    print("      python src/eval/chay_tap_gold.py --chuan-tu-gold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
