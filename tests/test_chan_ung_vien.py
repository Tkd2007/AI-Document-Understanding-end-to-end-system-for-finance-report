"""
Chặn ứng viên trước khi nhận — hai phép chặn của `src/chan_ung_vien.py`.

CA THẬT LÀM CHUẨN CHO CẢ FILE, `GVR_2026Q2_TT99` trong lượt chấm 03/09/2026.
Bảng cân đối nằm ở trang 6–8 nhưng dòng tổng cộng không đọc được, nên vòng lặp
VLM cày tiếp 65 trang thuyết minh rồi ở trang 78 nhận `tong_tai_san` =
406.588.902.083 trong khi giá trị thật là 90.263.949.529.178 — sai 222 lần, và
kéo theo ba lỗi câm nữa ở cùng biểu mẫu. Số trong file này lấy nguyên từ tài
liệu đó chứ không bịa, để test hỏng khi cơ chế thôi bắt được ca đã thật sự xảy
ra.

ĐIỀU QUAN TRỌNG NHẤT PHẢI CHỐT LẠI KHÔNG PHẢI "CHẶN ĐƯỢC", MÀ LÀ "KHÔNG CHẶN
QUÁ TAY". Một phép chặn quá tay làm mất chỉ tiêu đọc đúng, và mất chỉ tiêu là
mất thật — nên quá nửa số test dưới đây là test khẳng định ứng viên hợp lệ vẫn
đi qua.
"""

import json

from PIL import Image

import extract_vlm
from chan_ung_vien import da_di_qua_bieu_mau, vi_pham_dang_thuc
from fields_config import QuyUocDau, Standard
from layout_detection import TableRegion

# Số thật của GVR_2026Q2_TT99.
GVR_TSNH = 37_897_604_212_888
GVR_TONG_TAI_SAN_THAT = 90_263_949_529_178
GVR_TONG_TAI_SAN_BIA = 406_588_902_083


def _khong_xac_dinh(khoa, gia_tri, da_biet):
    """Gọi phép kiểm số học ở quy ước dấu mà lúc trích xuất thật sự có."""
    return vi_pham_dang_thuc(
        khoa, gia_tri, da_biet, Standard.TT99, QuyUocDau.KHONG_XAC_DINH
    )


# --- Phép chặn theo số học ------------------------------------------------


def test_bac_ung_vien_nho_hon_so_hang_da_biet():
    """
    Ca GVR nguyên bản: tổng tài sản nhỏ hơn tài sản ngắn hạn đã biết.

    Cận này chắc chắn vì tài sản dài hạn bị cấm âm, nên nó không phải một
    phỏng đoán thống kê mà là một bất khả.
    """
    ly_do = _khong_xac_dinh(
        "tong_tai_san", GVR_TONG_TAI_SAN_BIA, {"tai_san_ngan_han": GVR_TSNH}
    )
    assert ly_do is not None
    assert "không âm" in ly_do


def test_nhan_ung_vien_dung_cua_chinh_ca_do():
    """Giá trị THẬT của GVR phải đi qua — nếu không, cơ chế vô dụng."""
    assert (
        _khong_xac_dinh(
            "tong_tai_san", GVR_TONG_TAI_SAN_THAT, {"tai_san_ngan_han": GVR_TSNH}
        )
        is None
    )


def test_khong_bac_khi_chua_biet_so_hang_nao():
    """Không có gì để so thì không được từ chối — im lặng, không đoán."""
    assert _khong_xac_dinh("tong_tai_san", GVR_TONG_TAI_SAN_BIA, {}) is None


def test_khong_suy_can_khi_so_hang_duoc_phep_am():
    """
    `tong_nguon_von = no_phai_tra + von_chu_so_huu` KHÔNG cho cận.

    `von_chu_so_huu` được phép âm (doanh nghiệp lỗ luỹ kế vượt vốn góp), nên
    tổng nguồn vốn hoàn toàn có thể nhỏ hơn nợ phải trả. Suy cận ở đây là bịa
    ra một vi phạm, đúng loại dương tính giả mà `FieldRelation` đã cảnh báo.
    """
    assert _khong_xac_dinh("tong_nguon_von", 1_000, {"no_phai_tra": 999_999}) is None


