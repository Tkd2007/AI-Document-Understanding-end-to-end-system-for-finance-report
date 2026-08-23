"""
Render bảng tài chính thành ảnh, kèm bbox từng ô.

VẼ THẲNG BẰNG PILLOW, KHÔNG DỰNG HTML RỒI CHỤP — đây là chỗ đi khác
BUILD-SPEC, có chủ đích, và lý do gồm hai phần:

1. HTML sang ảnh cần một trình duyệt không đầu hoặc wkhtmltoimage nằm sẵn
   trong image. Đó đúng là cái giá mà dự án đã từ chối trả cho bộ giải MILP
   ở C2, nên trả nó ở đây thì mâu thuẫn. Pillow vốn đã ghim trong
   requirements.txt.
2. Vẽ thẳng cho bbox CHÍNH XÁC TỪNG Ô miễn phí. Tầng này cần bbox làm
   provenance ground truth — không có nó thì không đo được bước đọc lại có
   nhìn đúng vùng hay không, mà đọc lại chính là đóng góp cốt lõi. Đi đường
   HTML thì bbox phải suy ngược từ ảnh đã render, tức thêm một nguồn sai số
   vào chính thứ dùng làm chuẩn.

SynFinTabs (ICDAR 2025 Workshops) vẫn nên trích dẫn và vẫn dùng lại được
phần sinh ảnh của họ nếu cần bản trình bày đa dạng hơn. KHÁC BIỆT PHẢI GIỮ
khi nhắc tới họ: nội dung SynFinTabs là số NGẪU NHIÊN nên không đẳng thức
kế toán nào đúng trên đó. Toàn bộ giá trị của tầng này nằm ở chỗ giữ được
identity thật từ calculation linkbase.

GIỚI HẠN, phải nêu trong paper: ảnh sinh ra ở đây sạch và đều, không có
nhiễu scan, không lệch trang, không mất dấu. Nó đo được khả năng định vị và
sửa lỗi, KHÔNG đo được độ bền với chất lượng ảnh — phần đó thuộc tập Stress
của tầng gold Việt Nam. Hai tầng bù đúng điểm yếu của nhau, và đó là lập
luận nên viết thẳng vào bài.

CHỮ TRÊN ẢNH MẶC ĐỊNH LÀ TIẾNG ANH, và đó không phải cẩu thả: dữ liệu của
tầng này là hồ sơ SEC nên nhãn chỉ tiêu vốn là tiếng Anh, mà font đi kèm
Pillow lại không có glyph tiếng Việt có dấu. Muốn render nhãn tiếng Việt —
việc mà ablation "Transfer XBRL → BCTC Việt Nam" cần — thì truyền
`font_path` trỏ tới một font có dấu và truyền luôn phần chữ cố định.
Render bằng font thiếu glyph sẽ NÉM LỖI chứ không im lặng vẽ ô vuông: một
ảnh trông vẫn ra bảng nhưng chữ hỏng là thứ chỉ lộ ra sau khi đã chạy xong
cả lượt thí nghiệm.
"""

from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFont

from eval.xbrl_tier.table import FinancialTable

# Kích thước và khoảng cách, đơn vị pixel.
#
# Chọn theo chiều rộng ảnh mà VLM nhận vào: quá nhỏ thì chữ số dính nhau và
# ta đo lỗi của khâu render chứ không phải lỗi của model.
CO_CHU = 20
CAO_DONG = 34
LE = 24
RONG_COT_NHAN = 420
RONG_COT_SO = 220

# Phần chữ cố định trên ảnh. Tiếng Anh vì dữ liệu tầng này là hồ sơ SEC;
# đổi được qua tham số của render() cho ai cần bản tiếng Việt.
TIEU_DE_COT_CHI_TIEU = "Indicator"
MAU_DONG_DON_VI = "Unit: {don_vi}"

# Ký tự cho ô trống, cố ý dùng gạch nối ASCII chứ không dùng gạch dài.
#
# Báo cáo thật in gạch dài, nhưng font đi kèm Pillow không có glyph đó, và
# một ô trống vẽ thành ô vuông tofu thì VLM đọc ra ký tự lạ chứ không đọc ra
# "trống" — tức tầng này tự tạo cho mình một chế độ lỗi không có thật.
O_TRONG = "-"


