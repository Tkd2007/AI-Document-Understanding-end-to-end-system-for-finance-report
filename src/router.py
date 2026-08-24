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
from extraction_types import ExtractionResult, FieldResult
from fields_config import DEFAULT_STANDARD, UNIT_KEY, Standard, empty_result
from metrics import RunMetrics, merge_into_totals, thong_tin_tai_lap, timer
from ocr_baseline import iter_table_regions, ocr_page_regions
from validation import has_required_fields, validate_result

load_dotenv()

def _co_bat(ten_bien: str, mac_dinh: str = "false") -> bool:
    """Đọc một cờ bật/tắt từ biến môi trường."""
    return os.getenv(ten_bien, mac_dinh).strip().lower() in {"1", "true", "yes"}


# Bật lại nhánh OCR bằng USE_OCR_FIRST=true trong .env
USE_OCR_FIRST = _co_bat("USE_OCR_FIRST")

# Tắt HOÀN TOÀN cổng ràng buộc. CHỈ DÙNG KHI ĐO, không dùng khi phục vụ.
#
# Vì sao cờ này phải tồn tại: H1 so "vi phạm ràng buộc" với "confidence của
# model" như hai bộ dự báo lỗi. Nhưng pipeline hiện ĐÃ dùng chính đẳng thức
# kế toán làm cổng quyết định fallback — is_acceptable() gọi
# validate_result(), và khi có warning thì run_vlm() cho VLM ghi đè. Nghĩa
# là đầu ra đã được chính tín hiệu ấy làm sạch.
#
# Đo AUROC của vi phạm ràng buộc trên dữ liệu đó là VÒNG LẶP LUẬN CHỨNG:
# ta đang đánh giá một tín hiệu trên tập đã bị chính nó lọc, và con số thu
# được không nói lên điều gì về khả năng dự báo thật. Bật cờ này cho ta
# nhánh đối chứng: đầu ra thô, chưa từng thấy ràng buộc.
#
# Đây là mục rẻ nhất trong cả kế hoạch thi công, và bỏ qua nó thì toàn bộ
# kết quả H1 vô giá trị bất kể phần còn lại làm tốt tới đâu.
DISABLE_CONSTRAINT_GATE = _co_bat("DISABLE_CONSTRAINT_GATE")

# Khoá tạm để nhánh VLM chuyển meta của nó ra tới route_document, tách khỏi
# các khoá dùng cho thong_tin_tai_lap(). Đặt tên thành hằng số thay vì viết
# chuỗi tay ở hai nơi, vì quên đồng bộ một trong hai chỗ sẽ làm early_stop
# lặng lẽ biến mất lần nữa — đúng lỗi vừa sửa.
META_VLM = "_meta_vlm"


def chon_chuan(standard: Standard | None) -> tuple[Standard, str]:
    """
    Chốt chuẩn mẫu biểu cho cả lượt chạy, kèm NGUỒN của kết luận đó.

    Trả về (chuẩn, nguồn) với nguồn thuộc tập đóng:
      "tham_so"  — người gọi chỉ định thẳng, khỏi phải đoán.
      "mac_dinh" — không ai chỉ định và đường chạy này chưa dò được, nên
                   lùi về DEFAULT_STANDARD.

    VÌ SAO PHẢI TRẢ CẢ NGUỒN chứ không chỉ trả chuẩn: hai lượt chạy có cùng
    `standard` nhưng một cái do người chỉ định còn một cái do lùi về mặc
    định là hai thứ khác hẳn nhau về độ tin cậy, và bảng kết quả phải tách
    được chúng. Nếu chỉ ghi chuẩn thì một lượt lùi mặc định trông y hệt một
    lượt nhận diện chắc chắn, và chế độ lỗi "nhận diện sai chuẩn" biến mất
    khỏi mọi phép đo — đúng thứ mà detect_standard() cố ý không đoán bừa để
    giữ lại.

    CHƯA CÓ NGUỒN "nhan_dien" Ở ĐÂY, và đó là hiện trạng chứ không phải ý
    đồ. detect_standard() cần text của trang, mà đường VLM (USE_OCR_FIRST
    tắt, tức cấu hình mặc định) không sinh ra text nào. Bước dò sự tồn tại
    của dòng sẽ mang OCR tới đường đó, và khi có thì thêm nguồn thứ ba vào
    đây.
    """
    if standard is not None:
        return standard, "tham_so"

    print(
        f"[STANDARD] Không ai chỉ định chuẩn và đường chạy này chưa dò được — "
        f"lùi về {DEFAULT_STANDARD.value}. Kết quả có thể dùng sai bảng mã số "
        f"dòng và sai bộ đẳng thức."
    )
    return DEFAULT_STANDARD, "mac_dinh"


