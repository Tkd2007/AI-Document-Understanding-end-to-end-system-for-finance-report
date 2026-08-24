"""
Pipeline step 2: Raw Text -> Structured JSON (Extraction baseline)

Rule-based / regex extraction of key financial line items from
OCR raw text. This is the baseline to compare against a VLM-based
approach later.

Hai chiến lược tìm, thử theo thứ tự:
  1. Theo TÊN chỉ tiêu (FIELD_ALIASES) — khớp được thì cho kết quả sát
     nhất, nhưng phải kèm luật loại trừ. Tên chỉ tiêu KHÔNG duy nhất
     trong tài liệu: một alias ngắn có thể nằm gọn ở đầu ("Lợi nhuận sau
     thuế" trong "...chưa phân phối") hoặc ở ĐUÔI ("Hàng tồn kho" trong
     "Dự phòng giảm giá hàng tồn kho") của một nhãn khác hẳn. Vì vậy
     FIELD_EXCLUDE soi cả đoạn trước lẫn đoạn sau chỗ khớp.
  2. Theo MÃ SỐ dòng (FIELD_LINE_CODES) — dự phòng cho trường hợp OCR
     làm hỏng tên. Chữ số ASCII gần như không bao giờ bị đọc sai, trong
     khi chữ tiếng Việt có dấu thì hay hỏng: trên báo cáo VNM, EasyOCR
     đọc "TỔNG TÀI SẢN" thành "TỖNG TÀISẢN" (sai dấu + mất khoảng trắng)
     nên không alias nào khớp, còn mã "280" thì đọc đúng tuyệt đối.
"""

import json
import re
import sys
from pathlib import Path

from fields_config import (
    DEFAULT_STANDARD,
    FIELD_ALIASES,
    FIELD_EXCLUDE,
    FIELD_MAP,
    Standard,
    detect_standard,
    fields_for,
    line_codes_for,
    marker_for_form,
)

# Một giá trị tiền tệ trong BCTC luôn có dấu phân cách nghìn
# (13.217.639.635.987). Bắt buộc phải có ít nhất một nhóm 3 chữ số là
# cách rẻ nhất để bỏ qua hai cột nằm chen giữa nhãn và giá trị trên mọi
# mẫu BCTC Việt Nam: cột "Mã số" (10, 60, 270) và cột "Thuyết minh"
# (VI.1). Nếu không có ràng buộc này, regex sẽ lấy mã số làm giá trị.
#
# Số âm trong BCTC được ghi bằng ngoặc đơn — "(1.234.567)" — nên phần
# ngoặc và dấu trừ cũng phải nằm trong pattern để parse_number() biết dấu.
NUMBER_RE = r"\(?\s*-?\s*\d{1,3}(?:[.,]\d{3})+\s*\)?"

# Sau khi bắt được nhãn, chỉ tìm số trong khoảng này. Đủ rộng để vượt qua
# mã số + thuyết minh (kể cả khi OCR xuống dòng giữa chừng), nhưng đủ hẹp
# để không vô tình lấy sang giá trị của dòng chỉ tiêu kế tiếp.
LOOKAHEAD_CHARS = 80

# Độ dài đoạn text phía TRƯỚC nhãn đem đi đối chiếu FIELD_EXCLUDE["before"].
# Chỉ cần đủ ôm phần đầu của nhãn dài nhất mà alias có thể nằm lọt ở đuôi
# ("Dự phòng giảm giá " trước "hàng tồn kho"). Để rộng hơn thì đoạn này
# tràn sang cả dòng chỉ tiêu phía trên và sinh loại trừ oan.
LOOKBEHIND_CHARS = 40


def load_raw_text(file_path: str) -> str:
    with open(file_path, encoding="utf-8") as f:
        text = f.read()
    return text


def parse_number(raw: str) -> int:
    """
    Chuyển chuỗi số kiểu Việt Nam thành int.

        "13.217.639.635.987"  ->  13217639635987
        "(1.234.567)"         ->  -1234567
        "-1.234.567"          ->  -1234567
    """
    stripped = raw.strip()
    is_negative = stripped.startswith(("(", "-"))

    digits = re.sub(r"\D", "", stripped)
    if not digits:
        raise ValueError(f"Không có chữ số nào trong {raw!r}")

    value = int(digits)
    return -value if is_negative else value


