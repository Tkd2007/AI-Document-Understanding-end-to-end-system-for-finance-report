import re
from fields_config import NON_NEGATIVE_FIELDS


# Doanh thu một kỳ lớn hơn tổng tài sản gấp nhiều lần là bất thường với
# doanh nghiệp sản xuất — thường là dấu hiệu đọc nhầm dòng hoặc nhầm cột.
REVENUE_TO_ASSETS_LIMIT = 10


def validate_result(result: dict) -> dict:
    warnings = []
    data = {}

    for key, value in result.items():
        number = coerce_number(value)
        if value is not None and number is None:
            warnings.append(f"{key}: không đọc được giá trị {value!r} thành số")
        data[key] = number

    for key in NON_NEGATIVE_FIELDS:
        value = data.get(key)
        if value is not None and value < 0:
            warnings.append(f"{key} có giá trị âm bất thường: {value}")

    doanh_thu = data.get("doanh_thu_thuan")
    tong_tai_san = data.get("tong_tai_san")

    if doanh_thu is not None and tong_tai_san is not None:
        if tong_tai_san > 0 and doanh_thu > tong_tai_san * REVENUE_TO_ASSETS_LIMIT:
            warnings.append("Doanh thu thuần lớn bất thường so với Tổng tài sản")

    missing = [key for key, value in data.items() if value is None]
    if missing:
        warnings.append(f"Không trích xuất được các chỉ tiêu: {', '.join(missing)}")

    return {"data": data, "warnings": warnings}


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