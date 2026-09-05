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

## Mục lục — THÊM 31/08/2026, không thuộc nội dung đã đăng ký

> Bảng này là **phụ trợ tra cứu**, thêm vào sau ngày đăng ký và không sửa một
> chữ nào của nội dung gốc. Nó có mặt vì file này dài và không bao giờ nên đọc
> trọn: mở đúng mục cần rồi đóng lại. Mục "Sửa đổi" ở cuối là nơi DUY NHẤT
> được ghi thay đổi, và nó vẫn nguyên vẹn.

| Mục | Nội dung | Đọc khi |
|---|---|---|
| 0 | Bối cảnh, ký hiệu `x*`, `A`, `δ` | lần đầu đọc file này |
| **1** | **Bốn giả thuyết H0–H3** | trước mọi phép đo, và khi dựng bảng kết quả |
| 2 | Đối chứng trung tâm: baseline 9 | so phương pháp đề xuất với bộ giải liên tục |
| **3** | **Điều kiện phản chứng** — viết trước, không giấu | khi kết quả ra ngược mong đợi |
| 4 | Ba mốc dừng | quyết định đóng một mốc |
| 5 | Nguồn phương sai và cách xử lý | thiết kế lượt chạy nhiều model / nhiều tài liệu |
| **6** | **Quy tắc bootstrap** | trước khi báo bất kỳ khoảng tin cậy nào |
| 7 | Quy trình gán nhãn — cam kết | tổ chức gán nhãn, gán nhãn đôi |
| 8 | Tái lập được | đóng gói kết quả, viết phần Reproducibility |
| **9** | **Danh mục kiểm cho mọi bảng kết quả** | mỗi lần dựng một bảng |
| **Sửa đổi** | Mọi tu chính kèm ngày và lý do | **trước khi đổi bất cứ thứ gì ở trên** |

**Chỗ hay phải tra nhất:** lập luận `Aδ = (c−1)Ax* = 0` — sai đơn vị toàn cục
luôn vô hình với mọi đẳng thức — nằm ở mục 0. Đây là **nhà duy nhất** của mệnh
đề đó; các file khác trong repo chỉ được trỏ về đây, đừng chép lại lần nữa.

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

> *Bổ sung, không sửa đè:* cách CHẤM hai chỉ số này khi một phương pháp từ
> chối trả lời đã được chốt ở **tu chính 25/08/2026** cuối file — ba con số,
> và chỉ số quyết định là con số chia cho tổng số lượt.

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

> *Bổ sung, không sửa đè:* trên **tầng XBRL**, dòng H3 nay đọc thành ba
> trạng thái chứ không phải hai — hoà HOÃN phán quyết sang tầng gold thay vì
> kích hoạt phản chứng. Lý do đo được, và tu chính được chốt trước khi có kết
> quả: xem **tu chính 25/08/2026** cuối file. Trên tầng gold Việt Nam thì
> bảng này giữ nguyên.

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

> *Bổ sung, không sửa đè:* điều kiện dừng này áp ở **tầng gold Việt Nam**.
> Ở tầng XBRL, chỉ kết quả **thua** mới kích hoạt nó; hoà thì hoãn phán
> quyết. Xem tu chính 25/08/2026 cuối file — lý do là tầng XBRL không có ảnh
> nên hai trong năm nguồn ứng viên không chạy được ở đó.

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

**Tài liệu đã chạy pipeline không được vào tập gán nhãn đôi** (tu chính
28/08/2026). Với phương án tự gán nhãn lại thì người gán lại chính là người
đã chạy pipeline, nên đầu ra máy đoán cho từng ô là một mỏ neo có thật.
Trạng thái ở khoá `gan_nhan_doi` của `data/nguon_gold.json`, đối chiếu bằng
`src/eval/tap_dong_thuan.py`.

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
- [ ] **Bảng localization: đủ ba con số** — chia cho tổng số lượt (chỉ số
  CHÍNH), tỷ lệ ra tay, và định vị trên lượt có ra tay. Con số thứ ba
  **không bao giờ đứng một mình**. Xem tu chính 25/08/2026

---

## Sửa đổi

**Mười bảy tu chính, không cái nào được rút gọn hay viết đè.** Đó là điều kiện
để việc đăng ký trước còn giá trị: một bản ghi sửa được sau khi thấy kết quả
thì không chứng minh được gì. **Mục này vì thế cố ý nằm ngoài mọi đợt dọn dẹp
tài liệu của repo** — nén nó lại là phá đúng thứ nó tồn tại để bảo vệ. Mục lục
dưới đây thêm ngày 26/08/2026 để tìm nhanh, và nó là thứ DUY NHẤT được thêm
vào phần này ngoài các tu chính.

Phân biệt với `CHANGELOG.md`: ở đây là **thay đổi cam kết nghiên cứu** (giả
thuyết, chỉ số, điều kiện phản chứng, quy trình gán nhãn); ở đó là **thay đổi
đổi con số**, kèm số đo trước và sau. Một thay đổi có thể phải vào cả hai — tu
chính ghi *ta cam kết đo khác đi*, changelog ghi *con số đã đổi bao nhiêu*.

| Ngày | Tu chính | Chạm tới |
|---|---|---|
| 22/08 | Trần số trường được sửa ở 2; tách hai loại ABSTAIN | H2, H3 |
| 23/08 | Bộ chỉ tiêu lên 21; không gán nhãn cột kỳ so sánh | H0, chi phí gán nhãn |
| 24/08 | Dòng vắng mặt ghi `0`, không phải `null` | H1, guideline 3.4 |
| 25/08 | Chỉ số định vị báo cáo **ba** con số, nêu tên con số quyết định | H2 |
| 25/08 | Ma trận nhầm chữ số đo được, dùng chung hai phía khác độ sâu | H3, bộ tiêm lỗi |
| 25/08 | Chỉ số chính của H3 ở tầng XBRL tính ở mức **lượt** | H3 |
| 25/08 | Tầng XBRL chỉ kiểm được khả năng SỬA cho 2 trong 4 chế độ lỗi | giới hạn H3 |
| 25/08 | Hoà ở tầng XBRL **hoãn** phán quyết H3, không kích hoạt phản chứng | điều kiện dừng |
| 25/08 | Bộ chỉ tiêu chuyển sang **kịch bản E** (27/26 chỉ tiêu, 9 đẳng thức) | H0, H2, H3 |
| 25/08 | Giao thức trần người bỏ con số 15 phút cố định | diễn giải kết quả |
| 26/08 | Hệ số 0,6 được chốt; `thoi_gian_giay` đổi định nghĩa | diễn giải kết quả |
| 26/08 | Độ phân giải bản quét thành hiệp biến ghi trước, phân tích thứ cấp | H1, H2, giới hạn |
| 27/08 | Phân bố lỗi thật ở tầng gold khác hẳn phân bố bơm ở tầng XBRL | giới hạn H2, H3 |
| 28/08 | Tài liệu đã chạy pipeline bị loại khỏi tập gán nhãn đôi | đo đồng thuận |
| 28/08 | **HOÃN Mốc 2, chạy Mốc 3 trước** — kèm ngoại lệ cho ca hoà | thứ tự mốc dừng |
| 01/09 | Phạm vi tổng thể loại thêm chứng khoán, bảo hiểm, quản lý quỹ | tính khái quát của H1, H2 |
| 01/09 | Nhãn chép **nguyên văn**; quy ước dấu B02 thành một trường đọc từ tài liệu | H1, H2, guideline 3.3, tập gold |

Mọi sửa đổi ghi vào đây kèm ngày và lý do, không sửa đè lên trên.

### 01/09/2026 (muộn hơn) — Nhãn chép nguyên văn; quy ước dấu thành tham số tài liệu

**Sửa đổi.** Hai thay đổi đi liền nhau, và cái sau là hệ quả bắt buộc của cái
trước.

*(a) Giao thức gán nhãn.* Mọi giá trị chép **NGUYÊN VĂN như in** — ngoặc đơn
là âm, không ngoặc là dương — cho MỌI chỉ tiêu. Ba ngoại lệ diễn giải bị bỏ:
"giá vốn luôn dương", "mã 51/52 ghi theo nghĩa kinh tế", và quy tắc TT99 riêng
"giữ nguyên dấu như in". Người gán nhãn không còn phải phán đoán một dòng là
chi phí hay thu nhập; việc của họ thuần là ĐỌC.

*(b) Hình dạng ràng buộc.* Hai đẳng thức B02 — mã 20 và mã 60 — nay chọn dạng
theo một **tham số của từng tài liệu**, `quy_uoc_dau ∈ {tong, tru,
khong_xac_dinh}`, đọc từ trang giấy và lưu trong file gold. Trước đó dạng của
chúng bị buộc theo CHUẨN Thông tư.

**Vì sao (b) là hệ quả bắt buộc của (a).** Chép nguyên văn thì con số một mình
không diễn giải được: `51 = 68.069.473.287` không nói được đó là chi phí hay
thu nhập thuế. Quy ước vì thế là **dữ liệu phải ghi**, không phải kiến thức
suy ra được — đúng khuôn mẫu `unit_declared` / `unit_multiplier` mà mục 3.1 đã
dùng cho đơn vị tính. Bỏ (b) mà giữ (a) sẽ để lại một tập gold không diễn giải
được; giữ (b) mà bỏ (a) là quay lại bắt người gán nhãn phán đoán kế toán.

