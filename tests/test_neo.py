"""
Neo toạ độ chỉ tiêu — tâm của hình chữ thập.

Xếp hạng ô lân cận chỉ có nghĩa khi có tâm để đo. Bản trước lấy tâm từ
`Provenance.bbox`, vốn là bbox của cả VÙNG BẢNG, nên mọi ô trong vùng đều
chồng lên nó theo cả hai trục: tất cả rơi vào hạng 0, cost bằng nhau tuyệt
đối, và phép cắt theo trần thành bốc thăm. File này khoá lại cái tâm ấy.
"""

from fields_config import Standard
from repair.candidates import tu_o_lan_can
from repair.neo import neo_bbox

# Một vùng bảng thu nhỏ nhưng giữ đúng hình học của báo cáo Việt Nam:
# cột tên chỉ tiêu, cột mã số, rồi hai cột giá trị (quý này / luỹ kế).
VUNG_BBOX = (100, 200, 2000, 1800)

O_MA_100 = ("100", (600, 900, 680, 940))
O_GT_QUY = ("71.249.595.744", (1200, 900, 1600, 940))
O_GT_LUY = ("95.000.000.000", (1700, 900, 2000, 940))
O_DONG_TREN = ("12.105.315.641", (1200, 700, 1600, 740))
O_DONG_DUOI = ("13.217.639.635", (1200, 1100, 1600, 1140))

VUNG = {
    "region_index": 0,
    "text": "…",
    "o": [
        ("Tài sản ngắn hạn", (200, 900, 550, 940)),
        O_MA_100,
        O_GT_QUY,
        O_GT_LUY,
        O_DONG_TREN,
        O_DONG_DUOI,
    ],
    "o_so": [
        (71_249_595_744, O_GT_QUY[1]),
        (95_000_000_000, O_GT_LUY[1]),
        (12_105_315_641, O_DONG_TREN[1]),
        (13_217_639_635, O_DONG_DUOI[1]),
    ],
}


def test_khop_gia_tri_neo_dung_o_do():
    """Neo chắc chắn nhất: ô mà EasyOCR đọc ra đúng con số VLM đã trả."""
    bbox, cach = neo_bbox("tai_san_ngan_han", 71_249_595_744, VUNG, Standard.TT200)

    assert cach == "khop_gia_tri"
    assert bbox == O_GT_QUY[1]


def test_VLM_DOC_SAI_thi_lui_ve_neo_theo_dong_ma_so():
    """
    Ca đáng quan tâm nhất, không phải ca hiếm. VLM đọc sai thì không ô nào mang
    con số sai ấy, nên tầng khớp giá trị trượt đúng vào những lượt cần sửa. Neo
    dự phòng dò ô MÃ SỐ để biết DÒNG — mã số là chữ số, chỗ EasyOCR đạt 0,999.
    """
    bbox, cach = neo_bbox("tai_san_ngan_han", 999_999, VUNG, Standard.TT200)

    assert cach == "dong_ma_so"
    # Dải phủ hai ô giá trị của đúng dòng đó, không phải bbox ô mã số.
    assert bbox == (1200, 900, 2000, 940)


def test_neo_dong_ma_so_van_giu_duoc_ung_vien_LECH_DONG():
    """
    Vì sao neo theo DẢI GIÁ TRỊ của dòng chứ không theo chính ô mã số: ô mã số
    nằm ở cột trái, nên các ô giá trị cùng dòng sẽ thành hạng 2 còn các ô cùng
    cột giá trị ở dòng khác thành CHÉO và bị loại — tức mất sạch ứng viên lệch
    dòng, đúng một trong hai chế độ lỗi nguồn này sinh ra để cứu.
    """
    bbox, _ = neo_bbox("tai_san_ngan_han", 999_999, VUNG, Standard.TT200)
    gia_tri = {uv.value for uv in tu_o_lan_can(VUNG["o_so"], bbox)}

    assert 95_000_000_000 in gia_tri, "mất ứng viên lệch cột"
    assert 12_105_315_641 in gia_tri, "mất ứng viên lệch dòng"
    assert 13_217_639_635 in gia_tri, "mất ứng viên lệch dòng"


def test_ma_so_phai_khop_TRON_O_khong_khop_khuc_con():
    """
    "100" là khúc con của "1.100.000". Nhận nhầm một ô giá trị làm ô mã số sẽ
    neo chỉ tiêu vào sai dòng, và sai lặng lẽ vì mọi thứ sau đó vẫn chạy.
    """
    vung = {
        "o": [("1.100.000", (1200, 300, 1600, 340))],
        "o_so": [(1_100_000, (1200, 300, 1600, 340))],
    }

    assert neo_bbox("tai_san_ngan_han", 999_999, vung, Standard.TT200) == (None, "khong_neo")


def test_truot_ca_hai_tang_thi_KHONG_neo_bua():
    """
    Trả None để `tu_o_lan_can()` biết mà tự khai là không xếp hạng được. Bản
    trước lặng lẽ dùng bbox vùng, và cái lặng lẽ đó là toàn bộ vấn đề.
    """
    vung = {"o": [("Tổng cộng tài sản", (200, 900, 550, 940))], "o_so": []}

    assert neo_bbox("tai_san_ngan_han", 999_999, vung, Standard.TT200) == (None, "khong_neo")


def test_chi_tieu_khong_co_ma_so_khai_bao_thi_khong_no():
    vung = {"o": [O_MA_100], "o_so": []}

    assert neo_bbox("khong_ton_tai", 1, vung, Standard.TT200) == (None, "khong_neo")


# ---------------------------------------------------------------------------
# Hồi quy: đúng cái lỗi đã làm xếp hạng nằm im
# ---------------------------------------------------------------------------


def test_bbox_ca_VUNG_lam_moi_cost_bang_nhau():
    """
    Khoá lại chế độ hỏng, để không ai vô tình quay về nó. Lấy bbox vùng làm tâm
    thì mọi ô đều hạng 0 và cost bằng nhau, nên trần `MAX_MOI_NGUON` cắt tuỳ
    tiện — đúng thứ đã kéo độ phủ 0,831 xuống 0,369 ở lần chạy trần 12.
    """
    cost = {uv.cost for uv in tu_o_lan_can(VUNG["o_so"], VUNG_BBOX)}

    assert len(cost) == 1


def test_neo_that_thi_cost_PHAN_BIET_DUOC():
    """Cùng dữ liệu ấy, neo bằng ô thật thì thứ tự trở lại có nghĩa."""
    bbox, _ = neo_bbox("tai_san_ngan_han", 71_249_595_744, VUNG, Standard.TT200)
    cost = {uv.cost for uv in tu_o_lan_can(VUNG["o_so"], bbox)}

    assert len(cost) > 1
