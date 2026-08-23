# Đo engine OCR trên ô số — easyocr

Sinh bằng `python src/eval/ocr_compare.py easyocr`. Bảng tổng hợp 50 ô, phổ độ lớn 4–13 chữ số, có số âm in trong ngoặc và ô trống.

Cột **Levenshtein** là chỉ số Ajayi et al. dùng, đo ở mức KÝ TỰ. Cột **Đúng con số** đo ở mức GIÁ TRỊ. Khoảng cách giữa hai cột chính là thứ đáng đọc: một chữ số sai không phải là 'gần đúng' với một con số tài chính.

| Engine | Ảnh | N ô | Levenshtein | Đúng con số | Không ra số |
|---|---|---:|---:|---:|---:|
| easyocr | sach | 45 | 0.999 | 0.978 | 0.022 |
| easyocr | mo | 45 | 1.000 | 1.000 | 0.000 |
| easyocr | nhieu | 45 | 1.000 | 1.000 | 0.000 |
| easyocr | phan_giai_thap | 45 | 0.934 | 0.467 | 0.000 |

## Cặp chữ số bị đọc nhầm

Chỉ tính những ô mà chuỗi đọc được dài bằng chuỗi thật, nên đây là cận dưới. Bảng này là dữ liệu đầu vào để hiệu chỉnh bảng cặp hay nhầm trong `src/repair/candidates.py` — **chưa được áp vào**, xem ghi chú trong HANDOFF.

| Thật | Đọc thành | Số lần |
|---|---|---:|
| 9 | 0 | 23 |
| 6 | 0 | 8 |
| 9 | 8 | 1 |
