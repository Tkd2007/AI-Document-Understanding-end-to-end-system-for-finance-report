"""
Luật định vị lỗi đảo dấu bằng residual.

Điều các test dưới đây bảo vệ không phải là "hàm chạy đúng" mà là **phạm vi**
của luật: nó phải ra tay đúng ở lỗi dấu và im lặng ở mọi thứ khác. Một luật
định vị hay ra tay là một luật đang đoán, và đoán thì không viết vào bài được.
"""

import numpy as np
import pytest

from constraints import build_matrix
from fields_config import QuyUocDau, Standard, fields_for, identities_for
from repair.candidates import generate
from repair.diagnose import RESIDUAL_TOL as TOL_DIAGNOSE
from repair.diagnose import diagnose
from repair.luat_dau import RESIDUAL_TOL, luat_dau_residual


def _he_don_gian():
    """`a + b = c`, ba chỉ tiêu, một đẳng thức."""
    A = np.array([[1.0, 1.0, -1.0]])
    return A, ["a", "b", "c"]


def test_hai_hang_dung_sai_phai_bang_nhau():
    """
    Hai module dùng chung một dung sai. Để chúng trôi khỏi nhau thì luật dấu
    và bộ giải sẽ bất đồng về việc bộ số đã cân hay chưa, và bất đồng đó im
    lặng — không gì nổ, chỉ có kết luận lệch nhau.
    """
    assert RESIDUAL_TOL == TOL_DIAGNOSE


# ---------------------------------------------------------------------------
# Luật ra tay đúng chỗ
# ---------------------------------------------------------------------------


def test_dinh_vi_dung_truong_bi_lon_dau():
    A, field_order = _he_don_gian()
    # Thật: 30 + 70 = 100. Đọc lộn dấu b thành −70.
    kq = luat_dau_residual({"a": 30.0, "b": -70.0, "c": 100.0}, A, field_order)

    assert kq.trang_thai == "dinh_vi_duoc"
    assert kq.truong == "b"
    assert kq.gia_tri_sau == 70.0


def test_residual_bang_dung_hai_lan_gia_tri_bi_lon_dau():
    """
    Chữ ký số học của lỗi dấu, và là lý do luật này chứng minh được chứ không
    phải quan sát may mắn: residual bằng đúng ±2 lần con số đang cầm trong tay.
    """
    A, field_order = _he_don_gian()
    x = np.array([30.0, -70.0, 100.0])

    assert A @ x == pytest.approx([-140.0])
    assert abs((A @ x)[0]) == pytest.approx(2 * 70.0)


def test_lat_dau_dua_residual_ve_dung_khong():
    A, field_order = _he_don_gian()
    values = {"a": 30.0, "b": -70.0, "c": 100.0}
    kq = luat_dau_residual(values, A, field_order)

    sau = dict(values)
    sau[kq.truong] = kq.gia_tri_sau
    x = np.array([sau[t] for t in field_order])
    assert A @ x == pytest.approx([0.0])


# ---------------------------------------------------------------------------
# Luật im lặng đúng chỗ — phần quan trọng hơn
# ---------------------------------------------------------------------------


def test_im_lang_khi_khong_phai_loi_dau():
    """Nhầm một chữ số: residual có thật nhưng không cột nào giải thích được."""
    A, field_order = _he_don_gian()
    kq = luat_dau_residual({"a": 30.0, "b": 7.0, "c": 100.0}, A, field_order)

    assert kq.trang_thai == "im_lang"
    assert kq.truong is None
    assert kq.cac_ung_vien == []


def test_khong_co_lech_khi_bo_so_da_can():
    A, field_order = _he_don_gian()
    kq = luat_dau_residual({"a": 30.0, "b": 70.0, "c": 100.0}, A, field_order)

    assert kq.trang_thai == "khong_co_lech"
    assert kq.truong is None


def test_chon_nham_bang_KHONG_bat_duoc_va_do_la_gioi_han_that():
    """
    Ca SBT thu nhỏ: mọi con số lấy từ một bảng khác nhưng NHẤT QUÁN với nhau.
    Residual bằng 0 tuyệt đối, nên luật báo "không có lệch" trong khi cả ba
    giá trị đều sai. Đây là giới hạn của thông tin, không phải của thuật toán
    — và nó phải được chốt bằng test để đừng ai hứa quá tay trong bài báo.
    """
    A, field_order = _he_don_gian()
    kq = luat_dau_residual({"a": 3.0, "b": 7.0, "c": 10.0}, A, field_order)

    assert kq.trang_thai == "khong_co_lech"


