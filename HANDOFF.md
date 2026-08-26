# Bàn giao — hạ tầng nghiên cứu ViFinKIE

Viết để một phiên Claude khác đọc và làm tiếp mà **không cần hỏi lại gì**.
Mọi tham chiếu đều là đường dẫn file hoặc commit hash.

- **Nhánh:** `research` (tách từ `main` tại `4216291`)
- **Commit gần nhất:** cố ý KHÔNG ghi hash ở đây — dòng này đã cũ đi ba lần
  chỉ trong một ngày, vì chính commit cập nhật nó lại thành commit mới nhất.
  Chạy `git log --oneline -1` và `git status -sb`. Quy ước: **push sau mỗi
  commit**, nên `research` khớp `origin/research` là trạng thái bình thường.
- **Test:** **484 xanh / 0 đỏ**, chạy hết khoảng 50 giây.
  `ruff check src tests chay_gan_nhan.py` sạch.
- **Bộ chỉ tiêu:** **27 với TT99, 26 với TT200; 9 đẳng thức** — kịch bản E,
  thi công 25/08/2026 (`f1c2738`). MỐC 1 đã đóng.
- **`main`:** **KHÔNG BAO GIỜ MERGE** — chỉ thị của người dùng, 24/08/2026.
  `research` đi trước 56 commit và cứ để vậy. Hệ quả: CI hiện chỉ chạy trên
  `main` và trên pull request, nên **CI thực tế không bao giờ chạy** — mọi
  việc kiểm phải làm tại chỗ. Muốn CI có ích thì thêm `research` vào phần
  trigger của `.github/workflows/ci.yml`, KHÔNG phải merge.
- **Tập gold:** **11 / khoảng 100** tài liệu đã gán nhãn — trọn cả **10 tài
  liệu của danh mục đầu** (mục 19.6) cộng `VNM_2026Q1_TT99` vốn có trước danh
  mục. Công cụ ở `src/gan_nhan/` — xem mục 19. **Chỉ 8 trong 11 có đồng hồ
  chạy thật** (`trang_thai_dong_ho` bằng `da_do`), nên còn thiếu **2 tài liệu**
  nữa mới chốt được số phút cho giao thức trần người — xem mục 19.4 bước 2.
- **Cập nhật:** 26/08/2026 (lần 3) — cả 10 tài liệu của danh mục đầu đã gán
  nhãn xong (mục 19.6), nên các con số đếm ở khối này và ở mục 0 được đồng bộ
  lại theo `data/gold/`. **Câu 10 và Câu 11 đã đóng**: nhóm Stress thứ ba đo
  bằng độ phân giải bản quét ghi làm biến liên tục (mục 19.7), và ký hiệu mẫu
  thôi là dấu hiệu nhận diện chuẩn.

---

## Mục lục

Đọc theo nhu cầu, không đọc tuần tự. **Cần gấp:** mục 0 (câu hỏi đang chờ),
mục 16 (bước kế tiếp), mục 15 (lệnh hay dùng).

| | Mục | Dùng khi |
|---|---|---|
| **0** | Câu hỏi đang chờ người chủ trì | luôn đọc trước tiên |
| 1–2 | Đọc gì trước · Bối cảnh | phiên đầu tiên |
| 3–9 | Nhật ký thi công, bẫy đã gặp, các phần A–F | tra khi đụng vào một phần cụ thể |
| 10 | **MỐC 1 — đã đóng**, bộ chỉ tiêu | cần biết vì sao bộ chỉ tiêu là 27/26 |
| 11 | Chỗ đã đi khác `BUILD-SPEC.md`, có chủ đích | trước khi "sửa lại cho đúng đặc tả" |
| 12 | Chưa làm, theo thứ tự phụ thuộc | chọn việc |
| 13 | **MỐC 3 — chưa đóng**, kết quả ở 13c | đọc bảng kết quả |
| 14–15 | Quy ước bắt buộc · Lệnh hay dùng | mỗi lần bắt tay làm |
| **16** | **Bước kế tiếp** | chọn việc |
| 17 | Đã quyết nhưng chưa thi công | tránh làm lại việc đã quyết |
| 18 | Nơi nộp — ICDAR 2027, hạn 28/02/2027 | lập lịch |
| **19** | **Tầng gold**: công cụ, đồng hồ, trình tự, nguồn, độ phân giải | việc đang làm |
| A | Hồ sơ đối chiếu Thông tư (Mốc 1) | tra mã số, đẳng thức, cạm bẫy văn bản |
| B | Sổ thi công phương án C, **bước D chưa làm** | làm tiếp nhận diện chuẩn |

---

## 0. CÂU HỎI ĐANG CHỜ NGƯỜI DÙNG TRẢ LỜI

Mục này là nơi DUY NHẤT liệt kê những thứ đang chờ quyết định. Phiên Claude
mới đọc mục này trước tiên; nếu người dùng chưa trả lời thì hỏi lại đúng
những câu dưới đây chứ đừng tự chọn, vì mỗi câu đều đổi kết luận khoa học
chứ không phải chi tiết cài đặt.

Người dùng trả lời được bằng một tin nhắn duy nhất, dạng "Câu 4 chọn ...".

**Đang chờ:** Câu 3 (hoãn được), Câu 8 (chỉ chặn lượt chạy Mốc 3 kế tiếp).
Không câu nào đang chặn việc gán nhãn.

**Mốc 3 đã chạy xong lúc 16:05 ngày 25/08/2026 — điều kiện dừng KHÔNG kích
hoạt.** Xem mục 13c. Việc kế tiếp không còn bị chặn: gán nhãn `data/gold/`
(hiện **11/100**, trọn danh mục 10 tài liệu đầu — mục 19), và ba baseline còn
thiếu (4, 5, 7).

**Câu 8 — MỚI, đang chờ.** Phép đo `do_nghich_dao_mot_loi.py` cho thấy tầng
XBRL tiêm đúng một lỗi mỗi lượt, mà lỗi đơn định vị được lại là ca bộ giải
liên tục nghịch đảo trọn vẹn — tức thiết kế đang chọn ca thuận lợi nhất cho
baseline 9. Có tiêm **nhiều hơn một lỗi mỗi lượt** ở lượt chạy tới không? Đây
là thay đổi thiết kế thí nghiệm nên phải vào mục Sửa đổi của
`PREREGISTRATION.md` TRƯỚC khi chạy. Chi tiết và số đo ở mục 13c.

**Câu 3 — NỘI DUNG CÂU ĐÃ MẤT KHỎI TÀI LIỆU.** Câu này được liệt kê là đang
chờ nhưng nguyên văn của nó không còn ở bất kỳ file nào trong repo — chỉ còn
lại cái tên. Nó từng nằm trong phần "giữ lại nguyên văn từng câu" ở cuối mục
này, và phần đó đã bị xoá trong một lần nén tài liệu. Vì không thể tự đoán
lại một câu hỏi đổi kết luận khoa học, việc đúng là **hỏi lại người chủ trì
xem Câu 3 là gì**, hoặc coi như nó không tồn tại và đánh số mới cho câu kế
tiếp. Nó được đánh dấu "hoãn được" nên chưa chặn việc gì.

**Câu 10 — ĐÃ TRẢ LỜI 26/08/2026: đổi tiêu chí sang độ phân giải bản quét,
ghi làm biến LIÊN TỤC chứ không chia nhóm theo ngưỡng.** Nhóm Stress thứ ba ở
`ANNOTATION-GUIDELINE.md` mục 7 nhận ra bằng `do_phan_giai_dpi` trong
`data/nguon_gold.json`, sinh bằng `python src/do_do_phan_giai.py`; chọn tài
liệu theo thứ hạng trong tập gold, không theo một con số dpi tuyệt đối. Hai tu
chính đã ghi: mục Sửa đổi của guideline (đổi tiêu chí) và của
`PREREGISTRATION.md` (độ phân giải thành hiệp biến, chỉ dùng cho phân tích
thứ cấp, không được dùng để loại tài liệu). Số đo và cạm bẫy ở mục 19.7.

**Câu 11 — ĐÃ TRẢ LỜI 26/08/2026: bỏ ký hiệu mẫu khỏi bảng dấu hiệu.** Mục
3.7 của `ANNOTATION-GUIDELINE.md` từng xếp `B 01a - DN` là dấu hiệu TT99,
mâu thuẫn với mục 2 của chính nó. Nay bảng chỉ còn số hiệu thông tư (đặt
trước, vì chắc chắn hơn) và tiêu đề báo cáo, kèm một luật phủ định nói thẳng
rằng hậu tố `a`/`b` không kết luận được gì về Thông tư. `SBT_2025Q2_TT200` và
`HNG_2025H1_TT200` giữ nguyên nhãn `TT200`, không phải gán nhãn lại. Tu chính
ở mục Sửa đổi của guideline; **thứ tự cam kết bị vượt đã ghi lại tại đó**, vì
hai tài liệu ấy được gán nhãn trước khi quy tắc được sửa.

