"""
Ma trận nhầm chữ số ĐÃ ĐO, dùng chung cho bộ tiêm lỗi và bộ sinh ứng viên.

Module này là NGUỒN DUY NHẤT của bảng nhầm chữ số trong repo. Trước nó, hai
chỗ cầm hai bảng khác nhau và cả hai đều là phỏng đoán:

  `eval/xbrl_tier/inject.py`  đổi một chữ số sang chữ số BẤT KỲ.
  `repair/candidates.py`      chỉ bốn cặp (0,8) (1,7) (3,8) (5,6).

Xác suất một lỗi tiêm vào nằm sẵn trong tập ứng viên vì thế xấp xỉ
(7/10)×(1/9) ≈ 0,078, đo được 0,092 — tức con số `digit_sub` của Mốc 3 là
ĐỘ TRÙNG CỦA HAI BẢNG PHỎNG ĐOÁN, không mang thông tin gì về phương pháp.

QUYẾT ĐỊNH CHI PHỐI MODULE NÀY — người dùng chốt 25/08/2026, phương án (a)
--------------------------------------------------------------------------
Cả hai phía cùng một nguồn, khác ĐỘ SÂU:

  Bộ TIÊM lấy mẫu theo TOÀN BỘ phân phối, kể cả phần đuôi.
  Bộ SINH ỨNG VIÊN chỉ mang `N_CAP_UNG_VIEN` cặp đầu bảng.

Khoảng hở giữa hai bên là thứ PHẢI GIỮ. Nếu hai bên là cùng một bảng hữu
hạn thì mọi lỗi tiêm vào đều sửa được, độ phủ lên 1,0, và thí nghiệm mất
khả năng làm lộ cơ chế ABSTAIN — mà ABSTAIN chính là lập luận chống bịa,
đóng góp cấu trúc của cả bài. Một thí nghiệm không tạo ra nổi tình huống nó
tuyên bố xử lý được thì nó không kiểm chứng điều đó.
`tests/test_nham_chu_so.py` chốt khoảng hở này bằng một test riêng.

HAI CHIỀU NGƯỢC NHAU — chỗ dễ đảo nhầm nhất
--------------------------------------------
Ma trận luôn đếm theo chiều `(thật → đọc thành)`. Nhưng:

  Bộ TIÊM biết giá trị THẬT, cần sinh cách đọc sai  → tra XUÔI.
  Bộ SINH ỨNG VIÊN chỉ thấy chữ số ĐÃ ĐỌC RA, phải đoán ngược giá trị thật
                                                    → tra NGƯỢC.

Đảo nhầm chiều là lỗi câm hoàn hảo: ứng viên vẫn sinh ra đủ số lượng, độ
phủ vẫn ra một con số trông hợp lý, chỉ có điều bộ sinh đi tìm sai chữ số
và không bao giờ trúng. Vì vậy hai chiều được tách thành hai hàm có tên nói
rõ chiều, thay vì một hàm nhận cờ.

VÌ SAO N = 6, VÀ VÌ SAO CON SỐ ĐÓ KHÔNG PHẢI CHỌN SAU KHI THẤY KẾT QUẢ
-----------------------------------------------------------------------
`N_CAP_UNG_VIEN` lấy đúng `MAX_MOI_NGUON` của `repair/candidates.py` —
hằng số đã nằm trong repo từ khi C1 ra đời, trước mọi phép đo ở đây. Nó là
trần số ứng viên mà nguồn `ocr_alt` được đóng góp cho mỗi chỉ tiêu, nên
mang nhiều hơn chừng ấy quy tắc nhầm cũng không sống sót qua bước cắt.

Hệ quả quan trọng: **độ phủ là KẾT QUẢ, không phải tham số.** Với ma trận
dưới đây, `khoi_luong_tich_luy(6)` bằng 0,933 — con số đó suy ra từ số đo
chứ không ai đặt nó.

GIỚI HẠN, PHẢI NÊU TRONG BÀI
-----------------------------
Đo bằng EasyOCR trên ảnh RENDER TỔNG HỢP sáu font, không phải trên scan
tiếng Việt thật. Lượt đo đầu chỉ dùng MỘT font và cho kết quả thoái hoá —
ba cặp, khối lượng chạm 1,000 ngay ở N = 3 — vì phân phối nhầm chữ số phụ
thuộc TYPEFACE chứ không phải phụ thuộc engine. Sáu font cho mười cặp, đủ
phần đuôi để phương án (a) chạy được, nhưng các cặp đuôi chỉ đếm được một
lần nên ước lượng ở đó rất yếu.

Con số độ phủ vì thế là con số TẠM và phải đo lại trên tập gold khi có.
Tầng XBRL lạc quan hơn tài liệu Việt Nam thật ở chế độ lỗi này.
"""

