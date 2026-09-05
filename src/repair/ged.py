"""
BASELINE 7 — kiểm định GED cổ điển: parity space và tỷ số hợp lý tổng quát.

`PREREGISTRATION.md` phần H2 gọi đây là **baseline bắt buộc**: "ít nhất một
GED test cổ điển (parity space hoặc generalized likelihood ratio), không chỉ
L1". Lý do nó bắt buộc chứ không tuỳ chọn: H2 là giả thuyết về ĐỊNH VỊ lỗi,
mà ngành data reconciliation đã định vị lỗi thô bằng phần dư từ trước khi có
học sâu. Chỉ có baseline 8 (L1, hướng compressed sensing) là so với đúng một
trong hai truyền thống, và người phản biện đến từ truyền thống còn lại sẽ hỏi.

THUẬT NGỮ, vì bài viết bằng tiếng Anh:

  * *gross error detection* (GED) — phát hiện lỗi thô, tức sai lệch lớn bất
    thường chứ không phải nhiễu đo thông thường.
  * *parity space* — không gian phần dư. Với hệ ràng buộc `A·x = 0`, phần dư
    `r = A·x` nằm trong một không gian mà mỗi lỗi một-trường sinh ra đúng một
    HƯỚNG cố định: lỗi độ lớn `δ` ở field `j` cho `r = δ·A[:, j]`. Định vị lỗi
    vì vậy quy về bài toán so hướng, và cột `A[:, j]` gọi là *fault direction*.
  * *generalized likelihood ratio* (GLR) — tỷ số hợp lý tổng quát. Dưới giả
    thiết đúng một field sai, ước lượng hợp lý cực đại của `δ` ở field `j` là
    phép chiếu phần dư lên cột `j`, và thống kê kiểm định là bình phương độ
    dài phép chiếu ấy. Xếp hạng theo thống kê đó chính là xếp hạng nghi ngờ.

NÓ KHÔNG SỬA, VÀ ĐÓ LÀ CHỦ Ý. Kiểm định GED trả về một BẢNG XẾP HẠNG mức nghi
ngờ — đúng thứ `eval.metrics.localization_top_k` nhận vào. Cho nó sửa luôn là
dựng lại baseline 8 dưới một cái tên khác, và H2 mất đối chứng thuần định vị.
Vì thế hàm ở đây trả `KetQuaGED` chứ không trả `Diagnosis`, và cố ý KHÔNG nhận
tham số `candidates`: nó không thể hoán đổi với họ `diagnose_*` bằng một cờ,
nên giả vờ cùng chữ ký chỉ tổ làm runner tưởng hoán đổi được.
"""

from dataclasses import dataclass, field
from typing import Literal

import numpy as np

# Dung sai phần dư, tính theo tỷ lệ trên độ lớn vector giá trị.
#
# Lấy đúng con số và đúng cách tính của `repair.diagnose.RESIDUAL_TOL`, không
# đặt ngưỡng riêng: hai baseline phải đồng ý với nhau ở câu hỏi "tài liệu này
# có lỗi không" thì hiệu số giữa chúng mới đo được việc ĐỊNH VỊ. Ngưỡng lệch
# nhau sẽ làm hai bên chấm trên hai tập tài liệu khác nhau mà bảng kết quả
# không có chỗ nào lộ ra điều đó.
RESIDUAL_TOL = 1e-9

# Dung sai coi hai thống kê là BẰNG NHAU khi gom nhóm đồng hạng.
#
# Đồng hạng ở đây không phải trùng hợp số học mà là hệ quả cấu trúc: hai field
# có cột tỷ lệ với nhau thì mọi phần dư đều cho cùng thống kê, nên không kiểm
# định nào tách nổi chúng. So bằng dấu `==` trên số thực sẽ bỏ sót đúng những
# nhóm ấy vì sai số dấu phẩy động, tức giấu mất trần định vị.
TOL_DONG_HANG = 1e-9

# Phân loại lý do kiểm định không cho ra bảng xếp hạng, tập ĐÓNG.
#
#   ""                 — chạy được, có phát hiện, bảng xếp hạng dùng được.
#   khong_phat_hien    — kiểm định toàn cục nói phần dư đã bằng 0. KHÔNG có
#                        gì để định vị, và đây là một KẾT LUẬN chứ không phải
#                        một thất bại: hoặc tài liệu đúng, hoặc lỗi của nó nằm
#                        trong không gian null của A và vô hình với mọi phương
#                        pháp dựa trên ràng buộc.
#   thieu_gia_tri      — không dựng được vector nên không tính được phần dư.
#
# Tách `khong_phat_hien` khỏi `thieu_gia_tri` vì bảng kết quả phải đếm riêng:
# ca đầu là giới hạn của RÀNG BUỘC, ca sau là giới hạn của khâu TRÍCH XUẤT.
LyDoGED = Literal["", "khong_phat_hien", "thieu_gia_tri"]


