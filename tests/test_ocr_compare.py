"""
Test bộ đo engine OCR trên ô số.

Chạy được không cần mạng và không cần model: mọi test dùng engine GIẢ — một
hàm nhận ảnh trả chuỗi. Đó chính là lý do `EngineOCR` được định nghĩa hẹp
lại thành `Callable[[Image.Image], str]` thay vì nhận nguyên đối tượng
reader của một thư viện cụ thể.

Phần đáng test nhất không phải phép tính Levenshtein — nó là quy hoạch động
sách giáo khoa — mà là hai quyết định dễ làm sai theo hướng lạc quan:
chuẩn hoá KHÔNG được sửa giúp OCR, và "đọc gần đúng" KHÔNG được tính là
đọc đúng con số.
"""

from PIL import Image

from eval.ocr_compare import (
    BIEN_THE_ANH,
    KetQuaEngine,
    KetQuaO,
    bang_markdown,
    bang_nham_chu_so,
    cat_o,
    chuan_hoa_so,
    do_chinh_xac_levenshtein,
    do_mot_bang,
    khoang_cach_levenshtein,
    so_sanh_engine,
    thong_ke_nham_chu_so,
)
from eval.xbrl_tier.render import render
from eval.xbrl_tier.table import FinancialTable


def _bang() -> FinancialTable:
    return FinancialTable(
        doc_id="THU-0001",
        concepts=["Assets", "Liabilities", "Equity"],
        labels={
            "Assets": "Total assets",
            "Liabilities": "Total liabilities",
            "Equity": "Total equity",
        },
        periods=["2025-12-31", "2024-12-31"],
        values={
            "Assets": {"2025-12-31": 5393002.0, "2024-12-31": 4812445.0},
            "Liabilities": {"2025-12-31": -1200000.0, "2024-12-31": None},
            "Equity": {"2025-12-31": 4193002.0, "2024-12-31": 3900000.0},
        },
    )


def _engine_hoan_hao(rendered):
    """
    Engine đọc đúng tuyệt đối, tra ngược từ chính chuỗi đã vẽ.

    Ảnh crop không mang khoá ô theo, nên hàm giả này trả chuỗi theo THỨ TỰ
    gọi. Thứ tự đó phải khớp đúng thứ tự `do_mot_bang` duyệt, nghĩa là
    phải bỏ ô trống y như nó bỏ — bản đầu không lọc và lệch nhịp ngay từ ô
    trống đầu tiên, làm engine "hoàn hảo" đọc sai mọi ô sau đó.
    """
    thu_tu = [
        chuoi
        for khoa in rendered.bboxes
        if chuan_hoa_so(chuoi := rendered.texts[khoa]) is not None
    ]
    dem = {"i": 0}

    def engine(anh):
        chuoi = thu_tu[dem["i"] % len(thu_tu)]
        dem["i"] += 1
        return chuoi

    return engine


# --- Levenshtein -----------------------------------------------------------


def test_khoang_cach_tren_vi_du_tinh_tay():
    """Ba phép thay: k->s, i->i(giữ), tten->tting. Ví dụ kinh điển."""
    assert khoang_cach_levenshtein("kitten", "sitting") == 3


def test_khoang_cach_bang_0_khi_giong_het():
    assert khoang_cach_levenshtein("1,234,567", "1,234,567") == 0


def test_khoang_cach_voi_chuoi_rong_la_do_dai_chuoi_kia():
    assert khoang_cach_levenshtein("", "123") == 3
    assert khoang_cach_levenshtein("123", "") == 3


def test_do_chinh_xac_chuan_hoa_theo_chuoi_dai_hon():
    """
    Chia cho chuỗi THẬT thì engine đọc ra rác dài gấp ba sẽ bị chặn về 0 và
    mất phân biệt với engine không đọc ra gì. Chia cho chuỗi dài hơn thì
    hai ca đó khác nhau.
    """
    im_lang = do_chinh_xac_levenshtein("123", "")
    rac_dai = do_chinh_xac_levenshtein("123", "abcdefghi")

    assert im_lang == 0.0
    assert 0.0 <= rac_dai < 1.0


def test_do_chinh_xac_hai_chuoi_rong_la_khop_hoan_toan():
    assert do_chinh_xac_levenshtein("", "") == 1.0


def test_mot_chu_so_sai_van_cho_do_chinh_xac_cao():
    """
    Chốt đúng cái bẫy mà `khop_gia_tri` sinh ra để chống: `5.393.002` đọc
    thành `5.898.002` cho Levenshtein accuracy rất cao, nghe như gần đúng,
    nhưng con số thì sai hoàn toàn.
    """
    assert do_chinh_xac_levenshtein("5,393,002", "5,898,002") > 0.75


# --- Chuẩn hoá số ----------------------------------------------------------


def test_bo_dau_phan_nhom_nghin():
    assert chuan_hoa_so("1,234,567") == 1234567.0


