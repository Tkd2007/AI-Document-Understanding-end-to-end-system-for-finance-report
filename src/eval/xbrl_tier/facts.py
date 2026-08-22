"""
Dựng bảng tài chính từ companyfacts của SEC.

`linkbase.py` cho biết đẳng thức nào đúng; module này cho biết CON SỐ nào
đã nộp. Ghép hai thứ lại mới ra được một bảng vừa có ràng buộc đã khai báo
vừa có giá trị thoả ràng buộc đó — tức ground truth hoàn hảo mà tầng này
tồn tại để khai thác.

LUẬT QUAN TRỌNG NHẤT CỦA MODULE NÀY: chỉ lấy fact thuộc CÙNG MỘT HỒ SƠ.

companyfacts gộp mọi lần công bố của cùng một chỉ tiêu, nên cùng một ngày
kết thúc kỳ có thể có nhiều giá trị khác nhau — bản gốc và các bản trình
bày lại ở những hồ sơ sau. Trộn giá trị của hai hồ sơ vào một bảng sẽ phá
vỡ đẳng thức kế toán một cách âm thầm, và khi đó tầng này mất đúng thứ duy
nhất làm nên giá trị của nó: ground truth chắc chắn đúng. Một bảng không
cân vì lý do đó sẽ bị đếm thành "lỗi trích xuất" trong khi thật ra là lỗi
của bước dựng dữ liệu, và nó làm sai mọi con số ở H1.
"""

from eval.xbrl_tier.table import FinancialTable

# Số ngày tối thiểu để coi một fact là kỳ NĂM.
#
# Hồ sơ 10-K chứa cả fact quý lẫn fact năm cho cùng một chỉ tiêu. Lấy nhầm
# fact quý vào bảng năm sẽ làm đẳng thức không cân, và đó lại là loại lỗi
# trông y hệt lỗi trích xuất.
NGAY_TOI_THIEU_KY_NAM = 300


def _so_ngay(start: str, end: str) -> int:
    """Khoảng cách ngày giữa hai chuỗi ISO, tính thô theo năm và tháng."""
    from datetime import date

    d1 = date.fromisoformat(start)
    d2 = date.fromisoformat(end)
    return (d2 - d1).days


def _cac_fact(companyfacts: dict, concept: str, unit: str) -> list[dict]:
    """Mọi lần công bố của một concept ở đơn vị chỉ định, mọi taxonomy."""
    for _khong_gian, cac_concept in companyfacts.get("facts", {}).items():
        if concept in cac_concept:
            return cac_concept[concept].get("units", {}).get(unit, [])
    return []


def _nhan(companyfacts: dict, concept: str) -> str | None:
    for _khong_gian, cac_concept in companyfacts.get("facts", {}).items():
        if concept in cac_concept:
            return cac_concept[concept].get("label")
    return None


def _chon_fact(cac_fact: list[dict], accn: str, end: str) -> dict | None:
    """
    Chọn đúng một fact cho (hồ sơ, ngày kết thúc kỳ).

    Ưu tiên fact thời điểm (không có `start`, tức chỉ tiêu bảng cân đối).
    Với fact thời kỳ thì chỉ nhận kỳ NĂM — xem NGAY_TOI_THIEU_KY_NAM.

    Trả None khi không có gì khớp. Ô trống là chuyện có thật của báo cáo và
    `FinancialTable` xử lý được; đoán bừa một giá trị thì không.
    """
    hop_le = [f for f in cac_fact if f.get("accn") == accn and f.get("end") == end]
    if not hop_le:
        return None

    thoi_diem = [f for f in hop_le if "start" not in f]
    if thoi_diem:
        return thoi_diem[0]

    ky_nam = [
        f
        for f in hop_le
        if _so_ngay(f["start"], f["end"]) >= NGAY_TOI_THIEU_KY_NAM
    ]
    return ky_nam[0] if ky_nam else None


def cac_ky_cua_ho_so(companyfacts: dict, accn: str, unit: str = "USD") -> list[str]:
    """
    Các ngày kết thúc kỳ có mặt trong một hồ sơ, mới nhất trước.

    Thứ tự này thành thứ tự cột của bảng, và quy ước "kỳ gần nhất đứng
    trước" phải khớp với cách báo cáo thật in ra — nếu không thì chế độ lỗi
    lệch cột sinh ra ở đây đi ngược chiều với lỗi lệch cột ngoài đời.
    """
    ngay: set[str] = set()
    for _khong_gian, cac_concept in companyfacts.get("facts", {}).items():
        for du_lieu in cac_concept.values():
            for fact in du_lieu.get("units", {}).get(unit, []):
                if fact.get("accn") == accn and "end" in fact:
                    ngay.add(fact["end"])
    return sorted(ngay, reverse=True)


def build_table(
    companyfacts: dict,
    concepts: list[str],
    accn: str,
    periods: list[str] | None = None,
    n_periods: int = 2,
    unit: str = "USD",
    doc_id: str | None = None,
) -> FinancialTable:
    """
    Dựng `FinancialTable` từ companyfacts, chỉ lấy fact của hồ sơ `accn`.

    `concepts` nên đến từ `linkbase.concepts_xuat_hien()` để bảng chứa đúng
    những chỉ tiêu mà đẳng thức nói tới — thêm chỉ tiêu ngoài hệ ràng buộc
    chỉ làm bảng dài ra mà không thêm thông tin cho H1 và H2.

    `periods` để None thì lấy `n_periods` kỳ gần nhất của chính hồ sơ đó.
    Cột kỳ so sánh không phải trang trí: nó vừa là nguồn của chế độ lỗi lệch
    cột vừa là ràng buộc gần như miễn phí, đúng câu hỏi (d) ở mục 6.1
    proposal.
    """
    cac_ky = periods or cac_ky_cua_ho_so(companyfacts, accn, unit)[:n_periods]

    gia_tri: dict[str, dict[str, float | None]] = {}
    nhan: dict[str, str] = {}

    for concept in concepts:
        cac_fact = _cac_fact(companyfacts, concept, unit)
        nhan[concept] = _nhan(companyfacts, concept) or concept
        gia_tri[concept] = {}
        for ky in cac_ky:
            fact = _chon_fact(cac_fact, accn, ky)
            gia_tri[concept][ky] = float(fact["val"]) if fact else None

    return FinancialTable(
        doc_id=doc_id or f"{companyfacts.get('cik', 'unknown')}_{accn}",
        concepts=list(concepts),
        labels=nhan,
        periods=list(cac_ky),
        values=gia_tri,
        unit_label=unit,
        unit_multiplier=1,
        meta={
            "accn": accn,
            "entity": companyfacts.get("entityName", ""),
            "cik": companyfacts.get("cik"),
        },
    )
