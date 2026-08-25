"""
Đọc con số như nó được IN trên báo cáo tài chính Việt Nam.

Tách khỏi công cụ gán nhãn vì đây là phần duy nhất trong đó có quy tắc thật
để sai, và nó phải test được mà không cần dựng máy chủ.

Mọi quy tắc dưới đây chép từ `ANNOTATION-GUIDELINE.md` mục 3.3 và 3.4, không
tự nghĩ ra. Chỗ nào guideline không nói thì hàm trả trạng thái `khong_ro` và
để người quyết, chứ không đoán — người gán nhãn đoán hộ máy chính là kiểu
nhiễm ground truth mà Luật 1 sinh ra để chặn.
"""

import re

# Ba trạng thái ĐÓNG của việc đọc một ô. Trả về tường minh thay vì để người
# đọc suy từ việc giá trị bằng None hay bằng 0 — hai thứ đó mang nghĩa khác
# hẳn nhau trong tập gold: 0 là "biết, và bằng không", None là "chưa biết".
SO = "so"                    # đọc ra một con số
BANG_KHONG = "bang_khong"    # ô trống hoặc dấu gạch — guideline mục 3.4 ghi 0
KHONG_DOC_RA = "khong_doc_ra"  # có dòng nhưng mờ/rách/che — ghi null
KHONG_RO = "khong_ro"        # chuỗi không khớp quy tắc nào, người phải xử

# Ô trống hoặc một dấu gạch bất kỳ đều là "có dòng, không phát sinh trong kỳ".
# Liệt kê cả bốn dấu gạch vì báo cáo in ra đủ loại và OCR còn đổi qua lại
# giữa chúng: gạch nối, gạch ngang en, em, và dấu trừ toán học.
_DAU_GACH = {"-", "–", "—", "−"}

# Người gán nhãn gõ đúng một trong các chuỗi này khi có dòng mà đọc không ra.
# Cố ý KHÔNG nhận chuỗi rỗng vào nhóm này: rỗng nghĩa là chưa gõ gì, và gộp
# hai thứ đó lại sẽ biến mọi ô bỏ quên thành "đã xem xét và chịu".
_KHONG_DOC_RA = {"?", "??", "null", "NULL", "n/a", "N/A"}

_CHI_SO = re.compile(r"^[0-9.,\s]+$")


def _bo_khoang_trang(raw: str) -> str:
    """Bỏ mọi loại khoảng trắng, kể cả khoảng trắng không ngắt của bản dán."""
    return re.sub(r"[\s ]+", "", raw)


def _nhom_hop_le(chuoi: str, dau: str) -> bool:
    """
    Chuỗi có đúng dạng phân nhóm hàng nghìn không: `1.234.567`, `29.403`.

    Cần kiểm riêng vì cách làm hiển nhiên — bỏ hết dấu phân nhóm rồi đọc số
    — nuốt trôi cả những chuỗi hỏng: `1..2` thành `12`, `1.23.4` thành
    `1234`. Cả hai đều là ca người gõ nhầm, và trả về một con số trông hợp
    lệ cho ca gõ nhầm chính là cách tập gold nhiễm lỗi câm.
    """
    return bool(re.fullmatch(rf"\d{{1,3}}(?:{re.escape(dau)}\d{{3}})+", chuoi))


