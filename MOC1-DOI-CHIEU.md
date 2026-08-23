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

## 3. Bảng đối chiếu — cần xác nhận từng dòng

### 3.1 Mã số dòng đang dùng trong code

Nguồn: `src/fields_config.py`, `FIELD_LINE_CODES`.

| Chỉ tiêu | TT200 | TT99 | Đã xác nhận? |
|---|---|---|---|
| `tai_san_ngan_han` | B01 · 100 | B01a · 100 | ☐ |
| `hang_ton_kho` | B01 · 140 | B01a · 140 | ☐ |
| `tai_san_dai_han` | B01 · 200 | B01a · 200 | ☐ |
| `tong_tai_san` | B01 · **270** | B01a · **280** | ☐ ← chỗ đã biết là khác nhau |
| `no_phai_tra` | B01 · 300 | B01a · 300 | ☐ |
| `von_chu_so_huu` | B01 · 400 | B01a · 400 | ☐ |
| `doanh_thu_thuan` | B02 · 10 | B02a · 10 | ☐ |
| `gia_von_hang_ban` | B02 · 11 | B02a · 11 | ☐ |
| `loi_nhuan_gop` | B02 · 20 | B02a · 20 | ☐ |
| `loi_nhuan_truoc_thue` | B02 · 50 | B02a · 50 | ☐ |
| `loi_nhuan_sau_thue` | B02 · 60 | B02a · 60 | ☐ |

### 3.2 Hai chỗ CHƯA xác nhận, đã biết là rủi ro

**(a) Ký hiệu mẫu biểu của TT200 là `B01-DN` hay `B01a-DN`?**

`FORM_MARKERS` trong `fields_config.py` đang giả định TT200 dùng `B 01` không
có hậu tố `a`, và TT99 dùng `B 01a`. Regex của TT200 mang `(?!s*a)` chính vì
chuỗi `"B 01"` nằm gọn trong `"B 01a"` — không có phần đó thì marker TT200 sẽ
khớp luôn trang TT99. Nếu giả định này sai thì **nhận diện chuẩn sai ở mọi tài
liệu**, và đó là một chế độ lỗi nằm ngay đầu chuỗi xử lý.

**(b) Bộ đẳng thức của TT99 hiện đang DÙNG CHUNG với TT200.**

`FIELD_IDENTITIES` khai báo TT99 với đúng ba đẳng thức giống hệt TT200. Chưa
ai đối chiếu xem TT99 có giữ nguyên quan hệ đó không. Đây là giả định nặng
nhất trong cả file, vì toàn bộ trục nghiên cứu "TT200 → TT99" dựa vào việc
hai chuẩn **khác nhau** — mà hiện code đang mô tả chúng là giống hệt.

### 3.3 Đẳng thức đang mã hoá

Cả hai chuẩn hiện dùng chung ba đẳng thức này:

| # | Đẳng thức | Xác nhận TT200 | Xác nhận TT99 |
|---|---|---|---|
| 1 | `tai_san_ngan_han + tai_san_dai_han = tong_tai_san` | ☐ | ☐ |
| 2 | `no_phai_tra + von_chu_so_huu = tong_tai_san` | ☐ | ☐ |
| 3 | `gia_von_hang_ban + loi_nhuan_gop = doanh_thu_thuan` | ☐ | ☐ |

Đẳng thức 2 đáng ngờ về mặt kết cấu: biểu mẫu in **Tổng cộng nguồn vốn** như
một chỉ tiêu riêng, nên quan hệ thật nhiều khả năng là hai bước —
`nợ + vốn = tổng nguồn vốn` rồi `tổng nguồn vốn = tổng tài sản`. Gộp lại làm
một là mất một đẳng thức và mất một số đọc được từ trang giấy. Đó chính là
kịch bản B ở mục 1.

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
| + phân rã TSNH (**chưa xác nhận**) | 21 | 6 | **5/21** |

Lý do: liên kết chéo gắn đẳng thức thứ hai vào `B01.110`, nhưng `B01.110`
phải **đã nằm trong một đẳng thức nào đó** thì mới có cái để gắn thêm. Đẳng
thức đó là phân rã Tài sản ngắn hạn — nằm ở Điều 112, tức **Công báo 287 +
288 mà ta chưa có**.

#### CÒN THIẾU — cần tải thêm

| Chuẩn | Cần | Nội dung | Đã có? |
|---|---|---|---|
| TT200 | Công báo **287 + 288** | Điều 112 (Bảng cân đối kế toán) + Điều 113 (B02) | ☐ |
| TT200 | Công báo 289 + 290 | Điều 114 (B03) trở đi | ✅ |
| TT99 | Công báo **1577 + 1578** và/hoặc **1579 + 1580** | Báo cáo tình hình tài chính + đầu B02a | ☐ |
| TT99 | Công báo 1581 + 1582 | Cuối B02a + B03 | ✅ |

TT200 có 6 số (279+280 → 289+290); TT99 có 10 số (1563+1564 → 1581+1582). Cả
hai file đang có đều là **số cuối cùng**, nên phần bảng cân đối nằm ở các số
trước đó.

Cách kiểm nhanh sau khi tải: tìm chuỗi `Mã số 270 =` (TT200) hoặc
`Mã số 280 =` (TT99). Có kết quả là đúng file.

#### Bảng để điền tiếp

| Biểu mẫu | Đẳng thức theo văn bản | Chuẩn | Trùng chỉ tiêu với đẳng thức nào khác? |
|---|---|---|---|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

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

**Hậu quả cụ thể.** Marker TT200 mang `(?!s*a)` nên **không khớp** trang
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
trong phạm vi một chuẩn đã biết. Toàn bộ cơ chế `(?!s*a)` đang giải một bài
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
