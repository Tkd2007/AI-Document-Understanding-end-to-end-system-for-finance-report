# ViFinKIE — hướng dẫn cho phiên Claude

Hệ trích xuất chỉ tiêu từ báo cáo tài chính Việt Nam, kèm một tầng dùng ràng
buộc kế toán để **định vị** ô sai. Đây là công trình nghiên cứu cá nhân của
`Tkd2007 <trankimdanh2007@gmail.com>`, có đăng ký trước, đang viết thành bài.

**File này là thứ DUY NHẤT phải đọc ở mọi phiên.** Mọi thứ khác đọc theo bảng
định tuyến bên dưới, đúng mục cần, không đọc trọn file. Trước khi bảng này tồn
tại, mỗi phiên mới nạp trọn `HANDOFF.md` — khoảng 32 nghìn token — để lấy về
vài nghìn token thật sự dùng tới.

**Ở đây KHÔNG chép số đo, không chép trạng thái.** Chúng đổi mỗi lượt chạy, và
một bản sao trong file tự nạp mỗi phiên là một bản sao sẽ cũ đi mà không ai
biết. Số ở `CHANGELOG.md`, trạng thái ở `HANDOFF.md` mục 0 và 16.

---

## Quy ước bắt buộc

| Quy ước | Chi tiết |
|---|---|
| **Kiểm sau MỖI thay đổi** | `python -m ruff check src tests` rồi `python -m pytest -q`. Không đợi tới lúc báo xong. Thêm tính năng kèm test thì **đục thủng tính năng đó và xác nhận test đỏ** |
| **Commit đứng tên người dùng** | **Tuyệt đối không** thêm trailer `Co-Authored-By: Claude` hay dòng `Generated with Claude Code`. Lịch sử git ở đây là hồ sơ tác giả |
| **Commit thẳng nhánh đang làm** | Mỗi việc một commit, message giải thích **lý do**. **Không tự tạo branch** |
| **`main` KHÔNG BAO GIỜ MERGE** | Chỉ thị người dùng 24/08/2026. Đừng đề xuất merge hay mở pull request. Hệ quả: CI không bao giờ chạy, mọi việc kiểm phải làm tại chỗ |
| **Import phẳng** | `pytest.ini` có `pythonpath = src`. Viết `from validation import ...`, KHÔNG `from src.validation import ...` |
| **Comment tiếng Việt** | Giải thích **tại sao**, không phải **cái gì** |
| **Docstring mô tả hiện trạng** | Không viết trạng thái dự định như thể đã làm xong |
| **Config tập trung** | Mọi hằng số miền nằm ở `src/fields_config.py` |
| **Trạng thái tường minh** | Trạng thái ghi ra log/metrics/JSON phải là khoá tường minh, không để người đọc suy ra từ sự vắng mặt của khoá khác |
| **Test không cần mạng** | Dùng fixture và hàm giả, không gọi API thật |
| **Nạp model lười** | Model nặng nạp trong getter |

`ruff.toml` đặt `line-length = 100` và bật rule sắp xếp import.

### Trước khi đụng vào phép đo

Thay đổi **thiết kế thí nghiệm** — chỉ số của H0–H3, giao thức tiêm lỗi, quy
tắc gán nhãn — phải ghi vào mục **Sửa đổi** của `PREREGISTRATION.md` hoặc
`ANNOTATION-GUIDELINE.md` **TRƯỚC** khi chạy. Giá trị khoa học của hai file đó
nằm ở chỗ không sửa được sau khi đã thấy kết quả, nên **đừng bao giờ nén hay
tóm tắt chúng**; muốn gọn thì thêm mục lục.

### Đừng chỉ bồi thêm vào tài liệu

Mỗi lần ghi một mục mới, đồng thời nén hoặc bỏ phần mà mục mới vừa làm cho lỗi
thời. Một sự thật có **đúng một nhà**:

| Loại nội dung | Nhà duy nhất |
|---|---|
| Lập luận, cam kết nghiên cứu | `PREREGISTRATION.md` |
| Số đo trước–sau | `CHANGELOG.md` |
| Hiện trạng code và lý do thiết kế | comment trong chính file code |
| Lịch sử thay đổi | `git log` |
| Việc đang dở, bước kế tiếp | `HANDOFF.md` |
| Hồ sơ việc đã đóng | `docs/lich-su/` |

