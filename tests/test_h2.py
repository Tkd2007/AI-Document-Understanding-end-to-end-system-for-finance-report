"""
Chỗ đo H2 — định vị lỗi.

Ba thứ phải khoá, xếp theo hậu quả nếu hỏng.

1. **Chiều xếp hạng của baseline 8 ngược với họ rời rạc.** `Candidate.cost`
   là `−log(xác suất)` ở họ rời rạc nhưng là `|delta|` ở baseline 8. Dùng
   chung một chiều làm baseline bắt buộc xếp NGƯỢC, mà bảng kết quả vẫn ra
   số trông bình thường. Đây là kiểu làm yếu đối chứng mà mục 2 của
   `PREREGISTRATION.md` dựng lên để chống.
2. **Bảng rỗng tính là TRƯỢT, không phải bỏ khỏi mẫu.** Bỏ khỏi mẫu là biến
   chỉ số chính thành chỉ số "đúng khi trả lời", và khi đó một hệ trả lời
   đúng một lượt rồi im lặng mọi lượt còn lại đạt điểm tuyệt đối.
3. **Con số "đúng trên lượt ra tay" không được đứng một mình.** Chốt bằng
   chính ca hack: im lặng gần hết để đẩy con số phụ lên 1,000.
"""

import numpy as np
import pytest

from eval.h2 import (
    CAC_MUC_K,
    DongBang,
    LuotDinhVi,
    bang,
    cong_mot_luot,
    khung_dem,
    xep_hang_ged,
    xep_hang_l1,
    xep_hang_roi_rac,
)
from repair.candidates import Candidate
from repair.diagnose import Diagnosis, diagnose_l1_continuous
from repair.ged import dinh_vi_ged

THU_TU = ["a", "b", "tong"]
A_MOT = np.array([[1.0, 1.0, -1.0]])


def _chan_doan(da_sua: dict) -> Diagnosis:
    return Diagnosis(verdict="REPAIRED" if da_sua else "ABSTAIN", changed_fields=da_sua)


# ------------------------------------------- 1. chiều xếp hạng hai họ


def test_ho_roi_rac_xep_cost_TANG_dan():
    """cost = −log(xác suất), nên thấp là hợp lý hơn và phải đứng trước."""
    kq = _chan_doan({
        "a": Candidate(1.0, "sign", cost=2.3),
        "b": Candidate(2.0, "ocr_alt", cost=1.05),
    })

    assert xep_hang_roi_rac(kq) == ["b", "a"]


def test_baseline8_xep_do_lech_GIAM_dan_nguoc_chieu_ho_roi_rac():
    """
    ĐÂY LÀ TEST CANH VIỆC LÀM YẾU ĐỐI CHỨNG. Cùng một bộ `changed_fields`,
    hai hàm phải cho hai thứ tự NGƯỢC nhau. Nếu một ngày chúng cho cùng thứ
    tự thì một trong hai đang xếp sai, và baseline bắt buộc là bên chịu thiệt.
    """
    kq = _chan_doan({
        "a": Candidate(1.0, "l1_continuous", cost=900.0),
        "b": Candidate(2.0, "l1_continuous", cost=3.0),
    })

    assert xep_hang_l1(kq) == ["a", "b"]
    assert xep_hang_roi_rac(kq) == ["b", "a"]


def test_baseline8_that_tren_bo_giai_that_xep_dung_truong_bi_hieu_chinh_manh_nhat():
    """
    Không dựng `Candidate` bằng tay mà chạy thẳng bộ giải LP, để chiều xếp
    hạng được kiểm trên thứ mà baseline 8 THẬT SỰ trả về.

    Khẳng định theo ĐỘ LỚN chứ không theo tên trường, và đó là chỗ phải cẩn
    thận: trên một đẳng thức đơn lẻ `a + b = tổng`, cực tiểu L1 suy biến —
    sửa 270 ở `a`, ở `b` hay ở `tổng` đều cùng chuẩn L1 — nên bộ giải chọn
    trường nào là chuyện của thuật toán đỉnh, không phải của phương pháp.
    Docstring `_min_l1_lp` đã nêu đúng sự suy biến này, và nó sâu hơn vẻ ngoài:
    ngay cả ĐỘ LỚN từng phép hiệu chỉnh cũng không xác định duy nhất. Trên hệ
    dưới đây mọi nghiệm với `t ∈ [0, 5]` đều có cùng chuẩn L1 bằng 105, nên
    đỉnh mà bộ giải trả về có thể là 100 hoặc 95 tuỳ cài đặt.

    Vì vậy test khẳng định BẤT BIẾN chứ không khẳng định con số: tổng chuẩn L1
    đúng bằng 105, thứ tự giảm dần, và đỉnh đầu bảng LỚN HƠN HẲN đỉnh cuối
    bảng. Điều kiện lớn-hơn-hẳn là thứ làm khẳng định thứ tự có răng — thiếu
    nó thì một bảng xếp ngược vẫn lọt khi mọi độ lớn bằng nhau.
    """
    # Hai đẳng thức lệch hai lượng khác nhau, cộng một đẳng thức liên kết chéo
    # để không một trường nào chữa được cả hai.
    thu_tu = ["tsnh", "tsdh", "tong_ts", "no", "vcsh", "tong_nv"]
    A = np.array([
        [1.0, 1.0, -1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0, 1.0, -1.0],
        [0.0, 0.0, -1.0, 0.0, 0.0, 1.0],
    ])
    gia_tri = {"tsnh": 400.0, "tsdh": 700.0, "tong_ts": 1000.0,
               "no": 405.0, "vcsh": 600.0, "tong_nv": 1000.0}

    kq = diagnose_l1_continuous(gia_tri, {}, A, thu_tu)
    assert kq.verdict == "REPAIRED"

    xep = xep_hang_l1(kq)
    do_lech = [abs(kq.changed_fields[t].cost) for t in xep]

    assert sum(do_lech) == pytest.approx(105.0)
    assert do_lech == sorted(do_lech, reverse=True)
    assert do_lech[0] > do_lech[-1]


