"""
Test các kịch bản mở rộng bộ ràng buộc.

Bộ đẳng thức trong `constraints_scenarios.py` đã đối chiếu nguyên văn Công
báo, nên con số của từng kịch bản là con số thật chứ không còn là ước lượng.
Test ở đây chốt hai lớp.

Lớp thứ nhất — **định luật**, thứ quyết định hướng đi của cả H0:

    Chỉ tiêu LÁ — xuất hiện trong đúng một đẳng thức, cùng với anh em của
    mình — không bao giờ định vị được, bất kể thêm bao nhiêu chỉ tiêu.

Lớp thứ hai — **tỷ lệ trao đổi giữa các bước**, thứ quyết định chi tiêu:
thêm một chỉ tiêu mua được bao nhiêu chỉ tiêu định vị được. Lớp này gồm cả
một test chốt lại một kết luận ĐÃ BỊ BÁC BỎ, để nó không quay lại — xem
`test_lien_ket_cheo_KHONG_hieu_qua_hon_phan_ra`.

Nếu một ngày test đỏ vì một chỉ tiêu lá bỗng định vị được, hoặc vì tỷ lệ
trao đổi đổi chiều, thì hoặc `single_field_localizable` đã hỏng, hoặc ai đó
vừa thêm một đẳng thức KHÔNG có trong văn bản — cả hai đều là chuyện phải
biết chứ không phải chuyện sửa test cho xanh.
"""

from constraints import build_matrix, single_field_localizable
from constraints_scenarios import KICH_BAN, KetQua, KichBan, bang_markdown, do


def _theo_ma() -> dict[str, KichBan]:
    return {kb.ma: kb for kb in KICH_BAN}


def test_kich_ban_a_khop_voi_bao_cao_moc_1():
    """
    Kịch bản A phải tái lập đúng con số mà `constraints.py` báo ở Mốc 1:
    3 đẳng thức, hạng 3, 8 chiều lỗi vô hình, 1/11 định vị được. Lệch đi
    nghĩa là hai đường tính ra hai kết quả khác nhau, và khi đó không biết
    tin đường nào.
    """
    kq = do(_theo_ma()["A"])

    assert kq.n_dang_thuc == 3
    assert kq.hang == 3
    assert kq.dim_null == 8
    assert kq.dinh_vi_duoc == ["tong_tai_san"]
    assert kq.minimal_set is None


def test_chi_tieu_la_khong_bao_gio_dinh_vi_duoc():
    """
    Định luật trung tâm. `hang_ton_kho` là ví dụ đắt nhất: nó đúng là chỉ
    tiêu ĐÃ có lỗi đọc thật trên báo cáo VNM, và nó vẫn nằm ngoài tầm ở
    MỌI kịch bản, kể cả kịch bản có liên kết chéo.
    """
    for kb in KICH_BAN:
        assert "hang_ton_kho" in do(kb).khong_dinh_vi_duoc, kb.ma


def test_mot_dang_thuc_don_le_khong_dinh_vi_duoc_chi_tieu_nao():
    """
    Chứng minh trực tiếp nguyên nhân, không qua trung gian.

    Hai chỉ tiêu thành phần có cột BẰNG NHAU từng phần tử, nên đương nhiên
    không phân biệt được. Nhưng chỉ tiêu TỔNG cũng vậy, và đó là phần dễ
    quên: cột của nó là [−1], tỷ lệ với cột [1] của thành phần, nên lỗi
    +δ ở `a` và lỗi −δ ở `tong` cho residual giống hệt nhau. Với một đẳng
    thức đơn lẻ thì cả ba chỉ tiêu đều nằm ngoài tầm.

    Đây là lý do toán học vì sao không thuật toán nào phân biệt được:
    thông tin không tồn tại, chứ không phải thuật toán yếu.
    """
    fields = ["a", "b", "tong"]
    idents = [(["a", "b"], "tong", "a + b = tổng")]

    A, order = build_matrix(fields, idents)

    assert list(A[:, order.index("a")]) == list(A[:, order.index("b")])
    assert single_field_localizable(A, order) == {"a": False, "b": False, "tong": False}


