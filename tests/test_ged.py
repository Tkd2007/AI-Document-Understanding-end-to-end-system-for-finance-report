"""
BASELINE 7 — kiểm định GED cổ điển trên không gian phần dư.

Ba lớp test, theo đúng thứ tự sức nặng.

**Lớp 1 — định lý.** Dưới giả thiết đúng MỘT field sai, thống kê GLR không
bao giờ xếp field nào khác lên trên field sai thật; và dấu bằng xảy ra đúng
khi hai cột tỷ lệ với nhau. Đây là bất đẳng thức Cauchy–Schwarz chứ không
phải một quan sát thực nghiệm, nên nó phải đúng trên ma trận ràng buộc THẬT
của cả hai chuẩn, với mọi field và mọi độ lớn lỗi. Nếu lớp này đỏ thì hoặc
công thức sai, hoặc ai đó vừa thay ma trận bằng thứ không phải hệ thuần nhất.

**Lớp 2 — chuẩn hoá theo chuẩn cột.** Bỏ phép chia cho `a_jᵀ·a_j` là cách làm
hỏng baseline này êm nhất: nó vẫn chạy, vẫn trả bảng xếp hạng, chỉ thiên vị
field xuất hiện trong nhiều đẳng thức. Một baseline bị làm yếu âm thầm thì
kết luận H2 so với nó mất giá trị — đúng thứ mục 2 của `PREREGISTRATION.md`
dựng lên để chống.

**Lớp 3 — trạng thái tường minh.** Không phát hiện, thiếu giá trị, và cột
toàn 0 là ba kết luận KHÁC NHAU về mặt khoa học, và bảng kết quả phải đếm
chúng riêng. Test chốt rằng chúng không bị gộp về một chỗ.
"""

import numpy as np
import pytest

from constraints import build_matrix
from fields_config import QuyUocDau, Standard, fields_for, identities_for
from repair.ged import dinh_vi_ged

# Hình dạng thu nhỏ của bảng cân đối, giữ đúng ba tính chất của hệ thật:
# có cặp cột trùng nhau (`tsnh`/`tsdh`), có cột riêng biệt (`tong_ts`), và
# có liên kết chéo giữa hai đẳng thức (`tong_ts` xuất hiện ở hai dòng).
THU_TU = ["tsnh", "tsdh", "tong_ts", "no", "vcsh", "tong_nv"]
A_CAN_DOI = np.array(
    [
        [1.0, 1.0, -1.0, 0.0, 0.0, 0.0],  # tsnh + tsdh = tong_ts
        [0.0, 0.0, 0.0, 1.0, 1.0, -1.0],  # no + vcsh  = tong_nv
        [0.0, 0.0, -1.0, 0.0, 0.0, 1.0],  # tong_nv    = tong_ts
    ]
)
DUNG = {"tsnh": 300.0, "tsdh": 700.0, "tong_ts": 1000.0, "no": 400.0,
        "vcsh": 600.0, "tong_nv": 1000.0}


def _cot(A: np.ndarray, field_order: list[str], ten: str) -> np.ndarray:
    return A[:, field_order.index(ten)]


def _ty_le(u: np.ndarray, v: np.ndarray) -> bool:
    """Hai vector khác 0 có tỷ lệ với nhau không — dấu bằng của Cauchy–Schwarz."""
    return bool(np.isclose(abs(float(u @ v)) ** 2, float(u @ u) * float(v @ v)))


def _dung_rieng(kq, ten: str) -> bool:
    """
    Field `ten` có đứng một mình ở thứ hạng của nó không?

    Hỏi đúng câu này chứ không hỏi "cả bảng có nhóm đồng hạng nào không":
    các field KHÁC đồng hạng với nhau là chuyện bình thường và không liên
    quan — chúng chỉ nói rằng phần dư không tách nổi mấy đứa vô can ấy.
    """
    return all(ten not in nhom for nhom in kq.nhom_dong_hang)


# ---------------------------------------------------------------- lớp 1


