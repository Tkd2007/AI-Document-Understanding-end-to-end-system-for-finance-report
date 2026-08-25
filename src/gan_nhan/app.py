"""
Máy chủ cục bộ cho việc gán nhãn tập gold.

VÌ SAO CÓ CÔNG CỤ NÀY: tập gold là 100 tài liệu × 26–27 chỉ tiêu rải qua BA
biểu mẫu, ước lượng 90–125 giờ công người. Cách làm hiện tại là mở PDF ở một
cửa sổ rồi gõ JSON tay ở cửa sổ khác — chậm nhất ở chỗ lật trang, và dễ sai
nhất ở chỗ gõ tên khoá với đếm số 0.

LUẬT 1 LÀ RÀNG BUỘC THIẾT KẾ CỦA CẢ MODULE, KHÔNG PHẢI LỜI NHẮC. Công cụ này
tuyệt đối không được đọc đầu ra pipeline, không import `router`,
`extract_vlm`, `extract_baseline`, và không chạm `data/output/`. Có test
chặn điều đó ở `tests/test_gan_nhan_mu_voi_pipeline.py` — nếu ai đó về sau
thêm tính năng "điền sẵn cho nhanh" thì test đỏ ngay, vì đó chính là cách
tập gold bị nhiễm mà không ai phát hiện được về sau.

Chạy:
    PYTHONPATH=src python -m uvicorn gan_nhan.app:app --reload --port 8100
rồi mở http://127.0.0.1:8100
"""

import os
import time
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel

from eval.schema import GOLD_DIR, GroundTruthDoc
from fields_config import (
    FIELD_MAP,
    FIELD_RULES,
    Standard,
    fields_for,
    line_codes_for,
    parse_unit,
)
from gan_nhan.kiem import DANH_MUC_KIEM, con_thieu_o_kiem, kiem_dang_thuc
from gan_nhan.so_viet import doc_so, quy_doi
from gan_nhan.trang import PHONG_MAC_DINH, anh_trang, so_trang

# Thư mục chứa PDF cần gán nhãn. Đổi được bằng biến môi trường vì tập gold
# 100 tài liệu sẽ không nằm chung chỗ với vài file mẫu của repo.
THU_MUC_PDF = Path(os.environ.get("GAN_NHAN_PDF_DIR", "data/samples"))

GIAO_DIEN = Path(__file__).parent / "giao_dien.html"

app = FastAPI(title="ViFinKIE — công cụ gán nhãn tập gold")

# Lúc mở tài liệu, theo doc_id. Dùng để đo thời gian gán nhãn thật, thứ mà
# ADDENDUM mục 6 cần để biết giao thức 15 phút một tài liệu còn sống không
# sau khi bộ chỉ tiêu trải qua ba biểu mẫu. Nằm trong bộ nhớ tiến trình nên
# tắt máy chủ là mất — chấp nhận được, vì con số này chỉ có nghĩa cho một
# phiên làm việc liền mạch, còn ghép các phiên đứt quãng lại thì nó đo thời
# gian nghỉ trưa chứ không đo tốc độ đọc.
_bat_dau: dict[str, float] = {}


class YeuCauKiem(BaseModel):
    standard: str
    values: dict[str, str | None]
    unit_declared: str = ""


class YeuCauLuu(BaseModel):
    doc_id: str
    ticker: str
    period: str
    standard: str
    unit_declared: str
    values: dict[str, str | None]
    source_url: str
    downloaded_at: str
    annotator: str
    notes: str = ""
    danh_muc_kiem: dict[str, bool] = {}
    so_lan_kiem: int = 0
    sua_sau_khi_kiem: bool = False


def _chuan(ten: str) -> Standard:
    try:
        return Standard(ten)
    except ValueError:
        raise HTTPException(400, f"Chuẩn không hợp lệ: {ten!r}") from None