def test_ged_giu_nguyen_bang_xep_hang_cua_no():
    kq = dinh_vi_ged({"a": 10.0, "b": 20.0, "tong": 300.0}, A_MOT, THU_TU)

    assert xep_hang_ged(kq) == kq.xep_hang
    assert xep_hang_ged(kq)[0] in {"a", "b", "tong"}


def test_abstain_cho_bang_RONG_chu_khong_no():
    assert xep_hang_roi_rac(_chan_doan({})) == []
    assert xep_hang_l1(_chan_doan({})) == []


# ------------------------------------------- 2. bảng rỗng tính là trượt


def test_bang_rong_tinh_la_TRUOT_o_moi_muc_k():
    dem = khung_dem()
    cong_mot_luot(dem, LuotDinhVi([], {"a"}, n_loi_tiem=1), sinh_phan_du=True)

    assert dem["n_luot"] == 1
    assert dem["ra_tay"] == 0
    assert all(dem["trung"][k] == 0 for k in CAC_MUC_K)


def test_top3_bat_duoc_cai_ma_top1_bo_lo():
    dem = khung_dem()
    cong_mot_luot(dem, LuotDinhVi(["x", "y", "a"], {"a"}, 1), sinh_phan_du=True)

    assert dem["trung"][1] == 0
    assert dem["trung"][3] == 1


def test_luot_khong_sinh_phan_du_duoc_dem_rieng():
    """
    Lỗi rơi vào null(A) thì không phương pháp nào định vị nổi, và khoảng cách
    nằm ở đó là kết quả của H0 chứ không phải của H2. Trộn vào làm cả hai chỉ
    số khó đọc.
    """
    dem = khung_dem()
    cong_mot_luot(dem, LuotDinhVi([], {"a"}, 1), sinh_phan_du=False)
    cong_mot_luot(dem, LuotDinhVi(["a"], {"a"}, 1), sinh_phan_du=True)

    assert dem["khong_sinh_phan_du"] == 1
    dong = DongBang("thử", dem["n_luot"], dem["ra_tay"],
                    dem["khong_sinh_phan_du"], dem["trung"])
    assert dong.chinh(1) == pytest.approx(0.5)
    assert dong.tren_luot_co_phan_du(1) == pytest.approx(1.0)


# ------------------------------- 3. con số phụ không được đứng một mình


def test_im_lang_gan_het_thi_con_so_phu_len_1_va_ty_le_ra_tay_lo_ra():
    """
    Ca hack: trả lời đúng đúng một lượt rồi im lặng chín lượt còn lại. Con số
    phụ đạt 1,000 trong khi chỉ số chính chỉ 0,100, và tỷ lệ ra tay 0,100 là
    thứ nói ra chuyện gì đã xảy ra. Bảng phải in cả ba.
    """
    dem = khung_dem()
    cong_mot_luot(dem, LuotDinhVi(["a"], {"a"}, 1), sinh_phan_du=True)
    for _ in range(9):
        cong_mot_luot(dem, LuotDinhVi([], {"a"}, 1), sinh_phan_du=True)

    dong = DongBang("im lặng", dem["n_luot"], dem["ra_tay"],
                    dem["khong_sinh_phan_du"], dem["trung"])

    assert dong.chinh(1) == pytest.approx(0.1)
    assert dong.khi_ra_tay(1) == pytest.approx(1.0)
    assert dong.ty_le_ra_tay() == pytest.approx(0.1)

    dong_bang = bang({"im lặng": dem})
    assert any("Tỷ lệ ra tay" in d for d in dong_bang)


def test_bang_ghi_so_loi_tiem_moi_luot():
    """
    Số lỗi tiêm mỗi lượt phải hiện trên bảng. Không có nó thì bảng H2 bị đọc
    như đo độ giỏi của phương pháp, trong khi ở giao thức một-lỗi nó đang đo
    trần định vị của hệ ràng buộc.
    """
    dem = khung_dem()
    for _ in range(4):
        cong_mot_luot(dem, LuotDinhVi(["a"], {"a"}, 1), sinh_phan_du=True)

    dong_bang = "\n".join(bang({"đề xuất": dem}))

    assert "1.00** lỗi mỗi lượt" in dong_bang
    assert "Câu 8" in dong_bang


def test_bang_rong_khong_no():
    assert bang({}) == ["*(không có lượt nào)*"]
