"""
Trần nhánh VLM: không đọc quá trang mà nhánh OCR đã dừng.

BA CA THẬT LÀM CHUẨN CHO CẢ FILE, đo từ log lượt chấm 70 tài liệu ngày
03/09/2026 (69 đoạn tài liệu có đủ dữ liệu). Trần này diệt 5 ô SAI và làm mất
0 ô ĐÚNG:

  * `GVR_2026Q2_TT99` — OCR dừng ở trang 22, VLM cày tới trang 78 rồi nhận
    `tong_tai_san` = 406.588.902.083 trong khi thật là 90.263.949.529.178.
  * `FLC_2021Q4_TT200` — OCR dừng ở trang 19, VLM nhận hai ô B02 ở trang 54,
    cả hai sai.
  * `DLG_2026Q2_TT99` — ca NGƯỢC LẠI, và là ca quyết định vì sao trần đặt
    ĐÚNG mốc OCR dừng chứ không lùi thêm. PDF ảnh scan, OCR không đọc được ô
    nào nên bỏ cuộc ngay ở trang 10, trong khi B02 bắt đầu ở trang 6 và VLM
    đọc đúng 13 ô ở trang 6–8. Lùi trần thêm 5 trang là mất sạch 13 ô ấy.

Bài học đằng sau ba ca: trang OCR dừng KHÔNG đo bảng nằm ở đâu, nó đo chỗ OCR
bỏ cuộc. Dùng nó làm trần thì được, lùi thêm thì cắt vào vùng còn bảng thật.
"""

import json

from PIL import Image

import extract_vlm
from fields_config import QuyUocDau, Standard
from layout_detection import TableRegion

# Số thật của GVR_2026Q2_TT99 và DLG_2026Q2_TT99.
GVR_OCR_DUNG = 22
GVR_TONG_TAI_SAN_BIA = 406_588_902_083
DLG_OCR_DUNG = 10
DLG_DOANH_THU = 23_270_602_774
DLG_LCTT_THUAN = 5_854_841_791


def _vung():
    return TableRegion(image=Image.new("RGB", (10, 10)), bbox=(0, 0, 10, 10), confidence=0.9)


def _lap_vlm_gia(monkeypatch, theo_trang: dict):
    """VLM giả trả về đúng bộ giá trị đã khai cho từng trang."""
    hien_tai = {"trang": None}
    da_goi = []

    def goi_gia(*_a, **_k):
        da_goi.append(hien_tai["trang"])
        return json.dumps(theo_trang.get(hien_tai["trang"], {}))

    def trang_gia(so_trang):
        hien_tai["trang"] = so_trang
        return {"page": so_trang, "regions": [_vung()]}

    monkeypatch.setattr(extract_vlm, "call_vlm", goi_gia)
    monkeypatch.setattr(extract_vlm, "encode_image_to_base64", lambda anh: "")
    return trang_gia, da_goi


def test_khong_doc_qua_trang_ocr_da_dung(monkeypatch):
    """Ca GVR: trang 78 nằm ngoài trần nên không bao giờ được gọi VLM."""
    trang_gia, da_goi = _lap_vlm_gia(monkeypatch, {
        6: {"tai_san_ngan_han": 37_897_604_212_888},
        78: {"tong_tai_san": GVR_TONG_TAI_SAN_BIA},
    })
    ket_qua = extract_vlm.extract_fields_from_regions(
        (trang_gia(so) for so in (6, 78)),
        standard=Standard.TT99,
        trang_toi_da=GVR_OCR_DUNG,
    )

    assert ket_qua.data["tong_tai_san"].value is None
    assert ket_qua.data["tai_san_ngan_han"].value == 37_897_604_212_888
    # Không chỉ "không nhận", mà là KHÔNG GỌI — trần phải chặn trước khi tiêu
    # tiền API, nếu không nó chỉ là một phép lọc đắt tiền.
    assert 78 not in da_goi


def test_ghi_ly_do_dung_rieng_cho_tran(monkeypatch):
    """
    `ly_do` của trần phải khác `het_bang_de_doc`.

    Dừng vì hết kiên nhẫn và dừng vì đụng trần là hai chuyện khác nhau khi đối
    chiếu chi phí giữa các lượt chạy, và chỉ khoá này phân biệt được.
    """
    trang_gia, _ = _lap_vlm_gia(monkeypatch, {6: {"tai_san_ngan_han": 1}})
    ket_qua = extract_vlm.extract_fields_from_regions(
        (trang_gia(so) for so in (6, 78)),
        standard=Standard.TT99,
        trang_toi_da=GVR_OCR_DUNG,
    )

    dung_som = ket_qua.meta["early_stop"]
    assert dung_som["da_dung_som"] is True
    assert dung_som["ly_do"] == "tran_ocr"
    # Trang cuối THẬT SỰ đọc, không phải trang bị chặn.
    assert dung_som["trang_cuoi"] == 77