def test_khong_bac_khi_dang_thuc_lech_ma_da_biet_du():
    """
    Đẳng thức lệch mà biết đủ mọi thành viên thì KHÔNG được bác ứng viên.

    Đây là quyết định thiết kế, không phải thiếu sót — xem docstring của
    `vi_pham_dang_thuc`. Lệch chỉ nói "có gì đó sai trong nhóm này", không nói
    thành viên nào sai, mà thủ phạm có thể là giá trị đã nhận từ trước. Quyết
    định thành viên nào sai CHÍNH LÀ bài toán định vị của H2, và làm nó tham
    lam ngay trong lúc trích xuất là giẫm lên thứ đang được đem đi đo.
    """
    da_biet = {"tai_san_ngan_han": 100, "tai_san_dai_han": 100}
    assert _khong_xac_dinh("tong_tai_san", 500, da_biet) is None


def test_gia_tri_khong_phai_so_thi_bo_qua():
    assert _khong_xac_dinh("tong_tai_san", None, {"tai_san_ngan_han": GVR_TSNH}) is None
    assert (
        _khong_xac_dinh("tong_tai_san", "không đọc được", {"tai_san_ngan_han": GVR_TSNH})
        is None
    )


# --- Phép chặn theo vị trí ------------------------------------------------


def test_bac_chi_tieu_B01_den_qua_muon():
    """Đúng khoảng cách của ca GVR: B03 xong ở trang 12, ứng viên ở trang 78."""
    ly_do = da_di_qua_bieu_mau("tong_tai_san", 78, {"B02": 10, "B03": 12})
    assert ly_do is not None
    assert "thuyết minh" in ly_do


def test_khong_bac_khi_hai_bieu_mau_ke_nhau_dao_thu_tu():
    """
    Vùng bảng ra ngược thứ tự trong vài trang liền là chuyện BÌNH THƯỜNG.

    Một trang có nhiều vùng và thứ tự vùng do khâu cắt quyết định, không do tờ
    giấy. Bản đầu của phép chặn này không có điều kiện khoảng cách và đã bác
    sạch B01 của một tài liệu hoàn toàn bình thường — bộ test
    `test_don_vi_theo_bang` bắt được. Đừng bỏ điều kiện khoảng cách đi.
    """
    assert da_di_qua_bieu_mau("tai_san_ngan_han", 5, {"B02": 3}) is None


def test_khong_bac_chi_tieu_cua_chinh_bieu_mau_muon_nhat():
    """B03 tới muộn là bình thường — nó vốn là biểu mẫu cuối."""
    assert da_di_qua_bieu_mau("lctt_thuan", 80, {"B02": 10, "B03": 12}) is None


def test_khoa_khong_phai_chi_tieu_thi_bo_qua():
    """`don_vi_tinh` đi cùng đường nhưng không thuộc biểu mẫu nào."""
    assert da_di_qua_bieu_mau("don_vi_tinh", 90, {"B03": 12}) is None


# --- Nối vào vòng lặp VLM -------------------------------------------------


def _vung() -> TableRegion:
    return TableRegion(image=Image.new("RGB", (10, 10)), bbox=(0, 0, 10, 10), confidence=0.9)


def _lap_vlm_gia(monkeypatch, theo_trang: dict):
    """Thay `call_vlm` bằng hàm giả trả phản hồi định sẵn theo số trang."""
    hien_tai = {"trang": 0}

    def goi_gia(base64_image, prompt, temperature=0.0):
        return json.dumps(theo_trang.get(hien_tai["trang"], {}))

    def trang_gia(so_trang):
        hien_tai["trang"] = so_trang
        return {"page": so_trang, "regions": [_vung()]}

    monkeypatch.setattr(extract_vlm, "call_vlm", goi_gia)
    monkeypatch.setattr(extract_vlm, "encode_image_to_base64", lambda anh: "")
    return trang_gia