def test_ngoac_don_la_so_am():
    """Đúng cách báo cáo tài chính in số âm, và là nguồn của lỗi mất dấu."""
    assert chuan_hoa_so("(1,234,567)") == -1234567.0


def test_o_trong_khong_ra_so():
    assert chuan_hoa_so("-") is None
    assert chuan_hoa_so("") is None
    assert chuan_hoa_so("   ") is None


def test_khong_sua_giup_cac_cap_ocr_hay_nham():
    """
    Quyết định thiết kế quan trọng nhất của module. Nếu `l23` được hiểu
    thành 123 thì ta đang đo một engine ĐÃ ĐƯỢC VÁ chứ không phải đo
    engine, và con số sẽ nói dối theo hướng lạc quan.
    """
    assert chuan_hoa_so("l23") is None
    assert chuan_hoa_so("O00") is None
    assert chuan_hoa_so("S6") is None


def test_dau_tru_cung_duoc_hieu_la_am():
    """Engine có thể đọc ngoặc thành dấu trừ; đó vẫn là đọc đúng DẤU."""
    assert chuan_hoa_so("-1,234") == -1234.0


# --- Đo trên bảng đã render ------------------------------------------------


def test_engine_doc_dung_thi_khop_het():
    rendered = render(_bang())
    kq = do_mot_bang(rendered, _engine_hoan_hao(rendered), "gia", "sach")

    assert kq.n_o > 0
    assert kq.do_chinh_xac_levenshtein == 1.0
    assert kq.ty_le_khop_gia_tri == 1.0
    assert kq.ty_le_khong_ra_so == 0.0


def test_o_trong_bi_loai_khoi_phep_do():
    """
    Bảng thử có đúng một ô None. "Engine đọc được dấu gạch không" không
    phải câu hỏi đang hỏi, và để nó trong phép đo thì một bảng nhiều ô
    trống sẽ đẩy con số đi mà không nói gì về khả năng đọc chữ số.
    """
    rendered = render(_bang())

    kq = do_mot_bang(rendered, lambda anh: "0", "gia", "sach")

    assert len(rendered.bboxes) == 6
    assert kq.n_o == 5


def test_doc_khong_ra_so_tach_rieng_khoi_doc_sai_so():
    """
    Phân biệt trung tâm của cả đề tài: không ra số là lỗi ỒN — hệ biết
    mình thất bại và fallback được. Ra một số SAI là lỗi CÂM — không tín
    hiệu nào báo, và lỗi lan xuống mọi tỷ số tài chính. Gộp hai thứ vào
    một con số là xoá mất phân biệt đó.
    """
    rendered = render(_bang())

    im_lang = do_mot_bang(rendered, lambda anh: "", "gia", "sach")
    cam = do_mot_bang(rendered, lambda anh: "999", "gia", "sach")

    assert im_lang.ty_le_khong_ra_so == 1.0
    assert im_lang.ty_le_khop_gia_tri == 0.0

    assert cam.ty_le_khong_ra_so == 0.0
    assert cam.ty_le_khop_gia_tri == 0.0


def test_doc_gan_dung_van_khong_tinh_la_khop_gia_tri():
    """Một chữ số sai không phải là "gần đúng" với một con số tài chính."""
    o = KetQuaO(
        concept="Assets",
        period="2025-12-31",
        chuoi_that="5,393,002",
        chuoi_doc_duoc="5,898,002",
        do_chinh_xac=do_chinh_xac_levenshtein("5,393,002", "5,898,002"),
        khop_chuoi=False,
        gia_tri_that=5393002.0,
        gia_tri_doc_duoc=5898002.0,
    )

    assert o.do_chinh_xac > 0.75
    assert o.khop_gia_tri is False


def test_cat_o_noi_them_dem_va_clamp_ve_trong_anh():
    """
    Cắt sát mép làm cụt nét chữ ở biên, và khi đó ta đo lỗi của phép cắt
    chứ không phải lỗi của engine.
    """
    anh = Image.new("RGB", (100, 100))

    trong = cat_o(anh, (20, 20, 40, 40), dem=5)
    sat_goc = cat_o(anh, (0, 0, 10, 10), dem=5)

    assert trong.size == (30, 30)
    assert sat_goc.size == (15, 15)


# --- Biến thể ảnh ----------------------------------------------------------


def test_moi_bien_the_deu_giu_nguyen_kich_thuoc_anh():
    """
    Đổi kích thước thì bbox trỏ sai ô, và phép đo lặng lẽ so chuỗi của ô
    này với ảnh của ô khác.
    """
    anh = Image.new("RGB", (120, 90), "white")

    for ten, ham in BIEN_THE_ANH.items():
        assert ham(anh).size == (120, 90), ten


def test_bien_the_nhieu_lap_lai_duoc():
    """
    Một biến thể ảnh khác nhau giữa hai lần chạy là một bộ dữ liệu khác
    nhau, và khi đó hai con số đo được không so với nhau được.
    """
    anh = Image.new("RGB", (40, 30), "white")

    a = BIEN_THE_ANH["nhieu"](anh)
    b = BIEN_THE_ANH["nhieu"](anh)

    assert a.tobytes() == b.tobytes()


