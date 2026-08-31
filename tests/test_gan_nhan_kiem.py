"""
Test phần kiểm đẳng thức của công cụ gán nhãn.

Điểm phải giữ bằng test, vì hỏng thì không có gì nổ: đẳng thức KHÔNG CHẠY
ĐƯỢC phải được báo riêng chứ không được đếm là đã đạt. Gộp hai thứ đó lại sẽ
biến một tài liệu gán nhãn dở dang thành một tài liệu trông đã sạch, và nó
đi thẳng vào tập gold như vậy.
"""

from fields_config import Standard, fields_for
from gan_nhan.kiem import (
    CHUA_GO,
    CHUA_QUYET_DINH_DUOC,
    DAT,
    DAU_DAT,
    LECH,
    NGHI_SAI_DAU,
    O_NGUOI_PHAI_TICK,
    THIEU_THANH_PHAN,
    con_thieu_o_kiem,
    kiem_dang_thuc,
    kiem_dau_khau_tru,
)


def _bo_can_bang() -> dict:
    """
    Bộ số cân đúng MỌI đẳng thức của TT99, dựng tay để đọc được bằng mắt.

    Không lấy từ báo cáo thật vì bộ số thật trong `tests/test_constraints.py`
    chỉ phủ B01 với B02 — bản PDF mẫu là ảnh scan nên không rút số B03 ra
    được. Ở đây cần một bộ phủ trọn 9 đẳng thức, và tính chất cần kiểm là
    hành vi của hàm chứ không phải tính thật của con số.
    """
    v = {ten: 0 for ten in fields_for(Standard.TT99)}
    v.update(
        {
            # B01: 100 = 110+120+130+140+150+160, và 280 = 100+200 = 300+400
            "tien_va_tuong_duong_tien": 300,
            "dau_tu_tc_ngan_han": 100,
            "phai_thu_ngan_han": 200,
            "hang_ton_kho": 350,
            "tai_san_sinh_hoc_ngan_han": 0,
            "tsnh_khac": 50,
            "tai_san_ngan_han": 1000,
            "tai_san_dai_han": 500,
            "tong_tai_san": 1500,
            "no_phai_tra": 900,
            "von_chu_so_huu": 600,
            "tong_nguon_von": 1500,
            # B02
            "doanh_thu_thuan": 800,
            "gia_von_hang_ban": 500,
            "loi_nhuan_gop": 300,
            "ln_thuan_hdkd": 200,
            "ln_khac": 20,
            "loi_nhuan_truoc_thue": 220,
            # TT99 — quy ước ĐỘ LỚN, chưa xác minh nên giữ như cũ. Bộ số
            # này chạy dưới Standard.TT99 nên đừng đồng bộ dấu với các ca
            # TT200 bên dưới; hai chuẩn đang cố ý khác nhau (31/08/2026).
            "thue_tndn_hien_hanh": 40,
            "thue_tndn_hoan_lai": 5,
            "loi_nhuan_sau_thue": 175,
            # B03: 50 = 20+30+40, và 110 = 50+60+61
            "lctt_hdkd": 400,
            "lctt_dau_tu": -250,
            "lctt_tai_chinh": -100,
            "lctt_thuan": 50,
            "tien_dau_ky": 240,
            "anh_huong_ty_gia": 10,
        }
    )
    return v


def test_bo_can_bang_thi_moi_dang_thuc_deu_dat():
    ket = kiem_dang_thuc(_bo_can_bang(), Standard.TT99)

    assert len(ket) == 9
    assert all(r.trang_thai == DAT for r in ket), [r.mo_ta for r in ket if r.trang_thai != DAT]


def test_lech_mot_o_thi_bao_dung_dang_thuc_do_va_bao_muc_lech():
    """
    Mức lệch phải có mặt: nó là thứ nói cho người biết đi đọc lại dòng nào.

    Nhưng đó cũng là toàn bộ những gì được nói ra — xem test dưới.
    """
    v = _bo_can_bang()
    v["hang_ton_kho"] = 400          # lệch +50 so với bộ cân

    ket = {r.mo_ta: r for r in kiem_dang_thuc(v, Standard.TT99)}
    hong = [r for r in ket.values() if r.trang_thai == LECH]

    assert len(hong) == 1
    assert "tài sản ngắn hạn" in hong[0].mo_ta.lower()
    assert hong[0].lech == 50


