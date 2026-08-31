"""
Kịch bản mở rộng bộ ràng buộc — trả lời câu hỏi thật của MỐC 1.

MỐC 1 hỏi "chốt bộ trường nào", nhưng kết quả của `constraints.py` cho thấy
câu hỏi đó đặt sai chỗ: với ba đẳng thức hiện có, `minimal_localizing_set()`
trả `None`, tức KHÔNG tập con nào của 11 chỉ tiêu làm mọi lỗi một-trường
định vị được. Nút thắt là ĐẲNG THỨC, không phải chỉ tiêu.

Module này đo xem mỗi nhóm đẳng thức ứng viên mua được bao nhiêu, để câu hỏi
"thêm chỉ tiêu nào" có căn cứ định lượng thay vì cảm tính — và vì mỗi chỉ
tiêu thêm vào là chi phí gán nhãn tay nhân với 60 tài liệu, khoản đắt nhất
của cả dự án.

MỌI ĐẲNG THỨC Ở ĐÂY ĐÃ ĐỐI CHIẾU NGUYÊN VĂN với Công báo — số 287+288 và
289+290 cho TT200, số 1579+1580 và 1581+1582 cho TT99. Mỗi mục ghi kèm mã số
đúng như văn bản viết, để đối chiếu lại được. Bản đầu của module này dùng
đẳng thức GIẢ THUYẾT và cho kết luận sai; xem mục "Bài học" cuối docstring.

KẾT QUẢ CHÍNH — một định luật về hình dạng đồ thị ràng buộc:

    Một chỉ tiêu định vị được KHI VÀ CHỈ KHI tập đẳng thức chứa nó khác với
    tập đẳng thức của MỌI chỉ tiêu khác.

Hệ quả thứ nhất: hai chỉ tiêu "anh em" cùng nằm trong ĐÚNG MỘT đẳng thức
phân rã có cột giống hệt nhau trong ma trận A, nên không bao giờ phân biệt
được. Chỉ tiêu TỔNG của đẳng thức đó cũng vậy — cột của nó là [−1], tỷ lệ
với cột [1] của thành phần.

Hệ quả thứ hai: phân rã một chỉ tiêu làm CHÍNH chỉ tiêu đó định vị được, vì
nó xuất hiện trong hai đẳng thức (của cha nó, và của chính nó) nên cột thành
[1, −1]. Nhưng nó sinh ra các thành phần MỚI, và những thành phần đó lại là
lá không định vị được. Phân rã vì vậy là một cái cối xay: mỗi vòng đổi một
chỉ tiêu định vị được lấy n chỉ tiêu mới không định vị được, mà mỗi chỉ tiêu
mới đều tốn chi phí gán nhãn tay nhân với 60 tài liệu.

TỶ LỆ TRAO ĐỔI THẬT, đo trên đẳng thức đã đối chiếu:

    A→B  + Tổng cộng nguồn vốn (mã 440)   +1 chỉ tiêu  → +1   tỷ lệ 1,00
    B→C  + chuỗi lãi lỗ B02               +4           → +1   tỷ lệ 0,25
    C→D  + phân rã Tài sản ngắn hạn       +4           → +2   tỷ lệ 0,50
    D→E  + B03 và liên kết chéo           +6           → +2   tỷ lệ 0,33

Bước RẺ NHẤT là A→B: thêm ĐÚNG MỘT chỉ tiêu, Tổng cộng nguồn vốn, và mua
được một chỉ tiêu định vị được. Nó rẻ vì văn bản khai báo tường minh HAI
đẳng thức mà repo đang gộp thành một — `Mã số 440 = Mã số 300 + Mã số 400`
và riêng `Tổng cộng Tài sản = Tổng cộng Nguồn vốn` — nên chỉ tiêu thêm vào
lập tức nằm trong hai đẳng thức. Nó còn là một con số in đậm ở cuối bảng cân
đối, tức rẻ cả về chi phí gán nhãn.

BÀI HỌC, ghi lại vì nó đã xảy ra hai lần trong cùng một phiên làm việc.
Bản đầu của module này dùng đẳng thức dựng lại từ hiểu biết chung về kết cấu
biểu mẫu, và kết luận rằng liên kết chéo hiệu quả GẤP ĐÔI phân rã. Đối chiếu
văn bản bác bỏ điều đó: liên kết chéo thật cho tỷ lệ 0,33, thấp hơn phân rã.
Sai lệch đến từ hai đẳng thức được giả định mà văn bản KHÔNG có — một liên
kết giữa Lợi nhuận chưa phân phối trên B01 với Lợi nhuận sau thuế trên B02,
và một phân rã Vốn chủ sở hữu. Kết luận rút ra: đừng để đẳng thức giả thuyết
chạy vào bảng kết quả, kể cả khi chúng "hợp lý về mặt kế toán".

Chạy:  PYTHONIOENCODING=utf-8 python src/constraints_scenarios.py
"""

