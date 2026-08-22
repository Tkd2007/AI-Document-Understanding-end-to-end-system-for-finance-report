# Bàn giao — hạ tầng nghiên cứu ViFinKIE

Tài liệu này viết để một phiên Claude khác đọc và làm tiếp mà **không cần
hỏi lại gì**. Nó đứng độc lập: mọi tham chiếu đều là đường dẫn file hoặc
commit hash, không có đại từ trỏ về một hội thoại đã mất.

- **Nhánh làm việc:** `research` (tách từ `main` tại `4216291`)
- **Commit gần nhất:** `9c3f7c9`
- **Trạng thái test:** **264 xanh / 0 đỏ**. `ruff check src tests` sạch.
- **CHƯA PUSH:** ba commit `f1d236e`, `1dacb34`, `9c3f7c9` mới chỉ nằm ở
  máy. `origin/research` vẫn đang ở `ff79991`.
- **Cập nhật:** 22/08/2026

---

## 1. Đọc gì trước

Bốn tài liệu nguồn, người dùng giữ bản gốc (chúng **không** nằm trong repo):

| Tài liệu | Vai trò |
|---|---|
| `FINAL-proposal-reread-dont-repair.md` | Proposal nghiên cứu, bốn giả thuyết H0–H3 |
| `ADDENDUM-statistical-treatment.md` | Phụ lục vá phần xử lý thống kê |
| `FINAL-repo-changes.md` | Bản dịch proposal sang việc trong repo |
| `BUILD-SPEC.md` | **Đặc tả thi công** — thứ đang được thực hiện |

Trong repo, đọc theo thứ tự:

1. [PREREGISTRATION.md](PREREGISTRATION.md) — bốn giả thuyết, chỉ số chính
   chốt trước, điều kiện phản chứng, ba mốc dừng. **Không sửa đè lên nội
   dung gốc**; mọi thay đổi ghi vào mục "Sửa đổi" ở cuối file kèm ngày và
   lý do, nếu không thì việc đăng ký trước mất hết giá trị. Mục Sửa đổi
   hiện đã có một mục ngày 22/08/2026 — đọc nó, vì nó chốt một hạn chế
   thật của phương pháp.
2. [data/output/identifiability_TT99.md](data/output/identifiability_TT99.md)
   — kết quả Mốc 1, đọc mục 4 dưới đây trước khi đi tiếp.
3. [src/eval/stats.py](src/eval/stats.py) — docstring đầu module giải thích
   nguyên tắc chi phối toàn bộ phần thống kê.
4. [src/repair/diagnose.py](src/repair/diagnose.py) — docstring đầu module
   và các hằng số ở đầu file. Đây là chỗ tập trung nhiều quyết định thiết
   kế nhất, và mọi quyết định đều có lý do viết kèm.

**File này nằm ở gốc repo nhưng CHƯA được commit.** Nếu muốn nó theo lịch
sử git thì `git add HANDOFF.md` rồi commit riêng.

---

## 2. Bối cảnh một đoạn

Repo gốc là một pipeline **trích xuất** 11 chỉ tiêu tài chính từ PDF báo
cáo tài chính Việt Nam: PDF → DocLayout-YOLO cắt vùng bảng → EasyOCR hoặc
VLM (Gemma qua OpenRouter) → validation → FastAPI.

Việc đang làm là biến nó thành hạ tầng **nghiên cứu** để kiểm bốn giả
thuyết. Đóng góp cốt lõi nằm ở H3, và nó gói trong một câu:

> Mọi paradigm sửa lỗi trước đây (Fellegi-Holt, data reconciliation,
> HoloClean) đều SỬA một tập số cố định. Không cái nào ĐỌC LẠI được nguồn.
> Với tài liệu thì ảnh gốc vẫn còn.

Hệ quả trực tiếp cho mọi quyết định kỹ thuật: **tập ứng viên sửa lỗi phải
ĐÓNG và mọi phần tử phải truy được về một chỗ cụ thể trên tài liệu.** Nếu
tồn tại đường nào để một con số không thuộc tập ứng viên lọt vào kết quả
thì hệ ép số được, và toàn bộ lập luận chống bịa sụp.

---

## 3. Đã làm — 14 commit trên `research`

| Commit | Mục | Nội dung |
|---|---|---|
| `689e2d0` | **D1** | `PREREGISTRATION.md` — đăng ký trước giả thuyết, có dấu thời gian git trước mọi thí nghiệm |
| `4b20aea` | **A1** | Điều kiện áp dụng cho `FIELD_RELATIONS` |
| `7fd34f0` | **A3** | Tách bảng mã số dòng và mẫu biểu theo TT200 / TT99 |
| `437e2a1` | **A4** | Chuẩn hoá đơn vị tính + mỏ neo biên độ lớn tuyệt đối |
| `88c031e` | **A2** | `src/constraints.py` — ma trận ràng buộc và identifiability |
| `c85c812` | **B1** | Cờ `DISABLE_CONSTRAINT_GATE` để đo H1 không vòng lặp luận chứng |
| `a5ec83e` | **B2** | Confidence từng trường bằng self-consistency |
| `0d74195` | **B3** | Provenance từng trường qua suốt chuỗi |
| `ad6684a` | **B6** | Eval harness, thống kê, trường tái lập |
| `2cf613a` | **C1** | Sinh tập ứng viên sửa lỗi từ tài liệu |
| `ff79991` | **C2** | WIP — 2 test đỏ *(đã sửa xong ở `f1d236e`)* |
| **`f1d236e`** | **C2** | **Hai baseline đối chứng không còn thua vì lý do cài đặt** |
| **`1dacb34`** | **B5** | **Tầng đánh giá XBRL** |
| **`9c3f7c9`** | **C2** | **Trần `max_changes` và tách ABSTAIN theo lý do** |

