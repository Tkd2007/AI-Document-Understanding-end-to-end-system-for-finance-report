"""
LAN KÝ HIỆU MẪU BIỂU: bộ báo cáo này là HỢP NHẤT hay RIÊNG.

Báo cáo tài chính Việt Nam in ký hiệu mẫu ngay phía trên bảng — `B01a-DN` cho
bộ riêng, `B01a-DN/HN` cho bộ hợp nhất. `layout_detection.tran_noi_tren()` nới
vùng cắt đi ngược lên theo chuỗi box chính là để lấy được dòng ấy, nên chuỗi
này nằm sẵn trong text OCR của vùng.

VẤN ĐỀ NÓ GIẢI. Ký hiệu không đọc được ở mọi bảng: trang xoay 90 độ thì ký hiệu
nằm ở CẠNH BÊN chứ không nằm phía trên, và không nới lên bao nhiêu cũng không
tới (đo được trên `SBT` trang 8 và `DGC` trang 7, đều là bảng kết quả kinh
doanh xoay ngang). Nhưng một hồ sơ BCTC thường thuần một bộ — Vietstock phát
hành bản riêng và bản hợp nhất thành hai file khác nhau, và cả 10 tài liệu gold
đều thuần một loại. Nên chỗ nào đọc được thì lan sang chỗ không đọc được.

CHỈ LAN HẬU TỐ, KHÔNG LAN CẢ CỤM. Ký hiệu gồm mấy phần có phạm vi khác hẳn
nhau:

    B01 / B02 / B03   bảng nào                KHÔNG lan — mỗi trang một khác
    a / b             loại kỳ báo cáo         lan được, nhưng không ai cần
    /HN hoặc không    hợp nhất / riêng        ĐƯỢC lan — đúng phần cần lan

Lan cả cụm thì trang báo cáo kết quả kinh doanh bị gán nhãn là bảng cân đối.

BA RÀNG BUỘC GIỮ CHO NÓ AN TOÀN:

  1. Chốt một lần và ghi lại NGUỒN, đúng khuôn `router.chon_chuan()` dùng cho
     chuẩn mẫu biểu. Một vùng đọc được ký hiệu và một vùng thừa hưởng từ vùng
     trước là hai mức tin cậy khác nhau, và bảng kết quả phải tách được chúng.
  2. Không ghi đè im lặng. Vùng sau đọc ra hậu tố khác vùng trước là TÍN HIỆU
     phải ghi lại chứ không phải thứ để đè đi: hoặc file thật sự đóng gói cả
     hai bộ, hoặc khâu cắt/đọc hỏng. Cả hai đều đáng biết, và cả hai đều biến
     mất nếu chỉ giữ giá trị cuối cùng.
  3. Không đọc được ở đâu cả thì trả None, không đoán bừa — nguyên tắc
     `fields_config.detect_standard()` đang giữ.

GIỚI HẠN ĐÃ BIẾT: tiền đề "mỗi hồ sơ thuần một bộ" mới kiểm trên 10 tài liệu
từ MỘT nguồn phát hành. Hồ sơ tải từ website công ty hoặc cổng HOSE đôi khi
đóng gói cả hai bộ trong một file. Vì thế quy tắc ở đây là "đọc ở đâu đọc
được, lan sang chỗ không đọc được, nhưng giữ phép đối chiếu" — chứ không phải
"đọc một lần rồi thôi".
"""

import re

# Ký hiệu mẫu, với chữ số viết kèm các chữ cái dễ nhầm — cùng lý do đã ghi ở
# `fields_config.FORM_MARKERS`: EasyOCR đọc "Mẫu B 01a - DN" ra "Mâu B Ola".
#
# Phần `DN` bắt buộc phải có mặt: nó là thứ phân biệt một ký hiệu mẫu thật với
# một chuỗi "B01" nhắc tới biểu mẫu trong câu văn (thuyết minh hay dẫn chiếu
# chéo đều nhắc "B01" mà không kèm gì). Không đòi `DN` thì mọi dẫn chiếu như
# thế đều bị đọc thành một ký hiệu mẫu "bộ riêng", tức bịa ra kết luận.
KY_HIEU = re.compile(
    r"B\s*[O0o]\s*[1lI|23]\s*[ab]?\s*[-–—]?\s*DN"
    r"(?P<hn>\s*[/|\\–-]\s*HN)?",
    flags=re.IGNORECASE,
)

