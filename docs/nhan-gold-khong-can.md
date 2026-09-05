# Nhãn gold không cân — bảng tra để kiểm tay

Sinh bởi `src/eval/do_lech_gold.py`. Cột **nhãn** là số đang ghi trong
`data/gold/`; cột **đẳng thức đòi** là số suy ra từ các dòng còn lại.

## Tóm tắt

- Tập gold: **70** tài liệu.
- **4** tài liệu lệch THẬT (từ 2,000,000 đồng trở lên), tổng 4 chỗ.
- **15** tài liệu lệch cỡ làm tròn, tổng 22 chỗ.

Mức lệch cỡ làm tròn nhiều khả năng là chính báo cáo in ra đã làm tròn,
không phải chép sai. Nhưng chúng vẫn làm phần dư khác 0, nên tầng ràng buộc
thấy tài liệu "không cân" và mọi phương pháp sẽ đi tìm một ô sai không tồn
tại — vì vậy vẫn phải quyết xử lý thế nào, không bỏ qua được.

Lệch thật: `DVD_2010Q4_TT200`, `FLC_2021Q4_TT200`, `PVD_2023Q4_TT200`, `VNM_2023Q2_TT200`

**4/4 chỗ lệch thật đã có ghi chú của người gán
nhãn giải thích nguyên nhân.** Ghi chú in kèm từng mục bên dưới. ĐỌC NÓ
trước khi mở tài liệu ra kiểm — phần lớn đã được kiểm rồi.


## LỆCH THẬT (4 chỗ)

### `DVD_2010Q4_TT200` — lệch +560,145,542 đồng

*B02 dạng trừ: Mã 60 = Mã 50 − Mã 51 − Mã 52*  
Đơn vị nhân 1, quy ước dấu `tru`.

> **Người gán nhãn đã ghi chú:** bản TT200 năm 2010 này, 52 đáng lẽ âm nhưng lại ghi trong báo cáo là dương.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B02 | 60 | `loi_nhuan_sau_thue` | 72,974,135,566 |
| thành phần | B02 | 51 | `thue_tndn_hien_hanh` | 30,375,875,073 |
| thành phần | B02 | 52 | `thue_tndn_hoan_lai` | 280,072,771 |
| **tổng** | **B02** | **50** | **`loi_nhuan_truoc_thue`** | **103,069,937,868** |

**Đẳng thức đòi `loi_nhuan_truoc_thue` = 102,509,792,326**, nhãn ghi 103,069,937,868 — lệch +560,145,542.

### `FLC_2021Q4_TT200` — lệch -49,409,493,606 đồng

*B03: Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61, và mã 70 ≡ mã 110 trên B01 — LIÊN KẾT CHÉO GIỮA HAI BIỂU MẪU*  
Đơn vị nhân 1, quy ước dấu `tru`.

> **Người gán nhãn đã ghi chú:** mã 70 ở B03 trong tài liệu này không giống với 110 trên B01, có vẻ không có rằng buộc.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B03 | 50 | `lctt_thuan` | -1,088,277,618,328 |
| thành phần | B03 | 60 | `tien_dau_ky` | 1,215,018,913,153 |
| thành phần | B03 | 61 | `anh_huong_ty_gia` | -70,176 |
| **tổng** | **B01** | **110** | **`tien_va_tuong_duong_tien`** | **176,150,718,255** |

**Đẳng thức đòi `tien_va_tuong_duong_tien` = 225,560,211,861**, nhãn ghi 176,150,718,255 — lệch -49,409,493,606.

### `PVD_2023Q4_TT200` — lệch -61,517,836,238 đồng

*B03: Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61, và mã 70 ≡ mã 110 trên B01 — LIÊN KẾT CHÉO GIỮA HAI BIỂU MẪU*  
Đơn vị nhân 1, quy ước dấu `tru`.

> **Người gán nhãn đã ghi chú:** mã 61 bảng b03 vẫn chưa được hoàn toàn tính ra, còn để 2 giá trị trong cùng 1 mã : "Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ" và "Chênh lệch tỷ giá do chuyển đổi báo cáo"

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B03 | 50 | `lctt_thuan` | 115,994,552,493 |
| thành phần | B03 | 60 | `tien_dau_ky` | 2,078,586,541,400 |
| thành phần | B03 | 61 | `anh_huong_ty_gia` | -51,772,851 |
| **tổng** | **B01** | **110** | **`tien_va_tuong_duong_tien`** | **2,256,047,157,280** |