@pytest.mark.parametrize("standard", [Standard.TT200, Standard.TT99])
@pytest.mark.parametrize("do_lech", [1.0, -5e11, 9.0e12])
def test_mot_loi_thi_field_sai_KHONG_BAO_GIO_bi_xep_duoi(standard, do_lech):
    """
    Định lý, kiểm trên ma trận thật: tiêm đúng một lỗi vào field j thì mọi
    field xếp trên j đều phải có cột TỶ LỆ với cột của j.

    Nói cách khác, baseline này không bao giờ thua vì thuật toán — nó chỉ
    thua vì thông tin không tồn tại. Đó chính là trần định vị mà H2 đo, và
    là lý do bảng kết quả H2 phải ghi nhóm đồng hạng chứ không chỉ ghi Top-1.
    """
    fields = fields_for(standard)
    A, order = build_matrix(fields, identities_for(standard, QuyUocDau.TRU))

    # Giá trị nền không cần thoả ràng buộc: phần dư của một lỗi đơn chỉ phụ
    # thuộc vào ĐỘ LỆCH, nên xuất phát từ một bộ số cân bằng bất kỳ là đủ.
    # Dùng vector 0 cho khỏi phải dựng một bộ báo cáo giả cân đối tới đồng.
    nen = dict.fromkeys(order, 0.0)

    for ten in order:
        cot_that = _cot(A, order, ten)
        if not cot_that.any():
            continue

        kq = dinh_vi_ged({**nen, ten: do_lech}, A, order)

        assert kq.phat_hien, f"{standard.value}/{ten}: lỗi đơn phải phát hiện được"
        assert ten in kq.xep_hang

        tren = kq.xep_hang[: kq.xep_hang.index(ten)]
        for ten_khac in tren:
            assert _ty_le(_cot(A, order, ten_khac), cot_that), (
                f"{standard.value}: `{ten_khac}` xếp trên `{ten}` mà cột không "
                "tỷ lệ — thống kê GLR đã hỏng"
            )


def test_field_dinh_vi_duoc_thi_dung_top_1_mot_minh():
    """
    Mặt còn lại của định lý: cột riêng biệt thì không ai chia hạng với nó.
    `tong_ts` xuất hiện ở hai đẳng thức nên cột của nó tách khỏi mọi cột khác.
    """
    kq = dinh_vi_ged({**DUNG, "tong_ts": 1000.0 + 42.0}, A_CAN_DOI, THU_TU)

    assert kq.xep_hang[0] == "tong_ts"
    assert _dung_rieng(kq, "tong_ts")


def test_hai_cot_trung_nhau_thi_bao_DONG_HANG_chu_khong_giau_di():
    """
    `tsnh` và `tsdh` có cột bằng nhau từng phần tử, nên không kiểm định nào
    tách nổi. Thứ hạng giữa hai đứa là do quy ước phá hoà, và bảng kết quả
    phải biết điều đó — nếu không, một Top-1 do bốc thăm sẽ được đọc thành
    một Top-1 do bằng chứng.
    """
    kq = dinh_vi_ged({**DUNG, "tsnh": 300.0 + 7.0}, A_CAN_DOI, THU_TU)

    assert kq.xep_hang[:2] == ["tsnh", "tsdh"]
    assert ["tsnh", "tsdh"] in kq.nhom_dong_hang


def test_pha_hoa_theo_field_order_chu_khong_theo_may_moc():
    """
    Quy ước phá hoà phải là thứ tự `field_order` — cố định và mù với đáp án.
    Đảo thứ tự cột thì Top-1 của nhóm đồng hạng đảo theo, và đó là hành vi
    ĐÚNG: nó nói thẳng rằng thứ hạng trong nhóm không mang thông tin.
    """
    thu_tu_dao = ["tsdh", "tsnh", "tong_ts", "no", "vcsh", "tong_nv"]
    A_dao = A_CAN_DOI[:, [THU_TU.index(ten) for ten in thu_tu_dao]]

    kq = dinh_vi_ged({**DUNG, "tsnh": 300.0 + 7.0}, A_dao, thu_tu_dao)

    assert kq.xep_hang[:2] == ["tsdh", "tsnh"]


def test_do_lech_uoc_luong_tru_di_thi_phan_du_ve_khong():
    """
    Quy ước dấu của δ̂, chốt bằng hành vi chứ không bằng lời: trừ δ̂ khỏi giá
    trị đang có phải làm phần dư về 0. Nhầm dấu không làm gì nổ, chỉ ra một
    con số lệch gấp đôi.
    """
    sai = {**DUNG, "tong_ts": 1000.0 + 42.0}
    kq = dinh_vi_ged(sai, A_CAN_DOI, THU_TU)

    assert kq.do_lech_uoc_luong["tong_ts"] == pytest.approx(42.0)

    sua = {**sai, "tong_ts": sai["tong_ts"] - kq.do_lech_uoc_luong["tong_ts"]}
    x = np.array([sua[ten] for ten in THU_TU])
    assert np.allclose(A_CAN_DOI @ x, 0.0)


# ---------------------------------------------------------------- lớp 2


# Cột của `u` là (1, 1, 0); cột của `w` là (1, 1, 1) — `w` phủ trọn giá đỡ
# của `u` nên phép chiếu THÔ của hai đứa bằng nhau, và chỉ phép chia cho
# chuẩn cột mới tách được chúng.
THU_TU_CHUAN_HOA = ["u", "w", "p", "q", "s"]
A_CHUAN_HOA = np.array(
    [
        [1.0, 1.0, -1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0, -1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, -1.0],
    ]
)


