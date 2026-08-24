# MỐC 1 — bảng đối chiếu ma trận ràng buộc với Thông tư

Tài liệu này để **người chủ trì** làm, không phải AI. BUILD-SPEC mục 0.5 nêu
lý do: sai một dấu trong ma trận ràng buộc thì toàn bộ kết quả identifiability
sai mà **không có gì báo** — code vẫn chạy, số vẫn ra, chỉ là sai.

Mốc này chặn B4, mà B4 quyết định chi phí gán nhãn tay cho 60 tài liệu gold —
khoản đắt nhất của cả dự án.

---

## 1. Vấn đề, giải thích bằng số thật

### 1.1 Ràng buộc phát hiện được lỗi, nhưng thường không chỉ ra lỗi ở đâu

Lấy đúng số của VNM Q1/2026, đơn vị đồng:

```
tai_san_ngan_han     29.403.116.984.122
tai_san_dai_han      18.372.709.942.261
                   + ────────────────────
tong_tai_san         47.775.826.926.383   ✓ khớp
```

Giả sử hệ đọc sai **một chữ số** của `tai_san_ngan_han`, thành
`29.403.116.984.**9**22` — lớn hơn giá trị thật 800 đồng. Bây giờ phép cộng
lệch 800. **Ta phát hiện được là có lỗi.** Đó là công dụng của ràng buộc.

Nhưng lỗi nằm ở đâu? Có đúng **ba** khả năng, và cả ba cho ra lệch 800 y hệt:

| Khả năng | Phép cộng lệch |
|---|---|
| `tai_san_ngan_han` lớn hơn thật 800 | +800 |
| `tai_san_dai_han` lớn hơn thật 800 | +800 |
| `tong_tai_san` nhỏ hơn thật 800 | +800 |

Nhìn vào con số lệch, **không có cách nào** phân biệt ba khả năng đó. Không
phải thuật toán của ta yếu — mà là **thông tin để phân biệt không tồn tại**.
Mọi thuật toán trên đời đều đâm vào cùng bức tường này.

Đó chính là nghĩa của "không định vị được", và đó là lý do bảng
identifiability hiện báo **1/11**.

### 1.2 Cái phá được thế bí: một con số nằm trong HAI quan hệ

Giả sử ngoài đẳng thức trên, ta còn biết thêm một quan hệ nữa — bảng cân đối
cũng phân rã tài sản ngắn hạn ra:

```
tien + đầu tư ngắn hạn + phải thu + hàng tồn kho + khác = tai_san_ngan_han
```

Giờ chạy lại ba khả năng, và xem **những đẳng thức nào** bị lệch:

| Khả năng | Đẳng thức 1 (TSNH+TSDH=TTS) | Đẳng thức 2 (phân rã TSNH) |
|---|---|---|
| `tai_san_ngan_han` sai | **lệch** | **lệch** |
| `tai_san_dai_han` sai | **lệch** | khớp |
| `tong_tai_san` sai | **lệch** | khớp |

`tai_san_ngan_han` giờ để lại một **dấu vân tay** khác hẳn: nó làm hỏng
*hai* đẳng thức, hai cái kia chỉ làm hỏng *một*. Ta phân biệt được nó.

Đó là toàn bộ ý tưởng, phát biểu gọn:

> Một chỉ tiêu **định vị được** khi tập các đẳng thức chứa nó khác với tập
> đẳng thức của **mọi** chỉ tiêu khác. Con số nào chỉ nằm trong **một** quan
> hệ, cùng với các anh em của nó, thì mãi mãi lẫn với anh em.

Trong ngôn ngữ ma trận: cột của nó trong `A` phải khác 0 và không tỷ lệ với
cột nào khác. `src/constraints.py` kiểm đúng điều đó.

### 1.3 Nhưng phân rã là một cái cối xay

Ở ví dụ trên, `tai_san_ngan_han` được cứu. Nhưng để cứu nó, ta vừa đưa thêm
**năm chỉ tiêu mới** vào — tiền, đầu tư ngắn hạn, phải thu, hàng tồn kho,
khác. Và mỗi chỉ tiêu mới đó giờ lại chỉ nằm trong **một** đẳng thức duy
nhất, cùng với bốn anh em của nó. **Chúng là lá mới, và chúng không định vị
được.**

Phân rã tiếp một trong số chúng thì cũng vậy: cứu được nó, sinh ra một tầng
lá mới bên dưới. Cối xay không bao giờ hết lá.

Và đây là chỗ đau: **mỗi chỉ tiêu thêm vào là chi phí gán nhãn tay nhân với
60 tài liệu.** Đó là khoản đắt nhất của cả dự án.

Số đo cho thấy tỷ lệ trao đổi. Chạy `python src/constraints_scenarios.py`:

| KB | Kịch bản | Chỉ tiêu | Đẳng thức | rank | Định vị được |
|---|---|---:|---:|---:|---:|
| A | Hiện tại | 11 | 3 | 3 | 1/11 (9%) |
| B | + Tổng nguồn vốn | 12 | 4 | 4 | 2/12 (17%) |
| C | + chuỗi lãi lỗ trên B02 | 15 | 6 | 6 | 3/15 (20%) |
| D | + phân rã Tài sản ngắn hạn | 19 | 7 | 7 | 5/19 (26%) |
| E | **+ quan hệ nối B01/B02/B03** | 26 | 11 | 11 | **13/26 (50%)** |

- Các bước phân rã **A→D**: thêm **8** chỉ tiêu, mua được **4** chỉ tiêu
  định vị được. Tỷ lệ 0,5.
- Bước nối chéo **D→E**: thêm **7** chỉ tiêu, mua được **8**. Tỷ lệ 1,1.

**Gấp đôi hiệu suất trên mỗi đồng chi phí gán nhãn.** Lý do: quan hệ nối
chéo gắn đẳng thức thứ hai vào một chỉ tiêu **đã có sẵn trong bộ**, thay vì
phải mở cả một tầng lá mới bên dưới.

### 1.4 Nên khi đọc Phụ lục IV, tìm cái gì

Không phải "còn chỉ tiêu nào chưa trích".

**Mà là: con số nào ta ĐÃ trích lại xuất hiện trong một quan hệ THỨ HAI.**

Ba ứng viên tôi dựng lại được từ kết cấu biểu mẫu — **đây là phỏng đoán,
chưa đối chiếu văn bản, đó chính là việc bạn sắp làm**:

| Ứng viên | Ý tưởng | Nó cứu chỉ tiêu nào |
|---|---|---|
| Tiền cuối kỳ trên **B03** chính là Tiền và tương đương tiền trên **B01** | Cùng một con số in ở hai biểu mẫu | `tien` — và qua đó cả nhóm tài sản ngắn hạn |
| Lợi nhuận chưa phân phối trên **B01** = LNCPP đầu kỳ + LNST trên **B02** − cổ tức | Nối bảng cân đối với báo cáo lãi lỗ | `loi_nhuan_sau_thue` |
| **Cột kỳ trước** cùng thoả một hệ đẳng thức | Đã có sẵn trên trang, không tốn gì thêm | Chưa đo — proposal mục 6.1(d) hỏi đúng câu này |

### 1.5 Một chỉ tiêu vẫn nằm ngoài tầm ở MỌI kịch bản

`hang_ton_kho` không định vị được ở A, B, C, D, lẫn E.

Đáng chú ý vì đó **đúng là chỉ tiêu đã có lỗi đọc thật** trên báo cáo VNM —
alias "Hàng tồn kho" khớp trúng dòng "Dự phòng giảm giá hàng tồn kho" (mã
142), cho ra giá trị nhỏ hơn thật khoảng nghìn lần nhưng hợp lệ về hình
thức.

Nghĩa là: **ràng buộc kế toán chứng minh được là không bao giờ bắt được lỗi
đó.** Chỉ mỏ neo đơn vị tính và việc đọc lại crop mới bắt được. Đây là ví dụ
cụ thể, có thật, để đưa vào bài — và nó chính là lập luận bảo vệ đóng góp
cốt lõi.

## 2. Lấy văn bản ở đâu

### Nguồn chính thức — dùng để TRÍCH DẪN trong bài

**Công báo Chính phủ** là công báo chính thức, và đây là nguồn nên trích dẫn:

- Thông tư 200/2014/TT-BTC (ban hành 22/12/2014):
  https://congbao.chinhphu.vn/van-ban/thong-tu-so-200-2014-tt-btc-6697.htm
- Thông tư 99/2025/TT-BTC (ban hành 27/10/2025, hiệu lực 01/01/2026):
  https://congbao.chinhphu.vn/van-ban/thong-tu-so-99-2025-tt-btc-46529.htm

**Lưu ý quan trọng về TT99:** Công báo tách nó thành **10 số** (từ số
1563+1564 tới số 1581+1582), mỗi số có bản `.pdf` và bản `.doc`. Lý do là các
phụ lục rất dài. Phần thân thông tư nằm ở số đầu; **Phụ lục IV nằm ở các số
cuối**. Tải bản `.doc` nếu định tìm chuỗi — dễ mở và dễ tìm hơn PDF quét.

### Nguồn tiện dụng — dùng để ĐỌC

thuvienphapluat.vn có bài đăng riêng gom các phụ lục thành file Word:
https://thuvienphapluat.vn/phap-luat-doanh-nghiep/bai-viet/file-word-phu-luc-che-do-ke-toan-doanh-nghiep-theo-thong-tu-99-2025-tt-btc-17560.html

