# Bàn giao — hạ tầng nghiên cứu ViFinKIE

Viết để một phiên Claude khác đọc và làm tiếp mà **không cần hỏi lại gì**. Mọi
tham chiếu đều là đường dẫn file hoặc commit hash.

**File này giữ HIỆN TRẠNG.** Bốn loại nội dung khác nằm ở chỗ khác, và đừng
chép lại vào đây:

| Cần gì | Đọc ở đâu |
|---|---|
| Thay đổi nào đổi con số, kèm số đo trước/sau | `CHANGELOG.md` |
| Cam kết nghiên cứu và mọi tu chính kèm ngày | `PREREGISTRATION.md`, mục Sửa đổi |
| Quy tắc gán nhãn và mọi tu chính kèm ngày | `ANNOTATION-GUIDELINE.md`, mục Sửa đổi |
| Cách chạy, cách cài, cấu trúc thư mục | `README.md` |
| Nhật ký commit | `git log --oneline` |

- **Nhánh:** `research` (tách từ `main` tại `4216291`). **`main` KHÔNG BAO GIỜ
  MERGE** — chỉ thị của người dùng 24/08/2026. Hệ quả: CI chỉ chạy trên `main`
  và trên pull request, nên **CI thực tế không bao giờ chạy** — mọi việc kiểm
  phải làm tại chỗ. Muốn CI có ích thì thêm `research` vào phần trigger của
  `.github/workflows/ci.yml`, **không phải merge**.
- **Trạng thái commit:** chạy `git log --oneline -1` và `git status -sb`. Quy
  ước: push sau mỗi commit, nên `research` khớp `origin/research` là bình thường.
- **Kiểm:** `pytest` (510 xanh, ~60 giây) và `ruff check src tests chay_gan_nhan.py`.
- **Bộ chỉ tiêu:** **27 với TT99, 26 với TT200; 9 đẳng thức** — kịch bản E
  (`f1c2738`). MỐC 1 đã đóng, MỐC 3 chưa đóng nhưng điều kiện dừng không kích
  hoạt.
- **Tập gold:** **11 / khoảng 100** tài liệu đã gán nhãn. `VNM_2026Q1_TT99`
  **không có PDF** trong `data/bctc/` nên mọi lượt chạy pipeline chỉ chấm được
  **10**. Chỉ **8/11** có đồng hồ chạy thật.
- **Số thật mới nhất:** 81,5% trường đúng, lỗi câm 10,0% (lượt gold 27/08); sau
  bản vá dấu `a0cd5ab` là **83,8%** và **7,5%**. **Lỗi câm không quy giản được
  chỉ 1,25%** — 21/24 lỗi câm là hai con bug. Mục 20.

---

## Mục lục

Đọc theo nhu cầu, không đọc tuần tự. **Cần gấp:** mục 0 (câu hỏi đang chờ),
mục 16 (bước kế tiếp), mục 15 (lệnh hay dùng).

| | Mục | Dùng khi |
|---|---|---|
| **0** | Câu hỏi đang chờ người chủ trì | luôn đọc trước tiên |
| 1–2 | Đọc gì trước · Bối cảnh | phiên đầu tiên |
| 3–5 | Hash còn được nhắc, bẫy đã gặp, các phần đã đóng | tra khi đụng vào một phần cụ thể |
| 10 | **MỐC 1 — đã đóng**, định luật của H0 | trước khi dựng bảng cho paper |
| 11 | Chỗ đã đi khác `BUILD-SPEC.md`, có chủ đích | trước khi "sửa lại cho đúng đặc tả" |
| **12** | Chưa làm, và **hai quyết định đang treo** | chọn việc |
| 13 | **MỐC 3 — chưa đóng**, trần trên của bộ giải liên tục | đọc bảng kết quả |
| 14–15 | Quy ước bắt buộc · Lệnh hay dùng | mỗi lần bắt tay làm |
| **16** | **Bước kế tiếp** | chọn việc |
| 17 | Đã quyết nhưng chưa thi công | tránh làm lại việc đã quyết |
| 18 | Nơi nộp — ICDAR 2027, hạn 28/02/2027 · related work | lập lịch, viết bài |
| **19** | **Tầng gold**: công cụ, trình tự, nguồn, độ phân giải | việc đang làm |
| **20** | **Chấm pipeline trên tập gold** — số thật đầu tiên | việc đang làm |
| A | Hồ sơ đối chiếu Thông tư (Mốc 1) | tra mã số, đẳng thức, cạm bẫy văn bản |
| B | Phương án C, **bước D chưa làm** | làm tiếp nhận diện chuẩn |

**Không có mục 6–9.** Chúng đã gộp vào mục 5; số mục của phần sau giữ nguyên để
mọi tham chiếu cũ còn trỏ đúng. "Mục 6/7/8/9" trong tài liệu cũ nay đọc là
5.2 / 5.3 / 5.5 / 5.6.

---

## 0. CÂU HỎI ĐANG CHỜ NGƯỜI CHỦ TRÌ

Nơi DUY NHẤT liệt kê những thứ đang chờ quyết định. Nếu người dùng chưa trả lời
thì **hỏi lại đúng những câu dưới đây chứ đừng tự chọn** — mỗi câu đổi kết luận
khoa học chứ không phải chi tiết cài đặt. Người dùng trả lời được bằng một tin
nhắn duy nhất, dạng "Câu 8 chọn ...".

**Đang chờ: Câu 3 (nội dung đã mất), Câu 8, và Câu 14 (MỚI 28/08).** Không câu
nào chặn việc gán nhãn, nhưng **Câu 14 chặn mọi bảng kết quả gộp qua tài liệu**.

**Câu 8 — có tiêm nhiều hơn một lỗi mỗi lượt ở tầng XBRL không?** Phép đo
`do_nghich_dao_mot_loi.py` cho thấy tầng XBRL tiêm đúng một lỗi mỗi lượt, mà lỗi
đơn định vị được lại chính là ca bộ giải liên tục nghịch đảo trọn vẹn — tức
thiết kế đang chọn **ca thuận lợi nhất cho baseline 9**. Đây là thay đổi thiết
kế thí nghiệm nên phải vào mục Sửa đổi của `PREREGISTRATION.md` **TRƯỚC** khi
chạy. Số đo và lập luận ở mục 13.3–13.4. *Chỉ chặn lượt chạy Mốc 3 kế tiếp.*

**Câu 14 — MỚI: quy ước dấu của HNG ngược với phần còn lại của tập gold.**
`HNG_2025H1_TT200` lỗ, và báo cáo đổi tên dòng thành "Lỗ thuần từ hoạt động
kinh doanh" rồi in số DƯƠNG — nhãn mang dấu, con số chỉ mang độ lớn. Gold chép
đúng như in theo guideline mục 3.3, nên `ln_thuan_hdkd` của HNG dương trong khi
cùng chỉ tiêu ở tài liệu khác âm khi lỗ. **Không khoá nào trong file gold khai
ra chuyện đó**, và ràng buộc kế toán chứng minh được là không phân xử được —
lật dấu trọn một hệ con nhất quán vẫn cân. Chi tiết và hai đường ra ở mục
20.4b. *Chặn mọi phân tích gộp qua tài liệu.*

**Câu 3 — NỘI DUNG CÂU ĐÃ MẤT.** Câu này được liệt kê là đang chờ nhưng nguyên
văn không còn ở bất kỳ file nào trong repo — chỉ còn cái tên; nó nằm trong phần
"giữ lại nguyên văn từng câu" đã bị xoá trong một lần nén tài liệu. Vì không thể
tự đoán lại một câu hỏi đổi kết luận khoa học, việc đúng là **hỏi lại người chủ
trì Câu 3 là gì**, hoặc coi như nó không tồn tại và đánh số mới cho câu kế tiếp.
Nó được đánh dấu "hoãn được" nên chưa chặn việc gì.

### Câu đã trả lời — tra ràng buộc kèm theo ở cột cuối

Nguyên văn các câu đã trả lời KHÔNG còn được giữ; ràng buộc thì còn, và nằm ở
mục Sửa đổi của `PREREGISTRATION.md` hoặc `ANNOTATION-GUIDELINE.md`.

| Câu | Ngày | Quyết định | Ràng buộc còn hiệu lực |
|---|---|---|---|
| 1 | 25/08 | Báo cáo **ba** con số định vị | Con số "trên lượt có ra tay" **không bao giờ đứng một mình** — mục 13.2 |
| 2 | 25/08 | Đo ma trận nhầm chữ số trước | Bộ tiêm và bộ sinh dùng chung nguồn, **khác độ sâu** — mục 13.1 |
| 4 | 25/08 | Cùng nguồn khác độ sâu | như trên |
| 5 | 25/08 | Nới trần ứng viên 6/12 → **10/20** | `CHANGELOG.md` 25/08 |
| 6 | 25/08 | Ghi làm giới hạn | — |
| 7 | 25/08 | Tầng XBRL **hoà thì hoãn** phán quyết H3 | Thắng trong phạm vi kiểm được ⇒ không kích hoạt điều kiện dừng — mục 13 |
| 9 | 26/08 | Giữ **hệ số 0,6** cho đồng hồ trần người | **ĐỪNG MỞ LẠI** — giá trị của nó nằm ở chỗ được chốt lúc chưa tài liệu nào có số đo, và cửa sổ đó đã đóng |
| 10 | 26/08 | Nhóm Stress thứ ba = **độ phân giải**, biến liên tục | Không được dùng để loại tài liệu khỏi phân tích chính — mục 19.5 |
| 11 | 26/08 | Bỏ ký hiệu mẫu khỏi bảng dấu hiệu nhận diện chuẩn | Hậu tố `a`/`b` là **kỳ báo cáo**; SBT và HNG giữ nhãn TT200 |
| 12 | 28/08 | Tài liệu **đã chạy pipeline bị loại vĩnh viễn** khỏi tập gán nhãn đôi | Hiện **0/11** đủ điều kiện; lượt gán nhãn đôi chờ tập gold vượt mốc 11 — mục 19.3 |
| 13 | 28/08 | **Nhãn gold đúng, guideline sai** — mã 51 và 52 giữ nguyên dấu như in | `chuan_hoa_dau()` không bao giờ đụng mã 52; chỗ vênh còn lại ở mã 51 — xem docstring hàm đó |
| — | 26/08 | **Không có người gán nhãn thứ hai**; người chủ trì tự gán lại sau ≥ 2 tuần | Bài phải nói rõ đây là bản thay thế kèm giới hạn |
| — | 26/08 | Quy mô tập gold theo mốc **10 → 60 → 100** | Đừng gộp ba mốc thành "gán nhãn cho tới khi đủ 100" |
| — | 25/08 | Chỉ số chính của H3 trên tầng XBRL tính ở **mức LƯỢT** | Tầng gold giữ mức trường |

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
5. [ANNOTATION-GUIDELINE.md](ANNOTATION-GUIDELINE.md) — cần ngay, vì việc
   gán nhãn đã bắt đầu (mục 19).

**Một tài liệu nằm NGOÀI repo, dễ quên vì không file nào trỏ tới:** "Sổ tay
phương pháp ViFinKIE" — artifact riêng của người dùng ở
`https://claude.ai/code/artifact/8d3cef49-a6b0-40d6-8533-7d42f340d347`. Nó
giải thích phương pháp nghiên cứu của từng giả thuyết H0–H3, thuật toán, cơ
sở thống kê, thuật ngữ tiếng Anh kèm nghĩa, cầu nối sang lý thuyết mã, và
bảng kết quả Mốc 3 kèm trần định vị. Bản HTML nguồn nằm trong thư mục
scratchpad của phiên đã tạo nó, tức **không còn** — phiên sau muốn sửa thì
đọc lại nội dung bằng công cụ Artifact với URL trên, rồi xuất bản đè lên
đúng URL đó. Sổ tay hiện CHƯA có phần công cụ gán nhãn và giao thức trần
người mới ở mục 19.

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

## 3. Nhật ký thi công — tra bằng `git log`, không chép lại ở đây

Bản trước liệt kê ~45 commit của ba ngày 21–24/08/2026 thành ba bảng. Đó là
thứ `git log --oneline` in ra chính xác hơn và không bao giờ cũ, nên phần
chép tay đã bỏ. Giữ lại đúng những hash mà các mục khác trỏ tới:

| Hash | Vì sao còn được nhắc |
|---|---|
| `023321c` | Sửa `FORM_MARKERS` — hậu tố `a`/`b` là KỲ BÁO CÁO, không phải Thông tư |
| `6744bee` | Thay đẳng thức giả thuyết bằng đẳng thức đã đối chiếu Công báo |
| `4064519` | B4 — bộ chỉ tiêu lên 21, hai chuẩn hết đẳng cấu |
| `df96ff2` | MỐC 1 đóng |
| `ada6f75` | Phương án C — probe dò dòng, điền `0` cho dòng vắng mặt |
| `e6c286c` | Donor thôi lấy từ chính công ty đang xét (rò rỉ đáp án) |
| `f1c2738` | Bộ chỉ tiêu chuyển sang kịch bản E (27/26 chỉ tiêu, 9 đẳng thức) |
| `90b271a` | Ma trận nhầm chữ số đo từ EasyOCR, dùng cho cả bộ tiêm lẫn bộ sinh |
| `f80a53d` | Cột kỳ so sánh chọn theo độ phủ chỉ tiêu thay vì theo ngày |

Chi tiết phương án C ở **Phụ lục B**; đối chiếu Thông tư ở **Phụ lục A**.

---

## 4. Cái bẫy đã gặp — phần còn ràng buộc việc đang làm

**A1 — quan hệ có điều kiện.** Ba trong sáu quan hệ `FIELD_RELATIONS` ngầm
giả định doanh nghiệp có lãi và VCSH dương, mâu thuẫn với `FIELD_RULES` vốn
cho phép âm. Mâu thuẫn không nằm yên: `FIELD_RELATIONS` nằm trong cổng
`is_acceptable()`, nên gặp báo cáo lỗ thì router coi kết quả **đúng** là
chưa đạt, gọi VLM, và `has_warnings` mở đường cho VLM ghi đè lên số vốn đã
đúng. *Đánh đổi đã biết:* field điều kiện cũng do model trích ra, nên nó bị
đọc sai thành âm sẽ làm luật tự tắt —
`test_field_dieu_kien_bi_doc_sai_thi_luat_tu_tat` chốt hành vi đó.

**A3 — không bao giờ đoán chuẩn.** `detect_standard()` trả `None` khi không
đủ dấu hiệu hoặc khi trang nhắc cả hai chuẩn, vì nhận diện sai chuẩn là một
chế độ lỗi riêng cần đo được. Dấu hiệu là **tên báo cáo** và **số hiệu thông
tư**, không phải ký hiệu mẫu biểu — xem tu chính 26/08 ở guideline.

**A4 — mỏ neo tuyệt đối, và nó là chỗ yếu nhất của cả hệ.** Hệ ràng buộc
thuần nhất nên `Aδ = (c−1)Ax* = 0`: **sai đơn vị toàn cục LUÔN vô hình với
mọi đẳng thức**, không phải "thường vô hình". `TOTAL_ASSETS_BOUNDS` là check
duy nhất trong `validate_result` không bất biến với phép nhân vô hướng.
`don_vi_tinh` cố ý **không** nằm trong `FIELD_MAP` vì `validate_result` chạy
`coerce_number` trên mọi khoá của nó. Đo trên tập gold 26–27/08 cho thấy
đúng chỗ này đang hỏng — xem mục 20.

**B1 — vòng lặp luận chứng.** Pipeline dùng chính đẳng thức kế toán làm cổng
quyết định fallback, nên đo AUROC của vi phạm ràng buộc trên đầu ra đó là
đánh giá một tín hiệu trên tập đã bị chính nó lọc. Lượt chạy ở chế độ đo
đánh dấu bằng khoá `constraint_gate: false` trong `metrics.jsonl`.