from dataclasses import dataclass, field

from constraints import (
    build_matrix,
    minimal_localizing_set,
    null_space,
    rank,
    single_field_localizable,
)


@dataclass(frozen=True)
class KichBan:
    """Một bộ (chỉ tiêu, đẳng thức) để đo."""

    ma: str
    ten: str
    fields: list[str]
    identities: list
    ghi_chu: str = ""


@dataclass(frozen=True)
class KetQua:
    kich_ban: KichBan
    n_field: int
    n_dang_thuc: int
    hang: int
    dim_null: int
    dinh_vi_duoc: list[str] = field(default_factory=list)
    khong_dinh_vi_duoc: list[str] = field(default_factory=list)
    minimal_set: list[str] | None = None

    @property
    def ty_le_dinh_vi(self) -> float:
        return len(self.dinh_vi_duoc) / self.n_field if self.n_field else 0.0


def do(kb: KichBan) -> KetQua:
    A, order = build_matrix(kb.fields, kb.identities)
    dv = single_field_localizable(A, order)
    tap, _ = minimal_localizing_set(kb.fields, kb.identities)

    return KetQua(
        kich_ban=kb,
        n_field=len(kb.fields),
        n_dang_thuc=A.shape[0],
        hang=rank(A),
        dim_null=null_space(A).shape[1],
        dinh_vi_duoc=[k for k, v in dv.items() if v],
        khong_dinh_vi_duoc=[k for k, v in dv.items() if not v],
        minimal_set=tap,
    )


# --- Các kịch bản ----------------------------------------------------------
#
# MỌI ĐẲNG THỨC DƯỚI ĐÂY ĐÃ ĐỐI CHIẾU NGUYÊN VĂN, không còn là giả thuyết.
# Nguồn: Công báo số 287+288 và 289+290 (TT200), số 1579+1580 và 1581+1582
# (TT99), trích bằng `pdftotext -layout` và `antiword`. Mỗi mục ghi kèm mã số
# đúng như văn bản viết, để đối chiếu lại được.
#
# Hai chuẩn có cấu trúc GIỐNG NHAU ở mọi đẳng thức dùng ở đây; chỉ khác mã số
# của Tổng cộng tài sản (270 ở TT200, 280 ở TT99). Các kịch bản dưới dùng tên
# chỉ tiêu chứ không dùng mã số nên áp được cho cả hai.
#
# Cộng dồn: mỗi kịch bản là kịch bản trước cộng thêm một NHÓM đẳng thức, để
# đọc được đóng góp riêng của từng nhóm chứ không chỉ đọc được tổng.

_A_FIELDS = [
    "tai_san_ngan_han",       # mã 100
    "hang_ton_kho",           # mã 140
    "tai_san_dai_han",        # mã 200
    "tong_tai_san",           # mã 270 (TT200) / 280 (TT99)
    "no_phai_tra",            # mã 300
    "von_chu_so_huu",         # mã 400
    "doanh_thu_thuan",        # B02 mã 10
    "gia_von_hang_ban",       # B02 mã 11
    "loi_nhuan_gop",          # B02 mã 20
    "loi_nhuan_truoc_thue",   # B02 mã 50
    "loi_nhuan_sau_thue",     # B02 mã 60
]

# Ba đẳng thức repo đang dùng. Đối chiếu cho thấy cả ba ĐÚNG, nhưng cái thứ
# hai là một đẳng thức SUY RA chứ không phải đẳng thức được khai báo: văn bản
# viết `440 = 300 + 400` rồi viết riêng `Tổng cộng tài sản = Tổng cộng nguồn
# vốn`. Gộp hai thành một vẫn đúng về toán, nhưng đánh mất một quan sát đọc
# được từ trang giấy — xem kịch bản B.
_A_IDENT = [
    (["tai_san_ngan_han", "tai_san_dai_han"], "tong_tai_san",
     "Mã số 270 = Mã số 100 + Mã số 200 (TT200) / Mã số 280 = ... (TT99)"),
    (["no_phai_tra", "von_chu_so_huu"], "tong_tai_san",
     "SUY RA từ (440 = 300 + 400) và (Tổng TS = Tổng NV)"),
    (["gia_von_hang_ban", "loi_nhuan_gop"], "doanh_thu_thuan",
     "B02: Mã số 20 = Mã số 10 - Mã số 11"),
]

