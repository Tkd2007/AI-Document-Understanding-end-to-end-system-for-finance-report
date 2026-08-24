"""
MỐC 3 — chạy baseline 9 đối đầu với phương pháp đề xuất.

Đây là mốc PHẢI DỪNG của `PREREGISTRATION.md` mục 4:

    Nếu baseline 9 ngang bằng phương pháp đề xuất thì dừng, báo cáo, và lùi
    paper về tầng dataset + identifiability.

Baseline 9 (`diagnose_fellegi_holt_donor`) giống `diagnose()` ở MỌI thứ trừ
đúng một biến: giá trị điền vào đến từ phân phối của chính chỉ tiêu đó trên
các tài liệu KHÁC, thay vì đến từ chính tài liệu đang xét. Nên hiệu số giữa
hai bên đo đúng một thứ — việc đọc lại nguồn có đáng gì không.

HAI CHỈ SỐ PHẢI BÁO CÁO CÙNG LÚC, đã đăng ký trước:

  1. Tỷ lệ lỗi câm giảm bao nhiêu.
  2. Chỉ số chống bịa có TĂNG không.

Thắng chiều một mà thua chiều hai là KẾT QUẢ TIÊU CỰC và phải nói ra. Một hệ
ép số cho khớp phương trình sẽ thắng tuyệt đối ở chiều một.

Đếm riêng `vo_nghiem` với `vuot_tran_thay_doi`: chỉ ca đầu mới chứng minh
được luận điểm chống bịa, tức "không cách đọc nào của tài liệu này làm bảng
cân đối được". Ca sau chỉ nói ta đã hết ngân sách tìm.

Chạy:

    PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/moc3.py
"""

import sys
from collections import Counter
from pathlib import Path

import numpy as np

# Chạy như script thì thư mục src/eval/ nằm đầu sys.path và eval/metrics.py
# che mất src/metrics.py của pipeline. Cùng họ với vụ src/types.py — xem
# HANDOFF.md mục 9. Gỡ thư mục script ra trước khi import bất cứ thứ gì.
if __name__ == "__main__":
    _thu_muc_script = str(Path(__file__).resolve().parent)
    sys.path[:] = [p for p in sys.path if Path(p).resolve() != Path(_thu_muc_script)]

from eval.metrics import fabrication_rate, silent_error_rate  # noqa: E402
from eval.xbrl_tier.facts import build_table  # noqa: E402
from eval.xbrl_tier.inject import ErrorType, inject  # noqa: E402
from eval.xbrl_tier.linkbase import (  # noqa: E402
    concepts_xuat_hien,
    parse_calculation_linkbase,
    to_matrix,
)
from repair.candidates import generate  # noqa: E402
from repair.diagnose import diagnose, diagnose_fellegi_holt_donor  # noqa: E402

THU_MUC_XBRL = Path("data/xbrl")

# Bốn chế độ lỗi đem ra đo. SCALE cố ý bị loại: hệ ràng buộc thuần nhất nên
# sai đơn vị TOÀN CỤC luôn vô hình với mọi đẳng thức — đó là mệnh đề đã
# chứng minh ở H0, không phải thứ cần đo lại bằng thực nghiệm ở đây.
CHE_DO_LOI = [ErrorType.DIGIT_SUB, ErrorType.ROW_SHIFT, ErrorType.COL_SHIFT, ErrorType.SIGN]

# Nhiều seed vì bảng kết quả phải chịu được phương sai của bước inject —
# ADDENDUM mục 5 liệt kê đây là một trong bốn nguồn phương sai.
CAC_SEED = [0, 1, 2, 3, 4]


