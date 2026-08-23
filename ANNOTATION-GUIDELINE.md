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
| Loại doanh nghiệp | **Phi tài chính** | Tổ chức tín dụng và chi nhánh ngân hàng nước ngoài theo chế độ kế toán riêng của Ngân hàng Nhà nước — mẫu biểu và mã số khác hẳn |
| Loại báo cáo | Báo cáo **riêng** hoặc **hợp nhất**, nhưng phải ghi rõ | Hai loại có số khác nhau trên cùng một doanh nghiệp cùng một kỳ. Không ghi rõ là trộn hai tổng thể |
| Biểu mẫu | B01 và B02 (mọi biến thể kỳ: không hậu tố, `a`, `b`) | **Chốt 23/08/2026:** B03 KHÔNG gán nhãn. Bộ chỉ tiêu chốt ở kịch bản D, không chạm B03 |
| Cột | **Cột kỳ báo cáo**, tức cột đầu | **Chốt 23/08/2026:** cột kỳ so sánh KHÔNG gán nhãn. Nó nhân đôi công mà không thêm một điểm nào cho trần định vị — lý do đầy đủ ở `PREREGISTRATION.md` mục Sửa đổi |

**Bộ chỉ tiêu: 21 với TT99, 20 với TT200.** Danh sách chính thức là
`FIELD_MAP` trong `src/fields_config.py`; đừng chép lại vào đây kẻo hai bản
lệch nhau. Chênh lệch một chỉ tiêu là do **Tài sản sinh học ngắn hạn** chỉ
tồn tại ở TT99.

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

### 3.3 Số âm

Báo cáo tài chính in số âm **trong ngoặc đơn**: `(1.234.567)`. Ghi giá trị âm:
`-1234567`.

Một số báo cáo dùng dấu trừ. Cả hai đều là số âm, ghi như nhau.

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
| Tiêu đề `Báo cáo tình hình tài chính` | TT99 |
| Tiêu đề `Bảng cân đối kế toán` | TT200 |
| Ký hiệu mẫu `B 01a - DN` | TT99 |
| Có trích dẫn `99/2025/TT-BTC` | TT99 |
| Có trích dẫn `200/2014/TT-BTC` | TT200 |

**Không đủ dấu hiệu, hoặc thấy dấu hiệu của cả hai:** ghi `standard` là
`"UNKNOWN"` và mô tả trong `notes`. **Đừng đoán.** Nhận diện sai chuẩn là
một chế độ lỗi riêng cần đo được, và một nhãn đoán bừa sẽ được tính thành
lỗi của model.

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

---

## 6. Trần người — 10 tài liệu

Không có số này thì không diễn giải được kết quả hệ thống: 83% là gần trần
hay còn xa?

**Quy trình:**

1. Gán nhãn 10 tài liệu dưới **áp lực thời gian thực tế** — đặt đồng hồ **15
   phút một tài liệu**, hết giờ thì dừng, không làm tỉ mỉ vô hạn.
2. So với bản gold **đã phân xử kỹ** (chính là 20 tài liệu ở mục 5).
3. Báo cáo độ chính xác mức trường **và** mức tài liệu.

**Cách đọc kết quả:**

| Trần người | Hệ thống 83% nghĩa là |
|---|---|
| ~97% | Còn khoảng cách lớn, có chỗ để cải thiện |
| ~88% | Gần trần, và câu chuyện đổi hẳn: tác vụ này **bản thân nó khó** |

Trường hợp thứ hai là kết quả có giá trị hơn, và nó chỉ nhìn thấy được nếu
đã đo.

Ghi lại **thời gian thật** từng tài liệu, không chỉ ghi có kịp 15 phút hay
không. Tham chiếu để đối chiếu: tài liệu kinh tế học lịch sử cho biết người
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
| Bản **scan** chất lượng thấp | Đo độ bền với chất lượng ảnh | Mở PDF, xem có phải ảnh nhúng không |
| Công ty **vốn hoá nhỏ, ít được nhắc** | Kiểm memorization | Không thuộc VN30 |

Nhóm cuối quan trọng và hay bị quên: VLM nhiều khả năng đã thấy số liệu
blue-chip trong pretraining. Nếu kết quả trên blue-chip cao hơn hẳn
small-cap thì đó là bằng chứng rò rỉ dữ liệu và **phải báo cáo riêng**.

---

## 8. Danh mục kiểm trước khi coi một tài liệu là xong

- [ ] Chưa từng mở đầu ra pipeline của tài liệu này (Luật 1)
- [ ] Đã xác định chuẩn mẫu biểu, hoặc ghi `UNKNOWN` kèm lý do
- [ ] `unit_declared` chép **nguyên văn**; `unit_multiplier` khớp
- [ ] Mọi giá trị đã quy đổi về **đồng**
- [ ] Số âm ghi bằng dấu trừ, không phải ngoặc
- [ ] Ô trống là `null`, khác với `0` in rõ
- [ ] Đã đối chiếu **mã số**, không chỉ tên chỉ tiêu
- [ ] Đã kiểm riêng các cặp dễ nhầm ở mục 3.6
- [ ] Không sửa số cho cân đẳng thức; lệch đáng kể thì ghi `notes`
- [ ] `source_url`, `downloaded_at`, `annotator`, `annotated_at` đều có
- [ ] File đặt đúng `data/gold/<doc_id>.json`

---

## Sửa đổi

> Mọi thay đổi guideline ghi vào đây kèm **ngày** và **lý do**, và ghi rõ
> **những tài liệu nào phải gán nhãn lại**. Không sửa đè lên nội dung trên.

*(chưa có sửa đổi nào)*
