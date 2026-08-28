# Luật dấu trên tập gold — đo lại trên kết quả đã lưu

Sinh bằng `PYTHONPATH=src python src/eval/do_luat_dau.py`.
Không gọi API; đọc `tap_gold_chuan_tu_gold.json` rồi so với `data/gold/`.

## Điều kiện A — đầu ra thô, TRƯỚC bản vá `chuan_hoa_dau()`

| doc_id | Đẳng thức | Trường sai | Lỗi dấu thật | Trạng thái luật | Phán xử | Ứng viên |
|---|---:|---:|---:|---|---|---|
| `BMP_2026Q1_TT99` | 6 | 1 | 0 | `im_lang` | **im_lang_dung** | — |
| `DGC_2025Q2_TT200` | 8 | 1 | 0 | `im_lang` | **im_lang_dung** | — |
| `DLG_2026Q2_TT99` | 7 | 0 | 0 | `khong_co_lech` | **im_lang_dung** | — |
| `HNG_2025H1_TT200` | 7 | 6 | 4 | `nghi_ngo` | **chi_dung_ten** | gia_von_hang_ban |
| `HPG_2026Q2_TT99` | 6 | 1 | 0 | `im_lang` | **im_lang_dung** | — |
| `MWG_2025Q1_TT200` | 9 | 3 | 3 | `nghi_ngo` | **chi_dung_ten** | gia_von_hang_ban |
| `SBT_2025Q2_TT200` | 9 | 8 | 0 | `im_lang` | **im_lang_dung** | — |
| `TTF_2026Q1_TT99` | 7 | 0 | 0 | `khong_co_lech` | **im_lang_dung** | — |
| `VHC_2025Q1_TT200` | 6 | 1 | 1 | `khong_co_lech` | **bo_sot** | — |
| `VRE_2026Q1_TT99` | 7 | 3 | 3 | `nghi_ngo` | **chi_dung_ten** | gia_von_hang_ban |

| Phán xử | Số tài liệu |
|---|---:|
| `im_lang_dung` | 6 |
| `chi_dung_ten` | 3 |
| `bo_sot` | 1 |

**Báo nhầm: 0 / 10**

## Điều kiện B — SAU `chuan_hoa_dau()`, tức hiện trạng pipeline

| doc_id | Đẳng thức | Trường sai | Lỗi dấu thật | Trạng thái luật | Phán xử | Ứng viên |
|---|---:|---:|---:|---|---|---|
| `BMP_2026Q1_TT99` | 6 | 1 | 0 | `im_lang` | **im_lang_dung** | — |
| `DGC_2025Q2_TT200` | 8 | 1 | 0 | `im_lang` | **im_lang_dung** | — |
| `DLG_2026Q2_TT99` | 7 | 0 | 0 | `khong_co_lech` | **im_lang_dung** | — |
| `HNG_2025H1_TT200` | 7 | 5 | 3 | `im_lang` | **bo_sot** | — |
| `HPG_2026Q2_TT99` | 6 | 1 | 0 | `im_lang` | **im_lang_dung** | — |
| `MWG_2025Q1_TT200` | 9 | 1 | 1 | `dinh_vi_duoc` | **dinh_vi_dung** | thue_tndn_hoan_lai |
| `SBT_2025Q2_TT200` | 9 | 8 | 0 | `im_lang` | **im_lang_dung** | — |
| `TTF_2026Q1_TT99` | 7 | 0 | 0 | `khong_co_lech` | **im_lang_dung** | — |
| `VHC_2025Q1_TT200` | 6 | 0 | 0 | `khong_co_lech` | **im_lang_dung** | — |
| `VRE_2026Q1_TT99` | 7 | 1 | 1 | `dinh_vi_duoc` | **dinh_vi_dung** | thue_tndn_hoan_lai |

| Phán xử | Số tài liệu |
|---|---:|
| `im_lang_dung` | 7 |
| `dinh_vi_dung` | 2 |
| `bo_sot` | 1 |

**Báo nhầm: 0 / 10**

## Hiệu quả trên chỉ số của dự án

| Điều kiện | Trường đúng | Lỗi câm |
|---|---:|---:|
| Thô — như pipeline đã ghi ra | 216/265 = **81.5%** | 24/240 = **10.0%** |
| Sau `chuan_hoa_dau()` (`a0cd5ab`) | 222/265 = **83.8%** | 18/240 = **7.5%** |
| Sau `chuan_hoa_dau()` + **tầng repair** | 224/265 = **84.5%** | 16/240 = **6.7%** |

Tầng repair đổi **2 ô** trên 10 tài liệu:
- `MWG_2025Q1_TT200` — thue_tndn_hoan_lai
- `VRE_2026Q1_TT99` — thue_tndn_hoan_lai

Đọc con số này cho đúng: phần đóng góp THÊM của tầng repair mỏng, vì `chuan_hoa_dau()` đã lấy hết phần dễ ở cùng chế độ lỗi. Giá trị của luật không nằm ở số ô nó sửa mà ở chỗ nó **chứng minh được** — và ở chỗ nó phân xử Câu 13 bằng số liệu thay vì bằng tranh luận câu chữ: cả hai lần ra tay đều rơi đúng vào `thue_tndn_hoan_lai`, chỉ tiêu mà guideline cũ bắt ghi dương.
