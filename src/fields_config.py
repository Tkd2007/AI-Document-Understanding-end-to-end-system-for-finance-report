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


# Bộ chỉ tiêu chốt ở MỐC 1 ngày 23/08/2026 — kịch bản D của
# `constraints_scenarios.py`, mở rộng từ 11 lên 21 chỉ tiêu.
#
# Vì sao mở rộng, tóm tắt số đo (chi tiết ở PREREGISTRATION.md mục Sửa đổi):
# với 11 chỉ tiêu thì BA chỉ tiêu có cột toàn 0 trong ma trận ràng buộc —
# hang_ton_kho, loi_nhuan_truoc_thue, loi_nhuan_sau_thue. Cột toàn 0 nghĩa là
# lỗi ở đó không làm residual nhúc nhích, tức vô hình với CẢ H1 (phát hiện)
# lẫn H2 (định vị), chứ không phải chỉ "khó định vị". Bộ 21 chỉ tiêu này đưa
# số chỉ tiêu vô hình về 0.
#
# Đo trên đúng 16 chỉ tiêu của kịch bản C, việc mở rộng sang D nâng trần
# Top-3 từ 0,938 lên 0,975: KHÔNG chỉ tiêu nào xấu đi khi thêm chỉ tiêu.
FIELD_MAP = {
    # --- B01: bảng cân đối kế toán (TT99 gọi là Báo cáo tình hình tài chính) ---
    "tai_san_ngan_han": "Tài sản ngắn hạn",
    "tien_va_tuong_duong_tien": "Tiền và các khoản tương đương tiền",
    "dau_tu_tc_ngan_han": "Đầu tư tài chính ngắn hạn",
    "phai_thu_ngan_han": "Các khoản phải thu ngắn hạn",
    "hang_ton_kho": "Hàng tồn kho",
    # Chỉ TT99 có chỉ tiêu này (mã 150). TT200 không tách nó ra khỏi tài sản
    # ngắn hạn khác — xem FIELDS_ONLY_IN và cảnh báo ở FIELD_LINE_CODES.
    "tai_san_sinh_hoc_ngan_han": "Tài sản sinh học ngắn hạn",
    "tsnh_khac": "Tài sản ngắn hạn khác",
    "tai_san_dai_han": "Tài sản dài hạn",
    "tong_tai_san": "Tổng tài sản",
    "no_phai_tra": "Nợ phải trả",
    "von_chu_so_huu": "Vốn chủ sở hữu",
    "tong_nguon_von": "Tổng cộng nguồn vốn",

    # --- B02: Báo cáo kết quả hoạt động kinh doanh ---
    "doanh_thu_thuan": "Doanh thu thuần",
    "gia_von_hang_ban": "Giá vốn hàng bán",
    "loi_nhuan_gop": "Lợi nhuận gộp",
    "ln_thuan_hdkd": "Lợi nhuận thuần từ hoạt động kinh doanh",
    "ln_khac": "Lợi nhuận khác",
    "loi_nhuan_truoc_thue": "Lợi nhuận trước thuế",
    "thue_tndn_hien_hanh": "Chi phí thuế thu nhập doanh nghiệp hiện hành",
    "thue_tndn_hoan_lai": "Chi phí thuế thu nhập doanh nghiệp hoãn lại",
    "loi_nhuan_sau_thue": "Lợi nhuận sau thuế",
}

# Chỉ tiêu chỉ tồn tại ở MỘT chuẩn. Khai báo tường minh thay vì để suy ra từ
# việc thiếu khoá trong FIELD_LINE_CODES, vì "thiếu vì chuẩn không có chỉ
# tiêu này" và "thiếu vì quên khai báo" là hai chuyện khác hẳn nhau và phải
# phân biệt được — test đối chiếu cấu hình dựa vào đúng bảng này.
FIELDS_ONLY_IN: dict[Standard, set[str]] = {
    Standard.TT99: {"tai_san_sinh_hoc_ngan_han"},
}

