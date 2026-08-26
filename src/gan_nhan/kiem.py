"""
Kiểm đẳng thức trên số NGƯỜI vừa gõ, và danh mục kiểm của guideline mục 8.

VÌ SAO CÔNG CỤ GÁN NHÃN ĐƯỢC PHÉP KIỂM ĐẲNG THỨC, DÙ LUẬT 1 CẤM XEM ĐẦU RA
PIPELINE: hai thứ này khác nhau về bản chất. Luật 1 cấm nhìn thấy con số của
model, vì thấy rồi thì sẽ neo vào đó và ground truth nhiễm đúng bằng lỗi mà
nó sinh ra để đo. Kiểm đẳng thức không mang con số nào từ bên ngoài vào — nó
chỉ nói bộ số NGƯỜI vừa gõ có tự mâu thuẫn không, đúng như một phép tính
tổng làm tay. Không có model nào tham gia.

NHƯNG NÓ CÓ MỘT RỦI RO RIÊNG, và cả module này được viết quanh việc chặn nó.
Thấy đẳng thức lệch, người gán nhãn có thể sửa một chữ số cho cân thay vì
đọc lại. Làm vậy sẽ cho ra một tập gold LUÔN cân — và tập gold luôn cân thì
không đo nổi tỷ lệ lỗi thật, tức phá đúng thứ đắt nhất của cả nghiên cứu.
Guideline mục 8 đã có dòng "Không sửa số cho cân đẳng thức; lệch đáng kể thì
ghi notes". Ba biện pháp ở đây làm dòng đó có hiệu lực thay vì chỉ là lời
khuyên:

  1. Kết quả kiểm nói ĐẲNG THỨC NÀO lệch và lệch BAO NHIÊU. Nó không bao giờ
     nói giá trị đúng phải là bao nhiêu, dù suy ra được — biết đáp án là
     đúng thứ biến việc đọc lại thành việc điền vào.
  2. Số lần kiểm và việc có sửa giá trị SAU khi kiểm hay không được đếm và
     ghi vào file gold. Rủi ro không biến mất, nhưng nó thành đo được: về
     sau tách được nhóm tài liệu "cân ngay từ đầu" khỏi nhóm "cân sau khi
     sửa", và nếu hai nhóm cho kết quả khác nhau thì biết ngay.
  3. Đẳng thức thiếu thành phần được báo là `thieu_thanh_phan`, KHÔNG phải
     `dat`. Coi đẳng thức không chạy được là đẳng thức đã đạt là cách âm
     thầm biến một tài liệu dở dang thành một tài liệu sạch.
"""

from dataclasses import dataclass

from fields_config import IDENTITY_TOLERANCE_RATIO, Standard, identities_for

# Dung sai theo TỶ LỆ, không tuyệt đối. Giá trị cỡ 1e13 nên sai số làm tròn
# tuyệt đối cũng cỡ lớn, và một ngưỡng tuyệt đối sẽ hoặc bỏ sót mọi thứ hoặc
# bắt oan mọi thứ tuỳ quy mô doanh nghiệp. Mượn thẳng ngưỡng của
# fields_config để công cụ gán nhãn và bước kiểm của pipeline không bao giờ
# dùng hai ngưỡng khác nhau — lệch nhau ở đây sẽ làm người gán nhãn thấy
# "cân" trong khi pipeline thấy "lệch", và không ai hiểu vì sao.
DUNG_SAI = IDENTITY_TOLERANCE_RATIO

DAT = "dat"
LECH = "lech"
THIEU_THANH_PHAN = "thieu_thanh_phan"


@dataclass(frozen=True)
class KetQuaMotDangThuc:
    """Một dòng kết quả kiểm. `lech` là None khi đẳng thức không chạy được."""

    mo_ta: str
    trang_thai: str
    lech: float | None = None
    thieu: tuple[str, ...] = ()


