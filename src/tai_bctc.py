"""
Tải báo cáo tài chính của tập gold từ danh mục nguồn.

VÌ SAO PHẢI CÓ SCRIPT NÀY, chứ không phải một thư mục PDF đem chia sẻ. Bản
PDF của báo cáo niêm yết vẫn có bản quyền trình bày, nên phương án phát hành
an toàn — thứ mà `src/eval/schema.py` đã chốt và là lý do `source_url` với
`downloaded_at` là trường bắt buộc — là phát hành **nhãn kèm URL nguồn và
script tải**, không phát hành file gốc. Không có script này thì `data/gold/`
không tái lập được trên máy người khác, và dataset mất một trong bốn kết quả
dự kiến của cả nghiên cứu.

Danh mục nguồn là `data/nguon_gold.json`. Nó VÀO git (chỉ có URL và siêu dữ
liệu, không có con số tài chính nào), còn PDF tải về thì không.

Chạy:
    python src/tai_bctc.py                      # tải hết vào data/bctc/
    python src/tai_bctc.py --thu-muc D:\\bctc    # chỗ khác
    python src/tai_bctc.py --chi VNM TTF        # chỉ vài mã

Rồi trỏ công cụ gán nhãn vào đúng thư mục đó:
    python chay_gan_nhan.py --pdf-dir data/bctc
"""

import argparse
import json
import sys
import time
from pathlib import Path

import requests

# Ép stdout/stderr về UTF-8. Máy Windows này chạy bảng mã cp1252, và cp1252
# KHÔNG có chữ "đ" — nên mọi dòng tiếng Việt in ra sẽ ném UnicodeEncodeError
# ngay khi output bị chuyển hướng vào file hay nối vào một lệnh khác. Chạy
# thẳng trong cửa sổ lệnh thì không lộ, vì lúc đó Python ghi bằng Unicode.
# Bẫy này đã bắt được ở lần chạy thử đầu tiên, đúng lúc nối vào `tail`.
for _luong in (sys.stdout, sys.stderr):
    if hasattr(_luong, "reconfigure"):
        _luong.reconfigure(encoding="utf-8", errors="replace")

DANH_MUC = Path("data/nguon_gold.json")
THU_MUC_MAC_DINH = Path("data/bctc")

# Máy chủ Vietstock từ chối yêu cầu không có User-Agent trình duyệt.
DAU = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def doc_danh_muc(duong_dan: Path = DANH_MUC) -> list[dict]:
    if not duong_dan.is_file():
        raise SystemExit(f"Không có danh mục nguồn {duong_dan}")
    return json.loads(duong_dan.read_text(encoding="utf-8"))["tai_lieu"]


def tai_mot(muc: dict, thu_muc: Path, ghi_de: bool = False) -> tuple[bool, str]:
    """
    Tải một tài liệu. Trả về (thành công, lý do).

    Kiểm `%PDF` ở đầu nội dung chứ không tin mã 200: khi tài liệu bị gỡ,
    Vietstock trả về trang lỗi HTML kèm mã 200, và một file HTML mang đuôi
    `.pdf` sẽ làm công cụ gán nhãn nổ ở chỗ khác hẳn nguyên nhân thật.
    """
    dich = thu_muc / f"{muc['doc_id']}.pdf"
    if dich.is_file() and dich.stat().st_size > 50_000 and not ghi_de:
        return True, "đã có"

    try:
        r = requests.get(muc["source_url"], headers=DAU, timeout=180)
    except requests.RequestException as e:
        return False, f"lỗi mạng: {e}"

    if r.status_code != 200:
        return False, f"HTTP {r.status_code}"
    if not r.content.startswith(b"%PDF"):
        return False, f"không phải PDF ({len(r.content)} byte, có thể tài liệu đã bị gỡ)"

    dich.parent.mkdir(parents=True, exist_ok=True)
    dich.write_bytes(r.content)
    return True, f"{len(r.content) / 1e6:.1f} MB"


def main() -> int:
    ps = argparse.ArgumentParser(description=__doc__)
    ps.add_argument("--thu-muc", default=str(THU_MUC_MAC_DINH))
    ps.add_argument("--danh-muc", default=str(DANH_MUC))
    ps.add_argument("--chi", nargs="*", default=None, help="chỉ tải các mã này")
    ps.add_argument("--ghi-de", action="store_true")
    ts = ps.parse_args()

    thu_muc = Path(ts.thu_muc)
    muc_ds = doc_danh_muc(Path(ts.danh_muc))
    if ts.chi:
        can = {m.upper() for m in ts.chi}
        muc_ds = [m for m in muc_ds if m["ticker"].upper() in can]

    hong = []
    for i, muc in enumerate(muc_ds, 1):
        ok, ly_do = tai_mot(muc, thu_muc, ts.ghi_de)
        print(f"[{i:2d}/{len(muc_ds)}] {muc['doc_id']:24s} {'✓' if ok else '✗'} {ly_do}")
        if not ok:
            hong.append((muc["doc_id"], ly_do))
        # Nghỉ giữa các lần tải: đây là máy chủ của người khác, và cả tập
        # gold chỉ tải một lần nên vài giây không đáng gì.
        if ok and ly_do != "đã có":
            time.sleep(1.0)

    print(f"\n{len(muc_ds) - len(hong)}/{len(muc_ds)} tài liệu đã có trong {thu_muc}")
    if hong:
        # In riêng thay vì chỉ đếm: tài liệu bị gỡ khỏi nguồn là chuyện có
        # thật, và người dùng cần biết ĐÚNG cái nào để đi tìm bản thay thế.
        print("\nCHƯA TẢI ĐƯỢC — cần tìm nguồn thay thế:")
        for doc_id, ly_do in hong:
            print(f"  {doc_id}: {ly_do}")
    return 1 if hong else 0


if __name__ == "__main__":
    sys.exit(main())