def nap_ho_so(thu_muc: Path = THU_MUC_XBRL) -> list[tuple[str, list, dict, str]]:
    """
    Đọc mọi companyfacts và calculation linkbase đã tải về.

    Trả về [(accn, equations, companyfacts, cik)] — MỖI hồ sơ mang theo
    companyfacts của đúng công ty nó.

    VÌ SAO PHẢI GẮN COMPANYFACTS THEO TỪNG HỒ SƠ: bản trước đọc đúng một
    file facts rồi dùng chung cho mọi linkbase. Với một công ty thì vô hại,
    nhưng Mốc 3 chỉ kết luận được khi có NHIỀU công ty — donor của
    Fellegi-Holt phải đến từ một tổng thể nhiều thực thể. Dùng chung một
    file facts cho hồ sơ của công ty khác thì `_chon_fact()` không tìm thấy
    accn nào khớp và bảng ra rỗng, tức mọi hồ sơ ngoài công ty đầu tiên bị
    bỏ IM LẶNG — mà số hồ sơ chạy được đúng là thứ quyết định phép so có
    nghĩa hay không.

    Ném lỗi khi thư mục trống, vì "chạy xong không có kết quả nào" và "chưa
    tải dữ liệu" là hai chuyện khác hẳn nhau mà bảng rỗng không phân biệt.
    """
    import json

    cac_facts = sorted(thu_muc.glob("*_facts.json"))
    if not cac_facts:
        raise SystemExit(
            f"Không có file *_facts.json trong {thu_muc}. Chạy fetch.py trước:\n"
            f"  SEC_USER_AGENT='Tên thật email@example.com' "
            f"python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --out data/xbrl"
        )

    # accn -> cik, dựng bằng cách hỏi chính companyfacts xem nó chứa những
    # hồ sơ nào. Ghép theo tên file sẽ hỏng ngay khi quy ước đặt tên đổi,
    # còn accn thì nằm trong chính dữ liệu.
    facts_theo_cik: dict[str, dict] = {}
    accn_ve_cik: dict[str, str] = {}
    for f in cac_facts:
        cf = json.loads(f.read_text(encoding="utf-8"))
        cik = str(cf.get("cik", f.stem))
        facts_theo_cik[cik] = cf
        for nhom in cf.get("facts", {}).values():
            for concept in nhom.values():
                for danh_sach in concept.get("units", {}).values():
                    for fact in danh_sach:
                        if fact.get("accn"):
                            accn_ve_cik[fact["accn"]] = cik

    ho_so = []
    for cal in sorted(thu_muc.glob("*_cal.xml")):
        accn = cal.name.replace("_cal.xml", "")
        cik = accn_ve_cik.get(accn)
        if cik is None:
            continue
        equations = parse_calculation_linkbase(cal.read_text(encoding="utf-8"))
        ho_so.append((accn, equations, facts_theo_cik[cik], cik))

    return ho_so


# Bảng đã dựng, nhớ theo accn.
#
# `_du_lieu_donor()` cần bảng của MỌI hồ sơ khác để lấy trung vị, nên nếu
# không nhớ thì với n hồ sơ ta dựng n×(n−1) lần — 650 lần với 26 hồ sơ, mỗi
# lần duyệt một companyfacts vài MB. Bảng chỉ phụ thuộc (accn, equations)
# nên nhớ lại là an toàn tuyệt đối, không đổi một con số nào của kết quả.
_NHO_BANG: dict = {}


def _bang_sach(companyfacts: dict, accn: str, equations: list):
    """
    Bảng chỉ giữ những chỉ tiêu ĐỦ giá trị ở kỳ chính, kèm ma trận của nó.

    Lọc chỉ tiêu thiếu giá trị chứ không điền 0: `to_matrix` bỏ đẳng thức
    nào có concept ngoài danh sách, đúng như A2 làm, vì coi chỉ tiêu không
    trích được là 0 sẽ làm hạng ma trận cao lên giả tạo.
    """
    if accn in _NHO_BANG:
        return _NHO_BANG[accn]

    concepts = concepts_xuat_hien(equations)
    bang = build_table(companyfacts, concepts, accn, n_periods=2)

    ky = bang.cot_chinh()
    du = [c for c in bang.concepts if bang.get(c, ky) is not None]
    if len(du) < 2:
        _NHO_BANG[accn] = (None, None, None)
        return _NHO_BANG[accn]

    bang = build_table(companyfacts, du, accn, periods=bang.periods)
    A, thu_tu = to_matrix(equations, du)
    if A.size == 0 or A.shape[0] == 0:
        _NHO_BANG[accn] = (None, None, None)
        return _NHO_BANG[accn]

    _NHO_BANG[accn] = (bang, A, thu_tu)
    return _NHO_BANG[accn]


