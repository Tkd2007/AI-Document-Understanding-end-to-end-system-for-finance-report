"""
Định vị lỗi: tìm tổ hợp sửa NHỎ NHẤT làm residual về 0.

Đây là Fellegi-Holt với tập ứng viên đến từ ẢNH thay vì từ donor. Bài toán
trong thuật ngữ gốc gọi là Minimum Weighted Fields to Impute và đã được
chứng minh NP-hard, nên phần lớn module này là chuyện kiểm soát chi phí
tìm kiếm.

VÔ NGHIỆM LÀ CÂU TRẢ LỜI ĐÚNG, không phải lỗi phần mềm cần bắt exception.
Nó nghĩa là: không tổ hợp cách-đọc-khác nào của tài liệu này làm bảng cân
đối được. Đó chính là cơ chế chống bịa số — không gian sửa không chứa số
bịa, nên hệ không thể bịa.

CÁCH GIẢI: tìm kiếm tăng dần theo cardinality thay vì gọi bộ giải MILP.
Quyết định này có chủ đích và có số liệu đỡ lưng:

  * Với 25 trường và tối đa 12 ứng viên mỗi trường, k=1 là khoảng 300 tổ
    hợp và k=2 là khoảng 43 nghìn — cả hai đều tức thì. Nghiệm thực tế gần
    như luôn là 1-2 trường, vì một tài liệu có ba trường cùng sai thì vấn
    đề nằm ở khâu trích xuất chứ không phải khâu sửa.
  * Không thêm bộ giải MILP kèm binary vào image: bộ thư viện đã ghim là
    bộ đã verify chạy trọn pipeline, và một binary mới là cái giá thật.
  * Test chạy được mà không cần binary ngoài.

Baseline 8 ở cuối file thì có dùng bộ giải LP của scipy, và đó không phải
ngoại lệ của nguyên tắc trên: scipy vốn đã nằm sẵn trong image theo chuỗi
easyocr → scikit-image → scipy, nên khai báo nó trong requirements.txt là
nói ra thứ đang dùng chứ không phải cài thêm gì.

Nếu về sau đo thấy chậm thật thì cắm bộ giải MILP vào đúng chỗ
`_tim_to_hop_nho_nhat()` mà không đụng phần còn lại. Nhưng cắt rẻ hơn
nhiều là hạ `max_changes` — xem ghi chú ở đó.
"""

import time
from dataclasses import dataclass, field
from itertools import combinations, product
from typing import Literal

import numpy as np
from scipy.optimize import linprog

from repair.candidates import Candidate
from repair.luat_dau import KetQuaLuatDau, luat_dau_residual

# Dung sai residual, tính theo tỷ lệ trên độ lớn của vector giá trị.
#
# Dùng tỷ lệ chứ không dùng ngưỡng tuyệt đối: giá trị cỡ 1e13 nên sai số
# dấu phẩy động tuyệt đối cũng cỡ lớn, và một ngưỡng tuyệt đối sẽ hoặc bỏ
# sót mọi thứ hoặc bắt oan mọi thứ tuỳ quy mô doanh nghiệp.
RESIDUAL_TOL = 1e-9

# Trần thời gian giải mặc định, tính bằng giây.
#
# Hết giờ thì trả ABSTAIN chứ không treo. Một tài liệu không chẩn đoán
# được trong 30 giây là một tài liệu cần người xem, và treo cả lượt chạy
# 60 tài liệu vì một ca khó là đánh đổi tệ.
TIME_LIMIT_S = 30.0

# Trọng số mặc định khi không biết confidence.
#
# 1.0 nghĩa là "sửa trường nào cũng đắt như nhau". Khi có confidence thì
# truyền vào để sửa một trường model rất chắc chắn thành đắt, còn sửa một
# trường model đang lưỡng lự thành rẻ.
TRONG_SO_MAC_DINH = 1.0

# Hệ số cho phần cost của ứng viên trong hàm mục tiêu.
#
# Mục tiêu = tổng trọng số trường bị sửa + LAMBDA * tổng cost ứng viên.
# Để 1.0 nghĩa là hai phần ngang nhau. Số trường bị sửa vẫn thắng tuyệt
# đối vì tìm kiếm duyệt theo cardinality TĂNG DẦN và dừng ở k đầu tiên có
# nghiệm — cost chỉ dùng để phân xử giữa các nghiệm CÙNG cardinality.
LAMBDA = 1.0

# Trần số trường được sửa, mặc định.
#
# ĐO ĐƯỢC, không đoán: trên bài toán 8 chỉ tiêu với 87 ứng viên, ca VÔ
# NGHIỆM tốn 30 giây khi không chặn và 16 mili giây khi chặn ở 2. Ca có
# nghiệm thì tức thì trong cả hai trường hợp — chi phí nằm trọn ở việc
# chứng minh KHÔNG có nghiệm, mà đó lại là ca thường gặp vì tập ứng viên
# đóng cố ý không chứa mọi cách sửa.
#
# Chọn 2 vì một tài liệu có ba trường cùng sai thì vấn đề nằm ở khâu trích
# xuất chứ không phải khâu sửa. Nhưng đây KHÔNG phải tham số tinh chỉnh: nó
# chặn cứng số lỗi đồng thời mà phương pháp có thể sửa, nên đã ghi vào mục
# Sửa đổi của PREREGISTRATION.md kèm ngày và lý do.
MAX_CHANGES_MAC_DINH = 2

