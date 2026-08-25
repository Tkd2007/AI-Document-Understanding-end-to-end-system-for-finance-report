"""
Test sinh tập ứng viên sửa lỗi.

Điều đáng bảo vệ nhất ở đây không phải "sinh đủ ứng viên" mà là TẬP ỨNG
VIÊN ĐÓNG: mọi giá trị đi ra phải truy được về một nguồn cụ thể trên tài
liệu. Nếu có đường nào để một con số không thuộc tập ứng viên lọt vào kết
quả thì luận điểm chống bịa của cả nghiên cứu sụp — bộ tối ưu sẽ luôn tìm
được nghiệm thoả ràng buộc, kể cả khi nghiệm đó là bịa.

Chạy được mà không cần OCR hay mạng: ô lân cận truyền vào dưới dạng đã
OCR sẵn.
"""

import pytest

from extraction_types import FieldResult
from repair.candidates import (
    BAC_SCALE,
    MAX_UNG_VIEN,
    Candidate,
    generate,
    tu_dau,
    tu_nham_chu_so,
    tu_o_lan_can,
    tu_phieu_vlm,
    tu_scale,
)


def _gia_tri(ung_vien: list[Candidate]) -> set:
    return {uv.value for uv in ung_vien}


# --- Từng nguồn --------------------------------------------------------------


def test_scale_sinh_dung_sau_ung_vien():
    """Ba bậc nghìn/triệu/tỷ theo cả hai chiều."""
    ung_vien = tu_scale(1_000_000_000)

    assert len(ung_vien) == len(BAC_SCALE) == 6
    assert _gia_tri(ung_vien) == {
        1_000_000_000 * 10**3,
        1_000_000_000 * 10**6,
        1_000_000_000 * 10**9,
        1_000_000,
        1_000,
        1,
    }


def test_scale_khong_sinh_ung_vien_khong_chia_het():
    """
    Chia không hết nghĩa là bậc đó không thể là cách đọc thay thế của con
    số này. Sinh ra một giá trị thập phân ở đây sẽ kéo sai số dấu phẩy
    động vào phép kiểm đẳng thức, vốn đang chạy với dung sai 1e-7.
    """
    ung_vien = tu_scale(1_234_567)

    assert all(isinstance(uv.value, int) for uv in ung_vien)
    assert 1_234_567 // 10**6 not in _gia_tri(ung_vien)


def test_dau_sinh_dung_mot_ung_vien():
    ung_vien = tu_dau(1_234_567)

    assert len(ung_vien) == 1
    assert ung_vien[0].value == -1_234_567


def test_dau_khong_sinh_gi_cho_so_0():
    assert tu_dau(0) == []


def test_nham_chu_so_chi_thay_MOT_chu_so():
    """
    Hai chữ số cùng sai trong một con số là chuyện hiếm hơn hẳn, và cho
    phép nó sẽ làm không gian ứng viên phình theo bình phương — mà bước
    chẩn đoán ở C2 là NP-hard nên nó chậm theo.
    """
    ung_vien = tu_nham_chu_so(18)

    # Suy từ sáu cặp đầu của ma trận đã đo, tra theo CHIỀU NGƯỢC:
    #   đọc ra "1" → thật có thể là "7"  (cặp 7→1)  → 78
    #   đọc ra "8" → thật có thể là "0"  (cặp 0→8)  → 10
    # Con số cụ thể ở đây neo vào ma trận đã đóng băng trong
    # src/nham_chu_so.py. Đo lại ma trận thì test này đỏ, và đỏ là ĐÚNG:
    # đổi ma trận là đổi hành vi của phương pháp, phải có người xem lại chứ
    # không được trôi qua im lặng.
    assert _gia_tri(ung_vien) == {78, 10}


def test_nham_chu_so_khong_sinh_so_bat_dau_bang_0():
    ung_vien = tu_nham_chu_so(85)

    assert all(uv.value >= 10 for uv in ung_vien)


def test_nham_chu_so_giu_dau_am():
    ung_vien = tu_nham_chu_so(-18)

    assert _gia_tri(ung_vien) == {-78, -10}


def test_nham_chu_so_tra_theo_CHIEU_NGUOC_khong_phai_chieu_xuoi():
    """
    Ma trận nhầm KHÔNG đối xứng, nên tra nhầm chiều cho tập khác hẳn.

    Cặp áp đảo là `9→0`: chữ số thật 9 bị OCR đọc thành 0, quan sát 23 lần,
    trong khi `0→9` không lần nào. Hàm này chỉ thấy con số ĐÃ ĐỌC RA, nên:

      đọc ra "0"  →  phải đề xuất "9"      (chiều đúng)
      đọc ra "9"  →  KHÔNG được đề xuất "0" (chiều sai)

    Nếu ai đó tra xuôi ở đây thì mọi thứ vẫn chạy, ứng viên vẫn sinh đủ số
    lượng, độ phủ vẫn ra một con số trông hợp lý — chỉ có điều bộ sinh đi
    tìm sai chữ số và không bao giờ trúng. Test này là thứ duy nhất bắt
    được chuyện đó.
    """
    # 40 đọc ra "0" ở vị trí cuối → thật có thể là 49 (9 bị đọc thành 0).
    assert 49 in _gia_tri(tu_nham_chu_so(40))

    # 49 đọc ra "9" → KHÔNG được đề xuất 40, vì không ai đọc 0 thành 9.
    assert 40 not in _gia_tri(tu_nham_chu_so(49))


