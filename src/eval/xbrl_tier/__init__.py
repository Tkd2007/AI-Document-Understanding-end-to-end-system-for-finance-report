"""
Tầng đánh giá XBRL — nơi H2 và H3 có power.

VÌ SAO TẦNG NÀY TỒN TẠI, gói trong một phép tính: tập gold 60 tài liệu cho
khoảng 1500 trường, và nếu tỷ lệ lỗi là 5–15% thì chỉ có 75–225 lỗi. Nhưng
H2 và H3 đo TRÊN SỐ LỖI chứ không phải trên 1500 trường. Với 75 quan sát,
khoảng tin cậy 95% cho một tỷ lệ quanh 0,6 rộng chừng ±0,11 — đủ để nói
"phương pháp này chạy được", không đủ để nói "hơn baseline 5 điểm". Muốn sai
số ±0,05 cần khoảng 380 quan sát.

Hồ sơ SEC kèm calculation linkbase: một bản ghi máy đọc nói rõ dòng nào cộng
vào tổng nào và với dấu gì. Ground truth vì thế hoàn hảo và miễn phí, trên
hàng nghìn tài liệu. Nên tầng XBRL không phải mục "nếu còn thời gian" — nó
là ĐIỀU KIỆN để H2 và H3 có power.

PHÂN VAI GIỮA HAI TẦNG, và đây là lập luận nên viết thẳng vào paper:

    tầng XBRL          — POWER:    đo hiệu số giữa các phương pháp
    tầng gold Việt Nam — VALIDITY: chứng minh kết quả đúng trên dữ liệu thật

Điểm yếu của mỗi tầng đúng là điểm mạnh của tầng kia. Lỗi inject ở tầng XBRL
không giống lỗi thật; tầng gold thì lỗi tự nhiên nhưng không đủ mẫu.

Sáu module:

    fetch    — tải hồ sơ từ EDGAR (SCRIPT CHO NGƯỜI DÙNG, container không
               có mạng tới sec.gov)
    facts    — companyfacts sang bảng, chỉ lấy fact CÙNG MỘT hồ sơ
    linkbase — calculation linkbase sang đẳng thức và ma trận A
    table    — cấu trúc bảng hai cột kỳ, thứ mà lỗi lệch dòng/cột cần
    render   — bảng sang ảnh, kèm bbox từng ô
    inject   — inject lỗi có kiểm soát theo taxonomy ở mục 3.1 proposal

Tầng này còn cho phép so TRỰC TIẾP với FinVerBench và VeriFin trên cùng loại
dữ liệu, và nhờ đó biến tiếng Việt từ "đóng góp chính" thành "ca kiểm chứng
khó nhất" — khung duy nhất bán được ở venue quốc tế.

PHÂN BIỆT VỚI SynFinTabs, phải giữ khi trích dẫn họ: SynFinTabs có 100.000
bảng tài chính tổng hợp kèm bbox từng ô, nhưng nội dung là số NGẪU NHIÊN nên
không đẳng thức kế toán nào đúng trên đó. Toàn bộ giá trị của tầng này nằm ở
chỗ giữ được identity thật.
"""
