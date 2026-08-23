"""
Đo engine OCR trên Ô SỐ, dùng bảng render từ tầng XBRL làm chuẩn.

VÌ SAO MODULE NÀY TỒN TẠI
-------------------------
Ajayi et al. (arXiv 2507.02009) đo ba engine trên bảng khoa học và thấy
EasyOCR yếu nhất: Levenshtein accuracy trung bình 0,646 so với PaddleOCR
0,715 và docTR 0,704. Repo này đang dùng EasyOCR, nên hoặc phải đổi engine,
hoặc phải có bằng chứng rằng trên chữ SỐ thì kết luận đó không áp được.
Để trống là chỗ reviewer hỏi ngay.

Số của Ajayi et al. đo trên văn bản khoa học — nhiều dòng, chữ cái, ký hiệu
toán. Ô số của báo cáo tài chính là một miền hẹp hơn hẳn: chỉ chữ số, dấu
phân nhóm, ngoặc đơn cho số âm. Không có gì đảm bảo thứ hạng giữa các
engine giữ nguyên khi đổi miền, và đó đúng là một câu hỏi thực nghiệm nhỏ
mà bài viết trả lời được bằng chính hạ tầng đã có.

VÌ SAO ĐO TRÊN TẦNG XBRL CHỨ KHÔNG CHỜ TẬP GOLD
------------------------------------------------
`render.py` đã cho ảnh bảng, bbox từng ô, và chuỗi ĐÚNG NHƯ đã vẽ. Tức là
ground truth mức ô đã có sẵn, chính xác tuyệt đối, và không tốn một phút
gán nhãn nào. Chờ 60 tài liệu gold mới đo được là chờ một thứ không cần
phải chờ.

GIỚI HẠN, PHẢI NÊU TRONG BÀI
-----------------------------
Ảnh render ra sạch và đều: không nhiễu scan, không lệch trang, không mất
dấu tiếng Việt. Đo trên đó là đo CẬN TRÊN của engine, không phải hiệu năng
trên báo cáo thật. Vì vậy module có sẵn các biến thể ảnh xuống cấp — mờ,
nhiễu, nén, hạ độ phân giải — để con số không chỉ đến từ điều kiện lý
tưởng. Phần còn thiếu mà chỉ tập Stress của tầng gold Việt Nam trả lời
được: chữ tiếng Việt có dấu, và bố cục do người khác trình bày.

KHÔNG "SỬA GIÚP" OCR TRƯỚC KHI SO
----------------------------------
Chuẩn hoá ở đây cố ý hẹp: bỏ khoảng trắng, hiểu ngoặc đơn là số âm, bỏ dấu
phân nhóm nghìn. KHÔNG sửa các cặp OCR hay nhầm (`O`→`0`, `l`→`1`,
`S`→`5`). Sửa chúng là đo một engine ĐÃ ĐƯỢC VÁ chứ không phải đo engine,
và con số thu được sẽ nói dối theo hướng lạc quan — đúng loại lỗi làm cả
phần so sánh mất giá trị.
"""

import random
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

from PIL import Image, ImageFilter

from eval.xbrl_tier.render import RenderedTable, render
from eval.xbrl_tier.table import FinancialTable

# Một engine OCR, nhìn từ phía module này: nhận ảnh, trả chuỗi đọc được.
#
# Hẹp có chủ đích. Mọi engine đều trả thêm bbox và confidence, nhưng phép đo
# ở đây chỉ hỏi "đọc ra chữ gì" — bbox đã biết trước vì chính ta cắt ô ra,
# còn confidence thì mỗi engine hiệu chỉnh một kiểu nên không so trực tiếp
# được. Giao diện hẹp cũng là thứ cho phép test chạy bằng engine giả, không
# cần model.
EngineOCR = Callable[[Image.Image], str]

# Bao nhiêu pixel nới ra quanh bbox khi cắt ô.
#
# Cắt sát mép làm cụt nét chữ ở biên, và khi đó ta đo lỗi của phép cắt chứ
# không phải lỗi của engine. Engine OCR cũng cần một ít nền trắng quanh chữ
# để bộ dò dòng làm việc.
DEM_CAT = 6


