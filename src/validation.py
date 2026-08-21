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
    FIELD_IDENTITIES,
    FIELD_MAP,
    FIELD_RATIO_BOUNDS,
    FIELD_RELATIONS,
    FIELD_RULES,
    IDENTITY_TOLERANCE_RATIO,
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

    # 3. Quan hệ số học giữa các chỉ tiêu.
    #
    #    Mặc định so trên trị tuyệt đối: một số dòng (giá vốn, lợi nhuận)
    #    có thể được trình bày âm tuỳ mẫu báo cáo, nhưng độ lớn thì vẫn
    #    phải theo đúng thứ bậc. Quan hệ nào cần so trên giá trị CÓ DẤU thì
    #    tự khai use_abs=False.
    #
    #    in_effect() là chỗ chặn báo oan trên báo cáo lỗ — xem docstring
    #    của FieldRelation trong fields_config.py để biết vì sao mấy bất
    #    đẳng thức này không phải lúc nào cũng đúng.
    for relation in FIELD_RELATIONS:
        smaller = data.get(relation.smaller)
        larger = data.get(relation.larger)
        if smaller is None or larger is None:
            continue
        if not relation.in_effect(data):
            continue

        left = abs(smaller) if relation.use_abs else smaller
        right = abs(larger) if relation.use_abs else larger

        if left > right:
            # In giá trị GỐC chứ không in bản đã lấy trị tuyệt đối: người
            # đọc cảnh báo cần thấy đúng con số nằm trong dữ liệu để đi dò.
            warnings.append(f"{relation.message} ({smaller:,} > {larger:,})")

    # 4. Đẳng thức kế toán — kiểm tra chặt nhất trong cả hàm.
    #    Các check ở trên chỉ bắt được lỗi thô; đẳng thức thì lệch một
    #    chữ số ở BẤT KỲ field nào trong nhóm là lộ ngay. Đây là thứ bắt
    #    được kiểu sai nguy hiểm nhất: giá trị đọc ra trông hợp lý, đúng
    #    thứ bậc, nhưng thực ra lấy nhầm dòng.
    for parts, total_key, message in FIELD_IDENTITIES:
        total = data.get(total_key)
        values = [data.get(key) for key in parts]

        if total is None or any(value is None for value in values):
            continue

        actual = sum(values)
        tolerance = abs(total) * IDENTITY_TOLERANCE_RATIO

        if abs(actual - total) > tolerance:
            diff = actual - total
            warnings.append(f"{message} — lệch {diff:,} ({actual:,} vs {total:,})")

    # 5. Tỷ trọng so với field cơ sở, cho những chỉ tiêu không đẳng thức
    #    kế toán nào phủ được. Bước 3 chỉ bắt sai thứ bậc, nên một giá
    #    trị đọc nhầm sang dòng con nhỏ hơn cả nghìn lần vẫn lọt qua —
    #    nó vẫn nhỏ hơn field cha đúng như luật đòi hỏi. Bước này bắt
    #    đúng loại lệch bậc độ lớn đó.
    for key, base_key, min_ratio, max_ratio, message in FIELD_RATIO_BOUNDS:
        value = data.get(key)
        base = data.get(base_key)
        if value is None or base is None or base == 0:
            continue

        ratio = abs(value) / abs(base)
        if not min_ratio <= ratio <= max_ratio:
            warnings.append(
                f"{message}: {ratio:.2%} "
                f"(ngoài khoảng {min_ratio:.0%}–{max_ratio:.0%})"
            )

    # 6. Tỷ lệ doanh thu / tổng tài sản
    doanh_thu = data.get("doanh_thu_thuan")
    tong_tai_san = data.get("tong_tai_san")
    if doanh_thu is not None and tong_tai_san is not None and tong_tai_san > 0:
        if doanh_thu > tong_tai_san * REVENUE_TO_ASSETS_LIMIT:
            warnings.append(
                f"Doanh thu thuần lớn bất thường so với Tổng tài sản "
                f"(gấp hơn {REVENUE_TO_ASSETS_LIMIT} lần)"
            )

    # 7. Thiếu chỉ tiêu bắt buộc
    missing_required = [
        field_label(key)
        for key, rules in FIELD_RULES.items()
        if rules.get("required") and data.get(key) is None
    ]
    if missing_required:
        warnings.append(f"Thiếu chỉ tiêu bắt buộc: {', '.join(missing_required)}")

    return {"data": data, "warnings": warnings}
