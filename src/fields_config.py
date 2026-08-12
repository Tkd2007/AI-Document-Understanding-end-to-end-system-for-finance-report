"""
Single source of truth cho các chỉ tiêu cần trích xuất.

FIELD_MAP là danh sách field chuẩn, dùng chung cho cả hai nhánh: nhánh
VLM đưa thẳng vào prompt, nhánh regex dùng làm schema kết quả.

FIELD_ALIASES và FIELD_EXCLUDE chỉ phục vụ nhánh regex, vì regex khớp
chữ theo mặt chữ nên phải liệt kê sẵn mọi cách gọi. Nhánh VLM không cần
hai bảng này — model tự hiểu ngữ nghĩa của dòng.
"""

FIELD_MAP = {
    "tong_tai_san": "Tổng tài sản",
    "doanh_thu_thuan": "Doanh thu thuần",
    "loi_nhuan_sau_thue": "Lợi nhuận sau thuế",
}

# Các cách gọi khác nhau của cùng một chỉ tiêu trong báo cáo thật.
#
# THỨ TỰ QUAN TRỌNG: extract_field() dừng ở alias đầu tiên tìm thấy, nên
# alias cụ thể phải đứng trước alias chung chung. Ví dụ nếu để "Lợi nhuận
# sau thuế" lên trước "Lợi nhuận sau thuế TNDN" thì nó sẽ vớ phải dòng
# "Lợi nhuận sau thuế chưa phân phối" trên bảng cân đối kế toán — một
# chỉ tiêu hoàn toàn khác nhưng trùng tiền tố.
FIELD_ALIASES = {
    "tong_tai_san": [
        "Tổng cộng tài sản",
        "Tổng tài sản",
    ],
    "doanh_thu_thuan": [
        "Doanh thu thuần về bán hàng và cung cấp dịch vụ",
        # OCR hay nuốt chữ ở các nhãn dài, nên cần thêm một biến thể ngắn
        # vẫn đủ đặc trưng để không lẫn với dòng doanh thu trong thuyết minh.
        "Doanh thu thuần về bán",
        "Doanh thu thuần",
    ],
    "loi_nhuan_sau_thue": [
        "Lợi nhuận sau thuế thu nhập doanh nghiệp",
        "Lợi nhuận sau thuế TNDN",
        "Lợi nhuận sau thuế",
    ],
}

# Cụm từ khiến một match bị loại. Được kiểm tra trên đoạn text nằm giữa
# nhãn và con số, dùng để phân biệt các chỉ tiêu chung tiền tố mà alias
# ở trên chưa tách được.
FIELD_EXCLUDE = {
    "loi_nhuan_sau_thue": [
        "chưa phân",        # "Lợi nhuận sau thuế chưa phân phối" (bảng cân đối)
        "được trích chia",  # "...được trích chia cổ tức cho các cổ đông"
    ],
}


# Chỉ tiêu mà giá trị âm là dấu hiệu bất thường. Lợi nhuận sau thuế cố ý
# KHÔNG nằm ở đây: doanh nghiệp lỗ là chuyện bình thường, và prompt VLM
# được yêu cầu giữ nguyên dấu âm nên số âm ở đó là kết quả đúng.
NON_NEGATIVE_FIELDS = ("tong_tai_san", "doanh_thu_thuan")