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

Mọi sửa đổi ghi vào đây kèm ngày và lý do, không sửa đè lên trên.

### 22/08/2026 — Chốt trần số trường được sửa ở 2, và tách hai loại ABSTAIN

**Sửa đổi:** `diagnose()` và baseline 9 chạy với `max_changes = 2` làm mặc
định, tức phương pháp chỉ xét các tổ hợp sửa từ hai trường trở xuống.

**Lý do — đo được, không đoán.** Trên bài toán 8 chỉ tiêu với 87 ứng viên,
ca có nghiệm mất 1,8 mili giây còn ca VÔ NGHIỆM mất **30 giây** khi không
chặn và **16 mili giây** khi chặn ở 2. Toàn bộ chi phí nằm ở việc chứng minh
KHÔNG có nghiệm, mà đó lại là ca thường gặp vì tập ứng viên đóng cố ý không
chứa mọi cách sửa. Với tầng XBRL hàng nghìn tài liệu, 30 giây một tài liệu
là không chạy nổi.

**Đây là hạn chế của phương pháp, không phải chi tiết cài đặt.** Một tài
liệu có ba trường cùng sai sẽ không được sửa, kể cả khi tổ hợp sửa đúng nằm
sẵn trong tập ứng viên. Phải nêu trong paper, và bảng kết quả phải báo cáo
tỷ lệ tài liệu rơi vào ca đó.

**Trần áp cho CẢ baseline 9**, vì H3 so ở cùng ngân sách và trần thay đổi là
một phần của ngân sách. Baseline 8 nằm ngoài vì delta của nó chạy tự do
trong `ℝⁿ`; nghiệm đỉnh của bài quy hoạch tuyến tính đã tự giới hạn số toạ
độ khác 0 không vượt quá `rank(A)`.

**Kèm theo — tách ABSTAIN thành các lý do phân loại được.** Verdict
`ABSTAIN` giờ đi kèm một mã trong tập đóng: `vo_nghiem`,
`vuot_tran_thay_doi`, `het_gio`, `thieu_gia_tri`, `bo_giai_that_bai`. Việc
tách là bắt buộc vì **chỉ `vo_nghiem` mới đỡ được luận điểm chống bịa**: nó
nghĩa là đã vét cạn mọi tổ hợp và không cách đọc nào làm bảng cân đối được.
`vuot_tran_thay_doi` chỉ nghĩa là ta đã không tìm. Gộp hai thứ lại là tính
công cho phương pháp ở những ca nó không chứng minh được gì, nên mọi bảng
kết quả phải đếm chúng riêng.

### 23/08/2026 — Chốt bộ chỉ tiêu ở 21, và không gán nhãn cột kỳ so sánh

**Sửa đổi.** Bộ chỉ tiêu mở rộng từ 11 lên **21** (kịch bản D của
`src/constraints_scenarios.py`, cộng một chỉ tiêu chỉ có ở TT99). Bộ đẳng
thức đi từ 3 lên **7**. Cột kỳ so sánh **không** được gán nhãn.

**Lý do — thước cũ đo sai thứ.** Bảng kịch bản ban đầu xếp hạng theo "số chỉ
tiêu định vị được trên mỗi chỉ tiêu thêm vào", và theo thước đó kịch bản B
thắng với tỷ lệ 1,00. Thước đó có hai lỗ. Thứ nhất, nó gộp "cột toàn 0" với
"lẫn với chỉ tiêu khác" làm một, trong khi cột toàn 0 nghĩa là lỗi vô hình
với **cả H1 lẫn H2** còn lẫn lớp thì H1 vẫn bắt được. Thứ hai, "định vị
được" là nhị phân trong khi H2 đo bằng Top-1/Top-3, mà một chỉ tiêu trong
lớp lẫn 2 đạt trần Top-3 bằng 100% còn lớp lẫn 5 chỉ đạt 60%.

Đo lại theo đúng chỉ số mà H1 và H2 báo cáo:

| Kịch bản | Chỉ tiêu | Chỉ tiêu VÔ HÌNH | Trần Top-1 | Trần Top-3 |
|---|---:|---:|---:|---:|
| A (cũ) | 11 | 3 | 0,36 | 0,73 |
| B | 12 | 3 | 0,42 | 0,75 |
| C | 16 | 1 | 0,50 | 0,94 |
| **D (chốt)** | **20–21** | **0** | **0,50** | **0,90** |
| E | 26 | 0 | 0,54 | 0,96 |

