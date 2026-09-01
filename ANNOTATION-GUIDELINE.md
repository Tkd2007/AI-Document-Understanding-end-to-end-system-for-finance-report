# Guideline gán nhãn tập gold — ViFinKIE

**Phiên bản 1.0 — 23/08/2026.**

> **Guideline này viết TRƯỚC khi gán nhãn tài liệu đầu tiên, và không được
> sửa giữa chừng.** Nếu buộc phải sửa, ghi vào mục "Sửa đổi" ở cuối kèm ngày
> và lý do, rồi **gán nhãn lại toàn bộ phần đã làm trước đó**. Không có kỷ
> luật này thì tập gold là hỗn hợp của nhiều quy tắc khác nhau và không ai
> biết tài liệu nào theo quy tắc nào — hỏng ở mức không sửa được bằng cách
> làm thêm.
>
> Căn cứ: `ADDENDUM-statistical-treatment.md` mục 5.

---

## Mục lục

1. **Ba luật bắt buộc** — mù với đầu ra pipeline, gán nhãn xong mới chạy
   pipeline, guideline viết trước không sửa giữa chừng
2. Phạm vi — doanh nghiệp, loại báo cáo, biểu mẫu, cột
3. **Quy tắc đọc số** — phần dễ bất đồng nhất, đọc kỹ 3.1, 3.3, 3.4, 3.6, 3.7
4. Định dạng file
5. Đo đồng thuận giữa hai người
6. **Trần người** — cách tính số phút đặt đồng hồ
7. Thành phần tập gold — bốn nhóm Stress
8. **Danh mục kiểm** trước khi coi một tài liệu là xong
9. Sửa đổi — mọi thay đổi quy tắc, kèm ngày và lý do

Tài liệu đã chọn và URL nguồn: `data/nguon_gold.json`, tải bằng
`python src/tai_bctc.py`.

---

## 1. Ba luật bắt buộc

Ba luật này quyết định tập gold có dùng được hay không. Vi phạm bất kỳ luật
nào cũng làm hỏng dữ liệu theo kiểu **không phát hiện được về sau**.

### Luật 1 — Người gán nhãn phải MÙ với đầu ra pipeline

Không mở `data/output/*_routed.json`, không chạy `router.py`, không xem log,
không xem kết quả của bất kỳ model nào trên tài liệu đang gán nhãn.

*Vì sao:* thấy con số của model trước thì sẽ neo vào đó. Một con số sai
nhưng trông hợp lý sẽ được chép lại thay vì bị bắt — và ground truth nhiễm
đúng bằng lỗi mà nó sinh ra để đo. Đây là luật quan trọng nhất và cũng là
luật dễ vi phạm nhất khi làm một mình cho nhanh.

### Luật 2 — Gán nhãn XONG mới chạy pipeline trên tài liệu đó

Thứ tự thời gian phải kiểm chứng được. `annotated_at` trong file JSON phải
**sớm hơn** dòng tương ứng trong `data/output/metrics.jsonl`.

### Luật 3 — Guideline viết trước, không sửa giữa chừng

Xem khung ở đầu file.

---

## 2. Phạm vi

| Mục | Quyết định | Lý do |
|---|---|---|
| Loại doanh nghiệp | **Phi tài chính.** Loại tổ chức tín dụng và chi nhánh ngân hàng nước ngoài, **công ty chứng khoán, doanh nghiệp bảo hiểm, công ty quản lý quỹ** | Cả bốn nhóm lập báo cáo theo chế độ kế toán riêng của ngành nên **mẫu biểu và mã số khác hẳn**. *Nói rõ 01/09/2026:* bản cũ chỉ kể tên tổ chức tín dụng, nên 9 tài liệu ngân hàng / chứng khoán / bảo hiểm vẫn lọt vào tập tải — xem mục Sửa đổi |
| Loại báo cáo | Báo cáo **riêng** hoặc **hợp nhất**, nhưng phải ghi rõ | Hai loại có số khác nhau trên cùng một doanh nghiệp cùng một kỳ. Không ghi rõ là trộn hai tổng thể |
| Biểu mẫu | B01, B02 **và B03** (mọi biến thể kỳ: không hậu tố, `a`, `b`) | **Sửa 25/08/2026:** bộ chỉ tiêu chuyển sang kịch bản E nên B03 nay CÓ gán nhãn — 6 chỉ tiêu. Xem mục Sửa đổi |
| Cột | **Kỳ NGẮN NHẤT và MỚI NHẤT**: bảng cân đối lấy cột có ngày mới nhất; bảng kết quả kinh doanh lấy nhóm **Quý**, kỳ này — **KHÔNG lấy cột luỹ kế** | **Chốt 23/08/2026:** cột kỳ so sánh KHÔNG gán nhãn — lý do ở `PREREGISTRATION.md` mục Sửa đổi. **Nói rõ 28/08/2026:** B02 có BỐN cột và hai nhóm kết thúc cùng ngày, nên đừng chọn bằng ngày kết thúc, cũng đừng chọn bằng vị trí (trang có thể xoay 90°) |

**Bộ chỉ tiêu: 27 với TT99, 26 với TT200.** Danh sách chính thức là
`FIELD_MAP` trong `src/fields_config.py`; đừng chép lại vào đây kẻo hai bản
lệch nhau. Chênh lệch một chỉ tiêu là do **Tài sản sinh học ngắn hạn** chỉ
tồn tại ở TT99.

**Sáu chỉ tiêu B03 là phần mới nhất, và có một chỗ dễ sai:** mã số 70 của
B03 (tiền và tương đương tiền cuối kỳ) **KHÔNG** phải một chỉ tiêu riêng.
Văn bản quy định nó bằng đúng mã 110 trên B01 kỳ đó, nên nó đã nằm sẵn ở
`tien_va_tuong_duong_tien`. Gán nhãn nó thành một trường thứ hai sẽ tạo ra
hai chỉ tiêu cho cùng một con số. Nếu số ở hai chỗ **khác nhau** thì đó là
lỗi của chính báo cáo hoặc của việc bạn đọc — dừng lại và ghi vào ghi chú,
đừng tự chọn một trong hai.

**Hậu tố `a`/`b` của ký hiệu mẫu biểu là KỲ BÁO CÁO, không phải Thông tư.**
`B01-DN` là báo cáo năm, `B01a-DN` là giữa niên độ dạng đầy đủ (tức quý),
`B01b-DN` là dạng tóm lược. Cả hai Thông tư đều dùng đủ ba ký hiệu, và biểu
mẫu giữa niên độ dùng **cùng bộ mã số** với biểu mẫu năm. Xác định chuẩn
bằng TÊN báo cáo (mục 3.7), đừng bao giờ bằng hậu tố này.

---

## 3. Quy tắc đọc số — phần dễ bất đồng nhất

### 3.1 Đơn vị tính

Ghi **hai** thứ, không phải một:

- `unit_declared` — **nguyên văn** dòng khai báo trên báo cáo. Chép đúng như
  in: `"Đơn vị tính: triệu đồng"`, `"(Đơn vị: VNĐ)"`, `"triệu VNĐ"`.
- `unit_multiplier` — hệ số đã diễn giải: đồng = `1`, nghìn đồng = `1000`,
  triệu đồng = `1000000`, tỷ đồng = `1000000000`.

*Vì sao giữ cả hai:* việc đọc được dòng đơn vị tính là **đối tượng nghiên
cứu hạng nhất**, không phải chú thích — nó là mỏ neo duy nhất phá được bất
biến scale. Giữ nguyên văn cho phép về sau đo riêng "hệ đọc đúng dòng này ở
bao nhiêu phần trăm báo cáo".

**Không tìm thấy dòng khai báo:** ghi `unit_declared` là chuỗi rỗng và
`unit_multiplier = 1`, rồi ghi vào `notes` rằng báo cáo không khai báo đơn
vị. **Đừng suy ra từ độ lớn con số** — đó chính là việc ta muốn đo xem hệ
thống làm được không, nên người gán nhãn làm thay là làm hỏng phép đo.

### 3.2 Giá trị ghi vào `values` đã QUY ĐỔI VỀ ĐỒNG

Báo cáo in `29.403` ở đơn vị "triệu đồng" thì ghi `29403000000`.

*Vì sao:* hai tài liệu khác đơn vị mà lưu ở đơn vị gốc thì không so được với
nhau, và mọi phép đo accuracy trên nhiều công ty mất nghĩa.

### 3.3 Số âm, và quy ước dấu của B02

**Luật một câu: chép ĐÚNG NHƯ IN. Ngoặc đơn là âm, không ngoặc là dương.**
Áp cho mọi chỉ tiêu, không trừ chỉ tiêu nào — kể cả giá vốn hàng bán và hai
dòng thuế. Một số báo cáo dùng dấu trừ thay ngoặc; cả hai đều là số âm.

*Vì sao không còn ngoại lệ nào:* chép nguyên văn là thao tác **cơ học và tái
lập được**. Hai người gán nhãn độc lập nhìn cùng một ô sẽ ra cùng một số, nên
độ đồng thuận đo được phản ánh chất lượng ĐỌC chứ không phản ánh mức độ hai
người hiểu kế toán giống nhau. Nó cũng nhất quán với mục 3.5 vốn đã cấm "sửa
cho cân": nhãn gold phải phản ánh tờ giấy, mọi diễn giải là việc của tầng sau.

#### Nhưng phải ghi thêm MỘT thứ: quy ước dấu của tài liệu

Chép nguyên văn thì con số một mình không tự diễn giải được. `51 =
68.069.473.287` không nói được đó là chi phí thuế hay thu nhập thuế; phải biết
tài liệu in theo quy ước nào mới biết. Quy ước ấy **cũng nằm trên tờ giấy**,
nên nó là dữ liệu phải ghi lại, không phải kiến thức phải suy.

Đây đúng khuôn mẫu đã dùng cho đơn vị tính ở mục 3.1: `unit_declared` giữ
nguyên văn, `unit_multiplier` giữ phần diễn giải. Quy ước dấu là mỏ neo phá
**bất biến dấu** y như dòng đơn vị tính là mỏ neo phá bất biến scale.

Ghi vào khoá `quy_uoc_dau` của file gold, ba giá trị:

| Giá trị | Trên báo cáo | Hai đẳng thức B02 thành |
|---|---|---|
| `tong` | khoản trừ in **trong ngoặc** (mã 11 âm) | `20 = 10 + 11`, `60 = 50 + 51 + 52` |
| `tru` | khoản trừ in **độ lớn** (mã 11 dương) | `20 = 10 − 11`, `60 = 50 − 51 − 52` |
| `khong_xac_dinh` | không đọc được | hai đẳng thức trên **bị bỏ qua** cho tài liệu này |

**Hai dạng là CÙNG MỘT PHƯƠNG TRÌNH**, chỉ khác chỗ dấu nằm ở dữ liệu hay nằm
ở công thức. Văn bản gốc viết ở dạng trừ — TT200 Điều 113 mục 3.18 ghi
`Mã số 60 = Mã số 50 - (Mã số 51 + Mã số 52)` — nên tài liệu in dạng trừ là
tài liệu chép đúng chữ Thông tư, còn tài liệu in dạng tổng đã tự chuyển vế.
Cả hai đều hợp lệ và cả hai đều gặp thật.

#### Cách đọc quy ước, theo thứ tự ưu tiên

1. **Công thức in trong nhãn dòng** — `(60 = 50 + 51 + 52)` hay
   `(60 = 50 - 51 - 52)`. Đây là lời khai tường minh của chính báo cáo. Phần
   lớn tài liệu dạng trừ có in, nhưng không phải tất cả.
2. **Dấu ngoặc của mã 11.** Giá vốn **luôn có mặt, luôn là khoản trừ, và không
   bao giờ hợp lệ mang nghĩa thu nhập** — nên dấu của nó do quy ước ấn định
   hoàn toàn. Trong ngoặc ⇒ `tong`; không ngoặc ⇒ `tru`.
   **Đừng dùng mã 51 hay 52 vào việc này:** chúng có thể bằng 0, và có thể đổi
   chiều thật khi thuế là thu nhập.
3. Hai nguồn trên **mâu thuẫn**, hoặc không nguồn nào đọc được ⇒
   `khong_xac_dinh`. Đừng chọn bừa: chạy đẳng thức theo bên đoán sai sẽ **bịa
   ra** một lỗi lệch đúng gấp đôi các dòng khấu trừ, tệ hơn hẳn việc bỏ qua.

**Quy ước ĐỒNG NHẤT trong một tài liệu** — mã 11 và mã 51 luôn cùng cách in.
Người chủ trì đã kiểm tay trên toàn bộ tài liệu đọc được ngày 01/09/2026. Nhờ
vậy nó là **một** bit cho cả tài liệu, không phải một bit cho mỗi đẳng thức.

#### Dấu của mã 51 và 52 KHÔNG có luật riêng

Chép như in, hết. Đừng áp luật dấu cho chúng, kể cả khi trông có vẻ sai: một
khoản **thu nhập** thuế hoãn lại đi cùng **chi phí** thuế hiện hành là trạng
thái kế toán có thật, nên hai dòng ngược chiều nhau là hợp lệ ở cả hai quy
ước. Đây là kết luận đã phân xử ở Câu 13 (28/08/2026) trên ba tài liệu gold —
HNG, MWG, VRE — cả ba đều cân đẳng thức tới từng đồng với hai dòng thuế ngược
chiều. Ép chúng theo luật dấu là **đẻ ra lỗi câm mới**.

Cái ràng buộc chúng là **đẳng thức mã 60**, không phải luật dấu.

#### Phép kiểm khi nghi ngờ

- Bộ số **đã cân** dưới quy ước đã ghi → không sửa gì.
- Đẳng thức lệch đúng **gấp đôi** một dòng khấu trừ → dòng đó ghi ngược dấu.
  Đọc lại đúng ô ấy trên báo cáo.
- **Cả hai** đẳng thức B02 cùng lệch gấp đôi → nhiều khả năng **ghi nhầm quy
  ước**, không phải nhầm ô. Đọc lại mã 11 và công thức mã 60.
- Đọc lại vẫn thấy như cũ → giữ nguyên và ghi `notes`, **đừng lật cho cân**.

Công cụ gán nhãn chạy sẵn các phép kiểm này, nên không phải tính tay.

> **Đổi ngày 01/09/2026.** Trước đó mã 11 bị ép "luôn dương" và mã 51/52 ghi
> theo "nghĩa kinh tế", còn dạng đẳng thức thì buộc vào CHUẨN Thông tư —
> TT200 dùng dạng tổng, TT99 dùng dạng trừ. Cách buộc ấy sai: cả hai cách in
> cùng tồn tại trong một chuẩn. Xem mục Sửa đổi để biết bằng chứng và hệ quả.

### 3.4 Ô trống, dấu gạch, và số không

Ba trường hợp **khác nhau**, không được gộp:

| Trên báo cáo | Ghi vào `values` | Nghĩa |
|---|---|---|
| `-` hoặc để trống | `0` | Chỉ tiêu có trên biểu mẫu nhưng không phát sinh trong kỳ |
| `0` in rõ ràng | `0` | Doanh nghiệp khai báo tường minh bằng 0 |
| Không có DÒNG đó trên biểu mẫu | `0` + ghi `notes` | Miễn trình bày vì không có số liệu |
| Có dòng nhưng **đọc không ra** (mờ, rách, che) | `null` + ghi `notes` | Thật sự chưa biết |

*Vì sao:* `null` phải để dành cho **"chưa biết"**, không dùng cho **"bằng
không"**. Chỉ tiêu vắng mặt không phải là chưa biết — TT99 mục 1.2.3 nói rõ
"các chỉ tiêu không có số liệu được miễn trình bày", tức chính văn bản bảo
đảm rằng phần vắng mặt không đóng góp vào tổng.

**Sửa đổi 23/08/2026, và lý do phải sửa.** Bản trước ghi cả hai ca vắng mặt
là `null`. Quy tắc đó vô hại khi bộ chỉ tiêu chỉ có 3 đẳng thức trên các
chỉ tiêu đầu bảng vốn luôn được in. Sau khi Mốc 1 thêm đẳng thức phân rã tài
sản ngắn hạn — 5 thành phần ở TT200, 6 ở TT99 — nó thành ra tai hại: bước
kiểm đẳng thức bỏ qua cả đẳng thức nếu **bất kỳ** thành phần nào là `null`,
nên chỉ cần một dòng vắng mặt là đẳng thức giá trị nhất im lặng không chạy.
Mà vắng mặt là chuyện thường, không phải ngoại lệ.

Bằng chứng ngay trên tài liệu mẫu: báo cáo VNM Q1/2026 in tiêu đề chỉ tiêu
kèm công thức **rút gọn của chính nó** — `Tài sản ngắn hạn (100 = 110 + 120
+ 130 + 140 + 160)` — bỏ hẳn mã 150 vì công ty không có tài sản sinh học.
Doanh nghiệp lập báo cáo cũng coi dòng vắng mặt là không đóng góp.

Ghi `notes` cho ca vắng dòng vẫn bắt buộc: nó phân biệt được "0 vì miễn
trình bày" với "0 vì công ty khai là 0", và đó là thông tin cần khi phân
tích bất đồng giữa hai người gán nhãn.

### 3.5 Làm tròn

**Không làm tròn, không sửa.** Chép đúng con số in trên giấy, kể cả khi nó
làm đẳng thức kế toán lệch vài đồng.

*Vì sao:* nếu người gán nhãn "sửa cho cân" thì tập gold không còn phản ánh
tài liệu, và ta mất khả năng đo xem chính báo cáo có tự nhất quán hay không.
Dung sai làm tròn là chuyện của bước so khớp (`IDENTITY_TOLERANCE_RATIO`),
không phải chuyện của người gán nhãn.

Nếu đẳng thức lệch **đáng kể** (quá một chữ số cuối), ghi vào `notes`.

### 3.6 Bắt đúng dòng — chỗ đã có lỗi thật

Đối chiếu bằng **cột "Mã số"**, không bằng tên chỉ tiêu.

*Vì sao:* mã số là thứ đáng tin nhất trên trang. Tên chỉ tiêu thì lồng nhau
và bẫy nhau. Lỗi đã quan sát được trên báo cáo VNM: dòng "Dự phòng giảm giá
hàng tồn kho" (mã 142) bị lấy nhầm cho "Hàng tồn kho" (mã 140) — giá trị nhỏ
hơn giá trị thật khoảng nghìn lần nhưng hoàn toàn hợp lệ về hình thức.

Cặp hay nhầm phải kiểm kỹ:

| Cần lấy | Dễ nhầm sang |
|---|---|
| Hàng tồn kho (140) | Dự phòng giảm giá hàng tồn kho (142 ở TT99, 149 ở TT200) |
| Tổng cộng tài sản (270 hoặc 280) | Tổng cộng nguồn vốn (440) — **giờ là hai chỉ tiêu riêng, phải lấy CẢ HAI** |
| Doanh thu thuần (10) | Doanh thu bán hàng và cung cấp dịch vụ (01) |
| Lợi nhuận sau thuế (60) | Lợi nhuận sau thuế của cổ đông công ty mẹ |
| Lợi nhuận sau thuế (60) | Lợi nhuận sau thuế chưa phân phối (420) trên bảng cân đối |
| Tài sản ngắn hạn khác (150 ở TT200, **160** ở TT99) | Dòng chi tiết ngay dưới nó (155 / 165) cùng tên |
| Chi phí thuế TNDN hiện hành (51) | Chi phí thuế TNDN hoãn lại (52) |

**BA mã số đổi nghĩa giữa hai chuẩn.** Xác định chuẩn trước, rồi mới tra mã
— tra nhầm bảng không làm gì báo lỗi, nó trả về một con số hợp lệ của chỉ
tiêu khác:

| Mã | TT200 | TT99 |
|---|---|---|
| **270** | Tổng cộng tài sản | Tài sản dài hạn khác |
| **150** | Tài sản ngắn hạn khác | **Tài sản sinh học ngắn hạn** |
| **142** | (thuộc nhóm khác) | Dự phòng giảm giá hàng tồn kho |

Kèm theo: **Tài sản sinh học ngắn hạn chỉ tồn tại ở TT99.** Với báo cáo
TT200 thì chỉ tiêu này không có trên biểu mẫu — bỏ trống, đừng đi tìm.

### 3.7 Nhận diện chuẩn mẫu biểu

| Dấu hiệu | Kết luận |
|---|---|
| Có trích dẫn `99/2025/TT-BTC` | TT99 |
| Có trích dẫn `200/2014/TT-BTC` | TT200 |
| Tiêu đề `Báo cáo tình hình tài chính` | TT99 |
| Tiêu đề `Bảng cân đối kế toán` | TT200 |