@dataclass(frozen=True)
class KetQuaO:
    """Kết quả đọc một ô, giữ đủ để truy lại vì sao con số tổng ra như vậy."""

    concept: str
    period: str
    chuoi_that: str
    chuoi_doc_duoc: str
    do_chinh_xac: float
    khop_chuoi: bool
    gia_tri_that: float | None
    gia_tri_doc_duoc: float | None

    @property
    def khop_gia_tri(self) -> bool:
        """
        Đọc ra ĐÚNG CON SỐ hay không.

        Đây mới là thứ pipeline cần, và nó khắt khe hơn `do_chinh_xac`
        theo một cách quan trọng: đọc `5.393.002` thành `5.898.002` cho
        Levenshtein accuracy 0,86 — nghe như gần đúng — nhưng con số thì
        sai hoàn toàn và mọi tỷ số tài chính dựng trên nó đều hỏng. Một
        chữ số sai không phải là "gần đúng".
        """
        return self.gia_tri_that == self.gia_tri_doc_duoc


@dataclass(frozen=True)
class KetQuaEngine:
    """Tổng hợp một lượt đo: một engine, một biến thể ảnh."""

    ten_engine: str
    bien_the_anh: str
    cac_o: list[KetQuaO] = field(default_factory=list)

    @property
    def n_o(self) -> int:
        return len(self.cac_o)

    @property
    def do_chinh_xac_levenshtein(self) -> float:
        """Trung bình theo Ô, cùng định nghĩa Ajayi et al. dùng."""
        if not self.cac_o:
            return 0.0
        return sum(o.do_chinh_xac for o in self.cac_o) / len(self.cac_o)

    @property
    def ty_le_khop_gia_tri(self) -> float:
        """
        Tỷ lệ ô đọc ra đúng con số. Chỉ số đáng quyết định nhất ở đây.
        """
        if not self.cac_o:
            return 0.0
        return sum(1 for o in self.cac_o if o.khop_gia_tri) / len(self.cac_o)

    @property
    def ty_le_khong_ra_so(self) -> float:
        """
        Tỷ lệ ô mà chuỗi đọc được không parse thành số nào.

        Tách riêng khỏi "đọc sai số" vì hai thứ này khác hẳn nhau về hậu
        quả, đúng theo phân loại lỗi ồn / lỗi câm của đề tài: không ra số
        là lỗi ỒN — hệ biết mình thất bại và có thể fallback; ra một số
        SAI là lỗi CÂM — không tín hiệu nào báo, và lỗi lan xuống mọi tỷ
        số tài chính. Gộp chúng vào một con số là xoá mất phân biệt trung
        tâm của cả nghiên cứu.
        """
        if not self.cac_o:
            return 0.0
        return sum(1 for o in self.cac_o if o.gia_tri_doc_duoc is None) / len(self.cac_o)


# --- Levenshtein -----------------------------------------------------------


def khoang_cach_levenshtein(a: str, b: str) -> int:
    """
    Số phép chèn/xoá/thay ký tự ít nhất để biến `a` thành `b`.

    Tự cài thay vì thêm `rapidfuzz` hay `python-Levenshtein` vào
    requirements: chuỗi ở đây dài chừng chục ký tự và số ô mỗi bảng cỡ vài
    chục, nên bản quy hoạch động hai hàng chạy dư sức. Thêm một phụ thuộc
    vào image production cho một hàm mười dòng là cái giá không đáng trả —
    cùng lập luận đã dùng khi từ chối `pulp` cho C2.
    """
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    truoc = list(range(len(b) + 1))

    for i, ky_tu_a in enumerate(a, start=1):
        hien_tai = [i]
        for j, ky_tu_b in enumerate(b, start=1):
            hien_tai.append(
                min(
                    truoc[j] + 1,                                    # xoá
                    hien_tai[j - 1] + 1,                             # chèn
                    truoc[j - 1] + (ky_tu_a != ky_tu_b),             # thay
                )
            )
        truoc = hien_tai

    return truoc[-1]


