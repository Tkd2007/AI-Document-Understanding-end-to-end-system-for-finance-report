"""
BASELINE 9-THUẦN — thay thẳng giá trị donor, không giải phương trình.

VÌ SAO HÀM NÀY TỒN TẠI, và vì sao phần lớn test dưới đây là test PHÂN BIỆT nó
với bản chiếu chứ không phải test nó chạy được. Lượt thử 10 tài liệu ngày
04/09/2026 cho thấy `diagnose_fellegi_holt_donor()` hầu như không dùng số
donor: nó chiếu donor lên không gian nghiệm, nên khi ràng buộc xác định nghiệm
duy nhất thì donor không đóng góp gì và hai phe của H3 ra kết quả trùng khít
tới từng chữ số. Bản thuần là bản duy nhất trong hai bản mà giá trị điền ra
THẬT SỰ đến từ tổng thể, tức bản duy nhất đo được câu hỏi của H3.

Nếu một thay đổi nào đó làm bản thuần lặng lẽ hành xử như bản chiếu thì đối
chứng trung tâm của cả nghiên cứu biến mất mà bảng điểm vẫn đẹp. Đó là thứ
những test này canh.
"""

import numpy as np
import pytest

from repair.diagnose import (
    diagnose_fellegi_holt_donor,
    diagnose_fellegi_holt_donor_thuan,
)

# Một đẳng thức duy nhất, hình dạng của tổng tài sản: a + b - c = 0.
THU_TU = ["a", "b", "c"]
A_MOT = np.array([[1.0, 1.0, -1.0]])


def test_dien_DUNG_gia_tri_donor_chu_khong_giai_phuong_trinh():
    """
    Chốt lõi: giá trị ghi ra phải BẰNG CHÍNH donor, không phải nghiệm gần donor.
    """
    do = diagnose_fellegi_holt_donor_thuan(
        {"a": 1.0, "b": 2.0, "c": 10.0}, A_MOT, THU_TU, {"c": 3.0},
    )

    assert do.verdict == "REPAIRED"
    assert set(do.changed_fields) == {"c"}
    assert do.changed_fields["c"].value == 3.0


def test_donor_khong_can_bang_thi_BO_CUOC_chu_khong_nan_cho_vua():
    """
    Đây là chỗ hai bản tách hẳn nhau, và là lý do bản thuần được viết ra.

    Cùng một đầu vào: bản chiếu SỬA được vì nó kéo donor về nghiệm gần nhất,
    bản thuần BỎ CUỘC vì số donor thật sự không làm bảng cân đối khớp. Một
    ngày nào đó bản thuần cũng đi sửa được ở ca này thì nó đã âm thầm biến
    thành bản chiếu, và H3 mất đối chứng.
    """
    gia_tri = {"a": 1.0, "b": 2.0, "c": 10.0}
    donor = {"a": 50.0, "b": 60.0, "c": 99.0}

    thuan = diagnose_fellegi_holt_donor_thuan(gia_tri, A_MOT, THU_TU, donor)
    assert thuan.verdict == "ABSTAIN"

    chieu = diagnose_fellegi_holt_donor(
        gia_tri, {k: [v] for k, v in donor.items()}, A_MOT, THU_TU,
        donor_values=donor,
    )
    assert chieu.verdict == "REPAIRED"


def test_truong_KHONG_co_donor_thi_khong_bao_gio_bi_dung_toi():
    """
    Không có donor thì không có gì để thay vào. Nếu trường ấy vẫn lọt vào tổ
    hợp thì hàm đang lấy giá trị từ chỗ khác — mà nguồn giá trị chính là biến
    số duy nhất H3 đem so.
    """
    do = diagnose_fellegi_holt_donor_thuan(
        {"a": 1.0, "b": 2.0, "c": 10.0}, A_MOT, THU_TU, {"a": 4.0},
    )

    # Chỉ `a` có donor, mà thay a=4 thì 4+2-10 vẫn khác 0.
    assert do.verdict == "ABSTAIN"
    assert do.changed_fields == {}


def test_bo_so_da_can_thi_VERIFIED_va_khong_dong_gi():
    do = diagnose_fellegi_holt_donor_thuan(
        {"a": 4.0, "b": 6.0, "c": 10.0}, A_MOT, THU_TU, {"c": 999.0},
    )

    assert do.verdict == "VERIFIED"
    assert do.changed_fields == {}


def test_nhieu_tap_cung_thoa_thi_chon_tap_THAY_DOI_IT_NHAT():
    """
    Nguyên tắc minimum change của chính Fellegi-Holt, và cũng là tiêu chí
    `diagnose()` dùng cho ứng viên đọc từ tài liệu — hai phe phải phân xử
    giống nhau thì khác biệt còn lại mới đúng bằng một biến số là nguồn giá
    trị.

    `b` đứng TRƯỚC trong `field_order` nên vòng duyệt tổ hợp gặp nó trước.
    Trả về tập đầu tiên gặp được sẽ chọn `b`; phân xử đúng phải chọn `a` vì
    nó thay đổi ít hơn (3 so với 6).
    """
    thu_tu = ["b", "a", "c"]
    A = np.array([[1.0, 2.0, -1.0]])  # b + 2a - c = 0
    gia_tri = {"b": 2.0, "a": 1.0, "c": 10.0}
    donor = {"b": 8.0, "a": 4.0}

    do = diagnose_fellegi_holt_donor_thuan(gia_tri, A, thu_tu, donor)

    assert do.verdict == "REPAIRED"
    assert set(do.changed_fields) == {"a"}
    assert do.changed_fields["a"].value == 4.0


def test_thieu_gia_tri_thi_bo_cuoc_co_ma_ly_do_rieng():
    """
    `thieu_gia_tri` phải tách khỏi `vo_nghiem`: một bên là không kiểm được,
    một bên là đã kiểm và không có nghiệm. Gộp hai thứ đó vào bảng kết quả là
    khai sai baseline bỏ cuộc vì lý do gì.
    """
    do = diagnose_fellegi_holt_donor_thuan(
        {"a": 1.0, "b": None, "c": 10.0}, A_MOT, THU_TU, {"c": 3.0},
    )

    assert do.verdict == "ABSTAIN"
    assert do.ma_ly_do == "thieu_gia_tri"


def test_nguon_ung_vien_ghi_ro_la_donor_thuan():
    """Bảng điểm phải phân biệt được ba nguồn giá trị, không để suy ra ngầm."""
    do = diagnose_fellegi_holt_donor_thuan(
        {"a": 1.0, "b": 2.0, "c": 10.0}, A_MOT, THU_TU, {"c": 3.0},
    )

    assert do.changed_fields["c"].source == "donor_thuan"
    assert do.changed_fields["c"].evidence["donor"] == pytest.approx(3.0)