import random

# Ma trận đo được, đóng băng từ `data/output/ma_tran_nham_chu_so_easyocr.json`.
#
# Sinh lại bằng:
#     PYTHONIOENCODING=utf-8 PYTHONPATH=src \
#         python src/eval/do_ma_tran_nham_chu_so.py easyocr
#
# Lượt đo 25/08/2026: EasyOCR, 6 font (pillow mặc định, Arial, Times,
# Calibri, Consolas, Verdana) × 4 biến thể ảnh (sạch, mờ, nhiễu, độ phân
# giải thấp), 1080 lượt đọc ô, 60 quan sát nhầm chữ số.
#
# CHÉP TAY VÀO ĐÂY CHỨ KHÔNG NẠP TỪ JPSON LÚC CHẠY, và đó là chủ ý: đăng ký
# trước đòi ma trận phải có dấu thời gian TRƯỚC lượt chạy Mốc 3. Một hằng số
# nằm trong git diff chứng minh được điều đó; một lời gọi đọc file thì không,
# vì file có thể đổi sau mà không để lại vết trong lịch sử mã.
DEM_DO_DUOC: dict[tuple[str, str], int] = {
    ("9", "0"): 23,
    ("5", "3"): 13,
    ("6", "0"): 8,
    ("0", "8"): 6,
    ("7", "1"): 3,
    ("8", "6"): 3,
    ("9", "8"): 1,
    ("4", "1"): 1,
    ("4", "8"): 1,
    ("1", "4"): 1,
}

# Số cặp mà BỘ SINH ỨNG VIÊN được mang. Xem phần "VÌ SAO N = 6" ở đầu file.
#
# ĐÃ TÁCH KHỎI `MAX_MOI_NGUON`, ngày 25/08/2026. Con số 6 ban đầu lấy từ
# `MAX_MOI_NGUON` như nó đứng lúc đó; cùng ngày `MAX_MOI_NGUON` được nâng
# lên 10 sau khi đo thời gian giải, nhưng N Ở ĐÂY GIỮ NGUYÊN 6.
#
# Hai lý do, và lý do thứ hai mới là lý do thật:
#
# Một, ma trận đo được chỉ có 10 cặp. Để N = 10 nghĩa là bộ sinh mang TRỌN
# ma trận, độ phủ lên 1,0, và khoảng hở giữa bộ tiêm với bộ sinh biến mất —
# tức rơi đúng vào phương án (c) đã bị loại, nơi cơ chế ABSTAIN không còn
# lượt nào để lộ ra.
#
# Hai, N được chốt TRƯỚC khi có bất kỳ kết quả Mốc 3 nào theo cấu hình mới.
# Giữ nguyên nó chính là thứ bảo toàn giá trị của việc đăng ký trước; suy
# lại N từ `MAX_MOI_NGUON` mới sau khi đã nhìn thấy bảng độ phủ là chọn
# tham số theo kết quả, đúng thứ đăng ký trước sinh ra để ngăn.
N_CAP_UNG_VIEN = 6

CHU_SO = "0123456789"


def _xep_theo_tan_suat(dem: dict[tuple[str, str], int]) -> list[tuple[str, str]]:
    """
    Cặp xếp giảm dần theo số lần, hoà thì xếp theo thứ tự chữ.

    Phá hoà bằng thứ tự chữ chứ không để nguyên thứ tự dict: phần đuôi của
    ma trận có nhiều cặp cùng đếm được 1 lần, và nếu N cắt vào giữa đám hoà
    đó thì tập ứng viên sẽ đổi theo thứ tự chèn — tức đổi theo một thứ không
    ai kiểm soát, và lượt chạy sau không tái lập được lượt trước.
    """
    return [cap for cap, _ in sorted(dem.items(), key=lambda x: (-x[1], x[0]))]


