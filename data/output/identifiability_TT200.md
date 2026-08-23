# Identifiability — chuẩn TT200

> Sinh tự động bởi `src/constraints.py`. Đối chiếu bảng ma trận bên dưới
> với Phụ lục của Thông tư trước khi tin vào bất kỳ con số nào ở đây.

## Tổng quan

- Số chỉ tiêu (n): **20**
- Số đẳng thức dùng được: **7**
- Hạng `rank(A)`: **7**
- Chiều không gian null `dim null(A)`: **13**
- Số field định vị được lỗi một-trường: **5 / 20**
- Số field có **cột toàn 0** (lỗi không PHÁT HIỆN được): **0 / 20** — không có

Nghĩa là **13/20** chiều trong không gian lỗi hoàn toàn vô hình
với mọi phương pháp dựa trên ràng buộc — residual bằng 0 tuyệt đối.

## Ma trận ràng buộc A

Mỗi dòng một đẳng thức, `+1` cho thành phần, `-1` cho tổng, `.` cho 0.

| Đẳng thức | tai_san_ngan_han | tien_va_tuong_duong_tien | dau_tu_tc_ngan_han | phai_thu_ngan_han | hang_ton_kho | tsnh_khac | tai_san_dai_han | tong_tai_san | no_phai_tra | von_chu_so_huu | tong_nguon_von | doanh_thu_thuan | gia_von_hang_ban | loi_nhuan_gop | ln_thuan_hdkd | ln_khac | loi_nhuan_truoc_thue | thue_tndn_hien_hanh | thue_tndn_hoan_lai | loi_nhuan_sau_thue |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tài sản ngắn hạn + Tài sản dài hạn phải bằng Tổng tài sản | +1 | . | . | . | . | . | +1 | -1 | . | . | . | . | . | . | . | . | . | . | . | . |
| Nợ phải trả + Vốn chủ sở hữu phải bằng Tổng cộng nguồn vốn (mã 440) | . | . | . | . | . | . | . | . | +1 | +1 | -1 | . | . | . | . | . | . | . | . | . |
| Tổng cộng nguồn vốn phải bằng Tổng cộng tài sản | . | . | . | . | . | . | . | -1 | . | . | +1 | . | . | . | . | . | . | . | . | . |
| Giá vốn hàng bán + Lợi nhuận gộp phải bằng Doanh thu thuần | . | . | . | . | . | . | . | . | . | . | . | -1 | +1 | +1 | . | . | . | . | . | . |
| Lợi nhuận thuần từ HĐKD + Lợi nhuận khác phải bằng Lợi nhuận trước thuế | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | -1 | . | . | . |
| Lợi nhuận sau thuế + chi phí thuế hiện hành + hoãn lại phải bằng Lợi nhuận trước thuế | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | -1 | +1 | +1 | +1 |
| Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn (TT200: mã 100 = 110+120+130+140+150) | -1 | +1 | +1 | +1 | +1 | +1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . |

## Định vị lỗi một-trường

Định vị được khi cột của field khác 0 **và** không tỷ lệ với cột nào khác.