Ba commit in đậm là việc của ngày 22/08/2026, mô tả chi tiết ở mục 6, 7, 8.

Ngoài ra có một commit trên `main` từ trước loạt này: `debac2f` (test khoá
threading cho `merge_into_totals`).

### Cái bẫy đã gặp ở các mục cũ

**A1 — điều kiện áp dụng cho bất đẳng thức.**
Ba trong sáu quan hệ trong `FIELD_RELATIONS` ngầm giả định doanh nghiệp có
lãi và VCSH dương, mâu thuẫn với `FIELD_RULES` vốn cho phép âm. Mâu thuẫn
này không nằm yên: `FIELD_RELATIONS` là một phần cổng `is_acceptable()`,
nên gặp báo cáo lỗ thì router coi kết quả **đúng** là chưa đạt, gọi VLM, và
`has_warnings` mở đường cho VLM ghi đè lên số vốn đã đúng.
*Đánh đổi đã biết:* điều kiện áp dụng đọc từ chính một field cũng do model
trích ra, nên field điều kiện bị đọc sai thành âm sẽ làm luật tự tắt. Có
test `test_field_dieu_kien_bi_doc_sai_thi_luat_tu_tat` chốt hành vi đó.

**A2 — ma trận ràng buộc.** Xem mục 4, đây là chỗ có kết quả quan trọng nhất.

**A3 — hai chuẩn.** Bẫy tinh vi nhất: chuỗi `"B 01"` nằm gọn trong `"B 01a"`,
nên marker TT200 sẽ khớp luôn trang TT99 nếu để trần. Marker TT200 vì vậy
mang `(?!\s*a)`. `detect_standard()` trả `None` khi không đủ dấu hiệu hoặc
khi trang nhắc cả hai chuẩn — **không bao giờ đoán bừa**, vì nhận diện sai
chuẩn là một chế độ lỗi riêng cần đo được.

**A4 — đơn vị tính.** Mỏ neo tuyệt đối duy nhất phá được bất biến scale. Hệ
ràng buộc là thuần nhất nên `Aδ = (c−1)Ax* = 0`: sai đơn vị toàn cục
**luôn** vô hình với mọi đẳng thức. `TOTAL_ASSETS_BOUNDS` là check duy nhất
trong `validate_result` không bất biến với phép nhân vô hướng.
`don_vi_tinh` cố ý **không** nằm trong `FIELD_MAP` vì `validate_result`
chạy `coerce_number` trên mọi khoá của nó.

**B1 — tắt cổng ràng buộc.** Pipeline đang dùng chính đẳng thức kế toán làm
cổng quyết định fallback, nên đo AUROC của vi phạm ràng buộc trên đầu ra đó
là vòng lặp luận chứng. Lượt chạy ở chế độ đo được đánh dấu bằng khoá
`constraint_gate: false` trong `metrics.jsonl`.

**B2 — confidence.** Ba quyết định trong cách tính phiếu, cả ba đều có thể
làm sai theo hướng lạc quan: `None` cũng là ứng viên bỏ phiếu; mẫu số là
`n_samples` chứ không phải số mẫu parse được; hoà phiếu thì ưu tiên non-null
rồi tới giá trị xuất hiện sớm nhất. `n_samples > 1` với `temperature = 0`
**ném lỗi** thay vì chạy.

**B3 — provenance.** Chuỗi từng đứt ở ba chỗ. Lọc IoU đi kèm chứ không phải
việc rời: YOLO trả box chồng nhau (quan sát ở trang 31 và 35 báo cáo VNM),
và kể từ khi có provenance thì đó là **sai dữ liệu** chứ không còn là lãng
phí. `bbox` trả về là bbox **đã cộng padding và đã clamp**, có test cắt lại
rồi so từng byte.

**B6 — eval harness.** Bootstrap **theo cụm tài liệu**, không theo trường.
Có test chứng minh việc phân cụm nới khoảng tin cậy hơn gấp đôi trên dữ
liệu phân cụm. Hàm `item_bootstrap_ci` (cách SAI) được giữ lại có chủ đích
để paper nêu định lượng khoảng tin cậy sẽ hẹp giả tạo bao nhiêu.
**Không dùng DeLong** — lý do trong `PREREGISTRATION.md` mục 1 và docstring
`src/eval/stats.py`. McNemar dùng kiểm định nhị thức **chính xác** nên
không cần scipy cho phần đó.

**C1 — tập ứng viên.** Năm nguồn. `cost = −log(xác suất tiên nghiệm)` để
cộng cost tương đương nhân xác suất. **Bốn xác suất tiên nghiệm trong
`XAC_SUAT_TIEN_NGHIEM` chưa đo trên dữ liệu thật** — xem mục 9.

---

## 4. MỐC 1 — vẫn đang chờ người quyết, vẫn chặn B4

**Trạng thái không đổi so với bản bàn giao trước. Đây vẫn là việc quan
trọng nhất mà AI không làm thay được.**

Chạy `python src/constraints.py` sinh lại hai báo cáo. Kết quả hiện tại,
giống nhau ở cả hai chuẩn:

| Chỉ số | Giá trị |
|---|---|
| `rank(A)` | **3** |
| `dim null(A)` | **8 / 11** chiều lỗi vô hình |
| Field định vị được lỗi một-trường | **1 / 11** — chỉ `tong_tai_san` |
| Field cột toàn 0 (không phát hiện được) | **3** |