@dataclass(frozen=True)
class RenderedTable:
    """
    Ảnh bảng kèm bbox từng ô giá trị.

    `bboxes` khoá theo `(concept, period)` và toạ độ tính trong ảnh TRANG,
    cùng hệ với `Provenance.bbox` ở B3 — để so trực tiếp được vùng mà bước
    đọc lại nhìn vào với vùng chứa giá trị thật, không phải quy đổi hệ toạ
    độ giữa hai chỗ.
    """

    image: Image.Image
    bboxes: dict[tuple[str, str], tuple[int, int, int, int]]
    header_bbox: tuple[int, int, int, int]

    # Chuỗi ĐÚNG NHƯ đã được vẽ lên ảnh, khoá giống `bboxes`.
    #
    # Có mặt ở đây vì bộ đo OCR cần so cái đọc được với cái đã VẼ, không
    # phải với giá trị số. Hai thứ đó khác nhau: 1234567.0 được vẽ thành
    # "1,234,567", còn số âm thành "(1,234,567)". Để bên đo tự dựng lại
    # chuỗi từ giá trị là chép lại quy tắc định dạng ở chỗ thứ hai, và
    # ngày nào quy tắc đổi thì phép đo lệch đi mà không có gì báo — bộ đo
    # sẽ tính là OCR đọc sai trong khi thật ra nó đọc đúng thứ trên ảnh.
    texts: dict[tuple[str, str], str] = field(default_factory=dict)


def _font(co_chu: int, font_path: str | None = None) -> ImageFont.FreeTypeFont:
    """
    Font để vẽ. Mặc định là font đi kèm Pillow.

    Không tự tìm font hệ thống: tầng này phải render ra ẢNH GIỐNG NHAU trên
    máy người dùng, trong CI và trong Docker. Một ảnh khác font là một bộ dữ
    liệu khác, và khi đó con số đo được ở hai nơi không so với nhau được
    nữa. Ai cần font khác thì nói ra bằng `font_path`, và tự chịu trách
    nhiệm ghi lại font đã dùng cho phần tái lập.
    """
    if font_path:
        return ImageFont.truetype(font_path, co_chu)
    return ImageFont.load_default(size=co_chu)


def _chu_ky_glyph(font: ImageFont.FreeTypeFont, ky_tu: str) -> bytes:
    mask = font.getmask(ky_tu)
    return bytes(mask) if mask.size[0] else b""


def ky_tu_khong_ve_duoc(font: ImageFont.FreeTypeFont, chu: str) -> set[str]:
    """
    Các ký tự mà font này không có glyph.

    Không có API tra bảng glyph nên so bằng ảnh: mọi ký tự thiếu đều được
    vẽ thành cùng một glyph .notdef, nên chỉ cần so với ảnh của một ký tự
    chắc chắn không tồn tại (U+FFFF là noncharacter theo chuẩn Unicode).

    Cần thiết vì đây là lỗi im lặng đúng nghĩa: ảnh vẫn ra một cái bảng
    trông bình thường, chỉ có chữ là ô vuông, và không có gì báo cho tới khi
    ai đó mở ảnh ra xem.
    """
    khong_ton_tai = _chu_ky_glyph(font, "￿")
    return {
        ky_tu
        for ky_tu in set(chu)
        if not ky_tu.isspace() and _chu_ky_glyph(font, ky_tu) == khong_ton_tai
    }


def _dinh_dang(gia_tri: float | None) -> str:
    """
    Định dạng số theo cách báo cáo tài chính in ra: phân nhóm nghìn, số âm
    trong ngoặc đơn, ô trống là dấu gạch.

    Số âm trong ngoặc không phải chi tiết thẩm mỹ: nó chính là nguồn của
    chế độ lỗi mất dấu âm, và render số âm bằng dấu trừ sẽ xoá mất một chế
    độ lỗi khỏi tầng này.
    """
    if gia_tri is None:
        return O_TRONG
    nguyen = int(round(abs(gia_tri)))
    chuoi = f"{nguyen:,}"
    return f"({chuoi})" if gia_tri < 0 else chuoi