def _du_lieu_donor(ho_so: list, thu_tu: list, cik_dang_xet: str) -> dict:
    """
    Giá trị donor: trung vị của chính chỉ tiêu đó trên các CÔNG TY KHÁC.

    Đây là phần làm baseline 9 trung thực. Fellegi-Holt kinh điển điền từ
    bản ghi donor, nên donor phải là dữ liệu thật của cùng chỉ tiêu ở tài
    liệu khác — không phải số ngẫu nhiên, vốn sẽ làm baseline thua oan và
    biến cả thí nghiệm thành vô giá trị.

    PHẢI LOẠI CẢ CÔNG TY ĐANG XÉT, không chỉ hồ sơ đang xét. Hai bản trước
    đều sai ở đây và mỗi lần sai đều làm lợi cho baseline 9:

      - Bản 1 gộp cả hồ sơ đang xét, nên donor CHỨA chính giá trị thật —
        đo được 32% chỉ tiêu trùng khít, 36% lệch dưới 1%. Baseline khi đó
        là oracle được đưa sẵn đáp án.
      - Bản 2 chỉ loại hồ sơ đang xét nhưng vẫn lấy từ báo cáo năm liền kề
        của CHÍNH công ty đó. Tổng tài sản của một công ty lệch vài phần
        trăm giữa hai năm, nên donor vẫn gần đáp án hơn hẳn thực tế.

    Fellegi-Holt thật lấy donor từ một TỔNG THỂ nhiều thực thể, nơi giá trị
    donor chẳng liên quan gì tới giá trị thật của bản ghi đang sửa. Chỉ khi
    donor được lấy như vậy thì hiệu số giữa hai phương pháp mới đo đúng cái
    cần đo: việc đọc lại nguồn có đáng gì không.
    """
    gom: dict[str, list[float]] = {ten: [] for ten in thu_tu}
    for accn, equations, cf, cik in ho_so:
        if cik == cik_dang_xet:
            continue
        bang, _, _ = _bang_sach(cf, accn, equations)
        if bang is None:
            continue
        for ten in thu_tu:
            v = bang.get(ten, bang.cot_chinh())
            if v is not None:
                gom[ten].append(v)

    return {ten: float(np.median(vs)) for ten, vs in gom.items() if vs}


def _o_lan_can(bang, concept: str, ky: str) -> list[tuple[float, tuple]]:
    """
    Các ô số ĐỌC LẠI ĐƯỢC quanh một chỉ tiêu, đúng thứ bước đọc lại nhìn thấy.

    Gồm hai nhóm, tương ứng hai chế độ lỗi mà chúng cứu được:
      - giá trị của DÒNG TRÊN và DÒNG DƯỚI ở cùng kỳ  -> cứu ROW_SHIFT
      - giá trị của CHÍNH dòng đó ở các kỳ khác        -> cứu COL_SHIFT

    KHÔNG ĐƯỢC BỎ NGUỒN NÀY KHI ĐO. `candidates.tu_o_lan_can()` tự mô tả nó
    là "nguồn GIÁ TRỊ NHẤT" và là "thứ KHÔNG PARADIGM NÀO trước đây có" —
    Fellegi-Holt điền từ bản ghi donor, data reconciliation hiệu chỉnh liên
    tục, HoloClean tra từ điển ngoài; không cái nào lấy ứng viên từ chính
    trang giấy. Chạy Mốc 3 mà tắt nguồn này là đem so baseline 9 với một
    phiên bản đã bị gỡ mất đúng cơ chế đang cần chứng minh, và con số thu
    được không nói lên điều gì về luận điểm.

    bbox để None vì tầng XBRL không có ảnh — ứng viên ở đây truy về Ô NÀO
    chứ không truy về toạ độ. Ở pipeline thật thì bbox có sẵn từ B3.
    """
    ra = []
    for hang_xom in bang.hang_xom_doc(concept):
        v = bang.get(hang_xom, ky)
        if v is not None:
            ra.append((v, None))

    for ky_khac in bang.periods:
        if ky_khac == ky:
            continue
        v = bang.get(concept, ky_khac)
        if v is not None:
            ra.append((v, None))

    return ra


def _ung_vien_cho_bang(bang, gia_tri: dict, ky: str) -> dict:
    """Tập ứng viên của từng chỉ tiêu, KÈM các ô lân cận đọc lại được."""
    return {
        ten: generate(ten, v, o_lan_can=_o_lan_can(bang, ten, ky))
        for ten, v in gia_tri.items()
        if v is not None
    }