def khung_rong(standard: Standard) -> dict[str, FieldResult]:
    """
    Khung tích luỹ của router: mỗi chỉ tiêu một FieldResult chưa có gì.

    Router tích luỹ FieldResult chứ không tích luỹ giá trị trần, vì
    confidence và về sau là provenance phải sống sót qua bước merge. Trước
    đây merge trả về giá trị trần nên mọi thứ biết được về độ tin cậy của
    một con số đều bị vứt ngay tại đây.
    """
    return {khoa: FieldResult(value=None, confidence=0.0) for khoa in empty_result(standard)}


def gia_tri_tran(tich_luy: dict[str, FieldResult]) -> dict:
    """
    Chỉ giá trị, cho validate_result() và is_acceptable() — hai hàm cố ý
    không biết gì về confidence.
    """
    return {khoa: ket_qua.value for khoa, ket_qua in tich_luy.items()}


def _lap_cho_trong(tich_luy: dict[str, FieldResult], nguon: dict[str, FieldResult]) -> bool:
    """
    Lấp các chỉ tiêu còn trống, không ghi đè giá trị đã tìm được.
    Trả về True nếu có lấp được ít nhất một chỗ.
    """
    co_field_moi = False
    for khoa in tich_luy:
        if tich_luy[khoa].value is None and nguon.get(khoa) is not None:
            tich_luy[khoa] = nguon[khoa]
            co_field_moi = True
    return co_field_moi


def _ghi_lai_luot_vlm(ghi_lai, extraction: ExtractionResult) -> None:
    """
    Bồi thông tin tái lập của lượt gọi VLM vào dict do người gọi đưa.

    Bồi tại chỗ thay vì đổi kiểu trả về, cùng cách cached_pages vẫn làm:
    hai nhánh run_vlm và run_unconstrained đều trả về accumulator, và
    đổi cả hai sang trả tuple sẽ làm nơi gọi phải phân biệt hai dạng kết
    quả chỉ để lấy vài trường metadata.
    """
    if ghi_lai is None:
        return

    ghi_lai.update(
        model=extraction.model,
        temperature=extraction.temperature,
        n_samples=extraction.n_samples,
        prompt_hash=extraction.meta.get("prompt_hash"),
        standard=extraction.meta.get("standard"),
    )

    # early_stop đi theo đường RIÊNG, dưới khoá META_VLM, vì nó không phải
    # thông tin tái lập mà là thông tin về việc lượt chạy đã CẮT BỚT những
    # gì. thong_tin_tai_lap() có chữ ký cố định nên nhét thẳng vào sẽ nổ;
    # route_document() lấy nó ra khỏi dict trước khi gọi hàm đó.
    #
    # Vì sao phải mang ra tận đây: extract_fields_from_regions() ghi
    # meta["early_stop"] đúng như docstring của nó hứa, nhưng route_document
    # trước đây gán meta = meta của validate_result(), tức ĐÈ mất. Nên trên
    # đường chạy thật — API và CLI — không ai thấy được lượt chạy đã dừng ở
    # trang nào và còn thiếu field gì, đúng thứ mà cờ dừng sớm sinh ra để
    # không giấu.
    ghi_lai[META_VLM] = {"early_stop": extraction.meta.get("early_stop")}


