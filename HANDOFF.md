# Bàn giao — hạ tầng nghiên cứu ViFinKIE

Viết để một phiên Claude khác đọc và làm tiếp mà **không cần hỏi lại gì**.
Mọi tham chiếu đều là đường dẫn file hoặc commit hash.

- **Nhánh:** `research` (tách từ `main` tại `4216291`)
- **Commit gần nhất:** cố ý KHÔNG ghi hash ở đây — dòng này đã cũ đi ba lần
  chỉ trong một ngày, vì chính commit cập nhật nó lại thành commit mới nhất.
  Chạy `git log --oneline -1` và `git status -sb`. Quy ước: **push sau mỗi
  commit**, nên `research` khớp `origin/research` là trạng thái bình thường.
- **Test:** **374 xanh / 0 đỏ** ở CẢ `USE_OCR_FIRST=true` lẫn `false`.
  `ruff check src tests` sạch.
- **Bộ chỉ tiêu:** 21 với TT99, 20 với TT200; 7 đẳng thức. MỐC 1 đã đóng.
- **`main`:** **KHÔNG BAO GIỜ MERGE** — chỉ thị của người dùng, 24/08/2026.
  `research` đi trước 56 commit và cứ để vậy. Hệ quả: CI hiện chỉ chạy trên
  `main` và trên pull request, nên **CI thực tế không bao giờ chạy** — mọi
  việc kiểm phải làm tại chỗ. Muốn CI có ích thì thêm `research` vào phần
  trigger của `.github/workflows/ci.yml`, KHÔNG phải merge.
- **Cập nhật:** 24/08/2026

---

## 0. CÂU HỎI ĐANG CHỜ NGƯỜI DÙNG TRẢ LỜI

Mục này là nơi DUY NHẤT liệt kê những thứ đang chờ quyết định. Phiên Claude
mới đọc mục này trước tiên; nếu người dùng chưa trả lời thì hỏi lại đúng
những câu dưới đây chứ đừng tự chọn, vì mỗi câu đều đổi kết luận khoa học
chứ không phải chi tiết cài đặt.

Người dùng trả lời được bằng một tin nhắn duy nhất, dạng "Câu 4 chọn ...".

**Đang chờ:** Câu 3 (hoãn được). Không câu nào đang chặn việc gì.
**Đã trả lời 25/08/2026 — tất cả trong một ngày:** Câu 1 → (a) ba con số định
vị; Câu 2 → (a) đo ma trận trước; Câu 4 → (a) cùng nguồn khác độ sâu; Câu 5 →
nới trần 10/20; Câu 6 → ghi làm giới hạn; Câu 7 → (a) hoà thì hoãn phán
quyết. Cộng thêm một quyết định không đánh số: chỉ số chính của H3 trên tầng
XBRL chuyển sang mức LƯỢT.

Giữ lại nguyên văn từng câu ở dưới vì mỗi câu kèm một ràng buộc phải nhớ khi
đọc bảng kết quả về sau.

---

## 1. Đọc gì trước

Bốn tài liệu nguồn do người dùng giữ, nằm ở thư mục `MD file/` **và nội dung
bị gitignore** (`MD file/.gitignore` chứa `*.md`), nên chỉ có trên máy người
dùng: `FINAL-proposal-reread-dont-repair.md` (proposal, bốn giả thuyết
H0–H3), `ADDENDUM-statistical-treatment.md` (vá phần thống kê),
`FINAL-repo-changes.md` (dịch proposal sang việc trong repo),
`BUILD-SPEC.md` (**đặc tả thi công** — thứ đang được thực hiện).

Trong repo, đọc theo thứ tự:

1. [PREREGISTRATION.md](PREREGISTRATION.md) — bốn giả thuyết, chỉ số chốt
   trước, điều kiện phản chứng, ba mốc dừng. **Không sửa đè lên nội dung
   gốc**; mọi thay đổi ghi vào mục "Sửa đổi" ở cuối kèm ngày và lý do, nếu
   không thì việc đăng ký trước mất hết giá trị.
2. **Phụ lục A** ở cuối file này — bảng đối chiếu ma trận ràng buộc
   với Thông tư, **đã đối chiếu xong và Mốc 1 đã đóng**. Mục 10 dưới đây tóm
   tắt kết quả và quyết định bộ chỉ tiêu.
3. [src/eval/stats.py](src/eval/stats.py) — docstring đầu module, nguyên tắc
   chi phối toàn bộ phần thống kê.
4. [src/repair/diagnose.py](src/repair/diagnose.py) — docstring đầu module
   và các hằng số đầu file. Đây là chỗ tập trung nhiều quyết định thiết kế
   nhất, mỗi cái đều có lý do viết kèm.
5. [ANNOTATION-GUIDELINE.md](ANNOTATION-GUIDELINE.md) — chỉ cần khi bắt đầu
   gán nhãn tập gold.

---

## 2. Bối cảnh

Repo gốc là pipeline **trích xuất** chỉ tiêu tài chính từ PDF báo cáo tài
chính Việt Nam — 11 chỉ tiêu lúc đầu, 21 sau Mốc 1: PDF → DocLayout-YOLO cắt
vùng bảng → EasyOCR hoặc VLM (Gemma qua OpenRouter) → validation → FastAPI.

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

## 3. Đã làm

### Ngày 21–22/08/2026

| Commit | Mục | Nội dung |
|---|---|---|
| `689e2d0` | D1 | `PREREGISTRATION.md` — dấu thời gian git là bằng chứng |
| `4b20aea` | A1 | Điều kiện áp dụng cho `FIELD_RELATIONS` |
| `7fd34f0` | A3 | Tách mã số dòng và mẫu biểu theo TT200 / TT99 |
| `437e2a1` | A4 | Chuẩn hoá đơn vị tính + mỏ neo biên độ lớn |
| `88c031e` | A2 | `src/constraints.py` — ma trận ràng buộc, identifiability |
| `c85c812` | B1 | Cờ `DISABLE_CONSTRAINT_GATE` để đo H1 không vòng lặp |
| `a5ec83e` | B2 | Confidence từng trường bằng self-consistency |
| `0d74195` | B3 | Provenance từng trường qua suốt chuỗi |
| `ad6684a` | B6 | Eval harness, thống kê, trường tái lập |
| `2cf613a` | C1 | Sinh tập ứng viên sửa lỗi từ tài liệu |
| `f1d236e` | C2 | Hai baseline đối chứng không còn thua vì lý do cài đặt — mục 5 |
| `1dacb34` | B5 | Tầng đánh giá XBRL — mục 6 |
| `9c3f7c9` | C2 | Trần `max_changes`, tách ABSTAIN theo lý do — mục 7 |

Ngoài ra `main` có `debac2f` (test khoá threading cho `merge_into_totals`).

### Ngày 23/08/2026

| Commit | Mục | Nội dung |
|---|---|---|
| `895b731` | F | Tách `requirements-dev.txt`; **sửa CI đang hỏng** — mục 8 |
| `66296a6` | F | `MAX_UPLOAD_BYTES` đọc theo khối; `save=False` cho đường API |
| `3abc812` | F | Early-stop ở vòng vùng; `DISABLE_EARLY_STOP` + `meta["early_stop"]` |
| `100afb9` | F | Histogram latency, tự chia bucket |
| `a3a5ea7` | F | **Đo engine OCR → quyết định GIỮ EasyOCR** — mục 9 |
| `2015e8c` | — | README khớp lại hiện trạng |
| `1d3f89d` | Mốc 1 | `constraints_scenarios.py` + bảng đối chiếu (nay là Phụ lục A) |
| `9724504` | — | `ANNOTATION-GUIDELINE.md` |
| `2c14420` | — | `fetch.py --dry-run` kiểm `SEC_USER_AGENT` |
| `3fb6472` | Mốc 1 | Trích đẳng thức từ Công báo, đợt 1 |
| **`023321c`** | A3 | **Sửa `FORM_MARKERS`: hậu tố a/b là KỲ, không phải Thông tư** — mục 10 |
| **`6744bee`** | Mốc 1 | **Thay đẳng thức giả thuyết bằng đẳng thức đã đối chiếu** — mục 10 |
| `e08d5e8` | Mốc 1 | Bảng đối chiếu đầy đủ cả hai chuẩn |
| `32db2f7` | Mốc 1 | Đóng các ô chưa xác nhận của bảng đối chiếu |
| **`4064519`** | **B4** | **Bộ chỉ tiêu lên 21, hai chuẩn hết đẳng cấu** — mục 10 |
| **`df96ff2`** | **Mốc 1** | **Ghi quyết định vào đăng ký trước, đóng hai ô chờ của guideline** |

### Ngày 24/08/2026

| Commit | Mục | Nội dung |
|---|---|---|
| `5810ea2` | — | Vá bốn chỗ tài liệu tự mâu thuẫn; chốt nơi nộp (mục 17) |
| **`fa5c6d2`** | **C** | **Chuẩn đi tới nơi kiểm đẳng thức; meta hợp nhất thay vì đè** |
| **`88a77f5`** | **C** | **Bộ chỉ tiêu đi theo chuẩn ở prompt, trích xuất, dừng sớm** |
| **`19fe938`** | **C** | **Oracle `tim_theo_ma_so()`; ô số hỏng thôi mượn số dòng dưới** |
| **`ada6f75`** | **C** | **Probe dò dòng + điền 0; đẳng thức phân rã chạy được** |
| `0088218` | — | Gộp bảng đối chiếu Mốc 1 và sổ thi công vào file này |
| `fc7fc42` | — | Thôi OCR một trang hai lần; test thôi phụ thuộc `.env` |
| `709e58c` | — | Đo lại trần `max_changes` trên bộ chỉ tiêu đã chốt |
| `f09c407` | — | Bốn file MD khớp lại hiện trạng |
| **`62b5be5`** | **MỐC 3** | **Runner `src/eval/moc3.py`; pilot Apple lộ 3 trục trặc** |
| `7ad3cc1` | — | Hồ sơ XBRL thôi nằm trong git |
| `29995f7` | — | Ghi kết quả pilot và mục 17 (lưu ý việc đã quyết chưa làm) |
| **`e6c286c`** | **MỐC 3** | **Xử được nhiều công ty; donor thôi lấy từ công ty đang xét** |

Chi tiết đầy đủ của phương án C ở **Phụ lục B**.

Xen giữa là các commit cập nhật chính file này (`fa399e4`, `7c37ec9`,
`7d93593`, `41c1a14`, `b53ed8f`, `b55722d`, `2a2198f`, `463bc5b`) và hai
commit của người dùng (`78bf74a`, `2b28fe1`) tạo `MD file/.gitkeep` và
`MD file/.gitignore`.

---

## 4. Cái bẫy đã gặp ở từng mục

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
một chế độ lỗi riêng cần đo được. Dấu hiệu nó dùng là **tên báo cáo**
("Bảng cân đối kế toán" của TT200 so với "Báo cáo tình hình tài chính" của
TT99), và tên đó **đã đối chiếu văn bản, đúng**.

> **Phần suy luận về ký hiệu mẫu biểu ở mục này ĐÃ BỊ BÁC BỎ.** Bản trước
> lập luận rằng `"B 01"` nằm trong `"B 01a"` nên marker TT200 phải mang
> `(?!\s*a)`. Đối chiếu Công báo cho thấy tiền đề sai — xem mục 10.

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

**B4.** Ba chỗ suýt sai khi mở bộ chỉ tiêu, cả ba đều là lỗi im lặng.

*Một,* dựng ma trận TT200 trên toàn bộ `FIELD_MAP` sẽ kéo theo
`tai_san_sinh_hoc_ngan_han` — chỉ tiêu TT200 không có — và bịa ra một cột
toàn 0 không tồn tại, làm sai luôn chiều không gian null của TT200. Đó là lý
do có `fields_for(standard)`; đừng quay lại dùng `list(FIELD_MAP)`.

*Hai,* `report()` trước đây chỉ nhắc "cột toàn 0" trong ghi chú từng dòng
của bảng, nên khi không còn chỉ tiêu nào vô hình thì báo cáo trông y hệt một
báo cáo quên in phần đó. Nay có dòng tổng quan nêu số đó kể cả khi bằng 0.

*Ba,* test giá trị thật `A @ x_ref ≈ 0` **không** bắt được việc bỏ sót hạng
tử tài sản sinh học, vì giá trị của nó trên báo cáo VNM đúng bằng 0. Cái bắt
được là test cột toàn 0. Bài học: test trên một bộ số thật không thay được
test trên cấu trúc ma trận.

**C1.** Năm nguồn ứng viên. `cost = −log(xác suất tiên nghiệm)` để cộng cost
tương đương nhân xác suất. **Bốn xác suất trong `XAC_SUAT_TIEN_NGHIEM` chưa
đo trên dữ liệu thật** — xem mục 12.

---

## 5. C2 — đã xong, hai test đỏ sửa thế nào

File [src/repair/diagnose.py](src/repair/diagnose.py), test
[tests/test_diagnose.py](tests/test_diagnose.py) (31 test, tất cả xanh).

### Test đỏ 1 — baseline 8 trả nghiệm không thưa

IRLS xuất phát từ trọng số đều nên vòng đầu ra đúng nghiệm bình phương tối
thiểu. Với hệ đối xứng như `a + b = c` thì nghiệm đó lại đều (δ = 5/3 ở cả
ba toạ độ), nên trọng số vòng sau vẫn đều và thuật toán kẹt ở **điểm bất
động thật sự**. Thêm nữa, trên chính ví dụ đó nghiệm rải đều **cũng** có
chuẩn L1 bằng 5: cực tiểu L1 suy biến, và thứ test thật sự đòi là nghiệm
**đỉnh**.

Đã thay bằng `scipy.optimize.linprog` (HiGHS), tách `delta = u − v` với
`u, v ≥ 0` rồi tối thiểu hoá `Σ(u + v)`. Nghiệm LP là nghiệm đỉnh nên số
toạ độ khác 0 không vượt quá `rank(A)`. Lợi ích ngoài việc test xanh:
baseline 8 hết là nghiệm xấp xỉ, bỏ được caveat trong paper — baseline mạnh
hơn thì kết luận về phương pháp đề xuất đáng tin hơn.

### Test đỏ 2 — baseline 9 chọn trường theo thứ tự chỉ số

`diagnose()` duyệt **hết** mọi tổ hợp ở một cardinality rồi mới chọn theo
hàm mục tiêu, còn `diagnose_fellegi_holt_donor()` trả về tổ hợp **đầu tiên**
theo thứ tự chỉ số rồi thoát — trong khi docstring của chính nó khẳng định
"Giống hệt `diagnose()` ở việc chọn TRƯỜNG nào sửa". Tức baseline trung tâm
của cả nghiên cứu đang thắng thua theo thứ tự khai báo field.

