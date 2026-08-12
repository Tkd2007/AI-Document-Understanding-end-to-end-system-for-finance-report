"""
Validation

Ép kiểu số và chạy các sanity check trên kết quả trích xuất.

Tách khỏi api.py để router.py dùng được làm cổng quyết định fallback mà
không tạo import vòng (api.py đã import router.py).

Mọi quy tắc đều đọc từ fields_config.py chứ không hardcode tên field ở
đây — thêm một chỉ tiêu mới chỉ cần sửa fields_config.py.
"""

import re

from fields_config import (
    FIELD_MAP,
    FIELD_RELATIONS,
    FIELD_RULES,
    REVENUE_TO_ASSETS_LIMIT,
)


def coerce_number(value) -> int | float | None:
    """
    Ép giá trị VLM trả về thành số.

    VLM đôi khi trả số dưới dạng chuỗi ("13217639635987" hoặc
    "13.217.639.635.987") dù prompt đã yêu cầu integer. Không ép kiểu ở
    đây thì các phép so sánh bên dưới sẽ nổ TypeError và API trả 500.
    Trả về None nếu không đọc được thành số.
    """
    if value is None:
        return None
    # bool là subclass của int trong Python, chặn sớm kẻo True thành 1.
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value

    text = str(value).strip()
    is_negative = text.startswith(("(", "-"))
    digits = re.sub(r"\D", "", text)
    if not digits:
        return None

    number = int(digits)
    return -number if is_negative else number


def field_label(key: str) -> str:
    """Tên tiếng Việt của field, để câu cảnh báo đọc được."""
    return FIELD_MAP.get(key, key)


def has_required_fields(data: dict) -> bool:
    """
    Các field bắt buộc đã có giá trị chưa?

    Không đòi hỏi MỌI field: danh sách chỉ tiêu càng dài thì càng dễ
    thiếu một chỉ tiêu phụ, và nếu lấy đó làm điều kiện thì gần như lần
    nào cũng phải fallback sang VLM.
    """
    for key, rules in FIELD_RULES.items():
        if rules.get("required") and data.get(key) is None:
            return False
    return True


def validate_result(result: dict) -> dict:
    """
    Trả về {"data": <đã ép kiểu số>, "warnings": [...]}.

    warnings rỗng nghĩa là không phát hiện bất thường. Không chặn kết
    quả — chỉ gắn cờ để người dùng (và router) biết chỗ nào cần xem lại.
    """
    warnings = []
    data = {}

    # 1. Ép kiểu số
    for key, value in result.items():
        number = coerce_number(value)
        if value is not None and number is None:
            warnings.append(f"{field_label(key)}: không đọc được giá trị {value!r} thành số")
        data[key] = number

    # 2. Số âm ở những chỉ tiêu không được phép âm
    for key, value in data.items():
        if value is None or value >= 0:
            continue
        rules = FIELD_RULES.get(key, {})
        if not rules.get("allow_negative", True):
            warnings.append(f"{field_label(key)} có giá trị âm bất thường: {value}")

    # 3. Quan hệ số học giữa các chỉ tiêu. So sánh trên giá trị tuyệt đối:
    #    một số dòng (giá vốn, lợi nhuận) có thể được trình bày âm tuỳ mẫu
    #    báo cáo, nhưng độ lớn thì vẫn phải theo đúng thứ bậc.
    for smaller_key, larger_key, message in FIELD_RELATIONS:
        smaller = data.get(smaller_key)
        larger = data.get(larger_key)
        if smaller is None or larger is None:
            continue
        if abs(smaller) > abs(larger):
            warnings.append(f"{message} ({smaller:,} > {larger:,})")

    # 4. Tỷ lệ doanh thu / tổng tài sản
    doanh_thu = data.get("doanh_thu_thuan")
    tong_tai_san = data.get("tong_tai_san")
    if doanh_thu is not None and tong_tai_san is not None and tong_tai_san > 0:
        if doanh_thu > tong_tai_san * REVENUE_TO_ASSETS_LIMIT:
            warnings.append(
                f"Doanh thu thuần lớn bất thường so với Tổng tài sản "
                f"(gấp hơn {REVENUE_TO_ASSETS_LIMIT} lần)"
            )

    # 5. Thiếu chỉ tiêu bắt buộc
    missing_required = [
        field_label(key)
        for key, rules in FIELD_RULES.items()
        if rules.get("required") and data.get(key) is None
    ]
    if missing_required:
        warnings.append(f"Thiếu chỉ tiêu bắt buộc: {', '.join(missing_required)}")

    return {"data": data, "warnings": warnings}