def do_chinh_xac_levenshtein(that: str, doc_duoc: str) -> float:
    """
    1 − khoảng_cách / độ_dài_lớn_hơn, chặn trong [0, 1].

    Chuẩn hoá theo chuỗi DÀI HƠN chứ không theo chuỗi thật: nếu chia cho
    độ dài chuỗi thật thì một engine đọc ra chuỗi rác dài gấp ba sẽ có
    "độ chính xác" âm rồi bị chặn về 0, mất phân biệt với engine không đọc
    ra gì. Hai chuỗi cùng rỗng tính là khớp hoàn toàn.
    """
    if not that and not doc_duoc:
        return 1.0

    dai_nhat = max(len(that), len(doc_duoc))
    return 1.0 - khoang_cach_levenshtein(that, doc_duoc) / dai_nhat


# --- Chuẩn hoá số ----------------------------------------------------------

# Ký tự bị bỏ trước khi parse. Dấu phẩy và dấu chấm đều là dấu phân nhóm
# nghìn trong phạm vi tầng này, vì render.py chỉ vẽ số NGUYÊN.
#
# CẢNH BÁO cho ngày áp module này lên tầng gold Việt Nam: ở đó `1.234` vừa
# có thể là một nghìn hai trăm ba tư (quy ước Việt Nam) vừa có thể là một
# phẩy hai ba tư. Quy tắc dưới đây sẽ chọn nghĩa thứ nhất mà không hỏi ai.
# Đừng dùng lại nguyên xi — hãy quyết định tường minh dựa trên đơn vị tính
# đọc được ở header.
KY_TU_BO = " \t\n ,._'"


def chuan_hoa_so(chuoi: str) -> float | None:
    """
    Chuỗi in trên bảng -> giá trị số, hoặc None nếu không ra số nào.

    Hiểu ngoặc đơn là số âm, vì đó chính là cách báo cáo tài chính in số
    âm và cũng chính là nguồn của chế độ lỗi mất dấu âm.

    Trả None cho ô trống (`-`) và cho mọi chuỗi còn sót ký tự không phải
    chữ số. Không đoán, không sửa: một chuỗi `l23` được trả về None chứ
    không được hiểu thành 123 — xem phần cuối docstring đầu module.
    """
    goc = chuoi.strip()
    if not goc:
        return None

    am = goc.startswith("(") and goc.endswith(")")
    if am:
        goc = goc[1:-1]
    elif goc.startswith("-"):
        am = True
        goc = goc[1:]

    for ky_tu in KY_TU_BO:
        goc = goc.replace(ky_tu, "")

    if not goc or not goc.isdigit():
        return None

    gia_tri = float(goc)
    return -gia_tri if am else gia_tri


# --- Xuống cấp ảnh ---------------------------------------------------------


def anh_sach(anh: Image.Image) -> Image.Image:
    return anh


def anh_mo(anh: Image.Image, ban_kinh: float = 1.1) -> Image.Image:
    """Mô phỏng scan lệch tiêu cự — chế độ hỏng phổ biến nhất của bản scan."""
    return anh.filter(ImageFilter.GaussianBlur(radius=ban_kinh))


def anh_nhieu(anh: Image.Image, muc: int = 34, seed: int = 0) -> Image.Image:
    """
    Thêm nhiễu hạt, mô phỏng scan chất lượng thấp.

    Có `seed` vì một biến thể ảnh khác nhau giữa hai lần chạy là một bộ dữ
    liệu khác nhau, và khi đó hai con số đo được không so với nhau được.
    Dùng `random` của thư viện chuẩn thay vì numpy để hàm này không kéo
    thêm phụ thuộc vào một module vốn chỉ cần Pillow.
    """
    rng = random.Random(seed)
    xam = anh.convert("L")
    diem = xam.load()
    rong, cao = xam.size

    for y in range(cao):
        for x in range(rong):
            lech = rng.randint(-muc, muc)
            diem[x, y] = min(255, max(0, diem[x, y] + lech))

    return xam.convert("RGB")


