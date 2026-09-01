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
    # Quy ước dấu MÀ BÁO CÁO NÀY DÙNG để in các dòng khấu trừ của B02:
    # "tong" (khoản trừ in trong ngoặc, 60 = 50+51+52), "tru" (in độ lớn,
    # 60 = 50-51-52), hay "khong_xac_dinh" khi không đọc được.
    #
    # BẮT BUỘC, và không có mặc định, vì cùng lý do với `unit_declared`: đây
    # là một tham số TRÌNH BÀY đọc được từ trang giấy mà thiếu nó thì con số
    # đã lưu không diễn giải được. `51 = 68.069.473.287` một mình không nói
    # được đó là chi phí thuế hay thu nhập thuế; phải có quy ước mới biết.
    # Đo được ngày 01/09/2026: cả hai cách in cùng tồn tại trong chuẩn TT200,
    # nên suy nó ra từ `standard` là suy sai.
    quy_uoc_dau: str
    unit_declared: str
    unit_multiplier: int
    values: dict
    source_url: str
    downloaded_at: str
    annotator: str
    annotated_at: str
    adjudicated: bool = False        # đã qua phân xử bất đồng chưa
    notes: str = ""

    # Bốn trường dưới ghi lại CÁCH tài liệu này được gán nhãn, không phải nội
    # dung của nó. Chúng có giá trị mặc định nên mọi file gold ghi trước khi
    # thêm chúng vẫn đọc lại được.
    #
    # thoi_gian_giay phục vụ một phép đo đã cam kết: ADDENDUM mục 6 chốt giao
    # thức trần người ở 15 phút một tài liệu, đo khi bộ chỉ tiêu còn nằm trên
    # hai biểu mẫu. Kịch bản E trải nó qua ba biểu mẫu, nên giao thức ấy phải
    # được đo lại chứ không giả định. Ghi thời gian ngay lúc gán nhãn là cách
    # rẻ nhất để có số liệu đó mà không phải tổ chức một buổi đo riêng.
    #
    # Hai trường còn lại là dấu vết kiểm toán cho một rủi ro thật: công cụ
    # gán nhãn cho phép kiểm đẳng thức trên chính số người vừa gõ, và người
    # có thể sửa một chữ số cho cân thay vì đọc lại. Guideline mục 8 cấm việc
    # đó, nhưng lời cấm không tự kiểm chứng được. Ghi lại số lần kiểm và việc
    # có sửa sau khi kiểm hay không làm rủi ro thành ĐO ĐƯỢC: về sau tách
    # được nhóm "cân ngay từ đầu" khỏi nhóm "cân sau khi sửa", và nếu hai
    # nhóm cho kết quả khác nhau thì biết ngay thay vì ngờ ngợ.
    #
    # Ghi đè một file gold đã có là chuyện BÌNH THƯỜNG — phát hiện đọc nhầm
    # một chữ số thì phải sửa được. Nhưng nó phải để lại dấu vết: một bản ghi
    # đã sửa ba lần và một bản ghi viết một lần rồi không đụng tới nữa là hai
    # thứ khác nhau khi phân tích chất lượng gán nhãn, và không có khoá này
    # thì chúng trông y hệt nhau.
    so_lan_ghi: int = 1
    thoi_gian_giay: int = 0
    so_lan_kiem_dang_thuc: int = 0
    sua_gia_tri_sau_khi_kiem: bool = False

    # trang_thai_dong_ho nói RÕ tài liệu này có được bấm giờ hay không, thay
    # vì để người đọc suy ra từ `thoi_gian_giay == 0`. Hai thứ đó khác nhau:
    # một tài liệu không ai bấm giờ và một tài liệu bấm giờ ra 0 giây là hai
    # sự kiện khác hẳn, mà nếu chỉ nhìn con số 0 thì chúng giống hệt nhau.
    # Phân biệt được là điều kiện cần để tính trung vị của giao thức trần
    # người: trung vị đó chỉ được lấy trên các tài liệu `da_do`, và gộp nhầm
    # một số 0 vào sẽ kéo tụt nó mà không ai thấy.
    #
    # `VNM_2026Q1_TT99` là ca đã xảy ra thật: nó có `thoi_gian_giay` bằng 0
    # và không rõ vì đồng hồ không chạy hay vì file được sửa tay. Mặc định
    # `khong_do` khiến mọi file ghi trước khi có khoá này tự khai đúng điều
    # duy nhất chắc chắn về chúng — rằng không có số đo thời gian nào.
    #
    # so_lan_tam_dung là dấu vết đi kèm: `thoi_gian_giay` nay đếm thời gian
    # LÀM VIỆC chứ không đếm thời gian đồng hồ tường, nên một tài liệu làm
    # liền mạch và một tài liệu ngắt quãng năm lần có thể ra cùng một con số.
    # Chúng không đáng tin như nhau, và chỉ khoá này mới tách được.
    trang_thai_dong_ho: str = "khong_do"   # "da_do" | "khong_do"
    so_lan_tam_dung: int = 0

    def __post_init__(self):
        thieu = [
            ten
            for ten in ("doc_id", "source_url", "downloaded_at", "annotator",
                        "annotated_at", "quy_uoc_dau")
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
        noi_dung = json.loads(Path(duong_dan).read_text(encoding="utf-8"))
        # File gold ghi trước 01/09/2026 không có khoá `quy_uoc_dau`, và
        # KHÔNG được đoán hộ chúng: quy ước là thứ chỉ đọc được trên tờ giấy,
        # còn giá trị đã lưu thì đã qua nhiều lượt lật dấu cơ học nên suy
        # ngược từ nó ra cách báo cáo trình bày là suy từ chính quy tắc đang
        # bị thay. Báo lỗi nói rõ phải làm gì thay vì để TypeError khó hiểu.
        if "quy_uoc_dau" not in noi_dung:
            raise ValueError(
                f"{Path(duong_dan).name} thiếu khoá `quy_uoc_dau` — file này "
                f"được gán nhãn trước 01/09/2026, khi quy ước dấu còn bị suy "
                f"từ chuẩn Thông tư. Phải đọc lại mã 11 và mã 51 trên chính "
                f"PDF rồi gán nhãn lại, không suy từ giá trị đang lưu."
            )
        return cls(**noi_dung)


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