def kiem_dang_thuc(values: dict, standard: Standard) -> list[KetQuaMotDangThuc]:
    """
    Chạy mọi đẳng thức của chuẩn trên bộ số người vừa gõ.

    `values` nhận giá trị ĐÃ QUY ĐỔI VỀ ĐỒNG, đúng thứ sẽ ghi vào file gold,
    để cái được kiểm là chính cái được lưu chứ không phải một bản trung gian.

    Giá trị `None` nghĩa là "có dòng mà đọc không ra" nên đẳng thức chứa nó
    KHÔNG chạy được; giá trị `0` là một con số bình thường và đẳng thức vẫn
    chạy. Phân biệt hai thứ này là toàn bộ lý do guideline mục 3.4 tồn tại.
    """
    ket = []
    for cac_thanh_phan, tong, mo_ta in identities_for(standard):
        can_co = [*cac_thanh_phan, tong]
        thieu = tuple(ten for ten in can_co if values.get(ten) is None)
        if thieu:
            ket.append(KetQuaMotDangThuc(mo_ta, THIEU_THANH_PHAN, None, thieu))
            continue

        lech = sum(values[ten] for ten in cac_thanh_phan) - values[tong]
        thang = max(abs(values[tong]), 1.0)
        trang_thai = DAT if abs(lech) / thang <= DUNG_SAI else LECH
        ket.append(KetQuaMotDangThuc(mo_ta, trang_thai, lech))

    return ket


# Danh mục kiểm, chép từ `ANNOTATION-GUIDELINE.md` mục 8.
#
# Để ở đây dưới dạng dữ liệu chứ không nhúng vào HTML, vì hai lý do: nó phải
# test được, và khi guideline sửa mục 8 thì chỗ phải sửa theo là một chỗ
# chứ không phải hai. Ô nào MÁY tự kiểm được thì đánh dấu `tu_dong` — công
# cụ tick hộ và người khỏi phải tick lại, còn ô nào chỉ người biết thì bắt
# người tick. Tick hộ một ô mà máy không thật sự kiểm được là cách biến
# danh mục kiểm thành thủ tục hình thức.
DANH_MUC_KIEM = [
    ("mu_voi_pipeline", "Chưa từng mở đầu ra pipeline của tài liệu này (Luật 1)", False),
    ("da_xac_dinh_chuan", "Đã xác định chuẩn mẫu biểu, hoặc ghi UNKNOWN kèm lý do", True),
    ("don_vi_nguyen_van", "unit_declared chép nguyên văn; unit_multiplier khớp", True),
    ("da_quy_doi", "Mọi giá trị đã quy đổi về đồng", True),
    ("am_bang_dau_tru", "Số âm ghi bằng dấu trừ, không phải ngoặc", True),
    ("o_trong_ghi_0", "Ô trống, dấu gạch, dòng vắng mặt ghi 0; null chỉ khi đọc không ra", False),
    ("doi_chieu_ma_so", "Đã đối chiếu mã số, không chỉ tên chỉ tiêu", False),
    ("kiem_cap_de_nham", "Đã kiểm riêng các cặp dễ nhầm ở guideline mục 3.6", False),
    ("khong_sua_cho_can", "Không sửa số cho cân đẳng thức; lệch đáng kể thì ghi notes", False),
    ("du_sieu_du_lieu", "source_url, downloaded_at, annotator, annotated_at đều có", True),
    ("da_bam_gio", "Đã bấm giờ tài liệu này, hoặc khai rõ là không đo giờ", True),
]

# Ô người PHẢI tự tick — máy không có cách nào biết.
O_NGUOI_PHAI_TICK = tuple(ma for ma, _, tu_dong in DANH_MUC_KIEM if not tu_dong)


def con_thieu_o_kiem(da_tick: dict) -> list[str]:
    """Những ô người phải tự tick mà chưa tick. Rỗng nghĩa là đủ."""
    return [ma for ma in O_NGUOI_PHAI_TICK if not da_tick.get(ma)]
