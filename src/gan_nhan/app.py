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
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from eval.schema import GOLD_DIR, GroundTruthDoc
from fields_config import (
    FIELD_MAP,
    FIELD_RULES,
    Standard,
    fields_for,
    line_codes_for,
    parse_unit,
)
from gan_nhan.kiem import (
    DANH_MUC_KIEM,
    con_thieu_o_kiem,
    kiem_dang_thuc,
    kiem_dau_khau_tru,
)
from gan_nhan.so_viet import doc_so, quy_doi
from gan_nhan.trang import PHONG_MAC_DINH, anh_trang, so_trang

# Thư mục chứa PDF cần gán nhãn. Đổi được bằng biến môi trường vì tập gold
# 100 tài liệu sẽ không nằm chung chỗ với vài file mẫu của repo.
THU_MUC_PDF = Path(os.environ.get("GAN_NHAN_PDF_DIR", "data/samples"))

GIAO_DIEN = Path(__file__).parent / "giao_dien.html"

app = FastAPI(title="ViFinKIE — công cụ gán nhãn tập gold")


@app.exception_handler(StarletteHTTPException)
async def _in_ly_do_tu_choi(request, exc):
    """
    In mọi lần từ chối ra terminal đang chạy máy chủ.

    Người gán nhãn nhìn trình duyệt, còn khi có gì đó không hiểu thì người
    sửa lỗi nhìn terminal — và trước khi có dòng này, terminal chỉ có
    `400 Bad Request` trần trụi, không nói được thiếu gì. Mất hai vòng hỏi
    đáp cho một ô bỏ trống là quá đắt khi phía trước còn 100 tài liệu.
    """
    if exc.status_code >= 400:
        print(f"[TỪ CHỐI] {request.url.path} — {exc.detail}", file=sys.stderr)
    return await http_exception_handler(request, exc)

@dataclass
class DongHo:
    """
    Đồng hồ của một tài liệu: người gán nhãn tự bấm chạy và bấm dừng.

    VÌ SAO KHÔNG TỰ CHẠY LÚC MỞ TÀI LIỆU, cách bản đầu làm. Con số cần đo là
    thời gian một người đọc báo cáo và điền 27 ô, và nó nuôi thẳng vào giao
    thức trần người (`PREREGISTRATION.md`, tu chính 25/08/2026: số phút đặt
    đồng hồ bằng 0,6 × trung vị của 10 tài liệu đầu). Đồng hồ tự chạy đo sai
    theo cả hai chiều: gõ `doc_id` xong mới đi tìm file PDF, hay để cửa sổ đó
    mở qua buổi trưa, đều bơm thêm thời gian không phải thời gian làm việc;
    ngược lại, người gõ `doc_id` sau cùng thì đồng hồ gần như không chạy.
    Một trung vị dựng trên những con số đó không đáng để chốt tham số nào.

    Vì thế `tong_giay` cộng dồn các ĐOẠN CHẠY chứ không lấy hiệu hai mốc:
    tạm dừng là thao tác hạng nhất, và số lần tạm dừng được đếm để về sau
    tách được tài liệu làm liền mạch khỏi tài liệu ngắt quãng.

    Nằm trong bộ nhớ tiến trình nên tắt máy chủ là mất. Chấp nhận được, và
    nay còn AN TOÀN hơn trước: mất đồng hồ thì `/api/luu` từ chối ghi chứ
    không lặng lẽ ghi số 0 như một số đo.
    """

    # `da_bat_dau` là khoá riêng chứ không suy từ `tong_giay > 0`. Trên
    # Windows, `time.monotonic()` nhảy theo bước ~15 ms, nên bấm chạy rồi
    # bấm dừng ngay cho ra đúng 0,0 giây — và một đồng hồ đã chạy khi đó
    # trông y hệt một đồng hồ chưa ai đụng vào. Đây đúng là lỗi mà khoá
    # `trang_thai_dong_ho` của file gold đi sửa, chỉ khác tầng.
    da_bat_dau: bool = False
    tong_giay: float = 0.0
    chay_tu: float | None = None
    so_lan_tam_dung: int = 0

    @property
    def dang_chay(self) -> bool:
        return self.chay_tu is not None

    @property
    def da_tung_chay(self) -> bool:
        return self.da_bat_dau

    def giay(self) -> int:
        thoi = self.tong_giay
        if self.chay_tu is not None:
            thoi += time.monotonic() - self.chay_tu
        return int(thoi)

    def bat_dau(self) -> None:
        """Chạy tiếp từ chỗ đang có. Bấm lúc đang chạy thì không làm gì."""
        self.da_bat_dau = True
        if self.chay_tu is None:
            self.chay_tu = time.monotonic()

    def tam_dung(self) -> None:
        if self.chay_tu is not None:
            self.tong_giay += time.monotonic() - self.chay_tu
            self.chay_tu = None
            self.so_lan_tam_dung += 1

    def trang_thai(self) -> str:
        if not self.da_bat_dau:
            return "chua_bat_dau"
        return "dang_chay" if self.dang_chay else "tam_dung"