Trang này chặn truy cập tự động nên phải mở bằng trình duyệt, và có thể đòi
tài khoản. Dùng nó để đọc cho nhanh, nhưng **trích dẫn trong bài thì trích
Công báo**, vì đó mới là nguồn chính thức.

### Cách tìm đúng chỗ trong file

Đừng đọc từ đầu — phụ lục dài hàng trăm trang. Tìm theo chuỗi:

| Cần tìm | Chuỗi tìm trong TT200 | Chuỗi tìm trong TT99 |
|---|---|---|
| Bảng cân đối / Báo cáo tình hình tài chính | `Bảng cân đối kế toán` hoặc `B 01` | `Báo cáo tình hình tài chính` hoặc `B 01a` |
| Báo cáo kết quả kinh doanh | `Báo cáo kết quả hoạt động kinh doanh` hoặc `B 02` | `B 02a` |
| Báo cáo lưu chuyển tiền tệ | `Báo cáo lưu chuyển tiền tệ` hoặc `B 03` | `B 03a` |
| **Đẳng thức giữa các mã số** | `Mã số 270 = Mã số` | `Mã số 280 = Mã số` |

Chuỗi cuối là chuỗi đáng giá nhất. Phần "Nội dung và phương pháp lập các chỉ
tiêu" của phụ lục thường ghi thẳng công thức dưới dạng `Mã số X = Mã số Y +
Mã số Z`. **Tìm mọi lần xuất hiện của `Mã số` kèm dấu `=`** — đó chính là tập
đẳng thức mà mục 1 đang cần.

### Đặt file vào đâu

```
data/legal/TT200-2014-phu-luc-IV.pdf     (hoặc .doc)
data/legal/TT99-2025-phu-luc-IV.pdf
```

Thư mục `data/legal/` đã có sẵn và **đã gitignore**. Bản thân văn bản quy
phạm pháp luật không có bản quyền (Luật Sở hữu trí tuệ điều 15), nhưng file
Công báo nặng vài chục MB và tải lại được bất cứ lúc nào, nên không đưa vào
git. Thứ vào git là **kết quả đối chiếu**, tức chính file này.

---

## 3. Bảng đối chiếu — đã xác nhận từng dòng

> **Trạng thái: XONG, 23/08/2026.** Mọi ô ☐ trong mục này đã được đối chiếu
> với Công báo và đóng lại. Hai câu hỏi mở của bản trước đều đã có đáp án, và
> **một trong hai có đáp án ngược với giả định ban đầu** — xem 3.2.
>
> Nguồn dùng để đối chiếu, đều nằm trong `data/legal/` (đã gitignore):
> TT200 ở `2015_287 + 288` (Điều 88–113) và `2015_289 + 290` (Điều 114–130);
> TT99 ở `2025_1577 + 1578` (Phụ lục IV Mục 1 — biểu mẫu), `2025_1579 + 1580`
> (B01 + B02) và `2025_1581 + 1582` (cuối B02 + B03 + B09). Trích bằng
> `pdftotext -layout -enc UTF-8` cho PDF và `antiword -m UTF-8.txt` cho `.doc`.

### 3.1 Mã số dòng đang dùng trong code

Nguồn trong code: `src/fields_config.py`, `FIELD_LINE_CODES`.

Chỗ đối chiếu trong văn bản: TT200 Điều 112 (B01) và Điều 113 (B02); TT99
phần "Nội dung và phương pháp lập các chỉ tiêu" của Báo cáo tình hình tài
chính và của B02, cùng biểu mẫu ở Phụ lục IV Mục 1.

**Cột chuẩn không còn ghi hậu tố `a`.** Bản trước ghi TT99 là `B01a` để phân
biệt với `B01` của TT200. Cách ghi đó sai theo đúng phát hiện ở 3.5: hậu tố
`a`/`b` phân biệt **kỳ báo cáo**, không phân biệt Thông tư, và cả hai chuẩn
đều dùng đủ `B01`, `B01a`, `B01b` trên **cùng một bộ mã số**.

| Chỉ tiêu | TT200 | TT99 | Đã xác nhận? |
|---|---|---|---|
| `tai_san_ngan_han` | B01 · 100 | B01 · 100 | ✔ |
| `hang_ton_kho` | B01 · 140 | B01 · 140 | ✔ |
| `tai_san_dai_han` | B01 · 200 | B01 · 200 | ✔ |
| `tong_tai_san` | B01 · **270** | B01 · **280** | ✔ ← khác nhau, và xem cảnh báo dưới |
| `no_phai_tra` | B01 · 300 | B01 · 300 | ✔ |
| `von_chu_so_huu` | B01 · 400 | B01 · 400 | ✔ |
| `doanh_thu_thuan` | B02 · 10 | B02 · 10 | ✔ |
| `gia_von_hang_ban` | B02 · 11 | B02 · 11 | ✔ |
| `loi_nhuan_gop` | B02 · 20 | B02 · 20 | ✔ |
| `loi_nhuan_truoc_thue` | B02 · 50 | B02 · 50 | ✔ |
| `loi_nhuan_sau_thue` | B02 · 60 | B02 · 60 | ✔ |

Cả 11 mã đều khớp. Nhưng việc "khớp" không có nghĩa là an toàn, vì **hai mã
số mang nghĩa khác nhau giữa hai chuẩn**, và cả hai đều là nguồn lỗi câm:

| Mã | TT200 | TT99 | Vì sao nguy hiểm |
|---|---|---|---|
| **270** | Tổng cộng tài sản | **Tài sản dài hạn khác** (`270 = 271+272+273+274`) | Tra nhầm bảng mã thì đọc ra một con số **hợp lệ** của một chỉ tiêu hoàn toàn khác. Không quy tắc kiểm nào bắt được |
| **142** | Giá trị hao mòn luỹ kế thuộc nhóm hàng tồn kho | **Dự phòng giảm giá hàng tồn kho** (TT200 để mã **149**) | Cùng loại lỗi, quy mô nhỏ hơn |

Đây chính là lý do `standard` là tham số **bắt buộc** của
`extract_field_by_code()` chứ không có giá trị mặc định.

### 3.2 Hai chỗ từng CHƯA xác nhận — nay đã đóng lại

Giữ nguyên câu hỏi gốc để thấy được cái gì đã bị bác bỏ. Việc xoá đi rồi viết
lại như thể chưa từng sai sẽ làm mất đúng thông tin đáng giá nhất của mục này.

**(a) Ký hiệu mẫu biểu của TT200 là `B01-DN` hay `B01a-DN`? — ĐÃ BỊ BÁC BỎ.**

> *Giả định của bản trước:* `FORM_MARKERS` cho rằng TT200 dùng `B 01` không có
> hậu tố `a` còn TT99 dùng `B 01a`, nên regex TT200 phải mang `(?!\s*a)` để
> khỏi khớp nhầm trang TT99.

Văn bản trả lời: **cả hai chuẩn dùng đủ cả ba ký hiệu**, và chữ `a` không hề
là dấu hiệu của Thông tư — nó là dấu hiệu của **kỳ báo cáo**. Toàn bộ lập
luận trên đứng trên một tiền đề sai. Chi tiết, nguyên văn trích dẫn và hậu
quả cụ thể ở **mục 3.5**; bản sửa là commit `023321c`.

**(b) Bộ đẳng thức của TT99 dùng chung với TT200 — ĐÚNG, và đó là kết quả.**

> *Lo ngại của bản trước:* `FIELD_IDENTITIES` khai báo TT99 ba đẳng thức giống
> hệt TT200 mà chưa ai kiểm; nếu sai thì trục nghiên cứu "TT200 → TT99" hỏng,
> vì trục đó dựa vào việc hai chuẩn **khác nhau**.

Đã đối chiếu: với **ba đẳng thức đang xét ở mục này**, TT99 giữ nguyên cả ba,
chỉ đổi mã tổng tài sản từ 270 sang 280. Code đang mô tả đúng.

> **Bổ sung 23/08/2026, sau khi thi công bộ chỉ tiêu mới.** Kết luận trên
> đúng trong phạm vi ba đẳng thức, nhưng **không** tổng quát được thành "hai
> chuẩn đẳng cấu". Khi mở sang bộ 7 đẳng thức của kịch bản D thì lộ ra một
> khác biệt thật: phân rã tài sản ngắn hạn là `100 = 110+120+130+140+150` ở
> TT200 nhưng `100 = 110+120+130+140+150+160` ở TT99, vì TT99 chèn thêm
> **Tài sản sinh học ngắn hạn** vào mã 150 và đẩy Tài sản ngắn hạn khác sang
> 160. Nên TT200 có 20 chỉ tiêu, TT99 có 21, và ma trận của chúng khác chiều.
> Chi tiết ở `PREREGISTRATION.md` mục Sửa đổi ngày 23/08/2026.

Dù vậy, **sáu trên bảy** đẳng thức vẫn giống hệt nhau, nên nhận xét về trọng
tâm của trục nghiên cứu vẫn đứng: hai chuẩn khác nhau chủ yếu ở **cách đánh
số và cách gọi tên** chứ không ở cấu trúc quan hệ kế toán. Mã 270 đổi nghĩa,
mã 150 đổi nghĩa, dự phòng đổi từ 149 sang 142, và "Bảng cân đối kế toán" đổi
tên thành "Báo cáo tình hình tài chính".

Hệ quả cho bài viết: distribution shift giữa hai chuẩn nằm chủ yếu ở **tầng
nhận diện và tra cứu**, không ở tầng ràng buộc. Ablation số 8 (transfer TT200
→ TT99) vì thế kiểm chủ yếu một thứ — hệ có nhận diện đúng chuẩn rồi tra đúng
bảng mã không — chứ không kiểm khả năng tổng quát hoá của phần suy luận ràng
buộc. Đó là phát biểu hẹp hơn bản đăng ký ban đầu ngụ ý, và phải viết đúng
như vậy.

### 3.3 Đẳng thức đang mã hoá

Cả hai chuẩn dùng chung ba đẳng thức này, và **cả ba đều đã đối chiếu, đều
đúng**:

| # | Đẳng thức | Xác nhận TT200 | Xác nhận TT99 |
|---|---|---|---|
| 1 | `tai_san_ngan_han + tai_san_dai_han = tong_tai_san` | ✔ `Mã số 270 = Mã số 100 + Mã số 200` | ✔ `Mã số 280 = Mã số 100 + Mã số 200` |
| 2 | `no_phai_tra + von_chu_so_huu = tong_tai_san` | ✔ **suy ra hai bước** | ✔ **suy ra hai bước** |
| 3 | `gia_von_hang_ban + loi_nhuan_gop = doanh_thu_thuan` | ✔ `Mã số 20 = Mã số 10 - Mã số 11` | ✔ `Mã số 20 = Mã số 10 - Mã số 11` |

**Đẳng thức 2 không có trong văn bản dưới dạng một dòng.** Nghi ngờ của bản
trước là đúng: cả hai Thông tư viết `Mã số 440 = Mã số 300 + Mã số 400`, rồi
viết **riêng** ở một khối kẻ khung ngay sau đó:

> Chỉ tiêu "Tổng cộng Tài sản Mã số 270" = Chỉ tiêu "Tổng cộng Nguồn vốn Mã số 440"

(TT99 giống hệt, thay 270 bằng 280.)

Tức quan hệ thật là **hai bước**, và code đang gộp chúng làm một. Gộp lại làm
mất một đẳng thức và mất một con số đọc được từ trang giấy — **Tổng cộng nguồn
vốn** in ngay cuối bảng cân đối. Đó chính là kịch bản B ở mục 1, và đó là lý do
kịch bản B mua được tỷ lệ 1,00: nó không thêm ràng buộc mới, nó chỉ **thôi vứt
đi** một ràng buộc mà văn bản vốn đã khai báo tách bạch.

### 3.4 Đẳng thức tìm thêm được — điền vào đây

Đây là phần chính của cả buổi làm việc. Sáu bước:

**Bước 1.** Mở file, tìm phần **"Nội dung và phương pháp lập các chỉ tiêu"**
của Báo cáo tình hình tài chính (TT99) hoặc Bảng cân đối kế toán (TT200).

**Bước 2.** Tìm mọi lần xuất hiện của chuỗi `Mã số` đứng gần dấu `=`. Văn
bản thường viết công thức ngay trong phần mô tả từng chỉ tiêu, kiểu:

```
Chỉ tiêu này phản ánh ...
Mã số 100 = Mã số 110 + Mã số 120 + Mã số 130 + Mã số 140 + Mã số 150
```

**Bước 3.** Chép **nguyên văn** vào bảng bên dưới. Đừng dịch sang tên chỉ
tiêu, đừng rút gọn — mã số là thứ đối chiếu được, tên thì mỗi chỗ viết một
kiểu.

**Bước 4.** Với mỗi đẳng thức, đánh dấu cột cuối: **có chỉ tiêu nào trong đó
cũng xuất hiện ở một đẳng thức KHÁC không?** Đó là câu hỏi ăn tiền — xem mục
1.4. Nếu có, ghi rõ đẳng thức kia là cái nào.

**Bước 5.** Lặp lại cho **B02** (kết quả kinh doanh) và **B03** (lưu chuyển
tiền tệ). B03 quan trọng dù hiện chưa trích chỉ tiêu nào từ đó, vì đó là chỗ
nhiều khả năng có quan hệ nối sang B01 nhất.

**Bước 6.** Làm cả hai Thông tư, ghi riêng. **Đừng giả định TT99 giống
TT200** — chính chỗ đó đang là giả định chưa kiểm, xem mục 3.2(b).

#### Ví dụ đã điền (minh hoạ cách ghi, KHÔNG phải số liệu thật)

| Biểu mẫu | Đẳng thức theo văn bản | Chuẩn | Trùng chỉ tiêu với đẳng thức nào khác? |
|---|---|---|---|
| B01a | `Mã số 100 = MS 110 + MS 120 + MS 130 + MS 140 + MS 150` | TT99 | Có — MS 100 cũng nằm trong `MS 280 = MS 100 + MS 200` |
| B01a | `Mã số 280 = Mã số 100 + Mã số 200` | TT99 | Có — MS 100 (ở trên), MS 200 |
| B03a | `Mã số 70 = MS 60 + MS 50 + MS 61` | TT99 | *(điền sau khi kiểm MS 70 có bằng MS 110 của B01a không)* |

Dòng thứ ba là loại đáng giá nhất nếu xác nhận được: nó nối **hai biểu mẫu
khác nhau**, tức gắn một đẳng thức thứ hai vào một chỉ tiêu đã có sẵn.

#### ĐÃ TRÍCH ĐƯỢC — 23/08/2026

Nguồn: `data/legal/2015_289 + 290-200_2014_TT-BTC.pdf` (TT200, Điều 114) và
`data/legal/2025_1581 + 1582_99-2025-TT-BTC.doc` (TT99, phần B03). Trích bằng
`pdftotext -layout` và `antiword`.

Cả hai chuẩn khai báo **giống hệt nhau**, chỉ khác tên biểu mẫu B01:

| # | Đẳng thức theo văn bản | Cả hai chuẩn? | Liên kết chéo? |
|---|---|---|---|
| 1 | `Mã số 50 = Mã số 20 + Mã số 30 + Mã số 40` | Có | Không — nội bộ B03 |
| 2 | `Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61` | Có | Không — nội bộ B03 |
| 3 | `Mã số 70` (B03) **= Mã số 110** trên B01, cột "Số cuối kỳ" | Có | **CÓ** |
| 4 | `Mã số 60` (B03) **= Mã số 110** trên B01, cột "Số đầu kỳ" | Có | **CÓ — và nối sang KỲ TRƯỚC** |

Nguyên văn TT200, Điều 114, mục "Tiền và tương đương tiền cuối kỳ (Mã số 70)":

> Chỉ tiêu này bằng số "Tổng cộng" của các chỉ tiêu Mã số 50, 60 và 61 và
> **bằng chỉ tiêu Mã số 110 trên Bảng cân đối kế toán kỳ đó**. Mã số 70 =
> Mã số 50 + Mã số 60 + Mã số 61.

TT99 nói y hệt, chỉ thay "Bảng cân đối kế toán" bằng "Báo cáo tình hình tài
chính".

**Ý nghĩa.** Đây đúng là loại quan hệ mục 1.4 đi tìm, và nó được văn bản
khai báo tường minh chứ không phải suy diễn. Ghép mục 2, 3, 4 lại cho:

```
B01.110 (cuối kỳ) = B01.110 (đầu kỳ) + B03.50 + B03.61
```

Tức nó nối **bảng cân đối kỳ này với bảng cân đối kỳ trước**. Đó chính là câu
hỏi ở proposal mục 6.1(d) về giá trị của cột kỳ trước — và câu trả lời là
cột kỳ trước **có** ràng buộc thật nối vào, qua báo cáo lưu chuyển tiền tệ.

**Nhưng nó chưa trả tiền ngay.** Đo bằng `constraints.py`:

| Bộ | Chỉ tiêu | Đẳng thức | Định vị được |
|---|---:|---:|---:|
| Hiện tại | 11 | 3 | 1/11 |
| + chuỗi B03 đã xác nhận | 18 | 5 | 2/18 |
| + phân rã TSNH (**đã xác nhận**) | 21 | 6 | **5/21** |

Lý do: liên kết chéo gắn đẳng thức thứ hai vào `B01.110`, nhưng `B01.110`
phải **đã nằm trong một đẳng thức nào đó** thì mới có cái để gắn thêm. Đẳng
thức đó là phân rã Tài sản ngắn hạn — nằm ở Điều 112.

#### ĐÃ TRÍCH NỐT — 23/08/2026, đủ cả năm file Công báo

Thêm `2015_287 + 288-200_2014_TT-BTC.pdf` (TT200, Điều 88–113, có phân rã
Tài sản ngắn hạn ở Điều 112) và `2025_1579 + 1580_99-2025-TT-BTC.doc` (TT99,
Báo cáo tình hình tài chính + B02).

> **Đính chính.** Bản trước ghi số `1577 + 1578` "không chứa phần báo cáo
> tài chính — 0 đẳng thức". Sai, và sai theo hướng nguy hiểm: nó không chứa
> đẳng thức viết bằng lời, nhưng nó chính là **Phụ lục IV Mục 1 — BIỂU MẪU
> BÁO CÁO TÀI CHÍNH**, tức đúng nguồn mà `BUILD-SPEC.md` mục A3 bắt phải lấy
> mã số dòng TT99 từ đó thay vì từ bài tóm tắt trên mạng. Biểu mẫu còn in
> sẵn đẳng thức ngay trong tên chỉ tiêu: `TỔNG CỘNG TÀI SẢN (280 = 100 +
> 200)`. Đừng bỏ qua file này.

Bảng cân đối / Báo cáo tình hình tài chính, **cấu trúc giống nhau ở cả hai
chuẩn**, chỉ khác mã số Tổng cộng tài sản:

| Đẳng thức | TT200 | TT99 |
|---|---|---|
| Tổng tài sản | `270 = 100 + 200` | `280 = 100 + 200` |
| **Tổng nguồn vốn** | `440 = 300 + 400` | `440 = 300 + 400` |
| **Cân đối** | `270 = 440` | `280 = 440` |
| Tài sản ngắn hạn | `100 = 110+120+130+140+150` | `100 = 110+…+150+160` |
| Tiền | `110 = 111 + 112` | `110 = 111 + 112` |
| Hàng tồn kho | `140 = 141 + **149**` | `140 = 141 + **142**` |
| Nợ phải trả | `300 = 310 + 330` | `300 = 310 + 330` |
| Vốn chủ sở hữu | `400 = 410 + 430` | `400 = 411 + 412 + …` |

Báo cáo kết quả kinh doanh, **giống hệt nhau ở cả hai chuẩn**:

| Đẳng thức | Nội dung |
|---|---|
| `10 = 01 − 02` | Doanh thu thuần |
| `20 = 10 − 11` | Lợi nhuận gộp |
| `40 = 31 − 32` | Lợi nhuận khác |
| `50 = 30 + 40` | Lợi nhuận trước thuế |
| `60 = 50 − (51 + 52)` | Lợi nhuận sau thuế |

##### Ba đẳng thức repo đang dùng: đều ĐÚNG

- `100 + 200 = 270/280` ✅ khớp nguyên văn
- `300 + 400 = 270/280` ✅ đúng, nhưng là đẳng thức **suy ra** — văn bản viết
  `440 = 300 + 400` rồi viết **riêng** `Tổng cộng Tài sản = Tổng cộng Nguồn
  vốn`. Gộp làm một vẫn đúng về toán nhưng mất một quan sát đọc được.
- `11 + 20 = 10` ✅ khớp `20 = 10 − 11`

##### Kết quả đo — và một kết luận cũ bị bác bỏ

Chạy `python src/constraints_scenarios.py`:

| KB | Kịch bản | Chỉ tiêu | Định vị được | Bước này mua được |
|---|---|---:|---:|---|
| A | Hiện tại | 11 | 1/11 (9%) | — |
| B | **+ Tổng cộng nguồn vốn (440)** | 12 | 2/12 (17%) | **+1 → +1, tỷ lệ 1,00** |
| C | + chuỗi lãi lỗ B02 | 16 | 3/16 (19%) | +4 → +1, tỷ lệ 0,25 |
| D | + phân rã Tài sản ngắn hạn | 20 | 5/20 (25%) | +4 → +2, tỷ lệ 0,50 |
| E | + B03 và liên kết chéo | 26 | 7/26 (27%) | +6 → +2, tỷ lệ 0,33 |

**Bước rẻ nhất là B: thêm ĐÚNG MỘT chỉ tiêu.** Tổng cộng nguồn vốn nằm ngay
trong hai đẳng thức nên định vị được lập tức, và nó là con số in ở cuối bảng
cân đối — rẻ cả về chi phí gán nhãn.

> **Kết luận ở mục 1.3 đã bị bác bỏ.** Bản trước dùng đẳng thức giả thuyết
> và nói liên kết chéo hiệu quả **gấp đôi** phân rã. Sai: hai đẳng thức từng
> được giả định — liên kết Lợi nhuận chưa phân phối (B01) với Lợi nhuận sau
> thuế (B02), và phân rã Vốn chủ sở hữu — **không có trong văn bản**. Với
> đẳng thức thật, liên kết chéo cho tỷ lệ 0,33, **thấp hơn** phân rã 0,50.
> Đã chốt bằng `test_lien_ket_cheo_KHONG_hieu_qua_hon_phan_ra`.

##### Hai chỗ khác nhau giữa hai chuẩn — nguồn lỗi câm

**Mã 270 mang nghĩa KHÁC HẲN.** Ở TT200 là "Tổng cộng tài sản"; ở TT99 là
"Tài sản dài hạn khác" (`270 = 271+272+273+274`). Tra nhầm bảng mã thì đọc
"Tài sản dài hạn khác" ra thành "Tổng tài sản" — có giá trị, hợp lệ hình
thức, không cảnh báo. Đây là lý do `standard` phải là tham số **bắt buộc**
của `extract_field_by_code()`.

**Dự phòng giảm giá hàng tồn kho đổi mã:** `149` ở TT200, `142` ở TT99.

##### Vẫn không đạt bộ tối thiểu

`minimal_localizing_set()` trả `None` ở **mọi** kịch bản, và `hang_ton_kho`
không định vị được ở kịch bản nào. Kết luận cho bài: ràng buộc kế toán đơn
thuần **không đủ**, và trọng số dồn sang mỏ neo đơn vị tính (proposal 6.3)
cùng bước đọc lại (6.2) — đúng như mục 6.1 đã lường trước.

### 3.5 PHÁT HIỆN NGOÀI DỰ KIẾN — `FORM_MARKERS` đang sai

Mục 3.2(a) đặt câu hỏi "ký hiệu mẫu biểu TT200 là `B01-DN` hay `B01a-DN`".
Văn bản trả lời: **cả hai**, và chữ `a` không hề là dấu hiệu của chuẩn.

Đếm trong Công báo 289+290 của TT200 thấy đủ `B01-DN`, `B01a-DN`, `B01b-DN`,
`B02-DN`, `B02a-DN`, `B02b-DN`, `B03-DN`, `B03a-DN`, `B03b-DN`. Nguyên văn
tại chỗ khai báo biểu mẫu:

> 7. Bảng cân đối kế toán **giữa niên độ (dạng đầy đủ)** — Mẫu số **B01a-DN**

Tức hậu tố phân biệt **kỳ báo cáo**, không phân biệt Thông tư:

| Ký hiệu | Nghĩa |
|---|---|
| `B01-DN` | Bảng cân đối kế toán **năm** |
| `B01a-DN` | **giữa niên độ, dạng đầy đủ** — tức báo cáo quý |
| `B01b-DN` | giữa niên độ, dạng tóm lược |

Và TT200 nói rõ biểu mẫu giữa niên độ dùng **cùng bộ mã số** với biểu mẫu
năm:

> (*) Nội dung các chỉ tiêu và mã số của báo cáo này như các chỉ tiêu của
> Báo cáo lưu chuyển tiền tệ năm - Mẫu B03-DN

Trong khi đó `src/fields_config.py` đang ghi ngược lại:

> "TT200 dùng `Mẫu số B 01 - DN`, TT99 dùng `Mẫu số B 01a - DN`."

**Hậu quả cụ thể.** Marker TT200 mang `(?!\s*a)` nên **không khớp** trang
`B01a-DN`. Mà `B01a-DN` chính là báo cáo **quý** theo TT200 — đúng loại tài
liệu dự án đang xử lý, kể cả báo cáo VNM Q1/2026 dùng làm mẫu. Khi marker
không khớp, `extract_field_by_code()` trả `None`, tức **đường dự phòng theo
mã số tắt hẳn** — im lặng, không cảnh báo. Đó đúng là đường sinh ra để cứu
khi OCR làm hỏng tên chỉ tiêu.

Chiều ngược lại: TT99 in `Mẫu số B03-DN` và `B09-DN` **không có** hậu tố `a`,
nên marker TT99 vốn đòi `a` cũng sẽ trượt.

**Điểm sáng:** `detect_standard()` không dùng `FORM_MARKERS` mà dùng
`STANDARD_MARKERS`, dựa vào tên báo cáo — và cái đó **đúng**, đã đối chiếu:
TT200 gọi "Bảng cân đối kế toán", TT99 gọi "Báo cáo tình hình tài chính".
Nên việc nhận diện CHUẨN không hỏng; chỉ việc nhận diện MẪU BIỂU hỏng.

Hệ quả thiết kế: vì chuẩn đã được `detect_standard()` xác định trước, và
`extract_field_by_code()` nhận `standard` làm tham số bắt buộc, `FORM_MARKERS`
**không cần phân biệt chuẩn chút nào** — nó chỉ cần phân biệt B01/B02/B03
trong phạm vi một chuẩn đã biết. Toàn bộ cơ chế `(?!\s*a)` đang giải một bài
toán mà chỗ khác đã giải rồi.

#### Nếu KHÔNG tìm thấy đẳng thức nối chéo nào

Đó cũng là một kết quả, và là kết quả phải báo cáo chứ không phải thất bại.
Nó xác nhận rằng ràng buộc kế toán **đơn thuần** không đủ để định vị lỗi
trên BCTC Việt Nam, và dồn trọng số của bài sang mỏ neo đơn vị tính (proposal
mục 6.3) cùng bước đọc lại (mục 6.2) — tức sang đúng đóng góp cốt lõi.
Proposal mục 6.1 đã lường trước dưới tên "chuẩn bị tinh thần cho kết quả bi
quan".

---

## 4. Làm xong thì làm gì tiếp

1. Sửa `src/fields_config.py` cho khớp văn bản — `FIELD_LINE_CODES`,
   `FIELD_IDENTITIES`, `FORM_MARKERS`, `STANDARD_MARKERS`.
2. Chạy `python src/constraints.py` để sinh lại
   `data/output/identifiability_TT200.md` và `identifiability_TT99.md`.
3. Chạy `python src/constraints_scenarios.py` với bộ đẳng thức thật để biết
   bộ trường nào đáng trả chi phí gán nhãn.
4. Chốt bộ trường → mở khoá B4.
5. Ghi quyết định và lý do vào mục "Sửa đổi" của `PREREGISTRATION.md` kèm
   ngày. **Không sửa đè lên nội dung gốc** — việc đăng ký trước mất hết giá
   trị nếu nội dung đăng ký thay đổi được mà không để lại dấu vết.