Ba field không ràng buộc nào bảo vệ: `hang_ton_kho`,
`loi_nhuan_truoc_thue`, `loi_nhuan_sau_thue`. Đáng chú ý nhất là
`hang_ton_kho` vì đó đúng là field đã có lỗi đọc thật trên báo cáo VNM.

Các field còn lại đi thành cặp không phân biệt được:
`tai_san_ngan_han ↔ tai_san_dai_han`, `no_phai_tra ↔ von_chu_so_huu`, và
`doanh_thu_thuan ↔ gia_von_hang_ban ↔ loi_nhuan_gop`.

**Phát hiện quyết định hướng đi:** `minimal_localizing_set()` trả `None` —
với ba đẳng thức hiện có, **không tập con nào** của 11 chỉ tiêu làm mọi lỗi
một-trường định vị được. Nút thắt là số **ĐẲNG THỨC**, không phải số chỉ
tiêu. Thêm field mà không thêm đẳng thức thì con số 1/11 không nhúc nhích
và H2 vẫn vô nghĩa.

**Người chủ trì phải làm, không được để AI làm thay:**

1. Đối chiếu từng dòng bảng mã trong [src/fields_config.py](src/fields_config.py)
   với **Phụ lục IV văn bản gốc** của cả hai Thông tư. Cảnh báo đã ghi ngay
   tại chỗ trong file. Chỗ lệch đã biết: tổng tài sản là 270 ở TT200, 280 ở
   TT99. Còn chưa xác nhận: ký hiệu mẫu biểu TT200 là `B01-DN` hay
   `B01a-DN`, và bộ đẳng thức của TT99 (hiện dùng chung với TT200).
2. Trả lời câu hỏi mà kết quả trên đặt ra: **Phụ lục IV còn những đẳng thức
   nào chưa khai thác?** Đó mới là đường ra cho H2.
3. Chốt bộ trường. Nó quyết định chi phí gán nhãn tay cho 60 tài liệu gold,
   khoản đắt nhất của cả dự án.

---

## 5. Việc của ngày 22/08/2026 — tóm tắt

Ba việc, theo thứ tự đã làm:

1. **Sửa 2 test đỏ của C2** (`f1d236e`) — cả hai đều là chuyện baseline đối
   chứng bị làm yếu bởi chi tiết cài đặt chứ không phải bởi khoa học.
2. **Dựng B5, tầng đánh giá XBRL** (`1dacb34`) — sáu module, 35 test.
3. **Chốt trần `max_changes` và tách ABSTAIN theo lý do** (`9c3f7c9`) —
   xuất phát từ một phép đo thời gian chạy trong lúc thử B5.

---

## 6. C2 — đã xong, hai test đỏ sửa thế nào

File: [src/repair/diagnose.py](src/repair/diagnose.py),
test: [tests/test_diagnose.py](tests/test_diagnose.py) (31 test, tất cả xanh).

### Test đỏ 1 — baseline 8 trả nghiệm không thưa

**Nguyên nhân:** IRLS xuất phát từ trọng số đều nên vòng đầu ra đúng nghiệm
bình phương tối thiểu. Với hệ đối xứng như `a + b = c` thì nghiệm đó lại
đều (δ = 5/3 ở cả ba toạ độ), nên trọng số vòng sau vẫn đều và thuật toán
kẹt ở **điểm bất động thật sự** — không lịch giảm epsilon nào thoát ra
được, vì không có bất đối xứng nào để bám vào. Thêm nữa, trên chính ví dụ
đó nghiệm rải đều **cũng** có chuẩn L1 bằng 5: cực tiểu L1 suy biến, và thứ
test thật sự đòi là nghiệm **đỉnh**.

**Đã sửa:** thay IRLS bằng `scipy.optimize.linprog` (HiGHS), tách
`delta = u − v` với `u, v ≥ 0` rồi tối thiểu hoá `Σ(u + v)`. Nghiệm LP là
nghiệm đỉnh nên số toạ độ khác 0 không vượt quá `rank(A)`.

**Quyết định về thư viện, cần biết để không "sửa ngược":** `scipy` **đã có
sẵn trong image từ trước**, kéo về theo chuỗi
`easyocr → scikit-image → scipy`. Dòng `scipy==1.18.0` thêm vào
[requirements.txt](requirements.txt) là **khai báo thứ đang dùng, không
phải cài thêm**. Điều này không mâu thuẫn với quyết định trước đó là không
thêm `pulp` cho `diagnose()`: `pulp` chưa có trong môi trường và kéo theo
binary CBC, còn scipy thì đã ở đó rồi.

**Lợi ích ngoài việc test xanh:** baseline 8 hết là nghiệm xấp xỉ, nên bỏ
được dòng caveat "phải nêu trong paper rằng đây là nghiệm xấp xỉ". Baseline
mạnh hơn thì kết luận về phương pháp đề xuất đáng tin hơn.

### Test đỏ 2 — baseline 9 chọn trường theo thứ tự chỉ số

Bản bàn giao trước kết luận "kỳ vọng trong test SAI, code ĐÚNG". Kết luận
đó **chỉ đúng một nửa**, và nửa còn lại quan trọng.

Đúng ở chỗ: với `a + b = c` thì sửa riêng `a`, `b` hay `c` đều đủ, nên ba
tập trường hoà nhau về cardinality và test không bị toán học ép buộc.

