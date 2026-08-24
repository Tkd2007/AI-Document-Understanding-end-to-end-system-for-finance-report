from fields_config import Standard
from validation import coerce_number, validate_result


def test_coerce_number_tu_string_co_dau_cham():
    assert coerce_number("13.217.639.635.987") == 13217639635987


def test_coerce_number_bool_tra_none():
    assert coerce_number(True) is None


def test_coerce_number_none():
    assert coerce_number(None) is None


def test_coerce_number_so_san_co():
    assert coerce_number(13217639635987) == 13217639635987


def test_coerce_number_chuoi_rac():
    assert coerce_number("abc") is None


# Số thật từ báo cáo VNM Q1/2026 (đơn vị VND). Cả ba đẳng thức kế toán
# trong FIELD_IDENTITIES khớp tới từng đồng trên bộ số này.
#
# don_vi_tinh là phần bắt buộc của một bộ số hợp lệ, không phải trang trí:
# thiếu nó thì không xác minh được bậc độ lớn, và đó chính là ca mà mọi
# đẳng thức kế toán đều bó tay vì hệ ràng buộc là thuần nhất.
VNM_Q1_2026 = {
    "tai_san_ngan_han": 29403116984122,
    "hang_ton_kho": 5393002084291,
    "tai_san_dai_han": 18372709942261,
    "tong_tai_san": 47775826926383,
    "no_phai_tra": 16666572149360,
    "von_chu_so_huu": 31109254777023,
    "doanh_thu_thuan": 13217639635987,
    "gia_von_hang_ban": 7278764406353,
    "loi_nhuan_gop": 5938875229634,
    "loi_nhuan_truoc_thue": 2523887147085,
    "loi_nhuan_sau_thue": 2049247209782,
    "don_vi_tinh": "đồng",
}


def test_bao_cao_that_khong_co_warning():
    assert validate_result(VNM_Q1_2026, Standard.TT99)["warnings"] == []


def test_lech_mot_chu_so_bi_bat():
    """
    Sửa Tài sản ngắn hạn lệch 10 triệu đồng — mức lệch nhỏ tới mức mọi
    check bất đẳng thức đều bỏ qua, chỉ đẳng thức kế toán với dung sai
    1e-7 mới bắt được.
    """
    sai = dict(VNM_Q1_2026)
    sai["tai_san_ngan_han"] += 10_000_000

    assert validate_result(sai, Standard.TT99)["warnings"] != []


# Doanh nghiệp lỗ nặng: lỗ luỹ kế đã ăn hết vốn nên VCSH âm, bán dưới giá
# vốn nên lãi gộp âm, và chi phí thuế hoãn lại làm LNST âm sâu hơn LNTT.
#
# Bộ số này KHÔNG phải bịa cho vừa test: cả ba đẳng thức kế toán vẫn khớp
# tới từng đồng, đúng như trên một báo cáo đã kiểm toán. Nó là ca biên mà
# tập Stress trong proposal cố ý đưa vào, và trước bản vá A1 thì cả ba bất
# đẳng thức đều báo oan trên đúng một bộ số hoàn toàn đúng.
DOANH_NGHIEP_LO = {
    "tai_san_ngan_han": 600_000_000_000,
    "hang_ton_kho": 100_000_000_000,
    "tai_san_dai_han": 400_000_000_000,
    "tong_tai_san": 1_000_000_000_000,
    "no_phai_tra": 1_200_000_000_000,
    "von_chu_so_huu": -200_000_000_000,
    "doanh_thu_thuan": 500_000_000_000,
    "gia_von_hang_ban": 600_000_000_000,
    "loi_nhuan_gop": -100_000_000_000,
    "loi_nhuan_truoc_thue": -300_000_000_000,
    "loi_nhuan_sau_thue": -320_000_000_000,
    "don_vi_tinh": "đồng",
}


def _canh_bao_nhac_toi(result: dict, cum_tu: str) -> list[str]:
    """Các cảnh báo có nhắc tới cụm từ này — để assert đúng luật cần xét."""
    return [w for w in validate_result(result, Standard.TT99)["warnings"] if cum_tu in w]


def test_doanh_nghiep_lo_khong_sinh_warning_nao():
    """
    Ca biên tổng hợp: cả ba bất đẳng thức có điều kiện đều bị vi phạm về
    mặt hình thức, nhưng bộ số hoàn toàn đúng nên không được báo gì.
    """
    assert validate_result(DOANH_NGHIEP_LO, Standard.TT99)["warnings"] == []


def test_vcsh_am_thi_no_vuot_tong_tai_san_khong_bi_bao_oan():
    """
    VCSH âm nghĩa là nợ VƯỢT tổng tài sản, và đó là hệ quả số học của
    chính đẳng thức no_phai_tra + von_chu_so_huu = tong_tai_san chứ không
    phải lỗi đọc.
    """
    assert _canh_bao_nhac_toi(DOANH_NGHIEP_LO, "Nợ phải trả") == []


def test_lai_gop_am_thi_gia_von_vuot_doanh_thu_khong_bi_bao_oan():
    """Bán dưới giá vốn là chuyện có thật, không phải lỗi trích xuất."""
    assert _canh_bao_nhac_toi(DOANH_NGHIEP_LO, "Giá vốn hàng bán") == []


def test_lo_thi_lnst_am_sau_hon_lntt_khong_bi_bao_oan():
    """
    LNTT = -300 tỷ, LNST = -320 tỷ là bình thường khi lỗ. Cách cũ so trên
    trị tuyệt đối (320 > 300) nên báo oan đúng ca này.
    """
    assert _canh_bao_nhac_toi(DOANH_NGHIEP_LO, "Lợi nhuận sau thuế") == []


