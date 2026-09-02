---
name: chay-tap-gold
description: Chấm pipeline ViFinKIE trên tập gold có nhãn tay bằng src/eval/chay_tap_gold.py. Dùng khi cần chạy hoặc chạy lại phép đo trên tập gold, chấm một vài mã (--chi), nối một lượt chạy bị đứt (--tiep-tuc), hoặc đọc/so sánh kết quả trong data/output/tap_gold_*.json. Mục "Chạy ngay" ở đầu file đủ để bắt đầu mà không cần đọc thêm tài liệu nào khác; phần sau là tham chiếu.
---

# Chấm pipeline trên tập gold

## Chạy ngay — hai lệnh, không cần đọc tiếp

```bash
python .claude/skills/chay-tap-gold/tien_kiem.py
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --chuan-tu-gold
```

**Lệnh 1 không tốn gì và không gọi API.** Nó sao lưu kết quả lượt trước sang
`data/output/sao_luu_tu_dong/`, nạp thử mọi file gold đúng đường mà lượt chấm
sẽ đi, đối chiếu bộ chỉ tiêu và PDF, rồi in hiện trạng tập gold. **Thoát mã 1
nghĩa là chưa chạy được** — đọc danh sách vấn đề nó in ra, đừng chạy lệnh 2.

**Lệnh 2 là lượt chấm thật: tốn tiền gọi API và chạy hàng giờ.** Đọc mục thời
gian ngay dưới trước khi bấm.

Chỉ kiểm một tài liệu thì thêm `--chi <MÃ>` vào lệnh 2 — `--chi` khớp theo mã
chứng khoán ở đầu `doc_id`, nên `--chi DGC` chạy cả hai kỳ của DGC. Lượt chạy
bị đứt thì nối lại bằng `--tiep-tuc`, nó bỏ qua doc_id đã có trong file kết
quả nên không trả tiền API hai lần.

`PYTHONPATH=src` **bắt buộc** ở lệnh 2: thiếu nó thì `from eval.metrics import
...` nổ `ModuleNotFoundError: No module named 'eval'` ngay dòng import. Lệnh 1
tự chèn `src` vào `sys.path` nên không cần.

## Thời gian và cái giá — biết trước khi bấm

Ba lượt đo thật trên cùng một tài liệu (`VHC_2025Q1_TT200`, 40 trang), lấy từ
`data/output/metrics.jsonl`:

| Lượt | Tổng | Trang xử lý | OCR | Ghi chú |
|---|---:|---:|---:|---|
| 27/08 | 18,4 phút | 40/40 | 879 s | chưa có dừng sớm |
| 28/08 | 40,5 phút | 12/40 | 2.254 s | dừng sớm `het_bang_de_doc` |
| 30/08 | 12,1 phút | 12/40 | 550 s | dừng sớm, bật tầng repair |

Cùng 12 trang mà OCR lúc 550 s lúc 2.254 s — **chênh bốn lần**, và OCR chiếm
76–93% tổng thời gian. Nên đừng hứa một con số: lượt chạy thử 02/09/2026 trên
đúng tài liệu này chạy chậm gấp khoảng ba lần lượt 30/08 (layout 7,9–11 s mỗi
trang so với 3,2 s) mà không giải thích được bằng tranh CPU. **Ước cho trọn bộ
tập gold: hàng chục giờ máy, và cận trên rộng.** Muốn số của lượt gần nhất thì
đọc `stages` trong `metrics.jsonl` chứ đừng tin bảng này.

Cái giá thứ hai không mua lại được: **tài liệu nào chạy qua pipeline thì mất
vĩnh viễn quyền vào tập gán nhãn đôi** (quyết định Câu 12, 28/08/2026), vì
`data/output/` giữ giá trị máy đoán cho từng ô và người gán nhãn lại chính là
người đã chạy pipeline. Chỉ muốn chạy thử cho biết máy còn chạy được không thì
**chọn một mã đã bị loại từ trước**; `PYTHONPATH=src python
src/eval/tap_dong_thuan.py` liệt kê chúng.

## Hai chế độ, và khoảng cách giữa chúng chính là phép đo

`router.chon_chuan` chưa có nguồn `nhan_dien`, nên không ai chỉ định thì nó lùi
về `DEFAULT_STANDARD` là TT99; tập gold có cả TT200, mà mã 270 của TT200 là mã
280 của TT99. `--chuan-tu-gold` là điều kiện **oracle**, đo trích xuất tách
khỏi nhận diện. Bỏ cờ đi là chế độ **đầu-cuối**, pipeline tự nhận diện. Hiệu số
hai chế độ đo đúng một thứ: bước D của phương án C đáng giá bao nhiêu.