**Câu 9 — ĐÃ TRẢ LỜI 26/08/2026: giữ hệ số 0,6.** Số phút đặt đồng hồ đo
trần người là `0,6 × trung vị thoi_gian_giay của 10 tài liệu gold đầu tiên`,
sàn 5 phút. **Đừng mở lại câu này**: giá trị của hệ số nằm ở chỗ nó được chốt
lúc chưa tài liệu nào có số đo thời gian, và cửa sổ đó đã đóng khi tài liệu
gold thứ hai có đồng hồ chạy thật. Tu chính ghi ở `PREREGISTRATION.md`
(26/08/2026) và `ANNOTATION-GUIDELINE.md` mục Sửa đổi.

**Đã trả lời 26/08/2026 (đợt 2) — ba quyết định về tầng gold:**

- **Người gán nhãn thứ hai: KHÔNG có. Người chủ trì tự gán nhãn.** Nghĩa là
  phương án dự phòng ở `ADDENDUM` mục 5 được kích hoạt: chính người ấy gán
  nhãn lại, sau **ít nhất hai tuần**, không xem bản cũ, và bài phải nói rõ
  đây là bản thay thế kèm giới hạn. **Hệ quả lịch, tính được ngay:** mười
  tài liệu đầu gán nhãn ngày 25–26/08/2026, nên lượt gán lại sớm nhất là
  **09/09/2026**. Hai tuần ấy là thời gian CHỜ nằm trên đường găng, không
  phải thời gian làm — bắt đầu muộn là mất trắng.
- **Quy mô tập gold đi theo mốc: 10 → 60 → 100.** Mốc 10 đã xong. Mốc 60 là
  chỗ mọi con số tính power của `ADDENDUM` mục 4 áp đúng như đã viết, vì bảng
  đó lấy 60 làm số cụm độc lập; mốc 100 là đích. Đừng gộp ba mốc lại thành
  "gán nhãn cho tới khi đủ 100".
- **Quy tắc `None` ở pipeline: HOÃN, tính sau.** Đây là câu "coi `None` là 0
  hay giữ nguyên" ở mục 12. Hoãn tường minh, không phải quên — nhưng nó vẫn
  chặn việc chạy pipeline diện rộng trên tài liệu thật, nên phải quyết trước
  bước đó.

**Đã trả lời 26/08/2026:** Câu 9 → giữ hệ số 0,6.

**Đã trả lời 25/08/2026 — tất cả trong một ngày:** Câu 1 → (a) ba con số định
vị; Câu 2 → (a) đo ma trận trước; Câu 4 → (a) cùng nguồn khác độ sâu; Câu 5 →
nới trần 10/20; Câu 6 → ghi làm giới hạn; Câu 7 → (a) hoà thì hoãn phán
quyết. Cộng thêm một quyết định không đánh số: chỉ số chính của H3 trên tầng
XBRL chuyển sang mức LƯỢT.

Nguyên văn của các câu đã trả lời KHÔNG còn được giữ ở đây — phần đó đã bị
xoá trong một lần nén tài liệu, và đó cũng là lý do Câu 3 nay chỉ còn cái
tên. Ràng buộc kèm theo từng câu đã trả lời thì vẫn còn, nhưng nằm ở mục Sửa
đổi của `PREREGISTRATION.md` chứ không ở đây; tra theo ngày trả lời.

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

### Bốn kết quả còn lại — đã dời sang Phụ lục A để khỏi chép hai lần

Liên kết chéo B03 → B01 có thật và được văn bản khai báo tường minh; hai mã
số đổi nghĩa giữa hai chuẩn (270 và 142) là nguồn lỗi câm; `FORM_MARKERS`
đã sai và đã sửa (`023321c`); trục TT200 → TT99 hẹp hơn tưởng nhưng không
rỗng. Cả bốn ở **Phụ lục A** cuối file, kèm nguyên văn trích dẫn.

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

### Phương án C — đã quyết và đã thi công 24/08/2026

Người dùng chốt: phân biệt "dòng vắng mặt" với "dòng đọc hỏng" bằng cách dò
**mã số dòng** trên text OCR, và ghi số `0` của dòng vắng mặt vào **cả `data`
đầu ra** kèm khoá trạng thái tường minh. Bốn commit, bẫy đã gặp, và bước D
còn lại: xem **Phụ lục B**.

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

**Người chủ trì đã HOÃN câu này ngày 26/08/2026** — hoãn tường minh, không
phải quên. Nhưng nó vẫn chặn việc chạy pipeline diện rộng trên tài liệu thật,
nên phải quyết trước bước đó. Đánh đổi có hai chiều thật:

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

## 13. MỐC 3 — điều kiện dừng KHÔNG kích hoạt, mốc chưa đóng

**Hiện trạng nằm ở mục 13c.** Hai lượt chạy trước (24/08 và 24/08 tối) đã bị
lượt 25/08 thay thế hoàn toàn; dưới đây chỉ giữ lý do của từng thứ đã chặn,
vì mỗi cái là một cạm bẫy có thể lặp lại.

`BUILD-SPEC.md` phần E định nghĩa mốc: **nếu baseline 9 ngang bằng phương pháp
đề xuất thì luận điểm "đọc lại nguồn" sai** — dừng, báo cáo, lùi paper về tầng
dataset + identifiability, đừng chạy tiếp C3 và toàn bộ ablation.

**Bốn thứ từng chặn phép đo, đã gỡ hết trong ngày 25/08:**

| Thứ chặn | Vì sao nó làm hỏng phép đo | Đã gỡ |
|---|---|---|
| Rò rỉ đáp án | Donor tính trung vị trên cả hồ sơ đang xét nên 32% chỉ tiêu có donor trùng khít giá trị thật — baseline 9 khi đó là oracle. Sau khi sửa, chỉ số chống bịa **đảo chiều** sang có lợi cho đề xuất | `e6c286c` loại cả công ty đang xét, không chỉ hồ sơ |
| Tắt mất nguồn ứng viên chính | Gọi `generate()` không truyền `o_lan_can`, tức bỏ hẳn việc đọc lại ô lân cận — đúng cơ chế cần chứng minh | đã sửa |
| Cột kỳ so sánh rỗng | 0/158 chỉ tiêu có giá trị ở kỳ thứ hai nên `col_shift` bỏ 120/130 lượt | `f80a53d` chọn kỳ theo **độ phủ chỉ tiêu** thay vì theo ngày |
| Ma trận nhầm chữ số chưa đo từ dữ liệu thật | Bộ tiêm và bộ sinh dùng hai mô hình lỗi khác nhau nên chỉ số `digit_sub` không mang thông tin về phương pháp | `90b271a` đo từ EasyOCR trên sáu font; độ phủ 0,046 → 0,615 |

Cộng thêm hai thứ không phải lỗi mà là quyết định của người: cách chấm khi một
phương pháp **từ chối trả lời** (đếm ABSTAIN là trượt tức đo mức sẵn sàng
đoán, không đo độ đúng — chốt báo cáo cả ba con số, Câu 1), và trần ứng viên
nới 6/12 → 10/20 theo số đo (`68ce4d2`, Câu 5).

**Một giới hạn không gỡ được ở tầng XBRL:** `row_shift` cần ảnh, tức cần
`data/gold/`. Và toàn bộ dữ liệu là doanh nghiệp Mỹ theo US-GAAP.

**Phép đo phải chạy lại mỗi lần đụng vào bộ sinh ứng viên hoặc bộ tiêm lỗi:**
[src/eval/do_phu_ung_vien.py](src/eval/do_phu_ung_vien.py) — nhanh, không gọi
`diagnose()`. Độ phủ chính là thứ quyết định bảng Mốc 3 đọc ra nghĩa gì.


### 13c. Lượt chạy Mốc 3 sau khi sửa hết bốn thứ chặn — 25/08/2026

**Chạy 14:22–16:05, 103 phút**, 26 hồ sơ của 14 công ty, **520 lượt** (4 chế
độ lỗi × 5 seed × 26 hồ sơ). Kết quả đầy đủ ở
[data/output/moc3_15congty.md](data/output/moc3_15congty.md). Khác lượt chạy
24/08 ở bốn điểm, mỗi điểm là một thứ chặn đã gỡ:

1. Ma trận nhầm chữ số nay **đo được từ EasyOCR trên sáu font** (`90b271a`),
   dùng chung cho bộ tiêm và bộ sinh nhưng **khác độ sâu** — bộ sinh giữ 6
   cặp đầu, bộ tiêm lấy trọn phân phối. Độ phủ `digit_sub` 0,046 → 0,615.
2. Cột kỳ so sánh nay chọn theo **độ phủ chỉ tiêu** thay vì theo ngày
   (`f80a53d`), nên `col_shift` inject được đủ 130 lượt thay vì 10.
3. Trần ứng viên nới 6/12 → **10/20** theo số đo (`68ce4d2`).
4. Bảng tách theo chế độ lỗi thêm **trước** lượt chạy (`ea1ffb2`), vì việc
   đếm nằm ở `chay()` chứ không ở `bao_cao()`.

#### Bảng gộp — và vì sao nó không đọc được một mình

