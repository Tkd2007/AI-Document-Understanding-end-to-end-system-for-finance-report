"""
Ma trận ràng buộc và phân tích identifiability.

Chuyển FIELD_IDENTITIES từ dạng khai báo sang ma trận A, để trả lời được
những câu mà dạng list tuple không trả lời được: lỗi ở trường nào phát hiện
được, định vị được, hay vô hình về nguyên lý.

NỀN TOÁN HỌC — quyết định cả cách viết bài lẫn cách đọc kết quả:

Mọi đẳng thức kế toán có dạng "tổng các thành phần trừ đi tổng bằng 0", nên
toàn bộ hệ là hệ THUẦN NHẤT: Ax = 0, vector b luôn bằng 0.

Gọi x* là giá trị thật (thoả Ax* = 0) và x̂ = x* + δ là giá trị trích xuất.
Residual:

    r = Ax̂ = A(x* + δ) = Ax* + Aδ = Aδ

Nên δ thuộc null(A) khi và chỉ khi lỗi đó VÔ HÌNH với mọi phương pháp dựa
trên ràng buộc. Không phải "khó phát hiện" — là không tồn tại thông tin để
phát hiện.

Hệ quả tức thì, đáng viết thành một mệnh đề trong paper: với δ = (c−1)x*
(tức đọc sai đơn vị, x̂ = c·x*), ta có Aδ = (c−1)Ax* = 0. SAI ĐƠN VỊ TOÀN
CỤC LUÔN VÔ HÌNH, chứng minh trong một dòng. Đó là lý do mỏ neo tuyệt đối
(dòng khai báo đơn vị ở header bảng, và TOTAL_ASSETS_BOUNDS) là bắt buộc
chứ không phải tuỳ chọn.

Chạy trực tiếp để sinh báo cáo cho cả hai chuẩn:

    python src/constraints.py
"""

import sys
from itertools import combinations
from pathlib import Path

import numpy as np

from fields_config import QuyUocDau, Standard, fields_for, identities_for

# Dung sai đặt TƯỜNG MINH thay vì để numpy tự chọn.
#
# np.linalg.matrix_rank mặc định dùng tol phụ thuộc kích thước ma trận và
# giá trị kỳ dị lớn nhất. Với ma trận toàn 0 và ±1 thì mọi giá trị kỳ dị
# khác 0 đều cỡ đơn vị, nên một ngưỡng cố định vừa đủ nhỏ là chặt chẽ hơn
# và quan trọng hơn là ỔN ĐỊNH — kết quả identifiability không được đổi chỉ
# vì có ai đó thêm một đẳng thức làm ma trận to ra.
TOL = 1e-10

# Trần số tập con được duyệt vét cạn trong minimal_localizing_set().
#
# 2^16 = 65536 tập con chạy trong khoảng một giây. Vượt trần thì chuyển
# sang tham lam và NÓI RÕ kết quả chỉ là cận trên, vì bài toán này là
# set-cover nên tham lam không đảm bảo tối ưu.
TRAN_VET_CAN = 2 ** 16


def build_matrix(
    fields: list[str],
    identities: list,
) -> tuple[np.ndarray, list[str]]:
    """
    Dựng ma trận A từ khai báo đẳng thức.

    Trả về (A, field_order). A có shape (số_đẳng_thức_dùng_được, số_field).
    Mỗi dòng: +1 ở các field thành phần, −1 ở field tổng, 0 còn lại.

    field_order được trả về TƯỜNG MINH để mọi hàm dưới đây nói cùng một
    thứ tự cột. Nhầm thứ tự cột là loại lỗi im lặng nguy hiểm nhất ở đây:
    nó không làm gì nổ, chỉ gán kết luận của field này cho field khác.

    Đẳng thức nào có field KHÔNG nằm trong `fields` thì bị BỎ, không phải
    bị coi như hệ số 0. Lý do: không trích một chỉ tiêu thì không kiểm được
    đẳng thức chứa nó — coi nó bằng 0 sẽ dựng ra một ràng buộc sai và làm
    hạng cao lên một cách giả tạo, tức là báo cáo lạc quan hơn sự thật về
    khả năng định vị.
    """
    field_order = list(fields)
    vi_tri = {ten: i for i, ten in enumerate(field_order)}

    cac_dong = []
    for parts, total, _ in identities:
        lien_quan = [*parts, total]
        if any(ten not in vi_tri for ten in lien_quan):
            continue

        dong = np.zeros(len(field_order))
        for ten in parts:
            dong[vi_tri[ten]] += 1.0
        dong[vi_tri[total]] -= 1.0
        cac_dong.append(dong)

    if not cac_dong:
        return np.zeros((0, len(field_order))), field_order

    return np.vstack(cac_dong), field_order


