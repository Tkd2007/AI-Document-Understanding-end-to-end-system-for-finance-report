# Nhật ký thay đổi — ViFinKIE

Mỗi mục ghi **thay đổi**, **lý do**, và **hiệu quả đo được**. Cột hiệu quả là
lý do file này tồn tại: khi viết bài, mọi câu dạng "chúng tôi cải thiện X"
phải trỏ được về một con số đo trước và sau, chứ không phải về một commit.

**Quy ước đọc:**

- *Đã đo* — có số trước và sau, kèm nơi lấy số.
- *CHƯA đo* — thay đổi đã thi công nhưng chưa có phép đo. Không được viết
  vào bài như một cải thiện.
- *Không đo được* — thay đổi thuộc loại không có chỉ số (tài liệu, quy ước).

Lịch sử đầy đủ ở `git log`; file này chỉ giữ những thay đổi **đổi con số
hoặc đổi kết luận**. Trạng thái hiện tại ở `HANDOFF.md`; cam kết nghiên cứu ở
`PREREGISTRATION.md` mục Sửa đổi; quy tắc gán nhãn ở `ANNOTATION-GUIDELINE.md`
mục Sửa đổi.

---

## 04/09/2026

### Bốn bản vá sau lượt chấm đầy đủ đầu tiên — lỗi câm 5,48% xuống 4,05%

Lượt chấm 70 tài liệu ngày 03/09 lộ ra bốn khuyết tật, ba trong bốn nằm ở
chính cơ chế thi công cùng ngày. Vá xong rồi chấm lại trọn 70 tài liệu.

| Chỉ số | Trước | Sau |
|---|---:|---:|
| Trường đúng | 1674/1854 = 90,29% | **1681/1854 = 90,67%** |
| **Lỗi câm** | 97/1771 = **5,48%** | **71/1752 = 4,05%** |
| Tài liệu trọn vẹn | 16/70 | **17/70** |
| Nhận đúng đơn vị | 67/70 | 67/70 |

**Tám tài liệu đổi, không tài liệu nào xấu đi.** Đây là bảng đáng đọc hơn
bảng gộp, vì nó cho biết cơ chế nào ra tay ở đâu:

| Tài liệu | Trước | Sau | Cơ chế đã ra tay |
|---|---|---|---|
| `VHC_2025Q1_TT200` | 14/26, cam 11 | **17/26, cam 4** | cổng điền 0 + rút quyền từ chối |
| `GVR_2026Q2_TT99` | 23/27, cam 4 | 23/27, **cam 0** | trần biểu mẫu (`bieu_mau_da_di_qua`) |
| `MSN_2020Q3_TT200` | 21/26, cam 5 | 21/26, **cam 1** | cổng `CO_THE_VANG_MAT` |
| `VNM_2023Q2_TT200` | 17/26, cam 9 | 17/26, **cam 5** | cổng `CO_THE_VANG_MAT` |
| `VJC_2022Q1_TT200` | 22/26, cam 4 | 22/26, **cam 1** | cổng `CO_THE_VANG_MAT` |
| `FPT_2023Q3_TT200` | 24/26, cam 2 | **26/26, cam 0** | rút quyền từ chối |
| `REE_2023Q2_TT200` | 23/26, cam 1 | **25/26**, cam 1 | rút quyền từ chối |
| `FLC_2021Q4_TT200` | 12/26, cam 2 | 12/26, **cam 0** | trần nhánh OCR |

Tổng: **trường đúng +7, lỗi câm −26**.

**Phần lớn mức giảm là chuyển lỗi CÂM thành lỗi ỒN, không phải đọc đúng
thêm.** Trường đúng chỉ nhích 0,38 điểm trong khi lỗi câm giảm 1,43 điểm —
đúng như thiết kế, và đúng thứ tự ưu tiên mà `src/eval/metrics.py` tuyên bố:
một ô trống thì người ta biết mà đi tra, một con số sai thì không.

**Bốn bản vá:**

- `de62355` — phép số học của `chan_ung_vien` **mất quyền từ chối**, chỉ còn
  chẩn đoán. Nó ra tay 8 lần ở lượt trước: đúng 1, sai 7, trong đó 6 lần vứt
  đi giá trị đúng tới từng đồng. Nguyên nhân: cận suy từ dấu neo vào giá trị
  ĐÃ NHẬN, nên khi giá trị đã nhận là thứ sai thì cận thành thước hỏng.
- `028ff25` — `CO_THE_VANG_MAT`, danh sách trắng tám dòng chi tiết được phép
  vắng mặt. Trước đó probe bảo "không thấy dòng" là điền 0 vô điều kiện, cho
  ra 27 ô đúng và 22 ô sai; 22 ô sai đều ở dòng xương sống của biểu mẫu.
- `5d4fc86` — ghi ra `dang_thuc_khong_kiem_duoc` thay vì bỏ qua im lặng.
  Lượt này đo được **77 lần** đẳng thức không kiểm được.
- `7f7401f` — trần nhánh VLM = trang nhánh OCR đã dừng. Ra tay **2 lần**
  (`DLG`, `FLC`), không làm mất ô đúng nào.

**Một lỗi câm trong chính hệ ghi chép, vá ở `01e0dcb`.** `_ghi_lai_luot_vlm()`
là allowlist, và `cad32fc` thêm khoá vào `chay_tap_gold.py` mà quên thêm vào
đó: cơ chế chạy, log in ra, cột tồn tại, nhưng cột nhận `None` ở mọi tài liệu.
Phát hiện vì bảng điểm nói "mâu thuẫn 0" trong khi log của cùng lượt chạy ghi
9 dòng. Lượt này đã nạp mã cũ nên hai cột ấy vẫn rỗng — số tra ở log.

**Cạm bẫy đã trả giá, ghi lại kẻo lặp:** `commit_hien_tai()` ghi mã commit
lúc CHẤM XONG một tài liệu, không phải mã đã nạp vào tiến trình. Lượt này ghi
ra bốn mã khác nhau vì tôi commit trong lúc nó chạy, nhưng cả 70 tài liệu đều
chạy trên đúng một ảnh mã đã nạp lúc khởi động (`7f7401f`) — Python không nạp
lại module khi file trên đĩa đổi. **Đừng đọc bốn mã ấy thành một lượt trộn.**
Muốn tránh hẳn thì đừng commit trong lúc chấm.

## 31/08/2026

### Đơn vị tính buộc theo BẢNG, không buộc theo tài liệu

Tiền đề "mỗi tài liệu một đơn vị tính" sai trên hồ sơ thật.
`HNG_2025H1_TT200` là công văn giải trình gửi HNX kèm BCTC: trang 1 khai
`ĐVT: tỷ đồng` cho một bảng hai dòng, các trang sau là BCTC khai `Ngàn VND`.
Pipeline đối xử với đơn vị như một chỉ tiêu bình thường nên **vùng đầu tiên
đọc được chốt cho cả tài liệu và không bao giờ được đọc lại** — công văn thắng
bảng cân đối, và 24/26 chỉ tiêu sai đúng `1e6` lần dù mọi chữ số đọc ra đều
đúng tuyệt đối.

