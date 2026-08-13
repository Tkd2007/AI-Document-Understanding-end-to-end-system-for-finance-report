"""
Single source of truth cho các chỉ tiêu cần trích xuất.

FIELD_MAP là danh sách field chuẩn, dùng chung cho cả hai nhánh: nhánh
VLM đưa thẳng vào prompt, nhánh regex dùng làm schema kết quả.

FIELD_ALIASES, FIELD_EXCLUDE và FIELD_LINE_CODES chỉ phục vụ nhánh regex,
vì regex khớp chữ theo mặt chữ nên phải liệt kê sẵn mọi cách gọi. Nhánh
VLM không cần các bảng này — model tự hiểu ngữ nghĩa của dòng.

FIELD_RULES gắn quy tắc kiểm tra vào chính định nghĩa field, để thêm một
field mới chỉ cần sửa file này chứ không phải lục lại validation.py.
"""

FIELD_MAP = {
    # --- B01a-DN: Báo cáo tình hình tài chính (bảng cân đối kế toán) ---
    "tai_san_ngan_han": "Tài sản ngắn hạn",
    "hang_ton_kho": "Hàng tồn kho",
    "tai_san_dai_han": "Tài sản dài hạn",
    "tong_tai_san": "Tổng tài sản",
    "no_phai_tra": "Nợ phải trả",
    "von_chu_so_huu": "Vốn chủ sở hữu",

    # --- B02a-DN: Báo cáo kết quả hoạt động kinh doanh ---
    "doanh_thu_thuan": "Doanh thu thuần",
    "gia_von_hang_ban": "Giá vốn hàng bán",
    "loi_nhuan_gop": "Lợi nhuận gộp",
    "loi_nhuan_truoc_thue": "Lợi nhuận trước thuế",
    "loi_nhuan_sau_thue": "Lợi nhuận sau thuế",
}

# Quy tắc kiểm tra gắn với từng field.
#
#   allow_negative — số âm có phải dấu hiệu đọc sai không? Lợi nhuận âm
#     là doanh nghiệp lỗ, hoàn toàn bình thường. Tổng tài sản âm thì chắc
#     chắn là lỗi.
#   required — field bắt buộc phải có thì kết quả mới được coi là đạt.
#     Không đánh dấu tất cả là required: càng nhiều field bắt buộc thì
#     càng dễ phải fallback VLM chỉ vì một chỉ tiêu phụ không tìm thấy.
FIELD_RULES = {
    "tai_san_ngan_han":     {"allow_negative": False, "required": False},
    "hang_ton_kho":         {"allow_negative": False, "required": False},
    "tai_san_dai_han":      {"allow_negative": False, "required": False},
    "tong_tai_san":         {"allow_negative": False, "required": True},
    "no_phai_tra":          {"allow_negative": False, "required": False},
    "von_chu_so_huu":       {"allow_negative": True,  "required": False},
    "doanh_thu_thuan":      {"allow_negative": False, "required": True},
    "gia_von_hang_ban":     {"allow_negative": False, "required": False},
    "loi_nhuan_gop":        {"allow_negative": True,  "required": False},
    "loi_nhuan_truoc_thue": {"allow_negative": True,  "required": False},
    "loi_nhuan_sau_thue":   {"allow_negative": True,  "required": True},
}

# Quan hệ số học giữa các field, dùng để bắt lỗi đọc nhầm dòng/nhầm cột.
# Mỗi mục: (field nhỏ hơn, field lớn hơn, mô tả).
# Chỉ kiểm tra khi cả hai field đều có giá trị.
FIELD_RELATIONS = [
    ("tai_san_ngan_han", "tong_tai_san", "Tài sản ngắn hạn không thể lớn hơn Tổng tài sản"),
    ("tai_san_dai_han", "tong_tai_san", "Tài sản dài hạn không thể lớn hơn Tổng tài sản"),
    ("hang_ton_kho", "tai_san_ngan_han", "Hàng tồn kho không thể lớn hơn Tài sản ngắn hạn"),
    ("no_phai_tra", "tong_tai_san", "Nợ phải trả không thể lớn hơn Tổng tài sản"),
    ("gia_von_hang_ban", "doanh_thu_thuan", "Giá vốn hàng bán không thể lớn hơn Doanh thu thuần"),
    ("loi_nhuan_sau_thue", "loi_nhuan_truoc_thue", "Lợi nhuận sau thuế không thể lớn hơn Lợi nhuận trước thuế"),
]