def rank(A: np.ndarray) -> int:
    """Hạng của A. Ma trận không có dòng nào thì hạng 0."""
    if A.shape[0] == 0:
        return 0
    return int(np.linalg.matrix_rank(A, tol=TOL))


def null_space(A: np.ndarray, tol: float = TOL) -> np.ndarray:
    """
    Cơ sở trực chuẩn của null(A), shape (n_fields, dim_null).

    Dùng SVD: vector kỳ dị nào ứng với giá trị kỳ dị nhỏ hơn tol thì nằm
    trong không gian null. Không dùng khử Gauss vì nó nhạy với sai số làm
    tròn theo cách khó đoán, còn ở đây kết luận "chiều này vô hình" phải
    đáng tin.
    """
    n = A.shape[1]
    if n == 0:
        return np.zeros((0, 0))
    if A.shape[0] == 0:
        # Không ràng buộc nào -> mọi hướng lỗi đều vô hình.
        return np.eye(n)

    _, gia_tri_ky_di, vh = np.linalg.svd(A)

    day_du = np.zeros(n)
    day_du[: len(gia_tri_ky_di)] = gia_tri_ky_di

    return vh[day_du <= tol].T


def scale_direction_in_null(A: np.ndarray, x_ref: np.ndarray, tol: float = 1e-9) -> bool:
    """
    Hướng sai-đơn-vị có nằm trong null(A) không?

    Về lý thuyết LUÔN True với hệ thuần nhất, vì δ = (c−1)x* và Ax* = 0.
    Hàm này tồn tại như một ASSERT CHẠY ĐƯỢC: trả False nghĩa là ma trận
    dựng sai (sai dấu, sai thứ tự cột, sót một hệ số), KHÔNG phải lý thuyết
    sai. Đây là lưới an toàn rẻ nhất cho đúng chỗ mà spec đã cảnh báo là
    người dùng phải tự kiểm.

    So trên chuẩn TƯƠNG ĐỐI: giá trị thật cỡ 1e13 nên sai số dấu phẩy động
    tuyệt đối cũng cỡ lớn, dùng ngưỡng tuyệt đối sẽ báo sai.
    """
    if A.shape[0] == 0:
        return True

    do_lon = np.linalg.norm(x_ref)
    if do_lon == 0:
        return True

    return bool(np.linalg.norm(A @ x_ref) / do_lon <= tol)


def _cot_khac_khong(A: np.ndarray, i: int, tol: float = TOL) -> bool:
    return bool(np.linalg.norm(A[:, i]) > tol)


def _ty_le_voi_nhau(A: np.ndarray, i: int, j: int, tol: float = TOL) -> bool:
    """Hai cột có tỷ lệ với nhau không (kể cả tỷ lệ âm)?"""
    ci, cj = A[:, i], A[:, j]
    chuan_i, chuan_j = np.linalg.norm(ci), np.linalg.norm(cj)

    if chuan_i <= tol or chuan_j <= tol:
        return False

    don_vi_i, don_vi_j = ci / chuan_i, cj / chuan_j

    return bool(
        np.linalg.norm(don_vi_i - don_vi_j) <= tol
        or np.linalg.norm(don_vi_i + don_vi_j) <= tol
    )


def collinear_columns(
    A: np.ndarray, field_order: list[str], tol: float = TOL
) -> list[tuple[str, str]]:
    """
    Các cặp field mà cột của chúng trong A tỷ lệ với nhau.

    Lỗi ở hai field như vậy sinh ra residual pattern KHÔNG PHÂN BIỆT ĐƯỢC:
    lỗi d ở field i cho residual d·A[:,i], và nếu A[:,j] = k·A[:,i] thì lỗi
    d/k ở field j cho đúng residual đó. Mọi thuật toán định vị đều bất lực,
    không phải vì thuật toán yếu mà vì thông tin không tồn tại. Đây là kết
    quả cốt lõi của H0.

    Cột toàn 0 bị LOẠI khỏi kết quả, dù về hình thức nó tỷ lệ với mọi cột.
    Field cột 0 không phải "khó phân biệt với field khác" mà là "không được
    ràng buộc nào bảo vệ" — một tình trạng khác hẳn, báo riêng ở
    zero_columns().
    """
    cap = []
    for i, j in combinations(range(len(field_order)), 2):
        if _ty_le_voi_nhau(A, i, j, tol):
            cap.append((field_order[i], field_order[j]))
    return cap