Hai dòng số hiệu thông tư đặt trước vì chúng **chắc chắn hơn**: chúng là
trích dẫn văn bản, không phải cách gọi tên mà doanh nghiệp có thể giữ theo
thói quen cũ. Chúng chỉ in ở dòng "Ban hành theo…" đầu biểu mẫu, nên khi có
thì dùng, không có thì mới xét tới tiêu đề.

**KHÔNG có dấu hiệu nào nằm ở hậu tố `a`/`b` của ký hiệu mẫu biểu.** Hậu tố
đó là KỲ BÁO CÁO — mục 2 đã nêu, và cả hai Thông tư đều dùng đủ ba ký hiệu
`B01-DN`, `B01a-DN`, `B01b-DN`. Thấy `B01a-DN` thì chỉ kết luận được rằng
đây là báo cáo giữa niên độ dạng đầy đủ, tuyệt đối không kết luận gì về
Thông tư. Xem tu chính 26/08/2026 ở mục Sửa đổi.

**Không đủ dấu hiệu, hoặc thấy dấu hiệu của cả hai:** ghi `standard` là
`"UNKNOWN"` và mô tả trong `notes`. **Đừng đoán.** Nhận diện sai chuẩn là
một chế độ lỗi riêng cần đo được, và một nhãn đoán bừa sẽ được tính thành
lỗi của model.

Lưu ý cái bẫy ngược lại: "thấy dấu hiệu của cả hai" nghĩa là hai dấu hiệu
TRONG BẢNG TRÊN chỏi nhau, chứ không phải một dấu hiệu trong bảng chỏi với
một suy đoán của người đọc. Ký hiệu mẫu không còn là dấu hiệu, nên
`B01a-DN` kèm tiêu đề *Bảng cân đối kế toán* là một tài liệu TT200 có đúng
một dấu hiệu — không phải một ca mâu thuẫn.

---

## 4. Định dạng file

Một file JSON cho mỗi tài liệu, đặt ở `data/gold/<doc_id>.json`. Cấu trúc do
`src/eval/schema.py` quy định — dùng `GroundTruthDoc` để ghi thay vì gõ tay
JSON, vì nó tự kiểm các trường bắt buộc.

```json
{
  "doc_id": "VNM_2026Q1_TT99",
  "ticker": "VNM",
  "period": "2026Q1",
  "standard": "TT99",
  "unit_declared": "Đơn vị tính: VND",
  "unit_multiplier": 1,
  "values": {
    "tai_san_ngan_han": 29403116984122,
    "hang_ton_kho": 5393002084291,
    "tai_san_dai_han": 18372709942261,
    "tong_tai_san": 47775826926383,
    "no_phai_tra": 16666572149360,
    "von_chu_so_huu": 31109254777023,
    "doanh_thu_thuan": 13217639635987,
    "gia_von_hang_ban": 7278764406353,
    "loi_nhuan_gop": 5938875229634,
    "loi_nhuan_truoc_thue": 2523887147085,
    "loi_nhuan_sau_thue": 2049247209782
  },
  "source_url": "https://...",
  "downloaded_at": "2026-08-23T10:00:00+07:00",
  "annotator": "TKD",
  "annotated_at": "2026-08-23T11:30:00+07:00",
  "adjudicated": false,
  "notes": ""
}
```

`doc_id` theo mẫu `<mã CK>_<kỳ>_<chuẩn>`, ví dụ `VNM_2026Q1_TT99`.

Ngoài nội dung tài liệu, file còn mang mấy khoá ghi lại **cách** tài liệu này
được gán nhãn: `so_lan_ghi`, `so_lan_kiem_dang_thuc`, `sua_gia_tri_sau_khi_kiem`,
`trang_thai_dong_ho`, `thoi_gian_giay`, `so_lan_tam_dung`. Công cụ gán nhãn
tự điền hết. Khoá đáng chú ý nhất là `trang_thai_dong_ho`: `"da_do"` nghĩa là
`thoi_gian_giay` là một số đo thật, `"khong_do"` nghĩa là không ai bấm giờ và
con số 0 kia **không phải** một phép đo. Phân biệt hai ca đó là điều kiện cần
để tính trung vị ở mục 6.

`source_url` và `downloaded_at` **bắt buộc**: phương án phát hành dataset an
toàn là phát hành annotation kèm URL nguồn và script tải, **không** phát hành
file PDF gốc — bản PDF của báo cáo niêm yết vẫn có bản quyền trình bày.
Thiếu hai trường này thì không phát hành dataset được.

---

## 5. Đo đồng thuận giữa hai người

**Cam kết: 20 trong 60 tài liệu được gán nhãn đôi**, tức một phần ba tập gold.

Hai người gán nhãn **độc lập**, không xem bản của nhau. Ghi vào hai thư mục
riêng (`data/gold/annotator_a/`, `data/gold/annotator_b/`) rồi mới so.

### Báo cáo ba con số, không phải một

Với trích xuất số thì Cohen's kappa gượng ép vì miền giá trị mở. Báo cáo:

1. **Tỷ lệ khớp tuyệt đối theo trường** — hai người ra cùng con số ở bao
   nhiêu phần trăm trường.
2. **Krippendorff's alpha**, nếu muốn một chỉ số có hiệu chỉnh ngẫu nhiên.
3. **Phân loại bất đồng** theo ba nhóm:

| Nhóm | Nghĩa | Xử lý |
|---|---|---|
| Đọc sai chữ số | Hai người đọc khác nhau cùng một ô | Phân xử, ghi lại |
| Chọn nhầm dòng | Hai người lấy hai dòng khác nhau | Phân xử, và **kiểm xem guideline mục 3.6 có thiếu cặp nào không** |
| Guideline mơ hồ | Guideline không nói rõ phải làm gì | **Tín hiệu phải sửa guideline** — xem Luật 3 |

Nhóm thứ ba là nhóm đáng chú ý nhất: nó không phải lỗi của người gán nhãn.

### Phân xử

Bất đồng được phân xử để tạo bản gold cuối, đặt `adjudicated = true`.

**Báo cáo số trường phải phân xử.** Con số đó tự nó là thông tin về độ khó
của tác vụ, và nó vào bài.

### Nếu không tìm được người thứ hai

Phương án dự phòng, yếu hơn nhưng còn hơn không: **gán nhãn lại 20 tài liệu
sau ít nhất hai tuần**, bởi chính mình, không xem bản cũ. Đó là
intra-annotator agreement. **Nói rõ trong bài đây là bản thay thế và nêu
giới hạn** — nó đo được tính nhất quán của một người, không đo được tính
khách quan của quy tắc.

### Tài liệu đã chạy pipeline bị LOẠI khỏi tập gán nhãn đôi

Phương án tự gán nhãn lại làm Luật 1 nặng hơn hẳn trường hợp hai người:
người gán lại chính là người đã chạy pipeline, và `data/output/tap_gold_*.json`
cùng `..._pipeline.log` giữ giá trị máy đoán cho **từng ô** của những tài
liệu đã chạy. Mở nhầm một trong hai file là lượt gán lại bị neo, mà không có
cách nào phát hiện ngược từ dữ liệu — con số đồng thuận vẫn tính ra, chỉ là
nó đo trí nhớ chứ không đo tính nhất quán của quy tắc.

**Quy tắc: tài liệu nào đã có đầu ra pipeline thì vĩnh viễn không được vào
tập gán nhãn đôi.** Không rút lại được bằng cách xoá file — việc người ấy đã
nhìn thấy máy đoán gì thì đã xảy ra rồi. Tập gán nhãn đôi vì thế phải lấy từ
những tài liệu gán nhãn **sau** lượt chạy pipeline, và tập đích ~100 tài liệu
thừa chỗ cho 20–33 tài liệu ấy.

Trạng thái ghi ở khoá `gan_nhan_doi` trong `data/nguon_gold.json`, ba giá
trị: `loai_da_chay_pipeline`, `du_dieu_kien`, `chua_xet`. Đối chiếu khai báo
với hiện trạng `data/output/` bằng

```
PYTHONPATH=src python src/eval/tap_dong_thuan.py
```

và `tests/test_tap_dong_thuan.py` đỏ nếu một tài liệu có đầu ra pipeline mà
danh mục chưa đánh dấu.

**Hệ quả về lịch, không phải chi tiết vặt:** mười tài liệu gold đầu tiên đều
đã chạy pipeline ngày 26–27/08/2026, và `VNM_2026Q1_TT99` cũng vậy, nên tính
tới 28/08/2026 **không tài liệu nào đủ điều kiện**. Lượt gán nhãn đôi không
bắt đầu được cho tới khi tập gold vượt mốc 11 tài liệu — mốc hai tuần
09/09/2026 chỉ là điều kiện cần.

---

## 6. Trần người — 10 tài liệu

Không có số này thì không diễn giải được kết quả hệ thống: 83% là gần trần
hay còn xa?

**Quy trình:**

1. Gán nhãn 10 tài liệu dưới **áp lực thời gian thực tế** — đặt đồng hồ, hết
   giờ thì dừng, không làm tỉ mỉ vô hạn. Số phút đặt đồng hồ **suy ra từ nhịp
   gán nhãn kỹ đo được**, không phải một con số chọn sẵn; cách tính ở khung
   ngay dưới.
2. So với bản gold **đã phân xử kỹ** (chính là 20 tài liệu ở mục 5).
3. Báo cáo độ chính xác mức trường **và** mức tài liệu.

**Đặt đồng hồ bao nhiêu phút, và vì sao không còn là 15.** Con số cũ là 15
phút, chốt khi bộ chỉ tiêu còn nằm trên hai biểu mẫu. Kịch bản E trải bộ chỉ
tiêu qua ba biểu mẫu nên con số phải xem lại — và khi xem lại thì nó hỏng
theo chiều **ngược** với dự đoán. Người chủ trì gán nhãn tài liệu đầu tiên
(`VNM_2026Q1_TT99`, 27 chỉ tiêu, ba biểu mẫu) ước lượng hết **khoảng 10
phút** cho công đoạn điền. Nếu làm KỸ đã hết 10 phút thì đồng hồ 15 phút
không tạo áp lực nào: bản "có áp lực" và bản "làm kỹ" thành cùng một người
làm cùng một việc, trần người ra gần 100%, và phép đo không nói lên gì. Giao
thức không vỡ — nó **chùng**, mà chùng thì vô dụng y như vỡ.