# B — Tổng cộng nguồn vốn (mã 440) thành một chỉ tiêu riêng.
#
# Văn bản khai báo tường minh HAI đẳng thức chứ không phải một:
#     k) Tổng cộng nguồn vốn (Mã số 440) ... Mã số 440 = Mã số 300 + Mã số 400.
#     Chỉ tiêu "Tổng cộng Tài sản Mã số 270" = Chỉ tiêu "Tổng cộng Nguồn vốn
#     Mã số 440"
# Giống hệt ở TT99, chỉ đổi 270 thành 280.
_B_FIELDS = [*_A_FIELDS, "tong_nguon_von"]
_B_IDENT = [
    (["tai_san_ngan_han", "tai_san_dai_han"], "tong_tai_san", "Mã số 270/280 = 100 + 200"),
    (["no_phai_tra", "von_chu_so_huu"], "tong_nguon_von", "Mã số 440 = Mã số 300 + Mã số 400"),
    (["tong_nguon_von"], "tong_tai_san", "Tổng cộng Tài sản = Tổng cộng Nguồn vốn"),
    (["gia_von_hang_ban", "loi_nhuan_gop"], "doanh_thu_thuan", "B02: Mã số 20 = 10 - 11"),
]

# C — chuỗi lãi lỗ trên B02. Hiện `loi_nhuan_truoc_thue` và
# `loi_nhuan_sau_thue` KHÔNG nằm trong đẳng thức nào, nên cột của chúng toàn
# 0: sai bao nhiêu cũng không ràng buộc nào thấy.
#
#     Mã số 50 = Mã số 30 + Mã số 40
#     Mã số 60 = Mã số 50 + Mã số 51 + Mã số 52  (51/52 lưu CÓ DẤU, xem
#     `fields_config` — Thông tư viết `50 - (51 + 52)` với 51/52 là độ lớn)
_C_FIELDS = [
    *_B_FIELDS,
    "ln_thuan_hdkd",          # B02 mã 30
    "ln_khac",                # B02 mã 40
    "thue_tndn_hien_hanh",    # B02 mã 51
    "thue_tndn_hoan_lai",     # B02 mã 52
]
_C_IDENT = [
    *_B_IDENT,
    (["ln_thuan_hdkd", "ln_khac"], "loi_nhuan_truoc_thue", "B02: Mã số 50 = 30 + 40"),
    (["loi_nhuan_truoc_thue", "thue_tndn_hien_hanh", "thue_tndn_hoan_lai"],
     "loi_nhuan_sau_thue", "B02: Mã số 60 = 50 + 51 + 52 (51/52 có dấu)"),
]

# D — phân rã Tài sản ngắn hạn, nhằm đưa `hang_ton_kho` vào một đẳng thức.
#
#     Mã số 100 = Mã số 110 + Mã số 120 + Mã số 130 + Mã số 140 + Mã số 150
#
# TT99 có thêm mã 160 trong danh sách này; bỏ qua ở đây vì kịch bản dùng
# chung cho cả hai chuẩn và việc thêm một hạng tử không đổi kết luận.
_D_FIELDS = [
    *_C_FIELDS,
    "tien_va_tuong_duong_tien",   # mã 110
    "dau_tu_tc_ngan_han",         # mã 120
    "phai_thu_ngan_han",          # mã 130
    "tsnh_khac",                  # mã 150
]
_D_IDENT = [
    *_C_IDENT,
    (["tien_va_tuong_duong_tien", "dau_tu_tc_ngan_han", "phai_thu_ngan_han",
      "hang_ton_kho", "tsnh_khac"],
     "tai_san_ngan_han", "Mã số 100 = 110 + 120 + 130 + 140 + 150"),
]

# E — báo cáo lưu chuyển tiền tệ, và LIÊN KẾT CHÉO sang bảng cân đối.
#
# Đây là nhóm đáng giá nhất, và nó được văn bản khai báo tường minh:
#     Mã số 50 = Mã số 20 + Mã số 30 + Mã số 40
#     Mã số 70 = Mã số 50 + Mã số 60 + Mã số 61
#     "Chỉ tiêu này ... bằng chỉ tiêu Mã số 110 trên Bảng cân đối kế toán
#      kỳ đó"                                              <- mã 70 ≡ B01.110
#     Tiền đầu kỳ (Mã số 60) lấy từ "Mã số 110, cột Số đầu kỳ"
#                                                <- mã 60 ≡ B01.110 kỳ trước
#
# Vì mã 70 ĐỒNG NHẤT với B01 mã 110 nên không cần thêm một chỉ tiêu riêng cho
# nó — dùng thẳng `tien_va_tuong_duong_tien`. Đó chính là cơ chế làm liên kết
# chéo rẻ hơn phân rã: nó gắn đẳng thức thứ hai vào một chỉ tiêu ĐÃ CÓ.
_E_FIELDS = [
    *_D_FIELDS,
    "tien_dau_ky",        # B03 mã 60 ≡ B01 mã 110 của kỳ TRƯỚC
    "lctt_hdkd",          # B03 mã 20
    "lctt_dau_tu",        # B03 mã 30
    "lctt_tai_chinh",     # B03 mã 40
    "lctt_thuan",         # B03 mã 50
    "anh_huong_ty_gia",   # B03 mã 61
]
_E_IDENT = [
    *_D_IDENT,
    (["lctt_hdkd", "lctt_dau_tu", "lctt_tai_chinh"], "lctt_thuan",
     "B03: Mã số 50 = 20 + 30 + 40"),
    (["lctt_thuan", "tien_dau_ky", "anh_huong_ty_gia"], "tien_va_tuong_duong_tien",
     "B03: Mã số 70 = 50 + 60 + 61, và mã 70 ≡ B01 mã 110 — LIÊN KẾT CHÉO"),
]