# Đồng hồ đang mở, theo doc_id.
_dong_ho: dict[str, DongHo] = {}


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
    khong_do_gio: bool = False


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


def _he_so_don_vi_hop_le(unit_declared: str, notes: str) -> int:
    """
    Hệ số đơn vị, phân biệt BA ca mà guideline mục 3.1 nói tới.

      để trống      -> báo cáo KHÔNG khai báo đơn vị. Guideline quy định ghi
                       hệ số 1 và nêu lý do vào notes. Đây là ca HỢP LỆ, và
                       bản đầu của máy chủ đã từ chối nhầm nó — tức chặn đúng
                       lối thoát mà guideline chỉ ra.
      có chữ, đọc được  -> dùng hệ số đọc ra.
      có chữ, không đọc được -> từ chối. Ở đây người đã gõ một cái gì đó, nên
                       im lặng lấy hệ số 1 là biến một dòng gõ sai thành một
                       tuyên bố "báo cáo ghi bằng đồng", lệch tới 10⁶ lần mà
                       không dấu hiệu nào.

    Bắt buộc có `notes` cho ca để trống, vì đó là chỗ DUY NHẤT phân biệt
    "báo cáo không khai báo đơn vị" với "người gán nhãn quên chép dòng đó".
    Hai thứ này cho ra file gold giống hệt nhau nếu không có ghi chú.
    """
    if not unit_declared.strip():
        if not notes.strip():
            raise HTTPException(
                400,
                {
                    "loi": "de_trong_don_vi_ma_khong_ghi_chu",
                    "chi_dan": "Guideline mục 3.1: báo cáo không khai báo đơn vị thì để "
                    "trống unit_declared VÀ ghi lý do vào notes. Ghi chú là chỗ duy nhất "
                    "phân biệt 'báo cáo không có dòng đó' với 'quên chép'.",
                },
            )
        return 1

    he_so, _ = parse_unit(unit_declared)
    if he_so is None:
        raise HTTPException(
            400,
            {
                "loi": "khong_doc_duoc_don_vi",
                "chi_dan": "Chuỗi này không nhận ra được. Chép lại NGUYÊN VĂN dòng trên "
                "báo cáo, ví dụ 'Đơn vị tính: VND' hoặc 'Đơn vị tính: triệu đồng'. Nếu "
                "báo cáo thật sự không có dòng nào thì để TRỐNG ô này và ghi lý do vào "
                "notes — guideline mục 3.1 cấm suy hệ số từ độ lớn con số.",
            },
        )
    return he_so


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

    MỘT FILE HỎNG KHÔNG ĐƯỢC KÉO SẬP CẢ DANH SÁCH. Trước 01/09/2026 chỗ này
    gọi `so_trang` trong một list comprehension trần: `FLC_2021Q4_TT200.pdf`
    tải về từ Vietstock bị cụt mất 5,4 MB cuối, `so_trang` ném PdfiumError,
    và cả endpoint trả 500 — người gán nhãn thấy danh sách trống trơn dù 69
    tài liệu kia đọc tốt, không có manh mối nào chỉ ra file nào có lỗi.
    """
    if not THU_MUC_PDF.is_dir():
        raise HTTPException(500, f"Không có thư mục {THU_MUC_PDF}")

    da_co = {f.stem for f in GOLD_DIR.glob("*.json")} if GOLD_DIR.is_dir() else set()
    tai_lieu = [_mo_ta_tai_lieu(f) for f in sorted(THU_MUC_PDF.glob("*.pdf"))]
    return {
        "thu_muc": str(THU_MUC_PDF),
        "tai_lieu": tai_lieu,
        "doc_id_da_gan_nhan": sorted(da_co),
        "so_da_xong": len(da_co),
        # Đếm riêng thay vì để người đọc tự lọc `doc_duoc`: số này là thứ
        # phải hiện lên giao diện, vì file hỏng nghĩa là thiếu tài liệu
        # trong tập gold chứ không phải một phiền toái hiển thị.
        "so_hong": sum(1 for t in tai_lieu if not t["doc_duoc"]),
    }


def _mo_ta_tai_lieu(duong_dan: Path) -> dict:
    """
    Một dòng trong danh sách tài liệu, kèm khoá `doc_duoc` tường minh.

    File hỏng vẫn được LIỆT KÊ chứ không bị lọc đi im lặng: tập gold đếm
    theo tài liệu, nên một cái tên biến mất khỏi danh sách là một tài liệu
    bị bỏ sót mà không ai biết. Hiện nó ra kèm lý do thì người gán nhãn đi
    tìm được bản thay thế.
    """
    try:
        so = so_trang(duong_dan)
    except Exception as e:  # pypdfium2 ném PdfiumError, nhưng file rác ném đủ loại khác
        return {
            "ten_file": duong_dan.name,
            "so_trang": 0,
            "doc_duoc": False,
            "loi": f"{type(e).__name__}: {e}",
        }
    return {"ten_file": duong_dan.name, "so_trang": so, "doc_duoc": True, "loi": None}


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


@app.get("/api/gold/{doc_id}")
def doc_lai_ban_ghi(doc_id: str) -> dict:
    """
    Nạp lại một file gold đã ghi để SỬA, thay vì phải gõ lại cả 27 ô.

    Vì sao cần: bản đầu của công cụ chỉ ghi được chứ không mở lại được, nên
    phát hiện đọc nhầm MỘT chữ số nghĩa là gõ lại toàn bộ tài liệu. Với 100
    tài liệu và cam kết gán nhãn đôi 20 tài liệu, tình huống này chắc chắn
    lặp lại hàng chục lần. Lộ ra ngay ở tài liệu đầu tiên: một chỗ đọc nhầm
    `1` thành `0` làm đẳng thức thuế lệch 10.000 đồng.

    Giá trị trả về ĐỔI NGƯỢC về thang của báo cáo (chia lại hệ số đơn vị), vì
    ô nhập nhận đúng con số như in trên giấy. Trả nguyên giá trị đã quy về
    đồng sẽ khiến lần lưu sau nhân hệ số thêm một lần nữa.

    Đây KHÔNG phải đầu ra pipeline — nó là chính ghi chép của người gán nhãn,
    nên không đụng Luật 1.
    """
    duong_dan = GOLD_DIR / f"{Path(doc_id).name}.json"
    if not duong_dan.is_file():
        raise HTTPException(404, f"Chưa có file gold cho {doc_id}")

    ban_ghi = GroundTruthDoc.load(duong_dan)
    he_so = ban_ghi.unit_multiplier or 1

    return {
        "doc_id": ban_ghi.doc_id,
        "ticker": ban_ghi.ticker,
        "period": ban_ghi.period,
        "standard": ban_ghi.standard,
        "unit_declared": ban_ghi.unit_declared,
        "source_url": ban_ghi.source_url,
        "downloaded_at": ban_ghi.downloaded_at,
        "annotator": ban_ghi.annotator,
        "notes": ban_ghi.notes,
        "so_lan_ghi": ban_ghi.so_lan_ghi,
        # Chia lại hệ số. Giá trị lưu là số nguyên đồng và hệ số là luỹ thừa
        # của 10, nên phép chia này khôi phục đúng con số trên giấy; dùng
        # Fraction-free integer division khi chia hết để khỏi ra đuôi .0.
        "values": {
            ten: None if x is None else (x // he_so if x % he_so == 0 else x / he_so)
            for ten, x in ban_ghi.values.items()
        },
    }


HANH_DONG_DONG_HO = ("bat-dau", "tam-dung")


def _tra_ve_dong_ho(doc_id: str, dh: DongHo) -> dict:
    return {
        "doc_id": doc_id,
        "trang_thai": dh.trang_thai(),
        "da_troi_giay": dh.giay(),
        "so_lan_tam_dung": dh.so_lan_tam_dung,
    }


@app.get("/api/dong-ho/{doc_id}")
def xem_dong_ho(doc_id: str) -> dict:
    """
    Trạng thái đồng hồ của một tài liệu, kể cả khi chưa ai bấm.

    Cần vì giao diện phải vẽ đúng nút ngay lúc người gõ xong `doc_id`: một
    tài liệu đang dừng giữa chừng phải hiện "Tiếp tục" chứ không hiện "Bắt
    đầu", nếu không thì bấm một cái là mất đoạn đã đo. Trả `chua_bat_dau`
    cho doc_id chưa từng bấm chứ không báo 404 — chưa bấm là một trạng thái
    hợp lệ, không phải một lỗi.
    """
    return _tra_ve_dong_ho(doc_id, _dong_ho.get(doc_id, DongHo()))


@app.post("/api/dong-ho/{doc_id}/{hanh_dong}")
def dieu_khien_dong_ho(doc_id: str, hanh_dong: str) -> dict:
    """Chạy hoặc tạm dừng đồng hồ của một tài liệu."""
    if hanh_dong not in HANH_DONG_DONG_HO:
        raise HTTPException(400, f"Hành động không hợp lệ: {hanh_dong!r}")

    dh = _dong_ho.setdefault(doc_id, DongHo())
    if hanh_dong == "bat-dau":
        dh.bat_dau()
    else:
        dh.tam_dung()

    return _tra_ve_dong_ho(doc_id, dh)


@app.post("/api/kiem")
def kiem(yeu_cau: YeuCauKiem) -> dict:
    """
    Chạy đẳng thức và kiểm dấu ba dòng khấu trừ trên số người vừa gõ.
    KHÔNG bao giờ trả về giá trị đề nghị.

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
        "dau_khau_tru": [
            {"truong": r.truong, "trang_thai": r.trang_thai, "ly_do": r.ly_do}
            for r in kiem_dau_khau_tru(gia_tri, ch)
        ],
    }