---

## Bảng định tuyến — đọc mục nào khi làm gì

| Việc bạn sắp làm | Đọc |
|---|---|
| Bắt đầu bất kỳ phiên nào | `HANDOFF.md` mục 0 (câu đang chờ) và 16 (bước kế tiếp) |
| Chọn việc để làm | `HANDOFF.md` mục 12, 17 |
| Sửa `validation.py`, đẳng thức, ràng buộc | `HANDOFF.md` mục 10, Phụ lục A |
| Sửa đơn vị tính, bậc độ lớn | `HANDOFF.md` mục 20.8; `src/fields_config.py` quanh `UNIT_KEY` |
| Sửa tầng repair, sinh ứng viên, định vị | `HANDOFF.md` mục 5.8, 13 |
| Sửa nhánh OCR, dừng sớm, probe dò dòng | `HANDOFF.md` mục 12.2, Phụ lục B |
| Chạy chấm tập gold | **Câu 17 đang chặn** — đọc `HANDOFF.md` mục 0 trước. Hết chặn thì chạy thẳng hai lệnh ở mục Lệnh hay dùng; cần tham chiếu thì kỹ năng `chay-tap-gold` |
| Đụng vào nhãn gold, hay đọc chỗ nhãn không cân | **`HANDOFF.md` mục 19.7** — và ĐỌC `notes` của chính file gold trước khi kết luận, 10/70 file có ghi chú giải thích sẵn |
| Gán nhãn tập gold | `ANNOTATION-GUIDELINE.md`; `HANDOFF.md` mục 19 |
| Đọc / dựng bảng kết quả cho bài | `HANDOFF.md` mục 13.2, 20.4; `CHANGELOG.md` |
| Đụng vào tầng XBRL Mỹ | `HANDOFF.md` mục 5.2, 13 |
| Cài đặt, cấu trúc thư mục, API | `README.md` |
| Tra "vì sao code chỗ này lại thế" | **đọc comment trong chính file đó trước** — dự án này comment rất dày và luôn nêu lý do |

Cần tra một mục đã đóng mà `HANDOFF.md` chỉ còn dòng trỏ: nội dung nguyên văn
ở `docs/lich-su/HANDOFF-da-dong.md`, **giữ nguyên số mục cũ** nên mọi tham
chiếu dạng "mục 20.4b" vẫn tra được.

---

## Bẫy môi trường — đã cắn thật, sẽ cắn lại

- **Console Windows mặc định cp1252.** In tiếng Việt ra stdout sẽ nổ
  `UnicodeEncodeError`. Đặt `PYTHONIOENCODING=utf-8` ở đầu mọi lệnh một dòng;
  khối `__main__` phải có `sys.stdout.reconfigure(encoding="utf-8")`.
- **Shell chính của máy là PowerShell.** `VAR=x lệnh` chạy trên bash nhưng
  **lỗi cú pháp** trên PowerShell. Đã mất thời gian vì việc này một lần.
- **Script trong `src/eval/` cần `PYTHONPATH=src`**, và chạy như script thì
  `src/eval/metrics.py` che mất `src/metrics.py` — xem mục 5.7.
- **Heredoc bash vỡ** khi nội dung tiếng Việt có số lẻ dấu nháy đơn. Viết file
  dài bằng công cụ ghi file.
- **`sed` ăn mất backslash** khi thay chuỗi có regex. Dùng Python để thay.
- **Force-push bị trình phân loại quyền chặn.** Cần viết lại lịch sử thì để
  người dùng tự chạy lệnh.
- **`time.monotonic()` trên Windows quá thô** để test khoảng vài mili giây.
  Test bộ điều tốc của `fetch.py` dùng đồng hồ giả qua `monkeypatch`.
- **`.env.docker` đang chứa OpenRouter key thật.** Không nằm trong git và chưa
  từng được commit (đã kiểm cả lịch sử), nhưng **repo là public** — đừng in nó
  ra, đừng chép nội dung nó vào bất cứ file nào.
- **CI không cài torch**, nên model nặng phải nạp trong getter chứ không nạp
  lúc import.

---

## Tài liệu nằm NGOÀI repo — dễ quên vì không file nào khác trỏ tới