def _doc_bo_gia_tri(thoi: dict, chuan: Standard, he_so: int) -> tuple[dict, list[str]]:
    """
    Đổi chuỗi người gõ thành giá trị đã quy về đồng, kèm danh sách ô không rõ.

    Ô `KHONG_RO` được trả riêng chứ không lặng lẽ thành `None`: `None` trong
    tập gold có nghĩa hẹp là "có dòng mà đọc không ra", còn ô người gõ nhầm
    hay bỏ quên là chuyện khác hẳn. Gộp hai thứ đó lại sẽ biến mọi ô bỏ sót
    thành một tuyên bố đã xem xét.
    """
    gia_tri: dict = {}
    khong_ro: list[str] = []

    for ten in fields_for(chuan):
        so, trang_thai = doc_so(thoi.get(ten))
        if trang_thai == "khong_ro":
            khong_ro.append(ten)
            gia_tri[ten] = None
        else:
            gia_tri[ten] = quy_doi(so, he_so)

    return gia_tri, khong_ro


@app.get("/", response_class=HTMLResponse)
def giao_dien() -> str:
    return GIAO_DIEN.read_text(encoding="utf-8")


@app.get("/api/tai-lieu")
def danh_sach_tai_lieu() -> dict:
    """
    PDF trong thư mục làm việc, kèm việc đã có file gold hay chưa.

    Trạng thái `da_gan_nhan` là khoá tường minh chứ không để suy từ việc
    thiếu tên trong một danh sách khác — người gán nhãn cần thấy ngay còn
    bao nhiêu tài liệu, và đó cũng chính là thanh tiến độ của cả việc.
    """
    if not THU_MUC_PDF.is_dir():
        raise HTTPException(500, f"Không có thư mục {THU_MUC_PDF}")

    da_co = {f.stem for f in GOLD_DIR.glob("*.json")} if GOLD_DIR.is_dir() else set()
    tai_lieu = [
        {"ten_file": f.name, "so_trang": so_trang(f)}
        for f in sorted(THU_MUC_PDF.glob("*.pdf"))
    ]
    return {
        "thu_muc": str(THU_MUC_PDF),
        "tai_lieu": tai_lieu,
        "doc_id_da_gan_nhan": sorted(da_co),
        "so_da_xong": len(da_co),
    }


@app.get("/api/trang/{ten_file}/{chi_so}")
def anh_mot_trang(ten_file: str, chi_so: int, phong: float = PHONG_MAC_DINH) -> Response:
    duong_dan = THU_MUC_PDF / Path(ten_file).name
    if not duong_dan.is_file():
        raise HTTPException(404, f"Không có {ten_file}")

    try:
        png = anh_trang(duong_dan, chi_so, phong)
    except IndexError as e:
        raise HTTPException(404, str(e)) from None

    return Response(png, media_type="image/png")


@app.get("/api/chi-tieu")
def bo_chi_tieu(chuan: str) -> dict:
    """
    Bộ chỉ tiêu của một chuẩn, nhóm theo biểu mẫu và xếp theo MÃ SỐ.

    Xếp theo mã số chứ không theo thứ tự khai báo trong `FIELD_MAP`, vì
    người gán nhãn đọc dọc theo tờ giấy — mã số tăng dần đúng bằng thứ tự
    dòng in trên biểu mẫu. Bắt họ nhảy qua nhảy lại giữa biểu mẫu và biểu
    nhập là nguồn lỗi lệch dòng, đúng chế độ lỗi mà cả nghiên cứu đang đo.
    """
    ch = _chuan(chuan)
    ma_so = line_codes_for(ch)

    nhom: dict[str, list] = {}
    for ten in fields_for(ch):
        bieu_mau, ma = ma_so[ten]
        nhom.setdefault(bieu_mau, []).append(
            {
                "ten": ten,
                "nhan": FIELD_MAP[ten],
                "ma_so": ma,
                "cho_phep_am": FIELD_RULES[ten]["allow_negative"],
            }
        )

    for danh_sach in nhom.values():
        danh_sach.sort(key=lambda o: int(o["ma_so"]))

    return {
        "chuan": ch.value,
        "nhom": [{"bieu_mau": bm, "chi_tieu": nhom[bm]} for bm in sorted(nhom)],
        "danh_muc_kiem": [
            {"ma": ma, "mo_ta": mo_ta, "tu_dong": tu_dong}
            for ma, mo_ta, tu_dong in DANH_MUC_KIEM
        ],
    }


