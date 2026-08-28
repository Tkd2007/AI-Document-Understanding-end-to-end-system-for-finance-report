"""
Đo MA TRẬN NHẦM CHỮ SỐ của engine OCR, để cả hai phía cùng dùng một nguồn.

VÌ SAO MODULE NÀY TỒN TẠI
-------------------------
Hai chỗ trong repo cùng cầm một bảng chữ số, và cho tới nay chúng cầm hai
bảng khác nhau, cả hai đều là phỏng đoán:

  `eval/xbrl_tier/inject.py`  đổi một chữ số sang chữ số BẤT KỲ, đều xác
                              suất trên 9 chữ số còn lại.
  `repair/candidates.py`      chỉ sinh ứng viên từ bốn cặp (0,8) (1,7)
                              (3,8) (5,6).

Xác suất một lỗi tiêm vào nằm sẵn trong tập ứng viên vì thế xấp xỉ
(7/10)×(1/9) ≈ 0,078, và đo được 0,092 trên lượt chạy Mốc 3 ngày
24/08/2026. Con số đó là ĐỘ TRÙNG CỦA HAI BẢNG PHỎNG ĐOÁN, không mang thông
tin gì về phương pháp — xem HANDOFF.md mục 13.1.

Module này biến bảng đó từ phỏng đoán thành số đếm được, một lần, để
`src/nham_chu_so.py` đóng băng lại và cả hai phía cùng đọc từ đó.

HAI PHÍA DÙNG CÙNG MỘT MA TRẬN THEO HAI CHIỀU NGƯỢC NHAU
---------------------------------------------------------
Đây là chỗ dễ đảo nhầm nhất, và đảo nhầm thì không có gì nổ:

  Bộ TIÊM biết giá trị THẬT và cần sinh ra một cách đọc sai hợp lý.
      → tra theo chiều (thật → đọc thành).
  Bộ SINH ỨNG VIÊN chỉ thấy chữ số ĐÃ ĐỌC RA và cần đoán ngược lại giá trị
  thật có thể là gì.
      → tra theo chiều (đọc thành → thật), tức chiều NGƯỢC.

Ma trận đếm ở đây luôn ghi theo chiều thứ nhất: khoá `(that, doc)`.

VÌ SAO KHÔNG DÙNG CHUNG NGUYÊN VẸN MỘT BẢNG HỮU HẠN
----------------------------------------------------
Quyết định của người dùng ngày 25/08/2026 là phương án (a): cả hai phía
cùng nguồn, khác ĐỘ SÂU. Bộ tiêm lấy mẫu theo toàn bộ phân phối kể cả phần
đuôi; bộ sinh ứng viên chỉ lấy N cặp đầu bảng, với N do `MAX_UNG_VIEN` chặn
sẵn từ trước chứ không phải núm vặn mới.

Lý do phải giữ khoảng hở đó: nếu hai bên là cùng một bảng hữu hạn thì mọi
lỗi tiêm vào đều sửa được, độ phủ lên gần 1,0, và thí nghiệm mất khả năng
làm lộ cơ chế ABSTAIN — mà ABSTAIN chính là lập luận chống bịa, đóng góp
cấu trúc của cả bài. Một thí nghiệm không tạo ra nổi tình huống nó tuyên bố
xử lý được thì nó không kiểm chứng điều đó.

Với phương án (a), độ phủ trở thành **khối lượng xác suất của N cặp đầu**,
tức một đại lượng SUY RA ĐƯỢC từ số đo, không phải tham số chọn tay.

GIỚI HẠN, PHẢI NÊU TRONG BÀI
-----------------------------
Ma trận này đo bằng EasyOCR trên ảnh RENDER TỔNG HỢP, không phải trên scan
tiếng Việt thật. Nó là mô hình của *engine này trên ảnh sạch và ảnh xuống
cấp nhân tạo*. Con số độ phủ suy ra từ nó vì thế là con số TẠM, và phải đo
lại trên tập gold khi có. Đây là lý do tầng XBRL lạc quan hơn tài liệu
Việt Nam thật ở chế độ lỗi này.

Chạy (chậm, vài chục phút vì EasyOCR chạy CPU):
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/do_ma_tran_nham_chu_so.py
"""

import json
import sys
from pathlib import Path

if __name__ == "__main__":
    _thu_muc_script = str(Path(__file__).resolve().parent)
    sys.path[:] = [p for p in sys.path if Path(p or ".").resolve() != Path(_thu_muc_script)]
    _src = str(Path(__file__).resolve().parents[1])
    if _src not in sys.path:
        sys.path.insert(0, _src)

from eval.ocr_compare import (  # noqa: E402
    ENGINES,
    bang_nham_chu_so,
    bang_tong_hop,
    so_sanh_engine,
    thong_ke_nham_chu_so,
)
from eval.xbrl_tier.render import render  # noqa: E402

