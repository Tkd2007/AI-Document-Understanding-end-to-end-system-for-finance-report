# MỐC 1 — bảng đối chiếu ma trận ràng buộc với Thông tư

Tài liệu này để **người chủ trì** làm, không phải AI. BUILD-SPEC mục 0.5 nêu
lý do: sai một dấu trong ma trận ràng buộc thì toàn bộ kết quả identifiability
sai mà **không có gì báo** — code vẫn chạy, số vẫn ra, chỉ là sai.

Mốc này chặn B4, mà B4 quyết định chi phí gán nhãn tay cho 60 tài liệu gold —
khoản đắt nhất của cả dự án.

---

## 1. Câu hỏi thật của Mốc 1 đã đổi

Kế hoạch ban đầu hỏi "chốt bộ trường nào". Kết quả đo được cho thấy câu hỏi
đó đặt sai chỗ.

Chạy `python src/constraints_scenarios.py` cho bảng sau. Mỗi kịch bản là kịch
bản trước cộng thêm một **nhóm** đẳng thức, nên đọc được đóng góp riêng của
từng nhóm:

| KB | Kịch bản | Chỉ tiêu | Đẳng thức | rank | dim null | Định vị được | Bộ tối thiểu |
|---|---|---:|---:|---:|---:|---:|---|
| A | Hiện tại | 11 | 3 | 3 | 8 | 1/11 (9%) | None |
| B | + Tổng nguồn vốn | 12 | 4 | 4 | 8 | 2/12 (17%) | None |
| C | + chuỗi lãi lỗ trên B02 | 15 | 6 | 6 | 9 | 3/15 (20%) | None |
| D | + phân rã Tài sản ngắn hạn | 19 | 7 | 7 | 12 | 5/19 (26%) | None |
| E | **+ liên kết chéo B01/B02/B03** | 26 | 11 | 11 | 15 | **13/26 (50%)** | None |

Đọc bảng này theo hai hướng.

**Hướng thứ nhất — thêm chỉ tiêu cùng loại gần như vô ích.** Từ A sang D, số
chỉ tiêu tăng gần gấp đôi (11 → 19) nhưng tỷ lệ định vị được chỉ nhích từ 9%
lên 26%. Mỗi chỉ tiêu thêm vào là chi phí gán nhãn nhân với 60 tài liệu, nên
đây là cái giá đắt cho một khoản lợi nhỏ.

**Hướng thứ hai — liên kết chéo mới là thứ đáng mua.** Riêng bước D → E đẩy
tỷ lệ từ 26% lên 50%, gấp đôi, và nó là bước duy nhất làm được vậy.

### Vì sao, phát biểu thành một định luật

> Một chỉ tiêu định vị được **khi và chỉ khi** cột của nó trong ma trận `A`
> khác 0 và không tỷ lệ với cột nào khác. Tức là: tập đẳng thức chứa nó phải
> khác tập đẳng thức của **mọi** chỉ tiêu còn lại.

Hệ quả, và đây là chỗ quyết định:

- Trong một đẳng thức phân rã đơn lẻ `a + b = tổng`, **cả ba** chỉ tiêu đều
  nằm ngoài tầm. `a` và `b` có cột bằng nhau; `tổng` có cột `[−1]` tỷ lệ với
  cột `[1]`, nên lỗi `+δ` ở `a` và lỗi `−δ` ở `tổng` cho residual giống hệt
  nhau.
- Thêm bao nhiêu **chỉ tiêu anh em** cũng không phá được chuyện đó, vì mỗi
  chỉ tiêu mới lại chỉ nằm trong đúng một đẳng thức.
- Chỉ khi một chỉ tiêu xuất hiện trong **hai đẳng thức khác nhau** thì cột
  của nó mới tách ra. Trong biểu mẫu BCTC, thứ làm được điều đó là **liên kết
  chéo giữa các biểu mẫu**.

Định luật này đã chốt bằng test — xem `tests/test_constraints_scenarios.py`.

### Vậy phải tìm gì trong Phụ lục IV

**Không phải "còn chỉ tiêu nào". Mà là: còn con số nào xuất hiện ở HAI CHỖ.**

Ba ứng viên tôi dựng lại được từ kết cấu biểu mẫu, **chưa đối chiếu văn bản**:

| Liên kết chéo | Nối gì | Cần xác nhận |
|---|---|---|
| Tiền cuối kỳ trên **B03** = Tiền và tương đương tiền trên **B01** | B03 ↔ B01 | Mã số của cả hai ở từng chuẩn |
| Lợi nhuận chưa phân phối trên **B01** = LNCPP đầu kỳ + LNST trên **B02** − cổ tức | B01 ↔ B02 | Có mã số riêng cho LNCPP không, và cổ tức lấy ở đâu |
| **Cột kỳ trước** cùng thoả một hệ đẳng thức | Trong cùng B01 | Proposal mục 6.1(d) hỏi nó làm hạng tăng bao nhiêu — chưa đo |

Nếu Phụ lục IV **không** khai báo tường minh những liên kết này, đó cũng là
một kết quả: nó xác nhận rằng ràng buộc kế toán đơn thuần không đủ, và trọng
số của bài dồn sang mỏ neo đơn vị tính (mục 6.3) và bước đọc lại (mục 6.2) —
đúng như proposal mục 6.1 đã lường trước dưới tên "chuẩn bị tinh thần cho kết
quả bi quan".

### Một chỉ tiêu vẫn nằm ngoài tầm ở MỌI kịch bản

`hang_ton_kho` không định vị được ở A, B, C, D, lẫn E. Nó là chỉ tiêu lá, luôn
đứng cùng các anh em trong đúng một đẳng thức.

Đáng chú ý vì đó **đúng là chỉ tiêu đã có lỗi đọc thật** trên báo cáo VNM —
alias "Hàng tồn kho" khớp trúng dòng "Dự phòng giảm giá hàng tồn kho" (mã 142)
và cho ra một giá trị nhỏ hơn giá trị thật khoảng nghìn lần nhưng hợp lệ về
hình thức. Ràng buộc kế toán **chứng minh được là không bao giờ bắt được lỗi
đó**. Chỉ mỏ neo đơn vị tính và việc đọc lại crop mới bắt được.

Đây là một ví dụ cụ thể, có thật, để đưa vào bài.

---

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
có hậu tố `a`, và TT99 dùng `B 01a`. Regex của TT200 mang `(?!\s*a)` chính vì
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

> Ghi lại **mọi** dòng dạng `Mã số X = Mã số Y ± Mã số Z` tìm được, kể cả
> những dòng chứa chỉ tiêu hiện chưa trích. Chưa cần quyết có đưa vào bộ
> trường hay không — cứ ghi ra trước, rồi chạy `constraints_scenarios.py`
> với bộ mới để xem nó mua được bao nhiêu, rồi mới quyết.

| Biểu mẫu | Đẳng thức theo văn bản | Chuẩn | Có phải liên kết chéo? |
|---|---|---|---|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

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
