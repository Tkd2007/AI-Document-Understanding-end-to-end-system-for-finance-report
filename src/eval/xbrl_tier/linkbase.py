"""
Đọc calculation linkbase của hồ sơ XBRL để lấy đẳng thức đã khai báo.

ĐÂY LÀ LÝ DO TẦNG NÀY TỒN TẠI. Hồ sơ SEC kèm một bản ghi máy đọc nói rõ
dòng nào cộng vào tổng nào và với dấu gì. Ground truth của ràng buộc vì thế
hoàn hảo và miễn phí, trên hàng nghìn tài liệu — trong khi tầng gold Việt
Nam phải gán nhãn tay 60 tài liệu. Phân vai giữa hai tầng: XBRL lo POWER,
gold Việt Nam lo VALIDITY.

Nhắc lại giới hạn để không nhầm vai: có linkbase KHÔNG có nghĩa bài toán dễ
đi. Nó chỉ có nghĩa ở tầng này ta biết chắc đẳng thức nào đúng, nên đo được
khả năng định vị lỗi mà không phải cãi nhau về nhãn. Báo cáo Việt Nam không
có linkbase, và đó vẫn là ca kiểm chứng khó nhất.

PARSE TRỰC TIẾP, KHÔNG DÙNG arelle. arelle là một bộ xử lý XBRL đầy đủ và
kéo theo cả một cây phụ thuộc, trong khi thứ cần ở đây là đọc vài phần tử
XML. Nguyên tắc của requirements.txt là không thêm thư viện nặng cho một
việc thư viện chuẩn làm được — cùng lý do C2 không cắm bộ giải MILP.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass

import numpy as np

# Trọng số hợp lệ trong calculation linkbase.
#
# Chuẩn XBRL cho phép trọng số là số thực bất kỳ, nhưng calculation linkbase
# của báo cáo tài chính trên thực tế chỉ dùng ±1: một dòng hoặc cộng vào
# tổng hoặc trừ khỏi tổng. Gặp trọng số khác là dấu hiệu hồ sơ dùng linkbase
# theo cách ta chưa lường, và im lặng chấp nhận nó sẽ dựng ra một ma trận
# ràng buộc sai mà không có gì báo.
TRONG_SO_HOP_LE = (-1.0, 1.0)


@dataclass(frozen=True)
class CalcEquation:
    """
    Một đẳng thức khai báo: `total = Σ wᵢ · partᵢ`.

    `role` giữ lại URI của calculationLink để biết đẳng thức này thuộc báo
    cáo nào (bảng cân đối, kết quả kinh doanh, lưu chuyển tiền tệ). Cùng
    một concept có thể xuất hiện ở nhiều báo cáo với vai khác nhau, nên bỏ
    role đi là trộn lẫn các hệ ràng buộc vốn không nên trộn.
    """

    total: str
    parts: tuple[tuple[str, float], ...]
    role: str = ""

    @property
    def concepts(self) -> list[str]:
        return [self.total, *[ten for ten, _ in self.parts]]


def _ten_dia_phuong(tag: str) -> str:
    """Bỏ phần namespace trong tên thẻ XML."""
    return tag.rsplit("}", 1)[-1]


def concept_tu_href(href: str) -> str:
    """
    Lấy tên concept từ thuộc tính xlink:href của một phần tử `loc`.

    href có dạng `.../us-gaap-2025.xsd#us-gaap_AssetsCurrent`. Phần sau dấu
    `#` là id trong lược đồ, và quy ước của mọi taxonomy XBRL là
    `<tiền tố>_<tên concept>`. Cắt ở dấu gạch dưới ĐẦU TIÊN chứ không phải
    cuối cùng: tên concept của taxonomy riêng từng doanh nghiệp có thể chứa
    gạch dưới, còn tiền tố thì không.
    """
    manh = href.split("#")[-1]
    return manh.split("_", 1)[1] if "_" in manh else manh


def parse_calculation_linkbase(xml_text: str) -> list[CalcEquation]:
    """
    Đọc nội dung một file `*_cal.xml` thành danh sách đẳng thức.

    Mỗi `calculationArc` nối một concept cha (`xlink:from`) với một concept
    con (`xlink:to`) kèm trọng số. Gom các arc theo cặp (role, cha) sẽ ra
    đúng một đẳng thức cho mỗi tổng.

    Cây calculation lồng nhau sinh ra NHIỀU đẳng thức chứ không phải một:
    tổng tài sản gồm ngắn hạn và dài hạn, mà ngắn hạn lại gồm tiền và phải
    thu. Giữ cả hai tầng làm hạng của ma trận cao lên, tức khả năng định vị
    tốt lên — đúng thứ mục 6.1 của proposal đi đo.

    Duyệt theo TÊN ĐỊA PHƯƠNG của thẻ thay vì theo namespace đầy đủ: hồ sơ
    thật khai báo namespace linkbase theo vài cách khác nhau, và khớp cứng
    một URI sẽ làm hàm này im lặng trả về danh sách rỗng trên hồ sơ hợp lệ.
    """
    goc = ET.fromstring(xml_text)
    ket_qua: list[CalcEquation] = []

    for lien_ket in goc.iter():
        if _ten_dia_phuong(lien_ket.tag) != "calculationLink":
            continue

        role = ""
        for ten_thuoc_tinh, gia_tri in lien_ket.attrib.items():
            if _ten_dia_phuong(ten_thuoc_tinh) == "role":
                role = gia_tri

        # nhãn xlink:label -> tên concept
        nhan_toi_concept: dict[str, str] = {}
        for phan_tu in lien_ket:
            if _ten_dia_phuong(phan_tu.tag) != "loc":
                continue
            nhan = href = None
            for ten_thuoc_tinh, gia_tri in phan_tu.attrib.items():
                cuc_bo = _ten_dia_phuong(ten_thuoc_tinh)
                if cuc_bo == "label":
                    nhan = gia_tri
                elif cuc_bo == "href":
                    href = gia_tri
            if nhan and href:
                nhan_toi_concept[nhan] = concept_tu_href(href)

        # gom arc theo concept cha, giữ nguyên thứ tự gặp
        theo_cha: dict[str, list[tuple[str, float]]] = {}
        for phan_tu in lien_ket:
            if _ten_dia_phuong(phan_tu.tag) != "calculationArc":
                continue

            tu = toi = None
            trong_so = 1.0
            for ten_thuoc_tinh, gia_tri in phan_tu.attrib.items():
                cuc_bo = _ten_dia_phuong(ten_thuoc_tinh)
                if cuc_bo == "from":
                    tu = gia_tri
                elif cuc_bo == "to":
                    toi = gia_tri
                elif cuc_bo == "weight":
                    trong_so = float(gia_tri)

            if tu not in nhan_toi_concept or toi not in nhan_toi_concept:
                continue
            if trong_so not in TRONG_SO_HOP_LE:
                raise ValueError(
                    f"trọng số {trong_so} ngoài {TRONG_SO_HOP_LE} ở arc {tu} -> {toi}"
                )

            theo_cha.setdefault(nhan_toi_concept[tu], []).append(
                (nhan_toi_concept[toi], trong_so)
            )

        for cha, con in theo_cha.items():
            ket_qua.append(CalcEquation(total=cha, parts=tuple(con), role=role))

    return ket_qua


def to_matrix(
    equations: list[CalcEquation],
    concepts: list[str],
) -> tuple[np.ndarray, list[str]]:
    """
    Dựng ma trận ràng buộc A từ các đẳng thức đã khai báo.

    Trả về đúng cặp `(A, field_order)` mà `constraints.build_matrix` trả về,
    nên mọi hàm phân tích ở A2 — hạng, không gian null, cột tỷ lệ, bảng định
    vị, báo cáo — và cả bước chẩn đoán ở C2 dùng lại được nguyên vẹn.

    Đây là bản tổng quát có TRỌNG SỐ của `constraints.build_matrix`. Đẳng
    thức kế toán Việt Nam luôn có dạng "các thành phần cộng lại bằng tổng"
    nên bản ở A2 gán cứng +1 cho thành phần; linkbase của SEC thì cho phép
    trọng số −1, ví dụ chi phí trừ khỏi lợi nhuận. Hai hàm phải cho ra ma
    trận GIỐNG HỆT NHAU khi mọi trọng số bằng +1, và có test chốt điều đó —
    nếu chúng lệch nhau thì một trong hai đang dựng sai ràng buộc, mà ràng
    buộc sai là loại lỗi không có gì báo.

    Đẳng thức nào có concept không nằm trong `concepts` thì bị BỎ, cùng lý
    do với A2: không trích một chỉ tiêu thì không kiểm được đẳng thức chứa
    nó, và coi nó bằng 0 sẽ làm hạng cao lên một cách giả tạo, tức báo cáo
    lạc quan hơn sự thật về khả năng định vị.
    """
    field_order = list(concepts)
    vi_tri = {ten: i for i, ten in enumerate(field_order)}

    cac_dong = []
    for pt in equations:
        if any(ten not in vi_tri for ten in pt.concepts):
            continue

        dong = np.zeros(len(field_order))
        for ten, w in pt.parts:
            dong[vi_tri[ten]] += w
        dong[vi_tri[pt.total]] -= 1.0
        cac_dong.append(dong)

    if not cac_dong:
        return np.zeros((0, len(field_order))), field_order

    return np.vstack(cac_dong), field_order


def concepts_xuat_hien(equations: list[CalcEquation]) -> list[str]:
    """
    Mọi concept có mặt trong các đẳng thức, giữ thứ tự gặp lần đầu.

    Thứ tự phải TẤT ĐỊNH chứ không lấy từ set: thứ tự này thành thứ tự cột
    của ma trận, mà nhầm thứ tự cột là loại lỗi im lặng nguy hiểm nhất ở
    đây — nó không làm gì nổ, chỉ gán kết luận của chỉ tiêu này cho chỉ
    tiêu khác.
    """
    thu_tu: list[str] = []
    for pt in equations:
        for ten in pt.concepts:
            if ten not in thu_tu:
                thu_tu.append(ten)
    return thu_tu
