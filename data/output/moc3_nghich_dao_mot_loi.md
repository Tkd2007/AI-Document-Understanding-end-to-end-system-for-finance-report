# Ràng buộc tự chốt giá trị, hay donor đoán trúng — phép đo phân xử

26 hồ sơ, cùng danh sách và cùng seed với `moc3.chay()`.

| Chế độ lỗi | Lượt | Thật bằng 0 | Donor khớp | Ràng buộc CHỐT ĐÚNG | Không chốt | Cột bằng 0 |
|---|---:|---:|---:|---:|---:|---:|
| `col_shift` | 130 | 0 | 0 | **0.585** | 0.146 | 0.269 |
| `digit_substitution` | 130 | 0 | 0 | **0.608** | 0.146 | 0.246 |
| `row_shift` | 130 | 0 | 0 | **0.608** | 0.146 | 0.246 |
| `sign` | 130 | 0 | 0 | **0.608** | 0.146 | 0.246 |

**Đọc bảng này thế nào.** Cột *Ràng buộc CHỐT ĐÚNG* là tỷ lệ lượt mà
residual nằm trọn trên phương cột của trường bị lỗi, nên nghịch đảo cho
lại đúng giá trị thật tới từng chữ số. Ở những lượt đó, MỌI bộ giải liên
tục lấy lại được đáp án mà không cần đọc lại tài liệu — trần trên của cái
mà baseline 9 có thể đạt, và cũng là phần mà việc đọc lại nguồn không
đóng góp gì thêm.

Hai cột *Thật bằng 0* và *Donor khớp* là giả thuyết ĐẦU TIÊN, đã bị chính
phép đo này bác. Giữ lại trong bảng để lần sau không ai đi kiểm lại.

**Hệ quả cho lượt chạy tới.** Tầng XBRL tiêm đúng một lỗi mỗi lượt, mà
lỗi đơn định vị được chính là ca phép nghịch đảo giải trọn. Muốn đo đúng
phần mà việc đọc lại nguồn đóng góp thì phải tiêm NHIỀU HƠN MỘT lỗi, nơi
hệ trở nên dưới xác định và ràng buộc thôi chốt được giá trị.
