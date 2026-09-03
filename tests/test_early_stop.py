"""
Test điều kiện dừng sớm của nhánh VLM.

Dừng sớm là tối ưu chi phí cho đường phục vụ, nhưng nó cắt xén đầu vào của
phép đo theo một kiểu không nhìn thấy được từ bảng kết quả: một chỉ tiêu
bị bỏ qua vì đã dừng và một chỉ tiêu model đọc hỏng cho ra cùng một thứ —
ô null. Vì vậy hai thứ phải được chốt bằng test: số lời gọi VLM thật sự
giảm khi dừng sớm, và trạng thái dừng sớm luôn được ghi lại tường minh.

Chạy được không cần mạng và không cần model: call_vlm bị thay bằng hàm giả
đếm số lần được gọi.
"""

import json

from PIL import Image

import extract_vlm
from extract_vlm import extract_fields_from_regions
from fields_config import FIELD_MAP, Standard, fields_for
from layout_detection import TableRegion

# Ba chỉ tiêu này mang cờ required trong FIELD_RULES. Nhánh dừng vì
# "hết bảng để đọc" chỉ kích hoạt khi cả ba đã có giá trị.
FIELD_BAT_BUOC = ["tong_tai_san", "doanh_thu_thuan", "loi_nhuan_sau_thue"]


def _vung(bbox=(0, 0, 100, 100)) -> TableRegion:
    rong = max(1, bbox[2] - bbox[0])
    cao = max(1, bbox[3] - bbox[1])
    return TableRegion(image=Image.new("RGB", (rong, cao)), bbox=bbox, confidence=0.9)


def _lap_vlm_gia(monkeypatch, cac_phan_hoi: list) -> list:
    """
    Thay call_vlm bằng hàm giả, trả về danh sách ghi lại từng lời gọi.

    Danh sách đó là thứ chốt được "dừng sớm có thật sự tiết kiệm lời gọi
    API không" — nếu chỉ kiểm kết quả cuối thì một vòng lặp quét hết tài
    liệu rồi mới dừng trông y hệt một vòng lặp dừng đúng lúc.
    """
    con_lai = list(cac_phan_hoi)
    da_goi: list = []

    def goi_gia(base64_image, prompt, temperature=0.0):
        phan_hoi = con_lai.pop(0) if con_lai else {}
        da_goi.append(phan_hoi)
        return json.dumps(phan_hoi)

    monkeypatch.setattr(extract_vlm, "call_vlm", goi_gia)
    monkeypatch.setattr(extract_vlm, "encode_image_to_base64", lambda anh: "")
    return da_goi


# Các chỉ tiêu cộng lại thành Tài sản ngắn hạn. Viết ra ở đây thay vì tra
# ngược từ bộ đẳng thức: fixture cần một bộ số nhất quán, không cần một bản sao
# thứ hai của cấu hình ràng buộc.
_LA_TSNH = [
    "tien_va_tuong_duong_tien",
    "dau_tu_tc_ngan_han",
    "phai_thu_ngan_han",
    "hang_ton_kho",
    "tai_san_sinh_hoc_ngan_han",
    "tsnh_khac",
]


def _bo_so_nhat_quan(cac_field) -> dict:
    """
    Bộ giá trị lấp đầy mọi chỉ tiêu và KHÔNG tự mâu thuẫn.

    Fixture cũ dùng 100 cho mọi chỉ tiêu. Từ khi `src/chan_ung_vien.py` chặn
    ứng viên vi phạm cận suy từ dấu, bộ ấy bị pipeline từ chối — và từ chối
    ĐÚNG: tổng tài sản 100 không thể nhỏ hơn tài sản ngắn hạn 100 cộng tài sản
    dài hạn 100. Test ở file này đo ĐIỀU KIỆN DỪNG SỚM, nên giá trị chỉ là chất
    độn; nhưng chất độn tự mâu thuẫn thì nay chặn mất đúng thứ đang đo.
    """
    gia_tri = {khoa: 100 for khoa in cac_field}
    tsnh = sum(gia_tri[khoa] for khoa in _LA_TSNH if khoa in gia_tri)
    if "tai_san_ngan_han" in gia_tri:
        gia_tri["tai_san_ngan_han"] = tsnh
    if "tong_tai_san" in gia_tri:
        gia_tri["tong_tai_san"] = tsnh + gia_tri.get("tai_san_dai_han", 0)
    if "tong_nguon_von" in gia_tri:
        gia_tri["tong_nguon_von"] = gia_tri.get("tong_tai_san", 100)
    return gia_tri


