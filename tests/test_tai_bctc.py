"""
Test danh mục nguồn và script tải tài liệu gold.

Danh mục nguồn là thứ DUY NHẤT vào git để tái lập được tập PDF, nên một mục
hỏng ở đây nghĩa là một tài liệu gold không ai dựng lại được — mà lỗi đó chỉ
lộ ra trên máy người khác, sau khi bài đã nộp.
"""

import json
import re
from pathlib import Path

import pypdfium2 as pdfium
import pytest

from tai_bctc import doc_danh_muc, mo_duoc, tai_mot

DANH_MUC = Path("data/nguon_gold.json")
BAT_BUOC = ("doc_id", "ticker", "period", "san", "loai_bao_cao",
            "chuan_du_kien", "vai_tro", "source_url")


@pytest.fixture(scope="module")
def muc_ds():
    return doc_danh_muc(DANH_MUC)


def test_moi_muc_du_truong_bat_buoc(muc_ds):
    for muc in muc_ds:
        thieu = [t for t in BAT_BUOC if not muc.get(t)]
        assert not thieu, f"{muc.get('doc_id')} thiếu {thieu}"


def test_doc_id_khong_trung_nhau(muc_ds):
    """
    Trùng `doc_id` thì file gold sau ghi đè file trước mà không dấu hiệu nào —
    tập gold tự lặng lẽ nhỏ đi, và số tài liệu đếm được vẫn đúng như cũ.
    """
    ids = [m["doc_id"] for m in muc_ds]
    assert len(ids) == len(set(ids))


# Tỷ lệ tối thiểu mỗi chuẩn phải chiếm trong danh mục.
#
# NỚI TỪ NGƯỠNG TUYỆT ĐỐI ±1 SANG NGƯỠNG TỶ LỆ, ngày 05/09/2026, và đây là
# một lần nới nên phải nói rõ vì sao chứ không lặng lẽ đổi con số.
#
# Ngưỡng cũ viết khi danh mục còn 10 mục, lúc ±1 đúng là "chia đôi". Khi khai
# đủ 70 tài liệu của tập gold thì con số thật là 36 TT200 / 34 TT99 — tức
# 51,4% so với 48,6%. Một ngưỡng tuyệt đối ±1 ở cỡ 70 đòi sự cân bằng hoàn
# hảo tới từng tài liệu, và cách duy nhất thoả nó là VỨT BỚT một tài liệu
# gold — đúng thứ tệ hơn hẳn cái nó định chặn.
#
# Ngưỡng mới vẫn còn răng: nó bắt mọi lệch thật sự làm hỏng trục transfer của
# ablation 8. Một danh mục 50/20 cho ra 28,6% và vẫn đỏ.
TY_LE_TOI_THIEU_MOI_CHUAN = 0.45


def test_ty_le_hai_chuan_can_nhau(muc_ds):
    """
    Guideline mục 7 chốt chia đôi hai chuẩn, và trục transfer của ablation 8
    dựa thẳng vào tỷ lệ đó. Lệch tỷ lệ là hỏng một thí nghiệm, không phải
    hỏng một con số thống kê mô tả.
    """
    dem = {}
    for m in muc_ds:
        dem[m["chuan_du_kien"]] = dem.get(m["chuan_du_kien"], 0) + 1
    assert set(dem) == {"TT99", "TT200"}

    tong = sum(dem.values())
    for chuan, so in dem.items():
        assert so / tong >= TY_LE_TOI_THIEU_MOI_CHUAN, (chuan, dem)


def test_url_tro_ve_dung_ma_chung_khoan(muc_ds):
    """
    Chép nhầm URL giữa hai mã là lỗi câm hoàn hảo: tải về vẫn ra một báo cáo
    tài chính hợp lệ, gán nhãn vẫn chạy, chín đẳng thức vẫn cân — chỉ có
    `ticker` là sai, và không phép kiểm nào ở tầng sau bắt được.
    """
    for muc in muc_ds:
        assert muc["ticker"] in muc["source_url"], muc["doc_id"]


def test_da_kiem_khong_duoc_hua_suong(muc_ds):
    """
    `da_kiem` nghĩa là ĐÃ mở tài liệu ra xem. Một mục vừa khai đã kiểm chuẩn
    mẫu biểu vừa khai chưa kiểm chính thứ đó là mâu thuẫn tự thân, và nó phá
    đúng công dụng của hai trường này — nói cho người sau biết tin được tới
    đâu.
    """
    for muc in muc_ds:
        da = " ".join(muc.get("da_kiem", []))
        chua = " ".join(muc.get("chua_kiem", []))
        assert not ("dấu hiệu TT" in da and "chuẩn mẫu biểu chưa" in chua), muc["doc_id"]