def test_so_cap_ung_vien_khop_tran_moi_nguon():
    """
    N_CAP_UNG_VIEN phải bằng MAX_MOI_NGUON, và đó không phải trùng hợp.

    Con số 6 được chọn vì nó là trần số ứng viên mà nguồn `ocr_alt` được
    đóng góp cho mỗi chỉ tiêu — hằng số có từ khi C1 ra đời, TRƯỚC mọi phép
    đo ma trận. Chính vì thế độ phủ 0,933 là kết quả suy ra từ số đo chứ
    không phải tham số ai đặt sau khi nhìn kết quả.

    Để hai con số trôi khỏi nhau là làm mất lập luận đó, và đăng ký trước
    mất theo.
    """
    from nham_chu_so import N_CAP_UNG_VIEN
    from repair.candidates import MAX_MOI_NGUON

    assert N_CAP_UNG_VIEN == MAX_MOI_NGUON


def test_o_lan_can_giu_lai_bbox_lam_bang_chung():
    """
    bbox đi vào certificate của kết quả cuối: người đọc phải biết con số đã
    sửa đến từ ô nào trên trang.
    """
    ung_vien = tu_o_lan_can([(5_393_002_084_291, (10, 20, 30, 40))])

    assert ung_vien[0].evidence["bbox"] == (10, 20, 30, 40)


def test_phieu_vlm_sinh_ung_vien_tu_gia_tri_thua_phieu():
    """
    Model đã đọc ra những con số này rồi, chỉ là chúng không thắng. Gần như
    miễn phí nếu đã chạy k mẫu.
    """
    ung_vien = tu_phieu_vlm({"100": 3, "200": 2}, gia_tri_thang=100)

    assert _gia_tri(ung_vien) == {200}


def test_phieu_vlm_bo_qua_gia_tri_thang_va_null():
    ung_vien = tu_phieu_vlm({"100": 3, "None": 1, "200": 1}, gia_tri_thang=100)

    assert _gia_tri(ung_vien) == {200}


def test_nhieu_phieu_hon_thi_cost_thap_hon():
    """
    Một giá trị được 2/5 mẫu ủng hộ hợp lý hơn hẳn một giá trị chỉ 1/5, và
    bước chẩn đoán phải thấy được khác biệt đó qua cost.
    """
    ung_vien = tu_phieu_vlm({"100": 2, "200": 2, "300": 1}, gia_tri_thang=100)
    theo_gia_tri = {uv.value: uv.cost for uv in ung_vien}

    assert theo_gia_tri[200] < theo_gia_tri[300]


# --- Gộp, khử trùng, cắt trần -------------------------------------------------


def test_khu_trung_theo_gia_tri_giu_ung_vien_re_nhat():
    """
    Với bước chẩn đoán thì hai ứng viên cùng con số là cùng MỘT lựa chọn.
    Để cả hai chỉ làm không gian tìm kiếm phình mà không thêm lựa chọn nào.
    """
    # 100 sinh ra được cả từ ô lân cận lẫn từ phiếu VLM
    ung_vien = generate("tong_tai_san", 500, o_lan_can=[(100, (0, 0, 1, 1))], votes={"100": 1})

    trung = [uv for uv in ung_vien if uv.value == 100]

    assert len(trung) == 1
    assert trung[0].source == "neighbor_cell"   # rẻ hơn vlm_vote


def test_khong_sinh_ung_vien_trung_gia_tri_hien_tai():
    """Trả về đúng con số đang có thì không phải là một phương án SỬA."""
    ung_vien = generate("tong_tai_san", 100, o_lan_can=[(100, (0, 0, 1, 1))])

    assert 100 not in _gia_tri(ung_vien)


def test_ton_trong_tran_so_ung_vien():
    """
    Trần phải có: bước chẩn đoán ở C2 là NP-hard và số ứng viên mỗi trường
    vào thẳng cơ số của không gian tìm kiếm.
    """
    lan_can = [(i, (0, 0, 1, 1)) for i in range(1, 60)]

    ung_vien = generate("tong_tai_san", 13_217_639_635_987, o_lan_can=lan_can)

    assert len(ung_vien) <= MAX_UNG_VIEN


