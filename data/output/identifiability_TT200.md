# Identifiability — chuẩn TT200

> Sinh tự động bởi `src/constraints.py`. Đối chiếu bảng ma trận bên dưới
> với Phụ lục của Thông tư trước khi tin vào bất kỳ con số nào ở đây.

## Tổng quan

- Số chỉ tiêu (n): **26**
- Số đẳng thức dùng được: **9**
- Hạng `rank(A)`: **9**
- Chiều không gian null `dim null(A)`: **17**
- Số field định vị được lỗi một-trường: **7 / 26**
- Số field có **cột toàn 0** (lỗi không PHÁT HIỆN được): **0 / 26** — không có

Nghĩa là **17/26** chiều trong không gian lỗi hoàn toàn vô hình
với mọi phương pháp dựa trên ràng buộc — residual bằng 0 tuyệt đối.

## Ma trận ràng buộc A

Mỗi dòng một đẳng thức, `+1` cho thành phần, `-1` cho tổng, `.` cho 0.

| Đẳng thức | tai_san_ngan_han | tien_va_tuong_duong_tien | dau_tu_tc_ngan_han | phai_thu_ngan_han | hang_ton_kho | tsnh_khac | tai_san_dai_han | tong_tai_san | no_phai_tra | von_chu_so_huu | tong_nguon_von | doanh_thu_thuan | gia_von_hang_ban | loi_nhuan_gop | ln_thuan_hdkd | ln_khac | loi_nhuan_truoc_thue | thue_tndn_hien_hanh | thue_tndn_hoan_lai | loi_nhuan_sau_thue | lctt_hdkd | lctt_dau_tu | lctt_tai_chinh | lctt_thuan | tien_dau_ky | anh_huong_ty_gia |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tài sản ngắn hạn + Tài sản dài hạn phải bằng Tổng tài sản | +1 | . | . | . | . | . | +1 | -1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| Nợ phải trả + Vốn chủ sở hữu phải bằng Tổng cộng nguồn vốn (mã 440) | . | . | . | . | . | . | . | . | +1 | +1 | -1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| Tổng cộng nguồn vốn phải bằng Tổng cộng tài sản | . | . | . | . | . | . | . | -1 | . | . | +1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |
| Giá vốn hàng bán + Lợi nhuận gộp phải bằng Doanh thu thuần | . | . | . | . | . | . | . | . | . | . | . | -1 | +1 | +1 | . | . | . | . | . | . | . | . | . | . | . | . |
| Lợi nhuận thuần từ HĐKD + Lợi nhuận khác phải bằng Lợi nhuận trước thuế | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | -1 | . | . | . | . | . | . | . | . | . |
| Lợi nhuận sau thuế + chi phí thuế hiện hành + hoãn lại phải bằng Lợi nhuận trước thuế | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | -1 | +1 | +1 | +1 | . | . | . | . | . | . |
| B03: Mã số 50 = Mã số 20 + Mã số 30 + Mã số 40 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 | -1 | . | . |
| B03: Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61, và mã 70 ≡ mã 110 trên B01 — LIÊN KẾT CHÉO GIỮA HAI BIỂU MẪU | . | -1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 |
| Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn (TT200: mã 100 = 110+120+130+140+150) | -1 | +1 | +1 | +1 | +1 | +1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |

## Định vị lỗi một-trường

Định vị được khi cột của field khác 0 **và** không tỷ lệ với cột nào khác.

| Chỉ tiêu | Cột trong A | Định vị được | Ghi chú |
|---|---|---|---|
| `tai_san_ngan_han` | `+1 0 0 0 0 0 0 0 -1` | có | cột riêng biệt |
| `tien_va_tuong_duong_tien` | `0 0 0 0 0 0 0 -1 +1` | có | cột riêng biệt |
| `dau_tu_tc_ngan_han` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: hang_ton_kho, phai_thu_ngan_han, tsnh_khac |
| `phai_thu_ngan_han` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, tsnh_khac |
| `hang_ton_kho` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, phai_thu_ngan_han, tsnh_khac |
| `tsnh_khac` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, phai_thu_ngan_han |
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
- `dau_tu_tc_ngan_han` ↔ `tsnh_khac`
- `phai_thu_ngan_han` ↔ `hang_ton_kho`
- `phai_thu_ngan_han` ↔ `tsnh_khac`
- `hang_ton_kho` ↔ `tsnh_khac`
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

