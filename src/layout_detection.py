"""
Layout Detection

Runs DocLayout-YOLO on a page image to find table regions. Used to
(1) skip pages with no table at all, and (2) crop to just the table
region on pages that have one — reducing noise/size before OCR/VLM.
"""

from doclayout_yolo import YOLOv10
from PIL import Image

model = YOLOv10.from_pretrained("juliozhao/DocLayout-YOLO-DocStructBench")


def get_table_region(image: Image.Image) -> Image.Image | None:
    results = model.predict(image)
    result = results[0]

    table_boxes = []   # bước 2: list rỗng chứa toạ độ box là bảng

    for box in result.boxes:   # bước 3: lặp qua từng box phát hiện được
        class_name = model.names[int(box.cls)]
        if class_name == "table":
            x1, y1, x2, y2 = box.xyxy[0]
            table_boxes.append((int(x1), int(y1), int(x2), int(y2)))

    if not table_boxes:   # bước 4
        return None

    # bước 5: tính toạ độ bao trọn tất cả box trong table_boxes
    x1 = min(box[0] for box in table_boxes)   # x1 nhỏ nhất trong tất cả box
    y1 = min(box[1] for box in table_boxes)   # y1 nhỏ nhất
    x2 = max(box[2] for box in table_boxes)   # x2 lớn nhất
    y2 = max(box[3] for box in table_boxes)   # y2 lớn nhất

    # bước 6: crop và return
    return image.crop((x1, y1, x2, y2))