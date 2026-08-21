"""
Xử lý thống kê — bootstrap theo cụm, kiểm định ghép cặp, hiệu chỉnh đa so sánh.

ĐỌC PHẦN NÀY TRƯỚC KHI SỬA BẤT CỨ GÌ Ở ĐÂY.

Nguyên tắc chi phối cả module: BOOTSTRAP PHẢI THEO CỤM TÀI LIỆU, KHÔNG THEO
TRƯỜNG.

Các trường trong cùng một tài liệu KHÔNG độc lập. Chúng chia sẻ chất lượng
scan, cùng layout, cùng đơn vị tính, cùng công ty kiểm toán, cùng chuẩn mẫu
biểu. Một báo cáo scan mờ thì cả 25 trường đều khó; một báo cáo sạch thì cả
25 đều dễ.

Hệ quả: bootstrap lấy mẫu TỪNG TRƯỜNG cho khoảng tin cậy HẸP GIẢ TẠO, vì
nó giả định 1500 quan sát độc lập trong khi số cụm độc lập thật chỉ là 60.
Đây là loại lỗi reviewer có nền thống kê bắt được ngay, và nó làm sai mọi
khoảng tin cậy trong bài theo đúng một hướng: lạc quan.

Cách đúng: lấy mẫu lại TÀI LIỆU (có hoàn lại), rồi tính chỉ số trên toàn bộ
trường của các tài liệu được chọn.

VÌ SAO KHÔNG DÙNG DeLong CHO SO SÁNH AUROC: DeLong xử lý đúng tương quan
GIỮA CÁC ĐƯỜNG ROC đo trên cùng mẫu, nhưng vẫn giả định các QUAN SÁT độc
lập. Ở đây quan sát là từng trường, và chúng không độc lập trong cùng tài
liệu. Dùng DeLong sẽ mắc đúng loại lỗi mà bootstrap-theo-trường mắc.
Bootstrap theo cụm xử lý được cả hai nguồn tương quan cùng lúc.

Module không phụ thuộc scipy: AUROC dùng công thức hạng, McNemar dùng kiểm
định nhị thức CHÍNH XÁC. Thêm một thư viện nặng chỉ để lấy hai hàm là cái
giá không đáng, và kiểm định chính xác còn đúng hơn xấp xỉ chi-square ở
đúng cỡ mẫu của nghiên cứu này (N của H2 chỉ khoảng 75-225).
"""

import math
from collections.abc import Callable, Sequence

import numpy as np

# Số vòng lặp bootstrap. 2000 là mức thông dụng cho khoảng tin cậy
# percentile: đủ để hai lần chạy khác seed cho cùng kết quả tới chữ số thứ
# ba, mà vẫn chạy trong vài giây.
N_BOOT = 2000
ALPHA = 0.05


def auroc(scores: Sequence[float], labels: Sequence[bool]) -> float:
    """
    Diện tích dưới đường ROC, tính bằng công thức hạng (Mann-Whitney U).

    Xử lý hạng đồng đều cho các giá trị bằng nhau. Bỏ qua chuyện này sẽ
    khiến một bộ dự báo trả về cùng một điểm cho mọi quan sát — ví dụ cột
    confidence hằng số của lượt chạy k=1 — nhận được AUROC 1.0 hoặc 0.0
    thay vì 0.5.

    Trả về nan khi chỉ có một lớp: AUROC không định nghĩa được, và trả 0.5
    ở đó sẽ ngụy trang một tình huống không đo được thành một kết quả.
    """
    diem = np.asarray(scores, dtype=float)
    nhan = np.asarray(labels, dtype=bool)

    so_duong = int(nhan.sum())
    so_am = int((~nhan).sum())
    if so_duong == 0 or so_am == 0:
        return float("nan")

    thu_tu = np.argsort(diem, kind="mergesort")
    da_sap = diem[thu_tu]

    hang_da_sap = np.empty(len(diem), dtype=float)
    i = 0
    while i < len(da_sap):
        j = i
        while j + 1 < len(da_sap) and da_sap[j + 1] == da_sap[i]:
            j += 1
        hang_da_sap[i : j + 1] = (i + j) / 2 + 1
        i = j + 1

    hang = np.empty(len(diem), dtype=float)
    hang[thu_tu] = hang_da_sap

    tong_hang_duong = hang[nhan].sum()

    return (tong_hang_duong - so_duong * (so_duong + 1) / 2) / (so_duong * so_am)


def _lay_mau_lai(rng, n: int) -> np.ndarray:
    return rng.integers(0, n, size=n)