| Chỉ số | Đề xuất | Baseline 9 | Ai thắng |
|---|---:|---:|---|
| Tỷ lệ lượt còn sai sau sửa (CHÍNH) | 0,719 | 0,646 | baseline 9 |
| Tỷ lệ lỗi câm mức trường (phụ) | 0,00488 | 0,00597 | đề xuất |
| **Tỷ lệ bịa mức trường (phụ)** | **0,00400** | **0,00609** | **đề xuất** |
| Định vị đúng / tổng lượt (CHÍNH) | 0,227 | 0,288 | baseline 9 |
| Tỷ lệ ra tay | 0,285 | 0,606 | — |
| Định vị đúng TRÊN LƯỢT CÓ RA TAY | **0,797** | 0,476 | đề xuất |
| VERIFIED / REPAIRED / ABSTAIN | 125 / 148 / 247 | 125 / 315 / 80 |  |

#### Bảng tách theo chế độ lỗi — bảng quyết định

| Chế độ lỗi | Kiểm được khả năng SỬA? | Còn sai — đề xuất | Còn sai — baseline 9 | Ra tay — đề xuất |
|---|---|---:|---:|---:|
| `sign` | có | **0,392** | 0,600 | 0,608 |
| `digit_substitution` | có | **0,485** | 0,592 | 0,377 |
| `row_shift` | KHÔNG — phủ 0,015 | 1,000 | 0,654 | 0,062 |
| `col_shift` | KHÔNG — phủ 0,000 | 1,000 | 0,738 | 0,092 |

#### Đọc kết quả — theo ba tu chính ghi trước khi có bất kỳ con số nào

Đây là chỗ dễ bị cáo buộc đọc kết quả theo ý mình nhất, nên phải nói rõ thứ
tự thời gian, và nói cho đúng chứ không nói cho đẹp. Lượt chạy bắt đầu
**14:22:53** và chỉ sinh ra con số đầu tiên lúc **16:05** — `bao_cao()` in một
lần ở cuối, không có kết quả trung gian nào ra màn hình.

| Tu chính | Commit | Giờ | So với lúc chạy | So với lúc CÓ SỐ |
|---|---|---|---|---|
| Bảng tách theo chế độ lỗi | `ea1ffb2` | 14:18 | trước 5 phút | trước 107 phút |
| Câu 7 — hoà thì hoãn phán quyết | `113e741` | 14:23 | **sau 7 giây** | trước 102 phút |
| Câu 7 vào PREREGISTRATION | `525fb42` | 14:30 | **sau 7 phút** | trước 95 phút |

Hai dòng cuối commit sau lúc bấm chạy, nên câu "ghi trước khi chạy" là SAI và
không được viết vào bài. Câu đúng, và cũng là câu mang giá trị đăng ký trước
thật: **cả ba đều được ghi trước khi tồn tại bất kỳ con số nào của lượt
chạy** — sớm nhất là 95 phút. Quyết định Câu 7 do người dùng chốt trong tin
nhắn trước khi lượt chạy được bấm; commit chỉ là lúc chép nó vào file.

Kiểm lại bằng `git log --format='%h %ad %s' --date=format:'%d/%m %H:%M'` và
`ls -l --time-style=full-iso data/output/moc3_15congty.md` (file tạo lúc
14:22:53, kích thước 0 cho tới 16:05).

- Tu chính *"Tầng XBRL chỉ kiểm được khả năng SỬA cho 2 trong 4 chế độ lỗi"*
  nói bảng gộp là trung bình của hai nhóm khác bản chất nên không mang nghĩa,
  và H3 cho `row_shift`/`col_shift` **phải chờ tập gold**.
- Trên hai chế độ tầng này kiểm được, đề xuất thắng **+20,8 điểm phần trăm**
  (`sign`) và **+10,7 điểm** (`digit_substitution`) — cả hai vượt xa ngưỡng
  effect size 3 điểm đã chốt ở mục 1 của `PREREGISTRATION.md`.
- Tu chính Câu 7 nói trên tầng XBRL: **thua** kích hoạt điều kiện dừng,
  **hoà** hoãn phán quyết, **thắng** là bằng chứng mạnh.

Ghép lại: trong phạm vi tầng XBRL kiểm được, **đề xuất THẮNG**, và điều kiện
dừng Mốc 3 **không kích hoạt**. Hai chế độ lệch dòng/lệch cột chưa được kiểm
chứ không phải đã thua — ở đó đề xuất ABSTAIN đúng như thiết kế (ra tay 0,062
và 0,092) trong khi baseline 9 nặn giá trị donor.

Chiều chống bịa cũng thắng: **0,00400 so với 0,00609**. Theo mục 1 của
`PREREGISTRATION.md`, thắng chiều một mà thua chiều hai là kết quả tiêu cực —
lượt này thắng cả hai chiều.

#### ĐÃ ĐO XONG NGHI VẤN — và câu trả lời đổi cách đọc cả bảng

Nghi vấn ban đầu: baseline 9 sửa đúng **26–35% số lượt** `row_shift`/
`col_shift` trong khi ở hai chế độ đó giá trị thật đã bị ghi đè và biến mất
khỏi bảng, nên nó không có nguồn nào để lấy lại đúng con số ấy.

**Giả thuyết đầu — đã bị bác bằng số đo.** Nghi là các lượt trúng rơi vào chỉ
tiêu có giá trị thật bằng 0, vì tu chính 24/08 ghi dòng vắng mặt là `0` nên
trung vị donor bằng 0 sẽ khớp mà không cần biết gì. Đo được **0 trên 520
lượt** có giá trị thật bằng 0, và donor khớp giá trị thật **0 trên 520 lượt**.
Sai hoàn toàn. Bộ đếm giữ lại trong bảng để lần sau không ai kiểm lại.

**Lời giải thích đúng, và nó quan trọng hơn nhiều.** Baseline 9 không điền
thẳng giá trị donor: nó chọn bộ giá trị gần donor nhất **mà vẫn thoả ràng
buộc**, tức giải một bài tối ưu liên tục. Khi đúng một trường sai và trường
đó được thả ra một mình thì `r = δᵢ·aᵢ`, nên nghiệm duy nhất là `δ = −δᵢ`,
bất kể donor ở đâu. **Baseline 9 không bịa — nó NGHỊCH ĐẢO**, và với lỗi đơn
định vị được thì phép nghịch đảo trả lại đúng giá trị thật tới từng chữ số.

Dấu vết nằm sẵn trong bảng: tỷ lệ sửa đúng của baseline 9 gần trùng tỷ lệ
định vị đúng ở ba trong bốn chế độ — lệch 1–2 lượt trên 130. Nó sửa đúng KHI
VÀ CHỈ KHI nó định vị đúng.

Phép đo mới ([src/eval/do_nghich_dao_mot_loi.py](src/eval/do_nghich_dao_mot_loi.py),
kết quả ở [data/output/moc3_nghich_dao_mot_loi.md](data/output/moc3_nghich_dao_mot_loi.md))
xác nhận cơ chế bằng đại số và cho ra một con số dùng được cho cả bài:

| Trạng thái | Tỷ lệ | Nghĩa |
|---|---:|---|
| Ràng buộc **chốt đúng** giá trị | 0,608 | **Trần trên của mọi bộ giải liên tục** khi không đọc lại tài liệu |
| Không chốt | 0,146 | Khoảng hở mà việc đọc lại nguồn tồn tại để lấp |
| Cột bằng 0 | 0,246 | Không ràng buộc nào bảo vệ — kết quả của **H0** |

Con số 0,246 khớp với 125/520 = 0,240 lượt VERIFIED trong bảng Mốc 3, tức hai
phép đo độc lập cho cùng một câu trả lời.

#### Chuẩn hoá theo trần — bảng Mốc 3 đọc ra nghĩa khác hẳn bảng thô

| Chế độ lỗi | Trần | Đề xuất | % trần | Baseline 9 | % trần |
|---|---:|---:|---:|---:|---:|
| `sign` | 0,608 | **0,608** | **100,0%** | 0,400 | 65,8% |
| `digit_substitution` | 0,608 | 0,515 | 84,7% | 0,408 | 67,1% |
| `row_shift` | 0,608 | 0,000 | 0,0% | 0,346 | 56,9% |
| `col_shift` | 0,585 | 0,000 | 0,0% | 0,262 | 44,8% |

Ở `sign`, phương pháp đề xuất **giải đúng MỌI lượt mà thông tin tồn tại** và
im lặng ở phần còn lại. Không thể hơn được nữa. Đây là cách trình bày kết quả
nên dùng trong bài: chuẩn hoá theo trần identifiability biến H0 từ một mục
độc lập thành công cụ làm cho H2 và H3 đọc được.

#### HỆ QUẢ CHO THIẾT KẾ THÍ NGHIỆM — phần phải nhớ nhất

Tầng XBRL tiêm **đúng một lỗi mỗi lượt**, mà lỗi đơn định vị được lại chính
là ca phép nghịch đảo liên tục giải trọn vẹn. **Thiết kế hiện tại đang chọn
đúng ca thuận lợi nhất cho baseline 9.**

Khoảng hở mà "đọc lại nguồn" lấp là ca ràng buộc KHÔNG chốt được giá trị:
nhiều lỗi đồng thời, cột bằng 0, cột tỷ lệ với nhau, và lỗi nằm trong
`null(A)`. Đây là số đo chứ không phải lời bào chữa, và nó nói **lượt chạy
tới phải tiêm nhiều hơn một lỗi mỗi lượt**. Đó là thay đổi thiết kế, nên phải
ghi vào mục Sửa đổi của `PREREGISTRATION.md` TRƯỚC khi chạy.

