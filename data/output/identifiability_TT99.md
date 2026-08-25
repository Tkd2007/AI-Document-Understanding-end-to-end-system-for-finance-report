# Identifiability — chuẩn TT99

> Sinh tự động bởi `src/constraints.py`. Đối chiếu bảng ma trận bên dưới
> với Phụ lục của Thông tư trước khi tin vào bất kỳ con số nào ở đây.

## Tổng quan

- Số chỉ tiêu (n): **27**
- Số đẳng thức dùng được: **9**
- Hạng `rank(A)`: **9**
- Chiều không gian null `dim null(A)`: **18**
- Số field định vị được lỗi một-trường: **7 / 27**
- Số field có **cột toàn 0** (lỗi không PHÁT HIỆN được): **0 / 27** — không có

Nghĩa là **18/27** chiều trong không gian lỗi hoàn toàn vô hình
với mọi phương pháp dựa trên ràng buộc — residual bằng 0 tuyệt đối.

## Ma trận ràng buộc A

Mỗi dòng một đẳng thức, `+1` cho thành phần, `-1` cho tổng, `.` cho 0.

| Đẳng thức | tai_san_ngan_han | tien_va_tuong_duong_tien | dau_tu_tc_ngan_han | phai_thu_ngan_han | hang_ton_kho | tai_san_sinh_hoc_ngan_han | tsnh_khac | tai_san_dai_han | tong_tai_san | no_phai_tra | von_chu_so_huu | tong_nguon_von | doanh_thu_thuan | gia_von_hang_ban | loi_nhuan_gop | ln_thuan_hdkd | ln_khac | loi_nhuan_truoc_thue | thue_tndn_hien_hanh | thue_tndn_hoan_lai | loi_nhuan_sau_thue | lctt_hdkd | lctt_dau_tu | lctt_tai_chinh | lctt_thuan | tien_dau_ky | anh_huong_ty_gia |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tài sản ngắn hạn + Tài sản dài hạn phải bằng Tổng tài sản | +1 | . | . | . | . | . | . | +1 | -1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| Nợ phải trả + Vốn chủ sở hữu phải bằng Tổng cộng nguồn vốn (mã 440) | . | . | . | . | . | . | . | . | . | +1 | +1 | -1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| Tổng cộng nguồn vốn phải bằng Tổng cộng tài sản | . | . | . | . | . | . | . | . | -1 | . | . | +1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| Giá vốn hàng bán + Lợi nhuận gộp phải bằng Doanh thu thuần | . | . | . | . | . | . | . | . | . | . | . | . | -1 | +1 | +1 | . | . | . | . | . | . | . | . | . | . | . | . |
| Lợi nhuận thuần từ HĐKD + Lợi nhuận khác phải bằng Lợi nhuận trước thuế | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | -1 | . | . | . | . | . | . | . | . | . |
| Lợi nhuận sau thuế + chi phí thuế hiện hành + hoãn lại phải bằng Lợi nhuận trước thuế | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | -1 | +1 | +1 | +1 | . | . | . | . | . | . |
| B03: Mã số 50 = Mã số 20 + Mã số 30 + Mã số 40 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 | -1 | . | . |
| B03: Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61, và mã 70 ≡ mã 110 trên B01 — LIÊN KẾT CHÉO GIỮA HAI BIỂU MẪU | . | -1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 |
| Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn (TT99: mã 100 = 110+120+130+140+150+160) | -1 | +1 | +1 | +1 | +1 | +1 | +1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |

## Định vị lỗi một-trường

Định vị được khi cột của field khác 0 **và** không tỷ lệ với cột nào khác.