**Vì sao D chứ không phải C, dù Top-3 trung bình của D thấp hơn.** Con số
0,90 thấp hơn 0,94 là **hiệu ứng cấu thành, không phải hồi quy**. Đo trên
đúng 16 chỉ tiêu của kịch bản C, việc chuyển sang D nâng Top-3 từ 0,938 lên
**0,975** — không một chỉ tiêu nào xấu đi. Trung bình tụt vì D thêm bốn chỉ
tiêu vốn dĩ khó (các thành phần của mã 100, cùng lớp lẫn 5). Hệ quả bắt
buộc cho bảng kết quả: **Top-k trung bình phải in kèm phân rã theo lớp lẫn**,
nếu không bảng sẽ trông như D kém hơn C trong khi sự thật ngược lại.

**Vì sao D chứ không phải B.** B không cứu chỉ tiêu vô hình nào. Trong ba
chỉ tiêu vô hình của bộ cũ có `hang_ton_kho` — đúng chỉ tiêu đã có lỗi đọc
THẬT trên báo cáo VNM (alias khớp trúng dòng Dự phòng giảm giá) và là ví dụ
mở đầu của proposal mục 2.2. Ở bộ cũ, vòng đọc lại — đóng góp cốt lõi của cả
bài — **không bao giờ được kích hoạt trên chính ví dụ minh hoạ của nó**. Ở D
nó phát hiện được. Nó vẫn *không* định vị được (lẫn trong lớp 5 chỉ tiêu con
của mã 100), và đó là kết quả H0 phải báo cáo trung thực.

**Vì sao không E.** E hơn D trên mọi trần nhưng bắt gán nhãn B03, tức biểu
mẫu thứ ba. 26 chỉ tiêu qua ba báo cáo trong 15 phút nhiều khả năng vỡ giao
thức đo trần người ở ADDENDUM mục 6, mà giao thức đó đã viết vào
`ANNOTATION-GUIDELINE.md` rồi; đổi nó là vi phạm Luật 3 và phải đo lại trần
người từ đầu.

**Cột kỳ so sánh: không gán nhãn.** Proposal mục 6.1(d) để ngỏ khả năng đây
là "ràng buộc gần như miễn phí". Đo cho thấy ngược lại: thêm cột kỳ trước
nhân đôi số chỉ tiêu mà trần Top-1 và Top-3 **không đổi một điểm nào** (D:
0,50/0,90 trước và sau; E: 0,54/0,96 trước và sau). Lý do chứng minh được
chứ không cần đo — hai cột thoả cùng một hệ đẳng thức một cách độc lập nên
ma trận thành khối chéo `[[A,0],[0,A]]`, không residual nào nối hai cột. Kể
cả khi nối chéo qua B03 (tiền đầu kỳ này bằng tiền cuối kỳ trước) cũng chỉ
được 2 điểm Top-1 cho gấp đôi ngân sách gán nhãn. Mỏ neo chéo ở proposal mục
6.3 vẫn giữ, nhưng nó là kiểm **biên độ** chứ không phải đẳng thức, nên chỉ
cần một con số tổng tài sản kỳ trước, không cần cả cột.

**Một khác biệt thật giữa hai chuẩn lộ ra khi thi công.** Phân rã tài sản
ngắn hạn KHÔNG giống nhau: TT200 có `100 = 110+120+130+140+150` với 150 là
Tài sản ngắn hạn khác, còn TT99 có `100 = 110+120+130+140+150+160` với 150
là **Tài sản sinh học ngắn hạn** và 160 mới là Tài sản ngắn hạn khác. Nên
TT99 có 21 chỉ tiêu và TT200 có 20, và mã 150 gia nhập nhóm mã đổi nghĩa
giữa hai chuẩn cùng với 270 và 142. Đây là đẳng thức duy nhất trong cả cấu
hình mà hai chuẩn không đẳng cấu.