#### Việc phải làm mà lượt chạy này lộ ra

- **Kết quả không được lưu dạng JSON.** `chay()` trả dict rồi `bao_cao()` in
  ngay ra stdout; không gì được ghi lại. Muốn in lại bảng theo cách khác phải
  chạy lại 103 phút. Cần ghi `data/output/moc3_<ngày>.json` trong khối
  `__main__` trước lượt chạy kế tiếp.
- **`data/output/moc3_15congty.md` đã bị sửa tay** ở `db09dc8` đúng bằng thứ
  `bao_cao()` nay sinh ra, vì không có bản JSON để in lại. Lượt chạy sau sẽ
  ghi đè file này bằng bản sinh thật.

#### Trạng thái Mốc 3 sau lượt chạy này

**Điều kiện dừng KHÔNG kích hoạt.** Được phép đi tiếp sang C3, C4, D2–D4 và
sang việc gán nhãn `data/gold/`.

**Nhưng Mốc 3 chưa ĐÓNG**, và lý do nay chỉ còn đúng một: phán quyết cuối
cùng của H3 nằm ở **tầng gold Việt Nam**, nơi có ảnh nên cả năm nguồn ứng
viên đều chạy và cả bốn chế độ lỗi đều kiểm được khả năng sửa. Tầng XBRL đã
cho tất cả những gì nó có thể cho.
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

# TẢI 10 tài liệu gold đầu về data/bctc/ (danh mục ở data/nguon_gold.json)
python src/tai_bctc.py

# ĐO độ phân giải bản quét — trục phân nhóm Stress thứ ba (mục 19.7)
python src/do_do_phan_giai.py            # chỉ in bảng
python src/do_do_phan_giai.py --ghi      # ghi vào data/nguon_gold.json

# CÔNG CỤ GÁN NHÃN tập gold, rồi mở http://127.0.0.1:8100
# Dùng launcher chứ ĐỪNG gọi thẳng uvicorn: lệnh gọi thẳng cần đặt biến môi
# trường, mà `VAR=x lệnh` chạy trên bash nhưng LỖI CÚ PHÁP trên PowerShell —
# shell chính của máy này. Đã mất thời gian vì việc đó một lần ngày 25/08.
python chay_gan_nhan.py --pdf-dir data/bctc
python chay_gan_nhan.py --pdf-dir D:/bctc --port 8200

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

Cập nhật 26/08/2026. Đường găng nay đi qua **tầng gold**, không còn qua Mốc 3.

1. **Gán nhãn thêm 2 tài liệu có đồng hồ chạy thật** (mục 19.4 bước 2). Mười
   tài liệu của `data/bctc/` đã gán nhãn xong, nhưng chỉ 8 trong số đó đếm
   được vào trung vị, nên phải chọn thêm 2 mã mới. Đủ 10 thì tính trung vị và
   tuyên số phút cho giao thức trần người.
2. **Chọn 90 mã còn lại** rồi thêm vào `data/nguon_gold.json`. Nay là việc
   chọn, không còn là việc dò nguồn.
3. **Ba baseline còn thiếu: 4, 5, 7.**
4. **Bước D của phương án C** — nhận diện chuẩn mẫu biểu (Phụ lục B). Việc rẻ
   nên làm trước: chạy lại phép đo `tieu_de_trong_vung_cat` trên 10 tài liệu
   mới thay vì một tài liệu như hiện nay.
5. Sau đó: pilot 20 tài liệu → **MỐC 2** (tính lại power) → C3 → C4 → D2/D3/D4.

### Ngân sách tầng gold, đối chiếu với số đo thật

Dự trù cũ đoán 45–60 giờ cho 60 tài liệu và xếp công đoạn điền là khoản nặng
nhất. Cả hai đều sai, và sai theo hướng có lợi:

| Khoản | Dự trù cũ (60 tài liệu, 21 chỉ tiêu) | Ước theo số đo (100 tài liệu, 27 chỉ tiêu) |
|---|---:|---:|
| Điền nhãn | 20–25 giờ | **~17 giờ** |
| Gán nhãn đôi + phân xử | 8–10 giờ | ~3,5–6 giờ |
| Đo trần người | 3 giờ | ~1–2 giờ |
| Tìm và tải tài liệu | 15–20 giờ | **rẻ hẳn từ 26/08** — có API và script, xem mục 19.6 |

**Cập nhật 26/08/2026 — con số 10 phút nay có đồng hồ thay cho cảm giác.**
Tám tài liệu đã đo cho 361–579 giây, trung vị **442 giây ≈ 7,4 phút**, tức
công đoạn điền RẺ HƠN ước lượng cảm giác chừng một phần tư. Chiếu sang 100
tài liệu thì khoản "điền nhãn" rơi về **~12 giờ** thay vì ~17 giờ trong bảng
trên; bảng giữ nguyên con số cũ vì nó là ước dựa trên 10 phút, và ghi đè nó
lúc mới có 8 số đo là chỉnh dự trù theo mẫu mỏng. Đủ 10 số đo thì cập nhật
bảng một lần, không sửa dần.

### Ba việc song song, không cái nào chặn cái nào

- **Tìm người hướng dẫn hoặc đồng tác giả.** Nâng xác suất được nhận nhiều
  nhất trên mỗi đơn vị công sức — hơn bất kỳ thí nghiệm nào còn lại. Bài Q1
  đầu tay không có người hướng dẫn mạnh thường chết ở khâu framing và khâu
  trả lời reviewer, không phải ở khâu kết quả.
- **Đo throughput API thật trên 5 tài liệu.** B2 dùng self-consistency k=5;
  nhân với 10 baseline, nhiều model, nhiều seed, cộng tầng XBRL hàng nghìn
  tài liệu thì đây là hàng chục nghìn lời gọi trên free tier OpenRouter. Rủi
  ro này không làm chậm lịch — nó có thể **chặn hẳn việc tạo ra con số**.
- **Chốt người gán nhãn thứ hai.** Nếu dùng phương án dự phòng (`ADDENDUM`
  mục 5: tự gán lại sau ít nhất hai tuần) thì lượt gán lại phải bắt đầu SỚM,
  vì hai tuần là thời gian **chờ** nằm trên đường găng.


## 17. LƯU Ý — việc người dùng đã quyết nhưng CHƯA thi công

Mục này giữ những việc đã có quyết định nhưng cố ý hoãn lại. Đọc mục này
trước khi bắt đầu bất kỳ việc gì ở mục 16, kẻo làm theo con số cũ.

### 17.1 Đổi bộ chỉ tiêu từ kịch bản D sang **kịch bản E** — ĐÃ LÀM 25/08/2026

> **Thi công xong ở `f1c2738`.** Sáu bước dưới đây đã làm hết trừ bước 4 —
> đo lại trần người — vì chỉ người sẽ gán nhãn mới đo được. Giữ nguyên phần
> mô tả bên dưới làm hồ sơ lý do; hiện trạng và số đo ở ngay dưới đây.

**Đo được sau khi thi công:**

| | Kịch bản D | Kịch bản E |
|---|---:|---:|
| Chỉ tiêu (TT200 / TT99) | 20 / 21 | 26 / 27 |
| Đẳng thức | 7 | 9 |
| `rank(A)` | 7 | 9 |
| `dim null(A)` (TT200 / TT99) | 13 / 14 | 17 / 18 |
| Định vị được lỗi một-trường (TT200) | 5 / 20 | 7 / 26 |
| Chỉ tiêu có cột toàn 0 | 0 | 0 |

Hai chỉ tiêu mới định vị được: `lctt_thuan` và **`tien_va_tuong_duong_tien`**.
Cái thứ hai là điểm đáng giá riêng của E — nó ĐÃ nằm trong bộ từ trước
nhưng lẫn trong lớp năm thành phần của mã 100, và đẳng thức liên kết chéo
B03 gắn cho nó một đẳng thức THỨ HAI để tách ra. Không nhóm mở rộng nào
khác gỡ được một chỉ tiêu CŨ ra khỏi lớp lẫn.

**Phần không đẹp, phải báo cáo vì nó là kết quả của H0:** không gian null
tăng 13 → 17 chiều, còn TỶ LỆ định vị được gần như đứng yên (25% → 27%).
Thêm 6 chỉ tiêu mà chỉ mua 2 đẳng thức thì 4 chiều chênh lệch rơi thẳng vào
không gian vô hình. E tốt hơn D nhưng không sửa được kết luận nền của H0.

**~~CÒN LẠI, và nó CHẶN tài liệu gán nhãn đầu tiên~~ — ĐÃ GIẢI QUYẾT
25/08/2026, nhưng KHÔNG theo thứ tự đã cam kết.** Việc phải làm là bấm giờ
thử với 27 chỉ tiêu rải qua ba biểu mẫu, trước tài liệu đầu tiên. Thực tế
chạy ngược: tài liệu đầu tiên được gán nhãn trước, rồi chính nó cung cấp số
liệu. Kết quả ngược với dự đoán — giao thức 15 phút không vỡ mà **chùng** —
và con số 15 phút đã bị bỏ. Đầy đủ ở mục 19.3; tu chính đã ghi vào
`PREREGISTRATION.md` và `ANNOTATION-GUIDELINE.md`. Thiệt hại thực bằng 0 vì
số tài liệu đã gán nhãn dưới giao thức trần người vẫn là 0, nhưng thứ tự thì
đã khác cam kết và điều đó được ghi lại chứ không bỏ qua.

