"""
NEO TOẠ ĐỘ của một chỉ tiêu: nó nằm ở Ô NÀO trong vùng bảng.

VÌ SAO PHẢI CÓ MODULE NÀY. Xếp hạng ô lân cận theo hình chữ thập
(`candidates.hang_lan_can`) cần một tâm để đo: cùng dòng với cái gì, cùng cột
với cái gì. Đường VLM không cho biết tâm đó — `Provenance.bbox` là bbox của cả
VÙNG BẢNG, vì model nhận nguyên ảnh vùng rồi trả về giá trị, nó không nói giá
trị nằm ở ô nào.

Đem bbox vùng làm tâm thì MỌI ô trong vùng đều chồng lên nó theo cả hai trục,
tức tất cả rơi vào hạng 0 với khoảng cách 0,0 và cost BẰNG NHAU TUYỆT ĐỐI.
Lúc ấy phép cắt theo trần `MAX_MOI_NGUON` thành bốc thăm — đúng chế độ hỏng mà
cả thiết kế chữ thập sinh ra để chặn, và đúng thứ đã kéo độ phủ từ 0,831 xuống
0,369 ở lần chạy trần 12. Xếp hạng có mặt trong code mà không có neo thì nó
nằm im, và nằm im một cách không ai thấy.

HAI TẦNG NEO, thử theo thứ tự chắc chắn giảm dần:

  1. KHỚP GIÁ TRỊ — tìm ô mà EasyOCR đọc ra đúng con số VLM đã trả. Đây là neo
     chính xác nhất vì nó chốt được cả dòng lẫn CỘT.
  2. DÒNG CỦA MÃ SỐ — khi không ô nào khớp. Ca này không hiếm mà là ca ĐÁNG
     QUAN TÂM NHẤT: VLM đọc sai thì đương nhiên không có ô nào mang giá trị
     sai ấy, tức tầng 1 trượt đúng vào những lượt cần sửa. Tầng 2 dò ô mã số
     của chỉ tiêu để biết DÒNG, rồi lấy dải ngang phủ các ô giá trị của dòng
     đó. Neo này nói được "dòng nào" mà không nói được "cột nào" — và đó là
     mô tả trung thực của thứ ta biết, chứ không phải một thiếu sót.

Trượt cả hai thì trả None, để `tu_o_lan_can()` biết mà tự khai là không xếp
hạng được, thay vì lặng lẽ dùng bbox vùng như bản trước.
"""

import re

from fields_config import Standard, line_codes_for


def _o_khop_gia_tri(o_so: list, gia_tri) -> tuple | None:
    """
    Bbox của ô mà OCR đọc ra ĐÚNG con số đang xét, hoặc None.

    So sánh bằng `==` trên int chứ không theo dung sai: cả hai vế đều là số
    nguyên đọc từ cùng một tờ giấy, nên "gần bằng" ở đây không có nghĩa gì —
    hai giá trị lệch nhau một đồng là hai ô khác nhau.
    """
    if gia_tri is None:
        return None

    try:
        muc_tieu = int(gia_tri)
    except (TypeError, ValueError):
        return None

    for gia_tri_o, bbox in o_so:
        if gia_tri_o == muc_tieu:
            return bbox
    return None


def _o_ma_so(o: list, ma: str) -> tuple | None:
    """
    Bbox của ô chỉ chứa MÃ SỐ DÒNG, hoặc None.

    Đòi ô khớp TRỌN mã số chứ không tìm mã nằm lẫn trong chuỗi dài: "100" là
    khúc con của "1.100.000", và một ô giá trị bị nhận nhầm thành ô mã số sẽ
    neo cả chỉ tiêu vào sai dòng — sai lặng lẽ, vì mọi thứ sau đó vẫn chạy.

    Mã số là chữ số, chỗ EasyOCR mạnh nhất (0,999 Levenshtein trên ô số theo
    `data/output/ocr_engine_easyocr.md`). Chỗ nó hỏng là chữ tiếng Việt có
    dấu — thứ hàm này không dùng tới. Cùng lập luận đã dùng cho probe dò dòng.
    """
    mau = re.compile(rf"^\W*{re.escape(ma)}\W*$")
    for chu, bbox in o:
        if mau.match(chu.strip()):
            return bbox
    return None


def _dai_gia_tri_cung_dong(o_so: list, bbox_ma: tuple) -> tuple | None:
    """
    Dải bao các ô GIÁ TRỊ nằm cùng dòng với ô mã số, hoặc None nếu dòng trống.

    Trả về một bbox tổng hợp chứ không phải bbox của một ô có thật — nó là
    "chỗ giá trị của dòng này nằm", và đó đúng là thứ ta biết khi chỉ dò được
    dòng. Neo vào chính ô mã số thì hỏng: ô mã số nằm ở cột trái, nên các ô
    giá trị của cùng dòng sẽ xếp hạng 2 (lệch cột) còn các ô cùng cột giá trị
    ở dòng khác thành CHÉO và bị loại — tức mất sạch ứng viên lệch dòng, đúng
    một trong hai chế độ lỗi nguồn này sinh ra để cứu.
    """
    _, ma_y1, _, ma_y2 = bbox_ma

    cung_dong = [
        bbox for _, bbox in o_so if min(bbox[3], ma_y2) > max(bbox[1], ma_y1)
    ]
    if not cung_dong:
        return None

    return (
        min(bbox[0] for bbox in cung_dong),
        min(bbox[1] for bbox in cung_dong),
        max(bbox[2] for bbox in cung_dong),
        max(bbox[3] for bbox in cung_dong),
    )


def neo_bbox(field: str, gia_tri, vung: dict, standard: Standard) -> tuple[tuple | None, str]:
    """
    Toạ độ ô của một chỉ tiêu trong một vùng bảng, kèm CÁCH neo được.

    Trả `(bbox, cách)` với cách thuộc tập đóng:
      "khop_gia_tri"  — tìm thấy ô OCR đọc ra đúng con số đang xét.
      "dong_ma_so"    — không khớp giá trị, nhưng dò được dòng qua mã số.
      "khong_neo"     — trượt cả hai, bbox là None.

    Cách neo đi ra CÙNG bbox chứ không để người gọi suy từ việc bbox có hay
    không: ba trạng thái này nói ba mức tin cậy khác hẳn nhau về ứng viên sinh
    ra sau đó, và một chứng chỉ sửa lỗi không phân biệt được chúng thì không
    đọc được.
    """
    bbox = _o_khop_gia_tri(vung.get("o_so", []), gia_tri)
    if bbox is not None:
        return bbox, "khop_gia_tri"

    entry = line_codes_for(standard).get(field)
    if entry is not None:
        bbox_ma = _o_ma_so(vung.get("o", []), entry[1])
        if bbox_ma is not None:
            dai = _dai_gia_tri_cung_dong(vung.get("o_so", []), bbox_ma)
            if dai is not None:
                return dai, "dong_ma_so"

    return None, "khong_neo"