def cap_hang_dau(
    n: int, dem: dict[tuple[str, str], int] | None = None
) -> tuple[tuple[str, str], ...]:
    """`n` cặp hay nhầm nhất, theo chiều (thật → đọc thành)."""
    dem = DEM_DO_DUOC if dem is None else dem
    return tuple(_xep_theo_tan_suat(dem)[:n])


def khoi_luong_tich_luy(n: int, dem: dict[tuple[str, str], int] | None = None) -> float:
    """
    Tỷ lệ quan sát rơi vào `n` cặp hay nhầm nhất.

    ĐÂY LÀ ĐỘ PHỦ LÝ THUYẾT của bộ sinh ứng viên: khi bộ tiêm lấy mẫu theo
    đúng phân phối này, xác suất lỗi tiêm ra nằm sẵn trong tập ứng viên bằng
    đúng con số này. Là đại lượng suy ra, không phải tham số.
    """
    dem = DEM_DO_DUOC if dem is None else dem
    tong = sum(dem.values())
    if not tong:
        return 0.0
    return sum(dem[cap] for cap in cap_hang_dau(n, dem)) / tong


def ung_vien_cho_chu_so(
    doc: str, n: int | None = None, dem: dict[tuple[str, str], int] | None = None
) -> tuple[str, ...]:
    """
    CHIỀU NGƯỢC — đọc ra chữ số `doc` thì giá trị thật có thể là những gì.

    Chỉ tra trong `n` cặp đầu bảng, vì đây là phía bị giới hạn độ sâu theo
    phương án (a). Trả tuple rỗng khi không cặp nào trong `n` cặp đầu đọc
    nhầm THÀNH `doc` — và rỗng là câu trả lời đúng, không phải thiếu sót:
    nó nghĩa là tập ứng viên đóng không chứa cách đọc nào cho ô này.
    """
    n = N_CAP_UNG_VIEN if n is None else n
    return tuple(that for that, d in cap_hang_dau(n, dem) if d == doc)


def lay_mau_doc_nham(
    that: str, rng: random.Random, dem: dict[tuple[str, str], int] | None = None
) -> tuple[str, str]:
    """
    CHIỀU XUÔI — chữ số thật là `that`, lấy mẫu một cách đọc sai.

    Trả `(chữ_số_đọc_thành, nguồn)` với nguồn thuộc tập đóng:
      "do_duoc"      — lấy theo phân phối đã đo cho chính chữ số này.
      "deu_xac_suat" — chữ số này CHƯA TỪNG quan sát thấy hỏng, nên lùi về
                       đều xác suất trên chín chữ số còn lại.

    VÌ SAO PHẢI TRẢ CẢ NGUỒN. Hai ca cần đọc khác nhau khi phân tích: lỗi
    tiêm theo số đo là lỗi mô phỏng thực tế và phương pháp có cơ hội sửa
    đúng; lỗi tiêm khi lùi về đều xác suất là lỗi của một chữ số mà phép đo
    chưa từng thấy hỏng, và nó gần như chắc chắn nằm ngoài tập ứng viên.
    Gộp hai ca lại thì bảng kết quả không tách nổi "phương pháp thua" khỏi
    "phép đo chưa phủ tới", đúng loại nhập nhằng đã làm hỏng lượt chạy trước.

    Lấy mẫu theo TOÀN BỘ phân phối kể cả phần đuôi — đây là phía không bị
    giới hạn độ sâu, và chính phần đuôi tạo ra các lượt mà phương pháp buộc
    phải bỏ phiếu trắng.
    """
    dem = DEM_DO_DUOC if dem is None else dem

    kha_nang = [(d, so_lan) for (t, d), so_lan in dem.items() if t == that]
    if kha_nang:
        cac_doc = [d for d, _ in kha_nang]
        trong_so = [so_lan for _, so_lan in kha_nang]
        return rng.choices(cac_doc, weights=trong_so, k=1)[0], "do_duoc"

    return rng.choice([c for c in CHU_SO if c != that]), "deu_xac_suat"