# Mỗi font một seed, thay vì nhiều seed trên cùng một font.
#
# LƯỢT ĐO ĐẦU (25/08/2026) DÙNG SÁU SEED TRÊN MỘT FONT VÀ CHO KẾT QUẢ
# THOÁI HOÁ: 1080 lượt đọc ô, 208 quan sát nhầm, nhưng chỉ **ba cặp phân
# biệt** — `9→0` (168), `6→0` (38), `9→8` (2). Khối lượng tích luỹ chạm
# 1,000 ngay ở N = 3.
#
# Đó không phải phân phối nhầm chữ số của OCR. Đó là phân phối nhầm chữ số
# CỦA MỘT TYPEFACE: `render.py` cố ý dùng đúng font mặc định của Pillow để
# ảnh giống nhau trên mọi máy, nên mọi lỗi đo được đều là lỗi đọc đúng một
# bộ hình dạng chữ số. `9` và `6` đều có một vòng khép kín, và ở độ phân
# giải thấp vòng ấy đọc thành `0`.
#
# Hệ quả trực tiếp: đổi seed chỉ đổi CON SỐ trên bảng, không đổi hình dạng
# chữ số, nên thêm seed không bao giờ sinh ra cặp nhầm mới. Thứ sinh ra
# phần đuôi của phân phối là ĐA DẠNG THỊ GIÁC, và ở đây nó tới từ font.
#
# Đổi sáu seed một font thành sáu font một seed: cùng chi phí tính toán,
# đổi trục đa dạng sang đúng trục đang thiếu. `render()` cho phép việc này
# qua `font_path`, kèm điều kiện phải ghi lại font đã dùng — làm ở phần báo
# cáo và trong JSON.
#
# ĐÁNH ĐỔI PHẢI NÊU: font hệ thống khác nhau giữa các máy, nên lượt đo này
# KHÔNG tái lập được trên CI hay trong Docker như phần còn lại của tầng
# XBRL. Chấp nhận được vì thứ đi vào repo là MA TRẬN ĐÃ ĐÓNG BĂNG, không
# phải khả năng dựng lại nó; bù lại phải ghi rõ font nào đã dùng.
CAC_FONT: tuple[tuple[str, str | None, int], ...] = (
    ("pillow_mac_dinh", None, 20260823),
    ("arial", r"C:\Windows\Fonts\arial.ttf", 20260824),
    ("times", r"C:\Windows\Fonts\times.ttf", 20260825),
    ("calibri", r"C:\Windows\Fonts\calibri.ttf", 20260826),
    ("consolas", r"C:\Windows\Fonts\consola.ttf", 20260827),
    ("verdana", r"C:\Windows\Fonts\verdana.ttf", 20260828),
)

# Đo trên CẢ ảnh sạch lẫn ảnh xuống cấp.
#
# Chỉ đo ảnh sạch thì gần như không có lỗi nào để đếm — lượt cũ cho
# Levenshtein 0,999. Chỉ đo ảnh xấu nhất thì phân phối lệch hẳn về chế độ
# hỏng của riêng mức xuống cấp đó. Lấy cả bốn biến thể là lấy hỗn hợp mà
# một tập tài liệu thật cũng có: phần lớn đọc tốt, một phần xấu.
CAC_BIEN_THE = ("sach", "mo", "nhieu", "phan_giai_thap")

# Cỡ N đem ra lập bảng khối lượng tích luỹ, để chọn N có căn cứ.
CAC_N = (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20)


def chay(ten_engine: str = "easyocr") -> tuple[dict[tuple[str, str], int], int, list[str]]:
    """
    Đo trên mọi font × mọi biến thể ảnh.

    Trả (đếm theo cặp, số ô đã đọc, tên các font thật sự dùng được). Font
    thiếu trên máy thì BỎ QUA và ghi ra stderr chứ không ném lỗi: phép đo
    vẫn có nghĩa với ít font hơn, chỉ là phần đuôi phân phối mỏng đi, và
    danh sách font trả về nói ra chính xác lượt đo này đứng trên gì.
    """
    cac_bang = []
    font_dung_duoc: list[str] = []

    for ten_font, duong_dan, seed in CAC_FONT:
        if duong_dan is not None and not Path(duong_dan).exists():
            print(f"BỎ QUA font {ten_font}: không có {duong_dan}", file=sys.stderr)
            continue
        print(f"render bảng font={ten_font} seed={seed}...", file=sys.stderr, flush=True)
        cac_bang.append(render(bang_tong_hop(seed=seed), font_path=duong_dan))
        font_dung_duoc.append(ten_font)

    print(
        f"đo {ten_engine} trên {sum(len(b.bboxes) for b in cac_bang)} ô "
        f"× {len(CAC_BIEN_THE)} biến thể ảnh...",
        file=sys.stderr,
        flush=True,
    )
    ket_qua = so_sanh_engine(
        cac_bang,
        engines={ten_engine: ENGINES[ten_engine]},
        cac_bien_the=CAC_BIEN_THE,
    )

    return thong_ke_nham_chu_so(ket_qua), sum(kq.n_o for kq in ket_qua), font_dung_duoc