def test_khong_bao_gio_tra_ve_gia_tri_de_nghi():
    """
    Ràng buộc THIẾT KẾ, không phải chi tiết cài đặt.

    Với một lỗi đơn định vị được, ràng buộc chốt luôn giá trị đúng — phép đo
    `do_nghich_dao_mot_loi.py` cho thấy điều đó xảy ra ở 60,8% số lượt. Nên
    việc suy ra con số đúng là làm được, và chính vì làm được nên phải cố ý
    KHÔNG làm: đưa đáp án cho người gán nhãn là biến việc đọc lại thành việc
    điền vào, và tập gold sẽ luôn cân đúng theo cái cách làm nó vô dụng cho
    việc đo tỷ lệ lỗi thật.

    Test này khoá cái KHÔNG có mặt, nên nó phải kiểm trên toàn bộ hình dạng
    kết quả chứ không chỉ trên một khoá.
    """
    v = _bo_can_bang()
    v["hang_ton_kho"] = 400

    for r in kiem_dang_thuc(v, Standard.TT99):
        assert set(vars(r)) == {"mo_ta", "trang_thai", "lech", "thieu"}


def test_thieu_thanh_phan_khong_duoc_dem_la_dat():
    """
    `None` nghĩa là "có dòng mà đọc không ra", nên đẳng thức chứa nó không
    chạy được. Báo là `dat` sẽ nói dối rằng tài liệu đã sạch.
    """
    v = _bo_can_bang()
    v["hang_ton_kho"] = None

    ket = [r for r in kiem_dang_thuc(v, Standard.TT99) if r.trang_thai == THIEU_THANH_PHAN]

    assert len(ket) == 1
    assert ket[0].thieu == ("hang_ton_kho",)
    assert ket[0].lech is None


def test_gia_tri_0_van_cho_dang_thuc_chay_binh_thuong():
    """
    Phân biệt `0` với `None` là toàn bộ lý do guideline mục 3.4 tồn tại.
    Dòng vắng mặt ghi 0 chính là để đẳng thức phân rã vẫn chạy được.
    """
    v = _bo_can_bang()
    v["tai_san_sinh_hoc_ngan_han"] = 0

    assert all(r.trang_thai == DAT for r in kiem_dang_thuc(v, Standard.TT99))


def test_danh_muc_kiem_bat_nguoi_tick_dung_nhung_o_may_khong_biet():
    """
    Ô nào máy tự kiểm được thì đừng bắt người tick lại — tick hộ một ô mà
    máy không thật sự kiểm được mới là chỗ biến danh mục kiểm thành hình
    thức. Luật 1 là ô đầu tiên trong nhóm chỉ người biết.
    """
    assert "mu_voi_pipeline" in O_NGUOI_PHAI_TICK
    assert "khong_sua_cho_can" in O_NGUOI_PHAI_TICK
    assert "da_quy_doi" not in O_NGUOI_PHAI_TICK

    assert con_thieu_o_kiem({}) == list(O_NGUOI_PHAI_TICK)
    assert con_thieu_o_kiem(dict.fromkeys(O_NGUOI_PHAI_TICK, True)) == []


def _dau(values: dict, chuan: Standard = Standard.TT200) -> dict:
    """Kết quả kiểm dấu, tra theo tên trường cho dễ đọc."""
    return {r.truong: r.trang_thai for r in kiem_dau_khau_tru(values, chuan)}


def test_gia_von_am_bi_bao_la_nghi_sai_dau():
    """
    Guideline mục 3.3 bắt mã 11 ghi dương dù báo cáo in trong ngoặc đơn, vì
    văn bản đưa nó vào công thức `Mã 20 = Mã 10 - Mã 11`. `FIELD_RULES` đặt
    `allow_negative` False cho nó, nên âm là sai bất kể đẳng thức có cân hay
    không — không cần và không được chờ đẳng thức xác nhận.
    """
    v = {ten: 0 for ten in fields_for(Standard.TT200)}
    assert _dau({**v, "gia_von_hang_ban": 100})["gia_von_hang_ban"] == DAU_DAT
    assert _dau({**v, "gia_von_hang_ban": -100})["gia_von_hang_ban"] == NGHI_SAI_DAU