**Bằng chứng buộc phải đổi.** Người chủ trì đọc tay 15 báo cáo TT200 ngày
01/09/2026: **cả hai cách in cùng tồn tại trong một chuẩn** — 12 mã in dạng
tổng, 3 mã (`BCM`, `DPM`, `DVD`) in dạng trừ. Giả định "mỗi Thông tư một quy
ước", vốn là nền của cách buộc cũ, bị chính dữ liệu bác bỏ. Hệ quả đo được:
trên tài liệu TT200 in dạng trừ, tầng trích xuất để lại residual **đúng gấp
đôi mã 52** trên một tài liệu **không có lỗi đọc nào** — một dương tính giả có
hệ thống, sinh ra bởi cấu hình chứ không bởi tài liệu, ngay giữa phép đo của
H1. Số cụ thể trên ca đã kiểm: −56.149.699.672 đồng.

**Đã bác một phương án rẻ hơn, và ghi lại để không ai đề xuất lại.** Phương án
"chấp nhận nếu thoả MỘT TRONG HAI dạng" bị bác vì hai lý do đo được: (1) trên
`DGC_2025Q2_TT200`, một lỗi lật dấu thuần tuý ở mã 51 chuyển bộ số từ thoả
dạng này sang thoả dạng kia, nên phép tuyển cho lọt một sai lệch
**47.108.746.070 đồng** — hai vế lệch nhau đúng `2×(51+52)`, đúng bằng lượng
mà lỗi dấu dịch chuyển, nên phép tuyển mù với chính lớp lỗi cần bắt; (2) phép
tuyển không viết được thành ràng buộc tuyến tính, nên không có ma trận `A`,
không có `dim null(A)`, tức bỏ luôn toàn bộ H0.

**KHÔNG đổi kết luận nào của H0, và đây là số đo chứ không phải lập luận.**
Dựng `A` cho cả bốn tổ hợp (hai chuẩn × hai quy ước): cùng `rank(A)` bằng 9,
cùng `dim null(A)` (17 với TT200, 18 với TT99), cùng 7/26 và 7/27 chỉ tiêu
định vị được, cùng 0 cột toàn 0, và cùng **danh sách** cặp không phân biệt
được — trùng từng phần tử. Lý do: đổi quy ước chỉ lật dấu vài cột của `A`, mà
hạng, không gian null và quan hệ tỷ lệ giữa các cột đều bất biến với phép lật
ấy. Phép kiểm này nay chạy lại mỗi lần sinh `identifiability_*.md` thay vì
được chép từ trí nhớ.

**Giả thuyết H0–H3 giữ nguyên phát biểu; mốc dừng giữ nguyên.** Mốc 3 chạy
trên tầng XBRL của SEC nên không có biểu mẫu Việt Nam nào trong đó và không bị
chạm. Số đã công bố trên tầng gold không phải rút lại: bug chỉ nổ khi quy ước
in của tài liệu khác quy ước bị đóng cứng cho chuẩn của nó, mà 5 tài liệu gold
TT200 đều in dạng tổng — đúng nhánh đang cài.

**Cái phải dẫn lại:** mọi thống kê quy lỗi cho "xử lý dấu", cụ thể con số *8
trong 24 lỗi câm* đo ngày 27/08/2026, vì `chuan_hoa_dau()` — cơ chế sinh ra
chúng — đã bị xoá.

**Giới hạn mới, khai trước khi có kết quả.** Ràng buộc B02 nay phụ thuộc một
bit đọc từ tờ giấy. Sai chữ số vẫn bị bắt như cũ; riêng **lỗi đọc nhầm dấu
ngoặc ở mã 11** lật cả hai đẳng thức B02 của tài liệu đó. Giảm thiểu bằng hai
nguồn độc lập kiểm chéo (công thức in ưu tiên hơn dấu ngoặc mã 11), và ca hai
nguồn mâu thuẫn được đếm RIÊNG trong metrics để phần nào của giới hạn này thật
sự xảy ra là đo được chứ không phải ước đoán.

**Tập gold gán nhãn lại từ đầu.** Quyết định của người chủ trì cùng ngày. Giá
trị đang lưu đã qua nhiều lượt lật dấu cơ học khi quy tắc đổi nên không còn là
bản sao trung thực của trang giấy — `notes` của bốn file ghi thẳng điều đó.

### 01/09/2026 — Tổng thể thu hẹp: loại cả chứng khoán, bảo hiểm, quản lý quỹ

**Sửa đổi.** Tổng thể mà tập gold lấy mẫu từ đó nay loại **bốn** nhóm tổ chức
phát hành chứ không phải một: tổ chức tín dụng và chi nhánh ngân hàng nước
ngoài (đã có từ đầu), cộng thêm **công ty chứng khoán, doanh nghiệp bảo hiểm
và công ty quản lý quỹ**. Câu chữ tương ứng ở `ANNOTATION-GUIDELINE.md` mục 2
sửa cùng ngày.

**Vì sao phải vào đây chứ không chỉ vào guideline.** Đây là thay đổi **tổng
thể lấy mẫu**, nên nó đổi phạm vi khái quát của mọi kết luận H1 và H2: bài
viết từ nay phải nói rõ kết quả áp cho doanh nghiệp phi tài chính niêm yết,
không phải cho doanh nghiệp niêm yết nói chung. Một giới hạn về tính khái quát
là cam kết nghiên cứu, không phải chi tiết thao tác.

**Bằng chứng buộc phải thu hẹp.** `BVH_2026Q2_TT99` (Tập đoàn Bảo Việt) dùng
biểu mẫu B02 mở rộng cho hoạt động bảo hiểm: mã chạy 01 → 21 → 42 → 52 → 70,
**không có mã 10, 11, 20 lẫn 30**. Mã 30 là ca nặng nhất vì không có dòng nào
tương đương về nghĩa — biểu mẫu đi thẳng từ 42 sang 50 — nên mọi cách quy đổi
đều làm đẳng thức `ln_thuan_hdkd + ln_khac = loi_nhuan_truoc_thue` sai lệch
trên một tài liệu không có lỗi trích xuất nào. Nghĩa là giữ tài liệu ấy lại sẽ
**đưa dương tính giả vào chính ground truth**, tức làm hỏng đúng phép đo của
H1. B01 và B03 của tài liệu này thì chuẩn TT99 bình thường; một biểu mẫu lệch
là đủ.

**Vì sao đây không phải là loại dữ liệu sau khi đã thấy kết quả** — điểm mà
người phản biện sẽ đánh trước tiên. Tiêu chí loại phát biểu trên **ngành nghề
đăng ký của tổ chức phát hành**, quan sát được trước mọi phép đo và không dính
gì tới hiệu năng. Chín tài liệu bị loại **chưa từng được gán nhãn và chưa từng
chạy pipeline** — không có dấu vết nào của chúng trong `data/gold/` lẫn
`data/output/` — nên không có kết quả nào để mà nhìn thấy. Và mục 2 của
guideline đã chốt "phi tài chính" ngay từ 23/08/2026 với đúng lý do "mẫu biểu
và mã số khác hẳn"; tu chính này chỉ liệt kê đủ bốn nhóm mà lý do ấy phủ,
thay vì mỗi tổ chức tín dụng.

**Chín tài liệu bị loại và cách thay.** `MBB`, `STB`, `TCB`, `VCB`, `VPB`,
`KLB`, `VIB` (ngân hàng), `SSI` (chứng khoán), `BVH` (bảo hiểm). Mỗi cái được
thay bằng một tài liệu **cùng Thông tư, cùng kỳ báo cáo, cùng sàn, cùng hạng
quy mô, cũng là bản quét không lớp text**, nên cơ cấu 30 TT200 / 30 TT99 và
bốn nhóm Stress ở guideline mục 7 giữ nguyên. Bảng đối chiếu từng cặp ở
`data/bctc/NGUON.md`.

**Không đụng tới số đo nào**, nên không có mục tương ứng ở `CHANGELOG.md`: tập
gold đã gán nhãn không mất tài liệu nào, và không lượt chạy nào phải làm lại.

### 28/08/2026 (muộn hơn) — HOÃN Mốc 2, chạy Mốc 3 trước

**Sửa đổi.** Thứ tự ba mốc dừng ở mục 4 đảo lại: **Mốc 3 chạy trước, Mốc 2
làm sau**. Quyết định của người chủ trì, 28/08/2026, nguyên văn: *"kệ mốc 2
đi, đo hết mốc 3 rồi quay lại"*.

**Mốc 2 nói gì và vì sao nó vốn đứng trước.** Mục 4 đặt Mốc 2 sau pilot 20 tài
liệu: đo tỷ lệ lỗi thật, từ đó **tính lại power** và quyết quy mô tầng XBRL.
Nó đứng trước Mốc 3 vì chính nó nói cho biết cần bao nhiêu tài liệu thì phép
so ở Mốc 3 mới đủ sức phân biệt thắng thua với may rủi.