# Tên người đọc được, tra theo hậu tố. Trả nguyên hậu tố ra ngoài thì mọi nơi
# tiêu thụ phải tự biết "HN" nghĩa là gì, và một khoá metadata cần tự giải
# thích được.
TEN_LOAI = {"HN": "hop_nhat", "DN": "rieng"}


def doc_hau_to(text: str) -> str | None:
    """
    Hậu tố hợp nhất/riêng đọc được trong một đoạn text, hoặc None.

    Trả "HN", "DN", hoặc None khi không thấy ký hiệu mẫu nào. Trả None LUÔN CẢ
    khi trong cùng đoạn có hai ký hiệu mâu thuẫn nhau: đoạn đó không cho một
    kết luận, và một kết luận nửa vời ở đây sẽ được lan đi khắp tài liệu.

    KHÔNG BAO GIỜ trả về phần `B01`/`B02`/`B03`. Phần đó nói bảng nào, mỗi
    trang một khác, và lan nó đi là gán nhãn bảng cân đối cho trang kết quả
    kinh doanh.
    """
    tim_thay = {
        "HN" if khop.group("hn") else "DN" for khop in KY_HIEU.finditer(text or "")
    }
    if len(tim_thay) != 1:
        return None
    return tim_thay.pop()


def lan_ky_hieu(cac_vung) -> dict:
    """
    Lan hậu tố qua các vùng bảng theo ĐÚNG thứ tự đọc.

    `cac_vung` là iterable (số trang, chỉ số vùng, text OCR của vùng).

    Trả về:
      "loai"       — "hop_nhat" | "rieng" | None, kết luận CHỐT cho cả tài liệu.
      "nguon"      — "doc_duoc" khi có ít nhất một vùng đọc được ký hiệu,
                     "khong_doc_duoc" khi không vùng nào đọc được.
      "theo_vung"  — {"trang-vùng": (loại, "doc_duoc" | "lan")}, chỉ gồm vùng
                     có kết luận; vùng chưa lan tới được thì vắng mặt.
      "mau_thuan"  — danh sách vùng đọc ra hậu tố KHÁC với kết luận đã chốt.

    Kết luận chốt là hậu tố ĐỌC ĐƯỢC ĐẦU TIÊN, và những lần đọc sau mâu thuẫn
    với nó KHÔNG đè lên nó — chúng đi vào `mau_thuan`. Giữ giá trị cuối cùng
    thay vì ghi lại mâu thuẫn là cách xoá đúng tín hiệu đáng giá nhất mà cơ chế
    này thu được: hoặc file đóng gói cả hai bộ, hoặc khâu cắt/đọc hỏng.

    `theo_vung` vẫn ghi hậu tố ĐỌC ĐƯỢC TẠI CHỖ, kể cả khi nó mâu thuẫn với
    kết luận chốt — nó mô tả tờ giấy, còn "loai" mô tả kết luận về hồ sơ.
    """
    chot: str | None = None
    theo_vung: dict[str, tuple[str, str]] = {}
    mau_thuan: list[dict] = []

    for trang, chi_so_vung, text in cac_vung:
        khoa = f"{trang}-{chi_so_vung}"
        doc_duoc = doc_hau_to(text)

        if doc_duoc is None:
            if chot is not None:
                theo_vung[khoa] = (TEN_LOAI[chot], "lan")
            continue

        theo_vung[khoa] = (TEN_LOAI[doc_duoc], "doc_duoc")

        if chot is None:
            chot = doc_duoc
        elif doc_duoc != chot:
            mau_thuan.append(
                {
                    "trang": trang,
                    "vung": chi_so_vung,
                    "da_chot": TEN_LOAI[chot],
                    "doc_duoc": TEN_LOAI[doc_duoc],
                }
            )

    return {
        "loai": None if chot is None else TEN_LOAI[chot],
        "nguon": "khong_doc_duoc" if chot is None else "doc_duoc",
        "theo_vung": theo_vung,
        "mau_thuan": mau_thuan,
    }
