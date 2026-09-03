"""
Chặn ứng viên trước khi nhận, thay vì gắn cờ sau khi đã nhận.

VÌ SAO MODULE NÀY TỒN TẠI. Tầng ràng buộc của dự án chạy SAU khi trích xuất
xong: `validate_result()` gắn cảnh báo lên một bộ số đã chốt. Điều đó bỏ trống
đúng khoảnh khắc quan trọng nhất — lúc vòng lặp VLM quyết định NHẬN một con số
cho một chỉ tiêu còn trống. Ở khoảnh khắc ấy ta thường đã biết vài chỉ tiêu
khác của cùng tài liệu, và những gì đã biết đủ để nói "con số này không thể
đúng" mà không cần hỏi thêm ai.

CA ĐÃ DẪN TỚI NÓ, `GVR_2026Q2_TT99` trong lượt chấm 03/09/2026. Bảng cân đối
nằm ở trang 6–8 nhưng dòng tổng cộng không đọc được, nên `tong_tai_san` vẫn
trống. Điều kiện dừng sớm của nhánh VLM bị gác bởi `has_required_fields()`, mà
`tong_tai_san` là một trong ba field bắt buộc — thế là vòng lặp cày tiếp qua 65
trang thuyết minh và tới trang 78 thì nhận một con số của bảng khác:
406.588.902.083 trong khi giá trị thật là 90.263.949.529.178, sai 222 lần. Nó
kéo theo ba lỗi câm nữa ở cùng biểu mẫu. Trước tài liệu đó, bảng cân đối chưa
có một lỗi câm nào trong 18 tài liệu.

HAI PHÉP Ở ĐÂY KHÔNG BAO GIỜ SỬA, VÀ CHỈ MỘT TRONG HAI ĐƯỢC TỪ CHỐI.
`da_di_qua_bieu_mau()` từ chối; `vi_pham_dang_thuc()` chỉ chẩn đoán. Ứng viên
bị từ chối thì chỉ tiêu ở nguyên trạng thái trống, tức lỗi ỒN — cả module này
chỉ chuyển lỗi câm thành lỗi ồn chứ không sinh ra giá trị mới, nên không có
đường nào để nó làm đẹp con số một cách giả tạo. Xem `src/eval/metrics.py` về
vì sao lỗi ồn nhẹ hơn hẳn lỗi câm.

VÌ SAO PHÉP SỐ HỌC MẤT QUYỀN TỪ CHỐI, đo được ở lượt chấm 70 tài liệu ngày
03/09/2026. Nó ra tay 8 lần: đúng 1 lần (PLX, bác một `tong_tai_san` rụng chữ
số) và **sai 7 lần**, trong đó 6 lần vứt đi giá trị đúng tới từng đồng. Cả 6
lần đều cùng một cơ chế: cận suy từ dấu neo vào các giá trị ĐÃ NHẬN, nên khi
chính giá trị đã nhận là thứ sai thì cận trở thành thước hỏng. Ở REE,
`tai_san_ngan_han` vào trước với 893 tỷ trong khi giá trị thật là 8.931 tỷ —
rụng một chữ số — và từ cái neo ấy phép chặn bác sạch bốn số hạng đúng phía
sau, hai trong số đó mất vĩnh viễn. Ở VHC, `tai_san_ngan_han` nhận nhầm giá
trị của `tien_va_tuong_duong_tien`, rồi hai số hạng đúng bị bác và hai con số
SAI được nhận thay.

Ca GVR đã dẫn tới module này KHÔNG mất đi vì thay đổi ấy: ứng viên 406 tỷ đến
ở trang 78 trong khi B03 xong từ trang 12, nên `da_di_qua_bieu_mau()` bắt được
nó một mình.

QUAN HỆ VỚI `validate_result()`: không thay thế, và cố ý đặt ngưỡng khác hẳn.
Phép kiểm ở đây là lưới thưa, chỉ bắt mâu thuẫn THÔ BẠO — sai vài trăm lần,
tổng nhỏ hơn một số hạng của chính nó. Sai lệch cỡ vài phần trăm vẫn lọt qua và
vẫn phải để `validate_result()` bắt. Đặt lưới dày ở đây sẽ từ chối cả những con
số đúng chỉ vì một chỉ tiêu khác đọc hơi lệch, và mất chỉ tiêu là mất thật.
"""

from fields_config import FIELD_RULES, QuyUocDau, Standard, identities_for
from validation import coerce_number