def test_nguon_dong_khong_chiem_het_cho_cua_nguon_khac():
    """
    TEST BẢO VỆ TÍNH ĐA DẠNG CỦA TẬP ỨNG VIÊN.

    Một con số 14 chữ số sinh ra hàng chục biến thể nhầm chữ số, tất cả
    đều rẻ hơn mọi ứng viên scale. Xếp thuần theo cost sẽ để chúng chiếm
    hết trần, mà scale lại đúng là nguồn bắt chế độ lỗi mà ràng buộc kế
    toán CHỨNG MINH ĐƯỢC là không bao giờ phát hiện nổi.
    """
    ung_vien = generate("tong_tai_san", 13_217_639_635_987)
    cac_nguon = {uv.source for uv in ung_vien}

    assert "scale" in cac_nguon
    assert "sign" in cac_nguon
    assert "ocr_alt" in cac_nguon


def test_ket_qua_xep_theo_cost_tang_dan():
    ung_vien = generate("tong_tai_san", 13_217_639_635_987)
    cac_cost = [uv.cost for uv in ung_vien]

    assert cac_cost == sorted(cac_cost)


def test_ket_qua_tat_dinh():
    """
    Cùng đầu vào phải cho cùng đầu ra tới từng phần tử, nếu không thì thí
    nghiệm không tái lập được.
    """
    lan_can = [(i, (0, 0, 1, 1)) for i in range(1, 20)]

    lan_1 = generate("tong_tai_san", 999_999, o_lan_can=lan_can)
    lan_2 = generate("tong_tai_san", 999_999, o_lan_can=lan_can)

    assert lan_1 == lan_2


def test_nhan_ca_FieldResult_lan_so_tran():
    """
    Các baseline đối chứng chạy trên giá trị trần, không có confidence.
    Bắt chúng gói vào FieldResult chỉ để gọi được hàm này là thêm nghi
    thức mà không thêm thông tin.
    """
    tu_so_tran = generate("tong_tai_san", 100)
    tu_field_result = generate("tong_tai_san", FieldResult(value=100, confidence=1.0))

    assert tu_so_tran == tu_field_result


def test_gia_tri_none_thi_khong_co_ung_vien_nao():
    """
    Không đọc được thì không có gì để sửa. Đây là lỗi ỒN và cách xử lý là
    đọc lại hoặc đẩy cho người, không phải đoán.
    """
    assert generate("tong_tai_san", None) == []


def test_khong_truyen_o_lan_can_thi_tat_nguon_gia_tri_nhat():
    """
    Chốt lại rằng đây là một quyết định về CHI PHÍ chứ không phải mặc định
    êm ái: ô lân cận đòi OCR toàn vùng bảng, và nó là nguồn duy nhất bắt
    được lỗi lệch dòng / lệch cột.
    """
    ung_vien = generate("tong_tai_san", 13_217_639_635_987)

    assert all(uv.source != "neighbor_cell" for uv in ung_vien)


def test_cost_la_am_log_xac_suat_nen_cong_duoc():
    """
    Cộng cost tương đương nhân xác suất, nên bước chẩn đoán tối thiểu hoá
    TỔNG cost chính là tìm tổ hợp sửa có khả năng nhất — chứ không phải tổ
    hợp ít thay đổi nhất một cách tuỳ tiện.
    """
    ung_vien = generate("tong_tai_san", 18)
    theo_nguon = {uv.source: uv.cost for uv in ung_vien}

    assert theo_nguon["ocr_alt"] < theo_nguon["sign"] < theo_nguon["scale"]
    assert all(cost > 0 for cost in theo_nguon.values())


def test_moi_ung_vien_deu_truy_duoc_ve_mot_nguon():
    """
    Luận điểm chống bịa đứng trên đúng chuyện này: mọi giá trị trong không
    gian sửa phải đến từ một chỗ cụ thể trên tài liệu hoặc từ một mẫu model
    đã đọc thật. Một ứng viên không có nguồn là một con số bịa.
    """
    ung_vien = generate(
        "tong_tai_san",
        FieldResult(value=13_217_639_635_987, confidence=0.6, votes={"13217639635987": 3}),
        o_lan_can=[(5_393_002_084_291, (10, 20, 30, 40))],
    )

    assert ung_vien
    for uv in ung_vien:
        assert uv.source in {"ocr_alt", "neighbor_cell", "sign", "scale", "vlm_vote"}
        assert uv.evidence != {} or uv.source == "sign"


@pytest.mark.parametrize("gia_tri", [1, 18, 999, 1_234_567, 13_217_639_635_987])
def test_khong_bao_gio_vuot_tran_du_gia_tri_the_nao(gia_tri):
    assert len(generate("tong_tai_san", gia_tri)) <= MAX_UNG_VIEN