**Rủi ro của việc đảo thứ tự, ghi ra trước khi có kết quả.** Chạy Mốc 3 mà
chưa tính lại power nghĩa là **không biết trước phép so có đủ sức hay không**.
Hệ quả cụ thể: một kết quả HOÀ ở Mốc 3 sẽ không phân biệt được hai khả năng
khác hẳn nhau — *phương pháp thật sự ngang nhau*, hay *mẫu quá mỏng nên không
thấy được khác biệt có thật*. Mà theo mục 4, hoà ở tầng gold thì **kích hoạt
điều kiện dừng**. Tức đảo thứ tự làm tăng nguy cơ dừng dự án vì một kết quả âm
tính giả.

**Ràng buộc kèm theo, để rủi ro đó không thành mất mát:**

1. Lượt chạy Mốc 3 trên tầng gold phải báo cáo **số lượt lỗi thực tế** đã dùng
   để so, kèm khoảng tin cậy bootstrap theo cụm tài liệu. Không được báo cáo
   một tỷ lệ trần trụi.
2. Nếu kết quả là HOÀ **và** số lượt lỗi dưới ngưỡng power tính được về sau ở
   Mốc 2, thì kết quả đó **KHÔNG kích hoạt điều kiện dừng** — nó được ghi là
   *chưa kết luận được*, và phải chạy lại sau khi đủ tài liệu. Ngoại lệ này
   ghi ở đây, TRƯỚC khi chạy, chứ không được viện ra sau khi thấy kết quả xấu.
3. Kết quả THUA vẫn kích hoạt điều kiện dừng như cũ. Mẫu mỏng làm khó thấy
   khác biệt, nó không tạo ra một chiều thua giả.
4. Mốc 2 **không bị bỏ**, chỉ bị hoãn. Nó vẫn phải chạy trước khi bất kỳ con
   số nào của Mốc 3 đi vào bài báo.

**Không tài liệu nào phải gán nhãn lại.**

### 28/08/2026 — Tài liệu đã chạy pipeline bị loại khỏi tập gán nhãn đôi

**Thu hẹp tập được chọn cho phép đo đồng thuận. Không đổi giả thuyết, không
đổi chỉ số, không tài liệu nào phải gán nhãn lại.**

Bối cảnh: quyết định 26/08/2026 bỏ người gán nhãn thứ hai và kích hoạt phương
án tự gán nhãn lại sau ít nhất hai tuần. Phương án ấy làm một ràng buộc vốn
nhẹ trở thành nặng — người gán lại chính là người đã chạy pipeline, và
`data/output/tap_gold_*.json` cùng `..._pipeline.log` giữ giá trị máy đoán
cho **từng ô** của mười tài liệu gold đầu tiên (lượt chạy 26–27/08/2026).

Vì sao phải là tu chính chứ không phải chi tiết thi công: nếu lượt gán nhãn
lại bị neo vào giá trị máy đoán thì Krippendorff alpha và tỷ lệ khớp tuyệt
đối **vẫn tính ra bình thường**, chỉ là chúng đo trí nhớ của người gán nhãn
chứ không đo tính nhất quán của quy tắc. Không có phép kiểm hậu nghiệm nào
phân biệt được hai chuyện đó từ dữ liệu, nên ràng buộc phải nằm ở khâu CHỌN
tài liệu, tức trước khi đo.

Hai đường ra đã cân nhắc. (a) Giữ kỷ luật không mở hai file kia: rẻ, nhưng là
một lời hứa không kiểm chứng được, và vi phạm nó không để lại dấu vết.
(b) Loại hẳn những tài liệu ấy khỏi tập gán nhãn đôi: kiểm được bằng máy, giá
phải trả là chỗ trong một tập ~100 tài liệu vốn thừa chỗ cho 20–33 tài liệu.
Chọn (b).

Hệ quả về lịch, ghi ra vì nó nằm trên đường găng: mười tài liệu gold đầu và
`VNM_2026Q1_TT99` đều đã chạy pipeline, nên tính tới 28/08/2026 **không tài
liệu nào đủ điều kiện gán nhãn đôi**. Mốc hai tuần 09/09/2026 là điều kiện
cần chứ không đủ; lượt gán nhãn đôi chỉ bắt đầu được sau khi tập gold có
thêm tài liệu mới.

Thi công: khoá `gan_nhan_doi` trong `data/nguon_gold.json`,
`src/eval/tap_dong_thuan.py` đối chiếu khai báo với hiện trạng
`data/output/`, `tests/test_tap_dong_thuan.py` khoá ràng buộc, và
`ANNOTATION-GUIDELINE.md` mục 5 kèm một dòng trong danh mục kiểm mục 8.

### 27/08/2026 — phân bố lỗi thật khác hẳn phân bố đang bơm ở tầng XBRL

**Ghi nhận, KHÔNG đổi thiết kế.** Tu chính này bắt buộc phải có trước khi
diễn giải bất kỳ con số nào của tầng XBRL trong bài.

Lượt chấm pipeline đầu tiên trên tập gold Việt Nam (10 tài liệu, 27/08/2026)
cho phân bố chế độ lỗi sau, trên 49 trường lệch:

| Chế độ lỗi | Số trường |
|---|---:|
| Bỏ trống | 25 |
| Đảo dấu | 11 |
| Định vị nhầm bảng | 10 |
| Nhầm ô (`row_shift`) | 2 |
| **Nhầm chữ số** | **1** |

`src/nham_chu_so.py` bơm lỗi theo **ma trận nhầm chữ số**, tức mô phỏng đúng
chế độ lỗi chiếm **1 trên 49** trường lệch của dữ liệu thật. Ba chế độ trội
— bỏ trống, đảo dấu, định vị nhầm bảng — **không có trong bộ lỗi được bơm**.

Hệ quả cho việc diễn giải, phải ghi vào phần Giới hạn của bài: mọi số đo
định vị và sửa lỗi ở tầng XBRL đang được đo trên một phân bố lỗi **không đại
diện** cho phân bố quan sát được ở tầng gold. Điều này KHÔNG làm hỏng tầng
XBRL — tầng đó dùng để đo **năng lực** trên lỗi biết trước, và giá trị của
nó nằm ở chỗ có ground truth về vị trí lỗi. Nhưng nó **cấm** việc chuyển
thẳng một con số recall từ tầng XBRL sang phát biểu về tài liệu thật.

**Không sửa bộ lỗi bơm ở lượt này**, vì đổi phân bố lỗi sau khi đã thấy kết
quả là chọn phân bố theo kết quả. Nếu đổi thì phải ghi tu chính riêng, nêu
rõ ngày và lý do, và chạy lại toàn bộ tầng XBRL.

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

### 25/08/2026 — Chỉ số định vị báo cáo ba con số, và nêu tên con số quyết định

**Sửa đổi.** Mọi bảng localization báo cáo **ba** con số thay vì một, và nói
rõ con số nào là chỉ số chính:

| Con số | Mẫu số | Vai trò |
|---|---|---|
| Định vị đúng / **tổng số lượt** | mọi lượt | **CHÍNH** — dùng cho mọi quyết định dừng |
| Tỷ lệ ra tay (coverage) | mọi lượt | phụ, bắt buộc đi kèm con số dưới |
| Định vị đúng / **số lượt có ra tay** | lượt có sửa ≥ 1 trường | phụ |
| Định vị đúng / **số lượt lỗi có sinh residual** | lượt không VERIFIED | phụ, tách phần thuộc về H0 |

**Lý do.** Phương pháp đề xuất chỉ sửa khi tập ứng viên đóng chứa một cách
đọc hợp lệ, nên nó bỏ phiếu trắng thường xuyên; baseline 9 giải quy hoạch
tuyến tính nên nặn được số thực bất kỳ và gần như không bao giờ từ chối. Trên
lượt chạy 26 hồ sơ ngày 24/08/2026, đề xuất ra tay 122 lần và trúng khoảng
70%, baseline 9 ra tay 234 lần và trúng khoảng 50% — nhưng bảng chia cho tổng
số lượt cho ra 0,212 so với 0,295, tức nó xếp hạng theo **mức sẵn sàng đoán**
chứ không theo độ đúng. Một con số duy nhất không so được hai hệ chạy ở hai
mức coverage khác nhau; đó là lý do nhánh selective prediction luôn báo cáo
cặp (coverage, selective risk) thay vì một điểm.

**Vì sao chỉ số CHÍNH vẫn là con số chia cho tổng, dù nó bất lợi.** Nó là con
số khắc nghiệt hơn với chính mình. Chọn nó làm chỉ số quyết định thì cáo buộc
"chọn chỉ số dễ sau khi thấy kết quả" tự rụng, và hai con số phụ vẫn còn đó
để giải thích cơ chế. Trường hợp bảng có lợi cho baseline 9 ở chỉ số chính,
điều đó **phải được báo cáo là bất lợi cho phương pháp đề xuất**.

**Ràng buộc kèm theo, không được bỏ.** Con số "định vị khi ra tay" **không
bao giờ được trình bày một mình**. Thiếu tỷ lệ ra tay đứng cạnh thì nó bị hack
bằng cách im lặng: một hệ trả lời đúng một lượt rồi từ chối mọi lượt còn lại
đạt 1,000. `tests/test_moc3_bao_cao.py` chốt ràng buộc này bằng đúng ca đó.