Nhưng `diagnose()` duyệt **hết** mọi tổ hợp ở một cardinality rồi mới chọn
theo hàm mục tiêu, còn `diagnose_fellegi_holt_donor()` trả về tổ hợp **đầu
tiên** theo thứ tự chỉ số rồi thoát — trong khi docstring của chính nó
khẳng định "Giống hệt `diagnose()` ở việc chọn TRƯỜNG nào sửa". Nghĩa là
baseline trung tâm của cả nghiên cứu đang thắng thua theo thứ tự khai báo
field trong `fields_config`.

**Đã sửa:** donor cũng duyệt hết một cardinality rồi phân xử bằng **tổng
khoảng cách tới donor**. Trường không có giá trị donor thì lấy chính giá
trị hiện tại làm mốc, nên khoảng cách của nó đo đúng phần phải bịa ra khi
không ai đỡ. Certificate ghi thêm `lech_so_voi_donor` cho từng trường bị
sửa.

**Ba test mới** chốt lại:
- L1 trên hệ hai đẳng thức lồng nhau, `n_changed ≤ rank(A)` — trên hệ một
  đẳng thức thì hạng bằng 1 nên mọi nghiệm đều thưa sẵn, không phân biệt
  được hai bộ giải.
- Donor chọn `b` chứ không chọn `a`, dù `a` đứng trước và cũng khả thi.
- Ca không trường đơn lẻ nào gánh nổi residual: sáu cặp cùng thoả, donor
  biết đúng `a` và `d` nên cặp `{a, d}` phải thắng — và nó khôi phục lại
  đúng giá trị thật.

---

## 7. B5 — tầng đánh giá XBRL, đã dựng xong

**Module mới:** [src/eval/xbrl_tier/](src/eval/xbrl_tier/) — sáu file.
**Test:** [tests/test_xbrl_tier.py](tests/test_xbrl_tier.py), 35 test, không
cái nào chạm mạng.

### Vì sao tầng này tồn tại

Tập gold 60 tài liệu cho khoảng 1500 trường, nhưng H2 và H3 đo trên **SỐ
LỖI** chứ không phải số trường. Với tỷ lệ lỗi 5–15% thì chỉ có 75–225 lỗi,
mà 75 quan sát cho khoảng tin cậy rộng chừng ±0,11 — đủ để nói "phương pháp
này chạy được", không đủ để nói "hơn baseline 5 điểm". Nên tầng này là
**điều kiện để H2 và H3 có power**, không phải mục làm thêm.

Phân vai: **XBRL lo power, gold Việt Nam lo validity.**

### Sáu module và quyết định thiết kế của từng cái

| File | Việc | Quyết định cần biết |
|---|---|---|
| `linkbase.py` | Đọc `*_cal.xml` thành đẳng thức, dựng ma trận A | Parse thẳng bằng `xml.etree`, **không dùng `arelle`** — cùng lý do C2 không cắm MILP |
| `facts.py` | companyfacts → bảng giá trị | **Chỉ lấy fact của CÙNG MỘT hồ sơ** — xem cảnh báo dưới |
| `table.py` | Cấu trúc bảng hai cột kỳ | Lỗi lệch dòng/cột định nghĩa bằng hình học trang nên cần thứ tự dòng và danh sách cột |
| `render.py` | Bảng → ảnh + bbox từng ô | Vẽ thẳng bằng Pillow, **không dựng HTML rồi chụp** |
| `inject.py` | Inject lỗi theo taxonomy mục 3.1 proposal | Bảng nhầm chữ số cố ý **RỘNG HƠN** bảng ở `repair.candidates` |
| `fetch.py` | Tải hồ sơ từ EDGAR | **SCRIPT CHO NGƯỜI DÙNG CHẠY**, container không có mạng tới sec.gov |

### Ba chỗ dễ làm hỏng nếu không biết lý do

**(a) `facts.py` chỉ lấy fact của cùng một hồ sơ.** companyfacts gộp mọi
lần công bố của cùng một chỉ tiêu, nên cùng một ngày kết thúc kỳ có thể có
nhiều giá trị khác nhau — bản gốc và các bản trình bày lại ở hồ sơ sau.
Trộn giá trị của hai hồ sơ vào một bảng sẽ **phá vỡ đẳng thức kế toán một
cách âm thầm**, và khi đó tầng này mất đúng thứ duy nhất làm nên giá trị
của nó là ground truth chắc chắn đúng. Một bảng không cân vì lý do đó sẽ bị
đếm thành "lỗi trích xuất" trong khi thật ra là lỗi của bước dựng dữ liệu.
Test `test_chi_lay_fact_cua_dung_mot_ho_so` chốt chuyện này.

**(b) `inject.py` KHÔNG được dùng chung bảng nhầm chữ số với
`repair.candidates`.** Nếu bộ sinh lỗi và bộ sinh ứng viên sửa dùng chung
một bảng thì mọi lỗi inject đều nằm sẵn trong tập ứng viên theo đúng cấu
trúc, và phương pháp đề xuất thắng vì thí nghiệm được dựng cho nó thắng.
Đó là loại lỗi reviewer giết bài ngay. Nên `inject` thay một chữ số bằng
**bất kỳ chữ số nào khác**, còn `repair.candidates` chỉ sinh bốn cặp hay
nhầm `(0,8) (1,7) (3,8) (5,6)`. Phần lỗi rơi ra ngoài tập ứng viên là phần
phương pháp **phải chịu thua**, và tỷ lệ đó tự nó là một con số đáng báo
cáo. **Đừng "thống nhất" hai bảng này lại.**

