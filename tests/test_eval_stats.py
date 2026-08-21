"""
Test xử lý thống kê — nhóm lý do gây reject nhiều hơn cả novelty.

Test quan trọng nhất của cả file là test đầu tiên: nó chứng minh việc
bootstrap theo CỤM TÀI LIỆU có tác dụng thật chứ không phải trang trí. Nếu
nó không đỏ khi chuyển sang bootstrap theo từng quan sát thì cả module này
đang giải quyết một vấn đề không tồn tại, và ta nên biết điều đó.

Chạy được mà không cần mạng, model, hay scipy.
"""

import math

import numpy as np
import pytest

from eval.split import kiem_khong_ro_ri, split_by_document
from eval.stats import (
    auroc,
    auroc_diff_cluster_bootstrap,
    cluster_bootstrap_ci,
    holm_bonferroni,
    item_bootstrap_ci,
    mcnemar,
    paired_cluster_bootstrap_diff,
)

# --- Bootstrap theo cụm ------------------------------------------------------


def _du_lieu_phan_cum(so_tai_lieu=20, so_truong=25):
    """
    Dữ liệu có cấu trúc cụm CỰC ĐOAN nhưng không hề bịa: một nửa tài liệu
    đúng hết, một nửa sai hết.

    Đây chính là hình dạng của dữ liệu thật ở mức nhẹ hơn — báo cáo scan mờ
    thì cả 25 trường đều khó, báo cáo sạch thì cả 25 đều dễ. Phóng đại nó
    lên để hiệu ứng nhìn thấy được với ít tài liệu.
    """
    tai_lieu = []
    for i in range(so_tai_lieu):
        dung = so_truong if i % 2 == 0 else 0
        tai_lieu.append({"dung": dung, "tong": so_truong})
    return tai_lieu


def _ty_le(cac_tai_lieu):
    tu = sum(t["dung"] for t in cac_tai_lieu)
    mau = sum(t["tong"] for t in cac_tai_lieu)
    return tu / mau if mau else 0.0


def test_bootstrap_theo_cum_cho_khoang_tin_cay_RONG_HON_theo_truong():
    """
    TEST QUAN TRỌNG NHẤT CỦA MODULE.

    Bootstrap theo từng trường giả định 500 quan sát độc lập, trong khi số
    cụm độc lập thật chỉ là 20. Hệ quả là khoảng tin cậy HẸP GIẢ TẠO, và
    nó sai theo đúng một hướng: lạc quan.

    Nếu test này không đỏ khi đổi sang bootstrap theo quan sát thì việc
    phân cụm không giải quyết vấn đề gì và nên bỏ đi.
    """
    tai_lieu = _du_lieu_phan_cum()
    quan_sat = [{"dung": 1, "tong": 1}] * 250 + [{"dung": 0, "tong": 1}] * 250

    _, cum_duoi, cum_tren = cluster_bootstrap_ci(tai_lieu, _ty_le, n_boot=500)
    _, truong_duoi, truong_tren = item_bootstrap_ci(quan_sat, _ty_le, n_boot=500)

    rong_theo_cum = cum_tren - cum_duoi
    rong_theo_truong = truong_tren - truong_duoi

    assert rong_theo_cum > rong_theo_truong
    assert rong_theo_cum > 2 * rong_theo_truong, (
        f"phân cụm chỉ nới khoảng tin cậy từ {rong_theo_truong:.3f} lên "
        f"{rong_theo_cum:.3f} — kiểm lại xem có thật sự lấy mẫu theo tài liệu không"
    )


def test_uoc_luong_diem_khong_bi_bootstrap_lam_lech():
    """Ước lượng điểm phải tính trên dữ liệu THẬT, không phải trung bình mẫu."""
    tai_lieu = _du_lieu_phan_cum()

    diem, duoi, tren = cluster_bootstrap_ci(tai_lieu, _ty_le, n_boot=200)

    assert diem == pytest.approx(0.5)
    assert duoi <= diem <= tren