**Con số thứ tư có mặt vì một lý do khác hẳn.** Lượt VERIFIED là lượt lỗi
tiêm vào nằm trong `null(A)` nên không sinh residual — không phương pháp
dựa-trên-ràng-buộc nào định vị nổi, và cả hai bên cùng mất điểm. Trên lượt
chạy 24/08 đó là 106/400, tức hơn một phần tư mẫu số. Phần khoảng cách nằm ở
đấy là kết quả của **H0**, không phải của phương pháp, và trộn nó vào chỉ số
H2 làm cả hai chỉ số khó đọc.

**Phạm vi.** Tu chính này đổi cách BÁO CÁO, không đổi phát biểu H2 cũng không
đổi điều kiện phản chứng ở mục 3. Nó được ghi **trước** lượt chạy Mốc 3 tiếp
theo, và lượt chạy ngày 24/08/2026 phải được đọc lại theo cách chấm này.

### 25/08/2026 — Ma trận nhầm chữ số đo được, dùng chung hai phía khác độ sâu

**Bối cảnh.** Bộ tiêm lỗi và bộ sinh ứng viên cầm hai bảng chữ số khác nhau,
cả hai đều là phỏng đoán: `inject.py` đổi một chữ số sang chữ số bất kỳ,
`repair/candidates.py` chỉ bốn cặp `(0,8) (1,7) (3,8) (5,6)`. Xác suất trùng
xấp xỉ (7/10)×(1/9) ≈ 0,078, đo được 0,092 trên lượt chạy 24/08/2026. Con số
`digit_substitution` của Mốc 3 vì thế là **độ trùng của hai bảng phỏng đoán**,
không mang thông tin gì về phương pháp.

**Sửa đổi.** Cả hai phía đọc từ một nguồn duy nhất là `src/nham_chu_so.py`,
nhưng **khác độ sâu**:

| Phía | Dùng gì | Chiều tra |
|---|---|---|
| `inject.py` | TOÀN BỘ phân phối, kể cả phần đuôi | xuôi, `thật → đọc thành` |
| `repair/candidates.py` | `N_CAP_UNG_VIEN = 6` cặp đầu bảng | ngược, `đọc thành → thật` |

**Khoảng hở giữa hai bên là thứ phải giữ, và đây là lý do.** Nếu hai phía
dùng cùng một bảng hữu hạn thì mọi lỗi tiêm vào đều sửa được, độ phủ lên
1,0, và thí nghiệm mất khả năng làm lộ cơ chế ABSTAIN — mà ABSTAIN chính là
lập luận chống bịa, đóng góp cấu trúc của cả bài. Một thí nghiệm không tạo
ra nổi tình huống nó tuyên bố xử lý được thì nó không kiểm chứng điều đó.
`tests/test_nham_chu_so.py::test_bo_sinh_ung_vien_KHONG_phu_het_ma_tran` chốt
ràng buộc này.

**N = 6 KHÔNG phải con số chọn sau khi thấy kết quả.** Nó lấy đúng
`MAX_MOI_NGUON` của `repair/candidates.py`, hằng số đã nằm trong repo từ khi
C1 ra đời, trước mọi phép đo ở đây. Hệ quả: **độ phủ là KẾT QUẢ, không phải
tham số** — với ma trận đã đóng băng, khối lượng tích luỹ của 6 cặp đầu bằng
**0,933**, và con số đó phải được báo cáo cùng bảng Mốc 3 chứ không giấu
trong phụ lục.

**Ma trận được commit TRƯỚC lượt chạy**, chép tay thành hằng số trong
`src/nham_chu_so.py` chứ không nạp từ file lúc chạy: một hằng số nằm trong
git diff chứng minh được thứ tự thời gian, còn một lời gọi đọc file thì
không, vì file đổi được sau mà không để lại vết trong lịch sử mã.

**Giới hạn phải nêu trong bài.** Lượt đo đầu chỉ dùng MỘT font và cho kết quả
thoái hoá — ba cặp, khối lượng chạm 1,000 ngay ở N = 3 — vì phân phối nhầm
chữ số phụ thuộc **typeface** chứ không phụ thuộc engine. Sáu font cho mười
cặp và đủ phần đuôi, nhưng các cặp đuôi chỉ đếm được một lần nên ước lượng ở
đó rất yếu. Ma trận đo trên ảnh render tổng hợp, không phải scan tiếng Việt
thật, nên tầng XBRL **lạc quan hơn** tài liệu Việt Nam thật ở chế độ lỗi này,
và con số phải đo lại trên tập gold khi có.

### 25/08/2026 — Chỉ số chính của H3 trên tầng XBRL tính ở mức LƯỢT

**Sửa đổi.** Trên tầng XBRL, chỉ số chính của H3 là **tỷ lệ lượt mà chỉ tiêu
bị tiêm lỗi vẫn còn sai sau khi sửa**, không phải tỷ lệ lỗi câm mức trường.
Tỷ lệ mức trường vẫn được báo cáo làm chỉ số phụ để so được với tầng gold.
Trên **tầng gold Việt Nam, chỉ số chính không đổi** — vẫn là tỷ lệ lỗi câm
mức trường như mục 1 đã chốt.

**Lý do — số học, không phải sở thích trình bày.** Hồ sơ XBRL có trung vị
**158 chỉ tiêu** (119–212 trên 26 hồ sơ đã tải), và mỗi lượt tiêm **đúng một
lỗi**. Qua 400 lượt, mẫu số của tỷ lệ lỗi câm mức trường là khoảng **65.200**
trong khi tử số nhiều nhất là **400**. Nghĩa là:

> Trần tuyệt đối của tỷ lệ lỗi câm trên tầng XBRL là **0,0061** — toàn bộ
> dải của chỉ số chỉ rộng **0,61 điểm phần trăm**.

Mục 1 lại chốt trước rằng *"hiệu số dưới 3 điểm phần trăm sẽ được trình bày
là không có khác biệt đáng kể về mặt thực tiễn, bất kể p-value"*. **Ba điểm
phần trăm lớn gấp gần năm lần toàn bộ dải của chỉ số.** Nên trên tầng XBRL,
mọi so sánh — dù phương pháp tốt đến đâu — đều tự động bị tuyên là không có
khác biệt đáng kể, và điều kiện phản chứng của H3 ở mục 3 **tự kích hoạt bất
kể kết quả**. Mốc 3 khi đó không thể đóng theo hướng đậu, chỉ có thể đóng
theo hướng trượt.

Ngưỡng 3 điểm phần trăm không sai; nó được viết cho tài liệu Việt Nam khoảng
25 chỉ tiêu, nơi một lỗi chiếm 4% số trường. Trên bảng XBRL 158 chỉ tiêu cùng
một lỗi chỉ chiếm 0,6%. **Ngưỡng không chuyển được giữa hai tầng**, và điều
đó không lộ ra vì hai tầng dùng chung một câu đăng ký trước.

**Kèm theo — số chữ số thập phân.** Báo cáo ba chữ số thập phân trên một chỉ
số có dải 0,0061 chỉ cho khoảng sáu giá trị phân biệt được: "0,005 so với
0,006" có thể là chênh 0 lượt, cũng có thể là chênh 65 lượt trên 400. Chỉ số
phụ mức trường phải in đủ chữ số để đọc được hiệu số, nếu không thì việc giữ
nó lại vô nghĩa.

**Phạm vi.** Tu chính này đổi ĐƠN VỊ QUAN SÁT của chỉ số chính trên một tầng
dữ liệu, không đổi phát biểu H3 và không đổi ngưỡng effect size 3 điểm phần
trăm. Nó được ghi **trước** lượt chạy Mốc 3 tiếp theo.

### 25/08/2026 — Tầng XBRL chỉ kiểm được khả năng SỬA cho 2 trong 4 chế độ lỗi

**Sửa đổi.** Ghi tường minh một giới hạn của tầng XBRL mà bản gốc không nêu:
tầng này kiểm được **phát hiện** và **định vị** cho cả bốn chế độ lỗi, nhưng
chỉ kiểm được **khả năng SỬA** cho `sign` và `digit_substitution`.

**Lý do — cấu trúc, không phải cài đặt.** `row_shift` và `col_shift` **ghi
đè** ô đích bằng giá trị của một ô khác, nên giá trị thật **biến mất khỏi
bảng**. Pipeline thật đọc lại ảnh vùng provenance thì lấy lại được; tầng
XBRL không có ảnh nên không nguồn ứng viên nào sinh lại nổi. Độ phủ ứng viên
đo được ngày 25/08/2026 trên 130 lượt mỗi chế độ: `row_shift` **0,015**,
`col_shift` **0,000**, so với `sign` 1,000 và `digit_substitution` 0,831.

Con số `col_shift` = 0,000 **không phải** do thiếu dữ liệu: việc chọn kỳ đã
sửa cùng ngày nên cả 130 lượt đều inject được, thay vì 10 lượt như lượt chạy
24/08/2026.