| Chỉ tiêu | Cột trong A | Định vị được | Ghi chú |
|---|---|---|---|
| `tai_san_ngan_han` | `+1 0 0 0 0 0 -1` | có | cột riêng biệt |
| `tien_va_tuong_duong_tien` | `0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, phai_thu_ngan_han, tsnh_khac |
| `dau_tu_tc_ngan_han` | `0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: hang_ton_kho, phai_thu_ngan_han, tien_va_tuong_duong_tien, tsnh_khac |
| `phai_thu_ngan_han` | `0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, tien_va_tuong_duong_tien, tsnh_khac |
| `hang_ton_kho` | `0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, phai_thu_ngan_han, tien_va_tuong_duong_tien, tsnh_khac |
| `tsnh_khac` | `0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, phai_thu_ngan_han, tien_va_tuong_duong_tien |
| `tai_san_dai_han` | `+1 0 0 0 0 0 0` | có | cột riêng biệt |
| `tong_tai_san` | `-1 0 -1 0 0 0 0` | có | cột riêng biệt |
| `no_phai_tra` | `0 +1 0 0 0 0 0` | KHÔNG | cột tỷ lệ với: von_chu_so_huu |
| `von_chu_so_huu` | `0 +1 0 0 0 0 0` | KHÔNG | cột tỷ lệ với: no_phai_tra |
| `tong_nguon_von` | `0 -1 +1 0 0 0 0` | có | cột riêng biệt |
| `doanh_thu_thuan` | `0 0 0 -1 0 0 0` | KHÔNG | cột tỷ lệ với: gia_von_hang_ban, loi_nhuan_gop |
| `gia_von_hang_ban` | `0 0 0 +1 0 0 0` | KHÔNG | cột tỷ lệ với: doanh_thu_thuan, loi_nhuan_gop |
| `loi_nhuan_gop` | `0 0 0 +1 0 0 0` | KHÔNG | cột tỷ lệ với: doanh_thu_thuan, gia_von_hang_ban |
| `ln_thuan_hdkd` | `0 0 0 0 +1 0 0` | KHÔNG | cột tỷ lệ với: ln_khac |
| `ln_khac` | `0 0 0 0 +1 0 0` | KHÔNG | cột tỷ lệ với: ln_thuan_hdkd |
| `loi_nhuan_truoc_thue` | `0 0 0 0 -1 -1 0` | có | cột riêng biệt |
| `thue_tndn_hien_hanh` | `0 0 0 0 0 +1 0` | KHÔNG | cột tỷ lệ với: loi_nhuan_sau_thue, thue_tndn_hoan_lai |
| `thue_tndn_hoan_lai` | `0 0 0 0 0 +1 0` | KHÔNG | cột tỷ lệ với: loi_nhuan_sau_thue, thue_tndn_hien_hanh |
| `loi_nhuan_sau_thue` | `0 0 0 0 0 +1 0` | KHÔNG | cột tỷ lệ với: thue_tndn_hien_hanh, thue_tndn_hoan_lai |

## Cặp chỉ tiêu không phân biệt được

Lỗi ở hai chỉ tiêu trong cùng một cặp cho residual pattern giống hệt nhau.

- `tien_va_tuong_duong_tien` ↔ `dau_tu_tc_ngan_han`
- `tien_va_tuong_duong_tien` ↔ `phai_thu_ngan_han`
- `tien_va_tuong_duong_tien` ↔ `hang_ton_kho`
- `tien_va_tuong_duong_tien` ↔ `tsnh_khac`
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

## Cơ sở không gian null

Mỗi vector dưới đây là một hướng lỗi mà residual không nhìn thấy.

1. +0.464·`tai_san_ngan_han`  -0.040·`tien_va_tuong_duong_tien`  +0.625·`dau_tu_tc_ngan_han`  -0.040·`phai_thu_ngan_han`  -0.040·`hang_ton_kho`  -0.040·`tsnh_khac`  -0.073·`tai_san_dai_han`  +0.391·`tong_tai_san`  +0.195·`no_phai_tra`  +0.195·`von_chu_so_huu`  +0.391·`tong_nguon_von`
2. -0.179·`tai_san_ngan_han`  -0.451·`tien_va_tuong_duong_tien`  -0.107·`dau_tu_tc_ngan_han`  +0.126·`phai_thu_ngan_han`  +0.126·`hang_ton_kho`  +0.126·`tsnh_khac`  +0.356·`tai_san_dai_han`  +0.177·`tong_tai_san`  +0.589·`no_phai_tra`  -0.411·`von_chu_so_huu`  +0.177·`tong_nguon_von`
3. -0.179·`tai_san_ngan_han`  -0.451·`tien_va_tuong_duong_tien`  -0.107·`dau_tu_tc_ngan_han`  +0.126·`phai_thu_ngan_han`  +0.126·`hang_ton_kho`  +0.126·`tsnh_khac`  +0.356·`tai_san_dai_han`  +0.177·`tong_tai_san`  -0.411·`no_phai_tra`  +0.589·`von_chu_so_huu`  +0.177·`tong_nguon_von`
4. +0.121·`tai_san_ngan_han`  +0.600·`tien_va_tuong_duong_tien`  -0.546·`dau_tu_tc_ngan_han`  +0.022·`phai_thu_ngan_han`  +0.022·`hang_ton_kho`  +0.022·`tsnh_khac`  +0.215·`tai_san_dai_han`  +0.335·`tong_tai_san`  +0.168·`no_phai_tra`  +0.168·`von_chu_so_huu`  +0.335·`tong_nguon_von`
5. +0.159·`tai_san_ngan_han`  -0.077·`tien_va_tuong_duong_tien`  -0.110·`dau_tu_tc_ngan_han`  +0.500·`phai_thu_ngan_han`  -0.077·`hang_ton_kho`  -0.077·`tsnh_khac`  -0.166·`tai_san_dai_han`  -0.006·`tong_tai_san`  -0.003·`no_phai_tra`  -0.003·`von_chu_so_huu`  -0.006·`tong_nguon_von`  +0.667·`doanh_thu_thuan`  +0.333·`gia_von_hang_ban`  +0.333·`loi_nhuan_gop`
6. -0.159·`tai_san_ngan_han`  +0.077·`tien_va_tuong_duong_tien`  +0.110·`dau_tu_tc_ngan_han`  -0.500·`phai_thu_ngan_han`  +0.077·`hang_ton_kho`  +0.077·`tsnh_khac`  +0.166·`tai_san_dai_han`  +0.006·`tong_tai_san`  +0.003·`no_phai_tra`  +0.003·`von_chu_so_huu`  +0.006·`tong_nguon_von`  +0.333·`doanh_thu_thuan`  +0.667·`gia_von_hang_ban`  -0.333·`loi_nhuan_gop`
7. -0.159·`tai_san_ngan_han`  +0.077·`tien_va_tuong_duong_tien`  +0.110·`dau_tu_tc_ngan_han`  -0.500·`phai_thu_ngan_han`  +0.077·`hang_ton_kho`  +0.077·`tsnh_khac`  +0.166·`tai_san_dai_han`  +0.006·`tong_tai_san`  +0.003·`no_phai_tra`  +0.003·`von_chu_so_huu`  +0.006·`tong_nguon_von`  +0.333·`doanh_thu_thuan`  -0.333·`gia_von_hang_ban`  +0.667·`loi_nhuan_gop`
8. -0.111·`tai_san_ngan_han`  +0.054·`tien_va_tuong_duong_tien`  +0.077·`dau_tu_tc_ngan_han`  +0.054·`phai_thu_ngan_han`  -0.524·`hang_ton_kho`  +0.228·`tsnh_khac`  +0.116·`tai_san_dai_han`  +0.004·`tong_tai_san`  +0.002·`no_phai_tra`  +0.002·`von_chu_so_huu`  +0.004·`tong_nguon_von`  +0.636·`ln_thuan_hdkd`  -0.364·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  +0.091·`thue_tndn_hien_hanh`  +0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`
9. -0.111·`tai_san_ngan_han`  +0.054·`tien_va_tuong_duong_tien`  +0.077·`dau_tu_tc_ngan_han`  +0.054·`phai_thu_ngan_han`  -0.524·`hang_ton_kho`  +0.228·`tsnh_khac`  +0.116·`tai_san_dai_han`  +0.004·`tong_tai_san`  +0.002·`no_phai_tra`  +0.002·`von_chu_so_huu`  +0.004·`tong_nguon_von`  -0.364·`ln_thuan_hdkd`  +0.636·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  +0.091·`thue_tndn_hien_hanh`  +0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`
10. +0.256·`tai_san_ngan_han`  -0.123·`tien_va_tuong_duong_tien`  -0.177·`dau_tu_tc_ngan_han`  -0.123·`phai_thu_ngan_han`  +0.454·`hang_ton_kho`  +0.225·`tsnh_khac`  -0.266·`tai_san_dai_han`  -0.010·`tong_tai_san`  -0.005·`no_phai_tra`  -0.005·`von_chu_so_huu`  -0.010·`tong_nguon_von`  +0.273·`ln_thuan_hdkd`  +0.273·`ln_khac`  +0.545·`loi_nhuan_truoc_thue`  +0.182·`thue_tndn_hien_hanh`  +0.182·`thue_tndn_hoan_lai`  +0.182·`loi_nhuan_sau_thue`
11. -0.144·`tai_san_ngan_han`  +0.070·`tien_va_tuong_duong_tien`  +0.100·`dau_tu_tc_ngan_han`  +0.070·`phai_thu_ngan_han`  +0.070·`hang_ton_kho`  -0.453·`tsnh_khac`  +0.150·`tai_san_dai_han`  +0.006·`tong_tai_san`  +0.003·`no_phai_tra`  +0.003·`von_chu_so_huu`  +0.006·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  +0.727·`thue_tndn_hien_hanh`  -0.273·`thue_tndn_hoan_lai`  -0.273·`loi_nhuan_sau_thue`
12. -0.144·`tai_san_ngan_han`  +0.070·`tien_va_tuong_duong_tien`  +0.100·`dau_tu_tc_ngan_han`  +0.070·`phai_thu_ngan_han`  +0.070·`hang_ton_kho`  -0.453·`tsnh_khac`  +0.150·`tai_san_dai_han`  +0.006·`tong_tai_san`  +0.003·`no_phai_tra`  +0.003·`von_chu_so_huu`  +0.006·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  -0.273·`thue_tndn_hien_hanh`  +0.727·`thue_tndn_hoan_lai`  -0.273·`loi_nhuan_sau_thue`
13. -0.144·`tai_san_ngan_han`  +0.070·`tien_va_tuong_duong_tien`  +0.100·`dau_tu_tc_ngan_han`  +0.070·`phai_thu_ngan_han`  +0.070·`hang_ton_kho`  -0.453·`tsnh_khac`  +0.150·`tai_san_dai_han`  +0.006·`tong_tai_san`  +0.003·`no_phai_tra`  +0.003·`von_chu_so_huu`  +0.006·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  -0.273·`thue_tndn_hien_hanh`  -0.273·`thue_tndn_hoan_lai`  +0.727·`loi_nhuan_sau_thue`
