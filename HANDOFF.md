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
| Quy ước bắt buộc, bẫy môi trường, bảng định tuyến | `CLAUDE.md` (máy tự nạp mỗi phiên) |
| Hồ sơ các phần đã đóng, giữ nguyên số mục | `docs/lich-su/HANDOFF-da-dong.md` |
| Cách chấm tập gold, cạm bẫy, mốc so sánh | kỹ năng `chay-tap-gold` (`.claude/skills/`) |
| Nhật ký commit | `git log --oneline` |

- **Nhánh:** `research` (tách từ `main` tại `4216291`). **`main` KHÔNG BAO GIỜ
  MERGE** — chỉ thị của người dùng 24/08/2026. Hệ quả: CI chỉ chạy trên `main`
  và trên pull request, nên **CI thực tế không bao giờ chạy** — mọi việc kiểm
  phải làm tại chỗ. Muốn CI có ích thì thêm `research` vào phần trigger của
  `.github/workflows/ci.yml`, **không phải merge**.
- **Trạng thái commit:** chạy `git log --oneline -1` và `git status -sb`. Quy
  ước: push sau mỗi commit, nên `research` khớp `origin/research` là bình thường.
- **Kiểm:** `python -m ruff check src tests` rồi `python -m pytest -q` (~90 giây).
  Số test không chép ở đây: một con số chép tay là một con số sẽ cũ đi mà không
  ai biết — bản trước ghi 510 trong khi thực tế đã hơn 600.
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

Đọc theo nhu cầu, **không đọc tuần tự** — file này không còn được thiết kế để
đọc trọn. Bảng định tuyến theo VIỆC ở `CLAUDE.md`; bảng dưới đây là mục lục
theo NỘI DUNG, dùng khi đã biết mình cần gì.

| | Mục | Dùng khi |
|---|---|---|
| **0** | Câu hỏi đang chờ người chủ trì | luôn đọc trước tiên |
| 2 | Bối cảnh | phiên đầu tiên |
| 3–5 | Hash còn được nhắc, bẫy đã gặp, các phần đã đóng | tra khi đụng vào một phần cụ thể |
| 11 | Chỗ đã đi khác `BUILD-SPEC.md`, có chủ đích | trước khi "sửa lại cho đúng đặc tả" |
| **12** | Chưa làm, và **hai quyết định đang treo** | chọn việc |
| 13 | **MỐC 3 — chưa đóng**, trần trên của bộ giải liên tục | đọc bảng kết quả |
| 15 | Lệnh hay dùng | cần một lệnh không có trong `CLAUDE.md` |
| **16** | **Bước kế tiếp** | chọn việc |
| 17.2 | Quy mô tập gold — chưa cập nhật tài liệu | tránh làm lại việc đã quyết |
| 19.3 | **Việc còn lại của tầng gold**, theo thứ tự chặn nhau | việc đang làm |
| 20.6 · 20.8 | **Việc lượt chạy lộ ra, chưa làm** · đơn vị theo bảng | việc đang làm |
| B | Phương án C, **bước D chưa làm** | làm tiếp nhận diện chuẩn |

**Mục 1, 10, 14, 18, 19.1–19.2, 19.4–19.5, 20.1–20.5, 20.7, Phụ lục A và ba mục
đầu của Phụ lục B không còn nội dung ở đây** — mỗi chỗ để lại một dòng trỏ. Quy
ước bắt buộc và bẫy môi trường sang `CLAUDE.md`; phần còn lại sang
`docs/lich-su/HANDOFF-da-dong.md`, **giữ nguyên văn và nguyên số mục** nên mọi
tham chiếu cũ vẫn tra được, chỉ đổi file.

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

> **Đã thay bằng bảng định tuyến trong `CLAUDE.md`** — máy tự nạp file đó
> mỗi phiên, nên một danh sách "đọc gì trước" nằm ở đây thì đã muộn: muốn
> đọc được nó thì phải mở đúng file mà nó định hướng dẫn cách mở.
>
> Bảng ấy trả lời theo VIỆC SẮP LÀM chứ không theo thứ tự file, nên nó cắt
> được cả phần không cần đọc chứ không chỉ rút ngắn phần cần đọc.

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

> **Đã chuyển sang `docs/lich-su/HANDOFF-da-dong.md`, giữ nguyên văn và
> nguyên số mục.** Gồm: định luật rút ra quyết định hướng đi của H0, cái
> bẫy đọc bảng kịch bản, và hai kết luận đã bị bác bỏ bằng số đo — đừng
> khôi phục. **Đọc trước khi dựng bảng cho paper hoặc trước khi đụng vào
> ma trận ràng buộc.**

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

