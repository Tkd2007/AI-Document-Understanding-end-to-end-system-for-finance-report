# Bàn giao — hạ tầng nghiên cứu ViFinKIE

Viết để một phiên Claude khác đọc và làm tiếp mà **không cần hỏi lại gì**.
Mọi tham chiếu đều là đường dẫn file hoặc commit hash.

- **Nhánh:** `research` (tách từ `main` tại `4216291`)
- **Commit gần nhất:** `e08d5e8`
- **Test:** **334 xanh / 0 đỏ**. `ruff check src tests` sạch.
- **Đã push hết.**
- **Cập nhật:** 23/08/2026

---

## 1. Đọc gì trước

Bốn tài liệu nguồn do người dùng giữ, **không** nằm trong repo:
`FINAL-proposal-reread-dont-repair.md` (proposal, bốn giả thuyết H0–H3),
`ADDENDUM-statistical-treatment.md` (vá phần thống kê),
`FINAL-repo-changes.md` (dịch proposal sang việc trong repo),
`BUILD-SPEC.md` (**đặc tả thi công** — thứ đang được thực hiện).

Trong repo, đọc theo thứ tự:

1. [PREREGISTRATION.md](PREREGISTRATION.md) — bốn giả thuyết, chỉ số chốt
   trước, điều kiện phản chứng, ba mốc dừng. **Không sửa đè lên nội dung
   gốc**; mọi thay đổi ghi vào mục "Sửa đổi" ở cuối kèm ngày và lý do, nếu
   không thì việc đăng ký trước mất hết giá trị. Mục đó đã có một mục ngày
   22/08/2026 — đọc nó, vì nó chốt một hạn chế thật của phương pháp.
2. [data/output/identifiability_TT99.md](data/output/identifiability_TT99.md)
   — kết quả Mốc 1. Đọc mục 3 dưới đây trước khi đi tiếp.
3. [src/eval/stats.py](src/eval/stats.py) — docstring đầu module, nguyên tắc
   chi phối toàn bộ phần thống kê.
4. [src/repair/diagnose.py](src/repair/diagnose.py) — docstring đầu module
   và các hằng số đầu file. Đây là chỗ tập trung nhiều quyết định thiết kế
   nhất, mỗi cái đều có lý do viết kèm.

**File này đã commit** (`fa399e4`) và được cập nhật tiếp sau đó.

---

## 2. Bối cảnh

Repo gốc là pipeline **trích xuất** 11 chỉ tiêu tài chính từ PDF báo cáo
tài chính Việt Nam: PDF → DocLayout-YOLO cắt vùng bảng → EasyOCR hoặc VLM
(Gemma qua OpenRouter) → validation → FastAPI.

Việc đang làm là biến nó thành hạ tầng **nghiên cứu**. Đóng góp cốt lõi nằm
ở H3, gói trong một câu:

> Mọi paradigm sửa lỗi trước đây (Fellegi-Holt, data reconciliation,
> HoloClean) đều SỬA một tập số cố định. Không cái nào ĐỌC LẠI được nguồn.
> Với tài liệu thì ảnh gốc vẫn còn.

Hệ quả chi phối mọi quyết định kỹ thuật: **tập ứng viên sửa lỗi phải ĐÓNG và
mọi phần tử phải truy được về một chỗ cụ thể trên tài liệu.** Nếu tồn tại
đường nào để một con số ngoài tập ứng viên lọt vào kết quả thì hệ ép số
được, và toàn bộ lập luận chống bịa sụp.

---

## 3. Đã làm — 14 commit trên `research`

| Commit | Mục | Nội dung |
|---|---|---|
| `689e2d0` | D1 | `PREREGISTRATION.md` — đăng ký trước, dấu thời gian git là bằng chứng |
| `4b20aea` | A1 | Điều kiện áp dụng cho `FIELD_RELATIONS` |
| `7fd34f0` | A3 | Tách mã số dòng và mẫu biểu theo TT200 / TT99 |
| `437e2a1` | A4 | Chuẩn hoá đơn vị tính + mỏ neo biên độ lớn |
| `88c031e` | A2 | `src/constraints.py` — ma trận ràng buộc và identifiability |
| `c85c812` | B1 | Cờ `DISABLE_CONSTRAINT_GATE` để đo H1 không vòng lặp luận chứng |
| `a5ec83e` | B2 | Confidence từng trường bằng self-consistency |
| `0d74195` | B3 | Provenance từng trường qua suốt chuỗi |
| `ad6684a` | B6 | Eval harness, thống kê, trường tái lập |
| `2cf613a` | C1 | Sinh tập ứng viên sửa lỗi từ tài liệu |
| `ff79991` | C2 | WIP — 2 test đỏ *(đã sửa ở `f1d236e`)* |
| **`f1d236e`** | **C2** | **Hai baseline đối chứng không còn thua vì lý do cài đặt** — mục 4 |
| **`1dacb34`** | **B5** | **Tầng đánh giá XBRL** — mục 5 |
| **`9c3f7c9`** | **C2** | **Trần `max_changes`, tách ABSTAIN theo lý do** — mục 6 |
| `895b731` | F | Tách `requirements-dev.txt`; **sửa CI đang hỏng** — mục 6b |
| `66296a6` | F | `MAX_UPLOAD_BYTES` đọc theo khối; `save=False` cho đường API |
| `3abc812` | F | Early-stop ở vòng vùng; `DISABLE_EARLY_STOP` + `meta["early_stop"]` |
| `100afb9` | F | Histogram latency, tự chia bucket |
| **`a3a5ea7`** | **F** | **Đo engine OCR trên ô số — quyết định GIỮ EasyOCR**, mục 6c |
| `2015e8c` | — | README khớp lại hiện trạng |
| **`1d3f89d`** | **Mốc 1** | **`constraints_scenarios.py` + `MOC1-DOI-CHIEU.md`** — mục 7 |
| `9724504` | — | `ANNOTATION-GUIDELINE.md` — guideline gán nhãn |
| `2c14420` | — | dry-run của `fetch.py` kiểm `SEC_USER_AGENT` |
| `3fb6472` `b53ed8f` | Mốc 1 | **Trích đẳng thức từ Công báo** — mục 7b |
| **`023321c`** | A3 | **Sửa `FORM_MARKERS`: hậu tố a/b là KỲ, không phải Thông tư** — mục 7b |

Ba commit `f1d236e`, `1dacb34`, `9c3f7c9` là việc ngày 22/08/2026; sáu
commit cuối là việc ngày 23/08/2026. Ngoài ra `main` có `debac2f` (test
khoá threading cho `merge_into_totals`) từ trước loạt này.

**Phần F đã XONG hết.** Chi tiết ở mục 6b và 6c.

### Cái bẫy đã gặp ở các mục cũ

**A1.** Ba trong sáu quan hệ `FIELD_RELATIONS` ngầm giả định doanh nghiệp có
lãi và VCSH dương, mâu thuẫn với `FIELD_RULES` vốn cho phép âm. Mâu thuẫn
không nằm yên: `FIELD_RELATIONS` là một phần cổng `is_acceptable()`, nên gặp
báo cáo lỗ thì router coi kết quả **đúng** là chưa đạt, gọi VLM, và
`has_warnings` mở đường cho VLM ghi đè lên số vốn đã đúng. *Đánh đổi đã
biết:* điều kiện áp dụng đọc từ một field cũng do model trích ra, nên field
điều kiện bị đọc sai thành âm sẽ làm luật tự tắt —
`test_field_dieu_kien_bi_doc_sai_thi_luat_tu_tat` chốt hành vi đó.