**Đẳng thức đòi `tien_va_tuong_duong_tien` = 2,317,564,993,518**, nhãn ghi 2,256,047,157,280 — lệch -61,517,836,238.

### `VNM_2023Q2_TT200` — lệch -309,483,038 đồng

*B03: Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61, và mã 70 ≡ mã 110 trên B01 — LIÊN KẾT CHÉO GIỮA HAI BIỂU MẪU*  
Đơn vị nhân 1, quy ước dấu `tru`.

> **Người gán nhãn đã ghi chú:** code thiếu mục 62 cho bảng b03

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B03 | 50 | `lctt_thuan` | -717,238,348,960 |
| thành phần | B03 | 60 | `tien_dau_ky` | 2,299,943,527,624 |
| thành phần | B03 | 61 | `anh_huong_ty_gia` | -507,969,495 |
| **tổng** | **B01** | **110** | **`tien_va_tuong_duong_tien`** | **1,582,506,692,207** |

**Đẳng thức đòi `tien_va_tuong_duong_tien` = 1,582,816,175,245**, nhãn ghi 1,582,506,692,207 — lệch -309,483,038.


## LỆCH CỠ LÀM TRÒN — nhiều khả năng vô hại (22 chỗ)

### `BCM_2021Q1_TT200` — lệch -10 đồng

*B02 dạng trừ: Mã 60 = Mã 50 − Mã 51 − Mã 52*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B02 | 60 | `loi_nhuan_sau_thue` | 467,901,654,073 |
| thành phần | B02 | 51 | `thue_tndn_hien_hanh` | 68,069,473,287 |
| thành phần | B02 | 52 | `thue_tndn_hoan_lai` | -28,074,849,836 |
| **tổng** | **B02** | **50** | **`loi_nhuan_truoc_thue`** | **507,896,277,534** |

**Đẳng thức đòi `loi_nhuan_truoc_thue` = 507,896,277,544**, nhãn ghi 507,896,277,534 — lệch -10.

### `BMP_2026Q1_TT99` — lệch +3,000 đồng

*Nợ phải trả + Vốn chủ sở hữu phải bằng Tổng cộng nguồn vốn (mã 440)*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B01 | 300 | `no_phai_tra` | 609,699,918,525 |
| thành phần | B01 | 400 | `von_chu_so_huu` | 2,924,588,567,701 |
| **tổng** | **B01** | **440** | **`tong_nguon_von`** | **3,534,288,483,226** |

**Đẳng thức đòi `tong_nguon_von` = 3,534,288,480,226**, nhãn ghi 3,534,288,483,226 — lệch +3,000.

### `BSR_2026Q2_TT99` — lệch -436 đồng

*Nợ phải trả + Vốn chủ sở hữu phải bằng Tổng cộng nguồn vốn (mã 440)*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B01 | 300 | `no_phai_tra` | 31,058,819,041,448 |
| thành phần | B01 | 400 | `von_chu_so_huu` | 74,359,830,656,848 |
| **tổng** | **B01** | **440** | **`tong_nguon_von`** | **105,418,649,698,732** |

**Đẳng thức đòi `tong_nguon_von` = 105,418,649,699,168**, nhãn ghi 105,418,649,698,732 — lệch -436.

### `DLG_2026Q2_TT99` — lệch +327 đồng

*B02 dạng trừ: Mã 20 = Mã 10 − Mã 11*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B02 | 11 | `gia_von_hang_ban` | 23,030,541,730 |
| thành phần | B02 | 20 | `loi_nhuan_gop` | 240,061,044 |
| **tổng** | **B02** | **10** | **`doanh_thu_thuan`** | **23,270,602,447** |

**Đẳng thức đòi `doanh_thu_thuan` = 23,270,602,120**, nhãn ghi 23,270,602,447 — lệch +327.

### `DPM_2022Q3_TT200` — lệch -1,000 đồng

*Tài sản ngắn hạn + Tài sản dài hạn phải bằng Tổng tài sản*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B01 | 100 | `tai_san_ngan_han` | 12,683,948,261,515 |
| thành phần | B01 | 200 | `tai_san_dai_han` | 4,078,593,473,774 |
| **tổng** | **B01** | **270** | **`tong_tai_san`** | **16,762,541,736,289** |