> **Đã chuyển sang `CLAUDE.md`**, cùng danh sách bẫy môi trường. Lý do là
> chính nội dung của nó: quy ước phải có hiệu lực từ dòng code đầu tiên của
> phiên, mà `CLAUDE.md` là file duy nhất máy tự nạp trước khi phiên bắt đầu.
> Giữ bản sao thứ hai ở đây thì hai bản sẽ lệch nhau, đúng cái lỗi mà luật
> "mỗi sự thật một nhà" sinh ra để chặn.

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

> **17.1 (bộ chỉ tiêu chuyển sang kịch bản E, ĐÃ LÀM 25/08/2026 `f1c2738`)
> đã chuyển sang `docs/lich-su/HANDOFF-da-dong.md`,** giữ nguyên văn.

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

> **Đã chuyển sang `docs/lich-su/HANDOFF-da-dong.md`, giữ nguyên văn.**
> Gồm cả danh sách related work đã tra 24/08/2026 — mở ra khi viết phần
> liên quan hoặc khi cần đối chiếu đối thủ, không cần ở phiên thường.

## 19. Tầng gold — công cụ, trình tự, nguồn tài liệu, độ phân giải

Hiện trạng của tầng gold. **Lý do và số đo của từng thay đổi ở `CHANGELOG.md`
(26/08/2026)**; mục này giữ cách dùng, ràng buộc, và việc còn lại.

> **19.1 (công cụ gán nhãn `src/gan_nhan/`) và 19.2 (`VNM_2026Q1_TT99` —
> tài liệu gold đầu tiên và ca dị thường) đã chuyển sang
> `docs/lich-su/HANDOFF-da-dong.md`,** giữ nguyên văn và nguyên số mục.

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

> **19.4 (nguồn tài liệu và 10 tài liệu đầu) và 19.5 (độ phân giải bản
> quét — cách đo và cạm bẫy) đã chuyển sang
> `docs/lich-su/HANDOFF-da-dong.md`,** giữ nguyên văn và nguyên số mục.
> Độ phân giải là trục phân nhóm Stress thứ ba, tra ở đó khi dựng bảng.

## 20. Chấm pipeline trên tập gold — số thật đầu tiên, 26–27/08/2026

Trước mục này, **mọi con số chất lượng của dự án đều lấy trên tầng XBRL Mỹ
hoặc trên đúng một báo cáo VNM**. Đây là chỗ đầu tiên pipeline bị chấm trên
bộ tài liệu Việt Nam có nhãn tay. **Số đo trước/sau của hai bản vá kèm theo
nằm ở `CHANGELOG.md` mục 27/08/2026** — mục này giữ cách chạy, cạm bẫy, và
những gì chưa làm.

> **20.1 tới 20.5 đã chuyển sang `docs/lich-su/HANDOFF-da-dong.md`,** giữ
> nguyên văn và nguyên số mục — nên tham chiếu dạng "mục 20.4b" ở các file
> khác vẫn tra được. Gồm: công cụ chấm, ba cạm bẫy đã trả giá, kết quả
> 27/08, phân bố chế độ lỗi, giải phẫu 16 lỗi câm, hai bản vá 27/08.
>
> **Cách chạy đã đóng thành kỹ năng `chay-tap-gold`** (`.claude/skills/`) —
> dùng cái đó thay vì đọc lại 20.1–20.2.

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

> **20.7 (lượt chạy 30/08/2026, BẬT tầng repair) đã chuyển sang
> `docs/lich-su/HANDOFF-da-dong.md`,** giữ nguyên văn. Bài học còn hiệu
> lực: **lượt chạy bật một cơ chế mới mà không lưu certificate của cơ chế
> đó thì cho ra số không quy được về nguyên nhân**, và cái giá là chạy lại.

---

### 20.8 Đơn vị tính buộc theo BẢNG — thi công và chạy lại HNG, 31/08/2026

**Tiền đề "mỗi tài liệu một đơn vị tính" đã bị bác bỏ trên hồ sơ thật.**
`HNG_2025H1_TT200` là công văn giải trình gửi HNX kèm BCTC soát xét bán niên:
trang 1 khai `ĐVT: tỷ đồng` cho một bảng hai dòng, các trang sau là BCTC khai
`Ngàn VND`. Pipeline cũ đối xử với đơn vị như một chỉ tiêu bình thường — vùng
đầu tiên đọc được thì chốt cho cả tài liệu và không bao giờ đọc lại — nên công
văn trang 1 thắng bảng cân đối trang 10.