def test_vong_lap_vlm_khong_nhan_ung_vien_bi_chan(monkeypatch):
    trang_gia = _lap_vlm_gia(monkeypatch, {
        6: {"tai_san_ngan_han": GVR_TSNH},
        12: {"lctt_thuan": 38_605_564_362},
        78: {"tong_tai_san": GVR_TONG_TAI_SAN_BIA},
    })
    ket_qua = extract_vlm.extract_fields_from_regions(
        (trang_gia(so) for so in (6, 12, 78)), standard=Standard.TT99
    )

    # Chỉ tiêu ở nguyên trạng thái TRỐNG, không mang con số bịa. Đây là toàn bộ
    # điểm của cơ chế: lỗi câm chuyển thành lỗi ồn.
    assert ket_qua.data["tong_tai_san"].value is None
    # Và chỉ tiêu đọc đúng vẫn còn nguyên.
    assert ket_qua.data["tai_san_ngan_han"].value == GVR_TSNH


def test_vong_lap_vlm_ghi_lai_ung_vien_bi_chan(monkeypatch):
    """
    Bị chặn phải ghi thành khoá tường minh trong meta.

    Không có sổ này thì "trống vì bị chặn" và "trống vì đọc không ra" trông y
    hệt nhau trong `data`, mà hai chuyện đó khác hẳn nhau khi đọc kết quả.
    """
    trang_gia = _lap_vlm_gia(monkeypatch, {
        6: {"tai_san_ngan_han": GVR_TSNH},
        78: {"tong_tai_san": GVR_TONG_TAI_SAN_BIA},
    })
    ket_qua = extract_vlm.extract_fields_from_regions(
        (trang_gia(so) for so in (6, 78)), standard=Standard.TT99
    )

    bi_chan = ket_qua.meta["ung_vien_bi_chan"]
    assert [m["khoa"] for m in bi_chan] == ["tong_tai_san"]
    assert bi_chan[0]["gia_tri"] == GVR_TONG_TAI_SAN_BIA
    assert bi_chan[0]["trang"] == 78


def test_tai_lieu_binh_thuong_khong_bi_chan_gi(monkeypatch):
    """
    Lưới chặn phải TRONG SUỐT với tài liệu đọc đúng.

    Đây là test quan trọng nhất file: một cơ chế chặn nhầm sẽ làm mất chỉ tiêu
    trên mọi tài liệu, và cái giá đó lớn hơn hẳn thứ nó cứu được ở vài ca hiếm.
    """
    trang_gia = _lap_vlm_gia(monkeypatch, {
        5: {"tai_san_ngan_han": 30_000, "tai_san_dai_han": 70_000,
            "tong_tai_san": 100_000},
        6: {"doanh_thu_thuan": 50_000},
        7: {"lctt_thuan": -1_000},
    })
    ket_qua = extract_vlm.extract_fields_from_regions(
        (trang_gia(so) for so in (5, 6, 7)), standard=Standard.TT99
    )

    assert ket_qua.meta["ung_vien_bi_chan"] == []
    assert ket_qua.data["tong_tai_san"].value == 100_000
    assert ket_qua.data["doanh_thu_thuan"].value == 50_000
    assert ket_qua.data["lctt_thuan"].value == -1_000


# --- Trần đọc: dừng khi mọi thứ còn thiếu đều đã đi qua --------------------