**Đẳng thức đòi `tong_tai_san` = 16,762,541,737,289**, nhãn ghi 16,762,541,736,289 — lệch -1,000.

### `DPM_2022Q3_TT200` — lệch -1,000 đồng

*Tổng cộng nguồn vốn phải bằng Tổng cộng tài sản*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B01 | 440 | `tong_nguon_von` | 16,762,541,735,289 |
| **tổng** | **B01** | **270** | **`tong_tai_san`** | **16,762,541,736,289** |

**Đẳng thức đòi `tong_tai_san` = 16,762,541,737,289**, nhãn ghi 16,762,541,736,289 — lệch -1,000.

### `DPM_2022Q3_TT200` — lệch +1 đồng

*B02 dạng trừ: Mã 60 = Mã 50 − Mã 51 − Mã 52*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B02 | 60 | `loi_nhuan_sau_thue` | 1,001,356,860,558 |
| thành phần | B02 | 51 | `thue_tndn_hien_hanh` | 211,954,062,386 |
| thành phần | B02 | 52 | `thue_tndn_hoan_lai` | 0 |
| **tổng** | **B02** | **50** | **`loi_nhuan_truoc_thue`** | **1,213,310,922,943** |

**Đẳng thức đòi `loi_nhuan_truoc_thue` = 1,213,310,922,942**, nhãn ghi 1,213,310,922,943 — lệch +1.

### `GAS_2023Q1_TT200` — lệch -1,000 đồng

*Tài sản ngắn hạn + Tài sản dài hạn phải bằng Tổng tài sản*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B01 | 100 | `tai_san_ngan_han` | 57,952,012,334,363 |
| thành phần | B01 | 200 | `tai_san_dai_han` | 26,176,371,445,281 |
| **tổng** | **B01** | **270** | **`tong_tai_san`** | **84,128,383,780,644** |

**Đẳng thức đòi `tong_tai_san` = 84,128,383,781,644**, nhãn ghi 84,128,383,780,644 — lệch -1,000.

### `GAS_2023Q1_TT200` — lệch -3,000 đồng

*B03: Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61, và mã 70 ≡ mã 110 trên B01 — LIÊN KẾT CHÉO GIỮA HAI BIỂU MẪU*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B03 | 50 | `lctt_thuan` | 2,165,875,053,901 |
| thành phần | B03 | 60 | `tien_dau_ky` | 10,550,229,675,118 |
| thành phần | B03 | 61 | `anh_huong_ty_gia` | -2,091,163,905 |
| **tổng** | **B01** | **110** | **`tien_va_tuong_duong_tien`** | **12,714,013,568,114** |

**Đẳng thức đòi `tien_va_tuong_duong_tien` = 12,714,013,571,114**, nhãn ghi 12,714,013,568,114 — lệch -3,000.

### `GAS_2023Q1_TT200` — lệch +1,000,000 đồng

*Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn (TT200: mã 100 = 110+120+130+140+150)*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B01 | 110 | `tien_va_tuong_duong_tien` | 12,714,013,568,114 |
| thành phần | B01 | 120 | `dau_tu_tc_ngan_han` | 24,165,496,262,737 |
| thành phần | B01 | 130 | `phai_thu_ngan_han` | 18,097,175,503,262 |
| thành phần | B01 | 140 | `hang_ton_kho` | 2,127,765,124,993 |
| thành phần | B01 | 150 | `tsnh_khac` | 847,562,875,257 |
| **tổng** | **B01** | **100** | **`tai_san_ngan_han`** | **57,952,012,334,363** |

**Đẳng thức đòi `tai_san_ngan_han` = 57,952,011,334,363**, nhãn ghi 57,952,012,334,363 — lệch +1,000,000.

### `GEX_2026Q2_TT99` — lệch +3,000 đồng

*B03: Mã số 50 = Mã số 20 + Mã số 30 + Mã số 40*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B03 | 20 | `lctt_hdkd` | 1,237,838,816,060 |
| thành phần | B03 | 30 | `lctt_dau_tu` | -15,965,886,691,695 |
| thành phần | B03 | 40 | `lctt_tai_chinh` | 11,820,362,923,635 |
| **tổng** | **B03** | **50** | **`lctt_thuan`** | **-2,907,684,955,000** |

**Đẳng thức đòi `lctt_thuan` = -2,907,684,958,000**, nhãn ghi -2,907,684,955,000 — lệch +3,000.