**Một khoảng trống mới sinh ra, đã chốt bằng test:** bộ số đối chiếu
`VNM_Q1_2026` trong `tests/test_constraints.py` do người đọc tay và chỉ phủ
B01 với B02. Bản PDF trong `data/samples/` là ảnh scan nên không rút số B03
bằng máy được. Hai test dùng bộ số này nay chạy trên phần phủ được, và
`test_bo_so_that_chua_phu_duoc_B03_va_test_phai_noi_ra` chốt tường minh sáu
chỉ tiêu còn thiếu — bổ sung số vào bộ đối chiếu thì test đó đỏ và nhắc gỡ
phần cắt bớt. Việc bổ sung cần người đọc tay từ báo cáo.

---

**Hồ sơ lý do** — vì sao E chứ không phải phân rã tiếp: nối chéo gắn đẳng
thức thứ hai vào chỉ tiêu ĐÃ CÓ, còn phân rã mở thêm một tầng lá mới mà mỗi
lá là chi phí gán nhãn nhân với cả tập gold. Số đo tỷ lệ đánh đổi ở Phụ lục
A.1; tu chính đầy đủ kèm ngày ở `PREREGISTRATION.md` mục Sửa đổi 25/08/2026.

Việc này cố ý làm khi `data/gold/` còn **trống hoàn toàn**, vì đổi bộ chỉ
tiêu sau đó sẽ buộc gán nhãn lại cả tập. Cửa sổ ấy nay đã đóng: tập gold có
một tài liệu, và mười tài liệu nữa đang chờ. **Đừng đổi bộ chỉ tiêu nữa.**

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

## 19. Tầng gold — công cụ, đồng hồ, trình tự, nguồn tài liệu, độ phân giải

Viết 25/08/2026. Đây là mục mô tả hiện trạng của tầng gold; trước mục này,
mọi tài liệu trong repo đều giả định `data/gold/` còn trống.

### 19.1 Công cụ gán nhãn `src/gan_nhan/`

Gán nhãn tay 100 tài liệu × 27 chỉ tiêu bằng cách gõ JSON thẳng là việc vừa
chậm vừa không kiểm chứng được, nên có một công cụ web chạy tại chỗ.

```
python chay_gan_nhan.py          # rồi mở http://127.0.0.1:8100
```

**Dùng launcher, ĐỪNG gọi thẳng `uvicorn`.** Gọi thẳng cần đặt biến môi
trường `GAN_NHAN_PDF_DIR`, mà cú pháp `VAR=x lệnh` chạy trên bash và **lỗi cú
pháp trên PowerShell** — shell chính của máy này. Đã mất thời gian vì đúng
việc đó một lần. Launcher còn đặt biến TRƯỚC khi uvicorn nạp app (nên nó
truyền chuỗi `"gan_nhan.app:app"` chứ không truyền đối tượng app), và kiểm
thư mục PDF tồn tại và không rỗng trước khi mở cổng.

| File | Việc |
|---|---|
| `src/gan_nhan/app.py` | FastAPI: phục vụ ảnh trang, danh sách chỉ tiêu, kiểm đẳng thức, ghi và đọc lại file gold |
| `src/gan_nhan/giao_dien.html` | Hai khung: PDF bên trái (PageUp/PageDown, +/− phóng to), bảng chỉ tiêu bên phải |
| `src/gan_nhan/trang.py` | Kết xuất trang PDF bằng **pypdfium2** — KHÔNG dùng pdf2image, máy này không có `pdftoppm` |
| `src/gan_nhan/so_viet.py` | Đọc số kiểu Việt: `1.234.567`, `(1.234)` là số âm, `-`/`–`/`—` là rỗng |
| `src/gan_nhan/kiem.py` | Chạy 9 đẳng thức trên chính số vừa gõ, cộng danh mục kiểm của guideline |

Đồng hồ nằm ở lớp `DongHo` trong `app.py` và **do người tự bấm** — xem mục
19.5, kể cả khi chỉ định đụng vào một chỗ khác của công cụ.

**Luật 1 (người gán nhãn mù với đầu ra pipeline) được chốt bằng test, không
bằng lời hứa.** `tests/test_gan_nhan_mu_voi_pipeline.py` phân tích AST của cả
gói và bắt đỏ nếu bất kỳ module nào import `router`, `extract_vlm`,
`extract_baseline`, `ocr_baseline`, `layout_detection`, `repair`, hay `api`.
Có một test riêng cho `giao_dien.html`. Test loại trừ docstring khỏi phần mã
thực thi, nếu không thì chính những comment giải thích lệnh cấm sẽ tự làm đỏ.

**Ghi đè được và có dấu vết.** Nút "Mở lại bản đã lưu" nạp lại toàn bộ ô từ
file gold đã có (giá trị chia ngược về đơn vị trên báo cáo để khớp cái mắt
đang nhìn), và mỗi lần ghi tăng `so_lan_ghi`. Phát hiện đọc nhầm một chữ số
thì phải sửa được mà không phải gõ lại 27 ô; nhưng một bản đã sửa ba lần và
một bản viết một lần rồi thôi là hai thứ khác nhau khi phân tích chất lượng
gán nhãn, nên lần ghi phải đếm được. Đồng hồ **cố ý chạy lại từ đầu** khi mở
lại chứ không cộng dồn: `thoi_gian_giay` đo tốc độ trên một tài liệu MỚI, trộn
một lần sửa một ô vào sẽ làm hỏng chính phép đo trần người.

#### Trình tự một tài liệu

Guideline giữ các QUY TẮC; đây là thao tác, và nó chưa nằm ở đâu khác.

1. Chọn file, gõ `doc_id` — **đúng bằng tên file bỏ đuôi** (`HPG_2026Q2_TT99`).
   Tên file trong `data/bctc/` cố ý đặt khớp `doc_id` để khỏi phải nghĩ.
2. Bấm **▶ Bắt đầu bấm giờ**. Nghỉ giữa chừng thì ⏸ Tạm dừng.
3. Xác định chuẩn **bằng mắt** theo guideline mục 3.7. Đừng suy từ năm báo
   cáo — xem cảnh báo về MSN ở cuối mục 19.6.
4. Chép `unit_declared` **nguyên văn**. Guideline mục 3.1 cấm suy hệ số từ độ
   lớn con số.
5. Điền, bấm **Kiểm đẳng thức**. Lệch thì **đọc lại báo cáo**, đừng sửa cho
   cân; công cụ cố ý không bao giờ gợi ý giá trị.
6. Tick danh mục kiểm, bấm Lưu.

**Thứ tự nên làm trong 10 tài liệu đầu.** Bắt đầu bằng `BMP` hoặc `DGC` — bản
in sạch, đơn vị VND, có lãi. Để `HNG` (lỗ, `Ngàn VND`, các dòng đổi tên thành
"Lỗ") lại sau khi đã quen tay. `SBT` và `HNG` đang vướng Câu 11 nên để cuối.

> **Không có đường tắt, và đó là chuyện tốt.** Cả 10 tài liệu đều là ảnh quét
> không lớp text (mục 19.6a), nên không `pdftotext` được, không copy-paste
> được. Ai định "tách nội dung ra khỏi PDF" cho nhanh thì hoặc phải chạy OCR —
> **vi phạm Luật 1** — hoặc phải đọc bằng mắt. Việc không có đường tắt khiến
> vi phạm khó xảy ra do vô ý, và vi phạm Luật 1 là loại **không để lại dấu
> vết**: file gold nhiễm trông y hệt file sạch.

### 19.2 Tài liệu gold đầu tiên

`data/gold/VNM_2026Q1_TT99.json` — Vinamilk, quý 1 năm 2026, chuẩn TT99, 27
chỉ tiêu, đơn vị VND (`unit_multiplier: 1`), cả **9 đẳng thức cân**.

**Nguồn gốc chưa xác định được, và đã thôi truy.** File thiếu khoá
`so_lan_ghi` và có `thoi_gian_giay` bằng 0, trong khi công cụ luôn ghi cả
hai — dấu vết nói nó được sửa tay trong trình soạn thảo, hoặc được ghi bởi
một bản máy chủ cũ hơn. Nội dung không sai: 9 đẳng thức cân, và chính người
dùng đã bắt được lỗi mã 52 trên nó. Người dùng chọn **xử lý nguyên nhân thay
vì chú thích triệu chứng**: thay vì ghi một dòng vào `notes` của một file,
công cụ nay có nút bấm giờ tường minh và từ chối ghi khi đồng hồ chưa chạy
(mục 19.5), nên ca này không lặp lại được nữa.

File giữ nguyên, không sửa. Với khoá `trang_thai_dong_ho` mới, nó tự đọc ra
`"khong_do"` theo giá trị mặc định của schema — tức tự khai đúng điều duy
nhất chắc chắn về nó, rằng không có số đo thời gian nào. **Hệ quả cho phép
đo giữ nguyên:** tài liệu này KHÔNG đóng góp số nào cho nhịp gán nhãn; trung
vị ở mục 19.3 phải lấy từ 10 tài liệu có đồng hồ chạy thật.

