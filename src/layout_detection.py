"""
Layout Detection

Runs DocLayout-YOLO on a page image to find table regions. Used to
(1) skip pages with no table at all, and (2) crop to just the table
region on pages that have one — reducing noise/size before OCR/VLM.
"""

from dataclasses import dataclass

from PIL import Image

# Tham số theo khuyến nghị của DocLayout-YOLO. Ngưỡng conf để thấp hơn
# mặc định vì bảng trong BCTC thường không kẻ khung đầy đủ, để mặc định
# hay bị sót cả bảng.
IMAGE_SIZE = 1024
CONFIDENCE = 0.2

# Nới thêm vài pixel quanh box trước khi cắt: YOLO hay bám sát mép làm
# mất chữ số ở cột ngoài cùng bên phải, đúng cột chứa giá trị cần lấy.
PADDING = 8

# Hai box chồng nhau quá mức này thì coi là cùng một bảng.
#
# 0.5 là ngưỡng quy ước của non-maximum suppression. Để cao hơn thì hai
# box lệch nhau chút vẫn lọt cả hai; để thấp hơn thì hai bảng nằm sát nhau
# trên cùng trang bị gộp làm một và mất dữ liệu.
IOU_THRESHOLD = 0.5

# confidence của vùng "cả trang" khi YOLO không tìm thấy bảng nào.
#
# Dùng đúng 0.0 làm dấu hiệu nhận biết được: mọi box THẬT đều có conf ít
# nhất bằng CONFIDENCE (0.2) vì đó là ngưỡng lọc của model, nên 0.0 không
# bao giờ trùng với một phát hiện thật.
WHOLE_PAGE_CONFIDENCE = 0.0


@dataclass
class TableRegion:
    """
    Một vùng bảng đã cắt, KÈM toạ độ của nó trên trang gốc.

    Trước đây hàm dò bố cục chỉ trả về ảnh đã cắt và vứt toạ độ đi. Với
    một pipeline trích xuất thuần thì không sao. Với nghiên cứu này thì
    đó là chỗ đứt của cả chuỗi: không có bbox thì không cắt lại được đúng
    vùng để ĐỌC LẠI, mà đọc lại nguồn chính là đóng góp cốt lõi — mọi
    paradigm sửa lỗi trước đây đều sửa trên một vector số cố định vì
    nguồn của chúng không hỏi lại được.

    bbox là toạ độ trong ảnh TRANG gốc, đã clamp và đã cộng PADDING, tức
    đúng vùng đã cắt. Cắt lại theo bbox này phải ra đúng `image`.
    """

    image: Image.Image
    bbox: tuple[int, int, int, int]
    confidence: float


def _iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    """Tỷ lệ giao trên hợp của hai hình chữ nhật (x1, y1, x2, y2)."""
    x1 = max(a[0], b[0])
    y1 = max(a[1], b[1])
    x2 = min(a[2], b[2])
    y2 = min(a[3], b[3])

    giao = max(0, x2 - x1) * max(0, y2 - y1)
    if giao == 0:
        return 0.0

    dien_tich_a = (a[2] - a[0]) * (a[3] - a[1])
    dien_tich_b = (b[2] - b[0]) * (b[3] - b[1])
    hop = dien_tich_a + dien_tich_b - giao

    return giao / hop if hop else 0.0


def filter_overlapping(
    regions: list[TableRegion], threshold: float = IOU_THRESHOLD
) -> list[TableRegion]:
    """
    Non-maximum suppression trên các box bảng: chồng lấn thì giữ box có
    confidence cao hơn.

    YOLO hiện trả về box chồng nhau nên cùng một bảng bị xử lý hai lần —
    quan sát được ở trang 31 và 35 của báo cáo VNM. Với pipeline trích
    xuất thuần thì đó chỉ là lãng phí một lượt gọi API.

    Với provenance thì đó là SAI DỮ LIỆU: một chỉ tiêu có hai nguồn mâu
    thuẫn, và bước đọc lại không có cách nào biết nên cắt lại vùng nào.
    Nói cách khác, lỗi này chuyển từ hạng "tốn tiền" sang hạng "hỏng kết
    quả" đúng lúc module này ra đời.

    Trả về theo thứ tự từ trên xuống dưới, giống hàm gọi nó vẫn mong đợi.
    """
    giu: list[TableRegion] = []

    for vung in sorted(regions, key=lambda r: -r.confidence):
        if all(_iou(vung.bbox, da_giu.bbox) <= threshold for da_giu in giu):
            giu.append(vung)

    return sorted(giu, key=lambda r: r.bbox[1])