Không đẳng thức nào bắt được (`Aδ = (c−1)Ax* = 0`, `PREREGISTRATION.md` mục 0),
và mỏ neo biên độ lớn chỉ **lọc** chứ không **sửa**: với tổng tài sản thô
`18.281.308.818` thì cả `×1e3` lẫn `×1` đều nằm trong biên. Quan trọng hơn,
**không hệ số toàn cục nào đúng được** cho tài liệu này — `loi_nhuan_sau_thue`
đọc từ đúng bảng `tỷ đồng` nên chọn `nghìn đồng` sẽ làm ô đó sai `1e6` lần theo
chiều ngược lại.

Thi công ở `extract_vlm._he_so_vung()` (đọc được thắng kế thừa, ngưỡng quá bán
chặn ghi đè bằng phiếu yếu) và tham số `he_so_theo_truong` của
`validate_result()`. Không mua thêm lời gọi VLM nào: prompt vốn đã bắt model
trả `don_vi_tinh` cho mọi vùng. Certificate ở `meta["don_vi_theo_vung"]`.

*Đã đo* — `--chuan-tu-gold --chi HNG`, `BAT_TANG_REPAIR=true`, cùng cấu hình
lượt 30/08. Kết quả: `data/output/tap_gold_chuan_tu_gold_HNG_2026-08-31.json`.

| `HNG_2025H1_TT200` | 30/08 | 31/08 |
|---|---:|---:|
| Trường đúng | 2/26 = 0,077 | **21/26 = 0,808** |
| Lỗi câm | 24/26 | **5/26** |
| Hệ số đơn vị | ✗ `1e9` | **✓ `1e3`** |

Certificate: 18 vùng, 8 đọc được đơn vị, 10 kế thừa; 25 ô mang hệ số `1000`,
một ô mang `1e9`.

**CHƯA đo trên 9 tài liệu còn lại.** Cơ chế mở ra một chế độ lỗi mới — mỗi bảng
là một cơ hội đọc sai đơn vị thay vì một lần cho cả tài liệu — nên chín tài
liệu kia là phép thử hồi quy bắt buộc. Con số gộp **232/265 = 0,875** là ngoại
suy giả định chúng không đổi, **không được viết vào bài như một cải thiện đã
đo**. Chi tiết ở `HANDOFF.md` mục 20.8.

Bốn trong năm ô còn sai của HNG chỉ lệch **dấu** (Câu 14, đang chờ người chủ
trì), không liên quan tới đơn vị.

### Mã 51/52 lưu theo dấu có hướng; đẳng thức mã 60 thành tổng thuần

Quy tắc cũ ghi mã 51/52 "giữ nguyên dấu như in" — dựa vào cách trình bày, mà
cách trình bày **không nhất quán ngay trong một báo cáo**. `VRE_2026Q1_TT99`
in mã 51 trong ngoặc đơn còn mã 52 ngoài ngoặc, ngược với nghĩa của hai dòng;
người gán nhãn đã ghi chỗ vênh đó vào `notes` ngày 26/08/2026. Quy tắc mới ghi
theo **nghĩa kinh tế** — tiền đi ra khỏi lợi nhuận thì âm — nên đẳng thức thành
`Mã 60 = Mã 50 + Mã 51 + Mã 52`.

Dạng này cố ý khác chữ trong TT200 Điều 113 mục 3.18
(`Mã số 60 = Mã số 50 - (Mã số 51 + Mã số 52)`). **Hai dạng là cùng một phương
trình**, chỉ khác chỗ dấu nằm ở dữ liệu hay ở công thức.

Mười một file gold lật dấu bằng script; cả mười một cân tới từng đồng sau khi
lật. Không tài liệu nào phải gán nhãn lại — phép biến đổi là song ánh và cơ
học, lý do ghi ở `ANNOTATION-GUIDELINE.md` mục Sửa đổi 31/08/2026.

*Không đo được* trên chất lượng trích xuất, và đây là chỗ dễ tưởng nhầm:

- **Identifiability KHÔNG đổi**, đã sinh lại `data/output/identifiability_*.md`
  trước và sau — cùng 7/26 chỉ tiêu định vị được, cùng `dim null(A)`, cùng danh
  sách cặp không phân biệt được. Đổi vế chỉ lật dấu hai cột, mà quan hệ tỷ lệ
  giữa các cột bất biến với phép lật ấy. **Đừng viết vào bài như một cải thiện
  định vị.**
- Cái được là ở khâu gán nhãn (quy tắc phát biểu được thành một câu không phụ
  thuộc cách in) và ở hình dạng bộ ràng buộc (cả chín đẳng thức cùng dạng tổng
  thuần, bỏ được ngoại lệ xử lý dấu).

**Mốc so sánh bị cắt tại đây.** Mọi kết quả chấm trước 31/08/2026 dùng gold quy
ước cũ nên **không so thẳng** với lượt sau ở hai ô 51/52. Cụ thể, lượt HNG cùng
ngày được ghi 21/26 dưới quy ước cũ; chấm lại chính bộ dự đoán ấy với gold mới
ra **20/26**.

### Cắt chi phí đọc tài liệu lúc mở phiên

*Không đo được* — thay đổi thuộc loại tài liệu và quy ước.

Repo không có `CLAUDE.md`, nên mỗi phiên Claude mới nạp trọn `HANDOFF.md`
(~32.500 token) để lấy về vài nghìn token thật sự dùng. Chia lại theo **tần
suất đọc**: `CLAUDE.md` (~2.500 token, tự nạp, có bảng định tuyến theo việc),
`HANDOFF.md` còn trạng thái sống, `docs/lich-su/HANDOFF-da-dong.md` giữ hồ sơ
đã đóng **nguyên văn và nguyên số mục**, kỹ năng `chay-tap-gold` cho quy trình
chỉ dùng khi chạy tập gold. `PREREGISTRATION.md` chỉ được **thêm** mục lục,
nội dung gốc không sửa một chữ.

## 28/08/2026

### Luật dấu bằng residual — một luật định vị chứng minh được (Ý tưởng 1)

Nếu chỉ tiêu j bị đọc lộn dấu thì `x̂ⱼ = −x*ⱼ`, nên residual của hệ bằng đúng
`A·δ = 2x̂ⱼ·A[:, j]` — một bội số của **cột j**, hệ số là hai lần con số đang
cầm trong tay. Đây là hệ quả đại số tất yếu, cùng loại lập luận với chứng minh
`Aδ = (c−1)Ax* = 0`, chỉ khác chiều: ở đó chênh lệch nằm trọn trong không gian
null nên vô hình, ở đây nó nằm trọn trên một cột nên **chỉ đúng tên được**.

Thi công ở `src/repair/luat_dau.py`, nối vào `diagnose()` thành một **nguồn
định vị riêng** (`Diagnosis.nguon_dinh_vi`). Tầng repair nối vào pipeline sau
cờ `BAT_TANG_REPAIR`, **mặc định tắt**.

*Đã đo* — `PYTHONPATH=src python src/eval/do_luat_dau.py`, chạy lại trên kết
quả đã lưu, **không tốn lệnh gọi API**:

| Điều kiện | Trường đúng | Lỗi câm |
|---|---:|---:|
| Thô — như pipeline đã ghi ra | 216/265 = 81,5% | 24/240 = 10,0% |
| Sau `chuan_hoa_dau()` (`a0cd5ab`) | 222/265 = 83,8% | 18/240 = 7,5% |
| **Sau + tầng repair** | **224/265 = 84,5%** | **16/240 = 6,7%** |

