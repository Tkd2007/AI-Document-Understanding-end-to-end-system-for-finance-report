"""
Inject lỗi có kiểm soát lên bảng đã dựng từ XBRL.

Đây là thứ cho tầng này POWER: biết chính xác trường nào bị hỏng và hỏng
kiểu gì, trên hàng nghìn tài liệu, không tốn một đồng gán nhãn nào. H2 và
H3 đo trên SỐ LỖI chứ không phải số trường, nên 60 tài liệu gold chỉ cho
khoảng 75–225 lỗi — đủ để nói "phương pháp này chạy được", không đủ để nói
"hơn baseline 5 điểm".

GIỚI HẠN PHẢI NÊU TRONG PAPER, không được giấu: lỗi inject không giống lỗi
thật. Taxonomy dưới đây phải RÚT RA TỪ LỖI QUAN SÁT ĐƯỢC ở tầng gold Việt
Nam rồi mới chốt tỷ lệ, chứ không bịa từ trực giác. Trước khi có phân loại
lỗi thật, mọi tỷ lệ ở đây là giả định.

MỘT CÁI BẪY PHƯƠNG PHÁP LUẬN, VÀ LÝ DO BẢNG CHỮ SỐ Ở ĐÂY KHÁC BẢNG Ở
`repair.candidates`: nếu bộ sinh lỗi và bộ sinh ứng viên sửa dùng CHUNG một
bảng nhầm lẫn chữ số thì mọi lỗi inject đều nằm sẵn trong tập ứng viên theo
đúng cấu trúc, và phương pháp đề xuất thắng vì thí nghiệm được dựng cho nó
thắng. Đó là loại lỗi reviewer giết bài ngay. Nên bảng ở đây RỘNG HƠN hẳn:
thay một chữ số bằng bất kỳ chữ số nào khác. Phần lỗi rơi ra ngoài tập ứng
viên là phần phương pháp PHẢI chịu thua, và tỷ lệ đó tự nó là một con số
đáng báo cáo.
"""

import random
from dataclasses import dataclass, field
from enum import Enum

from eval.xbrl_tier.table import FinancialTable

# Luỹ thừa 10 dùng cho lỗi sai đơn vị: nghìn và triệu, cả hai chiều.
#
# Hẹp hơn bảng ở repair.candidates (vốn có cả ±9) vì đơn vị trình bày thật
# trên báo cáo chỉ chạy trong khoảng đó. Sinh lỗi ×10⁹ là sinh một chế độ
# lỗi không ai gặp, và nó sẽ làm đẹp giả tạo cho mọi phương pháp có mỏ neo
# biên độ lớn — biên độ càng vô lý thì càng dễ bắt.
BAC_SCALE = (-6, -3, 3, 6)

CHU_SO = "0123456789"


class ErrorType(str, Enum):
    """Năm chế độ lỗi ở mục 3.1 của proposal."""

    DIGIT_SUB = "digit_substitution"
    ROW_SHIFT = "row_shift"
    COL_SHIFT = "col_shift"
    SCALE = "scale"
    SIGN = "sign"


@dataclass(frozen=True)
class InjectedError:
    """
    Ground truth của một lỗi đã inject. Đây là thứ H2 đo trên.

    `detail` giữ lại cơ chế cụ thể — vị trí chữ số bị đổi, concept bị lấy
    nhầm, luỹ thừa đã nhân. Không có nó thì không phân tích được "phương
    pháp mạnh ở chế độ lỗi nào và yếu ở chế độ nào", mà bảng đó mới là thứ
    nói lên điều gì đang xảy ra chứ không phải một con số Top-1 gộp chung.
    """

    concept: str
    period: str
    error_type: ErrorType
    original: float
    corrupted: float
    detail: dict = field(default_factory=dict)