def test_sai_don_vi_toan_cuc_cung_vo_hinh():
    """Hệ thuần nhất nên nhân cả vector với 1000 vẫn cân — `Aδ = (c−1)Ax* = 0`."""
    A, field_order = _he_don_gian()
    kq = luat_dau_residual({"a": 30e3, "b": 70e3, "c": 100e3}, A, field_order)

    assert kq.trang_thai == "khong_co_lech"


def test_gia_tri_bang_khong_khong_thanh_ung_vien():
    """Lật dấu số 0 không đổi gì, nên nó không được phép đếm là lời giải."""
    A, field_order = _he_don_gian()
    kq = luat_dau_residual({"a": 0.0, "b": 70.0, "c": 100.0}, A, field_order)

    assert "a" not in kq.cac_ung_vien


def test_thieu_gia_tri_thi_noi_ra_chu_khong_doan():
    A, field_order = _he_don_gian()
    kq = luat_dau_residual({"a": 30.0, "b": None, "c": 100.0}, A, field_order)

    assert kq.trang_thai == "thieu_gia_tri"
    assert kq.thieu == ["b"]


def test_mo_ho_thi_khong_chon_bua_mot_ung_vien():
    """
    Hai chỉ tiêu cùng giải thích được residual. Luật phải trả `mo_ho` và để
    `truong` là None — trình bày một trong hai như đã định vị là biến một ca
    không kết luận được thành một khẳng định.
    """
    A, field_order = _he_don_gian()
    # a = b = 50 và c = 0: residual = 100 = 2×50, nên lật dấu a hay lật dấu b
    # đều đưa nó về 0. c bị bỏ qua vì lật dấu số 0 không đổi gì.
    kq = luat_dau_residual({"a": 50.0, "b": 50.0, "c": 0.0}, A, field_order)

    assert kq.trang_thai == "mo_ho"
    assert kq.truong is None
    assert kq.cac_ung_vien == ["a", "b"]


def test_khong_nhan_ca_lat_dau_lam_vo_dang_thuc_khac():
    """
    Chỉ tiêu nằm trong hai đẳng thức: lật dấu làm cân cái thứ nhất nhưng làm
    vỡ cái thứ hai. Luật kiểm trên CẢ vector residual nên phải im lặng.

    Kiểm từng dòng riêng lẻ sẽ báo định vị được ở đây, và đó đúng là loại ca
    nguy hiểm nhất — một sửa đổi hợp lý cục bộ mà sai toàn cục.
    """
    # Đẳng thức 1: a + b = c. Đẳng thức 2: b + d = e.
    A = np.array(
        [
            [1.0, 1.0, -1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 1.0, -1.0],
        ]
    )
    field_order = ["a", "b", "c", "d", "e"]
    # b = −70 làm đẳng thức 1 lệch 2×70; nhưng đẳng thức 2 lại đang cân VỚI
    # b = −70, nên lật b sẽ làm nó vỡ.
    values = {"a": 30.0, "b": -70.0, "c": 100.0, "d": 10.0, "e": -60.0}
    kq = luat_dau_residual(values, A, field_order)

    assert kq.trang_thai == "im_lang"


# ---------------------------------------------------------------------------
# Nối vào diagnose()
# ---------------------------------------------------------------------------


def test_diagnose_ghi_nguon_dinh_vi_la_luat_dau():
    A, field_order = _he_don_gian()
    values = {"a": 30.0, "b": -70.0, "c": 100.0}
    candidates = {ten: generate(ten, values[ten]) for ten in field_order}

    kq = diagnose(values, candidates, A, field_order)

    assert kq.verdict == "REPAIRED"
    assert kq.nguon_dinh_vi == "luat_dau"
    assert kq.changed_fields["b"].value == 70.0