| Phán xử của luật (điều kiện B) | Số tài liệu |
|---|---:|
| Im lặng đúng — không có lỗi dấu để bắt | 7 |
| **Định vị đúng** | **2** |
| Bỏ sót | 1 |
| **Báo nhầm** | **0** |

**Thu hoạch mỏng và phải nói thẳng: 2 ô trên 265.** `chuan_hoa_dau()` đã lấy
hết phần dễ ở cùng chế độ lỗi. Giá trị nằm ở hai chỗ khác:

1. **Nó phân xử Câu 13 bằng số liệu.** Cả hai lần ra tay đều rơi đúng vào
   `thue_tndn_hoan_lai` của MWG và VRE — chỉ tiêu mà guideline cũ bắt ghi
   dương. Luật quyết định dấu mã 52 theo từng tài liệu, từ chính số liệu, và
   cả hai lần đều trùng nhãn gold. Nó **không cần** tới mệnh đề "dương khi mã
   60 < mã 50" đã bị bác bỏ.
2. **Báo nhầm 0/10.** Sáu đẳng thức lệch còn lại không phải lỗi dấu (nhầm chữ
   số, nhầm bảng) và luật im lặng ở cả sáu. Đó vừa là điểm mạnh vừa là giới
   hạn: nó phủ 2/8, không phải 8/8.

**Ba tính chất được khoá bằng test, đừng nới:**

- **Tập ứng viên vẫn ĐÓNG ở đường tắt của luật.** Luật chỉ được ÁP giá trị lật
  dấu khi giá trị ấy đã có sẵn trong tập ứng viên sinh từ tài liệu; truyền vào
  tập rỗng thì nó lui về vai trò chẩn đoán và trả ABSTAIN. Có đường nào để một
  con số ngoài tập lọt vào kết quả thì hệ ép số được và cả lập luận chống bịa
  sụp.
- **Hai mức, và chỉ mức toàn cục được sửa.** `dinh_vi_duoc` là lật dấu đưa CẢ
  vector residual về 0. `nghi_ngo` là lật dấu làm cân mọi đẳng thức chứa chỉ
  tiêu đó nhưng tài liệu còn lỗi khác — chẩn đoán thì dùng được, sửa thì không,
  vì sau phép sửa bảng vẫn không cân nên không có gì xác nhận nó đúng. Ở điều
  kiện A (trước bản vá), MWG/VRE/HNG đều rơi vào `nghi_ngo` và luật chỉ đúng
  tên `gia_von_hang_ban` ở cả ba.
- **Tầng repair chạy SAU `validate_result()`, và không chạy khi
  `DISABLE_CONSTRAINT_GATE` bật.** `warnings` phải ghi tình trạng vi phạm ràng
  buộc của đầu ra CHƯA sửa — đó đúng là biến H1 đem so với confidence. Đảo thứ
  tự thì cột warnings gần như phẳng và phép so mất nghĩa.

**Ca luật KHÔNG cứu được, đã chốt bằng test:** chọn nhầm bảng. Bộ số lấy từ
bảng khác tự nó cũng cân nên `residual = 0` tuyệt đối — SBT có 8 trường sai mà
luật báo `im_lang`, đúng như phải vậy. Đây là giới hạn của thông tin, không
phải của thuật toán.

### Nhánh OCR có bộ đếm kiên nhẫn (Ý tưởng 2)

`run_ocr_first()` trước đây chỉ dừng khi `is_acceptable()` đúng — điều kiện đòi
regex khớp TÊN chỉ tiêu tiếng Việt có dấu, đúng chỗ EasyOCR đọc hỏng. Thêm
`PATIENCE_PAGES_OCR = 10`: mười trang liên tiếp không trích thêm được chỉ tiêu
nào thì dừng, nhánh VLM đọc tiếp từ đó.

**Vì sao 10 chứ không phải 3 như nhánh VLM** — bản đầu để 3 và đó là một lỗi:
nhánh VLM chỉ bắt đầu đếm SAU khi đã đủ field bắt buộc, tức sau khi đã vào tới
phần bảng, còn nhánh này không có cái gác ấy nên bộ đếm chạy ngay từ trang 1.
Mà trang đầu báo cáo niêm yết là bìa, trang ký, mục lục, phần giới thiệu — để 3
thì vòng lặp dừng ở trang 3, TRƯỚC khi tới bảng nào, và nhánh OCR thành vô dụng
một cách **im lặng**. Trên tập gold, bảng B01 sớm nhất ở trang 4 (BMP) và muộn
nhất ở trang 5 (SBT). Ngưỡng này vì thế không phải tham số tinh chỉnh tốc độ mà
là điều kiện để nhánh OCR còn chạy; có test khoá `>= 10` và một ca hồi quy
"bảng bắt đầu ở trang 9".

*Đã đo, trước khi sửa* — trên `metrics.jsonl` của lượt chấm gold:

| | |
|---|---:|
| Lần `run_ocr_first` dừng sớm | **0 / 9** |
| Trang được quét | **100%** số trang của mọi tài liệu |
| OCR chiếm | **77%** tổng thời gian chạy (5,28 / 6,84 giờ) |
| Mỗi trang OCR | ~27,6 giây |

*CHƯA đo hiệu quả sau khi sửa* — cần một lượt chạy thật. Bảy test khoá hành vi
(dừng đúng trang, bộ đếm đặt lại khi gặp chỉ tiêu mới, generator không bị tiêu
thụ quá chỗ đã dừng), nhưng số giờ tiết kiệm được thì phải chạy mới biết.

**Quyết định ngược với đề xuất ban đầu: KHÔNG nâng `PATIENCE_PAGES` của nhánh
VLM.** Cơ chế đó đã có và đang chạy tốt — kích hoạt 9/10 tài liệu, dừng ở trang
6–18 của tài liệu 25–62 trang, 7–18 lượt gọi mỗi tài liệu. Nâng nó là nới đúng
nhánh đang được kiểm soát tốt và **không chạm nhánh chiếm 77% chi phí**.

**Cố ý KHÔNG gác điều kiện dừng sau `has_required_fields()`** như nhánh VLM
làm: ở nhánh regex điều kiện ấy gần như không bao giờ đúng, nên gác vào là dựng
lại đúng vòng lặp không có trần mà bộ đếm sinh ra để cắt.

**Cái giá, chưa đo:** probe dò dòng chỉ đọc `cached_pages`, nên nhánh OCR dừng
sớm hơn thì probe thấy ít trang hơn và kết luận "dòng vắng mặt trên biểu mẫu"
có thể đổi. Số trang probe thật sự đọc nay ghi vào `metrics.jsonl` dưới khoá
`probe_so_trang`, cùng với `ocr_dung_som` — hai lượt chạy khác cấu hình vì thế
so được với nhau. **Phải đo, không đoán.**


### Dọn tài liệu: mỗi loại sự kiện về đúng một file

Tài liệu của repo phình lên vì mỗi phiên chỉ biết **thêm vào**: cùng một phép
đo được chép lại ở `HANDOFF.md`, ở khối trạng thái của bốn file nguồn, và ở
mục Sửa đổi của hai file cam kết. Chép nhiều bản thì bản nào cũng thành nghi
vấn khi chúng lệch nhau, và không bản nào dám xoá.