**A3.** `detect_standard()` trả `None` khi không đủ dấu hiệu hoặc khi trang
nhắc cả hai chuẩn — **không bao giờ đoán bừa**, vì nhận diện sai chuẩn là
một chế độ lỗi riêng cần đo được. Dấu hiệu nó dùng là TÊN báo cáo, và tên đó
đã đối chiếu văn bản, đúng.

> **Phần suy luận về ký hiệu mẫu biểu ở mục này ĐÃ BỊ BÁC BỎ.** Bản trước
> lập luận rằng chuỗi `"B 01"` nằm trong `"B 01a"` nên marker TT200 phải
> mang `(?!\s*a)` để không khớp trang TT99. Đối chiếu Công báo cho thấy tiền
> đề sai: hậu tố `a`/`b` phân biệt KỲ BÁO CÁO chứ không phân biệt Thông tư.
> Đã sửa ở `023321c` — xem mục 7b.

**A4.** Mỏ neo tuyệt đối duy nhất phá được bất biến scale. Hệ ràng buộc
thuần nhất nên `Aδ = (c−1)Ax* = 0`: sai đơn vị toàn cục **luôn** vô hình với
mọi đẳng thức. `TOTAL_ASSETS_BOUNDS` là check duy nhất trong
`validate_result` không bất biến với phép nhân vô hướng. `don_vi_tinh` cố ý
**không** nằm trong `FIELD_MAP` vì `validate_result` chạy `coerce_number`
trên mọi khoá của nó.

**B1.** Pipeline dùng chính đẳng thức kế toán làm cổng quyết định fallback,
nên đo AUROC của vi phạm ràng buộc trên đầu ra đó là vòng lặp luận chứng.
Lượt chạy ở chế độ đo được đánh dấu bằng khoá `constraint_gate: false`
trong `metrics.jsonl`.

**B2.** Ba quyết định trong cách tính phiếu, cả ba đều có thể sai theo hướng
lạc quan: `None` cũng là ứng viên bỏ phiếu; mẫu số là `n_samples` chứ không
phải số mẫu parse được; hoà phiếu thì ưu tiên non-null rồi tới giá trị xuất
hiện sớm nhất. `n_samples > 1` với `temperature = 0` **ném lỗi**.

**B3.** Chuỗi từng đứt ở ba chỗ. Lọc IoU đi kèm chứ không phải việc rời:
YOLO trả box chồng nhau (quan sát ở trang 31 và 35 báo cáo VNM), và kể từ
khi có provenance thì đó là **sai dữ liệu** chứ không còn là lãng phí.
`bbox` trả về là bbox **đã cộng padding và đã clamp**, có test cắt lại rồi
so từng byte.

**B6.** Bootstrap **theo cụm tài liệu**, không theo trường; có test chứng
minh việc phân cụm nới khoảng tin cậy hơn gấp đôi trên dữ liệu phân cụm.
`item_bootstrap_ci` (cách SAI) giữ lại có chủ đích để paper nêu định lượng
khoảng tin cậy sẽ hẹp giả tạo bao nhiêu. **Không dùng DeLong** — lý do ở
`PREREGISTRATION.md` mục 1 và docstring `src/eval/stats.py`. McNemar dùng
kiểm định nhị thức **chính xác** nên phần đó không cần scipy.

**C1.** Năm nguồn ứng viên. `cost = −log(xác suất tiên nghiệm)` để cộng cost
tương đương nhân xác suất. **Bốn xác suất trong `XAC_SUAT_TIEN_NGHIEM` chưa
đo trên dữ liệu thật** — xem mục 7.

---

## 4. C2 — đã xong, hai test đỏ sửa thế nào

File [src/repair/diagnose.py](src/repair/diagnose.py), test
[tests/test_diagnose.py](tests/test_diagnose.py) (31 test, tất cả xanh).

### Test đỏ 1 — baseline 8 trả nghiệm không thưa

IRLS xuất phát từ trọng số đều nên vòng đầu ra đúng nghiệm bình phương tối
thiểu. Với hệ đối xứng như `a + b = c` thì nghiệm đó lại đều (δ = 5/3 ở cả
ba toạ độ), nên trọng số vòng sau vẫn đều và thuật toán kẹt ở **điểm bất
động thật sự** — không lịch giảm epsilon nào thoát ra được, vì không có bất
đối xứng nào để bám vào. Thêm nữa, trên chính ví dụ đó nghiệm rải đều
**cũng** có chuẩn L1 bằng 5: cực tiểu L1 suy biến, và thứ test thật sự đòi
là nghiệm **đỉnh**.

Đã thay bằng `scipy.optimize.linprog` (HiGHS), tách `delta = u − v` với
`u, v ≥ 0` rồi tối thiểu hoá `Σ(u + v)`. Nghiệm LP là nghiệm đỉnh nên số
toạ độ khác 0 không vượt quá `rank(A)`. Lợi ích ngoài việc test xanh:
baseline 8 hết là nghiệm xấp xỉ, bỏ được caveat "đây chỉ là nghiệm xấp xỉ"
trong paper — baseline mạnh hơn thì kết luận về phương pháp đề xuất đáng tin
hơn. Chuyện `scipy` trong `requirements.txt`: xem mục 8, chỗ lệch số 6.

### Test đỏ 2 — baseline 9 chọn trường theo thứ tự chỉ số

Bản bàn giao trước kết luận "kỳ vọng trong test SAI, code ĐÚNG". Đúng một
nửa, và nửa còn lại quan trọng.

Đúng ở chỗ: với `a + b = c` thì sửa riêng `a`, `b` hay `c` đều đủ, nên ba
tập trường hoà nhau về cardinality.

Nhưng `diagnose()` duyệt **hết** mọi tổ hợp ở một cardinality rồi mới chọn
theo hàm mục tiêu, còn `diagnose_fellegi_holt_donor()` trả về tổ hợp **đầu
tiên** theo thứ tự chỉ số rồi thoát — trong khi docstring của chính nó
khẳng định "Giống hệt `diagnose()` ở việc chọn TRƯỜNG nào sửa". Tức baseline
trung tâm của cả nghiên cứu đang thắng thua theo thứ tự khai báo field
trong `fields_config`.

Đã sửa: donor cũng duyệt hết một cardinality rồi phân xử bằng **tổng khoảng
cách tới donor**. Trường không có giá trị donor thì lấy chính giá trị hiện
tại làm mốc, nên khoảng cách của nó đo đúng phần phải bịa ra khi không ai
đỡ. Certificate ghi thêm `lech_so_voi_donor` cho từng trường bị sửa.

Ba test mới chốt lại: L1 trên hệ hai đẳng thức lồng nhau phải có
`n_changed ≤ rank(A)` (hệ một đẳng thức có hạng 1 nên mọi nghiệm đều thưa
sẵn, không phân biệt được hai bộ giải); donor chọn `b` chứ không chọn `a` dù
`a` đứng trước và cũng khả thi; và ca không trường đơn lẻ nào gánh nổi
residual với sáu cặp cùng thoả, donor biết đúng `a` và `d` nên cặp `{a, d}`
phải thắng và nó khôi phục đúng giá trị thật.

---

## 5. B5 — tầng đánh giá XBRL, đã dựng xong

Module [src/eval/xbrl_tier/](src/eval/xbrl_tier/) — sáu file. Test
[tests/test_xbrl_tier.py](tests/test_xbrl_tier.py), 35 test, không cái nào
chạm mạng.