| Chỉ tiêu | Cột trong A | Định vị được | Ghi chú |
|---|---|---|---|
| `tai_san_ngan_han` | `+1 0 0 0 0 0 0 0 -1` | có | cột riêng biệt |
| `tien_va_tuong_duong_tien` | `0 0 0 0 0 0 0 -1 +1` | có | cột riêng biệt |
| `dau_tu_tc_ngan_han` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: hang_ton_kho, phai_thu_ngan_han, tai_san_sinh_hoc_ngan_han, tsnh_khac |
| `phai_thu_ngan_han` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, tai_san_sinh_hoc_ngan_han, tsnh_khac |
| `hang_ton_kho` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, phai_thu_ngan_han, tai_san_sinh_hoc_ngan_han, tsnh_khac |
| `tai_san_sinh_hoc_ngan_han` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, phai_thu_ngan_han, tsnh_khac |
| `tsnh_khac` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, phai_thu_ngan_han, tai_san_sinh_hoc_ngan_han |
| `tai_san_dai_han` | `+1 0 0 0 0 0 0 0 0` | có | cột riêng biệt |
| `tong_tai_san` | `-1 0 -1 0 0 0 0 0 0` | có | cột riêng biệt |
| `no_phai_tra` | `0 +1 0 0 0 0 0 0 0` | KHÔNG | cột tỷ lệ với: von_chu_so_huu |
| `von_chu_so_huu` | `0 +1 0 0 0 0 0 0 0` | KHÔNG | cột tỷ lệ với: no_phai_tra |
| `tong_nguon_von` | `0 -1 +1 0 0 0 0 0 0` | có | cột riêng biệt |
| `doanh_thu_thuan` | `0 0 0 -1 0 0 0 0 0` | KHÔNG | cột tỷ lệ với: gia_von_hang_ban, loi_nhuan_gop |
| `gia_von_hang_ban` | `0 0 0 +1 0 0 0 0 0` | KHÔNG | cột tỷ lệ với: doanh_thu_thuan, loi_nhuan_gop |
| `loi_nhuan_gop` | `0 0 0 +1 0 0 0 0 0` | KHÔNG | cột tỷ lệ với: doanh_thu_thuan, gia_von_hang_ban |
| `ln_thuan_hdkd` | `0 0 0 0 +1 0 0 0 0` | KHÔNG | cột tỷ lệ với: ln_khac |
| `ln_khac` | `0 0 0 0 +1 0 0 0 0` | KHÔNG | cột tỷ lệ với: ln_thuan_hdkd |
| `loi_nhuan_truoc_thue` | `0 0 0 0 -1 -1 0 0 0` | có | cột riêng biệt |
| `thue_tndn_hien_hanh` | `0 0 0 0 0 +1 0 0 0` | KHÔNG | cột tỷ lệ với: loi_nhuan_sau_thue, thue_tndn_hoan_lai |
| `thue_tndn_hoan_lai` | `0 0 0 0 0 +1 0 0 0` | KHÔNG | cột tỷ lệ với: loi_nhuan_sau_thue, thue_tndn_hien_hanh |
| `loi_nhuan_sau_thue` | `0 0 0 0 0 +1 0 0 0` | KHÔNG | cột tỷ lệ với: thue_tndn_hien_hanh, thue_tndn_hoan_lai |
| `lctt_hdkd` | `0 0 0 0 0 0 +1 0 0` | KHÔNG | cột tỷ lệ với: lctt_dau_tu, lctt_tai_chinh |
| `lctt_dau_tu` | `0 0 0 0 0 0 +1 0 0` | KHÔNG | cột tỷ lệ với: lctt_hdkd, lctt_tai_chinh |
| `lctt_tai_chinh` | `0 0 0 0 0 0 +1 0 0` | KHÔNG | cột tỷ lệ với: lctt_dau_tu, lctt_hdkd |
| `lctt_thuan` | `0 0 0 0 0 0 -1 +1 0` | có | cột riêng biệt |
| `tien_dau_ky` | `0 0 0 0 0 0 0 +1 0` | KHÔNG | cột tỷ lệ với: anh_huong_ty_gia |
| `anh_huong_ty_gia` | `0 0 0 0 0 0 0 +1 0` | KHÔNG | cột tỷ lệ với: tien_dau_ky |

## Cặp chỉ tiêu không phân biệt được

Lỗi ở hai chỉ tiêu trong cùng một cặp cho residual pattern giống hệt nhau.

