"""
Vì sao baseline 9 sửa đúng ở lệch dòng/lệch cột — đo, chứ không đoán.

BỐI CẢNH. Lượt chạy Mốc 3 ngày 25/08/2026 cho baseline 9 sửa đúng 26–35% số
lượt `row_shift` và `col_shift`. Hai chế độ đó GHI ĐÈ ô đích bằng giá trị ô
khác nên giá trị thật biến mất khỏi bảng, và baseline 9 chỉ có donor là trung
vị của chính chỉ tiêu đó trên các công ty KHÁC. Một phần ba số lượt trúng là
con số cần giải thích trước khi trích vào bài: một baseline thắng mà không
giải thích được là dấu hiệu thí nghiệm rò rỉ đáp án.

GIẢ THUYẾT ĐẦU TIÊN — ĐÃ BỊ CHÍNH FILE NÀY BÁC. Nghi ngờ ban đầu là các lượt
trúng tập trung vào chỉ tiêu có giá trị thật bằng 0: tu chính 24/08/2026 ghi
dòng vắng mặt là `0` chứ không phải `null`, nên trung vị donor bằng 0 sẽ khớp
mà không cần biết gì. Đo được **0 trên 520 lượt** rơi vào chỉ tiêu có giá trị
thật bằng 0, và donor khớp giá trị thật **0 trên 520 lượt**. Giả thuyết sai
hoàn toàn, và bộ đếm của nó giữ lại trong file này làm bằng chứng đã kiểm.

GIẢ THUYẾT ĐÚNG, VÀ NÓ QUAN TRỌNG HƠN NHIỀU. Baseline 9 không điền thẳng giá
trị donor: nó chọn bộ giá trị GẦN DONOR NHẤT **mà vẫn thoả ràng buộc**, tức
giải một bài tối ưu liên tục. Khi đúng một trường sai và trường đó được thả
ra một mình, ràng buộc TỰ CHỐT giá trị: residual `r = δᵢ·aᵢ` nên nghiệm duy
nhất là `δ = −δᵢ`, bất kể donor ở đâu. Nói cách khác baseline 9 không bịa —
nó NGHỊCH ĐẢO, và với lỗi đơn định vị được thì phép nghịch đảo cho lại đúng
giá trị thật tới từng chữ số.

Dấu vết của cơ chế này nằm sẵn trong bảng Mốc 3: tỷ lệ sửa đúng của baseline
9 gần trùng tỷ lệ định vị đúng ở ba trong bốn chế độ — `sign` 0,400 so với
0,385, `row_shift` 0,346 so với 0,331, `col_shift` 0,262 so với 0,254. Nó sửa
đúng KHI VÀ CHỈ KHI nó định vị đúng. File này kiểm cơ chế trực tiếp bằng đại
số thay vì suy từ hai tỷ lệ trùng nhau.

HỆ QUẢ CHO THIẾT KẾ THÍ NGHIỆM — phần đáng đọc nhất. Tầng XBRL tiêm **đúng
một lỗi mỗi lượt**, mà lỗi đơn định vị được lại chính là ca mà phép nghịch
đảo liên tục giải trọn vẹn. Thiết kế hiện tại vì thế đang chọn đúng ca thuận
lợi nhất cho baseline 9. Khoảng hở mà "đọc lại nguồn" lấp là ca ràng buộc
KHÔNG chốt được giá trị: nhiều lỗi đồng thời, cột bằng 0, cột tỷ lệ với nhau,
và lỗi nằm trong `null(A)`. Đây là số đo, không phải lời bào chữa — và nó
nói lượt chạy tới phải tiêm nhiều hơn một lỗi.

Chạy:
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/do_nghich_dao_mot_loi.py
"""

import sys
from collections import Counter
from pathlib import Path

import numpy as np

# Cùng cái bẫy như moc3.py: chạy như script thì src/eval/ nằm đầu sys.path và
# eval/metrics.py che mất src/metrics.py. Gỡ ra trước khi import.
if __name__ == "__main__":
    _thu_muc_script = str(Path(__file__).resolve().parent)
    sys.path[:] = [p for p in sys.path if Path(p).resolve() != Path(_thu_muc_script)]