Cho nên số phút phải nhỏ hơn hẳn nhịp làm kỹ, và phải suy ra từ số đo:

- Trường `thoi_gian_giay` trong mỗi file gold ghi thời gian thật của lượt gán
  nhãn kỹ. Lấy **trung vị của 10 tài liệu gold đầu tiên** làm nhịp kỹ `M`.
- Chỉ tính các file có `trang_thai_dong_ho` bằng `"da_do"`. File `"khong_do"`
  là file không ai bấm giờ, và `thoi_gian_giay` của nó bằng 0 vì không có số
  đo chứ không phải vì làm xong trong 0 giây — gộp nó vào trung vị là kéo tụt
  `M` bằng một con số không tồn tại.
- Đặt đồng hồ ở **0,6 × M**, làm tròn tới phút, **sàn 5 phút**.
- Hệ số 0,6 không phải hằng số tự nhiên. Giá trị của nó nằm ở chỗ được **chốt
  trước khi đo**, đúng để không bị chọn lại sau khi đã nhìn thấy kết quả trần
  người. **Người chủ trì đã xác nhận 0,6 ngày 26/08/2026**, khi tập gold còn
  1 tài liệu và chưa tài liệu nào có số đo thời gian — tức chốt trước khi
  nhìn thấy bất kỳ dữ liệu nào mà hệ số này áp lên. Từ đây nó là con số cố
  định; đổi về sau phải ghi thêm một tu chính và nêu rõ lý do.

Với ước lượng 10 phút hiện có thì đồng hồ sẽ rơi vào khoảng 6 phút. **Đừng
dùng con số đó làm số chốt:** 10 phút là ước lượng của người chứ không phải
đồng hồ, và `thoi_gian_giay` của tài liệu gold duy nhất đang có vẫn bằng 0,
nên tới lúc này chưa có một số đo nào cả.

**Cách đọc kết quả:**

| Trần người | Hệ thống 83% nghĩa là |
|---|---|
| ~97% | Còn khoảng cách lớn, có chỗ để cải thiện |
| ~88% | Gần trần, và câu chuyện đổi hẳn: tác vụ này **bản thân nó khó** |

Trường hợp thứ hai là kết quả có giá trị hơn, và nó chỉ nhìn thấy được nếu
đã đo.

Ghi lại **thời gian thật** từng tài liệu, không chỉ ghi có kịp giờ hay
không — chính chuỗi số đó là thứ chốt con số đặt đồng hồ ở trên. Công cụ gán
nhãn đo giúp, nhưng **chỉ khi người gán nhãn tự bấm nút "Bắt đầu bấm giờ"**:
đồng hồ không tự chạy lúc mở tài liệu, vì như thế nó đếm cả quãng đi tìm file
PDF lẫn quãng bỏ đi pha cà phê. Nghỉ giữa chừng thì bấm "Tạm dừng"; số lần
dừng được ghi vào file để về sau tách tài liệu làm liền mạch khỏi tài liệu
ngắt quãng. Quên bấm thì công cụ **từ chối ghi file** chứ không lặng lẽ ghi
số 0 — một tài liệu quên bấm giờ chỉ lộ ra lúc gom số, và lúc đó không bấm
lại cho quá khứ được nữa. Tham chiếu để đối chiếu: tài liệu kinh tế học lịch sử cho biết người
kiểm tay tốn khoảng 20 phút một trang, còn OCR thương mại kèm sửa tay đưa
xuống khoảng 8 phút.

---

## 7. Thành phần tập gold

60 tài liệu, chia **30 TT200 + 30 TT99**.

Trong đó **tập Stress 30 tài liệu** phải cố ý gồm bốn nhóm:

| Nhóm | Vì sao cần | Cách nhận ra khi chọn |
|---|---|---|
| Doanh nghiệp **lỗ** | VCSH âm, lãi gộp âm — ca biên phá vỡ mọi bất đẳng thức giả định có lãi | LNST âm, hoặc VCSH âm |
| Báo cáo ghi **"triệu đồng"** | Ca biên của mỏ neo scale | Đọc dòng đơn vị tính |
| **Độ phân giải bản quét thấp** | Đo độ bền với chất lượng ảnh | `do_phan_giai_dpi.trung_vi` trong `data/nguon_gold.json`, sinh bằng `python src/do_do_phan_giai.py` — **sửa 26/08/2026**, xem ghi chú dưới bảng |
| Công ty **vốn hoá nhỏ, ít được nhắc** | Kiểm memorization | Không thuộc VN30 |

**Ghi chú 26/08/2026 — vì sao nhóm thứ ba đổi tiêu chí.** Tiêu chí cũ là
"bản scan chất lượng thấp", nhận ra bằng cách mở PDF xem có phải ảnh nhúng
không. Đo trên 23 tài liệu của 20 doanh nghiệp niêm yết thì tiêu chí ấy được
**100% quần thể thoả**: không tài liệu nào có lớp text thật, `pdftotext` lấy
ra 44–734 byte cho cả tài liệu 25–65 trang và phần ít ỏi đó là chú thích chữ
ký số. Một tiêu chí mà cả tổng thể đều thoả thì không chia được nhóm nào.

**Cách chọn tài liệu cho nhóm này: KHÔNG có ngưỡng dpi.** Ghi số đo vào danh
mục rồi chọn theo **thứ hạng trong chính tập gold** — lấy tài liệu ở phần
thấp của dải, không lấy tài liệu "dưới X dpi". Chốt một con số X lúc mới có
10 tài liệu là chọn tham số trên mẫu mỏng, và đó cũng là tham số dễ chỉnh lại
sau khi đã nhìn thấy kết quả nhất. Về sau phân tích bằng tương quan trên biến
liên tục, mạnh hơn so hai nhóm chia bằng ngưỡng.

**Độ phân giải không bao trọn chữ "chất lượng".** Trang lệch, dấu mộc đỏ đè
lên chữ số, in mờ lệch nét đều là thứ máy chưa đo được và mắt thì thấy ngay.
Ghi chúng vào `da_kiem` của danh mục bằng lời, và ghi vào `notes` của file
gold nếu chúng thật sự cản việc đọc số — đó là hai trục khác nhau, đừng gộp
vào con số dpi.

Danh mục tài liệu đã chọn nằm ở `data/nguon_gold.json`, tải bằng
`python src/tai_bctc.py`. Mỗi mục ghi rõ vai trò của tài liệu trong bốn nhóm
trên và những gì đã mở ra kiểm tận mắt.

Nhóm cuối quan trọng và hay bị quên: VLM nhiều khả năng đã thấy số liệu
blue-chip trong pretraining. Nếu kết quả trên blue-chip cao hơn hẳn
small-cap thì đó là bằng chứng rò rỉ dữ liệu và **phải báo cáo riêng**.

---

## 8. Danh mục kiểm trước khi coi một tài liệu là xong

- [ ] Chưa từng mở đầu ra pipeline của tài liệu này (Luật 1)
- [ ] Nếu đây là lượt gán nhãn **đôi**: tài liệu chưa từng chạy pipeline —
      `PYTHONPATH=src python src/eval/tap_dong_thuan.py` phải xếp nó vào
      nhóm đủ điều kiện (mục 5)
- [ ] Đã xác định chuẩn mẫu biểu, hoặc ghi `UNKNOWN` kèm lý do — theo
      bảng dấu hiệu ở mục 3.7, và **không** theo hậu tố `a`/`b`
- [ ] `unit_declared` chép **nguyên văn**; `unit_multiplier` khớp
- [ ] Mọi giá trị đã quy đổi về **đồng**
- [ ] Mọi giá trị chép **NGUYÊN VĂN như in**: ngoặc đơn là âm, không ngoặc
      là dương — kể cả mã 11, 51, 52. Không diễn giải nghĩa kinh tế (mục 3.3)
- [ ] Đã **ĐỌC** `quy_uoc_dau` trên tờ giấy: công thức mã 60 in trong nhãn
      dòng, hoặc dấu ngoặc của mã 11. **Không suy từ Thông tư** — cả hai cách
      in cùng tồn tại trong một chuẩn (mục 3.3)
- [ ] Ô trống, dấu gạch, và dòng vắng mặt đều ghi `0`; `null` **chỉ** dùng
      khi có dòng mà đọc không ra (mục 3.4)
- [ ] **Đúng cột**: bảng cân đối lấy cột có ngày mới nhất; bảng kết quả kinh
      doanh lấy nhóm **Quý**, kỳ này — KHÔNG lấy cột luỹ kế. Hai nhóm cột của
      B02 kết thúc cùng ngày nên đừng chọn bằng ngày (mục 2)
- [ ] **B02 đúng biểu mẫu doanh nghiệp thường**: có mã 10, 11, 20 và 30.
      Thiếu bất kỳ mã nào trong bốn mã đó thì **dừng, đừng gán nhãn tiếp** —
      đó là biểu mẫu riêng của ngành tài chính, và tài liệu nằm ngoài phạm vi
      (mục 2). Báo lại để loại tài liệu và tải một tài liệu thay thế
- [ ] Đã đối chiếu **mã số**, không chỉ tên chỉ tiêu
- [ ] Đã kiểm riêng các cặp dễ nhầm ở mục 3.6
- [ ] Không sửa số cho cân đẳng thức; lệch đáng kể thì ghi `notes`
- [ ] `source_url`, `downloaded_at`, `annotator`, `annotated_at` đều có
- [ ] Đã bấm giờ tài liệu này, hoặc khai rõ là không đo giờ (mục 6)
- [ ] File đặt đúng `data/gold/<doc_id>.json`

---

## Sửa đổi

> Mọi thay đổi guideline ghi vào đây kèm **ngày** và **lý do**, và ghi rõ
> **những tài liệu nào phải gán nhãn lại**. Không sửa đè lên nội dung trên.

### 01/09/2026 (muộn hơn) — Chép NGUYÊN VĂN, và quy ước dấu thành một trường

**Chỗ sửa:** mục 3.3 viết lại trọn; mục 8 đổi hai mục kiểm và thêm hai mục
mới; `data/gold/*.json` có thêm khoá bắt buộc `quy_uoc_dau`.