def test_co_lai_ma_lnst_lon_hon_lntt_van_phai_bao():
    """
    Test quan trọng nhất của A1: chốt rằng việc nới lỏng KHÔNG làm mất khả
    năng bắt lỗi. Doanh nghiệp có lãi thì thuế chỉ làm giảm, nên LNST vượt
    LNTT là dấu hiệu đọc nhầm dòng.
    """
    sai = dict(VNM_Q1_2026)
    sai["loi_nhuan_sau_thue"] = sai["loi_nhuan_truoc_thue"] + 100_000_000_000

    assert _canh_bao_nhac_toi(sai, "Lợi nhuận sau thuế") != []


def test_field_dieu_kien_bi_doc_sai_thi_luat_tu_tat():
    """
    Ghi lại tường minh CÁI GIÁ của bản vá A1, để nó không trở thành lỗi im
    lặng mà không ai biết.

    Điều kiện áp dụng đọc từ chính một field cũng do model trích ra. Nếu
    loi_nhuan_gop bị đọc sai thành âm thì luật gia_von <= doanh_thu tự tắt,
    và một lỗi thật ở giá vốn sẽ lọt qua.

    Test này KHÔNG khẳng định hành vi đó là tốt. Nó chốt rằng hành vi đó
    đúng như thiết kế, để nếu sau này ai đổi cách xử lý thì test đỏ và
    người đó phải đọc lại phần đánh đổi trong docstring FieldRelation.
    """
    lot_luoi = dict(VNM_Q1_2026)
    lot_luoi["gia_von_hang_ban"] = lot_luoi["doanh_thu_thuan"] * 2
    lot_luoi["loi_nhuan_gop"] = -lot_luoi["doanh_thu_thuan"]

    assert _canh_bao_nhac_toi(lot_luoi, "Giá vốn hàng bán") == []


# Bộ số TT200 dựng để chốt việc chuẩn phải đi tới nơi kiểm đẳng thức.
#
# Phân rã tài sản ngắn hạn CỐ Ý lệch 500 tỷ: tổng các thành phần là 4.500
# trong khi Tài sản ngắn hạn ghi 5.000. Không có tai_san_sinh_hoc_ngan_han
# vì đó là chỉ tiêu TT200 KHÔNG có — chính chỗ đó là bẫy.
BAO_CAO_TT200_LECH_PHAN_RA = {
    "tai_san_ngan_han": 5_000_000_000_000,
    "tien_va_tuong_duong_tien": 1_000_000_000_000,
    "dau_tu_tc_ngan_han": 1_000_000_000_000,
    "phai_thu_ngan_han": 1_000_000_000_000,
    "hang_ton_kho": 1_000_000_000_000,
    "tsnh_khac": 500_000_000_000,
    "tai_san_dai_han": 5_000_000_000_000,
    "tong_tai_san": 10_000_000_000_000,
    "no_phai_tra": 4_000_000_000_000,
    "von_chu_so_huu": 6_000_000_000_000,
    "tong_nguon_von": 10_000_000_000_000,
    "doanh_thu_thuan": 1_000_000_000_000,
    "loi_nhuan_sau_thue": 100_000_000_000,
    "don_vi_tinh": "đồng",
}


def _canh_bao_phan_ra(warnings) -> list:
    return [w for w in warnings if "thành phần tài sản ngắn hạn" in w]


def test_bao_cao_TT200_duoc_kiem_bang_dang_thuc_TT200():
    """
    Lệch phân rã tài sản ngắn hạn của báo cáo TT200 PHẢI bị bắt.

    Đây là hồi quy cho một lỗi câm đã có thật. validate_result() từng để
    standard=DEFAULT_STANDARD (tức TT99), nên báo cáo TT200 bị kiểm bằng
    đẳng thức TT99. Đẳng thức TT99 chứa tai_san_sinh_hoc_ngan_han — chỉ
    tiêu TT200 không có, nên luôn None, nên CẢ đẳng thức bị bỏ qua. Một lỗi
    500 tỷ đi qua không một tiếng động.
    """
    warnings = validate_result(BAO_CAO_TT200_LECH_PHAN_RA, Standard.TT200)["warnings"]

    assert _canh_bao_phan_ra(warnings), (
        "Lệch 500 tỷ trong phân rã tài sản ngắn hạn TT200 mà không sinh cảnh báo — "
        "gần như chắc chắn đang kiểm bằng đẳng thức của chuẩn khác"
    )


def test_dung_nham_chuan_thi_dang_thuc_phan_ra_im_lang():
    """
    Chốt CHIỀU NGƯỢC LẠI, tức chốt cái giá của việc nhận diện sai chuẩn.

    Cùng bộ số đó đem kiểm bằng TT99 thì đẳng thức phân rã im lặng, vì
    thiếu hạng tử tài sản sinh học. Test này tồn tại để nếu ai đó lỡ trả
    mặc định về cho validate_result() thì test trên đỏ và test này giải
    thích ngay vì sao.
    """
    warnings = validate_result(BAO_CAO_TT200_LECH_PHAN_RA, Standard.TT99)["warnings"]

    assert not _canh_bao_phan_ra(warnings)


def test_meta_ghi_dung_chuan_da_dung():
    """Chuẩn nào được đem đi kiểm phải đọc lại được từ kết quả, không phải đoán."""
    assert validate_result(VNM_Q1_2026, Standard.TT200)["meta"]["standard"] == "TT200"
    assert validate_result(VNM_Q1_2026, Standard.TT99)["meta"]["standard"] == "TT99"
