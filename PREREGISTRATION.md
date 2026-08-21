# Đăng ký trước giả thuyết và kế hoạch phân tích

**Dự án:** Re-Read, Don't Repair — Constraint-Based Error Localization with
Document-Grounded Candidates for Financial Statement Extraction

Tài liệu này được commit vào repo **trước khi chạy bất kỳ thí nghiệm nào**.
Dấu thời gian của git chính là bằng chứng.

Mục đích không phải thủ tục hành chính. Nó ngăn chính tác giả rơi vào
HARKing — đổi giả thuyết sau khi đã nhìn thấy dữ liệu — và cho phép viết
một câu rất mạnh trong paper: *các giả thuyết và kế hoạch phân tích được
đăng ký trước khi thu thập dữ liệu.*

Mọi thay đổi sau này phải ghi thành mục "Sửa đổi" ở cuối file, kèm ngày và
lý do, chứ **không được sửa đè lên nội dung gốc**. Sửa đè làm mất toàn bộ
giá trị của việc đăng ký trước.

---

## 0. Bối cảnh tối thiểu

Báo cáo tài chính dư thừa về mặt số học: cùng một thông tin xuất hiện lại
qua đẳng thức kế toán, quan hệ tổng–thành phần, và cột kỳ trước. Khi trích
xuất từ PDF bằng OCR hoặc VLM, sự dư thừa đó là tín hiệu duy nhất cho biết
kết quả có sai hay không, vì tại thời điểm suy luận không có nhãn để đối
chiếu.

Ký hiệu dùng xuyên suốt:

- `x* ∈ ℝⁿ` — vector giá trị THẬT của n chỉ tiêu, đã quy đổi về đồng
- `x̂ = x* + δ` — vector giá trị TRÍCH XUẤT được
- `A` — ma trận ràng buộc, mỗi dòng một đẳng thức kế toán
- `r = A x̂` — residual

Hệ ràng buộc kế toán là **thuần nhất**: `A x* = 0`. Do đó `r = A δ`.

---

## 1. Bốn giả thuyết

### H0 — Identifiability (không cần một nhãn nào)

**Phát biểu.** Với đồ thị ràng buộc dựng từ mẫu biểu B01a/B02a theo Thông
tư 200/2014/TT-BTC và Thông tư 99/2025/TT-BTC, tồn tại các mẫu lỗi
`δ ∈ null(A)` mà không phương pháp nào dựa trên ràng buộc có thể phát hiện.
Tập đó đặc trưng hoá được, và xác định được bộ trường tối thiểu để mọi lỗi
một-trường trở nên định vị được.

**Chỉ số chính, chốt trước:**

| Chỉ số | Định nghĩa |
|---|---|
| `rank(A)` | Hạng ma trận ràng buộc |
| `dim null(A)` | Số chiều không gian lỗi vô hình |
| Tỷ lệ trường định vị được | #(field có cột khác 0 và không tỷ lệ với cột nào khác) / #field |
| Kích thước bộ trường tối thiểu | Số field nhỏ nhất để mọi lỗi một-trường định vị được |

**Kiểm định.** Không có. Đây là kết quả đại số tuyến tính tất định, không
phải suy luận thống kê. Trình bày là mệnh đề kèm chứng minh, không kèm
p-value.

**Mệnh đề đăng ký trước, sẽ kiểm chứng bằng thực nghiệm ở tầng XBRL:** với
`δ = (c−1)x*` (tức đọc sai đơn vị, `x̂ = c·x*`), ta có
`Aδ = (c−1)Ax* = 0`. **Sai đơn vị toàn cục LUÔN vô hình với mọi đẳng thức
kế toán** — không phải "thường vô hình". Đây là lý do mỏ neo tuyệt đối
(dòng "Đơn vị tính:" ở header bảng) là bắt buộc chứ không phải tuỳ chọn.

---

### H1 — Detection

**Phát biểu.** Vi phạm ràng buộc dự báo lỗi trích xuất tốt hơn cả
confidence tự báo của model lẫn conformal prediction thuần thống kê.

**Chỉ số chính, chốt trước:** AUROC, với nhãn nhị phân "trường này sai" và
ba bộ điểm dự báo:

1. Mức vi phạm ràng buộc quy về từng trường
2. Confidence self-consistency của VLM (tỷ lệ đồng thuận qua k mẫu)
3. Conformal prediction thuần thống kê, theo Ajayi et al.

**Kiểm định.** Bootstrap theo **cụm tài liệu** trên hiệu số AUROC giữa từng
cặp. Báo cáo hiệu số kèm khoảng tin cậy 95%, không chỉ p-value.

**Ghi chú về việc KHÔNG dùng DeLong.** Phụ lục thống kê bản 20/08/2026 đề
xuất DeLong test cho ROC tương quan. Sau khi rà lại, kế hoạch chốt ở đây là
**không dùng DeLong**, và lý do phải nêu trong paper: DeLong xử lý đúng
tương quan **giữa các đường ROC** đo trên cùng mẫu, nhưng vẫn giả định các
**quan sát** độc lập. Ở đây các trường trong cùng một tài liệu không độc
lập — chung chất lượng scan, chung layout, chung đơn vị tính, chung công ty
kiểm toán. Dùng DeLong sẽ mắc đúng loại lỗi mà bootstrap-theo-trường mắc:
khoảng tin cậy hẹp giả tạo. Bootstrap theo cụm tài liệu xử lý được cả hai
nguồn tương quan cùng lúc.

**Hiệu chỉnh đa so sánh.** Ba cặp so sánh, dùng Holm-Bonferroni với
alpha = 0,05.

---

### H2 — Localization

**Phát biểu.** Mô hình lỗi rời rạc định vị đúng trường sai tốt hơn hiệu
chỉnh liên tục.

**Chỉ số chính, chốt trước:** Top-1 và Top-3 accuracy.

**Đơn vị quan sát — điểm dễ tự lừa nhất, chốt trước để khỏi cãi sau:**
N của H2 là **số TRƯỜNG BỊ LỖI**, không phải tổng số trường. Với 60 tài
liệu và khoảng 25 trường mỗi tài liệu thì tổng là khoảng 1500, nhưng nếu tỷ
lệ lỗi là 5–15% thì N thật chỉ là **75–225**. Mọi bảng kết quả localization
phải ghi N thật của bảng đó.

**Kiểm định.** McNemar ghép cặp theo trường cho từng cặp phương pháp, kèm
bootstrap ghép cặp theo cụm tài liệu trên **hiệu số** Top-k.

**Baseline bắt buộc:** ít nhất một GED test cổ điển (parity space hoặc
generalized likelihood ratio), không chỉ L1.

---

### H3 — Re-reading beats repairing

**Đây là giả thuyết trung tâm và cũng là giả thuyết dễ bị đánh nhất.**

**Phát biểu.** Sửa lỗi trên tập ứng viên **sinh từ tài liệu** giảm tỷ lệ
lỗi câm nhiều hơn mọi paradigm sửa lỗi không-đọc-lại, **ở cùng ngân sách
gọi model**, và không làm tăng số trường "thoả ràng buộc nhưng sai sự thật".

**Chỉ số chính, chốt trước — hai chiều, cả hai đều phải báo cáo:**

| Chiều | Chỉ số | Kỳ vọng |
|---|---|---|
| Chính | Tỷ lệ lỗi câm = #(có giá trị, sai) / #(có giá trị) | GIẢM |
| Chống bịa | Tỷ lệ trường thoả ràng buộc nhưng sai sự thật | KHÔNG TĂNG |

Thắng ở chiều một mà thua ở chiều hai là **kết quả tiêu cực**, và phải nói
ra. Đăng ký trước điều này để sau không có cớ chỉ báo cáo chiều thuận lợi.

**Kiểm định.** Bootstrap ghép cặp theo cụm tài liệu trên hiệu số tỷ lệ lỗi
câm giữa phương pháp đề xuất và baseline 9.

**Bắt buộc kèm effect size, không chỉ ý nghĩa thống kê.** Với 60 tài liệu,
một hiệu số "có ý nghĩa" nhưng bằng 1 điểm phần trăm thì không ai quan tâm.
Chốt trước: hiệu số dưới **3 điểm phần trăm** sẽ được trình bày là "không
có khác biệt đáng kể về mặt thực tiễn", bất kể p-value.