def _co_gia_tri(table: FinancialTable, ky: str) -> list[str]:
    """Các chỉ tiêu có giá trị khác 0 trong kỳ — chỉ chúng mới hỏng được."""
    return [
        ten
        for ten in table.concepts
        if table.get(ten, ky) not in (None, 0)
    ]


def _doi_mot_chu_so(gia_tri: float, rng: random.Random) -> tuple[float, dict]:
    """
    Đổi một chữ số của phần nguyên sang một chữ số khác bất kỳ.

    Giữ dấu và giữ độ dài: OCR đọc nhầm chữ số chứ không làm mất chữ số, và
    một lỗi làm đổi số chữ số sẽ bị mọi biên độ lớn bắt được ngay — tức là
    sinh ra một bài toán dễ hơn bài toán thật.

    Chữ số ĐẦU không được đổi thành 0, vì số 0 đứng đầu không tồn tại trong
    biểu diễn thập phân: 1000 sẽ thành 0 và mất luôn ba chữ số. Đó vừa là
    lỗi mất độ dài mà đoạn trên vừa loại, vừa tệ hơn thế — một giá trị bị
    hỏng thành 0 sẽ bị nhầm với ô trống ở mọi bước phía sau.
    """
    dau = -1 if gia_tri < 0 else 1
    chuoi = str(int(abs(gia_tri)))

    vi_tri = rng.randrange(len(chuoi))
    cu = chuoi[vi_tri]
    cam = {cu, "0"} if vi_tri == 0 and len(chuoi) > 1 else {cu}
    moi = rng.choice([c for c in CHU_SO if c not in cam])

    hong = chuoi[:vi_tri] + moi + chuoi[vi_tri + 1 :]
    return dau * float(int(hong)), {"vi_tri": vi_tri, "chu_so_cu": cu, "chu_so_moi": moi}


def _sinh_gia_tri_hong(
    table: FinancialTable,
    concept: str,
    ky: str,
    error_type: ErrorType,
    rng: random.Random,
) -> tuple[float, dict] | None:
    """
    Sinh giá trị hỏng cho một ô. Trả None khi chế độ lỗi này không áp được
    lên ô đó — ví dụ lệch cột trên bảng chỉ có một kỳ.

    Trả None thay vì ném lỗi vì việc một ô không hỏng được theo một kiểu là
    chuyện bình thường của dữ liệu, còn việc CẢ BẢNG không hỏng được mới là
    chuyện cần báo, và nơi gọi lo phần đó.
    """
    goc = table.get(concept, ky)

    if error_type is ErrorType.DIGIT_SUB:
        return _doi_mot_chu_so(goc, rng)

    if error_type is ErrorType.SIGN:
        return -goc, {}

    if error_type is ErrorType.SCALE:
        k = rng.choice(BAC_SCALE)
        return goc * (10.0 ** k), {"k": k, "toan_cuc": False}

    if error_type is ErrorType.ROW_SHIFT:
        ung_vien = [
            ten
            for ten in table.hang_xom_doc(concept)
            if table.get(ten, ky) not in (None, goc)
        ]
        if not ung_vien:
            return None
        lay_tu = rng.choice(ung_vien)
        return table.get(lay_tu, ky), {"lay_tu_concept": lay_tu}

    if error_type is ErrorType.COL_SHIFT:
        ung_vien = [
            k
            for k in table.periods
            if k != ky and table.get(concept, k) not in (None, goc)
        ]
        if not ung_vien:
            return None
        lay_tu = rng.choice(ung_vien)
        return table.get(concept, lay_tu), {"lay_tu_ky": lay_tu}

    raise ValueError(f"chế độ lỗi chưa hỗ trợ: {error_type}")


