"""
Chọn bộ dựng ảnh trang PDF bằng `PDF_BACKEND`.

VÌ SAO CÓ HAI BỘ DỰNG, và vì sao lựa chọn giữa chúng phải được chốt bằng
test. `pdf2image` gọi nhị phân Poppler ở ngoài, nên nó phụ thuộc vào thứ
nằm ngoài tầm với của `pip` — ngày 03/09/2026 nó segfault ngay khâu khởi
tạo trên máy phát triển vì máy thiếu Visual C++ Redistributable. `pypdfium2`
là wheel thuần, không có bề mặt hỏng đó, nên nó là đường lui khi một máy
không cài nổi Poppler.

THỨ PHẢI CHỐT KHÔNG PHẢI "ẢNH DỰNG RA ĐÚNG", mà là **cờ chọn đúng bộ dựng
nào**. Hai bộ dựng cho ra pixel khác nhau, nên một lượt chấm âm thầm rơi
sang bộ kia là một lượt chấm không so được với lượt trước — và không con số
nào trong kết quả nói ra điều đó. Vì thế các test dưới đây bịt kín đường
Poppler bằng hàm giả biết nổ: nếu nhánh `pdfium` lỡ gọi sang đó, test đỏ
ngay chứ không im lặng cho qua.

Chạy được không cần Poppler và không cần mạng: PDF dùng để thử được dựng
ngay trong test bằng chính `pypdfium2`.
"""

import io
import math

import pypdfium2 as pdfium
import pytest

import ocr_baseline


def _px(diem: float) -> int:
    """
    Cỡ pixel mà pypdfium2 dựng ra cho một cạnh dài `diem` point.

    Làm tròn LÊN, không làm tròn gần nhất: pdfium lấy `ceil` nên trang rộng
    200 point ở 300 dpi ra 834 pixel chứ không phải 833. Viết công thức ra
    đây thay vì chép sẵn con số, để test nói lên quan hệ point–dpi–pixel chứ
    không chỉ nói lên một kết quả đo được.
    """
    return math.ceil(diem / 72 * ocr_baseline.PDF_DPI)


def _pdf_thu(tmp_path, kich_thuoc=((200, 100), (300, 400))):
    """
    Một PDF trắng có số trang và cỡ trang biết trước, ghi vào `tmp_path`.

    Dựng bằng pypdfium2 chứ không kèm sẵn một file mẫu trong repo: cỡ trang
    tính bằng point là thứ test cần khẳng định, và nó phải đọc được ngay ở
    đây chứ không nằm trong một file nhị phân không ai mở ra xem.
    """
    tai_lieu = pdfium.PdfDocument.new()
    for rong, cao in kich_thuoc:
        tai_lieu.new_page(rong, cao)
    dem = io.BytesIO()
    tai_lieu.save(dem)
    tai_lieu.close()

    duong_dan = tmp_path / "thu.pdf"
    duong_dan.write_bytes(dem.getvalue())
    return duong_dan


@pytest.fixture
def chan_poppler(monkeypatch):
    """
    Thay hai lối vào Poppler bằng hàm nổ.

    Đây là phần cốt lõi của bộ test này: nó biến "nhánh pdfium lỡ gọi sang
    Poppler" từ một chuyện không ai thấy thành một test đỏ.
    """

    def no(*_args, **_kwargs):
        raise AssertionError("nhánh pdfium không được phép gọi sang pdf2image")

    monkeypatch.setattr(ocr_baseline, "convert_from_path", no)
    monkeypatch.setattr(ocr_baseline, "pdfinfo_from_path", no)


def test_backend_la_pdfium_thi_dem_trang_khong_dung_poppler(tmp_path, monkeypatch, chan_poppler):
    monkeypatch.setattr(ocr_baseline, "PDF_BACKEND", "pdfium")
    assert ocr_baseline.count_pages(str(_pdf_thu(tmp_path))) == 2


