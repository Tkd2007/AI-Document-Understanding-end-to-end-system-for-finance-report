"""
Test oracle dò SỰ TỒN TẠI của dòng, tách khỏi việc đọc giá trị.

Đây là nền của phương án phân biệt "dòng vắng mặt trên biểu mẫu" với "dòng
có mà đọc hỏng". Hai ca đó trước đây cùng cho ra `None` trần, và chính sự
nhập nhằng ấy buộc bước kiểm đẳng thức phải bỏ qua CẢ đẳng thức khi thiếu
bất kỳ thành phần nào — làm đẳng thức đắt nhất của Mốc 1 gần như không bao
giờ chạy.

Oracle dò theo MÃ SỐ chứ không theo tên chỉ tiêu, và đó là lựa chọn có số
liệu đằng sau: `data/output/ocr_engine_easyocr.md` đo EasyOCR đạt 0,999
Levenshtein trên ô số, trong khi chỗ nó hỏng là chữ tiếng Việt có dấu
("TỔNG TÀI SẢN" -> "TỖNG TÀISẢN").
"""

from extract_baseline import (
    DauVetDong,
    extract_field_by_code,
    tim_theo_ma_so,
    tong_hop_dau_vet,
)
from fields_config import Standard

# Trang bảng cân đối kiểu OCR trả về: có tiêu đề mẫu biểu, mã số nằm CUỐI
# dòng, giá trị xuống dòng ngay sau. Cố ý KHÔNG có mã 150 (Tài sản sinh học
# ngắn hạn) — đúng như báo cáo VNM, vốn in công thức rút gọn bỏ hẳn mã đó.
TRANG_B01_TT99 = """
BÁO CÁO TÌNH HÌNH TÀI CHÍNH
Mẫu số B 01a - DN
TÀI SẢN NGẮN HẠN                                      100
    29.403.116.984.122
Tiền và các khoản tương đương tiền                     110
    2.000.000.000.000
Đầu tư tài chính ngắn hạn                              120
    17.000.000.000.000
Các khoản phải thu ngắn hạn                            130
    4.500.000.000.000
Hàng tồn kho                                           140
    5.393.002.084.291
Tài sản ngắn hạn khác                                  160
    510.114.899.831
"""

# Cùng trang đó nhưng mã 130 in ra mà không đọc được số (giấy rách, ô mờ).
TRANG_B01_MAT_SO = TRANG_B01_TT99.replace("    4.500.000.000.000\n", "    ....\n")

# Trang thuyết minh: không mang dấu hiệu mẫu biểu B01 nào.
TRANG_THUYET_MINH = """
THUYẾT MINH BÁO CÁO TÀI CHÍNH
Các khoản phải thu ngắn hạn gồm phải thu khách hàng và trả trước người bán.
"""


def _trang_thai(text: str, field_key: str, standard=Standard.TT99) -> str:
    return tim_theo_ma_so(text, field_key, standard).trang_thai


def test_doc_duoc_so_thi_bao_co_gia_tri():
    dau_vet = tim_theo_ma_so(TRANG_B01_TT99, "hang_ton_kho", Standard.TT99)

    assert dau_vet.trang_thai == "co_gia_tri"
    assert dau_vet.gia_tri == 5393002084291


def test_dong_KHONG_CO_tren_bieu_mau_thi_bao_khong_thay_dong():
    """
    Mã 150 (Tài sản sinh học) không in trên trang này vì doanh nghiệp không
    có khoản đó. Đây là ca mà TT99 mục 1.2.3 gọi là "miễn trình bày", tức
    vắng mặt nghĩa là BẰNG KHÔNG chứ không phải chưa biết.
    """
    assert _trang_thai(TRANG_B01_TT99, "tai_san_sinh_hoc_ngan_han") == "khong_thay_dong"


def test_thay_dong_ma_khong_doc_ra_so_thi_bao_rieng():
    """
    Ca này PHẢI khác ca trên. Dòng có trên giấy nên giá trị thật khác 0, và
    gán 0 cho nó sẽ bịa ra một con số rồi đẩy sai lệch sang chỉ tiêu khác
    khi đẳng thức không cân.
    """
    assert _trang_thai(TRANG_B01_MAT_SO, "phai_thu_ngan_han") == "thay_dong_khong_ra_so"


def test_trang_khong_phai_bieu_mau_do_thi_khong_ket_luan_gi():
    """
    Trang thuyết minh không nói được gì về việc mã 150 có tồn tại hay không.
    Nhầm ca này thành "vắng mặt" là gán 0 cho một chỉ tiêu chỉ vì nó không
    xuất hiện ở một trang chẳng liên quan.
    """
    assert _trang_thai(TRANG_THUYET_MINH, "phai_thu_ngan_han") == "khong_thay_mau_bieu"


def test_chi_tieu_khong_thuoc_chuan_thi_bao_khong_khai_bao():
    assert (
        _trang_thai(TRANG_B01_TT99, "tai_san_sinh_hoc_ngan_han", Standard.TT200)
        == "khong_khai_bao"
    )


