"""
Định vị và sửa lỗi trên tập ứng viên SINH TỪ TÀI LIỆU.

Đây là phần mang đóng góp cốt lõi của cả nghiên cứu, và điều phân biệt nó
với sáu ngành đã giải cùng bài toán này gói gọn trong một câu:

    Mọi công trình trước đều SỬA một tập số cố định. Không công trình nào
    ĐỌC LẠI được nguồn.

Fellegi-Holt điền từ bản ghi donor. Data reconciliation hiệu chỉnh bằng
bình phương tối thiểu có ràng buộc. HoloClean tra từ điển ngoài. Với dữ
liệu khảo sát hay dữ liệu cảm biến thì phiếu gốc và cảm biến không hỏi lại
được, nên giả định đó là bắt buộc.

Với tài liệu thì ảnh gốc VẪN CÒN. Tập ứng viên sửa lỗi vì vậy sinh ra được
từ chính trang giấy, và điều đó vừa mở ra một không gian sửa mà các ngành
kia không có, vừa LOẠI BỎ VỀ MẶT CẤU TRÚC nguy cơ bịa số cho khớp phương
trình: không tổ hợp ứng viên nào làm residual về 0 thì hệ trả ABSTAIN chứ
không thể tự nghĩ ra một con số.
"""