from eval.do_phu_ung_vien import bang_nhau  # noqa: E402
from eval.moc3 import (  # noqa: E402
    CAC_SEED,
    CHE_DO_LOI,
    _bang_sach,
    _du_lieu_donor,
    nap_ho_so,
)
from eval.xbrl_tier.inject import inject  # noqa: E402

DUONG_DAN = Path("data/output/moc3_nghich_dao_mot_loi.md")

# Dung sai cho phép so phương của hai vector, tính theo tỷ lệ trên độ lớn.
# Không dùng ngưỡng tuyệt đối vì residual của một tập đoàn cỡ 1e13 còn của
# một công ty nhỏ cỡ 1e8, và một ngưỡng tuyệt đối sẽ hoặc khớp oan mọi thứ
# hoặc bỏ sót mọi thứ tuỳ quy mô doanh nghiệp.
DUNG_SAI_PHUONG = 1e-9


def _rang_buoc_co_chot_gia_tri(A, thu_tu, gia_tri_hong, gia_tri_that, concept) -> str:
    """
    Ràng buộc có tự chốt giá trị thật của MỘT trường sai không.

    Trả về một trong ba trạng thái TƯỜNG MINH, không để suy từ sự vắng mặt:

      `chot_dung`    — residual nằm trọn trên phương cột của trường đó và
                       nghịch đảo cho lại đúng giá trị thật. Đây là ca mà bất
                       kỳ bộ giải liên tục nào cũng lấy lại được đáp án mà
                       không cần đọc lại tài liệu.
      `khong_chot`   — residual không nằm trên phương ấy, hoặc nghịch đảo ra
                       giá trị khác. Ca này mới cần tới việc đọc lại nguồn.
      `cot_bang_khong` — trường không tham gia đẳng thức nào, tức không ràng
                       buộc nào bảo vệ nó. Kết quả của H0, không phải của
                       phương pháp nào cả.
    """
    i = thu_tu.index(concept)
    a_i = A[:, i]
    if not np.any(np.abs(a_i) > DUNG_SAI_PHUONG):
        return "cot_bang_khong"

    x = np.array([gia_tri_hong.get(ten, 0.0) for ten in thu_tu], dtype=float)
    r = A @ x

    # Nghịch đảo từ thành phần lớn nhất của cột: chia cho số bé làm khuếch
    # đại sai số dấu phẩy động.
    k = int(np.argmax(np.abs(a_i)))
    delta = -r[k] / a_i[k]

    # Nghịch đảo chỉ hợp lệ khi residual nằm TRỌN trên phương cột ấy. Bỏ kiểm
    # tra này thì mọi trường đều trông như chốt được, kể cả khi lỗi thật nằm
    # ở chỗ khác.
    thang = max(float(np.max(np.abs(r))), 1.0)
    if float(np.max(np.abs(r + delta * a_i))) / thang > 1e-7:
        return "khong_chot"

    return "chot_dung" if bang_nhau(x[i] + delta, gia_tri_that.get(concept)) else "khong_chot"


def _khung() -> dict:
    """Bộ đếm một nhóm. Mọi khoá có sẵn để bảng đọc được cả khi nhóm rỗng."""
    return {
        "luot": 0,
        "that_bang_khong": 0,
        "donor_khop": 0,
        "chot_dung": 0,
        "khong_chot": 0,
        "cot_bang_khong": 0,
    }