# Phân loại lý do ABSTAIN, tập ĐÓNG.
#
# Tách khỏi câu giải thích cho người đọc vì hai loại ABSTAIN mang ý nghĩa
# khoa học khác hẳn nhau, và bảng kết quả phải đếm chúng riêng:
#
#   vo_nghiem         — đã vét cạn MỌI tổ hợp và không có nghiệm. CHỈ ca này
#                       mới chứng minh được luận điểm chống bịa, tức "không
#                       cách đọc nào của tài liệu này làm bảng cân đối được".
#   vuot_tran_thay_doi— hết tổ hợp trong trần max_changes. KHÔNG chứng minh
#                       được là vô nghiệm: một nghiệm nhiều trường hơn vẫn
#                       có thể tồn tại, chỉ là không được tìm.
#   het_gio           — cũng không chứng minh được gì cả.
#   thieu_gia_tri     — không dựng được vector nên không kiểm được ràng buộc.
#   bo_giai_that_bai  — bộ giải LP của baseline 8 không trả nghiệm.
#
# Gộp bốn loại sau vào một chỗ với vo_nghiem sẽ làm luận điểm cốt lõi được
# tính công cho những ca nó không chứng minh được gì.
LyDoAbstain = Literal[
    "",
    "vo_nghiem",
    "vuot_tran_thay_doi",
    "het_gio",
    "thieu_gia_tri",
    "bo_giai_that_bai",
]


@dataclass
class Diagnosis:
    """Kết quả chẩn đoán một tài liệu."""

    verdict: Literal["VERIFIED", "REPAIRED", "ABSTAIN"]
    changed_fields: dict = field(default_factory=dict)
    residual_before: np.ndarray | None = None
    residual_after: np.ndarray | None = None
    n_changed: int = 0
    solve_time_s: float = 0.0
    ma_ly_do: LyDoAbstain = ""
    ly_do_abstain: str = ""
    # Cơ chế nào định vị được lỗi. Tập ĐÓNG: "" (chưa định vị được),
    # "luat_dau" (luật residual của repair.luat_dau), "tim_kiem_to_hop"
    # (duyệt tổ hợp trong _tim_to_hop_nho_nhat).
    #
    # Vì sao phải ghi tường minh thay vì suy từ n_changed == 1: hai cơ chế
    # cho cùng một kết quả nhưng KHÔNG cùng sức nặng khi viết vào bài. Luật
    # dấu là hệ quả đại số chứng minh được, còn duyệt tổ hợp là tìm kiếm
    # trong một tập ứng viên hữu hạn — gộp chúng lại là đánh mất đúng thứ
    # phân biệt một định lý với một phép thử.
    nguon_dinh_vi: str = ""
    # Kết quả luật dấu, LUÔN được ghi kể cả khi nó im lặng. Một luật im lặng
    # ở 6/8 đẳng thức lệch là số liệu về phạm vi áp dụng của nó, và số đó chỉ
    # có nếu ca im lặng cũng được ghi lại.
    luat_dau: KetQuaLuatDau | None = None

    def gia_tri_sau_sua(self, values: dict) -> dict:
        """Bộ giá trị sau khi áp các thay đổi đã chọn."""
        return {**values, **{ten: uv.value for ten, uv in self.changed_fields.items()}}


def _vector(values: dict, field_order: list) -> np.ndarray:
    return np.array([values[ten] for ten in field_order], dtype=float)


def _thoa_rang_buoc(residual: np.ndarray, do_lon: float, tol: float) -> bool:
    return bool(np.linalg.norm(residual) / (do_lon or 1.0) <= tol)


