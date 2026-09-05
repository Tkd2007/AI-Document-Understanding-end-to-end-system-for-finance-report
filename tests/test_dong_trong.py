"""
Luật dòng trống — tu chính `PREREGISTRATION.md` 05/09/2026.

Luật: chỉ tiêu không neo được vào vùng bảng nào **và** nằm trong
`CO_THE_VANG_MAT` thì tập ứng viên của nó là ĐÚNG MỘT phần tử `0`, thay thế
cả năm nguồn thông thường.

TOÀN BỘ GIÁ TRỊ CỦA LUẬT NÀY NẰM Ở CHỖ NÓ NỔ ĐÚNG CA. Ba ca dưới đây trông
giống hệt nhau nếu chỉ nhìn `o_lan_can` rỗng hay `vung is None`, nhưng chúng
nói ba điều khác hẳn:

  (a) **chưa hề OCR vùng nào** — mọi chỉ tiêu đều không có vùng. Kết luận
      "tám dòng này trống" khi đó là kết luận rút từ việc TA ĐÃ KHÔNG NHÌN,
      không phải từ tờ giấy. Bản cài đặt đầu ngày 05/09 mắc đúng lỗi này và
      bị `tests/test_tang_repair.py` bắt: nó xoá mất ứng viên lật dấu của
      `thue_tndn_hoan_lai` trong một fixture chưa từng OCR vùng nào.
  (b) **đã OCR vùng, chỉ tiêu vẫn không nằm trong vùng nào** — ca DUY NHẤT
      luật được áp.
  (c) **có vùng nhưng vùng không bóc được ô số nào** — vẫn là có vùng, nên
      luật không áp.

Và một lớp thứ hai: kể cả trong ca (b), luật chỉ áp cho tám dòng CHI TIẾT
của `CO_THE_VANG_MAT`. Dòng TỔNG lọt vào đây là dựng lại ca `PLX_2026Q2_TT99`
bị điền `tong_tai_san = 0` trong khi giá trị thật là 87.876 tỷ.
"""

import router
from extraction_types import FieldResult, Provenance
from fields_config import CO_THE_VANG_MAT, QuyUocDau, Standard
from repair.candidates import generate

# `thue_tndn_hoan_lai` nằm trong CO_THE_VANG_MAT; `tong_tai_san` thì không và
# không bao giờ được nằm trong — nó là dòng tổng.
TRONG_DANH_SACH = "thue_tndn_hoan_lai"
NGOAI_DANH_SACH = "tong_tai_san"


def _bo_so_can():
    """Đẳng thức mã 60 ở quy ước TỔNG: 1000 + (−300) + 50 = 750."""
    return {
        "loi_nhuan_truoc_thue": 1_000.0,
        "thue_tndn_hien_hanh": -300.0,
        "thue_tndn_hoan_lai": 50.0,
        "loi_nhuan_sau_thue": 750.0,
    }


def _prov(trang: int = 1, vung: int = 0) -> Provenance:
    """bbox không dùng tới ở đây nhưng là tham số bắt buộc của Provenance."""
    return Provenance(page=trang, region_index=vung, bbox=(0, 0, 10, 10))


def _ket_qua_co_provenance(gia_tri: dict, trang: int = 1, vung: int = 0) -> dict:
    return {
        k: FieldResult(value=v, confidence=1.0, provenance=_prov(trang, vung))
        for k, v in gia_tri.items()
    }


def _vung_gia(o_so=None) -> dict:
    """Một vùng bảng giả, khoá theo (trang, chỉ số vùng) đúng như `gom_vung`."""
    return {(1, 0): {"region_index": 0, "o_so": o_so or []}}


# ----------------------------------------------------- lớp 1: nổ đúng ca


def test_ca_b_da_ocr_vung_ma_khong_neo_duoc_thi_ung_vien_DUY_NHAT_la_0():
    """Ca duy nhất luật được áp."""
    uv = generate(TRONG_DANH_SACH, -50.0, khong_co_vung=True)

    assert len(uv) == 1
    assert uv[0].value == 0
    assert uv[0].source == "dong_trong"


