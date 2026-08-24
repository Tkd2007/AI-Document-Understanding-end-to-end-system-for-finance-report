MỐC 3 — 3 hồ sơ, 45 lượt chạy (4 chế độ lỗi × 5 seed)

| Chỉ số | Đề xuất | Baseline 9 | Ai thắng |
|---|---:|---:|---|
| Tỷ lệ lỗi câm sau sửa | 0.005 | 0.004 | **baseline 9** |
| Tỷ lệ bịa (thoả ràng buộc mà sai) | 0.003 | 0.004 | đề xuất |
| Định vị đúng trường bị lỗi | 0.333 | 0.556 | **baseline 9** |
| Số lượt kết quả thoả ràng buộc | 29 | 45 | — |

Phân bố verdict:

| Verdict | Đề xuất | Baseline 9 |
|---|---:|---:|
| VERIFIED | 7 | 7 |
| REPAIRED | 19 | 38 |
| ABSTAIN | 19 | 0 |

Lý do ABSTAIN — `vo_nghiem` là ca DUY NHẤT chứng minh được

| Lý do | Đề xuất | Baseline 9 |
|---|---:|---:|
| `vuot_tran_thay_doi` | 19 | 0 |

> **KẾT QUẢ NÀY CHƯA KẾT LUẬN ĐƯỢC MỐC 3.** Ba hạn chế đã biết, đều làm
> lợi cho baseline 9 hoặc làm hẹp phạm vi đo:
>
> 1. **Donor vẫn là hồ sơ của CÙNG một công ty.** Fellegi-Holt kinh điển
>    lấy donor từ một tổng thể nhiều thực thể khác nhau; lấy từ báo cáo
>    năm liền kề của chính công ty đó thì donor gần giá trị thật hơn hẳn
>    thực tế. Cần nhiều CIK mới có donor hợp lệ.
> 2. **Cột kỳ so sánh rỗng**, nên COL_SHIFT không inject được và nguồn
>    ứng viên chéo kỳ không đóng góp gì. Chỉ 3 trong 4 chế độ lỗi chạy.
> 3. **Chỉ số định vị phạt việc ABSTAIN.** Baseline 9 không bao giờ từ
>    chối trả lời nên luôn có cơ hội định vị đúng, còn phương pháp đề
>    xuất từ chối khi tập ứng viên đóng không chứa cách đọc nào hợp lệ —
>    mà đó chính là hành vi nó được thiết kế để có. Đếm ABSTAIN là
>    'định vị trượt' tức đo mức sẵn sàng đoán, không đo độ đúng.


Bỏ qua (ghi tường minh, không giấu):

- `khong_inject_duoc_col_shift`: 15

