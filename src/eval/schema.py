"""
Định dạng ground truth cho tập gold.

Một file JSON cho mỗi tài liệu, đặt ở data/gold/.

source_url và downloaded_at là BẮT BUỘC chứ không phải cho đẹp: bản PDF gốc
của báo cáo niêm yết vẫn có bản quyền trình bày, nên phương án phát hành an
toàn là phát hành annotation kèm URL nguồn và script tải, KHÔNG phát hành
file gốc. Thiếu hai trường đó thì không phát hành dataset được, và dataset
là một trong bốn kết quả dự kiến của cả nghiên cứu.

annotator và annotated_at cũng bắt buộc, vì quy trình gán nhãn cam kết ba
luật mà chỉ dấu thời gian mới kiểm chứng được: người gán nhãn mù với đầu ra
pipeline, gán nhãn xong mới chạy pipeline trên tài liệu đó, và guideline
viết trước không sửa giữa chừng.
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

GOLD_DIR = Path("data/gold")


@dataclass
class GroundTruthDoc:
    """
    Ground truth của một tài liệu.

    values đã QUY ĐỔI VỀ ĐỒNG, giống mọi thứ khác đi ra từ validate_result.
    Lưu ở đơn vị gốc của báo cáo sẽ khiến hai tài liệu khác đơn vị không so
    được với nhau, và cả phép đo accuracy trên nhiều công ty mất nghĩa.

    unit_declared giữ NGUYÊN VĂN dòng khai báo trên báo cáo, tách khỏi
    unit_multiplier đã diễn giải. Giữ cả hai vì việc đọc dòng đơn vị chính
    là một đối tượng nghiên cứu hạng nhất, không phải chú thích: nó là mỏ
    neo duy nhất phá được bất biến scale.
    """

    doc_id: str                      # <mã CK>_<kỳ>_<chuẩn>, vd VNM_2026Q1_TT99
    ticker: str
    period: str
    standard: str
    unit_declared: str
    unit_multiplier: int
    values: dict
    source_url: str
    downloaded_at: str
    annotator: str
    annotated_at: str
    adjudicated: bool = False        # đã qua phân xử bất đồng chưa
    notes: str = ""

    def __post_init__(self):
        thieu = [
            ten
            for ten in ("doc_id", "source_url", "downloaded_at", "annotator", "annotated_at")
            if not getattr(self, ten)
        ]
        if thieu:
            raise ValueError(
                f"Thiếu trường bắt buộc cho việc phát hành dataset và kiểm chứng "
                f"quy trình gán nhãn: {', '.join(thieu)}"
            )

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    def save(self, thu_muc: str | Path = GOLD_DIR) -> Path:
        duong_dan = Path(thu_muc) / f"{self.doc_id}.json"
        duong_dan.parent.mkdir(parents=True, exist_ok=True)
        duong_dan.write_text(self.to_json(), encoding="utf-8")
        return duong_dan

    @classmethod
    def load(cls, duong_dan: str | Path) -> "GroundTruthDoc":
        return cls(**json.loads(Path(duong_dan).read_text(encoding="utf-8")))


@dataclass
class PredictionDoc:
    """
    Kết quả của MỘT phương pháp trên MỘT tài liệu, đủ để tính mọi chỉ số.

    Tách khỏi ExtractionResult vì eval harness phải đọc được cả kết quả đã
    lưu từ những lượt chạy trước, không chỉ kết quả vừa sinh ra trong bộ
    nhớ. Tách thu thập khỏi phân tích còn cho phép tính lại chỉ số mà không
    phải gọi API lần nữa — với ngân sách free tier thì đó là khác biệt giữa
    "phân tích lại được" và "không".
    """

    doc_id: str
    method: str
    values: dict                                  # field -> giá trị, đã quy về đồng
    confidences: dict = field(default_factory=dict)
    ranking: list = field(default_factory=list)   # field xếp theo mức nghi ngờ giảm dần
    n_model_calls: int = 0
    experiment_id: str = ""