**PHẢI GÁN NHÃN LẠI TOÀN BỘ.** Người chủ trì quyết định chép lại tập gold từ
đầu, và đó là lựa chọn đúng chứ không phải thừa: giá trị đang lưu đã qua nhiều
lượt **lật dấu cơ học** khi quy tắc đổi — `notes` của bốn file ghi thẳng *"mã
51 và 52 đã LẬT DẤU CƠ HỌC… KHÔNG phải đọc lại tờ giấy"* — nên chúng không còn
là bản sao trung thực của trang giấy. Suy ngược từ chúng ra cách báo cáo trình
bày là suy từ chính quy tắc đang bị thay.

**Quy tắc cũ, ba mảnh, cả ba đều bỏ:**

1. Giá vốn (mã 11) *"luôn dương"*.
2. Mã 51 và 52 ghi theo *"nghĩa kinh tế"* — chi phí âm, thu nhập dương (áp cho
   TT200 từ 31/08/2026); TT99 giữ *"nguyên dấu như in"*.
3. Dạng đẳng thức mã 60 **buộc theo CHUẨN**: TT200 dùng tổng, TT99 dùng trừ.

**Quy tắc mới, một mảnh:** chép nguyên văn như in, rồi ghi thêm `quy_uoc_dau`
đọc được từ tờ giấy. Dạng của hai đẳng thức B02 do trường đó quyết định.

**Bằng chứng buộc phải đổi, đo trên tài liệu thật ngày 01/09/2026.** Người chủ
trì đọc tay 15 báo cáo TT200 và thấy **cả hai cách in cùng tồn tại trong một
chuẩn**: `DGC`, `HNG`, `KDH`, `MWG`, `NLG`, `NVL`, `REE`, `SBT`, `TTF`, `VCG`,
`VHC`, `VHM` in dạng tổng, còn `BCM`, `DPM`, `DVD` in dạng trừ. Buộc dạng theo
Thông tư vì thế chấm sai mọi tài liệu TT200 in dạng trừ — và sai theo kiểu tệ
nhất: đầu ra pipeline trên tài liệu như vậy để lại residual **đúng gấp đôi mã
52** trên một tài liệu **không có lỗi đọc nào**, tức một dương tính giả bảo
đảm, ngay giữa phép đo mà H1 sinh ra để làm.

**Vì sao KHÔNG dùng phép tuyển "thoả một trong hai dạng thì đạt".** Đo trên
`DGC_2025Q2_TT200`: lật dấu riêng mã 51 — lỗi dấu thuần tuý, không đụng chữ số
nào — làm bộ số chuyển từ thoả dạng tổng sang thoả dạng trừ, nên phép tuyển
cho nó đi qua trong khi sai lệch thật là **47.108.746.070 đồng**, bằng 7,5% mã
50. Hai vế lệch nhau đúng `2×(51+52)`, đúng bằng lượng mà một lỗi dấu dịch
chuyển, nên phép tuyển mù với **chính lớp lỗi** mà ràng buộc này tồn tại để
bắt. Thêm nữa nó không viết được thành ràng buộc tuyến tính, tức bỏ luôn H0.

**Cùng một bit chi phối CẢ HAI đẳng thức B02.** Trước tu chính này, mã 11 chạy
quy ước trừ còn mã 51 chạy quy ước tổng — ngay trong cùng một file gold. Thấy
rõ ở `DGC_2025Q2_TT200`: mã 11 lưu **dương** (dạng trừ) trong khi mã 51 lưu
**âm** (dạng tổng), mà `notes` của chính file đó ghi trên giấy **cả hai đều in
trong ngoặc**. Đó là cùng một lỗi, chỉ chưa ai gọi tên.

**Không mất gì về khả năng định vị, đã đo chứ không đoán.** Dựng ma trận cho
cả bốn tổ hợp (hai chuẩn × hai quy ước) cho ra cùng `rank(A)` bằng 9, cùng
`dim null(A)` (17 với TT200, 18 với TT99), cùng 7 chỉ tiêu định vị được, và
cùng **danh sách** cặp không phân biệt được — trùng từng phần tử chứ không chỉ
trùng số đếm. Phép kiểm này nay chạy lại mỗi lần sinh
`data/output/identifiability_*.md`.

**Giới hạn mới, phải khai trong bài.** Ràng buộc B02 nay phụ thuộc một bit đọc
từ tờ giấy. Sai chữ số vẫn bị bắt như cũ; riêng **lỗi đọc nhầm dấu ngoặc ở mã
11** sẽ lật cả hai đẳng thức B02 của tài liệu đó. Đây là lý do công thức in
trong nhãn dòng giữ quyền ưu tiên khi có — hai nguồn độc lập kiểm chéo nhau —
và là lý do ca `mau_thuan` được đếm riêng trong metrics.

### 01/09/2026 — Phạm vi loại thêm chứng khoán, bảo hiểm, quản lý quỹ

**Chỗ sửa:** mục 2, dòng "Loại doanh nghiệp"; và mục 8, thêm một mục vào danh
mục kiểm.

**KHÔNG phải gán nhãn lại tài liệu nào.** Chín tài liệu bị loại đều chưa từng
được gán nhãn và chưa từng chạy pipeline — không có file nào của chúng trong
`data/gold/` lẫn `data/output/`. Việc này lộ ra đúng lúc mở tài liệu đầu tiên
thuộc nhóm đó, nên tập gold hiện có không bị đụng tới.

**Chuyện gì đã xảy ra.** Người gán nhãn mở `BVH_2026Q2_TT99` (Tập đoàn Bảo
Việt) và không tìm thấy mã 10. B02 của tài liệu này chạy mã 01 → 21 → 42 →
52 → 70: **không có mã 10, 11, 20 lẫn 30**. Ba mã đầu còn có dòng tương đương
về nghĩa — 15 "Doanh thu thuần từ hoạt động kinh doanh bảo hiểm", 41 "Tổng chi
trực tiếp hoạt động kinh doanh bảo hiểm", 42 "Lợi nhuận gộp hoạt động kinh
doanh bảo hiểm" — nhưng **mã 30 thì không có dòng nào tương đương**, biểu mẫu
đi thẳng từ 42 sang 50.

**Vì sao không gán theo dòng tương đương mà lại loại cả tài liệu.** Gán
15 → 10, 41 → 11, 42 → 20 rồi ghi 0 cho mã 30 theo quy tắc ô trống của mục 3.4
làm đẳng thức `ln_thuan_hdkd + ln_khac = loi_nhuan_truoc_thue` sai lệch cả
nghìn tỷ đồng trên một tài liệu **không có lỗi trích xuất nào** — tức tự tay
nướng một dương tính giả vào chính ground truth, đúng thứ H1 sinh ra để đo. Lý
lẽ của mục 3.4 cũng không phủ được ca này: nó dựa vào TT99 mục 1.2.3, "chỉ tiêu
**không có số liệu** được miễn trình bày", mà mã 30 ở đây vắng vì **biểu mẫu
không có khái niệm ấy**, không phải vì kỳ này không phát sinh. Thêm nữa,
`doanh_thu_thuan` sẽ mang hai nghĩa khác nhau ở hai nhóm tài liệu, nên mọi con
số accuracy gộp theo chỉ tiêu mất nghĩa.

**Vì sao đây không phải là loại tài liệu sau khi đã nhìn thấy kết quả.** Tiêu
chí loại phát biểu trên **ngành nghề đăng ký của tổ chức phát hành**, quan sát
được trước mọi phép đo; Luật 1 còn nguyên vì chưa tài liệu nào trong chín cái
đó được chạy pipeline; và quyết định không hề dựa vào việc hệ chạy tốt hay xấu
trên chúng. Bản cũ của mục 2 đã chốt phạm vi là "phi tài chính" với đúng lý do
này ngay từ 23/08/2026 — tu chính hôm nay chỉ làm câu chữ khớp lại với lý do
của chính nó, chứ không mở ra một tiêu chí mới.

**Chín tài liệu bị loại**, tất cả là tổ chức tài chính: `MBB`, `STB`, `TCB`,
`VCB`, `VPB`, `KLB`, `VIB` (ngân hàng), `SSI` (chứng khoán), `BVH` (bảo hiểm).
Chúng được thay bằng chín tài liệu **cùng Thông tư, cùng kỳ báo cáo, cùng sàn,
cùng hạng quy mô, cũng là bản quét không lớp text**, nên tỷ lệ 30 TT200 / 30
TT99 và cơ cấu bốn nhóm Stress không đổi. Bảng đối chiếu từng cặp, kèm đặc
điểm đã mở ra kiểm tận mắt của từng tài liệu thay thế, ở `data/bctc/NGUON.md`
mục cuối.

**Cái bẫy để lần sau không phải phát hiện lại bằng tay:** danh mục kiểm mục 8
nay có một mục bắt người gán nhãn xác nhận B02 có đủ mã 10, 11, 20, 30 trước
khi ghi số. Thiếu mã nào trong bốn mã đó thì dừng, vì đó là dấu hiệu biểu mẫu
riêng của ngành chứ không phải chỉ tiêu vắng mặt.

### 31/08/2026 — Mã 51 và 52 ghi theo NGHĨA KINH TẾ — **CHỈ ÁP CHO TT200**

**Chỗ sửa:** mục 3.3, bảng ba dòng khấu trừ và phần lý giải kèm theo.

**PHẠM VI: TT200 và chỉ TT200.** TT99 giữ nguyên quy ước cũ vì chưa xác minh
được trên tài liệu — quyết định của người chủ trì, cùng ngày. Hệ quả là hai
chuẩn tạm thời dùng hai quy ước dấu khác nhau, và cả `fields_config` lẫn
`chuan_hoa_dau()` đều tách nhánh theo chuẩn. Yêu cầu về bộ tài liệu cần thu
thập để xác minh TT99 ở `docs/yeu-cau-tai-lieu-bctc.md`.

**Quy tắc cũ:** mã 51 và 52 *"giữ nguyên dấu như in"*, rồi kiểm bằng đẳng thức
`Mã 60 = Mã 50 − Mã 51 − Mã 52`. **Quy tắc mới:** ghi theo nghĩa kinh tế — chi
phí thuế **âm**, thu nhập thuế **dương** — và đẳng thức thành
`Mã 60 = Mã 50 + Mã 51 + Mã 52`.

**Vì sao đổi.** Quy tắc cũ dựa vào cách trình bày, mà cách trình bày **không
nhất quán ngay trong một báo cáo**. `VRE_2026Q1_TT99` in mã 51 trong ngoặc
đơn còn mã 52 ngoài ngoặc, đúng ngược với nghĩa của hai dòng; người gán nhãn
đã ghi chỗ vênh đó vào `notes` ngày 26/08/2026, tức bốn ngày trước tu chính
này, nhưng lúc ấy guideline không có chỗ nào chứa nó ngoài một dòng ghi chú.
Quy tắc mới phát biểu được thành một câu không phụ thuộc cách in: **tiền đi ra
khỏi lợi nhuận thì âm.**

