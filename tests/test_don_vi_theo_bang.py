"""
Test đơn vị tính buộc theo BẢNG, đo qua cả vòng lặp vùng của nhánh VLM.

`test_units.py` chốt từng mảnh rời — `_he_so_vung()`, `_don_vi_tai_lieu()`,
bước quy đổi trong `validate_result()`. File này chốt thứ mà các mảnh rời
không nói được: chúng có được nối đúng thứ tự qua `extract_fields_from_regions()`
hay không, tức một con số đọc ra ở vùng nào thì có thật sự mang hệ số của
vùng ấy đi tới bước quy đổi hay không.

CA ĐƯỢC DỰNG LẠI Ở ĐÂY LÀ CA THẬT, `HNG_2025H1_TT200`. Hồ sơ là công văn
giải trình gửi HNX kèm BCTC soát xét bán niên: trang 1 khai `ĐVT: tỷ đồng`
cho một bảng hai dòng, các trang sau là BCTC khai `nghìn đồng`. Lượt chạy
30/08/2026 đọc đúng từng chữ số nhưng chốt đơn vị ở trang 1 nên 24/26 chỉ
tiêu sai gấp 1e6 lần — hai ô đúng là hai ô bằng 0, tức hai ô bất biến với
phép nhân. Không đẳng thức kế toán nào bắt được, vì hệ ràng buộc thuần nhất.

Chạy được không cần mạng và không cần model: call_vlm bị thay bằng hàm giả.
"""

import json

import pytest
from PIL import Image

import extract_vlm
from extract_vlm import extract_fields_from_regions
from extraction_types import FieldResult, Provenance
from fields_config import Standard
from layout_detection import TableRegion
from router import _he_so_cua_o_da_giu
from validation import validate_result


def _vung() -> TableRegion:
    return TableRegion(image=Image.new("RGB", (100, 100)), bbox=(0, 0, 100, 100), confidence=0.9)


def _lap_vlm_gia(monkeypatch, cac_phan_hoi: list) -> None:
    """Mỗi vùng nhận đúng một phản hồi, theo thứ tự."""
    con_lai = list(cac_phan_hoi)

    def goi_gia(base64_image, prompt, temperature=0.0):
        return json.dumps(con_lai.pop(0) if con_lai else {})

    monkeypatch.setattr(extract_vlm, "call_vlm", goi_gia)
    monkeypatch.setattr(extract_vlm, "encode_image_to_base64", lambda anh: "")


# Bảng hai dòng của công văn giải trình: khai tỷ đồng, và chỉ đọc ra được
# đúng một chỉ tiêu. Con số 258,9 là lỗ sau thuế hợp nhất in trên trang 1.
CONG_VAN = {"loi_nhuan_sau_thue": -258.9, "don_vi_tinh": "ĐVT: tỷ đồng"}

# Bảng cân đối của chính hồ sơ ấy, khai nghìn đồng.
BANG_CAN_DOI = {
    "tong_tai_san": 18_281_308_818,
    "tai_san_ngan_han": 2_748_201_562,
    "tai_san_dai_han": 15_533_107_256,
    "don_vi_tinh": "Đơn vị tính: nghìn đồng",
}


def _hai_vung(monkeypatch, phan_hoi_thu_hai=None):
    _lap_vlm_gia(monkeypatch, [CONG_VAN, phan_hoi_thu_hai or BANG_CAN_DOI])
    trang = [{"page": 1, "regions": [_vung()]}, {"page": 5, "regions": [_vung()]}]
    return extract_fields_from_regions(trang, standard=Standard.TT200)


def test_moi_o_mang_he_so_cua_dung_bang_da_sinh_ra_no(monkeypatch):
    """
    Ô đọc từ công văn mang tỷ đồng, ô đọc từ bảng cân đối mang nghìn đồng —
    trong CÙNG một tài liệu. Đây là điều bản trước không biểu diễn được.
    """
    he_so = _hai_vung(monkeypatch).meta["he_so_don_vi_theo_truong"]

    assert he_so["loi_nhuan_sau_thue"] == 1_000_000_000
    assert he_so["tong_tai_san"] == 1_000
    assert he_so["tai_san_ngan_han"] == 1_000


def test_bang_sau_tu_khai_thi_de_don_vi_cua_bang_truoc(monkeypatch):
    """
    Chỗ đảo ngược hành vi cũ. Trước đây vùng đầu tiên đọc được đơn vị sẽ chốt
    cho cả tài liệu, nên `tỷ đồng` của công văn thắng và không bao giờ bị đọc
    lại — đúng cơ chế đã làm hỏng HNG.
    """
    theo_vung = _hai_vung(monkeypatch).meta["don_vi_theo_vung"]

    assert [v["nguon"] for v in theo_vung] == ["doc_duoc", "doc_duoc"]
    assert [v["he_so"] for v in theo_vung] == [1_000_000_000, 1_000]