@app.post("/api/mo/{doc_id}")
def bat_dau_bam_gio(doc_id: str) -> dict:
    """Bấm giờ từ lúc mở tài liệu. Mở lại cùng một doc_id thì KHÔNG đặt lại."""
    moc = _bat_dau.setdefault(doc_id, time.monotonic())
    return {"doc_id": doc_id, "da_troi_giay": int(time.monotonic() - moc)}


@app.post("/api/kiem")
def kiem(yeu_cau: YeuCauKiem) -> dict:
    """
    Chạy đẳng thức trên số người vừa gõ. KHÔNG bao giờ trả về giá trị đề nghị.

    Trả mức lệch để người biết đi đọc lại dòng nào, và cố ý dừng ở đó. Suy ra
    giá trị đúng thì được — với lỗi đơn định vị được thì ràng buộc chốt luôn
    con số — nhưng đưa con số ấy cho người gán nhãn là biến việc đọc lại
    thành việc điền vào, và tập gold sẽ luôn cân bằng đúng cái cách làm nó
    vô dụng cho việc đo tỷ lệ lỗi thật.
    """
    ch = _chuan(yeu_cau.standard)
    he_so, _ = parse_unit(yeu_cau.unit_declared)
    gia_tri, khong_ro = _doc_bo_gia_tri(yeu_cau.values, ch, he_so or 1)

    return {
        "he_so_don_vi": he_so,
        "o_khong_ro": khong_ro,
        "dang_thuc": [
            {
                "mo_ta": r.mo_ta,
                "trang_thai": r.trang_thai,
                "lech": r.lech,
                "thieu": list(r.thieu),
            }
            for r in kiem_dang_thuc(gia_tri, ch)
        ],
    }


@app.post("/api/luu")
def luu(yeu_cau: YeuCauLuu) -> dict:
    """
    Ghi file gold. Từ chối khi danh mục kiểm của guideline mục 8 chưa đủ.

    Từ chối chứ không cảnh báo rồi vẫn ghi: danh mục kiểm mà bỏ qua được thì
    sau vài chục tài liệu sẽ luôn bị bỏ qua, và mục 8 thành trang trí.
    """
    thieu_o = con_thieu_o_kiem(yeu_cau.danh_muc_kiem)
    if thieu_o:
        raise HTTPException(400, {"loi": "danh_muc_kiem_chua_du", "con_thieu": thieu_o})

    ch = _chuan(yeu_cau.standard)
    he_so, _ = parse_unit(yeu_cau.unit_declared)
    if he_so is None:
        raise HTTPException(
            400,
            {
                "loi": "khong_doc_duoc_don_vi",
                "chi_dan": "Guideline mục 3.1: không tìm thấy dòng khai báo thì để trống "
                "unit_declared và ghi lý do vào notes. ĐỪNG suy hệ số từ độ lớn con số.",
            },
        )

    gia_tri, khong_ro = _doc_bo_gia_tri(yeu_cau.values, ch, he_so)
    if khong_ro:
        raise HTTPException(400, {"loi": "o_khong_doc_duoc", "o": khong_ro})

    moc = _bat_dau.get(yeu_cau.doc_id)
    ban_ghi = GroundTruthDoc(
        doc_id=yeu_cau.doc_id,
        ticker=yeu_cau.ticker,
        period=yeu_cau.period,
        standard=ch.value,
        unit_declared=yeu_cau.unit_declared,
        unit_multiplier=he_so,
        values=gia_tri,
        source_url=yeu_cau.source_url,
        downloaded_at=yeu_cau.downloaded_at,
        annotator=yeu_cau.annotator,
        annotated_at=datetime.now(UTC).isoformat(),
        notes=yeu_cau.notes,
        thoi_gian_giay=int(time.monotonic() - moc) if moc else 0,
        so_lan_kiem_dang_thuc=yeu_cau.so_lan_kiem,
        sua_gia_tri_sau_khi_kiem=yeu_cau.sua_sau_khi_kiem,
    )
    duong_dan = ban_ghi.save()
    _bat_dau.pop(yeu_cau.doc_id, None)

    return {"da_ghi": str(duong_dan), "thoi_gian_giay": ban_ghi.thoi_gian_giay}