Phân vai sau khi dọn — quy tắc để phiên sau khỏi chép lại:

| File | Giữ gì | KHÔNG giữ gì |
|---|---|---|
| `README.md` | cách chạy, cách cài, hiện trạng từng khối | lịch sử, thiết kế nghiên cứu |
| `HANDOFF.md` | hiện trạng, câu hỏi đang chờ, bẫy còn ràng buộc, bước kế tiếp | số đo trước/sau, quy tắc gán nhãn, cam kết |
| `CHANGELOG.md` | thay đổi + lý do + **hiệu quả đo được** | hiện trạng |
| `PREREGISTRATION.md` | giả thuyết, kế hoạch phân tích, **sổ tu chính** | số đo |
| `ANNOTATION-GUIDELINE.md` | quy tắc gán nhãn, **sổ tu chính** | số đo |
| `MD file/*.md` | bản gốc 20/08, đóng băng | mọi thứ khác — chỉ một khối trỏ đi nơi khác |

*Đã đo* — đếm dòng trước và sau:

| File | Trước | Sau | |
|---|---:|---:|---|
| `HANDOFF.md` | 2 271 | **1 588** | −30% |
| `MD file/BUILD-SPEC.md` | 1 307 | 1 284 | khối trạng thái 52 → 25 dòng |
| `MD file/FINAL-proposal…` | 603 | 536 | khối trạng thái 94 → 26 |
| `MD file/ADDENDUM…` | 358 | 301 | khối trạng thái 81 → 24 |
| `MD file/FINAL-repo-changes` | 333 | 288 | khối trạng thái 71 → 25 |
| **Tổng bộ tài liệu** (trừ CHANGELOG) | **7 884** | **6 542** | **−17%** |

**Hai mục cố ý KHÔNG bị nén, và lý do phải nhớ:** mục Sửa đổi của
`PREREGISTRATION.md` và của `ANNOTATION-GUIDELINE.md`. Một bản đăng ký trước
rút gọn được sau khi thấy kết quả thì không chứng minh được gì; nén chúng là
phá đúng thứ chúng tồn tại để bảo vệ. Chỗ duy nhất được đụng tới: một tu chính
đã bị tu chính sau thay thế trọn vẹn (27/08 về mã 52) rút còn một đoạn ghi
nhận kèm con trỏ tới bản thay thế, và tu chính 26/08 về ba dòng khấu trừ được
gắn cảnh báo "đã bị sửa một phần" ở đầu.

Kèm theo: xoá `data/output/moc3.md` (trùng **byte-for-byte** với
`moc3_26082026.md`), và sửa ba con số đã cũ trong `README.md` — 318 → 510
test, "mới verify tay trên một báo cáo" → 10 tài liệu đã chấm, và bảng kết quả
gold thay cho ước lượng "88–92%" của lượt chạy chưa xong.

### Nhánh OCR quét 100% số trang vì không có bộ đếm kiên nhẫn

Đối chiếu `.env` với tài liệu phát hiện hai chỗ vênh cùng lúc: máy phát triển
đặt `USE_OCR_FIRST=true` trong khi docstring `router.py` nói nhánh này tắt mặc
định, và `run_ocr_first()` **không có bộ đếm kiên nhẫn** như nhánh VLM — nó chỉ
dừng khi `is_acceptable()` đúng, mà điều kiện đó đòi regex khớp tên chỉ tiêu
tiếng Việt có dấu, đúng chỗ EasyOCR đọc hỏng.

*Đã đo* — trên `metrics.jsonl` của lượt chấm gold, **không tốn lệnh gọi API**:

| | |
|---|---:|
| OCR chiếm | **77%** tổng thời gian chạy (5,28 / 6,84 giờ) |
| Mỗi trang OCR | ~27,6 giây |
| Trang được quét | **100%** số trang của mọi tài liệu |
| Lần `run_ocr_first` dừng sớm | **0 / 9** |
| Lần `PATIENCE_PAGES` kích hoạt ở nhánh VLM | **9 / 10**, dừng ở trang 6–18 |

Nhánh VLM tốn 7–18 lượt gọi mỗi tài liệu — nó đang được kiểm soát tốt, nên
**nâng `PATIENCE_PAGES` là nới nhầm nhánh**: nó không chạm tới nhánh chiếm 77%
chi phí.

*CHƯA đo hiệu quả của việc tắt.* Cái giá phải cân trước: probe dò dòng
(`do_dau_vet_dong`) chỉ đọc `cached_pages`, nên tắt OCR-first thì nó thấy ít
trang hơn và kết luận "dòng vắng mặt trên biểu mẫu" có thể đổi. Phải chạy lại
2 tài liệu để đo, không được đoán.

**Hệ quả cho việc trích dẫn:** lượt chấm gold 27/08 chạy với
`USE_OCR_FIRST=true`, tức một cấu hình khác cấu hình tài liệu mô tả — một số
giá trị có thể đến từ nhánh regex chứ không từ VLM. Docstring `router.py` và
`run_ocr_first()` đã sửa để mô tả đúng hiện trạng này.


### Câu 13 — mã 51 và 52 giữ nguyên dấu như in, quy tắc cũ đã sai

Guideline mục 3.3 quy định hai dòng thuế "ghi dương khi mã 60 < mã 50".
Mệnh đề đó đúng cho **tổng** hai dòng thuế nhưng sai khi áp riêng từng dòng,
vì `Mã 60 = Mã 50 − Mã 51 − Mã 52` chỉ ràng buộc tổng. Người chủ trì phân xử:
**nhãn gold đúng, guideline sai**.

*Đã đo* — rà toàn bộ 11 file `data/gold/`:

| | Số tài liệu |
|---|---:|
| Mã 51 âm | 0 |
| Mã 52 âm | 3 — `HNG`, `MWG`, `VRE` |
| Đẳng thức `mã 60 = mã 50 − mã 51 − mã 52` lệch | 0 |

Ba tài liệu có mã 52 âm đều cân đẳng thức tới từng đồng → dấu âm là số liệu
thật. **Không nhãn nào phải sửa, không hành vi code nào đổi**: `chuan_hoa_dau()`
đã cố ý bỏ mã 52 ra ngoài từ `a0cd5ab`, và `kiem_dau_khau_tru()` vốn đã xét
theo tiêu chí "lật dấu làm cân đẳng thức".

**Chỗ vênh còn lại, đã ghi vào docstring:** `chuan_hoa_dau()` vẫn xét mã 51
bằng chiều mã 50/60, chặt hơn guideline mới. Vô hại trên dữ liệu hiện có (mã
51 dương ở cả 11 file) nhưng sẽ lật nhầm nếu gặp mã 51 âm hợp lệ. Đóng nó
bằng cách chuyển quyết định dấu sang tầng repair.

### Câu 12 — tài liệu đã chạy pipeline bị loại khỏi tập gán nhãn đôi (`6a6a90d`)

