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

import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class Standard(str, Enum):
    """
    Chuẩn mẫu biểu báo cáo tài chính đang áp dụng.

    Kế thừa str để dùng thẳng làm khoá JSON và in ra log mà không phải gọi
    .value ở mọi chỗ.

    Vì sao repo phải mang cả hai: Thông tư 99/2025/TT-BTC ban hành
    27/10/2025, hiệu lực 01/01/2026, áp dụng cho năm tài chính bắt đầu từ
    hoặc sau ngày đó. Nên bộ dữ liệu thu thập trong 2026 BẮT BUỘC trải hai
    chuẩn — báo cáo năm tài chính 2025 theo TT200, từ 2026 theo TT99. Đó
    vừa là ràng buộc kỹ thuật, vừa là trục distribution shift có sẵn và có
    ý nghĩa thật cho phần đánh giá.
    """

    TT200 = "TT200"   # Thông tư 200/2014/TT-BTC
    TT99 = "TT99"     # Thông tư 99/2025/TT-BTC, hiệu lực 01/01/2026


# Chuẩn dùng khi KHÔNG nhận diện được từ nội dung trang.
#
# Đây là fallback cuối cùng, không phải giá trị mặc định êm ái: mọi chỗ rơi
# vào đây đều phải kêu ra log. Nhận diện sai chuẩn là một CHẾ ĐỘ LỖI RIÊNG
# cần đo được, nên nếu để nó im lặng thì sau này không có cách nào tách nó
# khỏi lỗi đọc số.
DEFAULT_STANDARD = Standard.TT99


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

def _khong_am(value) -> bool:
    """
    Giá trị này không âm chứ? Thiếu dữ liệu (None) cũng tính là không âm.

    Cho None đi qua là có chủ đích: một field điều kiện chưa đọc được KHÔNG
    phải bằng chứng doanh nghiệp đang lỗ, nên không được lấy nó làm cớ tắt
    luật. Cùng tinh thần "chỉ kiểm khi cả hai field đều có giá trị" mà các
    check khác trong validation.py vẫn theo.
    """
    return value is None or value >= 0


@dataclass(frozen=True)
class FieldRelation:
    """
    Một bất đẳng thức giữa hai chỉ tiêu, kèm ĐIỀU KIỆN ÁP DỤNG.

    Vì sao cần điều kiện thay vì một bất đẳng thức trần: ba trong sáu quan
    hệ dưới đây chỉ đúng khi doanh nghiệp có lãi và vốn chủ sở hữu dương —
    tức là chúng ngầm giả định một thứ mà FIELD_RULES vốn đã cho phép ngược
    lại (von_chu_so_huu và loi_nhuan_gop được khai báo allow_negative=True).
    Mâu thuẫn đó không vô hại: FIELD_RELATIONS là một phần cổng
    is_acceptable() trong router.py, nên gặp báo cáo lỗ thì router coi kết
    quả ĐÚNG là chưa đạt, gọi VLM, và has_warnings mở chế độ ghi đè lên
    những con số vốn đã đúng.

    smaller/larger — tên field, quy ước |smaller| <= |larger|.
    applies_when   — nhận dict data đã ép kiểu số, trả True nếu bất đẳng
                     thức CÓ HIỆU LỰC trong tình huống hiện tại. None nghĩa
                     là luôn áp dụng.
    use_abs        — so trên trị tuyệt đối hay trên giá trị có dấu.

    HẠN CHẾ ĐÃ BIẾT, đừng quên khi đọc kết quả: điều kiện áp dụng đọc từ
    chính một field cũng do model trích ra. Nếu field điều kiện bị đọc sai
    thành âm thì luật tự tắt và lỗi lọt im lặng. Đây là cái giá phải trả để
    không báo oan trên báo cáo lỗ, và là một lý do nữa khiến đẳng thức kế
    toán (FIELD_IDENTITIES) đáng tin hơn hẳn nhóm bất đẳng thức này.
    """

    smaller: str
    larger: str
    message: str
    applies_when: Callable[[dict], bool] | None = None
    use_abs: bool = True

    def in_effect(self, data: dict) -> bool:
        """Bất đẳng thức này có hiệu lực với bộ số hiện tại không?"""
        return self.applies_when is None or self.applies_when(data)


