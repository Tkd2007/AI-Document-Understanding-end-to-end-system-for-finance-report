"""
Phép dò nhãn gold không cân.

Công cụ này canh ĐÁP ÁN chứ không canh pipeline, nên nếu nó hỏng thì hỏng im
lặng hoàn toàn: nó chỉ báo "không có tài liệu nào lệch", mà đó cũng đúng là
câu ta muốn nghe. Vì vậy test phải chốt cả hai chiều — bắt được lệch thật, và
không bắt oan bộ số cân.

Ngưỡng tách "lệch thật" khỏi "lệch cỡ làm tròn" cũng được chốt ở đây: gộp hai
loại làm một là mất khả năng đọc bảng, vì chúng đòi hai cách xử lý khác hẳn.
"""

import numpy as np

from constraints import build_matrix
from eval.do_lech_gold import NGUONG_LAM_TRON
from fields_config import QuyUocDau, Standard, identities_for


def _phan_du(gia_tri: dict, chuan: Standard, quy_uoc: QuyUocDau) -> np.ndarray:
    co = [k for k, v in gia_tri.items() if v is not None]
    A, order = build_matrix(co, identities_for(chuan, quy_uoc))
    x = np.array([gia_tri[k] for k in order], float)
    return A @ x


def _bo_so_can() -> dict:
    """Bốn dòng của đẳng thức mã 60 ở quy ước TRỪ: 1000 − 300 − 50 = 650."""
    return {
        "loi_nhuan_truoc_thue": 1_000.0,
        "thue_tndn_hien_hanh": 300.0,
        "thue_tndn_hoan_lai": 50.0,
        "loi_nhuan_sau_thue": 650.0,
    }


def test_bo_so_can_thi_phan_du_bang_khong():
    r = _phan_du(_bo_so_can(), Standard.TT200, QuyUocDau.TRU)

    assert r.size == 1
    assert abs(r[0]) < 1


def test_lech_mot_dong_thi_phan_du_bang_dung_luong_lech():
    """
    Phần dư phải bằng CHÍNH lượng lệch, vì đó là thứ bảng tra in ra cho người
    đối chiếu tay. Lệch dấu hay lệch hệ số ở đây làm bảng chỉ sai chỗ.
    """
    sai = {**_bo_so_can(), "loi_nhuan_sau_thue": 650.0 + 42.0}
    r = _phan_du(sai, Standard.TT200, QuyUocDau.TRU)

    assert abs(abs(r[0]) - 42.0) < 1e-6


def test_nguong_tach_dung_hai_nhom_da_do_duoc():
    """
    Chốt ngưỡng bằng chính hai số đo ngày 05/09/2026 kẹp hai bên nó: nhóm làm
    tròn lớn nhất là 1 triệu đồng, nhóm lệch thật nhỏ nhất là 51,7 triệu
    (`PVD_2023Q4`). Ngưỡng phải nằm giữa hai con số ấy.

    Nếu một ngày ai đó chỉnh ngưỡng ra ngoài khoảng này thì hoặc bốn tài liệu
    lệch thật biến mất khỏi bảng, hoặc hai chục chỗ làm tròn tràn vào — cả hai
    đều làm bảng không đọc được nữa.
    """
    assert 1_000_000 < NGUONG_LAM_TRON < 51_772_851
