"""
Sinh tập ứng viên sửa lỗi từ chính tài liệu.

Năm nguồn, mỗi nguồn bắt một chế độ lỗi khác nhau. Ba nguồn đầu cần
provenance (bbox của vùng đã đọc), nguồn cuối cần các giá trị thua phiếu
của bước self-consistency.

VÌ SAO TẬP ỨNG VIÊN PHẢI ĐÓNG: nếu cho delta chạy tự do trong R^n thì bộ
tối ưu LUÔN tìm được nghiệm thoả ràng buộc, kể cả khi nghiệm đó là bịa. Hệ
sẽ trả về một bộ số cân đối hoàn hảo và sai hoàn toàn, kèm chứng chỉ PASS.
Giới hạn delta vào một tập ứng viên sinh từ tài liệu là cách chặn chuyện
đó VỀ MẶT CẤU TRÚC chứ không phải bằng heuristic — câu bán được cho
reviewer gói trong một dòng: phương pháp này không thể ép số, vì không
gian sửa không chứa số bịa.
"""

import math
from dataclasses import dataclass, field

from nham_chu_so import N_CAP_UNG_VIEN, ung_vien_cho_chu_so

# Xác suất tiên nghiệm của từng chế độ lỗi, dùng để tính cost.
#
# CHƯA HIỆU CHỈNH TRÊN DỮ LIỆU THẬT. Bốn con số này hiện dựa trên mô tả
# định tính trong các công trình được trích dẫn, không dựa trên tần suất
# đo được. Phải ước lượng lại từ phân loại lỗi trên tập gold rồi mới chốt,
# vì chúng đi THẲNG vào hàm mục tiêu của bước chẩn đoán: đặt sai thì thuật
# toán vẫn chạy và vẫn cho nghiệm, chỉ là ưu tiên sai loại sửa.
XAC_SUAT_TIEN_NGHIEM = {
    "ocr_alt": 0.35,        # nhầm chữ số — chế độ lỗi phổ biến nhất của OCR
    "neighbor_cell": 0.30,  # lệch dòng / lệch cột — hiện tượng của bố cục trang
    "sign": 0.20,           # mất dấu ngoặc âm
    "scale": 0.10,          # sai đơn vị ở MỘT trường (sai toàn cục do mỏ neo lo)
    "vlm_vote": 0.05,       # model đã từng đọc ra giá trị này ở một mẫu khác
}

# Cặp chữ số OCR hay đọc nhầm nay ĐO ĐƯỢC, không còn liệt kê tay.
#
# Bảng cũ là bốn cặp `(0,8) (1,7) (3,8) (5,6)` chọn theo hình dạng nhìn bằng
# mắt. Đối chiếu với số đo ở `src/nham_chu_so.py` thì ba trong bốn cặp đó
# gần như không xuất hiện, còn cặp áp đảo thật — `9→0`, chiếm 38% mọi quan
# sát — KHÔNG nằm trong bảng cũ. Nghĩa là nguồn `ocr_alt` trước đây đi tìm
# sai chế độ lỗi.
#
# Chiều tra là chiều NGƯỢC của ma trận: hàm này chỉ thấy chữ số ĐÃ ĐỌC RA và
# phải đoán ngược lại giá trị thật. Xem docstring `nham_chu_so` — đảo nhầm
# chiều ở đây là lỗi câm hoàn hảo, ứng viên vẫn sinh đủ số lượng nhưng không
# bao giờ trúng.
#
# Trần `N_CAP_UNG_VIEN` là phía BỊ GIỚI HẠN ĐỘ SÂU của phương án (a): bộ
# tiêm lỗi lấy toàn bộ phân phối, còn phía này chỉ lấy các cặp đầu bảng, và
# khoảng hở giữa hai bên là thứ giữ cho cơ chế ABSTAIN còn kiểm chứng được.

# Luỹ thừa 10 cho ứng viên sai đơn vị: nghìn, triệu, tỷ theo cả hai chiều.
BAC_SCALE = (-9, -6, -3, 3, 6, 9)

# Trần số ứng viên mỗi trường.
#
# Spec đề xuất 10. Để 12 vì riêng nguồn `scale` đã đóng góp 6 ứng viên có
# cấu trúc khác hẳn nhau, và cắt bớt chúng là cắt đúng chế độ lỗi mà ràng
# buộc kế toán CHỨNG MINH ĐƯỢC là không bao giờ phát hiện nổi — hệ ràng
# buộc thuần nhất nên mọi bội vô hướng của nghiệm cũng là nghiệm.
#
# Trần vẫn phải có: bước chẩn đoán ở C2 là NP-hard, và số ứng viên mỗi
# trường vào thẳng cơ số của không gian tìm kiếm.
MAX_UNG_VIEN = 12

# Trần cho MỖI nguồn, áp trước khi xếp theo cost.
#
# Không có nó thì xếp thuần theo cost sẽ để nguồn đông nhất chiếm hết chỗ:
# một con số 14 chữ số sinh ra tới 28 biến thể nhầm chữ số, tất cả đều rẻ
# hơn mọi ứng viên scale. Mà các nguồn bị chèn ra ngoài lại chính là các
# nguồn bắt những chế độ lỗi mà nguồn đông kia không bắt được.
MAX_MOI_NGUON = 6