### `GMD_2023Q3_TT200` — lệch +2 đồng

*Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn (TT200: mã 100 = 110+120+130+140+150)*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B01 | 110 | `tien_va_tuong_duong_tien` | 1,014,007,811,984 |
| thành phần | B01 | 120 | `dau_tu_tc_ngan_han` | 535,220,581,555 |
| thành phần | B01 | 130 | `phai_thu_ngan_han` | 1,245,739,363,611 |
| thành phần | B01 | 140 | `hang_ton_kho` | 65,953,873,992 |
| thành phần | B01 | 150 | `tsnh_khac` | 291,670,519,248 |
| **tổng** | **B01** | **100** | **`tai_san_ngan_han`** | **3,152,592,150,388** |

**Đẳng thức đòi `tai_san_ngan_han` = 3,152,592,150,386**, nhãn ghi 3,152,592,150,388 — lệch +2.

### `GVR_2026Q2_TT99` — lệch +1 đồng

*Tài sản ngắn hạn + Tài sản dài hạn phải bằng Tổng tài sản*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B01 | 100 | `tai_san_ngan_han` | 37,897,604,212,888 |
| thành phần | B01 | 200 | `tai_san_dai_han` | 52,366,345,316,291 |
| **tổng** | **B01** | **280** | **`tong_tai_san`** | **90,263,949,529,178** |

**Đẳng thức đòi `tong_tai_san` = 90,263,949,529,177**, nhãn ghi 90,263,949,529,178 — lệch +1.

### `GVR_2026Q2_TT99` — lệch -1 đồng

*B03: Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61, và mã 70 ≡ mã 110 trên B01 — LIÊN KẾT CHÉO GIỮA HAI BIỂU MẪU*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B03 | 50 | `lctt_thuan` | 38,605,564,362 |
| thành phần | B03 | 60 | `tien_dau_ky` | 8,237,433,366,831 |
| thành phần | B03 | 61 | `anh_huong_ty_gia` | -3,522,923,402 |
| **tổng** | **B01** | **110** | **`tien_va_tuong_duong_tien`** | **8,272,516,007,792** |

**Đẳng thức đòi `tien_va_tuong_duong_tien` = 8,272,516,007,793**, nhãn ghi 8,272,516,007,792 — lệch -1.

### `HVN_2026Q2_TT99` — lệch +1 đồng

*B02 dạng trừ: Mã 60 = Mã 50 − Mã 51 − Mã 52*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B02 | 60 | `loi_nhuan_sau_thue` | -606,237,636,293 |
| thành phần | B02 | 51 | `thue_tndn_hien_hanh` | 163,668,417,019 |
| thành phần | B02 | 52 | `thue_tndn_hoan_lai` | 1,402,666,006 |
| **tổng** | **B02** | **50** | **`loi_nhuan_truoc_thue`** | **-441,166,553,269** |

**Đẳng thức đòi `loi_nhuan_truoc_thue` = -441,166,553,270**, nhãn ghi -441,166,553,269 — lệch +1.

### `OGC_2019Q4_TT200` — lệch +1,000 đồng

*Lợi nhuận thuần từ HĐKD + Lợi nhuận khác phải bằng Lợi nhuận trước thuế*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B02 | 30 | `ln_thuan_hdkd` | 36,317,758,838 |
| thành phần | B02 | 40 | `ln_khac` | -2,722,792,696 |
| **tổng** | **B02** | **50** | **`loi_nhuan_truoc_thue`** | **33,594,965,142** |

**Đẳng thức đòi `loi_nhuan_truoc_thue` = 33,594,964,142**, nhãn ghi 33,594,965,142 — lệch +1,000.

### `REE_2023Q2_TT200` — lệch -1 đồng

*Nợ phải trả + Vốn chủ sở hữu phải bằng Tổng cộng nguồn vốn (mã 440)*  
Đơn vị nhân 1, quy ước dấu `tong`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B01 | 300 | `no_phai_tra` | 14,212,948,902,385 |
| thành phần | B01 | 400 | `von_chu_so_huu` | 20,059,277,233,511 |
| **tổng** | **B01** | **440** | **`tong_nguon_von`** | **34,272,226,135,897** |

**Đẳng thức đòi `tong_nguon_von` = 34,272,226,135,898**, nhãn ghi 34,272,226,135,897 — lệch -1.