def test_ca_a_chua_he_ocr_vung_nao_thi_luat_KHONG_ap():
    """
    Đây là lỗi mà test tầng repair đã bắt ngày 05/09, nên chốt lại ở đúng mức
    router: `vung_theo_khoa` rỗng thì không chỉ tiêu nào được coi là dòng trống,
    và ứng viên lật dấu vẫn phải còn để sửa được lỗi dấu.
    """
    gia_tri = {**_bo_so_can(), TRONG_DANH_SACH: -50.0}

    sau, cc = router.chay_tang_repair(
        gia_tri, _ket_qua_co_provenance(gia_tri), Standard.TT200, QuyUocDau.TONG,
        vung_theo_khoa=None,
    )

    assert cc["verdict"] == "REPAIRED"
    assert sau[TRONG_DANH_SACH] == 50.0
    assert cc["da_doi"][TRONG_DANH_SACH]["nguon_ung_vien"] == "sign"


def test_ca_c_co_vung_nhung_vung_khong_boc_duoc_o_so_nao_thi_luat_KHONG_ap():
    """
    Vùng bóc được 0 ô số là chuyện của chất lượng OCR, không phải bằng chứng
    dòng trống. Đây chính là ca mà phép xoay vùng ngày 04/09 sinh ra để chữa,
    nên nếu luật dòng trống nuốt nó thì hai cơ chế đánh nhau âm thầm.
    """
    gia_tri = {**_bo_so_can(), TRONG_DANH_SACH: -50.0}

    sau, cc = router.chay_tang_repair(
        gia_tri, _ket_qua_co_provenance(gia_tri), Standard.TT200, QuyUocDau.TONG,
        vung_theo_khoa=_vung_gia(o_so=[]),
    )

    assert cc["verdict"] == "REPAIRED"
    assert sau[TRONG_DANH_SACH] == 50.0
    assert cc["da_doi"][TRONG_DANH_SACH]["nguon_ung_vien"] == "sign"


def test_ca_b_that_su_qua_router_chi_tieu_lac_khoi_moi_vung():
    """
    Ca (b) dựng qua router chứ không chỉ qua `generate`: đã có vùng ở
    (trang 1, vùng 0), nhưng chỉ tiêu này khai provenance ở vùng 9 nên không
    tra ra vùng nào. Chỉ nó được hưởng luật; các chỉ tiêu khác vẫn có vùng.
    """
    gia_tri = {**_bo_so_can(), TRONG_DANH_SACH: -50.0}
    ket_qua = _ket_qua_co_provenance(gia_tri)
    ket_qua[TRONG_DANH_SACH] = FieldResult(
        value=-50.0, confidence=1.0, provenance=_prov(vung=9)
    )

    sau, cc = router.chay_tang_repair(
        gia_tri, ket_qua, Standard.TT200, QuyUocDau.TONG,
        vung_theo_khoa=_vung_gia(o_so=[]),
    )

    assert cc["neo"][TRONG_DANH_SACH] == "khong_co_vung"
    # Ứng viên duy nhất là 0, mà 0 không làm đẳng thức cân (cần +50), nên
    # phương pháp phải BỎ CUỘC thay vì lật dấu một con số nó không đọc lại được.
    assert sau[TRONG_DANH_SACH] == -50.0


# ----------------------------------------- lớp 2: chỉ tám dòng chi tiết


def test_dong_tong_KHONG_BAO_GIO_duoc_huong_luat():
    """
    Chốt bằng hành vi, không bằng lời: dòng tổng không neo được vào vùng nào
    vẫn phải giữ nguyên tập ứng viên thường. Đây là ca `PLX_2026Q2_TT99`.
    """
    uv = generate(NGOAI_DANH_SACH, 87_876_000_000.0, khong_co_vung=True)

    assert len(uv) > 1
    assert all(u.source != "dong_trong" for u in uv)


def test_danh_sach_trang_khong_chua_dong_tong_nao():
    """
    Bất biến trên chính danh sách, không qua trung gian. Nếu một ngày có người
    thêm dòng tổng vào `CO_THE_VANG_MAT` thì luật dòng trống lập tức thành cơ
    chế xoá trắng bảng cân đối, nên chốt ở đây nữa cho chắc.
    """
    dong_tong = {
        "tong_tai_san", "tong_nguon_von", "tai_san_ngan_han", "tai_san_dai_han",
        "no_phai_tra", "von_chu_so_huu", "loi_nhuan_truoc_thue",
        "loi_nhuan_sau_thue", "loi_nhuan_gop", "lctt_thuan",
    }

    assert CO_THE_VANG_MAT & dong_tong == set()


def test_gia_tri_None_thi_khong_sinh_gi_du_co_vung_hay_khong():
    """
    Chỉ tiêu chưa đọc được là `thieu_gia_tri`, không phải dòng trống. Hai thứ
    khác nhau: một bên máy không đọc được, một bên tờ giấy không in.
    """
    assert generate(TRONG_DANH_SACH, None, khong_co_vung=True) == []