def anh_do_phan_giai_thap(anh: Image.Image, ty_le: float = 0.5) -> Image.Image:
    """
    Thu nhỏ rồi phóng lại, mô phỏng bản scan độ phân giải thấp.

    Đây là biến thể sát thực tế nhất với báo cáo scan cũ, và cũng là biến
    thể đánh vào đúng điểm yếu của nhận dạng chữ số: các chữ số hẹp như
    `1` và `7` mất nét trước tiên.
    """
    rong, cao = anh.size
    nho = anh.resize((max(1, int(rong * ty_le)), max(1, int(cao * ty_le))), Image.BILINEAR)
    return nho.resize((rong, cao), Image.BILINEAR)


# Bộ biến thể mặc định. Tên là khoá tường minh, đi thẳng vào bảng kết quả
# và vào metrics — đừng để người đọc suy biến thể từ thứ tự dòng.
BIEN_THE_ANH: dict[str, Callable[[Image.Image], Image.Image]] = {
    "sach": anh_sach,
    "mo": anh_mo,
    "nhieu": anh_nhieu,
    "phan_giai_thap": anh_do_phan_giai_thap,
}


# --- Engine ----------------------------------------------------------------


def engine_easyocr(anh: Image.Image) -> str:
    """
    Engine đang dùng trong pipeline.

    Nạp lười qua `ocr_baseline.get_reader()` theo đúng quy ước của repo:
    CI không cài torch, nên import module này không được kéo theo model.
    """
    from ocr_baseline import ocr_image

    return ocr_image(anh)


# Cache reader của PaddleOCR, cùng mẫu với `_reader` ở ocr_baseline.py:
# dựng ở lần gọi đầu rồi dùng lại, vì khởi tạo tốn vài giây và một phép đo
# chạy qua hàng nghìn ô.
_paddle = None


def engine_paddleocr(anh: Image.Image) -> str:
    """
    Engine đối chứng theo Ajayi et al.

    CHƯA khai báo trong requirements.txt và cố ý như vậy: PaddleOCR kéo
    theo paddlepaddle, một runtime nặng ngang torch, và cài nó vào image
    production chỉ để chạy một phép đo một lần là cái giá sai. Ai muốn
    chạy nhánh này thì cài riêng ở môi trường phát triển.

    Ném lỗi có hướng dẫn thay vì `ImportError` trần: người chạy phép đo
    này thường không phải người đã đọc file này.
    """
    try:
        from paddleocr import PaddleOCR
    except ImportError as e:
        raise RuntimeError(
            "Nhánh PaddleOCR cần `pip install paddleocr paddlepaddle`. Nó cố ý "
            "KHÔNG nằm trong requirements.txt vì chỉ dùng cho phép đo đối "
            "chứng, không dùng trong pipeline."
        ) from e

    global _paddle
    if _paddle is None:
        _paddle = PaddleOCR(lang="en")

    import numpy as np

    ket_qua = _paddle.ocr(np.array(anh.convert("RGB")))
    if not ket_qua or not ket_qua[0]:
        return ""
    return "\n".join(dong[1][0] for dong in ket_qua[0])


ENGINES: dict[str, EngineOCR] = {
    "easyocr": engine_easyocr,
    "paddleocr": engine_paddleocr,
}


# --- Phép đo ---------------------------------------------------------------


def cat_o(anh: Image.Image, bbox: tuple[int, int, int, int], dem: int = DEM_CAT):
    """Cắt một ô ra khỏi ảnh trang, nới thêm `dem` pixel và clamp về trong ảnh."""
    trai, tren, phai, duoi = bbox
    rong, cao = anh.size
    return anh.crop(
        (
            max(0, trai - dem),
            max(0, tren - dem),
            min(rong, phai + dem),
            min(cao, duoi + dem),
        )
    )