def _tim_to_hop_nho_nhat(
    A: np.ndarray,
    x: np.ndarray,
    field_order: list,
    candidates: dict,
    trong_so: dict,
    tol: float,
    max_changes: int | None,
    time_limit_s: float,
    bat_dau: float,
):
    """
    Duyệt tổ hợp sửa theo cardinality TĂNG DẦN, dừng ở k đầu tiên có nghiệm.

    Trả về (tổ hợp tốt nhất, lý do dừng). Tổ hợp là dict {tên field: ứng
    viên}, hoặc None nếu không tìm được.

    Tính residual mới theo kiểu CỘNG DỒN thay vì dựng lại cả vector: thay
    field i bằng giá trị v làm residual đổi đúng (v − x_i)·A[:, i]. Nhờ vậy
    mỗi tổ hợp chỉ tốn vài phép cộng vector chứ không tốn một phép nhân ma
    trận, và đó là khác biệt giữa "chạy được" với "không" ở k = 3.

    Dừng ở k đầu tiên có nghiệm chính là định nghĩa min-cardinality. Trong
    cùng một k thì phân xử bằng hàm mục tiêu.

    Lý do trả về phân biệt `vo_nghiem` với `vuot_tran`: chỉ khi trần thay
    đổi KHÔNG cắt ngắn cuộc duyệt thì "không tìm thấy" mới đồng nghĩa với
    "không tồn tại", và chỉ nghĩa thứ hai mới đỡ được luận điểm chống bịa.
    """
    n = len(field_order)
    do_lon = float(np.linalg.norm(x))
    residual_goc = A @ x

    # Đóng góp của từng (trường, ứng viên) vào residual, tính sẵn một lần.
    dong_gop: dict = {}
    for i, ten in enumerate(field_order):
        cot = A[:, i]
        dong_gop[i] = [
            (uv, (uv.value - x[i]) * cot, trong_so.get(ten, TRONG_SO_MAC_DINH))
            for uv in candidates.get(ten, [])
        ]

    co_ung_vien = [i for i in range(n) if dong_gop[i]]
    tran_k = len(co_ung_vien) if max_changes is None else min(max_changes, len(co_ung_vien))

    for k in range(1, tran_k + 1):
        tot_nhat = None
        muc_tieu_tot_nhat = float("inf")

        for cac_truong in combinations(co_ung_vien, k):
            if time.perf_counter() - bat_dau > time_limit_s:
                return tot_nhat, "het_gio"

            for to_hop in product(*(dong_gop[i] for i in cac_truong)):
                residual = residual_goc + sum(delta for _, delta, _ in to_hop)
                if not _thoa_rang_buoc(residual, do_lon, tol):
                    continue

                muc_tieu = sum(w for _, _, w in to_hop) + LAMBDA * sum(
                    uv.cost for uv, _, _ in to_hop
                )
                if muc_tieu < muc_tieu_tot_nhat:
                    muc_tieu_tot_nhat = muc_tieu
                    tot_nhat = {
                        field_order[i]: uv for i, (uv, _, _) in zip(cac_truong, to_hop)
                    }

        if tot_nhat is not None:
            return tot_nhat, "tim_thay"

    return None, ("vo_nghiem" if tran_k == len(co_ung_vien) else "vuot_tran_thay_doi")