def test_lien_ket_cheo_lam_mot_chi_tieu_dinh_vi_duoc():
    """
    Mặt còn lại của cùng định luật: cho chỉ tiêu xuất hiện trong đẳng thức
    THỨ HAI thì cột của nó tách khỏi cột của anh em, và nó định vị được.
    Đây là toàn bộ lý do vì sao câu hỏi của Mốc 1 phải là "còn liên kết
    chéo nào" chứ không phải "thêm chỉ tiêu nào".
    """
    fields = ["a", "b", "tong", "a_o_bieu_mau_khac"]
    idents = [
        (["a", "b"], "tong", "a + b = tổng"),
        (["a_o_bieu_mau_khac"], "a", "cùng một số, in ở hai biểu mẫu"),
    ]

    A, order = build_matrix(fields, idents)
    dv = single_field_localizable(A, order)

    assert dv["a"] is True
    assert dv["b"] is False


def _ty_le_trao_doi() -> dict[str, float]:
    """Mỗi bước mua được bao nhiêu chỉ tiêu định vị được, trên mỗi chỉ tiêu thêm vào."""
    ket_qua = [do(kb) for kb in KICH_BAN]
    ty_le = {}

    for truoc, sau in zip(ket_qua, ket_qua[1:], strict=False):
        them = sau.n_field - truoc.n_field
        duoc = len(sau.dinh_vi_duoc) - len(truoc.dinh_vi_duoc)
        ty_le[sau.kich_ban.ma] = duoc / them if them else 0.0

    return ty_le


def test_them_tong_nguon_von_la_buoc_re_nhat():
    """
    Phát hiện quyết định của Mốc 1: thêm ĐÚNG MỘT chỉ tiêu — Tổng cộng nguồn
    vốn, mã 440 — mua được một chỉ tiêu định vị được. Tỷ lệ 1,00, cao hơn
    mọi bước khác.

    Nó rẻ vì văn bản khai báo tường minh HAI đẳng thức mà repo đang gộp làm
    một: `Mã số 440 = Mã số 300 + Mã số 400`, và riêng `Tổng cộng Tài sản =
    Tổng cộng Nguồn vốn`. Chỉ tiêu thêm vào lập tức nằm trong hai đẳng thức,
    nên định vị được ngay. Nó còn là con số in ở cuối bảng cân đối, tức rẻ
    cả về chi phí gán nhãn.
    """
    ty_le = _ty_le_trao_doi()

    assert ty_le["B"] == max(ty_le.values())
    assert ty_le["B"] >= 1.0


def test_lien_ket_cheo_KHONG_hieu_qua_hon_phan_ra():
    """
    Chốt lại một kết luận ĐÃ BỊ BÁC BỎ, để nó không quay lại.

    Bản đầu của `constraints_scenarios.py` dùng đẳng thức giả thuyết và kết
    luận liên kết chéo hiệu quả gấp đôi phân rã. Đối chiếu Công báo bác bỏ:
    hai đẳng thức từng được giả định — một liên kết giữa Lợi nhuận chưa phân
    phối trên B01 với Lợi nhuận sau thuế trên B02, và một phân rã Vốn chủ sở
    hữu — KHÔNG có trong văn bản. Với đẳng thức thật, bước liên kết chéo (E)
    cho tỷ lệ THẤP HƠN bước phân rã (D).

    Test này sẽ đỏ nếu ai đó thêm lại một đẳng thức không có trong văn bản.
    """
    ty_le = _ty_le_trao_doi()

    assert ty_le["E"] < ty_le["D"]


def test_khong_kich_ban_nao_dat_duoc_bo_toi_thieu():
    """
    Kết luận phải báo cáo trong bài: với ràng buộc kế toán ĐƠN THUẦN, không
    kịch bản nào làm mọi lỗi một-trường định vị được. Đó là kết quả hợp lệ
    và đáng công bố, nhưng nó dồn trọng số sang mỏ neo đơn vị tính và sang
    việc ĐỌC LẠI — đúng như proposal mục 6.1 đã lường trước.
    """
    assert all(do(kb).minimal_set is None for kb in KICH_BAN)


def test_bang_markdown_neu_du_cot_can_doc():
    bang = bang_markdown([do(kb) for kb in KICH_BAN])

    assert "rank" in bang
    assert "dim null" in bang
    assert "Bước này mua được" in bang
    # Mỗi kịch bản một dòng, cộng hai dòng tiêu đề.
    assert len(bang.splitlines()) == len(KICH_BAN) + 2


def test_ket_qua_rong_khong_no():
    kq = KetQua(kich_ban=KICH_BAN[0], n_field=0, n_dang_thuc=0, hang=0, dim_null=0)

    assert kq.ty_le_dinh_vi == 0.0