# Biểu mẫu của từng chỉ tiêu. Thứ tự in trong một bộ báo cáo tài chính Việt
# Nam là bắt buộc theo Thông tư: B01 rồi B02 rồi B03, sau đó mới tới thuyết
# minh. Đó là một tiền đề về TỜ GIẤY, không phải về pipeline, nên nó không đổi
# theo chất lượng đọc.
NHOM_BIEU_MAU = {
    # B01 — Bảng cân đối kế toán
    "tai_san_ngan_han": "B01",
    "tien_va_tuong_duong_tien": "B01",
    "dau_tu_tc_ngan_han": "B01",
    "phai_thu_ngan_han": "B01",
    "hang_ton_kho": "B01",
    "tai_san_sinh_hoc_ngan_han": "B01",
    "tsnh_khac": "B01",
    "tai_san_dai_han": "B01",
    "tong_tai_san": "B01",
    "no_phai_tra": "B01",
    "von_chu_so_huu": "B01",
    "tong_nguon_von": "B01",
    # B02 — Báo cáo kết quả hoạt động kinh doanh
    "doanh_thu_thuan": "B02",
    "gia_von_hang_ban": "B02",
    "loi_nhuan_gop": "B02",
    "ln_thuan_hdkd": "B02",
    "ln_khac": "B02",
    "loi_nhuan_truoc_thue": "B02",
    "thue_tndn_hien_hanh": "B02",
    "thue_tndn_hoan_lai": "B02",
    "loi_nhuan_sau_thue": "B02",
    # B03 — Báo cáo lưu chuyển tiền tệ
    "lctt_hdkd": "B03",
    "lctt_dau_tu": "B03",
    "lctt_tai_chinh": "B03",
    "lctt_thuan": "B03",
    "tien_dau_ky": "B03",
    "anh_huong_ty_gia": "B03",
}

THU_TU_BIEU_MAU = ["B01", "B02", "B03"]

# Ngưỡng coi là mâu thuẫn THÔ BẠO. Cố ý rất rộng — xem đoạn cuối docstring
# module. 25% nghĩa là một chỉ tiêu đọc lệch tới một phần tư vẫn được nhận, và
# việc bắt nó là phần của `validate_result()`. Cái lưới này chỉ để chặn những
# con số sai bậc độ lớn hoặc lấy từ bảng khác — ở GVR là 222 lần.
NGUONG_VI_PHAM = 0.25

# Số trang phải cách xa mới coi là "đã lạc sang phần thuyết minh".
#
# VÌ SAO KHÔNG CHẶN NGAY KHI THẤY BIỂU MẪU SAU. Bản đầu của phép chặn vị trí
# từ chối một chỉ tiêu B01 ngay khi tài liệu đã cho bất kỳ chỉ tiêu B02 nào,
# và nó sai: một trang có nhiều vùng bảng, thứ tự vùng do khâu cắt quyết định
# chứ không do tờ giấy, nên hai biểu mẫu kề nhau hoàn toàn có thể ra ngược thứ
# tự trong vài trang liền. Bộ test `test_don_vi_theo_bang` bắt được đúng ca
# đó: B02 ra trước, B01 ở trang 5, và luật không có khoảng cách bác sạch B01
# của một tài liệu hoàn toàn bình thường.
#
# Tín hiệu thật ở ca GVR không phải "sai thứ tự" mà là "cách quá xa": ứng viên
# B01 tới ở trang 78 trong khi B03 đã xong từ trang 12, tức 66 trang sau. Ba
# biểu mẫu của một bộ báo cáo luôn nằm sát nhau; cách hàng chục trang nghĩa là
# đã lạc vào thuyết minh. 5 trang chừa biên rộng cho mọi kiểu đảo vùng.
KHOANG_CACH_TRANG = 5

# Số chỉ tiêu tối thiểu phải đọc được từ một biểu mẫu thì mới coi là ĐÃ THẤY nó.
#
# VÌ SAO KHÔNG TIN MỘT CHỈ TIÊU ĐƠN LẺ. Bản đầu coi bất kỳ chỉ tiêu nào cũng là
# bằng chứng đã đi qua biểu mẫu của nó, và nó phá dữ liệu đúng ngay trong lượt
# chạy đầu tiên. Ca `HAG_2026Q2_TT99` ngày 03/09/2026: TRANG BÌA có một ô tóm
# tắt in "Lợi nhuận sau thuế 1.126 Tỷ đồng". Đúng một chỉ tiêu B02, ở trang 1,
# thuộc một bảng tóm tắt chứ không thuộc biểu mẫu B02 nào. Nó đặt "B02 kết thúc
# ở trang 1", và tới trang 6 thì `no_phai_tra`, `von_chu_so_huu`,
# `tong_nguon_von` — ba con số của bảng cân đối thật, cộng khớp nhau tuyệt đối
# — bị bác sạch.
#
# Trang bìa và trang tóm tắt "chỉ số nổi bật" là chuyện thường trong báo cáo
# niêm yết, nên đây không phải ca hiếm. Đòi vài chỉ tiêu mới coi là đã thấy
# biểu mẫu thì một ô lạc không đủ sức đầu độc cả tài liệu, trong khi một biểu
# mẫu đọc thật bao giờ cũng cho nhiều hơn thế — ở GVR, B03 cho trọn cả sáu.
TOI_THIEU_FIELD = 3


