"""
Quy tắc dấu của ba dòng khấu trừ — ANNOTATION-GUIDELINE.md mục 3.3.

Bộ test này neo vào ca thật đã đo trên tập gold ngày 27/08/2026: MWG và VRE
mỗi tài liệu sai đúng ba dòng này, không thừa không thiếu.
"""

from fields_config import Standard, chuan_hoa_dau
from validation import validate_result


def test_gia_von_am_thanh_duong():
    ra, da_doi = chuan_hoa_dau({"gia_von_hang_ban": -107_515_846_476})
    assert ra["gia_von_hang_ban"] == 107_515_846_476
    assert da_doi == ["gia_von_hang_ban"]


def test_gia_von_da_duong_thi_khong_dong_vao():
    ra, da_doi = chuan_hoa_dau({"gia_von_hang_ban": 107_515_846_476})
    assert ra["gia_von_hang_ban"] == 107_515_846_476
    assert da_doi == []


def test_thue_hien_hanh_thanh_am_khi_thue_lam_giam_loi_nhuan():
    """
    Mã 60 < mã 50 nghĩa là thuế là chi phí, nên mã 51 phải ÂM.

    Chiều lật đổi ngày 31/08/2026 cùng quy ước dấu có hướng. Trước đó mã 51
    lưu theo độ lớn nên ca này lật về dương; nay nó lưu theo nghĩa kinh tế
    nên tiền đi ra khỏi lợi nhuận phải mang dấu âm.
    """
    ra, da_doi = chuan_hoa_dau(
        {
            "loi_nhuan_truoc_thue": 1_000,
            "loi_nhuan_sau_thue": 800,
            "thue_tndn_hien_hanh": 150,
        }
    )
    assert ra["thue_tndn_hien_hanh"] == -150
    assert da_doi == ["thue_tndn_hien_hanh"]


def test_ma_52_khong_bi_dong_vao():
    """
    Mã 52 DƯƠNG là THU NHẬP thuế hoãn lại, và nó hợp lệ ngay cả khi mã 60 < mã 50.

    `Mã 60 = Mã 50 + Mã 51 + Mã 52`, nên một mã 52 dương sống chung được với
    mã 60 < mã 50 miễn mã 51 đủ âm. Gold của MWG và VRE ghi đúng như vậy. Áp
    chữ nghĩa guideline cho mã 52 sẽ lật nó thành âm và đẻ ra lỗi câm mới —
    đây là hàng rào chặn ai đó "hoàn thiện" quy tắc theo bảng trong mục 3.3.
    """
    ra, da_doi = chuan_hoa_dau(
        {
            "loi_nhuan_truoc_thue": 1_000,
            "loi_nhuan_sau_thue": 800,
            "thue_tndn_hien_hanh": 250,
            "thue_tndn_hoan_lai": 50,
        }
    )
    assert ra["thue_tndn_hoan_lai"] == 50
    assert da_doi == ["thue_tndn_hien_hanh"]


def test_thue_giu_nguyen_dau_khi_thue_la_thu_nhap():
    """
    Mã 60 > mã 50 là ca hẹp mà Thông tư dành cho: thuế là THU NHẬP, nên mã
    51 DƯƠNG ở đây là số liệu thật.

    Lật nó là xoá mất số liệu — đây là chỗ phân biệt quy tắc này với một
    lệnh `-abs()` mù.
    """
    ra, da_doi = chuan_hoa_dau(
        {
            "loi_nhuan_truoc_thue": 800,
            "loi_nhuan_sau_thue": 1_000,
            "thue_tndn_hien_hanh": 200,
        }
    )
    assert ra["thue_tndn_hien_hanh"] == 200
    assert da_doi == []


def test_thieu_moc_50_hoac_60_thi_khong_doan():
    """Guideline buộc quyết định bằng mã 50 và 60; vắng chúng thì không sửa."""
    ra, da_doi = chuan_hoa_dau(
        {"loi_nhuan_truoc_thue": 1_000, "thue_tndn_hien_hanh": 150}
    )
    assert ra["thue_tndn_hien_hanh"] == 150
    assert da_doi == []


def test_khong_dung_dang_thuc_de_chon_dau():
    """
    Sau khi sửa dấu, đẳng thức mã 60 VẪN có thể vỡ.

    Đây là tính chất phải giữ, không phải thiếu sót: nếu bước sửa dấu giải
    đẳng thức `Mã 60 = Mã 50 + Mã 51 + Mã 52` ra dấu thì mọi kết quả đều
    thoả nó, và phép đo H1 mất nghĩa vì tín hiệu vi phạm ràng buộc bị chính
    bước trích xuất làm phẳng. Ở đây độ lớn sai thì đẳng thức vẫn phải vỡ.
    """
    ra, _ = chuan_hoa_dau(
        {
            "loi_nhuan_truoc_thue": 1_000,
            "loi_nhuan_sau_thue": 800,
            "thue_tndn_hien_hanh": 999,
            "thue_tndn_hoan_lai": 0,
        }
    )
    assert ra["thue_tndn_hien_hanh"] == -999  # noqa: PLR2004
    assert ra["loi_nhuan_sau_thue"] != (
        ra["loi_nhuan_truoc_thue"] + ra["thue_tndn_hien_hanh"] + ra["thue_tndn_hoan_lai"]
    )


def test_gia_tri_chuoi_van_duoc_sua_qua_validate_result():
    """
    Ca hồi quy: VLM đôi khi trả số dưới dạng CHUỖI.

    Bản nháp đầu gọi chuan_hoa_dau() trong router trước bước ép kiểu, nên
    isinstance(value, (int, float)) là False và hàm lặng lẽ không làm gì —
    hỏng đúng kiểu không ai thấy. Nay nó chạy trong validate_result() ngay
    sau bước ép kiểu, nên chuỗi cũng phải được sửa.
    """
    da_kiem = validate_result(
        {"gia_von_hang_ban": "(107.515.846.476)", "don_vi_tinh": "VND"},
        Standard.TT200,
    )
    assert da_kiem["data"]["gia_von_hang_ban"] == 107_515_846_476
    assert da_kiem["meta"]["dau_da_sua"] == ["gia_von_hang_ban"]


def test_khong_con_canh_bao_gia_von_am():
    """
    Cảnh báo "giá vốn âm bất thường" từng nổ trên chính đầu ra của pipeline.

    Đo trên HNG ngày 27/08/2026: dự đoán sinh 4 cảnh báo, trong đó có dòng
    này cộng hai đẳng thức vỡ, còn gold chỉ 2. Hệ tự báo lỗi về số liệu do
    chính nó đọc sai dấu.
    """
    da_kiem = validate_result(
        {"gia_von_hang_ban": -107_515_846_476, "don_vi_tinh": "VND"},
        Standard.TT200,
    )
    assert not any("âm bất thường" in canh_bao for canh_bao in da_kiem["warnings"])