def render(
    table: FinancialTable,
    co_chu: int = CO_CHU,
    cao_dong: int = CAO_DONG,
    font_path: str | None = None,
    tieu_de_cot_chi_tieu: str = TIEU_DE_COT_CHI_TIEU,
    mau_dong_don_vi: str = MAU_DONG_DON_VI,
) -> RenderedTable:
    """
    Vẽ bảng thành ảnh và trả kèm bbox từng ô.

    Bố cục: một dòng khai báo đơn vị tính, một dòng tiêu đề cột kỳ, rồi mỗi
    chỉ tiêu một dòng với nhãn bên trái và các cột số căn phải.

    Dòng khai báo đơn vị được vẽ như một phần tử hạng nhất chứ không phải
    chú thích, và `header_bbox` trả về riêng: nó là mỏ neo tuyệt đối duy
    nhất phá được bất biến scale, nên việc đọc được nó hay không tự nó là
    một phép đo, không phải chuyện phụ.

    Ném `ValueError` khi font không vẽ được một ký tự nào đó trong bảng.
    Nhãn tiếng Việt cần `font_path` trỏ tới font có dấu — xem docstring đầu
    module.
    """
    font = _font(co_chu, font_path)
    nhan_don_vi = mau_dong_don_vi.format(don_vi=table.unit_label)

    moi_chu = "".join(
        [
            nhan_don_vi,
            tieu_de_cot_chi_tieu,
            *table.periods,
            *[table.labels.get(ten, ten) for ten in table.concepts],
            *[
                _dinh_dang(table.get(ten, ky))
                for ten in table.concepts
                for ky in table.periods
            ],
        ]
    )
    thieu = ky_tu_khong_ve_duoc(font, moi_chu)
    if thieu:
        raise ValueError(
            f"font không vẽ được các ký tự {sorted(thieu)} — truyền font_path "
            f"trỏ tới một font có glyph cho chúng"
        )

    rong = LE * 2 + RONG_COT_NHAN + RONG_COT_SO * len(table.periods)
    cao = LE * 2 + cao_dong * (len(table.concepts) + 2)

    anh = Image.new("RGB", (rong, cao), "white")
    ve = ImageDraw.Draw(anh)

    # Dòng đơn vị tính
    y = LE
    ve.text((LE, y), nhan_don_vi, fill="black", font=font)
    hop_chu = ve.textbbox((LE, y), nhan_don_vi, font=font)
    header_bbox = (LE, y, hop_chu[2], y + cao_dong)

    # Dòng tiêu đề cột
    y += cao_dong
    ve.text((LE, y), tieu_de_cot_chi_tieu, fill="black", font=font)
    for j, ky in enumerate(table.periods):
        x_phai = LE + RONG_COT_NHAN + RONG_COT_SO * (j + 1)
        ve.text((x_phai, y), ky, fill="black", font=font, anchor="ra")
    ve.line((LE, y + cao_dong - 4, rong - LE, y + cao_dong - 4), fill="black", width=2)

    # Các dòng chỉ tiêu
    bboxes: dict[tuple[str, str], tuple[int, int, int, int]] = {}
    texts: dict[tuple[str, str], str] = {}
    for i, concept in enumerate(table.concepts):
        y_dong = LE + cao_dong * (i + 2)
        ve.text(
            (LE, y_dong),
            table.labels.get(concept, concept),
            fill="black",
            font=font,
        )

        for j, ky in enumerate(table.periods):
            x_trai = LE + RONG_COT_NHAN + RONG_COT_SO * j
            x_phai = x_trai + RONG_COT_SO
            chuoi = _dinh_dang(table.get(concept, ky))
            ve.text(
                (x_phai, y_dong),
                chuoi,
                fill="black",
                font=font,
                anchor="ra",
            )
            bboxes[(concept, ky)] = (x_trai, y_dong, x_phai, y_dong + cao_dong)
            texts[(concept, ky)] = chuoi

    return RenderedTable(
        image=anh, bboxes=bboxes, header_bbox=header_bbox, texts=texts
    )
