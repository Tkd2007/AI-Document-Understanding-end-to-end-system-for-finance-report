"""
Luật 1 được cưỡng chế bằng CẤU TRÚC, không bằng lời nhắc trong tài liệu.

`ANNOTATION-GUIDELINE.md` Luật 1: người gán nhãn phải mù với đầu ra pipeline
— không mở `data/output/*_routed.json`, không chạy `router.py`, không xem log,
không xem kết quả của bất kỳ model nào trên tài liệu đang gán nhãn. Guideline
gọi đây là "luật quan trọng nhất và cũng là luật dễ vi phạm nhất khi làm một
mình cho nhanh".

VÌ SAO PHẢI CÓ TEST CHỨ KHÔNG CHỈ CÓ DOCSTRING: vi phạm luật này không làm
gì nổ và không để lại dấu vết. Một tính năng "điền sẵn cho nhanh" thêm vào
sáu tháng nữa sẽ trông như một cải tiến hiển nhiên — nó tiết kiệm hàng chục
giờ — trong khi nó âm thầm huỷ giá trị của toàn bộ tập gold, vì ground truth
nhiễm đúng bằng lỗi mà nó sinh ra để đo. Lúc đó không ai còn nhớ vì sao
không được làm vậy, và cũng không có cách nào phát hiện ngược lại từ dữ liệu.

Test đọc mã nguồn thay vì chạy nó, vì thứ cần chặn là sự TỒN TẠI của đường
dẫn tới pipeline, không phải một lần gọi cụ thể.
"""

import ast
from pathlib import Path

import pytest

THU_MUC = Path(__file__).resolve().parents[1] / "src" / "gan_nhan"

# Module thuộc đường trích xuất. Import bất kỳ cái nào cũng là mở đường cho
# con số của model đi vào màn hình người gán nhãn.
CAM_IMPORT = {
    "router",
    "extract_vlm",
    "extract_baseline",
    "ocr_baseline",
    "layout_detection",
    "repair",
    "repair.diagnose",
    "repair.candidates",
    "api",
}

CAC_FILE_PY = sorted(THU_MUC.glob("*.py"))


def test_co_du_file_de_kiem():
    """Chặn ca test xanh vì glob không khớp gì — im lặng mà vô dụng."""
    assert len(CAC_FILE_PY) >= 4


@pytest.mark.parametrize("duong_dan", CAC_FILE_PY, ids=lambda p: p.name)
def test_khong_import_bat_ky_module_nao_cua_duong_trich_xuat(duong_dan):
    cay = ast.parse(duong_dan.read_text(encoding="utf-8"))

    da_import = set()
    for nut in ast.walk(cay):
        if isinstance(nut, ast.Import):
            da_import.update(a.name for a in nut.names)
        elif isinstance(nut, ast.ImportFrom) and nut.module:
            da_import.add(nut.module)

    pham = {ten for ten in da_import if ten.split(".")[0] in CAM_IMPORT}

    assert not pham, (
        f"{duong_dan.name} import {sorted(pham)} — vi phạm Luật 1 của "
        f"ANNOTATION-GUIDELINE.md. Công cụ gán nhãn không được có đường dẫn "
        f"nào tới đầu ra pipeline."
    )


def _chuoi_trong_ma_thuc_thi(cay: ast.AST):
    """
    Mọi chuỗi trong mã, TRỪ docstring — và chú thích thì AST đã bỏ sẵn.

    Phải lọc như vậy vì chính các docstring của gói `gan_nhan` nhắc tới
    `data/output/` để GIẢI THÍCH lệnh cấm. Quét thô cả file sẽ bắt đúng
    những dòng đang bảo vệ luật, và cách sửa hiển nhiên khi đó là xoá lời
    giải thích đi — tức test lại đẩy người ta làm điều ngược với ý nó.
    """
    docstring = {
        d
        for nut in ast.walk(cay)
        if isinstance(nut, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
        for d in [ast.get_docstring(nut, clean=False)]
        if d is not None
    }
    return [
        nut.value
        for nut in ast.walk(cay)
        if isinstance(nut, ast.Constant)
        and isinstance(nut.value, str)
        and nut.value not in docstring
    ]


@pytest.mark.parametrize("duong_dan", CAC_FILE_PY, ids=lambda p: p.name)
def test_khong_cham_thu_muc_dau_ra_pipeline(duong_dan):
    """
    `data/output/` là nơi chứa kết quả của mọi model. Không đường dẫn nào
    trong mã thực thi của gói này được trỏ tới đó.
    """
    cay = ast.parse(duong_dan.read_text(encoding="utf-8"))

    pham = [
        chuoi
        for chuoi in _chuoi_trong_ma_thuc_thi(cay)
        if "data/output" in chuoi or "data\\output" in chuoi
    ]

    assert not pham, f"{duong_dan.name} trỏ tới {pham} — vi phạm Luật 1"


def test_giao_dien_cung_phai_mu_voi_dau_ra_pipeline():
    """Phần chạy trên trình duyệt cũng phải mù, không chỉ phần chạy trên máy chủ."""
    html = (THU_MUC / "giao_dien.html").read_text(encoding="utf-8")

    for cam in ("data/output", "routed", "/api/extract", "metrics.jsonl"):
        assert cam not in html, f"giao_dien.html nhắc tới {cam!r} — vi phạm Luật 1"
