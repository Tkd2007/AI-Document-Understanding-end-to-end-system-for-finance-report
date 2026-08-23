# Bàn giao — hạ tầng nghiên cứu ViFinKIE

Viết để một phiên Claude khác đọc và làm tiếp mà **không cần hỏi lại gì**.
Mọi tham chiếu đều là đường dẫn file hoặc commit hash.

- **Nhánh:** `research` (tách từ `main` tại `4216291`)
- **Commit gần nhất:** `df96ff2`
- **Test:** **340 xanh / 0 đỏ**. `ruff check src tests` sạch.
- **Bộ chỉ tiêu:** 21 với TT99, 20 với TT200; 7 đẳng thức. MỐC 1 đã đóng.
- **Cập nhật:** 23/08/2026

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
2. [MOC1-DOI-CHIEU.md](MOC1-DOI-CHIEU.md) — bảng đối chiếu ma trận ràng buộc
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
| `1d3f89d` | Mốc 1 | `constraints_scenarios.py` + `MOC1-DOI-CHIEU.md` |
| `9724504` | — | `ANNOTATION-GUIDELINE.md` |
| `2c14420` | — | `fetch.py --dry-run` kiểm `SEC_USER_AGENT` |
| `3fb6472` | Mốc 1 | Trích đẳng thức từ Công báo, đợt 1 |
| **`023321c`** | A3 | **Sửa `FORM_MARKERS`: hậu tố a/b là KỲ, không phải Thông tư** — mục 10 |
| **`6744bee`** | Mốc 1 | **Thay đẳng thức giả thuyết bằng đẳng thức đã đối chiếu** — mục 10 |
| `e08d5e8` | Mốc 1 | Bảng đối chiếu đầy đủ cả hai chuẩn |
| `32db2f7` | Mốc 1 | Đóng các ô chưa xác nhận của bảng đối chiếu |
| **`4064519`** | **B4** | **Bộ chỉ tiêu lên 21, hai chuẩn hết đẳng cấu** — mục 10 |
| **`df96ff2`** | **Mốc 1** | **Ghi quyết định vào đăng ký trước, đóng hai ô chờ của guideline** |

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
đầu-cuối trên bảng 8 chỉ tiêu, 3 đẳng thức:

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

Chi tiết đầy đủ ở [MOC1-DOI-CHIEU.md](MOC1-DOI-CHIEU.md). Tóm tắt:

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
| Bỏ qua đẳng thức khi thiếu thành phần | **Chưa** | Quyết định của người — xem dưới |
| **C3** vòng lặp đọc lại | Chưa | **MỐC 3** — mục 13 |
| **C4** verdict ba trạng thái | Chưa | C3 |
| **D2** runner / **D3** bảng / **D4** hình | Chưa | C4, rồi D2 |

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
4. `MAX_CHANGES_MAC_DINH = 2` — đo trên bài toán 8 chỉ tiêu, **chưa đo trên
   25**. Đo lại sau khi chốt bộ trường.
5. Bảng bốn cặp nhầm chữ số trong `repair/candidates.py` — cặp áp đảo `9→0`
   **không nằm trong bảng**. Lý do chưa sửa ở mục 9.
6. `MAX_UPLOAD_BYTES = 50 MB` trong `api.py` — chọn theo đúng một tài liệu.

---

## 13. MỐC 3 — mốc phải dừng thật, và nó đang mở

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

# Đo engine OCR trên ô số (cần easyocr; vài phút vì chạy CPU)
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/ocr_compare.py easyocr

# Trích lại text từ Công báo (poppler và antiword đã có sẵn)
pdftotext -layout -enc UTF-8 "data/legal/<file>.pdf" out.txt
antiword -m UTF-8.txt "data/legal/<file>.doc" > out.txt

# Tải hồ sơ XBRL — CHỈ CHẠY ĐƯỢC TRÊN MÁY NGƯỜI DÙNG
export SEC_USER_AGENT="Tên thật email@example.com"
python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --dry-run
```

---

## 16. Bước kế tiếp đề xuất

Mốc 1 đã đóng, nên đường găng giờ đi qua Mốc 3.

1. **Quyết cách xử lý thành phần thiếu trong đẳng thức** (mục 12). Đây là
   việc duy nhất còn lại mà B4 mở ra, và nó chặn việc chạy pipeline trên tài
   liệu thật — không quyết thì đẳng thức phân rã tài sản ngắn hạn gần như
   không bao giờ chạy, tức phần lớn cái Mốc 1 mua được không tới được
   pipeline.
2. **Người dùng chạy `fetch.py`** để có dữ liệu XBRL (mục 13). Việc này
   không chặn bởi mục 1 — làm song song được.
3. **Chạy MỐC 3** ngay khi có dữ liệu. **Đây là mốc phải dừng thật** — nếu
   baseline 9 ngang bằng thì toàn bộ novelty tầng 1 sai, dừng và lùi paper
   về tầng dataset + identifiability. Không chạy tiếp C3 và ablation trước
   khi biết kết quả, vì chạy tiếp chỉ để tích luỹ số liệu cho một luận điểm
   đã sai.
4. **Sau khi qua Mốc 3:** C3 rồi C4, rồi D2/D3/D4.

Ngoài đường găng, ba việc phải xong trước khi có con số vào paper, và không
việc nào chặn việc nào:

- **Pilot 20 tài liệu gold** rồi tính lại power (MỐC 2). Guideline đã sẵn
  sàng, bộ chỉ tiêu đã chốt, nên việc này bắt đầu được ngay.
- **Chốt người gán nhãn thứ hai** cho 20 tài liệu, hoặc dùng phương án dự
  phòng ở `ADDENDUM` mục 5 (tự gán lại sau hai tuần).
- **Đo trần người** trên 10 tài liệu, 15 phút mỗi tài liệu.

**Lưu ý khi merge sang `main`:** CI chỉ chạy trên `main` và trên pull
request, nên lỗi thiếu thư viện ở mục 8 chỉ lộ ra ở lần merge đầu tiên. Nó
đã được sửa, nhưng nguyên tắc thì còn: thêm bất kỳ import mức module nào
cũng phải sửa danh sách cài trong `.github/workflows/ci.yml`.