Đã sửa: donor cũng duyệt hết một cardinality rồi phân xử bằng **tổng khoảng
cách tới donor**. Trường không có giá trị donor thì lấy chính giá trị hiện
tại làm mốc. Certificate ghi thêm `lech_so_voi_donor` cho từng trường bị sửa.

---

## 6. B5 — tầng đánh giá XBRL, đã dựng xong

Module [src/eval/xbrl_tier/](src/eval/xbrl_tier/) — sáu file. Test
[tests/test_xbrl_tier.py](tests/test_xbrl_tier.py), 38 test, không cái nào
chạm mạng.

**Vì sao tồn tại:** tập gold 60 tài liệu cho khoảng 1500 trường, nhưng H2 và
H3 đo trên **SỐ LỖI**. Tỷ lệ lỗi 5–15% chỉ cho 75–225 lỗi, mà 75 quan sát
cho khoảng tin cậy rộng chừng ±0,11. Nên đây là **điều kiện để H2 và H3 có
power**. Phân vai: **XBRL lo power, gold Việt Nam lo validity.**

| File | Việc | Quyết định cần biết |
|---|---|---|
| `linkbase.py` | `*_cal.xml` → đẳng thức, → ma trận A | Parse thẳng bằng `xml.etree`, **không dùng `arelle`** |
| `facts.py` | companyfacts → bảng giá trị | **Chỉ lấy fact CÙNG MỘT hồ sơ** — (a) |
| `table.py` | Bảng hai cột kỳ | Lỗi lệch dòng/cột định nghĩa bằng hình học trang |
| `render.py` | Bảng → ảnh + bbox + chuỗi đã vẽ | Vẽ thẳng bằng Pillow, ném lỗi khi font thiếu glyph — (c) |
| `inject.py` | Inject lỗi theo taxonomy | Bảng nhầm chữ số **RỘNG HƠN** `repair.candidates` — (b) |
| `fetch.py` | Tải hồ sơ từ EDGAR | **SCRIPT CHO NGƯỜI DÙNG CHẠY** |

### Ba chỗ dễ làm hỏng nếu không biết lý do

**(a) `facts.py` chỉ lấy fact của cùng một hồ sơ.** companyfacts gộp mọi lần
công bố, nên cùng một ngày kết thúc kỳ có thể có nhiều giá trị. Trộn hai hồ
sơ vào một bảng sẽ **phá vỡ đẳng thức kế toán một cách âm thầm**, và khi đó
tầng này mất đúng thứ duy nhất làm nên giá trị của nó.
`test_chi_lay_fact_cua_dung_mot_ho_so` chốt chuyện này.

**(b) `inject.py` KHÔNG dùng chung bảng nhầm chữ số với
`repair.candidates`.** Dùng chung thì mọi lỗi inject đều nằm sẵn trong tập
ứng viên, và phương pháp đề xuất thắng vì thí nghiệm được dựng cho nó thắng.
Nên `inject` thay một chữ số bằng **bất kỳ chữ số nào khác**, còn
`repair.candidates` chỉ sinh bốn cặp hay nhầm. Phần lỗi rơi ra ngoài tập ứng
viên là phần phương pháp **phải chịu thua**. **Đừng "thống nhất" hai bảng
này lại.**

**(c) `render.py` ném lỗi khi font thiếu glyph.** Font đi kèm Pillow không
có glyph tiếng Việt có dấu: "Đơn vị tính" render ra "□n v□ t□nh" mà ảnh vẫn
trông bình thường. Nên chữ cố định mặc định **tiếng Anh**, ô trống dùng gạch
nối ASCII, và `render()` kiểm mọi ký tự rồi **ném `ValueError`**.

`RenderedTable` mang thêm khoá `texts` — chuỗi **đúng như đã vẽ** cho từng
ô. Bộ đo OCR ở mục 9 cần so với cái đã VẼ chứ không phải với giá trị số:
`1234567.0` được vẽ thành `"1,234,567"`, số âm thành `"(1,234,567)"`.

### Kết quả chạy thử toàn chuỗi

Chuỗi `linkbase → bảng → inject → sinh ứng viên → chẩn đoán` đã chạy thông
đầu-cuối trên bảng 8 chỉ tiêu, 3 đẳng thức.

> **Bảng 8 chỉ tiêu này KHÔNG phải bộ chỉ tiêu TT200/TT99.** Dự án có hai
> bảng số tách biệt hẳn nhau, và trộn chúng là hiểu sai cả mục 7 lẫn mục 12:
>
> | | Bộ chỉ tiêu Việt Nam | Bảng tầng XBRL |
> |---|---|---|
> | Khai ở | `src/fields_config.py` | `src/eval/xbrl_tier/` |
> | Nguồn | Thông tư 200 và 99 | Linkbase hồ sơ SEC (Mỹ) |
> | Quy mô | 20–21 chỉ tiêu, 7 đẳng thức | 8 chỉ tiêu, 3 đẳng thức |
> | Dùng để | Trích xuất báo cáo Việt Nam thật | Sinh lỗi có kiểm soát cho H2/H3 |
>
> `diagnose()` không biết gì về bộ chỉ tiêu nào cả — nó nhận `A` và
> `field_order` từ nơi gọi, nên chạy trên **cả hai**.

Kết quả:

1. Inject `DIGIT_SUB` vào `Cash` (`1 → 9`) làm đúng **1 đẳng thức** vi phạm.
2. Giá trị thật **không** nằm trong tập ứng viên vì cặp `1→9` không thuộc
   bốn cặp hay nhầm. `diagnose()` trả `ABSTAIN` — **thua đúng**.
3. Baseline 9 trả `REPAIRED` nhưng **sửa sai trường** — cho ra bảng cân đối
   hoàn hảo và sai sự thật. Đúng thứ `fabrication_rate` sinh ra để bắt.

Sau `inject_scale_toan_cuc` với `k = 3`, **mọi đẳng thức vẫn thoả tuyệt
đối** — bản chạy được của chứng minh ở `constraints.py`.

---

## 7. Trần `max_changes` và tách ABSTAIN — `9c3f7c9`

Trong lúc chạy thử B5, `diagnose()` **hết 30 giây** trên bài toán chỉ có 8
chỉ tiêu và 87 ứng viên:

| Ca | `max_changes` | Kết quả | Thời gian |
|---|---|---|---|
| Lỗi KHÔNG sửa được | không đặt | ABSTAIN vì **hết giờ** | **30.158 ms** |
| Lỗi KHÔNG sửa được | 2 | ABSTAIN vì **vô nghiệm** | **16 ms** |
| Lỗi sửa được | không đặt | REPAIRED, đúng `Cash` | 1,8 ms |

**Chi phí nằm trọn ở việc chứng minh KHÔNG có nghiệm**, mà đó lại là ca
thường gặp vì tập ứng viên đóng cố ý không chứa mọi cách sửa.

Đã chốt `MAX_CHANGES_MAC_DINH = 2`, áp cho `diagnose()` **và** baseline 9,
vì H3 so ở cùng ngân sách. Baseline 8 **không** áp trần có chủ đích: delta
của nó chạy tự do trong `ℝⁿ`, và nghiệm đỉnh đã tự giới hạn số toạ độ khác
0 không vượt quá `rank(A)`.

**Đây là hạn chế của phương pháp, không phải chi tiết cài đặt.** Tài liệu có
ba trường cùng sai sẽ không được sửa. Đã ghi vào mục Sửa đổi của
`PREREGISTRATION.md`. **Bảng kết quả phải báo cáo tỷ lệ tài liệu rơi vào ca
đó.**

### Tách ABSTAIN — đừng gộp lại

`Diagnosis` có `ma_ly_do`, lấy giá trị trong một **tập đóng**:

| Mã | Nghĩa |
|---|---|
| `vo_nghiem` | Đã vét cạn **MỌI** tổ hợp và không có nghiệm |
| `vuot_tran_thay_doi` | Hết tổ hợp trong trần — **chưa duyệt tới tổ hợp lớn hơn** |
| `het_gio` | Hết ngân sách thời gian |
| `thieu_gia_tri` | Không dựng được vector nên không kiểm được ràng buộc |
| `bo_giai_that_bai` | Bộ giải LP của baseline 8 không trả nghiệm |
| `""` | Không ABSTAIN |

Luận điểm chống bịa phát biểu là *không cách đọc nào của tài liệu này làm
bảng cân đối được*. **Chỉ `vo_nghiem` mới chứng minh được điều đó.**
`vuot_tran_thay_doi` chỉ nghĩa là ta đã không tìm. Gộp hai thứ lại là tính
công cho phương pháp ở những ca nó không chứng minh được gì.

---

## 8. Phần F đã xong — và một lỗi CI nằm im từ `f1d236e`

Tám mục dọn dẹp của BUILD-SPEC Phần F đều đã làm. Ba chỗ đáng nhớ:

**CI đang hỏng mà không ai biết.** Bước cài của workflow liệt kê tay
`pytest ruff numpy pillow openai python-dotenv`, không có `scipy`, trong
khi `repair/diagnose.py` import `scipy.optimize.linprog` ở mức module từ
`f1d236e`. Hậu quả không phải một test đỏ mà là pytest hỏng ở bước
**collect** — cả 31 test của `test_diagnose.py` biến mất. Nó lọt lưới vì CI
chỉ chạy khi push lên `main` và khi mở PR, còn loạt việc này nằm trên
`research`. Đã kiểm chứng bằng cách chặn import `scipy` để mô phỏng đúng môi
trường CI, rồi sửa danh sách và ghi kèm lý do nó phải phủ mọi import mức
module.

**`meta["early_stop"]` là khoá tường minh, và nó tồn tại vì phép ĐO.**
Nhánh `PATIENCE_PAGES` dừng khi mới đủ field BẮT BUỘC, tức cố ý bỏ qua phần
đuôi tài liệu. Sau B4 mở rộng bộ trường, một chỉ tiêu mới nằm ở phần đuôi đó
sẽ có tỷ lệ "không đọc được" cao — nhưng đó là tạo tác của điều kiện dừng,
và **không nhìn ra được từ bảng kết quả** vì trường bị bỏ qua và trường đọc
hỏng đều là một ô null. Cờ `DISABLE_EARLY_STOP=true` tắt hẳn, cùng vai với
`DISABLE_CONSTRAINT_GATE`.

**Test khoá threading đã được kiểm chứng đúng cách spec đòi.** Thay
`_totals_lock` bằng `contextlib.nullcontext()` rồi chạy lại: đỏ cả 3/3 lượt.

Mọi thay đổi trong loạt này đều được kiểm bằng cách **đục thủng đúng tính
năng mà test canh, rồi xác nhận test đỏ** — tổng 14 đột biến, tất cả đều bị
bắt.

---

## 9. Engine OCR — đã quyết: GIỮ EasyOCR

BUILD-SPEC nói rõ mục này "không được để trống". Đã đo, không đổi engine.

Module [src/eval/ocr_compare.py](src/eval/ocr_compare.py), báo cáo ở
`data/output/ocr_engine_easyocr.md` (đã gỡ khỏi `.gitignore`).

**Vì sao đo được ngay mà không cần tập gold:** `render.py` đã cho ảnh bảng,
bbox từng ô và chuỗi đúng như đã vẽ. Ground truth mức ô có sẵn, chính xác
tuyệt đối, không tốn một phút gán nhãn.

Kết quả trên 45 ô số, phổ độ lớn 4–13 chữ số:

| Ảnh | Levenshtein | Đúng con số | Không ra số |
|---|---:|---:|---:|
| sạch | 0,999 | 0,978 | 0,022 |
| mờ | 1,000 | 1,000 | 0,000 |
| nhiễu | 1,000 | 1,000 | 0,000 |
| **độ phân giải thấp** | **0,934** | **0,467** | **0,000** |

**Kết luận 1 — giữ EasyOCR.** Con số 0,646 của Ajayi et al. đo trên bảng
KHOA HỌC. Trên ô số thì 0,999. Đây là câu trả lời có số liệu cho reviewer.

**Kết luận 2, quan trọng hơn với luận điểm của bài.** Ở độ phân giải thấp,
chỉ số ký tự vẫn báo 0,934 trong khi **chưa tới một nửa** số đọc ra là đúng.
Và tỷ lệ "không ra số" bằng **0** — mọi ô sai đều parse ra một con số hợp
lệ. Đó chính là lỗi câm, đo được, trên dữ liệu có ground truth hoàn hảo.
Hệ quả: **không được báo cáo Levenshtein accuracy một mình.**

### Việc còn chờ người quyết

Cặp nhầm chữ số quan sát được ở độ phân giải thấp: `9→0` (23 lần),
`6→0` (8), `9→8` (1). `repair/candidates.py` đang sinh ứng viên từ bốn cặp
`(0,8) (1,7) (3,8) (5,6)` — **cặp áp đảo `9→0` không nằm trong đó**.

**CHƯA áp vào, và cố ý.** Đây mới là một engine, một bảng tổng hợp, một mức
xuống cấp. Lưu ý ranh giới ở mục 6(b): việc hiệu chỉnh `candidates` theo số
đo là hợp lệ; việc cho `inject` sinh lỗi theo đúng bảng mà `candidates` biết
cách sửa thì không.

### Bẫy đã gặp khi dựng module này

`python src/eval/ocr_compare.py` đặt `src/eval/` lên **đầu** `sys.path`, và
`eval/metrics.py` ở đó che mất `src/metrics.py` của pipeline. Lỗi nổ ra tận
trong `ocr_baseline` với `ImportError: cannot import name 'timer' from
'metrics'`, trỏ vào một file chẳng liên quan. Cùng họ với vụ `src/types.py`.
Khối `__main__` của `ocr_compare.py` tự gỡ thư mục script khỏi `sys.path`.
`fetch.py` đã kiểm, KHÔNG dính lỗi này.

---

## 10. MỐC 1 — ĐÃ ĐÓNG

Người dùng đã tải năm file Công báo vào `data/legal/` (đã gitignore). Trích
bằng `pdftotext -layout` cho PDF và `antiword -m UTF-8.txt` cho `.doc` cũ.