def test_thue_hoan_lai_duong_HOP_LE_khi_dang_thuc_da_can():
    """
    Hồi quy trên ca dương tính giả đã xảy ra thật, chép từ `MWG_2025Q1_TT200`.

    Bản đầu của phép kiểm này xét dấu từng chỉ tiêu thuế bằng dấu của TỔNG số
    thuế — tức so mã 60 với mã 50 — nên nó báo oan mã 52 ở đây. Mã 51 là chi
    phí thuế lớn (âm), mã 52 là khoản hoàn nhập (dương), tổng lại vẫn làm
    giảm lợi nhuận, và đẳng thức B02 cân chính xác đến từng đồng.

    Báo oan ở đây tốn hơn bỏ sót: giao diện nói "sửa DẤU, đây không phải lỗi
    của báo cáo", nên một cảnh báo sai sẽ đẩy người gán nhãn đi hỏng một giá
    trị vốn đúng.
    """
    v = {ten: 0 for ten in fields_for(Standard.TT200)}
    v.update(
        {
            "loi_nhuan_truoc_thue": 1_934_661_387_220,
            "thue_tndn_hien_hanh": -397_722_415_583,
            "thue_tndn_hoan_lai": 10_894_797_039,
            "loi_nhuan_sau_thue": 1_547_833_768_676,
        }
    )

    # Chỉ đẳng thức thuế mới nói được gì ở đây; các đẳng thức khác lệch vì bộ
    # số dựng tay này để trống phần còn lại của B01 và B02.
    dang_thuc_thue = next(
        r for r in kiem_dang_thuc(v, Standard.TT200) if "thuế hiện hành" in r.mo_ta
    )
    assert dang_thuc_thue.trang_thai == DAT
    assert _dau(v)["thue_tndn_hoan_lai"] == DAU_DAT


def test_thieu_thanh_phan_thi_bao_CHUA_QUYET_DINH_DUOC_chu_khong_bao_dat():
    """
    Cùng lý do mà đẳng thức thiếu thành phần được báo riêng: coi một phép
    kiểm không chạy được là một phép kiểm đã qua là cách âm thầm cấp giấy
    thông hành cho đúng chỗ đang nghi ngờ.
    """
    v = {ten: 0 for ten in fields_for(Standard.TT200)}
    v.update(
        {
            "gia_von_hang_ban": None,
            "thue_tndn_hien_hanh": -20,
            "loi_nhuan_truoc_thue": None,
            "loi_nhuan_sau_thue": 80,
        }
    )

    dat = _dau(v)
    assert dat["thue_tndn_hien_hanh"] == CHUA_QUYET_DINH_DUOC
    assert dat["thue_tndn_hoan_lai"] == DAU_DAT
    # Ô chưa gõ là trạng thái RIÊNG, không gộp vào ca nghi sai dấu: không có
    # số thì không có dấu để mà sai.
    assert dat["gia_von_hang_ban"] == CHUA_GO


def test_bo_so_DGC_that_da_tung_lot_qua_muoi_mot_lan_kiem_dang_thuc():
    """
    Hồi quy trên ca đã xảy ra thật, chép từ B02 của `DGC_2025Q2_TT200`.

    Bộ số này chép đúng từng chữ số trên báo cáo nhưng sai dấu ở mã 11 và
    mã 51, nên hai đẳng thức B02 lệch. File gold khi đó có
    `so_lan_kiem_dang_thuc` bằng 11: người gán nhãn kiểm mười một lần mà
    không tìm ra, vì không có lỗi đọc nào để tìm. Phép kiểm dấu tồn tại để
    lần sau câu trả lời hiện ra ngay lần kiểm đầu.
    """
    v = {ten: 0 for ten in fields_for(Standard.TT200)}
    v.update(
        {
            "doanh_thu_thuan": 196_237_282_225,
            "gia_von_hang_ban": -107_515_846_476,
            "loi_nhuan_gop": 88_721_435_749,
            "ln_thuan_hdkd": 628_952_962_840,
            "ln_khac": -83_660_312,
            "loi_nhuan_truoc_thue": 628_869_302_528,
            "thue_tndn_hien_hanh": 23_554_373_035,
            "thue_tndn_hoan_lai": 0,
            "loi_nhuan_sau_thue": 605_314_929_493,
        }
    )

    dat = _dau(v)
    assert dat["gia_von_hang_ban"] == NGHI_SAI_DAU
    assert dat["thue_tndn_hien_hanh"] == NGHI_SAI_DAU

    # Mức lệch đúng bằng GẤP ĐÔI trường bị đảo dấu — chữ ký số học của lỗi
    # dấu, thứ tách nó khỏi ca báo cáo tự mâu thuẫn.
    lech = {r.mo_ta: r.lech for r in kiem_dang_thuc(v, Standard.TT200) if r.trang_thai == LECH}
    assert set(lech.values()) == {-2 * 107_515_846_476, 2 * 23_554_373_035}

    # Đảo dấu theo mục 3.3 thì mọi đẳng thức cân, không phải đổi chữ số nào.
    v["gia_von_hang_ban"] = 107_515_846_476
    v["thue_tndn_hien_hanh"] = -23_554_373_035
    assert all(r.trang_thai == DAT for r in kiem_dang_thuc(v, Standard.TT200))
    assert all(t == DAU_DAT for t in _dau(v).values())
