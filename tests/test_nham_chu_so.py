"""
Test ma trận nhầm chữ số dùng chung — nhất là CHIỀU TRA.

Ma trận đếm theo chiều `(thật → đọc thành)`, nhưng hai phía dùng nó theo hai
chiều ngược nhau: bộ tiêm lỗi biết giá trị thật và cần sinh cách đọc sai
(chiều xuôi), còn bộ sinh ứng viên chỉ thấy chữ số ĐÃ ĐỌC RA và phải đoán
ngược lại giá trị thật (chiều ngược).

Đảo nhầm chiều là lỗi câm hoàn hảo: mọi thứ vẫn chạy, ứng viên vẫn sinh ra
đủ số lượng, độ phủ vẫn ra một con số trông hợp lý — chỉ có điều bộ sinh ứng
viên đi tìm sai chữ số và không bao giờ trúng. Phần lớn test ở đây tồn tại
vì lý do đó.

Test dùng ma trận DỰNG TAY chứ không dùng ma trận đo được, để chúng chốt
LOGIC chứ không chốt số đo — số đo sẽ thay đổi mỗi lần đo lại trên dữ liệu
mới, và test gãy theo là test sai chỗ.
"""

import pytest

from nham_chu_so import (
    DEM_DO_DUOC,
    N_CAP_UNG_VIEN,
    cap_hang_dau,
    khoi_luong_tich_luy,
    lay_mau_doc_nham,
    ung_vien_cho_chu_so,
)

# Ma trận dựng tay: 9 hay bị đọc thành 0, ít hơn thì 6 thành 0, hiếm thì 9
# thành 8. Đúng hình dạng quan sát được ở HANDOFF mục 9, nhưng con số ở đây
# là do test đặt ra để tính nhẩm được.
DEM_MAU = {
    ("9", "0"): 60,
    ("6", "0"): 30,
    ("9", "8"): 10,
}


def test_chieu_nguoc_cho_bo_sinh_ung_vien():
    """
    Đọc ra `0` thì giá trị thật có thể là `9` hoặc `6` — KHÔNG phải ngược lại.

    Đây là test quan trọng nhất file. Nếu ai đó tra ma trận theo chiều xuôi ở
    phía sinh ứng viên, hàm sẽ trả về các chữ số mà `0` bị đọc THÀNH, tức đi
    tìm sai hướng hoàn toàn, và không có gì trong pipeline báo lỗi.
    """
    assert set(ung_vien_cho_chu_so("0", n=3, dem=DEM_MAU)) == {"9", "6"}

    # Chiều xuôi: `9` chưa bao giờ là thứ bị đọc nhầm THÀNH, nên tra ngược
    # cho `9` phải ra rỗng.
    assert ung_vien_cho_chu_so("9", n=3, dem=DEM_MAU) == ()


def test_ung_vien_ton_trong_tran_n_cap():
    """Chỉ N cặp hay nhầm nhất được dùng, phần đuôi bị bỏ."""
    # n=1 giữ đúng cặp (9,0), nên đọc ra `0` chỉ còn ứng viên `9`.
    assert set(ung_vien_cho_chu_so("0", n=1, dem=DEM_MAU)) == {"9"}
    # n=2 thêm cặp (6,0).
    assert set(ung_vien_cho_chu_so("0", n=2, dem=DEM_MAU)) == {"9", "6"}
    # Cặp (9,8) hạng ba, nên đọc ra `8` chỉ có ứng viên khi n >= 3.
    assert ung_vien_cho_chu_so("8", n=2, dem=DEM_MAU) == ()
    assert set(ung_vien_cho_chu_so("8", n=3, dem=DEM_MAU)) == {"9"}


def test_cap_hang_dau_xep_theo_tan_suat_giam_dan():
    assert cap_hang_dau(2, dem=DEM_MAU) == (("9", "0"), ("6", "0"))


def test_khoi_luong_tich_luy_don_dieu_va_ve_1():
    """
    Khối lượng tích luỹ tăng dần theo N và chạm 1.0 khi lấy hết cặp.

    Chạm 1.0 khi lấy hết là chỗ phải hiểu đúng: nó KHÔNG có nghĩa độ phủ
    thật bằng 1.0, mà chỉ có nghĩa mọi cặp ĐÃ QUAN SÁT ĐƯỢC đều nằm trong
    tập ứng viên. Lỗi thật rơi vào cặp chưa từng quan sát vẫn không sửa nổi.
    """
    m = [khoi_luong_tich_luy(n, dem=DEM_MAU) for n in (1, 2, 3, 4)]
    assert m == sorted(m)
    assert m[0] == pytest.approx(0.6)
    assert m[1] == pytest.approx(0.9)
    assert m[2] == pytest.approx(1.0)
    assert m[3] == pytest.approx(1.0)


def test_lay_mau_doc_nham_tai_lap_duoc_va_bao_nguon():
    """
    Bộ tiêm lấy mẫu theo phân phối đo được, và NÓI RA nó đã dùng số đo hay
    đã lùi về đều xác suất.

    Phải nói ra vì hai ca cần đọc khác nhau khi phân tích kết quả: lỗi tiêm
    theo số đo là lỗi mô phỏng thực tế, còn lỗi tiêm khi lùi về đều xác suất
    là lỗi của một chữ số mà phép đo chưa từng thấy hỏng — không cùng ý
    nghĩa, và gộp lại thì không tách được nữa.
    """
    import random

    a = lay_mau_doc_nham("9", random.Random(0), dem=DEM_MAU)
    b = lay_mau_doc_nham("9", random.Random(0), dem=DEM_MAU)
    assert a == b
    assert a[0] in {"0", "8"}
    assert a[1] == "do_duoc"

    # Chữ số chưa từng quan sát thấy hỏng: vẫn phải hỏng được, nhưng ghi rõ
    # là đã lùi về đều xác suất.
    doc, nguon = lay_mau_doc_nham("4", random.Random(0), dem=DEM_MAU)
    assert doc != "4"
    assert nguon == "deu_xac_suat"


def test_ma_tran_dong_bang_co_that_va_dung_hinh_dang():
    """Ma trận đã đo phải có mặt và mọi khoá là một cặp chữ số đơn."""
    assert DEM_DO_DUOC, "chưa có ma trận đo được — chạy do_ma_tran_nham_chu_so.py"
    for (that, doc), so_lan in DEM_DO_DUOC.items():
        assert that.isdigit() and len(that) == 1
        assert doc.isdigit() and len(doc) == 1
        assert that != doc
        assert so_lan > 0


def test_bo_sinh_ung_vien_KHONG_phu_het_ma_tran():
    """
    Tập ứng viên phải là tập con THỰC SỰ của giá đỡ phân phối tiêm.

    Đây là test bảo vệ chính quyết định của phương án (a). Nếu bộ sinh ứng
    viên mang trọn ma trận thì mọi lỗi tiêm vào đều sửa được, độ phủ lên
    1.0, và thí nghiệm mất khả năng làm lộ cơ chế ABSTAIN — mà ABSTAIN là
    lập luận chống bịa, đóng góp cấu trúc của cả bài.

    Test đỏ ở đây nghĩa là ai đó vừa biến thí nghiệm thành thứ không bác bỏ
    được, không phải nghĩa là một con số bị lệch.
    """
    assert N_CAP_UNG_VIEN < len(DEM_DO_DUOC)
    assert khoi_luong_tich_luy(N_CAP_UNG_VIEN) < 1.0