def test_ca_DLG_tran_dung_moc_thi_khong_mat_o_nao(monkeypatch):
    """
    Ca quyết định: OCR bỏ cuộc sớm vì PDF ảnh scan, nhưng bảng nằm TRONG trần.

    Đây là test giữ cho trần khỏi bị lùi thêm vài trang cho "an toàn". Lùi 5
    trang là trần thành trang 5, và cả 13 ô đúng của DLG ở trang 6–8 mất sạch.
    """
    trang_gia, _ = _lap_vlm_gia(monkeypatch, {
        6: {"doanh_thu_thuan": DLG_DOANH_THU},
        8: {"lctt_thuan": DLG_LCTT_THUAN},
    })
    ket_qua = extract_vlm.extract_fields_from_regions(
        (trang_gia(so) for so in (6, 7, 8)),
        standard=Standard.TT99,
        trang_toi_da=DLG_OCR_DUNG,
    )

    assert ket_qua.data["doanh_thu_thuan"].value == DLG_DOANH_THU
    assert ket_qua.data["lctt_thuan"].value == DLG_LCTT_THUAN


def test_khong_co_tran_thi_doc_nhu_cu(monkeypatch):
    """
    `trang_toi_da=None` phải giữ NGUYÊN hành vi cũ.

    Nhánh OCR có thể không chạy (`USE_OCR_FIRST=false`), và khi ấy không có
    mốc nào để lấy. Trần mà tự dựng ra một con số trong ca đó thì nó chặn sạch
    nhánh VLM ở đúng lượt chạy cần nhánh ấy nhất.
    """
    trang_gia, da_goi = _lap_vlm_gia(monkeypatch, {
        78: {"tong_tai_san": GVR_TONG_TAI_SAN_BIA},
    })
    ket_qua = extract_vlm.extract_fields_from_regions(
        (trang_gia(so) for so in (6, 78)), standard=Standard.TT99
    )

    assert ket_qua.data["tong_tai_san"].value == GVR_TONG_TAI_SAN_BIA
    assert 78 in da_goi


def test_tat_early_stop_thi_tran_cung_tat(monkeypatch):
    """
    Đường ĐO phải tắt được trần, cùng lý do với ba nhánh dừng sớm kia.

    Một ô vắng mặt vì chưa được quét tới và một ô vắng mặt vì model đọc hỏng
    trông giống hệt nhau trong bảng kết quả — xem docstring DISABLE_EARLY_STOP.
    """
    monkeypatch.setattr(extract_vlm, "DISABLE_EARLY_STOP", True)
    trang_gia, da_goi = _lap_vlm_gia(monkeypatch, {
        78: {"tong_tai_san": GVR_TONG_TAI_SAN_BIA},
    })
    ket_qua = extract_vlm.extract_fields_from_regions(
        (trang_gia(so) for so in (6, 78)),
        standard=Standard.TT99,
        trang_toi_da=GVR_OCR_DUNG,
    )

    assert ket_qua.data["tong_tai_san"].value == GVR_TONG_TAI_SAN_BIA
    assert 78 in da_goi


# --- Nối dây: router phải chuyển mốc OCR xuống nhánh VLM -------------------


def _bat_tham_so(monkeypatch):
    """Bắt tham số `trang_toi_da` mà router truyền xuống nhánh VLM."""
    import router
    from extraction_types import ExtractionResult

    da_nhan = {}

    def vlm_gia(pages, *_a, **kwargs):
        list(pages)
        da_nhan["trang_toi_da"] = kwargs.get("trang_toi_da")
        return ExtractionResult(data={}, meta={})

    monkeypatch.setattr(router, "extract_fields_from_regions", vlm_gia)
    monkeypatch.setattr(router, "validate_result", lambda *a, **k: {"warnings": []})
    return da_nhan


def test_run_vlm_chuyen_moc_ocr_xuong_nhanh_vlm(monkeypatch):
    """
    Mốc phải đi từ certificate của nhánh OCR xuống tận `extract_...()`.

    Đây là chỗ dễ nối sai nhất: trần đúng, test đơn vị xanh, mà đường thật vẫn
    đọc tới hết tài liệu vì không ai truyền mốc xuống.
    """
    import router

    da_nhan = _bat_tham_so(monkeypatch)
    router.run_vlm(
        iter([]), [], {}, Standard.TT99, QuyUocDau.TRU,
        trang_toi_da=GVR_OCR_DUNG,
    )

    assert da_nhan["trang_toi_da"] == GVR_OCR_DUNG


def test_khong_co_moc_thi_chuyen_None_chu_khong_chuyen_0(monkeypatch):
    """
    Nhánh OCR không chạy -> `trang_cuoi` là None -> phải xuống nguyên None.

    Nếu chỗ nào đó lùi về `len(cached_pages)` thì lượt chạy không bật nhánh
    OCR sẽ nhận trần 0 và nhánh VLM bị chặn sạch ngay từ trang đầu — đúng lượt
    chạy cần nhánh ấy nhất.
    """
    import router

    da_nhan = _bat_tham_so(monkeypatch)
    router.run_vlm(
        iter([]), [], {}, Standard.TT99, QuyUocDau.TRU,
    )

    assert da_nhan["trang_toi_da"] is None