**B2 — ba quyết định trong cách tính phiếu**, cả ba có thể sai theo hướng
lạc quan: `None` cũng là ứng viên bỏ phiếu; mẫu số là `n_samples` chứ không
phải số mẫu parse được; hoà phiếu thì ưu tiên non-null rồi tới giá trị xuất
hiện sớm nhất. `n_samples > 1` với `temperature = 0` **ném lỗi**.

**B3 — provenance đứt là mất đóng góp cốt lõi.** Lọc IoU đi kèm chứ không
phải việc rời: YOLO trả box chồng nhau (quan sát ở trang 31 và 35 báo cáo
VNM), và kể từ khi có provenance thì đó là **sai dữ liệu** chứ không còn là
lãng phí. `bbox` trả về đã cộng padding và đã clamp, có test cắt lại rồi so
từng byte.

**B4 — ba lỗi im lặng khi mở bộ chỉ tiêu.** *Một,* dựng ma trận TT200 trên
toàn bộ `FIELD_MAP` sẽ kéo theo `tai_san_sinh_hoc_ngan_han` — chỉ tiêu TT200
không có — và bịa ra một cột toàn 0, làm sai chiều không gian null. Đó là lý
do có `fields_for(standard)`; **đừng quay lại `list(FIELD_MAP)`**. *Hai,*
`report()` từng chỉ nhắc "cột toàn 0" trong ghi chú từng dòng, nên khi không
còn chỉ tiêu vô hình thì báo cáo trông y hệt báo cáo quên in phần đó. *Ba,*
test `A @ x_ref ≈ 0` trên bộ số thật **không** bắt được việc bỏ sót hạng tử,
vì giá trị của nó trên báo cáo VNM đúng bằng 0 — cái bắt được là test cột
toàn 0. Bài học: test trên một bộ số thật không thay được test trên cấu trúc
ma trận.

**B6 — bootstrap theo CỤM TÀI LIỆU, không theo trường.** Có test chứng minh
việc phân cụm nới khoảng tin cậy hơn gấp đôi trên dữ liệu phân cụm.
`item_bootstrap_ci` (cách SAI) giữ lại có chủ đích để paper nêu định lượng
khoảng tin cậy hẹp giả tạo bao nhiêu. **Không dùng DeLong** — lý do ở
`PREREGISTRATION.md` mục 1. McNemar dùng kiểm định nhị thức **chính xác**
nên phần đó không cần scipy.

**C1 — năm nguồn ứng viên**, `cost = −log(xác suất tiên nghiệm)` để cộng
cost tương đương nhân xác suất. **Bảng `XAC_SUAT_TIEN_NGHIEM` vẫn CHƯA hiệu
chỉnh trên dữ liệu thật** — xem mục 12.

---

## 5. Các phần đã đóng — chỉ giữ ràng buộc còn hiệu lực

Năm mục C2, B5, `max_changes`, Phần F và engine OCR đều đã xong. Bản trước
dành ~230 dòng kể lại quá trình; dưới đây chỉ còn những gì **ràng buộc việc
sẽ làm**. Muốn quá trình thì tra hash ở mục 3.

### 5.1 C2 — hai baseline không được thua vì lý do cài đặt

**Baseline 8 dùng quy hoạch tuyến tính, KHÔNG dùng IRLS.** Trên hệ đối xứng
như `a + b = c`, cực tiểu L1 suy biến: nghiệm rải đều `δ = 5/3` ở cả ba toạ
độ có cùng chuẩn L1 với nghiệm dồn một chỗ, và IRLS xuất phát từ trọng số
đều thì kẹt ở đó vĩnh viễn. Nay tách `delta = u − v` với `u, v ≥ 0` rồi tối
thiểu hoá `Σ(u + v)` bằng `scipy.optimize.linprog` (HiGHS) — nghiệm LP là
nghiệm đỉnh nên số toạ độ khác 0 không vượt `rank(A)`. Baseline mạnh hơn thì
kết luận về phương pháp đề xuất đáng tin hơn.

**Baseline 9 phải VÉT HẾT một cardinality rồi mới phân xử**, không được trả
tổ hợp đầu tiên theo thứ tự chỉ số — nếu không thì đối chứng trung tâm của
cả nghiên cứu thắng thua theo thứ tự khai báo field. Phân xử bằng **tổng
khoảng cách tới donor**; trường không có donor thì lấy giá trị hiện tại làm
mốc.

### 5.2 B5 — tầng XBRL: vì sao có, và ba chỗ dễ làm hỏng

**Phân vai: XBRL lo POWER, gold Việt Nam lo VALIDITY.** Tập gold cho khoảng
1500 trường nhưng H2/H3 đo trên **số lỗi**, mà tỷ lệ lỗi 5–15% chỉ cho
75–225 quan sát — 75 quan sát cho khoảng tin cậy rộng chừng ±0,11.

**(a) `facts.py` chỉ lấy fact của CÙNG MỘT hồ sơ.** companyfacts gộp mọi lần
công bố, nên trộn hai hồ sơ vào một bảng sẽ phá vỡ đẳng thức kế toán một
cách âm thầm — mất đúng thứ duy nhất làm nên giá trị của tầng này.
`test_chi_lay_fact_cua_dung_mot_ho_so` chốt chuyện này.

**(b) Bộ tiêm và bộ sinh ứng viên dùng CHUNG ma trận nhầm chữ số, nhưng
KHÁC ĐỘ SÂU.** *(Sửa 25/08/2026 — bản trước ghi ngược lại, và câu "đừng
thống nhất hai bảng này" ở đây đã hết hiệu lực.)* Cảnh báo cũ đúng khi cả
hai bảng đều là phỏng đoán, nhưng cái giá của nó không ai tính: hai bảng
lệch nhau làm độ phủ `digit_substitution` chỉ còn 0,092 — tức chỉ số đo ĐỘ
TRÙNG CỦA HAI BẢNG PHỎNG ĐOÁN, không đo phương pháp. Nay cả hai đọc từ ma
trận **đã đo** ở `src/nham_chu_so.py`, nhưng bộ tiêm lấy **trọn phân phối**
còn bộ sinh chỉ lấy **6 cặp đầu**. Khoảng hở đó giữ nguyên tinh thần cảnh
báo cũ và là thứ giữ cho cơ chế ABSTAIN còn kiểm chứng được. Độ phủ sau khi
sửa: 0,615.

**(c) `render.py` ném lỗi khi font thiếu glyph.** Font đi kèm Pillow không
có glyph tiếng Việt có dấu: "Đơn vị tính" render ra "□n v□ t□nh" mà ảnh vẫn
trông bình thường. Chữ cố định mặc định **tiếng Anh**, ô trống dùng gạch nối
ASCII, và `render()` kiểm mọi ký tự rồi ném `ValueError`. `RenderedTable`
mang khoá `texts` — chuỗi **đúng như đã vẽ**, vì bộ đo OCR phải so với cái
đã VẼ chứ không phải với giá trị số (`1234567.0` vẽ thành `"1,234,567"`).

> **Hai bảng số tách biệt hẳn nhau, trộn là hiểu sai cả mục 7 lẫn mục 12:**
>
> | | Bộ chỉ tiêu Việt Nam | Bảng tầng XBRL |
> |---|---|---|
> | Khai ở | `src/fields_config.py` | `src/eval/xbrl_tier/` |
> | Nguồn | Thông tư 200 và 99 | Linkbase hồ sơ SEC (Mỹ) |
> | Quy mô | 27/26 chỉ tiêu, 9 đẳng thức | trung vị 158 chỉ tiêu |
> | Dùng để | Trích xuất báo cáo Việt Nam thật | Sinh lỗi có kiểm soát cho H2/H3 |
>
> `diagnose()` không biết gì về bộ chỉ tiêu nào — nó nhận `A` và
> `field_order` từ nơi gọi, nên chạy trên **cả hai**.

### 5.3 Trần `max_changes = 2` — hạn chế của phương pháp, không phải cài đặt

Chi phí nằm trọn ở việc **chứng minh KHÔNG có nghiệm**, mà đó lại là ca
thường gặp vì tập ứng viên đóng cố ý không chứa mọi cách sửa. Đo trên bài
toán 8 chỉ tiêu / 87 ứng viên: không đặt trần thì hết 30 giây; đặt trần 2
thì 16 mili giây. Đo lại 24/08 trên chính ma trận TT200/TT99 (20–21 chỉ
tiêu, 100–105 ứng viên): trần 2 mất 33–56 ms, trần 3 mất 958–1128 ms, không
đặt trần thì vẫn hết giờ 30 giây. **Mỗi nấc đắt lên khoảng 20 lần.**

Áp cho `diagnose()` **và** baseline 9 vì H3 so ở cùng ngân sách. Baseline 8
**không** áp trần, có chủ đích: delta của nó chạy tự do trong `ℝⁿ` và nghiệm
đỉnh đã tự giới hạn số toạ độ khác 0.

**Tài liệu có ba trường cùng sai sẽ không được sửa.** Đã ghi vào mục Sửa đổi
của `PREREGISTRATION.md`. **Bảng kết quả phải báo cáo tỷ lệ tài liệu rơi vào
ca đó.**

Ở `max_changes = 2` chi phí đi theo `C(n,2)`, nên tăng từ 21 lên 40 chỉ tiêu
chỉ đắt lên chừng 3,7 lần — vẫn dưới một phần tư giây. **Ràng buộc thật khi
mở rộng bộ chỉ tiêu là chi phí gán nhãn tay, không phải chi phí tính toán.**

### 5.4 Tách ABSTAIN theo lý do — đừng bao giờ gộp lại

| Mã | Nghĩa | Chứng minh được luận điểm chống bịa? |
|---|---|---|
| `vo_nghiem` | Đã vét cạn MỌI tổ hợp và không có nghiệm | **CÓ — ca duy nhất** |
| `vuot_tran_thay_doi` | Hết tổ hợp trong trần, chưa duyệt tổ hợp lớn hơn | không |
| `het_gio` | Hết ngân sách thời gian | không |
| `thieu_gia_tri` | Không dựng được vector nên không kiểm được ràng buộc | không |
| `bo_giai_that_bai` | Bộ giải LP của baseline 8 không trả nghiệm | không |

Luận điểm chống bịa phát biểu là *không cách đọc nào của tài liệu này làm
bảng cân đối được*. Gộp `vuot_tran_thay_doi` vào `vo_nghiem` là tính công
cho phương pháp ở những ca nó không chứng minh được gì.

**Đo được ở cả hai lượt Mốc 3: `vo_nghiem` = 0 trên 520 lượt.** Xem mục 13.4.

### 5.5 Phần F — hai thứ còn ràng buộc

**CI thực tế KHÔNG BAO GIỜ CHẠY.** Workflow chỉ trigger trên `main` và trên
pull request, mà `research` không bao giờ merge. Một lỗi từng nằm im vì
chuyện này: bước cài liệt kê tay `pytest ruff numpy pillow openai
python-dotenv`, thiếu `scipy`, trong khi `repair/diagnose.py` import
`scipy.optimize.linprog` ở mức module — pytest hỏng ở bước **collect** nên
cả 31 test của `test_diagnose.py` biến mất chứ không phải đỏ. Đã sửa danh
sách, nhưng **mọi việc kiểm vẫn phải làm tại chỗ**. Muốn CI có ích thì thêm
`research` vào phần trigger của `.github/workflows/ci.yml`, KHÔNG phải merge.

**`meta["early_stop"]` là khoá tường minh, và nó tồn tại vì phép ĐO.** Nhánh
`PATIENCE_PAGES` dừng khi mới đủ field BẮT BUỘC, tức cố ý bỏ qua phần đuôi
tài liệu. Một chỉ tiêu nằm ở phần đuôi sẽ có tỷ lệ "không đọc được" cao —
nhưng đó là tạo tác của điều kiện dừng, và **không nhìn ra được từ bảng kết
quả** vì trường bị bỏ qua và trường đọc hỏng đều là một ô null.
`DISABLE_EARLY_STOP=true` tắt hẳn, cùng vai với `DISABLE_CONSTRAINT_GATE`.

### 5.6 Engine OCR — GIỮ EasyOCR, và một kết quả dùng được cho bài

Đo trên 45 ô số render sẵn (ground truth mức ô chính xác tuyệt đối, không
tốn một phút gán nhãn — `render.py` cho cả ảnh, bbox và chuỗi đã vẽ):

| Ảnh | Levenshtein | Đúng con số | Không ra số |
|---|---:|---:|---:|
| sạch | 0,999 | 0,978 | 0,022 |
| mờ | 1,000 | 1,000 | 0,000 |
| nhiễu | 1,000 | 1,000 | 0,000 |
| **độ phân giải thấp** | **0,934** | **0,467** | **0,000** |

**Kết luận 1 — giữ EasyOCR.** Con số 0,646 của Ajayi et al. đo trên bảng
KHOA HỌC; trên ô số thì 0,999. Đây là câu trả lời có số liệu cho reviewer.

**Kết luận 2, quan trọng hơn.** Ở độ phân giải thấp, chỉ số ký tự vẫn báo
0,934 trong khi **chưa tới một nửa** số đọc ra là đúng, và tỷ lệ "không ra
số" bằng **0** — mọi ô sai đều parse ra một con số hợp lệ. Đó chính là lỗi
câm, đo được, trên dữ liệu có ground truth hoàn hảo. **Không được báo cáo
Levenshtein accuracy một mình.**

*(Mục "việc còn chờ người quyết" ở đây đã ĐÓNG: cặp `9→0` áp đảo mà bảng bốn
cặp cũ không có, nay đã đo thành ma trận đầy đủ và áp vào cả hai phía —
`90b271a`, xem 5.2(b).)*

### 5.7 Bẫy `sys.path` — đã cắn hai lần, sẽ cắn lần ba

Chạy `python src/eval/<file>.py` đặt `src/eval/` lên **đầu** `sys.path`, và
`eval/metrics.py` ở đó che mất `src/metrics.py` của pipeline. Lỗi nổ ra tận
trong `ocr_baseline` với `ImportError: cannot import name 'timer' from
'metrics'`, trỏ vào một file chẳng liên quan. Cùng họ với vụ `src/types.py`
che module `types` chuẩn (mục 11). **Mọi script trong `src/eval/` phải tự gỡ
thư mục của chính nó khỏi `sys.path` trong khối `__main__`** — `moc3.py`,
`ocr_compare.py`, `chay_tap_gold.py` đều đã làm; `fetch.py` đã kiểm, không
dính.

---

### 5.8 Đọc lại tờ giấy — neo, chữ thập, lan ký hiệu mẫu (30/08/2026)

Nguồn ứng viên `o_lan_can` nay chạy trên đường tài liệu thật, không chỉ ở tầng
XBRL. Ba ràng buộc đi kèm, cả ba đều là chỗ đã hoặc suýt trả giá.

**Trần chỉ có nghĩa khi thứ tự có nghĩa.** `MAX_MOI_NGUON = 10` cắt theo cost;
cost bằng nhau thì phép cắt là bốc thăm. Vì thế ô lân cận xếp theo hình CHỮ
THẬP: hạng 0 đọc lại chính ô đó bằng EasyOCR, hạng 1 cùng cột lệch dòng
(`row_shift`), hạng 2 cùng dòng lệch cột (`col_shift`); ô nằm chéo bị loại vì
không ứng với chế độ lỗi nào. Không lọc hình học trước — không có số đo nào về
việc lệch dòng đi xa bao nhiêu, nên để trần cắt phần đuôi.

**`Provenance.bbox` KHÔNG dùng làm tâm chữ thập được.** Nó là bbox của cả VÙNG
BẢNG, nên mọi ô đều chồng lên nó theo hai trục và tất cả rơi vào hạng 0 với
cost bằng nhau — xếp hạng nằm im mà không ai thấy. Tâm thật do
[src/repair/neo.py](src/repair/neo.py) dò: khớp giá trị trước, dòng của mã số
sau. Tầng hai không phải dự phòng cho vui — VLM đọc sai thì không ô nào mang
con số sai ấy, tức tầng một trượt đúng vào những lượt cần sửa. Trượt cả hai
thì trả `None`, và certificate khai `neo` THEO TỪNG CHỈ TIÊU: `o_lan_can: true`
mà toàn `khong_neo` nghĩa là nguồn bật nhưng vô dụng.

**Ô lân cận lấy trong VÙNG BẢNG, không phải trong trang.** Một trang có thể
mang nhiều bảng, và một con số hợp lệ của bảng khác thì vẫn hợp lệ — không
đẳng thức nào bắt được, đúng kiểu lỗi đã thấy ở `SBT_2025Q2_TT200`. Kết quả OCR
vì thế chia theo vùng: `{"region_index", "text", "o", "o_so"}`.

**Lan ký hiệu mẫu** ([src/ky_hieu_mau.py](src/ky_hieu_mau.py)): đọc `B01a-DN/HN`
phía trên bảng để biết bộ báo cáo là hợp nhất hay riêng, lan sang bảng không
đọc được (trang xoay ngang thì ký hiệu nằm ngoài vùng cắt). **Chỉ lan hậu tố** —
phần `B01/B02/B03` nói bảng nào, lan nó đi là gán nhãn bảng cân đối cho trang
kết quả kinh doanh. Mâu thuẫn giữa các vùng được GHI LẠI chứ không đè lên kết
luận đã chốt: nó nghĩa là hoặc file đóng gói cả hai bộ, hoặc khâu cắt/đọc hỏng.
Cơ chế này **không sửa được lỗi câm nào hiện có**; giá trị của nó nằm ở bước D
(nhận diện chuẩn) và ở độ bền khi gặp hồ sơ lạ. Chạy cùng probe dò dòng và tắt
cùng nó, vì cả hai sống nhờ đúng một lượt OCR. Kết quả ở `meta["ky_hieu_mau"]`.

*Giới hạn của tiền đề "mỗi hồ sơ thuần một bộ":* mới kiểm trên 10 tài liệu từ
MỘT nguồn phát hành. Hồ sơ tải từ website công ty hoặc cổng HOSE đôi khi đóng
gói cả hai bộ trong một file.

---

## 10. MỐC 1 — ĐÃ ĐÓNG, và định luật rút ra từ nó

Đối chiếu ma trận ràng buộc với năm file Công báo (`data/legal/`, đã gitignore).
**Hồ sơ đối chiếu đầy đủ kèm nguyên văn trích dẫn ở Phụ lục A**; bảng số của
từng kịch bản ở `CHANGELOG.md` 23/08 và 25/08/2026. Mục này giữ ba thứ còn chi
phối việc sẽ làm.

**Ba đẳng thức repo đang dùng từ đầu: đều ĐÚNG.** `100 + 200 = 270/280` khớp
nguyên văn; `300 + 400 = 270/280` đúng nhưng là đẳng thức **suy ra** (văn bản
viết `Mã 440 = Mã 300 + Mã 400` rồi viết **riêng** `Tổng cộng Tài sản = Tổng
cộng Nguồn vốn`); `11 + 20 = 10` khớp `Mã 20 = Mã 10 − Mã 11`.

### Định luật rút ra — thứ quyết định hướng đi của H0

> Một chỉ tiêu định vị được **khi và chỉ khi** tập đẳng thức chứa nó khác tập
> đẳng thức của **mọi** chỉ tiêu khác.

Trong một đẳng thức phân rã đơn lẻ `a + b = tổng` thì **cả ba** nằm ngoài tầm —
hai thành phần có cột bằng nhau, còn cột của tổng là `[−1]` tỷ lệ với cột `[1]`.
Phân rã một chỉ tiêu làm **chính nó** định vị được nhưng sinh ra một tầng lá
mới; đó là cái cối xay, và mỗi lá mới tốn chi phí gán nhãn nhân với cả tập gold.

`minimal_localizing_set()` trả `None` ở **mọi** kịch bản, và `hang_ton_kho`
không định vị được ở kịch bản nào — mà đó đúng là chỉ tiêu đã có lỗi đọc thật
trên báo cáo VNM. **Ràng buộc kế toán chứng minh được là không bao giờ bắt được
lỗi đó.** Kết luận cho bài: ràng buộc đơn thuần không đủ, trọng số dồn sang mỏ
neo đơn vị tính (proposal 6.3) và bước đọc lại (6.2).

### Cái bẫy đọc bảng kịch bản — sẽ quay lại khi dựng bảng cho paper

Top-3 của kịch bản D (0,90) thấp hơn C (0,94) nhìn như bước lùi, nhưng đo trên
**đúng 16 chỉ tiêu của C** thì D cho **0,975** so với 0,938 — không chỉ tiêu nào
xấu đi. Trung bình tụt vì D thêm bốn chỉ tiêu vốn dĩ khó. Đây là **hiệu ứng cấu
thành**, và **bảng kết quả phải in Top-k kèm phân rã theo lớp lẫn**, nếu không
người đọc sẽ rút ra kết luận ngược.

Cùng loại bẫy, một tầng khác: xếp hạng kịch bản theo "số chỉ tiêu định vị được
trên mỗi chỉ tiêu thêm vào" là **sai thước** — nó gộp *cột toàn 0* (vô hình với
cả H1 lẫn H2) với *lẫn lớp* (H1 vẫn bắt được), và nhị phân hoá "định vị được"
trong khi H2 báo cáo bằng Top-1/Top-3.