def _tu_extraction(extraction: ExtractionResult) -> dict[str, FieldResult]:
    """
    Đưa ExtractionResult về dạng phẳng mà router merge được.

    Đơn vị tính nằm ở meta của ExtractionResult nhưng phải quay lại thành
    một khoá phẳng ở đây, vì validate_result() đọc nó từ chính dict giá
    trị — nó cần đơn vị TRƯỚC khi quy đổi bất cứ con số nào.
    """
    phang = dict(extraction.data)

    don_vi = extraction.meta.get(UNIT_KEY)
    if don_vi is not None:
        phang[UNIT_KEY] = FieldResult.khong_do(don_vi)

    return phang


def _ocr_mot_trang(page, metrics=None) -> dict[str, FieldResult]:
    """
    OCR một trang rồi trích bằng regex, trả về dạng FieldResult.

    Nhánh OCR không đo được confidence nên mọi giá trị đi ra với
    confidence 1.0 theo nghĩa "không đo được" — xem FieldResult.khong_do().
    """
    with timer(metrics, "ocr"):
        ocr_result = ocr_page_regions(page)

    return {
        khoa: FieldResult.khong_do(gia_tri)
        for khoa, gia_tri in extract_all_fields(ocr_result["text"]).items()
        if gia_tri is not None
    }


def run_ocr_first(
    pages_iter, cached_pages: list, result: dict, standard: Standard, metrics=None
) -> dict:
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
        _lap_cho_trong(result, _ocr_mot_trang(page, metrics))

        if is_acceptable(gia_tri_tran(result), standard):
            print(f"--- OCR đã đủ và hợp lệ, dừng ở trang {page['page']} ---")
            break

    return result


def _remaining_pages(pages_iter, cached_pages: list):
    """
    Trang đã đọc ở nhánh OCR thì dùng lại, phần chưa duyệt thì đọc tiếp từ
    generator — không convert PDF hay chạy YOLO lần nữa.
    """
    yield from cached_pages
    for page in pages_iter:
        cached_pages.append(page)
        yield page


def run_unconstrained(
    pages_iter, cached_pages: list, result: dict, standard: Standard, metrics=None, ghi_lai=None
) -> dict:
    """
    Chạy ĐÚNG MỘT nhánh, không cổng ràng buộc, không fallback.

    Nhánh nào là do USE_OCR_FIRST quyết định. Điểm khác biệt với đường
    thường không phải ở việc bỏ fallback, mà ở chỗ KHÔNG một quyết định
    nào trong đường đi này đọc kết quả của validate_result(). Đầu ra vì
    vậy chưa từng bị ràng buộc kế toán chạm vào, và đó là điều kiện để
    con số AUROC ở H1 có nghĩa.

    Kể cả điều kiện dừng sớm của run_ocr_first() cũng phải bỏ: nó gọi
    is_acceptable(), nên nó quyết định đọc tới trang nào dựa trên chính
    tín hiệu đang được đem đi đánh giá.

    KHÔNG bỏ điều kiện dừng sớm theo PATIENCE_PAGES bên trong nhánh VLM:
    cái đó dựa trên "đã đủ field bắt buộc chưa", tức là tính đầy đủ chứ
    không phải tính hợp lệ theo ràng buộc. Nó là một nguồn thiên lệch
    khác và được xử lý riêng trong danh mục dọn dẹp.
    """
    if USE_OCR_FIRST:
        for page in pages_iter:
            cached_pages.append(page)
            _lap_cho_trong(result, _ocr_mot_trang(page, metrics))

        return result

    extraction = extract_fields_from_regions(
        _remaining_pages(pages_iter, cached_pages), metrics, standard
    )
    _ghi_lai_luot_vlm(ghi_lai, extraction)
    _lap_cho_trong(result, _tu_extraction(extraction))

    return result


def run_vlm(
    pages_iter, cached_pages: list, result: dict, standard: Standard, metrics=None, ghi_lai=None
) -> dict:
    """
    Chạy nhánh VLM và trộn kết quả vào result.

    Hai lý do khiến kết quả trước đó không đáng tin, xử lý khác nhau:
      1. Field còn None       -> VLM lấp chỗ trống.
      2. Validate báo warning -> giá trị đang có tồn tại nhưng SAI, nên
         phải cho VLM ghi đè. Nếu chỉ lấp chỗ None, con số sai vẫn nằm
         nguyên đó và cả validation gate thành vô nghĩa: tốn tiền gọi VLM
         rồi vứt kết quả đúng đi.
    """
    has_warnings = bool(validate_result(gia_tri_tran(result), standard)["warnings"])

    extraction = extract_fields_from_regions(
        _remaining_pages(pages_iter, cached_pages), metrics, standard
    )
    _ghi_lai_luot_vlm(ghi_lai, extraction)
    tu_vlm = _tu_extraction(extraction)

    for key in result:
        moi = tu_vlm.get(key)
        if moi is None or moi.value is None:
            continue
        if result[key].value is None or has_warnings:
            result[key] = moi

    return result