Phương án đo đồng thuận đang dùng là người chủ trì tự gán nhãn lại, nên người
gán lại chính là người đã chạy pipeline, mà `data/output/tap_gold_*.json` giữ
giá trị máy đoán cho **từng ô**. Một lượt gán nhãn bị neo vẫn cho ra
Krippendorff alpha bình thường, không dấu vết — nên ràng buộc phải nằm ở khâu
**chọn** tài liệu và phải kiểm được bằng máy.

*Đã đo* — `PYTHONPATH=src python src/eval/tap_dong_thuan.py`:

| | |
|---|---|
| Tài liệu đủ điều kiện gán nhãn đôi | **0 / 11** |
| Bị loại vì đã chạy pipeline | 10 (danh mục) + `VNM_2026Q1_TT99` (ngoài danh mục) |

**Hiệu quả không nằm ở một tỷ lệ mà ở lịch:** lượt gán nhãn đôi không bắt đầu
được cho tới khi tập gold vượt mốc 11 tài liệu. Mốc hai tuần 09/09/2026 chỉ là
điều kiện cần. Phát hiện kèm theo: `VNM_2026Q1_TT99` có nhãn gold và có đầu ra
pipeline nhưng không nằm trong danh mục nguồn — đúng loại tài liệu dễ lọt nhất
vì không sổ nào ghi rằng đáp án của nó đã lộ.

---

## 27/08/2026

### Quy tắc dấu ba dòng khấu trừ (`a0cd5ab`)

`parse_number()` không biết mình đang đọc chỉ tiêu nào nên áp "ngoặc là âm"
cho cả hai nghĩa của dấu ngoặc trên trang B02: ở mã 40 là số liệu, ở mã 11 chỉ
là cách trình bày "dòng này bị trừ đi".

*Đã đo* — chạy lại phép chấm trên kết quả đã lưu, **không tốn lệnh gọi API**:

| | Trước | Sau |
|---|---:|---:|
| Trường đúng | 216/265 = 81,5% | **222/265 = 83,8%** |
| Lỗi câm | 24/240 = 10,0% | **18/240 = 7,5%** |

Chi tiết: MWG 23/26 → 25/26 · VRE 22/27 → 24/27 · VHC lỗi câm 0,053 → 0,000 ·
HNG 0,250 → 0,208.

### Nới mép trên vùng cắt để lấy dòng "Đơn vị tính" (`05d00d0`)

`get_table_regions()` lọc `!= "table"` rồi `continue`, nên box chứa dòng "Đơn
vị tính" bị vứt ngay tại vòng lọc. VLM không đọc sai dòng ấy — nó chưa từng
được đưa cho xem. Lượt gold mất dòng này ở 2/10 tài liệu.

*CHƯA đo hiệu quả trên kết quả trích xuất.* Bản vá đổi ảnh đầu vào nên phải
chạy lại pipeline mới biết VLM có đọc ra đúng không. Mới kiểm hình học:

| Trang | Vùng cắt cũ | Vùng cắt mới | Box lọt thêm |
|---|---:|---:|---|
| BMP tr.4 (3504 px) | y 508 | y 416 | `plain text` conf 0,86 — đúng dòng đơn vị |
| SBT tr.5 (3508 px) | y 531 | y 440 | `abandon` conf 0,62 ở góc phải |

**Đừng ghi vào bài rằng chỗ này đã sửa xong.**

### Ghi kết quả sau mỗi tài liệu thay vì một lần ở cuối (`ad34768`)

*Đã đo bằng thiệt hại thực tế:* lượt chạy đêm 26/08 chết ở tài liệu 7/11 và
**mất sáu tài liệu đã chấm xong cùng ba tiếng gọi API**. Bài học đã có sẵn
trong docstring từ lượt Mốc 3 nhưng chỉ được áp một nửa — "ghi trước khi in"
chống được lỗi định dạng, không chống được tiến trình bị giết.

### Tách kết xuất từng ô ra khỏi stdout (`72f9827`)

*Đã đo:* lượt chạy đầu có **79 khối "Page N"** lẫn vào cùng file với bảng gộp.
Nay `redirect_stdout` đổ chúng vào `tap_gold_<chế độ>_pipeline.log`.

### Lượt chấm pipeline đầu tiên trên tập gold — số thật đầu tiên của dự án

Không phải một thay đổi mà là một **phép đo**, ghi ở đây vì mọi con số dưới nó
đều lấy mốc từ đây. Kết quả đầy đủ và phân tích ở `HANDOFF.md` mục 20.

| | |
|---|---|
| Trường đúng | 216/265 = **81,5%** |
| Lỗi câm | 24/240 = **10,0%** |
| Đơn vị tính đúng | 8/10 |
| Tài liệu đúng trọn vẹn | **0/10** |
| **Lỗi câm không quy giản được** | **3/240 = 1,25%** |

Con số cuối là kết quả đáng giá nhất: **21 trong 24 lỗi câm là hai con bug**
(11 đảo dấu, 10 định vị nhầm bảng ở SBT), không phải giới hạn của mô hình. Tỷ
lệ 10,0% đang bị hai lỗi cài đặt kéo lên gấp tám lần.

---

## 26/08/2026

### Nguồn tài liệu gold và script tải (`537afc3`, `fc202ee`)

Rào chặn lớn nhất của tầng gold — "chưa biết lấy 99 tài liệu còn lại ở đâu" —
đã gỡ. Nguồn `finance.vietstock.vn`, lấy được bằng máy.

*Đã đo:* khoản "tìm và tải tài liệu" trong bảng ngân sách rơi từ **15–20 giờ**
xuống còn việc chọn mã. 10 tài liệu đầu đã tải và gán nhãn xong.

### Đồng hồ do người tự bấm thay cho đo tự động (`f1468ae`, `0d27e35`)

Đo tự động lệch theo **cả hai** chiều: gõ `doc_id` rồi mới đi tìm file PDF, hay
để cửa sổ mở qua buổi trưa, đều cộng thời gian không phải thời gian làm; ngược
lại người điền siêu dữ liệu sau cùng thì đồng hồ gần như không chạy. Với
`n = 10` thì một tài liệu lệch đủ sức đẩy trung vị.

*Đã đo:* 8 tài liệu có đồng hồ chạy thật cho 361–579 giây, **trung vị 442 giây
≈ 7,4 phút**. Công đoạn điền vì thế rẻ hơn ước lượng cảm giác (10 phút) chừng
một phần tư; chiếu sang 100 tài liệu thì khoản "điền nhãn" là **~12 giờ** thay
vì ~17 giờ.

**Hệ quả đã cố định về mặt số học:** trung vị của 10 số chỉ chạy được trong
dải 435,5–453,5 giây, nhân 0,6 ra 4,36–4,54 phút — toàn dải nằm dưới sàn 5
phút. Đồng hồ trần người **sẽ là 5 phút**. Vẫn phải đo đủ 10 rồi mới tuyên, vì
công thức đăng ký là "trung vị của 10 tài liệu".

### Phép kiểm dấu thôi xét theo dấu của TỔNG số thuế (`5c8a915`)

Bản đầu xét dấu từng chỉ tiêu thuế bằng dấu của tổng, nên báo oan ca hoàn toàn
hợp lệ: thuế hiện hành là chi phí lớn còn thuế hoãn lại là khoản hoàn nhập âm.

