"""
Test đọc con số như nó được in trên báo cáo tài chính Việt Nam.

Mọi ca ở đây lấy từ `ANNOTATION-GUIDELINE.md` mục 3.3 và 3.4. Đọc sai một ô
không làm gì nổ — nó tạo ra một giá trị trông hợp lệ trong tập gold, tức
đúng loại lỗi câm mà cả nghiên cứu sinh ra để đo. Nên phần này phải có test
dày hơn phần còn lại của công cụ.
"""

import pytest

from gan_nhan.so_viet import BANG_KHONG, KHONG_DOC_RA, KHONG_RO, SO, doc_so, quy_doi


@pytest.mark.parametrize(
    ("raw", "mong_doi"),
    [
        ("1.234.567", 1234567),      # phân nhóm kiểu Việt Nam
        ("1,234,567", 1234567),      # phân nhóm kiểu Anh Mỹ
        ("1 234 567", 1234567),      # bản dán từ PDF hay ra khoảng trắng
        ("29403", 29403),
        ("0", 0),
    ],
)
def test_doc_so_duong(raw, mong_doi):
    assert doc_so(raw) == (mong_doi, SO)


@pytest.mark.parametrize("raw", ["(1.234.567)", "-1.234.567", "−1.234.567"])
def test_so_am_ghi_bang_ngoac_hay_dau_tru_deu_la_so_am(raw):
    """
    Guideline mục 3.3: báo cáo in số âm trong ngoặc đơn, một số báo cáo dùng
    dấu trừ, cả hai ghi như nhau. Dấu trừ toán học (U+2212) có mặt vì OCR
    trả về nó thay cho dấu trừ ASCII trên bản scan.
    """
    assert doc_so(raw) == (-1234567, SO)


@pytest.mark.parametrize("raw", ["-", "–", "—", "  -  "])
def test_dau_gach_la_khong_chu_khong_phai_thieu_du_lieu(raw):
    """
    Guideline mục 3.4: dấu gạch nghĩa là chỉ tiêu CÓ trên biểu mẫu nhưng
    không phát sinh trong kỳ, ghi 0.

    Trả kèm trạng thái riêng chứ không chỉ trả 0, vì `0` do người đọc thấy
    dấu gạch và `0` do người gõ thẳng số không là hai chuyện khác nhau khi
    phân tích bất đồng giữa hai người gán nhãn.
    """
    assert doc_so(raw) == (0.0, BANG_KHONG)


@pytest.mark.parametrize("raw", ["?", "null", "N/A"])
def test_co_dong_ma_doc_khong_ra_thi_la_null_chu_khong_phai_0(raw):
    """
    Đây là ranh giới đắt nhất của guideline mục 3.4: `null` dành riêng cho
    "chưa biết", còn "bằng không" thì ghi 0. Lẫn hai thứ này làm hỏng bước
    kiểm đẳng thức, vì đẳng thức chứa `null` sẽ KHÔNG chạy.
    """
    assert doc_so(raw) == (None, KHONG_DOC_RA)


def test_chuoi_rong_khong_phai_la_bang_khong():
    """
    Rỗng nghĩa là chưa gõ gì, KHÔNG phải "đã xem và không có số".

    Gộp hai thứ này lại là cách âm thầm biến mọi ô bỏ quên thành một tuyên
    bố đã xem xét — và một tài liệu gán nhãn dở dang sẽ đi vào tập gold
    trông y hệt một tài liệu đã xong.
    """
    assert doc_so("") == (None, KHONG_RO)
    assert doc_so(None) == (None, KHONG_RO)


@pytest.mark.parametrize("raw", ["12a3", "abc", "1..2", "1.2.3,4,5"])
def test_chuoi_khong_khop_quy_tac_nao_thi_bao_khong_ro(raw):
    """Không đoán. Người gõ nhầm phải thấy ô đỏ chứ không phải một con số."""
    assert doc_so(raw)[1] == KHONG_RO


def test_ca_nhap_nhang_mot_dau_cham_ba_chu_so_chon_phan_nhom():
    """
    `1.234` nhập nhằng thật: một nghìn hai trăm ba mươi tư, hay 1,234?

    Chọn phân nhóm, và lý do là bất đối xứng của hậu quả. Báo cáo ghi bằng
    ĐỒNG gần như không bao giờ có phần thập phân, nên chọn phân nhóm gần như
    luôn đúng. Quan trọng hơn: chọn sai theo hướng này lệch 1000 lần — đủ
    lớn để đẳng thức kế toán bắt được — còn chọn sai theo hướng kia cho ra
    một con số nhỏ trông hoàn toàn hợp lý và không ràng buộc nào thấy.
    """
    assert doc_so("1.234") == (1234, SO)
    assert doc_so("1,234") == (1234, SO)


def test_hai_loai_dau_thi_dau_dung_sau_la_thap_phan():
    """
    Quy tắc này đúng với cả quy ước Việt Nam lẫn Anh Mỹ mà không cần biết
    báo cáo theo quy ước nào — đó chính là lý do chọn nó.
    """
    assert doc_so("1.234,5") == (1234.5, SO)     # Việt Nam
    assert doc_so("1,234.5") == (1234.5, SO)     # Anh Mỹ


def test_mot_dau_cham_hai_chu_so_la_thap_phan():
    """`29,4` không thể là phân nhóm vì nhóm hàng nghìn luôn đủ 3 chữ số."""
    assert doc_so("29,4") == (29.4, SO)


def test_quy_doi_ve_dong_theo_he_so_don_vi():
    """
    Guideline mục 3.2: báo cáo in `29.403` ở đơn vị "triệu đồng" thì tập gold
    ghi `29403000000`.
    """
    assert quy_doi(29403, 1_000_000) == 29_403_000_000
    assert quy_doi(-1234.5, 1000) == -1_234_500
    assert quy_doi(None, 1_000_000) is None


def test_quy_doi_lam_tron_ve_nguyen():
    """Đơn vị nhỏ nhất của tiền Việt Nam là đồng; phần lẻ chỉ tạo sai lệch giả."""
    assert quy_doi(1.4, 1) == 1
    assert quy_doi(1.6, 1) == 2