KICH_BAN = [
    KichBan("A", "Hiện tại — 11 chỉ tiêu", _A_FIELDS, _A_IDENT,
            "Trạng thái repo đang có."),
    KichBan("B", "+ Tổng cộng nguồn vốn (440)", _B_FIELDS, _B_IDENT,
            "Tách đẳng thức cân đối làm hai, đúng như văn bản khai báo."),
    KichBan("C", "+ chuỗi lãi lỗ B02", _C_FIELDS, _C_IDENT,
            "Trước đó LNTT và LNST có cột toàn 0."),
    KichBan("D", "+ phân rã Tài sản ngắn hạn", _D_FIELDS, _D_IDENT,
            "Nhằm đưa hang_ton_kho vào một đẳng thức."),
    KichBan("E", "+ B03 và liên kết chéo", _E_FIELDS, _E_IDENT,
            "Nhóm duy nhất gắn đẳng thức thứ hai vào chỉ tiêu đã có."),
]


def bang_markdown(ket_qua: list[KetQua]) -> str:
    """
    Bảng kết quả, kèm cột TỶ LỆ TRAO ĐỔI của từng bước.

    Cột cuối là thứ quyết định: nó trả lời "thêm một chỉ tiêu thì mua được
    bao nhiêu chỉ tiêu định vị được". Chỉ nhìn cột "định vị được" thì kịch
    bản nào thêm nhiều chỉ tiêu cũng trông tốt hơn, trong khi mỗi chỉ tiêu
    thêm vào là chi phí gán nhãn tay nhân với 60 tài liệu.
    """
    dong = [
        "| KB | Kịch bản | Chỉ tiêu | Đẳng thức | rank | dim null | Định vị được "
        "| Bước này mua được |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for i, kq in enumerate(ket_qua):
        kb = kq.kich_ban

        if i == 0:
            buoc = "—"
        else:
            truoc = ket_qua[i - 1]
            them = kq.n_field - truoc.n_field
            duoc = len(kq.dinh_vi_duoc) - len(truoc.dinh_vi_duoc)
            ty_le = f"{duoc / them:.2f}" if them else "—"
            buoc = f"+{them} chỉ tiêu → +{duoc} (tỷ lệ {ty_le})"

        dong.append(
            f"| {kb.ma} | {kb.ten} | {kq.n_field} | {kq.n_dang_thuc} | {kq.hang} "
            f"| {kq.dim_null} | {len(kq.dinh_vi_duoc)}/{kq.n_field} "
            f"({kq.ty_le_dinh_vi:.0%}) | {buoc} |"
        )
    return "\n".join(dong)


if __name__ == "__main__":
    import sys

    # Console Windows mặc định cp1252, in tiếng Việt sẽ nổ UnicodeEncodeError.
    sys.stdout.reconfigure(encoding="utf-8")

    ket_qua = [do(kb) for kb in KICH_BAN]
    print(bang_markdown(ket_qua))
    print()

    cuoi = ket_qua[-1]
    print("Chỉ tiêu VẪN không định vị được kể cả ở kịch bản E:")
    for ten in cuoi.khong_dinh_vi_duoc:
        print(f"  - {ten}")
    print()
    print(
        "Chúng đều là chỉ tiêu LÁ: xuất hiện trong đúng MỘT đẳng thức, cùng với\n"
        "các anh em của mình, nên cột trong ma trận A giống hệt nhau.\n\n"
        "Phân rã tiếp một chỉ tiêu lá sẽ làm CHÍNH nó định vị được, nhưng lại\n"
        "sinh ra một tầng lá mới bên dưới — cái cối xay không bao giờ hết lá.\n"
        "Thứ thoát ra được là đẳng thức THỨ HAI gắn vào một chỉ tiêu ĐÃ CÓ SẴN,\n"
        "và Phụ lục IV có bao nhiêu quan hệ như vậy là câu hỏi phải đọc văn bản\n"
        "mới trả lời được."
    )
