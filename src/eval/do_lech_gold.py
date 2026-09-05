"""
Nhãn gold nào KHÔNG CÂN — bảng tra để đối chiếu tay với tờ giấy.

VÌ SAO CÔNG CỤ NÀY TỒN TẠI. Nhãn gold là ĐÁP ÁN. Khi đáp án không thoả đẳng
thức kế toán, mọi phương pháp nhìn tài liệu ấy đều thấy bảng lệch và đi tìm ô
sai — nhưng ô sai nằm ở đáp án chứ không ở chỗ máy đọc. Chúng sẽ "sửa" một con
số vốn đã đúng rồi bị chấm là làm hỏng, và cả H2 lẫn H3 nhận thêm nhiễu ở đúng
chỗ chúng đo. Phát hiện 05/09/2026: 4 trong 70 tài liệu lệch thật, và ba trong
bốn lệch ở CÙNG một đẳng thức — cái nối B03 với B01.

In BIỂU MẪU, MÃ SỐ dòng, giá trị nhãn đang ghi và giá trị đẳng thức đòi, để mở
tờ giấy ra là so được ngay mà không phải tự tính.

Chạy:

    PYTHONIOENCODING=utf-8 PYTHONPATH=src \
        python src/eval/do_lech_gold.py > docs/nhan-gold-khong-can.md
"""

import json
import sys
from pathlib import Path

import numpy as np

# Chạy như script thì thư mục src/eval/ nằm đầu sys.path và eval/metrics.py che
# mất src/metrics.py của pipeline — xem HANDOFF.md mục 5.7.
if __name__ == "__main__":
    _thu_muc_script = str(Path(__file__).resolve().parent)
    sys.path[:] = [p for p in sys.path if Path(p).resolve() != Path(_thu_muc_script)]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from constraints import build_matrix  # noqa: E402
from fields_config import (  # noqa: E402
    QuyUocDau,
    Standard,
    identities_for,
    line_codes_for,
)

THU_MUC_GOLD = Path("data/gold")

# Ngưỡng tách "lệch thật" khỏi "lệch cỡ làm tròn", tính bằng ĐỒNG.
#
# Không phải tham số tinh chỉnh mà là ranh giới giữa hai chế độ lỗi khác hẳn
# nhau: dưới ngưỡng là chính báo cáo in ra đã làm tròn ở vài chữ số cuối, trên
# ngưỡng là có một con số chép sai hoặc một đẳng thức khai thiếu thành phần.
# Số đo 05/09/2026 cho thấy khoảng trống giữa hai nhóm rất rộng — nhóm dưới
# lớn nhất là 1 triệu đồng, nhóm trên nhỏ nhất là 51,7 triệu — nên đặt ngưỡng
# ở đâu trong khoảng đó cũng ra cùng một cách chia.
NGUONG_LAM_TRON = 2_000_000


def main():
    print("# Nhãn gold không cân — bảng tra để kiểm tay\n")
    print("Sinh bởi scratchpad/bao_lech_gold.py. Cột **nhãn** là số đang ghi trong")
    print("`data/gold/`; cột **đẳng thức đòi** là số suy ra từ các dòng còn lại.\n")

    nang, nhe = [], []

    for f in sorted(THU_MUC_GOLD.glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        g = d["values"]
        chuan = Standard(d["standard"])
        ma = line_codes_for(chuan)
        co = [k for k, v in g.items() if v is not None]
        idents = identities_for(chuan, QuyUocDau(d["quy_uoc_dau"]))
        dung = [i for i in idents if all(t in co for t in [*i[0], i[1]])]
        A, order = build_matrix(co, idents)
        if A.shape[0] == 0:
            continue
        x = np.array([g[k] for k in order], float)
        r = A @ x

        for (parts, total, msg), lech in zip(dung, r):
            if abs(lech) < 1:
                continue
            muc = {
                "doc": f.stem,
                "don_vi": d["unit_multiplier"],
                "quy_uoc": d["quy_uoc_dau"],
                "msg": msg,
                "lech": float(lech),
                "parts": [(t, ma.get(t, ("?", "?")), g[t]) for t in parts],
                "total": (total, ma.get(total, ("?", "?")), g[total]),
            }
            (nang if abs(lech) >= NGUONG_LAM_TRON else nhe).append(muc)

    doc_nang = sorted({m["doc"] for m in nang})
    doc_nhe = sorted({m["doc"] for m in nhe})
    tong_doc = len(list(THU_MUC_GOLD.glob("*.json")))

    print("## Tóm tắt")
    print()
    print(f"- Tập gold: **{tong_doc}** tài liệu.")
    print(f"- **{len(doc_nang)}** tài liệu lệch THẬT (từ {NGUONG_LAM_TRON:,} đồng trở lên), "
          f"tổng {len(nang)} chỗ. Đây là phần phải kiểm tay.")
    print(f"- **{len(doc_nhe)}** tài liệu lệch cỡ làm tròn, tổng {len(nhe)} chỗ.")
    print()
    print("Mức lệch cỡ làm tròn nhiều khả năng là chính báo cáo in ra đã làm tròn,")
    print("không phải chép sai. Nhưng chúng vẫn làm phần dư khác 0, nên tầng ràng buộc")
    print("thấy tài liệu \"không cân\" và mọi phương pháp sẽ đi tìm một ô sai không tồn")
    print("tại — vì vậy vẫn phải quyết xử lý thế nào, không bỏ qua được.")
    print()
    print(f"Lệch thật: {', '.join('`' + d + '`' for d in doc_nang)}")
    print()

    for ten, nhom in (("LỆCH THẬT — phải kiểm", nang),
                      ("LỆCH CỠ LÀM TRÒN — nhiều khả năng vô hại", nhe)):
        print(f"\n## {ten} ({len(nhom)} chỗ)\n")
        for m in nhom:
            tong_ten, (tong_bm, tong_ma), tong_gt = m["total"]
            doi = tong_gt - m["lech"]
            print(f"### `{m['doc']}` — lệch {m['lech']:+,.0f} đồng")
            print(f"\n*{m['msg']}*  \n"
                  f"Đơn vị nhân {m['don_vi']}, quy ước dấu `{m['quy_uoc']}`.\n")
            print("| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |")
            print("|---|---|---:|---|---:|")
            for t, (bm, mma), gt in m["parts"]:
                print(f"| thành phần | {bm} | {mma} | `{t}` | {gt:,.0f} |")
            print(f"| **tổng** | **{tong_bm}** | **{tong_ma}** | **`{tong_ten}`** "
                  f"| **{tong_gt:,.0f}** |")
            print(f"\n**Đẳng thức đòi `{tong_ten}` = {doi:,.0f}**, "
                  f"nhãn ghi {tong_gt:,.0f} — lệch {m['lech']:+,.0f}.\n")


if __name__ == "__main__":
    main()