def route_document(
    file_path: str, save: bool = True, standard: Standard | None = None
) -> ExtractionResult:
    """
    Chạy trọn pipeline cho một tài liệu.

    Trả về ExtractionResult chứ không phải dict giá trị trần: confidence
    của từng chỉ tiêu là đầu vào bắt buộc của H1 và H2, còn các giá trị
    THUA phiếu là tập ứng viên sửa lỗi. Trả về dict trần đồng nghĩa với
    việc vứt cả hai ngay tại cửa ra, rồi phải gọi lại VLM để có lại.

    Giá trị trong .data đã ÉP KIỂU SỐ và QUY ĐỔI VỀ ĐỒNG, còn .warnings
    gộp cả cảnh báo của bước bỏ phiếu lẫn cảnh báo của validate_result().

    save — có ghi data/output/<stem>_routed.json hay không.

    Đường CLI để mặc định True vì file đó CHÍNH LÀ output của lệnh.
    Đường API truyền False: client đã nhận dữ liệu qua HTTP và
    metrics.jsonl đã ghi lại lượt chạy, nên file kia là bản sao không ai
    đọc. Tên nó còn mang hậu tố ngẫu nhiên của request
    (report_a3f2b1c9_routed.json) nên cũng không tra cứu bằng tay được —
    chỉ để lại rác trong data/output/, mỗi request một file, không ai dọn.
    """
    # Nhánh VLM luôn có thể được gọi làm fallback, kể cả khi USE_OCR_FIRST
    # bật, nên thiếu config là hỏng chắc chắn. Kiểm ngay đây — trước cả
    # RunMetrics — để không ghi lại một "lượt chạy" vốn chưa từng bắt đầu,
    # và để lỗi nổ ra trước khi tốn công convert PDF + chạy YOLO.
    require_config()

    # Chốt chuẩn MỘT lần cho cả lượt chạy, trước khi đụng tới trang nào.
    # Prompt VLM, bảng mã số dòng, bộ đẳng thức và câu cảnh báo đều phải
    # nói về cùng một chuẩn; để mỗi nơi tự quyết là cách chắc chắn nhất để
    # chúng lệch nhau mà không ai thấy.
    standard, nguon_chuan = chon_chuan(standard)

    metrics = RunMetrics(file_path)

    try:
        pages_iter = iter_table_regions(file_path, metrics)
        cached_pages: list = []
        result = khung_rong(standard)
        thong_tin_vlm: dict = {}

        if DISABLE_CONSTRAINT_GATE:
            print("--- CỔNG RÀNG BUỘC ĐANG TẮT: chế độ ĐO, không dùng để phục vụ ---")
            result = run_unconstrained(
                pages_iter, cached_pages, result, standard, metrics, thong_tin_vlm
            )
        else:
            if USE_OCR_FIRST:
                result = run_ocr_first(pages_iter, cached_pages, result, standard, metrics)

            if not is_acceptable(gia_tri_tran(result), standard):
                if USE_OCR_FIRST:
                    missing = [k for k, kq in result.items() if kq.value is None]
                    print(f"--- OCR chưa đạt (thiếu/nghi ngờ: {missing}), chuyển sang VLM ---")
                result = run_vlm(pages_iter, cached_pages, result, standard, metrics, thong_tin_vlm)

        # Ép kiểu số TRƯỚC khi lưu và trả về. VLM đôi khi trả số dưới dạng
        # chuỗi, nên nếu lưu thẳng result thô thì file _routed.json và
        # response HTTP sẽ khác nhau về kiểu dữ liệu cho cùng một lượt
        # chạy — rất khó lần khi đi đối chiếu.
        da_kiem = validate_result(gia_tri_tran(result), standard)
        data = da_kiem["data"]

        # Ghi giá trị đã ép kiểu và quy đổi NGƯỢC vào FieldResult, giữ
        # nguyên confidence và votes. Nếu bỏ qua bước này thì .values() trả
        # về số thô chưa quy đổi trong khi .data lại nói đã quy đổi — hai
        # nguồn sự thật lệch nhau trong cùng một object.
        ket_qua_cuoi = {
            khoa: FieldResult(
                value=data.get(khoa),
                confidence=result[khoa].confidence,
                votes=result[khoa].votes,
                provenance=result[khoa].provenance,
            )
            for khoa in result
            if khoa != UNIT_KEY
        }

        # Lấy meta của nhánh VLM ra TRƯỚC khi thong_tin_tai_lap() nhận dict
        # này — hàm đó có chữ ký cố định nên khoá lạ sẽ làm nó nổ.
        meta_vlm = thong_tin_vlm.pop(META_VLM, {})

        # HỢP NHẤT meta, không đè. Bản trước gán thẳng meta = da_kiem["meta"]
        # nên mọi thứ nhánh trích xuất biết mà validate_result không biết —
        # early_stop và prompt_hash — bị vứt ngay tại cửa ra.
        #
        # standard và nguon_chuan ghi thành HAI khoá riêng: biết chuẩn nào
        # được dùng là chưa đủ, còn phải biết kết luận đó đến từ đâu. Một
        # lượt lùi về mặc định và một lượt do người chỉ định cho ra cùng chữ
        # "TT99", và gộp chúng lại là xoá mất một chế độ lỗi khỏi phép đo.
        extraction = ExtractionResult(
            data=ket_qua_cuoi,
            meta={
                **meta_vlm,
                **da_kiem["meta"],
                "standard_nguon": nguon_chuan,
            },
            warnings=da_kiem["warnings"],
        )

        if save:
            save_result(file_path, data)

        # constraint_gate ghi thành khoá TƯỜNG MINH trong metrics: một lượt
        # chạy ở chế độ đo và một lượt chạy phục vụ cho ra dữ liệu không so
        # được với nhau, nên người đọc metrics.jsonl phải phân biệt được hai
        # loại đó bằng một khoá có sẵn chứ không phải suy đoán.
        metrics.set_info(
            pages_processed=len(cached_pages),
            ocr_first=USE_OCR_FIRST,
            constraint_gate=not DISABLE_CONSTRAINT_GATE,
            **thong_tin_tai_lap(**thong_tin_vlm),
        )
        metrics.status = "ok"
        return extraction

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