def test_cung_seed_cho_cung_khoang_tin_cay():
    """
    Không tái lập được thì con số trong paper không kiểm chứng lại được.
    """
    tai_lieu = _du_lieu_phan_cum()

    lan_1 = cluster_bootstrap_ci(tai_lieu, _ty_le, n_boot=300, seed=42)
    lan_2 = cluster_bootstrap_ci(tai_lieu, _ty_le, n_boot=300, seed=42)

    assert lan_1 == lan_2


def test_khac_seed_cho_khoang_tin_cay_khac():
    """Chốt rằng seed thật sự được dùng, không phải tham số trang trí."""
    tai_lieu = _du_lieu_phan_cum()

    lan_1 = cluster_bootstrap_ci(tai_lieu, _ty_le, n_boot=300, seed=1)
    lan_2 = cluster_bootstrap_ci(tai_lieu, _ty_le, n_boot=300, seed=2)

    assert lan_1[1:] != lan_2[1:]


def test_ghep_cap_dung_cung_mot_lan_lay_mau_cho_ca_hai_phuong_phap():
    """
    Hai phương pháp giống hệt nhau thì hiệu số phải bằng 0 TUYỆT ĐỐI ở mọi
    vòng lặp, nên khoảng tin cậy của hiệu số cũng phải là [0, 0].

    Nếu lấy mẫu độc lập cho từng phương pháp thì hai lần lấy mẫu khác nhau
    sẽ tạo ra hiệu số khác 0 từ hư không — đúng phần phương sai mà việc
    ghép cặp sinh ra để triệt tiêu.
    """
    tai_lieu = _du_lieu_phan_cum()

    hieu, duoi, tren = paired_cluster_bootstrap_diff(
        tai_lieu, _ty_le, _ty_le, n_boot=200
    )

    assert hieu == 0.0
    assert (duoi, tren) == (0.0, 0.0)


def test_hieu_so_co_dau_dung_chieu():
    """Hiệu số là A trừ B, không phải ngược lại."""
    tai_lieu = [{"dung": 8, "tong": 10}] * 5

    def tot_hon(cac_tai_lieu):
        return 1.0

    hieu, _, _ = paired_cluster_bootstrap_diff(tai_lieu, tot_hon, _ty_le, n_boot=100)

    assert hieu == pytest.approx(0.2)


# --- AUROC -------------------------------------------------------------------


def test_auroc_phan_tach_hoan_hao():
    assert auroc([1, 2, 3, 4], [False, False, True, True]) == 1.0


def test_auroc_phan_tach_nguoc_hoan_toan():
    assert auroc([4, 3, 2, 1], [False, False, True, True]) == 0.0


def test_auroc_bo_du_bao_vo_dung_cho_0_5():
    """
    Mọi quan sát cùng một điểm — ví dụ cột confidence hằng số của lượt chạy
    k=1 — phải cho 0.5. Không xử lý hạng đồng đều thì nó nhận 1.0 hoặc 0.0,
    tức một bộ dự báo vô dụng trông như hoàn hảo.
    """
    assert auroc([5, 5, 5, 5], [False, False, True, True]) == 0.5


def test_auroc_mot_lop_thi_khong_dinh_nghia_duoc():
    """
    Trả 0.5 ở đây sẽ nguỵ trang một tình huống KHÔNG ĐO ĐƯỢC thành một kết
    quả. Với tập gold nhỏ, một tài liệu không có lỗi nào là chuyện thường.
    """
    assert math.isnan(auroc([1, 2, 3], [True, True, True]))