@dataclass
class KetQuaGED:
    """Kết quả kiểm định GED trên một tài liệu."""

    # Kiểm định toàn cục (*global test*): có lỗi thô nào không.
    phat_hien: bool
    # γ = ‖r‖². Đơn vị là bình phương đơn vị tiền, nên so được GIỮA các field
    # trong cùng tài liệu chứ KHÔNG so được giữa hai tài liệu khác quy mô.
    thong_ke_toan_cuc: float = 0.0
    # Field xếp theo mức nghi ngờ GIẢM DẦN. Chỉ chứa field phát hiện được.
    xep_hang: list[str] = field(default_factory=list)
    # T_j của từng field phát hiện được.
    thong_ke: dict[str, float] = field(default_factory=dict)
    # δ̂_j — độ lệch ước lượng nếu field j là field sai duy nhất. Quy ước dấu:
    # δ̂ là ĐỘ LỆCH CỦA GIÁ TRỊ ĐANG CÓ, nên `values[j] − δ̂_j` mới là giá trị
    # làm phần dư về 0. Ghi rõ ở đây vì dấu ngược lại cũng "hợp lý" như nhau
    # khi đọc công thức, và nhầm dấu thì không có gì nổ — chỉ ra một con số
    # sai gấp đôi độ lệch.
    #
    # Ghi ra dù bảng xếp hạng không dùng tới, vì nó là chỗ baseline này khác
    # phương pháp đề xuất rõ nhất: δ̂ là một số LIÊN TỤC nặn cho khớp phương
    # trình, không neo vào bất kỳ cách đọc nào của tờ giấy.
    do_lech_uoc_luong: dict[str, float] = field(default_factory=dict)
    # Các nhóm field có thống kê bằng nhau, cỡ từ 2 trở lên, trong số field
    # có thống kê dương. Đây là TRẦN ĐỊNH VỊ của kiểm định, phải ghi tường
    # minh — xem `_gom_dong_hang`.
    nhom_dong_hang: list[list[str]] = field(default_factory=list)
    # Field có cột toàn 0 trong A: lỗi ở đó không đổi phần dư nên không kiểm
    # định nào dựa trên ràng buộc phát hiện được.
    khong_phat_hien_duoc: list[str] = field(default_factory=list)
    ma_ly_do: LyDoGED = ""
    ly_do: str = ""


def _gom_dong_hang(
    xep_hang: list[str],
    thong_ke: dict[str, float],
    tol: float,
) -> list[list[str]]:
    """
    Gom các field mà kiểm định KHÔNG tách nổi nhau.

    Chỉ gom trong số field có thống kê dương. Đồng hạng ở mức 0 nghĩa là cả
    nhóm cùng trực giao với phần dư, tức cùng được kiểm định loại trừ — đó là
    sự đồng thuận chứ không phải sự mơ hồ, và đưa nó vào bảng trần định vị sẽ
    thổi phồng trần lên bằng gần trọn bộ chỉ tiêu.
    """
    nhom: list[list[str]] = []
    hien_tai: list[str] = []

    for ten in xep_hang:
        if thong_ke[ten] <= 0.0:
            break

        if hien_tai and abs(thong_ke[ten] - thong_ke[hien_tai[0]]) <= tol * max(
            abs(thong_ke[hien_tai[0]]), 1.0
        ):
            hien_tai.append(ten)
            continue

        if len(hien_tai) >= 2:
            nhom.append(hien_tai)
        hien_tai = [ten]

    if len(hien_tai) >= 2:
        nhom.append(hien_tai)

    return nhom


