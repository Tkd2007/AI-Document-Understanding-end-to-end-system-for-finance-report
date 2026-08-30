"""
Nguồn ứng viên "đọc lại tờ giấy" — các ô số trong cùng vùng bảng.

Đây là nguồn phân biệt nghiên cứu này với mọi paradigm sửa lỗi trước đó, nên
thứ phải khoá không phải là "hàm chạy được" mà là **thứ tự**: trần chỉ giữ 10
ứng viên mỗi nguồn, và nếu mọi ô cùng cost thì phép cắt thành bốc thăm. Dự án
đã trả giá đúng chỗ này một lần — độ phủ rơi 0,831 → 0,369, đúng tỷ lệ của
phép chọn ngẫu nhiên.

Vùng lân cận có hình CHỮ THẬP: cùng cột (lệch dòng) hoặc cùng dòng (lệch cột).
Ô nằm chéo không ứng với chế độ lỗi nào nên bị loại hẳn.
"""

from repair.candidates import (
    MAX_MOI_NGUON,
    generate,
    hang_lan_can,
    tu_o_lan_can,
)

# Ô đang xét: một ô số ở cột thứ hai, dòng giữa bảng.
DANG_XET = (1200, 900, 1600, 950)


# ---------------------------------------------------------------------------
# Xếp hạng
# ---------------------------------------------------------------------------


def test_hang_0_la_chinh_o_do_doc_lai():
    """
    Ô chồng lên bbox của chỉ tiêu đang xét — cùng ô, đọc bằng engine khác.

    Đây là ứng viên giá trị nhất: VLM đọc ảnh bảng theo kiểu hiểu ngữ cảnh,
    EasyOCR đọc từng ô theo nhận dạng ký tự và đo được 0,999 trên ô số. Ca BMP
    (máy đọc ...595..., giấy ghi ...959... — ĐẢO CHỖ hai chữ số) chỉ cứu được
    bằng hạng này, vì nguồn nhầm chữ số chỉ biết đổi MỘT chữ số.
    """
    assert hang_lan_can((1205, 905, 1595, 945), DANG_XET) == (0, 0.0)


def test_hang_1_la_cung_cot_lech_dong():
    hang, khoang_cach = hang_lan_can((1200, 1100, 1600, 1150), DANG_XET)

    assert hang == 1
    assert khoang_cach == 200.0


def test_hang_2_la_cung_dong_lech_cot():
    hang, khoang_cach = hang_lan_can((1800, 900, 2200, 950), DANG_XET)

    assert hang == 2
    assert khoang_cach == 600.0


def test_o_nam_CHEO_bi_loai_han():
    """
    Vừa lệch dòng vừa lệch cột thì không ứng với chế độ lỗi nào cả. Nhận nó vào
    chỉ làm tập ứng viên phình ra bằng những con số tình cờ ở gần — mà tập ứng
    viên phình ra đúng là thứ làm tăng xác suất một con số ngẫu nhiên tình cờ
    làm bảng cân.
    """
    assert hang_lan_can((1800, 1100, 2200, 1150), DANG_XET) is None


# ---------------------------------------------------------------------------
# Cost phải xếp được thứ tự, nếu không trần cắt tuỳ tiện
# ---------------------------------------------------------------------------


def test_cost_tang_dan_theo_hang():
    o = [
        (111, (1800, 900, 2200, 950)),    # hạng 2
        (222, (1200, 1100, 1600, 1150)),  # hạng 1
        (333, (1205, 905, 1595, 945)),    # hạng 0
    ]
    theo_gia_tri = {uv.value: uv.cost for uv in tu_o_lan_can(o, DANG_XET)}

    assert theo_gia_tri[333] < theo_gia_tri[222] < theo_gia_tri[111]


def test_cung_hang_thi_gan_hon_re_hon():
    o = [
        (111, (1200, 1400, 1600, 1450)),  # hạng 1, xa
        (222, (1200, 1000, 1600, 1050)),  # hạng 1, gần
    ]
    theo_gia_tri = {uv.value: uv.cost for uv in tu_o_lan_can(o, DANG_XET)}

    assert theo_gia_tri[222] < theo_gia_tri[111]


