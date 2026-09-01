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
| Lợi nhuận thuần từ HĐKD + Lợi nhuận khác phải bằng Lợi nhuận trước thuế | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | -1 | . | . | . | . | . | . | . | . | . |
| B03: Mã số 50 = Mã số 20 + Mã số 30 + Mã số 40 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 | -1 | . | . |
| B03: Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61, và mã 70 ≡ mã 110 trên B01 — LIÊN KẾT CHÉO GIỮA HAI BIỂU MẪU | . | -1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 |
| B02 dạng tổng: Mã 20 = Mã 10 + Mã 11 | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | -1 | . | . | . | . | . | . | . | . | . | . | . | . |
| B02 dạng tổng: Mã 60 = Mã 50 + Mã 51 + Mã 52 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 | -1 | . | . | . | . | . | . |
| Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn (TT99: mã 100 = 110+120+130+140+150+160) | -1 | +1 | +1 | +1 | +1 | +1 | +1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |

## Định vị lỗi một-trường

Định vị được khi cột của field khác 0 **và** không tỷ lệ với cột nào khác.

| Chỉ tiêu | Cột trong A | Định vị được | Ghi chú |
|---|---|---|---|
| `tai_san_ngan_han` | `+1 0 0 0 0 0 0 0 -1` | có | cột riêng biệt |
| `tien_va_tuong_duong_tien` | `0 0 0 0 0 -1 0 0 +1` | có | cột riêng biệt |
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
| `doanh_thu_thuan` | `0 0 0 0 0 0 +1 0 0` | KHÔNG | cột tỷ lệ với: gia_von_hang_ban, loi_nhuan_gop |
| `gia_von_hang_ban` | `0 0 0 0 0 0 +1 0 0` | KHÔNG | cột tỷ lệ với: doanh_thu_thuan, loi_nhuan_gop |
| `loi_nhuan_gop` | `0 0 0 0 0 0 -1 0 0` | KHÔNG | cột tỷ lệ với: doanh_thu_thuan, gia_von_hang_ban |
| `ln_thuan_hdkd` | `0 0 0 +1 0 0 0 0 0` | KHÔNG | cột tỷ lệ với: ln_khac |
| `ln_khac` | `0 0 0 +1 0 0 0 0 0` | KHÔNG | cột tỷ lệ với: ln_thuan_hdkd |
| `loi_nhuan_truoc_thue` | `0 0 0 -1 0 0 0 +1 0` | có | cột riêng biệt |
| `thue_tndn_hien_hanh` | `0 0 0 0 0 0 0 +1 0` | KHÔNG | cột tỷ lệ với: loi_nhuan_sau_thue, thue_tndn_hoan_lai |
| `thue_tndn_hoan_lai` | `0 0 0 0 0 0 0 +1 0` | KHÔNG | cột tỷ lệ với: loi_nhuan_sau_thue, thue_tndn_hien_hanh |
| `loi_nhuan_sau_thue` | `0 0 0 0 0 0 0 -1 0` | KHÔNG | cột tỷ lệ với: thue_tndn_hien_hanh, thue_tndn_hoan_lai |
| `lctt_hdkd` | `0 0 0 0 +1 0 0 0 0` | KHÔNG | cột tỷ lệ với: lctt_dau_tu, lctt_tai_chinh |
| `lctt_dau_tu` | `0 0 0 0 +1 0 0 0 0` | KHÔNG | cột tỷ lệ với: lctt_hdkd, lctt_tai_chinh |
| `lctt_tai_chinh` | `0 0 0 0 +1 0 0 0 0` | KHÔNG | cột tỷ lệ với: lctt_dau_tu, lctt_hdkd |
| `lctt_thuan` | `0 0 0 0 -1 +1 0 0 0` | có | cột riêng biệt |
| `tien_dau_ky` | `0 0 0 0 0 +1 0 0 0` | KHÔNG | cột tỷ lệ với: anh_huong_ty_gia |
| `anh_huong_ty_gia` | `0 0 0 0 0 +1 0 0 0` | KHÔNG | cột tỷ lệ với: tien_dau_ky |

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