### Hai kết luận đã bị bác bỏ bằng số đo — đừng khôi phục

1. **Liên kết chéo KHÔNG hiệu quả gấp đôi phân rã.** Bản trước dùng đẳng thức
   **giả thuyết**; hai trong số đó — nối Lợi nhuận chưa phân phối (B01) với Lợi
   nhuận sau thuế (B02), và phân rã Vốn chủ sở hữu — **không có trong văn bản**.
   Với đẳng thức thật: liên kết chéo 0,33, phân rã 0,50 — ngược hẳn. Chốt bằng
   `test_lien_ket_cheo_KHONG_hieu_qua_hon_phan_ra`. **Bài học đã ghi vào docstring
   `constraints_scenarios.py`: đừng để đẳng thức giả thuyết chạy vào bảng kết
   quả, kể cả khi chúng hợp lý về kế toán.**
2. **Không gán nhãn cột kỳ so sánh** (trả lời proposal 6.1(d)). Thêm cột kỳ
   trước **nhân đôi** số chỉ tiêu mà trần Top-1 và Top-3 **không đổi một điểm
   nào**: hai cột thoả cùng một hệ đẳng thức độc lập nên ma trận thành khối chéo
   `[[A,0],[0,A]]`, không residual nào nối chúng. Mỏ neo chéo ở proposal 6.3 vẫn
   giữ, nhưng nó là kiểm biên độ nên chỉ cần **một** con số tổng tài sản kỳ
   trước, không cần cả cột.

**Bộ chỉ tiêu chốt ở kịch bản D ngày 23/08, rồi chuyển sang E ngày 25/08** —
xem mục 17.1. **Đừng đổi nữa.**

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

## 12. Chưa làm, và hai quyết định đang treo

Theo thứ tự phụ thuộc trong `BUILD-SPEC.md` phần E.

| Mục | Trạng thái | Chặn bởi |
|---|---|---|
| A1–A4, B1–B6, C1, C2, Phần F, README, guideline | **XONG** | — |
| **MỐC 1** | **ĐÓNG** — `df96ff2` | — |
| Bỏ qua đẳng thức khi thiếu thành phần | **XONG** — phương án C, `ada6f75` | — |
| Nhận diện chuẩn thật (nguồn `nhan_dien`) | **Chưa** — bước D, Phụ lục B | Quyết định của người |
| **C3** vòng lặp đọc lại | Chưa | **MỐC 3** — mục 13 |
| **C4** verdict ba trạng thái | Chưa | C3 |
| **D2** runner / **D3** bảng / **D4** hình | Chưa | C4, rồi D2 |

### 12.1 Quy tắc `None` ở pipeline — HOÃN tường minh 26/08/2026

