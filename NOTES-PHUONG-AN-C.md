# Sổ thi công — Phương án C và ba lỗi đi kèm

Viết cuốn chiếu trong lúc sửa, để phiên sau nối tiếp được nếu phiên này hết
quota giữa chừng. Khi làm xong hết thì gộp vào `HANDOFF.md` rồi xoá file này.

- **Bắt đầu:** 24/08/2026, từ commit `5810ea2`
- **Nhánh:** `research`

---

## Quyết định của người dùng, 24/08/2026

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

## Ràng buộc phát hiện lúc bắt tay vào làm

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

## Thứ tự thi công

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

### Bước A đã làm gì — `fa5c6d2`

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

### Bước B đã làm gì — `88a77f5`

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

### Bước C1 đã làm gì — `19fe938`

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

### Bước C2 đã làm gì — `ada6f75`

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

## Bước D — việc còn lại, CHƯA làm

`chon_chuan()` vẫn chỉ có hai nguồn `tham_so` và `mac_dinh`. Trên cấu hình mặc
định (không ai truyền `standard`), mọi tài liệu vẫn được xử như **TT99** —
đúng, nhưng vì lùi mặc định chứ không vì nhận diện. Khác biệt so với trước
bước A: việc lùi nay **kêu ra log và ghi vào `meta["standard_nguon"]`** thay vì
im lặng.

Với báo cáo TT200 thật, hậu quả vẫn còn: prompt dùng bảng mã TT99 (mã 280 thay
vì 270) và bộ đẳng thức TT99.

### Hai vướng mắc của bước D, đã khảo sát — ĐỌC TRƯỚC KHI THI CÔNG

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

### Bước A — vì sao đi trước

C cần biết "dòng này có trên biểu mẫu của chuẩn này không", mà câu đó chỉ
trả lời được khi `standard` đã đi tới nơi cần dùng. Hiện `router.py` gọi
`validate_result()` ở ba chỗ (dòng 233, 303, 372) mà không truyền `standard`,
nên mọi tài liệu bị kiểm bằng đẳng thức TT99. Ngoài ra `router.py:327` gán
`meta=da_kiem["meta"]`, tức **đè** lên meta thật và làm đầu ra khai sai chuẩn
đã nhận diện, đồng thời đánh rơi `early_stop` và `prompt_hash`.

### Bước C — hợp đồng của probe

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