def test_chuan_hoa_theo_chuan_cot_moi_tach_duoc_field_it_dang_thuc():
    """
    ĐÂY LÀ TEST CANH VIỆC LÀM YẾU BASELINE. Bỏ phép chia cho `a_jᵀ·a_j` thì
    `u` và `w` có cùng phép chiếu thô, nên `u` — field sai thật — tụt xuống
    đồng hạng với `w` thay vì đứng riêng ở Top-1.

    Thiên vị field xuất hiện trong nhiều đẳng thức là đúng loại khuyết tật
    không ai thấy: bảng xếp hạng vẫn ra, Top-3 gần như không đổi, chỉ Top-1
    xấu đi một cách có hệ thống trên đúng những field mà H2 quan tâm nhất.
    """
    nen = dict.fromkeys(THU_TU_CHUAN_HOA, 0.0)
    kq = dinh_vi_ged({**nen, "u": 10.0}, A_CHUAN_HOA, THU_TU_CHUAN_HOA)

    chieu_tho = A_CHUAN_HOA.T @ (A_CHUAN_HOA @ np.array([10.0, 0.0, 0.0, 0.0, 0.0]))
    assert abs(chieu_tho[0]) == pytest.approx(abs(chieu_tho[1])), (
        "tiền đề của test: phép chiếu THÔ của u và w phải bằng nhau"
    )

    assert kq.xep_hang[0] == "u"
    assert kq.thong_ke["u"] > kq.thong_ke["w"]
    assert _dung_rieng(kq, "u")


# ---------------------------------------------------------------- lớp 3


def test_khong_phat_hien_KHAC_thieu_gia_tri():
    """
    Hai ca cùng cho bảng xếp hạng rỗng nhưng nói hai điều trái ngược: một
    bên là giới hạn của RÀNG BUỘC, bên kia là giới hạn của khâu TRÍCH XUẤT.
    Gộp chúng lại là mất khả năng đọc bảng kết quả.
    """
    sach = dinh_vi_ged(DUNG, A_CAN_DOI, THU_TU)
    assert sach.phat_hien is False
    assert sach.ma_ly_do == "khong_phat_hien"
    assert sach.xep_hang == []

    thieu = dinh_vi_ged({**DUNG, "vcsh": None}, A_CAN_DOI, THU_TU)
    assert thieu.phat_hien is False
    assert thieu.ma_ly_do == "thieu_gia_tri"
    assert "vcsh" in thieu.ly_do


def test_cot_toan_khong_duoc_bao_rieng_va_khong_lam_no_phep_chia():
    """
    Field không xuất hiện trong đẳng thức nào có cột toàn 0. Lỗi ở đó không
    đổi phần dư, nên kiểm định không có gì để nói — nhưng phải nói ra rằng
    nó không có gì để nói, thay vì cho field ấy một thứ hạng vô nghĩa.

    Và phép chia cho `a_jᵀ·a_j` = 0 phải được chặn TRƯỚC khi chia.
    """
    thu_tu = [*THU_TU, "le_loi"]
    A = np.hstack([A_CAN_DOI, np.zeros((3, 1))])
    gia_tri = {**DUNG, "tong_ts": 1000.0 + 3.0, "le_loi": 5.0}

    kq = dinh_vi_ged(gia_tri, A, thu_tu)

    assert kq.khong_phat_hien_duoc == ["le_loi"]
    assert "le_loi" not in kq.xep_hang
    assert "le_loi" not in kq.thong_ke


def test_cot_toan_khong_van_duoc_bao_ca_khi_khong_phat_hien_gi():
    """
    Danh sách cột toàn 0 là tính chất của MA TRẬN, không phải của tài liệu,
    nên nó đúng kể cả khi tài liệu sạch. Trả rỗng ở ca sạch sẽ khiến người
    đọc tưởng trần phát hiện thay đổi theo từng tài liệu.
    """
    thu_tu = [*THU_TU, "le_loi"]
    A = np.hstack([A_CAN_DOI, np.zeros((3, 1))])

    kq = dinh_vi_ged({**DUNG, "le_loi": 5.0}, A, thu_tu)

    assert kq.ma_ly_do == "khong_phat_hien"
    assert kq.khong_phat_hien_duoc == ["le_loi"]


def test_khong_sua_gi_ca():
    """
    Baseline 7 là kiểm định ĐỊNH VỊ, không phải tầng sửa. Cho nó sửa là dựng
    lại baseline 8 dưới tên khác và H2 mất đối chứng thuần định vị, nên chốt
    bằng test rằng kết quả trả về không có chỗ nào chứa giá trị đã sửa.
    """
    kq = dinh_vi_ged({**DUNG, "tong_ts": 1000.0 + 42.0}, A_CAN_DOI, THU_TU)

    assert not hasattr(kq, "changed_fields")
    assert not hasattr(kq, "verdict")
