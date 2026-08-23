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
from fields_config import Standard, fields_for, identities_for

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

# Số liệu ĐỌC TAY từ chính báo cáo trong data/samples (bản soát xét Q1/2026,
# riêng, mẫu B01a-DN và B02a-DN theo Thông tư 99/2025). Không lấy từ đầu ra
# pipeline — nếu lấy từ đó thì test chỉ chứng minh pipeline nhất quán với
# chính nó, chứ không chứng minh ma trận A dựng đúng.
#
# tai_san_sinh_hoc_ngan_han = 0 chứ không phải None, và đó là con số ĐÚNG:
# VNM không có tài sản sinh học nên TT99 mục 1.2.3 cho phép miễn trình bày,
# và báo cáo in thẳng công thức rút gọn "100 = 110 + 120 + 130 + 140 + 160"
# ngay dưới tên chỉ tiêu. Dòng vắng mặt nghĩa là bằng 0, không phải chưa
# biết — xem ghi chú về chế độ bỏ qua đẳng thức ở HANDOFF.md.
VNM_Q1_2026 = {
    "tai_san_ngan_han": 29403116984122,
    "tien_va_tuong_duong_tien": 1362241151028,
    "dau_tu_tc_ngan_han": 17709033917800,
    "phai_thu_ngan_han": 4737004862410,
    "hang_ton_kho": 5393002084291,
    "tai_san_sinh_hoc_ngan_han": 0,
    "tsnh_khac": 201834968593,
    "tai_san_dai_han": 18372709942261,
    "tong_tai_san": 47775826926383,
    "no_phai_tra": 16666572149360,
    "von_chu_so_huu": 31109254777023,
    "tong_nguon_von": 47775826926383,
    "doanh_thu_thuan": 13217639635987,
    "gia_von_hang_ban": 7278764406353,
    "loi_nhuan_gop": 5938875229634,
    "ln_thuan_hdkd": 2498569420889,
    "ln_khac": 25317726196,
    "loi_nhuan_truoc_thue": 2523887147085,
    "thue_tndn_hien_hanh": 426210619002,
    "thue_tndn_hoan_lai": 48429318301,
    "loi_nhuan_sau_thue": 2049247209782,
}


def _ma_tran_that(standard: Standard):
    return build_matrix(fields_for(standard), identities_for(standard))


@pytest.mark.parametrize("standard", list(Standard))
def test_bay_dang_thuc_hien_tai_doc_lap_tuyen_tinh(standard):
    """
    Hạng 7 nghĩa là bảy đẳng thức thật sự độc lập, không cái nào suy ra
    được từ những cái kia. Không giả định điều này — nếu sau này ai thêm
    một đẳng thức trùng lặp thì hạng đứng yên và test nói ra ngay.
    """
    A, _ = _ma_tran_that(standard)

    assert A.shape[0] == 7
    assert rank(A) == 7


@pytest.mark.parametrize(
    ("standard", "n_field", "chieu_null"),
    [(Standard.TT200, 20, 13), (Standard.TT99, 21, 14)],
)
def test_chieu_khong_gian_null_theo_tung_chuan(standard, n_field, chieu_null):
    """
    Con số trung tâm của H0 với bộ chỉ tiêu chốt ở Mốc 1.

    Hai chuẩn KHÔNG cùng số chiều, và đây là chỗ duy nhất trong cả cấu hình
    thể hiện điều đó: TT99 có thêm Tài sản sinh học ngắn hạn nên nhiều hơn
    một chỉ tiêu, trong khi hạng vẫn là 7 ở cả hai.

    Ghi cả n_field lẫn chiều null thay vì chỉ ghi hiệu số, để nếu ai đó thêm
    chỉ tiêu mà quên thêm đẳng thức thì test chỉ ra được là hỏng ở vế nào.

    Lưu ý khi đọc kết quả: mở rộng bộ chỉ tiêu KHÔNG thu hẹp không gian null
    theo chiều tuyệt đối — 11 chỉ tiêu cho 8 chiều, 21 chỉ tiêu cho 14. Cái
    được cải thiện là số chỉ tiêu PHÁT HIỆN và ĐỊNH VỊ được, nên đừng đọc
    dim null một mình như thước đo tiến bộ.
    """
    A, _ = _ma_tran_that(standard)

    assert len(fields_for(standard)) == n_field
    assert null_space(A).shape == (n_field, chieu_null)


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


@pytest.mark.parametrize("standard", list(Standard))
def test_khong_con_field_nao_vo_hinh_voi_rang_buoc(standard):
    """
    Đây là thứ MỐC 1 mua được, và là lý do chính chọn kịch bản D.

    Cột toàn 0 là tình trạng NẶNG HƠN việc không định vị được: lỗi ở chỉ
    tiêu đó cho residual đúng bằng 0, tức không PHÁT HIỆN được — vô hình với
    cả H1 lẫn H2, không chỉ H2.

    Với bộ 11 chỉ tiêu cũ, ba chỉ tiêu ở tình trạng đó: hang_ton_kho,
    loi_nhuan_truoc_thue, loi_nhuan_sau_thue. Riêng hang_ton_kho là chỉ tiêu
    mà báo cáo VNM đã có lỗi đọc THẬT (alias khớp trúng dòng Dự phòng giảm
    giá, mã 142) — tức ví dụ mở đầu của cả proposal nằm ngoài tầm với của
    phương pháp. Phân rã Tài sản ngắn hạn kéo nó vào một đẳng thức.

    Nó vẫn CHƯA định vị được (lẫn trong lớp 5 chỉ tiêu con của mã 100), và
    đó là kết quả H0 phải báo cáo trung thực. Nhưng phát hiện được thì vòng
    đọc lại còn có chỗ bám; vô hình thì không.
    """
    A, field_order = _ma_tran_that(standard)

    assert zero_columns(A, field_order) == []