@dataclass(frozen=True)
class Candidate:
    """
    Một cách đọc THAY THẾ cho giá trị hiện tại của một chỉ tiêu.

    cost thấp nghĩa là hợp lý hơn. Nó đi thẳng vào hàm mục tiêu của bước
    chẩn đoán nên không được đặt tuỳ tiện — xem XAC_SUAT_TIEN_NGHIEM.

    evidence giữ lại vì sao ứng viên này được sinh ra. Nó là thứ đi vào
    certificate của kết quả cuối: người đọc phải biết con số đã sửa đến từ
    ô nào, biến thể chữ số nào, hay mẫu VLM thứ mấy.
    """

    value: int | float
    source: str
    cost: float
    evidence: dict = field(default_factory=dict)


def _cost(source: str, trong_so: float = 1.0) -> float:
    """
    cost = -log(xác suất). Cộng cost tương đương nhân xác suất, nên bước
    chẩn đoán tối thiểu hoá tổng cost chính là tìm tổ hợp sửa CÓ KHẢ NĂNG
    NHẤT chứ không phải tổ hợp ít thay đổi nhất một cách tuỳ tiện.
    """
    return -math.log(XAC_SUAT_TIEN_NGHIEM[source] * trong_so)


def tu_scale(gia_tri) -> list[Candidate]:
    """
    Ứng viên sai đơn vị: nhân 10^k.

    Giữ nguyên kiểu số nguyên khi chia hết, vì mọi con số trên báo cáo tài
    chính là số nguyên đồng và một giá trị thành float ở đây sẽ kéo theo
    sai số dấu phẩy động vào phép kiểm đẳng thức.
    """
    ung_vien = []
    for k in BAC_SCALE:
        moi = gia_tri * (10**k) if k > 0 else gia_tri / (10 ** abs(k))
        if k < 0:
            if gia_tri % (10 ** abs(k)) != 0:
                continue
            moi = gia_tri // (10 ** abs(k))
        ung_vien.append(
            Candidate(value=moi, source="scale", cost=_cost("scale"), evidence={"k": k})
        )
    return ung_vien


def tu_dau(gia_tri) -> list[Candidate]:
    """
    Ứng viên mất dấu âm: số âm trên BCTC ghi bằng ngoặc đơn, và OCR đọc
    "(1.234.567)" thành "1234567" là chuyện thường.
    """
    if gia_tri == 0:
        return []

    return [
        Candidate(
            value=-gia_tri,
            source="sign",
            cost=_cost("sign"),
            evidence={"ly_do": "mất dấu ngoặc âm"},
        )
    ]


def tu_nham_chu_so(gia_tri, n_cap: int | None = None) -> list[Candidate]:
    """
    Ứng viên nhầm chữ số: mỗi chữ số ĐÃ ĐỌC RA được thay bằng các chữ số
    THẬT có thể đã sinh ra nó, theo ma trận nhầm đã đo.

    Chiều tra là chiều NGƯỢC. Con số đang cầm trong tay là con số OCR đã
    đọc ra, nên câu hỏi đúng là "chữ số thật nào bị đọc thành chữ số này",
    không phải "chữ số này bị đọc thành gì". Hai câu đó cho hai tập khác
    hẳn nhau vì ma trận nhầm KHÔNG đối xứng: `9→0` quan sát được 23 lần
    còn `0→9` không lần nào.

    Chỉ thay MỘT chữ số mỗi ứng viên. Hai chữ số cùng sai trong một con số
    là chuyện hiếm hơn hẳn, và cho phép nó sẽ làm không gian ứng viên phình
    theo bình phương — mà không gian phình thì bước chẩn đoán NP-hard ở C2
    chậm theo.
    """
    am = gia_tri < 0
    chu_so = str(abs(int(gia_tri)))
    n_cap = N_CAP_UNG_VIEN if n_cap is None else n_cap

    ung_vien = []
    for vi_tri, ky_tu in enumerate(chu_so):
        for thay in ung_vien_cho_chu_so(ky_tu, n=n_cap):
            if vi_tri == 0 and thay == "0" and len(chu_so) > 1:
                continue   # số không bắt đầu bằng 0

            moi_chuoi = chu_so[:vi_tri] + thay + chu_so[vi_tri + 1 :]
            moi = int(moi_chuoi)
            ung_vien.append(
                Candidate(
                    value=-moi if am else moi,
                    source="ocr_alt",
                    cost=_cost("ocr_alt"),
                    evidence={"vi_tri": vi_tri, "doc_ra": ky_tu, "that_co_the": thay},
                )
            )
    return ung_vien


