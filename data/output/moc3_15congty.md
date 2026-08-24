MỐC 3 — 14 công ty, 26 hồ sơ, 400 lượt chạy (4 chế độ lỗi × 5 seed)

| Chỉ số | Đề xuất | Baseline 9 | Ai thắng |
|---|---:|---:|---|
| Tỷ lệ lỗi câm sau sửa | 0.005 | 0.006 | đề xuất |
| Tỷ lệ bịa (thoả ràng buộc mà sai) | 0.005 | 0.006 | đề xuất |
| Định vị đúng trường bị lỗi | 0.212 | 0.295 | **baseline 9** |
| Số lượt kết quả thoả ràng buộc | 246 | 340 | — |

Phân bố verdict:

| Verdict | Đề xuất | Baseline 9 |
|---|---:|---:|
| VERIFIED | 106 | 106 |
| REPAIRED | 122 | 234 |
| ABSTAIN | 172 | 60 |

Lý do ABSTAIN — `vo_nghiem` là ca DUY NHẤT chứng minh được

| Lý do | Đề xuất | Baseline 9 |
|---|---:|---:|
| `vuot_tran_thay_doi` | 172 | 60 |

> **KẾT QUẢ NÀY CHƯA KẾT LUẬN ĐƯỢC MỐC 3.** Ba hạn chế đã biết, đều làm
> lợi cho baseline 9 hoặc làm hẹp phạm vi đo:
>
> 1. **Chỉ tổng thể donor là hợp lệ, phần còn lại thì chưa.** Donor nay
>    lấy từ các công ty KHÁC nên phần này đã đúng; nhưng toàn bộ dữ liệu
>    vẫn là doanh nghiệp Mỹ nộp theo US-GAAP, chưa có báo cáo Việt Nam nào.
> 2. **Cột kỳ so sánh rỗng**, nên COL_SHIFT không inject được và nguồn
>    ứng viên chéo kỳ không đóng góp gì. Chỉ 3 trong 4 chế độ lỗi chạy.
> 3. **Chỉ số định vị phạt việc ABSTAIN.** Baseline 9 không bao giờ từ
>    chối trả lời nên luôn có cơ hội định vị đúng, còn phương pháp đề
>    xuất từ chối khi tập ứng viên đóng không chứa cách đọc nào hợp lệ —
>    mà đó chính là hành vi nó được thiết kế để có. Đếm ABSTAIN là
>    'định vị trượt' tức đo mức sẵn sàng đoán, không đo độ đúng.


Bỏ qua (ghi tường minh, không giấu):

- `khong_inject_duoc_col_shift`: 120