_model = None
MODEL_ID = "juliozhao/DocLayout-YOLO-DocStructBench"
MODEL_FILENAME = "doclayout_yolo_docstructbench_imgsz1024.pt"


def get_model():
    """
    Nạp model ở lần gọi đầu tiên rồi tái sử dụng.

    Trước đây model được nạp ngay lúc import module, nên bất kỳ file nào
    import layout_detection cũng phải chờ nạp checkpoint — kể cả khi lượt
    chạy đó không hề dùng tới layout detection.
    """
    global _model
    if _model is None:
        from doclayout_yolo import YOLOv10
        from huggingface_hub import hf_hub_download

        filepath = hf_hub_download(repo_id=MODEL_ID, filename=MODEL_FILENAME)
        _model = YOLOv10(filepath)
    return _model


def cat_vung(image: Image.Image, box: tuple[int, int, int, int], confidence: float) -> TableRegion:
    """
    Nới PADDING quanh box, clamp về trong khung ảnh, rồi cắt.

    Tách thành hàm riêng vì đây là chỗ DUY NHẤT được phép quyết định
    "vùng đã cắt là vùng nào": bbox trả về phải là bbox đã dùng để cắt,
    không phải bbox thô của YOLO. Lệch giữa hai thứ đó không làm gì nổ —
    nó chỉ khiến bước đọc lại nhìn nhầm sang một ô khác rồi trả về một
    con số hoàn toàn hợp lệ.
    """
    x1, y1, x2, y2 = box
    width, height = image.size

    crop_box = (
        max(0, x1 - PADDING),
        max(0, y1 - PADDING),
        min(width, x2 + PADDING),
        min(height, y2 + PADDING),
    )

    return TableRegion(image=image.crop(crop_box), bbox=crop_box, confidence=confidence)


def get_table_regions(image: Image.Image) -> list[TableRegion]:
    """
    Trả về danh sách TableRegion, mỗi phần tử là một vùng bảng kèm toạ độ
    trên trang gốc, sắp xếp từ trên xuống dưới. Rỗng nếu không có bảng nào.

    Trả về NHIỀU vùng thay vì gộp tất cả thành một bounding box duy nhất:
    trang có hai bảng nằm ở đầu và cuối thì vùng gộp sẽ ôm trọn cả phần
    văn bản ở giữa — đúng thứ mà việc cắt bảng muốn loại bỏ.

    Box chồng lấn được lọc bằng NMS trước khi trả về — xem
    filter_overlapping() để biết vì sao việc đó chuyển từ "tối ưu" thành
    "bắt buộc" khi có provenance.
    """
    model = get_model()
    result = model.predict(image, imgsz=IMAGE_SIZE, conf=CONFIDENCE)[0]

    regions = []
    for box in result.boxes:
        if model.names[int(box.cls)] != "table":
            continue
        toa_do = tuple(int(value) for value in box.xyxy[0])
        regions.append(cat_vung(image, toa_do, float(box.conf)))

    return filter_overlapping(regions)


def ca_trang(image: Image.Image) -> TableRegion:
    """
    Vùng "cả trang", dùng khi YOLO không tìm thấy bảng nào (fail open).

    Vẫn phải là một TableRegion đầy đủ chứ không phải ảnh trần: bước đọc
    lại cần bbox kể cả trong ca này, và bbox của cả trang vẫn là một câu
    trả lời đúng.
    """
    width, height = image.size
    return TableRegion(
        image=image,
        bbox=(0, 0, width, height),
        confidence=WHOLE_PAGE_CONFIDENCE,
    )
