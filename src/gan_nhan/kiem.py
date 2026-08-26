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

`kiem_dau_khau_tru` phục vụ cùng mục đích nhưng cho một chế độ lỗi khác:
người gán nhãn chép đúng từng chữ số mà vẫn thấy đẳng thức lệch, vì ba dòng
khấu trừ in trong ngoặc đơn đã bị ghi thành số âm. Nó cũng chỉ BÁO chứ không
sửa hộ — đảo dấu giúp một giá trị người vừa gõ là đúng loại can thiệp âm
thầm mà cả module này được viết ra để chặn.
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


# Ba chỉ tiêu mà guideline mục 3.3 bắt ghi DƯƠNG dù báo cáo in trong ngoặc
# đơn. Để dưới dạng dữ liệu ở đây vì quy tắc phải có đúng một nơi định nghĩa.
GIA_VON = "gia_von_hang_ban"
TRUONG_THUE = ("thue_tndn_hien_hanh", "thue_tndn_hoan_lai")

DAU_DAT = "dat"
NGHI_SAI_DAU = "nghi_sai_dau"
CHUA_GO = "chua_go"
CHUA_QUYET_DINH_DUOC = "chua_quyet_dinh_duoc"


@dataclass(frozen=True)
class KetQuaMotDau:
    """Kết quả kiểm dấu của MỘT chỉ tiêu khấu trừ."""

    truong: str
    trang_thai: str
    ly_do: str


def _dao_dau_lam_can(values: dict, ten: str, identities) -> bool | None:
    """
    Đảo dấu MỘT trường có biến một đẳng thức đang lệch thành cân không.

    Trả None khi không đẳng thức nào chứa trường này chạy được — thiếu thành
    phần thì không kết luận được gì, và nói "không sao" lúc đó là kết luận.

    Đây là tiêu chí thay cho phép so mã 50 với mã 60 mà bản đầu dùng. Bản đầu
    xét dấu từng chỉ tiêu thuế bằng dấu của TỔNG số thuế, nên nó báo oan ca
    hoàn toàn hợp lệ: thuế hiện hành là chi phí lớn còn thuế hoãn lại là một
    khoản hoàn nhập âm. `MWG_2025Q1_TT200` đúng là ca đó — mã 52 bằng
    -10.894.797.039 mà đẳng thức B02 vẫn cân chính xác đến từng đồng.

    Tiêu chí mới không có chỗ cho ca ấy: nếu bộ số đã cân thì không có gì để
    báo. Nó cũng chính là chữ ký "lệch đúng gấp đôi" mà guideline mục 3.3 mô
    tả, viết dưới dạng kiểm được thay vì dạng lời khuyên.
    """
    chay_duoc = False

    for cac_thanh_phan, tong, _ in identities:
        can_co = [*cac_thanh_phan, tong]
        if ten not in can_co or any(values.get(t) is None for t in can_co):
            continue

        chay_duoc = True
        thang = max(abs(values[tong]), 1.0)
        if abs(sum(values[t] for t in cac_thanh_phan) - values[tong]) / thang <= DUNG_SAI:
            continue

        thu = dict(values)
        thu[ten] = -thu[ten]
        if abs(sum(thu[t] for t in cac_thanh_phan) - thu[tong]) / thang <= DUNG_SAI:
            return True

    return False if chay_duoc else None


def kiem_dau_khau_tru(values: dict, standard: Standard) -> list[KetQuaMotDau]:
    """
    Kiểm dấu ba chỉ tiêu khấu trừ, theo guideline mục 3.3.

    Vì sao cần một phép kiểm riêng thay vì để đẳng thức tự bắt: đẳng thức có
    bắt được, nhưng nó báo ra một con số lệch, và người gán nhãn không có
    cách nào phân biệt "lệch vì tôi ghi sai dấu" với "lệch vì báo cáo tự mâu
    thuẫn". Hai ca đó cần hai hành động trái ngược — một bên sửa, một bên
    tuyệt đối không được sửa mà phải ghi `notes`. Đoán nhầm ca là cách nhanh
    nhất để một tài liệu sạch bị chữa hỏng.

    Hai chỉ tiêu thuế xét theo `_dao_dau_lam_can`, KHÔNG theo dấu của tổng số
    thuế: mã 51 và mã 52 có dấu độc lập với nhau, nên một khoản hoàn nhập
    thuế hoãn lại ghi âm là hợp lệ ngay cả khi tổng số thuế là chi phí.

    Giá vốn hàng bán thì xét thẳng theo dấu, không cần đẳng thức:
    `FIELD_RULES` đặt `allow_negative` là False cho nó, tức âm là sai bất kể
    các chỉ tiêu quanh nó có cân hay không.
    """
    ket = []
    identities = identities_for(standard)

    gia_von = values.get(GIA_VON)
    if gia_von is None:
        ket.append(KetQuaMotDau(GIA_VON, CHUA_GO, "chưa gõ hoặc đọc không ra"))
    elif gia_von < 0:
        ket.append(
            KetQuaMotDau(
                GIA_VON,
                NGHI_SAI_DAU,
                "giá vốn hàng bán ghi âm — báo cáo in trong ngoặc đơn nhưng "
                "guideline mục 3.3 bắt ghi dương",
            )
        )
    else:
        ket.append(KetQuaMotDau(GIA_VON, DAU_DAT, ""))

    for ten in TRUONG_THUE:
        gia_tri = values.get(ten)
        if gia_tri is None:
            ket.append(KetQuaMotDau(ten, CHUA_GO, "chưa gõ hoặc đọc không ra"))
            continue
        if gia_tri >= 0:
            ket.append(KetQuaMotDau(ten, DAU_DAT, ""))
            continue

        theo_dang_thuc = _dao_dau_lam_can(values, ten, identities)
        if theo_dang_thuc is None:
            ket.append(
                KetQuaMotDau(
                    ten,
                    CHUA_QUYET_DINH_DUOC,
                    "ghi âm, nhưng đẳng thức chứa nó chưa chạy được vì thiếu "
                    "thành phần, nên chưa kết luận được gì về dấu",
                )
            )
        elif theo_dang_thuc:
            ket.append(
                KetQuaMotDau(
                    ten,
                    NGHI_SAI_DAU,
                    "ghi âm, và đảo dấu riêng trường này làm đẳng thức đang "
                    "lệch trở nên cân — guideline mục 3.3",
                )
            )
        else:
            ket.append(KetQuaMotDau(ten, DAU_DAT, ""))

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
    ("am_bang_dau_tru",
     "Số âm ghi bằng dấu trừ, không phải ngoặc; mã 11, 51, 52 ghi dương", True),
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
