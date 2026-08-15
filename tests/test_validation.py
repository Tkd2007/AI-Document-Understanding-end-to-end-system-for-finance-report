from validation import coerce_number


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


from validation import validate_result

# Số thật từ báo cáo VNM Q1/2026 (đơn vị VND). Cả ba đẳng thức kế toán
# trong FIELD_IDENTITIES khớp tới từng đồng trên bộ số này.
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
}


def test_bao_cao_that_khong_co_warning():
    assert validate_result(VNM_Q1_2026)["warnings"] == []


def test_lech_mot_chu_so_bi_bat():
    """
    Sửa Tài sản ngắn hạn lệch 10 triệu đồng — mức lệch nhỏ tới mức mọi
    check bất đẳng thức đều bỏ qua, chỉ đẳng thức kế toán với dung sai
    1e-7 mới bắt được.
    """
    sai = dict(VNM_Q1_2026)
    sai["tai_san_ngan_han"] += 10_000_000

    assert validate_result(sai)["warnings"] != []