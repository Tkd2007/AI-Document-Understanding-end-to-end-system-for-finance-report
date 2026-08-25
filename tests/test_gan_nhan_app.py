"""
Test máy chủ gán nhãn — tập trung vào những chỗ nó TỪ CHỐI ghi.

Phần dựng ảnh và phần vẽ giao diện không test ở đây: hỏng thì người gán nhãn
thấy ngay trong hai giây. Phần đáng test là các đường từ chối, vì hỏng ở đó
nghĩa là một file gold thiếu sót được ghi ra trông y hệt một file đầy đủ, và
không ai phát hiện cho tới lúc phân tích kết quả cuối.
"""

import json

import pytest
from fastapi.testclient import TestClient

from eval.schema import GroundTruthDoc
from fields_config import Standard, fields_for
from gan_nhan import app as mod
from gan_nhan.kiem import O_NGUOI_PHAI_TICK


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Máy chủ ghi vào thư mục tạm, không đụng `data/gold/` thật."""
    monkeypatch.setattr(mod, "GOLD_DIR", tmp_path / "gold")
    monkeypatch.setattr(mod, "THU_MUC_PDF", tmp_path / "pdf")
    (tmp_path / "pdf").mkdir()
    monkeypatch.setattr(GroundTruthDoc, "save", lambda tu: _ghi(tu, tmp_path / "gold"))
    return TestClient(mod.app)


def _ghi(ban_ghi, thu_muc):
    thu_muc.mkdir(parents=True, exist_ok=True)
    duong_dan = thu_muc / f"{ban_ghi.doc_id}.json"
    duong_dan.write_text(ban_ghi.to_json(), encoding="utf-8")
    return duong_dan


def _than(**doi):
    than = {
        "doc_id": "TEST_2026Q1_TT99",
        "ticker": "TEST",
        "period": "2026Q1",
        "standard": "TT99",
        "unit_declared": "Đơn vị tính: VND",
        "values": dict.fromkeys(fields_for(Standard.TT99), "0"),
        "source_url": "https://example.vn/bctc.pdf",
        "downloaded_at": "2026-08-25",
        "annotator": "nguoi_kiem_thu",
        "danh_muc_kiem": dict.fromkeys(O_NGUOI_PHAI_TICK, True),
    }
    than.update(doi)
    return than


def test_bo_chi_tieu_xep_theo_ma_so_chu_khong_theo_thu_tu_khai_bao(client):
    """
    Người gán nhãn đọc dọc theo tờ giấy, mà mã số tăng dần đúng bằng thứ tự
    dòng in trên biểu mẫu. Bắt họ nhảy qua nhảy lại giữa biểu mẫu và biểu
    nhập chính là nguồn lỗi lệch dòng — chế độ lỗi mà cả nghiên cứu đang đo.
    """
    d = client.get("/api/chi-tieu", params={"chuan": "TT99"}).json()

    assert [n["bieu_mau"] for n in d["nhom"]] == ["B01", "B02", "B03"]
    for nhom in d["nhom"]:
        ma_so = [int(c["ma_so"]) for c in nhom["chi_tieu"]]
        assert ma_so == sorted(ma_so)


def test_chuan_khong_hop_le_bi_tu_choi_thay_vi_lui_ve_mac_dinh(client):
    """
    Lùi về chuẩn mặc định ở đây sẽ cho ra một file gold gắn nhãn sai chuẩn mà
    không dấu hiệu nào — và nhận diện sai chuẩn vốn là một chế độ lỗi riêng
    mà nghiên cứu này phải đo được, không phải thứ tự tay tạo thêm.
    """
    assert client.get("/api/chi-tieu", params={"chuan": "TT_KHONG_CO"}).status_code == 400


def test_tu_choi_ghi_khi_danh_muc_kiem_chua_du(client):
    r = client.post("/api/luu", json=_than(danh_muc_kiem={}))

    assert r.status_code == 400
    assert r.json()["detail"]["loi"] == "danh_muc_kiem_chua_du"
    assert set(r.json()["detail"]["con_thieu"]) == set(O_NGUOI_PHAI_TICK)


def test_tu_choi_ghi_khi_con_o_chua_go(client):
    """
    Ô chưa gõ KHÔNG được lặng lẽ thành `null`. `null` trong tập gold có nghĩa
    hẹp là "có dòng mà đọc không ra"; biến ô bỏ quên thành `null` là tự tay
    khai rằng đã xem xét và chịu.
    """
    gia_tri = dict.fromkeys(fields_for(Standard.TT99), "0")
    gia_tri["hang_ton_kho"] = ""

    r = client.post("/api/luu", json=_than(values=gia_tri))

    assert r.status_code == 400
    assert r.json()["detail"] == {"loi": "o_khong_doc_duoc", "o": ["hang_ton_kho"]}


def test_tu_choi_ghi_khi_khong_doc_duoc_don_vi_va_chi_dan_dung_guideline(client):
    """
    Guideline mục 3.1 cấm suy hệ số đơn vị từ độ lớn con số, vì đó chính là
    việc ta muốn đo xem hệ thống làm được không. Máy chủ cũng không được tự
    suy, và thông báo phải nhắc đúng lối thoát hợp lệ.
    """
    r = client.post("/api/luu", json=_than(unit_declared="đơn vị bịa"))

    assert r.status_code == 400
    assert r.json()["detail"]["loi"] == "khong_doc_duoc_don_vi"
    assert "3.1" in r.json()["detail"]["chi_dan"]


def test_ghi_thanh_cong_thi_gia_tri_da_quy_ve_dong(client, tmp_path):
    gia_tri = dict.fromkeys(fields_for(Standard.TT99), "0")
    gia_tri["tong_tai_san"] = "29.403"

    r = client.post(
        "/api/luu", json=_than(unit_declared="Đơn vị tính: triệu đồng", values=gia_tri)
    )

    assert r.status_code == 200
    ghi = json.loads((tmp_path / "gold" / "TEST_2026Q1_TT99.json").read_text(encoding="utf-8"))
    assert ghi["unit_multiplier"] == 1_000_000
    assert ghi["values"]["tong_tai_san"] == 29_403_000_000


def test_dau_vet_kiem_toan_di_vao_file_gold(client, tmp_path):
    """
    Số lần kiểm đẳng thức và việc có sửa giá trị sau khi kiểm phải được GHI.

    Công cụ cho phép kiểm đẳng thức trên chính số người vừa gõ, nên rủi ro
    sửa một chữ số cho cân là có thật. Guideline mục 8 cấm việc đó nhưng lời
    cấm không tự kiểm chứng được; ghi lại dấu vết biến rủi ro thành đo được.
    """
    r = client.post("/api/luu", json=_than(so_lan_kiem=3, sua_sau_khi_kiem=True))

    assert r.status_code == 200
    ghi = json.loads((tmp_path / "gold" / "TEST_2026Q1_TT99.json").read_text(encoding="utf-8"))
    assert ghi["so_lan_kiem_dang_thuc"] == 3
    assert ghi["sua_gia_tri_sau_khi_kiem"] is True


def test_kiem_khong_tra_ve_gia_tri_de_nghi_qua_HTTP(client):
    """
    Ràng buộc chống-mớm-đáp-án phải giữ ở CẢ tầng HTTP, không chỉ ở hàm
    thuần. Thêm một khoá tiện tay vào đây là đủ để mớm đáp án cho người gán
    nhãn, dù `kiem_dang_thuc()` vẫn sạch.
    """
    gia_tri = dict.fromkeys(fields_for(Standard.TT99), "0")
    gia_tri["tai_san_ngan_han"] = "100"

    d = client.post(
        "/api/kiem",
        json={"standard": "TT99", "values": gia_tri, "unit_declared": "Đơn vị tính: VND"},
    ).json()

    assert set(d) == {"he_so_don_vi", "o_khong_ro", "dang_thuc"}
    for r in d["dang_thuc"]:
        assert set(r) == {"mo_ta", "trang_thai", "lech", "thieu"}