def dinh_vi_ged(
    values: dict,
    A: np.ndarray,
    field_order: list,
    tolerance_ratio: float = RESIDUAL_TOL,
    tol_dong_hang: float = TOL_DONG_HANG,
) -> KetQuaGED:
    """
    BASELINE 7 — xếp hạng nghi ngờ bằng GLR một-lỗi trên không gian phần dư.

    Với `r = A·x` và `a_j = A[:, j]`, giả thiết "chỉ field j sai" cho

        δ̂_j = (a_jᵀ·r) / (a_jᵀ·a_j)        — độ lệch hợp lý cực đại
        T_j  = (a_jᵀ·r)² / (a_jᵀ·a_j)       — thống kê kiểm định

    và xếp hạng theo `T_j` giảm dần. Vì `‖r‖²` như nhau với mọi j, xếp hạng
    này trùng với xếp hạng theo góc giữa phần dư và hướng lỗi của từng field —
    tức đúng phát biểu parity space, chỉ khác cách viết.

    MA TRẬN HIỆP PHƯƠNG SAI ĐỂ LÀ ĐƠN VỊ, và đây là một HẠN CHẾ phải nói ra
    trong bài chứ không phải một chi tiết cài đặt. Công thức gốc của ngành
    chuẩn hoá theo `V`, hiệp phương sai sai số ĐO. Ở đây không có mô hình sai
    số đo nào cả: một con số trên báo cáo tài chính hoặc đọc đúng hoặc đọc
    sai, và các đẳng thức kế toán đúng tuyệt đối chứ không đúng trong sai số.
    Bịa ra một `V` để công thức trông giống sách là đưa vào một tham số không
    ai kiểm chứng được, và tham số đó sẽ lặng lẽ quyết định thứ hạng. Để `V`
    là đơn vị thì `a_jᵀ·a_j` chính là SỐ ĐẲNG THỨC mà field j tham gia, nên
    phép chuẩn hoá còn lại vẫn có nghĩa: field xuất hiện trong nhiều đẳng thức
    phải khớp hướng chặt hơn mới được xếp cao.

    Thiếu bất kỳ giá trị nào thì ABSTAIN thay vì đoán, giống hệt baseline 8:
    hai baseline phải cùng bỏ qua một tập tài liệu thì hiệu số giữa chúng mới
    đo được cái cần đo.
    """
    thieu = [ten for ten in field_order if values.get(ten) is None]
    if thieu:
        return KetQuaGED(
            phat_hien=False,
            ma_ly_do="thieu_gia_tri",
            ly_do=f"thiếu giá trị cho: {', '.join(thieu)}",
        )

    x = np.array([values[ten] for ten in field_order], dtype=float)
    r = A @ x
    do_lon = float(np.linalg.norm(x)) or 1.0
    thong_ke_toan_cuc = float(r @ r)

    # Field có cột toàn 0 được tách ra TRƯỚC khi xét phát hiện, vì danh sách
    # này là tính chất của ma trận ràng buộc chứ không phải của tài liệu — nó
    # đúng kể cả khi kiểm định toàn cục không phát hiện gì.
    chuan_cot = np.einsum("ij,ij->j", A, A)
    khong_phat_hien_duoc = [
        ten for j, ten in enumerate(field_order) if chuan_cot[j] <= 0.0
    ]

    if np.linalg.norm(r) / do_lon <= tolerance_ratio:
        return KetQuaGED(
            phat_hien=False,
            thong_ke_toan_cuc=thong_ke_toan_cuc,
            khong_phat_hien_duoc=khong_phat_hien_duoc,
            ma_ly_do="khong_phat_hien",
            ly_do="phần dư bằng 0 — không có lỗi thô nào để định vị",
        )

    chieu = A.T @ r
    thong_ke: dict[str, float] = {}
    do_lech: dict[str, float] = {}

    for j, ten in enumerate(field_order):
        if chuan_cot[j] <= 0.0:
            continue
        thong_ke[ten] = float(chieu[j] ** 2 / chuan_cot[j])
        do_lech[ten] = float(chieu[j] / chuan_cot[j])

    # Sắp xếp ỔN ĐỊNH nên field đồng hạng giữ nguyên thứ tự của `field_order`.
    #
    # Đây là một quy ước phá hoà, và nó phải là quy ước CỐ ĐỊNH VÀ MÙ VỚI ĐÁP
    # ÁN chứ không phải thứ tự tình cờ mà `argsort` trả về: Top-1 của một nhóm
    # đồng hạng khi đó do đúng quy ước này quyết định, và một quy ước đổi theo
    # cài đặt của numpy sẽ làm con số Top-1 không tái lập được. Nhóm đồng hạng
    # được ghi riêng ở `nhom_dong_hang` để bảng kết quả nói được rằng thứ hạng
    # trong nhóm là do quy ước, không do bằng chứng.
    xep_hang = sorted(thong_ke, key=lambda ten: -thong_ke[ten])

    return KetQuaGED(
        phat_hien=True,
        thong_ke_toan_cuc=thong_ke_toan_cuc,
        xep_hang=xep_hang,
        thong_ke=thong_ke,
        do_lech_uoc_luong=do_lech,
        nhom_dong_hang=_gom_dong_hang(xep_hang, thong_ke, tol_dong_hang),
        khong_phat_hien_duoc=khong_phat_hien_duoc,
    )