@pytest.mark.parametrize("standard", list(Standard))
def test_nam_chi_tieu_dinh_vi_duoc_va_dung_nam_chi_tieu_do(standard):
    """
    Kết quả H0 với bộ chỉ tiêu chốt ở Mốc 1: 5 chỉ tiêu có cột riêng biệt,
    tăng từ đúng 1 (`tong_tai_san`) của bộ 11 chỉ tiêu cũ.

    Chốt cả DANH SÁCH chứ không chỉ số lượng, vì con số 5 có thể giữ nguyên
    trong khi thành phần đổi — và thành phần mới là thứ quyết định bảng kết
    quả H2 đọc ra sao.

    Hai chuẩn cho cùng danh sách dù TT99 nhiều hơn một chỉ tiêu: Tài sản
    sinh học ngắn hạn rơi vào đúng lớp lẫn của các thành phần mã 100, nên nó
    không tự định vị được và cũng không kéo ai ra khỏi lớp đó.
    """
    A, field_order = _ma_tran_that(standard)
    dinh_vi = single_field_localizable(A, field_order)

    assert [ten for ten, duoc in dinh_vi.items() if duoc] == [
        "tai_san_ngan_han",
        "tai_san_dai_han",
        "tong_tai_san",
        "tong_nguon_von",
        "loi_nhuan_truoc_thue",
    ]


def test_van_khong_ton_tai_bo_field_nao_dinh_vi_duoc_hoan_toan():
    """
    Trả None là một KẾT QUẢ NGHIÊN CỨU hợp lệ, không phải lỗi, và nó SỐNG
    SÓT qua việc mở rộng bộ chỉ tiêu: kể cả với 21 chỉ tiêu và 7 đẳng thức,
    không tập con nào làm mọi lỗi một-trường đều định vị được.

    Đây là phát biểu H0 mà bài phải bảo vệ, và nó không dịu đi khi thêm chỉ
    tiêu — mỗi phân rã làm chính chỉ tiêu bị phân rã định vị được nhưng đẻ
    ra một tầng lá mới cùng lớp lẫn với nhau. Hệ quả: ràng buộc đơn thuần
    không bao giờ đủ, và trọng số dồn sang mỏ neo đơn vị tính với bước đọc
    lại — đúng như proposal mục 6.1 đã lường trước.

    Khác bộ 11 chỉ tiêu ở một điểm về PHƯƠNG PHÁP, không về kết luận: 21 chỉ
    tiêu là quá nhiều để vét cạn mọi tập con, nên hàm rơi về tìm kiếm tham
    lam và trả `chac_chan=False`. Cờ đó phải được đọc đúng — "không tìm
    thấy" chứ không phải "đã chứng minh không tồn tại".
    """
    bo, chac_chan = minimal_localizing_set(fields_for(Standard.TT99), identities_for(Standard.TT99))

    assert bo is None
    assert not chac_chan, "21 field thì không vét cạn nổi, phải báo là kết quả tham lam"


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
    bốn con số quyết định (hạng, chiều null, số field định vị được, số field
    cột toàn 0) và bảng ma trận có tên field phải nằm trong đó.
    """
    A, field_order = _ma_tran_that(Standard.TT99)
    duong_dan = tmp_path / "identifiability.md"

    noi_dung = report(A, field_order, identities_for(Standard.TT99), out_path=duong_dan)

    assert duong_dan.read_text(encoding="utf-8") == noi_dung
    assert "`rank(A)`: **7**" in noi_dung
    assert "`dim null(A)`: **14**" in noi_dung
    assert "**5 / 21**" in noi_dung
    assert "tong_tai_san" in noi_dung
    assert "cột toàn 0" in noi_dung


def test_bao_cao_noi_ro_KHONG_CO_field_cot_toan_0_thay_vi_im_lang(tmp_path):
    """
    Với bộ chỉ tiêu chốt ở Mốc 1 thì không còn field nào cột toàn 0, và báo
    cáo phải NÓI RA điều đó.

    Vì sao cần một test riêng: nếu chỉ dựa vào ghi chú từng dòng trong bảng
    thì "không còn field vô hình" và "quên in phần đó" trông giống hệt nhau
    trên trang giấy. Người đọc báo cáo không có cách nào phân biệt, mà đây
    lại đúng là con số Mốc 1 mua được.
    """
    A, field_order = _ma_tran_that(Standard.TT99)

    noi_dung = report(A, field_order, identities_for(Standard.TT99))

    assert "**cột toàn 0** (lỗi không PHÁT HIỆN được): **0 / 21** — không có" in noi_dung
