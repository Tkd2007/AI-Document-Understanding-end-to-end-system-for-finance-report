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

CẢNH BÁO — CÁC ĐẲNG THỨC Ở ĐÂY LÀ GIẢ THUYẾT, CHƯA ĐỐI CHIẾU VĂN BẢN.
Chúng được dựng lại từ hiểu biết chung về kết cấu biểu mẫu, KHÔNG phải đọc
ra từ Phụ lục IV của Thông tư. Đúng theo BUILD-SPEC mục 0.5, ma trận ràng
buộc là một trong hai chỗ người chủ trì PHẢI tự kiểm. Dùng module này để
biết NÊN TÌM GÌ trong văn bản, đừng dùng nó thay cho việc đọc văn bản.

KẾT QUẢ CHÍNH — một định luật về hình dạng đồ thị ràng buộc:

    Một chỉ tiêu định vị được KHI VÀ CHỈ KHI tập đẳng thức chứa nó khác với
    tập đẳng thức của MỌI chỉ tiêu khác.

Hệ quả trực tiếp, và nó quyết định hướng đi: hai chỉ tiêu "anh em" cùng nằm
trong ĐÚNG MỘT đẳng thức phân rã tổng–thành phần luôn có cột giống hệt nhau
trong ma trận A, nên KHÔNG BAO GIỜ phân biệt được — thêm bao nhiêu chỉ tiêu
cùng loại cũng vô ích. Chỉ LIÊN KẾT CHÉO giữa các biểu mẫu mới phá được, vì
chỉ nó mới làm một chỉ tiêu xuất hiện trong hai đẳng thức khác nhau.

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
# Cộng dồn: mỗi kịch bản là kịch bản trước cộng thêm một NHÓM đẳng thức, để
# đọc được đóng góp riêng của từng nhóm chứ không chỉ đọc được tổng.

_A_FIELDS = [
    "tai_san_ngan_han",
    "hang_ton_kho",
    "tai_san_dai_han",
    "tong_tai_san",
    "no_phai_tra",
    "von_chu_so_huu",
    "doanh_thu_thuan",
    "gia_von_hang_ban",
    "loi_nhuan_gop",
    "loi_nhuan_truoc_thue",
    "loi_nhuan_sau_thue",
]

_A_IDENT = [
    (["tai_san_ngan_han", "tai_san_dai_han"], "tong_tai_san", "TS ngắn + TS dài = Tổng TS"),
    (["no_phai_tra", "von_chu_so_huu"], "tong_tai_san", "Nợ + VCSH = Tổng TS"),
    (["gia_von_hang_ban", "loi_nhuan_gop"], "doanh_thu_thuan", "GV + LN gộp = DTT"),
]

# B — tách đẳng thức cân đối làm hai bằng cách đưa Tổng nguồn vốn vào làm
# một chỉ tiêu riêng. Hiện `no_phai_tra + von_chu_so_huu = tong_tai_san`
# đang GỘP hai sự thật khác nhau: nợ cộng vốn bằng tổng nguồn vốn, và tổng
# nguồn vốn bằng tổng tài sản. Tách ra thì có thêm một đẳng thức và thêm
# một số đọc được từ trang giấy.
_B_FIELDS = [*_A_FIELDS, "tong_nguon_von"]
_B_IDENT = [
    (["tai_san_ngan_han", "tai_san_dai_han"], "tong_tai_san", "TS ngắn + TS dài = Tổng TS"),
    (["no_phai_tra", "von_chu_so_huu"], "tong_nguon_von", "Nợ + VCSH = Tổng NV"),
    (["tong_nguon_von"], "tong_tai_san", "Tổng NV = Tổng TS"),
    (["gia_von_hang_ban", "loi_nhuan_gop"], "doanh_thu_thuan", "GV + LN gộp = DTT"),
]

# C — nối Lợi nhuận trước thuế với Lợi nhuận sau thuế. Hiện hai chỉ tiêu này
# KHÔNG nằm trong đẳng thức nào, nên cột của chúng toàn 0: sai bao nhiêu
# cũng không đẳng thức nào phát hiện được.
_C_FIELDS = [*_B_FIELDS, "chi_phi_thue_tndn", "loi_nhuan_thuan_hdkd", "loi_nhuan_khac"]
_C_IDENT = [
    *_B_IDENT,
    (["loi_nhuan_sau_thue", "chi_phi_thue_tndn"], "loi_nhuan_truoc_thue", "LNST + CP thuế = LNTT"),
    (
        ["loi_nhuan_thuan_hdkd", "loi_nhuan_khac"],
        "loi_nhuan_truoc_thue",
        "LN thuần HĐKD + LN khác = LNTT",
    ),
]