def test_diagnose_KHONG_ap_gia_tri_ngoai_tap_ung_vien():
    """
    Tập ứng viên phải ĐÓNG kể cả ở đường tắt của luật dấu. Truyền vào một tập
    ứng viên rỗng thì luật vẫn định vị được, nhưng KHÔNG được phép tự dựng ra
    con số nó vừa tính — nếu có đường nào để một giá trị ngoài tập lọt vào kết
    quả thì hệ ép số được và cả lập luận chống bịa sụp.
    """
    A, field_order = _he_don_gian()
    values = {"a": 30.0, "b": -70.0, "c": 100.0}

    kq = diagnose(values, {}, A, field_order)

    assert kq.verdict == "ABSTAIN"
    assert kq.nguon_dinh_vi == ""
    # Luật vẫn nói được nó thấy gì — chẩn đoán còn, chỉ là không sửa.
    assert kq.luat_dau.trang_thai == "dinh_vi_duoc"
    assert kq.luat_dau.truong == "b"


def test_diagnose_van_ghi_luat_dau_khi_luat_im_lang():
    """Tỷ lệ im lặng là số đo phạm vi áp dụng, nên ca im lặng phải được ghi."""
    A, field_order = _he_don_gian()
    values = {"a": 30.0, "b": 7.0, "c": 100.0}

    kq = diagnose(values, {}, A, field_order)

    assert kq.luat_dau is not None
    assert kq.luat_dau.trang_thai == "im_lang"


def test_tat_co_thi_diagnose_khong_chay_luat_dau():
    """Cần tắt được để đo riêng phần đóng góp của luật."""
    A, field_order = _he_don_gian()
    values = {"a": 30.0, "b": -70.0, "c": 100.0}
    candidates = {ten: generate(ten, values[ten]) for ten in field_order}

    kq = diagnose(values, candidates, A, field_order, dung_luat_dau=False)

    assert kq.luat_dau is None
    assert kq.nguon_dinh_vi == "tim_kiem_to_hop"


def test_verified_thi_luat_dau_la_None_chu_khong_phai_im_lang():
    """
    None nghĩa là "luật chưa từng chạy", `im_lang` nghĩa là "luật đã chạy và
    không thấy lỗi dấu". Gộp hai thứ đó là mất một trạng thái.
    """
    A, field_order = _he_don_gian()
    kq = diagnose({"a": 30.0, "b": 70.0, "c": 100.0}, {}, A, field_order)

    assert kq.verdict == "VERIFIED"
    assert kq.luat_dau is None


# ---------------------------------------------------------------------------
# Trên chính ma trận ràng buộc của dự án
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("standard", [Standard.TT200, Standard.TT99])
def test_chay_duoc_tren_ma_tran_that(standard):
    """
    Luật phải chạy được trên ma trận 26/27 chỉ tiêu chứ không chỉ trên hệ đồ
    chơi ba cột — số cột và số đẳng thức thật khác hẳn về quy mô.
    """
    A, field_order = build_matrix(fields_for(standard), identities_for(standard, QuyUocDau.TRU))
    values = dict.fromkeys(field_order, 0.0)

    kq = luat_dau_residual(values, A, field_order)

    # Vector toàn 0 thoả mọi đẳng thức thuần nhất.
    assert kq.trang_thai == "khong_co_lech"


def test_dinh_vi_duoc_ma_52_tren_dang_thuc_that():
    """
    Ca thật của dự án, thu về đúng đẳng thức B02 gây tranh cãi ở Câu 13:
    `Mã 60 = Mã 50 − Mã 51 − Mã 52`. Đọc lộn dấu thuế hoãn lại thì luật phải
    chỉ đúng tên nó, mà KHÔNG cần tới mệnh đề "dương khi mã 60 < mã 50" vốn
    đã bị bác bỏ ngày 28/08/2026.
    """
    standard = Standard.TT200
    bon_dong = [
        "loi_nhuan_truoc_thue",
        "thue_tndn_hien_hanh",
        "thue_tndn_hoan_lai",
        "loi_nhuan_sau_thue",
    ]
    # build_matrix() bỏ mọi đẳng thức có field nằm ngoài danh sách, nên đây
    # đúng bằng đẳng thức mã 60 như dự án ĐANG KHAI, không phải bản chép tay.
    A, field_order = build_matrix(bon_dong, identities_for(standard, QuyUocDau.TONG))
    assert A.shape[0] == 1

    # Mã 60 = 1000 + (−300) + 50 = 750. Mã 52 DƯƠNG là thu nhập thuế hoãn
    # lại, đúng ca của MWG và VRE mà Câu 13 phân xử là hợp lệ.
    values = {
        "loi_nhuan_truoc_thue": 1_000.0,
        "thue_tndn_hien_hanh": -300.0,
        "thue_tndn_hoan_lai": 50.0,
        "loi_nhuan_sau_thue": 750.0,
    }
    assert luat_dau_residual(values, A, field_order).trang_thai == "khong_co_lech"

    values["thue_tndn_hoan_lai"] = -50.0  # lộn dấu
    kq = luat_dau_residual(values, A, field_order)

    assert kq.trang_thai == "dinh_vi_duoc"
    assert kq.truong == "thue_tndn_hoan_lai"
    assert kq.gia_tri_sau == 50.0