def bieu_mau_cua(khoa: str) -> str | None:
    """Biểu mẫu in ra chỉ tiêu này, hoặc None với khoá không phải chỉ tiêu."""
    return NHOM_BIEU_MAU.get(khoa)


def _khong_am(khoa: str) -> bool:
    """Chỉ tiêu này có bị cấm mang giá trị âm không?"""
    return not FIELD_RULES.get(khoa, {}).get("allow_negative", False)


def ghi_nhan_bieu_mau(da_thay: dict, khoa: str, trang: int) -> None:
    """
    Ghi một chỉ tiêu vừa được nhận vào sổ biểu mẫu, tại chỗ.

    `da_thay` có dạng {biểu mẫu: {"so_field": n, "trang_cuoi": trang}}. Đếm số
    chỉ tiêu chứ không chỉ giữ trang cuối, vì số đếm mới là thứ phân biệt "đã
    đọc biểu mẫu này" với "vớ được một ô lạc" — xem `TOI_THIEU_FIELD`.
    """
    bieu_mau = bieu_mau_cua(khoa)
    if bieu_mau is None:
        return
    muc = da_thay.setdefault(bieu_mau, {"so_field": 0, "trang_cuoi": trang})
    muc["so_field"] += 1
    muc["trang_cuoi"] = trang


def da_di_qua_bieu_mau(
    khoa: str,
    trang_hien_tai: int,
    da_thay: dict,
    khoang_cach: int = KHOANG_CACH_TRANG,
    toi_thieu: int = TOI_THIEU_FIELD,
) -> str | None:
    """
    Lý do từ chối theo VỊ TRÍ, hoặc None nếu ứng viên còn hợp lệ.

    Thứ tự B01 → B02 → B03 → thuyết minh là bắt buộc trên tờ giấy. Nên khi một
    biểu mẫu SAU đã thật sự được đọc từ lâu, mà giờ mới có ứng viên cho một chỉ
    tiêu của biểu mẫu TRƯỚC, thì bảng ấy đã đi qua mất rồi và con số này đến từ
    chỗ khác — gần như luôn là một bảng trong thuyết minh.

    Hai điều kiện, và THIẾU MỘT TRONG HAI LÀ CƠ CHẾ HỎNG THEO HAI KIỂU NGƯỢC
    NHAU:

      * `khoang_cach` trang — thiếu nó thì thứ tự vùng đảo lộn trong vài trang
        liền cũng bị coi là đã đi qua (`test_don_vi_theo_bang` bắt được).
      * `toi_thieu` chỉ tiêu — thiếu nó thì một ô lạc trên trang bìa đủ sức
        đầu độc cả tài liệu (ca HAG, xem `TOI_THIEU_FIELD`).

    `da_thay` là sổ do `ghi_nhan_bieu_mau()` dựng.
    """
    cua_khoa = bieu_mau_cua(khoa)
    if cua_khoa is None:
        return None

    vi_tri = THU_TU_BIEU_MAU.index(cua_khoa)
    for bieu_mau, muc in da_thay.items():
        if bieu_mau not in THU_TU_BIEU_MAU:
            continue
        if THU_TU_BIEU_MAU.index(bieu_mau) <= vi_tri:
            continue
        if muc["so_field"] < toi_thieu:
            continue
        if trang_hien_tai - muc["trang_cuoi"] >= khoang_cach:
            return (
                f"{cua_khoa} đã đi qua từ lâu: {bieu_mau} đọc được "
                f"{muc['so_field']} chỉ tiêu và kết thúc ở trang "
                f"{muc['trang_cuoi']}, ứng viên này ở trang {trang_hien_tai} — "
                f"cách {trang_hien_tai - muc['trang_cuoi']} trang, gần như "
                f"chắc chắn là một bảng trong thuyết minh"
            )

    return None


