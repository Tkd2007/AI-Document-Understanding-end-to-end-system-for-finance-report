"""
Pipeline step 1: Document -> Raw Text (OCR baseline)

Uses EasyOCR (Vietnamese + English) instead of training DBNet/PARSeq
from scratch. The goal at this stage is NOT the best possible OCR
quality, but a working end-to-end "walking skeleton" to build on.

Usage:
    python src/ocr_baseline.py data/samples/report.pdf
    python src/ocr_baseline.py data/samples/report.png
"""

import os
import re
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from PIL import Image

from extract_baseline import parse_number
from layout_detection import ca_trang, get_table_regions
from metrics import timer

load_dotenv()


LANGUAGES = ["vi", "en"]
PDF_DPI = 300

_reader = None

try:
    from pdf2image import convert_from_path, pdfinfo_from_path
except ImportError:
    convert_from_path = None
    pdfinfo_from_path = None


def _require_pdf2image() -> None:
    """
    Chặn sớm khi pdf2image không import được.

    Không có hàm này thì `pdfinfo_from_path` và `convert_from_path` vẫn là
    None và lời gọi nổ ra `TypeError: 'NoneType' object is not callable` —
    một câu báo lỗi không hề gợi ý rằng thư viện bị thiếu.
    """
    if convert_from_path is None or pdfinfo_from_path is None:
        raise RuntimeError(
            "pdf2image chưa cài (hoặc import thất bại) nên không đọc được PDF. "
            "Cài bằng: pip install -r requirements.txt"
        )


def count_pages(file_path: str) -> int:
    """
    Số trang của tài liệu, KHÔNG convert ảnh.

    pdfinfo_from_path chỉ đọc metadata qua binary `pdfinfo` của Poppler
    nên gần như tức thì, khác hẳn convert_from_path vốn render từng trang
    thành bitmap 300 DPI.
    """
    path = Path(file_path)
    if path.suffix.lower() != ".pdf":
        return 1

    # count_pages() chạy TRƯỚC load_page() trong iter_table_regions(), nên
    # đây mới là chỗ đầu tiên chạm tới pdf2image — check phải nằm ở đây,
    # không phải chỉ ở load_page().
    _require_pdf2image()

    info = pdfinfo_from_path(str(path), poppler_path=os.getenv("POPPLER_PATH"))
    return info["Pages"]


def load_page(file_path: str, page_no: int) -> Image.Image:
    """
    Convert ĐÚNG một trang thành ảnh. Đánh số từ 1.

    Thay cho cách cũ là convert cả tài liệu một lượt: đo trên
    báo cáo VNM 55 trang, convert toàn bộ mất 169s trong khi pipeline
    chỉ thực sự đọc tới trang 10. Generator ở iter_table_regions() không
    cứu được phần đó, vì toàn bộ chi phí đã phát sinh TRƯỚC lần yield
    đầu tiên.
    """
    path = Path(file_path)
    if path.suffix.lower() != ".pdf":
        return Image.open(path)

    _require_pdf2image()

    images = convert_from_path(
        str(path),
        dpi=PDF_DPI,
        poppler_path=os.getenv("POPPLER_PATH"),
        first_page=page_no,
        last_page=page_no,
    )
    return images[0]


def get_reader():
    """
    Khởi tạo EasyOCR ở lần gọi đầu tiên rồi tái sử dụng.

    Trước đây reader được tạo ngay lúc import. Vì extract_vlm.py cũng
    import module này (để dùng load_page/iter_table_regions), chạy nhánh
    VLM thuần vẫn phải chờ nạp xong model OCR không dùng tới.
    """
    global _reader
    if _reader is None:
        import easyocr

        _reader = easyocr.Reader(LANGUAGES)
    return _reader


def iter_table_regions(file_path: str, metrics=None) -> Iterator[dict]:
    """
    Generator: convert + layout detection cho TỪNG trang, yield từng trang một:
        {"page": 1, "regions": [TableRegion, ...]}

    regions mang TableRegion chứ không mang ảnh trần: bbox phải đi kèm
    tới tận bước gộp kết quả, vì đó là thứ cho phép cắt lại đúng vùng để
    ĐỌC LẠI. Chuỗi này đứt ở bất kỳ mắt nào thì đóng góp cốt lõi của cả
    nghiên cứu biến mất.

    Mỗi trang trả về các vùng bảng tìm được; nếu không tìm thấy bảng nào
    thì trả về nguyên trang gốc (fail open — để không mất dữ liệu ở trang
    mà YOLO nhận nhầm là plain text).

    Lười ở CẢ HAI khâu đắt tiền: cả convert PDF lẫn YOLO chỉ chạy cho
    trang nào thực sự được duyệt tới. Đo trên báo cáo VNM 55 trang, dừng
    ở trang 10 nghĩa là 45 trang còn lại không tốn gì.
    """
    total = count_pages(file_path)

    for i in range(1, total + 1):
        with timer(metrics, "pdf_convert"):
            page_img = load_page(file_path, i)

        with timer(metrics, "layout"):
            regions = get_table_regions(page_img)

        if not regions:
            print(f"--- Page {i}/{total}: không có bảng, dùng nguyên trang ---")
            yield {"page": i, "regions": [ca_trang(page_img)]}
            continue

        print(f"--- Page {i}/{total}: tìm thấy {len(regions)} bảng ---")
        yield {"page": i, "regions": regions}


