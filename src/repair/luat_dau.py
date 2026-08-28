"""
Định vị lỗi ĐẢO DẤU bằng residual, không cần tìm kiếm tổ hợp.

VÌ SAO LUẬT NÀY LÀ HỆ QUẢ TẤT YẾU, KHÔNG PHẢI HEURISTIC. Nếu chỉ tiêu j bị
đọc lộn dấu thì `x̂ⱼ = −x*ⱼ`, tức chênh lệch `δⱼ = x̂ⱼ − x*ⱼ = 2x̂ⱼ`. Residual
của hệ vì thế bằng đúng `A·δ = 2x̂ⱼ·A[:, j]` — một bội số của CỘT j, với hệ
số là hai lần chính con số đang cầm trong tay. Lật dấu j lại đưa residual về
đúng 0. Đây cùng loại lập luận với chứng minh `Aδ = (c−1)Ax* = 0` ở
`constraints.py` (sai đơn vị toàn cục luôn vô hình), chỉ khác chiều: ở đó
chênh lệch nằm TRỌN trong không gian null nên vô hình, còn ở đây nó nằm trọn
trên MỘT cột nên nhìn thấy được và chỉ đúng tên được.

Hệ quả thực hành: một luật định vị **chứng minh được** cho đúng một chế độ
lỗi. Nó không đoán, nên khi im lặng thì im lặng có nghĩa.

VÌ SAO LUẬT NẰM Ở ĐÂY CHỨ KHÔNG NẰM Ở `chuan_hoa_dau()` HAY
`validate_result()`. Đưa nó vào tầng trích xuất thì MỌI kết quả đầu ra đều
thoả những đẳng thức nó chạm tới, và phép đo H1 — so vi phạm ràng buộc với
confidence của model như hai bộ dự báo lỗi — mất sạch tín hiệu trên chính
những đẳng thức ấy, vì tín hiệu bị chính bước trích xuất làm phẳng. Đó là lý
do `tests/test_chuan_hoa_dau.py` khoá tính chất "không giải đẳng thức mã 60
để chọn dấu". Luật này sống ở tầng repair, tức SAU khi H1 đã đo xong, và chỉ
chạy khi cờ tầng repair được bật tường minh.

GIỚI HẠN, ĐO ĐƯỢC, phải nói kèm mỗi lần trích dẫn: luật chỉ bắt được lỗi
DẤU. Nó im lặng ở lỗi nhầm chữ số, nhầm ô, và — quan trọng nhất — ở lỗi CHỌN
NHẦM BẢNG, vì bộ số lấy từ một bảng khác tự nó cũng cân nên `residual = 0`
tuyệt đối và chênh lệch nằm trọn trong không gian null. Không luật nào bắt
được ca đó, không phải vì thuật toán yếu mà vì thông tin không tồn tại.
"""

from dataclasses import dataclass, field
from typing import Literal

import numpy as np

# Dung sai residual, cùng định nghĩa và cùng giá trị với diagnose.RESIDUAL_TOL:
# tỷ lệ trên độ lớn vector giá trị, vì giá trị cỡ 1e13 thì sai số dấu phẩy
# động tuyệt đối cũng cỡ lớn. Khai lại ở đây thay vì import để module này
# không phụ thuộc ngược vào diagnose — có test chốt hai hằng số bằng nhau.
RESIDUAL_TOL = 1e-9