def test_khoang_cach_KHONG_lan_at_hang():
    """
    Khoảng cách chỉ phân xử TRONG một hạng. Một ô hạng 1 rất xa vẫn phải rẻ hơn
    một ô hạng 2 rất gần — nếu không thì thứ tự hạng mất nghĩa và ta quay lại
    đúng bài toán "xếp theo khoảng cách hình tròn" mà hình chữ thập sinh ra để
    thay thế.
    """
    o = [
        (111, (1200, 100_000, 1600, 100_050)),  # hạng 1, cực xa
        (222, (1650, 900, 1700, 950)),          # hạng 2, sát ngay bên
    ]
    theo_gia_tri = {uv.value: uv.cost for uv in tu_o_lan_can(o, DANG_XET)}

    assert theo_gia_tri[111] < theo_gia_tri[222]


def test_tran_giu_lai_o_GAN_NHAT_chu_khong_cat_tuy_tien():
    """
    Ràng buộc quan trọng nhất của cả module. Đổ vào nhiều ô hơn trần, ô sống
    sót phải là những ô đáng tin nhất chứ không phải mấy ô đầu danh sách.
    """
    xa = [(1000 + i, (1200, 2000 + i * 100, 1600, 2050 + i * 100)) for i in range(30)]
    gan = [(999, (1205, 905, 1595, 945))]   # hạng 0

    kq = generate("tong_tai_san", 5_000, o_lan_can=xa + gan, bbox_dang_xet=DANG_XET)
    tu_lan_can = [uv for uv in kq if uv.source == "neighbor_cell"]

    assert len(tu_lan_can) <= MAX_MOI_NGUON
    assert 999 in [uv.value for uv in tu_lan_can], "ô đáng tin nhất bị cắt mất"


def test_khong_co_bbox_thi_van_chay_nhung_khong_xep_hang_duoc():
    """
    Các baseline đối chứng chạy trên giá trị trần, không có Provenance. Chúng
    vẫn phải gọi được hàm này — chỉ là lúc ấy trần cắt tuỳ tiện, và đó là lý do
    đường chạy thật LUÔN phải truyền bbox.
    """
    o = [(111, (1800, 1100, 2200, 1150))]   # ô chéo, có bbox thì đã bị loại

    assert len(tu_o_lan_can(o, None)) == 1


# ---------------------------------------------------------------------------
# Nối vào generate()
# ---------------------------------------------------------------------------


def test_gia_tri_dung_bang_gia_tri_hien_tai_thi_khong_thanh_ung_vien():
    """Sửa ra đúng con số đang có thì không phải một phép sửa."""
    o = [(5_000, (1205, 905, 1595, 945))]

    kq = generate("tong_tai_san", 5_000, o_lan_can=o, bbox_dang_xet=DANG_XET)

    assert 5_000 not in [uv.value for uv in kq]


def test_nguon_moi_KHONG_lam_bien_mat_cac_nguon_khac():
    """
    Trần tổng là 20 và nguồn mới ăn tối đa 10, nên bốn nguồn cũ vẫn phải còn
    chỗ. Nếu ứng viên lân cận chiếm sạch thì các chế độ lỗi khác mất khả năng
    sửa — đúng thứ MAX_MOI_NGUON sinh ra để chặn.
    """
    xa = [(1000 + i, (1200, 2000 + i * 100, 1600, 2050 + i * 100)) for i in range(30)]

    kq = generate("tong_tai_san", 71_249_595_744, o_lan_can=xa, bbox_dang_xet=DANG_XET)
    nguon = {uv.source for uv in kq}

    assert "neighbor_cell" in nguon
    assert nguon - {"neighbor_cell"}, "nguồn lân cận chiếm sạch chỗ"


# ---------------------------------------------------------------------------
# Đường dẫn dữ liệu: từ OCR -> toạ độ TRANG -> đúng chỉ tiêu
# ---------------------------------------------------------------------------