def tu_o_lan_can(o_lan_can) -> list[Candidate]:
    """
    Ứng viên lệch dòng / lệch cột: lấy thẳng giá trị của các ô lân cận
    trong cùng vùng bảng.

    Đây là nguồn GIÁ TRỊ NHẤT và cũng tốn nhất — nó đòi OCR toàn vùng bảng
    chứ không chỉ đọc một con số. Và nó là thứ KHÔNG PARADIGM NÀO trước
    đây có: Fellegi-Holt điền từ bản ghi donor, data reconciliation hiệu
    chỉnh liên tục, HoloClean tra từ điển ngoài. Không cái nào lấy ứng viên
    từ chính trang giấy, vì nguồn của chúng không hỏi lại được.

    o_lan_can là danh sách (giá trị, bbox) đã OCR sẵn — truyền vào chứ
    không tự OCR ở đây, để module này test được mà không cần EasyOCR.
    """
    ung_vien = []
    for gia_tri, bbox in o_lan_can:
        ung_vien.append(
            Candidate(
                value=gia_tri,
                source="neighbor_cell",
                cost=_cost("neighbor_cell"),
                evidence={"bbox": bbox},
            )
        )
    return ung_vien


def tu_phieu_vlm(votes: dict, gia_tri_thang) -> list[Candidate]:
    """
    Ứng viên từ các giá trị THUA phiếu của bước self-consistency.

    Gần như miễn phí nếu đã chạy k mẫu — model đã đọc ra những con số này
    rồi, chỉ là chúng không thắng. Vứt đi thì phải gọi lại VLM đúng số lần
    ấy để có lại.

    cost hạ theo tỷ lệ phiếu: một giá trị được 2/5 mẫu ủng hộ hợp lý hơn
    hẳn một giá trị chỉ 1/5, và bước chẩn đoán phải thấy được khác biệt đó.
    """
    tong_phieu = sum(votes.values())
    if not tong_phieu:
        return []

    ung_vien = []
    for chuoi, so_phieu in votes.items():
        if chuoi in ("None", str(gia_tri_thang)):
            continue
        try:
            gia_tri = int(chuoi)
        except ValueError:
            continue

        ty_le = so_phieu / tong_phieu
        ung_vien.append(
            Candidate(
                value=gia_tri,
                source="vlm_vote",
                cost=_cost("vlm_vote", ty_le),
                evidence={"so_phieu": so_phieu, "tong_phieu": tong_phieu},
            )
        )
    return ung_vien


def _khu_trung_va_cat(ung_vien: list[Candidate], gia_tri_hien_tai) -> list[Candidate]:
    """
    Khử trùng theo GIÁ TRỊ, giữ ứng viên rẻ nhất, rồi cắt theo trần.

    Khử trùng theo giá trị chứ không theo (giá trị, nguồn): với bước chẩn
    đoán thì hai ứng viên cùng con số là cùng một lựa chọn, và để cả hai
    chỉ làm không gian tìm kiếm phình lên mà không thêm lựa chọn nào.

    Cắt theo trần MỖI NGUỒN trước, rồi mới xếp chung theo cost. Xếp thuần
    theo cost sẽ để nguồn đông nhất chiếm hết chỗ — xem MAX_MOI_NGUON.
    """
    theo_nguon: dict[str, list[Candidate]] = {}
    for uv in ung_vien:
        if uv.value == gia_tri_hien_tai:
            continue   # không phải "sửa" nếu ra đúng giá trị đang có
        theo_nguon.setdefault(uv.source, []).append(uv)

    da_cat: list[Candidate] = []
    for cung_nguon in theo_nguon.values():
        cung_nguon.sort(key=lambda uv: uv.cost)
        da_cat.extend(cung_nguon[:MAX_MOI_NGUON])

    tot_nhat: dict = {}
    for uv in da_cat:
        cu = tot_nhat.get(uv.value)
        if cu is None or uv.cost < cu.cost:
            tot_nhat[uv.value] = uv

    ket_qua = sorted(tot_nhat.values(), key=lambda uv: (uv.cost, str(uv.value)))

    return ket_qua[:MAX_UNG_VIEN]


def generate(
    field_name: str,
    current,
    o_lan_can=None,
    votes: dict | None = None,
) -> list[Candidate]:
    """
    Sinh tập ứng viên cho MỘT chỉ tiêu, đã khử trùng và cắt theo trần.

    current là FieldResult hoặc một con số trần. Nhận cả hai vì các
    baseline đối chứng chạy trên giá trị trần, không có confidence.

    o_lan_can: danh sách (giá trị, bbox) các ô số trong cùng vùng bảng,
    đã OCR sẵn. None nghĩa là chưa OCR vùng — nguồn giá trị nhất bị tắt,
    và đó là một quyết định về chi phí cần ghi lại chứ không phải mặc định
    êm ái.

    Trả về danh sách xếp theo cost tăng dần.
    """
    gia_tri = getattr(current, "value", current)
    if gia_tri is None:
        return []

    phieu = votes if votes is not None else getattr(current, "votes", {})

    ung_vien = [
        *tu_nham_chu_so(gia_tri),
        *tu_o_lan_can(o_lan_can or []),
        *tu_dau(gia_tri),
        *tu_scale(gia_tri),
        *tu_phieu_vlm(phieu or {}, gia_tri),
    ]

    return _khu_trung_va_cat(ung_vien, gia_tri)
