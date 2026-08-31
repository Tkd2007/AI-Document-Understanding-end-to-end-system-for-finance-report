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
    FIELD_RATIO_BOUNDS,
    FIELD_RELATIONS,
    FIELD_RULES,
    IDENTITY_TOLERANCE_RATIO,
    REVENUE_TO_ASSETS_LIMIT,
    TOTAL_ASSETS_BOUNDS,
    UNIT_KEY,
    Standard,
    chuan_hoa_dau,
    identities_for,
    parse_unit,
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


def validate_result(
    result: dict, standard: Standard, he_so_theo_truong: dict[str, int] | None = None
) -> dict:
    """
    Trả về {"data": <đã ép kiểu số>, "warnings": [...]}.

    warnings rỗng nghĩa là không phát hiện bất thường. Không chặn kết
    quả — chỉ gắn cờ để người dùng (và router) biết chỗ nào cần xem lại.

    VÌ SAO CÓ `he_so_theo_truong`: một tài liệu KHÔNG nhất thiết chỉ có một
    đơn vị tính. Đo được trên `HNG_2025H1_TT200`: trang 1 là công văn giải
    trình gửi HNX, khai `ĐVT: tỷ đồng`, và `loi_nhuan_sau_thue` được đọc ra
    từ đúng bảng ấy; 25 chỉ tiêu còn lại đọc từ các bảng BCTC khai `nghìn
    đồng`. Không hệ số toàn cục nào đúng cho cả hai — chọn tỷ đồng thì 24 ô
    sai gấp 1e6, chọn nghìn đồng thì ô kia sai gấp 1e6 theo chiều ngược lại.

    Nên hệ số phải buộc theo BẢNG mà con số được đọc ra, không buộc theo tài
    liệu. Tham số này là ánh xạ {chỉ tiêu -> hệ số của bảng đã sinh ra nó},
    do `extract_vlm.extract_fields_from_regions()` dựng từ provenance của
    từng ô. Chỉ tiêu nào không có trong ánh xạ — ví dụ ô do nhánh OCR điền —
    thì lùi về hệ số mức tài liệu, đúng hành vi cũ.

    Để None thì hàm hoạt động y hệt bản trước: một hệ số cho tất cả.

    standard quyết định dùng bộ đẳng thức của chuẩn mẫu biểu nào, và là
    THAM SỐ BẮT BUỘC — không có mặc định.

    VÌ SAO MẶC ĐỊNH ĐÃ BỊ BỎ ĐI. Bản trước để `standard=DEFAULT_STANDARD`
    kèm lời cảnh báo rằng mặc định đó thành nguy hiểm "ngay khi việc đối
    chiếu Phụ lục IV cho thấy hai chuẩn khác nhau về đẳng thức". Điều kiện
    đó đã xảy ra: Mốc 1 (commit `4064519`) cho thấy phân rã Tài sản ngắn
    hạn khác nhau thật — TT200 có `100 = 110+120+130+140+150`, còn TT99 có
    thêm mã 160 vì mã 150 của nó là Tài sản sinh học ngắn hạn.

    Hậu quả của bản cũ, đo được: báo cáo TT200 bị kiểm bằng đẳng thức TT99,
    mà đẳng thức TT99 chứa `tai_san_sinh_hoc_ngan_han` — chỉ tiêu TT200
    không có, nên luôn `None`, nên CẢ đẳng thức bị bỏ qua im lặng. Một lỗi
    500 tỷ trong phân rã tài sản ngắn hạn của báo cáo TT200 đi qua mà không
    sinh một cảnh báo nào. Đó đúng là đẳng thức đắt nhất mà Mốc 1 mua về.

    Bắt người gọi nói rõ chuẩn là cách rẻ nhất để lỗi đó không xảy ra được
    nữa — cùng lý do `extract_field_by_code()` cũng không có mặc định.
    """
    warnings = []
    data = {}

    # 0. Đơn vị tính — xử lý TRƯỚC mọi thứ khác, vì nó quyết định con số
    #    đem đi kiểm là con số nào. Mọi giá trị trong "data" trả về đều đã
    #    quy về ĐỒNG, để số của các báo cáo khác đơn vị so được với nhau.
    don_vi_raw = result.get(UNIT_KEY)
    he_so, don_vi_chuan = parse_unit(don_vi_raw)

    if he_so is None:
        # Không im lặng coi là "đồng". Một tài liệu chưa biết bậc độ lớn
        # mà bị đối xử như đã biết thì mọi con số accuracy đo trên nó đều
        # vô nghĩa, và không có gì báo ra điều đó.
        thieu = "Không có khai báo đơn vị tính" if don_vi_raw is None else (
            f"Không đọc được đơn vị tính {don_vi_raw!r}"
        )
        warnings.append(f"{thieu} — không xác minh được bậc độ lớn của các con số")

    # 1. Ép kiểu số, rồi quy đổi về đồng
    #
    #    Hệ số lấy theo TỪNG CHỈ TIÊU khi người gọi biết chỉ tiêu ấy đọc ra
    #    từ bảng nào; lùi về hệ số mức tài liệu khi không biết. Ghi lại hệ số
    #    ĐÃ THẬT SỰ DÙNG cho từng ô chứ không chỉ ghi ánh xạ đầu vào: hai ô
    #    cùng nhận hệ số 1000 vì một ô đọc được đơn vị tại chỗ còn ô kia lùi
    #    về mức tài liệu là hai mức tin cậy khác nhau, và về sau không ai
    #    dựng lại được con số nếu bảng kết quả không nói nó đã nhân với gì.
    he_so_theo_truong = he_so_theo_truong or {}
    he_so_da_dung: dict[str, int] = {}

    for key, value in result.items():
        if key == UNIT_KEY:
            continue

        number = coerce_number(value)
        if value is not None and number is None:
            warnings.append(f"{field_label(key)}: không đọc được giá trị {value!r} thành số")

        he_so_o = he_so_theo_truong.get(key, he_so)
        if number is not None and he_so_o is not None:
            number *= he_so_o
            he_so_da_dung[key] = he_so_o

        data[key] = number

    # 1b. Sửa dấu ba dòng khấu trừ, NGAY SAU khi ép kiểu và TRƯỚC mọi phép
    #     kiểm. Phải nằm ở đây chứ không phải trong router: trước bước ép
    #     kiểu thì giá trị VLM còn có thể là chuỗi, và một hàm kiểm dấu chạy
    #     trên chuỗi sẽ lặng lẽ không làm gì cả — hỏng đúng kiểu khó thấy
    #     nhất. Đặt trước bước 2 và 4 vì để giá vốn âm đi tiếp thì cả cảnh
    #     báo "âm bất thường" lẫn đẳng thức mã 20 đều báo một lỗi không có
    #     thật, và tầng ràng buộc sẽ đi sửa chỗ không hỏng.
    data, dau_da_sua = chuan_hoa_dau(data)

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
    for parts, total_key, message in identities_for(standard):
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

    # 8. Biên độ lớn tuyệt đối cho Tổng tài sản — MỎ NEO chống sai đơn vị.
    #
    #    Đây là check duy nhất trong cả hàm không bất biến với phép nhân vô
    #    hướng, nên cũng là check duy nhất bắt được ca đọc "triệu đồng"
    #    thành "đồng": mọi đẳng thức ở trên vẫn khớp hoàn hảo trong ca đó
    #    vì hệ ràng buộc là thuần nhất.
    #
    #    Bỏ qua khi chưa biết hệ số quy đổi. Áp một biên tuyệt đối lên con
    #    số chưa biết bậc độ lớn thì không phân biệt được "doanh nghiệp
    #    nhỏ" với "đọc nhầm đơn vị" — báo ra sẽ là một phỏng đoán khoác áo
    #    kết luận. Cảnh báo ở mục 0 đã nói đúng cái đang thật sự sai.
    #
    #    Gác bằng hệ số ĐÃ DÙNG CHO CHÍNH tong_tai_san, không phải hệ số mức
    #    tài liệu: với đơn vị buộc theo bảng, hai con số đó có thể khác nhau,
    #    và lấy nhầm cái kia thì mỏ neo hoặc bỏ qua một ô đã quy đổi được,
    #    hoặc áp biên tuyệt đối lên một ô chưa quy đổi — đúng hai chế độ hỏng
    #    mà cái gác này sinh ra để tránh.
    tong_tai_san_quy_doi = data.get("tong_tai_san")
    if he_so_da_dung.get("tong_tai_san") is not None and tong_tai_san_quy_doi is not None:
        can_duoi, can_tren = TOTAL_ASSETS_BOUNDS
        if not can_duoi <= abs(tong_tai_san_quy_doi) <= can_tren:
            warnings.append(
                f"{field_label('tong_tai_san')} sau quy đổi ra đồng "
                f"({tong_tai_san_quy_doi:,}) nằm ngoài biên hợp lý "
                f"[{can_duoi:,.0f}; {can_tren:,.0f}] — nghi đọc sai đơn vị tính"
            )

    return {
        "data": data,
        "meta": {
            "don_vi_tinh_raw": don_vi_raw,
            "don_vi_tinh_chuan": don_vi_chuan or None,
            "don_vi_tinh_he_so": he_so,
            # Hệ số đã nhân cho từng ô. LUÔN có mặt, kể cả khi rỗng: để khoá
            # này vắng mặt ở lượt chạy không buộc đơn vị theo bảng thì người
            # đọc phải suy từ sự vắng mặt, mà suy thì sai. Rỗng nghĩa là không
            # ô nào quy đổi được; một hệ số duy nhất cho mọi ô nghĩa là tài
            # liệu thuần một đơn vị.
            "he_so_don_vi_theo_truong": he_so_da_dung,
            "standard": standard.value,
            # Khoá nào đã bị lật dấu. Không ghi lại thì về sau không ai phân
            # biệt được "báo cáo in dương" với "ta đã sửa", và một bước sửa
            # vô hình là bước không kiểm toán lại được.
            "dau_da_sua": dau_da_sua,
        },
        "warnings": warnings,
    }
