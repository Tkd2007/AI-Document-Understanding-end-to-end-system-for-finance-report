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
| B03: Mã số 50 = Mã số 20 + Mã số 30 + Mã số 40 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 | -1 | . | . |
| B03: Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61, và mã 70 ≡ mã 110 trên B01 — LIÊN KẾT CHÉO GIỮA HAI BIỂU MẪU | . | -1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 |
| Lợi nhuận trước thuế + thuế hiện hành + thuế hoãn lại (đều có dấu) phải bằng Lợi nhuận sau thuế | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 | -1 | . | . | . | . | . | . |
| Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn (TT200: mã 100 = 110+120+130+140+150) | -1 | +1 | +1 | +1 | +1 | +1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |

## Định vị lỗi một-trường

Định vị được khi cột của field khác 0 **và** không tỷ lệ với cột nào khác.

| Chỉ tiêu | Cột trong A | Định vị được | Ghi chú |
|---|---|---|---|
| `tai_san_ngan_han` | `+1 0 0 0 0 0 0 0 -1` | có | cột riêng biệt |
| `tien_va_tuong_duong_tien` | `0 0 0 0 0 0 -1 0 +1` | có | cột riêng biệt |
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
| `loi_nhuan_truoc_thue` | `0 0 0 0 -1 0 0 +1 0` | có | cột riêng biệt |
| `thue_tndn_hien_hanh` | `0 0 0 0 0 0 0 +1 0` | KHÔNG | cột tỷ lệ với: loi_nhuan_sau_thue, thue_tndn_hoan_lai |
| `thue_tndn_hoan_lai` | `0 0 0 0 0 0 0 +1 0` | KHÔNG | cột tỷ lệ với: loi_nhuan_sau_thue, thue_tndn_hien_hanh |
| `loi_nhuan_sau_thue` | `0 0 0 0 0 0 0 -1 0` | KHÔNG | cột tỷ lệ với: thue_tndn_hien_hanh, thue_tndn_hoan_lai |
| `lctt_hdkd` | `0 0 0 0 0 +1 0 0 0` | KHÔNG | cột tỷ lệ với: lctt_dau_tu, lctt_tai_chinh |
| `lctt_dau_tu` | `0 0 0 0 0 +1 0 0 0` | KHÔNG | cột tỷ lệ với: lctt_hdkd, lctt_tai_chinh |
| `lctt_tai_chinh` | `0 0 0 0 0 +1 0 0 0` | KHÔNG | cột tỷ lệ với: lctt_dau_tu, lctt_hdkd |
| `lctt_thuan` | `0 0 0 0 0 -1 +1 0 0` | có | cột riêng biệt |
| `tien_dau_ky` | `0 0 0 0 0 0 +1 0 0` | KHÔNG | cột tỷ lệ với: anh_huong_ty_gia |
| `anh_huong_ty_gia` | `0 0 0 0 0 0 +1 0 0` | KHÔNG | cột tỷ lệ với: tien_dau_ky |

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

