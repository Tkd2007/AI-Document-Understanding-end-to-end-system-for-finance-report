"""
Chia tập theo TÀI LIỆU, không theo trang.

Hai trang của cùng một báo cáo giống nhau đến mức nếu một trang vào train
và một trang vào test thì con số đo được là rác: cùng chất lượng scan, cùng
layout, cùng công ty kiểm toán, cùng bộ font, và thường cùng cả những con số
(cột kỳ trước của trang này là cột kỳ này của trang kia).

Reviewer bắt lỗi này rất nhanh, và nó là loại lỗi không sửa được sau khi đã
chạy xong thí nghiệm — phải chạy lại từ đầu.
"""

from collections.abc import Callable, Sequence

import numpy as np


def split_by_document(
    items: Sequence,
    ratios: dict[str, float],
    seed: int = 0,
    lay_doc_id: Callable = lambda item: item.doc_id,
) -> dict[str, list]:
    """
    Chia items thành các tập theo tỷ lệ, đảm bảo mọi item CÙNG doc_id nằm
    trọn trong MỘT tập.

    ratios ví dụ {"train": 0.7, "test": 0.3}. Tổng phải bằng 1.

    Chia theo TÀI LIỆU chứ không theo item, kể cả khi item là từng trang
    hay từng trường. Tỷ lệ vì vậy áp lên số TÀI LIỆU, và số item thực tế
    trong mỗi tập sẽ lệch chút — đó là cái giá đúng phải trả, vì lựa chọn
    còn lại là rò rỉ dữ liệu.

    seed cố định để tái lập được: cùng seed phải cho cùng phép chia, nếu
    không thì hai lần chạy thí nghiệm không so được với nhau.
    """
    tong = sum(ratios.values())
    if not math_gan_bang(tong, 1.0):
        raise ValueError(f"Tổng tỷ lệ phải bằng 1, đang là {tong}")

    theo_doc: dict = {}
    for item in items:
        theo_doc.setdefault(lay_doc_id(item), []).append(item)

    cac_doc = sorted(theo_doc)          # sắp trước để seed cho kết quả tất định
    rng = np.random.default_rng(seed)
    rng.shuffle(cac_doc)

    ket_qua: dict[str, list] = {ten: [] for ten in ratios}
    ten_tap = list(ratios)

    # Cắt theo mốc tích luỹ thay vì làm tròn từng tập: làm tròn độc lập có
    # thể để sót hoặc lặp một tài liệu ở ranh giới.
    moc = 0.0
    bat_dau = 0
    for i, ten in enumerate(ten_tap):
        moc += ratios[ten]
        ket_thuc = len(cac_doc) if i == len(ten_tap) - 1 else round(moc * len(cac_doc))
        for doc_id in cac_doc[bat_dau:ket_thuc]:
            ket_qua[ten].extend(theo_doc[doc_id])
        bat_dau = ket_thuc

    return ket_qua


def math_gan_bang(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol


def kiem_khong_ro_ri(cac_tap: dict[str, list], lay_doc_id: Callable = lambda item: item.doc_id):
    """
    Chốt lại rằng không tài liệu nào xuất hiện ở hai tập.

    Gọi hàm này ngay sau khi chia, và gọi lại trước khi báo cáo kết quả.
    Rò rỉ dữ liệu là loại lỗi không sửa được sau khi đã chạy xong — phải
    chạy lại từ đầu — nên phát hiện muộn đắt hơn hẳn một lần kiểm thừa.
    """
    da_thay: dict = {}
    for ten_tap, items in cac_tap.items():
        for item in items:
            doc_id = lay_doc_id(item)
            if doc_id in da_thay and da_thay[doc_id] != ten_tap:
                raise ValueError(
                    f"Rò rỉ dữ liệu: tài liệu {doc_id} có mặt ở cả tập "
                    f"{da_thay[doc_id]} lẫn tập {ten_tap}"
                )
            da_thay[doc_id] = ten_tap
