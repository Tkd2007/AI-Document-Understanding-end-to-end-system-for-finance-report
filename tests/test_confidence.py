"""
Test self-consistency: gọi VLM k lần rồi lấy tỷ lệ đồng thuận làm confidence.

Chạy được mà không cần mạng hay API key: call_vlm() bị thay bằng một hàm
giả trả lần lượt các chuỗi cho trước.

Confidence ở đây phục vụ ba việc cùng lúc, nên bộ test phải bảo vệ cả ba:
nó là nhóm so sánh cho H1, là trọng số cho H2, và các giá trị THUA phiếu
chính là tập ứng viên sửa lỗi đầu tiên.
"""

import json

import pytest

import extract_vlm
from extract_vlm import _bo_phieu, extract_fields_from_regions


def _mau(**gia_tri) -> dict:
    """Một mẫu trả về của VLM, các khoá không nêu coi như null."""
    return dict(gia_tri)


def _lap_vlm_gia(monkeypatch, cac_phan_hoi: list):
    """
    call_vlm() trả lần lượt các phản hồi cho trước, hết thì trả None (mô
    phỏng lượt gọi thất bại).

    encode_image_to_base64() cũng bị thay để khỏi cần ảnh thật.
    """
    con_lai = list(cac_phan_hoi)

    def goi_gia(base64_image, prompt, temperature=0.0):
        if not con_lai:
            return None
        phan_hoi = con_lai.pop(0)
        return phan_hoi if isinstance(phan_hoi, str) else json.dumps(phan_hoi)

    monkeypatch.setattr(extract_vlm, "call_vlm", goi_gia)
    monkeypatch.setattr(extract_vlm, "encode_image_to_base64", lambda anh: "")


def _mot_trang():
    return [{"page": 1, "regions": [None]}]


# --- Bỏ phiếu, kiểm ở mức thuật toán -----------------------------------------


def test_bon_tren_nam_mau_dong_thuan_cho_confidence_0_8():
    cac_mau = [_mau(tong_tai_san=100)] * 4 + [_mau(tong_tai_san=200)]

    ket_qua, canh_bao = _bo_phieu(cac_mau, "tong_tai_san", n_samples=5)

    assert ket_qua.value == 100
    assert ket_qua.confidence == pytest.approx(0.8)
    assert canh_bao is None


def test_model_nhat_quan_tra_null_cung_la_mot_ket_qua_co_confidence():
    """
    None là một ỨNG VIÊN bỏ phiếu chứ không phải phiếu trắng. Ba trên năm
    lần trả null là tín hiệu thật — chỉ tiêu này thường không đọc được trên
    ảnh đó — và biến nó thành phiếu trắng sẽ làm confidence của hai lần còn
    lại trông cao giả tạo (2/2 thay vì 2/5).
    """
    cac_mau = [_mau()] * 3 + [_mau(tong_tai_san=100)] * 2

    ket_qua, _ = _bo_phieu(cac_mau, "tong_tai_san", n_samples=5)

    assert ket_qua.value is None
    assert ket_qua.confidence == pytest.approx(0.6)


def test_hoa_phieu_giua_hai_gia_tri_non_null_thi_canh_bao():
    """
    Hoà 2-2 là ca đáng ngờ nhất: model chia đôi giữa hai con số khác nhau,
    tức là nó đang đoán. Phải chọn tất định để tái lập được, và phải nói ra
    rằng đã chọn.
    """
    cac_mau = [_mau(tong_tai_san=100), _mau(tong_tai_san=200)] * 2

    ket_qua, canh_bao = _bo_phieu(cac_mau, "tong_tai_san", n_samples=4)

    assert ket_qua.value == 100          # xuất hiện trước
    assert ket_qua.confidence == pytest.approx(0.5)
    assert canh_bao is not None and "hoà phiếu" in canh_bao


def test_hoa_phieu_thi_uu_tien_gia_tri_non_null_hon_null():
    """
    Hoà giữa null và một con số thì lấy con số: null không mang thông tin
    nào để đi tiếp, còn con số thì ít nhất còn kiểm được bằng ràng buộc.
    """
    cac_mau = [_mau(), _mau(), _mau(tong_tai_san=100), _mau(tong_tai_san=100)]

    ket_qua, _ = _bo_phieu(cac_mau, "tong_tai_san", n_samples=4)

    assert ket_qua.value == 100


def test_votes_giu_du_moi_gia_tri_da_xuat_hien():
    """
    Các giá trị THUA phiếu là nguồn ứng viên sửa lỗi đầu tiên và gần như
    miễn phí ở đây. Vứt đi thì phải gọi lại VLM đúng số lần vừa gọi để có
    lại chúng.
    """
    cac_mau = [_mau(tong_tai_san=100)] * 3 + [_mau(tong_tai_san=200), _mau()]

    ket_qua, _ = _bo_phieu(cac_mau, "tong_tai_san", n_samples=5)

    assert ket_qua.votes == {"100": 3, "200": 1, "None": 1}