**Vì sao tồn tại:** tập gold 60 tài liệu cho khoảng 1500 trường, nhưng H2 và
H3 đo trên **SỐ LỖI**. Tỷ lệ lỗi 5–15% chỉ cho 75–225 lỗi, mà 75 quan sát
cho khoảng tin cậy rộng chừng ±0,11 — đủ để nói "phương pháp này chạy
được", không đủ để nói "hơn baseline 5 điểm". Nên đây là **điều kiện để H2
và H3 có power**, không phải mục làm thêm. Phân vai: **XBRL lo power, gold
Việt Nam lo validity.**

| File | Việc | Quyết định cần biết |
|---|---|---|
| `linkbase.py` | `*_cal.xml` → đẳng thức, → ma trận A | Parse thẳng bằng `xml.etree`, **không dùng `arelle`** |
| `facts.py` | companyfacts → bảng giá trị | **Chỉ lấy fact CÙNG MỘT hồ sơ** — (a) dưới đây |
| `table.py` | Bảng hai cột kỳ | Lỗi lệch dòng/cột định nghĩa bằng hình học trang |
| `render.py` | Bảng → ảnh + bbox từng ô | Vẽ thẳng bằng Pillow, ném lỗi khi font thiếu glyph — (c) |
| `inject.py` | Inject lỗi theo taxonomy mục 3.1 proposal | Bảng nhầm chữ số **RỘNG HƠN** `repair.candidates` — (b) |
| `fetch.py` | Tải hồ sơ từ EDGAR | **SCRIPT CHO NGƯỜI DÙNG CHẠY**, container không có mạng tới sec.gov |

### Ba chỗ dễ làm hỏng nếu không biết lý do

**(a) `facts.py` chỉ lấy fact của cùng một hồ sơ.** companyfacts gộp mọi lần
công bố, nên cùng một ngày kết thúc kỳ có thể có nhiều giá trị — bản gốc và
các bản trình bày lại ở hồ sơ sau. Trộn hai hồ sơ vào một bảng sẽ **phá vỡ
đẳng thức kế toán một cách âm thầm**, và khi đó tầng này mất đúng thứ duy
nhất làm nên giá trị của nó là ground truth chắc chắn đúng; bảng không cân
sẽ bị đếm thành "lỗi trích xuất" trong khi thật ra là lỗi dựng dữ liệu.
`test_chi_lay_fact_cua_dung_mot_ho_so` chốt chuyện này.

**(b) `inject.py` KHÔNG dùng chung bảng nhầm chữ số với
`repair.candidates`.** Dùng chung thì mọi lỗi inject đều nằm sẵn trong tập
ứng viên theo đúng cấu trúc, và phương pháp đề xuất thắng vì thí nghiệm được
dựng cho nó thắng — loại lỗi reviewer giết bài ngay. Nên `inject` thay một
chữ số bằng **bất kỳ chữ số nào khác**, còn `repair.candidates` chỉ sinh bốn
cặp hay nhầm `(0,8) (1,7) (3,8) (5,6)`. Phần lỗi rơi ra ngoài tập ứng viên
là phần phương pháp **phải chịu thua**, và tỷ lệ đó tự nó đáng báo cáo.
**Đừng "thống nhất" hai bảng này lại.**

**(c) `render.py` ném lỗi khi font thiếu glyph.** Font đi kèm Pillow không
có glyph tiếng Việt có dấu: "Đơn vị tính" render ra "□n v□ t□nh" mà ảnh vẫn
trông như một cái bảng bình thường — lỗi im lặng đúng nghĩa, chỉ lộ ra khi
có người mở ảnh xem, thường là sau khi đã chạy xong cả lượt thí nghiệm. Nên
chữ cố định trên ảnh mặc định **tiếng Anh** (`Indicator`, `Unit: …`), ô
trống dùng gạch nối ASCII `-` chứ không dùng `—` (cũng không có glyph), và
`render()` kiểm mọi ký tự sắp vẽ rồi **ném `ValueError`**. Muốn nhãn tiếng
Việt — thứ ablation "Transfer XBRL → BCTC Việt Nam" cần — thì truyền
`font_path`, `tieu_de_cot_chi_tieu` và `mau_dong_don_vi`.

### Kết quả chạy thử toàn chuỗi

Chuỗi `linkbase → bảng → inject → sinh ứng viên → chẩn đoán` đã chạy thông
đầu-cuối trên bảng 8 chỉ tiêu, 3 đẳng thức:

1. Inject `DIGIT_SUB` vào `Cash` (`812.445.000 → 892.445.000`, chữ số
   `1 → 9`) làm đúng **1 đẳng thức** vi phạm, khớp bảng identifiability.
2. Giá trị thật **không** nằm trong tập ứng viên vì cặp `1→9` không thuộc
   bốn cặp hay nhầm. `diagnose()` trả `ABSTAIN` — **thua đúng**, cơ chế ở
   (b) hoạt động như thiết kế.
3. Baseline 9 trả `REPAIRED` nhưng **sửa sai trường** — nó sửa `Receivables`
   bằng giá trị donor, cho ra bảng cân đối hoàn hảo và sai sự thật. Đúng thứ
   `fabrication_rate` trong `src/eval/metrics.py` sinh ra để bắt.

Sau `inject_scale_toan_cuc` với `k = 3`, **mọi đẳng thức vẫn thoả tuyệt
đối** — bản chạy được của chứng minh một dòng ở `constraints.py`.

---

## 6. Trần `max_changes` và tách ABSTAIN — `9c3f7c9`

Trong lúc chạy thử B5, `diagnose()` **hết 30 giây** trên bài toán chỉ có 8
chỉ tiêu và 87 ứng viên. Đo lại có kiểm soát:

| Ca | `max_changes` | Kết quả | Thời gian |
|---|---|---|---|
| Lỗi KHÔNG sửa được | không đặt | ABSTAIN vì **hết giờ** | **30.158 ms** |
| Lỗi KHÔNG sửa được | 2 | ABSTAIN vì **vô nghiệm** | **16 ms** |
| Lỗi sửa được (đổi dấu) | không đặt | REPAIRED, đúng `Cash` | 1,8 ms |

Ca có nghiệm thì tức thì. **Chi phí nằm trọn ở việc chứng minh KHÔNG có
nghiệm**, mà đó lại là ca thường gặp vì tập ứng viên đóng cố ý không chứa
mọi cách sửa. Với hàng nghìn tài liệu XBRL, 30 giây một tài liệu là không
chạy nổi.

Đã chốt `MAX_CHANGES_MAC_DINH = 2`, áp cho `diagnose()` **và** baseline 9,
vì H3 so ở cùng ngân sách và trần thay đổi là một phần của ngân sách đó.
Baseline 8 **không** áp trần và để mặc định `None` có chủ đích: delta của nó
chạy tự do trong `ℝⁿ`, chặn số trường được sửa là khái niệm của tìm kiếm rời
rạc chứ không áp lên quy hoạch tuyến tính được, và nghiệm đỉnh đã tự giới
hạn số toạ độ khác 0 không vượt quá `rank(A)`; nhận tham số rồi lặng lẽ
không dùng thì runner sẽ tưởng hai nhánh chạy cùng ràng buộc.

**Đây là hạn chế của phương pháp, không phải chi tiết cài đặt.** Tài liệu có
ba trường cùng sai sẽ không được sửa, kể cả khi tổ hợp sửa đúng nằm sẵn
trong tập ứng viên. Đã ghi vào mục Sửa đổi của `PREREGISTRATION.md`. **Bảng
kết quả phải báo cáo tỷ lệ tài liệu rơi vào ca đó.**