def diagnose(
    values: dict,
    candidates: dict,
    A: np.ndarray,
    field_order: list,
    confidences: dict | None = None,
    tolerance_ratio: float = RESIDUAL_TOL,
    max_changes: int | None = MAX_CHANGES_MAC_DINH,
    time_limit_s: float = TIME_LIMIT_S,
    dung_luat_dau: bool = True,
) -> Diagnosis:
    """
    Tìm tổ hợp ứng viên nhỏ nhất làm residual về 0.

    values: {tên field: giá trị}, đã quy đổi về đồng.
    candidates: {tên field: [Candidate]}, sinh bởi repair.candidates.
    confidences: {tên field: 0..1}, dùng làm trọng số — sửa một trường model
        rất chắc chắn thì "đắt", sửa một trường model đang lưỡng lự thì "rẻ".

    Ba verdict:

      VERIFIED  — residual đã về 0 từ đầu. KHÔNG chạy tìm kiếm.
      REPAIRED  — tìm được tổ hợp ứng viên làm residual về 0.
      ABSTAIN   — không tổ hợp nào cho nghiệm, hoặc vượt trần thay đổi,
                  hoặc hết giờ. `ma_ly_do` nói rõ là ca nào.

    ABSTAIN là câu trả lời ĐÚNG chứ không phải thất bại. Nó nghĩa là không
    cách đọc nào của tài liệu này làm bảng cân đối được, và một hệ nói
    "tôi không biết" đúng lúc thì giá trị hơn hẳn một hệ luôn trả về số.

    Nhưng chỉ `ma_ly_do == "vo_nghiem"` mới mang đúng nghĩa đó. Với trần
    thay đổi mặc định là 2, một tài liệu ba lỗi sẽ ABSTAIN với lý do
    `vuot_tran_thay_doi` — nó không nói rằng tài liệu không sửa được, chỉ
    nói rằng ta đã không tìm. Bảng kết quả phải đếm hai loại này riêng, nếu
    không thì luận điểm chống bịa được tính công cho những ca nó không
    chứng minh được gì.

    Thiếu trường thì cũng ABSTAIN: không dựng được vector thì không kiểm
    được ràng buộc, và đoán bừa giá trị thiếu chính là việc module này
    sinh ra để chống.

    dung_luat_dau — chạy `repair.luat_dau.luat_dau_residual()` trước bước
    duyệt tổ hợp. Luật ấy định vị được lỗi ĐẢO DẤU bằng một lập luận đại số
    thay vì bằng tìm kiếm, nên khi nó ra tay thì `nguon_dinh_vi` ghi
    "luat_dau" và kết quả mang sức nặng khác hẳn một lần duyệt trúng. Nó chỉ
    được phép ÁP giá trị khi giá trị lật dấu đã nằm sẵn trong `candidates` —
    tập ứng viên vẫn đóng. Tắt cờ này để đo riêng phần đóng góp của nó.

    `Diagnosis.luat_dau` được ghi ở MỌI đường ra có chạy luật, kể cả khi luật
    im lặng, vì tỷ lệ im lặng chính là số đo phạm vi áp dụng của nó. Hai
    đường ra sớm — VERIFIED và `thieu_gia_tri` — trả None ở đó, đúng nghĩa
    "luật chưa từng chạy" chứ không phải "luật đã chạy và không nói gì".
    """
    bat_dau = time.perf_counter()
    trong_so = confidences or {}

    thieu = [ten for ten in field_order if values.get(ten) is None]
    if thieu:
        return Diagnosis(
            verdict="ABSTAIN",
            solve_time_s=time.perf_counter() - bat_dau,
            ma_ly_do="thieu_gia_tri",
            ly_do_abstain=f"thiếu giá trị cho: {', '.join(thieu)}",
        )

    x = _vector(values, field_order)
    residual_truoc = A @ x
    do_lon = float(np.linalg.norm(x))

    if _thoa_rang_buoc(residual_truoc, do_lon, tolerance_ratio):
        return Diagnosis(
            verdict="VERIFIED",
            residual_before=residual_truoc,
            residual_after=residual_truoc,
            solve_time_s=time.perf_counter() - bat_dau,
        )

    # LUẬT DẤU chạy trước tìm kiếm tổ hợp, và kết quả được ghi lại DÙ CÓ
    # dùng được hay không. Nó rẻ (một phép nhân ma trận-vector cho mỗi cột)
    # so với tìm kiếm tổ hợp vốn đi theo C(n,k).
    kq_luat_dau = (
        luat_dau_residual(values, A, field_order, tolerance_ratio)
        if dung_luat_dau
        else None
    )

    # TẬP ỨNG VIÊN VẪN LÀ TẬP ĐÓNG, kể cả ở đường tắt này. Luật dấu chỉ được
    # phép ÁP giá trị lật dấu khi giá trị ấy đã có sẵn trong tập ứng viên
    # sinh từ tài liệu. Nếu có bất kỳ đường nào để một con số ngoài tập lọt
    # vào kết quả thì hệ ép số được, và toàn bộ lập luận chống bịa của
    # nghiên cứu sụp — đó là lý do khối này kiểm tra rồi mới dùng, chứ không
    # tự dựng một Candidate mới từ con số nó vừa tính ra. Bình thường
    # candidates.tu_dau() đã sinh sẵn −x cho mọi chỉ tiêu nên nhánh này
    # trúng; ca trượt là khi người gọi truyền vào một tập ứng viên bị hạn
    # chế, và khi đó luật lui về vai trò CHẨN ĐOÁN, không sửa.
    if kq_luat_dau is not None and kq_luat_dau.dinh_vi_duoc:
        ten = kq_luat_dau.truong
        khop = [
            uv for uv in candidates.get(ten, [])
            if uv.value == kq_luat_dau.gia_tri_sau
        ]
        if khop:
            x_moi = x.copy()
            x_moi[field_order.index(ten)] = kq_luat_dau.gia_tri_sau
            return Diagnosis(
                verdict="REPAIRED",
                changed_fields={ten: khop[0]},
                residual_before=residual_truoc,
                residual_after=A @ x_moi,
                n_changed=1,
                solve_time_s=time.perf_counter() - bat_dau,
                nguon_dinh_vi="luat_dau",
                luat_dau=kq_luat_dau,
            )

    to_hop, ly_do = _tim_to_hop_nho_nhat(
        A, x, field_order, candidates, trong_so,
        tolerance_ratio, max_changes, time_limit_s, bat_dau,
    )

    if to_hop is None:
        giai_thich = {
            "het_gio": f"hết {time_limit_s}s mà chưa tìm ra tổ hợp nào",
            "vo_nghiem": "không tổ hợp ứng viên nào làm residual về 0",
            "vuot_tran_thay_doi": (
                f"không tổ hợp nào từ {max_changes} trường trở xuống cho nghiệm "
                f"— chưa duyệt tới các tổ hợp lớn hơn"
            ),
        }[ly_do]
        return Diagnosis(
            verdict="ABSTAIN",
            residual_before=residual_truoc,
            solve_time_s=time.perf_counter() - bat_dau,
            ma_ly_do=ly_do,
            ly_do_abstain=giai_thich,
            luat_dau=kq_luat_dau,
        )

    x_moi = x.copy()
    for ten, uv in to_hop.items():
        x_moi[field_order.index(ten)] = uv.value

    return Diagnosis(
        verdict="REPAIRED",
        changed_fields=to_hop,
        residual_before=residual_truoc,
        residual_after=A @ x_moi,
        n_changed=len(to_hop),
        solve_time_s=time.perf_counter() - bat_dau,
        nguon_dinh_vi="tim_kiem_to_hop",
        luat_dau=kq_luat_dau,
    )


# ---------------------------------------------------------------------------
# Hai baseline đối chứng, CÙNG interface để đổi bằng cờ
# ---------------------------------------------------------------------------