def test_o_so_doi_toa_do_ve_he_cua_TRANG():
    """
    bbox của ô là toạ độ trong ảnh VÙNG ĐÃ CẮT, còn Provenance nói bằng toạ độ
    TRANG. Trộn hai hệ là loại lỗi không làm gì nổ — nó chỉ khiến bước đọc lại
    nhìn sang một ô khác rồi trả về một con số hoàn toàn hợp lệ của ô đó.
    """
    from PIL import Image

    from layout_detection import TableRegion
    from ocr_baseline import o_so_trong_vung

    vung = TableRegion(image=Image.new("RGB", (10, 10)), bbox=(500, 300, 900, 700), confidence=0.9)
    chi_tiet = [("1.234.567", (10, 20, 60, 40))]

    assert o_so_trong_vung(vung, chi_tiet) == [(1234567, (510, 320, 560, 340))]


def test_o_chu_bi_bo_qua_khong_lam_no():
    from PIL import Image

    from layout_detection import TableRegion
    from ocr_baseline import o_so_trong_vung

    vung = TableRegion(image=Image.new("RGB", (10, 10)), bbox=(0, 0, 100, 100), confidence=0.9)
    chi_tiet = [("TỔNG CỘNG TÀI SẢN", (0, 0, 50, 10)), ("(1.234)", (0, 20, 50, 30))]

    assert o_so_trong_vung(vung, chi_tiet) == [(-1234, (0, 20, 50, 30))]


def test_chi_lay_o_cung_VUNG_BANG_voi_chi_tieu():
    """
    Lấy ô của bảng khác là mở đường cho đúng kiểu lỗi SBT: một con số hợp lệ
    của bảng khác vẫn là một con số hợp lệ, và không đẳng thức nào bắt được.
    Lọc theo TRANG là chưa đủ — một trang có thể mang nhiều bảng.
    """
    import router
    from extraction_types import FieldResult, Provenance

    kq = FieldResult(
        value=5_000,
        confidence=1.0,
        provenance=Provenance(page=4, region_index=0, bbox=DANG_XET),
    )
    theo_khoa = {
        (4, 0): {"o_so": [(111, (0, 0, 1, 1))]},
        (4, 1): {"o_so": [(222, (0, 0, 1, 1))]},   # bảng khác, CÙNG trang
        (8, 0): {"o_so": [(333, (0, 0, 1, 1))]},
    }

    assert router._vung_cua(kq, theo_khoa)["o_so"] == [(111, (0, 0, 1, 1))]


def test_khong_biet_vung_thi_KHONG_doan():
    """Thà không có ứng viên còn hơn có ứng viên lấy từ nhầm bảng."""
    import router
    from extraction_types import FieldResult

    khong_provenance = FieldResult(value=5_000, confidence=1.0)
    theo_khoa = {(4, 0): {"o_so": [(111, (0, 0, 1, 1))]}}

    assert router._vung_cua(khong_provenance, theo_khoa) is None
    assert router._vung_cua(None, theo_khoa) is None


def test_loc_bo_ma_so_va_thuyet_minh():
    """
    Cột Mã số và cột Thuyết minh là hai thứ chính prompt của VLM đang phải dặn
    tránh. Đưa chúng vào tập ứng viên thì chúng chiếm chỗ của ô thật trong trần,
    và mỗi con số thừa lại thêm một cơ hội để tổ hợp nào đó TÌNH CỜ làm bảng cân.
    """
    from PIL import Image

    from layout_detection import TableRegion
    from ocr_baseline import o_so_trong_vung

    vung = TableRegion(image=Image.new("RGB", (10, 10)), bbox=(0, 0, 100, 100), confidence=0.9)
    chi_tiet = [
        ("01", (0, 0, 20, 10)),          # mã số
        ("26.1", (30, 0, 60, 10)),       # thuyết minh
        ("V.5", (30, 20, 60, 30)),       # thuyết minh kiểu La Mã
        ("2025", (30, 40, 60, 50)),      # năm ở tiêu đề cột
        ("6.733.581.463.563", (70, 0, 200, 10)),   # giá trị thật
    ]

    assert o_so_trong_vung(vung, chi_tiet) == [
        (6733581463563, (70, 0, 200, 10))
    ]
