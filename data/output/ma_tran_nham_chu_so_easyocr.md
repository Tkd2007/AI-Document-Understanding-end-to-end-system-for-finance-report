# Ma trận nhầm chữ số đo được — easyocr

Sinh bằng `python src/eval/do_ma_tran_nham_chu_so.py easyocr`. 6 font × 4 biến thể ảnh (sach, mo, nhieu, phan_giai_thap), tổng **1080 lượt đọc ô** và **60 quan sát nhầm chữ số**.

Font đã dùng: `pillow_mac_dinh`, `arial`, `times`, `calibri`, `consolas`, `verdana`. Ghi ra vì phân phối nhầm chữ số PHỤ THUỘC TYPEFACE — lượt đo đầu chỉ dùng font mặc định của Pillow và chỉ thu được ba cặp phân biệt, tức nó đo một bộ hình dạng chữ số chứ không đo OCR.

Chiều của khoá là **(thật → đọc thành)**. Bộ tiêm lỗi tra theo chiều
này; bộ sinh ứng viên tra theo chiều NGƯỢC, vì nó chỉ thấy chữ số đã
đọc ra và phải đoán ngược lại giá trị thật.

Chỉ tính những ô mà chuỗi đọc được dài bằng chuỗi thật, nên đây là
cận dưới — xem docstring `thong_ke_nham_chu_so`.

## Cặp nhầm, xếp theo tần suất

| Thật | Đọc thành | Số lần |
|---|---|---:|
| 9 | 0 | 23 |
| 5 | 3 | 13 |
| 6 | 0 | 8 |
| 0 | 8 | 6 |
| 7 | 1 | 3 |
| 8 | 6 | 3 |
| 9 | 8 | 1 |
| 4 | 1 | 1 |
| 4 | 8 | 1 |
| 1 | 4 | 1 |

## Khối lượng tích luỹ của N cặp đầu bảng

Cột phải là **độ phủ lý thuyết** của bộ sinh ứng viên nếu nó chỉ mang
N cặp đầu: khi bộ tiêm lấy mẫu theo đúng phân phối này, xác suất lỗi
tiêm ra nằm sẵn trong tập ứng viên đúng bằng con số đó. Đây là đại
lượng SUY RA từ số đo, không phải tham số chọn tay.

| N cặp đầu | Khối lượng tích luỹ |
|---:|---:|
| 1 | 0.383 |
| 2 | 0.600 |
| 3 | 0.733 |
| 4 | 0.833 |
| 5 | 0.883 |
| 6 | 0.933 |
| 8 | 0.967 |
| 10 | 1.000 |
| 12 | 1.000 |
| 16 | 1.000 |
| 20 | 1.000 |

Số cặp phân biệt quan sát được: **10** trên tối đa 90 cặp có thể.

## Giới hạn

Đo bằng ảnh **render tổng hợp**, không phải scan tiếng Việt thật. Đây là
mô hình của engine này trên ảnh sạch và ảnh xuống cấp nhân tạo, nên con
số độ phủ suy ra từ nó là con số TẠM và phải đo lại trên tập gold khi
có. Tầng XBRL vì thế lạc quan hơn tài liệu Việt Nam thật ở chế độ lỗi
`digit_substitution`.