def _min_l1_lp(A: np.ndarray, b: np.ndarray):
    """
    Nghiệm chuẩn L1 nhỏ nhất của A·delta = b, giải CHÍNH XÁC bằng quy hoạch
    tuyến tính. Trả về `(delta, lý do thất bại)`; một trong hai luôn là None.

    Tách `delta = u − v` với `u, v ≥ 0` rồi tối thiểu hoá `Σ(u + v)` là cách
    chuẩn đưa chuẩn L1 về dạng tuyến tính. Điều quan trọng hơn: nghiệm bộ
    giải trả về là nghiệm ĐỈNH, nên số toạ độ khác 0 không vượt quá hạng
    của A — đúng tính chất thưa mà baseline này phải có.

    Vì sao không dùng IRLS: trên hệ đối xứng như `a + b = c`, cực tiểu L1
    suy biến — nghiệm rải đều ra ba trường có cùng chuẩn L1 với nghiệm dồn
    vào một trường. IRLS xuất phát từ trọng số đều rơi ngay vào nghiệm rải
    đều, và đó là điểm bất động thật sự của phép lặp: không có bất đối xứng
    nào để thoát ra, kể cả khi giảm dần epsilon. Một baseline rải sai lệch
    ra mọi trường là baseline bị làm yếu âm thầm, mà baseline yếu oan thì
    kết luận về phương pháp đề xuất mất giá trị — đúng thứ mục 2 của
    PREREGISTRATION.md dựng lên để chống.
    """
    n = A.shape[1]

    ket_qua = linprog(
        np.ones(2 * n),
        A_eq=np.hstack([A, -A]),
        b_eq=b,
        bounds=(0, None),
        method="highs",
    )

    if not ket_qua.success:
        return None, ket_qua.message

    return ket_qua.x[:n] - ket_qua.x[n:], None


def diagnose_l1_continuous(
    values: dict,
    candidates: dict,
    A: np.ndarray,
    field_order: list,
    confidences: dict | None = None,
    tolerance_ratio: float = RESIDUAL_TOL,
    max_changes: int | None = None,
    time_limit_s: float = TIME_LIMIT_S,
) -> Diagnosis:
    """
    BASELINE 8 — sửa lỗi L1 liên tục cổ điển.

    Tìm delta chuẩn L1 nhỏ nhất thoả A(x + delta) = 0, với delta chạy TỰ DO
    trong R^n. Đây là hướng compressed sensing và data reconciliation.

    Giải bằng quy hoạch tuyến tính nên đây là nghiệm L1 CHÍNH XÁC, không
    phải xấp xỉ — paper nói được điều đó mà không cần kèm caveat, và một
    baseline không có caveat thì kết quả so sánh với nó cũng không có.

    Tham số `candidates` bị BỎ QUA, và đó chính là điểm của baseline này:
    nó không cần tài liệu vì nó không đọc lại tài liệu. Giữ nguyên chữ ký
    hàm để đổi giữa các phương pháp bằng một cờ, không phải bằng một nhánh
    if trong runner.

    `max_changes` cũng bị BỎ QUA, và mặc định của nó để `None` chứ không
    theo trần chung để nói ra điều đó. Chặn số trường được sửa là khái niệm
    của tìm kiếm rời rạc; ở đây delta chạy tự do và nghiệm đỉnh của bài quy
    hoạch tuyến tính đã tự giới hạn số toạ độ khác 0 không vượt quá hạng của
    A. Nhận tham số rồi lặng lẽ không dùng thì runner sẽ tưởng hai phương
    pháp đang chạy cùng một ràng buộc.

    Baseline này KHÔNG BAO GIỜ ABSTAIN khi hệ có nghiệm — và đó là điểm
    yếu cần đo chứ không phải điểm mạnh: nó luôn trả về một bộ số cân đối,
    kể cả khi bộ số đó hoàn toàn bịa. Chỉ số chống bịa ở eval.metrics đo
    đúng chỗ này.
    """
    bat_dau = time.perf_counter()

    thieu = [ten for ten in field_order if values.get(ten) is None]
    if thieu:
        return Diagnosis(
            verdict="ABSTAIN",
            solve_time_s=time.perf_counter() - bat_dau,
            ma_ly_do="thieu_gia_tri",
            ly_do_abstain=f"thiếu giá trị cho: {', '.join(thieu)}",
        )

    x = _vector(values, field_order)
    residual_truoc = A @ x
    do_lon = float(np.linalg.norm(x))

    if _thoa_rang_buoc(residual_truoc, do_lon, tolerance_ratio):
        return Diagnosis(
            verdict="VERIFIED",
            residual_before=residual_truoc,
            residual_after=residual_truoc,
            solve_time_s=time.perf_counter() - bat_dau,
        )

    delta, that_bai = _min_l1_lp(A, -residual_truoc)

    # `b = −A·x` luôn nằm trong không gian cột của A theo đúng cách nó được
    # dựng, nên bài LP này về toán học luôn có nghiệm. Thất bại ở đây chỉ có
    # thể là chuyện của bộ giải, và phải nói ra thành ABSTAIN chứ không được
    # trả REPAIRED kèm một residual chưa về 0.
    if delta is None:
        return Diagnosis(
            verdict="ABSTAIN",
            residual_before=residual_truoc,
            solve_time_s=time.perf_counter() - bat_dau,
            ma_ly_do="bo_giai_that_bai",
            ly_do_abstain=f"bộ giải LP không trả nghiệm: {that_bai}",
        )

    x_moi = x + delta

    # Trường nào bị đổi đáng kể thì tính là đã sửa. Ngưỡng vẫn theo tỷ lệ
    # dù bộ giải LP trả về 0 đúng bằng 0 ở các toạ độ ngoài cơ sở: với giá
    # trị cỡ 1e13 thì sai số dấu phẩy động của chính phép giải cũng cỡ lớn,
    # và đếm nhầm một nhiễu 1e-3 đồng thành "một trường bị sửa" sẽ thổi
    # phồng số trường bị sửa của baseline này.
    da_sua = {
        ten: Candidate(
            value=float(x_moi[i]),
            source="l1_continuous",
            cost=abs(float(delta[i])),
            evidence={"delta": float(delta[i])},
        )
        for i, ten in enumerate(field_order)
        if abs(delta[i]) > tolerance_ratio * (do_lon or 1.0)
    }

    return Diagnosis(
        verdict="REPAIRED",
        changed_fields=da_sua,
        residual_before=residual_truoc,
        residual_after=A @ x_moi,
        n_changed=len(da_sua),
        solve_time_s=time.perf_counter() - bat_dau,
    )