### 19.3 Hai thứ rút ra, cả hai ngược với dự đoán đã ghi

**(a) Giao thức trần người 15 phút không vỡ — nó chùng.** `ADDENDUM` mục 6,
`PREREGISTRATION.md` và mục 17.1 của chính file này đều dự đoán rằng 27 chỉ
tiêu rải qua ba biểu mẫu sẽ làm **vỡ** đồng hồ 15 phút. Số thật đi ngược:
công đoạn điền hết khoảng **10 phút**. Đó không phải tin tốt. Con số 15 phút
tồn tại để tạo **áp lực thời gian**, tức để bản dùng đo trần khác với bản gold
đã phân xử kỹ. Nếu nhịp làm kỹ đã là 10 phút thì 15 phút là dư: hai bản thành
cùng một người làm cùng một việc, trần người ra gần 100%, và con số đó không
diễn giải nổi kết quả hệ thống — mất đúng công dụng mà câu đầu tiên của
`ADDENDUM` mục 6 nêu.

Giao thức mới: đồng hồ đặt ở **0,6 × trung vị `thoi_gian_giay` của 10 tài liệu
gold đầu tiên**, làm tròn tới phút, **sàn 5 phút**. Chốt công thức chứ không
chốt một con số, vì ước lượng 10 phút là cảm giác chứ không phải đồng hồ. Thứ
duy nhất thật sự cần đăng ký trước là **hệ số 0,6** — nó phải được chọn trước
khi nhìn thấy kết quả trần người. **Người dùng đã chốt giữ 0,6 ngày
26/08/2026**, lúc chưa tài liệu nào có số đo thời gian; Câu 9 đóng.

**(b) Bước kiểm đẳng thức bắt được lỗi mà mắt người vừa bỏ qua — ngay ở tài
liệu đầu tiên.** Thuế thu nhập hoãn lại (mã 52) bị đọc `1` thành `0` ở hàng
chục nghìn, lệch đúng 10.000 đồng trên một con số 48 tỷ. Đẳng thức
`LNST + thuế hiện hành + thuế hoãn lại = LNTT` báo ĐẠT vì sai số tương đối
4·10⁻⁹ nằm dưới `IDENTITY_TOLERANCE_RATIO` (10⁻⁷); người dùng đọc lại báo cáo
mới ra. **Không chỉnh ngưỡng dung sai** — dữ liệu mới có một công ty, và
chỉnh hằng số biên theo một quan sát là cách chắc chắn nhất để chốt nhầm.

Điều đáng ghi lại: **1↔0 KHÔNG có trong ma trận nhầm chữ số đo được từ
EasyOCR** — cặp phổ biến nhất của máy là 9→0 (23 lần) rồi 5→3 (13 lần). Nếu
mô hình lỗi của người thật sự khác mô hình lỗi của máy thì đó là một quan sát
dùng được trong bài, và nó cũng chạm tới thiết kế bộ tiêm lỗi. Nhưng **N = 1
chưa kết luận gì**; việc đúng là đếm dần từng lỗi người bắt gặp khi gán nhãn,
chứ không viết kết luận bây giờ.

### 19.4 Việc còn lại của tầng gold, theo thứ tự chặn nhau

1. ~~**Nguồn của 99 tài liệu còn lại — CHẶN mọi thứ khác**~~ — **ĐÃ GỠ CHẶN
   26/08/2026.** Nguồn là `finance.vietstock.vn`, lấy được bằng máy; mười tài
   liệu đầu đã chọn, đã tải, đã kiểm. Xem mục 19.6. Khoản "tìm và tải" mà mục
   16 xếp là đắt nhất nay rẻ đi hẳn: việc còn lại là chọn 90 mã, không phải đi
   dò từng nguồn.
2. **Chạy đồng hồ thật trên 10 tài liệu — CÒN THIẾU 2.** Không cần chờ đủ
   100: cứ gán nhãn tới đâu đồng hồ chạy tới đó, đủ 10 thì tính trung vị và
   chốt số phút cho giao thức trần người. Đồng hồ **không tự chạy**: bấm nút
   "Bắt đầu bấm giờ" (mục 19.5); quên bấm thì công cụ từ chối ghi, nên không
   mất số một cách âm thầm nữa.

   Hiện `data/gold/` có 11 file nhưng chỉ **8** mang `trang_thai_dong_ho`
   bằng `da_do`: 361, 416, 433, 438, 446, 461, 506, 579 giây. Ba file không
   tính là `VNM_2026Q1_TT99` (thiếu hẳn khoá, mục 19.2), `DGC_2025Q2_TT200`
   và `TTF_2026Q1_TT99` (`khong_do`). Vậy còn thiếu **2 tài liệu có đồng hồ**,
   và hai tài liệu ấy phải nằm ngoài 11 file đã có — gán nhãn lại một file cũ
   thì đo nhịp của lần gán nhãn thứ hai, không phải nhịp của lần đầu.

   Ghi trước để khỏi tưởng kết quả còn là ẩn số: **hai tài liệu cuối không
   đổi được kết luận nữa.** Trung vị của 10 số là trung bình số thứ 5 và thứ
   6; tám số đã có kẹp hai vị trí đó lại, nên dù hai số mới nhỏ tuỳ ý hay lớn
   tuỳ ý, trung vị cũng chỉ chạy trong dải 435,5–453,5 giây. Nhân 0,6 ra
   4,36–4,54 phút — **toàn dải nằm dưới sàn 5 phút**. Đồng hồ trần người vì
   thế sẽ là **5 phút**, và điều đó đã cố định về mặt số học.

   Dù vậy **vẫn phải đo đủ 10 rồi mới tuyên**, vì công thức đăng ký là "trung
   vị của 10 tài liệu". Tuyên sớm vì "đằng nào cũng ra 5 phút" thì con số vẫn
   đúng nhưng cam kết thì hỏng, và lần sau không còn cách nào phân biệt một
   suy luận số học với một lần tự cho phép mình bỏ bước.
3. **Chốt 20 hay 33 tài liệu gán nhãn đôi — CÒN MỞ, và nay gắn với mốc.**
   `ADDENDUM` mục 5 viết "một phần ba tập gold", chốt khi tập là 60 nên ra
   20. Tập đích nay khoảng 100 nên cách diễn đạt đó tự nó thành 33. Với lộ
   trình 10 → 60 → 100 thì câu hỏi thật là: một phần ba của MỐC NÀO. Phải
   chọn một và ghi tu chính, muộn nhất là trước khi lượt gán nhãn lại đầu
   tiên bắt đầu — vì chính lượt đó tiêu số tài liệu đã chọn.
4. **Người gán nhãn thứ hai — ĐÃ QUYẾT 26/08/2026: không có, người chủ trì
   tự gán nhãn.** Phương án dự phòng ở `ADDENDUM` mục 5 vì thế là phương án
   đang dùng: chính người ấy gán lại sau **ít nhất hai tuần**, không xem bản
   cũ. Mười tài liệu đầu gán nhãn 25–26/08/2026 nên **lượt gán lại sớm nhất
   là 09/09/2026**. Hai tuần đó là thời gian chờ nằm trên đường găng chứ
   không phải thời gian làm — mỗi ngày bắt đầu muộn là một ngày mất trắng.
5. **Đo trần người**, 10 tài liệu, sau khi có số phút ở bước 2.

### 19.5 Đồng hồ do người tự bấm — 26/08/2026

Bản đầu của công cụ tự khởi động đồng hồ lúc người gõ xong `doc_id` và lấy
hiệu tới lúc bấm Lưu. Người dùng yêu cầu thay bằng **nút bấm giờ tường
minh**, sau khi ca `VNM_2026Q1_TT99` cho thấy một file gold có thể ra đời với
ô thời gian không ai đọc được nghĩa.

**Vì sao đo tự động là sai chứ không chỉ là kém tiện.** Con số cần đo nuôi
thẳng vào giao thức trần người: số phút đặt đồng hồ bằng `0,6 × trung vị của
10 tài liệu đầu`. Với `n = 10`, một tài liệu lệch đủ sức đẩy trung vị. Mà đo
tự động lệch theo **cả hai** chiều: gõ `doc_id` rồi mới đi tìm file PDF, hay
để cửa sổ mở qua buổi trưa, đều cộng thêm thời gian không phải thời gian làm
việc; ngược lại, người điền siêu dữ liệu sau cùng thì đồng hồ gần như không
chạy.

**Đã làm:**

| Chỗ | Thay đổi |
|---|---|
| `src/gan_nhan/app.py` | Lớp `DongHo` (chạy / tạm dừng / cộng dồn), endpoint `GET` và `POST /api/dong-ho/{doc_id}/{bat-dau\|tam-dung}`, thay hẳn `POST /api/mo/{doc_id}` |
| `src/gan_nhan/giao_dien.html` | Nút "Bắt đầu bấm giờ" ⇄ "Tạm dừng" ⇄ "Tiếp tục", đồng hồ đổi màu theo trạng thái, ô tick "không đo giờ tài liệu này" |
| `src/eval/schema.py` | Hai khoá mới: `trang_thai_dong_ho` (`"da_do"` / `"khong_do"`) và `so_lan_tam_dung` |
| `src/gan_nhan/kiem.py` | Danh mục kiểm thêm ô `da_bam_gio`, đánh dấu máy tự kiểm |
| Tài liệu | Tu chính vào `PREREGISTRATION.md` và mục Sửa đổi của `ANNOTATION-GUIDELINE.md`; guideline mục 4, 6, 8 |