def _du_het_field() -> dict:
    """Một phản hồi lấp đầy mọi chỉ tiêu trong FIELD_MAP cùng lúc."""
    return _bo_so_nhat_quan(FIELD_MAP)


# --- Nhánh 1: đủ hết field -------------------------------------------------


def test_du_het_field_thi_dung_ngay_giua_trang(monkeypatch):
    """
    Mục Phần F của BUILD-SPEC: trước đây điều kiện này chỉ được kiểm ở cuối
    mỗi TRANG, nên vùng đầu tiên lấp đủ field xong thì ba vùng còn lại của
    chính trang đó vẫn bị gọi VLM để mua về đúng thứ đã có.
    """
    trang = [{"page": 1, "regions": [_vung(), _vung(), _vung(), _vung()]}]
    da_goi = _lap_vlm_gia(monkeypatch, [_du_het_field()])

    extract_fields_from_regions(trang)

    assert len(da_goi) == 1


def test_du_het_field_thi_khong_doc_sang_trang_sau(monkeypatch):
    trang = [
        {"page": 1, "regions": [_vung()]},
        {"page": 2, "regions": [_vung()]},
        {"page": 3, "regions": [_vung()]},
    ]
    da_goi = _lap_vlm_gia(monkeypatch, [_du_het_field()])

    extract_fields_from_regions(trang)

    assert len(da_goi) == 1


def test_du_het_field_ghi_lai_ly_do_va_trang_dung(monkeypatch):
    """Trạng thái tường minh: đọc từ một khoá có sẵn, không suy ra."""
    trang = [{"page": 4, "regions": [_vung()]}, {"page": 5, "regions": [_vung()]}]
    _lap_vlm_gia(monkeypatch, [_du_het_field()])

    ket_qua = extract_fields_from_regions(trang)

    assert ket_qua.meta["early_stop"] == {
        "da_dung_som": True,
        "ly_do": "du_het_field",
        "trang_cuoi": 4,
        "field_con_thieu": [],
    }


# --- Nhánh 2: hết bảng để đọc ----------------------------------------------


def test_du_field_bat_buoc_va_het_kien_nhan_thi_dung(monkeypatch):
    """
    Nhánh nguy hiểm cho phép đo: nó dừng khi CHƯA đủ field, chỉ đủ field
    bắt buộc. Ba trang trống liên tiếp sau đó là đủ hết kiên nhẫn.
    """
    trang = [{"page": i, "regions": [_vung()]} for i in range(1, 9)]
    da_goi = _lap_vlm_gia(monkeypatch, [{khoa: 100 for khoa in FIELD_BAT_BUOC}])

    ket_qua = extract_fields_from_regions(trang)

    # Trang 1 có dữ liệu, trang 2/3/4 trống -> dừng ở trang 4.
    assert len(da_goi) == 4
    assert ket_qua.meta["early_stop"]["ly_do"] == "het_bang_de_doc"
    assert ket_qua.meta["early_stop"]["trang_cuoi"] == 4


def test_field_con_thieu_duoc_liet_ke_ra_khi_dung_giua_chung(monkeypatch):
    """
    Đây là lý do khoá này phải tồn tại. Những chỉ tiêu trong danh sách này
    có thể nằm ở phần đuôi CHƯA HỀ được quét, nên đếm chúng vào tỷ lệ
    "model không đọc được" là đổ lỗi cho model một việc nó chưa được làm.
    """
    trang = [{"page": i, "regions": [_vung()]} for i in range(1, 9)]
    _lap_vlm_gia(monkeypatch, [{khoa: 100 for khoa in FIELD_BAT_BUOC}])

    ket_qua = extract_fields_from_regions(trang)
    con_thieu = ket_qua.meta["early_stop"]["field_con_thieu"]

    assert "hang_ton_kho" in con_thieu
    assert "tong_tai_san" not in con_thieu