**Ràng buộc cùng ngân sách.** Baseline 3, 4, 7, 8, 9 và phương pháp đề xuất
phải chạy ở **cùng số lần gọi model**. Runner phải cưỡng chế trần cứng này,
không chỉ báo cáo lại sau.

---

## 2. Đối chứng trung tâm: baseline 9

Baseline 9 là **Fellegi-Holt với ứng viên đến từ phân phối hoặc donor** thay
vì từ tài liệu. Nó giống hệt phương pháp đề xuất ở mọi mặt — cùng ràng
buộc, cùng thuật toán chọn trường, cùng ngân sách — và **khác đúng một biến
số: ứng viên đến từ đâu**.

Đây là thí nghiệm duy nhất tách bạch được đóng góp thật khỏi mọi thứ đã có
từ 1976. Đăng ký trước ở đây rằng nó là đối chứng quyết định, để sau không
thể lặng lẽ thay bằng một baseline dễ thắng hơn.

---

## 3. Điều kiện phản chứng — viết trước, không giấu

Với mỗi giả thuyết, ghi rõ **kết quả nào sẽ khiến nó sai**, và làm gì khi đó.

| Giả thuyết | Sai khi | Khi đó làm gì |
|---|---|---|
| **H0** | Không gian null quá lớn, hầu như không lỗi nào định vị được kể cả với bộ trường mở rộng | Vẫn là finding đáng công bố. Trọng tâm chuyển sang mỏ neo tuyệt đối và việc đọc lại |
| **H1** | AUROC của vi phạm ràng buộc không vượt confidence và CP **trên tầng XBRL** — nơi ground truth hoàn hảo, không đổ lỗi được cho nhãn | Luận điểm chính sụp. Lùi về paper dataset + benchmark + identifiability |
| **H2** | Ứng viên rời rạc không hơn L1 và GED cổ điển | Bỏ claim về mô hình lỗi, giữ claim về đọc lại |
| **H3** | **Baseline 9 ngang bằng phương pháp đề xuất** | Toàn bộ novelty tầng 1 sai. Paper lùi về tầng 2 và 3 — vẫn công bố được, ở venue thấp hơn |

Dòng cuối là dòng quan trọng nhất. Nếu baseline 9 hoà thì "đọc lại nguồn"
không có giá trị và **phải nói ra**.

Viết điều này vào proposal là điểm cộng, không phải điểm trừ: nó chứng minh
tác giả biết mình đang kiểm chứng cái gì.

---

## 4. Ba mốc dừng

Đăng ký trước cả các mốc bắt buộc dừng lại và báo cáo, để không có chuyện
chạy tiếp bất chấp kết quả xấu.

**Mốc 1 — sau khi có báo cáo identifiability.** Người chủ trì đối chiếu ma
trận `A` với văn bản Thông tư và **quyết định bộ trường**. Không đi tiếp
trước khi có quyết định đó: nó xác định chi phí gán nhãn tay, khoản đắt
nhất của cả dự án.

**Mốc 2 — sau pilot 20 tài liệu.** Đo tỷ lệ lỗi thật, từ đó **tính lại
power** và quyết quy mô tầng XBRL. Con số này không đoán được từ trước; mọi
ước lượng hiện tại chỉ là để lên kế hoạch.

**Mốc 3 — sau khi chạy baseline 9.** Nếu baseline 9 ngang bằng phương pháp
đề xuất thì dừng, báo cáo, và lùi paper về tầng dataset + identifiability.
**Không chạy tiếp vòng lặp đọc lại và toàn bộ ablation trước khi biết kết
quả này** — chạy tiếp chỉ để tích luỹ số liệu cho một luận điểm đã sai.

---

## 5. Nguồn phương sai và cách xử lý

Liệt kê tường minh trong paper. Bốn nguồn, xử lý khác nhau:

| Nguồn | Ảnh hưởng | Cách xử lý |
|---|---|---|
| Lấy mẫu VLM ở nhiệt độ lớn hơn 0 | Kết quả đổi giữa các lần chạy | Nhiều seed, báo cáo trung bình kèm độ lệch chuẩn |
| Chọn tài liệu vào tập gold | Ước lượng lệch theo mẫu | Bootstrap theo cụm tài liệu |
| Inject lỗi ở tầng XBRL | Kết quả đổi theo mẫu lỗi | Nhiều seed inject, cố định và ghi lại |
| Bất đồng người gán nhãn | Ground truth không tuyệt đối | Đo, không giả định bằng 0 |

Nguồn thứ nhất là nguồn người ta hay nhớ, và cũng là nguồn ít nghiêm trọng
nhất.

---

## 6. Quy tắc bootstrap — chốt trước vì đây là chỗ dễ làm sai nhất

Bootstrap **lấy mẫu lại TÀI LIỆU** (có hoàn lại), rồi tính chỉ số trên toàn
bộ trường của các tài liệu được chọn. Số vòng lặp `B = 2000`.

Không bao giờ bootstrap theo từng trường. Các trường trong cùng một tài
liệu không độc lập, nên bootstrap theo trường cho khoảng tin cậy **hẹp giả
tạo** — nó giả định 1500 quan sát độc lập trong khi số cụm độc lập thật chỉ
là 60. Đây là loại lỗi reviewer có nền thống kê bắt được ngay.

Áp cho: field-level accuracy, tỷ lệ lỗi câm, document-level fully-correct,
Top-k localization, chỉ số chống bịa, và AUROC.

---

## 7. Quy trình gán nhãn — cam kết, không phải mong muốn

1. **Người gán nhãn phải mù với đầu ra pipeline.** Thấy kết quả model trước
   thì sẽ neo vào đó và ground truth bị nhiễm. Đây là luật quan trọng nhất
   và cũng dễ vi phạm nhất khi làm một mình cho nhanh.
2. **Gán nhãn xong mới chạy pipeline trên tài liệu đó.** Thứ tự thời gian
   phải ghi lại được.
3. **Guideline viết trước, không sửa giữa chừng.** Nếu buộc phải sửa, ghi
   lại thời điểm và gán nhãn lại phần trước đó.

**Cam kết đo đồng thuận:** 20 tài liệu gán nhãn đôi (một phần ba tập gold).
Báo cáo tỷ lệ khớp tuyệt đối theo trường, Krippendorff alpha, và phân loại
bất đồng. Nếu không tìm được người thứ hai: gán nhãn lại 20 tài liệu sau ít
nhất hai tuần, bởi chính mình, không xem bản cũ — nói rõ trong paper đây là
bản thay thế và nêu giới hạn.

**Trần người:** 10 tài liệu, gán nhãn dưới áp lực thời gian thực tế (15
phút một tài liệu), so với bản gold đã phân xử kỹ. Không có số này thì
không diễn giải được kết quả hệ thống: 83% là gần trần hay còn xa?

---

## 8. Tái lập được

Ghi lại cho **mọi** lần chạy, không chỉ lần cuối: tên và phiên bản model,
nhiệt độ, k mẫu, seed, **băm nội dung prompt** (không chỉ số phiên bản),
commit hash, ma trận ràng buộc đã dùng, chuẩn mẫu biểu được nhận diện, thời
gian và chi phí.

**Chia tập theo TÀI LIỆU, không theo trang.** Hai trang cùng một báo cáo
giống nhau đến mức nếu một trang vào train và một trang vào test thì con số
đo được là rác.

---

## 9. Danh mục kiểm cho mọi bảng kết quả

- [ ] N thật của bảng đó — **số lỗi nếu là bảng localization**, không phải số trường
- [ ] Khoảng tin cậy, bootstrap **theo cụm tài liệu**
- [ ] Số seed và độ lệch chuẩn giữa các seed nếu có lấy mẫu
- [ ] Ngân sách gọi model của từng phương pháp
- [ ] Kiểm định ghép cặp cho mọi so sánh giữa phương pháp
- [ ] Hiệu số kèm CI, không chỉ p-value
- [ ] Nêu rõ tầng dữ liệu: XBRL, gold Việt Nam, hay distant

---

## Sửa đổi

Chưa có. Mọi sửa đổi ghi vào đây kèm ngày và lý do, không sửa đè lên trên.