- `dau_tu_tc_ngan_han` ↔ `phai_thu_ngan_han`
- `dau_tu_tc_ngan_han` ↔ `hang_ton_kho`
- `dau_tu_tc_ngan_han` ↔ `tai_san_sinh_hoc_ngan_han`
- `dau_tu_tc_ngan_han` ↔ `tsnh_khac`
- `phai_thu_ngan_han` ↔ `hang_ton_kho`
- `phai_thu_ngan_han` ↔ `tai_san_sinh_hoc_ngan_han`
- `phai_thu_ngan_han` ↔ `tsnh_khac`
- `hang_ton_kho` ↔ `tai_san_sinh_hoc_ngan_han`
- `hang_ton_kho` ↔ `tsnh_khac`
- `tai_san_sinh_hoc_ngan_han` ↔ `tsnh_khac`
- `no_phai_tra` ↔ `von_chu_so_huu`
- `doanh_thu_thuan` ↔ `gia_von_hang_ban`
- `doanh_thu_thuan` ↔ `loi_nhuan_gop`
- `gia_von_hang_ban` ↔ `loi_nhuan_gop`
- `ln_thuan_hdkd` ↔ `ln_khac`
- `thue_tndn_hien_hanh` ↔ `thue_tndn_hoan_lai`
- `thue_tndn_hien_hanh` ↔ `loi_nhuan_sau_thue`
- `thue_tndn_hoan_lai` ↔ `loi_nhuan_sau_thue`
- `lctt_hdkd` ↔ `lctt_dau_tu`
- `lctt_hdkd` ↔ `lctt_tai_chinh`
- `lctt_dau_tu` ↔ `lctt_tai_chinh`
- `tien_dau_ky` ↔ `anh_huong_ty_gia`

## Cơ sở không gian null

Mỗi vector dưới đây là một hướng lỗi mà residual không nhìn thấy.