# Trạng thái đi ra, tập ĐÓNG. Mỗi trạng thái mang một kết luận khác hẳn nhau
# và bảng kết quả phải đếm chúng RIÊNG — gộp lại là tính công cho luật ở
# những ca nó không kết luận được gì.
#
#   khong_co_lech  — residual đã bằng 0. Không có gì để định vị. KHÔNG đồng
#                    nghĩa với "không có lỗi": lỗi nằm trong không gian null
#                    (sai đơn vị toàn cục, chọn nhầm bảng) cũng cho ra đây.
#   dinh_vi_duoc   — ĐÚNG MỘT chỉ tiêu mà lật dấu đưa TOÀN BỘ residual về 0.
#                    Đây là ca duy nhất được phép sửa.
#   mo_ho          — nhiều hơn một chỉ tiêu cùng đưa toàn bộ residual về 0.
#                    Luật không phân xử; trả cả danh sách để tầng trên quyết.
#   nghi_ngo       — không chỉ tiêu nào đưa TOÀN BỘ residual về 0, nhưng có
#                    chỉ tiêu mà lật dấu làm cân MỌI đẳng thức chứa nó. Nghĩa
#                    là: chỉ tiêu ấy đúng là lộn dấu, VÀ tài liệu còn lỗi khác
#                    ở những đẳng thức không chứa nó. Chẩn đoán thì dùng được,
#                    sửa thì KHÔNG — sửa nó xong bảng vẫn không cân, nên
#                    không có gì xác nhận phép sửa là đúng.
#   im_lang        — không chỉ tiêu nào giải thích được. Đây là ca luật nói
#                    "đây KHÔNG phải lỗi dấu", và đó là thông tin thật.
#   thieu_gia_tri  — không dựng được vector nên không kiểm được gì.
TrangThaiLuatDau = Literal[
    "khong_co_lech",
    "dinh_vi_duoc",
    "mo_ho",
    "nghi_ngo",
    "im_lang",
    "thieu_gia_tri",
]


@dataclass
class KetQuaLuatDau:
    """Kết quả chạy luật dấu trên một bộ giá trị."""

    trang_thai: TrangThaiLuatDau
    # Tên chỉ tiêu bị lộn dấu. CHỈ có giá trị khi trang_thai == "dinh_vi_duoc";
    # ở "mo_ho" và "nghi_ngo" thì cố ý để None và đọc `cac_ung_vien` — luật
    # không được phép chọn bừa một ứng viên rồi trình bày như đã định vị.
    truong: str | None = None
    # Ứng viên tương ứng với `trang_thai`, xếp theo thứ tự field_order:
    # ứng viên TOÀN CỤC ở "dinh_vi_duoc"/"mo_ho", ứng viên CỤC BỘ ở "nghi_ngo".
    cac_ung_vien: list[str] = field(default_factory=list)
    # Giá trị SAU khi lật dấu, cho chỉ tiêu ở `truong`. None khi không định vị.
    gia_tri_sau: float | None = None
    thieu: list[str] = field(default_factory=list)
    # Số đẳng thức còn lệch sau khi đã tính tới mọi ứng viên cục bộ. Lớn hơn 0
    # ở "nghi_ngo" chính là bằng chứng tài liệu còn lỗi khác — con số này đi
    # thẳng vào certificate để người đọc biết phép sửa còn thiếu gì.
    so_dang_thuc_con_lech: int = 0

    @property
    def dinh_vi_duoc(self) -> bool:
        return self.trang_thai == "dinh_vi_duoc"