Kèm theo, bộ ràng buộc thành đồng nhất về dạng — cả chín đẳng thức nay đều là
tổng thuần — nên bỏ được ngoại lệ xử lý dấu vốn phải viết riêng cho hai dòng
thuế.

**Không được gì về khả năng định vị lỗi, và đã đo chứ không đoán.** Sinh lại
`data/output/identifiability_*.md` trước và sau tu chính cho ra cùng 7/26 chỉ
tiêu định vị được, cùng số chiều không gian null, cùng danh sách cặp không
phân biệt được. Đổi vế chỉ lật dấu hai cột của ma trận, mà quan hệ tỷ lệ giữa
các cột thì bất biến với phép lật ấy. Đừng viết tu chính này vào bài như một
cải thiện định vị.

**KHÔNG tài liệu nào phải gán nhãn lại, và đây là một ngoại lệ có lý do phải
nêu rõ.** (Áp cho 5 tài liệu TT200; 6 tài liệu TT99 không đổi gì.) Luật mở đầu guideline nói sửa quy tắc giữa chừng thì phải gán nhãn
lại toàn bộ phần đã làm. Ngoại lệ ở đây được phép vì phép biến đổi là **song
ánh và cơ học**: quy ước mới bằng đúng quy ước cũ nhân `−1` trên hai ô, không
cần nhìn lại tờ giấy để biết giá trị mới, và không có ca nào mà hai quy ước
cho cùng một con số. **Năm file gold TT200** đã được lật dấu bằng script ngày
31/08/2026 và cả năm đều cân `50 + 51 + 52 = 60` tới từng đồng sau khi lật.
Sáu file TT99 giữ nguyên và vẫn cân đẳng thức cũ của chúng.

Vì đây **không** phải gán nhãn lại, `notes` của năm file TT200 ghi rõ giá
trị hai ô ấy đến từ một phép lật cơ học chứ không từ một lượt đọc mới — hai
thứ có độ tin cậy khác hẳn nhau, và người đọc file gold phải thấy được ngay
tại file.

**Việc còn lại:** lượt gán nhãn tài liệu **TT200** tiếp theo phải theo quy tắc
mới; tài liệu TT99 giữ quy tắc cũ cho tới khi xác minh xong. Mọi kết quả chấm
pipeline trên tài liệu TT200 trước 31/08/2026 dùng quy ước cũ, nên **không so
trực tiếp** với lượt chạy sau mốc này ở hai ô 51/52.

### 28/08/2026 (muộn hơn) — "Cột đầu" nói rõ thành "cột QUÝ, không phải luỹ kế"

**Chỗ sửa:** mục 2, dòng "Cột". **Không tài liệu nào phải gán nhãn lại** — quy
tắc mới nói rõ đúng thứ các nhãn hiện có đã làm, chứ không đổi thứ phải làm.

**Vì sao phải nói rõ.** Bản cũ ghi *"Cột kỳ báo cáo, tức cột đầu"*. Chữ "cột
đầu" hỏng ở hai chỗ. Một, **trang có thể xoay 90 độ** — bảng kết quả kinh
doanh của `SBT_2025Q2` và `DGC_2025Q2` đều xoay ngang, và ở đó "đầu" không còn
nghĩa hình học nào chắc chắn. Hai, nó mô tả VỊ TRÍ chứ không mô tả THỨ CẦN
LẤY, nên không dùng để phân xử khi bảng có nhiều nhóm cột.

**Bố cục thật, soi trên hai tài liệu ngày 28/08/2026:**

| Biểu mẫu | Số cột số liệu | Lấy cột nào |
|---|---|---|
| Cân đối kế toán (B01) | 2 — hai THỜI ĐIỂM, vd "Ngày 31 tháng 12 năm 2025" và "Ngày 30 tháng 6 năm 2025" | cột có ngày **mới nhất** |
| Kết quả kinh doanh (B02) | **4** — nhóm "Quý N" và nhóm luỹ kế, mỗi nhóm có kỳ này và kỳ trước | **nhóm QUÝ, kỳ này** |

**Cạm bẫy chính, và nó đã cắn thật:** hai nhóm cột của B02 **kết thúc cùng một
ngày**. Trên `SBT_2025Q2`, cột "Quý II / Kỳ này" và cột "Kỳ kế toán 6 tháng
kết thúc ngày 31 tháng 12 / Kỳ này" đều kết thúc 31/12/2025. Nên **so ngày kết
thúc KHÔNG phân biệt được hai nhóm**. Phân biệt bằng ĐỘ DÀI kỳ: lấy kỳ ngắn
hơn.

Đây đúng chỗ pipeline đọc sai: nó lấy `12.105.315.641.553` (luỹ kế 6 tháng)
trong khi nhãn gold ghi `6.733.581.463.563` (quý II) — chênh lệch chiếm **8
trong 16 lỗi câm** còn lại của lượt chấm 27/08. Prompt của model đã sửa cùng
ngày.

**Số cột KHÔNG phụ thuộc báo cáo riêng hay hợp nhất.** `DGC_2025Q2` là báo cáo
**riêng** (`Mẫu số B 02 – DN`) và vẫn có đủ bốn cột; `SBT_2025Q2` là **hợp
nhất** (`B02a-DN/HN`) cũng bốn cột. Riêng/hợp nhất nói về PHẠM VI doanh nghiệp
được gộp, không nói gì về số cột kỳ.

### 28/08/2026 — Mã 51 và 52 giữ nguyên dấu như in; quy tắc cũ đã SAI

**Kết luận Câu 13: nhãn gold đúng, guideline sai.** Quy tắc *"dương khi mã 60
< mã 50"* ở mục 3.3 bị bỏ, thay bằng "giữ nguyên dấu như in, rồi kiểm bằng
đẳng thức mã 60". **Không tài liệu nào phải gán nhãn lại** — xem bằng chứng
bên dưới.

Vì sao quy tắc cũ sai: `Mã 60 = Mã 50 − Mã 51 − Mã 52` chỉ ràng buộc **tổng**
hai dòng thuế. Mã 51 đủ lớn thì mã 60 < mã 50 vẫn đúng trong khi mã 52 âm
hoàn toàn hợp lệ — mã 52 âm là **thu nhập** thuế hoãn lại, một trạng thái kế
toán có thật mà chính Thông tư mô tả (TT200 Điều 113 mục 3.17, phát sinh bên
Nợ ghi trong ngoặc đơn). Mệnh đề cũ đúng cho tổng thuế nhưng sai khi áp riêng
từng dòng, nên áp nguyên văn sẽ lật một giá trị hợp lệ thành sai.

Bằng chứng trên toàn bộ 11 file `data/gold/`, đo ngày 28/08/2026:

| | Số tài liệu |
|---|---|
| Mã 51 âm | **0** |
| Mã 52 âm | **3** — `HNG_2025H1_TT200`, `MWG_2025Q1_TT200`, `VRE_2026Q1_TT99` |
| Đẳng thức `mã 60 = mã 50 − mã 51 − mã 52` lệch | **0** |

Cả ba tài liệu có mã 52 âm đều cân đẳng thức tới từng đồng, tức dấu âm ấy là
số liệu thật chứ không phải lỗi chép. Quy tắc mới giữ nguyên chúng, nên không
nhãn nào phải sửa. (Tu chính 27/08/2026 chỉ nêu MWG và VRE; HNG là ca thứ ba,
tìm ra khi rà lại toàn bộ tập gold.)

Quy tắc mới cũng áp cho **mã 51**, dù Câu 13 chỉ hỏi về mã 52: cùng một lập
luận, và mã 51 âm cũng có nghĩa kế toán riêng. Không tài liệu nào bị ảnh
hưởng vì mã 51 dương ở cả 11 file.

Không có thay đổi hành vi nào ở code. `chuan_hoa_dau()` đã cố ý bỏ mã 52 ra
ngoài từ `a0cd5ab`, và `kiem_dau_khau_tru()` trong công cụ gán nhãn vốn đã
xét theo tiêu chí "lật dấu làm cân đẳng thức" chứ không theo chiều mã 50/60.
Tu chính này làm câu chữ guideline khớp lại với hai chỗ đó.

### 28/08/2026 — Tài liệu đã chạy pipeline bị loại khỏi tập gán nhãn đôi

**Trả lời Câu 12 của `HANDOFF.md` mục 0.** Mục 5 có thêm một tiểu mục, mục 8
có thêm một dòng danh mục kiểm. **Chưa tài liệu nào phải gán nhãn lại** —
thay đổi này chỉ thu hẹp tập được chọn cho phép đo đồng thuận, không đụng
tới quy tắc đọc số nên nhãn đã có vẫn dùng nguyên.

Lý do chọn loại hẳn thay vì "giữ kỷ luật không mở hai file kia": phương án
đo đồng thuận đang dùng là chính người chủ trì gán nhãn lại (chốt
26/08/2026), nên người gán lại đúng là người đã chạy pipeline. Kỷ luật ở đây
là một lời hứa không kiểm chứng được — nếu nó bị vi phạm thì con số đồng
thuận vẫn ra bình thường, không dấu vết. Loại tài liệu ra thì ràng buộc trở
thành kiểm được bằng máy, và cái giá phải trả chỉ là chỗ trong một tập ~100
tài liệu vốn thừa chỗ cho 20–33 tài liệu gán nhãn đôi.

Thi công kèm theo: khoá `gan_nhan_doi` trong `data/nguon_gold.json` (mười
tài liệu hiện có đều mang `loai_da_chay_pipeline`),
`src/eval/tap_dong_thuan.py` đối chiếu khai báo với hiện trạng
`data/output/`, và `tests/test_tap_dong_thuan.py` khoá chiều nguy hiểm — có
đầu ra pipeline mà danh mục chưa đánh dấu.

`VNM_2026Q1_TT99` cũng bị loại dù không nằm trong danh mục nguồn: nó có nhãn
gold và có đầu ra pipeline từ những lượt chạy trên tài liệu mẫu.

### 27/08/2026 — mã 52 của mục 3.3: ghi nhận mâu thuẫn, chưa sửa quy tắc