def cluster_bootstrap_ci(
    docs: list,
    metric_fn: Callable[[list], float],
    n_boot: int = N_BOOT,
    alpha: float = ALPHA,
    seed: int = 0,
) -> tuple[float, float, float]:
    """
    Khoảng tin cậy bootstrap, lấy mẫu lại theo CỤM TÀI LIỆU.

    Trả về (ước lượng điểm, cận dưới, cận trên).

    metric_fn nhận một DANH SÁCH TÀI LIỆU và trả về một con số. Ký hợp đồng
    ở mức danh sách chứ không ở mức từng tài liệu là có chủ đích: nó buộc
    người viết chỉ số phải tự quyết định cách gộp qua nhiều tài liệu, và
    chỗ đó có một cái bẫy thật — trung bình của các tỷ lệ khác tỷ lệ của
    tổng khi các tài liệu có số trường khác nhau. Xem gop_ty_le().

    seed cố định để tái lập được. Hai lần chạy cùng seed phải cho cùng
    khoảng tin cậy tới từng chữ số, nếu không thì con số trong paper không
    kiểm chứng lại được.
    """
    if not docs:
        raise ValueError("Không có tài liệu nào để bootstrap")

    rng = np.random.default_rng(seed)
    n = len(docs)

    mau = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        chon = _lay_mau_lai(rng, n)
        mau[b] = metric_fn([docs[i] for i in chon])

    can_duoi, can_tren = np.percentile(mau, [100 * alpha / 2, 100 * (1 - alpha / 2)])

    return metric_fn(docs), float(can_duoi), float(can_tren)


def item_bootstrap_ci(
    items: list,
    metric_fn: Callable[[list], float],
    n_boot: int = N_BOOT,
    alpha: float = ALPHA,
    seed: int = 0,
) -> tuple[float, float, float]:
    """
    Bootstrap lấy mẫu lại TỪNG QUAN SÁT — CÁCH SAI cho dữ liệu của dự án này.

    KHÔNG DÙNG hàm này để báo cáo bất cứ con số nào. Nó tồn tại đúng hai
    mục đích: (1) để test chứng minh việc phân cụm có tác dụng thật chứ
    không phải trang trí, và (2) để paper nêu được ĐỊNH LƯỢNG khoảng tin
    cậy sẽ hẹp giả tạo bao nhiêu nếu bỏ qua cấu trúc cụm.

    Mục thứ hai đáng làm: "chúng tôi bootstrap theo cụm" là một câu; "bỏ
    qua cấu trúc cụm làm khoảng tin cậy hẹp đi 2,3 lần trên chính dữ liệu
    này" là một bằng chứng.
    """
    if not items:
        raise ValueError("Không có quan sát nào để bootstrap")

    rng = np.random.default_rng(seed)
    n = len(items)

    mau = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        chon = _lay_mau_lai(rng, n)
        mau[b] = metric_fn([items[i] for i in chon])

    can_duoi, can_tren = np.percentile(mau, [100 * alpha / 2, 100 * (1 - alpha / 2)])

    return metric_fn(items), float(can_duoi), float(can_tren)


def paired_cluster_bootstrap_diff(
    docs: list,
    metric_fn_a: Callable[[list], float],
    metric_fn_b: Callable[[list], float],
    n_boot: int = N_BOOT,
    alpha: float = ALPHA,
    seed: int = 0,
) -> tuple[float, float, float]:
    """
    Khoảng tin cậy của HIỆU SỐ giữa hai phương pháp trên cùng bộ tài liệu.

    Trả về (hiệu số, cận dưới, cận trên), với hiệu số = A trừ B.

    Dùng CÙNG MỘT lần lấy mẫu cho cả hai phương pháp. Đó là toàn bộ điểm
    mấu chốt: hai phương pháp chạy trên cùng bộ tài liệu nên phần lớn
    phương sai là do bộ tài liệu chứ không do phương pháp, và ghép cặp
    triệt tiêu đúng phần đó. Lấy mẫu độc lập cho từng phương pháp sẽ vứt
    phần lớn power một cách vô ích.

    Trình bày hiệu số kèm khoảng tin cậy mạnh hơn nhiều so với chỉ trình
    bày p-value: nó trả lời "hơn bao nhiêu" chứ không chỉ "có hơn không",
    mà với 60 tài liệu thì một hiệu số có ý nghĩa thống kê nhưng bằng một
    điểm phần trăm thì không ai quan tâm.
    """
    if not docs:
        raise ValueError("Không có tài liệu nào để bootstrap")

    rng = np.random.default_rng(seed)
    n = len(docs)

    hieu_so = np.empty(n_boot, dtype=float)
    for b in range(n_boot):
        chon = _lay_mau_lai(rng, n)
        da_chon = [docs[i] for i in chon]
        hieu_so[b] = metric_fn_a(da_chon) - metric_fn_b(da_chon)

    can_duoi, can_tren = np.percentile(hieu_so, [100 * alpha / 2, 100 * (1 - alpha / 2)])

    return metric_fn_a(docs) - metric_fn_b(docs), float(can_duoi), float(can_tren)


