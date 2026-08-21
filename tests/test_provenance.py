"""
Test provenance: mỗi giá trị phải lần được về đúng vùng ảnh đã sinh ra nó.

Đây là module nhìn ít quan trọng nhất mà thật ra quan trọng nhất. Không có
provenance thì không cắt lại được đúng vùng để ĐỌC LẠI, và không đọc lại
được thì cả nghiên cứu mất đóng góp cốt lõi — mọi paradigm sửa lỗi trước
đây đều thao tác trên một vector số cố định chính vì nguồn của chúng
(phiếu khảo sát, cảm biến) không hỏi lại được. Ở đây ảnh gốc vẫn còn.

Chạy được mà không cần YOLO hay mạng: filter_overlapping và cat_vung là
hình học thuần, còn phần tích hợp dùng VLM giả.
"""

import json

from PIL import Image

import extract_vlm
from extract_vlm import extract_fields_from_regions
from layout_detection import (
    IOU_THRESHOLD,
    PADDING,
    TableRegion,
    _iou,
    ca_trang,
    cat_vung,
    filter_overlapping,
)


def _vung(bbox, confidence=0.9) -> TableRegion:
    rong = max(1, bbox[2] - bbox[0])
    cao = max(1, bbox[3] - bbox[1])
    return TableRegion(image=Image.new("RGB", (rong, cao)), bbox=bbox, confidence=confidence)


# --- Hình học --------------------------------------------------------------


def test_iou_tren_vi_du_tinh_tay():
    """
    Hai hình 10x10 lệch nhau 5 theo trục x: giao 5x10 = 50, hợp
    100 + 100 - 50 = 150, nên IoU = 1/3. Kiểm được bằng mắt.
    """
    assert _iou((0, 0, 10, 10), (5, 0, 15, 10)) == 50 / 150


def test_iou_bang_0_khi_khong_giao_nhau():
    assert _iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0


def test_iou_bang_1_khi_trung_khit():
    assert _iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0


def test_hai_box_chong_lan_nang_thi_chi_giu_mot():
    """
    Ca có thật đã quan sát được ở trang 31 và 35 của báo cáo VNM: YOLO trả
    hai box cho cùng một bảng.
    """
    giu = filter_overlapping([_vung((0, 0, 100, 100)), _vung((0, 0, 100, 95))])

    assert len(giu) == 1


def test_hai_box_chong_lan_it_thi_giu_ca_hai():
    """
    Trang có hai bảng nằm gần nhau là chuyện bình thường. Gộp chúng lại là
    mất dữ liệu, nên ngưỡng phải đủ cao để không nhầm.
    """
    giu = filter_overlapping([_vung((0, 0, 100, 100)), _vung((82, 0, 182, 100))])

    assert len(giu) == 2


def test_chong_lan_thi_giu_box_co_confidence_cao_hon():
    yeu = _vung((0, 0, 100, 100), confidence=0.3)
    manh = _vung((0, 0, 100, 96), confidence=0.9)

    giu = filter_overlapping([yeu, manh])

    assert giu == [manh]


def test_ket_qua_van_theo_thu_tu_tren_xuong_duoi():
    """
    Hàm gọi vẫn mong đợi thứ tự này: các chỉ tiêu trên một trang đọc theo
    thứ tự bảng, và bước gộp lấy giá trị non-null ĐẦU TIÊN.
    """
    duoi = _vung((0, 500, 100, 600))
    tren = _vung((0, 10, 100, 110))

    giu = filter_overlapping([duoi, tren])

    assert [v.bbox[1] for v in giu] == [10, 500]


def test_nguong_iou_de_o_muc_quy_uoc():
    """Chốt lại hằng số, để ai đổi nó phải đọc lý do trong docstring."""
    assert IOU_THRESHOLD == 0.5


# --- Toạ độ phải khớp với vùng đã cắt --------------------------------------


def test_cat_lai_theo_bbox_ra_dung_anh_da_cat():
    """
    TEST CHỐNG LỖI LỆCH HỆ TOẠ ĐỘ — loại lỗi làm bước đọc lại nhìn nhầm
    sang một ô khác rồi trả về một con số hoàn toàn hợp lệ, không báo gì.

    bbox phải là bbox ĐÃ CỘNG PADDING và đã clamp, tức đúng vùng đã cắt,
    chứ không phải bbox thô của YOLO.
    """
    trang = Image.effect_noise((300, 400), 50).convert("RGB")

    vung = cat_vung(trang, (50, 60, 200, 250), confidence=0.8)

    cat_lai = trang.crop(vung.bbox)
    assert cat_lai.size == vung.image.size
    assert cat_lai.tobytes() == vung.image.tobytes()