**Bốn tài liệu nguồn ở `MD file/` bị gitignore** (`MD file/.gitignore` chứa
`*.md`), nên chỉ có trên máy người dùng và không bao giờ xuất hiện trong
`git status`: `FINAL-proposal-reread-dont-repair.md` (proposal, bốn giả thuyết
H0–H3), `ADDENDUM-statistical-treatment.md` (vá phần thống kê),
`FINAL-repo-changes.md` (dịch proposal sang việc trong repo), `BUILD-SPEC.md`
(đặc tả thi công). **Khi đồng bộ tài liệu thì phải cập nhật cả bốn file này.**

**"Sổ tay phương pháp ViFinKIE"** — artifact riêng của người dùng ở
`https://claude.ai/code/artifact/8d3cef49-a6b0-40d6-8533-7d42f340d347`. Giải
thích phương pháp của từng giả thuyết H0–H3, thuật toán, cơ sở thống kê, thuật
ngữ tiếng Anh kèm nghĩa, cầu nối sang lý thuyết mã, bảng kết quả Mốc 3 kèm
trần định vị. **Bản HTML nguồn không còn** (nằm trong scratchpad của phiên đã
tạo), nên muốn sửa thì đọc lại nội dung bằng công cụ Artifact với URL trên rồi
xuất bản đè lên đúng URL đó — publish không kèm URL sẽ tạo một artifact khác.
Sổ tay **chưa có** phần công cụ gán nhãn và giao thức trần người.

Ngoài `CLAUDE.md` này, khi cần hiểu sâu thì đọc theo thứ tự:
`PREREGISTRATION.md` → docstring đầu `src/eval/stats.py` (nguyên tắc chi phối
toàn bộ phần thống kê) → docstring đầu `src/repair/diagnose.py` và các hằng số
đầu file (chỗ tập trung nhiều quyết định thiết kế nhất, mỗi cái đều có lý do
viết kèm) → `ANNOTATION-GUIDELINE.md`.

---

## Lệnh hay dùng

```bash
python -m ruff check src tests && python -m pytest -q   # sau MỖI thay đổi
python src/router.py data/samples/<file>.pdf            # chạy pipeline một tài liệu
python chay_gan_nhan.py --pdf-dir data/bctc             # công cụ gán nhãn, cổng 8100

# Dò nhãn gold không cân. Miễn phí, offline, vài giây. Chạy lại sau MỖI lần
# sửa nhãn. In kèm `notes` của người gán nhãn — ĐỌC nó trước khi kết luận.
PYTHONIOENCODING=utf-8 PYTHONPATH=src     python src/eval/do_lech_gold.py > docs/nhan-gold-khong-can.md

# Chấm tập gold. CÂU 17 ĐANG CHẶN lượt kế tiếp — đọc HANDOFF.md mục 0 trước.
# Lệnh đầu miễn phí: sao lưu kết quả cũ, tiền kiểm tập gold, in hiện trạng;
# thoát mã 1 thì DỪNG, đừng chạy lệnh sau. Lệnh sau tốn tiền API, chạy hàng giờ.
python .claude/skills/chay-tap-gold/tien_kiem.py
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --chuan-tu-gold

# ĐANG XẾP LỊCH — lượt H2 đủ trên tầng XBRL. KHÔNG tốn API, chạy offline,
# nhưng chiếm máy khoảng 20 giờ (26 hồ sơ × 4 chế độ lỗi × 5 seed × 3 mức số
# lỗi). Người chủ trì hoãn ngày 05/09/2026; chạy khi máy rảnh cả đêm.
PYTHONIOENCODING=utf-8 PYTHONPATH=src python -u src/eval/moc3.py > data/output/moc3_h2.md
```

Danh mục lệnh đầy đủ — chấm tập gold, đo luật dấu, tầng XBRL, đo độ phân giải
— ở `HANDOFF.md` mục 15. Các cờ môi trường (`BAT_TANG_REPAIR`,
`DISABLE_CONSTRAINT_GATE`, `DISABLE_LINE_PROBE`, `USE_OCR_FIRST`) đều có
comment giải thích hậu quả ngay tại chỗ khai báo trong `src/router.py` — đọc ở
đó, đừng đoán.
