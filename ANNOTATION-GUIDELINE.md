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
3. **Quy tắc đọc số** — phần dễ bất đồng nhất, đọc kỹ 3.1, 3.4, 3.6, 3.7
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
| Loại doanh nghiệp | **Phi tài chính** | Tổ chức tín dụng và chi nhánh ngân hàng nước ngoài theo chế độ kế toán riêng của Ngân hàng Nhà nước — mẫu biểu và mã số khác hẳn |
| Loại báo cáo | Báo cáo **riêng** hoặc **hợp nhất**, nhưng phải ghi rõ | Hai loại có số khác nhau trên cùng một doanh nghiệp cùng một kỳ. Không ghi rõ là trộn hai tổng thể |
| Biểu mẫu | B01, B02 **và B03** (mọi biến thể kỳ: không hậu tố, `a`, `b`) | **Sửa 25/08/2026:** bộ chỉ tiêu chuyển sang kịch bản E nên B03 nay CÓ gán nhãn — 6 chỉ tiêu. Xem mục Sửa đổi |
| Cột | **Cột kỳ báo cáo**, tức cột đầu | **Chốt 23/08/2026:** cột kỳ so sánh KHÔNG gán nhãn. Nó nhân đôi công mà không thêm một điểm nào cho trần định vị — lý do đầy đủ ở `PREREGISTRATION.md` mục Sửa đổi |

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
| Bản **scan** chất lượng thấp | Đo độ bền với chất lượng ảnh | Mở PDF, xem có phải ảnh nhúng không — **xem ghi chú ngay dưới bảng, cách nhận ra này đã hỏng** |
| Công ty **vốn hoá nhỏ, ít được nhắc** | Kiểm memorization | Không thuộc VN30 |

**Ghi chú 26/08/2026 — mọi báo cáo đều là ảnh quét, nên nhóm thứ ba như đang
viết không phân biệt được gì.** Đo trên 23 tài liệu của 20 doanh nghiệp niêm
yết: không tài liệu nào có lớp text thật; `pdftotext` lấy ra 44–734 byte cho
cả tài liệu 25–65 trang, và phần ít ỏi đó là chú thích chữ ký số. Chính
`VNM_2026Q1_TT99` cũng vậy. Trục thật sự đo được là **độ phân giải và độ sạch
của bản quét** — dải quan sát được trải từ ~100 dpi kèm trang lệch tới ~432
dpi. Việc sửa lời tiêu chí đang chờ người chủ trì quyết (`HANDOFF.md` mục 0,
Câu 10); tới lúc đó, đọc nhóm thứ ba theo nghĩa "bản quét độ phân giải thấp".

Danh mục tài liệu đã chọn nằm ở `data/nguon_gold.json`, tải bằng
`python src/tai_bctc.py`. Mỗi mục ghi rõ vai trò của tài liệu trong bốn nhóm
trên và những gì đã mở ra kiểm tận mắt.

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
- [ ] Ô trống, dấu gạch, và dòng vắng mặt đều ghi `0`; `null` **chỉ** dùng
      khi có dòng mà đọc không ra (mục 3.4)
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
