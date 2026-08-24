"""
Đo ĐỘ PHỦ ỨNG VIÊN của tầng XBRL — phép đo phải chạy TRƯỚC khi đọc Mốc 3.

Câu hỏi: khi tiêm đúng 1 lỗi, giá trị THẬT của ô bị hỏng có nằm trong tập
ứng viên sinh ra từ tài liệu không?

VÌ SAO PHÉP ĐO NÀY BẮT BUỘC: `diagnose()` chỉ sửa được bằng ứng viên lấy từ
chính tài liệu, nên khi tập ứng viên không chứa giá trị thật thì nó BUỘC
phải bỏ phiếu trắng. Lượt ABSTAIN đó không nói gì về phương pháp — nó nói
tầng XBRL không chứa thông tin để đọc lại. Đọc bảng Mốc 3 mà chưa có con số
này là kết luận sai chắc chắn: lần chạy 26 hồ sơ cho độ phủ 0.343, tức hai
phần ba số lượt vốn không thể sửa được bởi bất kỳ phương pháp đọc-lại nào.

Kết quả lần chạy 24/08/2026 nằm ở `data/output/moc3_do_phu_ung_vien.md`, và
HANDOFF.md mục 13b diễn giải kèm cạm bẫy đi theo.

TÁCH "generator thiếu" KHỎI "bị trần cắt": đếm cả trước lẫn sau
`_khu_trung_va_cat()`, vì hai nguyên nhân này cần hai cách sửa khác hẳn
nhau — một bên là bổ sung nguồn ứng viên, một bên là nới `MAX_UNG_VIEN`.
Gộp chúng lại sẽ dẫn tới nới trần trong khi lỗi nằm ở chỗ khác.

Chạy:
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/do_phu_ung_vien.py
"""

import sys
from collections import Counter
from pathlib import Path

# Cùng cái bẫy như moc3.py: chạy như script thì src/eval/ nằm đầu sys.path và
# eval/metrics.py che mất src/metrics.py. Gỡ ra trước khi import.
if __name__ == "__main__":
    _thu_muc_script = str(Path(__file__).resolve().parent)
    sys.path[:] = [p for p in sys.path if Path(p).resolve() != Path(_thu_muc_script)]

from eval.moc3 import (  # noqa: E402
    CAC_SEED,
    CHE_DO_LOI,
    _bang_sach,
    _o_lan_can,
    _ung_vien_cho_bang,
    nap_ho_so,
)
from eval.xbrl_tier.inject import inject  # noqa: E402
from repair.candidates import tu_dau, tu_nham_chu_so, tu_o_lan_can, tu_scale  # noqa: E402

# So khớp theo TỶ LỆ chứ không tuyệt đối: giá trị XBRL cỡ 1e13 nên sai số dấu
# phẩy động tuyệt đối cũng cỡ lớn, và một ngưỡng tuyệt đối sẽ hoặc bỏ sót mọi
# thứ hoặc khớp oan mọi thứ tuỳ quy mô doanh nghiệp.
DUNG_SAI = 1e-9


def bang_nhau(a, b) -> bool:
    """Hai giá trị coi như một, theo dung sai tỷ lệ."""
    if a is None or b is None:
        return False
    if a == b:
        return True
    thang = max(abs(a), abs(b), 1.0)
    return abs(a - b) / thang < DUNG_SAI


def chay() -> tuple[Counter, dict]:
    """Duyệt mọi hồ sơ × chế độ lỗi × seed, đếm độ phủ."""
    ho_so = nap_ho_so()
    tong: Counter = Counter()
    theo_che_do: dict[str, Counter] = {}

    for accn, _equations, companyfacts, _cik in ho_so:
        bang, _A, _thu_tu = _bang_sach(companyfacts, accn, _equations)
        if bang is None:
            continue
        ky = bang.cot_chinh()

        for che_do in CHE_DO_LOI:
            m = theo_che_do.setdefault(che_do.value, Counter())

            for seed in CAC_SEED:
                try:
                    hong, ground_truth = inject(bang, che_do, n_errors=1, seed=seed, period=ky)
                except ValueError:
                    continue

                gia_tri_hong = hong.values_cua_ky(ky)
                ung_vien = _ung_vien_cho_bang(hong, gia_tri_hong, ky)

                for e in ground_truth:
                    that = e.original
                    hien_tai = gia_tri_hong.get(e.concept)
                    tong["luot"] += 1
                    m["luot"] += 1

                    # SAU khi khử trùng và cắt trần — đúng cái diagnose() thấy.
                    co_sau = any(
                        bang_nhau(uv.value, that) for uv in ung_vien.get(e.concept, [])
                    )

                    # TRƯỚC khi cắt: gọi thẳng từng nguồn, để biết nguồn nào
                    # đáng lẽ đã cứu được lượt này.
                    nguon = {
                        "nham_chu_so": tu_nham_chu_so(hien_tai),
                        "o_lan_can": tu_o_lan_can(_o_lan_can(hong, e.concept, ky)),
                        "dau": tu_dau(hien_tai),
                        "scale": tu_scale(hien_tai),
                    }
                    trung = [
                        ten
                        for ten, ds in nguon.items()
                        if any(bang_nhau(uv.value, that) for uv in ds)
                    ]

                    tong["phu_sau"] += co_sau
                    tong["phu_truoc"] += bool(trung)
                    m["phu_sau"] += co_sau
                    m["phu_truoc"] += bool(trung)
                    if trung and not co_sau:
                        tong["bi_tran_cat"] += 1
                        m["bi_tran_cat"] += 1
                    for ten in trung:
                        tong[f"nguon_{ten}"] += 1

    return tong, theo_che_do


def bao_cao(tong: Counter, theo_che_do: dict) -> str:
    """Bảng kết quả, viết để dán thẳng vào bàn giao."""

    def ty(x, y):
        return f"{x / y:.3f}" if y else "—"

    dong = [
        "",
        f"ĐỘ PHỦ ỨNG VIÊN — {tong['luot']} lượt inject 1 lỗi",
        "",
        "| Chế độ lỗi | Lượt | Phủ trước trần | Phủ sau trần | Bị trần cắt |",
        "|---|---:|---:|---:|---:|",
    ]
    for ten, m in sorted(theo_che_do.items()):
        dong.append(
            f"| `{ten}` | {m['luot']} | {ty(m['phu_truoc'], m['luot'])} "
            f"| {ty(m['phu_sau'], m['luot'])} | {m['bi_tran_cat']} |"
        )
    dong += [
        f"| **TỔNG** | {tong['luot']} | {ty(tong['phu_truoc'], tong['luot'])} "
        f"| {ty(tong['phu_sau'], tong['luot'])} | {tong['bi_tran_cat']} |",
        "",
        "Nguồn nào sinh ra được giá trị thật (đếm trước trần, có thể trùng):",
        "",
        "| Nguồn | Số lượt |",
        "|---|---:|",
    ]
    for ten in ("nham_chu_so", "o_lan_can", "dau", "scale"):
        dong.append(f"| `{ten}` | {tong[f'nguon_{ten}']} |")

    return "\n".join(dong) + "\n"


if __name__ == "__main__":
    print(bao_cao(*chay()))