def _tach_phan_thap_phan(chuoi: str) -> tuple[str, str] | None:
    """
    Tách phần nguyên khỏi phần thập phân theo quy ước Việt Nam.

    Dấu chấm là dấu phân nhóm hàng nghìn, dấu phẩy là dấu thập phân — ngược
    với quy ước Anh Mỹ. Nhưng báo cáo dịch sang tiếng Anh thì lại theo quy
    ước kia, và cả hai loại đều nằm trong tập gold, nên không thể chọn cứng
    một quy ước.

    Cách phân xử, theo đúng thứ tự:

      1. Có CẢ hai dấu -> dấu xuất hiện SAU cùng là dấu thập phân, dấu kia
         là phân nhóm. Quy tắc này đúng với cả hai quy ước và không cần biết
         báo cáo theo quy ước nào.
      2. Chỉ có một loại dấu, xuất hiện NHIỀU LẦN -> chắc chắn là phân nhóm.
      3. Chỉ có một loại dấu, xuất hiện một lần, và sau nó đúng 3 chữ số ->
         coi là phân nhóm. Đây là ca thật sự nhập nhằng: `1.234` có thể là
         một nghìn hai trăm ba mươi tư hoặc 1,234. Chọn phân nhóm vì báo cáo
         tài chính ghi bằng ĐỒNG gần như không bao giờ có phần thập phân, và
         chọn sai theo hướng này lệch 1000 lần — đủ lớn để đẳng thức bắt
         được, trong khi chọn sai hướng kia cho ra con số trông hợp lý.
      4. Còn lại -> dấu thập phân.

    Trả None khi chuỗi không khớp dạng nào — `1..2`, `1.23.4`. Không đoán:
    xem `_nhom_hop_le()`.
    """
    co_cham, co_phay = "." in chuoi, "," in chuoi

    if not co_cham and not co_phay:
        return (chuoi, "") if chuoi.isdigit() else None

    if co_cham and co_phay:
        dau = "." if chuoi.rfind(".") > chuoi.rfind(",") else ","
    else:
        dau = "." if co_cham else ","
        if chuoi.count(dau) > 1 or len(chuoi) - chuoi.rfind(dau) - 1 == 3:
            return (chuoi.replace(dau, ""), "") if _nhom_hop_le(chuoi, dau) else None

    nguyen, _, thap_phan = chuoi.rpartition(dau)
    khac = "," if dau == "." else "."
    if khac in nguyen and not _nhom_hop_le(nguyen, khac):
        return None
    nguyen = nguyen.replace(khac, "")
    if not nguyen.isdigit() or not thap_phan.isdigit():
        return None
    return nguyen, thap_phan


def doc_so(raw: str | None) -> tuple[float | None, str]:
    """
    Đọc một ô trên báo cáo thành (giá trị, trạng thái).

    Giá trị trả về CHƯA quy đổi về đồng — việc nhân hệ số đơn vị làm ở
    `quy_doi()` để hai bước đó test riêng được, và để một lần sửa hệ số đơn
    vị không phải gõ lại toàn bộ số đã đọc.

    Số âm: báo cáo tài chính in trong ngoặc đơn `(1.234.567)`, một số báo
    cáo dùng dấu trừ. Guideline mục 3.3 coi cả hai là số âm.
    """
    if raw is None:
        return None, KHONG_RO

    chuoi = _bo_khoang_trang(raw)
    if not chuoi:
        return None, KHONG_RO

    if chuoi in _DAU_GACH:
        return 0.0, BANG_KHONG

    if chuoi in _KHONG_DOC_RA:
        return None, KHONG_DOC_RA

    am = False
    if chuoi.startswith("(") and chuoi.endswith(")"):
        am, chuoi = True, chuoi[1:-1]
    while chuoi[:1] in _DAU_GACH:
        am, chuoi = not am, chuoi[1:]

    if not chuoi or not _CHI_SO.match(chuoi):
        return None, KHONG_RO

    tach = _tach_phan_thap_phan(chuoi)
    if tach is None:
        return None, KHONG_RO

    nguyen, thap_phan = tach
    gia_tri = float(f"{nguyen or 0}.{thap_phan or 0}")
    return (-gia_tri if am else gia_tri), SO


def quy_doi(gia_tri: float | None, he_so: int) -> int | None:
    """
    Đưa giá trị về ĐỒNG, làm tròn về số nguyên.

    Guideline mục 3.2: báo cáo in `29.403` ở đơn vị "triệu đồng" thì tập gold
    ghi `29403000000`. Lưu ở đơn vị gốc sẽ khiến hai tài liệu khác đơn vị
    không so được với nhau và mọi phép đo accuracy trên nhiều công ty mất
    nghĩa.

    Làm tròn về nguyên vì đơn vị nhỏ nhất của tiền Việt Nam là đồng; giữ
    phần lẻ chỉ tạo ra sai lệch giả khi so khớp theo dung sai tỷ lệ.
    """
    if gia_tri is None:
        return None
    return round(gia_tri * he_so)