**Mọi chữ số đọc ra đều đúng tuyệt đối; 24/26 ô sai đúng 1e6 lần.** Hai ô đúng
ở lượt 30/08 là hai ô bằng `0`, tức hai ô bất biến với phép nhân. Đây là ca
sách giáo khoa của mệnh đề `Aδ = (c−1)Ax* = 0`.

**Mỏ neo biên độ lớn có báo nhưng KHÔNG phân xử được.** Với tổng tài sản thô
`18.281.308.818`, `×1e9` cho `1,8e19` (ngoài biên, bắt được) nhưng cả `×1e3`
(`1,8e13`) lẫn `×1` (`1,8e10`) đều nằm trong `[1e10; 1e15]`. Mỏ neo thu bốn ứng
viên xuống hai — nó là **bộ lọc, không phải bộ sửa**. Đừng trông vào nó để tự
chữa ca sai đơn vị.

**Và không hệ số toàn cục nào ĐÚNG được cho tài liệu này.** `loi_nhuan_sau_thue`
được đọc ra từ đúng bảng trang 1, nên chọn `nghìn đồng` sẽ làm ô đó sai 1e6 lần
theo chiều ngược lại. Đó là lập luận quyết định: hệ số phải buộc theo **bảng**
đã sinh ra con số.

#### Cơ chế (`e28b9db`, `b35fdd7`, `fed96af`)

- `extract_vlm` bỏ phiếu đơn vị ở **mọi** vùng. **Đọc được thắng kế thừa**; chỉ
  vùng không tự khai mới lấy đơn vị của vùng trước. Không mua thêm lời gọi VLM
  nào — prompt vốn đã bắt model trả `don_vi_tinh` cho mọi vùng, bản trước chỉ
  vứt nó đi từ vùng thứ hai.
- Ngưỡng quá bán (`NGUONG_DON_VI_VUNG`) chặn ghi đè bằng phiếu yếu. **Ở
  `n_samples=1` nó không có tác dụng** — đừng đọc `0,5` như tham số đã hiệu chỉnh.
- `validate_result(..., he_so_theo_truong)` quy đổi theo từng ô; mỏ neo biên độ
  lớn gác theo hệ số đã dùng cho **chính** `tong_tai_san`.
- Kết luận mức tài liệu = hệ số áp cho **đa số** chỉ tiêu. Định nghĩa này đổi vì
  gold chỉ có một `unit_multiplier`/tài liệu; lấy vùng đầu tiên sẽ báo sai đơn vị
  trong khi 25/26 con số đã quy đổi đúng.
- `meta["don_vi_theo_vung"]` là certificate: mỗi vùng khai đọc ra gì, tin bao
  nhiêu, áp hệ số nào, nguồn là `doc_duoc` / `ke_thua` / `chua_biet`.

**KHÔNG sao chép ba ràng buộc của `ky_hieu_mau.py`** dù khuôn mẫu trông giống
hệt. Ký hiệu mẫu thật sự thuần nhất trong một hồ sơ nên ở đó "chốt một lần" là
đúng và "vùng sau khác vùng trước" là dấu hiệu hỏng; đơn vị tính thì không, nên
cùng một sự kiện lại là chuyện bình thường và phải được phép ghi đè.

**Một lỗi đã sửa trước khi chạy (`fed96af`).** Nhánh VLM đọc được một chỉ tiêu
không có nghĩa là giá trị cuối cùng đến từ đó: với `USE_OCR_FIRST=true`,
`run_vlm()` chỉ ghi đè khi ô còn trống hoặc validate đã báo warning. Dùng thẳng
bản đồ hệ số thì con số của OCR bị nhân bằng hệ số của một vùng nó chưa từng
được đọc ra — bịa xuất xứ, và bịa theo kiểu vẫn ra một con số hợp lệ nên không
gì báo. Lọc bằng `provenance`.

#### Lượt chạy HNG 31/08/2026

Chế độ `--chuan-tu-gold --chi HNG`, `BAT_TANG_REPAIR=true`, `USE_OCR_FIRST=true`,
`n_samples=1`, `temperature=0.0`, model `google/gemma-4-31b-it:free`. Kết quả:
`data/output/tap_gold_chuan_tu_gold_HNG_2026-08-31.json`.

| | 30/08 | 31/08 |
|---|---:|---:|
| Trường đúng | 2/26 = 0,077 | **21/26 = 0,808** |
| Lỗi câm | 24/26 | **5/26** |
| Hệ số đơn vị | ✗ (1e9) | **✓ (1e3)** |
| Số cảnh báo | 2 | 1 |

