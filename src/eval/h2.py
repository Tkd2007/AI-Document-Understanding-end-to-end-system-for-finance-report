"""
Đo H2 — ĐỊNH VỊ lỗi, chứ không phải sửa lỗi.

H2 hỏi: khi bảng không cân, phương pháp có chỉ được đúng ô sai không. Chỉ số
là Top-1 và Top-3, và `PREREGISTRATION.md` đòi **một GED test cổ điển** làm
baseline bắt buộc — nay là `repair.ged.dinh_vi_ged`, baseline 7.

VÌ SAO MODULE NÀY TỒN TẠI RIÊNG. Bốn phương pháp đem so ở H2 trả về bốn kiểu
kết quả khác nhau, và quy chúng về một BẢNG XẾP HẠNG chung là việc có nhiều
quyết định phải nêu lý do. Nhét những quyết định ấy vào runner thì chúng biến
mất giữa vòng lặp; để riêng thì test được từng cái một.

CÁI BẪY LỚN NHẤT, và là lý do không có một quy tắc xếp hạng dùng chung:
trường `Candidate.cost` mang nghĩa NGƯỢC NHAU ở hai họ.

  * Họ rời rạc (đề xuất, baseline 9): `cost = −log(xác suất tiên nghiệm)`.
    THẤP là hợp lý hơn, nên xếp TĂNG dần.
  * Baseline 8 (L1 liên tục): `cost = |delta|`, tức độ lớn phép hiệu chỉnh.
    CAO là khả nghi hơn, nên xếp GIẢM dần.

Xếp cả hai theo cùng một chiều là làm baseline 8 xếp ngược, tức làm yếu một
đối chứng bắt buộc mà bảng kết quả vẫn ra số bình thường. Đó đúng là loại
hỏng hóc mà mục 2 của `PREREGISTRATION.md` dựng lên để chống, nên nó có test
canh riêng.

BỐN CON SỐ PHẢI BÁO CÁO CÙNG NHAU — tu chính `PREREGISTRATION.md` 25/08/2026.
Chỉ số CHÍNH là "định vị đúng / TỔNG số lượt", dù nó khắc nghiệt với chính
mình, vì hai họ chạy ở hai mức sẵn sàng trả lời khác hẳn nhau: họ rời rạc bỏ
phiếu trắng thường xuyên, còn baseline 7 và 8 gần như không bao giờ im lặng.
Con số "định vị đúng TRÊN LƯỢT CÓ RA TAY" **không bao giờ được đứng một
mình** — thiếu tỷ lệ ra tay bên cạnh thì nó bị hack bằng cách im lặng.
"""

from dataclasses import dataclass, field

from repair.diagnose import Diagnosis
from repair.ged import KetQuaGED

# Các mức k đem báo cáo. Top-1 là câu hỏi thật của người dùng cuối; Top-3 là
# con số ngành quen đọc và cũng là chỗ khoảng cách giữa các phương pháp lộ ra.
CAC_MUC_K = (1, 3)


def xep_hang_roi_rac(kq: Diagnosis) -> list[str]:
    """
    Bảng xếp hạng của một phương pháp SỬA rời rạc: đề xuất, hoặc baseline 9.

    Phương pháp loại này không xếp hạng — nó chỉ ra tay hoặc không. Bảng xếp
    hạng vì vậy chính là tập trường nó đã sửa, xếp theo `cost` TĂNG dần, tức
    ứng viên hợp lý nhất đứng trước. ABSTAIN cho bảng RỖNG, và bảng rỗng phải
    được tính là trượt ở mọi mức k chứ không phải bỏ khỏi mẫu — đó là ý nghĩa
    của chỉ số chính chia cho TỔNG số lượt.

    Bảng dài tối đa `max_changes` phần tử, nên ở Top-3 phương pháp loại này
    chịu một trần cấu trúc mà baseline 7 và 8 không chịu. Bảng kết quả phải
    nêu điều đó thay vì để người đọc tưởng khoảng cách là do độ chính xác.
    """
    if not kq.changed_fields:
        return []

    return sorted(kq.changed_fields, key=lambda ten: kq.changed_fields[ten].cost)


def xep_hang_l1(kq: Diagnosis) -> list[str]:
    """
    Bảng xếp hạng của baseline 8: xếp theo ĐỘ LỚN phép hiệu chỉnh, GIẢM dần.

    Chiều ngược với `xep_hang_roi_rac`, và đây không phải chuyện tuỳ chọn. Ở
    baseline 8, `Candidate.cost` được gán bằng `|delta|` chứ không phải
    `−log(xác suất)`, nên xếp tăng dần sẽ đưa trường bị hiệu chỉnh ÍT nhất
    lên đầu — tức xếp ngược hoàn toàn, và baseline bắt buộc bị làm yếu một
    cách im lặng.
    """
    if not kq.changed_fields:
        return []

    return sorted(kq.changed_fields, key=lambda ten: -abs(kq.changed_fields[ten].cost))


def xep_hang_ged(kq: KetQuaGED) -> list[str]:
    """
    Bảng xếp hạng của baseline 7. Nó vốn đã là bảng xếp hạng nên không phải
    quy đổi gì — đó chính là lý do nó được viết trả bảng chứ không trả
    `Diagnosis`.
    """
    return list(kq.xep_hang)