def _do_mot_luot(gia_tri_hong, gia_tri_that, ung_vien, A, thu_tu, donor):
    """Chạy cả hai phương pháp trên CÙNG một bộ số, cùng ngân sách."""
    ket = {}
    for ten, ham, kwargs in (
        ("de_xuat", diagnose, {}),
        ("baseline9", diagnose_fellegi_holt_donor, {"donor_values": donor}),
    ):
        kq = ham(gia_tri_hong, ung_vien, A, thu_tu, **kwargs)
        sau_sua = kq.gia_tri_sau_sua(gia_tri_hong)
        ket[ten] = {
            "verdict": kq.verdict,
            "ma_ly_do": kq.ma_ly_do,
            "n_changed": kq.n_changed,
            "sua_dung_truong": set(kq.changed_fields) if kq.changed_fields else set(),
            "cau": silent_error_rate(sau_sua, gia_tri_that),
            "bia": fabrication_rate(sau_sua, gia_tri_that, A, thu_tu),
        }
    return ket


def chay(thu_muc: Path = THU_MUC_XBRL) -> dict:
    """Chạy toàn bộ Mốc 3 và trả về số liệu thô để in bảng."""
    ho_so = nap_ho_so(thu_muc)

    tong: dict = {
        p: {
            "verdict": Counter(),
            "ly_do": Counter(),
            "dinh_vi_dung": 0,
            "cau_sai": 0,
            "cau_mau": 0,
            "bia_sai": 0,
            "bia_mau": 0,
            "thoa_rang_buoc": 0,
        }
        for p in ("de_xuat", "baseline9")
    }
    n_luot = 0
    bo_qua: Counter = Counter()

    cik_da_gap = set()

    for accn, equations, companyfacts, cik in ho_so:
        bang, A, thu_tu = _bang_sach(companyfacts, accn, equations)
        if bang is None:
            bo_qua["khong_du_chi_tieu"] += 1
            continue

        cik_da_gap.add(cik)
        print(
            f"[{len(cik_da_gap):>2}] {cik} {accn} — {len(thu_tu)} chỉ tiêu, "
            f"{A.shape[0]} đẳng thức",
            file=sys.stderr,
        )
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
                truong_hong = {e.concept for e in ground_truth}
                ung_vien = _ung_vien_cho_bang(hong, gia_tri_hong, ky)

                ket = _do_mot_luot(gia_tri_hong, gia_tri_that, ung_vien, A, thu_tu, donor)
                n_luot += 1

                for p, r in ket.items():
                    t = tong[p]
                    t["verdict"][r["verdict"]] += 1
                    if r["ma_ly_do"]:
                        t["ly_do"][r["ma_ly_do"]] += 1
                    if r["sua_dung_truong"] == truong_hong:
                        t["dinh_vi_dung"] += 1
                    t["cau_sai"] += r["cau"]["sai"]
                    t["cau_mau"] += r["cau"]["co_gia_tri"]
                    if r["bia"]["thoa_rang_buoc"]:
                        t["thoa_rang_buoc"] += 1
                        t["bia_sai"] += r["bia"]["bia"]
                        t["bia_mau"] += r["bia"]["co_gia_tri"]

    return {
        "tong": tong,
        "n_luot": n_luot,
        "bo_qua": bo_qua,
        "n_ho_so": len(ho_so),
        "n_cong_ty": len(cik_da_gap),
    }


def _ai_thang(d: dict, b: dict, khoa: str) -> str:
    """Ai hơn ở một chỉ số càng-cao-càng-tốt. Hoà thì nói HOÀ, không làm tròn."""
    if d[khoa] == b[khoa]:
        return "**HOÀ**"
    return "đề xuất" if d[khoa] > b[khoa] else "**baseline 9**"