# Quan hệ số học giữa các field, dùng để bắt lỗi đọc nhầm dòng/nhầm cột.
# Chỉ kiểm tra khi cả hai field đều có giá trị VÀ điều kiện áp dụng thoả.
FIELD_RELATIONS = [
    FieldRelation(
        "tai_san_ngan_han", "tong_tai_san",
        "Tài sản ngắn hạn không thể lớn hơn Tổng tài sản",
    ),
    FieldRelation(
        "tai_san_dai_han", "tong_tai_san",
        "Tài sản dài hạn không thể lớn hơn Tổng tài sản",
    ),
    FieldRelation(
        "hang_ton_kho", "tai_san_ngan_han",
        "Hàng tồn kho không thể lớn hơn Tài sản ngắn hạn",
    ),
    FieldRelation(
        "no_phai_tra", "tong_tai_san",
        "Nợ phải trả không thể lớn hơn Tổng tài sản",
        # Chỉ đúng khi vốn chủ sở hữu không âm. VCSH âm nghĩa là lỗ luỹ kế
        # đã ăn hết vốn — lúc đó nợ VƯỢT tổng tài sản là hệ quả số học của
        # chính đẳng thức no_phai_tra + von_chu_so_huu = tong_tai_san, chứ
        # không phải lỗi đọc.
        applies_when=lambda d: _khong_am(d.get("von_chu_so_huu")),
    ),
    FieldRelation(
        "gia_von_hang_ban", "doanh_thu_thuan",
        "Giá vốn hàng bán không thể lớn hơn Doanh thu thuần",
        # Chỉ đúng khi lãi gộp không âm. Bán dưới giá vốn là chuyện có thật
        # với doanh nghiệp đang xả hàng tồn hoặc gặp giá nguyên liệu tăng
        # đột biến, và khi đó gia_von > doanh_thu là đúng chứ không sai.
        applies_when=lambda d: _khong_am(d.get("loi_nhuan_gop")),
    ),
    FieldRelation(
        "loi_nhuan_sau_thue", "loi_nhuan_truoc_thue",
        "Lợi nhuận sau thuế không thể lớn hơn Lợi nhuận trước thuế",
        # Khi có lãi thì thuế chỉ làm giảm, nên LNST <= LNTT trên giá trị
        # CÓ DẤU. Khi lỗ thì quan hệ đảo chiều (LNTT = -100, LNST = -125 là
        # bình thường vì chi phí thuế hoãn lại), nên không kiểm được — và
        # so trên trị tuyệt đối như trước đây thì đúng ca đó bị báo oan.
        applies_when=lambda d: _khong_am(d.get("loi_nhuan_truoc_thue")),
        use_abs=False,
    ),
]