def test_backend_la_pdfium_thi_dung_anh_khong_dung_poppler(tmp_path, monkeypatch, chan_poppler):
    monkeypatch.setattr(ocr_baseline, "PDF_BACKEND", "pdfium")
    anh = ocr_baseline.load_page(str(_pdf_thu(tmp_path)), 1)

    # Cỡ ảnh phải theo PDF_DPI. PDF đo bằng point (72 mỗi inch), nên trang
    # rộng 200 point ở 300 dpi ra 200/72*300 pixel. Chốt con số này vì nó là
    # chỗ duy nhất hai bộ dựng phải khớp nhau: pdf2image nhận thẳng `dpi`,
    # pypdfium2 nhận hệ số phóng, và quy đổi sai thì ảnh vào OCR lệch cỡ mà
    # chẳng có gì báo.
    assert anh.size == (_px(200), _px(100))
    # JPEG gửi cho VLM không nhận RGBA, xem comment ở load_page().
    assert anh.mode == "RGB"


def test_trang_danh_so_tu_1(tmp_path, monkeypatch, chan_poppler):
    """
    `load_page` đánh số từ 1, còn pypdfium2 đánh chỉ số từ 0.

    Lệch một ở đây không làm gì nổ: nó chỉ khiến pipeline đọc nhầm trang,
    rồi mọi chỉ tiêu sai vì một lý do chẳng liên quan gì tới phương pháp.
    Hai trang trong PDF thử có cỡ khác nhau chính là để bắt được lệch ấy.
    """
    monkeypatch.setattr(ocr_baseline, "PDF_BACKEND", "pdfium")
    duong_dan = str(_pdf_thu(tmp_path))

    trang_1 = ocr_baseline.load_page(duong_dan, 1)
    trang_2 = ocr_baseline.load_page(duong_dan, 2)

    assert trang_1.size == (_px(200), _px(100))
    assert trang_2.size == (_px(300), _px(400))


def test_backend_la_lay_thi_no_ngay(tmp_path, monkeypatch):
    """
    Giá trị lạ phải nổ, không được lặng lẽ rơi về Poppler.

    Một lỗi gõ như `PDF_BACKEND=pdfum` mà rơi về mặc định thì máy vẫn chạy,
    kết quả vẫn ra, và cả lượt chấm dùng bộ dựng khác hẳn cái người chạy
    tưởng mình đã chọn.
    """
    monkeypatch.setattr(ocr_baseline, "PDF_BACKEND", "pdfum")
    duong_dan = str(_pdf_thu(tmp_path))

    with pytest.raises(RuntimeError, match="PDF_BACKEND"):
        ocr_baseline.count_pages(duong_dan)
    with pytest.raises(RuntimeError, match="PDF_BACKEND"):
        ocr_baseline.load_page(duong_dan, 1)


def test_cau_hinh_luot_chay_ghi_ra_backend(monkeypatch):
    """
    File kết quả tập gold phải tự khai nó chạy bằng bộ dựng nào.

    Không có khoá này thì hai file `tap_gold_*.json` dựng bằng hai bộ dựng
    khác nhau trông giống hệt nhau, và người đọc chỉ còn cách đoán.
    """
    from eval import chay_tap_gold

    monkeypatch.setattr(chay_tap_gold, "PDF_BACKEND", "pdfium")
    cau_hinh = chay_tap_gold.cau_hinh_luot_chay()

    assert cau_hinh["pdf_backend"] == "pdfium"
    # Trạng thái tường minh: các cờ định hình lượt chạy đều phải có mặt bằng
    # khoá riêng, không để người đọc suy ra từ sự vắng mặt của khoá khác.
    for khoa in ("thiet_bi", "ocr_first", "tang_repair", "tat_cong_rang_buoc", "tat_probe_dong"):
        assert khoa in cau_hinh


def test_thiet_bi_khong_co_torch_thi_noi_ra(monkeypatch):
    """
    Thiếu torch phải ra một chuỗi nói rõ điều đó, không được ném ImportError.

    CI không cài torch (xem CLAUDE.md), nên `cau_hinh_luot_chay()` mà nổ vì
    thiếu torch là làm hỏng cả lượt chấm ở đúng dòng đầu tiên.
    """
    import builtins

    from eval import chay_tap_gold

    that = builtins.__import__

    def gia(ten, *args, **kwargs):
        if ten == "torch":
            raise ImportError("gia vo nhu khong co torch")
        return that(ten, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", gia)
    assert chay_tap_gold._thiet_bi_tinh() == "khong-co-torch"
