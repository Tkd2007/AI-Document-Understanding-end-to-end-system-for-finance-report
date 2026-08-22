"""
Cấu trúc bảng tài chính hai cột kỳ — thứ mà tầng XBRL render ra ảnh và
inject lỗi lên.

VÌ SAO CẦN MỘT CẤU TRÚC RIÊNG chứ không dùng thẳng dict giá trị: hai trong
năm chế độ lỗi ở taxonomy được ĐỊNH NGHĨA BẰNG HÌNH HỌC CỦA TRANG, không
phải bằng giá trị. Lệch dòng là lấy giá trị của ô ngay trên hoặc ngay dưới;
lệch cột là lấy giá trị cột kỳ so sánh. Không có thứ tự dòng và danh sách
cột thì hai chế độ lỗi đó không sinh ra được, mà chúng lại đúng là hai chế
độ lỗi đặc thù của việc đọc tài liệu — thứ không tồn tại trong dữ liệu khảo
sát và cũng là một phần lý do bài toán này khác các paradigm sửa lỗi cũ.

Cột kỳ so sánh không phải chi tiết trang trí: báo cáo tài chính luôn in hai
kỳ cạnh nhau và cả hai cùng thoả một hệ ràng buộc, nên cột thứ hai vừa là
nguồn sinh lỗi lệch cột vừa là ràng buộc gần như miễn phí — đúng câu hỏi
(d) ở mục 6.1 của proposal.
"""

from dataclasses import dataclass, field


@dataclass
class FinancialTable:
    """
    Một bảng tài chính: các dòng chỉ tiêu × các cột kỳ.

    `values` để None cho ô trống. Ô trống là chuyện có thật trên báo cáo
    (chỉ tiêu không phát sinh trong kỳ), và nó khác hẳn số 0 — gộp hai thứ
    lại là tự tạo ra một chế độ lỗi không có thật.

    `concept` là tên chỉ tiêu theo taxonomy (vd `Assets`), `labels` là nhãn
    hiển thị trên trang. Giữ tách nhau vì ràng buộc nói bằng concept còn
    người và VLM đọc bằng nhãn, và chính khoảng cách giữa hai thứ đó là chỗ
    lỗi khớp nhầm dòng sinh ra.
    """

    doc_id: str
    concepts: list[str]
    labels: dict[str, str]
    periods: list[str]
    values: dict[str, dict[str, float | None]]
    unit_label: str = "USD"
    unit_multiplier: int = 1
    meta: dict = field(default_factory=dict)

    def get(self, concept: str, period: str) -> float | None:
        return self.values.get(concept, {}).get(period)

    def cot_chinh(self) -> str:
        """
        Kỳ báo cáo, tức cột đầu tiên.

        Quy ước thứ tự cột: kỳ gần nhất đứng trước, đúng như báo cáo in ra.
        Mọi phép đo mặc định chạy trên cột này; cột sau là kỳ so sánh.
        """
        return self.periods[0]

    def values_cua_ky(self, period: str | None = None) -> dict[str, float | None]:
        """Bộ giá trị của một kỳ, ở dạng phẳng để đưa thẳng vào ma trận A."""
        ky = period or self.cot_chinh()
        return {ten: self.get(ten, ky) for ten in self.concepts}

    def thay_gia_tri(self, concept: str, period: str, gia_tri: float | None):
        """
        Trả về một bảng MỚI với đúng một ô bị đổi.

        Không sửa tại chỗ: bước inject phải giữ được cả bảng gốc lẫn bảng
        đã hỏng để so, và một hàm sửa tại chỗ sẽ âm thầm làm hỏng ground
        truth của chính thí nghiệm đang chạy.
        """
        moi = {ten: dict(cot) for ten, cot in self.values.items()}
        moi.setdefault(concept, {})[period] = gia_tri

        return FinancialTable(
            doc_id=self.doc_id,
            concepts=list(self.concepts),
            labels=dict(self.labels),
            periods=list(self.periods),
            values=moi,
            unit_label=self.unit_label,
            unit_multiplier=self.unit_multiplier,
            meta=dict(self.meta),
        )

    def hang_xom_doc(self, concept: str) -> list[str]:
        """
        Chỉ tiêu ngay trên và ngay dưới trên trang in.

        Đây là tập giá trị mà lỗi lệch dòng lấy nhầm. Dòng đầu và dòng cuối
        chỉ có một hàng xóm, và đó là thông tin thật chứ không phải ca biên
        cần vá: lỗi lệch dòng ở mép bảng thật sự ít lựa chọn hơn.
        """
        i = self.concepts.index(concept)
        ke = []
        if i > 0:
            ke.append(self.concepts[i - 1])
        if i < len(self.concepts) - 1:
            ke.append(self.concepts[i + 1])
        return ke