@app.post("/api/luu")
def luu(yeu_cau: YeuCauLuu) -> dict:
    """
    Ghi file gold. Từ chối khi danh mục kiểm của guideline mục 8 chưa đủ.

    Từ chối chứ không cảnh báo rồi vẫn ghi: danh mục kiểm mà bỏ qua được thì
    sau vài chục tài liệu sẽ luôn bị bỏ qua, và mục 8 thành trang trí.
    """
    # Kiểm siêu dữ liệu TRƯỚC mọi thứ khác. GroundTruthDoc.__post_init__ cũng
    # kiểm và ném ValueError, nhưng ValueError lọt ra khỏi handler thành lỗi
    # 500 — người gán nhãn nhận một trang lỗi không nói được thiếu gì, đúng
    # lúc họ chỉ quên điền một ô. Bắt ở đây để nó thành 400 gọi tên từng ô.
    thieu_meta = [
        ten
        for ten in ("doc_id", "ticker", "period", "source_url", "downloaded_at", "annotator")
        if not getattr(yeu_cau, ten).strip()
    ]
    if thieu_meta:
        raise HTTPException(400, {"loi": "thieu_sieu_du_lieu", "con_thieu": thieu_meta})

    thieu_o = con_thieu_o_kiem(yeu_cau.danh_muc_kiem)
    if thieu_o:
        raise HTTPException(400, {"loi": "danh_muc_kiem_chua_du", "con_thieu": thieu_o})

    # Từ chối khi đồng hồ chưa từng chạy, trừ khi người khai rõ là không đo.
    #
    # Ghi lặng lẽ số 0 chính là cách `VNM_2026Q1_TT99` ra đời với một ô thời
    # gian không ai đọc được nghĩa. Mà giao thức trần người lấy trung vị của
    # 10 tài liệu đầu, nên một tài liệu quên bấm giờ không phải chuyện nhỏ:
    # nó chỉ lộ ra lúc gom số, tức lúc đã quá muộn để bấm lại.
    #
    # Có lối thoát, và lối thoát phải là một hành động tường minh — cùng cách
    # guideline mục 3.1 cho phép để trống đơn vị tính nhưng bắt ghi lý do.
    # Gán nhãn lại một tài liệu cũ, hay sửa một ô sau khi phát hiện đọc nhầm,
    # đều là việc hợp lệ mà con số thời gian ở đó vô nghĩa.
    dh = _dong_ho.get(yeu_cau.doc_id, DongHo())
    if not dh.da_tung_chay and not yeu_cau.khong_do_gio:
        raise HTTPException(
            400,
            {
                "loi": "dong_ho_chua_chay",
                "chi_dan": "Bấm 'Bắt đầu bấm giờ' trước khi gán nhãn, hoặc tick 'không đo "
                "giờ tài liệu này' nếu đây là lần sửa lại chứ không phải lần gán nhãn "
                "đầu. Trung vị thời gian của 10 tài liệu đầu là thứ chốt số phút cho "
                "giao thức trần người, nên một số 0 lẫn vào không sửa lại được.",
            },
        )

    ch = _chuan(yeu_cau.standard)
    he_so = _he_so_don_vi_hop_le(yeu_cau.unit_declared, yeu_cau.notes)

    gia_tri, khong_ro = _doc_bo_gia_tri(yeu_cau.values, ch, he_so)
    if khong_ro:
        raise HTTPException(400, {"loi": "o_khong_doc_duoc", "o": khong_ro})

    # Ghi đè bản đã có thì ĐẾM, không im lặng. Một bản ghi sửa ba lần và một
    # bản viết một lần rồi thôi là hai thứ khác nhau khi phân tích chất lượng
    # gán nhãn, mà nếu không đếm thì chúng trông y hệt nhau trên đĩa.
    da_co = GOLD_DIR / f"{Path(yeu_cau.doc_id).name}.json"
    so_lan_ghi = GroundTruthDoc.load(da_co).so_lan_ghi + 1 if da_co.is_file() else 1

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
        # Đồng hồ đã chạy thì con số của nó thắng, kể cả khi ô "không đo giờ"
        # được tick: một số đo có thật đáng giữ hơn một lời khai mâu thuẫn
        # với nó, và giao diện chỉ hiện ô đó khi đồng hồ đứng yên.
        thoi_gian_giay=dh.giay() if dh.da_tung_chay else 0,
        so_lan_kiem_dang_thuc=yeu_cau.so_lan_kiem,
        sua_gia_tri_sau_khi_kiem=yeu_cau.sua_sau_khi_kiem,
        so_lan_ghi=so_lan_ghi,
        trang_thai_dong_ho="da_do" if dh.da_tung_chay else "khong_do",
        so_lan_tam_dung=dh.so_lan_tam_dung,
    )
    duong_dan = ban_ghi.save()
    _dong_ho.pop(yeu_cau.doc_id, None)

    return {
        "da_ghi": str(duong_dan),
        "trang_thai_dong_ho": ban_ghi.trang_thai_dong_ho,
        "thoi_gian_giay": ban_ghi.thoi_gian_giay,
        "so_lan_tam_dung": ban_ghi.so_lan_tam_dung,
        "so_lan_ghi": so_lan_ghi,
    }