def test_luot_goi_that_bai_keo_confidence_xuong():
    """
    Mẫu số là n_samples chứ không phải số mẫu parse được. Một lượt gọi hỏng
    là một lượt KHÔNG CÓ BẰNG CHỨNG, nên nó phải kéo confidence xuống. Lấy
    số mẫu thành công làm mẫu số sẽ cho confidence 1.0 trên một tài liệu mà
    bốn trên năm lần gọi đều thất bại — đúng lúc cần nghi ngờ nhất.
    """
    cac_mau = [_mau(tong_tai_san=100)]   # 4 lượt còn lại hỏng, không vào list

    ket_qua, _ = _bo_phieu(cac_mau, "tong_tai_san", n_samples=5)

    assert ket_qua.value == 100
    assert ket_qua.confidence == pytest.approx(0.2)


def test_khong_mau_nao_dung_duoc_thi_confidence_bang_0():
    ket_qua, canh_bao = _bo_phieu([], "tong_tai_san", n_samples=5)

    assert ket_qua.value is None
    assert ket_qua.confidence == 0.0
    assert canh_bao is None


def test_don_vi_tinh_bo_phieu_tren_chuoi_chu_khong_ep_kieu_so():
    """
    Đơn vị tính là chuỗi. Nếu nó đi qua coerce_number như các chỉ tiêu khác
    thì "triệu đồng" thành None và mỏ neo scale mất tác dụng hoàn toàn.
    """
    cac_mau = [_mau(don_vi_tinh="triệu đồng")] * 3 + [_mau(don_vi_tinh="đồng")]

    ket_qua, _ = _bo_phieu(cac_mau, "don_vi_tinh", n_samples=4)

    assert ket_qua.value == "triệu đồng"
    assert ket_qua.confidence == pytest.approx(0.75)


# --- Mức tích hợp ------------------------------------------------------------


def test_mot_mau_nhiet_do_0_giu_nguyen_hanh_vi_cu(monkeypatch):
    """
    Hồi quy quan trọng nhất: mặc định phải cho hành vi Y HỆT bản trước, để
    mọi thứ đang chạy không vỡ khi thêm self-consistency.

    confidence 1.0 ở đây KHÔNG có nghĩa là chắc chắn — một mẫu duy nhất
    luôn tự đồng thuận với chính nó. Nó có nghĩa là KHÔNG ĐO ĐƯỢC.
    """
    _lap_vlm_gia(monkeypatch, [_mau(tong_tai_san=100, doanh_thu_thuan=50)])

    ket_qua = extract_fields_from_regions(_mot_trang())

    assert ket_qua.values()["tong_tai_san"] == 100
    assert ket_qua.data["tong_tai_san"].confidence == 1.0
    assert ket_qua.n_samples == 1
    assert ket_qua.temperature == 0.0


def test_nhieu_mau_o_nhiet_do_duong_cho_confidence_do_duoc(monkeypatch):
    _lap_vlm_gia(
        monkeypatch,
        [_mau(tong_tai_san=100)] * 4 + [_mau(tong_tai_san=999)],
    )

    ket_qua = extract_fields_from_regions(_mot_trang(), n_samples=5, temperature=0.7)

    assert ket_qua.values()["tong_tai_san"] == 100
    assert ket_qua.data["tong_tai_san"].confidence == pytest.approx(0.8)
    assert ket_qua.data["tong_tai_san"].votes == {"100": 4, "999": 1}


def test_nhieu_mau_o_nhiet_do_0_la_loi_chu_khong_phai_ket_qua_vo_nghia():
    """
    Ở nhiệt độ 0 thì k mẫu giống hệt nhau nên tỷ lệ đồng thuận luôn bằng 1.
    Chạy im lặng sẽ tốn gấp k lần tiền API để lấy về một cột confidence
    hằng số — thứ vô dụng cho H1 mà lại trông như đã đo.
    """
    with pytest.raises(ValueError, match="temperature"):
        extract_fields_from_regions(_mot_trang(), n_samples=5, temperature=0.0)


def test_don_vi_tinh_di_ra_o_meta_chu_khong_lan_vao_data(monkeypatch):
    """
    Mọi hàm hạ nguồn giả định .data chỉ chứa số. Để chuỗi đơn vị lọt vào đó
    là validate_result() ép kiểu nó thành None kèm một cảnh báo sai.
    """
    _lap_vlm_gia(monkeypatch, [_mau(tong_tai_san=100, don_vi_tinh="triệu đồng")])

    ket_qua = extract_fields_from_regions(_mot_trang())

    assert "don_vi_tinh" not in ket_qua.data
    assert ket_qua.meta["don_vi_tinh"] == "triệu đồng"


def test_canh_bao_hoa_phieu_noi_ro_trang_nao(monkeypatch):
    """Cảnh báo phải lần được về trang, nếu không thì không đi dò được."""
    _lap_vlm_gia(
        monkeypatch,
        [_mau(tong_tai_san=100), _mau(tong_tai_san=200)] * 2,
    )

    ket_qua = extract_fields_from_regions(_mot_trang(), n_samples=4, temperature=0.7)

    assert any("Trang 1" in canh_bao for canh_bao in ket_qua.warnings)