def do_mot_bang(
    rendered: RenderedTable,
    engine: EngineOCR,
    ten_engine: str = "?",
    bien_the: str = "sach",
    bo_o_trong: bool = True,
) -> KetQuaEngine:
    """
    Chạy `engine` trên từng ô số của một bảng đã render.

    `bo_o_trong` mặc định True: ô trống được vẽ thành một dấu gạch, và
    "engine có đọc được dấu gạch không" không phải câu hỏi đang hỏi. Để
    chúng trong phép đo thì một bảng nhiều ô trống sẽ đẩy con số lên hoặc
    xuống tuỳ engine xử lý dấu gạch thế nào, chứ không nói gì về khả năng
    đọc chữ số.

    Ảnh được xuống cấp MỘT LẦN cho cả trang rồi mới cắt ô, không xuống cấp
    từng ô sau khi cắt. Thứ tự này quan trọng: bản scan xuống cấp ở mức
    trang, nên làm mờ từng ô đã cắt sẽ bỏ mất phần nhiễu tràn qua biên ô —
    đúng thứ gây lỗi lệch dòng trên báo cáo thật.
    """
    lam_xuong_cap = BIEN_THE_ANH[bien_the]
    anh = lam_xuong_cap(rendered.image)

    cac_o: list[KetQuaO] = []

    for (concept, period), bbox in rendered.bboxes.items():
        chuoi_that = rendered.texts.get((concept, period), "")
        gia_tri_that = chuan_hoa_so(chuoi_that)

        if bo_o_trong and gia_tri_that is None:
            continue

        doc_duoc = engine(cat_o(anh, bbox)).strip()

        cac_o.append(
            KetQuaO(
                concept=concept,
                period=period,
                chuoi_that=chuoi_that,
                chuoi_doc_duoc=doc_duoc,
                do_chinh_xac=do_chinh_xac_levenshtein(chuoi_that, doc_duoc),
                khop_chuoi=chuoi_that == doc_duoc,
                gia_tri_that=gia_tri_that,
                gia_tri_doc_duoc=chuan_hoa_so(doc_duoc),
            )
        )

    return KetQuaEngine(ten_engine=ten_engine, bien_the_anh=bien_the, cac_o=cac_o)


def so_sanh_engine(
    cac_bang: Iterable[RenderedTable],
    engines: dict[str, EngineOCR] | None = None,
    cac_bien_the: Iterable[str] = ("sach", "mo", "nhieu", "phan_giai_thap"),
) -> list[KetQuaEngine]:
    """
    Chạy mọi engine trên mọi biến thể ảnh, gộp kết quả theo (engine, biến thể).

    Trả về danh sách phẳng chứ không phải bảng lồng nhau: đây là dạng đi
    thẳng vào `src/experiments/tables.py` được, và mỗi dòng tự mang đủ nhãn
    để không phụ thuộc vị trí.
    """
    engines = engines if engines is not None else {"easyocr": engine_easyocr}
    cac_bang = list(cac_bang)
    ket_qua: list[KetQuaEngine] = []

    for ten, engine in engines.items():
        for bien_the in cac_bien_the:
            gop: list[KetQuaO] = []
            for bang in cac_bang:
                gop.extend(do_mot_bang(bang, engine, ten, bien_the).cac_o)
            ket_qua.append(
                KetQuaEngine(ten_engine=ten, bien_the_anh=bien_the, cac_o=gop)
            )

    return ket_qua