**Hệ quả cho cách đọc kết quả, và đây là phần quan trọng.** Phân vai "tầng
XBRL lo power, tầng gold Việt Nam lo validity" ở `ADDENDUM` mục 4 **hẹp hơn
đã viết**: với hai chế độ lỗi thuộc về BỐ CỤC TRANG — đúng hai chế độ mà
proposal mục 3.1 nêu là không tồn tại trong dữ liệu khảo sát và vì thế là
phần mới của đóng góp — tầng XBRL không cho power về khả năng sửa, chỉ tầng
gold Việt Nam cho. Trọng số của tập gold vì thế **tăng**, và mọi kết luận về
H3 cho `row_shift`/`col_shift` phải chờ tập gold.

**Không được lấp bằng cách sửa bộ tiêm.** Cho `inject` giữ lại giá trị gốc ở
đâu đó để bộ sinh ứng viên tìm thấy là dựng một tầng dữ liệu có ảnh giả, và
kết quả thu được sẽ không nói gì về pipeline thật.

### 25/08/2026 — Hoà ở tầng XBRL HOÃN phán quyết H3, không kích hoạt phản chứng

**Chốt khi CHƯA AI nhìn thấy một con số kết quả nào.** Lượt chạy Mốc 3 theo
cấu hình mới khởi động sau commit `68ce4d2`; câu hỏi được đặt và ghi vào repo
ở commit `113e741`, trước khi lượt chạy cho ra bảng. Thứ tự đó là điều kiện
để tu chính này còn giá trị, và nó kiểm chứng được bằng dấu thời gian git.

**Sửa đổi.** Bảng điều kiện phản chứng ở mục 3 quy định H3 sai khi *"baseline
9 ngang bằng phương pháp đề xuất"*. Trên **tầng XBRL**, điều kiện đó nay đọc
thành ba trạng thái thay vì hai:

| Kết quả trên tầng XBRL | Kết luận |
|---|---|
| Đề xuất **thắng** baseline 9 | Bằng chứng ủng hộ H3, và là bằng chứng MẠNH — xem lý do dưới |
| **Hoà** | **HOÃN phán quyết sang tầng gold Việt Nam.** Không kích hoạt điều kiện phản chứng |
| Đề xuất **thua** | Kích hoạt điều kiện phản chứng. Dừng, báo cáo, lùi bài |

Trên **tầng gold Việt Nam, mục 3 giữ nguyên**: hoà là hoà, và hoà kích hoạt
điều kiện phản chứng.

**Lý do — đo được, không phải lập luận.** Tầng XBRL đo phương pháp đề xuất
với cơ chế trung tâm của nó gần như bị tháo ra. Đo ngày 25/08/2026 trên 520
lượt: nguồn ứng viên `o_lan_can` sinh ra được giá trị thật **3 lần**, nguồn
`vlm_vote` **0 lần** vì tầng này không có phiếu VLM. Cả hai đều cần thứ mà
tầng này không có — **ảnh của trang giấy**.

Mà "đọc lại nguồn" chính là mệnh đề của H3. Nên trên tầng này, phương pháp đề
xuất đang chạy gần như chỉ với hai nguồn không cần ảnh (`nham_chu_so` và
`dau`), tức nó bị đo trong điều kiện đã bỏ đi đúng cái đang cần chứng minh.

Từ đó ra bất đối xứng:

- **Thắng** ở điều kiện đó là bằng chứng mạnh hơn bình thường, vì phương pháp
  thắng dù bị tháo cơ chế chính.
- **Hoà** không nói gì về H3. Nó nói: khi không có gì để đọc lại thì việc đọc
  lại không giúp gì — một mệnh đề hiển nhiên, không phải một phép bác bỏ.
- **Thua** vẫn là tín hiệu xấu thật, vì nó nghĩa là ngay cả ở hai nguồn không
  cần ảnh, việc neo ứng viên vào tài liệu cũng thua việc điền từ donor.

**Điều này KHÔNG nới lỏng H3, và đây là chỗ phải giữ.** Phán quyết được hoãn
sang tầng gold chứ không được bỏ. Tầng gold có ảnh, nên ở đó cả năm nguồn ứng
viên đều chạy và `o_lan_can` — nguồn mà `candidates.py` tự mô tả là "giá trị
nhất" — mới thực sự được kiểm. Nếu hoà ở tầng gold thì H3 sai, đúng như mục 3
đã viết.

**Hệ quả về nguồn lực, phải nói ra vì nó tốn tiền thật.** Mốc 3 sinh ra để
tránh bỏ 45–60 giờ gán nhãn cho một luận điểm đã chết. Tu chính này thu hẹp
quyền đó: một kết quả hoà ở tầng XBRL **không còn** cho phép huỷ việc gán
nhãn. Đổi lại, nó ngăn việc huỷ nhầm vì một phép đo không kiểm được thứ nó
định kiểm. Đánh đổi này được chấp nhận có ý thức.

---

### 25/08/2026 — Bộ chỉ tiêu chuyển từ kịch bản D sang kịch bản E

**Sửa đổi.** Bộ chỉ tiêu chốt ở Mốc 1 chuyển từ **kịch bản D** (20 chỉ tiêu
TT200 / 21 TT99, 7 đẳng thức) sang **kịch bản E** (26 / 27 chỉ tiêu, 9 đẳng
thức). Sáu chỉ tiêu thêm vào đều thuộc báo cáo lưu chuyển tiền tệ B03: ba
dòng lưu chuyển (mã 20, 30, 40), lưu chuyển thuần (50), tiền đầu kỳ (60),
ảnh hưởng tỷ giá (61).

Hai đẳng thức thêm vào, chép nguyên văn Công báo — TT200 Điều 114 và TT99
phần B03 khai báo **giống hệt nhau**:

    Mã số 50 = Mã số 20 + Mã số 30 + Mã số 40
    Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61

**Lý do chọn E.** Quyết định của người chủ trì ngày 24/08/2026, với lý do
học thuật: D vốn chỉ được chọn vì tính khả thi của việc gán nhãn chứ không
phải vì đúng hơn, còn E hơn D trên mọi trần định vị đo được (Top-1 0,54 so
với 0,50; Top-3 0,96 so với 0,90).

**Cơ chế riêng của E, và là lý do nó khác mọi nhóm mở rộng khác.** Văn bản
quy định mã 70 của B03 **bằng đúng** mã 110 của B01 kỳ đó, nên nó không cần
một chỉ tiêu riêng — đẳng thức thứ hai gắn thẳng vào `tien_va_tuong_duong_tien`
đã có sẵn. Đây là nhóm duy nhất mua được khả năng định vị cho một chỉ tiêu
**đã nằm trong bộ**, thay vì chỉ thêm chỉ tiêu mới. Nó cũng là câu trả lời
cho mục 6.1(d) của proposal: cột kỳ trước **có** ràng buộc thật nối vào, qua
`tien_dau_ky` — thứ mà văn bản quy định lấy từ mã 110 cột "Số đầu kỳ".

**Kết quả đo được sau khi thi công, báo cáo cả hai chiều.**

| | Kịch bản D | Kịch bản E |
|---|---:|---:|
| Chỉ tiêu (TT200 / TT99) | 20 / 21 | 26 / 27 |
| Đẳng thức | 7 | 9 |
| `rank(A)` | 7 | 9 |
| `dim null(A)` (TT200 / TT99) | 13 / 14 | **17 / 18** |
| Định vị được lỗi một-trường (TT200) | 5 / 20 | **7 / 26** |
| Chỉ tiêu có cột toàn 0 | 0 | 0 |

Chiều thuận: hai chỉ tiêu mới định vị được là `tien_va_tuong_duong_tien` và
`lctt_thuan`, và cái đầu đúng là cái mà cơ chế liên kết chéo nhắm tới.

**Chiều nghịch, và nó phải nằm trong bài chứ không chỉ trong repo:** không
gian null tăng từ 13 lên 17 chiều, còn **tỷ lệ** định vị được gần như đứng
yên — 25% lên 27%. Thêm 6 chỉ tiêu mà chỉ mua được 2 đẳng thức thì 4 chiều
chênh lệch rơi thẳng vào không gian vô hình. E tốt hơn D, nhưng nó không sửa
được kết luận nền tảng của H0: phần lớn mẫu lỗi vẫn vô hình với ràng buộc
đơn thuần, và đó vẫn là lý do phải đọc lại nguồn.

**Phạm vi.** Tu chính này đổi bộ chỉ tiêu, tức đổi đơn vị quan sát của H2 và
H3 và đổi mọi con số identifiability của H0. Nó KHÔNG đổi phát biểu của bốn
giả thuyết, không đổi chỉ số chính, không đổi điều kiện phản chứng, và không
đổi ngưỡng effect size 3 điểm phần trăm.

**Thời điểm, và vì sao nó hợp lệ.** `data/gold/` còn **trống hoàn toàn** khi
tu chính này được ghi, nên không tài liệu nào phải gán nhãn lại và không kết
quả nào trên tầng gold tồn tại để tu chính này có thể được chọn cho vừa. Đây
cũng là lần cuối cùng điều đó còn đúng: ngay khi tài liệu đầu tiên được gán
nhãn, mọi thay đổi bộ chỉ tiêu đều buộc phải quay lại cả tập.

