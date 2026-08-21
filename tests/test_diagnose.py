"""
Test định vị lỗi bằng tìm kiếm min-cardinality trên tập ứng viên.

Test quan trọng nhất là test_khong_bao_gio_tra_ve_gia_tri_ngoai_tap_ung_vien.
Nó bảo vệ luận điểm cốt lõi của cả nghiên cứu: nếu có đường nào để một con
số không thuộc tập ứng viên lọt vào kết quả thì phương pháp này ép số được,
và toàn bộ lập luận chống bịa sụp.

Ví dụ dùng xuyên suốt là a + b = c, đủ nhỏ để kiểm mọi khẳng định bằng mắt.
"""

import numpy as np
import pytest

from repair.candidates import Candidate
from repair.diagnose import (
    diagnose,
    diagnose_fellegi_holt_donor,
    diagnose_l1_continuous,
)

A = np.array([[1.0, 1.0, -1.0]])
THU_TU = ["a", "b", "c"]


def _uv(gia_tri, cost=1.0, source="ocr_alt") -> Candidate:
    return Candidate(value=gia_tri, source=source, cost=cost)


# --- Đường đi cơ bản ---------------------------------------------------------


def test_residual_da_ve_0_thi_VERIFIED_va_khong_chay_tim_kiem():
    """
    Không chạy tìm kiếm khi không cần. Với 60 tài liệu thì phần lớn là ca
    này, và tìm kiếm NP-hard trên chúng là lãng phí thuần tuý.
    """
    ket_qua = diagnose({"a": 10, "b": 20, "c": 30}, {}, A, THU_TU)

    assert ket_qua.verdict == "VERIFIED"
    assert ket_qua.n_changed == 0


def test_vi_du_tinh_tay_sua_dung_mot_truong():
    """
    Đúng là (10, 20, 30), bị hỏng thành (10, 20, 35). Ứng viên cho c gồm
    30, nên phải sửa ĐÚNG một trường và chọn ĐÚNG c = 30.
    """
    ket_qua = diagnose(
        {"a": 10, "b": 20, "c": 35},
        {"c": [_uv(30), _uv(38)]},
        A,
        THU_TU,
    )

    assert ket_qua.verdict == "REPAIRED"
    assert ket_qua.n_changed == 1
    assert ket_qua.changed_fields["c"].value == 30
    assert np.allclose(ket_qua.residual_after, 0)


def test_khong_ung_vien_nao_khop_thi_ABSTAIN():
    """
    Vô nghiệm là câu trả lời ĐÚNG, không phải lỗi phần mềm. Nó nghĩa là
    không cách đọc nào của tài liệu này làm bảng cân đối được.
    """
    ket_qua = diagnose(
        {"a": 10, "b": 20, "c": 35},
        {"c": [_uv(99), _uv(77)]},
        A,
        THU_TU,
    )

    assert ket_qua.verdict == "ABSTAIN"
    assert ket_qua.changed_fields == {}
    assert "residual" in ket_qua.ly_do_abstain


def test_khong_co_ung_vien_nao_ca_thi_ABSTAIN():
    ket_qua = diagnose({"a": 10, "b": 20, "c": 35}, {}, A, THU_TU)

    assert ket_qua.verdict == "ABSTAIN"


def test_thieu_gia_tri_thi_ABSTAIN_chu_khong_doan():
    """
    Không dựng được vector thì không kiểm được ràng buộc. Đoán bừa giá trị
    thiếu chính là việc module này sinh ra để chống.
    """
    ket_qua = diagnose({"a": 10, "b": None, "c": 35}, {"c": [_uv(30)]}, A, THU_TU)

    assert ket_qua.verdict == "ABSTAIN"
    assert "thiếu giá trị" in ket_qua.ly_do_abstain


# --- Min-cardinality và phân xử ---------------------------------------------


def test_uu_tien_sua_MOT_truong_hon_sua_HAI():
    """
    Cả hai đường đều làm residual về 0, nhưng min-cardinality phải chọn
    đường sửa ít trường hơn. Đây là nguyên lý gốc của Fellegi-Holt: giả
    định ít lỗi hơn thì hợp lý hơn.
    """
    ket_qua = diagnose(
        {"a": 10, "b": 20, "c": 35},
        {
            "c": [_uv(30)],                  # một trường là đủ
            "a": [_uv(15)],                  # hoặc sửa cả a và b
            "b": [_uv(25)],
        },
        A,
        THU_TU,
    )

    assert ket_qua.n_changed == 1


def test_cung_cardinality_thi_phan_xu_bang_cost():
    """
    Hai nghiệm cùng sửa một trường thì chọn cái rẻ hơn — tức cái mà mô hình
    lỗi cho là có khả năng xảy ra hơn.
    """
    ket_qua = diagnose(
        {"a": 10, "b": 20, "c": 35},
        {
            "c": [_uv(30, cost=5.0)],
            "a": [_uv(5, cost=0.1)],         # 5 + 20 = 25, không khớp
            "b": [_uv(15, cost=0.1)],        # 10 + 15 = 25, không khớp
        },
        A,
        THU_TU,
    )

    # Chỉ c = 30 cho nghiệm, nên vẫn phải là c bất kể cost
    assert ket_qua.changed_fields["c"].value == 30


