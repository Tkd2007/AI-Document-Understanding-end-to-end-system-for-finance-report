"""
Chốt việc bộ chỉ tiêu đi theo CHUẨN, không đi theo FIELD_MAP.

`FIELD_MAP` là HỢP của cả hai chuẩn. Dùng nó ở chỗ lẽ ra phải dùng
`fields_for(standard)` không làm gì nổ — nó chỉ lặng lẽ thêm vào một chỉ
tiêu mà chuẩn đang xét không có, và mọi hỏng hóc sau đó đều là hỏng hóc im
lặng. Mốc 1 đã gặp đúng lỗi này một lần ở `constraints.py` và dựng
`fields_for()` để chống; các test dưới đây chống nốt ba chỗ còn lại.
"""

import os

import pytest

os.environ.setdefault("OPENROUTER_API_KEY", "khoa-gia-cho-test")
os.environ.setdefault("OPENROUTER_MODEL", "model-gia-cho-test")

from extract_baseline import extract_all_fields  # noqa: E402
from extract_vlm import build_prompt  # noqa: E402
from fields_config import Standard, empty_result, fields_for  # noqa: E402

# Chỉ tiêu CHỈ có ở TT99. Với TT200 nó không tồn tại trên biểu mẫu, nên mọi
# nơi hỏi tới nó trong ngữ cảnh TT200 đều là hỏi về một dòng không có thật.
RIENG_TT99 = "tai_san_sinh_hoc_ngan_han"


def test_prompt_TT200_khong_hoi_ve_dong_ma_TT200_khong_co():
    """
    Prompt cho báo cáo TT200 không được nhắc tới Tài sản sinh học ngắn hạn.

    Bản trước duyệt FIELD_MAP nên chỉ tiêu này rơi vào "NHÓM KHÁC" — nhóm
    không có mã số để model đối chiếu — rồi vào cả khuôn JSON bắt buộc trả
    về. Tức prompt đi bảo model tìm một dòng không tồn tại trên giấy. Luật 3
    có dặn trả null khi không thấy, nhưng mời model đi tìm cái không có là
    tự tạo áp lực bịa ở đúng chỗ nhạy cảm nhất với luận điểm của cả bài.
    """
    prompt = build_prompt(Standard.TT200)

    assert RIENG_TT99 not in prompt
    assert "Tài sản sinh học" not in prompt


def test_prompt_TT99_van_hoi_ve_dong_ma_TT99_co():
    """Chiều ngược lại: cắt quá tay cũng là lỗi, và nó lặng lẽ y hệt."""
    assert RIENG_TT99 in build_prompt(Standard.TT99)


@pytest.mark.parametrize(
    "standard, so_field",
    [(Standard.TT200, 26), (Standard.TT99, 27)],
)
def test_khung_ket_qua_dung_so_chi_tieu_cua_chuan(standard, so_field):
    """
    Khung tích luỹ phải đúng bộ chỉ tiêu của chuẩn, cộng khoá đơn vị tính.

    Khung thừa một chỉ tiêu không bao giờ điền được sẽ làm mọi chỗ đếm "đã
    đủ field chưa" chờ nó vĩnh viễn — xem test dừng sớm bên dưới.
    """
    khung = empty_result(standard)

    assert len(khung) == so_field + 1
    assert "don_vi_tinh" in khung
    assert len(fields_for(standard)) == so_field


def test_nhanh_OCR_khong_di_tim_dong_khong_thuoc_chuan():
    """
    Nhánh regex cũng chỉ trích những chỉ tiêu chuẩn đó thật sự có.

    Ít tai hại hơn prompt vì regex không khớp thì chỉ trả None, nhưng nó
    vẫn sinh ra một khoá lẽ ra không tồn tại trong kết quả của TT200 — và
    khoá thừa đó chính là thứ làm đẳng thức bị bỏ qua ở tầng dưới.
    """
    ket_qua = extract_all_fields("một trang không có gì", Standard.TT200)

    assert RIENG_TT99 not in ket_qua
    assert set(ket_qua) == set(fields_for(Standard.TT200))