1. +0.141·`tai_san_ngan_han`  -0.310·`tien_va_tuong_duong_tien`  +0.131·`dau_tu_tc_ngan_han`  +0.155·`phai_thu_ngan_han`  +0.155·`hang_ton_kho`  -0.144·`tai_san_sinh_hoc_ngan_han`  +0.155·`tsnh_khac`  +0.153·`tai_san_dai_han`  +0.294·`tong_tai_san`  +0.647·`no_phai_tra`  -0.353·`von_chu_so_huu`  +0.294·`tong_nguon_von`  -0.028·`lctt_hdkd`  -0.028·`lctt_dau_tu`  -0.028·`lctt_tai_chinh`  -0.085·`lctt_thuan`  -0.113·`tien_dau_ky`  -0.113·`anh_huong_ty_gia`
2. +0.141·`tai_san_ngan_han`  -0.310·`tien_va_tuong_duong_tien`  +0.131·`dau_tu_tc_ngan_han`  +0.155·`phai_thu_ngan_han`  +0.155·`hang_ton_kho`  -0.144·`tai_san_sinh_hoc_ngan_han`  +0.155·`tsnh_khac`  +0.153·`tai_san_dai_han`  +0.294·`tong_tai_san`  -0.353·`no_phai_tra`  +0.647·`von_chu_so_huu`  +0.294·`tong_nguon_von`  -0.028·`lctt_hdkd`  -0.028·`lctt_dau_tu`  -0.028·`lctt_tai_chinh`  -0.085·`lctt_thuan`  -0.113·`tien_dau_ky`  -0.113·`anh_huong_ty_gia`
3. +0.168·`tai_san_ngan_han`  +0.426·`tien_va_tuong_duong_tien`  -0.569·`dau_tu_tc_ngan_han`  +0.003·`phai_thu_ngan_han`  +0.003·`hang_ton_kho`  +0.301·`tai_san_sinh_hoc_ngan_han`  +0.003·`tsnh_khac`  +0.168·`tai_san_dai_han`  +0.336·`tong_tai_san`  +0.168·`no_phai_tra`  +0.168·`von_chu_so_huu`  +0.336·`tong_nguon_von`  +0.039·`lctt_hdkd`  +0.039·`lctt_dau_tu`  +0.039·`lctt_tai_chinh`  +0.116·`lctt_thuan`  +0.155·`tien_dau_ky`  +0.155·`anh_huong_ty_gia`
4. +0.030·`tai_san_ngan_han`  +0.060·`tien_va_tuong_duong_tien`  +0.222·`dau_tu_tc_ngan_han`  +0.082·`phai_thu_ngan_han`  +0.082·`hang_ton_kho`  +0.082·`tai_san_sinh_hoc_ngan_han`  -0.496·`tsnh_khac`  +0.037·`tai_san_dai_han`  +0.067·`tong_tai_san`  +0.034·`no_phai_tra`  +0.034·`von_chu_so_huu`  +0.067·`tong_nguon_von`  +0.667·`doanh_thu_thuan`  -0.333·`gia_von_hang_ban`  +0.333·`loi_nhuan_gop`  +0.005·`lctt_hdkd`  +0.005·`lctt_dau_tu`  +0.005·`lctt_tai_chinh`  +0.016·`lctt_thuan`  +0.022·`tien_dau_ky`  +0.022·`anh_huong_ty_gia`
5. +0.030·`tai_san_ngan_han`  +0.060·`tien_va_tuong_duong_tien`  +0.222·`dau_tu_tc_ngan_han`  +0.082·`phai_thu_ngan_han`  +0.082·`hang_ton_kho`  +0.082·`tai_san_sinh_hoc_ngan_han`  -0.496·`tsnh_khac`  +0.037·`tai_san_dai_han`  +0.067·`tong_tai_san`  +0.034·`no_phai_tra`  +0.034·`von_chu_so_huu`  +0.067·`tong_nguon_von`  -0.333·`doanh_thu_thuan`  +0.667·`gia_von_hang_ban`  +0.333·`loi_nhuan_gop`  +0.005·`lctt_hdkd`  +0.005·`lctt_dau_tu`  +0.005·`lctt_tai_chinh`  +0.016·`lctt_thuan`  +0.022·`tien_dau_ky`  +0.022·`anh_huong_ty_gia`
6. -0.030·`tai_san_ngan_han`  -0.060·`tien_va_tuong_duong_tien`  -0.222·`dau_tu_tc_ngan_han`  -0.082·`phai_thu_ngan_han`  -0.082·`hang_ton_kho`  -0.082·`tai_san_sinh_hoc_ngan_han`  +0.496·`tsnh_khac`  -0.037·`tai_san_dai_han`  -0.067·`tong_tai_san`  -0.034·`no_phai_tra`  -0.034·`von_chu_so_huu`  -0.067·`tong_nguon_von`  +0.333·`doanh_thu_thuan`  +0.333·`gia_von_hang_ban`  +0.667·`loi_nhuan_gop`  -0.005·`lctt_hdkd`  -0.005·`lctt_dau_tu`  -0.005·`lctt_tai_chinh`  -0.016·`lctt_thuan`  -0.022·`tien_dau_ky`  -0.022·`anh_huong_ty_gia`
7. +0.148·`tai_san_ngan_han`  +0.074·`tien_va_tuong_duong_tien`  +0.244·`dau_tu_tc_ngan_han`  -0.476·`phai_thu_ngan_han`  +0.102·`hang_ton_kho`  +0.102·`tai_san_sinh_hoc_ngan_han`  +0.102·`tsnh_khac`  -0.082·`tai_san_dai_han`  +0.065·`tong_tai_san`  +0.033·`no_phai_tra`  +0.033·`von_chu_so_huu`  +0.065·`tong_nguon_von`  +0.636·`ln_thuan_hdkd`  -0.364·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  -0.091·`thue_tndn_hien_hanh`  -0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`  +0.007·`lctt_hdkd`  +0.007·`lctt_dau_tu`  +0.007·`lctt_tai_chinh`  +0.020·`lctt_thuan`  +0.027·`tien_dau_ky`  +0.027·`anh_huong_ty_gia`
8. +0.148·`tai_san_ngan_han`  +0.074·`tien_va_tuong_duong_tien`  +0.244·`dau_tu_tc_ngan_han`  -0.476·`phai_thu_ngan_han`  +0.102·`hang_ton_kho`  +0.102·`tai_san_sinh_hoc_ngan_han`  +0.102·`tsnh_khac`  -0.082·`tai_san_dai_han`  +0.065·`tong_tai_san`  +0.033·`no_phai_tra`  +0.033·`von_chu_so_huu`  +0.065·`tong_nguon_von`  -0.364·`ln_thuan_hdkd`  +0.636·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  -0.091·`thue_tndn_hien_hanh`  -0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`  +0.007·`lctt_hdkd`  +0.007·`lctt_dau_tu`  +0.007·`lctt_tai_chinh`  +0.020·`lctt_thuan`  +0.027·`tien_dau_ky`  +0.027·`anh_huong_ty_gia`
9. +0.204·`tai_san_ngan_han`  -0.030·`tien_va_tuong_duong_tien`  -0.177·`dau_tu_tc_ngan_han`  +0.536·`phai_thu_ngan_han`  -0.042·`hang_ton_kho`  -0.042·`tai_san_sinh_hoc_ngan_han`  -0.042·`tsnh_khac`  -0.275·`tai_san_dai_han`  -0.071·`tong_tai_san`  -0.036·`no_phai_tra`  -0.036·`von_chu_so_huu`  -0.071·`tong_nguon_von`  +0.273·`ln_thuan_hdkd`  +0.273·`ln_khac`  +0.545·`loi_nhuan_truoc_thue`  -0.182·`thue_tndn_hien_hanh`  -0.182·`thue_tndn_hoan_lai`  +0.182·`loi_nhuan_sau_thue`  -0.003·`lctt_hdkd`  -0.003·`lctt_dau_tu`  -0.003·`lctt_tai_chinh`  -0.008·`lctt_thuan`  -0.011·`tien_dau_ky`  -0.011·`anh_huong_ty_gia`
10. +0.351·`tai_san_ngan_han`  +0.044·`tien_va_tuong_duong_tien`  +0.067·`dau_tu_tc_ngan_han`  +0.060·`phai_thu_ngan_han`  +0.060·`hang_ton_kho`  +0.060·`tai_san_sinh_hoc_ngan_han`  +0.060·`tsnh_khac`  -0.357·`tai_san_dai_han`  -0.006·`tong_tai_san`  -0.003·`no_phai_tra`  -0.003·`von_chu_so_huu`  -0.006·`tong_nguon_von`  -0.091·`ln_thuan_hdkd`  -0.091·`ln_khac`  -0.182·`loi_nhuan_truoc_thue`  +0.727·`thue_tndn_hien_hanh`  -0.273·`thue_tndn_hoan_lai`  +0.273·`loi_nhuan_sau_thue`  +0.004·`lctt_hdkd`  +0.004·`lctt_dau_tu`  +0.004·`lctt_tai_chinh`  +0.012·`lctt_thuan`  +0.016·`tien_dau_ky`  +0.016·`anh_huong_ty_gia`
11. +0.351·`tai_san_ngan_han`  +0.044·`tien_va_tuong_duong_tien`  +0.067·`dau_tu_tc_ngan_han`  +0.060·`phai_thu_ngan_han`  +0.060·`hang_ton_kho`  +0.060·`tai_san_sinh_hoc_ngan_han`  +0.060·`tsnh_khac`  -0.357·`tai_san_dai_han`  -0.006·`tong_tai_san`  -0.003·`no_phai_tra`  -0.003·`von_chu_so_huu`  -0.006·`tong_nguon_von`  -0.091·`ln_thuan_hdkd`  -0.091·`ln_khac`  -0.182·`loi_nhuan_truoc_thue`  -0.273·`thue_tndn_hien_hanh`  +0.727·`thue_tndn_hoan_lai`  +0.273·`loi_nhuan_sau_thue`  +0.004·`lctt_hdkd`  +0.004·`lctt_dau_tu`  +0.004·`lctt_tai_chinh`  +0.012·`lctt_thuan`  +0.016·`tien_dau_ky`  +0.016·`anh_huong_ty_gia`
12. -0.351·`tai_san_ngan_han`  -0.044·`tien_va_tuong_duong_tien`  -0.067·`dau_tu_tc_ngan_han`  -0.060·`phai_thu_ngan_han`  -0.060·`hang_ton_kho`  -0.060·`tai_san_sinh_hoc_ngan_han`  -0.060·`tsnh_khac`  +0.357·`tai_san_dai_han`  +0.006·`tong_tai_san`  +0.003·`no_phai_tra`  +0.003·`von_chu_so_huu`  +0.006·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  +0.273·`thue_tndn_hien_hanh`  +0.273·`thue_tndn_hoan_lai`  +0.727·`loi_nhuan_sau_thue`  -0.004·`lctt_hdkd`  -0.004·`lctt_dau_tu`  -0.004·`lctt_tai_chinh`  -0.012·`lctt_thuan`  -0.016·`tien_dau_ky`  -0.016·`anh_huong_ty_gia`
13. +0.030·`tai_san_ngan_han`  +0.125·`tien_va_tuong_duong_tien`  +0.216·`dau_tu_tc_ngan_han`  +0.079·`phai_thu_ngan_han`  -0.421·`hang_ton_kho`  -0.050·`tai_san_sinh_hoc_ngan_han`  +0.079·`tsnh_khac`  +0.036·`tai_san_dai_han`  +0.066·`tong_tai_san`  +0.033·`no_phai_tra`  +0.033·`von_chu_so_huu`  +0.066·`tong_nguon_von`  +0.739·`lctt_hdkd`  -0.261·`lctt_dau_tu`  -0.261·`lctt_tai_chinh`  +0.216·`lctt_thuan`  -0.045·`tien_dau_ky`  -0.045·`anh_huong_ty_gia`
14. +0.030·`tai_san_ngan_han`  +0.125·`tien_va_tuong_duong_tien`  +0.216·`dau_tu_tc_ngan_han`  +0.079·`phai_thu_ngan_han`  -0.421·`hang_ton_kho`  -0.050·`tai_san_sinh_hoc_ngan_han`  +0.079·`tsnh_khac`  +0.036·`tai_san_dai_han`  +0.066·`tong_tai_san`  +0.033·`no_phai_tra`  +0.033·`von_chu_so_huu`  +0.066·`tong_nguon_von`  -0.261·`lctt_hdkd`  +0.739·`lctt_dau_tu`  -0.261·`lctt_tai_chinh`  +0.216·`lctt_thuan`  -0.045·`tien_dau_ky`  -0.045·`anh_huong_ty_gia`
15. +0.030·`tai_san_ngan_han`  +0.125·`tien_va_tuong_duong_tien`  +0.216·`dau_tu_tc_ngan_han`  +0.079·`phai_thu_ngan_han`  -0.421·`hang_ton_kho`  -0.050·`tai_san_sinh_hoc_ngan_han`  +0.079·`tsnh_khac`  +0.036·`tai_san_dai_han`  +0.066·`tong_tai_san`  +0.033·`no_phai_tra`  +0.033·`von_chu_so_huu`  +0.066·`tong_nguon_von`  -0.261·`lctt_hdkd`  -0.261·`lctt_dau_tu`  +0.739·`lctt_tai_chinh`  +0.216·`lctt_thuan`  -0.045·`tien_dau_ky`  -0.045·`anh_huong_ty_gia`
16. -0.016·`tai_san_ngan_han`  +0.168·`tien_va_tuong_duong_tien`  -0.120·`dau_tu_tc_ngan_han`  -0.044·`phai_thu_ngan_han`  +0.456·`hang_ton_kho`  -0.431·`tai_san_sinh_hoc_ngan_han`  -0.044·`tsnh_khac`  -0.020·`tai_san_dai_han`  -0.036·`tong_tai_san`  -0.018·`no_phai_tra`  -0.018·`von_chu_so_huu`  -0.036·`tong_nguon_von`  +0.197·`lctt_hdkd`  +0.197·`lctt_dau_tu`  +0.197·`lctt_tai_chinh`  +0.591·`lctt_thuan`  -0.212·`tien_dau_ky`  -0.212·`anh_huong_ty_gia`
17. +0.013·`tai_san_ngan_han`  +0.293·`tien_va_tuong_duong_tien`  +0.096·`dau_tu_tc_ngan_han`  +0.035·`phai_thu_ngan_han`  +0.035·`hang_ton_kho`  -0.481·`tai_san_sinh_hoc_ngan_han`  +0.035·`tsnh_khac`  +0.016·`tai_san_dai_han`  +0.029·`tong_tai_san`  +0.015·`no_phai_tra`  +0.015·`von_chu_so_huu`  +0.029·`tong_nguon_von`  -0.064·`lctt_hdkd`  -0.064·`lctt_dau_tu`  -0.064·`lctt_tai_chinh`  -0.193·`lctt_thuan`  +0.743·`tien_dau_ky`  -0.257·`anh_huong_ty_gia`
18. +0.013·`tai_san_ngan_han`  +0.293·`tien_va_tuong_duong_tien`  +0.096·`dau_tu_tc_ngan_han`  +0.035·`phai_thu_ngan_han`  +0.035·`hang_ton_kho`  -0.481·`tai_san_sinh_hoc_ngan_han`  +0.035·`tsnh_khac`  +0.016·`tai_san_dai_han`  +0.029·`tong_tai_san`  +0.015·`no_phai_tra`  +0.015·`von_chu_so_huu`  +0.029·`tong_nguon_von`  -0.064·`lctt_hdkd`  -0.064·`lctt_dau_tu`  -0.064·`lctt_tai_chinh`  -0.193·`lctt_thuan`  -0.257·`tien_dau_ky`  +0.743·`anh_huong_ty_gia`

## Bất biến với quy ước dấu

Ma trận trên dựng ở quy ước `tong`. Dựng lại ở quy ước `tru` cho ra **cùng** hạng, cùng số chiều không gian null, cùng danh sách chỉ tiêu
định vị được và cùng danh sách cặp không phân biệt được — so từng phần tử chứ
không chỉ so số đếm.

Lý do: đổi quy ước chỉ lật dấu vài cột của `A`, mà hạng, không gian null và
quan hệ tỷ lệ giữa các cột đều bất biến với phép lật ấy. Câu này được KIỂM LẠI
mỗi lần sinh báo cáo, không chép từ trí nhớ.