def test_bbox_da_cong_padding():
    trang = Image.new("RGB", (300, 400))

    vung = cat_vung(trang, (50, 60, 200, 250), confidence=0.8)

    assert vung.bbox == (50 - PADDING, 60 - PADDING, 200 + PADDING, 250 + PADDING)


def test_bbox_bi_clamp_ve_trong_khung_anh():
    """Box sát mép thì padding không được đẩy toạ độ ra ngoài ảnh."""
    trang = Image.new("RGB", (100, 100))

    vung = cat_vung(trang, (0, 0, 100, 100), confidence=0.8)

    assert vung.bbox == (0, 0, 100, 100)


def test_ca_trang_van_mang_bbox_day_du():
    """
    Khi YOLO không tìm thấy bảng nào, pipeline fail open dùng cả trang.
    Bước đọc lại vẫn cần bbox trong ca đó, và bbox của cả trang là một câu
    trả lời đúng chứ không phải thiếu dữ liệu.
    """
    vung = ca_trang(Image.new("RGB", (250, 350)))

    assert vung.bbox == (0, 0, 250, 350)
    assert vung.confidence == 0.0


# --- Provenance đi tới tận kết quả -----------------------------------------


def _lap_vlm_gia(monkeypatch, cac_phan_hoi: list):
    con_lai = list(cac_phan_hoi)

    def goi_gia(base64_image, prompt, temperature=0.0):
        return json.dumps(con_lai.pop(0)) if con_lai else None

    monkeypatch.setattr(extract_vlm, "call_vlm", goi_gia)
    monkeypatch.setattr(extract_vlm, "encode_image_to_base64", lambda anh: "")


def test_gia_tri_lan_duoc_ve_dung_trang_da_sinh_ra_no(monkeypatch):
    """
    Các chỉ tiêu nằm rải ở nhiều trang: nhóm bảng cân đối ở một trang,
    nhóm kết quả kinh doanh ở trang khác. Nếu provenance không đi theo qua
    bước gộp thì mọi giá trị đều trỏ về trang cuối cùng đã đọc.
    """
    trang = [
        {"page": 5, "regions": [_vung((0, 0, 100, 100))]},
        {"page": 6, "regions": [_vung((0, 0, 100, 100))]},
        {"page": 7, "regions": [_vung((10, 20, 110, 220))]},
    ]
    _lap_vlm_gia(monkeypatch, [{}, {}, {"tong_tai_san": 100}])

    ket_qua = extract_fields_from_regions(trang)
    nguon = ket_qua.data["tong_tai_san"].provenance

    assert nguon is not None
    assert nguon.page == 7
    assert nguon.bbox == (10, 20, 110, 220)


def test_chi_so_vung_duoc_ghi_lai_khi_trang_co_nhieu_bang(monkeypatch):
    """
    Một trang có hai bảng thì chỉ số vùng là thứ duy nhất phân biệt được
    chúng — bbox thì có, nhưng đọc lại cần biết cắt vùng THỨ MẤY để lấy
    lại đúng ảnh đã lưu.
    """
    trang = [{"page": 3, "regions": [_vung((0, 0, 50, 50)), _vung((0, 200, 50, 250))]}]
    _lap_vlm_gia(monkeypatch, [{}, {"tong_tai_san": 100}])

    ket_qua = extract_fields_from_regions(trang)

    assert ket_qua.data["tong_tai_san"].provenance.region_index == 1


def test_khong_bat_luu_crop_thi_khong_ghi_file(monkeypatch):
    """
    Mặc định không lưu crop: bbox đủ để cắt lại từ PDF gốc, chỉ tốn công
    convert lại trang. Lưu mọi crop của mọi lượt chạy sẽ phình đĩa rất
    nhanh với báo cáo 55 trang.
    """
    _lap_vlm_gia(monkeypatch, [{"tong_tai_san": 100}])

    ket_qua = extract_fields_from_regions(_mot_trang_don())

    assert ket_qua.data["tong_tai_san"].provenance.crop_path is None


def test_bat_luu_crop_thi_ghi_ra_file_tra_cuu_duoc(monkeypatch, tmp_path):
    """
    Tên file mang (trang, chỉ số vùng) chứ không mang số ngẫu nhiên: crop
    tồn tại để tra cứu lại bằng tay khi đi dò một kết quả đáng ngờ, mà tên
    ngẫu nhiên thì không tra được.
    """
    _lap_vlm_gia(monkeypatch, [{"tong_tai_san": 100}])

    ket_qua = extract_fields_from_regions(_mot_trang_don(), crop_dir=tmp_path)
    duong_dan = ket_qua.data["tong_tai_san"].provenance.crop_path

    assert duong_dan is not None
    assert "p001_r0" in duong_dan
    assert (tmp_path / "p001_r0.png").exists()


def _mot_trang_don():
    return [{"page": 1, "regions": [_vung((0, 0, 100, 100))]}]