def test_dung_khi_moi_chi_tieu_con_thieu_deu_da_di_qua(monkeypatch):
    """
    Cái TRẦN thật sự, và vì sao `chan_ung_vien` một mình không đủ.

    Phép từ chối ứng viên cứu được con số sai nhưng KHÔNG dừng vòng lặp, nên
    tiền gọi API vẫn tiêu đúng như cũ. Ca GVR đọc tới trang 78 trên 105 vì
    nhánh 1 đòi đủ hết field còn nhánh 2 bị `has_required_fields()` gác —
    thiếu đúng một field bắt buộc là cả hai cùng câm.

    Dựng lại đúng hình dạng ấy: B01 ra một phần ở trang 6, TRỌN VẸN B03 ở trang
    12 — đúng như GVR thật, nơi cả sáu chỉ tiêu lưu chuyển tiền tệ đọc được ở
    trang 11–12 — rồi từ đó không trang nào cho thêm gì. Vòng lặp phải dừng ở
    trang 17 (12 + KHOANG_CACH_TRANG) chứ không đi hết 40 trang.

    B03 phải TRỌN VẸN thì luật mới kết luận được, và đó là giới hạn thật của
    nó: sau B03 không còn biểu mẫu nào, nên một chỉ tiêu B03 còn thiếu không
    bao giờ bị coi là "đã đi qua". Xem test kế tiếp.
    """
    da_doc: list = []
    trang_gia = _lap_vlm_gia(monkeypatch, {
        6: {"tai_san_ngan_han": GVR_TSNH},
        12: {
            "lctt_hdkd": 5_151_615_462_077,
            "lctt_dau_tu": -4_703_647_420_275,
            "lctt_tai_chinh": -409_362_477_440,
            "lctt_thuan": 38_605_564_362,
            "tien_dau_ky": 8_237_433_366_831,
            "anh_huong_ty_gia": -3_522_923_402,
        },
    })

    def cac_trang():
        for so in [6, 12] + list(range(13, 41)):
            da_doc.append(so)
            yield trang_gia(so)

    ket_qua = extract_vlm.extract_fields_from_regions(
        cac_trang(), standard=Standard.TT99
    )

    assert ket_qua.meta["early_stop"]["ly_do"] == "bieu_mau_da_di_qua"
    assert ket_qua.meta["early_stop"]["trang_cuoi"] == 17
    # Thứ phải chốt là SỐ TRANG ĐÃ ĐỌC, không phải giá trị đi ra: một vòng lặp
    # quét hết rồi mới dừng cho ra cùng kết quả, chỉ khác ở hoá đơn API.
    assert max(da_doc) == 17


def test_khong_dung_khi_van_con_bieu_mau_chua_toi(monkeypatch):
    """
    Chưa thấy biểu mẫu sau thì KHÔNG được dừng — thứ còn thiếu có thể ở phía trước.

    Đây là nửa còn lại của cái trần, và là nửa dễ làm hỏng: một điều kiện dừng
    quá hăng sẽ cắt trước khi tới bảng lưu chuyển tiền tệ, và mọi chỉ tiêu B03
    biến mất trên mọi tài liệu.
    """
    da_doc: list = []
    trang_gia = _lap_vlm_gia(monkeypatch, {5: {"tai_san_ngan_han": GVR_TSNH}})

    def cac_trang():
        for so in range(5, 20):
            da_doc.append(so)
            yield trang_gia(so)

    extract_vlm.extract_fields_from_regions(cac_trang(), standard=Standard.TT99)

    # Chưa có chỉ tiêu B02 hay B03 nào, nên không biểu mẫu nào "đã đi qua" —
    # phải đọc hết.
    assert max(da_doc) == 19


def test_khong_dung_khi_con_thieu_chi_tieu_cua_bieu_mau_cuoi(monkeypatch):
    """
    GIỚI HẠN ĐÃ BIẾT của cái trần, chốt lại để không ai tưởng nó rộng hơn thật.

    Luật kết luận "đã đi qua" bằng cách nhìn một biểu mẫu SAU. B03 là biểu mẫu
    cuối, nên một chỉ tiêu B03 còn thiếu không bao giờ có gì để so — và vòng
    lặp vẫn cày hết tài liệu. Đây đúng là ca `HAG_2026Q2_TT99` ngày 03/09/2026:
    `loi_nhuan_sau_thue` không đọc được, tài liệu chạy rất lâu.

    Muốn bịt nốt thì phải có tín hiệu "đã sang phần thuyết minh" độc lập với
    các chỉ tiêu — tức hướng 4 ở HANDOFF mục 17.3, đọc ký hiệu mẫu biểu.
    """
    da_doc: list = []
    trang_gia = _lap_vlm_gia(monkeypatch, {
        6: {"tai_san_ngan_han": GVR_TSNH},
        12: {"lctt_hdkd": 1_000},
    })

    def cac_trang():
        for so in [6, 12] + list(range(13, 31)):
            da_doc.append(so)
            yield trang_gia(so)

    extract_vlm.extract_fields_from_regions(cac_trang(), standard=Standard.TT99)
    assert max(da_doc) == 30