def zero_columns(A: np.ndarray, field_order: list[str], tol: float = TOL) -> list[str]:
    """
    Các field không tham gia đẳng thức nào.

    Đây là tình trạng NẶNG HƠN việc không định vị được: lỗi ở field cột 0
    cho residual đúng bằng 0, nên nó không phát hiện được chứ không chỉ là
    không định vị được. Ràng buộc kế toán hoàn toàn không bảo vệ nó.
    """
    if A.shape[0] == 0:
        return list(field_order)

    return [ten for i, ten in enumerate(field_order) if not _cot_khac_khong(A, i, tol)]


def single_field_localizable(
    A: np.ndarray, field_order: list[str], tol: float = TOL
) -> dict[str, bool]:
    """
    Với mỗi field, lỗi chỉ ở field đó có định vị được không?

    Định vị được khi và chỉ khi cột i khác 0 VÀ không tỷ lệ với cột j nào
    khác. Cột khác 0 cho phép PHÁT HIỆN; không tỷ lệ với cột nào cho phép
    ĐỊNH VỊ. Thiếu điều kiện nào cũng đủ để mất khả năng định vị.
    """
    ket_qua = {}
    for i, ten in enumerate(field_order):
        if not _cot_khac_khong(A, i, tol):
            ket_qua[ten] = False
            continue

        ket_qua[ten] = not any(
            _ty_le_voi_nhau(A, i, j, tol) for j in range(len(field_order)) if j != i
        )
    return ket_qua


def _moi_field_deu_dinh_vi_duoc(fields: list[str], identities: list) -> bool:
    if not fields:
        return False

    A, field_order = build_matrix(fields, identities)
    return all(single_field_localizable(A, field_order).values())


def minimal_localizing_set(
    candidate_fields: list[str],
    identities: list,
    must_include: list[str] | None = None,
) -> tuple[list[str] | None, bool]:
    """
    Bộ field nhỏ nhất mà MỌI lỗi một-trường trong bộ đó đều định vị được.

    Trả về (bộ_field, la_toi_uu_chac_chan). bộ_field là None khi KHÔNG tồn
    tại bộ nào thoả — và None là một kết quả nghiên cứu hợp lệ, không phải
    lỗi: nó nói rằng với bộ đẳng thức hiện có thì không cách nào chọn tập
    con nào của các chỉ tiêu này để định vị được lỗi một-trường.

    Đây là ĐÁP ÁN ĐỊNH LƯỢNG cho câu hỏi "trích 11 field hay 30 field" —
    quyết định thường được đưa ra bằng cảm tính, và là thứ nhân lên chi phí
    gán nhãn tay, khoản đắt nhất của cả dự án.

    must_include: các field bắt buộc phải có vì chúng là đầu ra người dùng
    cần, bất kể chúng có giúp định vị hay không.

    Vét cạn theo kích thước tăng dần khi số tập con còn trong TRAN_VET_CAN,
    nếu không thì tham lam và trả la_toi_uu_chac_chan=False. Bài toán này
    có dạng set-cover nên tham lam chỉ cho CẬN TRÊN, và gọi cận trên là
    "bộ tối thiểu" thì con số chi phí gán nhãn suy ra từ nó sẽ sai.
    """
    bat_buoc = list(must_include or [])
    con_lai = [ten for ten in candidate_fields if ten not in bat_buoc]

    if _moi_field_deu_dinh_vi_duoc(bat_buoc, identities):
        return bat_buoc, True

    if 2 ** len(con_lai) <= TRAN_VET_CAN:
        for so_them in range(1, len(con_lai) + 1):
            for them in combinations(con_lai, so_them):
                ung_vien = bat_buoc + list(them)
                if _moi_field_deu_dinh_vi_duoc(ung_vien, identities):
                    return ung_vien, True
        return None, True

    # Tham lam: mỗi vòng thêm field làm tăng nhiều nhất số field định vị được.
    hien_tai = list(bat_buoc)
    for _ in range(len(con_lai)):
        tot_nhat, diem_tot_nhat = None, -1
        for ten in con_lai:
            if ten in hien_tai:
                continue
            thu = hien_tai + [ten]
            A, field_order = build_matrix(thu, identities)
            diem = sum(single_field_localizable(A, field_order).values())
            if diem > diem_tot_nhat:
                tot_nhat, diem_tot_nhat = ten, diem

        if tot_nhat is None:
            break
        hien_tai.append(tot_nhat)

        if _moi_field_deu_dinh_vi_duoc(hien_tai, identities):
            return hien_tai, False

    return None, False