def test_confidence_cao_lam_viec_sua_truong_do_dat_hon():
    """
    Sửa một trường model rất chắc chắn thì "đắt", sửa một trường model
    đang lưỡng lự thì "rẻ". Hai đường cùng cardinality thì confidence phân
    xử.
    """
    ung_vien = {"a": [_uv(15, cost=1.0)], "b": [_uv(25, cost=1.0)]}

    #  a = 15: 15 + 20 = 35 -> khớp.  b = 25: 10 + 25 = 35 -> cũng khớp.
    ket_qua = diagnose(
        {"a": 10, "b": 20, "c": 35},
        ung_vien,
        A,
        THU_TU,
        confidences={"a": 0.95, "b": 0.20},
    )

    assert set(ket_qua.changed_fields) == {"b"}


def test_max_changes_chan_duoc_tim_kiem():
    """
    Trần thay đổi là cách cắt chi phí rẻ hơn nhiều so với đổi bộ giải: bài
    toán NP-hard nhưng nghiệm thực tế gần như luôn là 1-2 trường.
    """
    ket_qua = diagnose(
        {"a": 10, "b": 20, "c": 35},
        {"a": [_uv(12)], "b": [_uv(23)]},    # cần sửa CẢ HAI mới khớp
        A,
        THU_TU,
        max_changes=1,
    )

    assert ket_qua.verdict == "ABSTAIN"


def test_bo_tran_thi_tim_duoc_nghiem_hai_truong():
    ket_qua = diagnose(
        {"a": 10, "b": 20, "c": 35},
        {"a": [_uv(12)], "b": [_uv(23)]},
        A,
        THU_TU,
        max_changes=2,
    )

    assert ket_qua.verdict == "REPAIRED"
    assert ket_qua.n_changed == 2


def test_het_gio_thi_ABSTAIN_chu_khong_treo():
    """
    Một tài liệu không chẩn đoán được trong ngân sách thời gian là một tài
    liệu cần người xem. Treo cả lượt chạy 60 tài liệu vì một ca khó là
    đánh đổi tệ.
    """
    nhieu_ung_vien = {
        ten: [_uv(i * 7 + 1) for i in range(12)] for ten in THU_TU
    }

    ket_qua = diagnose(
        {"a": 10, "b": 20, "c": 35},
        nhieu_ung_vien,
        A,
        THU_TU,
        time_limit_s=0.0,
    )

    assert ket_qua.verdict == "ABSTAIN"
    assert "hết" in ket_qua.ly_do_abstain


# --- Chống bịa ---------------------------------------------------------------


def test_khong_bao_gio_tra_ve_gia_tri_ngoai_tap_ung_vien():
    """
    TEST BẢO VỆ LUẬN ĐIỂM CỐT LÕI. NẾU NÓ ĐỎ THÌ CẢ PAPER SAI.

    Tập ứng viên chỉ có 99 cho c, và 10 + 20 = 30 chứ không phải 99. Hệ
    PHẢI trả ABSTAIN. Nếu nó tự nghĩ ra 30 — con số đúng, dễ thấy, và làm
    residual về 0 hoàn hảo — thì nghĩa là có một đường ép số tồn tại, và
    lập luận "không gian sửa không chứa số bịa" không còn đúng.
    """
    ket_qua = diagnose({"a": 10, "b": 20, "c": 35}, {"c": [_uv(99)]}, A, THU_TU)

    assert ket_qua.verdict == "ABSTAIN"
    assert 30 not in [uv.value for uv in ket_qua.changed_fields.values()]


def test_moi_gia_tri_da_sua_deu_den_tu_tap_ung_vien():
    ung_vien = {"c": [_uv(30), _uv(38)], "a": [_uv(15)]}

    ket_qua = diagnose({"a": 10, "b": 20, "c": 35}, ung_vien, A, THU_TU)

    for ten, da_chon in ket_qua.changed_fields.items():
        assert da_chon in ung_vien[ten]


def test_gia_tri_sau_sua_tra_ve_bo_so_hoan_chinh():
    ket_qua = diagnose({"a": 10, "b": 20, "c": 35}, {"c": [_uv(30)]}, A, THU_TU)

    assert ket_qua.gia_tri_sau_sua({"a": 10, "b": 20, "c": 35}) == {
        "a": 10,
        "b": 20,
        "c": 30,
    }


# --- Baseline 8: L1 liên tục -------------------------------------------------