def vi_pham_dang_thuc(
    khoa: str,
    gia_tri,
    da_biet: dict,
    standard: Standard,
    quy_uoc: QuyUocDau,
    nguong: float = NGUONG_VI_PHAM,
) -> str | None:
    """
    Lý do MÂU THUẪN số học, hoặc None nếu ứng viên không mâu thuẫn với gì.

    KHÔNG DÙNG ĐỂ TỪ CHỐI. Người gọi phải nhận ứng viên rồi ghi lý do này vào
    `warnings`; xem đoạn "VÌ SAO PHÉP SỐ HỌC MẤT QUYỀN TỪ CHỐI" ở docstring
    module cho bảy ca đo được, và `src/extract_vlm.py` cho chỗ dùng thật. Lý
    do gốc thì đã nằm ngay dưới đây, ở đoạn về H2: cận này nói "nhóm chỉ tiêu
    này mâu thuẫn nhau", nó KHÔNG nói thành viên nào sai.

    Dùng chính bộ đẳng thức của `fields_config.identities_for()` — không dựng
    một bộ ràng buộc thứ hai, vì hai nguồn sự thật cho cùng một dữ kiện là cách
    chắc chắn nhất để chúng lệch nhau mà không ai thấy.

    Mỗi đẳng thức có dạng `tổng các số hạng = tổng cộng`. Phép kiểm ở đây CHỈ
    dùng cận suy từ dấu: khi mọi số hạng đều bị cấm âm thì `tổng cộng >= từng
    số hạng` là hệ quả chắc chắn, nên một ứng viên `tổng cộng` nhỏ hơn hẳn một
    số hạng đã biết là bất khả. Đây chính là phép bắt được ca GVR: ứng viên
    `tong_tai_san` 406 tỷ nhỏ hơn `tai_san_ngan_han` đã biết là 37.897 tỷ,
    trong khi tài sản dài hạn không thể âm.

    CỐ Ý KHÔNG KIỂM ĐẲNG THỨC KHI ĐÃ BIẾT ĐỦ MỌI THÀNH VIÊN, dù nghe có vẻ là
    phép mạnh hơn. Đẳng thức lệch chỉ nói "có gì đó sai trong nhóm này", nó
    KHÔNG nói thành viên nào sai — mà thủ phạm hoàn toàn có thể là một giá trị
    đã nhận từ trước chứ không phải ứng viên đang xét. Bác ứng viên khi ấy là
    chọn bừa, và có thể vứt đúng con số đúng để giữ lại con số sai.

    Còn một lý do nặng hơn: quyết định "thành viên nào sai" CHÍNH LÀ bài toán
    định vị mà H2 đang nghiên cứu. Làm nó một cách tham lam ngay trong lúc
    trích xuất là giẫm lên đúng thứ đang được đem đi đo. Đẳng thức lệch vẫn
    được `validate_result()` gắn cờ — đó mới là chỗ của nó.

    `da_biet` chỉ chứa các chỉ tiêu ĐÃ CHỐT, không chứa ứng viên đang xét.
    """
    ung_vien = coerce_number(gia_tri)
    if ung_vien is None:
        return None

    for so_hang, tong_cong, mo_ta in identities_for(standard, quy_uoc):
        thanh_vien = list(so_hang) + [tong_cong]
        if khoa not in thanh_vien:
            continue

        co = {ten: coerce_number(da_biet.get(ten)) for ten in thanh_vien}
        co[khoa] = ung_vien

        # Cận chỉ chắc chắn khi mọi số hạng đều không âm. Có `von_chu_so_huu`
        # và phần lớn chỉ tiêu B02 được phép âm, nên bỏ qua chúng ở đây thay
        # vì suy ra một cận sai.
        if not all(_khong_am(ten) for ten in so_hang):
            continue

        biet = [co[ten] for ten in so_hang if co[ten] is not None]
        if not biet:
            continue

        if khoa == tong_cong:
            can_duoi = sum(biet)
            if ung_vien < can_duoi * (1 - nguong):
                return (
                    f"nhỏ hơn tổng các số hạng đã biết ({can_duoi:,.0f}) "
                    f"trong khi mọi số hạng đều không âm ({mo_ta})"
                )
        elif co[tong_cong] is not None:
            can_tren = co[tong_cong]
            if ung_vien > can_tren * (1 + nguong):
                return (
                    f"lớn hơn tổng cộng đã biết ({can_tren:,.0f}) "
                    f"trong khi mọi số hạng đều không âm ({mo_ta})"
                )

    return None