**(c) `render.py` ném lỗi khi font thiếu glyph.** Font đi kèm Pillow không
có glyph tiếng Việt có dấu — phát hiện lúc chạy thử: "Đơn vị tính" render
ra "□n v□ t□nh" mà ảnh vẫn trông như một cái bảng bình thường. Đây là lỗi
im lặng đúng nghĩa, chỉ lộ ra khi có người mở ảnh xem, thường là sau khi đã
chạy xong cả lượt thí nghiệm. Nên:
- Phần chữ cố định trên ảnh mặc định **tiếng Anh** (`Indicator`, `Unit: …`),
  vì dữ liệu tầng này là hồ sơ SEC.
- Ô trống dùng gạch nối ASCII `-` chứ không dùng gạch dài `—`, vì gạch dài
  cũng không có glyph.
- `render()` kiểm mọi ký tự sắp vẽ và **ném `ValueError`** nếu font không
  vẽ được. Muốn nhãn tiếng Việt — thứ ablation "Transfer XBRL → BCTC Việt
  Nam" cần — thì truyền `font_path` trỏ tới font có dấu, và truyền luôn
  `tieu_de_cot_chi_tieu` với `mau_dong_don_vi`.

### Kết quả chạy thử toàn chuỗi

Chuỗi `linkbase → bảng → inject → sinh ứng viên → chẩn đoán` đã chạy thông
đầu-cuối trên một bảng 8 chỉ tiêu, 3 đẳng thức. Ba quan sát:

1. Inject `DIGIT_SUB` vào `Cash` (`812.445.000 → 892.445.000`, đổi chữ số
   `1 → 9`) làm đúng **1 đẳng thức** vi phạm, khớp với bảng identifiability.
2. Giá trị thật **không** nằm trong tập ứng viên, vì cặp `1→9` không thuộc
   bốn cặp hay nhầm. `diagnose()` trả `ABSTAIN` — **thua đúng**, và đây
   chính là cơ chế ở mục (b) trên hoạt động như thiết kế.
3. Baseline 9 trả `REPAIRED` nhưng **sửa sai trường** — nó sửa `Receivables`
   bằng giá trị donor, cho ra một bảng cân đối hoàn hảo và sai sự thật. Đó
   đúng là thứ `fabrication_rate` trong `src/eval/metrics.py` sinh ra để
   bắt, và là minh hoạ sống cho luận điểm của H3.

Sau `inject_scale_toan_cuc` với `k = 3`, **mọi đẳng thức vẫn thoả tuyệt
đối** — bản chạy được của chứng minh một dòng ở `constraints.py` rằng sai
đơn vị toàn cục luôn vô hình.

---

## 8. Trần `max_changes` và tách ABSTAIN — commit `9c3f7c9`

### Phép đo dẫn tới thay đổi

Trong lúc chạy thử B5, `diagnose()` **hết 30 giây** trên một bài toán chỉ
có 8 chỉ tiêu và 87 ứng viên. Đo lại có kiểm soát:

| Ca | `max_changes` | Kết quả | Thời gian |
|---|---|---|---|
| Lỗi KHÔNG sửa được | không đặt | ABSTAIN vì **hết giờ** | **30.158 ms** |
| Lỗi KHÔNG sửa được | 2 | ABSTAIN vì **vô nghiệm** | **16 ms** |
| Lỗi sửa được (đổi dấu) | không đặt | REPAIRED, đúng `Cash` | 1,8 ms |

Ca có nghiệm thì tức thì. **Chi phí nằm trọn ở việc chứng minh KHÔNG có
nghiệm**, mà đó lại là ca thường gặp vì tập ứng viên đóng cố ý không chứa
mọi cách sửa. Với tầng XBRL hàng nghìn tài liệu, 30 giây một tài liệu là
không chạy nổi.

### Đã chốt gì

`MAX_CHANGES_MAC_DINH = 2`, áp cho `diagnose()` **và** cho baseline 9, vì
H3 so ở cùng ngân sách và trần thay đổi là một phần của ngân sách đó.

Baseline 8 **không** áp trần và để mặc định `None` một cách có chủ đích:
delta của nó chạy tự do trong `ℝⁿ`, chặn số trường được sửa là khái niệm
của tìm kiếm rời rạc chứ không áp lên quy hoạch tuyến tính được, và nghiệm
đỉnh đã tự giới hạn số toạ độ khác 0 không vượt quá `rank(A)`. Nhận tham số
rồi lặng lẽ không dùng thì runner sẽ tưởng hai nhánh chạy cùng ràng buộc.

**Đây là hạn chế của phương pháp, không phải chi tiết cài đặt.** Một tài
liệu có ba trường cùng sai sẽ không được sửa, kể cả khi tổ hợp sửa đúng nằm
sẵn trong tập ứng viên. Đã ghi vào mục Sửa đổi của `PREREGISTRATION.md`
kèm ngày và lý do. **Bảng kết quả phải báo cáo tỷ lệ tài liệu rơi vào ca
đó.**

### Tách ABSTAIN — chỗ tinh tế nhất, đừng gộp lại

`Diagnosis` có thêm trường `ma_ly_do` lấy giá trị trong một **tập đóng**:

| Mã | Nghĩa |
|---|---|
| `vo_nghiem` | Đã vét cạn **MỌI** tổ hợp và không có nghiệm |
| `vuot_tran_thay_doi` | Hết tổ hợp trong trần `max_changes` — **chưa duyệt tới các tổ hợp lớn hơn** |
| `het_gio` | Hết ngân sách thời gian |
| `thieu_gia_tri` | Không dựng được vector nên không kiểm được ràng buộc |
| `bo_giai_that_bai` | Bộ giải LP của baseline 8 không trả nghiệm |
| `""` | Không ABSTAIN |