def test_l1_lien_tuc_luon_tim_duoc_nghiem_khi_he_co_nghiem():
    """
    Điểm YẾU cần đo chứ không phải điểm mạnh: baseline này luôn trả về một
    bộ số cân đối, kể cả khi bộ số đó hoàn toàn bịa. Nó không bao giờ nói
    "tôi không biết".
    """
    ket_qua = diagnose_l1_continuous({"a": 10, "b": 20, "c": 35}, {}, A, THU_TU)

    assert ket_qua.verdict == "REPAIRED"
    assert np.allclose(ket_qua.residual_after, 0, atol=1e-6)


def test_l1_lien_tuc_bo_qua_tap_ung_vien():
    """
    Đó chính là điểm của baseline: nó không cần tài liệu vì nó không đọc
    lại tài liệu. Chữ ký hàm giữ nguyên để đổi phương pháp bằng một cờ.
    """
    khong_ung_vien = diagnose_l1_continuous({"a": 10, "b": 20, "c": 35}, {}, A, THU_TU)
    co_ung_vien = diagnose_l1_continuous(
        {"a": 10, "b": 20, "c": 35}, {"c": [_uv(30)]}, A, THU_TU
    )

    assert khong_ung_vien.n_changed == co_ung_vien.n_changed


def test_l1_lien_tuc_van_VERIFIED_khi_da_khop():
    ket_qua = diagnose_l1_continuous({"a": 10, "b": 20, "c": 30}, {}, A, THU_TU)

    assert ket_qua.verdict == "VERIFIED"


def test_l1_lien_tuc_cho_nghiem_THUA():
    """
    L1 kéo nghiệm về phía thưa, nên với một lỗi một-trường nó không được
    rải sai lệch đều ra cả ba trường. Nếu nó rải đều thì đó là nghiệm L2
    chứ không phải L1, và baseline bị làm yếu một cách âm thầm.
    """
    ket_qua = diagnose_l1_continuous({"a": 10, "b": 20, "c": 35}, {}, A, THU_TU)

    assert ket_qua.n_changed <= 2


# --- Baseline 9: Fellegi-Holt với donor --------------------------------------


def test_donor_sua_duoc_nhung_bang_gia_tri_KHONG_den_tu_tai_lieu():
    """
    THÍ NGHIỆM QUAN TRỌNG NHẤT CỦA CẢ NGHIÊN CỨU, ở dạng nhỏ nhất.

    Cùng ràng buộc, cùng cách chọn trường, khác đúng một biến số: giá trị
    điền vào đến từ phân phối của field trên các tài liệu khác chứ không
    từ ảnh. Nếu baseline này ngang bằng diagnose() trên dữ liệu thật thì
    toàn bộ luận điểm "đọc lại nguồn" sai, và điều kiện phản chứng đó đã
    đăng ký trước.
    """
    ket_qua = diagnose_fellegi_holt_donor(
        {"a": 10, "b": 20, "c": 35},
        {},
        A,
        THU_TU,
        donor_values={"c": 31},
    )

    assert ket_qua.verdict == "REPAIRED"
    assert np.allclose(ket_qua.residual_after, 0, atol=1e-6)


def test_donor_keo_nghiem_ve_phia_gia_tri_donor():
    """
    Chọn bộ giá trị GẦN DONOR NHẤT mà vẫn thoả ràng buộc, chứ không điền
    thô rồi để nó không cân. Điền thô sẽ làm baseline thua oan vì lý do kỹ
    thuật thay vì vì lý do khoa học, và baseline yếu oan thì kết luận về
    phương pháp đề xuất mất giá trị.
    """
    gan = diagnose_fellegi_holt_donor(
        {"a": 10, "b": 20, "c": 35}, {}, A, THU_TU, donor_values={"c": 30}
    )

    assert gan.changed_fields["c"].value == pytest.approx(30)


def test_donor_van_VERIFIED_khi_da_khop():
    ket_qua = diagnose_fellegi_holt_donor({"a": 10, "b": 20, "c": 30}, {}, A, THU_TU)

    assert ket_qua.verdict == "VERIFIED"


def test_donor_ton_trong_max_changes():
    ket_qua = diagnose_fellegi_holt_donor(
        {"a": 10, "b": 20, "c": 35}, {}, A, THU_TU, max_changes=0
    )

    assert ket_qua.verdict == "ABSTAIN"


def test_ba_phuong_phap_cung_chu_ky_de_doi_bang_co():
    """
    Runner thí nghiệm phải đổi phương pháp bằng một cờ, không phải bằng
    một nhánh if. Ràng buộc cùng ngân sách của H3 chỉ cưỡng chế được khi
    ba đường đi qua cùng một chỗ.
    """
    doi_so = ({"a": 10, "b": 20, "c": 35}, {"c": [_uv(30)]}, A, THU_TU)

    for ham in (diagnose, diagnose_l1_continuous, diagnose_fellegi_holt_donor):
        ket_qua = ham(*doi_so)
        assert ket_qua.verdict in {"VERIFIED", "REPAIRED", "ABSTAIN"}
        assert ket_qua.solve_time_s >= 0