Chín test mới trong `tests/test_gan_nhan_app.py`, dưới tiêu đề "Đồng hồ do
người tự bấm".

**Ba quyết định thiết kế, mỗi cái có một lý do đáng nhớ:**

1. **Máy chủ giữ đồng hồ, trình duyệt chỉ vẽ lại.** Làm ngược lại thì một lần
   tải lại trang xoá sạch phép đo — mà tải lại trang là chuyện thường khi
   đang lật một PDF 40 trang.
2. **Từ chối ghi khi đồng hồ chưa từng chạy**, thay vì cảnh báo rồi vẫn ghi
   số 0. Một tài liệu quên bấm giờ chỉ lộ ra lúc gom số, và lúc đó không bấm
   lại cho quá khứ được nữa. Lối thoát là ô tick "không đo giờ tài liệu này",
   tường minh — cùng khuôn với ca để trống đơn vị tính ở guideline mục 3.1.
   Đồng hồ đã chạy thì số đo thắng lời khai, vì vứt một số đo có thật là mất
   mát không cứu lại được.
3. **Mở lại bản đã lưu KHÔNG tự chạy đồng hồ.** Thời gian sửa một ô không
   cùng đơn vị với thời gian gán nhãn một tài liệu mới, mà trung vị lấy trên
   loại thứ hai.

**Một lỗi mà test bắt được, đáng ghi vì nó sẽ tái diễn ở chỗ khác.** Bản đầu
của `DongHo` suy trạng thái từ `tong_giay > 0` — tức phân biệt "chưa bấm" với
"đang tạm dừng" bằng chính con số 0. Trên Windows, `time.monotonic()` nhảy
theo bước ~15 ms, nên bấm chạy rồi bấm dừng ngay cho ra đúng `0.0`, và đồng
hồ đã chạy trông y hệt đồng hồ chưa ai đụng vào. Đúng cái lỗi mà khoá
`trang_thai_dong_ho` đi sửa ở tầng file, lặp lại ở tầng bộ nhớ. Đã sửa bằng
khoá `da_bat_dau` riêng. **Bài học chung: đừng suy trạng thái từ một con số
bằng 0, ở bất kỳ tầng nào.**

### 19.6 Nguồn tài liệu đã chốt, và 10 tài liệu đầu đã tải — 26/08/2026

Rào chặn lớn nhất của tầng gold — "chưa biết lấy 99 tài liệu còn lại ở đâu" —
đã gỡ. Nguồn là **`finance.vietstock.vn`**, mục công bố thông tin của
HOSE/HNX/UPCoM.

**Cách lấy được danh mục theo mã.** Trang `/{MÃ}/tai-tai-lieu.htm` nạp danh
sách bằng AJAX nên `curl` trang đó không thấy gì. Danh sách thật nằm sau
`POST /data/getdocument` với thân `code={MÃ}&page={N}&__RequestVerificationToken={token}`;
token là input ẩn trong chính trang đó, và **thuộc tính HTML không đặt trong
dấu nháy** nên biểu thức tìm kiếm dạng `value="..."` trượt sạch. Bỏ `type` ra
khỏi thân yêu cầu: truyền `type=0` thì máy chủ trả mảng rỗng.

URL file rất đều, tiện cho việc mở rộng sau này:

```
https://static2.vietstock.vn/data/{HOSE|HNX|UPCOM}/{năm}/BCTC/VN/{QUY n}/{MÃ}_Baocaotaichinh_{Q n}_{năm}_{Congtyme|Hopnhat}.pdf
```

**Đã vào repo:** [data/nguon_gold.json](data/nguon_gold.json) là danh mục
nguồn (chỉ URL và siêu dữ liệu, không có số liệu tài chính, nên **vào git**),
và [src/tai_bctc.py](src/tai_bctc.py) tải chúng về `data/bctc/` (**không** vào
git). Đây chính là phương án phát hành mà `src/eval/schema.py` đã chốt từ đầu:
phát hành nhãn kèm URL nguồn và script tải, không phát hành file PDF gốc.

```
python src/tai_bctc.py                    # tải cả 10
python chay_gan_nhan.py --pdf-dir data/bctc
```

**Mười tài liệu, 5 TT99 + 5 TT200, mỗi tài liệu gánh một vai. Tính tới
26/08/2026 cả mười đã gán nhãn xong**, nằm ở `data/gold/`:

| doc_id | Vai | Đã kiểm tận mắt |
|---|---|---|
| `HPG_2026Q2_TT99` | nền, VN30, thép | tiêu đề TT99, cột VND |
| `VRE_2026Q1_TT99` | **mỏ neo scale** | `Đơn vị tính: Triệu VND` |
| `DLG_2026Q2_TT99` | **scan kém + số âm** | tiêu đề TT99, mã 420 âm 1.988 tỷ |
| `TTF_2026Q1_TT99` | **lỗ**, vốn hoá nhỏ | mới kiểm độ phân giải |
| `BMP_2026Q1_TT99` | đối chứng sạch TT99 | tiêu đề TT99, `Đơn vị tính: VND` |
| `DGC_2025Q2_TT200` | đối chứng sạch TT200 | tiêu đề TT200 |
| `HNG_2025H1_TT200` | **lỗ + `Ngàn VND` + dòng đổi tên** | cả ba, xem dưới |
| `SBT_2025Q2_TT200` | **niên độ lệch** | cột đầu năm là 30/6, không phải 1/1 |
| `MWG_2025Q1_TT200` | đối cực chất lượng ảnh | quét ~432 dpi, nét nhất lô |
| `VHC_2025Q1_TT200` | chống memorization | ngoài VN30 |

Năm trong mười là ca biên, đúng bằng tỷ lệ tập Stress mà guideline mục 7 chốt
(30/60). Cố ý: mười tài liệu này vừa là tập gold vừa là nguồn của **trung vị
nhịp gán nhãn** ở mục 19.3, nên chúng phải ĐẠI DIỆN cho tập 100, không được
dồn toàn ca dễ (trung vị tụt, đồng hồ trần người quá ngặt) cũng không được
dồn toàn ca khó (trung vị vống, đồng hồ quá rộng — đúng lỗi mà tu chính
25/08 vừa sửa).

#### Hai phát hiện làm lung lay giả định của guideline

**(a) KHÔNG có báo cáo nào là PDF chữ. Tất cả đều là ảnh quét.** Đo trên 23
tài liệu của 20 doanh nghiệp: `pdftotext` lấy ra từ 44 đến 734 byte cho cả
tài liệu 25–65 trang, tức bằng 0. Phần "text" ít ỏi ấy là chú thích chữ ký
số (`Reason: I am the author of this document`), không phải nội dung. Kiểm
lại chính `VNM_2026Q1_TT99` — tài liệu gold đầu tiên: 169 byte trên 55 trang.
Nó cũng là ảnh quét.

Hệ quả cho guideline mục 7: nhóm Stress **"bản scan chất lượng thấp"** như
viết cũ không phân biệt được gì, vì mọi tài liệu đều là bản scan. **ĐÃ SỬA
26/08/2026** — nhóm đó nay đo bằng độ phân giải bản quét; số đo, cạm bẫy và
hai tu chính kèm theo ở **mục 19.7**.

Ba con số ước lượng bằng mắt từng ghi ở đây (`MWG` ~432 dpi, `SBT` ~127 dpi,
`DGC` ~283 dpi) đều SAI và đã bỏ — chúng chia số điểm ảnh cho sai cạnh của
trang ở những tài liệu đặt ảnh xoay 90°. Số đo đúng ở mục 19.7.

Đây cũng là tin tốt cho hướng nghiên cứu: cả pipeline đi từ ảnh, nên không có
tài liệu nào "dễ" theo kiểu đọc thẳng text layer, và luận điểm đọc lại nguồn
áp cho **toàn bộ** tập gold chứ không riêng một nhóm.

**(b) Guideline mục 3.7 tự mâu thuẫn với mục 2 về hậu tố `a`/`b`.** Mục 3.7
xếp `Ký hiệu mẫu B 01a - DN` là dấu hiệu của **TT99**. Nhưng mục 2 của chính
file đó viết, in đậm: *"Hậu tố `a`/`b` của ký hiệu mẫu biểu là KỲ BÁO CÁO,
không phải Thông tư... Cả hai Thông tư đều dùng đủ ba ký hiệu"*. Hai chỗ
không thể cùng đúng.

