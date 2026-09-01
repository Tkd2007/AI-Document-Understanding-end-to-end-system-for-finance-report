"""
Document Classifier & Router

Điều phối giữa OCR Pipeline (rẻ, nhanh) và VLM Pipeline (đắt, chậm hơn
nhưng đáng tin hơn).

MẶC ĐỊNH CỦA CODE: nhánh OCR TẮT (USE_OCR_FIRST không đặt -> false).
Nhưng .env đè được lên mặc định đó, và trên máy phát triển nó ĐANG BẬT —
kiểm bằng dòng "--- Nhánh OCR: ... ---" in ra lúc chạy, đừng tin mặc định.

Lý do mặc định là tắt — EasyOCR đọc số rất chuẩn nhưng đọc chữ tiếng Việt
có dấu thì hỏng ("TỔNG TÀI SẢN" -> "TỖNG TÀISẢN"), trong khi regex phải
khớp đúng tên chỉ tiêu mới tìm được dòng. Trên báo cáo VNM Q1/2026, nhánh
VLM một mình trả đúng cả 11 field lúc đó và dừng ở trang 10, còn nhánh OCR
quét hết 55 trang rồi vẫn thiếu field.

CÁI GIÁ KHI BẬT, đo trên lượt chấm tập gold 27/08/2026: OCR chiếm 77% tổng
thời gian chạy (~27,6 giây một trang) và quét 100% số trang của mọi tài
liệu. Nguyên nhân nằm ở run_ocr_first(): nó chỉ dừng khi is_acceptable()
đúng — mà điều đó gần như không bao giờ xảy ra vì chính lý do đọc hỏng chữ
có dấu ở trên. Đo được 0/9 lần dừng sớm.

ĐÃ CHẶN 28/08/2026 bằng PATIENCE_PAGES_OCR — xem hằng số đó. Con số giờ
tiết kiệm được thì CHƯA đo; phải chạy lại tập gold mới biết.

Code nhánh OCR được GIỮ NGUYÊN, không xoá: hướng làm cho nó đáng tin là dò
theo MÃ SỐ DÒNG thay vì theo tên chỉ tiêu — xem
extract_baseline.extract_field_by_code, và probe của phương án C vốn đã
dùng đúng cách đó.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from constraints import build_matrix
from extract_baseline import extract_all_fields, tim_theo_ma_so, tong_hop_dau_vet
from extract_vlm import extract_fields_from_regions, require_config
from extraction_types import ExtractionResult, FieldResult
from fields_config import (
    DEFAULT_STANDARD,
    UNIT_KEY,
    QuyUocDau,
    Standard,
    empty_result,
    fields_for,
    identities_for,
    xac_dinh_quy_uoc,
)
from ky_hieu_mau import lan_ky_hieu
from metrics import RunMetrics, merge_into_totals, thong_tin_tai_lap, timer
from ocr_baseline import iter_table_regions, ocr_page_regions
from repair.candidates import generate as sinh_ung_vien
from repair.diagnose import diagnose
from repair.neo import neo_bbox
from validation import has_required_fields, validate_result

load_dotenv()

def _co_bat(ten_bien: str, mac_dinh: str = "false") -> bool:
    """Đọc một cờ bật/tắt từ biến môi trường."""
    return os.getenv(ten_bien, mac_dinh).strip().lower() in {"1", "true", "yes"}


# Bật lại nhánh OCR bằng USE_OCR_FIRST=true trong .env
USE_OCR_FIRST = _co_bat("USE_OCR_FIRST")

# Số trang liên tiếp nhánh OCR không trích thêm được chỉ tiêu nào thì dừng.
#
# VÌ SAO PHẢI CÓ, đo trên lượt chấm tập gold 27/08/2026: trước khi có bộ đếm
# này, `run_ocr_first()` chỉ dừng khi `is_acceptable()` đúng — mà điều kiện ấy
# đòi regex khớp đủ field bắt buộc, tức khớp TÊN chỉ tiêu tiếng Việt có dấu,
# đúng chỗ EasyOCR đọc hỏng. Kết quả: 0/9 lần dừng sớm, quét 100% số trang của
# mọi tài liệu, và OCR chiếm 77% tổng thời gian chạy (~27,6 giây một trang).
#
# KHÔNG gác điều kiện dừng sau `has_required_fields()` như nhánh VLM đang làm.
# Ở nhánh VLM cái gác đó hợp lý vì VLM thường lấp đủ field bắt buộc; ở nhánh
# regex thì nó gần như không bao giờ đúng, nên gác vào là dựng lại đúng cái
# vòng lặp không có trần mà bộ đếm này sinh ra để cắt.
#
# ĐỂ 10, RỘNG HƠN HẲN `PATIENCE_PAGES = 3` của nhánh VLM. Hai nhánh đếm cùng
# một thứ nhưng xuất phát từ hai chỗ khác nhau, và đó là lý do con số khác nhau:
#
#   * Nhánh VLM chỉ bắt đầu đếm SAU khi đã đủ field bắt buộc, tức sau khi đã
#     vào tới phần bảng. Ba trang liên tiếp không có gì mới ở đó thật sự nghĩa
#     là hết bảng để đọc.
#   * Nhánh này KHÔNG có cái gác ấy, nên bộ đếm chạy ngay từ trang 1 — mà
#     trang đầu báo cáo niêm yết là bìa, rồi tới trang ký, mục lục, phần giới
#     thiệu. Để 3 thì nó dừng ở trang 3, TRƯỚC khi tới bảng nào, và nhánh OCR
#     thành vô dụng một cách IM LẶNG: không gì nổ, chỉ là regex không bao giờ
#     được đưa cho xem một trang có số.
#
# Nói cách khác, ngưỡng này phải đủ lớn để vượt qua phần mở đầu tài liệu — nó
# không phải tham số tinh chỉnh tốc độ mà là điều kiện để nhánh OCR còn chạy.
# Trên tập gold, bảng B01 sớm nhất ở trang 4 (BMP) và muộn nhất ở trang 5
# (SBT); 10 chừa biên rộng cho hồ sơ có phần mở đầu dài hơn.
#
# CÁI GIÁ, phải đo chứ không được đoán: probe dò dòng chỉ đọc `cached_pages`,
# nên nhánh OCR dừng sớm hơn thì probe thấy ít trang hơn và kết luận "dòng
# vắng mặt trên biểu mẫu" có thể đổi. Số trang probe thật sự đọc được ghi vào
# metrics dưới khoá `probe_so_trang` để so được giữa các lượt chạy.
PATIENCE_PAGES_OCR = int(os.getenv("PATIENCE_PAGES_OCR", "10"))

# Bật TẦNG REPAIR trên đường chạy tài liệu Việt Nam. MẶC ĐỊNH TẮT, có chủ đích.
#
# Vì sao mặc định phải là TẮT. H1 so "vi phạm ràng buộc" với "confidence của
# model" như hai bộ dự báo lỗi, và phép so đó chỉ có nghĩa trên đầu ra mà tầng
# ràng buộc CHƯA đụng vào. Tầng repair thì sửa giá trị cho tới khi residual về
# 0 — bật nó mặc định là làm phẳng đúng tín hiệu H1 đang đem đi đánh giá, và
# làm phẳng một cách không nhìn thấy được từ bảng kết quả.
#
# Cùng họ với DISABLE_CONSTRAINT_GATE, nhưng ngược chiều: cái kia TẮT một thứ
# đang bật để đo, cái này BẬT một thứ đang tắt để phục vụ. Cả hai đều được ghi
# thành khoá tường minh trong metrics vì hai lượt chạy khác cấu hình cho ra dữ
# liệu không so với nhau được.
#
# Đây là tầng H2/H3 — nó CHẠY SAU khi validate_result() đã chấm xong, nên bật
# nó không xoá dấu vết của lần chấm đó: `warnings` giữ nguyên, và certificate
# ghi lại đúng những gì đã bị đổi.
BAT_TANG_REPAIR = _co_bat("BAT_TANG_REPAIR")

# Tắt HOÀN TOÀN cổng ràng buộc. CHỈ DÙNG KHI ĐO, không dùng khi phục vụ.
#
# Vì sao cờ này phải tồn tại: H1 so "vi phạm ràng buộc" với "confidence của
# model" như hai bộ dự báo lỗi. Nhưng pipeline hiện ĐÃ dùng chính đẳng thức
# kế toán làm cổng quyết định fallback — is_acceptable() gọi
# validate_result(), và khi có warning thì run_vlm() cho VLM ghi đè. Nghĩa
# là đầu ra đã được chính tín hiệu ấy làm sạch.
#
# Đo AUROC của vi phạm ràng buộc trên dữ liệu đó là VÒNG LẶP LUẬN CHỨNG:
# ta đang đánh giá một tín hiệu trên tập đã bị chính nó lọc, và con số thu
# được không nói lên điều gì về khả năng dự báo thật. Bật cờ này cho ta
# nhánh đối chứng: đầu ra thô, chưa từng thấy ràng buộc.
#
# Đây là mục rẻ nhất trong cả kế hoạch thi công, và bỏ qua nó thì toàn bộ
# kết quả H1 vô giá trị bất kể phần còn lại làm tốt tới đâu.
DISABLE_CONSTRAINT_GATE = _co_bat("DISABLE_CONSTRAINT_GATE")

# Tắt bước dò sự tồn tại của dòng theo mã số.
#
# Probe chạy EasyOCR trên các trang đã duyệt, nên nó CÓ chi phí — đó là cái
# giá của việc phân biệt "dòng vắng mặt" với "dòng đọc hỏng" mà không phải
# hỏi model. Cờ này để đo đúng cái giá đó, và để chạy nhanh khi không cần.
#
# TẮT LÀ AN TOÀN, KHÔNG PHẢI NGƯỢC LẠI: không có dấu vết thì mọi chỉ tiêu
# thiếu giá trị mang trạng thái "khong_doc_duoc", tức KHÔNG kết luận gì và
# không gán 0 cho ai. Hệ quả là đẳng thức phân rã lại hay bị bỏ qua như
# trước — mất tính năng, không sinh số sai.
DISABLE_LINE_PROBE = _co_bat("DISABLE_LINE_PROBE")

# Khoá tạm để nhánh VLM chuyển meta của nó ra tới route_document, tách khỏi
# các khoá dùng cho thong_tin_tai_lap(). Đặt tên thành hằng số thay vì viết
# chuỗi tay ở hai nơi, vì quên đồng bộ một trong hai chỗ sẽ làm early_stop
# lặng lẽ biến mất lần nữa — đúng lỗi vừa sửa.
META_VLM = "_meta_vlm"


def chon_chuan(standard: Standard | None) -> tuple[Standard, str]:
    """
    Chốt chuẩn mẫu biểu cho cả lượt chạy, kèm NGUỒN của kết luận đó.

    Trả về (chuẩn, nguồn) với nguồn thuộc tập đóng:
      "tham_so"  — người gọi chỉ định thẳng, khỏi phải đoán.
      "mac_dinh" — không ai chỉ định và đường chạy này chưa dò được, nên
                   lùi về DEFAULT_STANDARD.

    VÌ SAO PHẢI TRẢ CẢ NGUỒN chứ không chỉ trả chuẩn: hai lượt chạy có cùng
    `standard` nhưng một cái do người chỉ định còn một cái do lùi về mặc
    định là hai thứ khác hẳn nhau về độ tin cậy, và bảng kết quả phải tách
    được chúng. Nếu chỉ ghi chuẩn thì một lượt lùi mặc định trông y hệt một
    lượt nhận diện chắc chắn, và chế độ lỗi "nhận diện sai chuẩn" biến mất
    khỏi mọi phép đo — đúng thứ mà detect_standard() cố ý không đoán bừa để
    giữ lại.

    CHƯA CÓ NGUỒN "nhan_dien" Ở ĐÂY, và đó là hiện trạng chứ không phải ý
    đồ. detect_standard() cần text của trang, mà đường VLM (USE_OCR_FIRST
    tắt, tức cấu hình mặc định) không sinh ra text nào. Bước dò sự tồn tại
    của dòng sẽ mang OCR tới đường đó, và khi có thì thêm nguồn thứ ba vào
    đây.
    """
    if standard is not None:
        return standard, "tham_so"

    print(
        f"[STANDARD] Không ai chỉ định chuẩn và đường chạy này chưa dò được — "
        f"lùi về {DEFAULT_STANDARD.value}. Kết quả có thể dùng sai bảng mã số "
        f"dòng và sai bộ đẳng thức."
    )
    return DEFAULT_STANDARD, "mac_dinh"


def _ocr_mot_lan(page, bo_nho: dict, metrics=None) -> dict:
    """
    OCR một trang ĐÚNG MỘT LẦN, mọi lần hỏi sau đọc lại từ bộ nhớ.

    Cả text lẫn các ô số đều nằm trong CÙNG một kết quả, nên hai người gọi
    (`text_ocr_cua_trang` và `o_so_cua_trang`) dùng chung một lượt đọc. Tách
    ra thành hàm riêng để cái tính chất đó chỉ được viết ở MỘT chỗ: chép đôi
    thân hàm cache là cách quen thuộc nhất để một nhánh quên mất bộ nhớ rồi
    âm thầm nhân đôi khâu đắt nhất của pipeline.
    """
    so_trang = page["page"]
    if so_trang not in bo_nho:
        with timer(metrics, "ocr"):
            bo_nho[so_trang] = ocr_page_regions(page)
    return bo_nho[so_trang]


def text_ocr_cua_trang(page, bo_nho: dict, metrics=None) -> str:
    """
    Text OCR của một trang, đọc một lần rồi nhớ lại theo số trang.

    VÌ SAO CẦN GHI NHỚ. Khi USE_OCR_FIRST bật, cùng một trang bị OCR ở HAI
    chỗ: nhánh regex đọc nó để trích chỉ tiêu, rồi bước dò sự tồn tại của
    dòng đọc lại đúng trang ấy. EasyOCR chạy CPU và là khâu đắt nhất còn
    lại sau khi convert PDF với YOLO đã được cache, nên đọc hai lần là
    nhân đôi đúng chỗ đắt nhất.

    Khoá theo số trang chứ không theo object: `_remaining_pages()` yield
    lại chính các dict trong cached_pages nên so sánh đồng nhất cũng chạy,
    nhưng số trang là khoá ổn định và đọc log ra hiểu ngay.
    """
    return _ocr_mot_lan(page, bo_nho, metrics)["text"]


def vung_cua_trang(page, bo_nho: dict, metrics=None) -> list:
    """
    Kết quả OCR của một trang, CHIA THEO VÙNG BẢNG.

    Mỗi phần tử là {"region_index", "text", "o", "o_so"} với toạ độ ô đã quy
    về hệ của trang. Dùng CHUNG bộ nhớ với `text_ocr_cua_trang()` nên không
    tốn thêm một lượt OCR nào: lượt OCR phục vụ probe dò dòng đã phải chạy
    sẵn rồi, lấy thêm các ô chỉ là thôi vứt đi một thứ đã có trong tay.

    Đây là nguồn ứng viên ĐỌC LẠI TỜ GIẤY — thứ phân biệt nghiên cứu này với
    mọi paradigm sửa lỗi trước đó — và cũng là nguồn của việc neo toạ độ chỉ
    tiêu lẫn việc lan ký hiệu mẫu biểu.
    """
    return _ocr_mot_lan(page, bo_nho, metrics).get("vung", [])


def do_dau_vet_dong(
    cached_pages: list, standard: Standard, bo_nho_text: dict, metrics=None
) -> dict:
    """
    OCR các trang ĐÃ DUYỆT rồi dò từng chỉ tiêu theo mã số dòng.

    Trả về {field: DauVetDong} đã gộp qua mọi trang.

    VÌ SAO PHẢI CHẠY OCR Ở ĐÂY, dù nhánh OCR đang tắt mặc định. Câu hỏi
    "dòng này có trên biểu mẫu không" chỉ trả lời được từ chính tài liệu,
    và đường VLM không sinh ra một chữ text nào — nó gửi ảnh vùng thẳng cho
    model. Báo cáo mẫu lại là bản scan (`pdftotext -layout` chỉ ra 152 ký
    tự cho 12 trang), nên đường rẻ hơn là đọc text layer cũng không dùng
    được. Không có OCR thì không có oracle.

    HAI THỨ LÀM CHI PHÍ ĐÓ CHỊU ĐƯỢC:

    Một, probe dò theo MÃ SỐ chứ không theo tên chỉ tiêu. Mã số là chữ số,
    và `data/output/ocr_engine_easyocr.md` đo EasyOCR đạt 0,999 Levenshtein
    trên ô số. Chỗ EasyOCR hỏng là chữ tiếng Việt có dấu — thứ probe không
    dùng tới. Nên probe đứng vững ở đúng chỗ nhánh regex từng thất bại.

    Hai, nó chỉ chạy trên `cached_pages`, tức những trang pipeline THẬT SỰ
    đã duyệt. Convert PDF và YOLO đã chạy rồi và kết quả nằm sẵn trong đó,
    nên probe không mua lại hai khâu đắt nhất; dừng sớm ở trang 10 nghĩa là
    probe cũng chỉ đọc 10 trang.

    Tắt bằng DISABLE_LINE_PROBE=true. Khi tắt thì mọi chỉ tiêu thiếu giá
    trị đều mang trạng thái "khong_doc_duoc" — an toàn, vì đó là kết luận
    KHÔNG suy ra điều gì.
    """
    dau_vet_tung_trang: dict[str, list] = {khoa: [] for khoa in fields_for(standard)}

    for page in cached_pages:
        text = text_ocr_cua_trang(page, bo_nho_text, metrics)

        for khoa in dau_vet_tung_trang:
            dau_vet_tung_trang[khoa].append(tim_theo_ma_so(text, khoa, standard))

    return {
        khoa: tong_hop_dau_vet(cac_dau_vet)
        for khoa, cac_dau_vet in dau_vet_tung_trang.items()
    }


def lan_ky_hieu_mau(cached_pages: list, bo_nho_text: dict, metrics=None) -> dict:
    """
    Đọc ký hiệu mẫu trên từng vùng bảng đã duyệt rồi lan hậu tố hợp nhất/riêng.

    Duyệt theo ĐÚNG thứ tự trang rồi tới thứ tự vùng trong trang, vì phép lan
    có hướng: vùng không đọc được thừa hưởng của vùng đọc được TRƯỚC nó. Đảo
    thứ tự thì cùng một tài liệu cho hai kết luận khác nhau.

    Dùng chung bộ nhớ OCR với probe dò dòng nên không mua thêm lượt OCR nào.
    """
    return lan_ky_hieu(
        (page["page"], vung["region_index"], vung["text"])
        for page in cached_pages
        for vung in vung_cua_trang(page, bo_nho_text, metrics)
    )


def gom_vung(cached_pages: list, bo_nho_text: dict, metrics=None) -> dict:
    """
    {(số trang, chỉ số vùng): kết quả OCR của vùng đó} cho mọi trang đã duyệt.

    Khoá theo CẶP trang-vùng chứ không theo trang: `Provenance` ghi cả hai, và
    một trang có thể mang nhiều bảng. Gom cả trang lại thì ô của bảng khác lọt
    vào tập ứng viên — một con số hợp lệ của bảng khác thì vẫn hợp lệ, và
    không đẳng thức nào bắt được.

    Chỉ chạy trên `cached_pages` — những trang pipeline THẬT SỰ đã đọc — nên
    nó không mua lại convert PDF hay YOLO, và nhánh OCR dừng sớm ở trang 10
    thì nó cũng chỉ soi 10 trang.
    """
    return {
        (page["page"], vung["region_index"]): vung
        for page in cached_pages
        for vung in vung_cua_trang(page, bo_nho_text, metrics)
    }


def _vung_cua(ket_qua, vung_theo_khoa: dict | None) -> dict | None:
    """
    Vùng bảng mà một chỉ tiêu được đọc ra, theo Provenance. None nếu không rõ.

    Không biết chỉ tiêu đến từ vùng nào thì KHÔNG đoán: thà không có ứng viên
    còn hơn có ứng viên lấy từ nhầm bảng.
    """
    if not vung_theo_khoa or ket_qua is None:
        return None

    prov = getattr(ket_qua, "provenance", None)
    if prov is None:
        return None

    return vung_theo_khoa.get((prov.page, prov.region_index))


def dien_dong_vang_mat(gia_tri: dict, dau_vet: dict) -> tuple[dict, dict]:
    """
    Điền 0 cho dòng VẮNG MẶT, giữ None cho dòng chưa biết. Trả (giá trị, trạng thái).

    Ba trạng thái đi ra, tập ĐÓNG:
      "co_gia_tri"     — đọc được số.
      "vang_mat"       — biểu mẫu không có dòng đó, nên giá trị là 0.
      "khong_doc_duoc" — có dòng mà không đọc ra, hoặc probe không kết luận
                         được. Giá trị giữ None, nghĩa là CHƯA BIẾT.

    VÌ SAO VẮNG MẶT LÀ 0 CHỨ KHÔNG PHẢI None. TT99 mục 1.2.3 bảo đảm "các
    chỉ tiêu không có số liệu được miễn trình bày", tức văn bản pháp quy
    khẳng định phần vắng mặt không đóng góp vào tổng. Chính báo cáo VNM in
    công thức rút gọn của nó — `100 = 110 + 120 + 130 + 140 + 160`, bỏ hẳn
    mã 150 — nên doanh nghiệp lập báo cáo cũng hiểu vắng mặt là bằng không.

    Guideline gán nhãn mục 3.4 đã quy định gold ghi `0` cho ca này. Pipeline
    trả None thì `eval/metrics.py` tính là SAI ("None chỉ khớp với None"),
    nên field_accuracy và document_fully_correct bị trừ điểm oan trên mọi
    tài liệu có dòng vắng mặt. Đây là chỗ đóng khoảng cách đó.

    CHỖ NGUY HIỂM, ĐỌC KỸ TRƯỚC KHI SỬA: chỉ được gán 0 khi oracle KHẲNG
    ĐỊNH dòng vắng. Gán 0 cho ca "chưa biết" là bịa ra một con số, và nó
    không dừng ở đó — đẳng thức sẽ lệch đúng bằng giá trị thật bị mất, rồi
    C1/C2 đi tìm ứng viên sửa cho nhầm chỉ tiêu.
    """
    ra_gia_tri = dict(gia_tri)
    ra_trang_thai = {}

    for khoa, gia_tri_hien_co in gia_tri.items():
        if khoa == UNIT_KEY:
            continue

        if gia_tri_hien_co is not None:
            ra_trang_thai[khoa] = "co_gia_tri"
            continue

        # Không có dấu vết nghĩa là probe chưa chạy hoặc không phủ tới chỉ
        # tiêu này. Mặc định phải là "chưa biết", không phải "vắng mặt".
        ket_luan = dau_vet.get(khoa)
        if ket_luan is not None and ket_luan.trang_thai == "khong_thay_dong":
            ra_gia_tri[khoa] = 0
            ra_trang_thai[khoa] = "vang_mat"
        else:
            ra_trang_thai[khoa] = "khong_doc_duoc"

    return ra_gia_tri, ra_trang_thai


def khung_rong(standard: Standard) -> dict[str, FieldResult]:
    """
    Khung tích luỹ của router: mỗi chỉ tiêu một FieldResult chưa có gì.

    Router tích luỹ FieldResult chứ không tích luỹ giá trị trần, vì
    confidence và về sau là provenance phải sống sót qua bước merge. Trước
    đây merge trả về giá trị trần nên mọi thứ biết được về độ tin cậy của
    một con số đều bị vứt ngay tại đây.
    """
    return {khoa: FieldResult(value=None, confidence=0.0) for khoa in empty_result(standard)}


def gia_tri_tran(tich_luy: dict[str, FieldResult]) -> dict:
    """
    Chỉ giá trị, cho validate_result() và is_acceptable() — hai hàm cố ý
    không biết gì về confidence.
    """
    return {khoa: ket_qua.value for khoa, ket_qua in tich_luy.items()}


def _lap_cho_trong(tich_luy: dict[str, FieldResult], nguon: dict[str, FieldResult]) -> bool:
    """
    Lấp các chỉ tiêu còn trống, không ghi đè giá trị đã tìm được.
    Trả về True nếu có lấp được ít nhất một chỗ.
    """
    co_field_moi = False
    for khoa in tich_luy:
        if tich_luy[khoa].value is None and nguon.get(khoa) is not None:
            tich_luy[khoa] = nguon[khoa]
            co_field_moi = True
    return co_field_moi


def _ghi_lai_luot_vlm(ghi_lai, extraction: ExtractionResult) -> None:
    """
    Bồi thông tin tái lập của lượt gọi VLM vào dict do người gọi đưa.

    Bồi tại chỗ thay vì đổi kiểu trả về, cùng cách cached_pages vẫn làm:
    hai nhánh run_vlm và run_unconstrained đều trả về accumulator, và
    đổi cả hai sang trả tuple sẽ làm nơi gọi phải phân biệt hai dạng kết
    quả chỉ để lấy vài trường metadata.
    """
    if ghi_lai is None:
        return

    ghi_lai.update(
        model=extraction.model,
        temperature=extraction.temperature,
        n_samples=extraction.n_samples,
        prompt_hash=extraction.meta.get("prompt_hash"),
        standard=extraction.meta.get("standard"),
    )

    # early_stop đi theo đường RIÊNG, dưới khoá META_VLM, vì nó không phải
    # thông tin tái lập mà là thông tin về việc lượt chạy đã CẮT BỚT những
    # gì. thong_tin_tai_lap() có chữ ký cố định nên nhét thẳng vào sẽ nổ;
    # route_document() lấy nó ra khỏi dict trước khi gọi hàm đó.
    #
    # Vì sao phải mang ra tận đây: extract_fields_from_regions() ghi
    # meta["early_stop"] đúng như docstring của nó hứa, nhưng route_document
    # trước đây gán meta = meta của validate_result(), tức ĐÈ mất. Nên trên
    # đường chạy thật — API và CLI — không ai thấy được lượt chạy đã dừng ở
    # trang nào và còn thiếu field gì, đúng thứ mà cờ dừng sớm sinh ra để
    # không giấu.
    #
    # Hệ số đơn vị theo từng chỉ tiêu đi cùng đường này vì cùng một lý do: nó
    # là thứ nhánh trích xuất biết mà validate_result() không tự biết được.
    # route_document() phải lấy được nó TRƯỚC khi gọi validate_result(), nếu
    # không thì mọi ô lại bị nhân bằng đúng một hệ số mức tài liệu và cả cơ
    # chế buộc đơn vị theo bảng không có đường nào chạm tới con số.
    ghi_lai[META_VLM] = {
        "early_stop": extraction.meta.get("early_stop"),
        "he_so_don_vi_theo_truong": extraction.meta.get("he_so_don_vi_theo_truong", {}),
        "don_vi_theo_vung": extraction.meta.get("don_vi_theo_vung", []),
    }


def _tu_extraction(extraction: ExtractionResult) -> dict[str, FieldResult]:
    """
    Đưa ExtractionResult về dạng phẳng mà router merge được.

    Đơn vị tính nằm ở meta của ExtractionResult nhưng phải quay lại thành
    một khoá phẳng ở đây, vì validate_result() đọc nó từ chính dict giá
    trị — nó cần đơn vị TRƯỚC khi quy đổi bất cứ con số nào.
    """
    phang = dict(extraction.data)

    don_vi = extraction.meta.get(UNIT_KEY)
    if don_vi is not None:
        phang[UNIT_KEY] = FieldResult.khong_do(don_vi)

    return phang


def _he_so_cua_o_da_giu(
    tich_luy: dict[str, FieldResult], he_so_theo_truong: dict[str, int] | None
) -> dict[str, int] | None:
    """
    Lọc bản đồ hệ số đơn vị xuống còn những ô THẬT SỰ do nhánh VLM giữ.

    VÌ SAO KHÔNG DÙNG THẲNG BẢN ĐỒ CỦA NHÁNH VLM. Nhánh VLM đọc ra một chỉ
    tiêu không có nghĩa là giá trị cuối cùng của chỉ tiêu ấy đến từ đó:
    `run_vlm()` chỉ cho VLM ghi đè khi ô còn trống hoặc khi validate đã báo
    warning, nên với `USE_OCR_FIRST=true` một ô do regex điền vẫn có thể ở
    lại trong khi VLM cũng đọc được nó. Dùng bản đồ thô thì con số của OCR bị
    nhân bằng hệ số của một vùng mà nó chưa từng được đọc ra — một xuất xứ
    bịa, và bịa theo kiểu không có gì báo vì kết quả vẫn là một con số hợp lệ.

    Phân biệt bằng `provenance`: giá trị của nhánh VLM luôn mang nó, giá trị
    của nhánh OCR đi qua `FieldResult.khong_do()` nên không. Đó cũng đúng
    định nghĩa của provenance — biết được con số này đọc từ đâu trên tờ giấy.
    """
    if not he_so_theo_truong:
        return None

    return {
        khoa: he_so
        for khoa, he_so in he_so_theo_truong.items()
        if getattr(tich_luy.get(khoa), "provenance", None) is not None
    }


def _ocr_mot_trang(page, bo_nho_text: dict, metrics=None) -> dict[str, FieldResult]:
    """
    OCR một trang rồi trích bằng regex, trả về dạng FieldResult.

    Nhánh OCR không đo được confidence nên mọi giá trị đi ra với
    confidence 1.0 theo nghĩa "không đo được" — xem FieldResult.khong_do().
    """
    text = text_ocr_cua_trang(page, bo_nho_text, metrics)

    return {
        khoa: FieldResult.khong_do(gia_tri)
        for khoa, gia_tri in extract_all_fields(text).items()
        if gia_tri is not None
    }


def run_ocr_first(
    pages_iter, cached_pages: list, result: dict, standard: Standard,
    bo_nho_text: dict, metrics=None,
) -> dict:
    """
    Quét OCR theo từng trang, merge dần, dừng theo một trong hai điều kiện.

    Nhận generator chứ không nhận list: YOLO chỉ chạy cho trang nào thực
    sự được duyệt tới, nên dừng sớm ở trang 10 nghĩa là 45 trang còn lại
    không hề bị xử lý.

    cached_pages được bồi vào tại chỗ để nhánh VLM dùng lại kết quả YOLO,
    khỏi phải convert PDF và chạy detect lần hai.

    HAI ĐIỀU KIỆN DỪNG, và cái thứ hai mới là cái thật sự chặn được vòng lặp:

    1. `is_acceptable()` đúng — kết quả đã đủ và hợp lệ. Đo được **0/9 lần**
       trên tập gold 27/08/2026, vì điều kiện này đòi regex khớp tên chỉ tiêu
       tiếng Việt có dấu, đúng chỗ EasyOCR đọc hỏng. Trước khi có điều kiện 2,
       hàm này vì thế chạy như một vòng lặp không có trần và quét tới trang
       cuối của mọi tài liệu.
    2. `PATIENCE_PAGES_OCR` trang liên tiếp không trích thêm được chỉ tiêu nào.
       Không gác sau `has_required_fields()`, nên bộ đếm chạy ngay từ trang 1 —
       và vì mấy trang đầu báo cáo niêm yết là bìa với mục lục, ngưỡng phải đủ
       rộng để không dừng TRƯỚC khi tới bảng đầu tiên. Xem ghi chú ở hằng số.

    Trả về `(result, thông tin dừng)`. Thông tin dừng đi ra TƯỜNG MINH thay vì
    để người đọc suy từ `len(cached_pages)`: một lượt dừng vì kiên nhẫn và một
    lượt quét hết tài liệu 8 trang cho ra cùng con số trang, mà hai chuyện đó
    khác hẳn nhau khi đối chiếu chi phí giữa các lượt chạy.
    """
    trang_khong_co_field_moi = 0
    dung_som = {"da_dung_som": False, "ly_do": "het_trang", "trang_cuoi": None}

    for page in pages_iter:
        cached_pages.append(page)
        co_field_moi = _lap_cho_trong(result, _ocr_mot_trang(page, bo_nho_text, metrics))
        dung_som["trang_cuoi"] = page["page"]

        quy_uoc, _ = quy_uoc_cua_luot(gia_tri_tran(result), bo_nho_text)
        if is_acceptable(gia_tri_tran(result), standard, quy_uoc):
            print(f"--- OCR đã đủ và hợp lệ, dừng ở trang {page['page']} ---")
            dung_som.update(da_dung_som=True, ly_do="du_va_hop_le")
            break

        trang_khong_co_field_moi = 0 if co_field_moi else trang_khong_co_field_moi + 1

        if trang_khong_co_field_moi >= PATIENCE_PAGES_OCR:
            print(
                f"--- OCR: {PATIENCE_PAGES_OCR} trang liên tiếp không có chỉ tiêu "
                f"mới -> dừng ở trang {page['page']}. Nhánh VLM đọc tiếp từ đây ---"
            )
            dung_som.update(da_dung_som=True, ly_do="het_bang_de_doc")
            break

    return result, dung_som


def _remaining_pages(pages_iter, cached_pages: list):
    """
    Trang đã đọc ở nhánh OCR thì dùng lại, phần chưa duyệt thì đọc tiếp từ
    generator — không convert PDF hay chạy YOLO lần nữa.
    """
    yield from cached_pages
    for page in pages_iter:
        cached_pages.append(page)
        yield page


def run_unconstrained(
    pages_iter, cached_pages: list, result: dict, standard: Standard,
    bo_nho_text: dict, metrics=None, ghi_lai=None,
) -> dict:
    """
    Chạy ĐÚNG MỘT nhánh, không cổng ràng buộc, không fallback.

    Nhánh nào là do USE_OCR_FIRST quyết định. Điểm khác biệt với đường
    thường không phải ở việc bỏ fallback, mà ở chỗ KHÔNG một quyết định
    nào trong đường đi này đọc kết quả của validate_result(). Đầu ra vì
    vậy chưa từng bị ràng buộc kế toán chạm vào, và đó là điều kiện để
    con số AUROC ở H1 có nghĩa.

    run_ocr_first() có HAI điều kiện dừng và đường này bỏ CẢ HAI, nhưng vì
    hai lý do khác nhau — đừng gộp lại:

      * `is_acceptable()` phải bỏ vì nó quyết định đọc tới trang nào dựa
        trên chính tín hiệu đang được đem đi đánh giá. Đây là lý do bắt buộc.
      * `PATIENCE_PAGES_OCR` thì KHÔNG dính vào ràng buộc — nó đếm chỉ tiêu
        mới, tức tính đầy đủ. Bỏ nó ở đây là một lựa chọn THẬN TRỌNG, không
        phải một tất yếu: đường đo đọc trọn tài liệu nên không chỉ tiêu nào
        vắng mặt vì chưa được quét tới.

    Cái giá của lựa chọn đó là đường đo CHẬM HƠN hẳn đường phục vụ, và con
    số thời gian của hai đường vì thế không so với nhau được.

    KHÔNG bỏ điều kiện dừng sớm theo PATIENCE_PAGES bên trong nhánh VLM:
    cái đó cũng dựa trên tính đầy đủ chứ không phải tính hợp lệ theo ràng
    buộc. Nó là một nguồn thiên lệch khác và được xử lý riêng trong danh
    mục dọn dẹp.
    """
    if USE_OCR_FIRST:
        for page in pages_iter:
            cached_pages.append(page)
            _lap_cho_trong(result, _ocr_mot_trang(page, bo_nho_text, metrics))

        return result

    extraction = extract_fields_from_regions(
        _remaining_pages(pages_iter, cached_pages), metrics, standard
    )
    _ghi_lai_luot_vlm(ghi_lai, extraction)
    _lap_cho_trong(result, _tu_extraction(extraction))

    return result


def run_vlm(
    pages_iter, cached_pages: list, result: dict, standard: Standard,
    quy_uoc: QuyUocDau, metrics=None, ghi_lai=None,
) -> dict:
    """
    Chạy nhánh VLM và trộn kết quả vào result.

    Hai lý do khiến kết quả trước đó không đáng tin, xử lý khác nhau:
      1. Field còn None       -> VLM lấp chỗ trống.
      2. Validate báo warning -> giá trị đang có tồn tại nhưng SAI, nên
         phải cho VLM ghi đè. Nếu chỉ lấp chỗ None, con số sai vẫn nằm
         nguyên đó và cả validation gate thành vô nghĩa: tốn tiền gọi VLM
         rồi vứt kết quả đúng đi.
    """
    has_warnings = bool(validate_result(gia_tri_tran(result), standard, quy_uoc)["warnings"])

    extraction = extract_fields_from_regions(
        _remaining_pages(pages_iter, cached_pages), metrics, standard
    )
    _ghi_lai_luot_vlm(ghi_lai, extraction)
    tu_vlm = _tu_extraction(extraction)

    for key in result:
        moi = tu_vlm.get(key)
        if moi is None or moi.value is None:
            continue
        if result[key].value is None or has_warnings:
            result[key] = moi

    return result


def van_ban_da_ocr(bo_nho_text: dict) -> str:
    """
    Nối text OCR của mọi trang đã đọc, để dò công thức mã 60 in trên biểu mẫu.

    Đọc từ bộ nhớ OCR sẵn có chứ không OCR lại: công thức nằm trong nhãn dòng
    của chính bảng B02, tức trang nào chứa mã 60 thì trang đó đã được đọc rồi.
    """
    return "\n".join(
        muc["text"] for muc in bo_nho_text.values()
        if isinstance(muc, dict) and isinstance(muc.get("text"), str)
    )


def quy_uoc_cua_luot(gia_tri: dict, bo_nho_text: dict) -> tuple[QuyUocDau, str]:
    """
    Quy ước dấu của tài liệu đang chạy, kèm nguồn đã dùng để chốt nó.

    Tính LẠI ở mỗi chỗ cần thay vì chốt một lần đầu lượt chạy, và đó là chủ
    đích: cả hai nguồn — công thức in và dấu ngoặc mã 11 — chỉ có sau khi đã
    đọc được trang, nên chốt trước lúc trích xuất là chốt trên hư không. Hàm
    rẻ (một regex trên text đã có sẵn) nên gọi lại nhiều lần không tốn gì.
    """
    return xac_dinh_quy_uoc(van_ban_da_ocr(bo_nho_text), gia_tri)


def chay_tang_repair(
    data: dict, result: dict, standard: Standard, quy_uoc: QuyUocDau,
    vung_theo_khoa: dict | None = None
) -> tuple[dict, dict]:
    """
    Chạy tầng định vị/sửa lỗi trên bộ giá trị ĐÃ ép kiểu và quy đổi.

    Trả về `(giá trị sau sửa, certificate)`. Certificate luôn được trả, kể cả
    khi không sửa gì — nó là bản khai những gì tầng này đã làm, và một tầng sửa
    số mà không khai ra thì không kiểm toán lại được.

    ỨNG VIÊN SINH TỪ TÀI LIỆU, không từ donor. Đây là mệnh đề trung tâm của cả
    nghiên cứu, nên nguồn ứng viên ở đây phải là những gì ĐỌC ĐƯỢC từ trang
    giấy: phiếu bầu của VLM (`votes`), biến thể nhầm chữ số, biến thể dấu, biến
    thể bậc đơn vị. Không có nguồn nào lấy số từ tài liệu KHÁC.

    `vung_theo_khoa` là {(trang, vùng): kết quả OCR của vùng} do `gom_vung()`
    dựng từ chính lượt OCR đã chạy cho probe dò dòng. Có nó thì nguồn ĐỌC LẠI
    TỜ GIẤY bật; không có thì nó tắt, và certificate tự khai là tắt
    (`o_lan_can`) chứ không im lặng — đo trên tầng XBRL, đó là nguồn duy nhất
    từng lấy lại được giá trị thật ở những ca các nguồn khác chịu thua, nên
    một lượt chạy thiếu nó KHÔNG được đọc như một lượt đầy đủ.

    Ô lân cận chỉ lấy trong ĐÚNG VÙNG BẢNG mà chỉ tiêu đó được đọc ra, và tâm
    của hình chữ thập là bbox do `neo_bbox()` dò ra — KHÔNG phải
    `Provenance.bbox`, vốn là bbox của cả vùng nên mọi ô đều tương đương và
    trần cắt thành bốc thăm. Cách neo được ghi vào certificate (`neo`) vì ba
    cách neo cho ba mức tin cậy khác hẳn nhau.
    """
    co_gia_tri = [k for k, v in data.items() if v is not None and k != UNIT_KEY]
    A, field_order = build_matrix(co_gia_tri, identities_for(standard, quy_uoc))

    if A.shape[0] == 0:
        return data, {"da_chay": True, "verdict": "ABSTAIN", "ma_ly_do": "thieu_gia_tri",
                      "ly_do": "không dựng được đẳng thức nào từ các chỉ tiêu đọc được"}

    gia_tri = {k: data[k] for k in field_order}
    neo: dict[str, str] = {}
    ung_vien = {}
    for k in field_order:
        vung = _vung_cua(result.get(k), vung_theo_khoa)
        if vung is None:
            neo[k] = "khong_co_vung"
            bbox = None
        else:
            bbox, neo[k] = neo_bbox(k, gia_tri[k], vung, standard)
        ung_vien[k] = sinh_ung_vien(
            k,
            gia_tri[k],
            o_lan_can=[] if vung is None else vung["o_so"],
            votes=getattr(result.get(k), "votes", {}),
            bbox_dang_xet=bbox,
        )
    do = diagnose(
        gia_tri,
        ung_vien,
        A,
        field_order,
        confidences={k: result[k].confidence for k in field_order if k in result},
    )

    chung_chi = {
        "da_chay": True,
        "verdict": do.verdict,
        "nguon_dinh_vi": do.nguon_dinh_vi,
        "ma_ly_do": do.ma_ly_do,
        "ly_do": do.ly_do_abstain,
        "so_dang_thuc": int(A.shape[0]),
        "so_chi_tieu": len(field_order),
        "solve_time_s": round(do.solve_time_s, 4),
        "o_lan_can": bool(vung_theo_khoa),
        # Neo khai THEO TỪNG CHỈ TIÊU, không gộp thành một cờ. Một lượt chạy
        # neo được mọi chỉ tiêu bằng khớp giá trị và một lượt toàn `khong_neo`
        # cho ra cùng một câu 'đã bật nguồn ô lân cận', trong khi lượt sau thực
        # chất đang cắt ứng viên bằng bốc thăm.
        "neo": neo,
        # Luật dấu khai riêng, kể cả khi nó im lặng: tỷ lệ im lặng là số đo
        # phạm vi áp dụng của nó, và số đó chỉ có nếu ca im lặng cũng được ghi.
        "luat_dau": (
            None
            if do.luat_dau is None
            else {
                "trang_thai": do.luat_dau.trang_thai,
                "truong": do.luat_dau.truong,
                "cac_ung_vien": do.luat_dau.cac_ung_vien,
                "so_dang_thuc_con_lech": do.luat_dau.so_dang_thuc_con_lech,
            }
        ),
        # Ghi CẢ giá trị trước và sau. Chỉ ghi tên chỉ tiêu bị đổi thì về sau
        # không dựng lại được đầu ra chưa sửa, mà đó chính là bộ số H1 cần.
        "da_doi": {
            ten: {
                "truoc": gia_tri[ten],
                "sau": uv.value,
                "nguon_ung_vien": uv.source,
                "cost": uv.cost,
            }
            for ten, uv in do.changed_fields.items()
        },
    }

    if do.verdict != "REPAIRED":
        return data, chung_chi

    return {**data, **{ten: uv.value for ten, uv in do.changed_fields.items()}}, chung_chi


def route_document(
    file_path: str, save: bool = True, standard: Standard | None = None
) -> ExtractionResult:
    """
    Chạy trọn pipeline cho một tài liệu.

    Trả về ExtractionResult chứ không phải dict giá trị trần: confidence
    của từng chỉ tiêu là đầu vào bắt buộc của H1 và H2, còn các giá trị
    THUA phiếu là tập ứng viên sửa lỗi. Trả về dict trần đồng nghĩa với
    việc vứt cả hai ngay tại cửa ra, rồi phải gọi lại VLM để có lại.

    Giá trị trong .data đã ÉP KIỂU SỐ và QUY ĐỔI VỀ ĐỒNG, còn .warnings
    gộp cả cảnh báo của bước bỏ phiếu lẫn cảnh báo của validate_result().

    save — có ghi data/output/<stem>_routed.json hay không.

    Đường CLI để mặc định True vì file đó CHÍNH LÀ output của lệnh.
    Đường API truyền False: client đã nhận dữ liệu qua HTTP và
    metrics.jsonl đã ghi lại lượt chạy, nên file kia là bản sao không ai
    đọc. Tên nó còn mang hậu tố ngẫu nhiên của request
    (report_a3f2b1c9_routed.json) nên cũng không tra cứu bằng tay được —
    chỉ để lại rác trong data/output/, mỗi request một file, không ai dọn.
    """
    # Nhánh VLM luôn có thể được gọi làm fallback, kể cả khi USE_OCR_FIRST
    # bật, nên thiếu config là hỏng chắc chắn. Kiểm ngay đây — trước cả
    # RunMetrics — để không ghi lại một "lượt chạy" vốn chưa từng bắt đầu,
    # và để lỗi nổ ra trước khi tốn công convert PDF + chạy YOLO.
    require_config()

    # Chốt chuẩn MỘT lần cho cả lượt chạy, trước khi đụng tới trang nào.
    # Prompt VLM, bảng mã số dòng, bộ đẳng thức và câu cảnh báo đều phải
    # nói về cùng một chuẩn; để mỗi nơi tự quyết là cách chắc chắn nhất để
    # chúng lệch nhau mà không ai thấy.
    standard, nguon_chuan = chon_chuan(standard)

    metrics = RunMetrics(file_path)

    try:
        pages_iter = iter_table_regions(file_path, metrics)
        cached_pages: list = []
        result = khung_rong(standard)

        # Text OCR dùng chung cho nhánh regex và bước dò dòng, để một trang
        # không bị đọc hai lần khi USE_OCR_FIRST bật.
        bo_nho_text: dict = {}
        thong_tin_vlm: dict = {}
        # Khai trước, tường minh: một lượt chạy KHÔNG bật nhánh OCR phải khác
        # được với một lượt bật mà quét hết tài liệu. Để khoá này vắng mặt ở ca
        # đầu thì người đọc metrics.jsonl phải suy từ ocr_first, và suy thì sai.
        dung_som_ocr = {"da_dung_som": False, "ly_do": "khong_chay", "trang_cuoi": None}

        if DISABLE_CONSTRAINT_GATE:
            print("--- CỔNG RÀNG BUỘC ĐANG TẮT: chế độ ĐO, không dùng để phục vụ ---")
            result = run_unconstrained(
                pages_iter, cached_pages, result, standard, bo_nho_text, metrics, thong_tin_vlm
            )
        else:
            if USE_OCR_FIRST:
                result, dung_som_ocr = run_ocr_first(
                    pages_iter, cached_pages, result, standard, bo_nho_text, metrics
                )

            quy_uoc_cong, _ = quy_uoc_cua_luot(gia_tri_tran(result), bo_nho_text)
            if not is_acceptable(gia_tri_tran(result), standard, quy_uoc_cong):
                if USE_OCR_FIRST:
                    missing = [k for k, kq in result.items() if kq.value is None]
                    print(f"--- OCR chưa đạt (thiếu/nghi ngờ: {missing}), chuyển sang VLM ---")
                result = run_vlm(
                    pages_iter, cached_pages, result, standard, quy_uoc_cong, metrics,
                    thong_tin_vlm,
                )

        # Ép kiểu số TRƯỚC khi lưu và trả về. VLM đôi khi trả số dưới dạng
        # chuỗi, nên nếu lưu thẳng result thô thì file _routed.json và
        # response HTTP sẽ khác nhau về kiểu dữ liệu cho cùng một lượt
        # chạy — rất khó lần khi đi đối chiếu.
        # Dò sự tồn tại của dòng TRƯỚC khi kiểm đẳng thức, vì kết quả dò
        # quyết định chỉ tiêu nào được điền 0. Điền sau bước kiểm thì đẳng
        # thức vẫn bị bỏ qua đúng như cũ và cả cơ chế thành vô nghĩa.
        dau_vet = (
            {}
            if DISABLE_LINE_PROBE
            else do_dau_vet_dong(cached_pages, standard, bo_nho_text, metrics)
        )

        # Lan ký hiệu mẫu đi CÙNG probe dò dòng, và tắt cùng nó. Cả hai sống
        # nhờ đúng một lượt OCR, nên khi người dùng tắt probe để khỏi mua OCR
        # thì chạy cái này là mua lại đúng thứ vừa từ chối. Trạng thái
        # 'không chạy' ghi tường minh, để nó không lẫn với 'chạy mà không đọc
        # được ký hiệu nào' — hai chuyện khác hẳn nhau.
        ky_hieu = (
            {"loai": None, "nguon": "khong_chay", "theo_vung": {}, "mau_thuan": []}
            if DISABLE_LINE_PROBE
            else lan_ky_hieu_mau(cached_pages, bo_nho_text, metrics)
        )
        gia_tri_da_dien, trang_thai_chi_tieu = dien_dong_vang_mat(
            gia_tri_tran(result), dau_vet
        )

        # Lấy meta của nhánh VLM ra Ở ĐÂY, trước validate_result(), vì trong
        # đó có hệ số đơn vị theo từng chỉ tiêu mà bước quy đổi cần. Bản trước
        # lấy sau khi đã chấm xong — đủ cho early_stop vốn chỉ để ghi lại,
        # nhưng không đủ cho một dữ kiện tham gia vào chính phép tính.
        meta_vlm = thong_tin_vlm.pop(META_VLM, {})

        # validate_result() sửa dấu ba dòng khấu trừ ngay sau bước ép kiểu —
        # xem mục 1b trong đó. Ở đây không đụng vào dấu: trước khi ép kiểu,
        # giá trị VLM còn có thể là chuỗi.
        #
        # Ô nào nhánh VLM đọc ra thì quy đổi bằng hệ số của ĐÚNG bảng đã sinh
        # ra nó; ô do nhánh OCR điền lùi về hệ số mức tài liệu. Đó là hành vi
        # đúng chứ không phải chỗ hụt: nhánh OCR không ghi lại nó đọc ô ấy từ
        # vùng nào, nên gán cho nó hệ số của một vùng cụ thể sẽ là bịa ra một
        # xuất xứ không ai kiểm được.
        #
        # Bản đồ hệ số ĐI VÀO chấm điểm được rút khỏi meta_vlm ngay sau khi
        # dùng, vì validate_result() trả ra một khoá cùng tên mang bản đồ hệ
        # số ĐÃ THẬT SỰ NHÂN. Hai bản đồ gần giống nhau nhưng không bằng nhau
        # — ô nhánh VLM đọc được rồi bị bước sau bỏ đi chỉ có trong bản đầu —
        # và để cả hai cùng tên trong một dict là mời người đọc sau này lấy
        # nhầm cái không nói lên điều đã xảy ra với con số.
        # Chốt quy ước dấu TRÊN BỘ GIÁ TRỊ CUỐI CÙNG, sau khi cả hai nhánh đã
        # điền xong: mã 11 có thể do nhánh VLM lấp vào sau nhánh OCR, và quy
        # ước đọc từ một ô chưa có thì đọc được gì.
        quy_uoc, nguon_quy_uoc = quy_uoc_cua_luot(gia_tri_da_dien, bo_nho_text)
        da_kiem = validate_result(
            gia_tri_da_dien,
            standard,
            quy_uoc,
            _he_so_cua_o_da_giu(result, meta_vlm.pop("he_so_don_vi_theo_truong", None)),
        )
        # Nguồn đã chốt quy ước là khoá TƯỜNG MINH, không suy từ chỗ khác:
        # `cong_thuc` và `ma_11` cho hai mức tin cậy khác hẳn, còn `mau_thuan`
        # là ca đáng đếm riêng vì nó chính là giới hạn đã khai của thiết kế.
        da_kiem["meta"]["nguon_quy_uoc_dau"] = nguon_quy_uoc
        data = da_kiem["data"]

        # TẦNG REPAIR chạy SAU khi validate_result() đã chấm xong, không phải
        # trước. Thứ tự này là điều kiện để H1 còn đo được: `warnings` ở đây
        # ghi lại tình trạng vi phạm ràng buộc của đầu ra CHƯA sửa, và đó đúng
        # là biến mà H1 đem so với confidence. Chạy repair trước rồi mới chấm
        # thì cột warnings gần như phẳng, và phép so mất nghĩa.
        #
        # Cũng vì thế tầng này không chạy ở chế độ đo: DISABLE_CONSTRAINT_GATE
        # bật nghĩa là lượt chạy đang phục vụ phép đo H1, và ở đó mọi thứ đọc
        # ràng buộc đều phải im.
        chung_chi_repair = {"da_chay": False, "ly_do": "tang_repair_dang_tat"}
        if BAT_TANG_REPAIR and not DISABLE_CONSTRAINT_GATE:
            data, chung_chi_repair = chay_tang_repair(
                data, result, standard, quy_uoc,
                gom_vung(cached_pages, bo_nho_text, metrics),
            )

        # Ghi giá trị đã ép kiểu và quy đổi NGƯỢC vào FieldResult, giữ
        # nguyên confidence và votes. Nếu bỏ qua bước này thì .values() trả
        # về số thô chưa quy đổi trong khi .data lại nói đã quy đổi — hai
        # nguồn sự thật lệch nhau trong cùng một object.
        ket_qua_cuoi = {
            khoa: FieldResult(
                value=data.get(khoa),
                confidence=result[khoa].confidence,
                votes=result[khoa].votes,
                provenance=result[khoa].provenance,
            )
            for khoa in result
            if khoa != UNIT_KEY
        }

        # HỢP NHẤT meta, không đè. Bản trước gán thẳng meta = da_kiem["meta"]
        # nên mọi thứ nhánh trích xuất biết mà validate_result không biết —
        # early_stop và prompt_hash — bị vứt ngay tại cửa ra.
        #
        # standard và nguon_chuan ghi thành HAI khoá riêng: biết chuẩn nào
        # được dùng là chưa đủ, còn phải biết kết luận đó đến từ đâu. Một
        # lượt lùi về mặc định và một lượt do người chỉ định cho ra cùng chữ
        # "TT99", và gộp chúng lại là xoá mất một chế độ lỗi khỏi phép đo.
        extraction = ExtractionResult(
            data=ket_qua_cuoi,
            meta={
                **meta_vlm,
                **da_kiem["meta"],
                "standard_nguon": nguon_chuan,
                # Vì sao trạng thái phải đi kèm giá trị: sau bước điền, một
                # số 0 trong data có thể là "doanh nghiệp khai bằng 0" hoặc
                # "biểu mẫu không có dòng đó". Hai chuyện khác hẳn nhau khi
                # phân tích, và không suy ra được từ chính con số 0.
                "trang_thai_chi_tieu": trang_thai_chi_tieu,
                "line_probe": not DISABLE_LINE_PROBE,
                # Bộ báo cáo là hợp nhất hay riêng, đọc từ ký hiệu mẫu và lan
                # sang các bảng không đọc được. Đi kèm cả nguồn lẫn danh sách
                # mâu thuẫn: một kết luận lan từ trang khác và một kết luận đọc
                # được tại chỗ không cùng độ tin cậy.
                "ky_hieu_mau": ky_hieu,
                # Certificate của tầng repair đi ra CÙNG kết quả, không nằm
                # riêng ở log: một con số đã bị sửa mà người đọc kết quả không
                # thấy dấu vết thì đúng bằng một con số bịa.
                "chung_chi_repair": chung_chi_repair,
            },
            warnings=da_kiem["warnings"],
        )

        if save:
            save_result(file_path, data)

        # constraint_gate ghi thành khoá TƯỜNG MINH trong metrics: một lượt
        # chạy ở chế độ đo và một lượt chạy phục vụ cho ra dữ liệu không so
        # được với nhau, nên người đọc metrics.jsonl phải phân biệt được hai
        # loại đó bằng một khoá có sẵn chứ không phải suy đoán.
        metrics.set_info(
            pages_processed=len(cached_pages),
            ocr_first=USE_OCR_FIRST,
            # Vì sao ba khoá này phải tường minh: chúng là ba cách khác nhau để
            # một lượt chạy đọc ít trang hơn lượt khác, và gộp lại thì không
            # đối chiếu được chi phí giữa hai lượt. `probe_so_trang` đo đúng
            # cái giá mà bộ đếm kiên nhẫn của nhánh OCR đánh đổi lấy tốc độ —
            # probe chỉ đọc cached_pages, nên dừng sớm hơn là thấy ít hơn.
            ocr_dung_som=dung_som_ocr,
            probe_so_trang=0 if DISABLE_LINE_PROBE else len(cached_pages),
            constraint_gate=not DISABLE_CONSTRAINT_GATE,
            tang_repair=chung_chi_repair.get("da_chay", False),
            **thong_tin_tai_lap(**thong_tin_vlm),
        )
        metrics.status = "ok"
        return extraction

    except BaseException:
        # Bắt cả KeyboardInterrupt/SystemExit: lượt chạy không đi hết
        # pipeline thì dòng metrics của nó không được trông như bình
        # thường. Đánh dấu ở đây rồi raise lại — không nuốt lỗi.
        metrics.status = "error"
        raise

    finally:
        metrics.save()
        merge_into_totals(metrics)
        print(metrics.summary())


def is_acceptable(result: dict, standard: Standard, quy_uoc: QuyUocDau) -> bool:
    """
    Kết quả có đáng tin để dừng sớm / khỏi cần fallback VLM không?

    standard bắt buộc vì điều kiện 2 gọi validate_result(), và bộ đẳng thức
    khác nhau giữa hai chuẩn kể từ Mốc 1. Cổng này quyết định có gọi VLM hay
    không, nên kiểm bằng đẳng thức của nhầm chuẩn sẽ vừa bỏ sót lỗi thật vừa
    gọi VLM cho những ca vốn đã đúng.

    Hai điều kiện, cả hai đều phải đạt:
    1. Đủ các field BẮT BUỘC (theo FIELD_RULES). Field bổ sung thiếu vẫn
       chấp nhận được — danh sách chỉ tiêu càng dài thì càng dễ thiếu một
       chỉ tiêu phụ, và nếu bắt đủ hết mới cho qua thì lần nào cũng phải
       fallback sang VLM.
    2. Validate không sinh warning. Chỉ kiểm tra "có giá trị" là chưa đủ,
       vì regex có thể bắt trúng một con số SAI (không phải None) và
       router sẽ tin dùng luôn mà không bao giờ gọi VLM.
    """
    if not has_required_fields(result):
        return False

    return not validate_result(result, standard, quy_uoc)["warnings"]


def save_result(file_path: str, result: dict) -> Path:
    out_path = Path("data/output") / (Path(file_path).stem + "_routed.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return out_path


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python router.py <file_path>")
        sys.exit(1)

    # Console Windows mặc định cp1252 nên in tiếng Việt sẽ nổ.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print(f"--- Nhánh OCR: {'BẬT' if USE_OCR_FIRST else 'TẮT'} (USE_OCR_FIRST) ---")
    print(
        f"--- Cổng ràng buộc: {'TẮT (chế độ ĐO)' if DISABLE_CONSTRAINT_GATE else 'BẬT'} "
        f"(DISABLE_CONSTRAINT_GATE) ---"
    )

    input_path = sys.argv[1]
    ket_qua = route_document(input_path)

    print(json.dumps(ket_qua.values(), ensure_ascii=False, indent=2))
    if ket_qua.warnings:
        print("\nCảnh báo:")
        for canh_bao in ket_qua.warnings:
            print(f"  - {canh_bao}")