| File | Chuẩn | Nội dung |
|---|---|---|
| `2015_287 + 288-200_2014_TT-BTC.pdf` | TT200 | Điều 88–113; đẳng thức B01 ở Điều 112, B02 ở Điều 113 |
| `2015_289 + 290-200_2014_TT-BTC.pdf` | TT200 | Điều 114–130; đẳng thức B03 ở Điều 114 |
| `2025_1577 + 1578_99-2025-TT-BTC.doc` | TT99 | **Phụ lục IV Mục 1 — biểu mẫu**, tức bảng mã số gốc |
| `2025_1579 + 1580_99-2025-TT-BTC.doc` | TT99 | Báo cáo tình hình tài chính + B02 |
| `2025_1581 + 1582_99-2025-TT-BTC.doc` | TT99 | cuối B02 + B03 + B09 |

**Bộ này đã đủ, không cần tìm thêm văn bản.** Năm file phủ trọn chương báo cáo
tài chính của cả hai Thông tư, gồm cả B09 mà dự án chưa dùng tới.

Đừng bỏ qua số `1577 + 1578` vì bản trước của tài liệu này ghi nhầm là nó
"không chứa phần báo cáo tài chính". Nó không chứa đẳng thức viết bằng lời,
nhưng nó chính là **Phụ lục IV Mục 1 — BIỂU MẪU BÁO CÁO TÀI CHÍNH**, tức đúng
cái nguồn mà `BUILD-SPEC.md` mục A3 đòi phải lấy mã số dòng TT99 từ đó thay vì
từ bài tóm tắt trên mạng. Biểu mẫu còn in sẵn đẳng thức ngay trong tên chỉ
tiêu: `TỔNG CỘNG TÀI SẢN (280 = 100 + 200)`.

Chi tiết đầy đủ ở **Phụ lục A** cuối file này. Tóm tắt:

### Ba đẳng thức repo đang dùng: đều ĐÚNG

- `100 + 200 = 270/280` — khớp nguyên văn
- `300 + 400 = 270/280` — đúng, nhưng là đẳng thức **suy ra**: văn bản viết
  `Mã số 440 = Mã số 300 + Mã số 400` rồi viết **riêng** `Tổng cộng Tài sản
  = Tổng cộng Nguồn vốn`
- `11 + 20 = 10` — khớp `Mã số 20 = Mã số 10 − Mã số 11`

### Kết quả đo — `python src/constraints_scenarios.py`

| KB | Kịch bản | Chỉ tiêu | Định vị được | Bước này mua được |
|---|---|---:|---:|---|
| A | Hiện tại | 11 | 1/11 (9%) | — |
| B | **+ Tổng cộng nguồn vốn (440)** | 12 | 2/12 (17%) | **+1 → +1, tỷ lệ 1,00** |
| C | + chuỗi lãi lỗ B02 | 16 | 3/16 (19%) | +4 → +1, tỷ lệ 0,25 |
| D | + phân rã Tài sản ngắn hạn | 20 | 5/20 (25%) | +4 → +2, tỷ lệ 0,50 |
| E | + B03 và liên kết chéo | 26 | 7/26 (27%) | +6 → +2, tỷ lệ 0,33 |

**Bước rẻ nhất là B: thêm ĐÚNG MỘT chỉ tiêu.** Tổng cộng nguồn vốn nằm ngay
trong hai đẳng thức nên định vị được lập tức, và là con số in ở cuối bảng
cân đối — rẻ cả về chi phí gán nhãn.

> **MỘT KẾT LUẬN CŨ ĐÃ BỊ BÁC BỎ.** Bản trước của mục này dùng đẳng thức
> **giả thuyết** và nói liên kết chéo hiệu quả **gấp đôi** phân rã. Sai: hai
> đẳng thức từng được giả định — liên kết Lợi nhuận chưa phân phối (B01) với
> Lợi nhuận sau thuế (B02), và phân rã Vốn chủ sở hữu — **không có trong văn
> bản**. Với đẳng thức thật, liên kết chéo cho tỷ lệ 0,33, **thấp hơn** phân
> rã 0,50. Đã chốt bằng `test_lien_ket_cheo_KHONG_hieu_qua_hon_phan_ra`.
>
> **Bài học, đã ghi vào docstring `constraints_scenarios.py`:** đừng để đẳng
> thức giả thuyết chạy vào bảng kết quả, kể cả khi chúng hợp lý về kế toán.

### Định luật rút ra — thứ quyết định hướng đi của H0

> Một chỉ tiêu định vị được **khi và chỉ khi** tập đẳng thức chứa nó khác
> tập đẳng thức của **mọi** chỉ tiêu khác.

Trong một đẳng thức phân rã đơn lẻ `a + b = tổng` thì **cả ba** nằm ngoài
tầm — hai thành phần có cột bằng nhau, còn cột của tổng là `[−1]` tỷ lệ với
cột `[1]`. Phân rã một chỉ tiêu làm **chính nó** định vị được nhưng sinh ra
một tầng lá mới; đó là cái cối xay, và mỗi lá mới tốn chi phí gán nhãn.

`minimal_localizing_set()` trả `None` ở **mọi** kịch bản, và `hang_ton_kho`
không định vị được ở kịch bản nào — mà đó đúng là chỉ tiêu đã có lỗi đọc
thật trên báo cáo VNM. **Ràng buộc kế toán chứng minh được là không bao giờ
bắt được lỗi đó.** Kết luận cho bài: ràng buộc đơn thuần không đủ, trọng số
dồn sang mỏ neo đơn vị tính (proposal 6.3) và bước đọc lại (6.2) — đúng như
mục 6.1 đã lường trước.

### Liên kết chéo có thật, khai báo tường minh

TT200 Điều 114, mục "Tiền và tương đương tiền cuối kỳ (Mã số 70)":

> Chỉ tiêu này bằng số "Tổng cộng" của các chỉ tiêu Mã số 50, 60 và 61 và
> **bằng chỉ tiêu Mã số 110 trên Bảng cân đối kế toán kỳ đó**.

