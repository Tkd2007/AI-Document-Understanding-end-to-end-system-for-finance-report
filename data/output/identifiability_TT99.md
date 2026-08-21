# Identifiability — chuẩn TT99

> Sinh tự động bởi `src/constraints.py`. Đối chiếu bảng ma trận bên dưới
> với Phụ lục của Thông tư trước khi tin vào bất kỳ con số nào ở đây.

## Tổng quan

- Số chỉ tiêu (n): **11**
- Số đẳng thức dùng được: **3**
- Hạng `rank(A)`: **3**
- Chiều không gian null `dim null(A)`: **8**
- Số field định vị được lỗi một-trường: **1 / 11**

Nghĩa là **8/11** chiều trong không gian lỗi hoàn toàn vô hình
với mọi phương pháp dựa trên ràng buộc — residual bằng 0 tuyệt đối.

## Ma trận ràng buộc A

Mỗi dòng một đẳng thức, `+1` cho thành phần, `-1` cho tổng, `.` cho 0.

| Đẳng thức | tai_san_ngan_han | hang_ton_kho | tai_san_dai_han | tong_tai_san | no_phai_tra | von_chu_so_huu | doanh_thu_thuan | gia_von_hang_ban | loi_nhuan_gop | loi_nhuan_truoc_thue | loi_nhuan_sau_thue |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Tài sản ngắn hạn + Tài sản dài hạn phải bằng Tổng tài sản | +1 | . | +1 | -1 | . | . | . | . | . | . | . |
| Nợ phải trả + Vốn chủ sở hữu phải bằng Tổng tài sản | . | . | . | -1 | +1 | +1 | . | . | . | . | . |
| Giá vốn hàng bán + Lợi nhuận gộp phải bằng Doanh thu thuần | . | . | . | . | . | . | -1 | +1 | +1 | . | . |

## Định vị lỗi một-trường

Định vị được khi cột của field khác 0 **và** không tỷ lệ với cột nào khác.

| Chỉ tiêu | Cột trong A | Định vị được | Ghi chú |
|---|---|---|---|
| `tai_san_ngan_han` | `+1 0 0` | KHÔNG | cột tỷ lệ với: tai_san_dai_han |
| `hang_ton_kho` | `0 0 0` | KHÔNG | **cột toàn 0 — không ràng buộc nào bảo vệ, lỗi không PHÁT HIỆN được** |
| `tai_san_dai_han` | `+1 0 0` | KHÔNG | cột tỷ lệ với: tai_san_ngan_han |
| `tong_tai_san` | `-1 -1 0` | có | cột riêng biệt |
| `no_phai_tra` | `0 +1 0` | KHÔNG | cột tỷ lệ với: von_chu_so_huu |
| `von_chu_so_huu` | `0 +1 0` | KHÔNG | cột tỷ lệ với: no_phai_tra |
| `doanh_thu_thuan` | `0 0 -1` | KHÔNG | cột tỷ lệ với: gia_von_hang_ban, loi_nhuan_gop |
| `gia_von_hang_ban` | `0 0 +1` | KHÔNG | cột tỷ lệ với: doanh_thu_thuan, loi_nhuan_gop |
| `loi_nhuan_gop` | `0 0 +1` | KHÔNG | cột tỷ lệ với: doanh_thu_thuan, gia_von_hang_ban |
| `loi_nhuan_truoc_thue` | `0 0 0` | KHÔNG | **cột toàn 0 — không ràng buộc nào bảo vệ, lỗi không PHÁT HIỆN được** |
| `loi_nhuan_sau_thue` | `0 0 0` | KHÔNG | **cột toàn 0 — không ràng buộc nào bảo vệ, lỗi không PHÁT HIỆN được** |

## Cặp chỉ tiêu không phân biệt được

Lỗi ở hai chỉ tiêu trong cùng một cặp cho residual pattern giống hệt nhau.

- `tai_san_ngan_han` ↔ `tai_san_dai_han`
- `no_phai_tra` ↔ `von_chu_so_huu`
- `doanh_thu_thuan` ↔ `gia_von_hang_ban`
- `doanh_thu_thuan` ↔ `loi_nhuan_gop`
- `gia_von_hang_ban` ↔ `loi_nhuan_gop`

## Cơ sở không gian null

Mỗi vector dưới đây là một hướng lỗi mà residual không nhìn thấy.

1. +0.479·`tai_san_ngan_han`  +0.483·`hang_ton_kho`  +0.113·`tai_san_dai_han`  +0.592·`tong_tai_san`  +0.296·`no_phai_tra`  +0.296·`von_chu_so_huu`
2. +0.125·`tai_san_ngan_han`  -0.612·`hang_ton_kho`  +0.125·`tai_san_dai_han`  +0.250·`tong_tai_san`  +0.625·`no_phai_tra`  -0.375·`von_chu_so_huu`
3. +0.125·`tai_san_ngan_han`  -0.612·`hang_ton_kho`  +0.125·`tai_san_dai_han`  +0.250·`tong_tai_san`  -0.375·`no_phai_tra`  +0.625·`von_chu_so_huu`
4. -0.349·`tai_san_ngan_han`  +0.075·`hang_ton_kho`  +0.440·`tai_san_dai_han`  +0.092·`tong_tai_san`  +0.046·`no_phai_tra`  +0.046·`von_chu_so_huu`  +0.667·`doanh_thu_thuan`  +0.333·`gia_von_hang_ban`  +0.333·`loi_nhuan_gop`
5. +0.349·`tai_san_ngan_han`  -0.075·`hang_ton_kho`  -0.440·`tai_san_dai_han`  -0.092·`tong_tai_san`  -0.046·`no_phai_tra`  -0.046·`von_chu_so_huu`  +0.333·`doanh_thu_thuan`  +0.667·`gia_von_hang_ban`  -0.333·`loi_nhuan_gop`
6. +0.349·`tai_san_ngan_han`  -0.075·`hang_ton_kho`  -0.440·`tai_san_dai_han`  -0.092·`tong_tai_san`  -0.046·`no_phai_tra`  -0.046·`von_chu_so_huu`  +0.333·`doanh_thu_thuan`  -0.333·`gia_von_hang_ban`  +0.667·`loi_nhuan_gop`
7. +1.000·`loi_nhuan_truoc_thue`
8. +1.000·`loi_nhuan_sau_thue`