**Vì sao bắt buộc tách:** luận điểm chống bịa phát biểu là *không cách đọc
nào của tài liệu này làm bảng cân đối được*. **Chỉ `vo_nghiem` mới chứng
minh được điều đó.** `vuot_tran_thay_doi` chỉ nghĩa là ta đã không tìm —
một nghiệm nhiều trường hơn vẫn có thể tồn tại. Gộp hai thứ lại là tính
công cho phương pháp ở những ca nó không chứng minh được gì.

Trước thay đổi này, muốn phân biệt phải so khớp chuỗi tiếng Việt trong
`ly_do_abstain`, tức một lần sửa câu chữ trong thông báo lỗi sẽ làm hỏng
thống kê mà không có gì báo.

---

## 9. Chưa làm

Theo thứ tự phụ thuộc trong `BUILD-SPEC.md` phần E.

| Mục | Trạng thái | Chặn bởi |
|---|---|---|
| **C2** | **XONG** | — |
| **B5** | **XONG** | — |
| **B4** mở rộng bộ trường | Chưa | Mốc 1 (mục 4) |
| **C3** vòng lặp đọc lại | Chưa | **MỐC 3** — xem mục 10 |
| **C4** verdict ba trạng thái | Chưa | C3 |
| **D2** runner thí nghiệm | Chưa | C4 |
| **D3** bảng kết quả | Chưa | D2 |
| **D4** hình | Chưa | D2 |
| **Phần F** dọn dẹp | Chưa (1/8 xong) | Không chặn gì |
| **README** đã cũ | Chưa | Không chặn gì |

### Hằng số chưa hiệu chỉnh — phải đo lại trước khi tin

Bốn nhóm, đều đã ghi cảnh báo ngay tại chỗ trong code:

1. `TOTAL_ASSETS_BOUNDS` trong [src/fields_config.py](src/fields_config.py)
   — hiện `(1e10, 1e15)`, dựa trên suy luận về phổ doanh nghiệp niêm yết,
   chưa dựa trên phân phối đo được.
2. `XAC_SUAT_TIEN_NGHIEM` trong
   [src/repair/candidates.py](src/repair/candidates.py) — bốn xác suất tiên
   nghiệm của các chế độ lỗi. Chúng đi **thẳng** vào hàm mục tiêu của C2,
   nên đặt sai thì thuật toán vẫn chạy và vẫn cho nghiệm, chỉ là ưu tiên
   sai loại sửa. Phải ước lượng lại từ phân loại lỗi trên tập gold.
3. `FIELD_RATIO_BOUNDS` và `REVENUE_TO_ASSETS_LIMIT` — hiệu chỉnh trên
   **đúng một công ty** (VNM Q1/2026). Người dùng đã ra chỉ thị rõ: **không
   chỉnh các ngưỡng này khi dữ liệu mới chỉ có một công ty**, chờ bộ báo
   cáo nhiều công ty.
4. `MAX_CHANGES_MAC_DINH = 2` trong
   [src/repair/diagnose.py](src/repair/diagnose.py) — đã đo trên bài toán 8
   chỉ tiêu, **chưa đo trên bài toán 25 chỉ tiêu**. Đo lại sau khi Mốc 1
   chốt bộ trường, vì không gian tìm kiếm tăng theo luỹ thừa của số ứng
   viên mỗi trường.

### Phần F — dọn dẹp, không chặn nghiên cứu

Đã xong: bỏ `validate_result` gọi hai lần ở `api.py` (làm kèm B2, vì lần
gọi thứ hai giờ không chỉ thừa mà còn sai — nó chạy trên dữ liệu đã quy đổi
nhưng không còn khoá đơn vị tính).

Còn lại: `MAX_UPLOAD_SIZE`, early-stop ở vòng region, `PATIENCE_PAGES` khi
eval, tách `requirements-dev.txt`, `save=False` cho đường API, latency
histogram, và **quyết định engine OCR** (spec nói rõ không được để trống,
reviewer sẽ hỏi — hoặc đổi sang PaddleOCR, hoặc đo Levenshtein accuracy
riêng cho ô SỐ trên tập gold để chứng minh trên chữ số thì khác).

### README đã lệch với repo

[README.md](README.md) vẫn mô tả pipeline trích xuất cũ. Cụ thể:
- Mục "Not yet done" ghi *"Chuẩn hoá đơn vị tính… Cần thêm field đơn vị
  hoặc bước quy đổi"* trong khi A4 (`437e2a1`) đã làm xong.
- Không hề nhắc tới `src/constraints.py`, `src/eval/`, `src/repair/` — tức
  toàn bộ phần nghiên cứu.

Không chặn gì, nhưng nó là tài liệu đầu tiên người ngoài đọc.

---

## 10. MỐC 3 — mốc phải dừng thật, và nó đang tới

`BUILD-SPEC.md` phần E nói rõ:

> **MỐC 3 — sau C2, chạy baseline 9.** Nếu baseline 9 ngang bằng phương
> pháp đề xuất thì luận điểm "đọc lại nguồn" sai. Dừng, báo cáo, và lùi
> paper về tầng dataset + identifiability. Đừng chạy tiếp C3 và toàn bộ
> ablation trước khi biết kết quả này.

C2 đã xong nên **mốc này đang mở**. Tầng XBRL vừa dựng chính là thứ làm nó
đánh giá được ở quy mô có power, nhưng nó cần dữ liệu thật.

### Việc người dùng phải chạy — container không có mạng tới sec.gov