**Việc chưa làm, và nó CHẶN việc gán nhãn tài liệu đầu tiên.** `ADDENDUM`
mục 6 chốt giao thức trần người ở 15 phút một tài liệu, đo khi bộ chỉ tiêu
còn nằm trên hai biểu mẫu. Với 26 chỉ tiêu rải qua **ba** biểu mẫu, giao
thức đó nhiều khả năng vỡ. Phải bấm giờ thử trên 3–5 tài liệu trước; nếu vỡ
thì sửa giao thức và ghi một tu chính nữa, **trước** khi gán nhãn tài liệu
đầu tiên chứ không phải sau.

### 25/08/2026 (muộn hơn) — Giao thức trần người bỏ con số 15 phút cố định

**Tu chính.** Giao thức đo trần người (`ADDENDUM` mục 6, thi hành ở
`ANNOTATION-GUIDELINE.md` mục 6) bỏ con số "15 phút một tài liệu". Số phút
đặt đồng hồ nay là **0,6 × trung vị `thoi_gian_giay` của 10 tài liệu gold đầu
tiên**, làm tròn tới phút, sàn 5 phút.

**Lý do, và nó ngược hẳn với điều tu chính ngay trên đây dự đoán.** Tu chính
kịch bản E ở trên viết rằng 26 chỉ tiêu rải qua ba biểu mẫu "nhiều khả năng
vỡ" giao thức 15 phút. Tài liệu gold đầu tiên (`VNM_2026Q1_TT99`, 27 chỉ
tiêu, ba biểu mẫu) cho số ngược lại: người chủ trì ước lượng công đoạn điền
hết **khoảng 10 phút**.

Điều đó không cứu giao thức, nó phá giao thức theo chiều khác. Con số 15 phút
tồn tại để **tạo áp lực thời gian**, tức để bản gán nhãn dùng đo trần khác
với bản gold đã phân xử kỹ. Nếu nhịp làm kỹ là 10 phút thì 15 phút là dư 5
phút: hai bản sẽ do cùng một người làm cùng một cách, trần người ra gần 100%,
và con số đó không diễn giải được kết quả hệ thống — tức mất đúng công dụng
mà `ADDENDUM` mục 6 nêu ở câu đầu tiên của nó.

**Vì sao chốt công thức chứ không chốt một con số.** Chốt thẳng "6 phút" từ
một ước lượng bằng cảm giác trên một tài liệu là chuyện không bảo vệ được:
`thoi_gian_giay` của tài liệu đó đang bằng 0, nên chưa có số đo nào tồn tại.
Ràng buộc thật sự cần đăng ký trước chỉ là **hệ số 0,6** — nó phải được chọn
trước khi nhìn thấy kết quả trần người, còn trung vị thì cứ để dữ liệu quyết.
Hệ số 0,6 không phải một hằng số dẫn xuất từ đâu cả; nó được ghi ở đây đúng
để không bị chọn lại về sau cho vừa kết quả. **Nó đang chờ người chủ trì xác
nhận hoặc đổi** — xem `HANDOFF.md` mục 0, Câu 9. Hạn chót của việc đổi là
thời điểm có đủ 10 tài liệu gold; sau đó, đổi hệ số là chọn tham số sau khi
đã thấy dữ liệu, và tu chính này mất hiệu lực bảo vệ.

> *Đã giải quyết:* người chủ trì xác nhận giữ 0,6 ngày 26/08/2026, khi tập
> gold còn 1 tài liệu và chưa tài liệu nào có số đo thời gian. Xem tu chính
> 26/08/2026 ở cuối file.

**Phạm vi: không tài liệu nào phải gán nhãn lại.** Tu chính chạm giao thức
của 10 tài liệu đo trần người, mà số tài liệu đã gán nhãn dưới giao thức đó
là **0**. `VNM_2026Q1_TT99` gán nhãn kỹ, không dưới đồng hồ. Không chỉ số
nào của H0–H3 đổi; trần người là số dùng để **diễn giải** kết quả chứ không
nằm trong phát biểu giả thuyết nào.

**Một thứ tự cam kết đã bị vượt.** Tu chính ngay trên đây tuyên bố việc đo
lại trần người "CHẶN việc gán nhãn tài liệu đầu tiên" và phải làm trước.
Thực tế chạy ngược: tài liệu đầu tiên được gán nhãn trước, và chính nó là
nguồn số liệu duy nhất để sửa giao thức. Ghi lại ở đây vì preregistration
mất giá trị nếu chỉ ghi những lần làm đúng thứ tự. Thiệt hại đo được bằng 0
theo đoạn Phạm vi ở trên, nhưng cam kết thì đã không được giữ nguyên văn, và
người đọc đối chiếu hai tu chính này sẽ thấy điều đó mà không cần ai giải
thích.

### 26/08/2026 — Hệ số 0,6 được chốt, và `thoi_gian_giay` đổi định nghĩa

**Tu chính, hai phần.** Cả hai chạm giao thức đo trần người ở `ADDENDUM` mục
6 và `ANNOTATION-GUIDELINE.md` mục 6, không phần nào chạm phát biểu của bốn
giả thuyết.

**(a) Hệ số 0,6 hết trạng thái chờ.** Tu chính 25/08/2026 ngay trên đây đặt
số phút đo trần người ở `0,6 × trung vị thoi_gian_giay của 10 tài liệu gold
đầu tiên`, và ghi rõ rằng hệ số 0,6 do phiên Claude đề xuất chứ không phải
người chủ trì chọn. Người chủ trì xác nhận **giữ 0,6** ngày 26/08/2026.

Thời điểm là thứ đáng ghi hơn cả con số. Lúc xác nhận, `data/gold/` có đúng
**một** tài liệu và nó mang `thoi_gian_giay` bằng 0 — tức **chưa một số đo
thời gian nào tồn tại**, nên hệ số không thể được chọn cho vừa một trung vị
đã nhìn thấy. Đây đúng là điều kiện mà việc đăng ký trước cần, và nó chỉ còn
đúng trong một cửa sổ hẹp: tài liệu gold thứ hai có đồng hồ chạy thật sẽ đóng
cửa sổ đó lại vĩnh viễn.

**(b) `thoi_gian_giay` nay là thời gian LÀM VIỆC, không phải thời gian đồng
hồ tường.** Đây là thay đổi định nghĩa của chính đại lượng mà công thức ở
phần (a) lấy trung vị, nên nó phải nằm ở đây chứ không chỉ nằm trong
guideline.

Bản trước, công cụ gán nhãn tự khởi động đồng hồ lúc người gõ xong `doc_id`
và lấy hiệu tới lúc bấm Lưu. Cách đo đó lệch theo cả hai chiều, và không
chiều nào nhỏ: gõ `doc_id` xong mới đi tìm file PDF, hay để cửa sổ mở qua
buổi trưa, đều cộng vào những quãng không phải thời gian làm việc; ngược lại,
người điền siêu dữ liệu sau cùng thì đồng hồ gần như không chạy. Với `n = 10`
thì một tài liệu lệch kiểu đó đủ sức đẩy trung vị, và trung vị đó nhân với
0,6 ra thẳng số phút mà bản đo trần người phải sống dưới nó.

Nay người gán nhãn tự bấm **Bắt đầu** và **Tạm dừng**; `thoi_gian_giay` là
tổng các đoạn chạy. Hai khoá mới đi kèm, cả hai đều để phép đo tự khai giới
hạn của nó thay vì bắt người đọc suy đoán:

- `trang_thai_dong_ho` — `"da_do"` hoặc `"khong_do"`. Trung vị chỉ lấy trên
  các file `"da_do"`. Trước khoá này, một tài liệu không ai bấm giờ và một
  tài liệu bấm giờ ra 0 giây ghi ra file giống hệt nhau.
- `so_lan_tam_dung` — số lần ngắt quãng. Một tài liệu làm liền mạch và một
  tài liệu dừng năm lần có thể ra cùng một `thoi_gian_giay`, nhưng chúng
  không đáng tin như nhau, và về sau kiểm được xem có nên loại các lượt ngắt
  quãng nhiều khỏi trung vị hay không.

Công cụ **từ chối ghi file gold** khi đồng hồ chưa từng chạy, trừ khi người
gán nhãn tick "không đo giờ tài liệu này". Lối thoát đó có thật vì gán nhãn
lại một tài liệu cũ là việc hợp lệ mà con số thời gian ở đó vô nghĩa, nhưng
nó phải là một hành động tường minh — cùng nguyên tắc mà guideline mục 3.1
đã dùng cho ca báo cáo không khai báo đơn vị tính.

**Phạm vi: không tài liệu nào phải gán nhãn lại, và lần này thứ tự cam kết
được giữ.** Số tài liệu mang số đo thời gian dưới định nghĩa cũ là **0**, nên
không có số liệu nào phải bỏ đi. Không chỉ số nào của H0–H3 đổi. Khác với tu
chính 25/08 — nơi tài liệu đầu tiên chạy trước tu chính đáng lẽ phải chặn nó —
tu chính này được ghi **trước** khi bất kỳ tài liệu nào được gán nhãn dưới
giao thức bấm giờ mới.

---

### 26/08/2026 (muộn nhất) — Độ phân giải bản quét là hiệp biến, ghi trước khi có kết quả

**Cam kết thêm, không cam kết nào bị rút.** Kể từ đây mỗi tài liệu gold mang
một số đo độ phân giải bản quét, ghi ở khoá `do_phan_giai_dpi` trong
`data/nguon_gold.json` và sinh bằng `python src/do_do_phan_giai.py`.