def _bang_ma_tran(A: np.ndarray, field_order: list[str], identities: list) -> list[str]:
    """Ma trận dạng bảng markdown, tên field làm tiêu đề cột."""
    mo_ta = [
        mo_ta_i
        for parts, total, mo_ta_i in identities
        if all(ten in field_order for ten in [*parts, total])
    ]

    dong = ["| Đẳng thức | " + " | ".join(field_order) + " |"]
    dong.append("|---" * (len(field_order) + 1) + "|")

    for i in range(A.shape[0]):
        o = " | ".join(f"{int(gia_tri):+d}" if gia_tri else "." for gia_tri in A[i])
        nhan = mo_ta[i] if i < len(mo_ta) else f"(đẳng thức {i})"
        dong.append(f"| {nhan} | {o} |")

    return dong


def report(
    A: np.ndarray,
    field_order: list[str],
    identities: list,
    tieu_de: str = "Identifiability",
    out_path: str | Path | None = None,
) -> str:
    """
    Sinh báo cáo người đọc được: hạng, chiều null, cơ sở null kèm tên field,
    cặp cột tỷ lệ, bảng định vị từng field.

    ĐÂY LÀ ARTIFACT NGƯỜI DÙNG PHẢI ĐỌC VÀ ĐỐI CHIẾU VỚI THÔNG TƯ. Sai một
    dấu trong ma trận là toàn bộ kết quả identifiability sai mà không có gì
    báo, nên ma trận được in ở dạng bảng có tên field làm tiêu đề cột để
    dò bằng mắt được.
    """
    n = len(field_order)
    hang = rank(A)
    co_so_null = null_space(A)
    chieu_null = co_so_null.shape[1] if co_so_null.size else n - hang

    dinh_vi = single_field_localizable(A, field_order)
    cot_khong = zero_columns(A, field_order)
    cap_ty_le = collinear_columns(A, field_order)

    dong = [
        f"# {tieu_de}",
        "",
        "> Sinh tự động bởi `src/constraints.py`. Đối chiếu bảng ma trận bên dưới",
        "> với Phụ lục của Thông tư trước khi tin vào bất kỳ con số nào ở đây.",
        "",
        "## Tổng quan",
        "",
        f"- Số chỉ tiêu (n): **{n}**",
        f"- Số đẳng thức dùng được: **{A.shape[0]}**",
        f"- Hạng `rank(A)`: **{hang}**",
        f"- Chiều không gian null `dim null(A)`: **{chieu_null}**",
        f"- Số field định vị được lỗi một-trường: "
        f"**{sum(dinh_vi.values())} / {n}**",
        # Nêu tường minh cả khi bằng 0. Trước đây con số này chỉ hiện ra gián
        # tiếp qua ghi chú từng dòng của bảng bên dưới, nên một bộ chỉ tiêu
        # KHÔNG còn field vô hình và một báo cáo quên mất phần đó trông giống
        # hệt nhau. Đây là chỉ số nặng hơn "định vị được": cột toàn 0 nghĩa là
        # lỗi vô hình với cả H1 lẫn H2, chứ không riêng H2.
        f"- Số field có **cột toàn 0** (lỗi không PHÁT HIỆN được): "
        f"**{len(cot_khong)} / {n}**"
        + (f" — {', '.join(f'`{t}`' for t in cot_khong)}" if cot_khong else " — không có"),
        "",
        f"Nghĩa là **{chieu_null}/{n}** chiều trong không gian lỗi hoàn toàn vô hình",
        "với mọi phương pháp dựa trên ràng buộc — residual bằng 0 tuyệt đối.",
        "",
        "## Ma trận ràng buộc A",
        "",
        "Mỗi dòng một đẳng thức, `+1` cho thành phần, `-1` cho tổng, `.` cho 0.",
        "",
        *_bang_ma_tran(A, field_order, identities),
        "",
        "## Định vị lỗi một-trường",
        "",
        "Định vị được khi cột của field khác 0 **và** không tỷ lệ với cột nào khác.",
        "",
        "| Chỉ tiêu | Cột trong A | Định vị được | Ghi chú |",
        "|---|---|---|---|",
    ]

    for i, ten in enumerate(field_order):
        cot = " ".join(f"{int(v):+d}" if v else "0" for v in A[:, i]) if A.shape[0] else "(rỗng)"
        if ten in cot_khong:
            ghi_chu = "**cột toàn 0 — không ràng buộc nào bảo vệ, lỗi không PHÁT HIỆN được**"
        elif not dinh_vi[ten]:
            trung = sorted({b if a == ten else a for a, b in cap_ty_le if ten in (a, b)})
            ghi_chu = f"cột tỷ lệ với: {', '.join(trung)}"
        else:
            ghi_chu = "cột riêng biệt"
        dong.append(f"| `{ten}` | `{cot}` | {'có' if dinh_vi[ten] else 'KHÔNG'} | {ghi_chu} |")

    dong += [
        "",
        "## Cặp chỉ tiêu không phân biệt được",
        "",
    ]
    if cap_ty_le:
        dong.append("Lỗi ở hai chỉ tiêu trong cùng một cặp cho residual pattern giống hệt nhau.")
        dong.append("")
        for a, b in cap_ty_le:
            dong.append(f"- `{a}` ↔ `{b}`")
    else:
        dong.append("Không có cặp nào — mọi chỉ tiêu có cột riêng biệt.")

    dong += [
        "",
        "## Cơ sở không gian null",
        "",
        "Mỗi vector dưới đây là một hướng lỗi mà residual không nhìn thấy.",
        "",
    ]
    if chieu_null == 0:
        dong.append("Không gian null rỗng — mọi hướng lỗi đều để lại residual.")
    else:
        for j in range(co_so_null.shape[1]):
            thanh_phan = [
                f"{co_so_null[i, j]:+.3f}·`{field_order[i]}`"
                for i in range(n)
                if abs(co_so_null[i, j]) > 1e-8
            ]
            dong.append(f"{j + 1}. " + "  ".join(thanh_phan))

    noi_dung = "\n".join(dong) + "\n"

    if out_path is not None:
        duong_dan = Path(out_path)
        duong_dan.parent.mkdir(parents=True, exist_ok=True)
        duong_dan.write_text(noi_dung, encoding="utf-8")

    return noi_dung