def test_so_auroc_giua_hai_bo_diem_tren_cung_du_lieu():
    tai_lieu = [
        {"tot": [1, 2, 3, 4], "te": [4, 3, 2, 1], "nhan": [False, False, True, True]}
        for _ in range(10)
    ]

    hieu, duoi, tren = auroc_diff_cluster_bootstrap(
        tai_lieu,
        lambda t: t["tot"],
        lambda t: t["te"],
        lambda t: t["nhan"],
        n_boot=100,
    )

    assert hieu == pytest.approx(1.0)
    assert duoi == pytest.approx(1.0)


# --- McNemar -----------------------------------------------------------------


def test_mcnemar_tren_vi_du_tinh_tay():
    """
    b = 8 (A đúng, B sai), c = 2 (A sai, B đúng), n = 10.

    Thống kê chi-square = (8-2)^2 / 10 = 3.6.
    p chính xác hai phía = 2 * (C(10,0) + C(10,1) + C(10,2)) / 2^10
                         = 2 * 56 / 1024 = 0,109375.

    Cả hai đều tính được bằng tay, nên test này không cần scipy để đối
    chiếu — và không cần thêm một thư viện nặng vào requirements chỉ để
    lấy một hàm.
    """
    a = [True] * 8 + [False] * 2
    b = [False] * 8 + [True] * 2

    thong_ke, p = mcnemar(a, b)

    assert thong_ke == pytest.approx(3.6)
    assert p == pytest.approx(0.109375)


def test_mcnemar_bat_dong_hoan_toan_mot_chieu():
    """b = 10, c = 0: p = 2 * C(10,0) / 2^10 = 2/1024."""
    thong_ke, p = mcnemar([True] * 10, [False] * 10)

    assert thong_ke == pytest.approx(10.0)
    assert p == pytest.approx(2 / 1024)


def test_mcnemar_chi_nhin_cac_cap_bat_dong():
    """
    Những trường mà cả hai cùng đúng hoặc cùng sai không nói gì về việc
    phương pháp nào tốt hơn. Thêm bao nhiêu cặp đồng thuận cũng không được
    làm đổi p-value.
    """
    a = [True] * 8 + [False] * 2
    b = [False] * 8 + [True] * 2

    goc = mcnemar(a, b)
    them_dong_thuan = mcnemar(a + [True] * 50, b + [True] * 50)

    assert goc == them_dong_thuan


def test_mcnemar_khong_cap_nao_bat_dong_thi_khong_co_bang_chung():
    assert mcnemar([True] * 10, [True] * 10) == (0.0, 1.0)


def test_mcnemar_doi_hoi_ghep_cap_dung_do_dai():
    with pytest.raises(ValueError, match="ghép cặp"):
        mcnemar([True, False], [True])


# --- Holm-Bonferroni ---------------------------------------------------------


def test_holm_bac_bo_gia_thuyet_manh_nhat():
    assert holm_bonferroni([0.01, 0.04, 0.03]) == [True, False, False]


def test_holm_DUNG_ngay_lan_dau_khong_bac_bo_duoc():
    """
    Cách làm hỏng Holm phổ biến nhất: quên bước dừng.

    p = 0,04 một mình thì nhỏ hơn alpha = 0,05, nên nếu duyệt tiếp sau khi
    0,03 đã trượt thì nó bị bác bỏ oan. Bỏ quên bước dừng làm thủ tục mất
    kiểm soát sai số họ, tức mất hết ý nghĩa của việc hiệu chỉnh.
    """
    assert holm_bonferroni([0.001, 0.03, 0.04]) == [True, False, False]


def test_holm_bac_bo_het_khi_moi_p_deu_du_nho():
    assert holm_bonferroni([0.001, 0.002, 0.003]) == [True, True, True]


def test_holm_danh_sach_rong():
    assert holm_bonferroni([]) == []


# --- Chia tập ----------------------------------------------------------------


class _Trang:
    def __init__(self, doc_id, so_trang):
        self.doc_id = doc_id
        self.so_trang = so_trang

    def __repr__(self):
        return f"{self.doc_id}#{self.so_trang}"


