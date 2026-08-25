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



def cac_ky_phu_rong_nhat(
    companyfacts: dict,
    accn: str,
    concepts: list[str],
    n: int = 2,
    unit: str = "USD",
) -> list[str]:
    """
    `n` kỳ có NHIỀU CHỈ TIÊU CÓ GIÁ TRỊ NHẤT, trả về mới nhất trước.

    VÌ SAO KHÔNG LẤY THẲNG `n` NGÀY GẦN NHẤT, và đây là lỗi đã quan sát
    được chứ không phải phòng xa: một hồ sơ 10-K chứa đủ loại ngày kết thúc
    kỳ, không chỉ ngày lập bảng cân đối — ngày trang bìa, ngày sự kiện sau
    niên độ, ngày của vài fact lẻ. Trên hồ sơ `0000012927-25-000015`, sắp
    theo ngày giảm dần cho `2024-12-31` với 204/311 chỉ tiêu có giá trị,
    rồi tới `2024-10-31` với **0/311**. Lấy hai ngày đầu là lấy một cột
    rỗng làm kỳ so sánh.

    Hậu quả không phải một cột trống vô hại: chế độ lỗi lệch cột lấy giá
    trị từ cột kỳ so sánh, nên cột rỗng làm nó KHÔNG INJECT ĐƯỢC. Lượt chạy
    Mốc 3 ngày 24/08/2026 bỏ 120/130 lượt `col_shift` đúng vì lý do này,
    tức chỉ ba trong bốn chế độ lỗi thật sự chạy.

    Sắp lại theo ngày giảm dần sau khi đã chọn, để giữ quy ước "kỳ gần nhất
    đứng trước" của `cot_chinh()`. Hoà độ phủ thì kỳ mới hơn thắng.
    """
    fact_theo_concept = {c: _cac_fact(companyfacts, c, unit) for c in concepts}

    # Tính độ phủ MỘT LẦN cho mỗi kỳ: _chon_fact() quét cả danh sách fact
    # nên gọi nó lại trong khoá sắp là quét lại toàn bộ hồ sơ nhiều lần.
    do_phu = {
        ky: sum(1 for c in concepts if _chon_fact(fact_theo_concept[c], accn, ky))
        for ky in cac_ky_cua_ho_so(companyfacts, accn, unit)
    }

    # Ngày ở dạng ISO nên so chuỗi cũng là so thời gian: sắp giảm dần theo
    # (độ phủ, ngày) cho ra độ phủ cao trước, hoà thì kỳ mới hơn trước.
    xep = sorted(do_phu, key=lambda ky: (do_phu[ky], ky), reverse=True)

    return sorted(xep[:n], reverse=True)


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

    `periods` để None thì lấy `n_periods` kỳ có ĐỘ PHỦ RỘNG NHẤT trên chính
    `concepts` — không phải `n_periods` ngày gần nhất. Lý do ở docstring
    `cac_ky_phu_rong_nhat()`: hồ sơ 10-K có nhiều ngày kết thúc kỳ không
    phải ngày lập bảng cân đối, và lấy theo ngày sẽ chọn trúng một cột rỗng.

    Cột kỳ so sánh không phải trang trí: nó vừa là nguồn của chế độ lỗi lệch
    cột vừa là ràng buộc gần như miễn phí, đúng câu hỏi (d) ở mục 6.1
    proposal.
    """
    cac_ky = periods or cac_ky_phu_rong_nhat(
        companyfacts, accn, list(concepts), n_periods, unit
    )

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
