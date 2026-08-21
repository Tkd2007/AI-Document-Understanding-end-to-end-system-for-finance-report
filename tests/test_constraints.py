"""
Test ma trận ràng buộc và phân tích identifiability.

Đây là một trong hai chỗ mà spec chỉ đích danh là KHÔNG được để AI làm rồi
tin luôn: sai một dấu trong ma trận là toàn bộ kết quả identifiability sai
mà không có gì báo. Nên bộ test này cố ý bắt đầu bằng ví dụ tính tay đủ nhỏ
để kiểm bằng mắt, rồi mới tới bộ field thật.

Chạy được mà không cần mạng hay model: toàn bộ là đại số tuyến tính.
"""

import numpy as np
import pytest

from constraints import (
    build_matrix,
    collinear_columns,
    minimal_localizing_set,
    null_space,
    rank,
    report,
    scale_direction_in_null,
    single_field_localizable,
    zero_columns,
)
from fields_config import FIELD_MAP, Standard, identities_for

# --- Ví dụ tính tay: a + b = c ---------------------------------------------
#
# A = [[1, 1, -1]]. Hạng 1, chiều null 2. Đủ nhỏ để kiểm bằng mắt, và mọi
# khẳng định dưới đây tự kiểm được không cần chạy code.
BA_FIELD = ["a", "b", "c"]
MOT_DANG_THUC = [(["a", "b"], "c", "a + b = c")]


def test_vi_du_tinh_tay_dung_hinh_dang_ma_tran():
    A, field_order = build_matrix(BA_FIELD, MOT_DANG_THUC)

    assert field_order == ["a", "b", "c"]
    assert A.shape == (1, 3)
    np.testing.assert_array_equal(A, [[1.0, 1.0, -1.0]])


def test_vi_du_tinh_tay_dung_hang_va_chieu_null():
    A, _ = build_matrix(BA_FIELD, MOT_DANG_THUC)

    assert rank(A) == 1
    assert null_space(A).shape == (3, 2)


def test_vi_du_tinh_tay_khong_field_nao_dinh_vi_duoc():
    """
    Ba cột là [1], [1], [-1] — đôi một tỷ lệ với nhau, nên lỗi ở a, ở b hay
    ở c đều cho residual pattern giống hệt. Một đẳng thức duy nhất phát
    hiện được có lỗi nhưng tuyệt đối không nói được lỗi ở đâu.
    """
    A, field_order = build_matrix(BA_FIELD, MOT_DANG_THUC)

    assert single_field_localizable(A, field_order) == {"a": False, "b": False, "c": False}
    assert len(collinear_columns(A, field_order)) == 3


def test_thu_tu_cot_theo_dung_thu_tu_field_truyen_vao():
    """
    Nhầm thứ tự cột là loại lỗi im lặng nguy hiểm nhất ở module này: nó
    không làm gì nổ, chỉ gán kết luận của field này cho field khác.
    """
    A, field_order = build_matrix(["c", "b", "a"], MOT_DANG_THUC)

    assert field_order == ["c", "b", "a"]
    np.testing.assert_array_equal(A, [[-1.0, 1.0, 1.0]])


def test_dang_thuc_thieu_field_thi_bi_bo_chu_khong_coi_he_so_bang_0():
    """
    Không trích một chỉ tiêu thì không kiểm được đẳng thức chứa nó. Coi nó
    bằng 0 sẽ dựng ra một ràng buộc SAI và làm hạng cao lên giả tạo, tức là
    báo cáo lạc quan hơn sự thật về khả năng định vị.
    """
    A, _ = build_matrix(["a", "b"], MOT_DANG_THUC)

    assert A.shape == (0, 2)
    assert rank(A) == 0


def test_khong_rang_buoc_nao_thi_moi_huong_deu_vo_hinh():
    A, field_order = build_matrix(["a", "b"], [])

    assert null_space(A).shape == (2, 2)
    assert zero_columns(A, field_order) == ["a", "b"]


# --- Bộ field thật ---------------------------------------------------------

VNM_Q1_2026 = {
    "tai_san_ngan_han": 29403116984122,
    "hang_ton_kho": 5393002084291,
    "tai_san_dai_han": 18372709942261,
    "tong_tai_san": 47775826926383,
    "no_phai_tra": 16666572149360,
    "von_chu_so_huu": 31109254777023,
    "doanh_thu_thuan": 13217639635987,
    "gia_von_hang_ban": 7278764406353,
    "loi_nhuan_gop": 5938875229634,
    "loi_nhuan_truoc_thue": 2523887147085,
    "loi_nhuan_sau_thue": 2049247209782,
}


