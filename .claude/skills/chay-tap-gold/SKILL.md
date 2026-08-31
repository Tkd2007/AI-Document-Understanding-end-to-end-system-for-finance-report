---
name: chay-tap-gold
description: Chấm pipeline ViFinKIE trên tập gold có nhãn tay bằng src/eval/chay_tap_gold.py. Dùng khi cần chạy hoặc chạy lại phép đo trên tập gold, chấm một vài mã (--chi), nối một lượt chạy bị đứt (--tiep-tuc), hoặc đọc/so sánh kết quả trong data/output/tap_gold_*.json. Chứa cách chạy, ba cạm bẫy đã trả giá, và các mốc so sánh không được xoá.
---

# Chấm pipeline trên tập gold

**Tốn tiền gọi API thật và chậm — 5 đến 50 phút một tài liệu** (nhánh OCR chạy
CPU chiếm phần lớn). Đừng chạy trọn bộ nếu chỉ cần kiểm một tài liệu.

## Lệnh

```bash
# Trọn bộ, chế độ oracle: lấy chuẩn mẫu biểu từ nhãn
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --chuan-tu-gold

# Chế độ đầu-cuối: pipeline tự nhận diện chuẩn
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py

# Nối lượt chạy bị đứt (bỏ qua doc_id đã có trong file kết quả)
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --tiep-tuc --chuan-tu-gold

# Chỉ vài mã — ĐỌC CẠM BẪY 3 TRƯỚC KHI DÙNG
PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --chuan-tu-gold --chi HNG
```

`PYTHONPATH=src` **bắt buộc**: thiếu nó thì `from eval.metrics import ...` nổ
`ModuleNotFoundError: No module named 'eval'` ngay dòng import.

Cờ môi trường đặt thêm khi cần, phải ghi lại vào bảng kết quả vì hai lượt khác
cấu hình không so với nhau được: `BAT_TANG_REPAIR=true` (bật tầng repair —
lượt chạy đó **không dùng được cho H1**), `USE_OCR_FIRST` (đọc từ `.env`),
`DISABLE_CONSTRAINT_GATE=true` (chế độ đo H1).

## Hai chế độ, và khoảng cách giữa chúng chính là phép đo

`router.chon_chuan` chưa có nguồn `nhan_dien`, nên không ai chỉ định thì nó lùi
về `DEFAULT_STANDARD` là TT99; tập gold có 5 tài liệu TT200, mà mã 270 của
TT200 là mã 280 của TT99. `--chuan-tu-gold` là điều kiện **oracle**, đo trích
xuất tách khỏi nhận diện. Hiệu số hai chế độ đo đúng một thứ: bước D của
phương án C đáng giá bao nhiêu.

Chấm ở mức TRƯỜNG, **gộp tử và mẫu** qua các tài liệu chứ không lấy trung bình
của các tỷ lệ — TT200 có 26 chỉ tiêu còn TT99 có 27 nên hai cách cho hai con số
khác nhau, và chỉ cách đầu cộng dồn được cho bootstrap theo cụm.

## Ba cạm bẫy đã trả giá

1. **Ghi kết quả một lần ở cuối = mất sạch khi tiến trình bị giết.** Nay ghi
   sau **mỗi** tài liệu, và `--tiep-tuc` bỏ qua doc_id đã có.
2. **Pipeline tự in giá trị từng ô ra cùng stdout.** Nay `redirect_stdout` đổ
   chúng vào `data/output/tap_gold_<chế độ>_pipeline.log`. Bảng gộp ở stdout,
   chi tiết ở log — đừng trộn lại.
3. **`--chi BMP SBT` mà KHÔNG kèm `--tiep-tuc` sẽ ghi đè
   `tap_gold_chuan_tu_gold.json` bằng đúng 2 tài liệu**, xoá sạch kết quả trọn
   bộ. **Sao lưu file kết quả trước khi chạy `--chi`.**

## Mốc so sánh — đừng xoá cái nào

- `data/output/tap_gold_chuan_tu_gold_TRUOC-VA-2026-08-27.json` — trước hai bản vá 27/08
- `data/output/tap_gold_chuan_tu_gold_2026-08-29.json` — mốc tầng repair TẮT
- `data/output/tap_gold_chuan_tu_gold_2026-08-30.json` — mốc tầng repair BẬT

Mỗi lượt chạy trọn bộ phải được sao lưu sang tên có ngày **ngay khi xong**,
vì `tap_gold_chuan_tu_gold.json` là tên cố định và lượt sau sẽ đè.

## Lượt chạy bật cơ chế mới phải lưu certificate của cơ chế đó

Bài học đắt của lượt 30/08/2026: file kết quả không giữ `chung_chi_repair` lẫn
`ky_hieu_mau`, nên bảng số nói được kết quả mà không nói được vì sao — và cái
giá là chạy lại cả tập. Trước khi chạy một lượt bật cơ chế mới, kiểm rằng
`chay_mot_tai_lieu()` có ghi lại bản khai của cơ chế ấy.

## Đọc kết quả

`data/output/tap_gold_<chế độ>.json` có `tong_hop`, `tung_tai_lieu` (kèm
`gia_tri_du_doan`, `he_so_don_vi_theo_truong`, `don_vi_theo_vung`,
`chung_chi_repair`, `ky_hieu_mau`), `khong_chay_duoc`, `thieu_pdf`.

**Bảng gộp không đọc được một mình** — phải tách theo chế độ lỗi trước, xem
`HANDOFF.md` mục 13.2 và 20.4. Và `HNG_2025H1_TT200` có quy ước dấu ngược với
phần còn lại của tập (Câu 14, mục 20.4b), việc này **chặn mọi phân tích gộp
qua tài liệu** cho tới khi người chủ trì quyết.

## Ràng buộc: tài liệu đã chạy pipeline thì đáp án đã lộ

`tap_gold_*.json` và `tap_gold_*_pipeline.log` chứa giá trị từng ô, nên 10 tài
liệu đã chấm cùng `VNM_2026Q1_TT99` bị **loại vĩnh viễn khỏi tập gán nhãn
đôi**. Khai báo ở khoá `gan_nhan_doi` của `data/nguon_gold.json`, đối chiếu
bằng `PYTHONPATH=src python src/eval/tap_dong_thuan.py`.