def do(thu_muc: Path | None = None) -> dict:
    """
    Đếm theo chế độ lỗi, dùng đúng danh sách hồ sơ và seed của `moc3.chay()`.

    Nhờ khớp một-một như vậy, tỷ lệ ở đây so thẳng được với bảng Mốc 3 mà
    không phải căn chỉnh mẫu số.
    """
    ho_so = nap_ho_so(thu_muc) if thu_muc else nap_ho_so()

    theo_che_do: dict[str, dict] = {c.value: _khung() for c in CHE_DO_LOI}
    bo_qua: Counter = Counter()

    for accn, equations, companyfacts, cik in ho_so:
        bang, A, thu_tu = _bang_sach(companyfacts, accn, equations)
        if bang is None:
            bo_qua["khong_du_chi_tieu"] += 1
            continue

        ky = bang.cot_chinh()
        gia_tri_that = bang.values_cua_ky(ky)
        donor = _du_lieu_donor(ho_so, thu_tu, cik)

        for che_do in CHE_DO_LOI:
            for seed in CAC_SEED:
                try:
                    hong, ground_truth = inject(bang, che_do, n_errors=1, seed=seed, period=ky)
                except ValueError:
                    bo_qua[f"khong_inject_duoc_{che_do.value}"] += 1
                    continue

                gia_tri_hong = hong.values_cua_ky(ky)
                for e in ground_truth:
                    that = gia_tri_that.get(e.concept)
                    if that is None or e.concept not in thu_tu:
                        bo_qua["truong_hong_ngoai_bang"] += 1
                        continue

                    n = theo_che_do[che_do.value]
                    n["luot"] += 1
                    if that == 0:
                        n["that_bang_khong"] += 1
                    if e.concept in donor and bang_nhau(donor[e.concept], that):
                        n["donor_khop"] += 1
                    n[
                        _rang_buoc_co_chot_gia_tri(
                            A, thu_tu, gia_tri_hong, gia_tri_that, e.concept
                        )
                    ] += 1

        print(f"xong {accn}", file=sys.stderr)

    return {"theo_che_do": theo_che_do, "bo_qua": bo_qua, "n_ho_so": len(ho_so)}


def bao_cao(kq: dict) -> str:
    """Bảng đối chiếu ba lời giải thích cho việc baseline 9 sửa đúng."""
    theo = kq["theo_che_do"]

    def ty_le(x, y):
        return f"{x / y:.3f}" if y else "—"

    dong = [
        "# Ràng buộc tự chốt giá trị, hay donor đoán trúng — phép đo phân xử",
        "",
        f"{kq['n_ho_so']} hồ sơ, cùng danh sách và cùng seed với `moc3.chay()`.",
        "",
        "| Chế độ lỗi | Lượt | Thật bằng 0 | Donor khớp | Ràng buộc CHỐT ĐÚNG "
        "| Không chốt | Cột bằng 0 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for ten in sorted(theo):
        n = theo[ten]
        dong.append(
            f"| `{ten}` | {n['luot']} | {n['that_bang_khong']} | {n['donor_khop']} "
            f"| **{ty_le(n['chot_dung'], n['luot'])}** | "
            f"{ty_le(n['khong_chot'], n['luot'])} | "
            f"{ty_le(n['cot_bang_khong'], n['luot'])} |"
        )

    dong += [
        "",
        "**Đọc bảng này thế nào.** Cột *Ràng buộc CHỐT ĐÚNG* là tỷ lệ lượt mà",
        "residual nằm trọn trên phương cột của trường bị lỗi, nên nghịch đảo cho",
        "lại đúng giá trị thật tới từng chữ số. Ở những lượt đó, MỌI bộ giải liên",
        "tục lấy lại được đáp án mà không cần đọc lại tài liệu — trần trên của cái",
        "mà baseline 9 có thể đạt, và cũng là phần mà việc đọc lại nguồn không",
        "đóng góp gì thêm.",
        "",
        "Hai cột *Thật bằng 0* và *Donor khớp* là giả thuyết ĐẦU TIÊN, đã bị chính",
        "phép đo này bác. Giữ lại trong bảng để lần sau không ai đi kiểm lại.",
        "",
        "**Hệ quả cho lượt chạy tới.** Tầng XBRL tiêm đúng một lỗi mỗi lượt, mà",
        "lỗi đơn định vị được chính là ca phép nghịch đảo giải trọn. Muốn đo đúng",
        "phần mà việc đọc lại nguồn đóng góp thì phải tiêm NHIỀU HƠN MỘT lỗi, nơi",
        "hệ trở nên dưới xác định và ràng buộc thôi chốt được giá trị.",
    ]

    if kq["bo_qua"]:
        dong += ["", "Bỏ qua (ghi tường minh, không giấu):", ""]
        for k, v in sorted(kq["bo_qua"].items()):
            dong.append(f"- `{k}`: {v}")

    return "\n".join(dong) + "\n"


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ket = bao_cao(do())
    DUONG_DAN.parent.mkdir(parents=True, exist_ok=True)
    DUONG_DAN.write_text(ket, encoding="utf-8")
    print(ket)