def thong_ke_nham_chu_so(ket_qua: Iterable[KetQuaEngine]) -> dict[tuple[str, str], int]:
    """
    Đếm các cặp chữ số bị đọc nhầm: `{(thật, đọc_được): số lần}`.

    Chỉ xét những ô mà chuỗi đọc được DÀI BẰNG chuỗi thật. Khi độ dài lệch
    nhau thì việc căn ký tự nào ứng với ký tự nào là một bài toán riêng, và
    đoán bừa ở đó sẽ sinh ra những cặp nhầm không có thật rồi đưa thẳng vào
    taxonomy lỗi — làm hỏng đúng thứ hàm này sinh ra để phục vụ.

    Vì sao cần: `repair/candidates.py` sinh ứng viên từ một bảng bốn cặp
    hay nhầm, và `inject.py` sinh lỗi theo taxonomy chế độ lỗi. Cả hai đang
    dựa trên phân loại chưa đo trên dữ liệu thật. Hàm này biến câu hỏi
    "engine hay nhầm cặp nào" từ phỏng đoán thành số đếm được.
    """
    dem: dict[tuple[str, str], int] = {}

    for kq in ket_qua:
        for o in kq.cac_o:
            if len(o.chuoi_that) != len(o.chuoi_doc_duoc):
                continue
            for that, doc in zip(o.chuoi_that, o.chuoi_doc_duoc, strict=True):
                if that != doc and that.isdigit() and doc.isdigit():
                    dem[(that, doc)] = dem.get((that, doc), 0) + 1

    return dem


def bang_nham_chu_so(dem: dict[tuple[str, str], int], top: int = 10) -> str:
    """Bảng cặp nhầm hay gặp nhất, sắp giảm dần."""
    if not dem:
        return "_Không quan sát được cặp nhầm chữ số nào._"

    dong = ["| Thật | Đọc thành | Số lần |", "|---|---|---:|"]
    for (that, doc), so_lan in sorted(dem.items(), key=lambda x: -x[1])[:top]:
        dong.append(f"| {that} | {doc} | {so_lan} |")

    return "\n".join(dong)


def bang_markdown(ket_qua: Iterable[KetQuaEngine]) -> str:
    """
    Bảng người đọc được, để dán thẳng vào bài hoặc vào tài liệu bàn giao.

    Cột N có mặt vì danh mục kiểm ở ADDENDUM mục 10 đòi mọi bảng phải nêu
    N THẬT của chính nó — ở đây là số Ô, không phải số bảng.
    """
    dong = [
        "| Engine | Ảnh | N ô | Levenshtein | Đúng con số | Không ra số |",
        "|---|---|---:|---:|---:|---:|",
    ]

    for kq in ket_qua:
        dong.append(
            f"| {kq.ten_engine} | {kq.bien_the_anh} | {kq.n_o} "
            f"| {kq.do_chinh_xac_levenshtein:.3f} "
            f"| {kq.ty_le_khop_gia_tri:.3f} "
            f"| {kq.ty_le_khong_ra_so:.3f} |"
        )

    return "\n".join(dong)