def diagnose_fellegi_holt_donor(
    values: dict,
    candidates: dict,
    A: np.ndarray,
    field_order: list,
    donor_values: dict | None = None,
    confidences: dict | None = None,
    tolerance_ratio: float = RESIDUAL_TOL,
    max_changes: int | None = MAX_CHANGES_MAC_DINH,
    time_limit_s: float = TIME_LIMIT_S,
) -> Diagnosis:
    """
    BASELINE 9 — THÍ NGHIỆM QUAN TRỌNG NHẤT CỦA CẢ NGHIÊN CỨU.

    Giống hệt diagnose() ở việc chọn TRƯỜNG nào sửa: cũng tìm tập trường
    nhỏ nhất mà sau khi thả tự do thì hệ có nghiệm. Khác đúng MỘT biến số:
    giá trị điền vào không đến từ tài liệu mà đến từ phân phối của chính
    field đó trên các tài liệu khác — đúng cách Fellegi-Holt kinh điển làm
    với bản ghi donor.

    Cùng ràng buộc, cùng thuật toán chọn trường, cùng ngân sách. Khác đúng
    một thứ: ứng viên đến từ đâu.

    Nếu baseline này ngang bằng diagnose() thì toàn bộ luận điểm "đọc lại
    nguồn" sai, và PHẢI NÓI RA. Điều kiện phản chứng này đã đăng ký trước
    trong PREREGISTRATION.md, nên không thể lặng lẽ thay bằng một baseline
    dễ thắng hơn.

    Cách điền giá trị: trong tập trường được thả, chọn bộ giá trị GẦN DONOR
    NHẤT mà vẫn thoả ràng buộc. Chọn thế để baseline không thua oan chỉ vì
    giá trị donor thô không cân bảng.

    NHƯNG PHẢI GỌI ĐÚNG TÊN NÓ, và đây là chỗ dễ viết sai trong bài. Đây
    KHÔNG phải donor substitution kinh điển của Fellegi-Holt 1976; y văn
    thống kê chính thức gọi nó là `imputation under edit constraints`
    (Pannekoek & Scholtus) — donor chỉ là điểm neo, còn giá trị điền ra do
    ràng buộc quyết định. Đo ngày 04/09/2026 trên 10 tài liệu: trong 17 ô hàm
    này sửa, chỉ 3 ô rơi đúng vào giá trị donor, lệch trung vị 55,9%.

    HỆ QUẢ PHẢI BÁO CÁO, KHÔNG ĐƯỢC GIẤU: khi ràng buộc xác định nghiệm duy
    nhất thì donor không đóng góp gì, nên hai phe của H3 ra kết quả TRÙNG
    KHÍT tới từng chữ số — đã xảy ra ở `PLX_2026Q2_TT99` và
    `REE_2023Q2_TT200`. Ở những ca ấy thí nghiệm không đo được biến số nào.
    Vì vậy `diagnose_fellegi_holt_donor_thuan()` chạy song song và bài báo
    cáo cả hai: bản thuần mới là bản thật sự đo được câu hỏi của H3.

    Cách chọn TẬP TRƯỜNG cũng phải trung thực như vậy, và đó là lý do vòng
    lặp dưới đây duyệt HẾT mọi tập trường ở một cardinality rồi mới phân xử
    — đúng như `diagnose()` làm với cost ứng viên. Trả về tập đầu tiên gặp
    được thì tập trường phụ thuộc vào thứ tự khai báo field, tức baseline
    trung tâm của cả nghiên cứu thắng thua vì một chi tiết cài đặt. Ở đây
    phân xử bằng tổng khoảng cách tới donor: tập trường nào donor đỡ được
    nhiều nhất thì tập đó thắng, và khác biệt còn lại giữa hai nhánh đúng
    bằng một biến số là nguồn giá trị.

    Trường không có giá trị donor thì lấy chính giá trị hiện tại làm mốc,
    nên khoảng cách của nó đo đúng phần phải bịa ra khi không ai đỡ.
    """
    bat_dau = time.perf_counter()

    thieu = [ten for ten in field_order if values.get(ten) is None]
    if thieu:
        return Diagnosis(
            verdict="ABSTAIN",
            solve_time_s=time.perf_counter() - bat_dau,
            ma_ly_do="thieu_gia_tri",
            ly_do_abstain=f"thiếu giá trị cho: {', '.join(thieu)}",
        )

    x = _vector(values, field_order)
    residual_truoc = A @ x
    do_lon = float(np.linalg.norm(x))

    if _thoa_rang_buoc(residual_truoc, do_lon, tolerance_ratio):
        return Diagnosis(
            verdict="VERIFIED",
            residual_before=residual_truoc,
            residual_after=residual_truoc,
            solve_time_s=time.perf_counter() - bat_dau,
        )

    donor = donor_values or {}
    n = len(field_order)
    tran_k = n if max_changes is None else min(max_changes, n)

    for k in range(1, tran_k + 1):
        tot_nhat = None
        het_gio = False

        for cac_truong in combinations(range(n), k):
            if time.perf_counter() - bat_dau > time_limit_s:
                het_gio = True
                break

            chi_so = list(cac_truong)
            A_tha = A[:, chi_so]

            # Phần cố định đóng góp gì vào residual
            x_co_dinh = x.copy()
            x_co_dinh[chi_so] = 0.0
            b = -(A @ x_co_dinh)

            # Điểm xuất phát: giá trị donor, hoặc giá trị hiện tại nếu
            # không có donor cho field đó.
            d = np.array(
                [donor.get(field_order[i], x[i]) for i in chi_so], dtype=float
            )

            # Bộ giá trị gần donor nhất mà vẫn thoả A_tha·x_tha = b
            con_lai = b - A_tha @ d
            x_tha = d + np.linalg.pinv(A_tha) @ con_lai

            x_moi = x.copy()
            x_moi[chi_so] = x_tha

            if not _thoa_rang_buoc(A @ x_moi, do_lon, tolerance_ratio):
                continue

            khoang_cach = float(np.abs(x_tha - d).sum())
            if tot_nhat is None or khoang_cach < tot_nhat[0]:
                tot_nhat = (khoang_cach, chi_so, x_tha)

        # Hết giờ giữa chừng vẫn dùng được tập tốt nhất đã tìm ra ở chính
        # cardinality này: nó là một nghiệm k-trường hợp lệ, chỉ là chưa
        # chắc tối ưu. Bỏ nó đi để trả ABSTAIN là mất trắng công đã làm.
        if tot_nhat is not None:
            _, chi_so, x_tha = tot_nhat
            x_moi = x.copy()
            x_moi[chi_so] = x_tha

            da_sua = {
                field_order[i]: Candidate(
                    value=float(x_moi[i]),
                    source="donor",
                    cost=abs(float(x_moi[i] - x[i])),
                    evidence={
                        "donor": donor.get(field_order[i]),
                        "lech_so_voi_donor": abs(
                            float(x_moi[i] - donor.get(field_order[i], x[i]))
                        ),
                    },
                )
                for i in chi_so
            }

            return Diagnosis(
                verdict="REPAIRED",
                changed_fields=da_sua,
                residual_before=residual_truoc,
                residual_after=A @ x_moi,
                n_changed=len(da_sua),
                solve_time_s=time.perf_counter() - bat_dau,
            )

        if het_gio:
            return Diagnosis(
                verdict="ABSTAIN",
                residual_before=residual_truoc,
                solve_time_s=time.perf_counter() - bat_dau,
                ma_ly_do="het_gio",
                ly_do_abstain=f"hết {time_limit_s}s",
            )

    het_moi_tap = max_changes is None or max_changes >= n
    return Diagnosis(
        verdict="ABSTAIN",
        residual_before=residual_truoc,
        solve_time_s=time.perf_counter() - bat_dau,
        ma_ly_do="vo_nghiem" if het_moi_tap else "vuot_tran_thay_doi",
        ly_do_abstain=(
            "không tập trường nào cho nghiệm"
            if het_moi_tap
            else f"không tập từ {max_changes} trường trở xuống nào cho nghiệm"
        ),
    )