def inject(
    table: FinancialTable,
    error_type: ErrorType,
    n_errors: int = 1,
    seed: int = 0,
    period: str | None = None,
) -> tuple[FinancialTable, list[InjectedError]]:
    """
    Inject `n_errors` lỗi cùng một chế độ lên một kỳ của bảng.

    Trả về `(bảng đã hỏng, danh sách ground truth)`. Bảng gốc không bị đụng
    tới, nên so được hai bên mà không sợ ground truth bị chính bước inject
    làm hỏng.

    `seed` cố định thì kết quả tái lập được từng bit — điều kiện để mục 7
    của ADDENDUM ghi lại được lượt chạy, và để một kết quả bất thường có thể
    dựng lại mà xem.

    Ném `ValueError` khi không đủ ô hỏng được theo chế độ đã chọn. Trả ít
    lỗi hơn yêu cầu một cách im lặng sẽ làm mẫu số của mọi chỉ số ở H2 sai
    mà không có gì báo — đúng loại lỗi mà quy ước "trạng thái tường minh"
    của repo dựng lên để chống.
    """
    rng = random.Random(seed)
    ky = period or table.cot_chinh()

    ung_vien = _co_gia_tri(table, ky)
    rng.shuffle(ung_vien)

    hong = table
    da_inject: list[InjectedError] = []

    for concept in ung_vien:
        if len(da_inject) == n_errors:
            break

        ket_qua = _sinh_gia_tri_hong(table, concept, ky, error_type, rng)
        if ket_qua is None:
            continue

        gia_tri_moi, chi_tiet = ket_qua
        if gia_tri_moi == table.get(concept, ky):
            continue

        hong = hong.thay_gia_tri(concept, ky, gia_tri_moi)
        da_inject.append(
            InjectedError(
                concept=concept,
                period=ky,
                error_type=error_type,
                original=table.get(concept, ky),
                corrupted=gia_tri_moi,
                detail=chi_tiet,
            )
        )

    if len(da_inject) < n_errors:
        raise ValueError(
            f"chỉ inject được {len(da_inject)}/{n_errors} lỗi kiểu "
            f"{error_type.value} trên {table.doc_id} kỳ {ky}"
        )

    return hong, da_inject


def inject_scale_toan_cuc(
    table: FinancialTable,
    seed: int = 0,
    k: int | None = None,
) -> tuple[FinancialTable, list[InjectedError]]:
    """
    Nhân MỌI ô của bảng với 10^k — lỗi đọc nhầm đơn vị tính toàn cục.

    Tách khỏi `inject()` vì nó khác hẳn về bản chất: đây không phải n lỗi
    độc lập mà là MỘT lỗi tác động lên toàn bảng, nên đếm nó thành 25 lỗi
    sẽ thổi phồng mẫu số của H2.

    Giá trị của ca này nằm ở chỗ nó là phản ví dụ chạy được cho một mệnh đề
    chứng minh trong một dòng ở `constraints.py`: hệ ràng buộc kế toán là hệ
    thuần nhất nên mọi bội vô hướng của nghiệm cũng là nghiệm, tức sai đơn
    vị toàn cục LUÔN vô hình với mọi phương pháp dựa trên ràng buộc. Không
    phải "thường vô hình" — là luôn. Đây là ca dùng để chứng minh mỏ neo
    tuyệt đối ở mục 6.3 proposal là bắt buộc chứ không phải tuỳ chọn, và có
    test chốt rằng mọi đẳng thức vẫn thoả sau khi inject.
    """
    rng = random.Random(seed)
    bac = k if k is not None else rng.choice(BAC_SCALE)
    he_so = 10.0 ** bac

    hong = table
    da_inject: list[InjectedError] = []

    for concept in table.concepts:
        for ky in table.periods:
            goc = table.get(concept, ky)
            if goc is None:
                continue
            hong = hong.thay_gia_tri(concept, ky, goc * he_so)
            da_inject.append(
                InjectedError(
                    concept=concept,
                    period=ky,
                    error_type=ErrorType.SCALE,
                    original=goc,
                    corrupted=goc * he_so,
                    detail={"k": bac, "toan_cuc": True},
                )
            )

    hong.meta["scale_toan_cuc_k"] = bac
    return hong, da_inject
