# Hồ sơ các phần đã đóng của `HANDOFF.md`

Tách khỏi `HANDOFF.md` ngày 31/08/2026 để file bàn giao còn lại đúng phần
**trạng thái sống** mà mọi phiên đều phải đọc. Ở đây là hồ sơ của việc đã
xong: vẫn còn giá trị, nhưng là giá trị **tra cứu**, không phải giá trị nạp
mỗi phiên.

**Nội dung giữ NGUYÊN VĂN và NGUYÊN SỐ MỤC.** Không tóm tắt, không sửa. Nhờ
vậy mọi tham chiếu chéo sẵn có trong repo — dạng "mục 20.4b", "mục 19.5",
"Phụ lục A" — vẫn tra được, chỉ đổi file. `HANDOFF.md` để lại ở mỗi chỗ một
dòng trỏ sang đây kèm phần ràng buộc còn hiệu lực.

Vì sao tách: đọc trọn `HANDOFF.md` tốn khoảng 32 nghìn token mỗi phiên, mà
hơn một nửa số đó là hồ sơ của việc đã đóng. Xem `CLAUDE.md` cho bảng định
tuyến quyết định lúc nào cần mở file này.

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


---

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


---

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


---

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
   tài liệu. Mỗi lượt chạy trọn bộ vì thế phải được sao lưu NGAY khi xong, và
   ba mốc so sánh hiện có — `..._TRUOC-VA-2026-08-27.json` (hai bản vá 27/08),
   `..._2026-08-29.json` (mốc repair TẮT), `..._2026-08-30.json` (mốc repair
   BẬT, mục 20.7) — **đừng xoá cái nào**.

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


---

### 20.7 Lượt chạy 30/08/2026 — BẬT tầng repair, có neo và ô lân cận

**Con số của lượt này KHÔNG dùng được cho H1.** Tầng repair sửa giá trị cho tới
khi residual về 0, tức làm phẳng đúng tín hiệu mà H1 đem so với confidence.
Lượt chạy sinh ra để xem cơ chế đọc lại tờ giấy có hoạt động trên tài liệu
thật, không phải để sinh số cho bài.

Chế độ `--chuan-tu-gold`, `BAT_TANG_REPAIR=true`, `USE_OCR_FIRST=true`,
`n_samples=1`, `temperature=0.0`, model `google/gemma-4-31b-it:free`. 10 tài
liệu (VNM vẫn thiếu PDF). Kết quả đầy đủ: `data/output/tap_gold_chuan_tu_gold_2026-08-30.json`;
mốc so sánh 29/08 ở `..._2026-08-29.json` — **đừng xoá cả hai**.

| | 30/08 repair BẬT | 29/08 repair TẮT |
|---|---:|---:|
| Trường đúng | **0,804** (213/265) | 0,728 (193/265) |
| Lỗi câm | **0,148** (37/250) | 0,215 |
| Đúng trọn vẹn | **2/10** | 0/10 |
| Nhận diện chuẩn | 10/10 | 10/10 |
| Hệ số đơn vị | 9/10 | 9/10 |

| doc_id | 30/08 | 29/08 | Đổi |
|---|---:|---:|---:|
| `MWG_2025Q1_TT200` | 26/26, câm 0 | 25/26, câm 1 | +1 |
| `VRE_2026Q1_TT99` | 27/27, câm 0 | 24/27, câm 1 | +3 |
| `DLG_2026Q2_TT99` | 24/27, câm 0 | 17/27, câm 7 | **+7** |
| `SBT_2025Q2_TT200` | 23/26, câm 2 | 17/26, câm 8 | **+6** |
| `VHC_2025Q1_TT200` | 17/26, câm 8 | 15/26, câm 10 | +2 |
| `HNG_2025H1_TT200` | 2/26, câm 24 | 0/26, câm 24 | +2 |
| `BMP` · `TTF` · `HPG` | không đổi | | 0 |
| `DGC_2025Q2_TT200` | 23/26, câm 2 | 24/26, câm 1 | **−1** |

**BA THAY ĐỔI CÙNG LÚC, nên bảng này KHÔNG quy được nhân quả.** Lượt 30/08
khác lượt 29/08 ở: bật tầng repair, thêm nguồn ô lân cận có neo (mục 5.8), và
thêm lan ký hiệu mẫu. Hai bước nhảy lớn nhất nằm đúng chỗ hợp lý — SBT là ca
nhầm cột mà hạng 2 của hình chữ thập sinh ra để cứu, và nó là **việc số 1 của
mục 20.6** — nhưng "hợp lý" không phải bằng chứng.

**Vì sao không tách được ngay tại chỗ:** file kết quả của lượt này không giữ
`chung_chi_repair` lẫn `ky_hieu_mau`. Đã vá (`8056b33`) nhưng quá muộn cho
chính nó — bản vá không tác động lên tiến trình đã nạp code cũ. Rút ra: **lượt
chạy bật một cơ chế mới mà không lưu certificate của cơ chế đó thì cho ra số
không quy được về nguyên nhân**, và cái giá là chạy lại.

**`DGC` là ca duy nhất tệ đi**, mất một trường và thêm một lỗi câm. Đúng cái
giá đã lường: mọi ứng viên vẫn truy được về một chỗ trên tờ giấy nên hệ không
bịa số, nhưng tập ứng viên rộng ra thì xác suất một ô tình cờ làm bảng cân
cũng tăng. Đây là chỉ số phải theo dõi mỗi lần nới nguồn ứng viên.

**`HNG` vẫn hỏng vì lý do cũ** — quy ước dấu ngược (Câu 14), và là tài liệu duy
nhất sai hệ số đơn vị. Không liên quan gì tới lượt này.

---


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


---

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


---

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


---