### Tách ABSTAIN — đừng gộp lại

`Diagnosis` có thêm `ma_ly_do`, lấy giá trị trong một **tập đóng**:

| Mã | Nghĩa |
|---|---|
| `vo_nghiem` | Đã vét cạn **MỌI** tổ hợp và không có nghiệm |
| `vuot_tran_thay_doi` | Hết tổ hợp trong trần — **chưa duyệt tới các tổ hợp lớn hơn** |
| `het_gio` | Hết ngân sách thời gian |
| `thieu_gia_tri` | Không dựng được vector nên không kiểm được ràng buộc |
| `bo_giai_that_bai` | Bộ giải LP của baseline 8 không trả nghiệm |
| `""` | Không ABSTAIN |

Luận điểm chống bịa phát biểu là *không cách đọc nào của tài liệu này làm
bảng cân đối được*. **Chỉ `vo_nghiem` mới chứng minh được điều đó.**
`vuot_tran_thay_doi` chỉ nghĩa là ta đã không tìm — nghiệm nhiều trường hơn
vẫn có thể tồn tại. Gộp hai thứ lại là tính công cho phương pháp ở những ca
nó không chứng minh được gì. Trước thay đổi này phải so khớp chuỗi tiếng
Việt trong `ly_do_abstain`, tức một lần sửa câu chữ sẽ làm hỏng thống kê mà
không có gì báo.

---

## 6b. Phần F đã xong — và một lỗi CI nằm im từ `f1d236e`

Tám mục dọn dẹp của BUILD-SPEC Phần F đều đã làm. Ba chỗ đáng nhớ vì lý do
chứ không vì code:

**CI đang hỏng mà không ai biết.** Bước cài của workflow liệt kê tay
`pytest ruff numpy pillow openai python-dotenv`, không có `scipy`, trong
khi `repair/diagnose.py` import `scipy.optimize.linprog` ở mức module từ
`f1d236e`. Hậu quả không phải một test đỏ mà là pytest hỏng ở bước
**collect** — cả 31 test của `test_diagnose.py` biến mất, số test giảm mà
không có gì báo. Nó lọt lưới vì CI chỉ chạy khi push lên `main` và khi mở
PR, còn toàn bộ loạt việc này nằm trên `research`. Đã kiểm chứng bằng cách
chặn import `scipy` để mô phỏng đúng môi trường CI, rồi sửa danh sách và
ghi kèm lý do nó phải phủ mọi import mức module.

**`meta["early_stop"]` là khoá tường minh, và nó tồn tại vì phép ĐO.**
Nhánh `PATIENCE_PAGES` dừng khi mới đủ field BẮT BUỘC, tức cố ý bỏ qua
phần đuôi tài liệu. Sau B4 mở rộng bộ trường, một chỉ tiêu mới nằm ở phần
đuôi đó sẽ có tỷ lệ "không đọc được" cao — nhưng đó là tạo tác của điều
kiện dừng, không phải của mô hình, và **không nhìn ra được từ bảng kết
quả** vì trường bị bỏ qua và trường đọc hỏng đều là một ô null. Khoá này
ghi: đã dừng chưa, vì lý do gì, ở trang nào, còn thiếu field nào. Cờ
`DISABLE_EARLY_STOP=true` tắt hẳn, cùng vai với `DISABLE_CONSTRAINT_GATE`.

**Test khoá threading đã được kiểm chứng đúng cách spec đòi.** Thay
`_totals_lock` bằng `contextlib.nullcontext()` rồi chạy lại: đỏ cả 3/3
lượt. Không phải sửa code gì, nhưng giờ đã biết test đó có tác dụng thật.

Mọi thay đổi trong loạt này đều được kiểm bằng cách **đục thủng đúng tính
năng mà test canh, rồi xác nhận test đỏ** — bỏ trần upload, bỏ xoá file
dở, trả early-stop về cuối trang, bỏ cộng dồn bucket, đổi `<=` thành `<`,
bỏ bucket `+Inf`. Tổng 14 đột biến, tất cả đều bị bắt.

---

## 6c. Engine OCR — đã quyết: GIỮ EasyOCR, và một phát hiện đi kèm

BUILD-SPEC nói rõ mục này "không được để trống". Đã đo, không đổi engine.

Module [src/eval/ocr_compare.py](src/eval/ocr_compare.py), báo cáo sinh ra
ở `data/output/ocr_engine_easyocr.md` (đã gỡ khỏi `.gitignore`, cùng lý do
với báo cáo identifiability). Chạy lại:

```bash
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/ocr_compare.py easyocr
```

**Vì sao đo được ngay mà không cần tập gold:** `render.py` đã cho ảnh
bảng, bbox từng ô và chuỗi đúng như đã vẽ. Ground truth mức ô có sẵn,
chính xác tuyệt đối, không tốn một phút gán nhãn.

Kết quả trên 45 ô số, phổ độ lớn 4–13 chữ số:

| Ảnh | Levenshtein | Đúng con số | Không ra số |
|---|---:|---:|---:|
| sạch | 0,999 | 0,978 | 0,022 |
| mờ | 1,000 | 1,000 | 0,000 |
| nhiễu | 1,000 | 1,000 | 0,000 |
| **độ phân giải thấp** | **0,934** | **0,467** | **0,000** |

**Kết luận 1 — giữ EasyOCR.** Con số 0,646 của Ajayi et al. đo trên bảng
KHOA HỌC: nhiều dòng, chữ cái, ký hiệu toán. Trên ô số thì 0,999. Khác
biệt về bản chất, nên lo ngại đó không áp được sang miền này. Đây là câu
trả lời có số liệu cho reviewer.

**Kết luận 2, quan trọng hơn với luận điểm của bài.** Ở độ phân giải thấp,
chỉ số ký tự vẫn báo 0,934 trong khi **chưa tới một nửa** số đọc ra là
đúng. Và tỷ lệ "không ra số" bằng **0** — mọi ô sai đều parse ra một con
số hợp lệ, không một tín hiệu nào báo. Đó chính là lỗi câm, đo được, trên
dữ liệu có ground truth hoàn hảo. Hệ quả cho cách viết bài: **không được
báo cáo Levenshtein accuracy một mình.**

### Việc còn chờ người quyết

Bảng cặp nhầm chữ số quan sát được ở độ phân giải thấp:

| Thật | Đọc thành | Số lần |
|---|---|---:|
| 9 | 0 | 23 |
| 6 | 0 | 8 |
| 9 | 8 | 1 |

`repair/candidates.py` đang sinh ứng viên từ bốn cặp `(0,8) (1,7) (3,8)
(5,6)`. **Cặp áp đảo trong số đo — `9→0` — không nằm trong đó.**

**CHƯA áp vào, và cố ý.** Đây mới là một engine, một bảng tổng hợp, một
mức xuống cấp; chỉnh một hằng số đi thẳng vào hàm mục tiêu của C2 dựa trên
chừng đó dữ liệu là đúng thứ đã bị chặn ở `FIELD_RATIO_BOUNDS`. Cần đo
thêm trên hồ sơ XBRL thật và trên tập gold Việt Nam rồi mới quyết.

Lưu ý ranh giới ở mục 5(b): `inject.py` **không** được dùng chung bảng
này với `repair/candidates.py`. Việc hiệu chỉnh `candidates` theo số đo
của một engine là hợp lệ; việc cho `inject` sinh lỗi theo đúng bảng mà
`candidates` biết cách sửa thì không.