def test_tu_choi_noi_dung_khong_phai_pdf(tmp_path, monkeypatch):
    """
    Vietstock trả trang lỗi HTML kèm mã 200 khi tài liệu bị gỡ. Ghi nó ra
    thành file `.pdf` sẽ làm công cụ gán nhãn nổ ở chỗ dựng ảnh trang, cách
    xa nguyên nhân thật, đúng lúc người dùng đang tìm hiểu vì sao thiếu tài
    liệu.
    """
    class GiaMao:
        status_code = 200
        content = b"<html>Khong tim thay tai lieu</html>"

    monkeypatch.setattr("tai_bctc.requests.get", lambda *a, **k: GiaMao())
    ok, ly_do = tai_mot({"doc_id": "X", "source_url": "https://vi.du/x.pdf"}, tmp_path)

    assert ok is False
    assert "không phải PDF" in ly_do
    assert not (tmp_path / "X.pdf").exists()


def test_danh_muc_khong_chua_con_so_tai_chinh():
    """
    File này VÀO git, nên nó không được mang số liệu doanh nghiệp.

    Cái cần chặn là những con số kiểu `1.988.004.827.520` — số tiền viết theo
    lối Việt, ba chữ số một nhóm. Ngày tháng và số dpi thì vô hại và có mặt
    khắp nơi trong `vai_tro`, nên phép kiểm phải nhắm đúng dạng số tiền chứ
    không chặn mọi chữ số.

    `da_kiem` được miễn: nó cố ý chép vài con số làm bằng chứng đã mở tài
    liệu ra xem tận mắt, và bằng chứng đó chính là thứ làm nó có giá trị.
    """
    tien = re.compile(r"\d{1,3}(?:\.\d{3}){2,}")
    tho = json.loads(DANH_MUC.read_text(encoding="utf-8"))
    for muc in tho["tai_lieu"]:
        for khoa, gt in muc.items():
            if khoa in ("da_kiem", "chua_kiem"):
                continue
            assert not tien.search(str(gt)), f"{muc['doc_id']}.{khoa} có số tiền"


def test_tu_choi_pdf_cut_du_dung_chu_ky_pdf(tmp_path, monkeypatch):
    """
    Chế độ lỗi có thật, `FLC_2021Q4_TT200.pdf` ngày 01/09/2026: bản Vietstock
    phục vụ chỉ 8,0 MB trong khi dict linearization của chính nó khai 13,5 MB,
    hết file giữa một stream, không có `startxref` lẫn `%%EOF`. Nó bắt đầu
    bằng `%PDF` và nặng vài megabyte nên lọt qua cả phép kiểm chữ ký lẫn
    ngưỡng 50 KB, rồi mới nổ ở công cụ gán nhãn — cách nguyên nhân thật rất
    xa. Ghi nó ra đĩa còn tệ hơn: lượt chạy sau đếm nó là "đã có".
    """
    class GiaMao:
        status_code = 200
        content = b"%PDF-1.4\n" + b"x" * 60_000

    monkeypatch.setattr("tai_bctc.requests.get", lambda *a, **k: GiaMao())
    ok, ly_do = tai_mot({"doc_id": "X", "source_url": "https://vi.du/x.pdf"}, tmp_path)

    assert ok is False
    assert "PDF hỏng" in ly_do
    assert not (tmp_path / "X.pdf").exists()


def test_file_da_co_nhung_hong_thi_tai_lai_chu_khong_bao_da_co(tmp_path, monkeypatch):
    """
    Ngưỡng 50 KB vốn để nhận ra trang lỗi HTML; nó không nói gì về một PDF
    cụt vài megabyte. Nếu đường tắt "đã có" chỉ đo kích thước thì lượt chạy
    nào cũng báo xanh cho đúng cái file không mở nổi, và người dùng không có
    cách nào để script tự sửa ngoài việc tự tay đi xoá file.
    """
    hong = tmp_path / "X.pdf"
    hong.write_bytes(b"%PDF-1.4\n" + b"x" * 60_000)

    class GiaMao:
        status_code = 200
        content = _pdf_that_byte()

    monkeypatch.setattr("tai_bctc.requests.get", lambda *a, **k: GiaMao())
    ok, ly_do = tai_mot({"doc_id": "X", "source_url": "https://vi.du/x.pdf"}, tmp_path)

    assert ok is True
    assert ly_do != "đã có"
    assert mo_duoc(hong) is None


def _pdf_that_byte() -> bytes:
    """Một PDF hợp lệ nhỏ nhất, dựng bằng chính thư viện dùng để kiểm."""
    import io

    tai_lieu = pdfium.PdfDocument.new()
    tai_lieu.new_page(200, 300)
    dem = io.BytesIO()
    tai_lieu.save(dem)
    tai_lieu.close()
    return dem.getvalue()