def test_ma_so_doi_nghia_giua_hai_chuan_khong_bi_tra_nham():
    """
    Mã 160 là Tài sản ngắn hạn khác ở TT99, còn ở TT200 chỉ tiêu đó mang mã
    150. Tra bằng bảng mã TT200 trên một trang TT99 phải KHÔNG ra giá trị
    của mã 160 — nếu ra thì đó đúng là loại lỗi câm mà việc tách bảng mã
    theo chuẩn sinh ra để chặn.
    """
    theo_tt99 = tim_theo_ma_so(TRANG_B01_TT99, "tsnh_khac", Standard.TT99)
    theo_tt200 = tim_theo_ma_so(TRANG_B01_TT99, "tsnh_khac", Standard.TT200)

    assert theo_tt99.gia_tri == 510114899831
    assert theo_tt200.gia_tri != 510114899831


def test_extract_field_by_code_giu_nguyen_hanh_vi_cu():
    """Hàm cũ nay chỉ là lớp mỏng trên oracle — không được đổi kết quả."""
    assert extract_field_by_code(TRANG_B01_TT99, "hang_ton_kho", Standard.TT99) == (
        5393002084291
    )
    assert extract_field_by_code(TRANG_THUYET_MINH, "hang_ton_kho", Standard.TT99) is None


# --- Gộp dấu vết qua nhiều trang ------------------------------------------


def test_gop_uu_tien_trang_doc_duoc_so():
    """Một trang đọc được thì trang khác không được ghi đè thành không biết."""
    gop = tong_hop_dau_vet([
        DauVetDong(None, "khong_thay_mau_bieu"),
        DauVetDong(123, "co_gia_tri"),
        DauVetDong(None, "khong_thay_dong"),
    ])

    assert gop == DauVetDong(123, "co_gia_tri")


def test_gop_uu_tien_doc_hong_hon_vang_mat():
    """
    Thấy dòng ở một trang thì kết luận phải là "có dòng mà đọc hỏng", kể cả
    khi trang khác của cùng mẫu biểu không có mã đó.

    Đây là lớp bảo vệ chống gán 0 nhầm: chỉ cần MỘT trang chứng minh dòng
    tồn tại là đủ để bác bỏ kết luận vắng mặt.
    """
    gop = tong_hop_dau_vet([
        DauVetDong(None, "khong_thay_dong"),
        DauVetDong(None, "thay_dong_khong_ra_so"),
    ])

    assert gop.trang_thai == "thay_dong_khong_ra_so"


def test_chua_duyet_trang_nao_thi_khong_ket_luan_vang_mat():
    """
    Danh sách rỗng nghĩa là chưa có bằng chứng gì. Câu trả lời trung thực
    là "không kết luận được", không phải "dòng vắng mặt" — kết luận sai ở
    đây sẽ gán 0 cho mọi chỉ tiêu của một tài liệu chưa hề được dò.
    """
    assert tong_hop_dau_vet([]).trang_thai == "khong_thay_mau_bieu"


def test_chi_ket_luan_vang_mat_khi_da_thay_bieu_mau():
    """Thấy mẫu biểu mà không trang nào có mã đó -> mới được kết luận vắng."""
    gop = tong_hop_dau_vet([
        DauVetDong(None, "khong_thay_mau_bieu"),
        DauVetDong(None, "khong_thay_dong"),
    ])

    assert gop.trang_thai == "khong_thay_dong"


def test_o_so_khong_doc_duoc_thi_KHONG_muon_so_cua_dong_ke_tiep():
    """
    Hồi quy cho một lỗi câm có thật, đo được trước khi sửa.

    Pattern lấy giá trị từng dùng `(.{0,80}?)` kèm cờ DOTALL, tức dấu chấm
    nuốt cả ký tự xuống dòng. Khi ô số của một chỉ tiêu không đọc được,
    pattern đi tiếp xuống dưới và lấy về giá trị của CHỈ TIÊU KẾ TIẾP: với
    mã 130 bị mờ, hàm trả về đúng con số của mã 140.

    Đây là chế độ lỗi tệ nhất trong cả hệ — một giá trị hợp lệ của một chỉ
    tiêu hoàn toàn khác, không cảnh báo, không dấu vết. Nó còn phá luôn
    oracle trạng thái: ca đáng lẽ là "đọc hỏng" bị khai thành "có giá trị".
    """
    hong = tim_theo_ma_so(TRANG_B01_MAT_SO, "phai_thu_ngan_han", Standard.TT99)
    ke_tiep = tim_theo_ma_so(TRANG_B01_MAT_SO, "hang_ton_kho", Standard.TT99)

    assert hong.gia_tri is None
    assert hong.gia_tri != ke_tiep.gia_tri
    assert ke_tiep.gia_tri == 5393002084291, "Dòng kế tiếp vẫn phải đọc được như thường"