1. +0.109·`tai_san_ngan_han`  -0.193·`tien_va_tuong_duong_tien`  -0.102·`dau_tu_tc_ngan_han`  +0.135·`phai_thu_ngan_han`  +0.135·`hang_ton_kho`  +0.135·`tsnh_khac`  -0.038·`tai_san_dai_han`  +0.071·`tong_tai_san`  -0.620·`no_phai_tra`  +0.691·`von_chu_so_huu`  +0.071·`tong_nguon_von`  -0.018·`lctt_hdkd`  -0.018·`lctt_dau_tu`  -0.018·`lctt_tai_chinh`  -0.053·`lctt_thuan`  -0.070·`tien_dau_ky`  -0.070·`anh_huong_ty_gia`
2. -0.033·`tai_san_ngan_han`  +0.441·`tien_va_tuong_duong_tien`  -0.505·`dau_tu_tc_ngan_han`  +0.010·`phai_thu_ngan_han`  +0.010·`hang_ton_kho`  +0.010·`tsnh_khac`  +0.393·`tai_san_dai_han`  +0.360·`tong_tai_san`  +0.168·`no_phai_tra`  +0.192·`von_chu_so_huu`  +0.360·`tong_nguon_von`  +0.040·`lctt_hdkd`  +0.040·`lctt_dau_tu`  +0.040·`lctt_tai_chinh`  +0.120·`lctt_thuan`  +0.160·`tien_dau_ky`  +0.160·`anh_huong_ty_gia`
3. +0.091·`tai_san_ngan_han`  -0.128·`tien_va_tuong_duong_tien`  -0.134·`dau_tu_tc_ngan_han`  +0.502·`phai_thu_ngan_han`  -0.075·`hang_ton_kho`  -0.075·`tsnh_khac`  -0.055·`tai_san_dai_han`  +0.036·`tong_tai_san`  +0.104·`no_phai_tra`  -0.068·`von_chu_so_huu`  +0.036·`tong_nguon_von`  +0.667·`doanh_thu_thuan`  +0.333·`gia_von_hang_ban`  +0.333·`loi_nhuan_gop`  -0.012·`lctt_hdkd`  -0.012·`lctt_dau_tu`  -0.012·`lctt_tai_chinh`  -0.035·`lctt_thuan`  -0.047·`tien_dau_ky`  -0.047·`anh_huong_ty_gia`
4. -0.091·`tai_san_ngan_han`  +0.128·`tien_va_tuong_duong_tien`  +0.134·`dau_tu_tc_ngan_han`  -0.502·`phai_thu_ngan_han`  +0.075·`hang_ton_kho`  +0.075·`tsnh_khac`  +0.055·`tai_san_dai_han`  -0.036·`tong_tai_san`  -0.104·`no_phai_tra`  +0.068·`von_chu_so_huu`  -0.036·`tong_nguon_von`  +0.333·`doanh_thu_thuan`  +0.667·`gia_von_hang_ban`  -0.333·`loi_nhuan_gop`  +0.012·`lctt_hdkd`  +0.012·`lctt_dau_tu`  +0.012·`lctt_tai_chinh`  +0.035·`lctt_thuan`  +0.047·`tien_dau_ky`  +0.047·`anh_huong_ty_gia`
5. -0.091·`tai_san_ngan_han`  +0.128·`tien_va_tuong_duong_tien`  +0.134·`dau_tu_tc_ngan_han`  -0.502·`phai_thu_ngan_han`  +0.075·`hang_ton_kho`  +0.075·`tsnh_khac`  +0.055·`tai_san_dai_han`  -0.036·`tong_tai_san`  -0.104·`no_phai_tra`  +0.068·`von_chu_so_huu`  -0.036·`tong_nguon_von`  +0.333·`doanh_thu_thuan`  -0.333·`gia_von_hang_ban`  +0.667·`loi_nhuan_gop`  +0.012·`lctt_hdkd`  +0.012·`lctt_dau_tu`  +0.012·`lctt_tai_chinh`  +0.035·`lctt_thuan`  +0.047·`tien_dau_ky`  +0.047·`anh_huong_ty_gia`
6. -0.165·`tai_san_ngan_han`  +0.140·`tien_va_tuong_duong_tien`  +0.028·`dau_tu_tc_ngan_han`  +0.082·`phai_thu_ngan_han`  -0.496·`hang_ton_kho`  +0.082·`tsnh_khac`  +0.057·`tai_san_dai_han`  -0.108·`tong_tai_san`  -0.148·`no_phai_tra`  +0.040·`von_chu_so_huu`  -0.108·`tong_nguon_von`  +0.636·`ln_thuan_hdkd`  -0.364·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  -0.091·`thue_tndn_hien_hanh`  -0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`  +0.013·`lctt_hdkd`  +0.013·`lctt_dau_tu`  +0.013·`lctt_tai_chinh`  +0.038·`lctt_thuan`  +0.051·`tien_dau_ky`  +0.051·`anh_huong_ty_gia`
7. -0.165·`tai_san_ngan_han`  +0.140·`tien_va_tuong_duong_tien`  +0.028·`dau_tu_tc_ngan_han`  +0.082·`phai_thu_ngan_han`  -0.496·`hang_ton_kho`  +0.082·`tsnh_khac`  +0.057·`tai_san_dai_han`  -0.108·`tong_tai_san`  -0.148·`no_phai_tra`  +0.040·`von_chu_so_huu`  -0.108·`tong_nguon_von`  -0.364·`ln_thuan_hdkd`  +0.636·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  -0.091·`thue_tndn_hien_hanh`  -0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`  +0.013·`lctt_hdkd`  +0.013·`lctt_dau_tu`  +0.013·`lctt_tai_chinh`  +0.038·`lctt_thuan`  +0.051·`tien_dau_ky`  +0.051·`anh_huong_ty_gia`
8. -0.058·`tai_san_ngan_han`  -0.105·`tien_va_tuong_duong_tien`  -0.347·`dau_tu_tc_ngan_han`  -0.061·`phai_thu_ngan_han`  +0.516·`hang_ton_kho`  -0.061·`tsnh_khac`  -0.050·`tai_san_dai_han`  -0.108·`tong_tai_san`  +0.017·`no_phai_tra`  -0.125·`von_chu_so_huu`  -0.108·`tong_nguon_von`  +0.273·`ln_thuan_hdkd`  +0.273·`ln_khac`  +0.545·`loi_nhuan_truoc_thue`  -0.182·`thue_tndn_hien_hanh`  -0.182·`thue_tndn_hoan_lai`  +0.182·`loi_nhuan_sau_thue`  -0.010·`lctt_hdkd`  -0.010·`lctt_dau_tu`  -0.010·`lctt_tai_chinh`  -0.029·`lctt_thuan`  -0.038·`tien_dau_ky`  -0.038·`anh_huong_ty_gia`
9. -0.223·`tai_san_ngan_han`  +0.035·`tien_va_tuong_duong_tien`  -0.320·`dau_tu_tc_ngan_han`  +0.021·`phai_thu_ngan_han`  +0.021·`hang_ton_kho`  +0.021·`tsnh_khac`  +0.008·`tai_san_dai_han`  -0.216·`tong_tai_san`  -0.132·`no_phai_tra`  -0.084·`von_chu_so_huu`  -0.216·`tong_nguon_von`  -0.091·`ln_thuan_hdkd`  -0.091·`ln_khac`  -0.182·`loi_nhuan_truoc_thue`  +0.727·`thue_tndn_hien_hanh`  -0.273·`thue_tndn_hoan_lai`  +0.273·`loi_nhuan_sau_thue`  +0.003·`lctt_hdkd`  +0.003·`lctt_dau_tu`  +0.003·`lctt_tai_chinh`  +0.010·`lctt_thuan`  +0.013·`tien_dau_ky`  +0.013·`anh_huong_ty_gia`
10. -0.223·`tai_san_ngan_han`  +0.035·`tien_va_tuong_duong_tien`  -0.320·`dau_tu_tc_ngan_han`  +0.021·`phai_thu_ngan_han`  +0.021·`hang_ton_kho`  +0.021·`tsnh_khac`  +0.008·`tai_san_dai_han`  -0.216·`tong_tai_san`  -0.132·`no_phai_tra`  -0.084·`von_chu_so_huu`  -0.216·`tong_nguon_von`  -0.091·`ln_thuan_hdkd`  -0.091·`ln_khac`  -0.182·`loi_nhuan_truoc_thue`  -0.273·`thue_tndn_hien_hanh`  +0.727·`thue_tndn_hoan_lai`  +0.273·`loi_nhuan_sau_thue`  +0.003·`lctt_hdkd`  +0.003·`lctt_dau_tu`  +0.003·`lctt_tai_chinh`  +0.010·`lctt_thuan`  +0.013·`tien_dau_ky`  +0.013·`anh_huong_ty_gia`
11. +0.223·`tai_san_ngan_han`  -0.035·`tien_va_tuong_duong_tien`  +0.320·`dau_tu_tc_ngan_han`  -0.021·`phai_thu_ngan_han`  -0.021·`hang_ton_kho`  -0.021·`tsnh_khac`  -0.008·`tai_san_dai_han`  +0.216·`tong_tai_san`  +0.132·`no_phai_tra`  +0.084·`von_chu_so_huu`  +0.216·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  +0.273·`thue_tndn_hien_hanh`  +0.273·`thue_tndn_hoan_lai`  +0.727·`loi_nhuan_sau_thue`  -0.003·`lctt_hdkd`  -0.003·`lctt_dau_tu`  -0.003·`lctt_tai_chinh`  -0.010·`lctt_thuan`  -0.013·`tien_dau_ky`  -0.013·`anh_huong_ty_gia`
12. -0.003·`tai_san_ngan_han`  +0.186·`tien_va_tuong_duong_tien`  +0.101·`dau_tu_tc_ngan_han`  +0.070·`phai_thu_ngan_han`  +0.070·`hang_ton_kho`  -0.430·`tsnh_khac`  -0.044·`tai_san_dai_han`  -0.047·`tong_tai_san`  -0.104·`no_phai_tra`  +0.057·`von_chu_so_huu`  -0.047·`tong_nguon_von`  +0.744·`lctt_hdkd`  -0.256·`lctt_dau_tu`  -0.256·`lctt_tai_chinh`  +0.233·`lctt_thuan`  -0.023·`tien_dau_ky`  -0.023·`anh_huong_ty_gia`
13. -0.003·`tai_san_ngan_han`  +0.186·`tien_va_tuong_duong_tien`  +0.101·`dau_tu_tc_ngan_han`  +0.070·`phai_thu_ngan_han`  +0.070·`hang_ton_kho`  -0.430·`tsnh_khac`  -0.044·`tai_san_dai_han`  -0.047·`tong_tai_san`  -0.104·`no_phai_tra`  +0.057·`von_chu_so_huu`  -0.047·`tong_nguon_von`  -0.256·`lctt_hdkd`  +0.744·`lctt_dau_tu`  -0.256·`lctt_tai_chinh`  +0.233·`lctt_thuan`  -0.023·`tien_dau_ky`  -0.023·`anh_huong_ty_gia`
14. -0.003·`tai_san_ngan_han`  +0.186·`tien_va_tuong_duong_tien`  +0.101·`dau_tu_tc_ngan_han`  +0.070·`phai_thu_ngan_han`  +0.070·`hang_ton_kho`  -0.430·`tsnh_khac`  -0.044·`tai_san_dai_han`  -0.047·`tong_tai_san`  -0.104·`no_phai_tra`  +0.057·`von_chu_so_huu`  -0.047·`tong_nguon_von`  -0.256·`lctt_hdkd`  -0.256·`lctt_dau_tu`  +0.744·`lctt_tai_chinh`  +0.233·`lctt_thuan`  -0.023·`tien_dau_ky`  -0.023·`anh_huong_ty_gia`
15. +0.304·`tai_san_ngan_han`  +0.115·`tien_va_tuong_duong_tien`  -0.160·`dau_tu_tc_ngan_han`  -0.050·`phai_thu_ngan_han`  -0.050·`hang_ton_kho`  +0.450·`tsnh_khac`  -0.321·`tai_san_dai_han`  -0.017·`tong_tai_san`  +0.049·`no_phai_tra`  -0.066·`von_chu_so_huu`  -0.017·`tong_nguon_von`  +0.192·`lctt_hdkd`  +0.192·`lctt_dau_tu`  +0.192·`lctt_tai_chinh`  +0.577·`lctt_thuan`  -0.231·`tien_dau_ky`  -0.231·`anh_huong_ty_gia`
16. +0.301·`tai_san_ngan_han`  +0.301·`tien_va_tuong_duong_tien`  -0.059·`dau_tu_tc_ngan_han`  +0.020·`phai_thu_ngan_han`  +0.020·`hang_ton_kho`  +0.020·`tsnh_khac`  -0.365·`tai_san_dai_han`  -0.064·`tong_tai_san`  -0.055·`no_phai_tra`  -0.009·`von_chu_so_huu`  -0.064·`tong_nguon_von`  -0.064·`lctt_hdkd`  -0.064·`lctt_dau_tu`  -0.064·`lctt_tai_chinh`  -0.191·`lctt_thuan`  +0.746·`tien_dau_ky`  -0.254·`anh_huong_ty_gia`
17. +0.301·`tai_san_ngan_han`  +0.301·`tien_va_tuong_duong_tien`  -0.059·`dau_tu_tc_ngan_han`  +0.020·`phai_thu_ngan_han`  +0.020·`hang_ton_kho`  +0.020·`tsnh_khac`  -0.365·`tai_san_dai_han`  -0.064·`tong_tai_san`  -0.055·`no_phai_tra`  -0.009·`von_chu_so_huu`  -0.064·`tong_nguon_von`  -0.064·`lctt_hdkd`  -0.064·`lctt_dau_tu`  -0.064·`lctt_tai_chinh`  -0.191·`lctt_thuan`  -0.254·`tien_dau_ky`  +0.746·`anh_huong_ty_gia`