TT99 nói y hệt. Thêm: `Mã số 60` (tiền đầu kỳ) = `Mã số 110` cột "Số đầu
kỳ". Ghép lại: `B01.110 (cuối kỳ) = B01.110 (đầu kỳ) + lưu chuyển tiền
thuần + ảnh hưởng tỷ giá` — nối bảng cân đối kỳ này với **kỳ trước**, chính
là câu hỏi proposal mục 6.1(d).

### `FORM_MARKERS` đã sai, đã sửa — `023321c`

TT200 dùng ĐỦ CẢ `B01-DN`, `B01a-DN`, `B01b-DN`. Nguyên văn: *"Bảng cân đối
kế toán giữa niên độ (dạng đầy đủ) — Mẫu số B01a-DN"*. Hậu tố phân biệt
**kỳ báo cáo**: không hậu tố = năm, `a` = giữa niên độ dạng đầy đủ tức
**quý**, `b` = tóm lược. TT200 nói rõ biểu mẫu giữa niên độ dùng **cùng bộ
mã số**.

Hậu quả bản cũ: lookahead `(?!\s*a)` làm marker TT200 trượt mọi trang
`B01a-DN`, tức trượt mọi báo cáo **quý** theo TT200 — đúng loại tài liệu dự
án xử lý, gồm cả VNM Q1/2026. Khi trượt thì `extract_field_by_code()` trả
`None` và **đường dự phòng theo mã số tắt hẳn, im lặng**.

Hướng sửa: bỏ hẳn việc dùng ký hiệu mẫu biểu để phân biệt chuẩn, vì
`detect_standard()` đã làm việc đó bằng tên báo cáo. `FORM_MARKERS` thành
dict phẳng; `form_markers_for(standard)` → `marker_for_form(form)`.

### Hai chỗ khác nhau giữa hai chuẩn — nguồn lỗi câm

- **Mã 270 mang nghĩa KHÁC HẲN.** TT200: "Tổng cộng tài sản". TT99: "Tài sản
  dài hạn khác" (`270 = 271+272+273+274`). Tra nhầm bảng mã thì đọc ra một
  con số hợp lệ của chỉ tiêu hoàn toàn khác. Đây là lý do `standard` phải là
  tham số **bắt buộc** của `extract_field_by_code()`.
- Dự phòng giảm giá hàng tồn kho: mã **149** ở TT200, mã **142** ở TT99.

### Trục TT200 → TT99 hẹp hơn tưởng, nhưng KHÔNG rỗng

Ba đẳng thức của bộ chỉ tiêu cũ giống hệt nhau ở hai chuẩn. Khi mở sang bộ 7
đẳng thức của kịch bản D thì lộ ra một khác biệt thật, và nó là **chỗ duy
nhất** trong cả cấu hình mà hai chuẩn không đẳng cấu:

```
TT200:  100 = 110 + 120 + 130 + 140 + 150          (150 = TSNH khác)
TT99:   100 = 110 + 120 + 130 + 140 + 150 + 160    (150 = TS sinh học, 160 = TSNH khác)
```

Nên TT200 có **20** chỉ tiêu và TT99 có **21**, hạng 7 ở cả hai, chiều null
13 và 14. Bỏ hạng tử tài sản sinh học đi thì đẳng thức TT99 lệch đúng bằng
giá trị đàn vật nuôi hoặc vườn cây với doanh nghiệp nông nghiệp — cảnh báo
SAI, ở đúng nhóm doanh nghiệp mà tập gold nhắm tới.

Dù vậy sáu trên bảy đẳng thức vẫn trùng nhau, nên hệ quả cho bài viết giữ
nguyên: ablation số 8 (transfer TT200 → TT99) kiểm chủ yếu **tầng nhận diện
và tra cứu mã số** — hệ có nhận đúng chuẩn rồi tra đúng bảng không — chứ
**không** kiểm khả năng tổng quát hoá của phần suy luận ràng buộc. Phát biểu
hẹp hơn bản đăng ký ban đầu ngụ ý, và phải viết đúng phạm vi đó.

### MỐC 1 ĐÃ ĐÓNG — bộ chỉ tiêu chốt ở kịch bản D

Người dùng chốt ngày 23/08/2026: **kịch bản D**, và **không** gán nhãn cột kỳ
so sánh. Đã ghi vào mục Sửa đổi của [PREREGISTRATION.md](PREREGISTRATION.md)
và thi công ở commit `4064519`.

**Đề xuất trong bản bàn giao trước là kịch bản B, và nó SAI vì dùng nhầm
thước.** Ghi lại đây để phiên sau đừng lặp lại: bảng kịch bản xếp hạng theo
"số chỉ tiêu định vị được trên mỗi chỉ tiêu thêm vào", một chỉ số có hai lỗ.
Nó gộp *cột toàn 0* với *lẫn lớp* làm một, trong khi cột toàn 0 nghĩa là vô
hình với **cả H1 lẫn H2** còn lẫn lớp thì H1 vẫn bắt được. Và nó nhị phân
hoá "định vị được", trong khi H2 báo cáo bằng Top-1/Top-3 — lớp lẫn 2 đạt
trần Top-3 100%, lớp lẫn 5 chỉ đạt 60%.

Đo lại theo đúng chỉ số H1/H2 dùng:

| KB | Chỉ tiêu | **Vô hình** | Trần Top-1 | Trần Top-3 | Ô gán nhãn (×60) |
|---|---:|---:|---:|---:|---:|
| A cũ | 11 | 3 | 0,36 | 0,73 | 660 |
| B | 12 | 3 | 0,42 | 0,75 | 720 |
| C | 16 | 1 | 0,50 | 0,94 | 960 |
| **D chốt** | **20–21** | **0** | **0,50** | **0,90** | **1 200** |
| E | 26 | 0 | 0,54 | 0,96 | 1 560 |

**Cái bẫy đọc bảng này, và nó sẽ quay lại khi dựng bảng cho paper:** Top-3
của D thấp hơn C nhìn như bước lùi, nhưng đo trên đúng 16 chỉ tiêu của C thì
D cho **0,975** so với 0,938 của C — không chỉ tiêu nào xấu đi. Trung bình
tụt vì D thêm bốn chỉ tiêu vốn dĩ khó. Đây là hiệu ứng cấu thành, và **bảng
kết quả phải in Top-k kèm phân rã theo lớp lẫn**, nếu không người đọc sẽ rút
ra kết luận ngược.

Con số cho cột kỳ so sánh, trả lời proposal mục 6.1(d): thêm cột kỳ trước
nhân đôi số chỉ tiêu mà trần Top-1 và Top-3 **không đổi một điểm nào**. Hai
cột thoả cùng một hệ đẳng thức độc lập nên ma trận thành khối chéo
`[[A,0],[0,A]]` — không residual nào nối chúng. Mỏ neo chéo ở proposal 6.3
vẫn giữ, nhưng nó là kiểm biên độ nên chỉ cần **một** con số tổng tài sản kỳ
trước, không cần cả cột.

---

## 11. Chỗ đã đi khác `BUILD-SPEC.md` — có chủ đích, đã kiểm chứng

Ghi lại để phiên sau không "sửa ngược" theo spec.

1. **`src/types.py` → `src/extraction_types.py`.** Repo import phẳng với
   `pythonpath = src`, nên `src/types.py` che khuất module `types` của thư
   viện chuẩn, mà `enum` lại `from types import MappingProxyType` — trình
   thông dịch chết lúc khởi động với lỗi circular import không hề gợi ý
   nguyên nhân. Đã kiểm chứng bằng cách chạy thật trước khi đổi tên.
2. **Test đơn điệu của `minimal_localizing_set` kiểm chiều NGƯỢC với spec.**
   Spec đòi chốt "thêm field không làm bộ tối thiểu NHỎ ĐI" — chiều đó sai
   về toán: tập ứng viên rộng hơn chỉ thêm lựa chọn.
3. **Báo cáo identifiability gỡ khỏi `.gitignore`.** Spec bảo ghi vào
   `data/output/` nhưng cả thư mục đó bị ignore, nên artifact Mốc 1 sẽ không
   bao giờ tới tay người chủ trì. Sau này thêm ngoại lệ tương tự cho
   `ocr_engine_*.md`.
4. **Trần ứng viên mỗi trường để 12 thay vì 10.** Riêng nguồn `scale` đã
   đóng góp 6 ứng viên có cấu trúc khác hẳn nhau. Kèm trần riêng cho mỗi
   nguồn, vì xếp thuần theo cost sẽ để biến thể nhầm chữ số của một con số
   14 chữ số chiếm hết chỗ.
5. **Không dùng DeLong cho H1**, khác `ADDENDUM` mục 3. DeLong xử lý đúng
   tương quan giữa các đường ROC nhưng vẫn giả định quan sát độc lập, mà các
   trường trong cùng tài liệu thì không.
6. **Baseline 8 dùng `scipy.optimize.linprog`.** scipy **đã nằm sẵn trong
   image** theo chuỗi `easyocr → scikit-image → scipy`, nên khai báo nó là
   nói ra một phụ thuộc đang dùng chứ không phải cài thêm; `pulp` thì chưa
   có và kéo theo binary CBC.
7. **B5 có SÁU module thay vì bốn.** `table.py` vì hai trong năm chế độ lỗi
   được định nghĩa bằng hình học của trang. `facts.py` vì spec không nói con
   số lấy từ đâu.
8. **`render.py` vẽ thẳng bằng Pillow thay vì dựng HTML rồi chụp.** Đường
   HTML cần trình duyệt không đầu trong image — đúng cái giá đã từ chối trả
   cho MILP ở C2. Vẽ thẳng còn cho **bbox chính xác từng ô miễn phí**.
   SynFinTabs vẫn nên trích dẫn, nhưng **khác biệt phải giữ**: nội dung của
   họ là số ngẫu nhiên nên không đẳng thức kế toán nào đúng trên đó.
9. **`FIELDS_ONLY_IN` và `fields_for()` không có trong spec.** Spec giả định
   mọi chỉ tiêu tồn tại ở cả hai chuẩn và bảo test phải chốt điều đó
   (`test_moi_bang_config_phu_du_field`). Đối chiếu văn bản cho thấy giả
   định sai: Tài sản sinh học ngắn hạn chỉ có ở TT99. Nới test để chấp nhận
   mọi khoảng trống thì nó không còn phân biệt được "chuẩn không có chỉ tiêu
   này" với "quên khai mã" — nên thay bằng khai báo tường minh, cộng hai test
   canh chiều ngược lại (khai báo thừa, và khai báo trỏ tới chỉ tiêu không
   tồn tại).
10. **`src/constraints_scenarios.py` và `src/eval/ocr_compare.py` là module
   mới không có trong spec.** Cái đầu để trả lời câu hỏi thật của Mốc 1 bằng
   số thay vì cảm tính; cái sau để trả lời mục "engine OCR không được để
   trống" mà không phải chờ tập gold.

---

## 12. Chưa làm

Theo thứ tự phụ thuộc trong `BUILD-SPEC.md` phần E.

| Mục | Trạng thái | Chặn bởi |
|---|---|---|
| C2, B5, Phần F, README | **XONG** | — |
| Guideline gán nhãn, bảng đối chiếu Mốc 1 | **XONG** | — |
| Đối chiếu Công báo | **XONG** — mục 10 | — |
| **B4** mở rộng bộ trường | **XONG** — `4064519` | — |
| **MỐC 1** | **ĐÓNG** — `df96ff2` | — |
| Bỏ qua đẳng thức khi thiếu thành phần | **XONG** — phương án C, `ada6f75` | — |
| Nhận diện chuẩn thật (nguồn `nhan_dien`) | **Chưa** — bước D, Phụ lục B | Quyết định của người |
| **C3** vòng lặp đọc lại | Chưa | **MỐC 3** — mục 13 |
| **C4** verdict ba trạng thái | Chưa | C3 |
| **D2** runner / **D3** bảng / **D4** hình | Chưa | C4, rồi D2 |

### ĐÃ QUYẾT VÀ ĐÃ THI CÔNG — 24/08/2026

Người dùng chốt **phương án C**: phân biệt "dòng vắng mặt" với "dòng đọc
hỏng" bằng cách dò **mã số dòng** trên text OCR, và ghi số `0` của dòng vắng
mặt vào **cả `data` đầu ra** kèm khoá trạng thái tường minh.

Đã thi công ở bốn commit — chi tiết đầy đủ, kèm bẫy đã gặp và việc còn lại, ở
**Phụ lục B** cuối file này:

| Commit | Nội dung |
|---|---|
| `fa5c6d2` | Chuẩn đi tới nơi kiểm đẳng thức; meta hợp nhất thay vì đè |
| `88a77f5` | Bộ chỉ tiêu đi theo chuẩn ở prompt, trích xuất, điều kiện dừng sớm |
| `19fe938` | Oracle `tim_theo_ma_so()` nói ra lý do; sửa lỗi mượn số dòng dưới |
| `ada6f75` | Probe OCR + `dien_dong_vang_mat()`; đẳng thức phân rã chạy được |

**Kết quả đo được.** Trên bộ số kiểu VNM với hàng tồn kho đọc nhầm sang dòng
dự phòng — lỗi có thật, ví dụ mở đầu của proposal — cảnh báo phân rã tài sản
ngắn hạn đi từ **không có** sang **bắt được**.

**Việc còn lại (bước D):** `chon_chuan()` vẫn chỉ có nguồn `tham_so` và
`mac_dinh`, chưa có `nhan_dien`. Trên cấu hình mặc định mọi tài liệu vẫn được
xử như TT99 vì lùi mặc định — nay có kêu ra log và ghi vào
`meta["standard_nguon"]` thay vì im lặng. Vướng mắc đã khảo sát và ghi ở
NOTES: tiêu đề báo cáo, dấu hiệu duy nhất phân biệt hai chuẩn, gần như chắc
chắn nằm NGOÀI vùng bảng đã cắt vì `PADDING` chỉ có 8 pixel.

Phần mô tả bên dưới giữ nguyên làm hồ sơ bài toán ban đầu.

### Việc mở ra từ B4, cần quyết trước khi chạy pipeline trên tài liệu thật

`validate_result()` bỏ qua **cả đẳng thức** nếu bất kỳ thành phần nào là
`None` ([src/validation.py:168](src/validation.py#L168)). Với bộ đẳng thức
cũ — 3 đẳng thức trên các chỉ tiêu đầu bảng vốn luôn được in — điều đó vô
hại. Với đẳng thức phân rã tài sản ngắn hạn (5 thành phần ở TT200, 6 ở TT99)
thì chỉ cần **một** dòng không đọc được là đẳng thức giá trị nhất im lặng
không chạy.

Phía **gán nhãn tay** đã xử lý: `ANNOTATION-GUIDELINE.md` mục 3.4 nay quy
định dòng vắng mặt ghi `0` chứ không phải `null`, vì TT99 mục 1.2.3 bảo đảm
chỉ tiêu không có số liệu được miễn trình bày — vắng mặt là *bằng không*,
không phải *chưa biết*. Chính báo cáo VNM in công thức rút gọn của nó,
`100 = 110 + 120 + 130 + 140 + 160`, bỏ hẳn mã 150.

Phía **pipeline** thì chưa. VLM và OCR đều trả `None` cho dòng không đọc
được, và ở đó `None` thật sự nhập nhằng giữa "dòng vắng mặt" với "đọc hỏng".
Chưa sửa vì đây là đánh đổi có hai chiều thật, cần người quyết:

- Coi `None` là 0 → đẳng thức chạy được trên phần lớn tài liệu, nhưng một
  thành phần đọc hỏng sẽ sinh cảnh báo lệch đúng bằng giá trị của nó. Lệch
  đó là **cảnh báo đúng hướng** (có gì đó sai thật) nhưng **quy trách nhiệm
  sai chỗ**, và C1/C2 sẽ đi tìm ứng viên cho nhầm chỉ tiêu.
- Giữ nguyên → an toàn nhưng đẳng thức mới gần như không bao giờ chạy, tức
  phần lớn cái mà Mốc 1 mua được sẽ không tới được pipeline.

Gợi ý nếu cần một hướng: phân biệt được hai ca bằng chính **mã số dòng** —
nếu `extract_field_by_code()` tìm thấy dòng nhưng không đọc ra số thì là đọc
hỏng, còn không tìm thấy dòng thì là vắng mặt. Đường đó cần B3 provenance,
vốn đã có. Dù chọn hướng nào cũng phải ghi trạng thái **tường minh** vào kết
quả, đừng để suy ra từ sự vắng mặt của khoá khác.

### Hằng số chưa hiệu chỉnh — đo lại trước khi tin

1. `TOTAL_ASSETS_BOUNDS` trong `fields_config.py` — hiện `(1e10, 1e15)`,
   dựa trên suy luận, chưa dựa trên phân phối đo được.
2. `XAC_SUAT_TIEN_NGHIEM` trong `repair/candidates.py` — đi **thẳng** vào
   hàm mục tiêu của C2, nên đặt sai thì thuật toán vẫn chạy và vẫn cho
   nghiệm, chỉ là ưu tiên sai loại sửa.
3. `FIELD_RATIO_BOUNDS` và `REVENUE_TO_ASSETS_LIMIT` — hiệu chỉnh trên
   **đúng một công ty** (VNM Q1/2026). Người dùng đã ra chỉ thị rõ: **không
   chỉnh các ngưỡng này khi dữ liệu mới chỉ có một công ty**.
4. `MAX_CHANGES_MAC_DINH = 2` — **ĐÃ ĐO LẠI 24/08/2026 trên bộ chỉ tiêu đã
   chốt, giữ nguyên giá trị 2.** Số đo cũ lấy trên bảng 8 chỉ tiêu của tầng
   XBRL; số mới lấy trên chính ma trận ràng buộc TT200/TT99, ca vô nghiệm
   (đắt nhất), 5 ứng viên mỗi chỉ tiêu:

   | Chuẩn | Chỉ tiêu | Ứng viên | `max_changes` | Thời gian |
   |---|---:|---:|---:|---:|
   | TT200 | 20 | 100 | 2 | **33 ms** |
   | TT200 | 20 | 100 | 3 | 958 ms |
   | TT200 | 20 | 100 | không đặt | **hết giờ 30 s** |
   | TT99 | 21 | 105 | 2 | **56 ms** |
   | TT99 | 21 | 105 | 3 | 1 128 ms |
   | TT99 | 21 | 105 | không đặt | **hết giờ 30 s** |

   Kết luận: trần 2 vẫn thừa sức ở bộ 21, và **mỗi nấc `max_changes` đắt lên
   khoảng 20 lần**. Bỏ trần thì vẫn hết giờ y như ở bộ 8 — chi phí nằm trọn ở
   việc chứng minh KHÔNG có nghiệm, đúng như kết luận cũ.

   Hệ quả cho việc mở rộng bộ chỉ tiêu về sau: ở `max_changes = 2` chi phí đi
   theo `C(n,2)`, nên tăng từ 21 lên 40 chỉ tiêu chỉ đắt lên chừng 3,7 lần —
   vẫn dưới một phần tư giây. **Ràng buộc thật khi mở rộng là chi phí gán
   nhãn tay, không phải chi phí tính toán.**
5. Bảng bốn cặp nhầm chữ số trong `repair/candidates.py` — cặp áp đảo `9→0`
   **không nằm trong bảng**. Lý do chưa sửa ở mục 9.
6. `MAX_UPLOAD_BYTES = 50 MB` trong `api.py` — chọn theo đúng một tài liệu.

---

## 13. MỐC 3 — ĐÃ CHẠY ĐẦY ĐỦ, VẪN CHƯA KẾT LUẬN ĐƯỢC

**Cập nhật 24/08/2026.** Đã tải 3 hồ sơ 10-K của Apple từ EDGAR (`fetch.py`
chạy được từ shell trên máy người dùng — cảnh báo "container không ra được
sec.gov" trong docstring chỉ đúng với Docker) và chạy pilot bằng
[src/eval/moc3.py](src/eval/moc3.py). Kết quả ở
`data/output/moc3_pilot_apple.md`.

**Pilot làm đúng việc nó được giao: lộ trục trặc đường ống.** Ba chỗ, hai
trong đó là lỗi của chính runner và đã sửa:

1. **Rò rỉ đáp án** — donor tính trung vị trên cả hồ sơ đang xét, nên 32% chỉ
   tiêu có donor trùng khít giá trị thật. Baseline 9 khi đó là oracle. Đã sửa;
   sau khi sửa, chỉ số chống bịa **đảo chiều** sang có lợi cho đề xuất.
2. **Tắt mất nguồn ứng viên quan trọng nhất** — gọi `generate()` không truyền
   `o_lan_can`, tức bỏ hẳn việc đọc lại ô lân cận, đúng cơ chế cần chứng minh.
   Đã sửa.
3. **Cột kỳ so sánh rỗng** — 0/158 chỉ tiêu có giá trị ở kỳ thứ hai, nên
   COL_SHIFT không inject được. **CHƯA SỬA.**

**VÌ SAO CHƯA KẾT LUẬN ĐƯỢC, và đừng coi số hiện tại là kết quả Mốc 3:**
donor vẫn lấy từ hồ sơ của **cùng một công ty**, trong khi Fellegi-Holt kinh
điển lấy donor từ một tổng thể nhiều thực thể — nên baseline 9 vẫn đang được
lợi thế giả tạo. Cộng thêm chỉ 3 trong 4 chế độ lỗi chạy được, và chỉ số định
vị đang phạt việc ABSTAIN, tức đo mức sẵn sàng đoán chứ không đo độ đúng.

**Đã làm tiếp, 24/08 tối:** tải **15 công ty Mỹ đa ngành, 26 hồ sơ**, và sửa
donor để loại **cả công ty đang xét** chứ không chỉ hồ sơ đang xét (`e6c286c`).
Lượt chạy đầy đủ trên bộ này mất chừng 90 phút; kết quả ghi vào
`data/output/moc3_15congty.md`.

**Hai việc còn lại để Mốc 3 kết luận được:**

1. **Sửa việc chọn kỳ** cho cột so sánh có số — hiện 0/158 chỉ tiêu có giá trị
   ở kỳ thứ hai nên COL_SHIFT không inject được.
2. **Chốt cách tính chỉ số định vị khi một phương pháp TỪ CHỐI trả lời.** Đây
   là quyết định của người, không phải việc kỹ thuật — xem mục 16 điểm 2.

---

### Bối cảnh gốc của mốc này

`BUILD-SPEC.md` phần E:

> **MỐC 3 — sau C2, chạy baseline 9.** Nếu baseline 9 ngang bằng phương pháp
> đề xuất thì luận điểm "đọc lại nguồn" sai. Dừng, báo cáo, lùi paper về
> tầng dataset + identifiability. Đừng chạy tiếp C3 và toàn bộ ablation
> trước khi biết kết quả này.

C2 đã xong nên mốc này đang mở. Cần dữ liệu thật — container không ra được
sec.gov nên người dùng phải chạy. Quy mô đã chốt: **pilot 1 công ty, 3 hồ
sơ**, đủ để chạy đầu-cuối và lộ mọi trục trặc đường ống.

```bash
export SEC_USER_AGENT="Trần Kim Danh trankimdanh2007@gmail.com"
python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --dry-run   # xem trước
python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --out data/xbrl
```

SEC chặn IP nếu thiếu `User-Agent` có tên thật và email, hoặc quá 10
request/giây; script đặt trần 5/giây. `--dry-run` **không chạm mạng** nhưng
vẫn kiểm `SEC_USER_AGENT` và in rõ thiếu hay đủ (`2c14420`); lượt chạy thật
mới **ném lỗi** khi thiếu.

Sau khi có dữ liệu: chạy `diagnose()` so với `diagnose_fellegi_holt_donor()`
trên cùng bộ tài liệu, cùng ngân sách, cùng trần. Theo `PREREGISTRATION.md`,
hai chỉ số phải báo cáo cùng lúc — tỷ lệ lỗi câm giảm bao nhiêu, **VÀ** chỉ
số chống bịa có tăng không. Thắng chiều một mà thua chiều hai là kết quả
tiêu cực và phải nói ra. Đếm riêng `vo_nghiem` với `vuot_tran_thay_doi`.

### 13b. Lượt chạy đầy đủ 14 công ty — và phép đo giải thích nó

**24/08/2026, sau pilot Apple.** Đã chạy trên 26 hồ sơ của 14 công ty
(`data/output/moc3_15congty.md`), 400 lượt, mỗi lượt tiêm đúng 1 lỗi.

| Chỉ số | Đề xuất | Baseline 9 |
|---|---:|---:|
| Tỷ lệ lỗi câm sau sửa | 0.005 | 0.006 |
| Tỷ lệ bịa | 0.005 | 0.006 |
| Định vị đúng trường bị lỗi | 0.212 | **0.295** |
| VERIFIED / REPAIRED / ABSTAIN | 106 / 122 / 172 | 106 / 234 / 60 |

Đọc thô thì baseline 9 thắng chỉ số định vị, tức chạm điều kiện dừng của
`PREREGISTRATION.md` mục 4. **Nhưng phép đo bên dưới cho thấy con số đó
không đo phương pháp.**

#### Độ phủ ứng viên — phép đo phải chạy trước khi đọc bảng trên

Câu hỏi: khi tiêm 1 lỗi, giá trị THẬT của ô bị hỏng có nằm trong tập ứng
viên sinh từ tài liệu không? Nếu không thì việc `diagnose()` bỏ phiếu
trắng chẳng nói gì về phương pháp — nó nói tầng XBRL không chứa thông tin
để đọc lại. Kết quả ở `data/output/moc3_do_phu_ung_vien.md`:

| Chế độ lỗi | Lượt | Phủ trước trần | Phủ sau trần |
|---|---:|---:|---:|
| `sign` | 130 | 1.000 | 1.000 |
| `digit_substitution` | 130 | 0.092 | 0.046 |
| `row_shift` | 130 | 0.008 | 0.008 |
| `col_shift` | 10 | 0.000 | 0.000 |
| **TỔNG** | 400 | 0.357 | 0.343 |

Nguồn `tu_o_lan_can()` sinh đúng giá trị thật **0 lần trên 400**, dù
docstring của nó tự mô tả là "nguồn giá trị nhất".

#### Ba kết luận, theo thứ tự quan trọng

**1. Phương pháp đã hành xử ĐÚNG như thiết kế, và điều đó bị chỉ số che
mất.** Phủ 137/400, REPAIRED 122, VERIFIED 106 — tức `diagnose()` sửa gần
đúng khi và chỉ khi tài liệu chứa câu trả lời, và im lặng khi không chứa.
Nó không bịa lấy một lần trong 400 lượt. Đó chính là luận điểm của bài
báo. Tính riêng trên các lượt CÓ RA TAY: đề xuất ~85/122 ≈ 70% định vị
đúng, baseline 9 ~118/234 ≈ 50%. Baseline thắng bảng tổng vì nó giải LP
nên nặn được số thực bất kỳ ([diagnose.py](src/repair/diagnose.py) hàm
`diagnose_fellegi_holt_donor`) — nó đoán nhiều gấp đôi và trúng ít hơn.

**2. Độ phủ `digit_sub` thấp là do HAI MÔ HÌNH LỖI KHÔNG KHỚP, không phải
lỗi bộ sinh ứng viên.** Bộ tiêm `_doi_mot_chu_so()` đổi một chữ số sang
"một chữ số khác bất kỳ", đều xác suất trên 9 chữ số còn lại. Bộ sinh
`tu_nham_chu_so()` chỉ đảo 4 cặp `CAP_CHU_SO_NHAM = (0,8) (1,7) (3,8)
(5,6)`. Xác suất trùng ≈ (7/10) × (1/9) ≈ 0.078, đo được 0.092 — khớp gần
hoàn toàn. Con số 9.2% là tỷ lệ trùng của hai bảng chữ số, không mang
thông tin gì về phương pháp.

**3. `row_shift` không đo được VỀ NGUYÊN TẮC ở tầng XBRL.** Khi một ô bị
ghi đè bằng giá trị dòng bên cạnh, giá trị gốc biến mất khỏi bảng. Pipeline
thật đọc lại ảnh là lấy lại được; tầng XBRL không có ảnh. Cùng lý do đó,
`tu_phieu_vlm()` cũng không đóng góp gì vì không có phiếu VLM. Nghĩa là ta
đang đo phương pháp trong điều kiện bị tháo mất một phần cơ chế.

#### CẠM BẪY — đọc trước khi định chạy lại

Cho bộ tiêm và bộ sinh ứng viên dùng CHUNG một ma trận nhầm lẫn sẽ đẩy độ
phủ `digit_sub` lên gần 1.0, làm ABSTAIN sụp xuống, và phương pháp đề xuất
gần như chắc chắn thắng baseline 9. **Tham số này quyết định kết quả của
cả thí nghiệm.** Chỉnh nó SAU KHI đã thấy kết quả chính là thứ
preregistration sinh ra để ngăn.

Cách hợp lệ duy nhất: đo ma trận nhầm lẫn chữ số **từ dữ liệu thật** —
chạy EasyOCR trên các báo cáo trong `data/` và đối chiếu với nhãn — rồi
dùng đúng ma trận đó cho CẢ HAI phía, và ghi vào `PREREGISTRATION.md` như
một tu chính TRƯỚC khi chạy lại. Ghi rõ trong bài rằng ma trận đến từ đo
đạc chứ không phải chọn tay.

#### Trạng thái Mốc 3

**VẪN CHƯA ĐÓNG**, và lý do nay đã cụ thể hơn trước:

1. Ma trận nhầm lẫn chữ số chưa đo từ dữ liệu thật (chặn `digit_sub`).
2. Cột kỳ so sánh rỗng nên `col_shift` bỏ 120/130 lượt.
3. `row_shift` cần ảnh, tức cần `data/gold`, không cứu được ở tầng XBRL.
4. Chỉ số định vị hiện phạt ABSTAIN, tức đo mức sẵn sàng đoán chứ không đo
   độ đúng. Cần quyết cách chấm — đề nghị báo cáo cả hai: định vị trên
   toàn bộ lượt VÀ định vị có điều kiện trên các lượt có ra tay, kèm tỷ lệ
   ra tay. Đây là quyết định của người dùng, chưa chốt.
5. Toàn bộ dữ liệu là doanh nghiệp Mỹ theo US-GAAP, chưa có báo cáo Việt
   Nam nào.

Script đo độ phủ đã vào repo: [src/eval/do_phu_ung_vien.py](src/eval/do_phu_ung_vien.py).
Lệnh ở mục 15. Nó không gọi `diagnose()` nên chạy nhanh, dùng lại được mỗi
lần đụng vào bộ sinh ứng viên hoặc bộ tiêm lỗi — và **phải chạy lại mỗi lần
đó**, vì độ phủ chính là thứ quyết định bảng Mốc 3 đọc ra nghĩa gì.

---

## 14. Quy ước bắt buộc

Từ `BUILD-SPEC.md` mục 0.2 và chỉ thị trực tiếp của người dùng.

| Quy ước | Chi tiết |
|---|---|
| **Import phẳng** | `pytest.ini` có `pythonpath = src`. Viết `from validation import ...`, KHÔNG `from src.validation import ...` |
| **Comment tiếng Việt** | Giải thích **tại sao**, không phải **cái gì** |
| **Docstring mô tả hiện trạng** | Không viết trạng thái dự định như thể đã làm xong |
| **Config tập trung** | Mọi hằng số miền nằm ở `fields_config.py` |
| **Nạp model lười** | Model nặng nạp trong getter. CI không cài torch |
| **Chạy test liên tục** | `ruff check src tests` rồi `pytest` sau **mỗi** thay đổi, không đợi tới lúc báo xong. Thêm tính năng kèm test thì **đục thủng tính năng đó và xác nhận test đỏ** |
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
- **`sed` ăn mất dấu backslash** khi thay chuỗi có regex. Đã làm hỏng
  `(?!\s*a)` thành `(?!s*a)` một lần. Dùng Python để thay chuỗi có backslash.
- **`.env.docker` đang chứa OpenRouter key thật.** Không nằm trong git và
  chưa từng được commit (đã kiểm cả lịch sử), nhưng repo là public.
- **Force-push bị trình phân loại quyền chặn.** Cần viết lại lịch sử thì để
  người dùng tự chạy lệnh.
- **`time.monotonic()` trên Windows quá thô** để test khoảng vài mili giây.
  Test bộ điều tốc của `fetch.py` dùng đồng hồ giả qua `monkeypatch`.
- **Module trong `src/eval/` chạy như script sẽ che `src/metrics.py`** bằng
  `src/eval/metrics.py` — xem mục 9.

---

## 15. Lệnh hay dùng

```bash
# Kiểm sau MỖI thay đổi
python -m ruff check src tests
python -m pytest -q