Lượt chấm pipeline phát hiện nhãn gold của `MWG_2025Q1_TT200` và
`VRE_2026Q1_TT99` ghi mã 52 ÂM trong khi cả hai đều có mã 60 < mã 50, tức
ngược với chữ nghĩa mục 3.3 lúc đó. Mục này chỉ **ghi nhận** mâu thuẫn và
chuyển lên người chủ trì (Câu 13); quy tắc chưa đổi, không tài liệu nào phải
gán nhãn lại. **Đã được tu chính 28/08/2026 ở trên thay thế trọn vẹn** — đọc
mục đó để biết kết luận và bằng chứng.

### 26/08/2026 (muộn nhất) — Nhóm Stress thứ ba đo bằng độ phân giải bản quét

**Chỗ sửa:** mục 7 đổi nhóm Stress thứ ba từ "bản scan chất lượng thấp" thành
"độ phân giải bản quét thấp", và đổi cách nhận ra từ phán đoán mắt người sang
số đo trong `data/nguon_gold.json`.

**Lý do — tiêu chí cũ được 100% quần thể thoả.** Cách nhận ra cũ là "mở PDF,
xem có phải ảnh nhúng không". Đo trên 23 tài liệu của 20 doanh nghiệp niêm
yết thì không tài liệu nào có lớp text thật; `pdftotext` lấy ra 44–734 byte
cho cả tài liệu 25–65 trang, và phần ít ỏi đó là chú thích chữ ký số, kể cả
ở `VNM_2026Q1_TT99`. Một tiêu chí mà cả tổng thể đều thoả thì không chọn ra
được gì, nên nhóm thứ ba đang chiếm một phần tư tập Stress mà không đóng góp
trục biến thiên nào. Giữ nguyên chữ và "diễn giải lại" thì để lại trong một
tài liệu cam kết một tiêu chí đã biết chắc là vô hiệu — đúng thứ mà việc viết
guideline trước sinh ra để chống.

**Trục thay thế trải rộng thật, đã đo.** `python src/do_do_phan_giai.py` trên
mười tài liệu của danh mục đầu cho **89,9 – 295,8 dpi**, trung vị 200,0. Số
đo ghi vào khoá `do_phan_giai_dpi` của từng mục trong `data/nguon_gold.json`.

**Ghi làm biến LIÊN TỤC, không chia nhóm theo ngưỡng.** Chốt một ngưỡng "thấp
là dưới X dpi" lúc mới có 10 tài liệu là chọn tham số trên mẫu mỏng, và là
tham số dễ bị chỉnh lại nhất sau khi đã nhìn thấy kết quả. Chọn tài liệu cho
nhóm thì theo thứ hạng trong chính tập gold; phân tích thì bằng tương quan
trên biến liên tục.

**Một giới hạn phải nói ra:** sáu trong mười tài liệu đo được **đúng 200,0
dpi**. Phân bố hiện dồn cục chứ không trải đều, nên sức phân biệt của trục
này ở quy mô 10 tài liệu chủ yếu nằm ở hai đuôi — `SBT` với `DLG` ở đầu thấp,
`MWG` ở đầu cao. Đủ 100 tài liệu thì đo lại phân bố trước khi tin vào một
phép tương quan nào.

**Độ phân giải không bao trọn chữ "chất lượng".** Trang lệch, dấu mộc đỏ đè
lên chữ số, in mờ lệch nét là những trục khác mà máy chưa đo được — ghi bằng
lời vào `da_kiem` của danh mục và `notes` của file gold, đừng gộp vào dpi.

**Không tài liệu nào phải gán nhãn lại:** tu chính này đổi cách CHỌN tài liệu
và cách mô tả chúng, không đổi một quy tắc đọc số nào.

### 26/08/2026 (muộn hơn nữa) — Ký hiệu mẫu thôi là dấu hiệu nhận diện chuẩn

**Chỗ sửa:** mục 3.7 bỏ dòng `Ký hiệu mẫu B 01a - DN → TT99` khỏi bảng dấu
hiệu, xếp hai dòng số hiệu thông tư lên trước, và thêm một luật phủ định nói
thẳng rằng hậu tố `a`/`b` không kết luận được gì về Thông tư. Danh mục kiểm ở
mục 8 nhắc lại luật phủ định đó.

**Lý do — file này tự mâu thuẫn với chính nó.** Mục 2 viết in đậm rằng hậu tố
`a`/`b` là KỲ BÁO CÁO và cả hai Thông tư đều dùng đủ ba ký hiệu; mục 3.7 lại
xếp `B 01a - DN` là dấu hiệu của TT99. Hai chỗ không thể cùng đúng. Mục 2 là
chỗ đúng: nó dẫn nguyên văn Công báo, và `src/fields_config.py` đã sửa
`FORM_MARKERS` theo hướng đó từ `023321c` sau khi bản cũ trượt mọi trang
`B01a-DN`. Tức code đã đi trước guideline, và guideline là bản còn sai.

**Cái giá nếu không sửa, đo được:** `SBT_2025Q2_TT200` và `HNG_2025H1_TT200`
đều mang ký hiệu `B01a-DN/HN` kèm tiêu đề *Bảng cân đối kế toán hợp nhất*.
Theo bảng cũ đó là "thấy dấu hiệu của cả hai", nên cả hai phải ghi `UNKNOWN`
dù chúng rõ ràng là TT200 — hai tài liệu bị `UNKNOWN` một cách máy móc, và
tỷ lệ 5 TT99 / 5 TT200 của danh mục gold đầu tiên vỡ.

**Không tài liệu nào phải gán nhãn lại.** Cả hai file đã ghi `standard` là
`TT200`, đúng bằng kết luận mà bảng mới cho ra.

**Thứ tự cam kết đã bị vượt, ghi lại vì đó là điều kiện để sổ này có giá
trị.** Luật 3 nói guideline viết trước, không sửa giữa chừng; đúng trình tự
thì tu chính này phải có TRƯỚC khi hai tài liệu ấy được gán nhãn. Thực tế
ngược lại: hai tài liệu được gán nhãn `TT200` trước, và chính việc gán nhãn
chúng mới làm lộ ra mâu thuẫn. Thiệt hại bằng 0 vì nhãn không đổi, nhưng
một cuốn sổ chỉ ghi những lần làm đúng trình tự thì không chứng minh được
gì về những lần còn lại.

### 26/08/2026 (muộn hơn) — Ba dòng khấu trừ ghi dương, không theo dấu ngoặc

**Thay đổi ở mục 3.3 và danh mục kiểm mục 8. Một tài liệu phải sửa:
`DGC_2025Q2_TT200`.**

> **ĐÃ BỊ TU CHÍNH 28/08/2026 SỬA MỘT PHẦN.** Quy tắc "mã 51 và 52 ghi dương
> khi mã 60 < mã 50" đặt ra ở đây **đã bị bỏ**; hai dòng thuế nay giữ nguyên
> dấu như in rồi kiểm bằng đẳng thức mã 60. Phần về **mã 11 (giá vốn) vẫn còn
> hiệu lực nguyên vẹn**, và toàn bộ lập luận dưới đây vẫn là hồ sơ lý do của
> nó. Đọc tu chính 28/08 trước khi áp bất cứ điều gì cho mã 51 hoặc 52.

**Bản trước nói "in trong ngoặc đơn ⇒ ghi giá trị âm", không trừ trường hợp
nào.** Quy tắc đó đúng với dòng mà dấu âm là số liệu, và sai với dòng mà dấu
ngoặc chỉ là cách trình bày một khoản bị trừ. Bản BCTC quý II/2025 của DGC in
cả hai loại trên cùng một trang: mã 40 `(83.660.312)` là lợi nhuận khác thật
sự âm, còn mã 11 `(107.515.846.476)` là giá vốn — một số dương mà văn bản đưa
vào công thức dưới dạng `Mã 20 = Mã 10 − Mã 11`.

**Hậu quả đã quan sát được, và nó không phải giả thuyết.** `DGC_2025Q2_TT200`
được gán nhãn đúng theo mục 3.3 bản cũ nên mã 11 và mã 51 ghi âm. Hai đẳng
thức B02 vì thế lệch, và file có `so_lan_kiem_dang_thuc = 11` — người gán
nhãn đã kiểm mười một lần mà không tìm ra, vì không có lỗi nào để tìm. Chín
trên chín chữ số của biểu B02 chép đúng nguyên trang giấy.

Mức lệch của cả hai đẳng thức đúng bằng **gấp đôi** trường bị đảo dấu
(`215.031.692.952 = 2 × 107.515.846.476` và `47.108.746.070 = 2 ×
23.554.373.035`). Đó là chữ ký số học của lỗi dấu, không phải của lỗi đọc —
đáng nhớ vì nó tách ngay ca này khỏi ca báo cáo tự mâu thuẫn.

**Vì sao chọn quy ước trị tuyệt đối thay vì viết lại đẳng thức theo số có
dấu.** Phương án viết lại đẳng thức (`10 + 11 = 20`, `50 + 51 + 52 = 60`) giữ
được nguyên tắc "chép, đừng diễn giải", nhưng nó phá một thứ không lấy lại
được: Thông tư dùng dấu âm ở mã 51 và 52 để mã hoá riêng trạng thái *thu nhập
thuế*. Nếu dấu âm cũng dùng cho chi phí in trong ngoặc thì hai trạng thái
khác nhau về bản chất trở thành cùng một giá trị, và không ai tách lại được.
Quy ước trị tuyệt đối giữ dấu âm cho đúng một nghĩa. Nó cũng khớp số học của
chính văn bản, khớp `allow_negative` trong `src/fields_config.py`, và khớp
hai tài liệu gold còn lại — `BMP_2026Q1_TT99` và `VNM_2026Q1_TT99` vốn đã ghi
mã 11 và 51 dương và cân sạch mọi đẳng thức.

Giá phải trả, nói thẳng: quy ước này đòi người gán nhãn nhận ra dòng nào là
dòng khấu trừ, tức thêm một chút ngữ nghĩa vào việc vốn thuần tuý là chép.
Danh sách đó hữu hạn — đúng ba mã trong bộ 26/27 chỉ tiêu — nên mục 3.3 liệt
kê hết, và công cụ gán nhãn nay tự kiểm dấu ba trường đó
(`kiem_dau_khau_tru`) thay vì để quy tắc nằm im trong tài liệu.

