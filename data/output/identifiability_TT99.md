# Identifiability — chuẩn TT99

> Sinh tự động bởi `src/constraints.py`. Đối chiếu bảng ma trận bên dưới
> với Phụ lục của Thông tư trước khi tin vào bất kỳ con số nào ở đây.

## Tổng quan

- Số chỉ tiêu (n): **21**
- Số đẳng thức dùng được: **7**
- Hạng `rank(A)`: **7**
- Chiều không gian null `dim null(A)`: **14**
- Số field định vị được lỗi một-trường: **5 / 21**
- Số field có **cột toàn 0** (lỗi không PHÁT HIỆN được): **0 / 21** — không có

Nghĩa là **14/21** chiều trong không gian lỗi hoàn toàn vô hình
với mọi phương pháp dựa trên ràng buộc — residual bằng 0 tuyệt đối.

## Ma trận ràng buộc A

Mỗi dòng một đẳng thức, `+1` cho thành phần, `-1` cho tổng, `.` cho 0.

| Đẳng thức | tai_san_ngan_han | tien_va_tuong_duong_tien | dau_tu_tc_ngan_han | phai_thu_ngan_han | hang_ton_kho | tai_san_sinh_hoc_ngan_han | tsnh_khac | tai_san_dai_han | tong_tai_san | no_phai_tra | von_chu_so_huu | tong_nguon_von | doanh_thu_thuan | gia_von_hang_ban | loi_nhuan_gop | ln_thuan_hdkd | ln_khac | loi_nhuan_truoc_thue | thue_tndn_hien_hanh | thue_tndn_hoan_lai | loi_nhuan_sau_thue |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Tài sản ngắn hạn + Tài sản dài hạn phải bằng Tổng tài sản | +1 | . | . | . | . | . | . | +1 | -1 | . | . | . | . | . | . | . | . | . | . | . | . |
| Nợ phải trả + Vốn chủ sở hữu phải bằng Tổng cộng nguồn vốn (mã 440) | . | . | . | . | . | . | . | . | . | +1 | +1 | -1 | . | . | . | . | . | . | . | . | . |
| Tổng cộng nguồn vốn phải bằng Tổng cộng tài sản | . | . | . | . | . | . | . | . | -1 | . | . | +1 | . | . | . | . | . | . | . | . | . |
| Giá vốn hàng bán + Lợi nhuận gộp phải bằng Doanh thu thuần | . | . | . | . | . | . | . | . | . | . | . | . | -1 | +1 | +1 | . | . | . | . | . | . |
| Lợi nhuận thuần từ HĐKD + Lợi nhuận khác phải bằng Lợi nhuận trước thuế | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | +1 | +1 | -1 | . | . | . |
| Lợi nhuận sau thuế + chi phí thuế hiện hành + hoãn lại phải bằng Lợi nhuận trước thuế | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | . | -1 | +1 | +1 | +1 |
| Các thành phần tài sản ngắn hạn phải cộng bằng Tài sản ngắn hạn (TT99: mã 100 = 110+120+130+140+150+160) | -1 | +1 | +1 | +1 | +1 | +1 | +1 | . | . | . | . | . | . | . | . | . | . | . | . | . | . |

## Định vị lỗi một-trường

Định vị được khi cột của field khác 0 **và** không tỷ lệ với cột nào khác.

