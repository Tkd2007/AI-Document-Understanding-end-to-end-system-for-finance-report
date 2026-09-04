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

# Nới RIÊNG mép TRÊN thêm nữa, tính theo TỶ LỆ chiều cao trang.
#
# Vì sao cần: dòng "Đơn vị tính: VND" nằm ngay trên bảng và NGOÀI box bảng.
# Đo trên BMP trang 4 (cao 3504 px): DocLayout-YOLO nhận ra dòng ấy rất chắc
# chắn — box lớp `plain text` conf 0,86 ở y 416..471 — nhưng vùng bảng bắt
# đầu ở y 516 nên nó rơi ra ngoài, cách 45 px. Trên VNM trang 8 hụt 27 px.
# VLM không đọc sai dòng ấy, nó chưa từng được đưa cho xem.
#
# Vì sao chỗ hụt này nặng hơn mọi con số accuracy: với lỗi sai đơn vị toàn
# cục thì `Aδ = (c−1)Ax* = 0`, tức MỌI đẳng thức kế toán đều mù với nó. Bảng
# vẫn cân hoàn hảo trong khi mọi con số sai 1000 lần. Dòng đơn vị là mỏ neo
# tuyệt đối duy nhất, và mất nó là mất chế độ lỗi duy nhất mà cả tầng ràng
# buộc không nhìn thấy được.
#
# Vì sao TỶ LỆ chứ không phải số pixel cố định: tập gold trải từ 89,9 tới
# 295,8 dpi, nên cùng một khoảng cách vật lý trên trang cho ra số pixel khác
# nhau gấp hơn ba lần. Một hằng số pixel vừa cho bản 300 dpi sẽ hụt trên bản
# 100 dpi, và ngược lại thì nuốt cả tiêu đề công ty.
#
# NÂNG TỪ 0,05 LÊN 0,13 ngày 28/08/2026, và ĐỔI LUÔN Ý ĐỒ. Mức 0,05 cũ cố ý
# dừng TRƯỚC khối tiêu đề: nó chỉ nhắm dòng "Đơn vị tính" (2,9% trên BMP) và
# tránh chạm khối tiêu đề công ty (8,8%). Nay khối tiêu đề là thứ MUỐN lấy,
# vì hai thứ nằm trong đó trả lời hai câu hỏi đang mở:
#
#   * KÝ HIỆU MẪU (`B01a-DN` so với `B01a-DN/HN`) nói bảng thuộc bộ báo cáo
#     RIÊNG hay HỢP NHẤT. Hồ sơ có cả hai bộ mà không phân biệt được thì
#     pipeline lấy bảng cân đối từ bộ này và kết quả kinh doanh từ bộ kia.
#   * TIÊU ĐỀ báo cáo là dấu hiệu nhận diện CHUẨN mà `detect_standard()` cần,
#     và phép đo `tieu_de_trong_vung_cat` từng ghi nhận nó lọt vào vùng cắt
#     0/2 lần.
#
# 0,13 lấy từ số đo trên hai trang dựng đứng: ôm trọn mọi box phía trên cần
# 0,100 ở `SBT` trang 5 và 0,124 ở `BMP` trang 4. Đây là hằng số hiệu chỉnh
# trên HAI tài liệu — đo lại khi tập gold rộng ra.
#
# Trần vẫn phải có, và vẫn theo TỶ LỆ chứ không theo pixel: tập gold trải từ
# 89,9 tới 295,8 dpi nên cùng một khoảng cách vật lý cho ra số pixel khác nhau
# gấp hơn ba lần.
TY_LE_NOI_TREN = 0.13

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

    # Góc mà `image` đã bị xoay đi so với vùng cắt ra từ trang, tính bằng độ
    # ngược chiều kim đồng hồ. 0 nghĩa là chưa xoay, và bất biến ở docstring
    # trên giữ nguyên. Khác 0 thì bất biến ấy đọc là: cắt trang theo `bbox`
    # RỒI xoay `goc_xoay` độ mới ra `image`.
    #
    # `ocr_baseline.ocr_page_regions()` đặt trường này khi phải xoay mới đọc
    # được. Ghi lại thay vì xoay lặng lẽ vì hai lý do: toạ độ ô OCR sau đó
    # nằm trong hệ ĐÃ XOAY chứ không còn cùng hệ với `bbox`, và người đọc log
    # phải biết vùng nào đã bị can thiệp.
    goc_xoay: int = 0


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


def cat_vung(
    image: Image.Image,
    box: tuple[int, int, int, int],
    confidence: float,
    tran_tren: int | None = None,
) -> TableRegion:
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

    # tran_tren=None giữ nguyên hành vi cũ. Đây là mặc định có chủ đích chứ
    # không phải quên: hàm này còn được gọi ở chỗ không có danh sách box
    # khác để mà tính mép trên, và ở đó nới bừa là nới mù.
    mep_tren = y1 - PADDING if tran_tren is None else min(tran_tren, y1 - PADDING)

    crop_box = (
        max(0, x1 - PADDING),
        max(0, mep_tren),
        min(width, x2 + PADDING),
        min(height, y2 + PADDING),
    )

    return TableRegion(image=image.crop(crop_box), bbox=crop_box, confidence=confidence)