def bang_tong_hop(n_chi_tieu: int = 25, seed: int = 20260823) -> FinancialTable:
    """
    Bảng tổng hợp để đo engine khi CHƯA có hồ sơ XBRL thật trên máy.

    Nội dung số ở đây là ngẫu nhiên và KHÔNG thoả đẳng thức kế toán nào —
    đúng chỗ SynFinTabs dừng lại, và với mọi phép đo khác của dự án thì đó
    là khuyết tật chí mạng. Riêng phép đo này thì không, vì câu hỏi duy
    nhất là "engine đọc ra đúng chữ số trên ảnh hay không", và câu trả lời
    không phụ thuộc vào việc các con số có cộng lại đúng hay không.

    Cái phải giữ đúng là PHỔ ĐỘ LỚN và hình thức trình bày: từ số bốn chữ
    số tới số mười ba chữ số, có số âm in trong ngoặc, có ô trống. Chữ số
    hẹp như `1` và `7` mất nét trước tiên khi ảnh xuống cấp, nên một bảng
    toàn số nhỏ sẽ cho con số đẹp giả tạo.
    """
    rng = random.Random(seed)
    ky = ["2025-12-31", "2024-12-31"]

    concepts = [f"Concept{i:02d}" for i in range(n_chi_tieu)]
    labels = {ten: f"Line item {i}" for i, ten in enumerate(concepts)}
    values: dict[str, dict[str, float | None]] = {}

    for i, ten in enumerate(concepts):
        do_lon = 10 ** (4 + i % 10)
        values[ten] = {}
        for j, k in enumerate(ky):
            if (i + j) % 11 == 0:
                values[ten][k] = None            # ô trống, có thật trên báo cáo
                continue
            gia_tri = float(rng.randint(do_lon, do_lon * 9))
            values[ten][k] = -gia_tri if (i + j) % 7 == 0 else gia_tri

    return FinancialTable(
        doc_id="TONG-HOP",
        concepts=concepts,
        labels=labels,
        periods=ky,
        values=values,
        unit_label="USD",
    )


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Console Windows mặc định cp1252, in tiếng Việt ra stdout sẽ nổ
    # UnicodeEncodeError trước cả khi kịp thấy kết quả.
    sys.stdout.reconfigure(encoding="utf-8")

    # BẪY: `python src/eval/ocr_compare.py` đặt src/eval/ vào ĐẦU sys.path,
    # và ở đó có eval/metrics.py — file này che mất src/metrics.py của
    # pipeline. Hậu quả không lộ ra ở đây mà lộ ở tận trong ocr_baseline,
    # với `ImportError: cannot import name 'timer' from 'metrics'`, trỏ vào
    # một file chẳng liên quan gì. Cùng họ với vụ src/types.py che module
    # `types` của thư viện chuẩn.
    #
    # Bỏ thư mục script khỏi sys.path và đảm bảo src/ có mặt, để lệnh chạy
    # được cả hai kiểu: `python src/eval/ocr_compare.py` và
    # `python -m eval.ocr_compare`.
    _thu_muc_script = str(Path(__file__).resolve().parent)
    sys.path[:] = [p for p in sys.path if Path(p or ".").resolve() != Path(_thu_muc_script)]
    _src = str(Path(__file__).resolve().parents[1])
    if _src not in sys.path:
        sys.path.insert(0, _src)

    ten_engine = sys.argv[1] if len(sys.argv) > 1 else "easyocr"
    if ten_engine not in ENGINES:
        raise SystemExit(f"Engine không biết: {ten_engine}. Có: {sorted(ENGINES)}")

    bang = render(bang_tong_hop())
    print(f"Đo {ten_engine} trên {len(bang.bboxes)} ô của bảng tổng hợp...\n")

    ket_qua = so_sanh_engine([bang], engines={ten_engine: ENGINES[ten_engine]})
    bao_cao = bang_markdown(ket_qua)
    nham = bang_nham_chu_so(thong_ke_nham_chu_so(ket_qua))

    print(bao_cao)
    print()
    print(nham)

    dich = Path("data/output") / f"ocr_engine_{ten_engine}.md"
    dich.parent.mkdir(parents=True, exist_ok=True)
    dich.write_text(
        f"# Đo engine OCR trên ô số — {ten_engine}\n\n"
        f"Sinh bằng `python src/eval/ocr_compare.py {ten_engine}`. "
        f"Bảng tổng hợp {len(bang.bboxes)} ô, phổ độ lớn 4–13 chữ số, có số âm "
        f"in trong ngoặc và ô trống.\n\n"
        f"Cột **Levenshtein** là chỉ số Ajayi et al. dùng, đo ở mức KÝ TỰ. Cột "
        f"**Đúng con số** đo ở mức GIÁ TRỊ. Khoảng cách giữa hai cột chính là "
        f"thứ đáng đọc: một chữ số sai không phải là 'gần đúng' với một con số "
        f"tài chính.\n\n"
        f"{bao_cao}\n\n"
        f"## Cặp chữ số bị đọc nhầm\n\n"
        f"Chỉ tính những ô mà chuỗi đọc được dài bằng chuỗi thật, nên đây là "
        f"cận dưới. Bảng này là dữ liệu đầu vào để hiệu chỉnh bảng cặp hay nhầm "
        f"trong `src/repair/candidates.py` — **chưa được áp vào**, xem ghi chú "
        f"trong HANDOFF.\n\n"
        f"{nham}\n",
        encoding="utf-8",
    )
    print(f"\nĐã ghi {dich}")