def is_acceptable(result: dict, standard: Standard) -> bool:
    """
    Kết quả có đáng tin để dừng sớm / khỏi cần fallback VLM không?

    standard bắt buộc vì điều kiện 2 gọi validate_result(), và bộ đẳng thức
    khác nhau giữa hai chuẩn kể từ Mốc 1. Cổng này quyết định có gọi VLM hay
    không, nên kiểm bằng đẳng thức của nhầm chuẩn sẽ vừa bỏ sót lỗi thật vừa
    gọi VLM cho những ca vốn đã đúng.

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

    return not validate_result(result, standard)["warnings"]


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

    # Console Windows mặc định cp1252 nên in tiếng Việt sẽ nổ.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print(f"--- Nhánh OCR: {'BẬT' if USE_OCR_FIRST else 'TẮT'} (USE_OCR_FIRST) ---")
    print(
        f"--- Cổng ràng buộc: {'TẮT (chế độ ĐO)' if DISABLE_CONSTRAINT_GATE else 'BẬT'} "
        f"(DISABLE_CONSTRAINT_GATE) ---"
    )

    input_path = sys.argv[1]
    ket_qua = route_document(input_path)

    print(json.dumps(ket_qua.values(), ensure_ascii=False, indent=2))
    if ket_qua.warnings:
        print("\nCảnh báo:")
        for canh_bao in ket_qua.warnings:
            print(f"  - {canh_bao}")