def _ma_tran_that(standard: Standard):
    return build_matrix(list(FIELD_MAP), identities_for(standard))


@pytest.mark.parametrize("standard", list(Standard))
def test_ba_dang_thuc_hien_tai_doc_lap_tuyen_tinh(standard):
    """
    Hạng 3 nghĩa là ba đẳng thức thật sự độc lập, không cái nào suy ra
    được từ hai cái kia. Không giả định điều này — nếu sau này ai thêm một
    đẳng thức trùng lặp thì hạng đứng yên và test nói ra ngay.
    """
    A, _ = _ma_tran_that(standard)

    assert A.shape[0] == 3
    assert rank(A) == 3


@pytest.mark.parametrize("standard", list(Standard))
def test_tam_tren_muoi_mot_chieu_loi_la_vo_hinh(standard):
    """Con số trung tâm của H0 với bộ chỉ tiêu hiện tại."""
    A, _ = _ma_tran_that(standard)

    assert null_space(A).shape == (len(FIELD_MAP), 8)


def test_bat_bien_scale_nam_trong_khong_gian_null():
    """
    Mệnh đề một dòng của cả module: với δ = (c−1)x*, ta có
    Aδ = (c−1)Ax* = 0. Nhân mọi giá trị với một triệu — đúng ca đọc
    "triệu đồng" thành "đồng" — vẫn cho residual bằng 0 tuyệt đối.

    Hàm scale_direction_in_null() là một ASSERT CHẠY ĐƯỢC: trả False nghĩa
    là ma trận dựng sai chứ không phải lý thuyết sai.
    """
    A, field_order = _ma_tran_that(Standard.TT99)
    x_ref = np.array([VNM_Q1_2026[ten] for ten in field_order], dtype=float)

    assert scale_direction_in_null(A, x_ref)
    assert scale_direction_in_null(A, 1e6 * x_ref)


def test_bo_so_that_thoa_moi_dang_thuc():
    """
    Kiểm chứng chính bộ số VNM: nếu A @ x_ref khác 0 thì hoặc ma trận sai
    dấu, hoặc bộ số trong test sai — cả hai đều phải biết ngay.
    """
    A, field_order = _ma_tran_that(Standard.TT99)
    x_ref = np.array([VNM_Q1_2026[ten] for ten in field_order], dtype=float)

    np.testing.assert_allclose(A @ x_ref, 0, atol=1e-6)


def test_ba_field_khong_duoc_rang_buoc_nao_bao_ve():
    """
    Tình trạng NẶNG HƠN việc không định vị được: cột toàn 0 nghĩa là lỗi ở
    field đó cho residual đúng bằng 0, tức không PHÁT HIỆN được chứ không
    chỉ là không định vị được.

    hang_ton_kho đáng chú ý nhất — đây chính là field mà báo cáo VNM đã có
    lỗi đọc thật (alias khớp trúng dòng Dự phòng giảm giá), và ràng buộc kế
    toán hoàn toàn không giúp gì được.
    """
    A, field_order = _ma_tran_that(Standard.TT99)

    assert zero_columns(A, field_order) == [
        "hang_ton_kho",
        "loi_nhuan_truoc_thue",
        "loi_nhuan_sau_thue",
    ]


def test_chi_mot_tren_muoi_mot_field_dinh_vi_duoc():
    """
    Kết quả H0 quan trọng nhất với bộ chỉ tiêu hiện tại, và là lý do B4
    (mở rộng bộ trường) không phải việc tuỳ chọn: chỉ tong_tai_san có cột
    riêng biệt, mọi field còn lại hoặc không được bảo vệ, hoặc lẫn với một
    field khác.
    """
    A, field_order = _ma_tran_that(Standard.TT99)
    dinh_vi = single_field_localizable(A, field_order)

    assert [ten for ten, duoc in dinh_vi.items() if duoc] == ["tong_tai_san"]