def luat_dau_residual(
    values: dict,
    A: np.ndarray,
    field_order: list[str],
    tolerance_ratio: float = RESIDUAL_TOL,
) -> KetQuaLuatDau:
    """
    Tìm chỉ tiêu mà LẬT DẤU đưa residual của cả hệ về 0.

    values: {tên field: giá trị}, đã quy đổi về đồng.
    A, field_order: ma trận ràng buộc, dựng bằng `constraints.build_matrix()`.

    HAI MỨC, và khoảng cách giữa chúng chính là chỗ luật này phải cẩn thận.

    Mức TOÀN CỤC — lật dấu j đưa cả vector residual về 0. Chỉ mức này mới cho
    `dinh_vi_duoc`, và chỉ nó mới được phép sửa: bảng cân lại sau phép sửa
    chính là thứ xác nhận phép sửa đúng.

    Mức CỤC BỘ — lật dấu j làm cân MỌI đẳng thức chứa j, nhưng vẫn còn đẳng
    thức khác lệch. Vì phép lật chỉ đụng tới những dòng có `A[i, j] ≠ 0`, các
    dòng còn lại lệch vì lỗi KHÁC, không phải vì j. Khẳng định về j vẫn chắc,
    khẳng định về tài liệu thì không — nên mức này trả `nghi_ngo` và tầng trên
    KHÔNG được sửa theo nó. Ca thật của dự án nằm đúng ở đây: MWG và VRE mỗi
    tài liệu lộn dấu ba dòng cùng lúc, nên không phép lật đơn lẻ nào làm cân
    được cả hệ.

    Điều KHÔNG bao giờ được nới: một chỉ tiêu mà lật dấu làm cân đẳng thức này
    nhưng làm vỡ đẳng thức kia thì KHÔNG phải ứng viên ở bất kỳ mức nào. Kiểm
    từng dòng rời rạc sẽ nhận nó, và đó đúng là loại ca nguy hiểm nhất — một
    sửa đổi hợp lý cục bộ mà sai toàn cục.

    Chỉ tiêu có giá trị 0 bị bỏ qua: lật dấu số 0 không đổi gì, nên nó "giải
    thích" được residual một cách vô nghĩa và sẽ đẻ ra ứng viên rác.
    """
    thieu = [ten for ten in field_order if values.get(ten) is None]
    if thieu:
        return KetQuaLuatDau(trang_thai="thieu_gia_tri", thieu=thieu)

    x = np.array([values[ten] for ten in field_order], dtype=float)
    residual = A @ x
    do_lon = float(np.linalg.norm(x)) or 1.0

    if float(np.linalg.norm(residual)) / do_lon <= tolerance_ratio:
        return KetQuaLuatDau(trang_thai="khong_co_lech")

    nguong = tolerance_ratio * do_lon
    toan_cuc, cuc_bo = [], []

    for j, ten in enumerate(field_order):
        if x[j] == 0.0:
            continue

        cot = A[:, j]
        # Lật dấu j đổi residual đúng bằng (−xⱼ − xⱼ)·A[:, j] = −2xⱼ·A[:, j].
        residual_sau = residual - 2.0 * x[j] * cot

        if float(np.linalg.norm(residual_sau)) <= nguong:
            toan_cuc.append(ten)
            cuc_bo.append(ten)
            continue

        # Ứng viên CỤC BỘ: mọi đẳng thức CHỨA j đều cân sau khi lật, còn các
        # đẳng thức không chứa j thì phép lật không đụng tới nên chúng lệch vì
        # lỗi khác. Điều kiện này vẫn là một khẳng định chắc chắn về j, chỉ
        # không phải một khẳng định về cả tài liệu.
        chua_j = np.abs(cot) > 0
        if chua_j.any() and float(np.linalg.norm(residual_sau[chua_j])) <= nguong:
            cuc_bo.append(ten)

    if toan_cuc:
        if len(toan_cuc) > 1:
            return KetQuaLuatDau(trang_thai="mo_ho", cac_ung_vien=toan_cuc)

        ten = toan_cuc[0]
        return KetQuaLuatDau(
            trang_thai="dinh_vi_duoc",
            truong=ten,
            cac_ung_vien=toan_cuc,
            gia_tri_sau=-float(values[ten]),
        )

    if cuc_bo:
        # Lật hết ứng viên cục bộ rồi đếm xem còn bao nhiêu đẳng thức lệch —
        # đó là phần lỗi KHÔNG phải lỗi dấu, và là lý do ca này không sửa được.
        x_thu = x.copy()
        for ten in cuc_bo:
            x_thu[field_order.index(ten)] = -x_thu[field_order.index(ten)]
        con_lech = int(np.sum(np.abs(A @ x_thu) > nguong))

        return KetQuaLuatDau(
            trang_thai="nghi_ngo",
            cac_ung_vien=cuc_bo,
            so_dang_thuc_con_lech=con_lech,
        )

    return KetQuaLuatDau(
        trang_thai="im_lang",
        so_dang_thuc_con_lech=int(np.sum(np.abs(residual) > nguong)),
    )