Chấm ở mức TRƯỜNG, **gộp tử và mẫu** qua các tài liệu chứ không lấy trung bình
của các tỷ lệ — TT200 có 26 chỉ tiêu còn TT99 có 27 nên hai cách cho hai con số
khác nhau, và chỉ cách đầu cộng dồn được cho bootstrap theo cụm.

## Cờ môi trường

Đặt thêm khi cần, và **phải ghi lại vào bảng kết quả** vì hai lượt khác cấu
hình không so với nhau được: `BAT_TANG_REPAIR=true` (bật tầng repair — lượt
chạy đó **không dùng được cho H1**), `USE_OCR_FIRST` (đọc từ `.env`),
`DISABLE_CONSTRAINT_GATE=true` (chế độ đo H1).

## Bốn cạm bẫy đã trả giá

1. **Ghi kết quả một lần ở cuối = mất sạch khi tiến trình bị giết.** Nay ghi
   sau **mỗi** tài liệu, và `--tiep-tuc` bỏ qua doc_id đã có.
2. **Pipeline tự in giá trị từng ô ra cùng stdout.** Nay `redirect_stdout` đổ
   chúng vào `data/output/tap_gold_<chế độ>_pipeline.log`. Bảng gộp ở stdout,
   chi tiết ở log — đừng trộn lại.
3. **`--chi BMP SBT` mà KHÔNG kèm `--tiep-tuc` sẽ ghi đè file kết quả bằng
   đúng 2 tài liệu**, xoá sạch lượt chạy trọn bộ; và không có `--tiep-tuc` thì
   file log cũng mở ở chế độ `w`, tức bị đè luôn. `tien_kiem.py` sao lưu cả
   hai trước mỗi lượt nên cạm bẫy này đã được bọc — miễn là chạy lệnh 1.
4. **Không nhìn thấy tiến độ theo trang trong lúc chạy.** File log mở ở chế độ
   đệm khối và chỉ `flush()` sau khi chấm xong cả một tài liệu, nên `tail -f`
   nó sẽ thấy log đứng im hàng chục phút. Đó KHÔNG phải dấu hiệu treo. Muốn
   biết tiến trình còn sống thì xem CPU-time của nó có tăng không.

## Lượt chạy bật cơ chế mới phải lưu certificate của cơ chế đó

Bài học đắt của lượt 30/08/2026: file kết quả không giữ `chung_chi_repair` lẫn
`ky_hieu_mau`, nên bảng số nói được kết quả mà không nói được vì sao — và cái
giá là chạy lại cả tập. Trước khi chạy một lượt bật cơ chế mới, kiểm rằng
`chay_mot_tai_lieu()` có ghi lại bản khai của cơ chế ấy.

## Mốc so sánh — đừng xoá cái nào

- `data/output/tap_gold_chuan_tu_gold_TRUOC-VA-2026-08-27.json` — trước hai bản vá 27/08
- `data/output/tap_gold_chuan_tu_gold_2026-08-29.json` — mốc tầng repair TẮT
- `data/output/tap_gold_chuan_tu_gold_2026-08-30.json` — mốc tầng repair BẬT

Mỗi lượt chạy trọn bộ đáng giữ phải được đặt tên có ngày **ngay khi xong**, vì
`tap_gold_chuan_tu_gold.json` là tên cố định và lượt sau sẽ đè. Bản sao máy ở
`sao_luu_tu_dong/` là lưới an toàn, **không** phải mốc so sánh: nó chỉ chống
mất dữ liệu, còn mốc là thứ người chọn giữ lại và đặt tên có nghĩa.

## Đọc kết quả

`data/output/tap_gold_<chế độ>.json` có `tong_hop`, `tung_tai_lieu` (kèm
`gia_tri_du_doan`, `he_so_don_vi_theo_truong`, `don_vi_theo_vung`,
`chung_chi_repair`, `ky_hieu_mau`), `khong_chay_duoc`, `thieu_pdf`.

**Bảng gộp không đọc được một mình** — phải tách theo chế độ lỗi trước, xem
`HANDOFF.md` mục 13.2 và 20.4. Và quy ước dấu của `HNG_2025H1_TT200` ngược với
phần còn lại của tập (Câu 14, mục 20.4b), việc này **chặn mọi phân tích gộp
qua tài liệu** cho tới khi người chủ trì quyết.

## Luật 1 — người gán nhãn phải mù với đầu ra pipeline

`tap_gold_*.json` và `tap_gold_*_pipeline.log` chứa giá trị từng ô. Chúng tồn
tại cho lượt phân tích về sau, **không** phải để người gán nhãn đọc. Khai báo
tài liệu nào đã mất quyền vào tập gán nhãn đôi nằm ở khoá `gan_nhan_doi` của
`data/nguon_gold.json`; đối chiếu với hiện trạng `data/output/` bằng
`PYTHONPATH=src python src/eval/tap_dong_thuan.py`.
