"""
Phép chấm của `src/eval/do_luat_dau.py`.

Thứ đáng khoá ở đây không phải là bảng in ra đẹp, mà là **cách chấm**: một
lần luật ra tay chỉ được tính đúng khi chỉ tiêu nó gọi tên thật sự lộn dấu.
Nới chỗ đó ra thì con số "báo nhầm 0/10" mất hết nghĩa, và nó là con số duy
nhất trong báo cáo mà bài viết sẽ dựa vào.
"""

import pytest

from eval.do_luat_dau import _chay_mot_dieu_kien, _loi_dau_that, _truong_sai
from fields_config import Standard


def test_loi_dau_that_nhan_dung_ca_lat_dau():
    gold = {"gia_von_hang_ban": 100.0, "hang_ton_kho": 50.0}
    du_doan = {"gia_von_hang_ban": -100.0, "hang_ton_kho": 50.0}

    assert _loi_dau_that(du_doan, gold) == {"gia_von_hang_ban"}


def test_loi_dau_that_bo_qua_gold_bang_khong():
    """
    `−0 == 0`, nên mọi ô gold bằng 0 mà dự đoán cũng bằng 0 sẽ tự khai là lỗi
    dấu và làm mẫu số phồng lên bằng những ca không có lỗi nào. Sau tu chính
    24/08/2026, dòng vắng mặt trên biểu mẫu được ghi `0`, nên số ô như vậy
    không hề nhỏ.
    """
    gold = {"a": 0.0, "b": 0}
    du_doan = {"a": 0.0, "b": 0}

    assert _loi_dau_that(du_doan, gold) == set()


def test_loi_dau_that_bo_qua_o_khong_doc_duoc():
    """Bỏ trống không phải lỗi dấu — hệ biết mình thất bại ở đó."""
    gold = {"a": 100.0}
    du_doan = {"a": None}

    assert _loi_dau_that(du_doan, gold) == set()
    assert _truong_sai(du_doan, gold) == set()


def _bon_dong_thue(standard=Standard.TT200):
    """Bộ giá trị chỉ gồm bốn dòng của đẳng thức mã 60, đã cân."""
    gold = {
        "loi_nhuan_truoc_thue": 1_000.0,
        "thue_tndn_hien_hanh": -300.0,
        "thue_tndn_hoan_lai": 50.0,
        "loi_nhuan_sau_thue": 750.0,
    }
    return gold, standard


def test_ra_tay_dung_ten_thi_tinh_la_dinh_vi_dung():
    gold, standard = _bon_dong_thue()
    du_doan = {**gold, "thue_tndn_hoan_lai": -50.0}

    r = _chay_mot_dieu_kien(du_doan, gold, standard)

    assert r["trang_thai"] == "dinh_vi_duoc"
    assert r["phan_xu"] == "dinh_vi_dung"


def test_im_lang_khi_khong_co_loi_dau_thi_tinh_la_dung():
    gold, standard = _bon_dong_thue()

    r = _chay_mot_dieu_kien(dict(gold), gold, standard)

    assert r["phan_xu"] == "im_lang_dung"


def test_co_loi_dau_ma_luat_im_lang_thi_tinh_la_BO_SOT():
    """
    Im lặng trước một lỗi dấu có thật KHÔNG được tính là "im lặng đúng". Gộp
    hai thứ đó là biến giới hạn của luật thành thành tích của nó.

    Ca dựng ở đây là lỗi dấu nằm NGOÀI mọi đẳng thức dựng được, tức đúng loại
    lỗi mà ràng buộc kế toán mù — quan sát thật trên `VHC_2025Q1_TT200`.
    """
    gold, standard = _bon_dong_thue()
    gold = {**gold, "tien_dau_ky": 500.0}
    du_doan = {**gold, "tien_dau_ky": -500.0}

    r = _chay_mot_dieu_kien(du_doan, gold, standard)

    assert r["so_loi_dau_that"] == 1
    assert r["phan_xu"] == "bo_sot"


def test_khong_dung_dang_thuc_nao_thi_noi_ra_chu_khong_tinh_la_im_lang_dung():
    """
    Không dựng được đẳng thức nào thì luật chưa từng chạy. Trả `khong_do_duoc`
    thay vì `im_lang_dung`, nếu không thì mọi tài liệu đọc được quá ít chỉ tiêu
    sẽ lặng lẽ cộng điểm cho luật.
    """
    r = _chay_mot_dieu_kien({"hang_ton_kho": 1.0}, {"hang_ton_kho": 2.0}, Standard.TT200)

    assert r["phan_xu"] == "khong_do_duoc"


@pytest.mark.parametrize("standard", [Standard.TT200, Standard.TT99])
def test_chay_duoc_tren_ca_hai_chuan(standard):
    gold, _ = _bon_dong_thue()

    r = _chay_mot_dieu_kien(dict(gold), gold, standard)

    assert r["so_dang_thuc"] >= 1