### Bẫy đã gặp khi dựng module này

`python src/eval/ocr_compare.py` đặt `src/eval/` lên **đầu** `sys.path`, và
`eval/metrics.py` ở đó che mất `src/metrics.py` của pipeline. Lỗi nổ ra
tận trong `ocr_baseline` với `ImportError: cannot import name 'timer' from
'metrics'`, trỏ vào một file chẳng liên quan. Cùng họ với vụ `src/types.py`
che module `types` của thư viện chuẩn (mục 8.1). Khối `__main__` của
`ocr_compare.py` tự gỡ thư mục script khỏi `sys.path` để chống lại.
`fetch.py` đã kiểm, KHÔNG dính lỗi này.

---

## 7. MỐC 1 — vẫn chờ người quyết, vẫn chặn B4

**Không đổi so với bản bàn giao trước. Đây là việc AI không làm thay được.**

`python src/constraints.py` sinh lại hai báo cáo. Kết quả hiện tại, giống
nhau ở cả hai chuẩn:

| Chỉ số | Giá trị |
|---|---|
| `rank(A)` | **3** |
| `dim null(A)` | **8 / 11** chiều lỗi vô hình |
| Field định vị được lỗi một-trường | **1 / 11** — chỉ `tong_tai_san` |
| Field cột toàn 0 (không phát hiện được) | **3** |

Ba field không ràng buộc nào bảo vệ: `hang_ton_kho`,
`loi_nhuan_truoc_thue`, `loi_nhuan_sau_thue` — đáng chú ý nhất là
`hang_ton_kho` vì đó đúng là field đã có lỗi đọc thật trên báo cáo VNM. Các
field còn lại đi thành cặp không phân biệt được:
`tai_san_ngan_han ↔ tai_san_dai_han`, `no_phai_tra ↔ von_chu_so_huu`,
`doanh_thu_thuan ↔ gia_von_hang_ban ↔ loi_nhuan_gop`.

**Phát hiện quyết định hướng đi:** `minimal_localizing_set()` trả `None` —
với ba đẳng thức hiện có, **không tập con nào** của 11 chỉ tiêu làm mọi lỗi
một-trường định vị được. Nút thắt là số **ĐẲNG THỨC**, không phải số chỉ
tiêu. Thêm field mà không thêm đẳng thức thì 1/11 không nhúc nhích và H2 vẫn
vô nghĩa.

### Câu hỏi của mốc này ĐÃ ĐỔI — `1d3f89d`

`src/constraints_scenarios.py` đo xem mỗi nhóm đẳng thức ứng viên mua được
bao nhiêu. Kết quả đổi hẳn câu hỏi phải hỏi:

| KB | Kịch bản | Chỉ tiêu | Đẳng thức | rank | Định vị được |
|---|---|---:|---:|---:|---:|
| A | Hiện tại | 11 | 3 | 3 | 1/11 (9%) |
| B | + Tổng nguồn vốn | 12 | 4 | 4 | 2/12 (17%) |
| C | + chuỗi lãi lỗ B02 | 15 | 6 | 6 | 3/15 (20%) |
| D | + phân rã TS ngắn hạn | 19 | 7 | 7 | 5/19 (26%) |
| E | **+ liên kết chéo B01/B02/B03** | 26 | 11 | 11 | **13/26 (50%)** |

Thêm chỉ tiêu cùng loại gần như vô ích: A→D tăng gần gấp đôi số chỉ tiêu mà
chỉ được 9%→26%, trong khi mỗi chỉ tiêu là chi phí gán nhãn nhân 60 tài
liệu. Riêng D→E gấp đôi tỷ lệ, và là bước duy nhất làm được vậy.

**Định luật đứng sau, đã chốt bằng test:** một chỉ tiêu định vị được khi và
chỉ khi tập đẳng thức chứa nó khác tập đẳng thức của mọi chỉ tiêu khác.
Trong một đẳng thức phân rã đơn lẻ `a + b = tổng` thì CẢ BA nằm ngoài tầm —
hai thành phần có cột bằng nhau, còn cột của tổng là `[−1]` tỷ lệ với cột
`[1]`, nên lỗi `+δ` ở `a` và `−δ` ở `tổng` cho residual giống hệt nhau.

Nên câu hỏi hỏi Phụ lục IV **không phải "còn chỉ tiêu nào"** mà **"còn con
số nào xuất hiện ở HAI CHỖ"**.

`hang_ton_kho` không định vị được ở MỌI kịch bản, kể cả E — nó là chỉ tiêu
lá luôn đứng cùng anh em. Mà đó đúng là chỉ tiêu đã có lỗi đọc thật trên
báo cáo VNM. Ràng buộc kế toán **chứng minh được** là không bao giờ bắt
được lỗi đó; chỉ mỏ neo đơn vị tính và bước đọc lại mới bắt được. Ví dụ cụ
thể, có thật, để đưa vào bài.

**CẢNH BÁO:** các đẳng thức trong `constraints_scenarios.py` là GIẢ THUYẾT
dựng lại từ kết cấu biểu mẫu, **chưa đối chiếu văn bản**. Chúng để biết NÊN
TÌM GÌ, không thay được việc đọc Thông tư — BUILD-SPEC mục 0.5.

### Bảng đối chiếu đã dựng sẵn

[MOC1-DOI-CHIEU.md](MOC1-DOI-CHIEU.md) có: nguồn văn bản chính thức trên
`congbao.chinhphu.vn` (lưu ý TT99 bị tách thành **10 số công báo**, Phụ lục
IV nằm ở các số cuối), chuỗi cần tìm trong file — đáng giá nhất là tìm mọi
lần xuất hiện của `Mã số` kèm dấu `=` — nơi đặt file (`data/legal/`, đã
gitignore), bảng tick từng mã số, và ô trống để điền đẳng thức tìm thêm.

**Người chủ trì phải làm:**

1. Đối chiếu từng dòng bảng mã trong
   [src/fields_config.py](src/fields_config.py) với **Phụ lục IV văn bản
   gốc** của cả hai Thông tư. Cảnh báo đã ghi ngay tại chỗ trong file. Chỗ
   lệch đã biết: tổng tài sản 270 ở TT200, 280 ở TT99. Chưa xác nhận: ký
   hiệu mẫu biểu TT200 là `B01-DN` hay `B01a-DN`, và bộ đẳng thức của TT99
   (hiện dùng chung với TT200).
2. Trả lời câu hỏi mà kết quả trên đặt ra: **Phụ lục IV còn những đẳng thức
   nào chưa khai thác?** Đó mới là đường ra cho H2.
3. Chốt bộ trường — nó quyết định chi phí gán nhãn tay cho 60 tài liệu gold,
   khoản đắt nhất của cả dự án.

---

## 7b. Đã đối chiếu Công báo — hai kết quả, 23/08/2026

Người dùng tải hai số Công báo vào `data/legal/` (đã gitignore). Trích bằng
`pdftotext -layout` cho PDF và `antiword -m UTF-8.txt` cho `.doc` cũ.

**Cả hai file đều là số CUỐI CÙNG của bộ**, nên chỉ chứa phần B03 trở đi:

| File | Chuẩn | Nội dung |
|---|---|---|
| `2015_289 + 290-200_2014_TT-BTC.pdf` | TT200 | Điều 114 (B03) → hết |
| `2025_1581 + 1582_99-2025-TT-BTC.doc` | TT99 | cuối B02a + B03 |