def ocr_image_chi_tiet(image: Image.Image) -> list[tuple[str, tuple[int, int, int, int]]]:
    """
    OCR một ảnh, trả về [(chữ đọc được, bbox trong ảnh ĐÓ)].

    VÌ SAO PHẢI CÓ HÀM NÀY. `readtext(detail=0)` bảo EasyOCR chỉ trả chữ, bỏ
    toạ độ — mà toạ độ thì nó ĐÃ tính rồi, vì phải khoanh được ô mới đọc được
    chữ trong ô. Vứt chúng đi ngay tại cửa nghĩa là công đã trả mà không nhận
    hàng, và bước đọc lại tài liệu sau đó không còn gì để tra: nó biết ô nào
    sai nhưng không biết trên giấy chỗ đó ghi số mấy.

    EasyOCR trả bbox dạng bốn ĐỈNH (để đỡ được ô nghiêng). Ở đây quy về hình
    chữ nhật thẳng trục, vì mọi thứ hạ nguồn — Provenance, cắt lại vùng ảnh,
    phép đo chồng lấn — đều nói bằng (x1, y1, x2, y2).
    """
    ket_qua = get_reader().readtext(np.array(image), detail=1)

    o = []
    for da_giac, chu, _conf in ket_qua:
        xs = [int(diem[0]) for diem in da_giac]
        ys = [int(diem[1]) for diem in da_giac]
        o.append((chu, (min(xs), min(ys), max(xs), max(ys))))
    return o


def ocr_image(image: Image.Image) -> str:
    return "\n".join(chu for chu, _ in ocr_image_chi_tiet(image))


# Một Ô GIÁ TRỊ trên báo cáo tài chính Việt Nam luôn có dấu phân cách nghìn:
# 1.234.567, hoặc (1.234) khi âm. Mẫu này đòi đúng cấu trúc đó.
#
# VÌ SAO PHẢI LỌC BẰNG CẤU TRÚC chứ không dùng thẳng parse_number(). Hàm ấy
# cố ý dễ dãi — nó chạy SAU khi regex đã định vị được con số trên một dòng,
# nên chỉ cần vét chữ số là đủ. Đem nó lọc ô thì nó nuốt luôn hai cột mà
# chính prompt của VLM đang phải dặn tránh: cột Mã số (01 -> 1, 10 -> 10) và
# cột Thuyết minh (26.1 -> 261, V.5 -> 5), cộng thêm số trang và năm.
#
# Những con số rác ấy nguy hiểm hơn vẻ ngoài của chúng: chúng vào thẳng tập
# ứng viên sửa lỗi, chiếm chỗ của ô thật trong trần MAX_MOI_NGUON, và mỗi
# con số thừa lại thêm một cơ hội để tổ hợp nào đó TÌNH CỜ làm bảng cân.
#
# Cái giá đã biết: ô giá trị nhỏ viết không có dấu phân cách (0, hay 5) bị
# bỏ qua. Chấp nhận được — ở thang đồng thì chúng hiếm, và một ứng viên 0
# gần như không bao giờ là phép sửa đúng.
MAU_O_GIA_TRI = re.compile(r"^[(\-\u2013\u2014]?\s*\d{1,3}(?:\.\d{3})+\s*\)?$")