# Đẳng thức kế toán. Chặt hơn FIELD_RELATIONS ở trên rất nhiều: bất đẳng
# thức chỉ bắt được lỗi thô (A lớn hơn B), còn đẳng thức thì lệch một chữ
# số là lộ ngay. Trên báo cáo VNM Q1/2026, cả ba đẳng thức dưới đây khớp
# tới từng đồng — nên nếu một lần chạy nào đó không khớp, gần như chắc
# chắn có field bị đọc sai chứ không phải báo cáo sai.
#
# Mỗi mục: (danh sách field cộng lại, field tổng, mô tả).
# Chỉ kiểm tra khi TẤT CẢ field liên quan đều có giá trị.
_DANG_THUC_CHUNG = [
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

# Đẳng thức tách theo CHUẨN mẫu biểu.
#
# Hiện hai chuẩn dùng chung một bộ đẳng thức, vì ba quan hệ trên là quan hệ
# KẾ TOÁN chứ không phải quy ước trình bày: tài sản vẫn bằng nguồn vốn dù
# mẫu biểu có đổi tên hay đổi mã số dòng. Vẫn tách theo chuẩn thay vì dùng
# chung một list phẳng vì hai lý do:
#
#   1. constraints.py dựng ma trận A RIÊNG cho từng chuẩn. Đồ thị ràng buộc
#      là thứ quyết định kết quả identifiability, nên phải nói được "ma
#      trận này của chuẩn nào" chứ không được giả định hai chuẩn giống nhau.
#   2. TT99 đổi tên "Bảng cân đối kế toán" thành "Báo cáo tình hình tài
#      chính". Đổi tên thường đi kèm đổi cấu trúc, nên nếu sau này phát
#      hiện khác biệt thì sửa được đúng một chuẩn mà không đụng chuẩn kia.
#
# CẦN NGƯỜI ĐỐI CHIẾU: bộ đẳng thức của TT99 phải kiểm lại với Phụ lục IV
# văn bản gốc trước khi tin vào bất kỳ số identifiability nào.
FIELD_IDENTITIES: dict[Standard, list] = {
    Standard.TT200: _DANG_THUC_CHUNG,
    Standard.TT99: _DANG_THUC_CHUNG,
}

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

# Mã số dòng theo mẫu biểu Bộ Tài chính, TÁCH THEO CHUẨN.
#
# Mã số đáng tin hơn tên chữ: OCR đọc chữ số gần như không sai, còn chữ
# tiếng Việt có dấu thì hay hỏng ("TỔNG TÀI SẢN" -> "TỖNG TÀISẢN").
#
# CẢNH BÁO 1 — mã số chỉ duy nhất TRONG một mẫu biểu, không phải toàn tài
# liệu. Mã "10" là Doanh thu thuần ở B02 nhưng là Biến động hàng tồn kho ở
# B03; mã "20", "30", "50" cũng trùng tương tự. Nên mỗi field phải đi kèm
# mẫu biểu của nó, và chỉ dùng mã khi trang đúng mẫu đó.
#
# CẢNH BÁO 2 — mã số còn khác nhau GIỮA HAI CHUẨN. Chỗ lệch đã biết: tổng
# tài sản là 270 ở TT200 nhưng 280 ở TT99. Dùng nhầm bảng mã không làm gì
# nổ, nó chỉ lặng lẽ trả về sai dòng — nên nhận diện sai chuẩn phải được
# đếm như một chế độ lỗi riêng.
#
# ==========================================================================
# CHƯA ĐƯỢC NGƯỜI ĐỐI CHIẾU. Hai bảng dưới đây phải kiểm từng dòng với
# Phụ lục IV của văn bản gốc (Thông tư 200/2014/TT-BTC và Thông tư
# 99/2025/TT-BTC), KHÔNG lấy từ bài tóm tắt trên mạng. Sai một mã là toàn
# bộ kết quả identifiability sai mà không có gì báo.
# ==========================================================================
FIELD_LINE_CODES: dict[Standard, dict[str, tuple[str, str]]] = {
    Standard.TT200: {
        "tai_san_ngan_han":     ("B01", "100"),
        "hang_ton_kho":         ("B01", "140"),
        "tai_san_dai_han":      ("B01", "200"),
        "tong_tai_san":         ("B01", "270"),
        "no_phai_tra":          ("B01", "300"),
        "von_chu_so_huu":       ("B01", "400"),
        "doanh_thu_thuan":      ("B02", "10"),
        "gia_von_hang_ban":     ("B02", "11"),
        "loi_nhuan_gop":        ("B02", "20"),
        "loi_nhuan_truoc_thue": ("B02", "50"),
        "loi_nhuan_sau_thue":   ("B02", "60"),
    },
    Standard.TT99: {
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
    },
}

# Dấu hiệu nhận biết trang thuộc mẫu biểu nào.
#
# OCR đọc "Mẫu B 01a - DN" ra đủ kiểu biến thể vì chữ số và chữ cái nhìn
# giống nhau: trên báo cáo VNM, EasyOCR trả về "Mâu B Ola" — số 0 thành
# chữ O, số 1 thành chữ l thường. Nên chữ số nào cũng phải liệt kê kèm
# các chữ cái dễ nhầm với nó.
_ZERO = r"[O0o]"      # 0 hay bị đọc thành O hoa hoặc o thường
_ONE = r"[1lI|]"      # 1 hay bị đọc thành l thường, I hoa, hoặc gạch đứng

# Mẫu biểu cũng mang KÝ HIỆU KHÁC NHAU giữa hai chuẩn: TT200 dùng
# "Mẫu số B 01 - DN", TT99 dùng "Mẫu số B 01a - DN". Khác biệt chỉ là chữ
# "a", nhưng nó đủ để regex của chuẩn này không khớp mẫu của chuẩn kia.
#
# Chiều nguy hiểm là chiều TT200: pattern "B 01" nằm gọn bên trong "B 01a",
# nên nếu không chặn thì trang TT99 sẽ khớp luôn cả marker TT200 và bảng mã
# sai được đem ra dùng. Vì vậy marker TT200 có (?!\s*a) — không được theo
# sau bởi chữ a. Chiều ngược lại không cần chặn vì "B 01a" không nằm trong
# "B 01".
_KHONG_CO_A = r"(?!\s*a)"

FORM_MARKERS: dict[Standard, dict[str, str]] = {
    Standard.TT200: {
        "B01": rf"B\s*{_ZERO}\s*{_ONE}\s*{_KHONG_CO_A}",
        "B02": rf"B\s*{_ZERO}\s*2\s*{_KHONG_CO_A}",
        "B03": rf"B\s*{_ZERO}\s*3\s*{_KHONG_CO_A}",
    },
    Standard.TT99: {
        "B01a": rf"B\s*{_ZERO}\s*{_ONE}\s*a",
        "B02a": rf"B\s*{_ZERO}\s*2\s*a",
        "B03a": rf"B\s*{_ZERO}\s*3\s*a",
    },
}


def line_codes_for(standard: Standard) -> dict[str, tuple[str, str]]:
    """Bảng mã số dòng của một chuẩn. KeyError nếu chuẩn chưa được khai báo."""
    return FIELD_LINE_CODES[standard]


def identities_for(standard: Standard) -> list:
    """Bộ đẳng thức kế toán của một chuẩn."""
    return FIELD_IDENTITIES[standard]


def form_markers_for(standard: Standard) -> dict[str, str]:
    """Dấu hiệu nhận biết mẫu biểu, trong phạm vi một chuẩn."""
    return FORM_MARKERS[standard]


def _bo_dau(text: str) -> str:
    """
    Bỏ dấu tiếng Việt và hạ chữ thường, để so khớp không phụ thuộc dấu.

    OCR làm hỏng dấu một cách có hệ thống trên chữ tiếng Việt, nên liệt kê
    từng biến thể CÓ DẤU là cuộc đuổi bắt không có hồi kết — cách làm của
    FORM_MARKERS chỉ khả thi vì ở đó chuỗi cần khớp là "B 01a", gần như
    không có dấu. Với câu tiếng Việt đầy đủ như "Báo cáo tình hình tài
    chính" thì bỏ dấu cả hai phía rồi mới so là cách rẻ hơn hẳn và phủ
    được mọi biến thể dấu cùng lúc.

    Chữ "đ" phải thay tay: nó là ký tự riêng chứ không phải "d" cộng dấu,
    nên NFD không phân rã được.
    """
    text = text.replace("đ", "d").replace("Đ", "D")
    phan_ra = unicodedata.normalize("NFD", text)
    return "".join(ky_tu for ky_tu in phan_ra if not unicodedata.combining(ky_tu)).lower()


# Dấu hiệu nhận biết CHUẨN — khác với FORM_MARKERS vốn nhận biết MẪU BIỂU.
#
# Dấu hiệu rẻ nhất là việc TT99 đổi tên "Bảng cân đối kế toán" thành "Báo
# cáo tình hình tài chính"; đó là chuỗi nằm ngay tiêu đề trang. Số hiệu
# thông tư là dấu hiệu chắc chắn hơn nhưng chỉ xuất hiện ở trang đầu.
#
# Pattern viết KHÔNG DẤU vì detect_standard() bỏ dấu trước khi so.
STANDARD_MARKERS: dict[Standard, list[str]] = {
    Standard.TT99: [
        r"bao\s*cao\s*tinh\s*hinh\s*tai\s*chinh",
        r"99\s*/\s*2025",
    ],
    Standard.TT200: [
        r"bang\s*can\s*doi\s*ke\s*toan",
        r"200\s*/\s*2014",
    ],
}


def detect_standard(text: str) -> tuple[Standard | None, float]:
    """
    Nhận diện chuẩn mẫu biểu từ text OCR của trang.

    Trả về (chuẩn, độ tin cậy 0..1). Trả (None, 0.0) khi không đủ dấu hiệu
    HOẶC khi hai chuẩn hoà nhau.

    KHÔNG BAO GIỜ tự chọn mặc định khi không chắc. Nhận diện sai chuẩn là
    một chế độ lỗi riêng, và nó lặng lẽ: dùng nhầm bảng mã không làm gì nổ,
    chỉ trả về sai dòng. Nếu hàm này âm thầm đoán bừa thì chế độ lỗi đó
    biến mất khỏi mọi phép đo, và về sau không tách được nó khỏi lỗi đọc
    số. Người gọi phải tự quyết định làm gì với None, và phải ghi lại.

    Trang mục lục nhắc tên cả hai chuẩn là ca có thật, nên khi có dấu hiệu
    của cả hai thì độ tin cậy bị chia đôi, và hoà thì trả None.
    """
    khong_dau = _bo_dau(text)

    diem = {
        chuan: sum(1 for mau in mau_list if re.search(mau, khong_dau))
        for chuan, mau_list in STANDARD_MARKERS.items()
    }

    thang = max(diem, key=lambda chuan: diem[chuan])
    diem_thang = diem[thang]
    diem_thua = max(diem[chuan] for chuan in diem if chuan is not thang)

    if diem_thang == 0:
        print("[STANDARD] Không tìm thấy dấu hiệu chuẩn mẫu biểu nào trong trang")
        return None, 0.0

    if diem_thang == diem_thua:
        print(
            f"[STANDARD] Hoà {diem_thang}-{diem_thua} giữa các chuẩn "
            f"(trang nhắc cả hai?) — không kết luận"
        )
        return None, 0.0

    do_tin_cay = (diem_thang - diem_thua) / len(STANDARD_MARKERS[thang])

    if diem_thua > 0:
        # Có dấu hiệu của chuẩn kia trên cùng trang thì kết luận yếu hẳn đi,
        # dù bên này vẫn nhiều dấu hiệu hơn.
        do_tin_cay *= 0.5
        print(
            f"[STANDARD] Nhận diện {thang} nhưng trang còn dấu hiệu chuẩn khác "
            f"({diem_thang} vs {diem_thua}) — độ tin cậy {do_tin_cay:.2f}"
        )

    return thang, do_tin_cay