### Kết quả 1 — liên kết chéo CÓ THẬT, khai báo tường minh

TT200 Điều 114, mục "Tiền và tương đương tiền cuối kỳ (Mã số 70)":

> Chỉ tiêu này bằng số "Tổng cộng" của các chỉ tiêu Mã số 50, 60 và 61 và
> **bằng chỉ tiêu Mã số 110 trên Bảng cân đối kế toán kỳ đó**. Mã số 70 =
> Mã số 50 + Mã số 60 + Mã số 61.

TT99 nói y hệt, chỉ đổi tên biểu mẫu. Thêm: `Mã số 60` (tiền đầu kỳ) =
`Mã số 110` **cột "Số đầu kỳ"**. Ghép lại:

```
B01.110 (cuối kỳ) = B01.110 (đầu kỳ) + lưu chuyển tiền thuần + ảnh hưởng tỷ giá
```

Nối bảng cân đối kỳ này với **kỳ trước** — chính là câu hỏi proposal mục
6.1(d), và câu trả lời là cột kỳ trước CÓ ràng buộc thật nối vào.

**Chưa trả tiền ngay:** 1/11 → 2/18. Liên kết chéo gắn đẳng thức thứ hai vào
`B01.110`, nhưng `B01.110` phải đã nằm trong một đẳng thức thì mới có cái để
gắn — đẳng thức đó là phân rã Tài sản ngắn hạn, ở Điều 112 tức **Công báo
287+288 chưa có**. Có nó thì lên 5/21.

### Kết quả 2 — `FORM_MARKERS` đang sai, đã sửa (`023321c`)

Câu hỏi mục 3.2(a) của `MOC1-DOI-CHIEU.md` có đáp án, và nó lật ngược giả
định trong `fields_config.py`. TT200 dùng ĐỦ CẢ `B01-DN`, `B01a-DN`,
`B01b-DN`. Nguyên văn: *"Bảng cân đối kế toán giữa niên độ (dạng đầy đủ) —
Mẫu số B01a-DN"*. Hậu tố phân biệt **kỳ báo cáo**, không phân biệt Thông tư:
không hậu tố = năm, `a` = giữa niên độ dạng đầy đủ tức **quý**, `b` = tóm
lược. TT200 nói rõ biểu mẫu giữa niên độ dùng **cùng bộ mã số**.

Hậu quả bản cũ: lookahead `(?!\s*a)` làm marker TT200 trượt mọi trang
`B01a-DN`, tức trượt mọi báo cáo **quý** theo TT200 — đúng loại tài liệu dự
án xử lý, gồm cả VNM Q1/2026. Khi trượt thì `extract_field_by_code()` trả
`None` và **đường dự phòng theo mã số tắt hẳn, im lặng**.

Hướng sửa: bỏ hẳn việc dùng ký hiệu mẫu biểu để phân biệt chuẩn, vì
`detect_standard()` đã làm việc đó bằng TÊN báo cáo và **dấu hiệu đó đã đối
chiếu, đúng** — TT200 gọi "Bảng cân đối kế toán", TT99 gọi "Báo cáo tình
hình tài chính". `FORM_MARKERS` thành dict phẳng theo mẫu biểu;
`form_markers_for(standard)` → `marker_for_form(form)`.

### Kết quả 3 — đã đủ Công báo, và một kết luận cũ BỊ BÁC BỎ

Đã có nốt `287+288` (TT200) và `1579+1580` (TT99). Số `1577+1578` không chứa
phần báo cáo tài chính. Toàn bộ đẳng thức trong `constraints_scenarios.py`
giờ là **trích nguyên văn**, không còn giả thuyết.

Ba đẳng thức repo đang dùng **đều đúng**, nhưng cái thứ hai
(`nợ + VCSH = tổng tài sản`) là đẳng thức **suy ra**: văn bản viết
`Mã số 440 = Mã số 300 + Mã số 400` rồi viết **riêng** `Tổng cộng Tài sản =
Tổng cộng Nguồn vốn`.

| KB | Kịch bản | Chỉ tiêu | Định vị được | Bước này mua được |
|---|---|---:|---:|---|
| A | Hiện tại | 11 | 1/11 | — |
| B | **+ Tổng cộng nguồn vốn (440)** | 12 | 2/12 | **+1 → +1, tỷ lệ 1,00** |
| C | + chuỗi lãi lỗ B02 | 16 | 3/16 | +4 → +1, tỷ lệ 0,25 |
| D | + phân rã TSNH | 20 | 5/20 | +4 → +2, tỷ lệ 0,50 |
| E | + B03 và liên kết chéo | 26 | 7/26 | +6 → +2, tỷ lệ 0,33 |

**Bước rẻ nhất: thêm ĐÚNG MỘT chỉ tiêu, Tổng cộng nguồn vốn.**

> **BỊ BÁC BỎ:** bản trước của mục này nói liên kết chéo hiệu quả **gấp
> đôi** phân rã. Sai — kết luận đó dựa trên hai đẳng thức giả thuyết KHÔNG
> có trong văn bản (liên kết LNCPP↔LNST, và phân rã VCSH). Với đẳng thức
> thật, liên kết chéo cho tỷ lệ 0,33, **thấp hơn** phân rã 0,50. Đã chốt
> bằng `test_lien_ket_cheo_KHONG_hieu_qua_hon_phan_ra` để nó không quay lại.
>
> Bài học đã ghi vào docstring `constraints_scenarios.py`: **đừng để đẳng
> thức giả thuyết chạy vào bảng kết quả**, kể cả khi chúng hợp lý về kế toán.

**Hai chỗ khác nhau giữa hai chuẩn, đều là nguồn lỗi câm:**

- **Mã 270 mang nghĩa khác hẳn** — TT200: "Tổng cộng tài sản"; TT99: "Tài
  sản dài hạn khác" (`270 = 271+272+273+274`). Tra nhầm bảng mã thì đọc ra
  một con số hợp lệ của chỉ tiêu hoàn toàn khác. Đây là lý do `standard`
  phải là tham số bắt buộc của `extract_field_by_code()`.
- Dự phòng giảm giá hàng tồn kho: mã **149** ở TT200, mã **142** ở TT99.

`minimal_localizing_set()` vẫn trả `None` ở **mọi** kịch bản, và
`hang_ton_kho` không định vị được ở kịch bản nào.

### Việc còn chờ người quyết

Chốt bộ trường (B4). Số liệu để quyết đã đủ — xem bảng trên và
[MOC1-DOI-CHIEU.md](MOC1-DOI-CHIEU.md) mục 3.4. Quyết xong thì ghi vào mục
"Sửa đổi" của `PREREGISTRATION.md` kèm ngày và lý do.

---

## 8. Chỗ đã đi khác `BUILD-SPEC.md` — có chủ đích, đã kiểm chứng

Tám chỗ. Ghi lại để phiên sau không "sửa ngược" theo spec.

1. **`src/types.py` → `src/extraction_types.py`.** Repo import phẳng với
   `pythonpath = src`, nên `src/types.py` che khuất module `types` của thư
   viện chuẩn, mà `enum` lại `from types import MappingProxyType` — trình
   thông dịch chết lúc khởi động với lỗi circular import không hề gợi ý
   nguyên nhân. Đã kiểm chứng bằng cách chạy thật trước khi đổi tên.
