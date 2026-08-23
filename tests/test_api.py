"""
Test tầng HTTP: giới hạn kích thước upload, lọc định dạng, dọn file tạm.

Chạy được không cần mạng và không cần model: route_document() bị thay bằng
hàm giả qua monkeypatch, nên không có PDF nào được convert và không có lời
gọi VLM nào.

api.py gọi require_config() ở MỨC MODULE — đó là chủ ý (fail fast lúc
khởi động service, xem docstring của require_config), nên chỉ cần import
file này là đã đòi có biến môi trường. Vì vậy phải đặt giá trị giả TRƯỚC
lệnh import bên dưới. Giá trị là chuỗi rác cố ý: nếu có test nào lỡ đi tới
lời gọi API thật thì nó phải hỏng ầm ĩ, không được im lặng dùng key thật
trong .env của người chạy test.
"""

import os
from pathlib import Path

os.environ.setdefault("OPENROUTER_API_KEY", "test-khong-dung-that")
os.environ.setdefault("OPENROUTER_MODEL", "test-khong-dung-that")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import api  # noqa: E402
from extraction_types import ExtractionResult, FieldResult  # noqa: E402


@pytest.fixture
def client(monkeypatch, tmp_path):
    """
    TestClient với pipeline bị thay bằng hàm giả và thư mục upload riêng.

    Đổi UPLOAD_DIR sang tmp_path để test không đụng vào data/samples/ thật
    — một test ghi rác vào thư mục dữ liệu của người dùng là test không ai
    dám chạy.
    """
    monkeypatch.setattr(api, "UPLOAD_DIR", tmp_path)

    goi_ham = []

    def route_gia(file_path, save=True):
        goi_ham.append({"file_path": file_path, "save": save})
        return ExtractionResult(
            data={"tong_tai_san": FieldResult(value=100, confidence=1.0)},
            meta={"don_vi_tinh": "đồng", "standard": "TT99", "prompt_hash": "gia"},
            warnings=[],
        )

    monkeypatch.setattr(api, "route_document", route_gia)

    with TestClient(api.app) as c:
        c.goi_ham = goi_ham
        yield c


def test_upload_vuot_tran_bi_tu_choi_413(client, monkeypatch):
    """
    Trần kích thước phải chặn trước khi pipeline chạy, không phải sau.

    Hạ trần xuống 1 KB thay vì gửi 50 MB thật: test phải chạy trong vài
    mili giây, và thứ cần chốt là NHÁNH LOGIC chứ không phải con số.
    """
    monkeypatch.setattr(api, "MAX_UPLOAD_BYTES", 1024)

    r = client.post(
        "/extract",
        files={"file": ("to.pdf", b"x" * 5000, "application/pdf")},
    )

    assert r.status_code == 413
    # Pipeline KHÔNG được chạy. Nếu nó chạy thì trần chỉ là trang trí:
    # công việc nặng đã tốn rồi mới báo lỗi.
    assert client.goi_ham == []


def test_upload_vuot_tran_khong_de_lai_file_do(client, monkeypatch, tmp_path):
    """
    Để lại nửa file thì lần sau gặp một PDF cụt và lỗi hiện ra tận trong
    pdf2image, cách xa nguyên nhân thật.
    """
    monkeypatch.setattr(api, "MAX_UPLOAD_BYTES", 1024)

    client.post("/extract", files={"file": ("to.pdf", b"x" * 5000, "application/pdf")})

    assert list(tmp_path.iterdir()) == []


def test_upload_dung_tran_thi_qua(client, monkeypatch):
    """Ranh giới: đúng bằng trần là hợp lệ, chỉ vượt mới bị chặn."""
    monkeypatch.setattr(api, "MAX_UPLOAD_BYTES", 1024)

    r = client.post(
        "/extract",
        files={"file": ("vua.pdf", b"x" * 1024, "application/pdf")},
    )

    assert r.status_code == 200
    assert len(client.goi_ham) == 1


def test_duong_api_khong_ghi_file_ket_qua(client):
    """
    save=False cho đường API.

    Dữ liệu đã có ở response HTTP và metrics.jsonl; file thứ ba mang hậu
    tố ngẫu nhiên của request nên không tra cứu được, chỉ để lại rác.
    """
    r = client.post("/extract", files={"file": ("a.pdf", b"noi dung", "application/pdf")})

    assert r.status_code == 200
    assert client.goi_ham[0]["save"] is False


def test_file_tam_bi_xoa_sau_khi_xong(client, tmp_path):
    """Không xoá thì data/samples/ phình vô hạn theo số request."""
    client.post("/extract", files={"file": ("a.pdf", b"noi dung", "application/pdf")})

    assert list(tmp_path.iterdir()) == []


def test_file_tam_bi_xoa_ca_khi_pipeline_nem_loi(client, monkeypatch, tmp_path):
    """Đúng những lượt chạy HỎNG mới là lượt hay để lại rác nhất."""
    def route_no(file_path, save=True):
        raise RuntimeError("pipeline hỏng")

    monkeypatch.setattr(api, "route_document", route_no)

    with pytest.raises(RuntimeError):
        client.post("/extract", files={"file": ("a.pdf", b"x", "application/pdf")})

    assert list(tmp_path.iterdir()) == []


def test_dinh_dang_khong_ho_tro_bi_tu_choi(client):
    r = client.post("/extract", files={"file": ("a.exe", b"MZ", "application/octet-stream")})

    assert r.status_code == 400
    assert client.goi_ham == []


def test_ten_file_path_traversal_khong_thoat_ra_ngoai(client, tmp_path):
    """
    Tên file là dữ liệu do client kiểm soát, không bao giờ được tin.

    Chốt rằng file được ghi TRONG tmp_path chứ không leo lên thư mục cha.
    """
    r = client.post(
        "/extract",
        files={"file": ("../../../thoat.pdf", b"x", "application/pdf")},
    )

    assert r.status_code == 200
    duong_dan = Path(client.goi_ham[0]["file_path"])
    assert duong_dan.resolve().parent == tmp_path.resolve()


def test_metrics_tra_ve_dang_prometheus(client):
    r = client.get("/metrics")

    assert r.status_code == 200
    # Ba counter phải có sẵn từ lượt scrape đầu tiên, kể cả khi chưa có
    # lượt chạy nào — nếu không thì alert dựng trên rate() không bao giờ
    # bắn. Xem chú thích _totals trong metrics.py.
    assert "doc_ai_documents_total" in r.text
    assert "doc_ai_documents_error_total" in r.text
