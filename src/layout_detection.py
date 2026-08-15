"""
Layout Detection

Runs DocLayout-YOLO on a page image to find table regions. Used to
(1) skip pages with no table at all, and (2) crop to just the table
region on pages that have one — reducing noise/size before OCR/VLM.
"""

from PIL import Image

# Tham số theo khuyến nghị của DocLayout-YOLO. Ngưỡng conf để thấp hơn
# mặc định vì bảng trong BCTC thường không kẻ khung đầy đủ, để mặc định
# hay bị sót cả bảng.
IMAGE_SIZE = 1024
CONFIDENCE = 0.2

# Nới thêm vài pixel quanh box trước khi cắt: YOLO hay bám sát mép làm
# mất chữ số ở cột ngoài cùng bên phải, đúng cột chứa giá trị cần lấy.
PADDING = 8

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


def get_table_regions(image: Image.Image) -> list[Image.Image]:
    """
    Trả về danh sách ảnh đã cắt, mỗi ảnh là một vùng bảng, sắp xếp từ
    trên xuống dưới. Trả về list rỗng nếu trang không có bảng nào.

    Trả về NHIỀU vùng thay vì gộp tất cả thành một bounding box duy nhất:
    trang có hai bảng nằm ở đầu và cuối thì vùng gộp sẽ ôm trọn cả phần
    văn bản ở giữa — đúng thứ mà việc cắt bảng muốn loại bỏ.
    """
    model = get_model()
    result = model.predict(image, imgsz=IMAGE_SIZE, conf=CONFIDENCE)[0]

    boxes = []
    for box in result.boxes:
        if model.names[int(box.cls)] != "table":
            continue
        x1, y1, x2, y2 = (int(value) for value in box.xyxy[0])
        boxes.append((x1, y1, x2, y2))

    boxes.sort(key=lambda box: box[1])   # theo y1: từ trên xuống dưới

    width, height = image.size
    regions = []

    for x1, y1, x2, y2 in boxes:
        # clamp về trong khung ảnh, tránh crop ra ngoài biên
        crop_box = (
            max(0, x1 - PADDING),
            max(0, y1 - PADDING),
            min(width, x2 + PADDING),
            min(height, y2 + PADDING),
        )
        regions.append(image.crop(crop_box))

    return regions