```bash
export SEC_USER_AGENT="Trần Kim Danh trankimdanh2007@gmail.com"

# Xem trước sẽ gọi những URL nào, KHÔNG chạm mạng
python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --dry-run

# Tải thật
python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --out data/xbrl
```

SEC chặn IP nếu thiếu header `User-Agent` có tên thật và email, hoặc nếu
quá 10 request mỗi giây. Script đặt trần 5/giây để còn biên, và **ném lỗi
ngay** khi thiếu `SEC_USER_AGENT` thay vì điền một giá trị mặc định.

### Sau khi có dữ liệu

Chạy so `diagnose()` với `diagnose_fellegi_holt_donor()` trên cùng bộ tài
liệu, cùng ngân sách, cùng trần `max_changes`. Hai chỉ số phải báo cáo cùng
lúc, theo `PREREGISTRATION.md`:

- tỷ lệ lỗi câm giảm được bao nhiêu, **VÀ**
- chỉ số chống bịa có tăng không.

Thắng ở chiều một mà thua ở chiều hai là kết quả tiêu cực và phải nói ra.

Đếm riêng `ma_ly_do == "vo_nghiem"` và `ma_ly_do == "vuot_tran_thay_doi"`,
lý do ở mục 8.

---

## 11. Chỗ đã đi khác `BUILD-SPEC.md` — có chủ đích, đã kiểm chứng

Tám chỗ. Ghi lại đầy đủ để phiên sau không "sửa ngược" lại theo spec.

**1. `src/types.py` → `src/extraction_types.py`.** Spec đặt tên module kiểu
dùng chung là `types.py`. **Không dùng được.** Repo import phẳng với
`pythonpath = src`, nên `src/types.py` che khuất module `types` của thư
viện chuẩn, mà `enum` lại `from types import MappingProxyType` — trình
thông dịch chết ngay lúc khởi động với lỗi circular import không hề gợi ý
nguyên nhân. Đã kiểm chứng bằng cách chạy thật trước khi đổi tên.

**2. Test đơn điệu của `minimal_localizing_set` kiểm chiều NGƯỢC với spec.**
Spec yêu cầu chốt "thêm field vào tập ứng viên không làm bộ tối thiểu NHỎ
ĐI". Chiều đó sai về toán: tập ứng viên rộng hơn chỉ thêm lựa chọn chứ
không bớt, nên cực tiểu chỉ có thể giữ nguyên hoặc nhỏ đi. Test theo đúng
chữ của spec sẽ đóng đinh một bất biến sai vào bộ test.

**3. Báo cáo identifiability được gỡ khỏi `.gitignore`.** Spec bảo ghi vào
`data/output/`, nhưng cả thư mục đó bị ignore nên artifact Mốc 1 sẽ không
bao giờ tới tay người chủ trì. Giữ nguyên đường dẫn spec yêu cầu và thêm
ngoại lệ cho đúng `identifiability_*.md` — nó chỉ chứa ma trận ràng buộc,
không có số liệu doanh nghiệp nào.

**4. Trần ứng viên mỗi trường để 12 thay vì 10.** Riêng nguồn `scale` đã
đóng góp 6 ứng viên có cấu trúc khác hẳn nhau, và cắt bớt chúng là cắt đúng
chế độ lỗi mà ràng buộc kế toán **chứng minh được** là không bao giờ phát
hiện nổi. Kèm theo là trần riêng cho mỗi nguồn, vì xếp thuần theo cost sẽ
để biến thể nhầm chữ số của một con số 14 chữ số chiếm hết chỗ.

**5. `PREREGISTRATION.md` không dùng DeLong cho H1**, khác với đề xuất
trong `ADDENDUM-statistical-treatment.md` mục 3. Lý do đã ghi trong cả hai
chỗ: DeLong xử lý đúng tương quan giữa các đường ROC nhưng vẫn giả định
quan sát độc lập, mà các trường trong cùng tài liệu thì không.

**6. Baseline 8 dùng `scipy.optimize.linprog`, và `scipy` được khai báo
trong `requirements.txt`.** Không mâu thuẫn với quyết định không thêm thư
viện cho `diagnose()`: scipy đã nằm sẵn trong image theo chuỗi
`easyocr → scikit-image → scipy`, nên đây là nói ra một phụ thuộc đang có
chứ không phải cài thêm. Dựa vào một phụ thuộc bắc cầu mà không khai báo là
tự đặt bẫy cho ngày easyocr đổi phụ thuộc của nó.

**7. B5 có SÁU module thay vì bốn như spec liệt kê.** Thêm `table.py` và
`facts.py`:
- `table.py` vì hai trong năm chế độ lỗi (lệch dòng, lệch cột) được định
  nghĩa bằng hình học của trang, nên cần thứ tự dòng và danh sách cột.
- `facts.py` vì spec không nói con số lấy từ đâu — `render.py` cần giá trị
  mà không có module nào cung cấp. Nó đọc companyfacts của SEC.

**8. `render.py` vẽ thẳng bằng Pillow thay vì dựng HTML rồi chụp ảnh.**
Đường HTML cần một trình duyệt không đầu hoặc `wkhtmltoimage` nằm trong
image — đúng cái giá mà dự án đã từ chối trả cho bộ giải MILP ở C2. Vẽ
thẳng còn cho **bbox chính xác từng ô miễn phí**, thứ tầng này cần làm
provenance ground truth; đi đường HTML thì bbox phải suy ngược từ ảnh đã
render, tức thêm một nguồn sai số vào chính thứ dùng làm chuẩn.
SynFinTabs vẫn nên trích dẫn và vẫn dùng lại được phần sinh ảnh của họ nếu
cần bản trình bày đa dạng hơn — nhưng **khác biệt phải giữ khi nhắc tới
họ**: nội dung SynFinTabs là số ngẫu nhiên nên không đẳng thức kế toán nào
đúng trên đó.