# Sinh lại báo cáo identifiability cho cả hai chuẩn
PYTHONIOENCODING=utf-8 python src/constraints.py

# Đo xem đẳng thức nào đáng mua (Mốc 1)
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/constraints_scenarios.py

# Chạy pipeline trên một tài liệu
python src/router.py data/samples/<file>.pdf

# Chế độ ĐO cho H1 — tắt hoàn toàn cổng ràng buộc
DISABLE_CONSTRAINT_GATE=true python src/router.py data/samples/<file>.pdf

# Tắt bước dò sự tồn tại của dòng (probe OCR). Tắt là MẤT tính năng chứ
# không sinh số sai: dòng vắng mặt thôi được điền 0 nên đẳng thức phân rã
# lại hay bị bỏ qua. Dùng để đo chính cái giá của probe.
DISABLE_LINE_PROBE=true python src/router.py data/samples/<file>.pdf

# Đo engine OCR trên ô số (cần easyocr; vài phút vì chạy CPU)
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/ocr_compare.py easyocr

# Trích lại text từ Công báo (poppler và antiword đã có sẵn)
pdftotext -layout -enc UTF-8 "data/legal/<file>.pdf" out.txt
antiword -m UTF-8.txt "data/legal/<file>.doc" > out.txt

# Chạy MỐC 3 — so baseline 9 với phương pháp đề xuất.
# CHẬM: bảng XBRL Mỹ có 150-250 chỉ tiêu nên mỗi hồ sơ mất vài phút.
# Tiến độ in ra stderr; kết quả in ra stdout.
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/moc3.py > data/output/moc3.md

# Đo ĐỘ PHỦ ỨNG VIÊN — phải chạy TRƯỚC khi đọc bảng Mốc 3, xem mục 13b.
# Nhanh (không gọi diagnose(), chỉ dựng ứng viên rồi so khớp).
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/do_phu_ung_vien.py     > data/output/moc3_do_phu_ung_vien.md

