"""
Nới mép trên vùng bảng để dòng "Đơn vị tính" lọt vào vùng cắt.

Số đo trong bộ test này lấy từ BMP_2026Q1_TT99 trang 4, đo ngày 27/08/2026:
trang cao 3504 px, box `plain text` chứa dòng đơn vị ở y 416..471 (conf
0,86), vùng bảng bắt đầu ở y 516. Chạy được mà không cần YOLO — tran_noi_tren
là hàm hình học thuần.
"""

from PIL import Image

from layout_detection import PADDING, TY_LE_NOI_TREN, cat_vung, tran_noi_tren

CAO_TRANG = 3504
BANG = (300, 516, 2400, 2949)
DONG_DON_VI = (300, 416, 1200, 471)
TIEU_DE_CONG_TY = (300, 82, 2000, 208)


def test_noi_toi_dinh_box_gan_nhat_phia_tren():
    """
    Phải lấy TRỌN box phía trên, không dừng ở mép dưới của nó.

    Dòng cần lấy nằm bên trong box ấy; dừng ở mép dưới (471) thì vẫn hụt
    đúng dòng cần lấy, chỉ hụt ít hơn.
    """
    assert tran_noi_tren(BANG, [DONG_DON_VI], CAO_TRANG) == DONG_DON_VI[1]


def test_khong_co_box_o_tren_thi_noi_tron_khoang_du_phong():
    tran = tran_noi_tren(BANG, [], CAO_TRANG)
    assert tran == BANG[1] - int(CAO_TRANG * TY_LE_NOI_TREN)


def test_bi_chan_boi_ty_le_chieu_cao_trang():
    """Box tiêu đề công ty ở tận y 82 không được kéo vùng cắt lên tới đó."""
    tran = tran_noi_tren(BANG, [TIEU_DE_CONG_TY], CAO_TRANG)
    assert tran == BANG[1] - int(CAO_TRANG * TY_LE_NOI_TREN)
    assert tran > TIEU_DE_CONG_TY[3]


def test_box_khong_chong_ngang_thi_bo_qua():
    """
    Một box ở lề trang không được kéo vùng cắt lên.

    Bỏ điều kiện chồng ngang thì số trang hay ghi chú ngoài lề cũng nới được
    vùng cắt, và vùng rộng ra vì thứ chẳng liên quan gì tới bảng.
    """
    ngoai_le = (10, 300, 120, 340)
    assert tran_noi_tren(BANG, [ngoai_le], CAO_TRANG) == BANG[1] - int(
        CAO_TRANG * TY_LE_NOI_TREN
    )


def test_ty_le_khong_phai_pixel_co_dinh():
    """
    Cùng một bố cục, hai độ phân giải: khoảng nới phải khác nhau.

    Đây là ràng buộc người chủ trì đặt ra — tập gold trải từ 89,9 tới 295,8
    dpi, nên một hằng số pixel vừa cho bản này sẽ hụt hoặc thừa cho bản kia.
    """
    thap = tran_noi_tren((300, 200, 2400, 1000), [], 1200)
    cao = tran_noi_tren((300, 600, 2400, 3000), [], 3600)
    assert 200 - thap != 600 - cao


def test_cat_vung_khong_truyen_tran_thi_giu_hanh_vi_cu():
    trang = Image.new("RGB", (2500, CAO_TRANG))
    vung = cat_vung(trang, BANG, confidence=0.9)
    assert vung.bbox[1] == BANG[1] - PADDING


def test_cat_vung_lay_tran_rong_hon_padding():
    trang = Image.new("RGB", (2500, CAO_TRANG))
    vung = cat_vung(trang, BANG, confidence=0.9, tran_tren=DONG_DON_VI[1])
    assert vung.bbox[1] == DONG_DON_VI[1]
    # Vùng cắt phải ôm trọn dòng đơn vị, không chỉ chạm mép nó.
    assert vung.bbox[1] <= DONG_DON_VI[1] and vung.bbox[3] >= DONG_DON_VI[3]


def test_tran_hep_hon_padding_thi_padding_thang():
    """
    tran_tren sát bảng hơn PADDING thì vẫn phải giữ PADDING.

    Nới mép trên là để LẤY THÊM; không bao giờ được cắt hẹp lại hơn hành vi
    cũ, kẻo nó lặng lẽ làm mất hàng đầu của bảng.
    """
    trang = Image.new("RGB", (2500, CAO_TRANG))
    vung = cat_vung(trang, BANG, confidence=0.9, tran_tren=BANG[1] - 2)
    assert vung.bbox[1] == BANG[1] - PADDING
