"""
Sinh tập ứng viên sửa lỗi từ chính tài liệu.

Năm nguồn THÔNG THƯỜNG, mỗi nguồn bắt một chế độ lỗi khác nhau. Ba nguồn
đầu cần provenance (bbox của vùng đã đọc), nguồn cuối cần các giá trị thua
phiếu của bước self-consistency.

Nguồn thứ sáu, `dong_trong`, đứng riêng vì nó **thay thế** cả năm nguồn kia
chứ không cộng thêm vào — xem `tu_dong_trong()`. Nó chỉ nổ khi chỉ tiêu
không neo được vào vùng nào trên trang, tức khi không còn chỗ nào để đọc
lại, và khi đó năm nguồn kia đều chỉ là phép biến đổi của một con số máy đã
bịa ra.

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

from fields_config import CO_THE_VANG_MAT
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
    # Dòng trống trên biểu mẫu — tu chính PREREGISTRATION.md 05/09/2026.
    #
    # Đặt 0,20 (bằng `sign`, THẤP HƠN `ocr_alt`) là có chủ đích và lệch về
    # phía an toàn. Cost thấp nghĩa là ưu tiên cao, nên nếu để nguồn này rẻ
    # nhất thì bộ giải sẽ thích xoá trắng một dòng hơn là sửa một chữ số đọc
    # nhầm ở chỗ khác — mà xoá trắng một dòng CÓ IN chính là chế độ lỗi đã
    # điền `tong_tai_san = 0` cho PLX ngày 04/09. Sai theo chiều đắt thì chỉ
    # tiêu không được sửa; sai theo chiều rẻ thì nó bị điền 0 một cách im lặng.
    "dong_trong": 0.20,
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
# Spec đề xuất 10. Từng để 12 vì riêng nguồn `scale` đã đóng góp 6 ứng viên
# có cấu trúc khác hẳn nhau, và cắt bớt chúng là cắt đúng chế độ lỗi mà ràng
# buộc kế toán CHỨNG MINH ĐƯỢC là không bao giờ phát hiện nổi — hệ ràng
# buộc thuần nhất nên mọi bội vô hướng của nghiệm cũng là nghiệm.
#
# NÂNG LÊN 20 ngày 25/08/2026, dựa trên số đo chứ không phải cảm tính. Ở
# trần 12, bộ sinh sinh trung vị 14 ứng viên nhầm chữ số cho mỗi chỉ tiêu
# nhưng chỉ 6 sống sót, nên độ phủ `digit_substitution` rơi từ 0,831 xuống
# 0,369 — đúng tỷ lệ 6/14 của phép chọn ngẫu nhiên. Không cách XẾP nào cứu
# được (đã thử ba cách, xem HANDOFF mục 0 Câu 5), vì bộ tiêm chọn vị trí bị
# hỏng ĐỀU XÁC SUẤT nên không tương quan với bất kỳ thứ tự nào bộ sinh biết.
#
# Trần vẫn phải có: bước chẩn đoán ở C2 là NP-hard, và số ứng viên mỗi
# trường vào thẳng cơ số của không gian tìm kiếm.
MAX_UNG_VIEN = 20

# Trần cho MỖI nguồn, áp trước khi xếp theo cost.
#
# Không có nó thì xếp thuần theo cost sẽ để nguồn đông nhất chiếm hết chỗ:
# một con số 14 chữ số sinh ra tới 28 biến thể nhầm chữ số, tất cả đều rẻ
# hơn mọi ứng viên scale. Mà các nguồn bị chèn ra ngoài lại chính là các
# nguồn bắt những chế độ lỗi mà nguồn đông kia không bắt được.
#
# NÂNG TỪ 6 LÊN 10 ngày 25/08/2026. Đo trên 10 hồ sơ XBRL, 20 lượt mỗi mức,
# trần thời gian 10 giây:
#
#   | trần   | ứng viên/chỉ tiêu | median | chạm trần giờ | REPAIRED | vượt trần |
#   |--------|------------------:|-------:|--------------:|---------:|----------:|
#   | 6 / 12 |              11,9 |   5 ms |          10 % |        3 |         5 |
#   | 10 / 20|              18,6 |   6 ms |          20 % |        6 |         0 |
#   | 14 / 28|              22,1 |   7 ms |          20 % |        6 |         0 |
#
# Ba điều rút ra. Một, chi phí nằm TRỌN ở phần đuôi — median gần như không
# đổi, chỉ tỷ lệ chạm trần thời gian tăng. Hai, nới trần đổi 5 lượt
# `vuot_tran_thay_doi` lấy 3 lượt REPAIRED và 2 lượt hết giờ, tức số lượt
# sửa được TĂNG GẤP ĐÔI. Ba, mức 14/28 cho kết quả Y HỆT mức 10/20 nhưng
# tốn thêm ứng viên, nên 10/20 lấy trọn phần lợi ở chi phí thấp hơn.
#
# Hệ quả phải theo dõi: lượt chạm trần thời gian trả ABSTAIN với mã
# `het_gio`, tức một loại ABSTAIN THỨ BA bên cạnh `vo_nghiem` và
# `vuot_tran_thay_doi`. Nó KHÔNG chứng minh gì về tài liệu — chỉ nói ta hết
# giờ tìm — nên bảng kết quả phải đếm nó riêng, và `bao_cao()` đã làm vậy.
MAX_MOI_NGUON = 10

# Phạt cost theo HẠNG của ô lân cận. Cộng thẳng vào cost, tức nhân thêm một
# hệ số khả năng vào xác suất tiên nghiệm của nguồn — vẫn nhất quán với nghĩa
# `cost = −log(xác suất)`, không phải một thang điểm bịa ra.
#
# VÌ SAO BẮT BUỘC PHẢI CÓ. Nếu mọi ô lân cận cùng cost thì phép cắt theo trần
# `MAX_MOI_NGUON` thành BỐC THĂM: đổ vào 200 ô của một vùng bảng thì 10 ô sống
# sót là 10 ô tuỳ ý, và ô đúng gần như chắc chắn không nằm trong đó. Dự án đã
# trả giá đúng chỗ này một lần: ở trần 12, bộ sinh sinh trung vị 14 ứng viên
# nhầm chữ số mà chỉ 6 sống, độ phủ rơi 0,831 → 0,369 — ĐÚNG tỷ lệ 6/14 của
# phép chọn ngẫu nhiên. Trần chỉ có nghĩa khi thứ tự có nghĩa.
#
# 1.0 là một lựa chọn MÔ HÌNH, chưa hiệu chỉnh trên dữ liệu — nó chỉ nói "hạng
# sau đắt hơn hạng trước", chưa nói đắt hơn bao nhiêu là đúng. Đo bằng
# `src/eval/do_phu_ung_vien.py` rồi mới chốt.
PHAT_HANG_LAN_CAN = 1.0


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


def _chong_nhau(a1: int, a2: int, b1: int, b2: int) -> bool:
    """Hai đoạn [a1,a2] và [b1,b2] có phần chung không."""
    return min(a2, b2) > max(a1, b1)


def hang_lan_can(bbox_o, bbox_dang_xet) -> tuple[int, float] | None:
    """
    Xếp một ô lân cận vào HẠNG, kèm khoảng cách trong hạng đó.

    Trả `(hạng, khoảng cách)`, hoặc None nếu ô không thuộc hạng nào.

    VÙNG LÂN CẬN CÓ HÌNH CHỮ THẬP, KHÔNG PHẢI HÌNH TRÒN — và đó là chỗ đáng
    nhớ nhất của hàm này. Ba hạng ứng với ba chế độ lỗi khác nhau, xếp theo
    đúng thứ tự đáng tin:

      0 — CHÍNH Ô ĐÓ, đọc lại bằng engine khác. Ô chồng lên bbox của chỉ tiêu
          đang xét. Đây là ứng viên giá trị nhất và ít nhiễu nhất: VLM đọc ảnh
          bảng theo kiểu hiểu ngữ cảnh, EasyOCR đọc từng ô theo kiểu nhận dạng
          ký tự và đo được 0,999 trên ô số. Ca `BMP_2026Q1_TT99` — máy đọc
          ...595... trong khi giấy ghi ...959..., tức ĐẢO CHỖ hai chữ số — chỉ
          cứu được bằng hạng này, vì nguồn nhầm chữ số chỉ biết đổi MỘT chữ số
          thành chữ khác, không biết kiểu đảo chỗ.
      1 — CÙNG CỘT, lệch dòng. Chế độ lỗi `row_shift`.
      2 — CÙNG DÒNG, lệch cột. Chế độ lỗi `col_shift` — đúng thứ vừa cắn ở
          `SBT_2025Q2_TT200`, nơi máy lấy cột luỹ kế thay cột quý.

    Ô nằm CHÉO — vừa lệch dòng vừa lệch cột — bị loại hẳn: nó không ứng với
    chế độ lỗi nào cả, và nhận nó vào chỉ làm tập ứng viên phình ra bằng những
    con số chỉ tình cờ ở gần.
    """
    x1, y1, x2, y2 = bbox_o
    dx1, dy1, dx2, dy2 = bbox_dang_xet

    cung_dong = _chong_nhau(y1, y2, dy1, dy2)
    cung_cot = _chong_nhau(x1, x2, dx1, dx2)

    if cung_dong and cung_cot:
        return 0, 0.0
    if cung_cot:
        return 1, abs((y1 + y2) / 2 - (dy1 + dy2) / 2)
    if cung_dong:
        return 2, abs((x1 + x2) / 2 - (dx1 + dx2) / 2)
    return None


def tu_o_lan_can(o_lan_can, bbox_dang_xet=None) -> list[Candidate]:
    """
    Ứng viên đọc lại từ tờ giấy: giá trị các ô trong cùng vùng bảng.

    Đây là nguồn GIÁ TRỊ NHẤT và cũng tốn nhất — nó đòi OCR toàn vùng bảng
    chứ không chỉ đọc một con số. Và nó là thứ KHÔNG PARADIGM NÀO trước
    đây có: Fellegi-Holt điền từ bản ghi donor, data reconciliation hiệu
    chỉnh liên tục, HoloClean tra từ điển ngoài. Không cái nào lấy ứng viên
    từ chính trang giấy, vì nguồn của chúng không hỏi lại được.

    o_lan_can là danh sách (giá trị, bbox) đã OCR sẵn — truyền vào chứ
    không tự OCR ở đây, để module này test được mà không cần EasyOCR.

    bbox_dang_xet là bbox của chính chỉ tiêu đang sửa, lấy từ Provenance.
    Có nó thì ứng viên được XẾP HẠNG theo hình chữ thập (xem `hang_lan_can`)
    và cost tăng dần theo hạng, nên phép cắt theo trần giữ lại đúng những ô
    đáng tin nhất. KHÔNG có nó thì mọi ô cùng cost, và lúc ấy trần cắt tuỳ
    tiện — chấp nhận được cho baseline chạy trên giá trị trần, KHÔNG chấp
    nhận được cho đường chạy thật.
    """
    ung_vien = []
    for gia_tri, bbox in o_lan_can:
        if bbox_dang_xet is None:
            ung_vien.append(
                Candidate(
                    value=gia_tri,
                    source="neighbor_cell",
                    cost=_cost("neighbor_cell"),
                    evidence={"bbox": bbox},
                )
            )
            continue

        xep = hang_lan_can(bbox, bbox_dang_xet)
        if xep is None:
            continue

        hang, khoang_cach = xep
        ung_vien.append(
            Candidate(
                value=gia_tri,
                source="neighbor_cell",
                # Khoảng cách chỉ dùng để phân xử TRONG một hạng, nên nó phải
                # nhỏ hơn khoảng cách giữa hai hạng. Chuẩn hoá bằng 1e-6 chứ
                # không chia cho chiều cao trang: ở đây chỉ cần thứ tự đúng,
                # và một phép chia nữa là thêm một chỗ để sai đơn vị.
                cost=_cost("neighbor_cell") + hang * PHAT_HANG_LAN_CAN + khoang_cach * 1e-6,
                evidence={"bbox": bbox, "hang": hang, "khoang_cach": round(khoang_cach, 1)},
            )
        )
    return ung_vien


def tu_dong_trong(field_name: str) -> list[Candidate]:
    """
    Ứng viên `0` cho chỉ tiêu không neo được vào vùng nào — tu chính 05/09/2026.

    Trả về danh sách RỖNG nếu chỉ tiêu không nằm trong `CO_THE_VANG_MAT`, và
    người gọi phải hiểu danh sách rỗng ở đây là "không áp dụng" chứ không phải
    "đã áp dụng và không tìm được gì".

    VÌ SAO `0` VẪN LÀ ĐỌC TỪ TỜ GIẤY. Thông tư 99/2025 mục 1.2.3 cho phép miễn
    trình bày chỉ tiêu không có số liệu, nên một dòng vắng mặt trên biểu mẫu là
    *bằng không*, không phải *chưa biết*. Tu chính 24/08/2026 đã chốt đúng cách
    đọc này cho người gán nhãn tay; đây chỉ là đưa nó sang phía pipeline. Đó
    cũng là chỗ phân biệt nó với baseline 9: dòng trống là quan sát về tài liệu
    NÀY, không phải con số vay từ tài liệu khác.

    VÌ SAO HẸP THEO `CO_THE_VANG_MAT`. Trạng thái `khong_co_vung` gộp hai
    chuyện khác hẳn nhau — dòng thật sự trống, và dòng CÓ IN mà khâu neo trượt.
    Danh sách trắng gồm tám dòng CHI TIẾT chọn theo cấu trúc biểu mẫu, và có
    test bất biến chặn mọi dòng TỔNG lọt vào, vì dòng tổng là bộ xương biểu mẫu
    nên luôn được in. Bỏ giới hạn này là dựng lại đúng ca `PLX_2026Q2_TT99` bị
    điền `tong_tai_san = 0` trong khi giá trị thật là 87.876 tỷ.
    """
    if field_name not in CO_THE_VANG_MAT:
        return []

    return [
        Candidate(
            value=0,
            source="dong_trong",
            cost=_cost("dong_trong"),
            evidence={
                "ly_do": "không neo được vào vùng nào, và chỉ tiêu được phép "
                         "vắng mặt trên biểu mẫu",
                "can_cu": "TT99 mục 1.2.3",
            },
        )
    ]


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
    bbox_dang_xet=None,
    khong_co_vung: bool = False,
) -> list[Candidate]:
    """
    Sinh tập ứng viên cho MỘT chỉ tiêu, đã khử trùng và cắt theo trần.

    current là FieldResult hoặc một con số trần. Nhận cả hai vì các
    baseline đối chứng chạy trên giá trị trần, không có confidence.

    khong_co_vung: chỉ tiêu này KHÔNG neo được vào vùng bảng nào trên trang.
    Cờ này phải truyền TƯỜNG MINH chứ không suy từ `o_lan_can` rỗng, vì rỗng
    còn có nghĩa "có vùng nhưng vùng không bóc được ô số nào" — hai chuyện
    khác hẳn nhau, và gộp chúng lại sẽ cho chỉ tiêu có vùng hưởng luật của
    chỉ tiêu không có vùng.

    Khi cờ này bật VÀ chỉ tiêu nằm trong `CO_THE_VANG_MAT`, tập ứng viên là
    ĐÚNG MỘT phần tử `0` và năm nguồn thông thường bị THAY THẾ — xem tu chính
    `PREREGISTRATION.md` 05/09/2026. Lý do thay vì cộng thêm: không có vùng
    nghĩa là không còn chỗ nào trên giấy để đọc lại, nên mọi ứng viên còn lại
    đều chỉ là phép biến đổi của một con số máy đã bịa ra từ hư không. Số đo
    05/09 cho thấy cả 4 ô mà phương pháp làm hỏng đều sinh ra đúng như vậy.

    o_lan_can: danh sách (giá trị, bbox) các ô số trong cùng vùng bảng,
    đã OCR sẵn. None nghĩa là chưa OCR vùng — nguồn giá trị nhất bị tắt,
    và đó là một quyết định về chi phí cần ghi lại chứ không phải mặc định
    êm ái.

    bbox_dang_xet: bbox của chính chỉ tiêu này trên trang, lấy từ Provenance.
    Thiếu nó thì các ô lân cận không xếp hạng được và trần sẽ cắt tuỳ tiện —
    xem `tu_o_lan_can`.

    Trả về danh sách xếp theo cost tăng dần.
    """
    gia_tri = getattr(current, "value", current)
    if gia_tri is None:
        return []

    if khong_co_vung:
        thay_the = tu_dong_trong(field_name)
        if thay_the:
            return _khu_trung_va_cat(thay_the, gia_tri)

    phieu = votes if votes is not None else getattr(current, "votes", {})

    ung_vien = [
        *tu_nham_chu_so(gia_tri),
        *tu_o_lan_can(o_lan_can or [], bbox_dang_xet),
        *tu_dau(gia_tri),
        *tu_scale(gia_tri),
        *tu_phieu_vlm(phieu or {}, gia_tri),
    ]

    return _khu_trung_va_cat(ung_vien, gia_tri)
