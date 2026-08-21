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
  * Giữ requirements.txt nguyên vẹn: bộ đã ghim là bộ đã verify chạy trọn
    pipeline, và thêm một bộ giải kèm binary vào image là cái giá thật.
  * Test chạy được mà không cần binary ngoài.

Nếu về sau đo thấy chậm thật thì cắm bộ giải MILP vào đúng chỗ
`_tim_to_hop_nho_nhat()` mà không đụng phần còn lại. Nhưng cắt rẻ hơn
nhiều là hạ `max_changes` — xem ghi chú ở đó.
"""

import time
from dataclasses import dataclass, field
from itertools import combinations, product
from typing import Literal

import numpy as np

from repair.candidates import Candidate

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


@dataclass
class Diagnosis:
    """Kết quả chẩn đoán một tài liệu."""

    verdict: Literal["VERIFIED", "REPAIRED", "ABSTAIN"]
    changed_fields: dict = field(default_factory=dict)
    residual_before: np.ndarray | None = None
    residual_after: np.ndarray | None = None
    n_changed: int = 0
    solve_time_s: float = 0.0
    ly_do_abstain: str = ""

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

    return None, "vo_nghiem"


def diagnose(
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
    Tìm tổ hợp ứng viên nhỏ nhất làm residual về 0.

    values: {tên field: giá trị}, đã quy đổi về đồng.
    candidates: {tên field: [Candidate]}, sinh bởi repair.candidates.
    confidences: {tên field: 0..1}, dùng làm trọng số — sửa một trường model
        rất chắc chắn thì "đắt", sửa một trường model đang lưỡng lự thì "rẻ".

    Ba verdict:

      VERIFIED  — residual đã về 0 từ đầu. KHÔNG chạy tìm kiếm.
      REPAIRED  — tìm được tổ hợp ứng viên làm residual về 0.
      ABSTAIN   — không tổ hợp nào cho nghiệm, hoặc vượt trần thay đổi,
                  hoặc hết giờ.

    ABSTAIN là câu trả lời ĐÚNG chứ không phải thất bại. Nó nghĩa là không
    cách đọc nào của tài liệu này làm bảng cân đối được, và một hệ nói
    "tôi không biết" đúng lúc thì giá trị hơn hẳn một hệ luôn trả về số.

    Thiếu trường thì cũng ABSTAIN: không dựng được vector thì không kiểm
    được ràng buộc, và đoán bừa giá trị thiếu chính là việc module này
    sinh ra để chống.
    """
    bat_dau = time.perf_counter()
    trong_so = confidences or {}

    thieu = [ten for ten in field_order if values.get(ten) is None]
    if thieu:
        return Diagnosis(
            verdict="ABSTAIN",
            solve_time_s=time.perf_counter() - bat_dau,
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

    to_hop, ly_do = _tim_to_hop_nho_nhat(
        A, x, field_order, candidates, trong_so,
        tolerance_ratio, max_changes, time_limit_s, bat_dau,
    )

    if to_hop is None:
        giai_thich = {
            "het_gio": f"hết {time_limit_s}s mà chưa tìm ra tổ hợp nào",
            "vo_nghiem": "không tổ hợp ứng viên nào làm residual về 0",
        }[ly_do]
        return Diagnosis(
            verdict="ABSTAIN",
            residual_before=residual_truoc,
            solve_time_s=time.perf_counter() - bat_dau,
            ly_do_abstain=giai_thich,
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
    )


# ---------------------------------------------------------------------------
# Hai baseline đối chứng, CÙNG interface để đổi bằng cờ
# ---------------------------------------------------------------------------


def _min_l1_irls(A: np.ndarray, b: np.ndarray, so_vong: int = 50, eps: float = 1e-8):
    """
    Nghiệm chuẩn L1 nhỏ nhất của A·delta = b, giải xấp xỉ bằng IRLS.

    Bài toán chính xác là một bài quy hoạch tuyến tính. Ở đây không có bộ
    giải LP nào (quyết định giữ requirements nguyên vẹn), nên dùng
    iteratively reweighted least squares: lặp lại bài bình phương tối
    thiểu có trọng số nghịch với độ lớn nghiệm hiện tại, việc đó kéo nghiệm
    về phía thưa đúng như chuẩn L1 làm.

    PHẢI NÊU TRONG PAPER rằng đây là nghiệm xấp xỉ chứ không phải nghiệm
    LP chính xác. Baseline mạnh hơn thì kết luận về phương pháp đề xuất
    càng đáng tin, nên làm yếu baseline một cách âm thầm là tự bắn vào
    chân mình.
    """
    n = A.shape[1]
    w = np.ones(n)
    delta = np.zeros(n)

    for _ in range(so_vong):
        Q = np.diag(w)
        M = A @ Q @ A.T
        delta_moi = Q @ A.T @ np.linalg.pinv(M) @ b

        if np.allclose(delta_moi, delta, atol=eps):
            delta = delta_moi
            break

        delta = delta_moi
        w = np.maximum(np.abs(delta), eps)

    return delta


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

    Tham số `candidates` bị BỎ QUA, và đó chính là điểm của baseline này:
    nó không cần tài liệu vì nó không đọc lại tài liệu. Giữ nguyên chữ ký
    hàm để đổi giữa các phương pháp bằng một cờ, không phải bằng một nhánh
    if trong runner.

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

    delta = _min_l1_irls(A, -residual_truoc)
    x_moi = x + delta

    # Trường nào bị đổi đáng kể thì tính là đã sửa. Ngưỡng theo tỷ lệ vì
    # IRLS để lại nhiễu rất nhỏ ở mọi toạ độ chứ không đúng bằng 0.
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
    max_changes: int | None = None,
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
    NHẤT mà vẫn thoả ràng buộc. Đây là phiên bản trung thực của Fellegi-Holt
    kinh điển — nó không bị thua oan chỉ vì giá trị donor thô ngẫu nhiên
    không cân bảng.
    """
    bat_dau = time.perf_counter()

    thieu = [ten for ten in field_order if values.get(ten) is None]
    if thieu:
        return Diagnosis(
            verdict="ABSTAIN",
            solve_time_s=time.perf_counter() - bat_dau,
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
        for cac_truong in combinations(range(n), k):
            if time.perf_counter() - bat_dau > time_limit_s:
                return Diagnosis(
                    verdict="ABSTAIN",
                    residual_before=residual_truoc,
                    solve_time_s=time.perf_counter() - bat_dau,
                    ly_do_abstain=f"hết {time_limit_s}s",
                )

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

            da_sua = {
                field_order[i]: Candidate(
                    value=float(x_moi[i]),
                    source="donor",
                    cost=abs(float(x_moi[i] - x[i])),
                    evidence={"donor": donor.get(field_order[i])},
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

    return Diagnosis(
        verdict="ABSTAIN",
        residual_before=residual_truoc,
        solve_time_s=time.perf_counter() - bat_dau,
        ly_do_abstain="không tập trường nào cho nghiệm trong trần thay đổi",
    )
