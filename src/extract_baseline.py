"""
Pipeline step 2: Raw Text -> Structured JSON (Extraction baseline)

Rule-based / regex extraction of key financial line items from
OCR raw text. This is the baseline to compare against a VLM-based
approach later.
"""

import sys
import re
import json
from pathlib import Path

from fields_config import FIELD_MAP, FIELD_ALIASES, FIELD_EXCLUDE


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


def extract_field(text: str, field_key: str) -> int | None:
    """
    Tìm giá trị của một chỉ tiêu trong text OCR.

    Thử lần lượt từng alias theo thứ tự cụ thể -> chung chung (xem
    FIELD_ALIASES), với mỗi alias thì duyệt hết các vị trí xuất hiện và
    bỏ qua những vị trí dính từ khoá trong FIELD_EXCLUDE.
    """
    aliases = FIELD_ALIASES.get(field_key) or [FIELD_MAP[field_key]]
    excluded = FIELD_EXCLUDE.get(field_key, [])

    for alias in aliases:
        # re.escape: tên chỉ tiêu là dữ liệu chứ không phải regex. Không
        # escape thì một dấu "(" trong tên sẽ làm hỏng cả pattern.
        # IGNORECASE: báo cáo hay in hoa toàn bộ ("TỔNG CỘNG TÀI SẢN").
        # DOTALL: OCR trả text nhiều dòng, số thường nằm ở dòng sau nhãn.
        pattern = rf"{re.escape(alias)}(.{{0,{LOOKAHEAD_CHARS}}}?)({NUMBER_RE})"

        for match in re.finditer(pattern, text, flags=re.IGNORECASE | re.DOTALL):
            between = match.group(1).lower()
            if any(bad.lower() in between for bad in excluded):
                continue

            try:
                return parse_number(match.group(2))
            except ValueError:
                continue

    return None


def extract_all_fields(text: str) -> dict:
    return {key: extract_field(text, key) for key in FIELD_MAP}


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

    print(result)