---

## 12. Quy ước bắt buộc tuân theo

Lấy từ `BUILD-SPEC.md` mục 0.2 và từ chỉ thị trực tiếp của người dùng.

| Quy ước | Chi tiết |
|---|---|
| **Import phẳng** | `pytest.ini` có `pythonpath = src`. Viết `from validation import ...`, KHÔNG viết `from src.validation import ...` |
| **Comment tiếng Việt** | Giải thích **tại sao**, không phải **cái gì**. Đọc `src/metrics.py` và `src/fields_config.py` để bắt giọng văn |
| **Docstring mô tả hiện trạng** | Không viết trạng thái dự định như thể đã làm xong |
| **Config tập trung** | Mọi hằng số miền nằm ở `fields_config.py` |
| **Nạp model lười** | Model nặng nạp trong hàm getter, không nạp lúc import. CI không cài torch |
| **Lint + test** | `ruff check src tests` rồi `pytest`, **trước khi báo xong** |
| **Test không cần mạng** | Dùng fixture và hàm giả, không gọi API thật |
| **Trạng thái tường minh** | Trạng thái ghi ra log/metrics/JSON phải là khoá tường minh, không để người đọc suy ra từ sự vắng mặt của khoá khác |
| **Commit** | Mỗi module một commit, message giải thích **lý do**. Commit thẳng lên nhánh đang làm việc, **không tự tạo branch** |
| **KHÔNG ghi danh nghĩa Claude** | **Tuyệt đối không** thêm trailer `Co-Authored-By: Claude` vào commit, cũng không thêm dòng `Generated with Claude Code` vào mô tả PR. Mọi thứ đứng tên người dùng `Tkd2007 <trankimdanh2007@gmail.com>` |

### Cái bẫy môi trường đã gặp

- **Console Windows mặc định cp1252.** In tiếng Việt ra stdout sẽ nổ
  `UnicodeEncodeError`. Mọi khối `__main__` phải có
  `sys.stdout.reconfigure(encoding="utf-8")`. Khi chạy script một dòng, đặt
  `PYTHONIOENCODING=utf-8` ở đầu lệnh.
- **Heredoc của bash vỡ khi nội dung có số lẻ dấu nháy đơn.** Viết file dài
  bằng công cụ ghi file, đừng dùng `cat > file <<'EOF'` với nội dung tiếng
  Việt có dấu nháy hoặc chuỗi `'''`.
- **`.env.docker` đang chứa OpenRouter key thật.** Nó **không** nằm trong
  git và chưa từng được commit (đã kiểm cả lịch sử), nhưng repo là public
  nên một lần `git add -f` nhầm là lộ.
- **Force-push bị trình phân loại quyền chặn.** Nếu cần viết lại lịch sử,
  phải để người dùng tự chạy lệnh trong terminal của họ.
- **`time.monotonic()` trên Windows quá thô để test những khoảng vài mili
  giây.** Test bộ điều tốc của `fetch.py` dùng đồng hồ giả qua
  `monkeypatch` chứ không đo thời gian thật — một test đỏ ngẫu nhiên tệ hơn
  không có test.

---

## 13. Lệnh hay dùng

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

# Tải hồ sơ XBRL — CHỈ CHẠY ĐƯỢC TRÊN MÁY NGƯỜI DÙNG
export SEC_USER_AGENT="Tên thật email@example.com"
python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --dry-run
python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --out data/xbrl
```

---

## 14. Bước kế tiếp đề xuất

Theo thứ tự, và lý do của thứ tự đó:

1. **Đưa Mốc 1 cho người chủ trì** (mục 4). Nó chặn B4, mà B4 quyết định
   chi phí gán nhãn — khoản đắt nhất của dự án. Câu hỏi thật cần trả lời
   không phải "trích bao nhiêu field" mà **"Phụ lục IV còn đẳng thức nào
   chưa khai thác"**, vì nút thắt là số đẳng thức chứ không phải số chỉ
   tiêu.

2. **Người dùng chạy `fetch.py`** để có dữ liệu XBRL thật (mục 10).
   Container không ra được sec.gov.

3. **Chạy MỐC 3** ngay khi có dữ liệu: so `diagnose()` với baseline 9 ở
   cùng ngân sách. **Đây là mốc phải dừng thật.** Nếu baseline 9 ngang bằng
   thì toàn bộ novelty tầng 1 sai — dừng, báo cáo, lùi paper về tầng
   dataset + identifiability. Không chạy tiếp C3 và ablation trước khi biết
   kết quả này, vì chạy tiếp chỉ để tích luỹ số liệu cho một luận điểm đã
   sai.

4. **Trong lúc chờ, làm những việc không chạm mốc dừng:** Phần F dọn dẹp
   (mục 9), quyết định engine OCR, và cập nhật README cho khớp hiện trạng.

5. **Sau khi qua Mốc 3:** C3 (vòng lặp đọc lại) rồi C4 (verdict ba trạng
   thái), rồi D2/D3/D4.

Một lưu ý cho phiên sau: **ba commit `f1d236e`, `1dacb34`, `9c3f7c9` chưa
push.** Nếu người dùng muốn đẩy lên `origin/research` thì họ tự chạy lệnh,
hoặc yêu cầu rõ ràng thì mới đẩy.