1. +0.326·`tai_san_ngan_han`  -0.316·`tien_va_tuong_duong_tien`  +0.055·`dau_tu_tc_ngan_han`  +0.147·`phai_thu_ngan_han`  +0.147·`hang_ton_kho`  +0.147·`tai_san_sinh_hoc_ngan_han`  +0.147·`tsnh_khac`  -0.070·`tai_san_dai_han`  +0.256·`tong_tai_san`  +0.628·`no_phai_tra`  -0.372·`von_chu_so_huu`  +0.256·`tong_nguon_von`  -0.029·`lctt_hdkd`  -0.029·`lctt_dau_tu`  -0.029·`lctt_tai_chinh`  -0.086·`lctt_thuan`  -0.115·`tien_dau_ky`  -0.115·`anh_huong_ty_gia`
2. +0.326·`tai_san_ngan_han`  -0.316·`tien_va_tuong_duong_tien`  +0.055·`dau_tu_tc_ngan_han`  +0.147·`phai_thu_ngan_han`  +0.147·`hang_ton_kho`  +0.147·`tai_san_sinh_hoc_ngan_han`  +0.147·`tsnh_khac`  -0.070·`tai_san_dai_han`  +0.256·`tong_tai_san`  -0.372·`no_phai_tra`  +0.628·`von_chu_so_huu`  +0.256·`tong_nguon_von`  -0.029·`lctt_hdkd`  -0.029·`lctt_dau_tu`  -0.029·`lctt_tai_chinh`  -0.086·`lctt_thuan`  -0.115·`tien_dau_ky`  -0.115·`anh_huong_ty_gia`
3. -0.017·`tai_san_ngan_han`  +0.431·`tien_va_tuong_duong_tien`  -0.493·`dau_tu_tc_ngan_han`  +0.011·`phai_thu_ngan_han`  +0.011·`hang_ton_kho`  +0.011·`tai_san_sinh_hoc_ngan_han`  +0.011·`tsnh_khac`  +0.391·`tai_san_dai_han`  +0.374·`tong_tai_san`  +0.187·`no_phai_tra`  +0.187·`von_chu_so_huu`  +0.374·`tong_nguon_von`  +0.039·`lctt_hdkd`  +0.039·`lctt_dau_tu`  +0.039·`lctt_tai_chinh`  +0.118·`lctt_thuan`  +0.157·`tien_dau_ky`  +0.157·`anh_huong_ty_gia`
4. -0.030·`tai_san_ngan_han`  -0.060·`tien_va_tuong_duong_tien`  -0.222·`dau_tu_tc_ngan_han`  +0.496·`phai_thu_ngan_han`  -0.082·`hang_ton_kho`  -0.082·`tai_san_sinh_hoc_ngan_han`  -0.082·`tsnh_khac`  -0.037·`tai_san_dai_han`  -0.067·`tong_tai_san`  -0.034·`no_phai_tra`  -0.034·`von_chu_so_huu`  -0.067·`tong_nguon_von`  +0.667·`doanh_thu_thuan`  +0.333·`gia_von_hang_ban`  +0.333·`loi_nhuan_gop`  -0.005·`lctt_hdkd`  -0.005·`lctt_dau_tu`  -0.005·`lctt_tai_chinh`  -0.016·`lctt_thuan`  -0.022·`tien_dau_ky`  -0.022·`anh_huong_ty_gia`
5. +0.030·`tai_san_ngan_han`  +0.060·`tien_va_tuong_duong_tien`  +0.222·`dau_tu_tc_ngan_han`  -0.496·`phai_thu_ngan_han`  +0.082·`hang_ton_kho`  +0.082·`tai_san_sinh_hoc_ngan_han`  +0.082·`tsnh_khac`  +0.037·`tai_san_dai_han`  +0.067·`tong_tai_san`  +0.034·`no_phai_tra`  +0.034·`von_chu_so_huu`  +0.067·`tong_nguon_von`  +0.333·`doanh_thu_thuan`  +0.667·`gia_von_hang_ban`  -0.333·`loi_nhuan_gop`  +0.005·`lctt_hdkd`  +0.005·`lctt_dau_tu`  +0.005·`lctt_tai_chinh`  +0.016·`lctt_thuan`  +0.022·`tien_dau_ky`  +0.022·`anh_huong_ty_gia`
6. +0.030·`tai_san_ngan_han`  +0.060·`tien_va_tuong_duong_tien`  +0.222·`dau_tu_tc_ngan_han`  -0.496·`phai_thu_ngan_han`  +0.082·`hang_ton_kho`  +0.082·`tai_san_sinh_hoc_ngan_han`  +0.082·`tsnh_khac`  +0.037·`tai_san_dai_han`  +0.067·`tong_tai_san`  +0.034·`no_phai_tra`  +0.034·`von_chu_so_huu`  +0.067·`tong_nguon_von`  +0.333·`doanh_thu_thuan`  -0.333·`gia_von_hang_ban`  +0.667·`loi_nhuan_gop`  +0.005·`lctt_hdkd`  +0.005·`lctt_dau_tu`  +0.005·`lctt_tai_chinh`  +0.016·`lctt_thuan`  +0.022·`tien_dau_ky`  +0.022·`anh_huong_ty_gia`
7. +0.021·`tai_san_ngan_han`  +0.042·`tien_va_tuong_duong_tien`  +0.155·`dau_tu_tc_ngan_han`  +0.057·`phai_thu_ngan_han`  -0.520·`hang_ton_kho`  +0.231·`tai_san_sinh_hoc_ngan_han`  +0.057·`tsnh_khac`  +0.026·`tai_san_dai_han`  +0.047·`tong_tai_san`  +0.023·`no_phai_tra`  +0.023·`von_chu_so_huu`  +0.047·`tong_nguon_von`  +0.636·`ln_thuan_hdkd`  -0.364·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  +0.091·`thue_tndn_hien_hanh`  +0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`  +0.004·`lctt_hdkd`  +0.004·`lctt_dau_tu`  +0.004·`lctt_tai_chinh`  +0.011·`lctt_thuan`  +0.015·`tien_dau_ky`  +0.015·`anh_huong_ty_gia`
8. +0.021·`tai_san_ngan_han`  +0.042·`tien_va_tuong_duong_tien`  +0.155·`dau_tu_tc_ngan_han`  +0.057·`phai_thu_ngan_han`  -0.520·`hang_ton_kho`  +0.231·`tai_san_sinh_hoc_ngan_han`  +0.057·`tsnh_khac`  +0.026·`tai_san_dai_han`  +0.047·`tong_tai_san`  +0.023·`no_phai_tra`  +0.023·`von_chu_so_huu`  +0.047·`tong_nguon_von`  -0.364·`ln_thuan_hdkd`  +0.636·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  +0.091·`thue_tndn_hien_hanh`  +0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`  +0.004·`lctt_hdkd`  +0.004·`lctt_dau_tu`  +0.004·`lctt_tai_chinh`  +0.011·`lctt_thuan`  +0.015·`tien_dau_ky`  +0.015·`anh_huong_ty_gia`
9. -0.049·`tai_san_ngan_han`  -0.096·`tien_va_tuong_duong_tien`  -0.355·`dau_tu_tc_ngan_han`  -0.131·`phai_thu_ngan_han`  +0.447·`hang_ton_kho`  +0.217·`tai_san_sinh_hoc_ngan_han`  -0.131·`tsnh_khac`  -0.059·`tai_san_dai_han`  -0.108·`tong_tai_san`  -0.054·`no_phai_tra`  -0.054·`von_chu_so_huu`  -0.108·`tong_nguon_von`  +0.273·`ln_thuan_hdkd`  +0.273·`ln_khac`  +0.545·`loi_nhuan_truoc_thue`  +0.182·`thue_tndn_hien_hanh`  +0.182·`thue_tndn_hoan_lai`  +0.182·`loi_nhuan_sau_thue`  -0.009·`lctt_hdkd`  -0.009·`lctt_dau_tu`  -0.009·`lctt_tai_chinh`  -0.026·`lctt_thuan`  -0.035·`tien_dau_ky`  -0.035·`anh_huong_ty_gia`
10. +0.027·`tai_san_ngan_han`  +0.054·`tien_va_tuong_duong_tien`  +0.200·`dau_tu_tc_ngan_han`  +0.074·`phai_thu_ngan_han`  +0.074·`hang_ton_kho`  -0.448·`tai_san_sinh_hoc_ngan_han`  +0.074·`tsnh_khac`  +0.033·`tai_san_dai_han`  +0.061·`tong_tai_san`  +0.030·`no_phai_tra`  +0.030·`von_chu_so_huu`  +0.061·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  +0.727·`thue_tndn_hien_hanh`  -0.273·`thue_tndn_hoan_lai`  -0.273·`loi_nhuan_sau_thue`  +0.005·`lctt_hdkd`  +0.005·`lctt_dau_tu`  +0.005·`lctt_tai_chinh`  +0.015·`lctt_thuan`  +0.020·`tien_dau_ky`  +0.020·`anh_huong_ty_gia`
11. +0.027·`tai_san_ngan_han`  +0.054·`tien_va_tuong_duong_tien`  +0.200·`dau_tu_tc_ngan_han`  +0.074·`phai_thu_ngan_han`  +0.074·`hang_ton_kho`  -0.448·`tai_san_sinh_hoc_ngan_han`  +0.074·`tsnh_khac`  +0.033·`tai_san_dai_han`  +0.061·`tong_tai_san`  +0.030·`no_phai_tra`  +0.030·`von_chu_so_huu`  +0.061·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  -0.273·`thue_tndn_hien_hanh`  +0.727·`thue_tndn_hoan_lai`  -0.273·`loi_nhuan_sau_thue`  +0.005·`lctt_hdkd`  +0.005·`lctt_dau_tu`  +0.005·`lctt_tai_chinh`  +0.015·`lctt_thuan`  +0.020·`tien_dau_ky`  +0.020·`anh_huong_ty_gia`
12. +0.027·`tai_san_ngan_han`  +0.054·`tien_va_tuong_duong_tien`  +0.200·`dau_tu_tc_ngan_han`  +0.074·`phai_thu_ngan_han`  +0.074·`hang_ton_kho`  -0.448·`tai_san_sinh_hoc_ngan_han`  +0.074·`tsnh_khac`  +0.033·`tai_san_dai_han`  +0.061·`tong_tai_san`  +0.030·`no_phai_tra`  +0.030·`von_chu_so_huu`  +0.061·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  -0.273·`thue_tndn_hien_hanh`  -0.273·`thue_tndn_hoan_lai`  +0.727·`loi_nhuan_sau_thue`  +0.005·`lctt_hdkd`  +0.005·`lctt_dau_tu`  +0.005·`lctt_tai_chinh`  +0.015·`lctt_thuan`  +0.020·`tien_dau_ky`  +0.020·`anh_huong_ty_gia`
13. +0.110·`tai_san_ngan_han`  +0.122·`tien_va_tuong_duong_tien`  +0.183·`dau_tu_tc_ngan_han`  +0.076·`phai_thu_ngan_han`  +0.076·`hang_ton_kho`  +0.076·`tai_san_sinh_hoc_ngan_han`  -0.424·`tsnh_khac`  -0.061·`tai_san_dai_han`  +0.049·`tong_tai_san`  +0.025·`no_phai_tra`  +0.025·`von_chu_so_huu`  +0.049·`tong_nguon_von`  +0.738·`lctt_hdkd`  -0.262·`lctt_dau_tu`  -0.262·`lctt_tai_chinh`  +0.215·`lctt_thuan`  -0.046·`tien_dau_ky`  -0.046·`anh_huong_ty_gia`
14. +0.110·`tai_san_ngan_han`  +0.122·`tien_va_tuong_duong_tien`  +0.183·`dau_tu_tc_ngan_han`  +0.076·`phai_thu_ngan_han`  +0.076·`hang_ton_kho`  +0.076·`tai_san_sinh_hoc_ngan_han`  -0.424·`tsnh_khac`  -0.061·`tai_san_dai_han`  +0.049·`tong_tai_san`  +0.025·`no_phai_tra`  +0.025·`von_chu_so_huu`  +0.049·`tong_nguon_von`  -0.262·`lctt_hdkd`  +0.738·`lctt_dau_tu`  -0.262·`lctt_tai_chinh`  +0.215·`lctt_thuan`  -0.046·`tien_dau_ky`  -0.046·`anh_huong_ty_gia`
15. +0.110·`tai_san_ngan_han`  +0.122·`tien_va_tuong_duong_tien`  +0.183·`dau_tu_tc_ngan_han`  +0.076·`phai_thu_ngan_han`  +0.076·`hang_ton_kho`  +0.076·`tai_san_sinh_hoc_ngan_han`  -0.424·`tsnh_khac`  -0.061·`tai_san_dai_han`  +0.049·`tong_tai_san`  +0.025·`no_phai_tra`  +0.025·`von_chu_so_huu`  +0.049·`tong_nguon_von`  -0.262·`lctt_hdkd`  -0.262·`lctt_dau_tu`  +0.738·`lctt_tai_chinh`  +0.215·`lctt_thuan`  -0.046·`tien_dau_ky`  -0.046·`anh_huong_ty_gia`
16. +0.224·`tai_san_ngan_han`  +0.160·`tien_va_tuong_duong_tien`  -0.219·`dau_tu_tc_ngan_han`  -0.054·`phai_thu_ngan_han`  -0.054·`hang_ton_kho`  -0.054·`tai_san_sinh_hoc_ngan_han`  +0.446·`tsnh_khac`  -0.310·`tai_san_dai_han`  -0.086·`tong_tai_san`  -0.043·`no_phai_tra`  -0.043·`von_chu_so_huu`  -0.086·`tong_nguon_von`  +0.196·`lctt_hdkd`  +0.196·`lctt_dau_tu`  +0.196·`lctt_tai_chinh`  +0.589·`lctt_thuan`  -0.215·`tien_dau_ky`  -0.215·`anh_huong_ty_gia`
17. +0.333·`tai_san_ngan_han`  +0.283·`tien_va_tuong_duong_tien`  -0.036·`dau_tu_tc_ngan_han`  +0.022·`phai_thu_ngan_han`  +0.022·`hang_ton_kho`  +0.022·`tai_san_sinh_hoc_ngan_han`  +0.022·`tsnh_khac`  -0.370·`tai_san_dai_han`  -0.037·`tong_tai_san`  -0.018·`no_phai_tra`  -0.018·`von_chu_so_huu`  -0.037·`tong_nguon_von`  -0.065·`lctt_hdkd`  -0.065·`lctt_dau_tu`  -0.065·`lctt_tai_chinh`  -0.196·`lctt_thuan`  +0.739·`tien_dau_ky`  -0.261·`anh_huong_ty_gia`
18. +0.333·`tai_san_ngan_han`  +0.283·`tien_va_tuong_duong_tien`  -0.036·`dau_tu_tc_ngan_han`  +0.022·`phai_thu_ngan_han`  +0.022·`hang_ton_kho`  +0.022·`tai_san_sinh_hoc_ngan_han`  +0.022·`tsnh_khac`  -0.370·`tai_san_dai_han`  -0.037·`tong_tai_san`  -0.018·`no_phai_tra`  -0.018·`von_chu_so_huu`  -0.037·`tong_nguon_von`  -0.065·`lctt_hdkd`  -0.065·`lctt_dau_tu`  -0.065·`lctt_tai_chinh`  -0.196·`lctt_thuan`  -0.261·`tien_dau_ky`  +0.739·`anh_huong_ty_gia`