if __name__ == "__main__":
    # Console Windows mặc định cp1252 nên in tiếng Việt sẽ nổ
    # UnicodeEncodeError. Ép utf-8 để lệnh này chạy được ở mọi terminal.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    for chuan in Standard:
        cac_field = fields_for(chuan)
        # Báo cáo dựng trên quy ước TỔNG, nhưng phần bất biến dưới đây được
        # KIỂM LẠI mỗi lần chạy chứ không chép từ trí nhớ: nếu một ngày nào đó
        # hai quy ước cho kết quả khác nhau thì câu khẳng định in trong báo cáo
        # phải sai theo, chứ không được đứng yên nói điều không còn đúng.
        so_do = {}
        for quy_uoc in (QuyUocDau.TONG, QuyUocDau.TRU):
            A_q, thu_tu_q = build_matrix(cac_field, identities_for(chuan, quy_uoc))
            so_do[quy_uoc] = (
                rank(A_q),
                null_space(A_q).shape[1],
                sorted(k for k, v in single_field_localizable(A_q, thu_tu_q).items() if v),
                sorted(tuple(sorted(c)) for c in collinear_columns(A_q, thu_tu_q)),
            )
        bat_bien = so_do[QuyUocDau.TONG] == so_do[QuyUocDau.TRU]

        A, field_order = build_matrix(cac_field, identities_for(chuan, QuyUocDau.TONG))

        duong_dan = Path("data/output") / f"identifiability_{chuan.value}.md"
        noi_dung = report(
            A,
            field_order,
            identities_for(chuan, QuyUocDau.TONG),
            tieu_de=f"Identifiability — chuẩn {chuan.value}",
        )
        noi_dung += (
            """
## Bất biến với quy ước dấu

Ma trận trên dựng ở quy ước `tong`. Dựng lại ở quy ước `tru` cho ra """
            + ("**cùng** " if bat_bien else "**KHÁC** ")
            + """hạng, cùng số chiều không gian null, cùng danh sách chỉ tiêu
định vị được và cùng danh sách cặp không phân biệt được — so từng phần tử chứ
không chỉ so số đếm.

Lý do: đổi quy ước chỉ lật dấu vài cột của `A`, mà hạng, không gian null và
quan hệ tỷ lệ giữa các cột đều bất biến với phép lật ấy. Câu này được KIỂM LẠI
mỗi lần sinh báo cáo, không chép từ trí nhớ.
"""
        )
        duong_dan.parent.mkdir(parents=True, exist_ok=True)
        duong_dan.write_text(noi_dung, encoding="utf-8")

        print(noi_dung)
        print(f"--- Đã ghi: {duong_dan} ---\n")