| Chỉ tiêu | Cột trong A | Định vị được | Ghi chú |
|---|---|---|---|
| `tai_san_ngan_han` | `+1 0 0 0 0 0 -1` | có | cột riêng biệt |
| `tien_va_tuong_duong_tien` | `0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, phai_thu_ngan_han, tai_san_sinh_hoc_ngan_han, tsnh_khac |
| `dau_tu_tc_ngan_han` | `0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: hang_ton_kho, phai_thu_ngan_han, tai_san_sinh_hoc_ngan_han, tien_va_tuong_duong_tien, tsnh_khac |
| `phai_thu_ngan_han` | `0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, tai_san_sinh_hoc_ngan_han, tien_va_tuong_duong_tien, tsnh_khac |
| `hang_ton_kho` | `0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, phai_thu_ngan_han, tai_san_sinh_hoc_ngan_han, tien_va_tuong_duong_tien, tsnh_khac |
| `tai_san_sinh_hoc_ngan_han` | `0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, phai_thu_ngan_han, tien_va_tuong_duong_tien, tsnh_khac |
| `tsnh_khac` | `0 0 0 0 0 0 +1` | KHÔNG | cột tỷ lệ với: dau_tu_tc_ngan_han, hang_ton_kho, phai_thu_ngan_han, tai_san_sinh_hoc_ngan_han, tien_va_tuong_duong_tien |
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
- `tien_va_tuong_duong_tien` ↔ `tai_san_sinh_hoc_ngan_han`
- `tien_va_tuong_duong_tien` ↔ `tsnh_khac`
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

## Cơ sở không gian null

Mỗi vector dưới đây là một hướng lỗi mà residual không nhìn thấy.

1. -0.578·`tai_san_ngan_han`  -0.089·`tien_va_tuong_duong_tien`  +0.094·`dau_tu_tc_ngan_han`  -0.089·`phai_thu_ngan_han`  -0.089·`hang_ton_kho`  -0.089·`tai_san_sinh_hoc_ngan_han`  -0.317·`tsnh_khac`  +0.699·`tai_san_dai_han`  +0.120·`tong_tai_san`  +0.060·`no_phai_tra`  +0.060·`von_chu_so_huu`  +0.120·`tong_nguon_von`
2. +0.399·`tai_san_ngan_han`  -0.033·`tien_va_tuong_duong_tien`  +0.650·`dau_tu_tc_ngan_han`  -0.033·`phai_thu_ngan_han`  -0.033·`hang_ton_kho`  -0.033·`tai_san_sinh_hoc_ngan_han`  -0.118·`tsnh_khac`  +0.000·`tai_san_dai_han`  +0.400·`tong_tai_san`  +0.200·`no_phai_tra`  +0.200·`von_chu_so_huu`  +0.400·`tong_nguon_von`
3. +0.023·`tai_san_ngan_han`  -0.474·`tien_va_tuong_duong_tien`  -0.185·`dau_tu_tc_ngan_han`  +0.104·`phai_thu_ngan_han`  +0.104·`hang_ton_kho`  +0.104·`tai_san_sinh_hoc_ngan_han`  +0.370·`tsnh_khac`  +0.127·`tai_san_dai_han`  +0.149·`tong_tai_san`  +0.575·`no_phai_tra`  -0.425·`von_chu_so_huu`  +0.149·`tong_nguon_von`
4. +0.023·`tai_san_ngan_han`  -0.474·`tien_va_tuong_duong_tien`  -0.185·`dau_tu_tc_ngan_han`  +0.104·`phai_thu_ngan_han`  +0.104·`hang_ton_kho`  +0.104·`tai_san_sinh_hoc_ngan_han`  +0.370·`tsnh_khac`  +0.127·`tai_san_dai_han`  +0.149·`tong_tai_san`  -0.425·`no_phai_tra`  +0.575·`von_chu_so_huu`  +0.149·`tong_nguon_von`
5. +0.156·`tai_san_ngan_han`  +0.596·`tien_va_tuong_duong_tien`  -0.559·`dau_tu_tc_ngan_han`  +0.018·`phai_thu_ngan_han`  +0.018·`hang_ton_kho`  +0.018·`tai_san_sinh_hoc_ngan_han`  +0.065·`tsnh_khac`  +0.174·`tai_san_dai_han`  +0.330·`tong_tai_san`  +0.165·`no_phai_tra`  +0.165·`von_chu_so_huu`  +0.330·`tong_nguon_von`
6. +0.037·`tai_san_ngan_han`  -0.063·`tien_va_tuong_duong_tien`  -0.063·`dau_tu_tc_ngan_han`  +0.514·`phai_thu_ngan_han`  -0.063·`hang_ton_kho`  -0.063·`tai_san_sinh_hoc_ngan_han`  -0.225·`tsnh_khac`  -0.026·`tai_san_dai_han`  +0.011·`tong_tai_san`  +0.005·`no_phai_tra`  +0.005·`von_chu_so_huu`  +0.011·`tong_nguon_von`  +0.667·`doanh_thu_thuan`  +0.333·`gia_von_hang_ban`  +0.333·`loi_nhuan_gop`
7. -0.037·`tai_san_ngan_han`  +0.063·`tien_va_tuong_duong_tien`  +0.063·`dau_tu_tc_ngan_han`  -0.514·`phai_thu_ngan_han`  +0.063·`hang_ton_kho`  +0.063·`tai_san_sinh_hoc_ngan_han`  +0.225·`tsnh_khac`  +0.026·`tai_san_dai_han`  -0.011·`tong_tai_san`  -0.005·`no_phai_tra`  -0.005·`von_chu_so_huu`  -0.011·`tong_nguon_von`  +0.333·`doanh_thu_thuan`  +0.667·`gia_von_hang_ban`  -0.333·`loi_nhuan_gop`
8. -0.037·`tai_san_ngan_han`  +0.063·`tien_va_tuong_duong_tien`  +0.063·`dau_tu_tc_ngan_han`  -0.514·`phai_thu_ngan_han`  +0.063·`hang_ton_kho`  +0.063·`tai_san_sinh_hoc_ngan_han`  +0.225·`tsnh_khac`  +0.026·`tai_san_dai_han`  -0.011·`tong_tai_san`  -0.005·`no_phai_tra`  -0.005·`von_chu_so_huu`  -0.011·`tong_nguon_von`  +0.333·`doanh_thu_thuan`  -0.333·`gia_von_hang_ban`  +0.667·`loi_nhuan_gop`
9. -0.026·`tai_san_ngan_han`  +0.044·`tien_va_tuong_duong_tien`  +0.044·`dau_tu_tc_ngan_han`  +0.044·`phai_thu_ngan_han`  -0.533·`hang_ton_kho`  +0.218·`tai_san_sinh_hoc_ngan_han`  +0.157·`tsnh_khac`  +0.018·`tai_san_dai_han`  -0.007·`tong_tai_san`  -0.004·`no_phai_tra`  -0.004·`von_chu_so_huu`  -0.007·`tong_nguon_von`  +0.636·`ln_thuan_hdkd`  -0.364·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  +0.091·`thue_tndn_hien_hanh`  +0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`
10. -0.026·`tai_san_ngan_han`  +0.044·`tien_va_tuong_duong_tien`  +0.044·`dau_tu_tc_ngan_han`  +0.044·`phai_thu_ngan_han`  -0.533·`hang_ton_kho`  +0.218·`tai_san_sinh_hoc_ngan_han`  +0.157·`tsnh_khac`  +0.018·`tai_san_dai_han`  -0.007·`tong_tai_san`  -0.004·`no_phai_tra`  -0.004·`von_chu_so_huu`  -0.007·`tong_nguon_von`  -0.364·`ln_thuan_hdkd`  +0.636·`ln_khac`  +0.273·`loi_nhuan_truoc_thue`  +0.091·`thue_tndn_hien_hanh`  +0.091·`thue_tndn_hoan_lai`  +0.091·`loi_nhuan_sau_thue`
11. +0.059·`tai_san_ngan_han`  -0.101·`tien_va_tuong_duong_tien`  -0.101·`dau_tu_tc_ngan_han`  -0.101·`phai_thu_ngan_han`  +0.476·`hang_ton_kho`  +0.247·`tai_san_sinh_hoc_ngan_han`  -0.361·`tsnh_khac`  -0.042·`tai_san_dai_han`  +0.017·`tong_tai_san`  +0.008·`no_phai_tra`  +0.008·`von_chu_so_huu`  +0.017·`tong_nguon_von`  +0.273·`ln_thuan_hdkd`  +0.273·`ln_khac`  +0.545·`loi_nhuan_truoc_thue`  +0.182·`thue_tndn_hien_hanh`  +0.182·`thue_tndn_hoan_lai`  +0.182·`loi_nhuan_sau_thue`
12. -0.033·`tai_san_ngan_han`  +0.057·`tien_va_tuong_duong_tien`  +0.057·`dau_tu_tc_ngan_han`  +0.057·`phai_thu_ngan_han`  +0.057·`hang_ton_kho`  -0.465·`tai_san_sinh_hoc_ngan_han`  +0.204·`tsnh_khac`  +0.024·`tai_san_dai_han`  -0.010·`tong_tai_san`  -0.005·`no_phai_tra`  -0.005·`von_chu_so_huu`  -0.010·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  +0.727·`thue_tndn_hien_hanh`  -0.273·`thue_tndn_hoan_lai`  -0.273·`loi_nhuan_sau_thue`
13. -0.033·`tai_san_ngan_han`  +0.057·`tien_va_tuong_duong_tien`  +0.057·`dau_tu_tc_ngan_han`  +0.057·`phai_thu_ngan_han`  +0.057·`hang_ton_kho`  -0.465·`tai_san_sinh_hoc_ngan_han`  +0.204·`tsnh_khac`  +0.024·`tai_san_dai_han`  -0.010·`tong_tai_san`  -0.005·`no_phai_tra`  -0.005·`von_chu_so_huu`  -0.010·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  -0.273·`thue_tndn_hien_hanh`  +0.727·`thue_tndn_hoan_lai`  -0.273·`loi_nhuan_sau_thue`
14. -0.033·`tai_san_ngan_han`  +0.057·`tien_va_tuong_duong_tien`  +0.057·`dau_tu_tc_ngan_han`  +0.057·`phai_thu_ngan_han`  +0.057·`hang_ton_kho`  -0.465·`tai_san_sinh_hoc_ngan_han`  +0.204·`tsnh_khac`  +0.024·`tai_san_dai_han`  -0.010·`tong_tai_san`  -0.005·`no_phai_tra`  -0.005·`von_chu_so_huu`  -0.010·`tong_nguon_von`  +0.091·`ln_thuan_hdkd`  +0.091·`ln_khac`  +0.182·`loi_nhuan_truoc_thue`  -0.273·`thue_tndn_hien_hanh`  -0.273·`thue_tndn_hoan_lai`  +0.727·`loi_nhuan_sau_thue`
