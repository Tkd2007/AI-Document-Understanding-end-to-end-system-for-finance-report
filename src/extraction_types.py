"""
Kiểu dữ liệu dùng chung cho kết quả trích xuất.

Pipeline ban đầu trả `{field: value}` — đủ cho một hệ trích xuất, nhưng
thiếu ba thứ mà phần nghiên cứu bắt buộc phải có:

  * confidence từng trường  — H1 cần làm nhóm so sánh với vi phạm ràng
    buộc, H2 cần làm trọng số, và baseline 3 và 5 cần nó để tồn tại.
  * provenance từng trường  — bước đọc lại phải biết cắt lại đúng vùng ảnh
    nào. Không có nó thì không đọc lại được, và đóng góp cốt lõi của cả
    nghiên cứu biến mất.
  * các giá trị THUA phiếu — chúng là nguồn ứng viên sửa lỗi đầu tiên và
    gần như miễn phí. Vứt đi là phải gọi lại VLM để có lại.

Tách ra file riêng thay vì để trong extract_vlm.py vì cả router, api,
eval harness và về sau là các module sửa lỗi đều nói bằng ngôn ngữ này.

TÊN FILE: BUILD-SPEC đặt tên module này là `types.py`, nhưng KHÔNG dùng
được. Repo import phẳng với `pythonpath = src`, nên `src/types.py` che
khuất module `types` của thư viện chuẩn — và `enum` lại `from types
import MappingProxyType`, nên trình thông dịch chết ngay lúc khởi động
với một lỗi circular import không hề gợi ý nguyên nhân. Đã kiểm chứng
bằng cách chạy thật trước khi đổi tên.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Provenance:
    """
    Nguồn gốc của một giá trị: nó được đọc ra từ đâu trên tài liệu.

    bbox là toạ độ trong ảnh TRANG gốc, KHÔNG phải trong ảnh crop. Đây là
    chỗ dễ sai nhất và sai thì không có gì báo: bước đọc lại sẽ cắt nhầm
    vùng rồi trả về một con số hoàn toàn hợp lệ của một ô khác.
    """

    page: int
    region_index: int
    bbox: tuple[int, int, int, int]
    crop_path: str | None = None


@dataclass
class FieldResult:
    """
    Một chỉ tiêu kèm mọi thứ biết được về độ tin cậy và nguồn gốc của nó.

    votes giữ NGUYÊN VẸN mọi giá trị đã xuất hiện qua các mẫu, không chỉ
    giá trị thắng. Đó chính là nguồn ứng viên `vlm_vote` cho bước sinh ứng
    viên sửa lỗi, và nó gần như miễn phí ở đây — vứt đi thì phải gọi lại
    VLM đúng số lần ấy để có lại.
    """

    value: int | float | None
    confidence: float
    votes: dict[str, int] = field(default_factory=dict)
    provenance: Provenance | None = None

    @classmethod
    def khong_do(cls, value) -> "FieldResult":
        """
        Một giá trị KHÔNG đo được độ tin cậy, ví dụ đến từ nhánh OCR hoặc
        từ một lượt chạy k=1.

        confidence = 1.0 ở đây KHÔNG có nghĩa là chắc chắn. Nó có nghĩa là
        không đo được, và một mẫu duy nhất thì luôn tự đồng thuận với chính
        nó. Đừng đưa những giá trị này vào phép so AUROC của H1 mà không
        tách chúng ra — chúng sẽ tạo một cột confidence hằng số và làm bộ
        dự báo "confidence" trông tệ hơn thực tế một cách giả tạo.
        """
        return cls(value=value, confidence=1.0, votes={} if value is None else {str(value): 1})


@dataclass
class ExtractionResult:
    """
    Kết quả trích xuất một tài liệu, kèm đủ thông tin để tái lập.

    meta giữ những thứ nói về CÁCH ĐỌC cả bảng chứ không phải về một chỉ
    tiêu cụ thể: đơn vị tính, chuẩn mẫu biểu đã nhận diện.
    """

    data: dict[str, FieldResult]
    meta: dict = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    n_samples: int = 1
    temperature: float = 0.0
    model: str | None = None

    def values(self) -> dict:
        """
        Chỉ giá trị, cho những hàm chưa cần biết confidence —
        validate_result(), is_acceptable(), và phần ghi file kết quả.
        """
        return {ten: ket_qua.value for ten, ket_qua in self.data.items()}

    def confidences(self) -> dict[str, float]:
        """Confidence từng trường, cho eval harness."""
        return {ten: ket_qua.confidence for ten, ket_qua in self.data.items()}