# Đẳng thức kế toán. Chặt hơn FIELD_RELATIONS ở trên rất nhiều: bất đẳng
# thức chỉ bắt được lỗi thô (A lớn hơn B), còn đẳng thức thì lệch một chữ
# số là lộ ngay. Trên báo cáo VNM Q1/2026, cả hai đẳng thức dưới đây khớp
# tới từng đồng — nên nếu một lần chạy nào đó không khớp, gần như chắc
# chắn có field bị đọc sai chứ không phải báo cáo sai.
#
# Mỗi mục: (danh sách field cộng lại, field tổng, mô tả).
# Chỉ kiểm tra khi TẤT CẢ field liên quan đều có giá trị.
FIELD_IDENTITIES = [
    (
        ["tai_san_ngan_han", "tai_san_dai_han"],
        "tong_tai_san",
        "Tài sản ngắn hạn + Tài sản dài hạn phải bằng Tổng tài sản",
    ),
    (
        ["no_phai_tra", "von_chu_so_huu"],
        "tong_tai_san",
        "Nợ phải trả + Vốn chủ sở hữu phải bằng Tổng tài sản",
    ),
    (
        ["gia_von_hang_ban", "loi_nhuan_gop"],
        "doanh_thu_thuan",
        "Giá vốn hàng bán + Lợi nhuận gộp phải bằng Doanh thu thuần",
    ),
]

# Dung sai cho đẳng thức, tính theo tỷ lệ trên giá trị tổng.
#
# Để RẤT hẹp, vì báo cáo đã kiểm toán thì các đẳng thức này khớp tuyệt
# đối tới từng đồng — mọi sai lệch đều là do đọc sai, không phải do báo
# cáo. Dung sai rộng làm luật này mất tác dụng: với tổng tài sản 47
# nghìn tỷ, mức 0,1% cho phép lệch tới 47 tỷ đồng, tức là đọc nhầm một
# chữ số ở hàng chục tỷ vẫn lọt.
#
# 1e-7 tương đương ~4,7 triệu đồng trên báo cáo cỡ VNM: đủ để bỏ qua làm
# tròn ở đơn vị rút gọn, nhưng bắt được mọi lỗi đọc sai chữ số thực tế.
IDENTITY_TOLERANCE_RATIO = 1e-7

# Biên tỷ trọng cho những field không đẳng thức kế toán nào phủ được.
#
# FIELD_RELATIONS chỉ bắt lỗi sai THỨ BẬC (A lớn hơn B), nên một giá trị
# đọc nhầm sang dòng con nhỏ hơn cả nghìn lần vẫn lọt — nó vẫn nhỏ hơn
# field cha đúng như luật đòi hỏi. Bảng này bắt loại lệch BẬC ĐỘ LỚN đó.
#
# Đây là ràng buộc HEURISTIC chứ không phải đẳng thức kế toán, nên biên
# để rất rộng: mục tiêu là bắt lỗi lệch cả bậc độ lớn, không phải đánh
# giá cơ cấu tài sản của doanh nghiệp. Trên báo cáo VNM Q1/2026 hàng tồn
# kho chiếm 18,3% tài sản ngắn hạn — nằm thoải mái trong biên dưới đây,
# còn giá trị đọc nhầm từ dòng dự phòng chỉ chiếm 0,02% nên bị bắt.
#
# Mỗi mục: (field, field cơ sở, tỷ lệ tối thiểu, tỷ lệ tối đa, mô tả).
# Chỉ kiểm tra khi cả hai field có giá trị và field cơ sở khác 0.
FIELD_RATIO_BOUNDS = [
    (
        "hang_ton_kho", "tai_san_ngan_han", 0.01, 1.0,
        "Hàng tồn kho chiếm tỷ trọng bất thường trong Tài sản ngắn hạn",
    ),
]

# Doanh thu một kỳ lớn hơn tổng tài sản gấp nhiều lần là bất thường với
# doanh nghiệp sản xuất — thường là dấu hiệu đọc nhầm dòng hoặc nhầm cột.
REVENUE_TO_ASSETS_LIMIT = 10

# Các cách gọi khác nhau của cùng một chỉ tiêu trong báo cáo thật.
#
# THỨ TỰ QUAN TRỌNG: extract_field() dừng ở alias đầu tiên tìm thấy, nên
# alias cụ thể phải đứng trước alias chung chung. Ví dụ nếu để "Lợi nhuận
# sau thuế" lên trước "Lợi nhuận sau thuế TNDN" thì nó sẽ vớ phải dòng
# "Lợi nhuận sau thuế chưa phân phối" trên bảng cân đối kế toán — một
# chỉ tiêu hoàn toàn khác nhưng trùng tiền tố.
FIELD_ALIASES = {
    "tai_san_ngan_han": [
        "Tài sản ngắn hạn",
    ],
    "hang_ton_kho": [
        "Hàng tồn kho",
    ],
    "tai_san_dai_han": [
        "Tài sản dài hạn",
    ],
    "tong_tai_san": [
        "Tổng cộng tài sản",
        "Tổng tài sản",
    ],
    "no_phai_tra": [
        "Nợ phải trả",
    ],
    "von_chu_so_huu": [
        "Vốn chủ sở hữu",
    ],
    "doanh_thu_thuan": [
        "Doanh thu thuần về bán hàng và cung cấp dịch vụ",
        # OCR hay nuốt chữ ở các nhãn dài, nên cần thêm một biến thể ngắn
        # vẫn đủ đặc trưng để không lẫn với dòng doanh thu trong thuyết minh.
        "Doanh thu thuần về bán",
        "Doanh thu thuần",
    ],
    "gia_von_hang_ban": [
        "Giá vốn hàng bán và dịch vụ cung cấp",
        "Giá vốn hàng bán",
    ],
    "loi_nhuan_gop": [
        "Lợi nhuận gộp về bán hàng và cung cấp dịch vụ",
        "Lợi nhuận gộp",
    ],
    "loi_nhuan_truoc_thue": [
        "Lợi nhuận kế toán trước thuế",
        "Lợi nhuận trước thuế",
    ],
    "loi_nhuan_sau_thue": [
        "Lợi nhuận sau thuế thu nhập doanh nghiệp",
        "Lợi nhuận sau thuế TNDN",
        "Lợi nhuận sau thuế",
    ],
}