*Đã đo trên ca thật:* `MWG_2025Q1_TT200` có mã 52 bằng −10.894.797.039 mà đẳng
thức B02 cân **chính xác đến từng đồng**. Tiêu chí mới ("lật dấu có làm cân
đẳng thức không") không có chỗ cho ca ấy. Đây chính là tiêu chí mà tu chính
Câu 13 ngày 28/08 chép vào guideline.

### Nhóm Stress thứ ba đổi sang độ phân giải bản quét (`6b3ed0e`)

*Đã đo trên 23 tài liệu của 20 doanh nghiệp:* `pdftotext` lấy ra **44–734 byte**
cho cả tài liệu 25–65 trang, tức bằng 0 — **100% quần thể là ảnh quét**. Tiêu
chí "bản scan chất lượng thấp" vì thế không chia được nhóm nào.

Thay bằng độ phân giải, đo bằng máy (`src/do_do_phan_giai.py`): dải **89,9–295,8
dpi**, trung vị 200,0. Giới hạn phải nêu kèm: **6/10 tài liệu rơi đúng 200,0
dpi**, phân bố dồn cục nên sức phân biệt nằm gần hết ở hai đuôi.

*Cạm bẫy đã trả giá:* `horizontal_dpi`/`vertical_dpi` của pdfium **sai ở trang
đặt ảnh xoay** — SBT bị báo 127,3/63,5 dpi trong khi thật là 90 dpi đều cả hai
chiều. Ba con số ước lượng bằng mắt trước đó đều sai: MWG ~432 (thật 295,8),
DGC ~283 (thật 200,0), HNG ~204 (thật 143,9).

### Hậu tố `a`/`b` thôi là dấu hiệu nhận diện chuẩn (`ca854dc`)

Guideline mục 3.7 xếp `B 01a - DN` là dấu hiệu TT99, mâu thuẫn với mục 2 của
chính nó.

*Đã đo bằng hậu quả trên tài liệu thật:* `SBT_2025Q2` và `HNG_2025H1` mang ký
hiệu `B01a-DN/HN` với tiêu đề TT200 — theo quy tắc cũ thì phải ghi `UNKNOWN`
dù chúng rõ ràng là TT200, và tỷ lệ TT99/TT200 của tập gold sẽ vỡ. Cả hai giữ
nhãn `TT200`, không gán nhãn lại.

---

## 25/08/2026

### Bộ chỉ tiêu chuyển từ kịch bản D sang kịch bản E (`f1c2738`)

*Đã đo:*

| | Kịch bản D | Kịch bản E |
|---|---:|---:|
| Chỉ tiêu (TT200 / TT99) | 20 / 21 | **26 / 27** |
| Đẳng thức | 7 | **9** |
| `dim null(A)` (TT200 / TT99) | 13 / 14 | 17 / 18 |
| Định vị được lỗi một-trường (TT200) | 5 / 20 | **7 / 26** |
| Chỉ tiêu có cột toàn 0 | 0 | 0 |

Hai chỉ tiêu mới định vị được: `lctt_thuan` và `tien_va_tuong_duong_tien`. Cái
thứ hai là điểm đáng giá riêng của E — nó ĐÃ nằm trong bộ từ trước nhưng lẫn
trong lớp năm thành phần của mã 100, và đẳng thức liên kết chéo B03 gắn cho nó
một đẳng thức **thứ hai** để tách ra.

**Phần không đẹp, phải báo cáo vì nó là kết quả của H0:** không gian null tăng
13 → 17 chiều còn tỷ lệ định vị được gần như đứng yên (25% → 27%). Thêm 6 chỉ
tiêu mà chỉ mua 2 đẳng thức thì 4 chiều chênh lệch rơi thẳng vào không gian vô
hình. **E tốt hơn D nhưng không sửa được kết luận nền của H0.**

### Ma trận nhầm chữ số đo được thay cho bảng bốn cặp chọn bằng mắt (`90b271a`, `f80a53d`)

Bảng cũ là bốn cặp `(0,8) (1,7) (3,8) (5,6)` chọn theo hình dạng.

*Đã đo trên EasyOCR, sáu font:* ba trong bốn cặp cũ **gần như không xuất
hiện**, còn cặp áp đảo thật là **`9→0`, chiếm 38%** mọi quan sát, không nằm
trong bảng cũ. Nguồn `ocr_alt` trước đây đi tìm sai chế độ lỗi.

*Hiệu quả trên phép đo Mốc 3:* độ phủ ứng viên `digit_substitution` **0,046 →
0,615**.

### Nới trần ứng viên 6/12 → 10/20 (`68ce4d2`)

*Đã đo trên 10 hồ sơ XBRL, 20 lượt mỗi mức, trần thời gian 10 giây:*

| trần | ứng viên/chỉ tiêu | median | chạm trần giờ | REPAIRED | vượt trần |
|---|---:|---:|---:|---:|---:|
| 6 / 12 | 11,9 | 5 ms | 10 % | 3 | 5 |
| **10 / 20** | 18,6 | 6 ms | 20 % | **6** | **0** |
| 14 / 28 | 22,1 | 7 ms | 20 % | 6 | 0 |

Số lượt sửa được **tăng gấp đôi**; mức 14/28 cho kết quả y hệt 10/20 nhưng tốn
thêm ứng viên. Chi phí nằm trọn ở phần đuôi — median gần như không đổi.

### Donor thôi lấy từ chính công ty đang xét (`e6c286c`)

*Đã đo:* trước khi sửa, **32% chỉ tiêu có donor trùng khít giá trị thật** —
baseline 9 khi đó là oracle. Sau khi sửa, chỉ số chống bịa **đảo chiều** sang
có lợi cho phương pháp đề xuất. Đây là thứ chặn nặng nhất trong bốn thứ từng
làm hỏng phép đo Mốc 3.

### Cột kỳ so sánh chọn theo độ phủ chỉ tiêu thay vì theo ngày (`f80a53d`)

*Đã đo:* 0/158 chỉ tiêu có giá trị ở kỳ thứ hai khi chọn theo ngày, nên
`col_shift` bỏ **120/130 lượt**. Sau khi sửa, inject đủ 130 lượt.

### Lượt chạy Mốc 3 — điều kiện dừng KHÔNG kích hoạt

26 hồ sơ của 14 công ty, **520 lượt**, chạy 103 phút. Kết quả ở
`data/output/moc3_15congty.md`.

| Chỉ số | Đề xuất | Baseline 9 |
|---|---:|---:|
| Tỷ lệ lượt còn sai sau sửa (CHÍNH) | 0,719 | **0,646** |
| Định vị đúng / tổng lượt (CHÍNH) | 0,227 | **0,288** |
| Tỷ lệ ra tay | 0,285 | 0,606 |
| Định vị đúng TRÊN LƯỢT CÓ RA TAY | **0,797** | 0,476 |
| Tỷ lệ bịa mức trường | **0,00400** | 0,00609 |

Bảng gộp **không đọc được một mình** — nó là trung bình của hai nhóm khác bản
chất. Tách theo chế độ lỗi:

| Chế độ lỗi | Kiểm được khả năng SỬA? | Còn sai — đề xuất | — baseline 9 |
|---|---|---:|---:|
| `sign` | có | **0,392** | 0,600 |
| `digit_substitution` | có | **0,485** | 0,592 |
| `row_shift` | KHÔNG — phủ 0,015 | 1,000 | 0,654 |
| `col_shift` | KHÔNG — phủ 0,000 | 1,000 | 0,738 |

Trên hai chế độ tầng này kiểm được, đề xuất thắng **+20,8 điểm** (`sign`) và
**+10,7 điểm** (`digit_substitution`), cả hai vượt ngưỡng effect size 3 điểm đã
chốt trước.

### Trần trên của mọi bộ giải liên tục — phép đo đổi cách đọc cả bảng Mốc 3 (`73db89a`)

Nghi vấn: baseline 9 sửa đúng 26–35% lượt `row_shift`/`col_shift` trong khi ở
hai chế độ đó giá trị thật đã bị ghi đè và biến mất khỏi bảng.

*Giả thuyết đầu đã bị bác bằng số đo:* nghi các lượt trúng rơi vào chỉ tiêu có
giá trị thật bằng 0 — đo được **0 trên 520 lượt**.

*Lời giải thích đúng:* baseline 9 không bịa, nó **nghịch đảo**. Khi đúng một
trường sai và trường đó được thả ra một mình thì `r = δᵢ·aᵢ`, nên nghiệm duy
nhất là `δ = −δᵢ`, bất kể donor ở đâu.

| Trạng thái | Tỷ lệ | Nghĩa |
|---|---:|---|
| Ràng buộc **chốt đúng** giá trị | 0,608 | **Trần trên của mọi bộ giải liên tục** khi không đọc lại tài liệu |
| Không chốt | 0,146 | Khoảng hở mà việc đọc lại nguồn tồn tại để lấp |
| Cột bằng 0 | 0,246 | Không ràng buộc nào bảo vệ — kết quả của H0 |

Chuẩn hoá theo trần thì bảng Mốc 3 đọc ra nghĩa khác hẳn: ở `sign`, phương
pháp đề xuất đạt **100,0% của trần** (0,608/0,608) so với 65,8% của baseline 9
— **giải đúng mọi lượt mà thông tin tồn tại** và im lặng ở phần còn lại.

### Baseline 8 chuyển từ IRLS sang quy hoạch tuyến tính (`f1d236e`)

Trên hệ đối xứng như `a + b = c`, cực tiểu L1 suy biến: nghiệm rải đều
`δ = 5/3` ở cả ba toạ độ có cùng chuẩn L1 với nghiệm dồn một chỗ, và IRLS xuất
phát từ trọng số đều thì **kẹt ở đó vĩnh viễn**.

*Không đo bằng một tỷ lệ:* đây là điều kiện để đối chứng công bằng — baseline
mạnh hơn thì kết luận về phương pháp đề xuất đáng tin hơn.

### Chỉ số định vị thôi trộn độ đúng với mức sẵn sàng đoán (`0903df2`)

Đếm ABSTAIN là trượt thì đo mức sẵn sàng đoán, không đo độ đúng. Chốt báo cáo
**ba** con số: chia cho tổng số lượt (chỉ số CHÍNH), tỷ lệ ra tay, và định vị
trên lượt có ra tay. Con số thứ ba **không bao giờ đứng một mình**.

*Đã đo mức độ nghiêm trọng:* với cùng bộ dữ liệu, con số thứ ba là 0,797 còn
chỉ số chính là 0,227 — chênh nhau 3,5 lần.

---

## 24/08/2026

### Phương án C — dòng vắng mặt được điền `0` nhờ dò mã số (`fa5c6d2`, `88a77f5`, `19fe938`, `ada6f75`)

`validate_result()` bỏ qua **cả đẳng thức** nếu bất kỳ thành phần nào là
`None`. Với đẳng thức phân rã tài sản ngắn hạn (5–6 thành phần) thì chỉ cần
một dòng không đọc được là đẳng thức giá trị nhất im lặng không chạy.

*Đã đo bằng lỗi nó gỡ:* bước A của phương án C phát hiện `router.py` gọi
`validate_result()` ở **ba chỗ** mà không truyền `standard`, nên **mọi tài
liệu bị kiểm bằng đẳng thức TT99** — kể cả 5 tài liệu TT200 của tập gold. Cùng
lượt, `router.py` đè `meta` thật nên đầu ra khai sai chuẩn và đánh rơi
`early_stop` với `prompt_hash`.

*CHƯA đo hiệu quả trên tỷ lệ trường đúng.* Bước D (nhận diện chuẩn) chưa làm,
nên trên cấu hình mặc định mọi tài liệu vẫn lùi về TT99.

### Trần `max_changes` đo lại trên bộ chỉ tiêu đã chốt, giữ nguyên giá trị 2 (`709e58c`)

*Đã đo trên chính ma trận TT200/TT99, ca vô nghiệm (đắt nhất):*

| Chuẩn | Chỉ tiêu | Ứng viên | `max_changes` | Thời gian |
|---|---:|---:|---:|---:|
| TT200 | 20 | 100 | 2 | **33 ms** |
| TT200 | 20 | 100 | 3 | 958 ms |
| TT200 | 20 | 100 | không đặt | hết giờ 30 s |
| TT99 | 21 | 105 | 2 | **56 ms** |
| TT99 | 21 | 105 | 3 | 1 128 ms |
| TT99 | 21 | 105 | không đặt | hết giờ 30 s |

**Mỗi nấc `max_changes` đắt lên khoảng 20 lần.** Chi phí nằm trọn ở việc chứng
minh KHÔNG có nghiệm. Hệ quả cho việc mở rộng: ở `max_changes = 2` chi phí đi
theo `C(n,2)`, nên tăng từ 21 lên 40 chỉ tiêu chỉ đắt lên chừng 3,7 lần —
**ràng buộc thật khi mở rộng là chi phí gán nhãn tay, không phải chi phí tính
toán**.

### Nơi nộp đổi từ IJDAR journal track sang ICDAR 2027 main track

*Đo bằng lịch:* hạn journal track 15/11/2026 cho khoảng 12 tuần, trong khi phần
việc còn lại ước 13–16 tuần. Hạn ICDAR main 28/02/2027 cho **27 tuần**, và chừa
chỗ lùi phạm vi nếu Mốc 3 ra kết quả xấu.

*Ràng buộc phát hiện khi tra CFP:* journal track **loại bản mở rộng từ hội
nghị**, nên chiến lược "nộp song song RIVF/SoICT" của proposal gây hại — nó vừa
đóng cửa journal track vừa tạo vấn đề trùng lặp với ICDAR main.

---

## 23/08/2026

### MỐC 1 đóng — bộ chỉ tiêu mở từ 11 lên 21 chỉ tiêu (`4064519`, `df96ff2`)

*Đã đo bằng `src/constraints_scenarios.py`:*

| KB | Kịch bản | Chỉ tiêu | Vô hình | Trần Top-1 | Trần Top-3 | Ô gán nhãn (×60) |
|---|---|---:|---:|---:|---:|---:|
| A | Hiện tại | 11 | 3 | 0,36 | 0,73 | 660 |
| B | + Tổng cộng nguồn vốn | 12 | 3 | 0,42 | 0,75 | 720 |
| C | + chuỗi lãi lỗ B02 | 16 | 1 | 0,50 | 0,94 | 960 |
| **D chốt** | + phân rã TSNH | **20–21** | **0** | 0,50 | 0,90 | 1 200 |
| E | + B03 và liên kết chéo | 26 | 0 | 0,54 | 0,96 | 1 560 |

**Cái bẫy đọc bảng này, sẽ quay lại khi dựng bảng cho paper:** Top-3 của D thấp
hơn C nhìn như bước lùi, nhưng đo trên **đúng 16 chỉ tiêu của C** thì D cho
0,975 so với 0,938 — không chỉ tiêu nào xấu đi. Trung bình tụt vì D thêm bốn
chỉ tiêu vốn dĩ khó. Đây là hiệu ứng cấu thành, và **bảng kết quả phải in Top-k
kèm phân rã theo lớp lẫn**.

*Đo cho cột kỳ so sánh, trả lời proposal 6.1(d):* thêm cột kỳ trước **nhân đôi**
số chỉ tiêu mà trần Top-1 và Top-3 **không đổi một điểm nào** — hai cột thoả
cùng một hệ đẳng thức độc lập nên ma trận thành khối chéo `[[A,0],[0,A]]`.
Quyết định: **không gán nhãn cột kỳ so sánh.**

### Một kết luận cũ bị bác bỏ — liên kết chéo KHÔNG hiệu quả gấp đôi phân rã (`6744bee`)

Bản trước dùng đẳng thức **giả thuyết** và kết luận liên kết chéo hiệu quả gấp
đôi phân rã. Hai đẳng thức từng được giả định — nối Lợi nhuận chưa phân phối
(B01) với Lợi nhuận sau thuế (B02), và phân rã Vốn chủ sở hữu — **không có
trong văn bản**.

*Đã đo lại với đẳng thức thật:* liên kết chéo cho tỷ lệ **0,33**, phân rã cho
**0,50** — ngược hẳn kết luận cũ. Chốt bằng
`test_lien_ket_cheo_KHONG_hieu_qua_hon_phan_ra`.

**Bài học đã ghi vào docstring:** đừng để đẳng thức giả thuyết chạy vào bảng
kết quả, kể cả khi chúng hợp lý về kế toán.

### `FORM_MARKERS` sai — hậu tố `a`/`b` là kỳ báo cáo, không phải Thông tư (`023321c`)

*Đã đo bằng hậu quả:* marker TT200 mang `(?!\s*a)` nên **không khớp trang
`B01a-DN`** — đúng loại tài liệu dự án xử lý, kể cả báo cáo VNM mẫu. Marker
trượt thì `extract_field_by_code()` trả `None`, tức **đường dự phòng theo mã số
tắt hẳn, im lặng**.

Điểm sáng: `detect_standard()` dùng `STANDARD_MARKERS` theo TÊN báo cáo và cái
đó đúng — nhận diện CHUẨN không hỏng, chỉ nhận diện MẪU BIỂU hỏng.

### Engine OCR — giữ EasyOCR (`a3a5ea7`)

*Đã đo trên 45 ô số render sẵn (ground truth mức ô chính xác tuyệt đối):*

| Ảnh | Levenshtein | Đúng con số | Không ra số |
|---|---:|---:|---:|
| sạch | 0,999 | 0,978 | 0,022 |
| mờ | 1,000 | 1,000 | 0,000 |
| nhiễu | 1,000 | 1,000 | 0,000 |
| **độ phân giải thấp** | **0,934** | **0,467** | **0,000** |

**Kết luận 1 — giữ EasyOCR.** Con số 0,646 của Ajayi et al. đo trên bảng KHOA
HỌC; trên ô số thì 0,999.

**Kết luận 2, quan trọng hơn.** Ở độ phân giải thấp, chỉ số ký tự vẫn báo 0,934
trong khi **chưa tới một nửa** số đọc ra là đúng, và tỷ lệ "không ra số" bằng
**0** — mọi ô sai đều parse ra một con số hợp lệ. Đó là lỗi câm, đo được, trên
dữ liệu có ground truth hoàn hảo. **Không được báo cáo Levenshtein accuracy một
mình.**

### Dừng sớm thôi mua lại thứ đã có (`3abc812`)

Điều kiện "đủ hết field" trước đây chỉ được kiểm ở cuối mỗi **trang**, nên vùng
đầu tiên lấp đủ field xong thì ba vùng còn lại của chính trang đó vẫn bị gọi
VLM để mua về đúng thứ đã có. Kèm theo: điều kiện đếm trên `FIELD_MAP` (hợp của
hai chuẩn) làm nhánh dừng rẻ nhất **bất khả thi với báo cáo TT200**, vì
`tai_san_sinh_hoc_ngan_han` chỉ có ở TT99 — mọi lượt chạy TT200 phải rơi xuống
nhánh nguy hiểm cho phép đo.

---

## 22/08/2026 và trước đó — hạ tầng

Giai đoạn dựng pipeline và hạ tầng đo, không có phép đo trước/sau. Những thứ
còn ràng buộc việc đang làm:

| Thay đổi | Ràng buộc để lại |
|---|---|
| Ma trận ràng buộc và phân tích identifiability (`88c031e`) | Nền của H0; `scale_direction_in_null()` là assert chạy được cho việc dựng ma trận |
| Chế độ tắt cổng ràng buộc (`c85c812`) | `DISABLE_CONSTRAINT_GATE` — không có nó thì AUROC của H1 đo trên tập đã bị chính tín hiệu đó lọc |
| Provenance từng trường (`0d74195`) | Đứt chuỗi này là mất đóng góp cốt lõi — không đọc lại được vùng ảnh |
| Confidence bằng self-consistency (`a5ec83e`) | `n_samples=1` cho confidence 1,0 nghĩa là **không đo được**, không phải chắc chắn |
| Tập ứng viên đóng (`2cf613a`) | Nếu có đường nào để một con số ngoài tập lọt vào kết quả thì hệ ép số được, và lập luận chống bịa sụp |
| Tách ABSTAIN theo lý do (`9c3f7c9`) | `vo_nghiem` là ca DUY NHẤT chứng minh được luận điểm chống bịa — và nó **chưa từng xảy ra**: 0/520 ở cả hai lượt Mốc 3 |
| Tầng đánh giá XBRL (`1dacb34`) | XBRL lo POWER, gold Việt Nam lo VALIDITY |
| Bootstrap theo cụm tài liệu (`ad6684a`) | Phân cụm nới khoảng tin cậy hơn **gấp đôi** trên dữ liệu phân cụm; `item_bootstrap_ci` giữ lại để paper nêu định lượng |
| Mỏ neo biên độ lớn tuyệt đối (`437e2a1`) | Check DUY NHẤT không bất biến với phép nhân vô hướng — thứ duy nhất bắt được sai đơn vị toàn cục |

**Hai lượt chạy Mốc 3 (25/08 và 26/08) tái lập từng chữ số**, trừ bảng lý do
ABSTAIN: 71/249 lượt chuyển bucket giữa `het_gio` và `vuot_tran_thay_doi` chỉ
vì lượt sau phải chia CPU với việc chấm tập gold. **`het_gio` đo tải máy chứ
không đo phương pháp** — trong bài phải ghi rõ bảng lý do ABSTAIN phụ thuộc
ngân sách tính toán, hoặc bỏ `het_gio` ra khỏi mọi lập luận.