### `REE_2023Q2_TT200` — lệch -1 đồng

*B03: Mã số 50 = Mã số 20 + Mã số 30 + Mã số 40*  
Đơn vị nhân 1, quy ước dấu `tong`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B03 | 20 | `lctt_hdkd` | 1,064,760,705,585 |
| thành phần | B03 | 30 | `lctt_dau_tu` | 498,923,933,804 |
| thành phần | B03 | 40 | `lctt_tai_chinh` | -1,094,787,716,252 |
| **tổng** | **B03** | **50** | **`lctt_thuan`** | **468,896,923,138** |

**Đẳng thức đòi `lctt_thuan` = 468,896,923,139**, nhãn ghi 468,896,923,138 — lệch -1.

### `VCG_2022Q4_TT200` — lệch +30,001 đồng

*Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn (TT200: mã 100 = 110+120+130+140+150)*  
Đơn vị nhân 1, quy ước dấu `tong`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B01 | 110 | `tien_va_tuong_duong_tien` | 1,749,102,692,670 |
| thành phần | B01 | 120 | `dau_tu_tc_ngan_han` | 1,426,126,441,787 |
| thành phần | B01 | 130 | `phai_thu_ngan_han` | 9,376,166,715,864 |
| thành phần | B01 | 140 | `hang_ton_kho` | 6,767,187,228,994 |
| thành phần | B01 | 150 | `tsnh_khac` | 514,519,996,329 |
| **tổng** | **B01** | **100** | **`tai_san_ngan_han`** | **19,833,103,045,643** |

**Đẳng thức đòi `tai_san_ngan_han` = 19,833,103,015,642**, nhãn ghi 19,833,103,045,643 — lệch +30,001.

### `VHC_2025Q1_TT200` — lệch +80,000 đồng

*Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn (TT200: mã 100 = 110+120+130+140+150)*  
Đơn vị nhân 1, quy ước dấu `tong`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B01 | 110 | `tien_va_tuong_duong_tien` | 625,992,781,298 |
| thành phần | B01 | 120 | `dau_tu_tc_ngan_han` | 2,147,953,991,316 |
| thành phần | B01 | 130 | `phai_thu_ngan_han` | 2,306,528,049,394 |
| thành phần | B01 | 140 | `hang_ton_kho` | 1,102,447,595,935 |
| thành phần | B01 | 150 | `tsnh_khac` | 43,422,454,235 |
| **tổng** | **B01** | **100** | **`tai_san_ngan_han`** | **6,226,344,792,178** |

**Đẳng thức đòi `tai_san_ngan_han` = 6,226,344,712,178**, nhãn ghi 6,226,344,792,178 — lệch +80,000.

### `VOS_2026Q2_TT99` — lệch -10,000 đồng

*B03: Mã số 50 = Mã số 20 + Mã số 30 + Mã số 40*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B03 | 20 | `lctt_hdkd` | 166,662,964,986 |
| thành phần | B03 | 30 | `lctt_dau_tu` | -215,904,868,930 |
| thành phần | B03 | 40 | `lctt_tai_chinh` | -142,819,923,187 |
| **tổng** | **B03** | **50** | **`lctt_thuan`** | **-192,061,817,131** |

**Đẳng thức đòi `lctt_thuan` = -192,061,807,131**, nhãn ghi -192,061,817,131 — lệch -10,000.

### `VOS_2026Q2_TT99` — lệch +10,000 đồng

*B03: Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61, và mã 70 ≡ mã 110 trên B01 — LIÊN KẾT CHÉO GIỮA HAI BIỂU MẪU*  
Đơn vị nhân 1, quy ước dấu `tru`.

> Tài liệu này KHÔNG có ghi chú của người gán nhãn.

| Vai trò | Biểu mẫu | Mã số | Chỉ tiêu | Nhãn đang ghi |
|---|---|---:|---|---:|
| thành phần | B03 | 50 | `lctt_thuan` | -192,061,817,131 |
| thành phần | B03 | 60 | `tien_dau_ky` | 769,168,118,882 |
| thành phần | B03 | 61 | `anh_huong_ty_gia` | 909,041,328 |
| **tổng** | **B01** | **110** | **`tien_va_tuong_duong_tien`** | **578,015,333,079** |

**Đẳng thức đòi `tien_va_tuong_duong_tien` = 578,015,323,079**, nhãn ghi 578,015,333,079 — lệch +10,000.