def extract_field_by_alias(text: str, field_key: str) -> int | None:
    """
    Tìm giá trị theo TÊN chỉ tiêu.

    Thử lần lượt từng alias theo thứ tự cụ thể -> chung chung (xem
    FIELD_ALIASES), với mỗi alias thì duyệt hết các vị trí xuất hiện và
    bỏ qua những vị trí dính từ khoá trong FIELD_EXCLUDE — soi cả đoạn
    đứng trước nhãn lẫn đoạn nằm giữa nhãn và con số.
    """
    aliases = FIELD_ALIASES.get(field_key) or [FIELD_MAP[field_key]]
    excluded = FIELD_EXCLUDE.get(field_key, {})
    exclude_before = [bad.lower() for bad in excluded.get("before", [])]
    exclude_between = [bad.lower() for bad in excluded.get("between", [])]

    for alias in aliases:
        # re.escape: tên chỉ tiêu là dữ liệu chứ không phải regex. Không
        # escape thì một dấu "(" trong tên sẽ làm hỏng cả pattern.
        # IGNORECASE: báo cáo hay in hoa toàn bộ ("TỔNG CỘNG TÀI SẢN").
        # DOTALL: OCR trả text nhiều dòng, số thường nằm ở dòng sau nhãn.
        pattern = rf"{re.escape(alias)}(.{{0,{LOOKAHEAD_CHARS}}}?)({NUMBER_RE})"

        for match in re.finditer(pattern, text, flags=re.IGNORECASE | re.DOTALL):
            before = text[max(0, match.start() - LOOKBEHIND_CHARS):match.start()].lower()
            if any(bad in before for bad in exclude_before):
                continue

            between = match.group(1).lower()
            if any(bad in between for bad in exclude_between):
                continue

            try:
                return parse_number(match.group(2))
            except ValueError:
                continue

    return None


def extract_field_by_code(text: str, field_key: str, standard: Standard) -> int | None:
    """
    Tìm giá trị theo MÃ SỐ dòng — dự phòng khi OCR làm hỏng tên chỉ tiêu.

    Chỉ áp dụng khi text có dấu hiệu đúng mẫu biểu, vì mã số chỉ duy nhất
    TRONG một mẫu: "10" là Doanh thu thuần ở B02 nhưng là Biến động hàng
    tồn kho ở B03. Không kiểm tra mẫu biểu thì đây thành nguồn sai âm
    thầm — đúng loại lỗi tệ nhất, vì có giá trị nên router tin dùng luôn.

    standard là THAM SỐ BẮT BUỘC, không có mặc định: mã số còn khác nhau
    giữa hai chuẩn (tổng tài sản là 270 ở TT200, 280 ở TT99), nên chọn
    nhầm bảng mã cũng là một nguồn sai âm thầm y hệt. Bắt người gọi nói rõ
    chuẩn là cách rẻ nhất để lỗi đó không xảy ra được.
    """
    entry = line_codes_for(standard).get(field_key)
    if entry is None:
        return None

    form, code = entry
    marker = marker_for_form(form)
    if marker is None or not re.search(marker, text, flags=re.IGNORECASE):
        return None

    # Mã số phải nằm ở CUỐI một dòng. Cột "Mã số" là cột cuối trước khi
    # sang cột giá trị, nên OCR luôn xuống dòng ngay sau nó — hoặc mã
    # đứng riêng một dòng ("280"), hoặc khép lại dòng công thức
    # ("...+ 260 + 270) 200"). Ràng buộc cuối dòng là thứ phân biệt mã số
    # với một con số bất kỳ nằm giữa câu.
    #
    # Sau mã có thể còn cột thuyết minh (V.5, VI.1...) rồi mới tới giá
    # trị. NUMBER_RE bắt buộc có dấu phân cách nghìn nên số thuyết minh
    # và các mã số khác không lọt vào.
    pattern = rf"(?:^|\s){re.escape(code)}\s*$(.{{0,{LOOKAHEAD_CHARS}}}?)({NUMBER_RE})"

    for match in re.finditer(pattern, text, flags=re.MULTILINE | re.DOTALL):
        try:
            return parse_number(match.group(2))
        except ValueError:
            continue

    return None


def extract_field(text: str, field_key: str, standard: Standard) -> int | None:
    """Thử tên chỉ tiêu trước, không ra thì mới thử mã số dòng."""
    value = extract_field_by_alias(text, field_key)
    if value is not None:
        return value

    return extract_field_by_code(text, field_key, standard)


def extract_all_fields(text: str, standard: Standard | None = None) -> dict:
    """
    Trích mọi chỉ tiêu từ text OCR của một trang.

    standard=None nghĩa là "tự nhận diện từ nội dung trang". Khi nhận diện
    thất bại thì lùi về DEFAULT_STANDARD và KÊU RA LOG — không im lặng.

    Vì sao không để nó im: dùng nhầm bảng mã không làm gì nổ, nó chỉ trả về
    sai dòng. Nếu bước lùi này không để lại dấu vết thì về sau không tách
    được "lỗi do nhận diện sai chuẩn" khỏi "lỗi do đọc sai số", mà đó lại
    đúng là hai thứ cần đo riêng.
    """
    if standard is None:
        standard, do_tin_cay = detect_standard(text)
        if standard is None:
            standard = DEFAULT_STANDARD
            print(
                f"[STANDARD] Không nhận diện được chuẩn, lùi về {standard} "
                f"— kết quả trang này có thể dùng sai bảng mã số dòng"
            )
        else:
            print(f"[STANDARD] Trang dùng chuẩn {standard} (tin cậy {do_tin_cay:.2f})")

    return {key: extract_field(text, key, standard) for key in fields_for(standard)}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_baseline.py <file_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    text = load_raw_text(input_path)
    result = extract_all_fields(text)

    out_path = Path("data/output")/(Path(input_path).stem + "_extracted.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps(result, ensure_ascii=False, indent=2))
