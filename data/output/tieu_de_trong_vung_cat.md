# Tiêu đề báo cáo có lọt vào vùng bảng đã cắt không

Tài liệu: `data/samples/20260429_VNM_BCTC_DA_SOAT_XET_Q1_2026_RIENG_VN_920896fa41.pdf` — 12 trang đầu.

`fail_open` = YOLO không tìm thấy bảng nào nên pipeline lấy NGUYÊN
TRANG. Trang như vậy nhận diện được là chuyện tình cờ, không chứng
minh gì cho các trang mang bảng.

Hai cột dấu hiệu tách riêng vì chỉ cột TÊN liên quan tới câu hỏi:
`detect_standard()` kết luận được nhờ SỐ HIỆU thông tư trong khi tiêu
đề đã rơi ra ngoài vùng cắt là chuyện có thật, và gộp hai cột lại sẽ
đọc ra kết luận ngược.

| Trang | fail_open | Số vùng | TÊN trong cả trang | TÊN trong vùng cắt | SỐ HIỆU trong vùng cắt | Chuẩn từ vùng cắt | Chuẩn từ cả trang |
|---:|---|---:|---|---|---|---|---|
| 1 | CÓ | 1 | — | — | — | — | — |
| 2 | CÓ | 1 | TT99 | TT99 | — | TT99 (0.50) | TT99 (0.50) |
| 3 | CÓ | 1 | — | — | — | — | — |
| 4 | CÓ | 1 | — | — | — | — | — |
| 5 | CÓ | 1 | TT99 | TT99 | — | TT99 (0.50) | TT99 (0.50) |
| 6 | CÓ | 1 | — | — | — | — | — |
| 7 | CÓ | 1 | TT99 | TT99 | TT99 | TT99 (1.00) | TT99 (1.00) |
| 8 | — | 1 | TT99 | — | TT99 | TT99 (0.50) | TT99 (1.00) |
| 9 | CÓ | 1 | TT99 | TT99 | TT99 | TT99 (1.00) | TT99 (1.00) |
| 10 | — | 1 | — | — | TT99 | TT99 (0.50) | — |
| 11 | CÓ | 1 | — | — | TT99 | TT99 (0.50) | TT99 (0.50) |
| 12 | CÓ | 1 | — | — | — | — | — |

## Dòng chữ mang tên báo cáo, và nó nằm trong hay ngoài vùng cắt

- Trang 2: `BÁO CÁO TÌNH HÌNH TÀI CHÍNH RIÊNG` tại (312, 1255, 1254, 1323) — LỌT VÀO vùng cắt [(0, 0, 2481, 3508)]
- Trang 5: `Việt Nam ("Công ty"), bao gồm báo cáo tình hình tài chính` tại (227, 1277, 1435, 1346) — LỌT VÀO vùng cắt [(0, 0, 2481, 3508)]
- Trang 7: `Báo cáo tình hình tài chính` tại (256, 267, 848, 321) — LỌT VÀO vùng cắt [(0, 0, 2481, 3508)]
- Trang 8: `Báo cáo tình hình tài chính riêng tại ngày 31` tại (259, 254, 1222, 332) — NẰM NGOÀI vùng cắt [(247, 359, 2224, 2741)]
- Trang 9: `Báo cáo tình hình tài chính` tại (252, 260, 843, 320) — LỌT VÀO vùng cắt [(0, 0, 2481, 3508)]

## Chuỗi thật đã khớp trong text vùng cắt

- Trang 2: TT99/ten: 'bao cao tinh hinh tai chinh'
- Trang 5: TT99/ten: 'bao cao tinh hinh tai chinh'
- Trang 7: TT99/ten: 'bao cao tinh hinh tai chinh'; TT99/so_hieu: '99/2025'
- Trang 8: TT99/so_hieu: '99/2025'
- Trang 9: TT99/ten: 'bao cao tinh hinh tai chinh'; TT99/so_hieu: '99/2025'
- Trang 10: TT99/so_hieu: '99/2025'
- Trang 11: TT99/so_hieu: '99/2025'

## Số để chốt hướng đi

- Trang có bảng thật (không fail-open): **2/12**. Phần còn lại YOLO không thấy bảng nào nên pipeline lấy nguyên trang, và câu hỏi vùng cắt không đặt ra ở đó.
- Trang mang bảng mà **TÊN báo cáo lọt vào vùng cắt**: **0/2** ← đây mới là câu trả lời cho tiền đề.
- Trang mang bảng mà `detect_standard()` kết luận được từ text vùng cắt: **2/2**, trong đó **2** kết luận được **nhờ SỐ HIỆU chứ không nhờ tên**.

**Tiền đề ĐÚNG: tên báo cáo không lọt vào vùng cắt trên trang mang bảng nào.** Mọi lần nhận diện được từ vùng cắt đều nhờ số hiệu thông tư, tức nhờ một dấu hiệu KHÁC. Đó là chỗ phải cẩn thận: số hiệu chỉ xuất hiện trên báo cáo lập theo chuẩn mới còn nhắc văn bản ban hành, nên nó có thể vắng mặt hoàn toàn ở tài liệu khác, và mẫu `99\s*/\s*2025` cho `\s*` nuốt cả xuống dòng nên còn khớp oan được. Xem phần chuỗi đã khớp ở trên trước khi tin con số này.

**Một tài liệu không phải là bằng chứng cho mọi tài liệu.** Con số này đo trên đúng một báo cáo của một công ty, theo một chuẩn. Nó đủ để loại một hướng đi hiển nhiên sai, chưa đủ để chốt một hướng là đúng — muốn chốt thì đo lại trên tập gold khi có.