**Vì sao phải đăng ký trước, dù bản này chưa từng nhắc tới độ phân giải.**
`ANNOTATION-GUIDELINE.md` mục 7 vừa đổi nhóm Stress thứ ba sang trục độ phân
giải, nên từ nay tập gold có một biến giải thích mà trước đó không có. Một
biến như thế rất dễ trở thành thứ được lôi ra sau khi bảng kết quả đã xong,
để giải thích một chênh lệch không mong đợi — và lúc đó không ai phân biệt
được nó với việc đi tìm hậu nghiệm. Ghi trước là cách duy nhất giữ nó dùng
được.

**Nó dùng vào việc gì, và không dùng vào việc gì.**

- **Được dùng** cho một phân tích THỨ CẤP, khai báo là thứ cấp trong bài: hồi
  quy hoặc tương quan giữa độ phân giải và tỷ lệ lỗi mức trường, để trả lời
  câu "kết quả có phụ thuộc chất lượng ảnh không".
- **Được dùng** để chọn tài liệu vào nhóm Stress, theo thứ hạng trong tập
  gold chứ không theo ngưỡng tuyệt đối.
- **KHÔNG được dùng** để loại tài liệu khỏi phân tích chính, dù số đo thấp
  đến đâu. Loại theo một biến đo được sau khi đã thấy kết quả là cắt mẫu.
- **KHÔNG đổi** chỉ số chính hay điều kiện phản chứng của bất kỳ giả thuyết
  nào. H1, H2, H3 giữ nguyên định nghĩa.

**Không có ngưỡng nào được chốt ở đây**, cố ý. Số đo trên mười tài liệu đầu
là 89,9–295,8 dpi, nhưng **sáu trong mười rơi đúng 200,0 dpi** — phân bố dồn
cục chứ không trải đều. Chốt một ngưỡng trên phân bố như thế là chọn tham số
trên mẫu mỏng. Ngưỡng, nếu về sau cần, phải là tu chính riêng và phải ghi
trước khi nhìn bảng kết quả tương ứng.

**Giới hạn phải nêu trong bài:** độ phân giải không bao trọn chất lượng ảnh.
Trang lệch, dấu mộc đè lên chữ số và in mờ lệch nét là những trục riêng, hiện
chỉ ghi bằng lời chứ chưa đo được, nên một hệ số tương quan bằng 0 với dpi
KHÔNG cho phép kết luận rằng chất lượng ảnh không ảnh hưởng.

### 05/09/2026 — Dòng không neo được vào vùng nào: ứng viên duy nhất là `0`, và trần sửa nâng lên 4

**Hai sửa đổi trong một mục vì chúng cùng đến từ một lượt chạy và cùng đổi
hành vi của `diagnose()`.** Cả hai được người chủ trì quyết ngày 05/09/2026,
**SAU khi đã thấy kết quả lượt H3 ngày 05/09**. Ghi rõ điều đó ở đây thay vì
để người đọc tự phát hiện: đây là thời điểm xấu nhất để đổi thiết kế, nên
gánh nặng biện minh nằm về phía hai sửa đổi này.

#### Sửa đổi 1 — chỉ tiêu không neo được vào vùng nào thì ứng viên duy nhất là `0`

**Phát biểu.** Khi một chỉ tiêu không neo được vào vùng bảng nào trên trang
(trạng thái `khong_co_vung`) **và** tên nó nằm trong
`fields_config.CO_THE_VANG_MAT`, tập ứng viên của nó là **đúng một phần tử:
giá trị `0`**. Các nguồn ứng viên khác — biến thể nhầm chữ số, biến thể dấu,
biến thể bậc đơn vị, phiếu VLM — bị **thay thế**, không phải bổ sung.

**Vì sao thay thế chứ không bổ sung.** Không neo được vào vùng nào nghĩa là
không có chỗ nào trên tờ giấy để đọc lại. Khi đó mọi ứng viên còn lại đều là
phép biến đổi của một con số mà máy đã bịa ra từ hư không — lật dấu nó, đổi
bậc nó, đọc lệch một chữ số của nó. Giữ chúng lại là cho phương pháp tiếp tục
nặn một con số không có nguồn. Số đo ngày 05/09 cho thấy đúng điều đó: **cả 4
ô mà phương pháp đề xuất làm hỏng** đều nằm ở loại lỗi này (2 ô
`thue_tndn_hoan_lai`, 2 ô `thue_tndn_hien_hanh`), và không ô nào trong 14 ô
cùng loại được nó chữa đúng.

**Vì sao `0` vẫn là kết luận rút từ TỜ GIẤY.** Thông tư 99/2025 mục 1.2.3 cho
phép miễn trình bày chỉ tiêu không có số liệu, nên một dòng vắng mặt trên
biểu mẫu là **bằng không**, không phải *chưa biết*. Quy tắc này KHÔNG mới:
tu chính 24/08/2026 đã chốt đúng nó cho phía gán nhãn tay, và
`ANNOTATION-GUIDELINE.md` mục 3.4 đã áp dụng từ đó. Sửa đổi hôm nay chỉ đưa
cùng một cách đọc sang phía pipeline. Đây là lập luận phân biệt nó với việc
mượn phân phối ngành của baseline 9: dòng trống là một quan sát về tài liệu
NÀY, không phải một con số vay từ tài liệu khác.

**Vì sao hẹp theo `CO_THE_VANG_MAT` chứ không áp cho mọi chỉ tiêu.** Trạng
thái `khong_co_vung` gộp hai chuyện khác hẳn nhau: dòng thật sự trống, và
dòng CÓ IN mà khâu neo trượt. Áp cho mọi chỉ tiêu là dựng lại đúng khuyết tật
đã đo được ngày 04/09, khi tin kết luận "không thấy dòng" một cách vô điều
kiện đã điền `tong_tai_san = 0` cho `PLX_2026Q2_TT99` trong khi giá trị thật
là 87.876 tỷ. `CO_THE_VANG_MAT` gồm tám dòng CHI TIẾT, chọn theo cấu trúc
biểu mẫu, và có test bất biến chặn mọi dòng TỔNG lọt vào — dòng tổng là bộ
xương biểu mẫu nên luôn được in.

**ĐIỂM YẾU PHẢI NÊU TRONG BÀI, không được giấu.** Danh sách
`CO_THE_VANG_MAT` tuy dựng theo tiêu chí cấu trúc nhưng đã được **mô phỏng
đối chiếu với một lượt chạy** trước khi chốt ngày 04/09, nên nó không mù hoàn
toàn với đáp án. Và quyết định tái sử dụng nó cho sửa đổi hôm nay đến sau khi
biết rằng **cả bốn chỉ tiêu baseline 9 đang thắng ở loại lỗi này đều nằm
trong danh sách**. Người phản biện có quyền đọc đây là chọn phạm vi theo kết
quả. Phản biện lại được bằng ba điều, và bài phải nêu cả ba: tiêu chí là cấu
trúc biểu mẫu chứ không phải tần suất lỗi; danh sách chốt TRƯỚC lượt H3 và
không sửa sau đó; và hai ô sai đã biết là `tsnh_khac`, `ln_khac` vẫn được cố
ý để nguyên trong danh sách thay vì gỡ ra cho đẹp số.

**Chi phí ứng viên.** Nguồn mới `dong_trong` có xác suất tiên nghiệm `0,20`,
bằng nguồn `sign` và **thấp hơn** `ocr_alt` (`0,35`). Đặt thấp hơn là có chủ
đích và lệch về phía an toàn: nếu nó rẻ hơn mọi nguồn khác thì bộ giải sẽ
thích xoá trắng một dòng hơn là sửa một chữ số đọc nhầm ở chỗ khác, mà xoá
trắng một dòng CÓ IN chính là chế độ lỗi PLX ở trên. Sai theo chiều này thì
chỉ tiêu không được sửa; sai theo chiều kia thì nó bị điền `0` một cách im
lặng.

**Áp cho ai.** Chỉ áp cho phương pháp đề xuất. Baseline 9 không dùng tập ứng
viên sinh từ tài liệu nên khái niệm này không tồn tại ở đó, và baseline 8 sửa
liên tục nên cũng không. Đây KHÔNG phải vi phạm ràng buộc cùng ngân sách: ngân
sách tính bằng số lần gọi model, mà nguồn `dong_trong` không gọi model lần nào.

#### Sửa đổi 2 — trần `max_changes` nâng từ 2 lên 4, và giới hạn thời gian nâng theo

**Phát biểu.** `MAX_CHANGES_MAC_DINH` đổi từ `2` thành `4`. Trần vẫn áp cho
**cả** `diagnose()` lẫn hai bản của baseline 9, đúng như tu chính 22/08/2026
quy định, vì H3 so ở cùng ngân sách. Baseline 8 vẫn nằm ngoài.

**Lý do.** Số đo ngày 05/09 cho thấy trần 2 thực sự chặn phương pháp ở đúng
**hai** tài liệu — `HPG_2022Q2` sai 3 ô và `HVG_2020Q1` sai 5 ô. Tám tài liệu
còn lại mà phương pháp bỏ qua là do thiếu ứng viên chứ không do trần. Trần 4
mở được `HPG_2022Q2` và tiến sát `HVG_2020Q1`.