def bao_cao(kq: dict) -> str:
    """Bảng kết quả Mốc 3, viết để dán thẳng vào bàn giao."""
    t, n = kq["tong"], kq["n_luot"]
    if n == 0:
        return "KHÔNG CÓ LƯỢT NÀO CHẠY ĐƯỢC — xem mục bỏ qua.\n"

    d, b = t["de_xuat"], t["baseline9"]

    def ty_le(x, y):
        return f"{x / y:.3f}" if y else "—"

    dong = [
        f"MỐC 3 — {kq['n_cong_ty']} công ty, {kq['n_ho_so']} hồ sơ, {n} lượt chạy "
        f"({len(CHE_DO_LOI)} chế độ lỗi × {len(CAC_SEED)} seed)",
        "",
        "| Chỉ số | Đề xuất | Baseline 9 | Ai thắng |",
        "|---|---:|---:|---|",
    ]

    for nhan, khoa_sai, khoa_mau, thap_hon_tot in (
        ("Tỷ lệ lỗi câm sau sửa", "cau_sai", "cau_mau", True),
        ("Tỷ lệ bịa (thoả ràng buộc mà sai)", "bia_sai", "bia_mau", True),
    ):
        vd = d[khoa_sai] / d[khoa_mau] if d[khoa_mau] else 0.0
        vb = b[khoa_sai] / b[khoa_mau] if b[khoa_mau] else 0.0
        if abs(vd - vb) < 1e-9:
            ai = "**HOÀ**"
        elif (vd < vb) == thap_hon_tot:
            ai = "đề xuất"
        else:
            ai = "**baseline 9**"
        dong.append(f"| {nhan} | {vd:.3f} | {vb:.3f} | {ai} |")

    dong += [
        f"| Định vị đúng trường bị lỗi | {ty_le(d['dinh_vi_dung'], n)} "
        f"| {ty_le(b['dinh_vi_dung'], n)} | {_ai_thang(d, b, 'dinh_vi_dung')} |",
        f"| Số lượt kết quả thoả ràng buộc | {d['thoa_rang_buoc']} | {b['thoa_rang_buoc']} | — |",
        "",
        "Phân bố verdict:",
        "",
        "| Verdict | Đề xuất | Baseline 9 |",
        "|---|---:|---:|",
    ]
    for v in ("VERIFIED", "REPAIRED", "ABSTAIN"):
        dong.append(f"| {v} | {d['verdict'][v]} | {b['verdict'][v]} |")

    dong += ["", "Lý do ABSTAIN — `vo_nghiem` là ca DUY NHẤT chứng minh được", "",
             "| Lý do | Đề xuất | Baseline 9 |", "|---|---:|---:|"]
    for ly_do in sorted(set(d["ly_do"]) | set(b["ly_do"])):
        dong.append(f"| `{ly_do}` | {d['ly_do'][ly_do]} | {b['ly_do'][ly_do]} |")

    dong += [
        "",
        "> **KẾT QUẢ NÀY CHƯA KẾT LUẬN ĐƯỢC MỐC 3.** Ba hạn chế đã biết, đều làm",
        "> lợi cho baseline 9 hoặc làm hẹp phạm vi đo:",
        ">",
        "> 1. **Chỉ tổng thể donor là hợp lệ, phần còn lại thì chưa.** Donor nay",
        ">    lấy từ các công ty KHÁC nên phần này đã đúng; nhưng toàn bộ dữ liệu",
        ">    vẫn là doanh nghiệp Mỹ nộp theo US-GAAP, chưa có báo cáo Việt Nam nào.",
        "> 2. **Cột kỳ so sánh rỗng**, nên COL_SHIFT không inject được và nguồn",
        ">    ứng viên chéo kỳ không đóng góp gì. Chỉ 3 trong 4 chế độ lỗi chạy.",
        "> 3. **Chỉ số định vị phạt việc ABSTAIN.** Baseline 9 không bao giờ từ",
        ">    chối trả lời nên luôn có cơ hội định vị đúng, còn phương pháp đề",
        ">    xuất từ chối khi tập ứng viên đóng không chứa cách đọc nào hợp lệ —",
        ">    mà đó chính là hành vi nó được thiết kế để có. Đếm ABSTAIN là",
        ">    'định vị trượt' tức đo mức sẵn sàng đoán, không đo độ đúng.",
        "",
    ]

    if kq["bo_qua"]:
        dong += ["", "Bỏ qua (ghi tường minh, không giấu):", ""]
        for k, v in sorted(kq["bo_qua"].items()):
            dong.append(f"- `{k}`: {v}")

    return "\n".join(dong) + "\n"


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print(bao_cao(chay()))