2. **Test đơn điệu của `minimal_localizing_set` kiểm chiều NGƯỢC với spec.**
   Spec đòi chốt "thêm field không làm bộ tối thiểu NHỎ ĐI" — chiều đó sai
   về toán: tập ứng viên rộng hơn chỉ thêm lựa chọn, nên cực tiểu chỉ có thể
   giữ nguyên hoặc nhỏ đi. Theo đúng chữ của spec là đóng đinh một bất biến
   sai vào bộ test.
3. **Báo cáo identifiability gỡ khỏi `.gitignore`.** Spec bảo ghi vào
   `data/output/` nhưng cả thư mục đó bị ignore, nên artifact Mốc 1 sẽ không
   bao giờ tới tay người chủ trì. Giữ đường dẫn spec yêu cầu, thêm ngoại lệ
   cho đúng `identifiability_*.md` — nó chỉ chứa ma trận ràng buộc.
4. **Trần ứng viên mỗi trường để 12 thay vì 10.** Riêng nguồn `scale` đã
   đóng góp 6 ứng viên có cấu trúc khác hẳn nhau, cắt bớt là cắt đúng chế độ
   lỗi mà ràng buộc kế toán **chứng minh được** là không bao giờ phát hiện
   nổi. Kèm trần riêng cho mỗi nguồn, vì xếp thuần theo cost sẽ để biến thể
   nhầm chữ số của một con số 14 chữ số chiếm hết chỗ.
5. **Không dùng DeLong cho H1**, khác đề xuất ở `ADDENDUM` mục 3. DeLong xử
   lý đúng tương quan giữa các đường ROC nhưng vẫn giả định quan sát độc
   lập, mà các trường trong cùng tài liệu thì không.
6. **Baseline 8 dùng `scipy.optimize.linprog`, `scipy==1.18.0` khai báo
   trong `requirements.txt`.** Không mâu thuẫn với quyết định không thêm
   `pulp` cho `diagnose()`: scipy **đã nằm sẵn trong image** theo chuỗi
   `easyocr → scikit-image → scipy`, nên đây là nói ra một phụ thuộc đang
   dùng chứ không phải cài thêm; `pulp` thì chưa có và kéo theo binary CBC.
   Dựa vào phụ thuộc bắc cầu mà không khai báo là tự đặt bẫy cho ngày
   easyocr đổi phụ thuộc.
7. **B5 có SÁU module thay vì bốn.** `table.py` vì hai trong năm chế độ lỗi
   (lệch dòng, lệch cột) được định nghĩa bằng hình học của trang nên cần thứ
   tự dòng và danh sách cột. `facts.py` vì spec không nói con số lấy từ đâu
   — `render.py` cần giá trị mà không module nào cung cấp.
8. **`render.py` vẽ thẳng bằng Pillow thay vì dựng HTML rồi chụp.** Đường
   HTML cần trình duyệt không đầu hoặc `wkhtmltoimage` trong image — đúng
   cái giá đã từ chối trả cho MILP ở C2. Vẽ thẳng còn cho **bbox chính xác
   từng ô miễn phí**, thứ tầng này cần làm provenance ground truth; đi đường
   HTML thì bbox phải suy ngược từ ảnh đã render, tức thêm một nguồn sai số
   vào chính thứ dùng làm chuẩn. SynFinTabs vẫn nên trích dẫn và dùng lại
   được phần sinh ảnh nếu cần trình bày đa dạng hơn, nhưng **khác biệt phải
   giữ khi nhắc tới họ**: nội dung của họ là số ngẫu nhiên nên không đẳng
   thức kế toán nào đúng trên đó.

---

## 9. Chưa làm

Theo thứ tự phụ thuộc trong `BUILD-SPEC.md` phần E.

| Mục | Trạng thái | Chặn bởi |
|---|---|---|
| C2, B5 | **XONG** | — |
| **Phần F** dọn dẹp | **XONG (8/8)** — mục 6b, 6c | — |
| **README** | **XONG** (`2015e8c`) | — |
| Guideline gán nhãn | **XONG** (`9724504`) — điều kiện của pilot 20 tài liệu | — |
| Bảng đối chiếu Mốc 1 | **XONG** (`1d3f89d`) | — |
| **B4** mở rộng bộ trường | Chưa | Mốc 1 (mục 7) |
| **C3** vòng lặp đọc lại | Chưa | **MỐC 3** — mục 10 |
| **C4** verdict ba trạng thái | Chưa | C3 |
| **D2** runner / **D3** bảng / **D4** hình | Chưa | C4, rồi D2 |

Không còn việc nào làm được mà không chờ người: mọi thứ còn lại đều nằm sau
Mốc 1 hoặc Mốc 3, và cả hai mốc đều cần người chủ trì quyết hoặc cần dữ
liệu chỉ máy người dùng tải được.

### Hằng số chưa hiệu chỉnh — đo lại trước khi tin

Bốn nhóm, đều đã ghi cảnh báo tại chỗ trong code:

1. `TOTAL_ASSETS_BOUNDS` trong `fields_config.py` — hiện `(1e10, 1e15)`,
   dựa trên suy luận về phổ doanh nghiệp niêm yết, chưa dựa trên phân phối
   đo được.
2. `XAC_SUAT_TIEN_NGHIEM` trong `repair/candidates.py` — đi **thẳng** vào
   hàm mục tiêu của C2, nên đặt sai thì thuật toán vẫn chạy và vẫn cho
   nghiệm, chỉ là ưu tiên sai loại sửa. Ước lượng lại từ phân loại lỗi trên
   tập gold.
3. `FIELD_RATIO_BOUNDS` và `REVENUE_TO_ASSETS_LIMIT` — hiệu chỉnh trên
   **đúng một công ty** (VNM Q1/2026). Người dùng đã ra chỉ thị rõ: **không
   chỉnh các ngưỡng này khi dữ liệu mới chỉ có một công ty**.
4. `MAX_CHANGES_MAC_DINH = 2` — đã đo trên bài toán 8 chỉ tiêu, **chưa đo
   trên 25 chỉ tiêu**. Đo lại sau khi Mốc 1 chốt bộ trường, vì không gian
   tìm kiếm tăng theo luỹ thừa của số ứng viên mỗi trường.
5. Bảng bốn cặp nhầm chữ số trong `repair/candidates.py` — số đo ở mục 6c
   cho thấy cặp áp đảo `9→0` **không nằm trong bảng**. Chưa sửa, lý do và
   điều kiện để sửa ghi ở mục 6c.
6. `MAX_UPLOAD_BYTES = 50 MB` trong `api.py` — chọn theo đúng một tài liệu
   (báo cáo VNM 55 trang, ~9 MB). Chưa thấy báo cáo hợp nhất dày nào để
   biết biên trên thật.

### Phần F và README — đã xong

Cả tám mục Phần F và README đều đã làm, chi tiết ở mục 6b và 6c. README giờ
nói rõ repo có hai lớp và trỏ sang `PREREGISTRATION.md` với file này.

---

## 10. MỐC 3 — mốc phải dừng thật, và nó đang mở

`BUILD-SPEC.md` phần E:

> **MỐC 3 — sau C2, chạy baseline 9.** Nếu baseline 9 ngang bằng phương pháp
> đề xuất thì luận điểm "đọc lại nguồn" sai. Dừng, báo cáo, lùi paper về
> tầng dataset + identifiability. Đừng chạy tiếp C3 và toàn bộ ablation
> trước khi biết kết quả này.

C2 đã xong nên mốc này đang mở. Tầng XBRL vừa dựng là thứ làm nó đánh giá
được ở quy mô có power, nhưng cần dữ liệu thật — mà container không ra được
sec.gov, nên phần này người dùng phải chạy:

Quy mô đã chốt: **pilot 1 công ty, 3 hồ sơ**. Đủ để chạy Mốc 3 đầu-cuối và
xem chiều kết quả, chưa đủ power để kết luận — nhưng nó lộ mọi trục trặc
đường ống trước khi tốn thời gian tải nhiều.

```bash
export SEC_USER_AGENT="Trần Kim Danh trankimdanh2007@gmail.com"
python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --dry-run   # xem trước
python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --out data/xbrl
```

`--dry-run` giờ kiểm luôn `SEC_USER_AGENT` và in rõ thiếu hay đủ (`2c14420`)
— trước đó nó chạy trơn tru rồi lượt chạy thật mới hỏng ở request đầu.

SEC chặn IP nếu thiếu `User-Agent` có tên thật và email, hoặc quá 10
request/giây; script đặt trần 5/giây và **ném lỗi ngay** khi thiếu
`SEC_USER_AGENT` thay vì điền giá trị mặc định.

Sau khi có dữ liệu: chạy `diagnose()` so với `diagnose_fellegi_holt_donor()`
trên cùng bộ tài liệu, cùng ngân sách, cùng trần. Theo
`PREREGISTRATION.md`, hai chỉ số phải báo cáo cùng lúc — tỷ lệ lỗi câm giảm
bao nhiêu, **VÀ** chỉ số chống bịa có tăng không. Thắng chiều một mà thua
chiều hai là kết quả tiêu cực và phải nói ra. Đếm riêng `vo_nghiem` với
`vuot_tran_thay_doi` (lý do ở mục 6).

---

## 11. Quy ước bắt buộc

Từ `BUILD-SPEC.md` mục 0.2 và chỉ thị trực tiếp của người dùng.

| Quy ước | Chi tiết |
|---|---|
| **Import phẳng** | `pytest.ini` có `pythonpath = src`. Viết `from validation import ...`, KHÔNG `from src.validation import ...` |
| **Comment tiếng Việt** | Giải thích **tại sao**, không phải **cái gì**. Đọc `src/metrics.py` và `src/fields_config.py` để bắt giọng văn |
| **Docstring mô tả hiện trạng** | Không viết trạng thái dự định như thể đã làm xong |
| **Config tập trung** | Mọi hằng số miền nằm ở `fields_config.py` |
| **Nạp model lười** | Model nặng nạp trong getter, không nạp lúc import. CI không cài torch |
| **Lint + test** | `ruff check src tests` rồi `pytest`, **trước khi báo xong** |
| **Test không cần mạng** | Dùng fixture và hàm giả, không gọi API thật |
| **Trạng thái tường minh** | Trạng thái ghi ra log/metrics/JSON phải là khoá tường minh, không để người đọc suy ra từ sự vắng mặt của khoá khác |
| **Commit** | Mỗi module một commit, message giải thích **lý do**. Commit thẳng lên nhánh đang làm việc, **không tự tạo branch** |
| **KHÔNG ghi danh nghĩa Claude** | **Tuyệt đối không** thêm trailer `Co-Authored-By: Claude` hay dòng `Generated with Claude Code`. Mọi thứ đứng tên `Tkd2007 <trankimdanh2007@gmail.com>` |

### Bẫy môi trường đã gặp

- **Console Windows mặc định cp1252.** In tiếng Việt ra stdout sẽ nổ
  `UnicodeEncodeError`. Mọi khối `__main__` phải có
  `sys.stdout.reconfigure(encoding="utf-8")`; chạy script một dòng thì đặt
  `PYTHONIOENCODING=utf-8` ở đầu lệnh.
- **Heredoc của bash vỡ khi nội dung có số lẻ dấu nháy đơn.** Viết file dài
  bằng công cụ ghi file, đừng dùng `cat > file <<'EOF'` với nội dung tiếng
  Việt có dấu nháy hoặc chuỗi `'''`.
- **`.env.docker` đang chứa OpenRouter key thật.** Không nằm trong git và
  chưa từng được commit (đã kiểm cả lịch sử), nhưng repo là public nên một
  lần `git add -f` nhầm là lộ.
- **Force-push bị trình phân loại quyền chặn.** Cần viết lại lịch sử thì để
  người dùng tự chạy lệnh trong terminal của họ.
- **`time.monotonic()` trên Windows quá thô** để test những khoảng vài mili
  giây. Test bộ điều tốc của `fetch.py` dùng đồng hồ giả qua `monkeypatch`
  chứ không đo thời gian thật — một test đỏ ngẫu nhiên tệ hơn không có test.

---

## 12. Lệnh hay dùng

```bash
# Kiểm trước khi báo xong bất cứ gì
python -m ruff check src tests
python -m pytest -q

# Sinh lại báo cáo identifiability cho cả hai chuẩn
PYTHONIOENCODING=utf-8 python src/constraints.py

# Chạy pipeline trên một tài liệu
python src/router.py data/samples/<file>.pdf

# Chế độ ĐO cho H1 — tắt hoàn toàn cổng ràng buộc
DISABLE_CONSTRAINT_GATE=true python src/router.py data/samples/<file>.pdf

# Đo engine OCR trên ô số (cần easyocr; mất vài phút vì chạy CPU)
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/ocr_compare.py easyocr

# Tải hồ sơ XBRL — CHỈ CHẠY ĐƯỢC TRÊN MÁY NGƯỜI DÙNG
export SEC_USER_AGENT="Tên thật email@example.com"
python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --dry-run
```

---

## 13. Bước kế tiếp đề xuất

1. **Đưa Mốc 1 cho người chủ trì** (mục 7). Nó chặn B4, mà B4 quyết định chi
   phí gán nhãn. Câu hỏi thật không phải "trích bao nhiêu field" mà **"Phụ
   lục IV còn đẳng thức nào chưa khai thác"**.
2. **Người dùng chạy `fetch.py`** để có dữ liệu XBRL thật (mục 10).
3. **Chạy MỐC 3** ngay khi có dữ liệu. **Đây là mốc phải dừng thật** — nếu
   baseline 9 ngang bằng thì toàn bộ novelty tầng 1 sai, dừng và lùi paper
   về tầng dataset + identifiability. Không chạy tiếp C3 và ablation trước
   khi biết kết quả, vì chạy tiếp chỉ để tích luỹ số liệu cho một luận điểm
   đã sai.
4. **Sau khi qua Mốc 3:** C3 rồi C4, rồi D2/D3/D4.

**Không còn việc "trong lúc chờ".** Phần F, engine OCR, README, guideline
gán nhãn và bảng đối chiếu Mốc 1 đã xong hết; mọi thứ còn lại đều nằm sau
Mốc 1 hoặc Mốc 3.

**Sáu commit của ngày 23/08 chưa push** — `895b731`, `66296a6`, `3abc812`,
`100afb9`, `a3a5ea7`, `2015e8c`. `origin/research` đang ở `fa399e4`. Muốn
đẩy thì người dùng tự chạy, hoặc yêu cầu rõ ràng thì mới đẩy.

**Lưu ý khi merge sang `main`:** CI chỉ chạy trên `main` và trên pull
request, nên lỗi thiếu thư viện ở mục 6b chỉ lộ ra ở lần merge đầu tiên.
Nó đã được sửa, nhưng nguyên tắc thì còn: thêm bất kỳ import mức module
nào cũng phải sửa danh sách cài trong `.github/workflows/ci.yml`.