# Cụm từ khiến một match bị loại, dùng để tách các chỉ tiêu mà alias ở
# trên chưa phân biệt được. Mỗi field có hai danh sách, theo VỊ TRÍ của
# cụm từ so với chỗ alias khớp:
#
#   between — nằm SAU nhãn, giữa nhãn và con số. Loại các nhãn nối dài
#     thêm về phía sau: "Lợi nhuận sau thuế" + " chưa phân phối".
#
#   before — nằm TRƯỚC nhãn. Loại các nhãn có alias nằm ở phần ĐUÔI của
#     một nhãn dài hơn. Chỉ dùng between là không đủ, vì lúc đó cụm từ
#     phân biệt đứng phía trước nên không bao giờ lọt vào đoạn kiểm tra.
FIELD_EXCLUDE = {
    "loi_nhuan_sau_thue": {
        "between": [
            "chưa phân",        # "Lợi nhuận sau thuế chưa phân phối" (bảng cân đối)
            "được trích chia",  # "...được trích chia cổ tức cho các cổ đông"
        ],
    },
    "tai_san_ngan_han": {
        "between": [
            "khác",             # "Tài sản ngắn hạn khác"
        ],
    },
    "tai_san_dai_han": {
        "between": [
            "khác",             # "Tài sản dài hạn khác"
        ],
    },
    "no_phai_tra": {
        "between": [
            "người bán",        # "Phải trả người bán"
            "người lao",        # "Phải trả người lao động"
        ],
    },
    "hang_ton_kho": {
        # "Dự phòng giảm giá hàng tồn kho" (mã 142) kết thúc bằng đúng
        # cụm "hàng tồn kho", nên alias khớp trúng dòng dự phòng và lấy
        # về một khoản âm nhỏ hơn giá trị thật khoảng 1000 lần. Trên báo
        # cáo VNM Q1/2026 đây là ca có thật, vì OCR còn cắt mất chữ "Hàng"
        # ở dòng đúng (mã 140) khiến alias không khớp được dòng đó nữa.
        "before": [
            "giảm giá",
            "dự phòng",
        ],
    },
}

# Mã số dòng theo mẫu biểu Bộ Tài chính (Thông tư 99/2025/TT-BTC).
#
# Mã số đáng tin hơn tên chữ: OCR đọc chữ số gần như không sai, còn chữ
# tiếng Việt có dấu thì hay hỏng ("TỔNG TÀI SẢN" -> "TỖNG TÀISẢN").
#
# CẢNH BÁO: mã số chỉ duy nhất TRONG một mẫu biểu, không phải toàn tài
# liệu. Mã "10" là Doanh thu thuần ở B02a nhưng là Biến động hàng tồn kho
# ở B03a; mã "20", "30", "50" cũng trùng tương tự. Nên mỗi field phải đi
# kèm mẫu biểu của nó, và chỉ dùng mã khi trang đúng mẫu đó.
FIELD_LINE_CODES = {
    "tai_san_ngan_han":     ("B01a", "100"),
    "hang_ton_kho":         ("B01a", "140"),
    "tai_san_dai_han":      ("B01a", "200"),
    "tong_tai_san":         ("B01a", "280"),
    "no_phai_tra":          ("B01a", "300"),
    "von_chu_so_huu":       ("B01a", "400"),
    "doanh_thu_thuan":      ("B02a", "10"),
    "gia_von_hang_ban":     ("B02a", "11"),
    "loi_nhuan_gop":        ("B02a", "20"),
    "loi_nhuan_truoc_thue": ("B02a", "50"),
    "loi_nhuan_sau_thue":   ("B02a", "60"),
}

# Dấu hiệu nhận biết trang thuộc mẫu biểu nào.
#
# OCR đọc "Mẫu B 01a - DN" ra đủ kiểu biến thể vì chữ số và chữ cái nhìn
# giống nhau: trên báo cáo VNM, EasyOCR trả về "Mâu B Ola" — số 0 thành
# chữ O, số 1 thành chữ l thường. Nên chữ số nào cũng phải liệt kê kèm
# các chữ cái dễ nhầm với nó.
_ZERO = r"[O0o]"      # 0 hay bị đọc thành O hoa hoặc o thường
_ONE = r"[1lI|]"      # 1 hay bị đọc thành l thường, I hoa, hoặc gạch đứng

FORM_MARKERS = {
    "B01a": rf"B\s*{_ZERO}\s*{_ONE}\s*a",
    "B02a": rf"B\s*{_ZERO}\s*2\s*a",
    "B03a": rf"B\s*{_ZERO}\s*3\s*a",
}