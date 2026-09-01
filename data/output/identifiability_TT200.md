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
| Lợi nhuận thuần từ HĐKD + Lợi nhuận khác phải bằng Lợi nhuận trước thuế | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | -1 | . | . | . | . | . | . | . | . | . |
| B03: Mã số 50 = Mã số 20 + Mã số 30 + Mã số 40 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 | -1 | . | . |
| B03: Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61, và mã 70 ≡ mã 110 trên B01 — LIÊN KẾT CHÉO GIỮA HAI BIỂU MẪU | . | -1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 |
| B02 dạng tổng: Mã 20 = Mã 10 + Mã 11 | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | -1 | . | . | . | . | . | . | . | . | . | . | . | . |
| B02 dạng tổng: Mã 60 = Mã 50 + Mã 51 + Mã 52 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | +1 | -1 | . | . | . | . | . | . |
| Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn (TT200: mã 100 = 110+120+130+140+150) | -1 | +1 | +1 | +1 | +1 | +1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . |

## Định vị lỗi một-trường

Định vị được khi cột của field khác 0 **và** không tỷ lệ với cột nào khác.

| Chỉ tiêu | Cột trong A | Định vị được | Ghi chú |
|---|---|---|---|
| `tai_san_ngan_han` | `+1 0 0 0 0 0 0 0 -1` | có | cột riêng biệt |
| `tien_va_tuong_duong_tien` | `0 0 0 0 0 -1 0 0 +1` | có | cột riêng biệt |
| `dau_tu_tc_ngan_han` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: hang_ton_kho, phai_thu_ngan_han, tsnh_khac |
| `phai_thu_ngan_han` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, tsnh_khac |
| `hang_ton_kho` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, phai_thu_ngan_han, tsnh_khac |
| `tsnh_khac` | `0 0 0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, phai_thu_ngan_han |
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

1. -0.025·`tai_san_ngan_han`  -0.185·`tien_va_tuong_duong_tien`  -0.056·`dau_tu_tc_ngan_han`  +0.140·`phai_thu_ngan_han`  +0.140·`hang_ton_kho`  -0.063·`tsnh_khac`  +0.115·`tai_san_dai_han`  +0.090·`tong_tai_san`  -0.616·`no_phai_tra`  +0.706·`von_chu_so_huu`  +0.090·`tong_nguon_von`  -0.017·`lctt_hdkd`  -0.017·`lctt_dau_tu`  -0.017·`lctt_tai_chinh`  -0.050·`lctt_thuan`  -0.067·`tien_dau_ky`  -0.067·`anh_huong_ty_gia`
2. +0.164·`tai_san_ngan_han`  +0.428·`tien_va_tuong_duong_tien`  -0.573·`dau_tu_tc_ngan_han`  +0.003·`phai_thu_ngan_han`  +0.003·`hang_ton_kho`  +0.303·`tsnh_khac`  +0.167·`tai_san_dai_han`  +0.332·`tong_tai_san`  +0.163·`no_phai_tra`  +0.169·`von_chu_so_huu`  +0.332·`tong_nguon_von`  +0.039·`lctt_hdkd`  +0.039·`lctt_dau_tu`  +0.039·`lctt_tai_chinh`  +0.117·`lctt_thuan`  +0.156·`tien_dau_ky`  +0.156·`anh_huong_ty_gia`
3. +0.317·`tai_san_ngan_han`  +0.102·`tien_va_tuong_duong_tien`  -0.006·`dau_tu_tc_ngan_han`  +0.060·`phai_thu_ngan_han`  +0.060·`hang_ton_kho`  +0.101·`tsnh_khac`  -0.411·`tai_san_dai_han`  -0.094·`tong_tai_san`  -0.116·`no_phai_tra`  +0.022·`von_chu_so_huu`  -0.094·`tong_nguon_von`  +0.667·`doanh_thu_thuan`  -0.333·`gia_von_hang_ban`  +0.333·`loi_nhuan_gop`  +0.009·`lctt_hdkd`  +0.009·`lctt_dau_tu`  +0.009·`lctt_tai_chinh`  +0.028·`lctt_thuan`  +0.037·`tien_dau_ky`  +0.037·`anh_huong_ty_gia`
4. +0.317·`tai_san_ngan_han`  +0.102·`tien_va_tuong_duong_tien`  -0.006·`dau_tu_tc_ngan_han`  +0.060·`phai_thu_ngan_han`  +0.060·`hang_ton_kho`  +0.101·`tsnh_khac`  -0.411·`tai_san_dai_han`  -0.094·`tong_tai_san`  -0.116·`no_phai_tra`  +0.022·`von_chu_so_huu`  -0.094·`tong_nguon_von`  -0.333·`doanh_thu_thuan`  +0.667·`gia_von_hang_ban`  +0.333·`loi_nhuan_gop`  +0.009·`lctt_hdkd`  +0.009·`lctt_dau_tu`  +0.009·`lctt_tai_chinh`  +0.028·`lctt_thuan`  +0.037·`tien_dau_ky`  +0.037·`anh_huong_ty_gia`
5. -0.317·`tai_san_ngan_han`  -0.102·`tien_va_tuong_duong_tien`  +0.006·`dau_tu_tc_ngan_han`  -0.060·`phai_thu_ngan_han`  -0.060·`hang_ton_kho`  -0.101·`tsnh_khac`  +0.411·`tai_san_dai_han`  +0.094·`tong_tai_san`  +0.116·`no_phai_tra`  -0.022·`von_chu_so_huu`  +0.094·`tong_nguon_von`  +0.333·`doanh_thu_thuan`  +0.333·`gia_von_hang_ban`  +0.667·`loi_nhuan_gop`  -0.009·`lctt_hdkd`  -0.009·`lctt_dau_tu`  -0.009·`lctt_tai_chinh`  -0.028·`lctt_thuan`  -0.037·`tien_dau_ky`  -0.037·`anh_huong_ty_gia`
6. -0.129·`tai_san_ngan_han`  +0.137·`tien_va_tuong_duong_tien`  +0.015·`dau_tu_tc_ngan_han`  -0.497·`phai_thu_ngan_han`  +0.080·`hang_ton_kho`  +0.136·`tsnh_khac`  +0.016·`tai_san_dai_han`  -0.113·`tong_tai_san`  -0.149·`no_phai_tra`  +0.036·`von_chu_so_huu`  -0.113·`tong_nguon_von`  +0.636·`ln_thuan_hdkd`  -0.364·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  -0.091·`thue_tndn_hien_hanh`  -0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`  +0.012·`lctt_hdkd`  +0.012·`lctt_dau_tu`  +0.012·`lctt_tai_chinh`  +0.037·`lctt_thuan`  +0.050·`tien_dau_ky`  +0.050·`anh_huong_ty_gia`
7. -0.129·`tai_san_ngan_han`  +0.137·`tien_va_tuong_duong_tien`  +0.015·`dau_tu_tc_ngan_han`  -0.497·`phai_thu_ngan_han`  +0.080·`hang_ton_kho`  +0.136·`tsnh_khac`  +0.016·`tai_san_dai_han`  -0.113·`tong_tai_san`  -0.149·`no_phai_tra`  +0.036·`von_chu_so_huu`  -0.113·`tong_nguon_von`  -0.364·`ln_thuan_hdkd`  +0.636·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  -0.091·`thue_tndn_hien_hanh`  -0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`  +0.012·`lctt_hdkd`  +0.012·`lctt_dau_tu`  +0.012·`lctt_tai_chinh`  +0.037·`lctt_thuan`  +0.050·`tien_dau_ky`  +0.050·`anh_huong_ty_gia`
8. -0.086·`tai_san_ngan_han`  -0.103·`tien_va_tuong_duong_tien`  -0.338·`dau_tu_tc_ngan_han`  +0.517·`phai_thu_ngan_han`  -0.060·`hang_ton_kho`  -0.102·`tsnh_khac`  -0.018·`tai_san_dai_han`  -0.104·`tong_tai_san`  +0.017·`no_phai_tra`  -0.121·`von_chu_so_huu`  -0.104·`tong_nguon_von`  +0.273·`ln_thuan_hdkd`  +0.273·`ln_khac`  +0.545·`loi_nhuan_truoc_thue`  -0.182·`thue_tndn_hien_hanh`  -0.182·`thue_tndn_hoan_lai`  +0.182·`loi_nhuan_sau_thue`  -0.009·`lctt_hdkd`  -0.009·`lctt_dau_tu`  -0.009·`lctt_tai_chinh`  -0.028·`lctt_thuan`  -0.037·`tien_dau_ky`  -0.037·`anh_huong_ty_gia`
9. -0.214·`tai_san_ngan_han`  +0.034·`tien_va_tuong_duong_tien`  -0.323·`dau_tu_tc_ngan_han`  +0.020·`phai_thu_ngan_han`  +0.020·`hang_ton_kho`  +0.034·`tsnh_khac`  -0.003·`tai_san_dai_han`  -0.217·`tong_tai_san`  -0.132·`no_phai_tra`  -0.085·`von_chu_so_huu`  -0.217·`tong_nguon_von`  -0.091·`ln_thuan_hdkd`  -0.091·`ln_khac`  -0.182·`loi_nhuan_truoc_thue`  +0.727·`thue_tndn_hien_hanh`  -0.273·`thue_tndn_hoan_lai`  +0.273·`loi_nhuan_sau_thue`  +0.003·`lctt_hdkd`  +0.003·`lctt_dau_tu`  +0.003·`lctt_tai_chinh`  +0.009·`lctt_thuan`  +0.013·`tien_dau_ky`  +0.013·`anh_huong_ty_gia`
10. -0.214·`tai_san_ngan_han`  +0.034·`tien_va_tuong_duong_tien`  -0.323·`dau_tu_tc_ngan_han`  +0.020·`phai_thu_ngan_han`  +0.020·`hang_ton_kho`  +0.034·`tsnh_khac`  -0.003·`tai_san_dai_han`  -0.217·`tong_tai_san`  -0.132·`no_phai_tra`  -0.085·`von_chu_so_huu`  -0.217·`tong_nguon_von`  -0.091·`ln_thuan_hdkd`  -0.091·`ln_khac`  -0.182·`loi_nhuan_truoc_thue`  -0.273·`thue_tndn_hien_hanh`  +0.727·`thue_tndn_hoan_lai`  +0.273·`loi_nhuan_sau_thue`  +0.003·`lctt_hdkd`  +0.003·`lctt_dau_tu`  +0.003·`lctt_tai_chinh`  +0.009·`lctt_thuan`  +0.013·`tien_dau_ky`  +0.013·`anh_huong_ty_gia`
11. +0.214·`tai_san_ngan_han`  -0.034·`tien_va_tuong_duong_tien`  +0.323·`dau_tu_tc_ngan_han`  -0.020·`phai_thu_ngan_han`  -0.020·`hang_ton_kho`  -0.034·`tsnh_khac`  +0.003·`tai_san_dai_han`  +0.217·`tong_tai_san`  +0.132·`no_phai_tra`  +0.085·`von_chu_so_huu`  +0.217·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  +0.273·`thue_tndn_hien_hanh`  +0.273·`thue_tndn_hoan_lai`  +0.727·`loi_nhuan_sau_thue`  -0.003·`lctt_hdkd`  -0.003·`lctt_dau_tu`  -0.003·`lctt_tai_chinh`  -0.009·`lctt_thuan`  -0.013·`tien_dau_ky`  -0.013·`anh_huong_ty_gia`
12. -0.056·`tai_san_ngan_han`  +0.189·`tien_va_tuong_duong_tien`  +0.120·`dau_tu_tc_ngan_han`  +0.072·`phai_thu_ngan_han`  -0.428·`hang_ton_kho`  -0.008·`tsnh_khac`  +0.016·`tai_san_dai_han`  -0.040·`tong_tai_san`  -0.102·`no_phai_tra`  +0.063·`von_chu_so_huu`  -0.040·`tong_nguon_von`  +0.744·`lctt_hdkd`  -0.256·`lctt_dau_tu`  -0.256·`lctt_tai_chinh`  +0.233·`lctt_thuan`  -0.022·`tien_dau_ky`  -0.022·`anh_huong_ty_gia`
13. -0.056·`tai_san_ngan_han`  +0.189·`tien_va_tuong_duong_tien`  +0.120·`dau_tu_tc_ngan_han`  +0.072·`phai_thu_ngan_han`  -0.428·`hang_ton_kho`  -0.008·`tsnh_khac`  +0.016·`tai_san_dai_han`  -0.040·`tong_tai_san`  -0.102·`no_phai_tra`  +0.063·`von_chu_so_huu`  -0.040·`tong_nguon_von`  -0.256·`lctt_hdkd`  +0.744·`lctt_dau_tu`  -0.256·`lctt_tai_chinh`  +0.233·`lctt_thuan`  -0.022·`tien_dau_ky`  -0.022·`anh_huong_ty_gia`
14. -0.056·`tai_san_ngan_han`  +0.189·`tien_va_tuong_duong_tien`  +0.120·`dau_tu_tc_ngan_han`  +0.072·`phai_thu_ngan_han`  -0.428·`hang_ton_kho`  -0.008·`tsnh_khac`  +0.016·`tai_san_dai_han`  -0.040·`tong_tai_san`  -0.102·`no_phai_tra`  +0.063·`von_chu_so_huu`  -0.040·`tong_nguon_von`  -0.256·`lctt_hdkd`  -0.256·`lctt_dau_tu`  +0.744·`lctt_tai_chinh`  +0.233·`lctt_thuan`  -0.022·`tien_dau_ky`  -0.022·`anh_huong_ty_gia`
15. +0.031·`tai_san_ngan_han`  +0.132·`tien_va_tuong_duong_tien`  -0.066·`dau_tu_tc_ngan_han`  -0.040·`phai_thu_ngan_han`  +0.460·`hang_ton_kho`  -0.455·`tsnh_khac`  -0.009·`tai_san_dai_han`  +0.022·`tong_tai_san`  +0.057·`no_phai_tra`  -0.035·`von_chu_so_huu`  +0.022·`tong_nguon_von`  +0.194·`lctt_hdkd`  +0.194·`lctt_dau_tu`  +0.194·`lctt_tai_chinh`  +0.581·`lctt_thuan`  -0.225·`tien_dau_ky`  -0.225·`anh_huong_ty_gia`
16. -0.025·`tai_san_ngan_han`  +0.321·`tien_va_tuong_duong_tien`  +0.053·`dau_tu_tc_ngan_han`  +0.032·`phai_thu_ngan_han`  +0.032·`hang_ton_kho`  -0.463·`tsnh_khac`  +0.007·`tai_san_dai_han`  -0.018·`tong_tai_san`  -0.046·`no_phai_tra`  +0.028·`von_chu_so_huu`  -0.018·`tong_nguon_von`  -0.062·`lctt_hdkd`  -0.062·`lctt_dau_tu`  -0.062·`lctt_tai_chinh`  -0.185·`lctt_thuan`  +0.753·`tien_dau_ky`  -0.247·`anh_huong_ty_gia`
17. -0.025·`tai_san_ngan_han`  +0.321·`tien_va_tuong_duong_tien`  +0.053·`dau_tu_tc_ngan_han`  +0.032·`phai_thu_ngan_han`  +0.032·`hang_ton_kho`  -0.463·`tsnh_khac`  +0.007·`tai_san_dai_han`  -0.018·`tong_tai_san`  -0.046·`no_phai_tra`  +0.028·`von_chu_so_huu`  -0.018·`tong_nguon_von`  -0.062·`lctt_hdkd`  -0.062·`lctt_dau_tu`  -0.062·`lctt_tai_chinh`  -0.185·`lctt_thuan`  -0.247·`tien_dau_ky`  +0.753·`anh_huong_ty_gia`

## Bất biến với quy ước dấu

Ma trận trên dựng ở quy ước `tong`. Dựng lại ở quy ước `tru` cho ra **cùng** hạng, cùng số chiều không gian null, cùng danh sách chỉ tiêu
định vị được và cùng danh sách cặp không phân biệt được — so từng phần tử chứ
không chỉ so số đếm.

Lý do: đổi quy ước chỉ lật dấu vài cột của `A`, mà hạng, không gian null và
quan hệ tỷ lệ giữa các cột đều bất biến với phép lật ấy. Câu này được KIỂM LẠI
mỗi lần sinh báo cáo, không chép từ trí nhớ.