# Quy tắc kiểm tra gắn với từng field.
#
#   allow_negative — số âm có phải dấu hiệu đọc sai không? Lợi nhuận âm
#     là doanh nghiệp lỗ, hoàn toàn bình thường. Tổng tài sản âm thì chắc
#     chắn là lỗi.
#   required — field bắt buộc phải có thì kết quả mới được coi là đạt.
#     Không đánh dấu tất cả là required: càng nhiều field bắt buộc thì
#     càng dễ phải fallback VLM chỉ vì một chỉ tiêu phụ không tìm thấy.
#
# KHÔNG mở rộng danh sách required khi thêm chỉ tiêu ở MỐC 1: mười chỉ tiêu
# mới đều là thành phần chi tiết, và nhiều cái vắng mặt hợp lệ trên báo cáo
# thật (TT99 mục 1.2.3 cho phép miễn trình bày chỉ tiêu không có số liệu).
# Đánh dấu chúng required sẽ làm router fallback sang VLM chỉ vì một dòng
# doanh nghiệp không có — đắt tiền mà không mua được gì.
FIELD_RULES = {
    "tai_san_ngan_han":          {"allow_negative": False, "required": False},
    "tien_va_tuong_duong_tien":  {"allow_negative": False, "required": False},
    "dau_tu_tc_ngan_han":        {"allow_negative": False, "required": False},
    "phai_thu_ngan_han":         {"allow_negative": False, "required": False},
    "hang_ton_kho":              {"allow_negative": False, "required": False},
    "tai_san_sinh_hoc_ngan_han": {"allow_negative": False, "required": False},
    "tsnh_khac":                 {"allow_negative": False, "required": False},
    "tai_san_dai_han":           {"allow_negative": False, "required": False},
    "tong_tai_san":              {"allow_negative": False, "required": True},
    "no_phai_tra":               {"allow_negative": False, "required": False},
    "von_chu_so_huu":            {"allow_negative": True,  "required": False},
    "tong_nguon_von":            {"allow_negative": False, "required": False},
    "doanh_thu_thuan":           {"allow_negative": False, "required": True},
    "gia_von_hang_ban":          {"allow_negative": False, "required": False},
    "loi_nhuan_gop":             {"allow_negative": True,  "required": False},
    "ln_thuan_hdkd":             {"allow_negative": True,  "required": False},
    "ln_khac":                   {"allow_negative": True,  "required": False},
    "loi_nhuan_truoc_thue":      {"allow_negative": True,  "required": False},
    # Hai chỉ tiêu thuế cho phép âm vì chính văn bản quy định vậy: TT200
    # Điều 113 mục 3.16 và 3.17 (TT99 mục 3.17 và 3.18) nói số liệu "được
    # ghi vào chỉ tiêu này bằng số âm dưới hình thức ghi trong ngoặc đơn"
    # khi phát sinh bên Nợ — tức khi là THU NHẬP thuế chứ không phải chi phí.
    "thue_tndn_hien_hanh":       {"allow_negative": True,  "required": False},
    "thue_tndn_hoan_lai":        {"allow_negative": True,  "required": False},
    "loi_nhuan_sau_thue":        {"allow_negative": True,  "required": True},
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
# Sáu đẳng thức chung cho cả hai chuẩn. Cái thứ bảy — phân rã Tài sản ngắn
# hạn — KHÁC NHAU giữa hai chuẩn nên khai báo riêng bên dưới.
#
# Mọi đẳng thức ở đây đều đã đối chiếu nguyên văn với Công báo; mã số ghi
# kèm để tra ngược lại được. Bài học từ Mốc 1: đừng để đẳng thức GIẢ THUYẾT
# chạy vào cấu hình, kể cả khi nó hợp lý về kế toán.
_DANG_THUC_CHUNG = [
    (
        ["tai_san_ngan_han", "tai_san_dai_han"],
        "tong_tai_san",
        "Tài sản ngắn hạn + Tài sản dài hạn phải bằng Tổng tài sản",
    ),
    # Tách làm hai bước đúng như văn bản khai báo, thay vì gộp thành
    # `nợ + vốn = tổng tài sản` như trước. Văn bản viết `Mã số 440 = Mã số
    # 300 + Mã số 400` ở phần mô tả chỉ tiêu, rồi viết RIÊNG trong một khối
    # kẻ khung `Tổng cộng Tài sản = Tổng cộng Nguồn vốn`. Gộp hai thành một
    # vẫn đúng về toán nhưng vứt đi Tổng cộng nguồn vốn — một con số in sẵn
    # ở cuối bảng cân đối. Giữ lại nó làm chính nó ĐỊNH VỊ ĐƯỢC, và đó là
    # bước có tỷ lệ trao đổi tốt nhất trong cả năm kịch bản ở Mốc 1.
    (
        ["no_phai_tra", "von_chu_so_huu"],
        "tong_nguon_von",
        "Nợ phải trả + Vốn chủ sở hữu phải bằng Tổng cộng nguồn vốn (mã 440)",
    ),
    (
        ["tong_nguon_von"],
        "tong_tai_san",
        "Tổng cộng nguồn vốn phải bằng Tổng cộng tài sản",
    ),
    (
        ["gia_von_hang_ban", "loi_nhuan_gop"],
        "doanh_thu_thuan",
        "Giá vốn hàng bán + Lợi nhuận gộp phải bằng Doanh thu thuần",
    ),
    # Hai đẳng thức B02 dưới đây kéo loi_nhuan_truoc_thue và
    # loi_nhuan_sau_thue ra khỏi tình trạng CỘT TOÀN 0. Trước Mốc 1, hai chỉ
    # tiêu này không nằm trong đẳng thức nào — sai bao nhiêu cũng không ràng
    # buộc nào thấy, dù chúng là đầu ra người dùng thật sự cần.
    (
        ["ln_thuan_hdkd", "ln_khac"],
        "loi_nhuan_truoc_thue",
        "Lợi nhuận thuần từ HĐKD + Lợi nhuận khác phải bằng Lợi nhuận trước thuế",
    ),
    # Văn bản viết `Mã số 60 = Mã số 50 - (Mã số 51 + Mã số 52)`. Chuyển vế
    # thành dạng cộng để khớp cấu trúc (danh sách cộng, tổng) mà ma trận A
    # dựng trên đó.
    (
        ["loi_nhuan_sau_thue", "thue_tndn_hien_hanh", "thue_tndn_hoan_lai"],
        "loi_nhuan_truoc_thue",
        "Lợi nhuận sau thuế + chi phí thuế hiện hành + hoãn lại "
        "phải bằng Lợi nhuận trước thuế",
    ),
]

# Phân rã Tài sản ngắn hạn — CHỖ HAI CHUẨN KHÁC NHAU THẬT.
#
#   TT200: Mã số 100 = 110 + 120 + 130 + 140 + 150
#   TT99:  Mã số 100 = 110 + 120 + 130 + 140 + 150 + 160
#
# TT99 chèn thêm "Tài sản sinh học ngắn hạn" và cho nó mã 150, đẩy "Tài sản
# ngắn hạn khác" từ 150 sang 160. Đây là đẳng thức duy nhất trong cả cấu hình
# mà hai chuẩn KHÔNG đẳng cấu — mọi đẳng thức khác giống hệt nhau.
#
# Bỏ hạng tử tài sản sinh học đi thì với doanh nghiệp nông nghiệp hoặc chăn
# nuôi, đẳng thức TT99 sẽ lệch đúng bằng giá trị đàn vật nuôi hoặc vườn cây —
# một cảnh báo SAI, và sai ở đúng nhóm doanh nghiệp mà tập gold nhắm tới.
_PHAN_RA_TSNH_TT200 = (
    ["tien_va_tuong_duong_tien", "dau_tu_tc_ngan_han", "phai_thu_ngan_han",
     "hang_ton_kho", "tsnh_khac"],
    "tai_san_ngan_han",
    "Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn "
    "(TT200: mã 100 = 110+120+130+140+150)",
)
_PHAN_RA_TSNH_TT99 = (
    ["tien_va_tuong_duong_tien", "dau_tu_tc_ngan_han", "phai_thu_ngan_han",
     "hang_ton_kho", "tai_san_sinh_hoc_ngan_han", "tsnh_khac"],
    "tai_san_ngan_han",
    "Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn "
    "(TT99: mã 100 = 110+120+130+140+150+160)",
)

# Đẳng thức tách theo CHUẨN mẫu biểu.
#
# Việc tách theo chuẩn từng là biện pháp phòng xa — hai chuẩn khi đó dùng
# chung đúng một bộ đẳng thức. Sau khi đối chiếu Công báo ở Mốc 1 thì nó
# thành cần thiết thật: phân rã Tài sản ngắn hạn khác nhau giữa hai chuẩn.
#
# ĐÃ ĐỐI CHIẾU 23/08/2026 với Công báo số 287+288 và 289+290 (TT200) và số
# 1577+1578, 1579+1580, 1581+1582 (TT99). Bảng đối chiếu từng dòng ở
# MOC1-DOI-CHIEU.md mục 3.
FIELD_IDENTITIES: dict[Standard, list] = {
    Standard.TT200: [*_DANG_THUC_CHUNG, _PHAN_RA_TSNH_TT200],
    Standard.TT99: [*_DANG_THUC_CHUNG, _PHAN_RA_TSNH_TT99],
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


# ---------------------------------------------------------------------------
# Đơn vị tính — mỏ neo tuyệt đối
# ---------------------------------------------------------------------------
#
# Vì sao phần này bắt buộc, không phải tuỳ chọn: hệ ràng buộc kế toán là hệ
# THUẦN NHẤT (Ax = 0), nên mọi bội vô hướng của nghiệm cũng là nghiệm. Với
# lỗi đọc sai đơn vị, δ = (c−1)x*, ta có Aδ = (c−1)Ax* = 0 — residual bằng 0
# tuyệt đối. Đọc "triệu đồng" thành "đồng" khiến MỌI con số sai gấp một
# triệu lần trong khi bảng cân đối vẫn cân hoàn hảo và mọi đẳng thức vẫn
# khớp tới từng đồng.
#
# Không đẳng thức nào bắt được ca này. Chỉ có hai thứ bắt được: đọc đúng
# dòng khai báo đơn vị ở header bảng, và biên độ lớn tuyệt đối bên dưới.

# Khoá của đơn vị tính trong kết quả trích xuất.
#
# CỐ Ý KHÔNG nằm trong FIELD_MAP: validate_result() chạy coerce_number()
# trên mọi khoá của FIELD_MAP, nên chuỗi "triệu đồng" sẽ thành None kèm
# cảnh báo "không đọc được thành số". Nó là dữ liệu META về cách đọc cả
# bảng, không phải một chỉ tiêu tài chính.
UNIT_KEY = "don_vi_tinh"

# Hệ số quy đổi về đồng. Khoá là dạng chuẩn hoá mà parse_unit() trả về.
UNIT_MULTIPLIERS: dict[str, int] = {
    "đồng": 1,
    "nghìn đồng": 1_000,
    "triệu đồng": 1_000_000,
    "tỷ đồng": 1_000_000_000,
}

# Từ khoá bậc độ lớn, tra trên chuỗi ĐÃ BỎ DẤU. Xếp theo thứ tự thử.
_TU_KHOA_BAC = (
    ("ty", "tỷ đồng"),
    ("trieu", "triệu đồng"),
    ("nghin", "nghìn đồng"),
    ("ngan", "nghìn đồng"),
)

# Dấu hiệu cho biết chuỗi này THỰC SỰ nói về tiền tệ.
#
# Phải kiểm trước khi dò bậc độ lớn, nếu không thì một chuỗi rác bất kỳ có
# chứa "ngắn" (bỏ dấu thành "ngan") sẽ bị đọc thành "nghìn đồng".
_TU_KHOA_TIEN_TE = ("dong", "vnd")


def parse_unit(raw: str | None) -> tuple[int | None, str]:
    """
    Đọc dòng khai báo đơn vị tính, trả về (hệ số nhân, dạng chuẩn hoá).

    Trả (None, "") khi KHÔNG đọc được — và nơi gọi PHẢI xử lý trường hợp
    này, tuyệt đối không được ngầm coi là "đồng". Mặc định im lặng chính là
    lỗi mà cả mục này sinh ra để chống: nó biến một tài liệu chưa biết bậc
    độ lớn thành một tài liệu trông như đã biết.

    Chuỗi thật trên báo cáo rất đa dạng — "VND", "Đơn vị: triệu VNĐ",
    "(Đơn vị tính: Triệu đồng)" — nên phải bỏ dấu và hạ chữ thường trước
    khi tra, cùng cách detect_standard() làm.
    """
    if not raw:
        return None, ""

    khong_dau = _bo_dau(str(raw))

    # Cụm "đơn vị tính" bỏ dấu thành "don vi tinh", KHÔNG chứa "dong", nên
    # điều kiện này không bị chính cái nhãn của nó làm cho luôn đúng.
    if not any(re.search(rf"\b{tu}\b", khong_dau) for tu in _TU_KHOA_TIEN_TE):
        return None, ""

    for tu_khoa, dang_chuan in _TU_KHOA_BAC:
        if re.search(rf"\b{tu_khoa}\b", khong_dau):
            return UNIT_MULTIPLIERS[dang_chuan], dang_chuan

    # Có nói về tiền nhưng không có bậc độ lớn nào -> đơn vị là đồng.
    return UNIT_MULTIPLIERS["đồng"], "đồng"


# Biên độ lớn cho tong_tai_san SAU khi đã quy đổi về đồng.
#
# Đây là mỏ neo tuyệt đối: đẳng thức kế toán luôn cân bất kể đơn vị, nên
# chỉ một biên trên GIÁ TRỊ TUYỆT ĐỐI mới bắt được ca đọc nhầm đơn vị.
#
# Khoảng 1e10 đến 1e15 VND (10 tỷ tới 1 triệu tỷ) chọn cho rất rộng, đủ phủ
# từ doanh nghiệp niêm yết nhỏ nhất tới VIC/VCB. Mục tiêu là bắt lệch CẢ BẬC
# ĐỘ LỚN (sai số nhân 1e3, 1e6, 1e9), không phải đánh giá quy mô doanh
# nghiệp — biên hẹp sẽ báo oan hàng loạt.
#
# CẦN HIỆU CHỈNH LẠI SAU PILOT: hai con số này hiện dựa trên suy luận về
# phổ doanh nghiệp niêm yết, chưa dựa trên phân phối đo được. Phải kiểm lại
# trên tập gold nhiều công ty rồi mới chốt.
TOTAL_ASSETS_BOUNDS = (1e10, 1e15)


def empty_result() -> dict:
    """
    Khung kết quả rỗng: mọi chỉ tiêu cộng thêm khoá đơn vị tính.

    Gom vào một chỗ vì cả router.py lẫn extract_vlm.py đều dựng khung này,
    và trước đây cả hai đều dựng bằng {key: None for key in FIELD_MAP} —
    tức là khoá đơn vị tính do VLM trả về sẽ bị vứt lặng lẽ ở bước merge.
    """
    khung = {key: None for key in FIELD_MAP}
    khung[UNIT_KEY] = None
    return khung

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
    "tien_va_tuong_duong_tien": [
        "Tiền và các khoản tương đương tiền",
        "Tiền và tương đương tiền",
    ],
    "dau_tu_tc_ngan_han": [
        "Đầu tư tài chính ngắn hạn",
        "Các khoản đầu tư tài chính ngắn hạn",
    ],
    "phai_thu_ngan_han": [
        "Các khoản phải thu ngắn hạn",
        "Phải thu ngắn hạn",
    ],
    "hang_ton_kho": [
        "Hàng tồn kho",
    ],
    "tai_san_sinh_hoc_ngan_han": [
        "Tài sản sinh học ngắn hạn",
    ],
    "tsnh_khac": [
        "Tài sản ngắn hạn khác",
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
    "tong_nguon_von": [
        "Tổng cộng nguồn vốn",
        "Tổng nguồn vốn",
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
    "ln_thuan_hdkd": [
        "Lợi nhuận thuần từ hoạt động kinh doanh",
        "Lợi nhuận thuần từ HĐKD",
    ],
    "ln_khac": [
        "Lợi nhuận khác",
    ],
    "loi_nhuan_truoc_thue": [
        "Tổng lợi nhuận kế toán trước thuế",
        "Lợi nhuận kế toán trước thuế",
        "Lợi nhuận trước thuế",
    ],
    "thue_tndn_hien_hanh": [
        "Chi phí thuế thu nhập doanh nghiệp hiện hành",
        "Chi phí thuế TNDN hiện hành",
    ],
    "thue_tndn_hoan_lai": [
        "Chi phí thuế thu nhập doanh nghiệp hoãn lại",
        "Chi phí thuế TNDN hoãn lại",
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
# ĐÃ ĐỐI CHIẾU 23/08/2026 với Công báo, từng dòng một. TT200 ở số 287+288
# (Điều 112, 113); TT99 ở số 1577+1578 (Phụ lục IV Mục 1 — biểu mẫu) và
# 1579+1580 (nội dung và phương pháp lập). Bảng đối chiếu ở
# MOC1-DOI-CHIEU.md mục 3.1.
#
# BA MÃ MANG NGHĨA KHÁC NHAU GIỮA HAI CHUẨN — đây là nguồn lỗi câm, vì tra
# nhầm bảng mã không làm gì nổ, nó chỉ lặng lẽ trả về một con số HỢP LỆ của
# một chỉ tiêu hoàn toàn khác:
#
#   mã 270 — TT200: Tổng cộng tài sản. TT99: Tài sản dài hạn khác
#   mã 150 — TT200: Tài sản ngắn hạn khác. TT99: Tài sản sinh học ngắn hạn
#   mã 142 — TT200: (thuộc nhóm khác). TT99: Dự phòng giảm giá hàng tồn kho
#            (TT200 để dự phòng ở mã 149)
#
# Vì vậy `standard` là tham số BẮT BUỘC của extract_field_by_code(), không
# có giá trị mặc định.
# ==========================================================================
FIELD_LINE_CODES: dict[Standard, dict[str, tuple[str, str]]] = {
    Standard.TT200: {
        "tai_san_ngan_han":          ("B01", "100"),
        "tien_va_tuong_duong_tien":  ("B01", "110"),
        "dau_tu_tc_ngan_han":        ("B01", "120"),
        "phai_thu_ngan_han":         ("B01", "130"),
        "hang_ton_kho":              ("B01", "140"),
        "tsnh_khac":                 ("B01", "150"),
        "tai_san_dai_han":           ("B01", "200"),
        "tong_tai_san":              ("B01", "270"),
        "no_phai_tra":               ("B01", "300"),
        "von_chu_so_huu":            ("B01", "400"),
        "tong_nguon_von":            ("B01", "440"),
        "doanh_thu_thuan":           ("B02", "10"),
        "gia_von_hang_ban":          ("B02", "11"),
        "loi_nhuan_gop":             ("B02", "20"),
        "ln_thuan_hdkd":             ("B02", "30"),
        "ln_khac":                   ("B02", "40"),
        "loi_nhuan_truoc_thue":      ("B02", "50"),
        "thue_tndn_hien_hanh":       ("B02", "51"),
        "thue_tndn_hoan_lai":        ("B02", "52"),
        "loi_nhuan_sau_thue":        ("B02", "60"),
    },
    Standard.TT99: {
        "tai_san_ngan_han":          ("B01", "100"),
        "tien_va_tuong_duong_tien":  ("B01", "110"),
        "dau_tu_tc_ngan_han":        ("B01", "120"),
        "phai_thu_ngan_han":         ("B01", "130"),
        "hang_ton_kho":              ("B01", "140"),
        # Mã 150 ở TT99 KHÔNG phải tài sản ngắn hạn khác — xem cảnh báo trên.
        "tai_san_sinh_hoc_ngan_han": ("B01", "150"),
        "tsnh_khac":                 ("B01", "160"),
        "tai_san_dai_han":           ("B01", "200"),
        "tong_tai_san":              ("B01", "280"),
        "no_phai_tra":               ("B01", "300"),
        "von_chu_so_huu":            ("B01", "400"),
        "tong_nguon_von":            ("B01", "440"),
        "doanh_thu_thuan":           ("B02", "10"),
        "gia_von_hang_ban":          ("B02", "11"),
        "loi_nhuan_gop":             ("B02", "20"),
        "ln_thuan_hdkd":             ("B02", "30"),
        "ln_khac":                   ("B02", "40"),
        "loi_nhuan_truoc_thue":      ("B02", "50"),
        "thue_tndn_hien_hanh":       ("B02", "51"),
        "thue_tndn_hoan_lai":        ("B02", "52"),
        "loi_nhuan_sau_thue":        ("B02", "60"),
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

# HẬU TỐ "a"/"b" KHÔNG PHÂN BIỆT THÔNG TƯ — nó phân biệt KỲ BÁO CÁO.
#
# Bản trước ghi "TT200 dùng B 01 - DN, TT99 dùng B 01a - DN" và cài một
# lookahead (?!\s*a) để marker TT200 không khớp trang TT99. Đối chiếu Công
# báo số 289+290 (TT200) cho thấy điều đó sai: TT200 dùng ĐỦ CẢ ba ký hiệu
# B01-DN, B01a-DN và B01b-DN. Nguyên văn tại chỗ khai báo biểu mẫu:
#
#     7. Bảng cân đối kế toán giữa niên độ (dạng đầy đủ) — Mẫu số B01a-DN
#
# Tức: không hậu tố = báo cáo NĂM, "a" = giữa niên độ dạng đầy đủ (báo cáo
# QUÝ), "b" = giữa niên độ dạng tóm lược. Và TT200 nói rõ biểu mẫu giữa niên
# độ dùng CÙNG BỘ MÃ SỐ với biểu mẫu năm.
#
# Hậu quả của bản cũ: marker TT200 trượt mọi trang B01a-DN, tức trượt mọi
# báo cáo QUÝ theo TT200 — đúng loại tài liệu dự án xử lý, kể cả báo cáo VNM
# Q1/2026 dùng làm mẫu. Khi marker trượt thì extract_field_by_code() trả
# None và đường dự phòng theo mã số tắt hẳn, im lặng, không cảnh báo.
#
# VÌ SAO MARKER KHÔNG CẦN PHÂN BIỆT CHUẨN CHÚT NÀO: chuẩn đã được
# detect_standard() xác định từ TÊN báo cáo ("Bảng cân đối kế toán" của
# TT200 so với "Báo cáo tình hình tài chính" của TT99 — dấu hiệu này đã đối
# chiếu và đúng), và extract_field_by_code() nhận `standard` làm tham số bắt
# buộc. Nên marker chỉ còn một việc: phân biệt B01 với B02 với B03 TRONG
# một chuẩn ĐÃ BIẾT. Cơ chế lookahead cũ đang giải một bài toán mà chỗ khác
# đã giải rồi, và giải sai.
#
# Pattern dừng ngay sau chữ số nên nó khớp cả "B01", "B01a" lẫn "B01b" —
# đúng ý, vì cả ba đều là cùng một biểu mẫu ở ba kỳ khác nhau.
FORM_MARKERS: dict[str, str] = {
    "B01": rf"B\s*{_ZERO}\s*{_ONE}",
    "B02": rf"B\s*{_ZERO}\s*2",
    "B03": rf"B\s*{_ZERO}\s*3",
}


def line_codes_for(standard: Standard) -> dict[str, tuple[str, str]]:
    """Bảng mã số dòng của một chuẩn. KeyError nếu chuẩn chưa được khai báo."""
    return FIELD_LINE_CODES[standard]


def identities_for(standard: Standard) -> list:
    """Bộ đẳng thức kế toán của một chuẩn."""
    return FIELD_IDENTITIES[standard]


def fields_for(standard: Standard) -> list[str]:
    """
    Các chỉ tiêu THẬT SỰ tồn tại ở một chuẩn, giữ nguyên thứ tự FIELD_MAP.

    Dùng cái này thay vì `list(FIELD_MAP)` ở mọi chỗ dựng ma trận ràng buộc.
    Lý do: FIELD_MAP là hợp của cả hai chuẩn, nên dựng ma trận TT200 trên
    toàn bộ FIELD_MAP sẽ kèm theo `tai_san_sinh_hoc_ngan_han` — một chỉ tiêu
    TT200 không có. Cột của nó toàn 0, và báo cáo identifiability sẽ liệt kê
    nó vào nhóm "không được ràng buộc nào bảo vệ", tức bịa ra một điểm yếu
    không tồn tại và làm sai luôn số chiều không gian null của TT200.
    """
    rieng_chuan_khac = {
        field
        for chuan, fields in FIELDS_ONLY_IN.items()
        for field in fields
        if chuan is not standard
    }
    return [field for field in FIELD_MAP if field not in rieng_chuan_khac]


def marker_for_form(form: str) -> str | None:
    """
    Dấu hiệu nhận biết một mẫu biểu, hoặc None nếu mẫu chưa khai báo.

    KHÔNG nhận `standard`: ký hiệu mẫu biểu giống nhau ở cả hai Thông tư,
    và việc phân biệt chuẩn đã do detect_standard() làm bằng tên báo cáo.
    Nhận thêm tham số rồi bỏ qua nó sẽ khiến người gọi tưởng marker có phân
    biệt chuẩn — xem chú thích ở FORM_MARKERS.
    """
    return FORM_MARKERS.get(form)


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