def test_bang_khong_khai_don_vi_thi_ke_thua_bang_truoc(monkeypatch):
    """
    Phần lan của cơ chế, cho trang tiếp nối không in lại dòng đơn vị. Bản
    khai phải nói rõ đây là kế thừa chứ không phải đọc được tại chỗ: hai mức
    tin cậy khác nhau, và gộp lại thì mất một chế độ lỗi khỏi phép đo.
    """
    khong_khai = {k: v for k, v in BANG_CAN_DOI.items() if k != "don_vi_tinh"}

    ket_qua = _hai_vung(monkeypatch, khong_khai)
    theo_vung = ket_qua.meta["don_vi_theo_vung"]

    assert theo_vung[1]["nguon"] == "ke_thua"
    assert theo_vung[1]["raw"] is None
    assert ket_qua.meta["he_so_don_vi_theo_truong"]["tong_tai_san"] == 1_000_000_000


def test_don_vi_muc_tai_lieu_theo_da_so_chu_khong_theo_vung_dau_tien(monkeypatch):
    """
    Tập gold chấm bằng một `unit_multiplier` DUY NHẤT cho mỗi tài liệu
    (ANNOTATION-GUIDELINE mục 3.1), nên vẫn phải có một kết luận mức tài
    liệu. Lấy theo đa số chỉ tiêu thì HNG ra `nghìn đồng` — khớp gold; lấy
    theo vùng đầu tiên thì ra `tỷ đồng` và bảng chấm điểm sẽ báo sai đơn vị
    trong khi phần lớn con số đã quy đổi đúng.
    """
    assert _hai_vung(monkeypatch).meta["don_vi_tinh"] == "Đơn vị tính: nghìn đồng"


def test_ca_hai_bang_cung_ra_dung_so_VND(monkeypatch):
    """
    TEST CHỐNG TÁI PHÁT, dựng lại nguyên ca HNG từ đầu tới con số cuối.

    Điều kiện thắng không phải là "chọn được đơn vị đúng" mà là CẢ HAI bảng
    cùng đúng một lúc — thứ mà không hệ số toàn cục nào làm được. Con số so
    ở đây lấy thẳng từ `data/gold/HNG_2025H1_TT200.json`.
    """
    ket_qua = _hai_vung(monkeypatch)
    data = validate_result(
        ket_qua.values(), Standard.TT200, ket_qua.meta["he_so_don_vi_theo_truong"]
    )["data"]

    assert data["tong_tai_san"] == 18_281_308_818_000
    assert data["tai_san_ngan_han"] == 2_748_201_562_000
    # So xấp xỉ ở ô này, và chỉ ở ô này: công văn in `258,9` — một số THẬP
    # PHÂN — nên `-258,9 × 1e9` là phép nhân dấu phẩy động và ra
    # -258.899.999.999,99997. Bảng cân đối in số nguyên nghìn đồng nên hai ô
    # kia không có chuyện đó. Sai số 3e-5 đồng nằm sâu dưới biên 0,1% mà
    # `eval/metrics.py` dùng để chấm đúng/sai.
    assert data["loi_nhuan_sau_thue"] == pytest.approx(-258_900_000_000)


def test_o_do_nhanh_OCR_giu_thi_khong_muon_he_so_cua_vung_VLM():
    """
    Nhánh VLM đọc ra một chỉ tiêu KHÔNG có nghĩa là giá trị cuối cùng của chỉ
    tiêu ấy đến từ đó. Với `USE_OCR_FIRST=true` — cấu hình đang chạy thật —
    `run_vlm()` chỉ cho VLM ghi đè khi ô còn trống hoặc validate đã báo
    warning, nên một ô do regex điền vẫn có thể ở lại.

    Nếu bản đồ hệ số không lọc theo đó thì con số của OCR bị nhân bằng hệ số
    của một vùng nó chưa từng được đọc ra. Hỏng theo kiểu tệ nhất: kết quả
    vẫn là một con số hợp lệ và không có gì báo.
    """
    tu_vlm = FieldResult(value=1, confidence=1.0, provenance=Provenance(5, 0, (0, 0, 1, 1)))
    tu_ocr = FieldResult.khong_do(2)

    loc = _he_so_cua_o_da_giu(
        {"tong_tai_san": tu_vlm, "doanh_thu_thuan": tu_ocr},
        {"tong_tai_san": 1_000, "doanh_thu_thuan": 1_000},
    )

    assert loc == {"tong_tai_san": 1_000}