def diagnose_fellegi_holt_donor_thuan(
    values: dict,
    A: np.ndarray,
    field_order: list,
    donor_values: dict,
    tolerance_ratio: float = RESIDUAL_TOL,
    max_changes: int | None = MAX_CHANGES_MAC_DINH,
    time_limit_s: float = TIME_LIMIT_S,
) -> Diagnosis:
    """
    BASELINE 9-THUẦN — thay thẳng giá trị donor, không giải phương trình.

    VÌ SAO CẦN BIẾN THỂ NÀY, ĐO ĐƯỢC NGÀY 04/09/2026. Lượt thử 10 tài liệu
    cho thấy `diagnose_fellegi_holt_donor()` hầu như KHÔNG dùng số donor:
    trong 17 ô nó sửa, chỉ 3 ô rơi đúng vào giá trị donor, còn lệch trung vị
    55,9% so với donor. Lý do là nó chiếu donor lên không gian nghiệm, nên
    khi ràng buộc xác định nghiệm duy nhất thì donor không đóng góp gì — và
    hai phe của H3 ra kết quả TRÙNG KHÍT tới từng chữ số, đo được ở
    `PLX_2026Q2_TT99` và `REE_2023Q2_TT200`. Khi ấy thí nghiệm không còn đo
    được biến số nào cả.

    Hàm này là đầu kia của cùng một trục, và tồn tại để bài báo cáo cả hai
    chứ không phải chọn một:

      bản chiếu (`diagnose_fellegi_holt_donor`) — donor chỉ là điểm neo, giá
        trị điền ra do ràng buộc quyết định. Đây là `imputation under edit
        constraints` của Pannekoek & Scholtus, KHÔNG phải donor substitution
        kinh điển, và phải gọi đúng tên ấy trong bài.
      bản thuần (hàm này) — donor là giá trị điền ra, đúng nghĩa hot-deck của
        Fellegi-Holt 1976: giá trị đến từ một bản ghi đã thoả mọi ràng buộc.

    Bản thuần yếu hơn hẳn và điều đó nằm trong dự kiến: donor thô gần như
    không bao giờ làm bảng cân đối khớp. Nhưng nó là bản mà người phản biện
    sẽ đòi, vì nó là thứ duy nhất trong hai bản thực sự đo được câu hỏi của
    H3 — giá trị lấy từ tổng thể có thay được giá trị đọc từ tờ giấy không.

    Chỉ duyệt những trường CÓ donor: không có donor thì không có gì để thay,
    và đưa trường ấy vào tổ hợp chỉ làm baseline thua vì một lý do không liên
    quan tới nguồn giá trị.

    Phân xử giữa các tập cùng cardinality bằng TỔNG THAY ĐỔI nhỏ nhất — đúng
    nguyên tắc minimum change của chính Fellegi-Holt, và cùng tiêu chí mà
    `diagnose()` dùng cho ứng viên đọc từ tài liệu.
    """
    bat_dau = time.perf_counter()

    thieu = [ten for ten in field_order if values.get(ten) is None]
    if thieu:
        return Diagnosis(
            verdict="ABSTAIN",
            solve_time_s=time.perf_counter() - bat_dau,
            ma_ly_do="thieu_gia_tri",
            ly_do_abstain=f"thiếu giá trị cho: {', '.join(thieu)}",
        )

    x = _vector(values, field_order)
    residual_truoc = A @ x
    do_lon = float(np.linalg.norm(x))

    if _thoa_rang_buoc(residual_truoc, do_lon, tolerance_ratio):
        return Diagnosis(
            verdict="VERIFIED",
            residual_before=residual_truoc,
            residual_after=residual_truoc,
            solve_time_s=time.perf_counter() - bat_dau,
        )

    co_donor = [i for i, ten in enumerate(field_order) if ten in donor_values]
    tran_k = len(co_donor) if max_changes is None else min(max_changes, len(co_donor))

    for k in range(1, tran_k + 1):
        tot_nhat = None
        het_gio = False

        for cac_truong in combinations(co_donor, k):
            if time.perf_counter() - bat_dau > time_limit_s:
                het_gio = True
                break

            chi_so = list(cac_truong)
            x_moi = x.copy()
            for i in chi_so:
                x_moi[i] = float(donor_values[field_order[i]])

            if not _thoa_rang_buoc(A @ x_moi, do_lon, tolerance_ratio):
                continue

            thay_doi = float(np.abs(x_moi[chi_so] - x[chi_so]).sum())
            if tot_nhat is None or thay_doi < tot_nhat[0]:
                tot_nhat = (thay_doi, chi_so, x_moi)

        if tot_nhat is not None:
            _, chi_so, x_moi = tot_nhat
            da_sua = {
                field_order[i]: Candidate(
                    value=float(x_moi[i]),
                    source="donor_thuan",
                    cost=abs(float(x_moi[i] - x[i])),
                    evidence={"donor": donor_values[field_order[i]]},
                )
                for i in chi_so
            }
            return Diagnosis(
                verdict="REPAIRED",
                changed_fields=da_sua,
                residual_before=residual_truoc,
                residual_after=A @ x_moi,
                n_changed=len(da_sua),
                solve_time_s=time.perf_counter() - bat_dau,
            )

        if het_gio:
            return Diagnosis(
                verdict="ABSTAIN",
                residual_before=residual_truoc,
                solve_time_s=time.perf_counter() - bat_dau,
                ma_ly_do="het_gio",
                ly_do_abstain=f"hết {time_limit_s}s",
            )

    het_moi_tap = max_changes is None or max_changes >= len(co_donor)
    return Diagnosis(
        verdict="ABSTAIN",
        residual_before=residual_truoc,
        solve_time_s=time.perf_counter() - bat_dau,
        ma_ly_do="vo_nghiem" if het_moi_tap else "vuot_tran_thay_doi",
        ly_do_abstain=(
            "không tập trường có donor nào cho nghiệm"
            if het_moi_tap
            else f"không tập từ {max_changes} trường có donor trở xuống nào cho nghiệm"
        ),
    )