def _cac_trang(so_tai_lieu=10, trang_moi_tai_lieu=5):
    return [
        _Trang(f"DOC{i:02d}", trang)
        for i in range(so_tai_lieu)
        for trang in range(trang_moi_tai_lieu)
    ]


def test_moi_trang_cua_mot_tai_lieu_nam_tron_trong_mot_tap():
    """
    Hai trang cùng một báo cáo giống nhau đến mức nếu một trang vào train
    và một trang vào test thì con số đo được là rác.
    """
    cac_tap = split_by_document(_cac_trang(), {"train": 0.7, "test": 0.3}, seed=0)

    kiem_khong_ro_ri(cac_tap)   # không ném lỗi là đạt

    for ten, items in cac_tap.items():
        for item in items:
            cung_doc = [i for i in items if i.doc_id == item.doc_id]
            assert len(cung_doc) == 5, f"tập {ten} chỉ có {len(cung_doc)}/5 trang của {item.doc_id}"


def test_khong_mat_trang_nao():
    cac_tap = split_by_document(_cac_trang(), {"train": 0.7, "test": 0.3}, seed=0)

    assert sum(len(v) for v in cac_tap.values()) == 50


def test_cung_seed_cho_cung_phep_chia():
    lan_1 = split_by_document(_cac_trang(), {"train": 0.8, "test": 0.2}, seed=7)
    lan_2 = split_by_document(_cac_trang(), {"train": 0.8, "test": 0.2}, seed=7)

    assert [str(i) for i in lan_1["test"]] == [str(i) for i in lan_2["test"]]


def test_tong_ty_le_khac_1_thi_bao_loi():
    with pytest.raises(ValueError, match="Tổng tỷ lệ"):
        split_by_document(_cac_trang(), {"train": 0.7, "test": 0.4})


def test_kiem_ro_ri_bat_duoc_phep_chia_hong():
    """
    Rò rỉ dữ liệu không sửa được sau khi đã chạy xong thí nghiệm — phải
    chạy lại từ đầu — nên phát hiện muộn đắt hơn hẳn một lần kiểm thừa.
    """
    hong = {
        "train": [_Trang("DOC01", 1)],
        "test": [_Trang("DOC01", 2)],
    }

    with pytest.raises(ValueError, match="Rò rỉ"):
        kiem_khong_ro_ri(hong)


def test_ty_le_chia_ap_len_so_TAI_LIEU():
    """
    Tỷ lệ áp lên số tài liệu, không phải số item. Số item thực tế trong mỗi
    tập vì vậy lệch chút — đó là cái giá đúng phải trả, vì lựa chọn còn lại
    là rò rỉ dữ liệu.
    """
    cac_tap = split_by_document(_cac_trang(so_tai_lieu=10), {"train": 0.7, "test": 0.3}, seed=0)

    doc_train = {i.doc_id for i in cac_tap["train"]}
    doc_test = {i.doc_id for i in cac_tap["test"]}

    assert len(doc_train) == 7
    assert len(doc_test) == 3
    assert not (doc_train & doc_test)


def test_bootstrap_tren_danh_sach_rong_thi_bao_loi():
    with pytest.raises(ValueError, match="Không có tài liệu"):
        cluster_bootstrap_ci([], _ty_le)


def test_numpy_random_khong_bi_anh_huong_boi_seed_toan_cuc():
    """
    Dùng default_rng riêng chứ không dùng np.random toàn cục: state toàn
    cục bị thư viện khác đụng vào là mất tái lập mà không có gì báo.
    """
    np.random.seed(123)
    lan_1 = cluster_bootstrap_ci(_du_lieu_phan_cum(), _ty_le, n_boot=100, seed=5)
    np.random.seed(999)
    lan_2 = cluster_bootstrap_ci(_du_lieu_phan_cum(), _ty_le, n_boot=100, seed=5)

    assert lan_1 == lan_2