**PHẢI NÓI RÕ: đây là quyết định của người chủ trì, ngược với khuyến nghị.**
Phân tích đưa ra ngày 05/09 khuyến nghị GIỮ trần 2, với lý do khoản lợi nhỏ
còn tu chính 22/08 đã chốt trần là *hạn chế của phương pháp* chứ không phải
tham số tinh chỉnh. Người chủ trì quyết nâng lên 4. Ghi lại cả khuyến nghị lẫn
quyết định để bài không trình bày trần 4 như thể nó luôn là thiết kế gốc.

**Cái giá, đo được ngày 05/09 chứ không đoán.** Số tổ hợp phải duyệt là đa
thức đối xứng sơ cấp bậc k của số ứng viên từng trường, đếm chính xác:

| Trần | TT200 (26 chỉ tiêu) | TT99 (27 chỉ tiêu) |
|---:|---:|---:|
| 2 | 44 nghìn tổ hợp · 0,1 giây | 47 nghìn · 0,3 giây |
| 3 | 4,1 triệu · 13 giây | 4,5 triệu · 26 giây |
| 4 | **274 triệu · 14,5 phút** | **315 triệu · ~30 phút** |

Chi phí này chỉ phải trả ở ca **VÔ NGHIỆM**, vì tìm kiếm dừng ở `k` đầu tiên
có nghiệm. Nhưng ca vô nghiệm lại là ca thường gặp — tập ứng viên cố ý không
đóng — và cũng chính là ca duy nhất đỡ được luận điểm chống bịa.

**Hệ quả bắt buộc: `TIME_LIMIT_S` nâng từ 30 giây lên 2400 giây.** Không nâng
thì mọi ca vô nghiệm ở trần 4 đều chạm giới hạn thời gian và trả `het_gio`
thay vì `vo_nghiem`. Tu chính 22/08 đã chốt rằng chỉ `vo_nghiem` mới chứng
minh được "không cách đọc nào của tài liệu này làm bảng cân đối được", còn
`het_gio` không chứng minh gì cả. Nghĩa là trần 4 kèm giới hạn 30 giây sẽ
**xoá sạch bằng chứng chống bịa** trong khi mọi con số khác trông vẫn bình
thường — đúng loại hỏng hóc im lặng mà cơ chế phân loại `ma_ly_do` được dựng
lên để bắt.

**Ảnh hưởng tới lịch chạy, phải tính trước khi chạy.** Lượt H3 ngày 05/09 có
20 trong 28 tài liệu khó rơi vào ABSTAIN. Nếu tỷ lệ ấy giữ nguyên thì trần 4
cộng thêm khoảng **5–10 giờ** vào một lượt 70 tài liệu vốn đã tốn 9,5 giờ.
Con số này phải được kiểm lại bằng một lượt thử vài tài liệu trước khi cam kết
chạy trọn tập.

**HẠ XUỐNG 3 CÙNG NGÀY, sau khi thấy bảng chi phí trên.** Người chủ trì chốt
trần **3** thay vì 4. Ghi cả hai bước — nâng lên 4 rồi hạ xuống 3 trong cùng
ngày 05/09/2026 — chứ không sửa đè con số cũ, vì lịch sử ấy chính là thứ giải
thích vì sao trần không còn là 2: trần 3 mở được `HPG_2022Q2` (sai 3 ô) nên
lấy được phần lớn cái mà việc nâng trần nhắm tới, trong khi chỉ cộng khoảng 7
phút vào một lượt 70 tài liệu thay vì 5-10 giờ. `HVG_2020Q1` (sai 5 ô) vẫn
ngoài tầm, nhưng nó ngoài tầm cả ở trần 4.

`TIME_LIMIT_S` hạ theo, từ 2400 xuống **300 giây** — vẫn là biên hơn mười lần
so với 26 giây đo được ở trần 3, nên `vo_nghiem` vẫn tới được. Hai hằng số này
phải đi cùng nhau: một trần cao kèm giới hạn thời gian thấp sẽ biến mọi ca vô
nghiệm thành `het_gio` và xoá sạch bằng chứng chống bịa.

**Đường thoát nếu chi phí không chấp nhận được:** vòng tìm kiếm hiện duyệt vét
cạn mọi tích ứng viên. Vì phần dư nằm trong `R^9`, một cài đặt gặp-ở-giữa
(chia `k` làm hai nửa, băm nửa đầu rồi tra nửa sau) hạ 274 triệu tổ hợp xuống
cỡ hai lần 44 nghìn phép băm. Đó là thay đổi CÀI ĐẶT, không phải thay đổi
thiết kế thí nghiệm, nên không cần tu chính — nhưng nó đụng vào thuật toán
trung tâm của bài nên phải kèm test chứng minh cho ra cùng nghiệm.

### 05/09/2026 (muộn hơn) — H2 đo trên 1, 2 và 3 lỗi đồng thời, không chỉ 1

**Sửa đổi.** Giao thức tiêm lỗi của tầng XBRL chạy quét `n_errors ∈ {1, 2, 3}`
thay vì cố định `n_errors = 1`. Mọi bảng H2 báo cáo **tách theo số lỗi tiêm**,
không gộp. Đây là trả lời cho Câu 8, do người chủ trì quyết ngày 05/09/2026.

**Lý do, và nó là một CHỨNG MINH chứ không phải một nghi ngờ.** Bản đăng ký
trước chỉ nghi rằng giao thức một-lỗi chọn ca thuận lợi cho baseline 9. Với
baseline 7 (`repair.ged`) thì chứng minh được:

> Dưới giả thiết đúng MỘT trường sai, phần dư là `r = δ·a_j` với `a_j` là cột
> của trường sai. Thống kê GLR `T_i = (a_iᵀr)²/(a_iᵀa_i)` khi đó thoả
> `T_i ≤ T_j` với mọi `i`, theo bất đẳng thức Cauchy–Schwarz, và dấu bằng xảy
> ra đúng khi `a_i` tỷ lệ với `a_j`.

Nghĩa là ở giao thức một-lỗi, baseline 7 **không thể bị đánh bại bằng chất
lượng thuật toán** — nó chỉ trượt khi hai cột không phân biệt được, tức khi
thông tin không tồn tại. Một bảng H2 đo trên đúng một lỗi vì vậy đo **trần
định vị của hệ ràng buộc**, không đo phương pháp. Mệnh đề này có test chốt
trên ma trận ràng buộc thật của cả hai chuẩn (`tests/test_ged.py`, lớp 1).

Với hai hoặc ba lỗi đồng thời, phần dư là tổ hợp tuyến tính của nhiều cột nên
chữ ký hướng nhoè đi, cận trên kia không còn, và phép so mới tách được các
phương pháp theo đúng thứ nó định tách.

**QUÉT chứ không THAY THẾ.** Giữ nguyên `n = 1` trong bộ quét vì hai lý do:
mọi kết quả đã đo trước ngày này vẫn so được, và cái đáng giá về mặt khoa học
là **đường cong suy giảm** theo số lỗi — mỗi phương pháp tụt nhanh chậm ra sao
— chứ không phải một điểm đơn lẻ ở `n = 3`.

**H3 KHÔNG ĐỔI.** Bảng H3 và mọi chỉ số của nó (tỷ lệ lỗi câm, chỉ số chống
bịa, `luot_con_sai`) vẫn chỉ tính trên `n = 1`, đúng giao thức đã đăng ký. Trộn
các lượt nhiều lỗi vào đó sẽ đổi con số đầu bảng của Mốc 3 mà không ai thấy.
Sửa đổi này vì vậy **chỉ mở rộng H2**.

**Tính chất lồng nhau, ghi để người đọc khỏi tưởng ba lượt độc lập.** Với cùng
`seed`, `inject()` duyệt cùng một danh sách đã xáo theo cùng thứ tự, nên tập
lỗi của `n = 1` là tập con của `n = 2`, và tập của `n = 2` là tập con của
`n = 3`. Ba mức vì vậy KHÔNG độc lập, và mọi phép kiểm định trên hiệu số giữa
chúng phải là kiểm định GHÉP CẶP.

**Giới hạn phải nêu trong bài.** Trần `max_changes` ở tầng XBRL là 2, nên khi
tiêm 3 lỗi thì phương pháp đề xuất và baseline 9 **về cấu trúc không thể sửa
hết**, và bảng Top-k của chúng bị chặn ở 2 tên trong khi baseline 7 và 8 luôn
trả bảng đầy đủ. Khoảng cách ở Top-3 vì vậy có một phần là hình dạng của
phương pháp chứ không phải độ chính xác. Bảng kết quả in kèm số lỗi tiêm và
trần của từng phe để đọc được điều đó.

**Chi phí.** Bộ quét ba mức làm số lượt chạy của tầng XBRL tăng gấp ba. Lượt
`n = 1` đo được ngày 05/09 là ~7 giờ trên 26 hồ sơ, nên bộ quét đủ vào khoảng
20 giờ, chạy offline và không tốn lời gọi API nào.

**Phải chạy lại tầng XBRL** sau sửa đổi này. Kết quả H2 nào đo trước ngày
05/09/2026 chỉ là điểm `n = 1` của bộ quét, và không được trình bày như kết
quả H2 đầy đủ.
