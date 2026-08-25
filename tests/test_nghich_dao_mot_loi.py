"""
Test phần đại số của phép đo "ràng buộc có tự chốt giá trị thật không".

VÌ SAO ĐÁNG CÓ TEST RIÊNG: hàm này quyết định một con số sẽ vào bài — trần
trên mà mọi bộ giải liên tục đạt được mà không cần đọc lại tài liệu. Nó chỉ
trả về ba chuỗi, nên hỏng thì không có gì nổ: bảng vẫn in ra đủ ba cột, chỉ
là các con số nói sai. Cụ thể, bỏ bước kiểm residual có nằm TRỌN trên phương
cột hay không sẽ làm mọi trường trông như chốt được, kể cả khi lỗi thật nằm ở
chỗ khác, và trần bị thổi lên.

Dùng ma trận dựng tay chứ không dùng dữ liệu XBRL, để mỗi ca kiểm đúng một
tính chất và đọc được bằng mắt.
"""

import numpy as np

from eval.do_nghich_dao_mot_loi import _rang_buoc_co_chot_gia_tri

# Một đẳng thức duy nhất: a + b − tong = 0. Cột của `le` toàn 0, tức không
# ràng buộc nào bảo vệ nó — đúng ca mà H0 gọi là không định vị được.
THU_TU = ["a", "b", "tong", "le"]
A = np.array([[1.0, 1.0, -1.0, 0.0]])

THAT = {"a": 300.0, "b": 200.0, "tong": 500.0, "le": 42.0}


def test_mot_loi_tren_truong_co_rang_buoc_thi_chot_dung():
    """
    Lỗi đơn ở trường có cột khác 0: residual nằm trọn trên phương cột ấy.

    Đây là ca mà nghịch đảo cho lại đúng giá trị thật tới từng chữ số, nên
    MỌI bộ giải liên tục lấy lại được đáp án mà không cần đọc lại tài liệu.
    Chính nó là trần trên của baseline 9.
    """
    hong = dict(THAT, a=390.0)

    assert _rang_buoc_co_chot_gia_tri(A, THU_TU, hong, THAT, "a") == "chot_dung"


def test_truong_khong_tham_gia_dang_thuc_nao_thi_bao_cot_bang_khong():
    """
    Cột bằng 0 là kết quả của H0, không phải của phương pháp nào cả.

    Phải tách khỏi `khong_chot`: hai trạng thái này dẫn tới hai kết luận khác
    hẳn nhau. Cột bằng 0 nghĩa là thông tin KHÔNG TỒN TẠI, còn `khong_chot`
    nghĩa là thông tin có nhưng không đủ chốt một mình.
    """
    hong = dict(THAT, le=999.0)

    assert _rang_buoc_co_chot_gia_tri(A, THU_TU, hong, THAT, "le") == "cot_bang_khong"


def test_hai_loi_dong_thoi_thi_khong_chot():
    """
    Khi có lỗi thứ hai, residual thôi nằm trên phương cột của trường đang xét.

    Nghịch đảo lúc này ra một giá trị khác giá trị thật, và đó đúng là khoảng
    hở mà việc đọc lại nguồn tồn tại để lấp. Bỏ bước kiểm phương thì ca này
    bị đếm nhầm thành `chot_dung`.
    """
    hong = dict(THAT, a=390.0, b=250.0)

    assert _rang_buoc_co_chot_gia_tri(A, THU_TU, hong, THAT, "a") == "khong_chot"


def test_residual_bang_khong_van_khong_goi_la_chot_khi_gia_tri_con_sai():
    """
    Lỗi nằm trong `null(A)` thì residual bằng 0 mà giá trị vẫn sai.

    Ở đây sai đơn vị toàn cục: nhân mọi giá trị với 1000 giữ nguyên đẳng thức
    nên residual bằng 0, phương cột khớp tầm thường, nhưng nghịch đảo trả về
    chính giá trị hỏng chứ không phải giá trị thật. Hàm phải nói `khong_chot`
    — nếu nó nói `chot_dung` thì trần bị thổi lên bằng đúng số lượt mà H0 đã
    chứng minh là vô vọng.
    """
    hong = {"a": 300_000.0, "b": 200_000.0, "tong": 500_000.0, "le": 42_000.0}

    assert _rang_buoc_co_chot_gia_tri(A, THU_TU, hong, THAT, "a") == "khong_chot"


# Hai đẳng thức: a + b − tong = 0 và b − d = 0.
#
# Cần ma trận thứ hai vì với MỘT đẳng thức, residual và cột đều là vector một
# chiều nên luôn cùng phương một cách tầm thường — bước kiểm phương không bao
# giờ chạy tới. Chỉ từ hai đẳng thức trở lên nó mới có việc để làm.
THU_TU_2 = ["a", "b", "tong", "d"]
A_2 = np.array([[1.0, 1.0, -1.0, 0.0], [0.0, 1.0, 0.0, -1.0]])

THAT_2 = {"a": 300.0, "b": 200.0, "tong": 500.0, "d": 200.0}


def test_nghich_dao_ra_dung_gia_tri_van_la_khong_chot_khi_con_dang_thuc_khac_vi_pham():
    """
    Ca duy nhất bắt được lỗi bỏ bước kiểm phương, nên nó phải có mặt.

    Tiêm hai lỗi: `a` lệch +90 và `d` lệch −50. Xét riêng trường `a`, residual
    là [90, 50] còn cột của `a` là [1, 0]; nghịch đảo từ thành phần lớn nhất
    cho delta = −90, tức ra ĐÚNG giá trị thật 300. Nhưng thả một mình `a` thì
    đẳng thức thứ hai vẫn vi phạm, nên không bộ giải liên tục nào có nghiệm ở
    đây — câu trả lời đúng là `khong_chot`.

    Bỏ bước kiểm phương thì ca này bị đếm thành `chot_dung` và trần trên bị
    thổi lên, tức con số vào bài nói phương pháp đề xuất còn xa trần hơn thực
    tế. Đây là kiểu sai làm hại chính luận điểm của bài.
    """
    hong = dict(THAT_2, a=390.0, d=150.0)

    assert _rang_buoc_co_chot_gia_tri(A_2, THU_TU_2, hong, THAT_2, "a") == "khong_chot"


def test_loi_don_tren_ma_tran_nhieu_dang_thuc_van_chot_dung():
    """Đối chứng cho ca trên: cùng ma trận, một lỗi, thì phải chốt được."""
    hong = dict(THAT_2, a=390.0)

    assert _rang_buoc_co_chot_gia_tri(A_2, THU_TU_2, hong, THAT_2, "a") == "chot_dung"