**Việc đã làm với `DGC_2025Q2_TT200`:** đảo dấu `gia_von_hang_ban` và
`thue_tndn_hien_hanh` sang dương, `so_lan_ghi` tăng lên 2, và
`sua_gia_tri_sau_khi_kiem` đặt `true` — vì xét thuần tuý theo dấu vết kiểm
toán thì tài liệu này cân sau khi sửa giá trị, chứ không cân ngay từ đầu.
Không chữ số nào bị đổi. Hai tài liệu gold còn lại không phải gán nhãn lại.

### 26/08/2026 — Hệ số 0,6 được xác nhận; đồng hồ do người tự bấm

**Hai thay đổi, cả hai ở mục 6, không tài liệu nào phải gán nhãn lại.**

**(a) Hệ số 0,6 nay là con số chốt.** Tu chính 25/08 đặt số phút đo trần
người ở `0,6 × trung vị thoi_gian_giay của 10 tài liệu gold đầu`, nhưng ghi
rõ hệ số 0,6 do phiên Claude đề xuất và còn chờ người chủ trì. Người chủ trì
xác nhận giữ 0,6 ngày 26/08/2026. Thời điểm xác nhận là điều đáng ghi: tập
gold khi đó có 1 tài liệu và **chưa tài liệu nào có số đo thời gian**, nên hệ
số được chốt trước khi nhìn thấy bất kỳ dữ liệu nào nó áp lên — đúng điều kiện
mà việc đăng ký trước cần.

**(b) `thoi_gian_giay` đổi nghĩa: thời gian LÀM VIỆC, do người tự bấm.** Bản
trước, công cụ tự chạy đồng hồ lúc người gõ xong `doc_id`, nên con số ra là
thời gian đồng hồ tường từ lúc đó tới lúc bấm Lưu. Nó đo sai theo cả hai
chiều: gõ `doc_id` rồi mới đi tìm file PDF, hay để cửa sổ mở qua buổi trưa,
đều bơm thêm thời gian không phải thời gian làm việc; ngược lại, người gõ
`doc_id` sau cùng thì đồng hồ gần như không chạy. Một trung vị dựng trên
những con số đó không đủ để chốt tham số nào.

Nay có nút **"Bắt đầu bấm giờ"** và nút **"Tạm dừng"**; `thoi_gian_giay` là
tổng các đoạn chạy, `so_lan_tam_dung` đếm số lần ngắt quãng. Quên bấm thì
công cụ **từ chối ghi file** trừ khi người tick "không đo giờ tài liệu này",
và file ghi ra tự khai điều đó qua khoá `trang_thai_dong_ho`.

**Vì sao không tài liệu nào phải gán nhãn lại.** Số tài liệu có số đo thời
gian dưới giao thức cũ là **0** — `VNM_2026Q1_TT99` có `thoi_gian_giay` bằng
0, tức chưa từng có số đo nào để mất. Thay đổi này không chạm nội dung nhãn,
không đổi bộ chỉ tiêu, không đổi quy tắc đọc số.

### 25/08/2026 (muộn hơn) — Giao thức đo trần người bỏ con số 15 phút cố định

**Phải gán nhãn lại: không tài liệu nào.** Sửa đổi này chỉ chạm mục 6, tức
giao thức của **10 tài liệu đo trần người**, và số tài liệu đã gán nhãn dưới
giao thức đó hiện là **0**. Tài liệu gold duy nhất đang có
(`VNM_2026Q1_TT99`) gán nhãn KỸ chứ không dưới đồng hồ, nên nó nằm ngoài
phạm vi ảnh hưởng.

**Sửa đổi.** Mục 6 bỏ con số "15 phút một tài liệu". Thay bằng công thức
`0,6 × trung vị thoi_gian_giay của 10 tài liệu gold đầu tiên`, sàn 5 phút.

**Lý do — có số đo, và nó ngược với dự đoán.** Cả `ADDENDUM` mục 6 lẫn bản
ghi Sửa đổi phía dưới đều dự đoán rằng 27 chỉ tiêu rải qua ba biểu mẫu sẽ
làm **vỡ** giao thức 15 phút. Tài liệu đầu tiên cho thấy ngược lại: công
đoạn điền hết khoảng 10 phút, tức 15 phút là dư chứ không thiếu. Một đồng hồ
rộng hơn nhịp làm kỹ thì không đo được gì, vì trần người sẽ trùng với chính
bản gold dùng để so.

**Một thứ tự cam kết đã bị vượt, ghi lại chứ không lặng lẽ bỏ qua.** Bản ghi
Sửa đổi 25/08 mục (d) ngay dưới đây viết rằng việc đo lại trần người "chặn
việc gán nhãn tài liệu đầu tiên" và phải làm TRƯỚC. Thực tế đã chạy ngược:
tài liệu đầu tiên gán nhãn trước, và chính nó cung cấp số liệu để sửa giao
thức. Thiệt hại thực bằng 0 vì hai lý do đã nêu ở đoạn đầu, nhưng thứ tự thì
đã khác cam kết, và người đọc preregistration sẽ thấy — nên nó phải nằm ở
đây chứ không nằm trong trí nhớ ai.

### 25/08/2026 — Bộ chỉ tiêu chuyển sang kịch bản E, B03 vào phạm vi

**Phải gán nhãn lại: không tài liệu nào.** `data/gold/` vẫn còn trống tại
thời điểm sửa, nên Luật 3 được thoả mà không tốn công làm lại. **Đây là lần
cuối cùng điều đó còn đúng** — ngay khi tài liệu đầu tiên được gán nhãn, mọi
thay đổi bộ chỉ tiêu đều buộc phải quay lại cả tập.

**(a) Bộ chỉ tiêu lên 27 với TT99 và 26 với TT200** (trước là 21 và 20).
Thêm 6 chỉ tiêu của báo cáo lưu chuyển tiền tệ B03: ba dòng lưu chuyển (mã
20, 30, 40), lưu chuyển thuần (50), tiền đầu kỳ (60), ảnh hưởng tỷ giá (61).

**(b) Ô "Biểu mẫu" ở mục 2 đảo lại: B03 nay CÓ gán nhãn.** Quyết định
23/08 loại B03 vì bộ chỉ tiêu khi đó chốt ở kịch bản D. Người chủ trì chốt
ngày 24/08/2026 chuyển sang kịch bản E, với lý do học thuật và có số đo hậu
thuẫn — E hơn D trên mọi trần định vị.

**(c) Đo được sau khi thi công**, ghi lại vì nó là kết quả của H0 và phải
báo cáo trung thực chứ không chỉ báo phần thuận lợi:

| | Kịch bản D | Kịch bản E |
|---|---:|---:|
| Chỉ tiêu (TT200 / TT99) | 20 / 21 | 26 / 27 |
| Đẳng thức | 7 | 9 |
| `rank(A)` | 7 | 9 |
| `dim null(A)` (TT200 / TT99) | 13 / 14 | 17 / 18 |
| Định vị được (TT200) | 5 / 20 | 7 / 26 |
| Cột toàn 0 | 0 | 0 |

Hai chỉ tiêu mới định vị được là `tien_va_tuong_duong_tien` và `lctt_thuan`.
Cái đầu là điểm đáng giá nhất của E: nó vốn đã có trong bộ chỉ tiêu nhưng
nằm chung một phương với bốn thành phần tài sản ngắn hạn khác, nên không
định vị được; đẳng thức liên kết chéo B03 gắn cho nó một đẳng thức THỨ HAI
và tách nó ra. Đó là cơ chế riêng của E mà không nhóm nào khác có.

**Nhưng phải nói cả phần không đẹp:** không gian null tăng từ 13 lên 17
chiều, và tỷ lệ định vị được gần như đứng yên (25% lên 27%). Thêm 6 chỉ tiêu
mà chỉ mua được 2 đẳng thức thì phần chênh lệch rơi hết vào không gian vô
hình. E vẫn tốt hơn D vì trần định vị cao hơn, nhưng nó không sửa được vấn
đề nền tảng mà H0 đã chỉ ra.

**(d) Việc CHƯA làm, và nó chặn việc gán nhãn tài liệu đầu tiên:** đo lại
trần người với 26 chỉ tiêu rải qua **ba** biểu mẫu. `ADDENDUM` mục 6 chốt
giao thức 15 phút một tài liệu khi bộ chỉ tiêu còn nằm trên hai biểu mẫu.
Ba biểu mẫu nhiều khả năng làm vỡ giao thức đó. Nếu vỡ thì phải sửa giao
thức **trước** khi gán nhãn tài liệu đầu tiên, không phải sau.

### 23/08/2026 — Bộ chỉ tiêu, phạm vi biểu mẫu, và quy tắc ô trống

**Phải gán nhãn lại: không tài liệu nào.** Chưa có tài liệu nào được gán
nhãn tại thời điểm sửa (`data/gold/` còn trống), nên Luật 3 được thoả mà
không tốn công làm lại.

Bốn thay đổi, đều là hệ quả của việc Mốc 1 chốt bộ chỉ tiêu ở kịch bản D:

**(a) Bộ chỉ tiêu lên 21 với TT99 và 20 với TT200** (trước là 11). Danh sách
chính thức nằm ở `FIELD_MAP` trong `src/fields_config.py`, không chép lại
vào guideline để hai bản khỏi lệch nhau.

**(b) Hai ô phạm vi ở mục 2 đã chốt:** không gán nhãn B03, không gán nhãn
cột kỳ so sánh. Lý do đầy đủ ở `PREREGISTRATION.md` mục Sửa đổi cùng ngày.

**(c) Mục 3.4 đổi quy tắc ô trống: dòng vắng mặt ghi `0`, không phải `null`.**
Đây là thay đổi có ảnh hưởng thật tới số liệu, nên nêu lý do đầy đủ ngay
trong mục 3.4. Tóm tắt: bước kiểm đẳng thức bỏ qua **cả đẳng thức** nếu bất
kỳ thành phần nào là `null`, mà đẳng thức phân rã tài sản ngắn hạn có 5–6
thành phần — nên quy tắc cũ làm đẳng thức giá trị nhất im lặng không chạy
trên phần lớn tài liệu. `null` từ nay chỉ có nghĩa "có dòng mà đọc không
ra". Danh mục kiểm ở mục 8 đã sửa theo.

**(d) Mục 3.6 thêm ba mã đổi nghĩa giữa hai chuẩn** (270, 150, 142) và các
cặp dễ nhầm mới sinh ra từ bộ chỉ tiêu mở rộng.