def khoi_luong_tich_luy(dem: dict[tuple[str, str], int], n: int) -> float:
    """
    Tỷ lệ quan sát rơi vào `n` cặp hay nhầm nhất.

    ĐÂY CHÍNH LÀ ĐỘ PHỦ LÝ THUYẾT mà bộ sinh ứng viên đạt được nếu chỉ mang
    `n` cặp đầu bảng: nếu bộ tiêm lấy mẫu theo đúng phân phối này, thì xác
    suất lỗi tiêm ra nằm trong tập ứng viên đúng bằng con số này.

    Nó là đại lượng SUY RA, không phải tham số. Ghi rõ điều đó vì đây là chỗ
    một người đọc hoài nghi sẽ nghi ngờ đầu tiên.
    """
    tong = sum(dem.values())
    if not tong:
        return 0.0
    hang_dau = sorted(dem.values(), reverse=True)[:n]
    return sum(hang_dau) / tong


def bao_cao(
    dem: dict[tuple[str, str], int], n_o: int, ten_engine: str, cac_font: list[str]
) -> str:
    """Báo cáo Markdown, kèm bảng khối lượng tích luỹ để chọn N có căn cứ."""
    tong = sum(dem.values())

    dong = [
        f"# Ma trận nhầm chữ số đo được — {ten_engine}",
        "",
        f"Sinh bằng `python src/eval/do_ma_tran_nham_chu_so.py {ten_engine}`. "
        f"{len(cac_font)} font × {len(CAC_BIEN_THE)} biến thể ảnh "
        f"({', '.join(CAC_BIEN_THE)}), tổng **{n_o} lượt đọc ô** và "
        f"**{tong} quan sát nhầm chữ số**.",
        "",
        f"Font đã dùng: {', '.join(f'`{f}`' for f in cac_font)}. Ghi ra vì phân "
        f"phối nhầm chữ số PHỤ THUỘC TYPEFACE — lượt đo đầu chỉ dùng font mặc "
        f"định của Pillow và chỉ thu được ba cặp phân biệt, tức nó đo một bộ "
        f"hình dạng chữ số chứ không đo OCR.",
        "",
        "Chiều của khoá là **(thật → đọc thành)**. Bộ tiêm lỗi tra theo chiều",
        "này; bộ sinh ứng viên tra theo chiều NGƯỢC, vì nó chỉ thấy chữ số đã",
        "đọc ra và phải đoán ngược lại giá trị thật.",
        "",
        "Chỉ tính những ô mà chuỗi đọc được dài bằng chuỗi thật, nên đây là",
        "cận dưới — xem docstring `thong_ke_nham_chu_so`.",
        "",
        "## Cặp nhầm, xếp theo tần suất",
        "",
        bang_nham_chu_so(dem, top=30),
        "",
        "## Khối lượng tích luỹ của N cặp đầu bảng",
        "",
        "Cột phải là **độ phủ lý thuyết** của bộ sinh ứng viên nếu nó chỉ mang",
        "N cặp đầu: khi bộ tiêm lấy mẫu theo đúng phân phối này, xác suất lỗi",
        "tiêm ra nằm sẵn trong tập ứng viên đúng bằng con số đó. Đây là đại",
        "lượng SUY RA từ số đo, không phải tham số chọn tay.",
        "",
        "| N cặp đầu | Khối lượng tích luỹ |",
        "|---:|---:|",
    ]
    for n in CAC_N:
        dong.append(f"| {n} | {khoi_luong_tich_luy(dem, n):.3f} |")

    dong += [
        "",
        f"Số cặp phân biệt quan sát được: **{len(dem)}** trên tối đa 90 cặp có thể.",
        "",
        "## Giới hạn",
        "",
        "Đo bằng ảnh **render tổng hợp**, không phải scan tiếng Việt thật. Đây là",
        "mô hình của engine này trên ảnh sạch và ảnh xuống cấp nhân tạo, nên con",
        "số độ phủ suy ra từ nó là con số TẠM và phải đo lại trên tập gold khi",
        "có. Tầng XBRL vì thế lạc quan hơn tài liệu Việt Nam thật ở chế độ lỗi",
        "`digit_substitution`.",
        "",
    ]
    return "\n".join(dong) + "\n"


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    ten = sys.argv[1] if len(sys.argv) > 1 else "easyocr"
    if ten not in ENGINES:
        raise SystemExit(f"Engine không biết: {ten}. Có: {sorted(ENGINES)}")

    dem, n_o, cac_font = chay(ten)

    thu_muc = Path("data/output")
    thu_muc.mkdir(parents=True, exist_ok=True)

    (thu_muc / f"ma_tran_nham_chu_so_{ten}.md").write_text(
        bao_cao(dem, n_o, ten, cac_font), encoding="utf-8"
    )

    # JSON để đóng băng vào src/nham_chu_so.py, khoá dạng "9->0" vì tuple
    # không phải khoá JSON hợp lệ.
    (thu_muc / f"ma_tran_nham_chu_so_{ten}.json").write_text(
        json.dumps(
            {
                "engine": ten,
                "n_o": n_o,
                "fonts": cac_font,
                "bien_the": list(CAC_BIEN_THE),
                "dem": {f"{a}->{b}": v for (a, b), v in sorted(dem.items())},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(bao_cao(dem, n_o, ten, cac_font))
    print(f"Đã ghi {thu_muc}/ma_tran_nham_chu_so_{ten}.md và .json")