def test_thieu_field_bat_buoc_thi_khong_dung_du_bao_nhieu_trang_trong(monkeypatch):
    """
    Bộ đếm kiên nhẫn không được tự dừng khi field bắt buộc còn thiếu —
    nếu không thì một báo cáo có bảng cân đối nằm sâu sẽ không bao giờ
    được đọc tới.
    """
    trang = [{"page": i, "regions": [_vung()]} for i in range(1, 7)]
    da_goi = _lap_vlm_gia(monkeypatch, [{"hang_ton_kho": 100}])

    ket_qua = extract_fields_from_regions(trang)

    assert len(da_goi) == 6
    assert ket_qua.meta["early_stop"]["da_dung_som"] is False


# --- Cờ tắt dừng sớm khi ĐO ------------------------------------------------


def test_tat_dung_som_thi_quet_het_tai_lieu(monkeypatch):
    """
    DISABLE_EARLY_STOP là nhánh đối chứng cho phép đo, cùng vai với
    DISABLE_CONSTRAINT_GATE ở router.py: đo một hệ trên đầu ra mà chính hệ
    đó đã cắt xén thì con số thu được không nói lên điều gì.
    """
    monkeypatch.setattr(extract_vlm, "DISABLE_EARLY_STOP", True)

    trang = [{"page": i, "regions": [_vung()]} for i in range(1, 6)]
    da_goi = _lap_vlm_gia(monkeypatch, [_du_het_field()])

    ket_qua = extract_fields_from_regions(trang)

    assert len(da_goi) == 5
    assert ket_qua.meta["early_stop"]["da_dung_som"] is False


def test_khong_dung_som_van_ghi_khoa_trang_thai(monkeypatch):
    """
    Khoá phải luôn có mặt, kể cả khi không dừng sớm. Để nó vắng mặt khi
    "không có gì xảy ra" là bắt người đọc suy trạng thái từ sự thiếu vắng
    của một khoá — đúng thứ quy ước trạng thái tường minh cấm.
    """
    trang = [{"page": 1, "regions": [_vung()]}]
    _lap_vlm_gia(monkeypatch, [{"hang_ton_kho": 100}])

    ket_qua = extract_fields_from_regions(trang)

    assert ket_qua.meta["early_stop"]["da_dung_som"] is False
    assert ket_qua.meta["early_stop"]["ly_do"] == ""
    assert ket_qua.meta["early_stop"]["trang_cuoi"] is None


def test_bao_cao_TT200_van_dung_som_duoc_o_nhanh_du_het_field(monkeypatch):
    """
    Hồi quy: nhánh dừng sớm rẻ nhất phải KHẢ THI với báo cáo TT200.

    Điều kiện nhánh 1 từng là `all(... for khoa in FIELD_MAP)`, tức đòi cả
    21 chỉ tiêu. Nhưng FIELD_MAP là HỢP của hai chuẩn: Tài sản sinh học
    ngắn hạn chỉ có ở TT99. Với báo cáo TT200 thì chỉ tiêu đó không tồn tại
    trên giấy nên không bao giờ điền được, và nhánh 1 thành bất khả thi —
    mọi lượt chạy phải rơi xuống nhánh 2.

    Nhánh 2 chính là nhánh mà code tự dán nhãn "nguy hiểm cho phép đo": nó
    dừng khi CHƯA đủ field, nên field còn thiếu có thể chưa từng được nhìn
    tới. Nên lỗi này vừa tốn tiền API vừa làm mọi con số "model đọc không
    được" của H1 thành nhập nhằng.

    Phản hồi giả dưới đây mô phỏng đúng một báo cáo TT200 thật: đủ cả 20
    chỉ tiêu của TT200, và KHÔNG có Tài sản sinh học ngắn hạn.
    """
    du_het_TT200 = _bo_so_nhat_quan(fields_for(Standard.TT200))
    assert "tai_san_sinh_hoc_ngan_han" not in du_het_TT200

    trang = [{"page": 1, "regions": [_vung()]}, {"page": 2, "regions": [_vung()]}]
    da_goi = _lap_vlm_gia(monkeypatch, [du_het_TT200])

    ket_qua = extract_fields_from_regions(trang, standard=Standard.TT200)

    assert ket_qua.meta["early_stop"]["ly_do"] == "du_het_field", (
        "Đọc đủ mọi chỉ tiêu của TT200 mà vẫn không dừng — gần như chắc chắn "
        "điều kiện đang đếm trên FIELD_MAP thay vì fields_for(standard)"
    )
    assert len(da_goi) == 1, "Đã đủ field mà vẫn đọc sang trang sau"