1. -0.092·`tai_san_ngan_han`  -0.218·`tien_va_tuong_duong_tien`  -0.235·`dau_tu_tc_ngan_han`  +0.120·`phai_thu_ngan_han`  +0.120·`hang_ton_kho`  +0.120·`tsnh_khac`  +0.107·`tai_san_dai_han`  +0.015·`tong_tai_san`  -0.631·`no_phai_tra`  +0.646·`von_chu_so_huu`  +0.015·`tong_nguon_von`  -0.020·`lctt_hdkd`  -0.020·`lctt_dau_tu`  -0.020·`lctt_tai_chinh`  -0.059·`lctt_thuan`  -0.079·`tien_dau_ky`  -0.079·`anh_huong_ty_gia`
2. +0.264·`tai_san_ngan_han`  +0.477·`tien_va_tuong_duong_tien`  -0.307·`dau_tu_tc_ngan_han`  +0.031·`phai_thu_ngan_han`  +0.031·`hang_ton_kho`  +0.031·`tsnh_khac`  +0.178·`tai_san_dai_han`  +0.442·`tong_tai_san`  +0.185·`no_phai_tra`  +0.257·`von_chu_so_huu`  +0.442·`tong_nguon_von`  +0.043·`lctt_hdkd`  +0.043·`lctt_dau_tu`  +0.043·`lctt_tai_chinh`  +0.130·`lctt_thuan`  +0.173·`tien_dau_ky`  +0.173·`anh_huong_ty_gia`
3. +0.040·`tai_san_ngan_han`  -0.134·`tien_va_tuong_duong_tien`  -0.168·`dau_tu_tc_ngan_han`  +0.499·`phai_thu_ngan_han`  -0.078·`hang_ton_kho`  -0.078·`tsnh_khac`  -0.018·`tai_san_dai_han`  +0.022·`tong_tai_san`  +0.101·`no_phai_tra`  -0.079·`von_chu_so_huu`  +0.022·`tong_nguon_von`  +0.667·`doanh_thu_thuan`  +0.333·`gia_von_hang_ban`  +0.333·`loi_nhuan_gop`  -0.012·`lctt_hdkd`  -0.012·`lctt_dau_tu`  -0.012·`lctt_tai_chinh`  -0.037·`lctt_thuan`  -0.049·`tien_dau_ky`  -0.049·`anh_huong_ty_gia`
4. -0.040·`tai_san_ngan_han`  +0.134·`tien_va_tuong_duong_tien`  +0.168·`dau_tu_tc_ngan_han`  -0.499·`phai_thu_ngan_han`  +0.078·`hang_ton_kho`  +0.078·`tsnh_khac`  +0.018·`tai_san_dai_han`  -0.022·`tong_tai_san`  -0.101·`no_phai_tra`  +0.079·`von_chu_so_huu`  -0.022·`tong_nguon_von`  +0.333·`doanh_thu_thuan`  +0.667·`gia_von_hang_ban`  -0.333·`loi_nhuan_gop`  +0.012·`lctt_hdkd`  +0.012·`lctt_dau_tu`  +0.012·`lctt_tai_chinh`  +0.037·`lctt_thuan`  +0.049·`tien_dau_ky`  +0.049·`anh_huong_ty_gia`
5. -0.040·`tai_san_ngan_han`  +0.134·`tien_va_tuong_duong_tien`  +0.168·`dau_tu_tc_ngan_han`  -0.499·`phai_thu_ngan_han`  +0.078·`hang_ton_kho`  +0.078·`tsnh_khac`  +0.018·`tai_san_dai_han`  -0.022·`tong_tai_san`  -0.101·`no_phai_tra`  +0.079·`von_chu_so_huu`  -0.022·`tong_nguon_von`  +0.333·`doanh_thu_thuan`  -0.333·`gia_von_hang_ban`  +0.667·`loi_nhuan_gop`  +0.012·`lctt_hdkd`  +0.012·`lctt_dau_tu`  +0.012·`lctt_tai_chinh`  +0.037·`lctt_thuan`  +0.049·`tien_dau_ky`  +0.049·`anh_huong_ty_gia`
6. -0.028·`tai_san_ngan_han`  +0.094·`tien_va_tuong_duong_tien`  +0.117·`dau_tu_tc_ngan_han`  +0.055·`phai_thu_ngan_han`  -0.523·`hang_ton_kho`  +0.229·`tsnh_khac`  +0.013·`tai_san_dai_han`  -0.015·`tong_tai_san`  -0.071·`no_phai_tra`  +0.056·`von_chu_so_huu`  -0.015·`tong_nguon_von`  +0.636·`ln_thuan_hdkd`  -0.364·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  +0.091·`thue_tndn_hien_hanh`  +0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`  +0.009·`lctt_hdkd`  +0.009·`lctt_dau_tu`  +0.009·`lctt_tai_chinh`  +0.026·`lctt_thuan`  +0.034·`tien_dau_ky`  +0.034·`anh_huong_ty_gia`
7. -0.028·`tai_san_ngan_han`  +0.094·`tien_va_tuong_duong_tien`  +0.117·`dau_tu_tc_ngan_han`  +0.055·`phai_thu_ngan_han`  -0.523·`hang_ton_kho`  +0.229·`tsnh_khac`  +0.013·`tai_san_dai_han`  -0.015·`tong_tai_san`  -0.071·`no_phai_tra`  +0.056·`von_chu_so_huu`  -0.015·`tong_nguon_von`  -0.364·`ln_thuan_hdkd`  +0.636·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  +0.091·`thue_tndn_hien_hanh`  +0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`  +0.009·`lctt_hdkd`  +0.009·`lctt_dau_tu`  +0.009·`lctt_tai_chinh`  +0.026·`lctt_thuan`  +0.034·`tien_dau_ky`  +0.034·`anh_huong_ty_gia`
8. +0.065·`tai_san_ngan_han`  -0.215·`tien_va_tuong_duong_tien`  -0.269·`dau_tu_tc_ngan_han`  -0.126·`phai_thu_ngan_han`  +0.452·`hang_ton_kho`  +0.222·`tsnh_khac`  -0.029·`tai_san_dai_han`  +0.035·`tong_tai_san`  +0.163·`no_phai_tra`  -0.127·`von_chu_so_huu`  +0.035·`tong_nguon_von`  +0.273·`ln_thuan_hdkd`  +0.273·`ln_khac`  +0.545·`loi_nhuan_truoc_thue`  +0.182·`thue_tndn_hien_hanh`  +0.182·`thue_tndn_hoan_lai`  +0.182·`loi_nhuan_sau_thue`  -0.020·`lctt_hdkd`  -0.020·`lctt_dau_tu`  -0.020·`lctt_tai_chinh`  -0.059·`lctt_thuan`  -0.078·`tien_dau_ky`  -0.078·`anh_huong_ty_gia`
9. -0.036·`tai_san_ngan_han`  +0.121·`tien_va_tuong_duong_tien`  +0.152·`dau_tu_tc_ngan_han`  +0.071·`phai_thu_ngan_han`  +0.071·`hang_ton_kho`  -0.451·`tsnh_khac`  +0.017·`tai_san_dai_han`  -0.020·`tong_tai_san`  -0.092·`no_phai_tra`  +0.072·`von_chu_so_huu`  -0.020·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  +0.727·`thue_tndn_hien_hanh`  -0.273·`thue_tndn_hoan_lai`  -0.273·`loi_nhuan_sau_thue`  +0.011·`lctt_hdkd`  +0.011·`lctt_dau_tu`  +0.011·`lctt_tai_chinh`  +0.033·`lctt_thuan`  +0.044·`tien_dau_ky`  +0.044·`anh_huong_ty_gia`
10. -0.036·`tai_san_ngan_han`  +0.121·`tien_va_tuong_duong_tien`  +0.152·`dau_tu_tc_ngan_han`  +0.071·`phai_thu_ngan_han`  +0.071·`hang_ton_kho`  -0.451·`tsnh_khac`  +0.017·`tai_san_dai_han`  -0.020·`tong_tai_san`  -0.092·`no_phai_tra`  +0.072·`von_chu_so_huu`  -0.020·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  -0.273·`thue_tndn_hien_hanh`  +0.727·`thue_tndn_hoan_lai`  -0.273·`loi_nhuan_sau_thue`  +0.011·`lctt_hdkd`  +0.011·`lctt_dau_tu`  +0.011·`lctt_tai_chinh`  +0.033·`lctt_thuan`  +0.044·`tien_dau_ky`  +0.044·`anh_huong_ty_gia`
11. -0.036·`tai_san_ngan_han`  +0.121·`tien_va_tuong_duong_tien`  +0.152·`dau_tu_tc_ngan_han`  +0.071·`phai_thu_ngan_han`  +0.071·`hang_ton_kho`  -0.451·`tsnh_khac`  +0.017·`tai_san_dai_han`  -0.020·`tong_tai_san`  -0.092·`no_phai_tra`  +0.072·`von_chu_so_huu`  -0.020·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  -0.273·`thue_tndn_hien_hanh`  -0.273·`thue_tndn_hoan_lai`  +0.727·`loi_nhuan_sau_thue`  +0.011·`lctt_hdkd`  +0.011·`lctt_dau_tu`  +0.011·`lctt_tai_chinh`  +0.033·`lctt_thuan`  +0.044·`tien_dau_ky`  +0.044·`anh_huong_ty_gia`
12. +0.240·`tai_san_ngan_han`  +0.155·`tien_va_tuong_duong_tien`  -0.070·`dau_tu_tc_ngan_han`  +0.052·`phai_thu_ngan_han`  +0.052·`hang_ton_kho`  +0.052·`tsnh_khac`  -0.358·`tai_san_dai_han`  -0.118·`tong_tai_san`  -0.118·`no_phai_tra`  +0.000·`von_chu_so_huu`  -0.118·`tong_nguon_von`  +0.741·`lctt_hdkd`  -0.259·`lctt_dau_tu`  -0.259·`lctt_tai_chinh`  +0.224·`lctt_thuan`  -0.035·`tien_dau_ky`  -0.035·`anh_huong_ty_gia`
13. +0.240·`tai_san_ngan_han`  +0.155·`tien_va_tuong_duong_tien`  -0.070·`dau_tu_tc_ngan_han`  +0.052·`phai_thu_ngan_han`  +0.052·`hang_ton_kho`  +0.052·`tsnh_khac`  -0.358·`tai_san_dai_han`  -0.118·`tong_tai_san`  -0.118·`no_phai_tra`  +0.000·`von_chu_so_huu`  -0.118·`tong_nguon_von`  -0.259·`lctt_hdkd`  +0.741·`lctt_dau_tu`  -0.259·`lctt_tai_chinh`  +0.224·`lctt_thuan`  -0.035·`tien_dau_ky`  -0.035·`anh_huong_ty_gia`
14. +0.240·`tai_san_ngan_han`  +0.155·`tien_va_tuong_duong_tien`  -0.070·`dau_tu_tc_ngan_han`  +0.052·`phai_thu_ngan_han`  +0.052·`hang_ton_kho`  +0.052·`tsnh_khac`  -0.358·`tai_san_dai_han`  -0.118·`tong_tai_san`  -0.118·`no_phai_tra`  +0.000·`von_chu_so_huu`  -0.118·`tong_nguon_von`  -0.259·`lctt_hdkd`  -0.259·`lctt_dau_tu`  +0.741·`lctt_tai_chinh`  +0.224·`lctt_thuan`  -0.035·`tien_dau_ky`  -0.035·`anh_huong_ty_gia`
15. -0.428·`tai_san_ngan_han`  +0.086·`tien_va_tuong_duong_tien`  -0.315·`dau_tu_tc_ngan_han`  -0.066·`phai_thu_ngan_han`  -0.066·`hang_ton_kho`  -0.066·`tsnh_khac`  +0.347·`tai_san_dai_han`  -0.081·`tong_tai_san`  +0.036·`no_phai_tra`  -0.117·`von_chu_so_huu`  -0.081·`tong_nguon_von`  +0.190·`lctt_hdkd`  +0.190·`lctt_dau_tu`  +0.190·`lctt_tai_chinh`  +0.569·`lctt_thuan`  -0.241·`tien_dau_ky`  -0.241·`anh_huong_ty_gia`
16. -0.189·`tai_san_ngan_han`  +0.241·`tien_va_tuong_duong_tien`  -0.385·`dau_tu_tc_ngan_han`  -0.015·`phai_thu_ngan_han`  -0.015·`hang_ton_kho`  -0.015·`tsnh_khac`  -0.011·`tai_san_dai_han`  -0.199·`tong_tai_san`  -0.082·`no_phai_tra`  -0.117·`von_chu_so_huu`  -0.199·`tong_nguon_von`  -0.069·`lctt_hdkd`  -0.069·`lctt_dau_tu`  -0.069·`lctt_tai_chinh`  -0.207·`lctt_thuan`  +0.724·`tien_dau_ky`  -0.276·`anh_huong_ty_gia`
17. -0.189·`tai_san_ngan_han`  +0.241·`tien_va_tuong_duong_tien`  -0.385·`dau_tu_tc_ngan_han`  -0.015·`phai_thu_ngan_han`  -0.015·`hang_ton_kho`  -0.015·`tsnh_khac`  -0.011·`tai_san_dai_han`  -0.199·`tong_tai_san`  -0.082·`no_phai_tra`  -0.117·`von_chu_so_huu`  -0.199·`tong_nguon_von`  -0.069·`lctt_hdkd`  -0.069·`lctt_dau_tu`  -0.069·`lctt_tai_chinh`  -0.207·`lctt_thuan`  -0.276·`tien_dau_ky`  +0.724·`anh_huong_ty_gia`