@dataclass
class LuotDinhVi:
    """Kết quả định vị của MỘT phương pháp trên MỘT lượt tiêm lỗi."""

    xep_hang: list[str]
    truong_hong: set[str]
    # Số lỗi ĐÃ TIÊM ở lượt này. Ghi tường minh vì giao thức hiện tiêm đúng
    # một lỗi mỗi lượt (Câu 8 của `HANDOFF.md` mục 0 chưa quyết), và với một
    # lỗi duy nhất thì thống kê GLR của baseline 7 có một cận dưới chứng minh
    # được: nó không bao giờ xếp trường sai xuống dưới trường có cột không tỷ
    # lệ. Một bảng H2 không ghi con số này sẽ được đọc như đo độ giỏi của
    # phương pháp, trong khi nó đang đo trần định vị của hệ ràng buộc.
    n_loi_tiem: int

    @property
    def ra_tay(self) -> bool:
        return bool(self.xep_hang)

    def trung(self, k: int) -> bool:
        return bool(self.truong_hong & set(self.xep_hang[:k]))


def khung_dem() -> dict:
    """Bộ đếm rỗng cho MỘT phương pháp ở H2."""
    return {
        "n_luot": 0,
        "ra_tay": 0,
        # Lượt mà lỗi tiêm vào KHÔNG sinh phần dư — nó nằm trong null(A) nên
        # không phương pháp dựa-trên-ràng-buộc nào định vị nổi. Tách riêng vì
        # khoảng cách nằm ở đây là kết quả của H0, không phải của H2.
        "khong_sinh_phan_du": 0,
        "trung": dict.fromkeys(CAC_MUC_K, 0),
        "n_loi_tiem": 0,
    }


def cong_mot_luot(dem: dict, luot: LuotDinhVi, sinh_phan_du: bool) -> None:
    """Cộng một lượt vào bộ đếm, tại chỗ."""
    dem["n_luot"] += 1
    dem["n_loi_tiem"] += luot.n_loi_tiem

    if not sinh_phan_du:
        dem["khong_sinh_phan_du"] += 1

    if luot.ra_tay:
        dem["ra_tay"] += 1

    for k in CAC_MUC_K:
        if luot.trung(k):
            dem["trung"][k] += 1


@dataclass
class DongBang:
    """Một dòng của bảng H2, đã tính sẵn bốn con số."""

    ten: str
    n_luot: int
    ra_tay: int
    khong_sinh_phan_du: int
    trung: dict = field(default_factory=dict)

    def chinh(self, k: int) -> float:
        """CHỈ SỐ CHÍNH: định vị đúng chia cho TỔNG số lượt."""
        return self.trung[k] / self.n_luot if self.n_luot else 0.0

    def khi_ra_tay(self, k: int) -> float:
        """Phụ: định vị đúng trên lượt CÓ ra tay. Không được đứng một mình."""
        return self.trung[k] / self.ra_tay if self.ra_tay else 0.0

    def tren_luot_co_phan_du(self, k: int) -> float:
        """Phụ: bỏ các lượt lỗi rơi vào null(A) — phần đó thuộc về H0."""
        mau = self.n_luot - self.khong_sinh_phan_du
        return self.trung[k] / mau if mau else 0.0

    def ty_le_ra_tay(self) -> float:
        return self.ra_tay / self.n_luot if self.n_luot else 0.0


def bang(dem_theo_phuong_phap: dict[str, dict]) -> list[str]:
    """
    Bảng H2 dạng markdown, bốn con số cho mỗi mức k.

    In `n` của TỪNG bảng chứ không chỉ một con số tổng: cảnh báo ở
    `eval.metrics.localization_top_k` nói N thật của H2 là số lượt có lỗi,
    không phải tổng số trường, và mọi bảng localization phải ghi N của chính
    nó.
    """
    cac_dong = [
        DongBang(ten, d["n_luot"], d["ra_tay"], d["khong_sinh_phan_du"], d["trung"])
        for ten, d in dem_theo_phuong_phap.items()
    ]
    if not cac_dong:
        return ["*(không có lượt nào)*"]

    n_luot = cac_dong[0].n_luot
    tong_loi = sum(d["n_loi_tiem"] for d in dem_theo_phuong_phap.values())
    trung_binh_loi = tong_loi / (n_luot * len(cac_dong)) if n_luot and cac_dong else 0.0

    ra = [
        "## H2 — định vị lỗi",
        "",
        f"N = **{n_luot}** lượt tiêm lỗi, trung bình **{trung_binh_loi:.2f}** lỗi mỗi lượt.",
        "",
        "> Giao thức hiện tiêm **một** lỗi mỗi lượt. Với một lỗi duy nhất, thống kê",
        "> GLR của baseline 7 có cận dưới chứng minh được — nó không bao giờ xếp",
        "> trường sai xuống dưới một trường có cột không tỷ lệ — nên bảng này đo",
        "> **trần định vị của hệ ràng buộc** nhiều hơn là đo độ giỏi của từng",
        "> phương pháp. Xem Câu 8, `HANDOFF.md` mục 0.",
        "",
    ]

    for k in CAC_MUC_K:
        ra += [
            f"### Top-{k}",
            "",
            "| Phương pháp | CHÍNH: đúng/tổng | Tỷ lệ ra tay | Đúng/lượt ra tay "
            "| Đúng/lượt có phần dư |",
            "|---|---:|---:|---:|---:|",
        ]
        for dong in cac_dong:
            ra.append(
                f"| {dong.ten} | **{dong.chinh(k):.3f}** | {dong.ty_le_ra_tay():.3f} "
                f"| {dong.khi_ra_tay(k):.3f} | {dong.tren_luot_co_phan_du(k):.3f} |"
            )
        ra.append("")

    return ra