`validate_result()` bỏ qua **cả đẳng thức** nếu bất kỳ thành phần nào là `None`
([src/validation.py:168](src/validation.py#L168)). Với đẳng thức phân rã tài
sản ngắn hạn (5 thành phần ở TT200, 6 ở TT99) thì chỉ cần **một** dòng không
đọc được là đẳng thức giá trị nhất im lặng không chạy.

Phía **gán nhãn tay** đã xử lý: guideline mục 3.4 quy định dòng vắng mặt ghi
`0`, vì TT99 mục 1.2.3 bảo đảm chỉ tiêu không có số liệu được miễn trình bày —
vắng mặt là *bằng không*, không phải *chưa biết*. Phía **pipeline** thì chưa:
VLM và OCR đều trả `None`, và ở đó `None` thật sự nhập nhằng.

Người chủ trì đã **hoãn** — nhưng nó vẫn chặn việc chạy pipeline diện rộng trên
tài liệu thật. Đánh đổi có hai chiều thật:

- Coi `None` là 0 → đẳng thức chạy được trên phần lớn tài liệu, nhưng một
  thành phần đọc hỏng sẽ sinh cảnh báo lệch đúng bằng giá trị của nó. Lệch đó
  là **cảnh báo đúng hướng** nhưng **quy trách nhiệm sai chỗ**, và C1/C2 sẽ đi
  tìm ứng viên cho nhầm chỉ tiêu.
- Giữ nguyên → an toàn nhưng đẳng thức mới gần như không bao giờ chạy, tức phần
  lớn cái mà Mốc 1 mua được sẽ không tới được pipeline.

Gợi ý nếu cần một hướng: phân biệt hai ca bằng chính **mã số dòng** — probe của
phương án C đã làm được đúng việc đó ở nhánh OCR. Dù chọn hướng nào cũng phải
ghi trạng thái **tường minh** vào kết quả, đừng để suy ra từ sự vắng mặt của
khoá khác.

### 12.2 Nhánh OCR — đã có bộ đếm kiên nhẫn, còn phải đo cái giá

**Phát hiện 28/08/2026, phải chốt trước lượt chạy lại kế tiếp.** File `.env`
của máy này đặt `USE_OCR_FIRST=true`, trong khi docstring `router.py` nói nhánh
này **tắt mặc định**. Hệ quả đã đo được:

| | |
|---|---|
| OCR chiếm | **77%** tổng thời gian chạy (5,28 / 6,84 giờ) |
| Mỗi trang OCR | ~27,6 giây |
| Trang được quét | **100%** số trang của mọi tài liệu |
| Lần `run_ocr_first` dừng sớm | **0/9** — "OCR chưa đạt" 9 lần |

Lý do nhánh OCR không bao giờ dừng sớm: nó chỉ dừng khi `is_acceptable()` đúng,
mà nhánh regex đọc hỏng chữ tiếng Việt có dấu nên điều đó gần như không xảy ra.
Nhánh VLM thì ngược lại — `PATIENCE_PAGES = 3` kích hoạt ở **9/10** tài liệu,
dừng ở trang 6–18 của tài liệu 25–62 trang, chỉ tốn 7–18 lượt gọi.

**ĐÃ THI CÔNG 28/08/2026 — `PATIENCE_PAGES_OCR = 10`.** `run_ocr_first()` nay
dừng sau mười trang liên tiếp không trích thêm được chỉ tiêu nào, và nhánh VLM
đọc tiếp từ đó. Cố ý **không** gác điều kiện dừng sau `has_required_fields()`
như nhánh VLM làm: ở nhánh regex điều kiện ấy gần như không bao giờ đúng, nên
gác vào là dựng lại đúng vòng lặp không có trần mà bộ đếm sinh ra để cắt.

**Vì sao 10 chứ không phải 3 như nhánh VLM.** Không có cái gác trên nghĩa là bộ
đếm chạy ngay từ trang 1, mà trang đầu báo cáo niêm yết là bìa, trang ký, mục
lục, phần giới thiệu. Để 3 thì vòng lặp dừng ở trang 3 TRƯỚC khi tới bảng nào,
và nhánh OCR thành vô dụng một cách im lặng. Bảng B01 sớm nhất của tập gold ở
trang 4. **Ngưỡng này là điều kiện để nhánh OCR còn chạy, không phải tham số
tinh chỉnh tốc độ** — hạ nó xuống là tắt nhánh OCR mà không ai thấy.

**CÒN LẠI, chưa làm — đo cái giá.** Probe dò dòng (`do_dau_vet_dong`) chỉ đọc
`cached_pages`, nên nhánh OCR dừng sớm hơn thì probe thấy ít trang hơn và kết
luận "dòng vắng mặt trên biểu mẫu" có thể đổi. Hai khoá mới trong
`metrics.jsonl` để so hai lượt chạy: `ocr_dung_som` (dừng vì lý do gì, ở trang
nào) và `probe_so_trang`. **Chạy lại 2 tài liệu là đủ; phải đo, không đoán.**

Vẫn còn phải quyết `USE_OCR_FIRST` đặt gì cho các lượt chạy sau — bộ đếm chỉ
chặn được chi phí, nó không trả lời câu hỏi nhánh regex có đáng chạy không.

**Và một hệ quả cho việc trích dẫn:** lượt chấm gold 27/08 chạy với
`USE_OCR_FIRST=true`, tức một cấu hình khác cấu hình tài liệu mô tả. Một số giá
trị có thể đến từ nhánh regex chứ không từ VLM.

**ĐỪNG nâng `PATIENCE_PAGES`** — nó nới đúng nhánh đang được kiểm soát tốt và
không chạm nhánh chiếm 77% chi phí.

### 12.3 Hằng số chưa hiệu chỉnh — đo lại trước khi tin

1. `TOTAL_ASSETS_BOUNDS` trong `fields_config.py` — hiện `(1e10, 1e15)`, dựa
   trên suy luận, chưa dựa trên phân phối đo được.
2. `XAC_SUAT_TIEN_NGHIEM` trong `repair/candidates.py` — đi **thẳng** vào hàm
   mục tiêu của C2, nên đặt sai thì thuật toán vẫn chạy và vẫn cho nghiệm, chỉ
   là ưu tiên sai loại sửa.
3. `FIELD_RATIO_BOUNDS` và `REVENUE_TO_ASSETS_LIMIT` — hiệu chỉnh trên **đúng
   một công ty** (VNM Q1/2026). Chỉ thị của người dùng: **không chỉnh các ngưỡng
   này khi dữ liệu mới chỉ có một công ty.**
4. `MAX_CHANGES_MAC_DINH = 2` — **đã đo lại 24/08/2026 trên bộ chỉ tiêu đã
   chốt, giữ nguyên giá trị 2** (bảng ở `CHANGELOG.md`). Hai kết luận còn ràng
   buộc: mỗi nấc `max_changes` đắt lên **khoảng 20 lần**, chi phí nằm trọn ở
   việc chứng minh KHÔNG có nghiệm; và ở `max_changes = 2` chi phí đi theo
   `C(n,2)` nên **ràng buộc thật khi mở rộng bộ chỉ tiêu là chi phí gán nhãn
   tay, không phải chi phí tính toán**.
5. `MAX_UPLOAD_BYTES = 50 MB` trong `api.py` — chọn theo đúng một tài liệu.
6. `PHAT_HANG_LAN_CAN = 1.0` trong `repair/candidates.py` — phạt cost mỗi hạng
   của ô lân cận. Là lựa chọn MÔ HÌNH: nó chỉ nói "hạng sau đắt hơn hạng
   trước", chưa nói đắt hơn bao nhiêu là đúng. `do_phu_ung_vien.py` KHÔNG đo
   được nó — tầng XBRL truyền `bbox=None` nên không chạm tới nhánh xếp hạng.
   Muốn số cho nó thì phải chạy đường ảnh, tức tốn API.

---

## 13. MỐC 3 — điều kiện dừng KHÔNG kích hoạt, mốc chưa đóng

`BUILD-SPEC.md` phần E định nghĩa mốc: **nếu baseline 9 ngang bằng phương pháp
đề xuất thì luận điểm "đọc lại nguồn" sai** — dừng, báo cáo, lùi paper về tầng
dataset + identifiability, đừng chạy tiếp C3 và toàn bộ ablation.

**Kết quả: điều kiện dừng KHÔNG kích hoạt.** Được phép đi tiếp sang C3, C4,
D2–D4 và sang việc gán nhãn `data/gold/`. Bảng số đầy đủ ở
[data/output/moc3_15congty.md](data/output/moc3_15congty.md) và ở
`CHANGELOG.md` mục 25/08/2026; **mốc chưa ĐÓNG** vì phán quyết cuối cùng của H3
nằm ở **tầng gold Việt Nam**, nơi có ảnh nên cả năm nguồn ứng viên đều chạy và
cả bốn chế độ lỗi đều kiểm được khả năng sửa. Tầng XBRL đã cho hết những gì nó
có thể cho.

### 13.1 Bốn thứ từng làm hỏng phép đo — cạm bẫy có thể lặp lại

| Thứ chặn | Vì sao nó làm hỏng phép đo | Đã gỡ |
|---|---|---|
| Rò rỉ đáp án | Donor tính trung vị trên cả hồ sơ đang xét nên 32% chỉ tiêu có donor trùng khít giá trị thật — baseline 9 khi đó là **oracle** | `e6c286c` loại cả công ty đang xét |
| Tắt mất nguồn ứng viên chính | Gọi `generate()` không truyền `o_lan_can`, tức bỏ hẳn việc đọc lại ô lân cận — đúng cơ chế cần chứng minh | đã sửa |
| Xếp hạng ô lân cận nằm im | Lấy `Provenance.bbox` (bbox cả VÙNG) làm tâm chữ thập nên mọi ô cùng hạng 0, cost bằng nhau, trần cắt bằng bốc thăm — nguồn bật mà vô dụng, và certificate cũ không phân biệt được | `repair/neo.py`; certificate khai `neo` theo từng chỉ tiêu |
| Cột kỳ so sánh rỗng | 0/158 chỉ tiêu có giá trị ở kỳ thứ hai nên `col_shift` bỏ 120/130 lượt | `f80a53d` chọn kỳ theo **độ phủ chỉ tiêu** |
| Ma trận nhầm chữ số chưa đo từ dữ liệu thật | Bộ tiêm và bộ sinh dùng hai mô hình lỗi khác nhau nên chỉ số `digit_sub` không mang thông tin về phương pháp | `90b271a`; độ phủ 0,046 → 0,615 |

**Phép đo phải chạy lại mỗi lần đụng vào bộ sinh ứng viên hoặc bộ tiêm lỗi:**
[src/eval/do_phu_ung_vien.py](src/eval/do_phu_ung_vien.py) — nhanh, không gọi
`diagnose()`. **Độ phủ chính là thứ quyết định bảng Mốc 3 đọc ra nghĩa gì.**

**Một giới hạn không gỡ được ở tầng XBRL:** `row_shift` cần ảnh, tức cần
`data/gold/`. Và toàn bộ dữ liệu là doanh nghiệp Mỹ theo US-GAAP.

### 13.2 Bảng gộp không đọc được một mình — phải tách theo chế độ lỗi

| Chế độ lỗi | Kiểm được khả năng SỬA? | Còn sai — đề xuất | — baseline 9 | Ra tay — đề xuất |
|---|---|---:|---:|---:|
| `sign` | có | **0,392** | 0,600 | 0,608 |
| `digit_substitution` | có | **0,485** | 0,592 | 0,377 |
| `row_shift` | KHÔNG — phủ 0,015 | 1,000 | 0,654 | 0,062 |
| `col_shift` | KHÔNG — phủ 0,000 | 1,000 | 0,738 | 0,092 |

Trên hai chế độ tầng này kiểm được, đề xuất thắng **+20,8 điểm** (`sign`) và
**+10,7 điểm** (`digit_substitution`), cả hai vượt xa ngưỡng effect size 3 điểm.
Chiều chống bịa cũng thắng (0,00400 so 0,00609) — thắng cả hai chiều, chứ không
phải thắng chiều một mà thua chiều hai.

Ở `row_shift`/`col_shift` đề xuất **ABSTAIN đúng như thiết kế** (ra tay 0,062 và
0,092) trong khi baseline 9 nặn giá trị donor. Đó là **chưa được kiểm**, không
phải **đã thua**.

### 13.3 Trần trên của mọi bộ giải liên tục — kết quả đổi cách đọc cả bảng

Nghi vấn ban đầu: baseline 9 sửa đúng 26–35% lượt `row_shift`/`col_shift` trong
khi ở hai chế độ đó giá trị thật đã bị ghi đè và biến mất khỏi bảng.

**Giả thuyết đầu đã bị bác bằng số đo** — nghi các lượt trúng rơi vào chỉ tiêu
có giá trị thật bằng 0: đo được **0 trên 520 lượt**. Bộ đếm giữ lại trong bảng
để lần sau không ai kiểm lại.

**Lời giải thích đúng: baseline 9 không bịa, nó NGHỊCH ĐẢO.** Nó chọn bộ giá
trị gần donor nhất *mà vẫn thoả ràng buộc*. Khi đúng một trường sai và trường
đó được thả ra một mình thì `r = δᵢ·aᵢ`, nên nghiệm duy nhất là `δ = −δᵢ`, bất
kể donor ở đâu. Dấu vết nằm sẵn trong bảng: nó sửa đúng KHI VÀ CHỈ KHI nó định
vị đúng (lệch 1–2 lượt trên 130 ở ba trong bốn chế độ).

| Trạng thái | Tỷ lệ | Nghĩa |
|---|---:|---|
| Ràng buộc **chốt đúng** giá trị | 0,608 | **Trần trên của mọi bộ giải liên tục** khi không đọc lại tài liệu |
| Không chốt | 0,146 | Khoảng hở mà việc đọc lại nguồn tồn tại để lấp |
| Cột bằng 0 | 0,246 | Không ràng buộc nào bảo vệ — kết quả của **H0** |

Con số 0,246 khớp 125/520 = 0,240 lượt VERIFIED, tức hai phép đo độc lập cho
cùng một câu trả lời.

**Chuẩn hoá theo trần — cách trình bày nên dùng trong bài:**

| Chế độ lỗi | Trần | Đề xuất | % trần | Baseline 9 | % trần |
|---|---:|---:|---:|---:|---:|
| `sign` | 0,608 | **0,608** | **100,0%** | 0,400 | 65,8% |
| `digit_substitution` | 0,608 | 0,515 | 84,7% | 0,408 | 67,1% |
| `row_shift` | 0,608 | 0,000 | 0,0% | 0,346 | 56,9% |
| `col_shift` | 0,585 | 0,000 | 0,0% | 0,262 | 44,8% |

Ở `sign`, đề xuất **giải đúng MỌI lượt mà thông tin tồn tại** và im lặng ở phần
còn lại. Chuẩn hoá theo trần identifiability biến H0 từ một mục độc lập thành
công cụ làm cho H2 và H3 đọc được.

### 13.4 Bốn thứ ràng buộc lượt chạy sau

1. **Thiết kế hiện tại đang chọn ca thuận lợi nhất cho baseline 9** (Câu 8,
   mục 0). Tầng XBRL tiêm **đúng một lỗi mỗi lượt**, mà lỗi đơn định vị được
   lại chính là ca phép nghịch đảo liên tục giải trọn vẹn. Khoảng hở mà "đọc
   lại nguồn" lấp là ca ràng buộc KHÔNG chốt được giá trị: nhiều lỗi đồng thời,
   cột bằng 0, cột tỷ lệ với nhau, lỗi nằm trong `null(A)`. **Lượt chạy tới
   phải tiêm nhiều hơn một lỗi mỗi lượt** — thay đổi thiết kế, nên ghi vào mục
   Sửa đổi của `PREREGISTRATION.md` TRƯỚC khi chạy.
2. **`het_gio` đo tải máy chứ không đo phương pháp.** Lượt 26/08 tái lập từng
   chữ số mọi chỉ số chính, nhưng **71/249 lượt ABSTAIN chuyển bucket** giữa
   `het_gio` (85 → 156) và `vuot_tran_thay_doi` (162 → 93) chỉ vì phải chia CPU
   với việc chấm tập gold. Trong bài phải **ghi rõ bảng lý do ABSTAIN phụ thuộc
   ngân sách tính toán**, hoặc bỏ `het_gio` ra khỏi mọi lập luận.
3. **`vo_nghiem` = 0 trên 520 lượt, ở CẢ HAI lượt chạy.** Chính báo cáo ghi
   *`vo_nghiem` là ca DUY NHẤT chứng minh được* luận điểm chống bịa — và nó
   chưa từng xảy ra. Toàn bộ ABSTAIN đều là *ta đã không tìm*, không phải
   *không có*. Lập luận chống bịa ở tầng XBRL vì thế **không** tựa được vào
   bảng ABSTAIN; nó tựa vào tỷ lệ bịa mức trường, và đó mới là con số được
   phép dùng.
4. **Kết quả không được lưu dạng JSON.** `chay()` trả dict rồi `bao_cao()` in
   ngay ra stdout. Muốn in lại bảng theo cách khác phải chạy lại 103 phút. Cần
   ghi `data/output/moc3_<ngày>.json` trong khối `__main__` trước lượt kế tiếp.

> **Thứ tự thời gian của ba tu chính, ghi lại vì đây là chỗ dễ bị cáo buộc đọc
> kết quả theo ý mình.** Lượt chạy bấm lúc 14:22:53 và sinh con số đầu tiên lúc
> 16:05. Bảng tách theo chế độ lỗi commit 14:18 (trước khi chạy); hai tu chính
> Câu 7 commit 14:23 và 14:30 — **sau lúc bấm chạy**. Câu "ghi trước khi chạy"
> là SAI và không được viết vào bài. Câu đúng: **cả ba được ghi trước khi tồn
> tại bất kỳ con số nào**, sớm nhất 95 phút. Quyết định Câu 7 do người dùng
> chốt trong tin nhắn trước khi bấm chạy; commit chỉ là lúc chép vào file.

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
  `src/eval/metrics.py` — xem mục 5.7.

---

## 15. Lệnh hay dùng

```bash
# Kiểm sau MỖI thay đổi
python -m ruff check src tests
python -m pytest -q

# Sinh lại báo cáo identifiability cho cả hai chuẩn
PYTHONIOENCODING=utf-8 python src/constraints.py

# TẢI 10 tài liệu gold đầu về data/bctc/ (danh mục ở data/nguon_gold.json)
python src/tai_bctc.py

# ĐO độ phân giải bản quét — trục phân nhóm Stress thứ ba (mục 19.5)
python src/do_do_phan_giai.py            # chỉ in bảng
python src/do_do_phan_giai.py --ghi      # ghi vào data/nguon_gold.json

# CHẤM PIPELINE trên tập gold (mục 20). Tốn tiền gọi API thật, 5-50 phút
# một tài liệu. Kết quả ghi sau MỖI tài liệu nên đứt gánh không mất.
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --chuan-tu-gold
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --tiep-tuc --chuan-tu-gold

# CÔNG CỤ GÁN NHÃN tập gold, rồi mở http://127.0.0.1:8100
# Dùng launcher chứ ĐỪNG gọi thẳng uvicorn: lệnh gọi thẳng cần đặt biến môi
# trường, mà `VAR=x lệnh` chạy trên bash nhưng LỖI CÚ PHÁP trên PowerShell —
# shell chính của máy này. Đã mất thời gian vì việc đó một lần ngày 25/08.
python chay_gan_nhan.py --pdf-dir data/bctc
python chay_gan_nhan.py --pdf-dir D:/bctc --port 8200

# AI CÒN ĐƯỢC VÀO TẬP GÁN NHÃN ĐÔI (Câu 12). Chạy TRƯỚC khi chọn tài liệu
# cho lượt gán nhãn lại: tài liệu đã chạy pipeline thì đáp án đã lộ.
PYTHONPATH=src python src/eval/tap_dong_thuan.py

# ĐO LUẬT DẤU trên tập gold. Chạy lại trên kết quả đã lưu, KHÔNG gọi API,
# nên chạy lại được sau mỗi lần đụng vào luật. Kết quả:
# data/output/luat_dau_tap_gold.md
PYTHONPATH=src python src/eval/do_luat_dau.py

# BẬT TẦNG REPAIR trên đường chạy tài liệu (mặc định TẮT). Bật nó thì đầu ra
# đã bị ràng buộc làm sạch, nên lượt chạy đó KHÔNG dùng được cho H1.
# Certificate ghi ở meta["chung_chi_repair"] của kết quả.
BAT_TANG_REPAIR=true python src/router.py <file.pdf>

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

# Đo ĐỘ PHỦ ỨNG VIÊN — phải chạy TRƯỚC khi đọc bảng Mốc 3, xem mục 13.
# Nhanh (không gọi diagnose(), chỉ dựng ứng viên rồi so khớp).
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/do_phu_ung_vien.py     > data/output/moc3_do_phu_ung_vien.md

# Tải hồ sơ XBRL — chạy được từ shell trên máy người dùng.
# (Cảnh báo "container không ra được sec.gov" trong docstring fetch.py chỉ
#  đúng với Docker. Từ shell thường thì sec.gov với tới được bình thường.)
export SEC_USER_AGENT="Tên thật email@example.com"
python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --dry-run
```

---

## 16. Bước kế tiếp

Đường găng đi qua **tầng gold**, không còn qua Mốc 3.

1. **Chạy lại `--chi BMP SBT`** — một lượt chạy trả lời được BA câu cùng lúc,
   nên nó là việc rẻ nhất trên bàn:
   *(a)* bản vá nới mép có đọc ra dòng "Đơn vị tính" không (mục 20.5b);
   *(b)* bộ đếm kiên nhẫn của nhánh OCR tiết kiệm được bao nhiêu giờ (mục 12.2);
   *(c)* probe mất bao nhiêu trang vì bộ đếm ấy — so `probe_so_trang` với
   lượt 27/08. Xem bẫy `--tiep-tuc` ở 20.2.
2. **Chẩn đoán SBT** — 10/24 lỗi câm, nghi lỗi **chọn nguồn** (mục 20.4). Đây
   là khoản lớn nhất còn lại, và luật dấu **chứng minh được là không chạm tới
   nó**: bộ số lấy từ bảng khác tự nó cũng cân nên residual bằng 0 tuyệt đối.
4. **Gán nhãn thêm 2 tài liệu có đồng hồ chạy thật** (mục 19.3 bước 1).
5. **Chọn mã cho mốc 60** rồi thêm vào `data/nguon_gold.json`.
6. **Bước D của phương án C** — nhận diện chuẩn mẫu biểu (Phụ lục B). Cùng họ
   với việc 2: cả hai là "thứ cần đọc nằm ngoài vùng bảng đã cắt". Chạy lại
   `tieu_de_trong_vung_cat` trên 10 tài liệu thay vì một.
7. **Ba baseline còn thiếu: 4, 5, 7.**
8. **Bật `n_samples > 1`** — không có nó thì H1 không đo được (mục 20.6).
9. Sau đó: **C3** (vòng lặp đọc lại) → **C4** (verdict) → chạy Mốc 3 TRÊN TẦNG
   GOLD → D2/D3/D4. **Chỉ bước đó mới đóng được Mốc 3.**

### Ngân sách tầng gold, đối chiếu với số đo thật

| Khoản | Dự trù cũ (60 tài liệu, 21 chỉ tiêu) | Ước theo số đo (100 tài liệu, 27 chỉ tiêu) |
|---|---:|---:|
| Điền nhãn | 20–25 giờ | **~12 giờ** (trung vị 442 giây × 100) |
| Gán nhãn đôi + phân xử | 8–10 giờ | ~3,5–6 giờ |
| Đo trần người | 3 giờ | ~1–2 giờ |
| Tìm và tải tài liệu | 15–20 giờ | **còn việc chọn mã** — có API và script |

Con số ~12 giờ dựa trên **8** số đo; đủ 10 thì cập nhật bảng **một lần**, không
sửa dần theo mẫu mỏng.

### Ba việc song song, không cái nào chặn cái nào

- **Tìm người hướng dẫn hoặc đồng tác giả.** Nâng xác suất được nhận nhiều
  nhất trên mỗi đơn vị công sức — hơn bất kỳ thí nghiệm nào còn lại. Bài Q1
  đầu tay không có người hướng dẫn mạnh thường chết ở khâu framing và khâu trả
  lời reviewer, không phải ở khâu kết quả.
- **Đo throughput API thật trên 5 tài liệu.** B2 dùng self-consistency k=5;
  nhân với 10 baseline, nhiều model, nhiều seed, cộng tầng XBRL thì đây là hàng
  chục nghìn lời gọi trên free tier OpenRouter. Rủi ro này không làm chậm lịch
  — nó có thể **chặn hẳn việc tạo ra con số**.
- **Bắt đầu chuỗi hai tuần cho lượt gán nhãn lại càng sớm càng tốt** (mục 19.3
  bước 4): đó là thời gian **chờ** nằm trên đường găng.

---

## 17. Việc đã quyết nhưng CHƯA thi công

Đọc mục này trước khi bắt đầu bất kỳ việc gì ở mục 16, kẻo làm theo con số cũ.

### 17.1 Bộ chỉ tiêu đã chuyển sang kịch bản E — ĐÃ LÀM 25/08/2026 (`f1c2738`)

Số đo D so với E ở `CHANGELOG.md` 25/08/2026. Ba thứ còn ràng buộc:

- **`tien_va_tuong_duong_tien` là điểm đáng giá riêng của E.** Nó ĐÃ nằm trong
  bộ từ trước nhưng lẫn trong lớp năm thành phần của mã 100; đẳng thức liên kết
  chéo B03 gắn cho nó một đẳng thức **thứ hai** để tách ra. Không nhóm mở rộng
  nào khác gỡ được một chỉ tiêu CŨ ra khỏi lớp lẫn.
- **Phần không đẹp, phải báo cáo vì nó là kết quả của H0:** không gian null
  tăng 13 → 17 chiều còn tỷ lệ định vị được gần như đứng yên (25% → 27%). **E
  tốt hơn D nhưng không sửa được kết luận nền của H0.**
- **ĐỪNG ĐỔI BỘ CHỈ TIÊU NỮA.** Việc này cố ý làm khi `data/gold/` còn trống
  hoàn toàn, vì đổi sau đó buộc gán nhãn lại cả tập. Cửa sổ ấy đã đóng.

**Một khoảng trống mới sinh ra, đã chốt bằng test:** bộ số đối chiếu
`VNM_Q1_2026` trong `tests/test_constraints.py` do người đọc tay và chỉ phủ B01
với B02 — bản PDF trong `data/samples/` là ảnh scan nên không rút số B03 bằng
máy được. `test_bo_so_that_chua_phu_duoc_B03_va_test_phai_noi_ra` chốt tường
minh sáu chỉ tiêu còn thiếu; bổ sung số thì test đó đỏ và nhắc gỡ phần cắt bớt.

**Thứ tự cam kết đã bị vượt, ghi lại chứ không bỏ qua:** việc bấm giờ thử đáng
lẽ phải làm **trước** tài liệu đầu tiên; thực tế tài liệu đầu tiên được gán
nhãn trước rồi chính nó cung cấp số liệu. Thiệt hại thực bằng 0 vì số tài liệu
đã gán nhãn dưới giao thức trần người vẫn là 0.

### 17.2 Quy mô tập gold lên khoảng 100 — CHƯA CẬP NHẬT TÀI LIỆU

Người dùng chốt 24/08/2026: khoảng **100** thay vì 60. Việc sửa tài liệu cho
khớp được **cố ý hoãn**; đây là danh sách chỗ phải sửa khi làm:

- `ANNOTATION-GUIDELINE.md` mục 7 — đang ghi "60 tài liệu, chia 30 TT200 + 30
  TT99". **Giữ tỷ lệ 50/50** vì trục transfer của ablation 8 dựa vào đó.
- `PREREGISTRATION.md` — thêm mục Sửa đổi. Bắt buộc: quy mô mẫu là tham số của
  mọi phép tính power.
- `ADDENDUM` mục 4 — mọi con số tính power lấy 60 làm số cụm độc lập. Với 100
  thì cả bảng đó đổi.

**Điều phải nói kèm, kẻo con số 100 bị hiểu sai:** thêm tài liệu chủ yếu chỉ
giúp **H1**. H2 và H3 đo trên **số lỗi**, không phải số trường — ở 60 tài liệu
số lỗi rơi vào 75–225, lên 100 cũng chỉ thành 125–375. Đó đúng là lý do
`ADDENDUM` mục 4 kết luận tầng XBRL là **bắt buộc**. Muốn thêm số liệu cho
H2/H3 thì **mở rộng tầng XBRL rẻ hơn hẳn** so với gán nhãn thêm tài liệu tay.

---

## 18. Nơi nộp — đã chốt 24/08/2026

**Đích: ICDAR 2027 main track, hạn 28/02/2027.** Kuala Lumpur, 18–22/08/2027.
Springer LNCS, tối đa 17 trang kể cả hình và tài liệu tham khảo, phản biện ẩn
danh hai chiều có rebuttal, cho phép đăng arXiv trước. Lý do đổi khỏi
ICDAR-IJDAR journal track ở `CHANGELOG.md` 24/08/2026.

**Hai ràng buộc còn hiệu lực:**

- **KHÔNG nộp RIVF hay SoICT** với nội dung trùng. Journal track loại bản mở
  rộng từ hội nghị (*"Journal versions of previously published conference papers
  ... will not be considered"*), nên chiến lược "nộp song song" của proposal vừa
  đóng cửa journal track vừa tạo vấn đề trùng lặp với ICDAR main.
- **Đường lên Q1 không mất.** Bài đã đăng hội nghị vẫn nộp IJDAR được qua quy
  trình thường. Lộ trình: ICDAR 2027 main → mở rộng thành bài IJDAR sau đó.
  IJDAR có IF 2,5, SJR 0,83, **Q1** ở Computer Vision & Pattern Recognition.

### Related work — đối thủ đã kiểm, tra 24/08/2026

Kết quả đầy đủ ở `MD file/FINAL-proposal-reread-dont-repair.md` **mục 14b**.

**Đóng góp lõi vẫn chưa ai làm:** đọc lại nguồn thay vì sửa trên tập số cố
định; H0 identifiability; ViFinKIE.

| Công trình | Có chiếm chỗ không | Hệ quả |
|---|---|---|
| **arXiv 2608.14639** — *Valid Per-Field Selective Risk Control* (08/2026) | Không: không ràng buộc miền, không sửa, không sinh ứng viên từ ảnh, không identifiability | **Thu hẹp kết quả dự kiến số 4** — phần risk–coverage phải phát biểu là "ràng buộc miền làm bộ điểm thứ ba", KHÔNG được phát biểu là "chúng tôi làm selective prediction". Ngược lại nó **làm mạnh H1**: có công trình độc lập ghi nhận chế độ hỏng của cách tiếp cận dựa trên confidence |
| **FinReporting** — arXiv 2604.05966 | Không: không định vị bằng ma trận ràng buộc, không đọc lại ảnh nguồn | Trích dẫn phải thêm |
| **Blueprint** (VLDB) | Không: chỉ chấm điểm các phương án trích xuất đã có | — |
| **FinStat2SQL** — arXiv 2506.23273 | Không: lấy Excel từ FiinPro, không OCR, không PDF, không benchmark | Là công trình tài chính Việt Nam gần nhất |

**Một câu đáng trích dẫn nguyên văn**, từ ban tổ chức ICDAR 2026 HIPE-OCRepair:
*"Trong thực hành hậu-xử-lý OCR chuẩn, hệ thống chỉ làm việc trên văn bản và
không có quyền truy cập ảnh tài liệu gốc."* Dùng ở Introduction thì luận điểm
"không ai đọc lại nguồn" có người ngoài chứng thực.

**Nhịp lấp của mảng này là lý do thật để đi nhanh** — đối thủ gần nhất đăng
đúng tháng tra cứu. Luật dừng của proposal vẫn giữ: kiểm lại arXiv **một lần
duy nhất** ngay trước khi nộp, không tra liên tục.

---

## 19. Tầng gold — công cụ, trình tự, nguồn tài liệu, độ phân giải

Hiện trạng của tầng gold. **Lý do và số đo của từng thay đổi ở `CHANGELOG.md`
(26/08/2026)**; mục này giữ cách dùng, ràng buộc, và việc còn lại.

### 19.1 Công cụ gán nhãn `src/gan_nhan/`

```
python chay_gan_nhan.py          # rồi mở http://127.0.0.1:8100
```

**Dùng launcher, ĐỪNG gọi thẳng `uvicorn`.** Gọi thẳng cần đặt biến môi trường
`GAN_NHAN_PDF_DIR`, mà cú pháp `VAR=x lệnh` chạy trên bash và **lỗi cú pháp
trên PowerShell** — shell chính của máy này. Đã mất thời gian vì đúng việc đó
một lần. Launcher còn đặt biến TRƯỚC khi uvicorn nạp app (nên truyền chuỗi
`"gan_nhan.app:app"`), và kiểm thư mục PDF tồn tại và không rỗng trước khi mở
cổng.

| File | Việc |
|---|---|
| `src/gan_nhan/app.py` | FastAPI: phục vụ ảnh trang, danh sách chỉ tiêu, kiểm đẳng thức, ghi/đọc file gold, lớp `DongHo` |
| `src/gan_nhan/giao_dien.html` | Hai khung: PDF bên trái (PageUp/PageDown, +/− phóng to), bảng chỉ tiêu bên phải |
| `src/gan_nhan/trang.py` | Kết xuất trang PDF bằng **pypdfium2** — KHÔNG dùng pdf2image, máy này không có `pdftoppm` |
| `src/gan_nhan/so_viet.py` | Đọc số kiểu Việt: `1.234.567`, `(1.234)` là số âm, `-`/`–`/`—` là rỗng |
| `src/gan_nhan/kiem.py` | Chạy 9 đẳng thức trên chính số vừa gõ, cộng danh mục kiểm của guideline |

**Luật 1 (người gán nhãn mù với đầu ra pipeline) được chốt bằng test, không
bằng lời hứa.** `tests/test_gan_nhan_mu_voi_pipeline.py` phân tích AST của cả
gói và bắt đỏ nếu bất kỳ module nào import `router`, `extract_vlm`,
`extract_baseline`, `ocr_baseline`, `layout_detection`, `repair`, hay `api`;
có test riêng cho `giao_dien.html`. Test loại trừ docstring khỏi phần mã thực
thi, nếu không thì chính comment giải thích lệnh cấm sẽ tự làm đỏ.

**Ghi đè được và có dấu vết.** Nút "Mở lại bản đã lưu" nạp lại toàn bộ ô từ
file gold đã có, và mỗi lần ghi tăng `so_lan_ghi`. Đồng hồ **cố ý chạy lại từ
đầu** khi mở lại chứ không cộng dồn: `thoi_gian_giay` đo tốc độ trên một tài
liệu MỚI, trộn một lần sửa một ô vào sẽ làm hỏng chính phép đo trần người.

**Ba quyết định thiết kế của đồng hồ, mỗi cái một lý do còn ràng buộc:**

1. **Máy chủ giữ đồng hồ, trình duyệt chỉ vẽ lại.** Làm ngược lại thì một lần
   tải lại trang xoá sạch phép đo — mà tải lại trang là chuyện thường khi đang
   lật một PDF 40 trang.
2. **Từ chối ghi khi đồng hồ chưa từng chạy**, thay vì cảnh báo rồi vẫn ghi số
   0. Một tài liệu quên bấm giờ chỉ lộ ra lúc gom số, và lúc đó không bấm lại
   cho quá khứ được nữa. Lối thoát là ô tick "không đo giờ tài liệu này".
3. **Mở lại bản đã lưu KHÔNG tự chạy đồng hồ.**

> **Một lỗi test bắt được, sẽ tái diễn ở chỗ khác.** Bản đầu của `DongHo` suy
> trạng thái từ `tong_giay > 0`. Trên Windows `time.monotonic()` nhảy theo bước
> ~15 ms, nên bấm chạy rồi dừng ngay cho ra đúng `0.0`, và đồng hồ đã chạy
> trông y hệt đồng hồ chưa ai đụng vào. Đã sửa bằng khoá `da_bat_dau` riêng.
> **Bài học: đừng suy trạng thái từ một con số bằng 0, ở bất kỳ tầng nào.**

#### Trình tự một tài liệu

Guideline giữ các QUY TẮC; đây là thao tác, và nó chưa nằm ở đâu khác.

1. Chọn file, gõ `doc_id` — **đúng bằng tên file bỏ đuôi** (`HPG_2026Q2_TT99`).
2. Bấm **▶ Bắt đầu bấm giờ**. Nghỉ giữa chừng thì ⏸ Tạm dừng.
3. Xác định chuẩn **bằng mắt** theo guideline mục 3.7. Đừng suy từ năm báo cáo.
4. Chép `unit_declared` **nguyên văn**. Guideline mục 3.1 cấm suy hệ số từ độ
   lớn con số.
5. Điền, bấm **Kiểm đẳng thức**. Lệch thì **đọc lại báo cáo**, đừng sửa cho
   cân; công cụ cố ý không bao giờ gợi ý giá trị.
6. Tick danh mục kiểm, bấm Lưu.

> **Không có đường tắt, và đó là chuyện tốt.** Cả 10 tài liệu đều là ảnh quét
> không lớp text, nên không `pdftotext` được, không copy-paste được. Ai định
> "tách nội dung ra khỏi PDF" cho nhanh thì hoặc phải chạy OCR — **vi phạm Luật
> 1** — hoặc phải đọc bằng mắt. Vi phạm Luật 1 là loại **không để lại dấu vết**:
> file gold nhiễm trông y hệt file sạch.

### 19.2 `VNM_2026Q1_TT99` — tài liệu gold đầu tiên, và ca dị thường

27 chỉ tiêu, đơn vị VND, cả 9 đẳng thức cân. **Nguồn gốc chưa xác định được, và
đã thôi truy:** file thiếu khoá `so_lan_ghi` và có `thoi_gian_giay` bằng 0,
trong khi công cụ luôn ghi cả hai. Người dùng chọn **xử lý nguyên nhân thay vì
chú thích triệu chứng** — công cụ nay có nút bấm giờ tường minh và từ chối ghi
khi đồng hồ chưa chạy, nên ca này không lặp lại được.

File giữ nguyên, không sửa; nó tự đọc ra `trang_thai_dong_ho = "khong_do"`.
**Hệ quả:** tài liệu này KHÔNG đóng góp số nào cho nhịp gán nhãn. Nó cũng
**thiếu PDF** trong `data/bctc/` — xem mục 20.3 và 20.6.

**Một lỗi bắt được trên chính nó, đáng nhớ vì nó là ca H1 sẽ gặp:** mã 52 bị
đọc `1` thành `0` ở hàng chục nghìn, lệch đúng 10.000 đồng trên một con số 48
tỷ. Đẳng thức báo ĐẠT vì sai số tương đối 4·10⁻⁹ nằm dưới
`IDENTITY_TOLERANCE_RATIO` (10⁻⁷); người dùng đọc lại báo cáo mới ra. **Không
chỉnh ngưỡng dung sai** — dữ liệu mới có một công ty. Và cặp `1↔0` KHÔNG có
trong ma trận nhầm chữ số đo từ EasyOCR (cặp trội của máy là `9→0`): nếu mô
hình lỗi của người khác mô hình lỗi của máy thì đó là quan sát dùng được cho
bài, nhưng **N = 1 chưa kết luận gì**.

### 19.3 Việc còn lại của tầng gold, theo thứ tự chặn nhau

1. **Chạy đồng hồ thật trên 10 tài liệu — CÒN THIẾU 2.** `data/gold/` có 11
   file nhưng chỉ **8** mang `trang_thai_dong_ho = da_do`: 361, 416, 433, 438,
   446, 461, 506, 579 giây. Ba file không tính: `VNM_2026Q1_TT99` (thiếu hẳn
   khoá), `DGC_2025Q2_TT200` và `TTF_2026Q1_TT99` (`khong_do`). Hai tài liệu bù
   phải nằm **ngoài** 11 file đã có — gán nhãn lại một file cũ thì đo nhịp của
   lần thứ hai.

   > **Kết quả đã cố định về mặt số học, nhưng vẫn phải đo đủ 10 rồi mới
   > tuyên.** Trung vị của 10 số chỉ chạy được trong dải 435,5–453,5 giây, nhân
   > 0,6 ra 4,36–4,54 phút — toàn dải dưới sàn 5 phút, nên đồng hồ trần người
   > **sẽ là 5 phút**. Tuyên sớm vì "đằng nào cũng ra 5 phút" thì con số vẫn
   > đúng nhưng cam kết thì hỏng, và lần sau không còn cách nào phân biệt một
   > suy luận số học với một lần tự cho phép mình bỏ bước.

2. **Chọn mã cho mốc 60** rồi thêm vào `data/nguon_gold.json`. Lộ trình
   10 → 60 → 100 chốt 26/08. Nay là việc chọn, không còn là việc dò nguồn.
3. **Chốt 20 hay 33 tài liệu gán nhãn đôi — CÒN MỞ.** `ADDENDUM` mục 5 viết
   "một phần ba tập gold", chốt khi tập là 60 nên ra 20; tập đích nay khoảng
   100 nên cách diễn đạt đó tự thành 33. Câu hỏi thật: một phần ba của MỐC NÀO.
   Từ 28/08/2026 số ấy phải lấy trên tài liệu **chưa chạy pipeline** (Câu 12),
   mà hiện chưa có tài liệu nào như vậy — nên bước này chặn **sau** bước gán
   nhãn thêm tài liệu.
4. **Lượt gán nhãn lại** — người chủ trì tự gán, cách lần đầu **ít nhất hai
   tuần**, không xem bản cũ. Mười tài liệu đầu gán nhãn 25–26/08/2026 nên sớm
   nhất là **09/09/2026**, nhưng chúng đã bị loại theo Câu 12, nên mốc thật là
   hai tuần sau khi có tài liệu mới. Hai tuần ấy là thời gian **chờ** nằm trên
   đường găng.
5. **Đo trần người**, 10 tài liệu, sau khi có số phút ở bước 1.

### 19.4 Nguồn tài liệu và 10 tài liệu đầu

Nguồn là **`finance.vietstock.vn`**, mục công bố thông tin HOSE/HNX/UPCoM.
[data/nguon_gold.json](data/nguon_gold.json) là danh mục nguồn (chỉ URL và siêu
dữ liệu, **vào git**); [src/tai_bctc.py](src/tai_bctc.py) tải về `data/bctc/`
(**không** vào git). Đây đúng là phương án phát hành `src/eval/schema.py` chốt
từ đầu: phát hành nhãn kèm URL nguồn và script tải, không phát hành PDF gốc.

```
python src/tai_bctc.py                    # tải cả 10
python chay_gan_nhan.py --pdf-dir data/bctc
```

**Cách lấy danh mục, ghi lại vì hai chỗ đã mất thời gian.** Trang
`/{MÃ}/tai-tai-lieu.htm` nạp danh sách bằng AJAX nên `curl` trang đó không thấy
gì; danh sách thật nằm sau `POST /data/getdocument` với thân
`code={MÃ}&page={N}&__RequestVerificationToken={token}`. Token là input ẩn
trong chính trang đó, và **thuộc tính HTML không đặt trong dấu nháy** nên biểu
thức dạng `value="..."` trượt sạch. Bỏ `type` ra khỏi thân yêu cầu: truyền
`type=0` thì máy chủ trả mảng rỗng. URL file rất đều:

```
https://static2.vietstock.vn/data/{HOSE|HNX|UPCOM}/{năm}/BCTC/VN/{QUY n}/{MÃ}_Baocaotaichinh_{Q n}_{năm}_{Congtyme|Hopnhat}.pdf
```

**Mười tài liệu, 5 TT99 + 5 TT200, mỗi tài liệu gánh một vai:**

| doc_id | Vai | dpi |
|---|---|---:|
| `HPG_2026Q2_TT99` | nền, VN30, thép | 200,0 |
| `VRE_2026Q1_TT99` | **mỏ neo scale** (`Đơn vị tính: Triệu VND`) | 200,0 |
| `DLG_2026Q2_TT99` | **scan kém + số âm** (mã 420 âm 1.988 tỷ) | **100,0** |
| `TTF_2026Q1_TT99` | **lỗ**, vốn hoá nhỏ | 200,0 |
| `BMP_2026Q1_TT99` | đối chứng sạch TT99 | 200,0 |
| `DGC_2025Q2_TT200` | đối chứng sạch TT200 | 200,0 |
| `HNG_2025H1_TT200` | **lỗ + `Ngàn VND` + dòng đổi tên "Lỗ"** | **143,9** |
| `SBT_2025Q2_TT200` | **niên độ lệch** (cột đầu năm là 30/6) | **89,9** |
| `MWG_2025Q1_TT200` | đối cực chất lượng ảnh, nét nhất lô | **295,8** |
| `VHC_2025Q1_TT200` | chống memorization, ngoài VN30 | 200,0 |

Năm trong mười là ca biên, đúng bằng tỷ lệ tập Stress guideline mục 7 chốt. Cố
ý: mười tài liệu này vừa là tập gold vừa là nguồn của **trung vị nhịp gán
nhãn**, nên chúng phải ĐẠI DIỆN cho tập 100 — dồn toàn ca dễ thì đồng hồ trần
người quá ngặt, dồn toàn ca khó thì quá rộng.

**Một mã đáng thêm vào tập Stress về sau:** `MSN_2026Q2` — mục lục quý 2 **năm
2026** ghi *Bảng cân đối kế toán (Mẫu số B01a-DN)*, tên gọi TT200 trên một kỳ
mà TT99 đã có hiệu lực. Chưa soi tới trang biểu mẫu thật nên chưa kết luận.
**Đừng suy chuẩn từ năm báo cáo.**

### 19.5 Độ phân giải bản quét — cách đo và cạm bẫy

Nhóm Stress thứ ba đổi từ "bản scan chất lượng thấp" (100% quần thể thoả, tức
không chia được nhóm nào) sang **độ phân giải bản quét**, ghi làm **biến liên
tục**. Số đo ở bảng mục 19.4; dải **89,9–295,8 dpi, trung vị 200,0**.

**Công cụ:** `python src/do_do_phan_giai.py` in bảng, thêm `--ghi` thì ghi vào
khoá `do_phan_giai_dpi` của `data/nguon_gold.json`. **Đừng sửa tay khoá đó.**

> **Cạm bẫy đã mất thời gian: `horizontal_dpi`/`vertical_dpi` của pdfium SAI ở
> trang đặt ảnh xoay.** Hai trường đó chỉ chia cho phần đường chéo của ma trận
> đặt ảnh; ma trận xoay 90° có đường chéo bằng 0 nên pdfium chia nhầm cạnh. SBT
> bị báo `127,3 / 63,5` dpi — trông như bản quét bị kéo dãn — trong khi sự thật
> là **90 dpi đều cả hai chiều**. Cách đúng: chiếu qua ma trận, cạnh ngang trải
> theo `(a, b)` và cạnh dọc theo `(c, d)`, lấy chuẩn Euclid từng véc-tơ. Đã
> chốt bằng `tests/test_do_do_phan_giai.py`.

**Bốn giới hạn phải nêu kèm bất cứ khi nào dùng trục này:**

1. **Sáu trong mười rơi đúng 200,0 dpi** — phân bố dồn cục, sức phân biệt nằm
   gần hết ở hai đuôi. Đủ 100 tài liệu thì đo lại phân bố TRƯỚC khi tin vào một
   hệ số tương quan nào.
2. **Không ngưỡng nào được chốt**, cố ý. Ngưỡng, nếu về sau cần, phải là tu
   chính riêng ghi trước khi nhìn bảng kết quả tương ứng.
3. **Độ phân giải không bao trọn chữ "chất lượng".** Trang lệch, dấu mộc đỏ đè
   lên chữ số, in mờ lệch nét là những trục riêng máy chưa đo được. Tương quan
   bằng 0 với dpi KHÔNG cho phép kết luận chất lượng ảnh không ảnh hưởng.
4. `HNG_2025H1_TT200` là tài liệu DUY NHẤT **trộn nhiều độ phân giải** trong
   cùng một file (có trang tới 300).

`PREREGISTRATION.md` đăng ký nó làm **hiệp biến cho phân tích THỨ CẤP**: dùng
cho việc chọn tài liệu theo thứ hạng, **không** được dùng để loại tài liệu khỏi
phân tích chính. Lý do phải đăng ký: một biến giải thích mới rất dễ bị lôi ra
sau khi bảng kết quả đã xong để giải thích một chênh lệch không mong đợi, và
lúc đó không ai phân biệt được nó với việc đi tìm hậu nghiệm.

---

## 20. Chấm pipeline trên tập gold — số thật đầu tiên, 26–27/08/2026

Trước mục này, **mọi con số chất lượng của dự án đều lấy trên tầng XBRL Mỹ
hoặc trên đúng một báo cáo VNM**. Đây là chỗ đầu tiên pipeline bị chấm trên
bộ tài liệu Việt Nam có nhãn tay. **Số đo trước/sau của hai bản vá kèm theo
nằm ở `CHANGELOG.md` mục 27/08/2026** — mục này giữ cách chạy, cạm bẫy, và
những gì chưa làm.

### 20.1 Công cụ `src/eval/chay_tap_gold.py`

```
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --chuan-tu-gold
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py            # đầu-cuối
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --tiep-tuc  # nối lượt đứt
```

**Hai chế độ, và khoảng cách giữa chúng CHÍNH LÀ phép đo.** `router.chon_chuan`
chưa có nguồn `nhan_dien` nên không ai chỉ định thì nó lùi về `DEFAULT_STANDARD`
là TT99; tập gold có 5 tài liệu TT200, mà mã 270 của TT200 là mã 280 của TT99.
`--chuan-tu-gold` là điều kiện **oracle**, đo trích xuất tách khỏi nhận diện.
Hiệu số hai chế độ đo đúng một thứ: **bước D của phương án C đáng giá bao nhiêu.**

Chấm ở mức TRƯỜNG, **gộp tử và mẫu** qua các tài liệu chứ không lấy trung bình
của các tỷ lệ — TT200 có 26 chỉ tiêu còn TT99 có 27 nên hai cách cho hai con số
khác nhau, và chỉ cách đầu cộng dồn được cho bootstrap theo cụm.

### 20.2 Ba cạm bẫy đã trả giá

1. **Ghi kết quả một lần ở cuối = mất sạch khi tiến trình bị giết.** Bài học
   có sẵn trong docstring nhưng chỉ được áp một nửa: *ghi TRƯỚC khi in* chống
   được lỗi định dạng, **không** chống được tiến trình bị giết. Nay ghi sau
   **mỗi** tài liệu, và `--tiep-tuc` bỏ qua doc_id đã có.
2. **Pipeline tự in giá trị từng ô ra cùng stdout.** Nay `redirect_stdout` đổ
   chúng vào `data/output/tap_gold_<chế độ>_pipeline.log`.
3. **`--chi BMP SBT` mà KHÔNG kèm `--tiep-tuc` sẽ ghi đè
   `tap_gold_chuan_tu_gold.json` bằng đúng 2 tài liệu**, xoá sạch kết quả 10
   tài liệu. Bản sao mốc so sánh giữ ở `..._TRUOC-VA-2026-08-27.json` —
   **đừng xoá**, nó là mốc duy nhất cho hai bản vá 27/08.

> **Hệ quả cho Luật 1, đã gỡ tận gốc 28/08/2026 (Câu 12).** `tap_gold_*.json`
> và `tap_gold_*_pipeline.log` có giá trị từng ô, nên 10 tài liệu này cùng
> `VNM_2026Q1_TT99` bị **loại vĩnh viễn khỏi tập gán nhãn đôi**. Khai báo ở
> khoá `gan_nhan_doi` của `data/nguon_gold.json`, đối chiếu bằng
> `src/eval/tap_dong_thuan.py`.

### 20.3 Kết quả — 10 tài liệu, chế độ `--chuan-tu-gold`, 27/08/2026

**Là 10 chứ không phải 11.** `VNM_2026Q1_TT99` có nhãn gold nhưng **không có
PDF** trong `data/bctc/`, nên runner ghi vào `thieu_pdf` rồi bỏ qua. Đây là
chỗ lệch sổ sách chưa vá: `data/gold/` có 11 file, `data/nguon_gold.json` khai
10, và VNM không có `do_phan_giai_dpi` nên mọi phân tích theo độ phân giải sẽ
**lặng lẽ** bỏ sót nó.

| doc_id | Trường đúng | Lỗi câm | Đơn vị | Cảnh báo |
|---|---:|---:|---|---:|
| `DGC_2025Q2_TT200` | 24/26 = 0,923 | 0,040 | ok | 1 |
| `DLG_2026Q2_TT99` | 24/27 = 0,889 | **0,000** | ok | 0 |
| `TTF_2026Q1_TT99` | 24/27 = 0,889 | **0,000** | ok | 0 |
| `MWG_2025Q1_TT200` | 23/26 = 0,885 | 0,115 | ok | 3 |
| `BMP_2026Q1_TT99` | 23/27 = 0,852 | 0,042 | **SAI** | 2 |
| `HPG_2026Q2_TT99` | 22/27 = 0,815 | 0,043 | ok | 2 |
| `VRE_2026Q1_TT99` | 22/27 = 0,815 | 0,120 | ok | 4 |
| `HNG_2025H1_TT200` | 18/26 = 0,692 | 0,250 | ok | 3 |
| `SBT_2025Q2_TT200` | 18/26 = 0,692 | **0,308** | **SAI** | 3 |
| `VHC_2025Q1_TT200` | 18/26 = 0,692 | 0,053 | ok | 0 |

**Tổng: 216/265 = 81,5% trường đúng · lỗi câm 24/240 = 10,0% · đơn vị đúng
8/10 · tài liệu đúng trọn vẹn 0/10.** Sau bản vá dấu `a0cd5ab`: 83,8% và 7,5%.

Nhịp chạy **17–33 phút một tài liệu**, phần lớn là bước dò mã số dòng bằng OCR
— 864 trên 1161 giây của tài liệu cuối, tức **74%**. Bộ nhớ dao động 1,4–4,7 GB
theo trang, **không** rò rỉ tuyến tính (ba lần báo động đều là báo động sai).

> **CẢNH BÁO CẤU HÌNH, phát hiện 28/08/2026.** Lượt chạy này chạy với
> `USE_OCR_FIRST=true` trong `.env`, trong khi docstring `router.py` nói nhánh
> OCR tắt mặc định. Một số giá trị có thể đến từ nhánh regex chứ không từ VLM.
> Xem mục 12 — cấu hình phải chốt trước khi chạy lại trọn bộ.

### 20.4 Phân bố chế độ lỗi — kết quả quan trọng nhất của lượt chạy

49 trường lệch, phân loại bằng script đối chiếu dự đoán với gold:

| Chế độ lỗi | Số trường | Nguồn gốc |
|---|---:|---|
| Bỏ trống | 25 | không đọc được — **vô hại**, hệ biết mình thất bại |
| **Đảo dấu** | **11** | quy tắc ngoại lệ guideline 3.3 chưa cài — **đã vá** |
| **Khác (toàn bộ của SBT)** | **10** | định vị nhầm bảng B02 — **CHƯA vá** |
| Nhầm ô | 2 | `row_shift` thật |
| Nhầm chữ số | 1 | lỗi OCR thật |

**Kết luận đáng giá nhất: 21 trong 24 lỗi câm là hai con bug, không phải giới
hạn của mô hình.** Chỉ còn **3 lỗi câm là lỗi thật** — hai ca nhầm ô, một ca
nhầm chữ số. **Tỷ lệ lỗi câm không quy giản được là 3/240 = 1,25%.**

**Hai chế độ trội đi theo hai nguyên nhân tách bạch:** *bỏ trống ↔ độ phân
giải* (DLG 100 dpi bỏ trống 3, lỗi câm 0; MWG 296 dpi bỏ trống 0 — ảnh xấu thì
hệ không đọc được và nó **biết** mình không đọc được), còn *đảo dấu ↔ lỗi cài
đặt*, không phụ thuộc dpi chút nào.

**Trường hay sai nhất:** `thue_tndn_hien_hanh` 9 lần, `thue_tndn_hoan_lai` 7,
`tai_san_sinh_hoc_ngan_han` 5 (đều bỏ trống), `anh_huong_ty_gia` 4 (đều bỏ
trống), `gia_von_hang_ban` 4. Chỗ hụt nằm ở **vài chỉ tiêu cụ thể**, không rải
đều.

**SBT và VHC là ca đối chứng tự nhiên đẹp nhất lượt chạy cho ra.** Cả hai hỏng
ở cùng một khâu — định vị bảng — mà kết cục ngược nhau:

- **SBT** không tìm đúng B02 → **điền số của bảng khác vào**, 8 lỗi câm, B01
  đúng sạch. Sáu trong tám trường có nhiều hơn đúng một chữ số so với gold.
  Giả thuyết dẫn đầu: hồ sơ 62 trang chứa **hai bộ báo cáo**, pipeline lấy B01
  từ bộ này và B02 từ bộ kia. **Chưa kiểm được** vì nhật ký chỉ ghi tóm tắt,
  không giữ text.
- **VHC** không tìm được B03 → **để trống**, 6 trường lưu chuyển tiền bỏ trống,
  không một lỗi câm nào từ B03.

Cùng một hỏng hóc, một bên **thú nhận**, một bên **bịa**. Đây là chế độ lỗi
**nguy hiểm nhất** lượt chạy lộ ra — lỗi **chọn nguồn**, xảy ra trước khi trích
xuất, và không đẳng thức nào bắt được vì bộ số kia **tự nó cũng cân**
(`residual = 0` tuyệt đối).

> **Phân bố lỗi thật KHÁC HẲN thứ đang bơm ở tầng XBRL:** 1 lỗi chữ số trên 49
> trường lệch. Chế độ trội là dấu, định vị bảng, và bỏ trống.
> `src/nham_chu_so.py` bơm lỗi theo ma trận nhầm chữ số, tức đang mô phỏng một
> thế giới không phải thế giới này. Tu chính đã ghi ở `PREREGISTRATION.md`.

### 20.4b Giải phẫu 16 lỗi câm CÒN LẠI — sau cả hai cơ chế, 28/08/2026

Sau `chuan_hoa_dau()` và tầng repair: **224/265 = 84,5% trường đúng, lỗi câm
16/240 = 6,7%**. Đếm lại bằng
`PYTHONPATH=src python src/eval/do_luat_dau.py`.

**Chúng dồn cục vào hai tài liệu, không rải đều:**

| doc_id | Lỗi câm | Đẳng thức lệch | Ràng buộc nói được gì |
|---|---:|---:|---|
| `SBT_2025Q2_TT200` | **8** | 2 | phát hiện được, chưa định vị được |
| `HNG_2025H1_TT200` | **5** | 1 | phát hiện được, chưa định vị được |
| `DGC`, `HPG` | 1 mỗi tài liệu | 1 | phát hiện được |
| `BMP_2026Q1_TT99` | 1 | **0** | **VÔ HÌNH** |
| 5 tài liệu còn lại | 0 | 0 | — |

**13 trong 16 nằm ở SBT và HNG.** Hai tài liệu này không hỏng vì mô hình đọc
kém — chúng hỏng ở khâu TRƯỚC khi đọc số.

#### SBT — lấy B02 của một bộ báo cáo khác, và bộ số ấy TỰ CÂN

Bằng chứng đanh nhất lượt chạy cho ra, đo được chứ không suy đoán: **7 trên 9
đẳng thức khớp residual = 0 TUYỆT ĐỐI trên bộ số sai**. Riêng đẳng thức
`Giá vốn + Lợi nhuận gộp = Doanh thu thuần` cân tới từng đồng với cả ba con số
đều sai — 12.105.315.641.553 − 11.082.990.821.520 = 1.022.324.820.033.

**Giả thuyết "Riêng vs Hợp nhất" đã BỊ BÁC, 28/08/2026.** File nguồn của SBT là
bản `Hopnhat`, và `da_kiem` của nó ghi rõ nhãn gold lấy từ *"BẢNG CÂN ĐỐI KẾ
TOÁN HỢP NHẤT"*, ký hiệu `B01a-DN/HN` — tức gold ĐÃ là bản hợp nhất, nên máy
không thể lấy nhầm sang bản riêng mà ra số LỚN HƠN.

**Bằng chứng chỉ sang hướng khác: nhầm CỘT.** Lấy hiệu (máy − gold) của từng ô
rồi kiểm xem hiệu ấy có tự thoả đẳng thức không:

| | Hiệu (máy − gold) |
|---|---:|
| Doanh thu thuần | 5.371.734.177.990 |
| Giá vốn hàng bán | 4.872.249.382.154 |
| Lợi nhuận gộp | 499.484.795.836 |

Ba hiệu này **tự cân đẳng thức `giá vốn + lãi gộp = doanh thu`, residual 0 tuyệt
đối**. Một hiệu tự cân nghĩa là bản thân nó là số liệu của một KỲ hợp lệ — đúng
chữ ký của ca đọc nhầm cột *luỹ kế* thay vì cột *quý*. SBT lại là tài liệu niên
độ lệch (năm tài chính kết thúc 30/6), nên bố cục cột của nó khác mọi tài liệu
còn lại của tập gold.

**Nhưng KHÔNG phải nhầm cột trọn bảng.** Xuống phía dưới B02 thì hiệu vỡ:
`ln_khac` hiệu bằng **0** (máy đọc đúng), `loi_nhuan_sau_thue` hiệu **âm**, và
hai đẳng thức còn lại lệch. Nên ít nhất có hai chuyện xảy ra cùng lúc, và chẩn
đoán hiện chỉ vững cho ba dòng đầu B02.

**Việc phải làm để dứt điểm:** mở PDF của SBT, xem B02 có mấy cột và nhãn cột là
gì. Rẻ, và không đoán thêm được nữa nếu không làm.

**Vì sao không ràng buộc nào cứu được:** chênh lệch nằm trọn trong không gian
null. Một bộ số hợp lệ của doanh nghiệp KHÁC vẫn là một bộ số hợp lệ. Đây
không phải giới hạn của thuật toán mà là giới hạn của thông tin, và
`tests/test_luat_dau.py::test_chon_nham_bang_KHONG_bat_duoc_va_do_la_gioi_han_that`
chốt nó lại để đừng ai hứa quá tay trong bài.

#### HNG — dấu nằm ở NHÃN DÒNG, không nằm ở con số

HNG lỗ. Báo cáo đổi tên dòng thành *"Lỗ thuần từ hoạt động kinh doanh"* rồi in
số **dương**; nhãn mang dấu, con số chỉ mang độ lớn. Người gán nhãn chép đúng
như in theo guideline mục 3.3, nên gold ghi `ln_thuan_hdkd = +154.594.725.000`
cho một khoản LỖ. Pipeline đọc dấu ngoặc/dấu trừ và ghi âm.

Ba "lỗi đảo dấu" của HNG vì thế **không phải lỗi đọc số** — chúng là bất đồng
về quy ước, và cả hai bên đều tự nhất quán: bộ gold cân mọi đẳng thức, bộ máy
cũng gần cân.

> **CÂU 14 — MỚI, cần người chủ trì quyết.** Cùng một chỉ tiêu
> `ln_thuan_hdkd` mang dấu ngược nhau giữa HNG và các tài liệu khác của tập
> gold, mà không khoá nào trong file gold khai ra chuyện đó. Mọi phân tích
> gộp qua tài liệu — kể cả bảng kết quả của bài — sẽ cộng một khoản lỗ vào
> một khoản lãi. Hai đường: *(a)* chuẩn hoá gold về quy ước "số âm là lỗ" và
> gán nhãn lại B02 của HNG; *(b)* giữ nguyên và thêm một khoá khai quy ước
> dấu cho từng tài liệu. Đường (a) mất tính "chép, đừng diễn giải"; đường (b)
> đẩy việc diễn giải xuống mọi nơi tiêu thụ dữ liệu.
>
> **Ràng buộc kế toán KHÔNG phân xử được câu này**, và đó là hệ quả trực tiếp
> của H0: hệ thuần nhất nên lật dấu TRỌN một hệ con nhất quán vẫn cân — cùng
> một lập luận `Aδ = (c−1)Ax* = 0`, với `c = −1`.

#### BMP — lỗi thật, nhưng nằm DƯỚI dung sai

`thue_tndn_hien_hanh`: máy đọc 71.249.**595**.744, gold 71.249.**959**.744 —
đảo hai chữ số. Sai **364.000 đồng**, mà `‖x‖ = 7,0 · 10¹²`, nên residual
tương đối là **5,2 · 10⁻⁸** — dưới `IDENTITY_TOLERANCE_RATIO = 10⁻⁷`. Mọi phép
kiểm báo ĐẠT.

**Đây là lần thứ HAI cùng một chế độ lỗi được ghi nhận** — lần đầu là mã 52
của `VNM_2026Q1_TT99` (mục 19.2), lệch 10.000 đồng trên một con số 48 tỷ. Cơ
chế: dung sai tính theo tỷ lệ trên chuẩn của CẢ vector, nên một sai số tuyệt
đối nhỏ ở một chỉ tiêu nhỏ luôn bị nuốt bởi độ lớn của tổng tài sản.

**Đừng chỉnh `IDENTITY_TOLERANCE_RATIO`** — chỉ thị của người dùng về hằng số
ngưỡng khi dữ liệu còn mỏng vẫn áp. Hướng đúng nếu về sau muốn đóng: dung sai
theo độ lớn của **từng đẳng thức** thay vì của cả vector. Đó là thay đổi thiết
kế phép đo, nên phải vào mục Sửa đổi của `PREREGISTRATION.md` trước.

#### Đọc lại con số 1,25% cho đúng

Mục 20.4 kết luận "lỗi câm không quy giản được là 3/240 = 1,25%". Hai cơ chế
đã thi công đưa 24 xuống 16, tức **chưa chạm tới 13 lỗi của SBT và HNG** —
đúng như dự đoán, vì cả hai đều không phải lỗi đọc số. Con số 1,25% vẫn là
đích, nhưng đường tới nó đi qua **khâu chọn nguồn** và **quy ước dấu**, không
đi qua bộ sửa lỗi.

### 20.5 Hai bản vá 27/08/2026 — tính chất phải giữ

Chẩn đoán, cơ chế và số đo trước/sau ở `CHANGELOG.md` 27/08/2026. Hai điều
ràng buộc việc sau:

> **(a) `chuan_hoa_dau()` CỐ Ý không giải đẳng thức `Mã 60 = Mã 50 − Mã 51 −
> Mã 52` để chọn dấu.** Giải nó thì mọi kết quả đều thoả nó, và phép đo H1 —
> so vi phạm ràng buộc với confidence — mất sạch nghĩa vì tín hiệu bị chính
> bước trích xuất làm phẳng. Chỉ dùng **chiều** của mã 50 so với mã 60; độ lớn
> vẫn tự do sai nên đẳng thức vẫn là phép kiểm độc lập. Có test khoá tính chất
> này (`tests/test_chuan_hoa_dau.py`) — **đừng hoàn thiện nó.** Hàm đặt trong
> `validate_result()` ngay **sau** bước ép kiểu, không đặt ở router: trước ép
> kiểu giá trị VLM còn có thể là chuỗi và hàm sẽ lặng lẽ không làm gì.

> **(b) Nới mép trên vùng cắt MỚI LÀ KIỂM HÌNH HỌC.** Dòng "Đơn vị tính" nay
> nằm trong ảnh đưa cho VLM, nhưng **nó có đọc ra đúng hay không thì phải chạy
> lại pipeline mới biết**. Đừng ghi vào bài rằng chỗ này đã sửa xong. Ngưỡng
> `TY_LE_NOI_TREN = 0,05` theo **tỷ lệ chiều cao trang**, không theo pixel cố
> định, vì tập gold trải 89,9–295,8 dpi; nới tới **đỉnh** của box gần nhất phía
> trên có chồng ngang với bảng.

Vì sao chỗ (b) nặng hơn mọi con số accuracy: với sai đơn vị toàn cục thì
`Aδ = (c−1)Ax* = 0`, tức **mọi đẳng thức kế toán đều mù với nó**. Bảng vẫn cân
hoàn hảo, mọi phép kiểm vẫn báo ĐẠT, trong khi mọi con số sai 1000 lần. Đây là
chế độ lỗi DUY NHẤT cả tầng ràng buộc không nhìn thấy.

### 20.6 Việc lượt chạy này lộ ra, CHƯA làm

1. **Chẩn đoán SBT** — **10 trong 24 lỗi câm nằm ở đây**, và nếu là lỗi chọn
   nguồn thì không đẳng thức nào bắt được. Cần mở PDF xem hồ sơ có mấy bộ báo
   cáo, và phân biệt "Riêng" với "Hợp nhất".
2. **Chạy lại để đo hiệu quả bản vá nới mép.** Rẻ nhất là `--chi BMP SBT`
   (~25 phút) rồi mới quyết chạy trọn bộ (~3,5 giờ). Xem bẫy 3 ở mục 20.2.
3. **H1 CHƯA CHẠY ĐƯỢC ở cấu hình hiện tại.** `n_samples=1, temperature=0.0`
   cho confidence 1,0 ở mọi trường, mà `FieldResult.khong_do()` ghi rõ 1,0 ở
   đó nghĩa là **không đo được**. Cột confidence hằng số thì phép so vô nghĩa.
   Bật `n_samples > 1` thì chi phí API nhân đúng k lần.
4. **Mới có MỘT model, và là bản `:free`** (`google/gemma-4-31b-it:free`).
   Proposal baseline 2 đòi **ít nhất ba** — một open-weight, một closed, một
   model tiếng Việt.
5. **Chế độ đầu-cuối chưa chạy.** Chỉ khác ở 5 tài liệu TT200, nên `--chi`
   trên đúng 5 mã đó là đủ.
6. **`VNM_2026Q1_TT99` thiếu PDF.** Hoặc bổ sung vào `data/bctc/`, hoặc rút
   nhãn khỏi `data/gold/`.

---

## Phụ lục A — MỐC 1: hồ sơ đối chiếu ma trận ràng buộc với Thông tư

**Mốc 1 đã đóng 23/08/2026.** Phần này giữ lại KẾT LUẬN và những cạm bẫy còn
sống; phần hướng dẫn thao tác đã bỏ vì việc đã làm xong. Quyết định bộ chỉ
tiêu và số đo của nó ở mục 10; chuyển sang kịch bản E ở mục 17.1.

Việc này do **người chủ trì** làm chứ không phải AI, theo `BUILD-SPEC` mục
0.5: sai một dấu trong ma trận ràng buộc thì kết quả identifiability sai mà
không có gì báo — code vẫn chạy, số vẫn ra, chỉ là sai.

### A.1 Vì sao ràng buộc bắt được lỗi nhưng thường không chỉ ra lỗi ở đâu

Một đẳng thức lệch cho biết CÓ lỗi, không cho biết lỗi nằm ở số hạng nào:
`TSNH + TSDH = TTS` lệch 800 đồng thì cả ba số đều có thể là thủ phạm, và
con số lệch không phân biệt được. Không phải thuật toán yếu — **thông tin để
phân biệt không tồn tại**, nên mọi thuật toán đều đâm vào cùng bức tường.

Thứ phá được thế bí là một chỉ tiêu nằm trong **hai** quan hệ: nó để lại dấu
vân tay khác — làm hỏng hai đẳng thức thay vì một.

> Một chỉ tiêu **định vị được** khi tập đẳng thức chứa nó khác với tập đẳng
> thức của mọi chỉ tiêu khác. Trong ngôn ngữ ma trận: cột của nó trong `A`
> khác 0 và không tỷ lệ với cột nào khác. `src/constraints.py` kiểm đúng vậy.

**Nhưng phân rã là một cái cối xay.** Cứu `tai_san_ngan_han` bằng cách phân
rã nó ra năm thành phần thì năm chỉ tiêu mới ấy lại chỉ nằm trong một đẳng
thức, cùng nhau. Cối xay không bao giờ hết lá — mà mỗi lá là chi phí gán nhãn
tay nhân với cả tập gold. Số đo (`python src/constraints_scenarios.py`):

| KB | Kịch bản | Chỉ tiêu | Đẳng thức | Định vị được |
|---|---|---:|---:|---:|
| A | Hiện tại | 11 | 3 | 1/11 (9%) |
| D | + phân rã Tài sản ngắn hạn | 19 | 7 | 5/19 (26%) |
| E | **+ quan hệ nối B01/B02/B03** | 26 | 11 | **13/26 (50%)** |

Phân rã A→D: thêm 8 chỉ tiêu mua được 4 — tỷ lệ 0,5. Nối chéo D→E: thêm 7
mua được 8 — tỷ lệ 1,1. **Gấp đôi hiệu suất trên mỗi đồng chi phí gán nhãn**,
vì nối chéo gắn đẳng thức thứ hai vào chỉ tiêu ĐÃ CÓ thay vì mở tầng lá mới.

**Một chỉ tiêu nằm ngoài tầm ở MỌI kịch bản: `hang_ton_kho`.** Đáng nhớ vì
đó đúng là chỉ tiêu đã có lỗi đọc thật trên báo cáo VNM — alias "Hàng tồn
kho" khớp trúng dòng "Dự phòng giảm giá hàng tồn kho", ra giá trị nhỏ hơn
thật khoảng nghìn lần nhưng hợp lệ về hình thức. Tức **ràng buộc kế toán
chứng minh được là không bao giờ bắt được lỗi đó**; chỉ mỏ neo đơn vị tính
và việc đọc lại crop mới bắt được. Đây là ví dụ có thật để đưa vào bài, và
là lập luận bảo vệ đóng góp cốt lõi.

### A.2 Nguồn văn bản

Trích dẫn trong bài thì dùng Công báo Chính phủ:

- TT200/2014/TT-BTC: https://congbao.chinhphu.vn/van-ban/thong-tu-so-200-2014-tt-btc-6697.htm
- TT99/2025/TT-BTC (hiệu lực 01/01/2026): https://congbao.chinhphu.vn/van-ban/thong-tu-so-99-2025-tt-btc-46529.htm

Bản đã tải nằm ở `data/legal/` (gitignore). Trích text bằng `pdftotext
-layout` và `antiword`; lệnh ở mục 15. Công báo tách TT99 thành 10 số —
**đừng bỏ số `1577 + 1578`**: nó không có đẳng thức viết bằng lời nên dễ
tưởng là vô dụng, nhưng nó chính là Phụ lục IV Mục 1, biểu mẫu, và biểu mẫu
in sẵn đẳng thức ngay trong tên chỉ tiêu: `TỔNG CỘNG TÀI SẢN (280 = 100 + 200)`.

### A.3 Kết quả đối chiếu

**Mã số dòng: 11/11 khớp văn bản.** Nhưng khớp không có nghĩa là an toàn, vì
hai mã số **đổi nghĩa** giữa hai chuẩn, và cả hai là nguồn lỗi câm:

| Mã | TT200 | TT99 | Vì sao nguy hiểm |
|---|---|---|---|
| **270** | Tổng cộng tài sản | **Tài sản dài hạn khác** | Tra nhầm bảng mã thì đọc ra con số **hợp lệ** của một chỉ tiêu khác hẳn. Không quy tắc kiểm nào bắt được |
| **142** | Hao mòn luỹ kế nhóm hàng tồn kho | **Dự phòng giảm giá hàng tồn kho** (TT200 để ở 149) | Cùng loại lỗi, quy mô nhỏ hơn |

Đó là lý do `standard` là tham số **bắt buộc** của `extract_field_by_code()`,
không có giá trị mặc định.

**Ba đẳng thức gốc đều đúng ở cả hai chuẩn.** Một chi tiết đáng tiền: đẳng
thức `nợ + vốn = tổng tài sản` **không có trong văn bản dưới dạng một dòng**.
Văn bản viết `Mã số 440 = 300 + 400`, rồi viết RIÊNG ở khối kẻ khung rằng
`Tổng cộng Tài sản (270) = Tổng cộng Nguồn vốn (440)`. Quan hệ thật là **hai
bước**, và code gộp làm một — gộp lại là vứt đi một ràng buộc mà văn bản đã
khai báo tách bạch, cùng một con số đọc được ngay trên giấy.

**Liên kết chéo B03 → B01 có thật và được khai báo tường minh.** TT200 Điều
114: *"Chỉ tiêu này bằng số Tổng cộng của Mã số 50, 60 và 61 và **bằng chỉ
tiêu Mã số 110 trên Bảng cân đối kế toán kỳ đó**"*. TT99 y hệt. Ghép lại:

```
B01.110 (cuối kỳ) = B01.110 (đầu kỳ) + B03.50 + B03.61
```

Nó nối bảng cân đối kỳ này với kỳ trước — trả lời proposal mục 6.1(d): cột
kỳ trước **có** ràng buộc thật nối vào. Nhưng nó chỉ trả tiền khi `B01.110`
đã nằm sẵn trong một đẳng thức khác, tức phân rã Tài sản ngắn hạn (Điều 112).

**Hai chuẩn KHÔNG đẳng cấu, dù sáu trên bảy đẳng thức giống hệt.** Phân rã
tài sản ngắn hạn là `100 = 110+120+130+140+150` ở TT200 nhưng thêm `+160` ở
TT99, vì TT99 chèn **Tài sản sinh học ngắn hạn** vào mã 150. Nên TT200 có 26
chỉ tiêu còn TT99 có 27, và ma trận của chúng khác chiều.

Hệ quả cho bài, và phải viết đúng như vậy: distribution shift giữa hai chuẩn
nằm chủ yếu ở **tầng nhận diện và tra cứu**, không ở tầng ràng buộc. Ablation
8 (transfer TT200 → TT99) vì thế kiểm chủ yếu việc hệ có nhận đúng chuẩn rồi
tra đúng bảng mã hay không — phát biểu hẹp hơn bản đăng ký ban đầu ngụ ý.

### A.4 `FORM_MARKERS` đã sai — đã sửa `023321c`

`src/fields_config.py` từng ghi "TT200 dùng `Mẫu số B 01 - DN`, TT99 dùng
`B 01a - DN`", và marker TT200 mang `(?!\s*a)` để khỏi khớp nhầm.

Văn bản nói ngược: hậu tố là **kỳ báo cáo**, không phải Thông tư. `B01-DN`
là báo cáo năm, `B01a-DN` là giữa niên độ dạng đầy đủ (tức quý), `B01b-DN`
là dạng tóm lược; cả hai Thông tư dùng đủ ba ký hiệu trên **cùng bộ mã số**.

**Hậu quả cụ thể:** marker TT200 không khớp trang `B01a-DN` — đúng loại tài
liệu dự án xử lý, kể cả báo cáo VNM mẫu. Marker trượt thì
`extract_field_by_code()` trả `None`, tức **đường dự phòng theo mã số tắt
hẳn, im lặng** — đúng đường sinh ra để cứu khi OCR làm hỏng tên chỉ tiêu.

Điểm sáng: `detect_standard()` không dùng `FORM_MARKERS` mà dùng
`STANDARD_MARKERS` theo TÊN báo cáo, và cái đó đúng. Nhận diện CHUẨN không
hỏng; chỉ nhận diện MẪU BIỂU hỏng. Vì chuẩn đã xác định trước và
`extract_field_by_code()` nhận `standard` bắt buộc, `FORM_MARKERS` không cần
phân biệt chuẩn chút nào — toàn bộ cơ chế `(?!\s*a)` giải một bài toán mà
chỗ khác đã giải rồi.

> **Cảnh báo còn sống:** `ANNOTATION-GUIDELINE.md` mục 3.7 vẫn xếp ký hiệu
> `B 01a - DN` là dấu hiệu TT99 — cùng lỗi này, chưa sửa, và nay đã chặn hai
> tài liệu thật. Xem Câu 11 ở mục 0.

---

## Phụ lục B — Phương án C: quyết định, ràng buộc, và bước D còn lại

Phương án C phân biệt *dòng vắng mặt trên biểu mẫu* với *dòng đọc hỏng*, để
`validate_result()` thôi bỏ qua cả đẳng thức khi một thành phần là `None`.
Quyết định của người dùng 24/08/2026, thi công xong bước A–C; **bước D chưa
làm**. Số đo và hiệu quả ở `CHANGELOG.md` mục 24/08/2026.

### Hai lựa chọn con, và lý do — cả hai còn ràng buộc bước D

1. **Phân biệt bằng cách dò trên OCR text, không hỏi thẳng model.** Để model
   tự khai "dòng này không có" là một phán đoán của model, và phán đoán sai
   sẽ lặng lẽ thành số 0 đi vào đẳng thức — đúng chỗ nhạy cảm nhất với việc
   bịa. Dò trên text thì tất định, kiểm lại được, truy được về một chỗ cụ thể
   trên tài liệu.
2. **Số 0 của dòng vắng mặt ghi vào cả `data` đầu ra**, kèm khoá trạng thái
   tường minh. Guideline mục 3.4 buộc gold ghi `0`, mà `eval/metrics.py` quy
   định `None` chỉ khớp `None` — pipeline trả `None` thì `field_accuracy` và
   `document_fully_correct` bị trừ điểm oan một cách hệ thống.

### Hợp đồng của probe — ba trạng thái, đừng gộp

- `co_gia_tri` — đọc được số.
- `vang_mat` — probe khẳng định biểu mẫu **không có** dòng đó → giá trị `0`.
- `khong_doc_duoc` — probe thấy dòng nhưng không ra số, hoặc probe không chạy
  được → `None`, nghĩa là *chưa biết*.

Ca thứ ba phải giữ `None`; nhập nó vào `vang_mat` là quay lại đúng cái nhập
nhằng mà phương án C sinh ra để gỡ.

### Vì sao probe rẻ được — hai tính chất thiết kế dựa vào

- **Dò theo MÃ SỐ DÒNG, không theo tên chỉ tiêu.** Mã số là chữ số, và
  EasyOCR đạt 0,999 Levenshtein trên ô số. Chỗ nó yếu là tên tiếng Việt có
  dấu — thứ probe không dùng tới.
- **Probe chạy một lần cho mỗi MẪU BIỂU, không phải mỗi trang**, và tái dùng
  vùng bảng đã cắt sẵn cho VLM nên không tốn thêm convert PDF hay YOLO.

### Bước D — nhận diện chuẩn mẫu biểu, CHƯA làm

`chon_chuan()` vẫn chỉ có hai nguồn `tham_so` và `mac_dinh`, nên không ai
truyền `standard` thì mọi tài liệu bị xử như **TT99** — đúng vì lùi mặc định
chứ không vì nhận diện. Với báo cáo TT200 thật thì prompt dùng bảng mã TT99
(mã 280 thay vì 270) và bộ đẳng thức TT99. Việc lùi nay có kêu ra log và ghi
vào `meta["standard_nguon"]`.

**Vướng mắc 1 — thứ tự.** Chuẩn phải biết **trước** khi dựng prompt, còn
probe chạy **sau** khi trích xuất. Cách gỡ: kéo vài trang đầu ra khỏi
generator, OCR, gọi `detect_standard()`, rồi mới trích xuất. `cached_pages`
và `_remaining_pages()` đã hỗ trợ đúng kiểu tiêu thụ đó. Nên thêm cache text
theo số trang để probe khỏi OCR lại chính những trang ấy.

**Vướng mắc 2 — đã đo, và nó bác bỏ cách làm hiển nhiên.** Dấu hiệu duy nhất
`detect_standard()` dùng là TÊN BÁO CÁO ở tiêu đề trang, nhưng
`iter_table_regions()` chỉ yield vùng bảng đã cắt. Đo trên 12 trang đầu báo
cáo VNM (`data/output/tieu_de_trong_vung_cat.md`): trang mang bảng 2/12,
trang có TÊN báo cáo lọt vào vùng cắt **0/2**. Cả hai lần `detect_standard()`
kết luận được đều **nhờ SỐ HIỆU thông tư** — dấu hiệu khác hẳn, chỉ có trên
báo cáo còn nhắc văn bản ban hành, và mẫu `99\s*/\s*2025` cho `\s*` nuốt cả
xuống dòng nên còn khớp oan được.

Phép đo ấy trên **một** tài liệu: đủ để loại một hướng sai, chưa đủ để chốt
hướng đúng. Nay có 10 tài liệu ở `data/bctc/` nên **đo lại trên nhiều công ty
là việc rẻ và phải làm trước khi chọn hướng**.

Ba hướng, chưa chọn:

1. **Yield kèm ảnh cả trang** rồi OCR cả trang chỉ để nhận diện. Đúng đắn
   nhất, nhưng đắt hơn và EasyOCR chạy CPU.
2. **Nới `PADDING` riêng cho bước nhận diện.** Rẻ hơn, nhưng thành một hằng
   số nữa cần hiệu chỉnh mà chưa có dữ liệu để hiệu chỉnh. *(Lưu ý: bản vá
   `05d00d0` đã nới mép trên vùng cắt theo tỷ lệ cho việc khác — đọc lại
   `tran_noi_tren()` trước khi thêm hằng số mới.)*
3. **Nhận diện bằng bộ MÃ SỐ thay vì bằng tên.** Mã số là chữ số, đúng chỗ
   EasyOCR mạnh, và nằm trong vùng bảng. Nhưng mã 270 tồn tại ở CẢ HAI chuẩn
   với nghĩa khác nhau, nên dấu hiệu phải là *sự có mặt của mã 280*. Đối
   chiếu lại Phụ lục IV trước khi tin.

Dù chọn hướng nào cũng giữ nguyên tắc của `detect_standard()`: không đủ dấu
hiệu thì trả `None` và lùi mặc định **có ghi lại**, không đoán bừa. Và thêm
nguồn `nhan_dien` vào tập đóng của `chon_chuan()`.

**Cạm bẫy còn nguyên:** `extract_field_by_code()` trả `None` trần cho BA
nguyên nhân khác nhau (field không có trong bảng mã của chuẩn; không thấy
marker mẫu biểu; không khớp được số). Muốn phân biệt thì phải cho nó nói ra
lý do, không đọc được từ giá trị trả về.