def test_khong_ton_tai_bo_field_nao_dinh_vi_duoc_voi_dang_thuc_hien_co():
    """
    Trả None là một KẾT QUẢ NGHIÊN CỨU hợp lệ, không phải lỗi: với ba đẳng
    thức hiện có, không cách nào chọn tập con nào của 11 chỉ tiêu này để
    mọi lỗi một-trường đều định vị được.

    Hệ quả cho kế hoạch: muốn H2 có nghĩa thì phải thêm ĐẲNG THỨC, không
    phải chỉ thêm chỉ tiêu. Đây đúng là câu hỏi mà Mốc 1 cần người trả lời
    khi đối chiếu Thông tư.
    """
    bo, chac_chan = minimal_localizing_set(list(FIELD_MAP), identities_for(Standard.TT99))

    assert bo is None
    assert chac_chan, "11 field thì phải vét cạn được, không được rơi vào tham lam"


# --- minimal_localizing_set trên ví dụ có lời giải --------------------------
#
# Bốn field, hai đẳng thức lồng nhau:
#     a + b = c
#     b + c = d
# Cột: a=[1,0], b=[1,1], c=[-1,1], d=[0,-1] — đôi một không tỷ lệ, nên MỌI
# field đều định vị được. Kiểm bằng mắt được, không cần chạy.
BON_FIELD = ["a", "b", "c", "d"]
HAI_DANG_THUC = [
    (["a", "b"], "c", "a + b = c"),
    (["b", "c"], "d", "b + c = d"),
]


def test_hai_dang_thuc_long_nhau_thi_moi_field_dinh_vi_duoc():
    A, field_order = build_matrix(BON_FIELD, HAI_DANG_THUC)

    assert collinear_columns(A, field_order) == []
    assert all(single_field_localizable(A, field_order).values())


def test_bo_toi_thieu_la_ca_bon_field():
    """
    Không tập con nào nhỏ hơn dùng được: bỏ bất kỳ field nào cũng làm mất
    ít nhất một đẳng thức, và còn một đẳng thức thì ba cột lại tỷ lệ với
    nhau như ví dụ tính tay ở trên.
    """
    bo, chac_chan = minimal_localizing_set(BON_FIELD, HAI_DANG_THUC)

    assert bo is not None
    assert sorted(bo) == BON_FIELD
    assert chac_chan


def test_them_ung_vien_khong_lam_bo_toi_thieu_LON_HON():
    """
    Tính đơn điệu — CHÚ Ý CHIỀU.

    Spec (BUILD-SPEC mục A2) phát biểu là "thêm field vào tập ứng viên
    không làm bộ tối thiểu NHỎ ĐI". Chiều đó sai về mặt toán: tập ứng viên
    rộng hơn chỉ thêm lựa chọn chứ không bớt, nên cực tiểu chỉ có thể GIỮ
    NGUYÊN HOẶC NHỎ ĐI. Test theo đúng phát biểu của spec sẽ đóng đinh một
    bất biến sai vào bộ test, nên ở đây kiểm chiều đúng.

    Field "e" thêm vào không tham gia đẳng thức nào, nên nếu nó lọt vào bộ
    thì chính nó có cột toàn 0 và bộ đó hỏng — cực tiểu vì vậy giữ nguyên.
    """
    nho, _ = minimal_localizing_set(BON_FIELD, HAI_DANG_THUC)
    lon, _ = minimal_localizing_set([*BON_FIELD, "e"], HAI_DANG_THUC)

    assert lon is not None and nho is not None
    assert len(lon) <= len(nho)
    assert "e" not in lon


def test_must_include_luon_co_mat_trong_ket_qua():
    """
    tong_tai_san và doanh_thu_thuan là đầu ra người dùng cần, phải có mặt
    bất kể chúng có giúp định vị hay không.
    """
    bo, _ = minimal_localizing_set(BON_FIELD, HAI_DANG_THUC, must_include=["a"])

    assert bo is not None
    assert "a" in bo


# --- Báo cáo ---------------------------------------------------------------


def test_bao_cao_neu_ro_cac_con_so_quan_trong(tmp_path):
    """
    Báo cáo là artifact người dùng phải đọc và đối chiếu với Thông tư, nên
    ba con số quyết định (hạng, chiều null, số field định vị được) và bảng
    ma trận có tên field phải nằm trong đó.
    """
    A, field_order = _ma_tran_that(Standard.TT99)
    duong_dan = tmp_path / "identifiability.md"

    noi_dung = report(A, field_order, identities_for(Standard.TT99), out_path=duong_dan)

    assert duong_dan.read_text(encoding="utf-8") == noi_dung
    assert "`rank(A)`: **3**" in noi_dung
    assert "`dim null(A)`: **8**" in noi_dung
    assert "**1 / 11**" in noi_dung
    assert "tong_tai_san" in noi_dung
    assert "cột toàn 0" in noi_dung