# D — phân rã Tài sản ngắn hạn thành các thành phần, nhằm bảo vệ
# `hang_ton_kho`. Đây là chỉ tiêu ĐÃ CÓ lỗi đọc thật trên báo cáo VNM (alias
# khớp trúng dòng "Dự phòng giảm giá hàng tồn kho"), và hiện không ràng buộc
# nào chạm tới nó.
_D_FIELDS = [
    *_C_FIELDS,
    "tien_va_tuong_duong_tien",
    "dau_tu_tai_chinh_ngan_han",
    "phai_thu_ngan_han",
    "tai_san_ngan_han_khac",
]
_D_IDENT = [
    *_C_IDENT,
    (
        [
            "tien_va_tuong_duong_tien",
            "dau_tu_tai_chinh_ngan_han",
            "phai_thu_ngan_han",
            "hang_ton_kho",
            "tai_san_ngan_han_khac",
        ],
        "tai_san_ngan_han",
        "5 thành phần = TS ngắn hạn",
    ),
]

# E — LIÊN KẾT CHÉO giữa các biểu mẫu. Đây là nhóm duy nhất đổi được bản
# chất bài toán, vì chỉ nó mới làm một chỉ tiêu xuất hiện trong HAI đẳng
# thức khác nhau:
#   * Tiền cuối kỳ trên B03 chính là Tiền và tương đương tiền trên B01.
#   * Lợi nhuận chưa phân phối trên B01 nối sang Lợi nhuận sau thuế trên B02.
_E_FIELDS = [
    *_D_FIELDS,
    "tien_cuoi_ky_b03",
    "tien_dau_ky_b03",
    "lctt_thuan",
    "lncpp_cuoi_ky",
    "lncpp_dau_ky",
    "von_gop_chu_so_huu",
    "quy_khac_vcsh",
]
_E_IDENT = [
    *_D_IDENT,
    (["tien_cuoi_ky_b03"], "tien_va_tuong_duong_tien", "B03 tiền cuối kỳ = B01 tiền — CHÉO"),
    (["tien_dau_ky_b03", "lctt_thuan"], "tien_cuoi_ky_b03", "Tiền đầu kỳ + LCTT thuần = cuối kỳ"),
    (
        ["lncpp_dau_ky", "loi_nhuan_sau_thue"],
        "lncpp_cuoi_ky",
        "LNCPP đầu kỳ + LNST = LNCPP cuối kỳ — CHÉO (bỏ qua cổ tức)",
    ),
    (
        ["von_gop_chu_so_huu", "lncpp_cuoi_ky", "quy_khac_vcsh"],
        "von_chu_so_huu",
        "Vốn góp + LNCPP + quỹ = VCSH",
    ),
]

KICH_BAN = [
    KichBan("A", "Hiện tại — 11 chỉ tiêu, 3 đẳng thức", _A_FIELDS, _A_IDENT,
            "Trạng thái repo đang có."),
    KichBan("B", "+ Tổng nguồn vốn", _B_FIELDS, _B_IDENT,
            "Tách đẳng thức cân đối làm hai."),
    KichBan("C", "+ chuỗi lãi lỗ trên B02", _C_FIELDS, _C_IDENT,
            "Nối LNTT với LNST; trước đó cả hai có cột toàn 0."),
    KichBan("D", "+ phân rã Tài sản ngắn hạn", _D_FIELDS, _D_IDENT,
            "Nhằm bảo vệ hang_ton_kho."),
    KichBan("E", "+ LIÊN KẾT CHÉO B01/B02/B03", _E_FIELDS, _E_IDENT,
            "Nhóm duy nhất đổi được bản chất bài toán."),
]


def bang_markdown(ket_qua: list[KetQua]) -> str:
    dong = [
        "| KB | Kịch bản | Chỉ tiêu | Đẳng thức | rank | dim null | Định vị được | Bộ tối thiểu |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for kq in ket_qua:
        kb = kq.kich_ban
        bo = "None" if kq.minimal_set is None else f"{len(kq.minimal_set)} chỉ tiêu"
        dong.append(
            f"| {kb.ma} | {kb.ten} | {kq.n_field} | {kq.n_dang_thuc} | {kq.hang} "
            f"| {kq.dim_null} | {len(kq.dinh_vi_duoc)}/{kq.n_field} "
            f"({kq.ty_le_dinh_vi:.0%}) | {bo} |"
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
        "các anh em của mình, nên cột trong ma trận A giống hệt nhau. Không\n"
        "lượng chỉ tiêu nào thêm vào phá được chuyện đó — chỉ liên kết chéo mới\n"
        "phá được, và Phụ lục IV có bao nhiêu liên kết chéo là câu hỏi phải đọc\n"
        "văn bản mới trả lời được."
    )