# Tải hồ sơ XBRL — chạy được từ shell trên máy người dùng.
# (Cảnh báo "container không ra được sec.gov" trong docstring fetch.py chỉ
#  đúng với Docker. Từ shell thường thì sec.gov với tới được bình thường.)
export SEC_USER_AGENT="Tên thật email@example.com"
python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --dry-run
```

---

## 16. Bước kế tiếp đề xuất

Cập nhật 24/08/2026. Hai việc đầu của danh sách cũ **đã xong**: cách xử lý
thành phần thiếu đã quyết và thi công (phương án C, mục 12), và dữ liệu XBRL
đã tải (15 công ty, 26 hồ sơ), và lượt chạy Mốc 3 đầy đủ đã xong (mục 13b).
Đường găng vẫn đi qua Mốc 3, và nó vẫn chưa đóng — nay vì phép đo chưa hợp
lệ chứ không phải vì chưa chạy.

1. **Đo ma trận nhầm lẫn chữ số từ dữ liệu thật** (mục 13b). Lượt chạy đầy
   đủ 26 hồ sơ ĐÃ XONG, nhưng phép đo độ phủ ứng viên cho thấy bộ tiêm và bộ
   sinh ứng viên đang dùng hai mô hình lỗi khác nhau, nên chỉ số `digit_sub`
   không mang thông tin về phương pháp. Phải đo ma trận từ EasyOCR trên báo
   cáo thật, dùng chung cho cả hai phía, và ghi tu chính vào
   `PREREGISTRATION.md` TRƯỚC khi chạy lại — xem cạm bẫy ở mục 13b.
2. **Quyết cách tính chỉ số định vị khi một phương pháp TỪ CHỐI trả lời.**
   Đây là quyết định của người, và nó đổi kết luận. Baseline 9 không bao giờ
   ABSTAIN nên luôn có cơ hội định vị đúng; phương pháp đề xuất ABSTAIN khi
   tập ứng viên đóng không chứa cách đọc hợp lệ nào — mà đó chính là hành vi
   nó được thiết kế để có. Đếm ABSTAIN là "định vị trượt" tức đang đo **mức
   sẵn sàng đoán**, không đo độ đúng.
3. **Sửa việc chọn kỳ để cột so sánh có số.** Hiện 0/158 chỉ tiêu có giá trị
   ở kỳ thứ hai, nên COL_SHIFT không inject được và nguồn ứng viên chéo kỳ
   không đóng góp gì — chỉ 3 trong 4 chế độ lỗi thật sự chạy.
4. **Nếu Mốc 3 qua:** thi công kịch bản E (mục 17.1) → chốt quy mô tập gold
   (mục 17.2) → gán nhãn → C3 → C4 → D2/D3/D4.
   **Nếu Mốc 3 không qua:** dừng, báo cáo, lùi bài về tầng dataset +
   identifiability. Kịch bản E và 100 tài liệu khi đó phải xét lại từ đầu.

### ĐỪNG gán nhãn trước khi biết kết quả MỐC 3

Guideline đã sẵn sàng và bộ chỉ tiêu đã chốt, nên việc gán nhãn **kỹ thuật
mà nói** bắt đầu được ngay. Đừng bắt đầu.

Gán nhãn 60 tài liệu tốn khoảng **45–60 giờ công người**: tìm và tải tài
liệu đủ tiêu chí (15–20 giờ), gán nhãn 60 × 21 chỉ tiêu (20–25 giờ), gán
nhãn đôi 20 tài liệu và phân xử (8–10 giờ), đo trần người (3 giờ). Toàn bộ
khoản đó phục vụ một luận điểm mà **MỐC 3 có thể bác bỏ**, và MỐC 3 chỉ tốn
1–2 ngày cộng vài phút chạy `fetch.py`.

Thứ tự đúng: MỐC 3 trước, gán nhãn sau. Nếu baseline 9 hoà thì phạm vi bài
lùi về dataset + identifiability, và lúc đó quy mô tập gold cần bao nhiêu là
một câu hỏi khác hẳn.

### Ba việc song song, không cái nào chặn cái nào

- ~~Người dùng chạy `fetch.py`~~ — **đã xong**, 26 hồ sơ trong `data/xbrl/`.
- **Tìm người hướng dẫn hoặc đồng tác giả.** Đây là việc nâng xác suất được
  nhận nhiều nhất trên mỗi đơn vị công sức — hơn bất kỳ thí nghiệm nào còn
  lại. Bài Q1 đầu tay không có người hướng dẫn mạnh thường chết ở khâu
  framing và khâu trả lời reviewer, không phải ở khâu kết quả.
- **Đo throughput API thật trên 5 tài liệu.** B2 dùng self-consistency k=5;
  nhân với 10 baseline, nhiều model, nhiều seed, cộng tầng XBRL hàng nghìn
  tài liệu thì đây là hàng chục nghìn lời gọi trên free tier OpenRouter. Rủi
  ro này không làm chậm lịch, nó có thể **chặn hẳn việc tạo ra con số**. Biết
  sớm còn kịp tính chuyện trả tiền cho phần tầng XBRL.

Sau khi MỐC 3 qua, mới tới: chốt người gán nhãn thứ hai (hoặc dùng phương án
dự phòng ở `ADDENDUM` mục 5 — tự gán lại sau **ít nhất hai tuần**, nên phải
bắt đầu sớm chứ không để cuối), pilot 20 tài liệu, tính lại power (MỐC 2),
rồi hoàn tất 60 tài liệu.

**Lưu ý khi merge sang `main`:** CI chỉ chạy trên `main` và trên pull
request, nên lỗi thiếu thư viện ở mục 8 chỉ lộ ra ở lần merge đầu tiên. Nó
đã được sửa, nhưng nguyên tắc thì còn: thêm bất kỳ import mức module nào
cũng phải sửa danh sách cài trong `.github/workflows/ci.yml`.

---

## 17. LƯU Ý — việc người dùng đã quyết nhưng CHƯA thi công

Mục này giữ những việc đã có quyết định nhưng cố ý hoãn lại. Đọc mục này
trước khi bắt đầu bất kỳ việc gì ở mục 16, kẻo làm theo con số cũ.

### 17.1 Đổi bộ chỉ tiêu từ kịch bản D sang **kịch bản E** — CHƯA LÀM

Người dùng chốt ngày 24/08/2026: dùng **E**, vì E đúng hơn về học thuật. Số
đo hậu thuẫn: E hơn D trên mọi trần (Top-1 0,54 so 0,50; Top-3 0,96 so 0,90),
và D vốn chỉ được chọn vì tính khả thi của việc gán nhãn chứ không phải vì
tốt hơn.

E thêm **6 chỉ tiêu và 2 đẳng thức** của báo cáo lưu chuyển tiền tệ B03:
tiền đầu kỳ (mã 60), ba dòng lưu chuyển (20, 30, 40), lưu chuyển thuần (50),
ảnh hưởng tỷ giá (61). Tổng thành **26 chỉ tiêu / 9 đẳng thức**.

Việc phải làm khi thi công, theo thứ tự:

1. Khai thêm 6 chỉ tiêu vào `FIELD_MAP`, `FIELD_LINE_CODES` (cả hai chuẩn),
   `FIELD_ALIASES`, `FIELD_RULES`. Mẫu biểu B03 đã có marker sẵn trong
   `FORM_MARKERS`, không phải thêm.
2. Khai 2 đẳng thức vào `_DANG_THUC_CHUNG`. **Cả hai đã đối chiếu Công báo
   rồi** — nguyên văn ở Phụ lục A mục 3.4 — nên không phải tra văn bản lại.
3. Chạy lại `constraints.py` và `constraints_scenarios.py`, sinh lại hai báo
   cáo identifiability.
4. **Đo lại trần người** với 26 chỉ tiêu qua ba biểu mẫu. Đây là việc dễ bị
   bỏ qua nhất và cũng là lý do E từng bị loại: `ADDENDUM` mục 6 chốt giao
   thức 15 phút một tài liệu, và 26 chỉ tiêu rải qua ba báo cáo nhiều khả
   năng vỡ giao thức đó. Nếu vỡ thì phải sửa giao thức **trước** khi gán
   nhãn tài liệu đầu tiên.
5. Sửa `ANNOTATION-GUIDELINE.md` mục 2 (phạm vi biểu mẫu nay gồm B03) và ghi
   vào mục Sửa đổi của nó.
6. Ghi vào mục Sửa đổi của `PREREGISTRATION.md`.

**Cửa sổ để làm việc này đang mở và sẽ đóng.** `data/gold/` còn trống nên
Luật 3 được thoả mà không tốn công gán nhãn lại. Ngay khi tài liệu đầu tiên
được gán nhãn, đổi sang E buộc phải quay lại cả tập đã làm.

### 17.2 Quy mô tập gold lên **khoảng 100 tài liệu** — CHƯA CẬP NHẬT TÀI LIỆU

Người dùng chốt ngày 24/08/2026: tìm khoảng **100** tài liệu thay vì 60.
Việc sửa tài liệu cho khớp con số này được **cố ý hoãn**, và đây là danh sách
chỗ phải sửa khi làm:

- `ANNOTATION-GUIDELINE.md` mục 7 — đang ghi "60 tài liệu, chia 30 TT200 +
  30 TT99". Giữ tỷ lệ 50/50 vì trục transfer của ablation 8 dựa vào đó.
- `PREREGISTRATION.md` — thêm mục Sửa đổi. Bắt buộc: quy mô mẫu là tham số
  của mọi phép tính power.
- `ADDENDUM` mục 4 — mọi con số tính power đều lấy 60 làm số cụm độc lập
  ("1500 quan sát nhưng chỉ 60 cụm"). Với 100 tài liệu thì cả bảng đó đổi.

**Điều phải nói kèm, kẻo con số 100 bị hiểu sai:** thêm tài liệu chủ yếu chỉ
giúp **H1**. H2 và H3 đo trên **số lỗi**, không phải số trường — ở 60 tài
liệu số lỗi rơi vào 75–225, lên 100 cũng chỉ thành 125–375. Đó đúng là lý do
`ADDENDUM` mục 4 kết luận tầng XBRL là **bắt buộc** chứ không phải "nếu có
thời gian". Muốn thêm số liệu cho H2/H3 thì **mở rộng tầng XBRL rẻ hơn hẳn**
so với gán nhãn thêm tài liệu tay.

---

## 18. Nơi nộp — đã chốt 24/08/2026

**Đích: ICDAR 2027 main track, hạn nộp 28/02/2027.** Kuala Lumpur, 18–22/08/2027.
Springer LNCS, tối đa 17 trang kể cả hình và tài liệu tham khảo, phản biện ẩn
danh hai chiều có rebuttal, cho phép đăng arXiv trước.

Proposal mục 13 đề xuất **ICDAR-IJDAR journal track** làm đích tốt nhất. Đã
đổi, vì hai lý do tra được:

**Một — hạn journal track là 15/11/2026, không đủ thời gian.** Còn khoảng 12
tuần kể từ khi chốt, trong khi phần việc còn lại ước lượng 13–16 tuần: gán
nhãn 60 tài liệu (45–60 giờ công người), chạy 10 baseline trên 3 tầng (2–3
tuần wall-clock, phần lớn là chờ API), viết bài 20 trang (3–4 tuần). Ép vào
12 tuần nghĩa là nộp bản chưa chín vào đúng venue khó nhất. Hạn ICDAR main
cho **27 tuần**, và quan trọng hơn: nó chừa chỗ để lùi phạm vi nếu MỐC 3 ra
kết quả xấu mà vẫn kịp cùng hạn đó.

**Hai — journal track loại bản mở rộng từ hội nghị, và điều đó phá chiến
lược "nộp song song" của proposal.** Nguyên văn CFP: *"Journal versions of
previously published conference papers or survey papers will not be
considered for this special issue."* Nên **KHÔNG nộp RIVF hay SoICT** với
nội dung trùng — proposal mục 13 khuyên nộp song song để lấy phản biện sớm,
và lời khuyên đó ở đây gây hại nhiều hơn lợi: nó vừa đóng cửa journal track,
vừa tạo vấn đề trùng lặp với ICDAR main. (Hạn tham khảo nếu sau này cần: RIVF
2026 hết 31/08/2026, SoICT 2026 hết 16/09/2026.)

**Đường lên Q1 không mất.** Chính CFP đó nói bài đã đăng hội nghị vẫn nộp
IJDAR được qua **quy trình thường**, chỉ là không vào được special issue. Lộ
trình: ICDAR 2027 main → mở rộng thành bài IJDAR thường sau đó. IJDAR có IF
2,5, SJR 0,83, **Q1** ở Computer Vision & Pattern Recognition (Q2 ở CS
Applications và Software). Cái mất là slot oral tự động và thời gian.

### Đối thủ mới cần thêm vào related work

**Cập nhật 24/08/2026 — đã tra lại theo yêu cầu người dùng.** Kết quả đầy đủ
ghi ở `MD file/FINAL-proposal-reread-dont-repair.md` **mục 14b** (file đó bị
gitignore nên chỉ có trên máy người dùng). Tóm tắt cho người đọc bàn giao:

**Đóng góp lõi vẫn chưa ai làm.** Đọc lại nguồn thay vì sửa trên tập số cố
định — chưa có. H0 identifiability — chưa có. ViFinKIE — chưa có.

**Một đối thủ mới, đáng kể: arXiv 2608.14639** (đăng 08/2026), *Valid Per-Field
Selective Risk Control for Document Extraction*, chạy trên Claude-Sonnet-5 với
800 hoá đơn CORD. Nó **không** dùng ràng buộc miền, **không** sửa (chỉ từ chối),
**không** sinh ứng viên từ ảnh, **không** phân tích identifiability — nên không
chiếm chỗ đóng góp lõi. Nhưng nó **thu hẹp kết quả dự kiến số 4**: phần đường
cong risk–coverage nay phải phát biểu là "ràng buộc miền làm bộ điểm thứ ba",
không được phát biểu là "chúng tôi làm selective prediction".

Ngược lại nó **làm mạnh thêm H1**: nó ghi nhận các chế độ hỏng của cách tiếp
cận dựa trên confidence, gồm cả phân cụm theo tài liệu — tức có công trình độc
lập hậu thuẫn cho việc đi tìm một tín hiệu tốt hơn confidence.

**Hai cái đã kiểm và KHÔNG chiếm chỗ:** *Blueprint* (VLDB) chỉ chấm điểm các
phương án trích xuất đã có, không đọc lại ảnh; *FinStat2SQL* (arXiv 2506.23273)
tuy là tài chính Việt Nam nhưng lấy Excel từ FiinPro, không OCR, không PDF,
không phát hành benchmark.

**Một câu đáng trích dẫn nguyên văn**, từ ban tổ chức ICDAR 2026 HIPE-OCRepair:
*"Trong thực hành hậu-xử-lý OCR chuẩn, hệ thống chỉ làm việc trên văn bản và
không có quyền truy cập ảnh tài liệu gốc."* Dùng ở Introduction thì luận điểm
"không ai đọc lại nguồn" có người ngoài chứng thực.

**Nhịp lấp của mảng này là lý do thật để đi nhanh** — đối thủ gần nhất đăng
đúng tháng tra cứu.

#### Đối thủ ghi nhận trước đó

**FinReporting** — arXiv 2604.05966 (05/2026). Agentic workflow cho báo cáo
tài chính đa quốc gia, ontology hợp nhất ba báo cáo, LLM làm *constrained
verifier* dưới luật quyết định tường minh, có khâu anomaly logging; đánh giá
trên hồ sơ Mỹ, Nhật, Trung.

**Không chiếm chỗ:** nó không định vị lỗi bằng ma trận ràng buộc, không phân
tích identifiability, và **không đọc lại ảnh nguồn để sinh ứng viên**. Là
trích dẫn phải thêm, không phải lý do đổi hướng. Nhưng nó cho thấy mảng này
đang lấp dần, nên đừng kéo dài quá hạn 28/02/2027.

Luật dừng của proposal vẫn giữ: kiểm lại arXiv **một lần duy nhất** ngay
trước khi nộp, không tra liên tục.

---

## Phụ lục A — MỐC 1: bảng đối chiếu ma trận ràng buộc với Thông tư

Tài liệu này để **người chủ trì** làm, không phải AI. BUILD-SPEC mục 0.5 nêu
lý do: sai một dấu trong ma trận ràng buộc thì toàn bộ kết quả identifiability
sai mà **không có gì báo** — code vẫn chạy, số vẫn ra, chỉ là sai.

Mốc này chặn B4, mà B4 quyết định chi phí gán nhãn tay cho 60 tài liệu gold —
khoản đắt nhất của cả dự án.

---

### 1. Vấn đề, giải thích bằng số thật

#### 1.1 Ràng buộc phát hiện được lỗi, nhưng thường không chỉ ra lỗi ở đâu

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

#### 1.2 Cái phá được thế bí: một con số nằm trong HAI quan hệ

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

#### 1.3 Nhưng phân rã là một cái cối xay

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

#### 1.4 Nên khi đọc Phụ lục IV, tìm cái gì

Không phải "còn chỉ tiêu nào chưa trích".

**Mà là: con số nào ta ĐÃ trích lại xuất hiện trong một quan hệ THỨ HAI.**

Ba ứng viên tôi dựng lại được từ kết cấu biểu mẫu — **đây là phỏng đoán,
chưa đối chiếu văn bản, đó chính là việc bạn sắp làm**:

| Ứng viên | Ý tưởng | Nó cứu chỉ tiêu nào |
|---|---|---|
| Tiền cuối kỳ trên **B03** chính là Tiền và tương đương tiền trên **B01** | Cùng một con số in ở hai biểu mẫu | `tien` — và qua đó cả nhóm tài sản ngắn hạn |
| Lợi nhuận chưa phân phối trên **B01** = LNCPP đầu kỳ + LNST trên **B02** − cổ tức | Nối bảng cân đối với báo cáo lãi lỗ | `loi_nhuan_sau_thue` |
| **Cột kỳ trước** cùng thoả một hệ đẳng thức | Đã có sẵn trên trang, không tốn gì thêm | Chưa đo — proposal mục 6.1(d) hỏi đúng câu này |

#### 1.5 Một chỉ tiêu vẫn nằm ngoài tầm ở MỌI kịch bản

`hang_ton_kho` không định vị được ở A, B, C, D, lẫn E.

Đáng chú ý vì đó **đúng là chỉ tiêu đã có lỗi đọc thật** trên báo cáo VNM —
alias "Hàng tồn kho" khớp trúng dòng "Dự phòng giảm giá hàng tồn kho" (mã
142), cho ra giá trị nhỏ hơn thật khoảng nghìn lần nhưng hợp lệ về hình
thức.

Nghĩa là: **ràng buộc kế toán chứng minh được là không bao giờ bắt được lỗi
đó.** Chỉ mỏ neo đơn vị tính và việc đọc lại crop mới bắt được. Đây là ví dụ
cụ thể, có thật, để đưa vào bài — và nó chính là lập luận bảo vệ đóng góp
cốt lõi.

### 2. Lấy văn bản ở đâu

#### Nguồn chính thức — dùng để TRÍCH DẪN trong bài

**Công báo Chính phủ** là công báo chính thức, và đây là nguồn nên trích dẫn:

- Thông tư 200/2014/TT-BTC (ban hành 22/12/2014):
  https://congbao.chinhphu.vn/van-ban/thong-tu-so-200-2014-tt-btc-6697.htm
- Thông tư 99/2025/TT-BTC (ban hành 27/10/2025, hiệu lực 01/01/2026):
  https://congbao.chinhphu.vn/van-ban/thong-tu-so-99-2025-tt-btc-46529.htm

**Lưu ý quan trọng về TT99:** Công báo tách nó thành **10 số** (từ số
1563+1564 tới số 1581+1582), mỗi số có bản `.pdf` và bản `.doc`. Lý do là các
phụ lục rất dài. Phần thân thông tư nằm ở số đầu; **Phụ lục IV nằm ở các số
cuối**. Tải bản `.doc` nếu định tìm chuỗi — dễ mở và dễ tìm hơn PDF quét.

#### Nguồn tiện dụng — dùng để ĐỌC

thuvienphapluat.vn có bài đăng riêng gom các phụ lục thành file Word:
https://thuvienphapluat.vn/phap-luat-doanh-nghiep/bai-viet/file-word-phu-luc-che-do-ke-toan-doanh-nghiep-theo-thong-tu-99-2025-tt-btc-17560.html

Trang này chặn truy cập tự động nên phải mở bằng trình duyệt, và có thể đòi
tài khoản. Dùng nó để đọc cho nhanh, nhưng **trích dẫn trong bài thì trích
Công báo**, vì đó mới là nguồn chính thức.

#### Cách tìm đúng chỗ trong file

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

#### Đặt file vào đâu

```
data/legal/TT200-2014-phu-luc-IV.pdf     (hoặc .doc)
data/legal/TT99-2025-phu-luc-IV.pdf
```

Thư mục `data/legal/` đã có sẵn và **đã gitignore**. Bản thân văn bản quy
phạm pháp luật không có bản quyền (Luật Sở hữu trí tuệ điều 15), nhưng file
Công báo nặng vài chục MB và tải lại được bất cứ lúc nào, nên không đưa vào
git. Thứ vào git là **kết quả đối chiếu**, tức chính file này.

---

### 3. Bảng đối chiếu — đã xác nhận từng dòng

> **Trạng thái: XONG, 23/08/2026.** Mọi ô ☐ trong mục này đã được đối chiếu
> với Công báo và đóng lại. Hai câu hỏi mở của bản trước đều đã có đáp án, và
> **một trong hai có đáp án ngược với giả định ban đầu** — xem 3.2.
>
> Nguồn dùng để đối chiếu, đều nằm trong `data/legal/` (đã gitignore):
> TT200 ở `2015_287 + 288` (Điều 88–113) và `2015_289 + 290` (Điều 114–130);
> TT99 ở `2025_1577 + 1578` (Phụ lục IV Mục 1 — biểu mẫu), `2025_1579 + 1580`
> (B01 + B02) và `2025_1581 + 1582` (cuối B02 + B03 + B09). Trích bằng
> `pdftotext -layout -enc UTF-8` cho PDF và `antiword -m UTF-8.txt` cho `.doc`.

#### 3.1 Mã số dòng đang dùng trong code

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

#### 3.2 Hai chỗ từng CHƯA xác nhận — nay đã đóng lại

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

#### 3.3 Đẳng thức đang mã hoá

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

#### 3.4 Đẳng thức tìm thêm được — điền vào đây

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

##### Ví dụ đã điền (minh hoạ cách ghi, KHÔNG phải số liệu thật)

| Biểu mẫu | Đẳng thức theo văn bản | Chuẩn | Trùng chỉ tiêu với đẳng thức nào khác? |
|---|---|---|---|
| B01a | `Mã số 100 = MS 110 + MS 120 + MS 130 + MS 140 + MS 150` | TT99 | Có — MS 100 cũng nằm trong `MS 280 = MS 100 + MS 200` |
| B01a | `Mã số 280 = Mã số 100 + Mã số 200` | TT99 | Có — MS 100 (ở trên), MS 200 |
| B03a | `Mã số 70 = MS 60 + MS 50 + MS 61` | TT99 | *(điền sau khi kiểm MS 70 có bằng MS 110 của B01a không)* |

Dòng thứ ba là loại đáng giá nhất nếu xác nhận được: nó nối **hai biểu mẫu
khác nhau**, tức gắn một đẳng thức thứ hai vào một chỉ tiêu đã có sẵn.

##### ĐÃ TRÍCH ĐƯỢC — 23/08/2026

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

##### ĐÃ TRÍCH NỐT — 23/08/2026, đủ cả năm file Công báo

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

###### Ba đẳng thức repo đang dùng: đều ĐÚNG

- `100 + 200 = 270/280` ✅ khớp nguyên văn
- `300 + 400 = 270/280` ✅ đúng, nhưng là đẳng thức **suy ra** — văn bản viết
  `440 = 300 + 400` rồi viết **riêng** `Tổng cộng Tài sản = Tổng cộng Nguồn
  vốn`. Gộp làm một vẫn đúng về toán nhưng mất một quan sát đọc được.
- `11 + 20 = 10` ✅ khớp `20 = 10 − 11`

###### Kết quả đo — và một kết luận cũ bị bác bỏ

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

###### Hai chỗ khác nhau giữa hai chuẩn — nguồn lỗi câm

**Mã 270 mang nghĩa KHÁC HẲN.** Ở TT200 là "Tổng cộng tài sản"; ở TT99 là
"Tài sản dài hạn khác" (`270 = 271+272+273+274`). Tra nhầm bảng mã thì đọc
"Tài sản dài hạn khác" ra thành "Tổng tài sản" — có giá trị, hợp lệ hình
thức, không cảnh báo. Đây là lý do `standard` phải là tham số **bắt buộc**
của `extract_field_by_code()`.

**Dự phòng giảm giá hàng tồn kho đổi mã:** `149` ở TT200, `142` ở TT99.

###### Vẫn không đạt bộ tối thiểu

`minimal_localizing_set()` trả `None` ở **mọi** kịch bản, và `hang_ton_kho`
không định vị được ở kịch bản nào. Kết luận cho bài: ràng buộc kế toán đơn
thuần **không đủ**, và trọng số dồn sang mỏ neo đơn vị tính (proposal 6.3)
cùng bước đọc lại (6.2) — đúng như mục 6.1 đã lường trước.

#### 3.5 PHÁT HIỆN NGOÀI DỰ KIẾN — `FORM_MARKERS` đang sai

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

##### Nếu KHÔNG tìm thấy đẳng thức nối chéo nào

Đó cũng là một kết quả, và là kết quả phải báo cáo chứ không phải thất bại.
Nó xác nhận rằng ràng buộc kế toán **đơn thuần** không đủ để định vị lỗi
trên BCTC Việt Nam, và dồn trọng số của bài sang mỏ neo đơn vị tính (proposal
mục 6.3) cùng bước đọc lại (mục 6.2) — tức sang đúng đóng góp cốt lõi.
Proposal mục 6.1 đã lường trước dưới tên "chuẩn bị tinh thần cho kết quả bi
quan".

---

### 4. Làm xong thì làm gì tiếp

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

---

## Phụ lục B — Sổ thi công phương án C

Viết cuốn chiếu trong lúc sửa, để phiên sau nối tiếp được nếu phiên trước hết
quota giữa chừng. Ban đầu là file riêng `NOTES-PHUONG-AN-C.md`, đã gộp vào đây
ngày 24/08/2026.

- **Bắt đầu:** 24/08/2026, từ commit `5810ea2`
- **Nhánh:** `research`

---

### Quyết định của người dùng, 24/08/2026

Người dùng chọn **phương án C** cho câu hỏi treo ở `HANDOFF.md` mục 12
(`None` hay `0` khi một thành phần đẳng thức không đọc được), cộng hai lựa
chọn con:

1. **Nhánh VLM phân biệt "vắng mặt" với "đọc hỏng" bằng cách dò trên OCR
   text**, không hỏi thẳng model. Lý do chọn: việc model tự khai "dòng này
   không có" là một phán đoán của model, và phán đoán sai sẽ lặng lẽ thành
   số 0 đi vào đẳng thức — đúng chỗ nhạy cảm nhất với việc bịa. Dò trên text
   thì tất định, kiểm lại được, và truy được về một chỗ cụ thể trên tài liệu,
   khớp với luận điểm chống bịa của cả nghiên cứu.
2. **Số 0 của dòng vắng mặt được ghi vào cả `data` đầu ra**, kèm khoá trạng
   thái tường minh, chứ không chỉ tồn tại bên trong bước kiểm đẳng thức. Lý
   do: guideline mục 3.4 đã quy định gold ghi `0` cho dòng vắng mặt, mà
   `eval/metrics.py` quy định `None` chỉ khớp với `None`. Nếu pipeline vẫn
   trả `None` thì `field_accuracy` và `document_fully_correct` bị trừ điểm
   oan trên mọi tài liệu có dòng vắng mặt — tức hai trong ba chỉ số đầu bảng
   bị bóp méo một cách hệ thống.

### Ràng buộc phát hiện lúc bắt tay vào làm

**Báo cáo mẫu là bản scan.** `pdftotext -layout` trên
`data/samples/20260429_VNM_...pdf` chỉ ra 152 ký tự cho 12 trang. Nên đường
rẻ nhất — đọc text layer của PDF, miễn phí và chính xác tuyệt đối — **không
dùng được** cho loại tài liệu dự án nhắm tới. Poppler có sẵn trên máy nên
`pdftotext` vẫn đáng thử trước ở mỗi tài liệu, nhưng không được coi nó là
đường chính.

**`USE_OCR_FIRST=false` trong `.env`.** Nhánh OCR đang tắt, nên đường chạy
thường (VLM) hiện **không sinh ra một chữ OCR text nào**. Phương án C vì vậy
bắt buộc phải chạy OCR trên đường VLM — đúng thứ cấu hình mặc định cố ý tắt
vì nó chậm (EasyOCR chạy CPU).

Hai thứ làm chi phí đó chịu được, và thiết kế dựa vào cả hai:

- **Probe dò theo MÃ SỐ DÒNG, không theo tên chỉ tiêu.** Mã số là chữ số, và
  `data/output/ocr_engine_easyocr.md` đo được EasyOCR đạt 0,999 Levenshtein
  trên ô số. Chỗ nó yếu (0,934, và chỉ 0,467 đúng con số ở độ phân giải
  thấp) là tên tiếng Việt có dấu — thứ probe không dùng tới.
- **Probe chạy một lần cho mỗi MẪU BIỂU, không phải mỗi trang.** "Báo cáo
  này có dòng mã 150 không" là tính chất của trang bảng cân đối, không phải
  của cả tài liệu. Probe tái dùng vùng bảng đã cắt sẵn cho VLM nên không tốn
  thêm convert PDF hay YOLO — hai khâu đắt nhất đều đã chạy rồi.

---

### Thứ tự thi công

Ba lỗi dưới đây đã báo cáo ở phiên này; C phụ thuộc lỗi 1 nên lỗi 1 đi trước.

| Bước | Nội dung | Commit | Trạng thái |
|---|---|---|---|
| A | Lỗi 1 + 4 — truyền `standard` xuống `validate_result`, hợp nhất meta thay vì đè | `fa5c6d2` | **XONG** |
| B | Lỗi 3 + 2 — dùng `fields_for(standard)` ở prompt, trích xuất, và điều kiện dừng sớm | `88a77f5` | **XONG** |
| C1 | Oracle dò sự tồn tại của dòng, thuần logic, không cần OCR | `19fe938` | **XONG** |
| C2 | Nối oracle vào router: OCR probe trên đường VLM, trạng thái vào meta, vắng mặt = 0 | `ada6f75` | **XONG** |
| D | Nhận diện chuẩn thật (nguồn `nhan_dien`) thay vì luôn lùi mặc định | — | **chưa làm** |

Sau bước A: 346 test xanh (trước 340). Sau bước B: **352 test xanh**.
`ruff check src tests` sạch ở cả hai mốc.

#### Bước A đã làm gì — `fa5c6d2`

- `validate_result(result, standard)` — **bỏ hẳn mặc định**, `standard` thành
  tham số bắt buộc. Không chọn cách "truyền đúng ở chỗ gọi mà vẫn giữ mặc
  định", vì mặc định còn đó thì chỗ gọi mới nào cũng có thể quên lần nữa và
  lỗi sẽ im lặng y như cũ.
- `route_document(file_path, save=True, standard=None)` — chốt chuẩn MỘT lần ở
  đầu qua `chon_chuan()`, rồi dùng chung cho prompt VLM, bảng mã số, bộ đẳng
  thức và câu cảnh báo.
- `chon_chuan()` trả `(chuẩn, nguồn)` với nguồn thuộc tập đóng `tham_so` /
  `mac_dinh`. Nguồn được ghi vào `meta["standard_nguon"]`.
- `is_acceptable(result, standard)`, `run_ocr_first`, `run_vlm`,
  `run_unconstrained` đều nhận thêm `standard`.
- Meta của `ExtractionResult` nay **hợp nhất** `{**meta_vlm, **meta_validate}`
  thay vì gán đè, nên `early_stop` và `prompt_hash` sống sót ra tới API. Khoá
  hằng `META_VLM` trong `router.py` là đường chuyển tạm giữa hai nơi.

**Test mới (6 cái).** `tests/test_validation.py`:
`test_bao_cao_TT200_duoc_kiem_bang_dang_thuc_TT200`,
`test_dung_nham_chuan_thi_dang_thuc_phan_ra_im_lang`,
`test_meta_ghi_dung_chuan_da_dung`. `tests/test_router.py`:
`test_route_document_truyen_chuan_xuong_tan_buoc_kiem`,
`test_meta_ghi_ro_chuan_den_tu_dau`, `test_meta_giu_lai_early_stop_cua_nhanh_vlm`.

**Đã đục thủng ba chỗ, cả ba đều bị bắt:** bỏ truyền chuẩn xuống
`validate_result`; quay lại gán đè meta; cho TT200 dùng đẳng thức TT99.

**Việc bước A cố ý CHƯA làm:** `chon_chuan()` chưa có nguồn `nhan_dien`. Trên
cấu hình mặc định nó luôn trả `mac_dinh`, và nay việc đó **kêu ra log** thay vì
im lặng như trước. Bước C mang OCR tới đường VLM thì mới nối được
`detect_standard()` vào đây.

#### Bước B đã làm gì — `88a77f5`

Ba chỗ còn duyệt `FIELD_MAP` trong khi lẽ ra phải duyệt `fields_for(standard)`,
cộng một chỗ thứ tư phát hiện thêm khi sửa:

- `build_prompt()` — prompt cho TT200 thôi nhắc `tai_san_sinh_hoc_ngan_han`.
  Đã kiểm: `"NHÓM KHÁC"` biến mất khỏi prompt của **cả hai** chuẩn, vì nay mọi
  chỉ tiêu được hỏi đều có mã số trong bảng của chuẩn đó.
- Điều kiện dừng sớm nhánh 1 — đếm trên `cac_field_can = fields_for(standard)`.
- `extract_all_fields()` của nhánh regex.
- `empty_result(standard)` — **nay nhận standard bắt buộc**. Đây là chỗ thứ tư,
  không nằm trong danh sách ban đầu: khung tích luỹ thừa một chỉ tiêu không bao
  giờ điền được thì mọi phép đếm "đã đủ field chưa" chờ nó vĩnh viễn.

**Test mới:** `tests/test_bo_chi_tieu_theo_chuan.py` (5 test) và
`test_bao_cao_TT200_van_dung_som_duoc_o_nhanh_du_het_field` trong
`tests/test_early_stop.py`.

**Bài học đáng nhớ khi viết test cho bước C.** Bản đầu của test dừng sớm **mô
phỏng** điều kiện (`all(... for khoa in fields_for(std))`) thay vì chạy đường
thật. Nó xanh, trông hợp lý, nhưng khi đục thủng code thì **không đỏ** — vì nó
đang kiểm chính bản sao chép của nó, không kiểm code. Phải viết lại thành gọi
`extract_fields_from_regions()` với phản hồi VLM giả đúng kiểu báo cáo TT200.
Test nào không đỏ khi đục thủng thì test đó vô giá trị, và điều đó chỉ lộ ra
khi thật sự đi đục.

**Bẫy môi trường gặp lại:** heredoc `bash` vỡ khi nội dung Python có chuỗi kết
thúc bằng dấu nháy (`... dừng ở trang \"""`). Nó chèn rác vào giữa file mà
không báo lỗi ngay. `HANDOFF.md` mục 14 đã ghi bẫy này rồi — dùng công cụ ghi
file cho nội dung có nháy, đừng dùng heredoc.

#### Bước C1 đã làm gì — `19fe938`

Phần thuần logic của phương án C, test được mà không cần OCR hay model.

- `DauVetDong(gia_tri, trang_thai)` trong `src/extract_baseline.py`, trạng thái
  thuộc **tập đóng năm giá trị**: `co_gia_tri`, `thay_dong_khong_ra_so`,
  `khong_thay_dong`, `khong_thay_mau_bieu`, `khong_khai_bao`.
- `tim_theo_ma_so(text, field_key, standard)` — như `extract_field_by_code()`
  nhưng nói ra lý do. `extract_field_by_code()` nay là lớp mỏng gọi lại nó, nên
  chỉ còn một bản cài đặt.
- `tong_hop_dau_vet(cac_dau_vet)` — gộp dấu vết của MỘT chỉ tiêu qua nhiều
  trang theo thứ tự ưu tiên `_UU_TIEN_TRANG_THAI`.

**Lớp an toàn quan trọng nhất, đừng gỡ:** kết luận `khong_thay_dong` (tức vắng
mặt, tức sẽ gán 0) chỉ được rút ra khi **đã thấy mẫu biểu** ở đâu đó mà không
trang nào có mã số ấy. Bảng cân đối trải qua nhiều trang; rút kết luận từ một
trang lẻ sẽ gán 0 cho mọi chỉ tiêu nằm ở trang sau — tức bịa ra con số, đúng
thứ phương án C sinh ra để tránh. Danh sách rỗng trả `khong_thay_mau_bieu`.

**Lỗi câm có sẵn, phát hiện khi viết test, đã sửa trong cùng commit.** Pattern
lấy giá trị theo mã số dùng `(.{0,80}?)` kèm cờ `DOTALL`, nên dấu chấm nuốt cả
ký tự xuống dòng. Khi ô số của một chỉ tiêu không đọc được, pattern đi tiếp
xuống dưới và lấy về **giá trị của chỉ tiêu kế tiếp** — đo được: mã 130 bị mờ
thì hàm trả về đúng con số của mã 140. Nay đoạn giữa mã và giá trị bị chặn ở
tối đa **một** lần xuống dòng (`_GIUA_MA_VA_SO`), và cờ `DOTALL` bị bỏ.

Lỗi này quan trọng gấp đôi với phương án C: nó không chỉ trả sai số, nó còn
khai ca "đọc hỏng" thành "có giá trị", tức phá chính oracle đang được dựng.

**Test mới:** `tests/test_dau_vet_dong.py`, 12 test. Đục thủng bằng cách trả
pattern về `DOTALL` — hai test đỏ ngay.

#### Bước C2 đã làm gì — `ada6f75`

Nối oracle vào `route_document`. Sau bước này: **374 test xanh**, ruff sạch.

- `do_dau_vet_dong(cached_pages, standard, metrics)` — OCR các trang **đã
  duyệt** rồi dò từng chỉ tiêu theo mã số, gộp qua mọi trang.
- `dien_dong_vang_mat(gia_tri, dau_vet)` — trả `(giá trị, trạng thái)` với
  trạng thái thuộc tập đóng `co_gia_tri` / `vang_mat` / `khong_doc_duoc`.
- Gọi **TRƯỚC** `validate_result`, vì điền sau bước kiểm thì đẳng thức vẫn bị
  bỏ qua đúng như cũ và cả cơ chế thành vô nghĩa. Có test chốt thứ tự này.
- Meta thêm `trang_thai_chi_tieu` và `line_probe`.
- Cờ `DISABLE_LINE_PROBE`. **Tắt là mất tính năng, không sinh số sai:** không
  có dấu vết thì mọi chỉ tiêu thiếu giá trị mang `khong_doc_duoc`.

**Kết quả đo được, và đây là lý do tồn tại của cả phương án.** Trên bộ số kiểu
VNM (không có tài sản sinh học nên biểu mẫu bỏ mã 150) với hàng tồn kho đọc
nhầm sang dòng dự phòng — lỗi có thật, ví dụ mở đầu của proposal:

| | Cảnh báo phân rã TSNH |
|---|---|
| Trước C2 | **không có** — lỗi 1.499 tỷ đi qua im lặng |
| Sau C2 | **bắt được** |

Hai test `test_truoc_khi_dien_thi_loi_hang_ton_kho_di_qua_im_lang` và
`test_sau_khi_dien_thi_dung_loi_do_bi_bat` chốt cả hai chiều.

**Test mới:** `tests/test_dien_dong_vang_mat.py`, 10 test (5 hàm thuần, 3 hệ
quả lên đẳng thức, 2 đầu-cuối qua `route_document`). Đục thủng hai chỗ — bỏ
điều kiện trạng thái khi điền, và điền sau bước kiểm — đều bị bắt.

**Bẫy khi viết test đầu-cuối:** hàm VLM giả **phải duyệt hết generator trang**
(`list(pages)`), vì `cached_pages` được bồi vào trong lúc duyệt và probe chỉ
đọc những trang nằm trong đó. Hàm giả không duyệt thì `cached_pages` rỗng,
probe không có gì để dò, và test đỏ vì một lý do chẳng liên quan tới thứ đang
được kiểm.

---

### Bước D — việc còn lại, CHƯA làm

`chon_chuan()` vẫn chỉ có hai nguồn `tham_so` và `mac_dinh`. Trên cấu hình mặc
định (không ai truyền `standard`), mọi tài liệu vẫn được xử như **TT99** —
đúng, nhưng vì lùi mặc định chứ không vì nhận diện. Khác biệt so với trước
bước A: việc lùi nay **kêu ra log và ghi vào `meta["standard_nguon"]`** thay vì
im lặng.

Với báo cáo TT200 thật, hậu quả vẫn còn: prompt dùng bảng mã TT99 (mã 280 thay
vì 270) và bộ đẳng thức TT99.

#### Hai vướng mắc của bước D, đã khảo sát — ĐỌC TRƯỚC KHI THI CÔNG

**Vướng mắc 1 — thứ tự.** Chuẩn phải biết **trước** khi dựng prompt, còn probe
của C2 chạy **sau** khi trích xuất. Cách gỡ: kéo vài trang đầu ra khỏi
generator, OCR, gọi `detect_standard()`, rồi mới chạy trích xuất.
`cached_pages` và `_remaining_pages()` vốn đã hỗ trợ đúng kiểu tiêu thụ đó nên
trang đã kéo ra không bị convert hay chạy YOLO lần hai. Nên thêm một cache text
theo số trang để probe của C2 khỏi OCR lại chính những trang đó.

**Vướng mắc 2 — nghiêm trọng hơn, và nó bác bỏ cách làm hiển nhiên.** Dấu hiệu
duy nhất `detect_standard()` dùng là **TÊN BÁO CÁO** ở tiêu đề trang ("Bảng cân
đối kế toán" của TT200 so với "Báo cáo tình hình tài chính" của TT99). Nhưng
`iter_table_regions()` chỉ yield **vùng bảng đã cắt**, và `PADDING` trong
`src/layout_detection.py` chỉ có **8 pixel**. Tiêu đề báo cáo nằm phía trên
bảng, nên nó gần như chắc chắn **nằm ngoài** vùng đã cắt.

Hệ quả: OCR trên vùng bảng — thứ mà C2 đang làm — **không đủ** để nhận diện
chuẩn. Đây là suy luận từ cấu trúc code, chưa đo trên tài liệu thật; việc đầu
tiên của bước D nên là *kiểm chứng nó* bằng cách in text OCR của vài trang đầu
báo cáo VNM ra xem tiêu đề có lọt vào không. Ngoại lệ đã biết: khi YOLO không
tìm thấy bảng nào thì `ca_trang()` trả nguyên trang, và ca đó thì có tiêu đề.

Ba hướng, chưa chọn:

1. **Cho `iter_table_regions()` yield kèm ảnh cả trang**, rồi OCR cả trang chỉ
   để nhận diện, chỉ tới khi nhận ra thì thôi. Đúng đắn nhất, nhưng OCR cả
   trang đắt hơn OCR vùng bảng và EasyOCR chạy CPU.
2. **Nới `PADDING` riêng cho bước nhận diện** — cắt rộng lên phía trên vùng
   bảng đầu tiên để ôm lấy tiêu đề. Rẻ hơn, nhưng thành một hằng số nữa cần
   hiệu chỉnh mà chưa có dữ liệu để hiệu chỉnh.
3. **Nhận diện bằng bộ MÃ SỐ thay vì bằng tên.** Hấp dẫn vì mã số là chữ số,
   đúng chỗ EasyOCR mạnh, và mã số thì nằm trong vùng bảng. Nhưng phải rất cẩn
   thận: mã 270 tồn tại ở CẢ HAI chuẩn với nghĩa khác nhau (Tổng cộng tài sản ở
   TT200, Tài sản dài hạn khác ở TT99), nên dấu hiệu phải là *sự có mặt của mã
   280* chứ không phải sự có mặt của 270. Cần đối chiếu lại Phụ lục IV trước
   khi tin.

Dù chọn hướng nào cũng phải giữ nguyên tắc của `detect_standard()`: không đủ
dấu hiệu thì trả `None` và lùi mặc định **có ghi lại**, không đoán bừa. Và thêm
nguồn `nhan_dien` vào tập đóng của `chon_chuan()`.

#### Bước A — vì sao đi trước

C cần biết "dòng này có trên biểu mẫu của chuẩn này không", mà câu đó chỉ
trả lời được khi `standard` đã đi tới nơi cần dùng. Hiện `router.py` gọi
`validate_result()` ở ba chỗ (dòng 233, 303, 372) mà không truyền `standard`,
nên mọi tài liệu bị kiểm bằng đẳng thức TT99. Ngoài ra `router.py:327` gán
`meta=da_kiem["meta"]`, tức **đè** lên meta thật và làm đầu ra khai sai chuẩn
đã nhận diện, đồng thời đánh rơi `early_stop` và `prompt_hash`.

#### Bước C — hợp đồng của probe

Ba trạng thái, ghi tường minh, không suy ra từ sự vắng mặt của khoá khác:

- `co_gia_tri` — đọc được số.
- `vang_mat` — probe khẳng định biểu mẫu **không có** dòng đó → giá trị `0`.
- `khong_doc_duoc` — probe thấy dòng nhưng không ra số, hoặc probe không
  chạy được → giá trị `None`, nghĩa là *chưa biết*.

Ca thứ ba phải giữ `None` chứ không được nhập vào `vang_mat`: gộp lại là
quay về đúng cái nhập nhằng mà phương án C sinh ra để gỡ.

**Cạm bẫy đã biết, đừng lặp lại.** `extract_field_by_code()` hiện trả `None`
trần cho BA nguyên nhân khác nhau (field không có trong bảng mã của chuẩn;
không thấy marker mẫu biểu; không khớp được số). Muốn phân biệt thì phải cho
nó nói ra lý do, chứ không đọc được từ giá trị trả về.

Và nhánh OCR ở `router.py:147-151` đang **lọc bỏ hẳn** field `None`
(`if gia_tri is not None`), nên hiện không còn dấu vết field nào đã thử mà
trượt. Chỗ này phải sửa thì probe mới có cái để ghi.