**Hệ quả cho phát biểu về trục TT200 → TT99.** Sáu trong bảy đẳng thức giống
hệt nhau ở hai chuẩn. Nên ablation số 8 kiểm chủ yếu **tầng nhận diện và tra
cứu mã số**, không kiểm khả năng tổng quát hoá của phần suy luận ràng buộc.
Phải viết đúng phạm vi đó, không được phát biểu rộng hơn.

---

### 24/08/2026 — Dòng vắng mặt trên biểu mẫu được ghi `0`, không phải `null`

**Sửa đổi.** Khi hệ xác định được rằng một chỉ tiêu **không có dòng nào trên
biểu mẫu**, giá trị trả về là `0` chứ không phải `null`. Áp cho cả tập gold
(đã quy định ở `ANNOTATION-GUIDELINE.md` mục 3.4) lẫn đầu ra pipeline (thi
công ở commit `ada6f75`). `null` từ nay chỉ còn một nghĩa: **chưa biết**.

**Vì sao đây là sửa đổi của ĐĂNG KÝ TRƯỚC chứ không phải chi tiết cài đặt.**
Nó đổi giá trị của hai chỉ số đã chốt trước ở mục 9. `eval/metrics.py` quy
định `None` chỉ khớp với `None`, nên khi gold ghi `0` mà pipeline trả `null`
thì mọi dòng vắng mặt bị tính là SAI:

- **`field_accuracy`** bị trừ điểm trên mọi tài liệu có dòng vắng mặt — mà
  vắng mặt là chuyện thường, không phải ngoại lệ.
- **`document_fully_correct`** đòi cả 20–21 chỉ tiêu khớp, nên chỉ một dòng
  vắng mặt là cả tài liệu trượt. Chỉ số này sẽ tụt về gần 0 vì lý do quy ước.
- **`silent_error_rate`** KHÔNG bị ảnh hưởng, vì nó loại `null` khỏi mẫu số.

Sai lệch này đổ đều cho phương pháp đề xuất lẫn cả 10 baseline nên phép **so
sánh** vẫn sống, nhưng **con số tuyệt đối** in ra giấy thì sai theo quy ước.
Ghi vào đây để người đọc bài biết định nghĩa nào đang dùng.

**Căn cứ pháp lý, không phải quy ước tiện tay.** Thông tư 99 mục 1.2.3: "các
chỉ tiêu không có số liệu được miễn trình bày", tức chính văn bản bảo đảm
phần vắng mặt không đóng góp vào tổng. Báo cáo VNM Q1/2026 in công thức rút
gọn của chính nó — `100 = 110 + 120 + 130 + 140 + 160`, bỏ hẳn mã 150.

**Ranh giới, và đây là chỗ phải giữ.** Chỉ ghi `0` khi xác định được dòng
**vắng mặt trên biểu mẫu**. Ca "có dòng mà đọc không ra" giữ `null`. Gộp hai
ca lại là bịa ra một con số: đẳng thức sẽ lệch đúng bằng giá trị thật bị mất,
và bước chẩn đoán đi tìm ứng viên sửa cho nhầm chỉ tiêu — cảnh báo đúng hướng
nhưng quy trách nhiệm sai chỗ, tức làm hỏng chính chỉ số Top-k của H2.

Việc phân biệt hai ca do một **oracle tất định** đảm nhiệm: dò **mã số dòng**
trên text OCR của các trang đã duyệt, và chỉ kết luận "vắng mặt" khi đã thấy
mẫu biểu ở đâu đó mà không trang nào chứa mã đó. Cố ý **không** hỏi model,
vì model tự khai "dòng này không có" là một phán đoán, và phán đoán sai sẽ
lặng lẽ thành `0` đi vào đẳng thức — đúng chỗ nhạy cảm nhất với việc bịa số.

**Trạng thái ghi tường minh.** `meta["trang_thai_chi_tieu"]` ghi cho từng chỉ
tiêu một trong ba giá trị `co_gia_tri` / `vang_mat` / `khong_doc_duoc`, và
`meta["line_probe"]` ghi lượt chạy đó có bật oracle hay không. Bảng kết quả
phải đọc trạng thái từ khoá này chứ không suy ra từ con số: một số `0` có thể
là doanh nghiệp khai bằng 0, cũng có thể là dòng vắng mặt.
