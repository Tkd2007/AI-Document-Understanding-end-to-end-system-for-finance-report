"""
Document Classifier & Router

Điều phối giữa OCR Pipeline (rẻ, nhanh) và VLM Pipeline (đắt, chậm hơn
nhưng đáng tin hơn).

TRẠNG THÁI HIỆN TẠI: nhánh OCR đang TẮT mặc định (USE_OCR_FIRST=false).

Lý do tắt — đo trên báo cáo VNM Q1/2026:
  * EasyOCR đọc số rất chuẩn nhưng đọc chữ tiếng Việt có dấu thì hỏng
    ("TỔNG TÀI SẢN" -> "TỖNG TÀISẢN"), trong khi regex lại phải khớp
    đúng tên chỉ tiêu để tìm được dòng.
  * Hệ quả: nhánh OCR quét hết 55 trang (chậm, EasyOCR chạy CPU) rồi vẫn
    thiếu field, sau đó mới gọi VLM — tức người dùng phải chờ trọn một
    nhánh vô ích trước khi nhận kết quả.
  * Nhánh VLM một mình trả đúng cả 11/11 field và dừng ở trang 10.

Code nhánh OCR được GIỮ NGUYÊN, không xoá: bật lại bằng một dòng trong
.env khi regex đủ tin cậy (hướng đang làm dở là dò theo mã số dòng thay
vì theo tên chỉ tiêu — xem extract_baseline.extract_field_by_code).
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from extract_baseline import extract_all_fields
from extract_vlm import extract_fields_from_regions, require_config
from fields_config import empty_result
from metrics import RunMetrics, merge_into_totals, timer
from ocr_baseline import iter_table_regions, ocr_page_regions
from validation import has_required_fields, validate_result

load_dotenv()

# Bật lại nhánh OCR bằng USE_OCR_FIRST=true trong .env
USE_OCR_FIRST = os.getenv("USE_OCR_FIRST", "false").strip().lower() in {"1", "true", "yes"}


def run_ocr_first(pages_iter, cached_pages: list, result: dict, metrics=None) -> dict:
    """
    Quét OCR theo từng trang, merge dần, dừng khi kết quả đã đáng tin.

    Nhận generator chứ không nhận list: YOLO chỉ chạy cho trang nào thực
    sự được duyệt tới, nên dừng sớm ở trang 10 nghĩa là 45 trang còn lại
    không hề bị xử lý.

    cached_pages được bồi vào tại chỗ để nhánh VLM dùng lại kết quả YOLO,
    khỏi phải convert PDF và chạy detect lần hai.
    """
    for page in pages_iter:
        cached_pages.append(page)

        with timer(metrics, "ocr"):
            ocr_result = ocr_page_regions(page)
        page_fields = extract_all_fields(ocr_result["text"])

        # Chỉ lấp field còn trống, không ghi đè giá trị đã tìm được
        for key in result:
            if result[key] is None and page_fields.get(key) is not None:
                result[key] = page_fields[key]

        if is_acceptable(result):
            print(f"--- OCR đã đủ và hợp lệ, dừng ở trang {page['page']} ---")
            break

    return result


def run_vlm(pages_iter, cached_pages: list, result: dict, metrics=None) -> dict:
    """
    Chạy nhánh VLM và trộn kết quả vào result.

    Hai lý do khiến kết quả trước đó không đáng tin, xử lý khác nhau:
      1. Field còn None       -> VLM lấp chỗ trống.
      2. Validate báo warning -> giá trị đang có tồn tại nhưng SAI, nên
         phải cho VLM ghi đè. Nếu chỉ lấp chỗ None, con số sai vẫn nằm
         nguyên đó và cả validation gate thành vô nghĩa: tốn tiền gọi VLM
         rồi vứt kết quả đúng đi.
    """
    has_warnings = bool(validate_result(result)["warnings"])

    # Trang đã đọc ở nhánh OCR thì dùng lại, phần chưa duyệt thì đọc tiếp
    # từ generator — không convert PDF hay chạy YOLO lần nữa.
    def remaining_pages():
        yield from cached_pages
        for page in pages_iter:
            cached_pages.append(page)
            yield page

    vlm_result = extract_fields_from_regions(remaining_pages(), metrics)

    for key in result:
        if vlm_result.get(key) is None:
            continue
        if result[key] is None or has_warnings:
            result[key] = vlm_result[key]

    return result


def route_document(file_path: str, save: bool = True) -> dict:
    """
    Chạy trọn pipeline cho một tài liệu, trả về dict đã ép kiểu số.

    save — có ghi data/output/<stem>_routed.json hay không.

    Đường CLI để mặc định True vì file đó CHÍNH LÀ output của lệnh.
    Đường API SẼ truyền False, nhưng hiện api.py vẫn tạm truyền True để
    debug. Lý do đích đến là False: client đã nhận dữ liệu qua HTTP và
    metrics.jsonl đã ghi lại lượt chạy, nên file kia là bản sao không ai
    đọc. Tên nó còn mang hậu tố ngẫu nhiên của request
    (report_a3f2b1c9_routed.json) nên cũng không tra cứu bằng tay được —
    chỉ để lại rác trong data/output/, mỗi request một file, không ai dọn.
    Chi tiết trạng thái tạm này: mục "Kết quả upload qua API được ghi ra
    file (trạng thái debug hiện tại)" trong README.
    """
    # Nhánh VLM luôn có thể được gọi làm fallback, kể cả khi USE_OCR_FIRST
    # bật, nên thiếu config là hỏng chắc chắn. Kiểm ngay đây — trước cả
    # RunMetrics — để không ghi lại một "lượt chạy" vốn chưa từng bắt đầu,
    # và để lỗi nổ ra trước khi tốn công convert PDF + chạy YOLO.
    require_config()

    metrics = RunMetrics(file_path)

    try:
        pages_iter = iter_table_regions(file_path, metrics)
        cached_pages: list = []
        result = empty_result()

        if USE_OCR_FIRST:
            result = run_ocr_first(pages_iter, cached_pages, result, metrics)

        if not is_acceptable(result):
            if USE_OCR_FIRST:
                missing = [key for key, value in result.items() if value is None]
                print(f"--- OCR chưa đạt (thiếu/nghi ngờ: {missing}), chuyển sang VLM ---")
            result = run_vlm(pages_iter, cached_pages, result, metrics)

        # Ép kiểu số TRƯỚC khi lưu và trả về. VLM đôi khi trả số dưới dạng
        # chuỗi, nên nếu lưu thẳng result thô thì file _routed.json và
        # response HTTP (api.py có chạy validate_result) sẽ khác nhau về kiểu
        # dữ liệu cho cùng một lượt chạy — rất khó lần khi đi đối chiếu.
        data = validate_result(result)["data"]

        if save:
            save_result(file_path, data)

        metrics.set_info(pages_processed=len(cached_pages), ocr_first=USE_OCR_FIRST)
        metrics.status = "ok"
        return data

    except BaseException:
        # Bắt cả KeyboardInterrupt/SystemExit: lượt chạy không đi hết
        # pipeline thì dòng metrics của nó không được trông như bình
        # thường. Đánh dấu ở đây rồi raise lại — không nuốt lỗi.
        metrics.status = "error"
        raise

    finally:
        metrics.save()
        merge_into_totals(metrics)
        print(metrics.summary())


def is_acceptable(result: dict) -> bool:
    """
    Kết quả có đáng tin để dừng sớm / khỏi cần fallback VLM không?

    Hai điều kiện, cả hai đều phải đạt:
    1. Đủ các field BẮT BUỘC (theo FIELD_RULES). Field bổ sung thiếu vẫn
       chấp nhận được — danh sách chỉ tiêu càng dài thì càng dễ thiếu một
       chỉ tiêu phụ, và nếu bắt đủ hết mới cho qua thì lần nào cũng phải
       fallback sang VLM.
    2. Validate không sinh warning. Chỉ kiểm tra "có giá trị" là chưa đủ,
       vì regex có thể bắt trúng một con số SAI (không phải None) và
       router sẽ tin dùng luôn mà không bao giờ gọi VLM.
    """
    if not has_required_fields(result):
        return False

    return not validate_result(result)["warnings"]


def save_result(file_path: str, result: dict) -> Path:
    out_path = Path("data/output") / (Path(file_path).stem + "_routed.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python router.py <file_path>")
        sys.exit(1)

    print(f"--- Nhánh OCR: {'BẬT' if USE_OCR_FIRST else 'TẮT'} (USE_OCR_FIRST) ---")

    input_path = sys.argv[1]
    result = route_document(input_path)

    print(json.dumps(result, ensure_ascii=False, indent=2))