def tran_noi_tren(
    box: tuple[int, int, int, int],
    cac_box_khac: list[tuple[int, int, int, int]],
    height: int,
) -> int:
    """
    Mép trên xa nhất được phép cắt tới cho một vùng bảng.

    Đi NGƯỢC LÊN theo CHUỖI box nằm phía trên, mỗi lần lấy trọn box gần nhất,
    dừng khi hết box hoặc khi box kế tiếp vượt quá TY_LE_NOI_TREN nhân chiều
    cao trang. Không có box nào ở trên thì nới trọn khoảng dự phòng đó.

    VÌ SAO PHẢI ĐI THEO CHUỖI chứ không lấy đúng một box. Bản trước chỉ lấy
    box gần nhất, và trên thực tế nó luôn dừng ở dòng "Đơn vị tính" — box gần
    bảng nhất. Nhưng phía trên dòng ấy còn hai thứ cần đọc: KÝ HIỆU MẪU
    (`B01a-DN/HN`) nói bảng này thuộc bộ báo cáo riêng hay hợp nhất, và TIÊU
    ĐỀ báo cáo nói đây là chuẩn nào. Đo trên `SBT_2025Q2` trang 5: dòng đơn vị
    ở tỷ lệ 0,028 nên lọt, còn ký hiệu mẫu ở 0,100 nên bị bỏ lại. Cả hai đều
    nằm trong cùng một chuỗi box xếp chồng lên nhau, nên đi theo chuỗi thì lấy
    được cả, mà không phải nới mù một khoảng cố định.

    Lấy TRỌN box chứ KHÔNG dừng ở mép dưới của nó: thứ cần lấy nằm BÊN TRONG
    box ấy, nên dừng ở mép dưới thì vẫn hụt đúng dòng cần lấy, chỉ hụt ít hơn.

    GIỚI HẠN ĐÃ BIẾT, đo được: cách này chỉ cứu được trang DỰNG ĐỨNG. Trang
    xoay 90 độ thì ký hiệu mẫu nằm ở CẠNH BÊN chứ không nằm phía trên, và
    `SBT` trang 8 với `DGC` trang 7 — cả hai đều là bảng kết quả kinh doanh
    xoay ngang — không có box nào phía trên chồng ngang với bảng. Nới lên bao
    nhiêu cũng không tới. Ca đó cần một cơ chế khác.

    Chỉ xét box có phần chồng theo chiều NGANG với bảng. Bỏ điều kiện đó thì
    một box số trang hay ghi chú ở lề cũng kéo được vùng cắt lên tận đầu
    trang, và vùng cắt rộng ra vì một thứ không liên quan gì tới bảng.
    """
    x1, y1, x2, _ = box
    gioi_han = max(0, y1 - int(height * TY_LE_NOI_TREN))

    chong_ngang = [
        khac for khac in cac_box_khac if min(x2, khac[2]) > max(x1, khac[0])
    ]

    moc = y1
    dinh = None
    while True:
        ke_tiep = [khac for khac in chong_ngang if khac[3] <= moc and khac[1] < moc]
        if not ke_tiep:
            break

        gan_nhat = max(ke_tiep, key=lambda khac: khac[3])
        # Lấy TRỌN box hoặc không lấy nó. Cắt ngang một box là cắt ngang đúng
        # dòng chữ cần đọc, tức vẫn hụt, chỉ hụt ít hơn — mà lại còn đưa cho
        # model một dòng cụt trông như dòng đầy đủ.
        if gan_nhat[1] < gioi_han:
            break

        dinh = moc = gan_nhat[1]

    # Không chạm được box nào thì nới trọn khoảng dự phòng; chạm được thì dừng
    # ở đỉnh box cuối cùng của chuỗi, tức nới ĐÚNG tới chỗ có thứ để đọc.
    return gioi_han if dinh is None else max(gioi_han, dinh)


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

    # Giữ lại box KHÔNG phải bảng thay vì bỏ ngay tại vòng lặp. Bản trước
    # `continue` thẳng, nên box `plain text` chứa dòng "Đơn vị tính" bị vứt
    # đúng tại đó dù model nhận ra nó với conf 0,86 — và không chỗ nào phía
    # sau biết là nó từng tồn tại.
    tat_ca = [
        (tuple(int(gia_tri) for gia_tri in box.xyxy[0]), model.names[int(box.cls)], float(box.conf))
        for box in result.boxes
    ]
    khong_phai_bang = [toa_do for toa_do, ten_lop, _ in tat_ca if ten_lop != "table"]
    _, height = image.size

    regions = [
        cat_vung(image, toa_do, conf, tran_noi_tren(toa_do, khong_phai_bang, height))
        for toa_do, ten_lop, conf in tat_ca
        if ten_lop == "table"
    ]

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