Gặp thật khi soi: `SBT_2025Q2` mang ký hiệu `B01a-DN/HN` mà tiêu đề là *Bảng
cân đối kế toán hợp nhất* — theo mục 3.7 thì đó là "thấy dấu hiệu của cả
hai", tức phải ghi `UNKNOWN`, dù nó rõ ràng là TT200. `HNG_2025H1` cũng vậy
(`B01a-DN/HN`, *Bảng cân đối kế toán hợp nhất giữa niên độ*). Nếu không sửa,
hai tài liệu này bị gán `UNKNOWN` một cách máy móc và tỷ lệ TT99/TT200 vỡ.
**ĐÃ SỬA 26/08/2026** — tu chính ở mục Sửa đổi của
`ANNOTATION-GUIDELINE.md`: bảng mục 3.7 bỏ hẳn dòng ký hiệu mẫu, hai dòng số
hiệu thông tư lên trước vì chắc chắn hơn, và thêm luật phủ định cấm suy ra
Thông tư từ hậu tố. Cả hai file gold giữ nhãn `TT200`, không gán nhãn lại.
Cùng lượt sửa luôn một chú thích trong `src/extract_vlm.py` vẫn chép lại quy
tắc sai ấy — `FORM_MARKERS` trong `src/fields_config.py` thì đã đúng từ
`023321c`, tức code đã đi trước tài liệu ở chỗ này.

#### Một mã đáng thêm vào tập Stress về sau

`MSN_2026Q2` (Masan, đã tải thử): mục lục báo cáo quý 2 **năm 2026** ghi
*Bảng cân đối kế toán (Mẫu số B01a-DN)* — tên gọi TT200 trên một kỳ mà TT99
đã có hiệu lực. Chưa soi tới trang biểu mẫu thật nên chưa kết luận. Nếu đúng
là doanh nghiệp giữ tên gọi cũ sau ngày TT99 hiệu lực thì đó là ca nhận diện
chuẩn khó nhất có thể có, và **quy tắc "2026 thì là TT99" sai** — quy tắc ấy
đang được dùng ngầm để chọn tài liệu, tuy không dùng để gán nhãn.

### 19.7 Độ phân giải bản quét — số đo và cạm bẫy, 26/08/2026

Đây là chỗ trả lời Câu 10. Nhóm Stress thứ ba của guideline mục 7 đổi từ "bản
scan chất lượng thấp" — tiêu chí mà 100% quần thể thoả, tức không chia được
nhóm nào — sang **độ phân giải bản quét**, ghi làm **biến liên tục**.

**Công cụ:** `python src/do_do_phan_giai.py` in bảng, thêm `--ghi` thì ghi
vào khoá `do_phan_giai_dpi` của từng mục trong `data/nguon_gold.json`. Đừng
sửa tay khoá đó.

| doc_id | dpi (trung vị) | Ghi chú |
|---|---:|---|
| `SBT_2025Q2_TT200` | **89,9** | thấp nhất lô, kèm trang lệch |
| `DLG_2026Q2_TT99` | **100,0** | kèm trang lệch và nhoè |
| `HNG_2025H1_TT200` | **143,9** | tài liệu DUY NHẤT trộn nhiều độ phân giải: có trang tới 300 |
| `HPG_2026Q2_TT99` | 200,0 | |
| `VRE_2026Q1_TT99` | 200,0 | |
| `TTF_2026Q1_TT99` | 200,0 | |
| `BMP_2026Q1_TT99` | 200,0 | |
| `DGC_2025Q2_TT200` | 200,0 | |
| `VHC_2025Q1_TT200` | 200,0 | |
| `MWG_2025Q1_TT200` | **295,8** | cao nhất lô |

Dải 89,9–295,8 dpi, trung vị 200,0.

**Giới hạn đọc thẳng ra khỏi bảng: sáu trong mười rơi đúng 200,0 dpi.** Phân
bố dồn cục chứ không trải đều, nên ở quy mô mười tài liệu sức phân biệt của
trục này nằm gần hết ở hai đuôi. Đủ 100 tài liệu thì đo lại phân bố TRƯỚC khi
tin vào một hệ số tương quan nào.

**Cạm bẫy đã mất thời gian, đừng lặp lại: `horizontal_dpi` và `vertical_dpi`
của pdfium SAI ở trang đặt ảnh xoay.** Hai trường đó chỉ chia cho phần đường
chéo của ma trận đặt ảnh. Ma trận xoay 90° có đường chéo bằng 0 và giá trị
nằm ở hai ô còn lại, nên pdfium chia nhầm cạnh. `SBT_2025Q2_TT200` bị báo
`127,3 / 63,5` dpi — trông như bản quét bị kéo dãn gấp đôi theo một chiều —
trong khi sự thật là **90 dpi đều cả hai chiều**, chỉ thấp chứ không méo.

Cách đúng là chiếu qua ma trận: cạnh ngang của ảnh trải theo véc-tơ `(a, b)`,
cạnh dọc theo `(c, d)`, lấy chuẩn Euclid từng véc-tơ. Đúng cho cả trang xoay
lẫn trang thẳng. Đã chốt bằng test ở `tests/test_do_do_phan_giai.py`.

Cùng cái bẫy ấy giải thích ba con số ước lượng bằng mắt trước đó: `MWG` ~432
(thật: 295,8), `DGC` ~283 (thật: 200,0), `HNG` ~204 (thật: 143,9). Cả ba đều
là số điểm ảnh chia cho **chiều rộng** trang trong khi ảnh nằm xoay. Chúng đã
bị bỏ khỏi `da_kiem` của `data/nguon_gold.json` để file không mang hai con số
chỏi nhau cho cùng một thứ.

**Hai tu chính đã ghi.** Guideline mục Sửa đổi ghi việc đổi tiêu chí nhóm
Stress. `PREREGISTRATION.md` mục Sửa đổi ghi độ phân giải thành **hiệp biến
đăng ký trước**: được dùng cho phân tích THỨ CẤP và cho việc chọn tài liệu
theo thứ hạng, **không** được dùng để loại tài liệu khỏi phân tích chính, và
không đổi chỉ số chính hay điều kiện phản chứng của giả thuyết nào. Lý do
phải đăng ký: một biến giải thích mới rất dễ bị lôi ra sau khi bảng kết quả
đã xong để giải thích một chênh lệch không mong đợi, và lúc đó không ai phân
biệt được nó với việc đi tìm hậu nghiệm.

**Không có ngưỡng nào được chốt**, cố ý — chốt "thấp là dưới X dpi" trên một
phân bố dồn cục của mười tài liệu là chọn tham số trên mẫu mỏng. Ngưỡng, nếu
về sau cần, phải là tu chính riêng ghi trước khi nhìn bảng kết quả tương ứng.

**Độ phân giải không bao trọn chữ "chất lượng".** Trang lệch, dấu mộc đỏ đè
lên chữ số, in mờ lệch nét là những trục riêng mà máy chưa đo được —
`VHC_2025Q1_TT200` ghi đúng mấy thứ đó trong `notes`. Hệ quả phải nêu trong
bài: tương quan bằng 0 với dpi KHÔNG cho phép kết luận chất lượng ảnh không
ảnh hưởng.

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

### Bốn bước đã thi công — tra hash khi cần chi tiết

| Bước | Việc | Commit |
|---|---|---|
| A | Đưa `standard` đi tới nơi cần dùng: `router.py` gọi `validate_result()` ở ba chỗ mà không truyền `standard`, nên mọi tài liệu bị kiểm bằng đẳng thức TT99. Sửa kèm việc `router.py` đè `meta` thật, làm đầu ra khai sai chuẩn và đánh rơi `early_stop` với `prompt_hash` | `fa5c6d2` |
| B | Ghi `0` của dòng vắng mặt vào cả `data` đầu ra kèm khoá trạng thái tường minh, thay vì chỉ tồn tại trong bước kiểm đẳng thức | `88a77f5` |
| C1 | Hợp đồng của probe: trả ba trạng thái — có dòng, không có dòng, không kết luận được | `19fe938` |
| C2 | Probe dò theo mã số dòng trên text OCR của vùng bảng đã cắt | `ada6f75` |

Bước A phải đi trước vì C cần biết "dòng này có trên biểu mẫu của chuẩn này
không", mà câu đó chỉ trả lời được khi `standard` đã tới nơi.


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
chuẩn.

**ĐÃ ĐO, và tiền đề ĐÚNG** — `data/output/tieu_de_trong_vung_cat.md`, chạy
trên 12 trang đầu báo cáo VNM. Trang mang bảng thật: 2/12 (phần còn lại YOLO
không thấy bảng nên `ca_trang()` trả nguyên trang, và câu hỏi vùng cắt không
đặt ra ở đó). Trang mang bảng mà **TÊN báo cáo lọt vào vùng cắt: 0/2**. Cả
hai lần `detect_standard()` kết luận được đều **nhờ SỐ HIỆU thông tư**, một
dấu hiệu khác hẳn — mà số hiệu chỉ có trên báo cáo còn nhắc văn bản ban hành
nên có thể vắng hoàn toàn ở tài liệu khác, và mẫu `99\s*/\s*2025` cho `\s*`
nuốt cả xuống dòng nên còn khớp oan được.

Phép đo ấy đo trên **một** tài liệu nên đủ để loại một hướng sai, chưa đủ để
chốt hướng đúng. Nay đã có 10 tài liệu ở `data/bctc/` (mục 19.6) nên **đo lại
trên nhiều công ty là việc rẻ và nên làm trước khi chọn hướng**.

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