def o_trong_vung(region, chi_tiet: list) -> list[tuple[str, tuple[int, int, int, int]]]:
    """
    Mọi ô của một vùng, toạ độ đã dời về hệ của TRANG.

    Dời toạ độ ngay tại đây chứ không để người gọi tự cộng: `region.bbox` là
    toạ độ vùng trên trang, còn bbox EasyOCR trả về là toạ độ trong ảnh vùng
    ĐÃ CẮT. Trộn hai hệ là loại lỗi không làm gì nổ — nó chỉ khiến bước đọc
    lại nhìn sang một ô khác rồi trả về một con số hoàn toàn hợp lệ của ô đó.

    Giữ cả ô CHỮ chứ không chỉ ô số, vì hai người dùng cần chúng: bước neo
    toạ độ chỉ tiêu dò theo ô MÃ SỐ khi không khớp được giá trị, và bước lan
    ký hiệu mẫu đọc chuỗi "B01a-DN/HN" nằm phía trên bảng.
    """
    goc_x, goc_y = region.bbox[0], region.bbox[1]
    return [
        (chu, (x1 + goc_x, y1 + goc_y, x2 + goc_x, y2 + goc_y))
        for chu, (x1, y1, x2, y2) in chi_tiet
    ]


def loc_o_so(o: list) -> list[tuple[int, tuple[int, int, int, int]]]:
    """
    Lọc lấy các ô GIÁ TRỊ trong danh sách ô đã dời toạ độ.

    Chỉ nhận ô khớp `MAU_O_GIA_TRI` — xem ghi chú ở hằng số đó.
    """
    o_so = []
    for chu, bbox in o:
        if not MAU_O_GIA_TRI.match(chu.strip()):
            continue   # ô chữ, mã số, thuyết minh, số trang — không phải giá trị
        try:
            o_so.append((parse_number(chu), bbox))
        except ValueError:
            continue
    return o_so


def o_so_trong_vung(region, chi_tiet: list) -> list[tuple[int, tuple[int, int, int, int]]]:
    """Các ô GIÁ TRỊ của một vùng, toạ độ theo hệ của TRANG."""
    return loc_o_so(o_trong_vung(region, chi_tiet))


def ocr_page_regions(page: dict) -> dict:
    """
    OCR các vùng bảng của MỘT trang.

    Nhận {"page": 1, "regions": [TableRegion, ...]}, trả
    {"page": 1, "text": "...", "vung": [{"region_index", "text", "o", "o_so"}]}.

    Tách ra khỏi ocr_regions() để router.py gọi được theo từng trang khi
    duyệt generator, thay vì phải gom hết mọi trang lại rồi mới OCR.

    KẾT QUẢ CHIA THEO VÙNG, KHÔNG GỘP CẢ TRANG. Một trang có thể mang nhiều
    bảng, và ô của bảng khác không phải "lân cận" theo bất kỳ nghĩa nào —
    lấy nó làm ứng viên sửa lỗi là mở đường cho đúng kiểu lỗi nhầm cột đã
    thấy ở `SBT_2025Q2_TT200`: một con số hợp lệ của bảng khác thì vẫn hợp
    lệ, và không đẳng thức nào bắt được. Khoá `text` gộp cả trang vẫn giữ vì
    probe dò mã số dòng làm việc trên toàn trang.

    Mọi thứ ở đây đến từ ĐÚNG MỘT lượt OCR, mà OCR là khâu đắt nhất còn lại
    sau khi convert PDF và YOLO đã được cache.
    """
    vung = []
    for region_index, region in enumerate(page["regions"]):
        chi_tiet = ocr_image_chi_tiet(region.image)
        o = o_trong_vung(region, chi_tiet)
        vung.append(
            {
                "region_index": region_index,
                "text": "\n".join(chu for chu, _ in chi_tiet),
                "o": o,
                "o_so": loc_o_so(o),
            }
        )

    text = "\n".join(v["text"] for v in vung)
    tong_o_so = sum(len(v["o_so"]) for v in vung)
    print(f"--- OCR page {page['page']}: {len(text)} ký tự, {tong_o_so} ô số ---")
    return {"page": page["page"], "text": text, "vung": vung}


def ocr_regions(pages: Iterable[dict]) -> list[dict]:
    """
    OCR nhiều trang đã cắt sẵn bởi iter_table_regions().
    Format: [{"page": 1, "text": "...", "vung": [...]}, ...]
    """
    return [ocr_page_regions(page) for page in pages]


def ocr_document(file_path: str) -> list[dict]:
    """
    Run layout detection + OCR on the whole document, return results per page.
    Format: [{"page": 1, "text": "...", "vung": [...]}, ...]
    """
    return ocr_regions(iter_table_regions(file_path))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ocr_baseline.py <file_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output = ocr_document(input_path)

    out_path = Path("data/output") / (Path(input_path).stem + "_raw.txt")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        for page in output:
            f.write(f"===== PAGE {page['page']} =====\n")
            f.write(page["text"])
            f.write("\n\n")

    print(f"\nOCR result saved to: {out_path}")