Certificate: **18 vùng, 8 đọc được đơn vị, 10 kế thừa.** Trang 1 vùng 0 đọc
`tỷ đồng`; trang 10, 11, 12, 13, 14, 15, 17 đọc `Ngàn VND`. Hệ số theo trường:
25 ô mang `1000`, một ô (`loi_nhuan_sau_thue`) mang `1e9`. Đúng hình dạng đã
dự đoán.

#### Năm ô còn sai — KHÔNG ô nào do đơn vị

| Chỉ tiêu | Dự đoán | Gold |
|---|---:|---:|
| `ln_thuan_hdkd` | −154.594.725.000 | +154.594.725.000 |
| `ln_khac` | −103.872.097.000 | +103.872.097.000 |
| `loi_nhuan_truoc_thue` | −258.466.822.000 | +258.466.822.000 |
| `loi_nhuan_sau_thue` | −258.900.000.000 | +258.898.322.000 |
| `thue_tndn_hien_hanh` | 233.893.000 | 0 |

**Bốn ô đầu chỉ lệch DẤU** — đúng Câu 14, quy ước dấu ngược của HNG, và Câu 14
vẫn đang chờ người chủ trì. Riêng `loi_nhuan_sau_thue` lệch cả độ lớn 0,00065%,
nằm sâu trong biên 0,1%, nên nếu Câu 14 được giải thì ô này tự đúng.

**Ô thứ năm là bất đồng THẬT, chưa lý giải được.** Gold ghi `thue_tndn_hien_hanh
= 0`, pipeline đọc `233.893.000`. Hoặc gold bỏ sót một dòng có số, hoặc pipeline
bắt trúng một con số của dòng khác. **Phải mở PDF kiểm bằng mắt trước khi kết
luận bên nào sai** — đừng sửa gold theo pipeline.

#### Chỗ lượt chạy này KHÔNG kết luận được

**Mới chạy MỘT tài liệu, nên chưa biết cơ chế có làm hỏng 9 tài liệu kia
không.** Buộc đơn vị theo bảng mở ra một chế độ lỗi mới: trước đây cả tài liệu
chỉ có một lần đọc đơn vị có thể sai, giờ mỗi bảng là một cơ hội, và một đơn vị
bịa trên trang tiếp nối làm hỏng trọn bảng đó mà không đẳng thức nào bắt được.
Chín tài liệu kia đều khai `VND` (×1) và đều đúng đơn vị ở lượt 30/08, nên
chúng là phép thử hồi quy đúng nghĩa.

Nếu chúng không đổi thì gộp sẽ là **232/265 = 0,875** so với 0,804 — nhưng đó
là **phép ngoại suy, chưa phải số đo**. Việc kế tiếp: chạy trọn bộ 10 tài liệu,
và **sao lưu `tap_gold_chuan_tu_gold.json` trước khi chạy** (bẫy 3, mục 20.2).

> **File `tap_gold_chuan_tu_gold.json` hiện đang giữ kết quả của ĐÚNG MỘT tài
> liệu** vì lượt `--chi HNG` này. Bản 10 tài liệu của lượt 30/08 vẫn còn ở
> `..._2026-08-30.json`.

## Phụ lục A — MỐC 1: hồ sơ đối chiếu ma trận ràng buộc với Thông tư

> **Đã chuyển sang `docs/lich-su/HANDOFF-da-dong.md`, giữ nguyên văn và
> nguyên số mục A.1–A.4.** Đọc A.1 trước khi tin rằng ràng buộc kế toán
> chỉ ra được lỗi nằm ở đâu — nó bắt được lỗi nhưng thường không chỉ ra
> được ô nào, và đó là tiền đề của cả nghiên cứu.

## Phụ lục B — Phương án C: quyết định, ràng buộc, và bước D còn lại

Phương án C phân biệt *dòng vắng mặt trên biểu mẫu* với *dòng đọc hỏng*, để
`validate_result()` thôi bỏ qua cả đẳng thức khi một thành phần là `None`.
Quyết định của người dùng 24/08/2026, thi công xong bước A–C; **bước D chưa
làm**. Số đo và hiệu quả ở `CHANGELOG.md` mục 24/08/2026.

> **Ba mục đầu của phụ lục này — hai lựa chọn con, hợp đồng ba trạng thái
> của probe, và vì sao probe rẻ được — đã chuyển sang
> `docs/lich-su/HANDOFF-da-dong.md`.** Hợp đồng ba trạng thái là ràng buộc
> còn hiệu lực: **đừng gộp chúng lại.** Bước D bên dưới vẫn CHƯA làm.

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