def auroc_diff_cluster_bootstrap(
    docs: list,
    lay_diem_a: Callable,
    lay_diem_b: Callable,
    lay_nhan: Callable,
    n_boot: int = N_BOOT,
    alpha: float = ALPHA,
    seed: int = 0,
) -> tuple[float, float, float]:
    """
    So AUROC của hai bộ điểm trên cùng dữ liệu, bootstrap theo cụm tài liệu.

    Ba hàm truyền vào đều nhận MỘT tài liệu và trả về danh sách giá trị
    theo từng quan sát trong tài liệu đó.

    KHÔNG dùng DeLong — xem docstring đầu module để biết vì sao.
    """

    def auroc_cua(lay_diem):
        def tinh(cac_tai_lieu):
            diem, nhan = [], []
            for tai_lieu in cac_tai_lieu:
                diem.extend(lay_diem(tai_lieu))
                nhan.extend(lay_nhan(tai_lieu))
            return auroc(diem, nhan)

        return tinh

    return paired_cluster_bootstrap_diff(
        docs, auroc_cua(lay_diem_a), auroc_cua(lay_diem_b), n_boot, alpha, seed
    )


def mcnemar(a_correct: Sequence[bool], b_correct: Sequence[bool]) -> tuple[float, float]:
    """
    Kiểm định McNemar ghép cặp cho kết quả đúng/sai nhị phân.

    Trả về (thống kê chi-square, p-value CHÍNH XÁC theo nhị thức).

    Chỉ những cặp BẤT ĐỒNG mới mang thông tin: những trường mà cả hai
    phương pháp cùng đúng hoặc cùng sai không nói gì về việc phương pháp
    nào tốt hơn. Đó là lý do McNemar chỉ nhìn vào b và c.

    Dùng p-value chính xác thay vì xấp xỉ chi-square vì cỡ mẫu ở đây nhỏ:
    N của H2 là SỐ TRƯỜNG BỊ LỖI, khoảng 75-225, và số cặp bất đồng còn
    nhỏ hơn nữa. Xấp xỉ chi-square lệch đáng kể khi b + c dưới 25, đúng
    vùng ta sẽ rơi vào.

    Thống kê chi-square vẫn trả về để báo cáo, nhưng KẾT LUẬN phải dựa
    trên p-value chính xác.
    """
    if len(a_correct) != len(b_correct):
        raise ValueError(
            f"Hai danh sách phải ghép cặp theo cùng thứ tự và cùng độ dài: "
            f"{len(a_correct)} so với {len(b_correct)}"
        )

    b = sum(1 for x, y in zip(a_correct, b_correct) if x and not y)
    c = sum(1 for x, y in zip(a_correct, b_correct) if not x and y)
    n = b + c

    if n == 0:
        # Không cặp nào bất đồng: không có bằng chứng nào về khác biệt.
        return 0.0, 1.0

    thong_ke = (b - c) ** 2 / n
    nho_hon = min(b, c)
    p = 2 * sum(math.comb(n, i) for i in range(nho_hon + 1)) / (2**n)

    return float(thong_ke), float(min(1.0, p))


def holm_bonferroni(pvals: Sequence[float], alpha: float = ALPHA) -> list[bool]:
    """
    Hiệu chỉnh Holm-Bonferroni cho nhiều so sánh, trả về danh sách bác bỏ.

    Chặt hơn Bonferroni thuần mà vẫn kiểm soát cùng một sai số họ, nên
    không có lý do dùng Bonferroni thuần.

    Quy trình: sắp p-value tăng dần, so p thứ hạng i với alpha/(m − i).
    DỪNG ngay lần đầu không bác bỏ được — mọi giả thuyết còn lại cũng
    không bác bỏ, bất kể p-value của chúng nhỏ tới đâu. Bỏ quên bước dừng
    này là cách làm hỏng Holm phổ biến nhất, và nó làm thủ tục mất kiểm
    soát sai số họ tức là mất hết ý nghĩa.

    Với chín ablation thì lựa chọn TRUNG THỰC HƠN là trình bày thẳng chúng
    là THĂM DÒ chứ không phải xác nhận, và không hiệu chỉnh gì cả. Cách đó
    không mất gì mà lại nói đúng bản chất việc đang làm.
    """
    m = len(pvals)
    if m == 0:
        return []

    thu_tu = sorted(range(m), key=lambda i: pvals[i])
    bac_bo = [False] * m

    for hang, chi_so in enumerate(thu_tu):
        if pvals[chi_so] <= alpha / (m - hang):
            bac_bo[chi_so] = True
        else:
            break

    return bac_bo