# ---------------------------------------------------------------------------
# Mức CỤC BỘ — ca thật của MWG và VRE: ba dòng lộn dấu cùng lúc
# ---------------------------------------------------------------------------


def _hai_dang_thuc():
    """`a + b = c` và `d + e = f`, hai đẳng thức rời nhau."""
    A = np.array(
        [
            [1.0, 1.0, -1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0, 1.0, -1.0],
        ]
    )
    return A, ["a", "b", "c", "d", "e", "f"]


def test_nghi_ngo_khi_moi_dang_thuc_co_mot_loi_dau_rieng():
    """
    Hai lỗi dấu ở hai đẳng thức rời nhau. Không phép lật ĐƠN LẺ nào làm cân cả
    hệ, nên `dinh_vi_duoc` phải trượt — nhưng cả hai chỉ tiêu đều làm cân mọi
    đẳng thức chứa chúng, nên luật vẫn nói ra được cả hai.
    """
    A, field_order = _hai_dang_thuc()
    values = {"a": 30.0, "b": -70.0, "c": 100.0, "d": 5.0, "e": -15.0, "f": 20.0}

    kq = luat_dau_residual(values, A, field_order)

    assert kq.trang_thai == "nghi_ngo"
    assert kq.truong is None
    assert kq.cac_ung_vien == ["b", "e"]
    assert kq.so_dang_thuc_con_lech == 0


def test_nghi_ngo_dem_dung_so_dang_thuc_con_lech_vi_loi_khac():
    """
    Một đẳng thức lỗi dấu, một đẳng thức lỗi KHÔNG phải dấu. Luật chỉ tên được
    chỗ thứ nhất và phải nói thẳng rằng còn một đẳng thức nó không giải thích
    được — đó là con số đi vào certificate.
    """
    A, field_order = _hai_dang_thuc()
    values = {"a": 30.0, "b": -70.0, "c": 100.0, "d": 5.0, "e": 15.0, "f": 99.0}

    kq = luat_dau_residual(values, A, field_order)

    assert kq.trang_thai == "nghi_ngo"
    assert kq.cac_ung_vien == ["b"]
    assert kq.so_dang_thuc_con_lech == 1


def test_diagnose_KHONG_sua_theo_nghi_ngo():
    """
    `nghi_ngo` là chẩn đoán, không phải giấy phép sửa. Sửa theo nó thì bảng vẫn
    không cân sau phép sửa, tức mất luôn thứ duy nhất xác nhận phép sửa đúng —
    và một hệ sửa mà không xác nhận được chính là hệ bịa số.
    """
    A, field_order = _hai_dang_thuc()
    values = {"a": 30.0, "b": -70.0, "c": 100.0, "d": 5.0, "e": -15.0, "f": 20.0}
    candidates = {ten: generate(ten, values[ten]) for ten in field_order}

    kq = diagnose(values, candidates, A, field_order)

    assert kq.nguon_dinh_vi != "luat_dau"
    assert kq.luat_dau.trang_thai == "nghi_ngo"


def test_im_lang_van_dem_so_dang_thuc_con_lech():
    """Im lặng mà kèm con số thì người đọc biết luật đã bỏ qua bao nhiêu."""
    A, field_order = _hai_dang_thuc()
    values = {"a": 30.0, "b": 7.0, "c": 100.0, "d": 5.0, "e": 15.0, "f": 99.0}

    kq = luat_dau_residual(values, A, field_order)

    assert kq.trang_thai == "im_lang"
    assert kq.so_dang_thuc_con_lech == 2