def test_bien_the_xuong_cap_that_su_doi_anh():
    """Nếu một biến thể không đổi gì thì nó là một cột giả trong bảng."""
    goc = render(_bang()).image

    for ten in ("mo", "nhieu", "phan_giai_thap"):
        assert BIEN_THE_ANH[ten](goc).convert("RGB").tobytes() != goc.tobytes(), ten


# --- Gộp và trình bày ------------------------------------------------------


def test_so_sanh_engine_chay_moi_engine_tren_moi_bien_the():
    cac_bang = [render(_bang()), render(_bang())]

    ket_qua = so_sanh_engine(
        cac_bang,
        engines={"a": lambda anh: "1", "b": lambda anh: "2"},
        cac_bien_the=("sach", "mo"),
    )

    assert len(ket_qua) == 4
    assert {(kq.ten_engine, kq.bien_the_anh) for kq in ket_qua} == {
        ("a", "sach"),
        ("a", "mo"),
        ("b", "sach"),
        ("b", "mo"),
    }
    # Hai bảng gộp lại nên N phải gấp đôi N của một bảng.
    assert all(kq.n_o == 10 for kq in ket_qua)


def test_bang_markdown_neu_n_that_cua_chinh_no():
    """
    Danh mục kiểm ở ADDENDUM mục 10: mọi bảng phải nêu N THẬT của nó — ở
    đây là số Ô, không phải số bảng.
    """
    kq = KetQuaEngine(
        ten_engine="easyocr",
        bien_the_anh="sach",
        cac_o=[
            KetQuaO("A", "p", "1", "1", 1.0, True, 1.0, 1.0),
            KetQuaO("B", "p", "2", "3", 0.0, False, 2.0, 3.0),
        ],
    )

    bang = bang_markdown([kq])

    assert "N ô" in bang
    assert "| easyocr | sach | 2 " in bang
    assert "0.500" in bang


def test_ket_qua_rong_khong_no():
    """Bảng không có ô số nào là chuyện có thật, không phải lỗi."""
    kq = KetQuaEngine(ten_engine="x", bien_the_anh="sach", cac_o=[])

    assert kq.do_chinh_xac_levenshtein == 0.0
    assert kq.ty_le_khop_gia_tri == 0.0
    assert kq.ty_le_khong_ra_so == 0.0


# --- Thống kê nhầm chữ số --------------------------------------------------


def _o(chuoi_that: str, chuoi_doc: str) -> KetQuaO:
    return KetQuaO(
        concept="C",
        period="p",
        chuoi_that=chuoi_that,
        chuoi_doc_duoc=chuoi_doc,
        do_chinh_xac=do_chinh_xac_levenshtein(chuoi_that, chuoi_doc),
        khop_chuoi=chuoi_that == chuoi_doc,
        gia_tri_that=chuan_hoa_so(chuoi_that),
        gia_tri_doc_duoc=chuan_hoa_so(chuoi_doc),
    )


def test_dem_dung_cap_chu_so_bi_nham():
    kq = KetQuaEngine(
        ten_engine="x",
        bien_the_anh="phan_giai_thap",
        cac_o=[_o("3,458,566", "3,458,506"), _o("768,220,099", "768,220,000")],
    )

    dem = thong_ke_nham_chu_so([kq])

    # 566 -> 506 là một lần 6->0; 099 -> 000 là hai lần 9->0.
    assert dem[("6", "0")] == 1
    assert dem[("9", "0")] == 2


def test_bo_qua_o_lech_do_dai():
    """
    Độ dài lệch thì căn ký tự nào ứng với ký tự nào là bài toán riêng, và
    đoán bừa sẽ sinh ra những cặp nhầm KHÔNG CÓ THẬT rồi đưa thẳng vào
    taxonomy lỗi — hỏng đúng thứ hàm này sinh ra để phục vụ.
    """
    kq = KetQuaEngine(
        ten_engine="x", bien_the_anh="sach", cac_o=[_o("1,234", "234")]
    )

    assert thong_ke_nham_chu_so([kq]) == {}


def test_khong_dem_dau_phan_nhom_va_ngoac():
    """Chỉ chữ số mới vào taxonomy nhầm CHỮ SỐ."""
    kq = KetQuaEngine(
        ten_engine="x", bien_the_anh="sach", cac_o=[_o("(1,234)", "[1.234]")]
    )

    assert thong_ke_nham_chu_so([kq]) == {}


def test_bang_nham_sap_giam_dan_va_khong_no_khi_rong():
    dem = {("9", "0"): 7, ("6", "0"): 2}

    bang = bang_nham_chu_so(dem)

    assert bang.index("| 9 | 0 | 7 |") < bang.index("| 6 | 0 | 2 |")
    assert "Không quan sát được" in bang_nham_chu_so({})
