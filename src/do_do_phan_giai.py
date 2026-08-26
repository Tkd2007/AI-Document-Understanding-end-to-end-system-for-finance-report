"""
Đo độ phân giải bản quét của từng tài liệu trong tập gold.

VÌ SAO CẦN ĐO. `ANNOTATION-GUIDELINE.md` mục 7 chia tập Stress làm bốn nhóm,
nhóm thứ ba là "bản scan chất lượng thấp" với cách nhận ra là "mở PDF, xem có
phải ảnh nhúng không". Đo ngày 26/08/2026 trên 23 tài liệu của 20 doanh
nghiệp cho thấy tiêu chí ấy được 100% quần thể thoả: không báo cáo niêm yết
nào có lớp text thật. Một tiêu chí mà cả tổng thể đều thoả thì không chia
được nhóm nào, nên nhóm thứ ba mất hẳn sức phân biệt.

Trục thay thế là ĐỘ PHÂN GIẢI của bản quét, và nó trải rộng thật. Script này
là cách đo trục đó bằng máy, thay cho phán đoán mắt người vốn không tái lập
được.

CÁCH ĐO. Trang của báo cáo quét là một ảnh nhúng phủ gần kín khổ giấy, nên
độ phân giải hiệu dụng là số điểm ảnh chia cho chiều dài thật mà cạnh ấy trải
ra trên giấy.

**KHÔNG dùng `horizontal_dpi`/`vertical_dpi` của pdfium.** Hai trường đó chỉ
chia cho phần đường chéo của ma trận đặt ảnh, nên khi ảnh được đặt XOAY 90°
— ma trận có b và c khác 0 — chúng chia nhầm cạnh và trả ra một cặp số méo.
`SBT_2025Q2_TT200` là ca đó: pdfium báo 127,3 và 63,5 dpi, tức lệch nhau gấp
đôi như thể bản quét bị kéo dãn, trong khi tính từ ma trận thì nó là 90 dpi
đều cả hai chiều. Bản đầu của script này tin hai trường ấy và ghi 95,4 dpi
cho SBT — trung bình cộng của một cặp số vốn không có nghĩa.

Cách đúng là chiếu qua ma trận: cạnh ngang của ảnh trải theo véc-tơ (a, b),
cạnh dọc theo (c, d), nên chiều dài thật là chuẩn Euclid của từng véc-tơ.
Công thức này đúng cho cả trang xoay lẫn trang không xoay.

Số đại diện cho một trang là **nhỏ hơn trong hai chiều**, không phải trung
bình: chiều thưa điểm ảnh hơn là chiều quyết định nét chữ còn đọc được hay
không, nên trung bình sẽ báo đẹp hơn sự thật đúng ở những ca đáng lo nhất.

Mỗi trang lấy ảnh LỚN NHẤT chứ không lấy mọi ảnh, vì nhiều trang còn nhúng
thêm dấu mộc hoặc chữ ký số ở độ phân giải khác hẳn; gộp chúng vào sẽ kéo con
số đi mà không nói gì về chất lượng phần chữ.

Con số đại diện cho cả tài liệu là TRUNG VỊ theo trang, không phải trung bình:
báo cáo hay có vài trang bìa hoặc trang ký quét riêng ở độ phân giải khác, và
trung vị không bị mấy trang đó kéo.

Chạy:
    python src/do_do_phan_giai.py                  # in bảng, không sửa gì
    python src/do_do_phan_giai.py --ghi            # ghi vào data/nguon_gold.json
    python src/do_do_phan_giai.py --thu-muc D:\\bctc
"""

import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import pypdfium2 as pdfium

# Ép stdout/stderr về UTF-8, cùng lý do đã ghi ở đầu `src/tai_bctc.py`: bảng
# mã cp1252 của máy này không có chữ "đ", nên mọi dòng tiếng Việt in ra sẽ ném
# UnicodeEncodeError ngay khi output bị chuyển hướng vào file hay nối vào lệnh
# khác — chạy thẳng trong cửa sổ lệnh thì không lộ.
for _luong in (sys.stdout, sys.stderr):
    if hasattr(_luong, "reconfigure"):
        _luong.reconfigure(encoding="utf-8", errors="replace")

DANH_MUC = Path("data/nguon_gold.json")
THU_MUC_MAC_DINH = Path("data/bctc")

# Đơn vị độ dài của PDF là "điểm", quy ước 72 điểm một inch.
DIEM_MOI_INCH = 72.0

# Tên khoá ghi vào danh mục. Đặt tên nói rõ đây là số ĐO ĐƯỢC, để không lẫn
# với những trường mô tả bằng lời ở cùng chỗ.
KHOA = "do_phan_giai_dpi"


def dpi_hai_chieu(anh: pdfium.PdfImage) -> tuple[float, float] | None:
    """
    Độ phân giải theo hai cạnh của một ảnh, tính từ ma trận đặt ảnh.

    Trả None khi ảnh bị đặt suy biến (một cạnh dài 0 điểm) — không chia được
    thì không có số, và bịa ra 0 ở đây sẽ thành "quét cực kém" trong trung vị.
    """
    sieu_du_lieu = anh.get_metadata()
    ma_tran = anh.get_matrix()

    # Cạnh ngang của ảnh trải theo véc-tơ (a, b) của ma trận, cạnh dọc theo
    # (c, d). Lấy chuẩn Euclid nên công thức đúng cả khi ảnh bị xoay, tức
    # đúng ở đúng chỗ mà hai trường dpi của pdfium sai.
    diem_ngang = math.hypot(ma_tran.a, ma_tran.b)
    diem_doc = math.hypot(ma_tran.c, ma_tran.d)
    if diem_ngang <= 0 or diem_doc <= 0:
        return None

    return (
        sieu_du_lieu.width / (diem_ngang / DIEM_MOI_INCH),
        sieu_du_lieu.height / (diem_doc / DIEM_MOI_INCH),
    )


def do_mot_trang(trang: pdfium.PdfPage) -> float | None:
    """
    Độ phân giải hiệu dụng của một trang, hoặc None nếu trang không có ảnh.

    Trang không có ảnh nào là trang text thuần — hiếm, nhưng có thật ở vài
    trang mục lục. Trả None chứ không trả 0: 0 sẽ lọt vào trung vị và kéo con
    số của cả tài liệu xuống, trong khi sự thật là trang đó không đo được chứ
    không phải quét kém.
    """
    lon_nhat = None
    dpi_lon_nhat = None

    for doi_tuong in trang.get_objects():
        if not isinstance(doi_tuong, pdfium.PdfImage):
            continue
        sieu_du_lieu = doi_tuong.get_metadata()
        diem_anh = sieu_du_lieu.width * sieu_du_lieu.height
        if lon_nhat is not None and diem_anh <= lon_nhat:
            continue
        hai_chieu = dpi_hai_chieu(doi_tuong)
        if hai_chieu is None:
            continue
        lon_nhat = diem_anh
        dpi_lon_nhat = min(hai_chieu)

    return dpi_lon_nhat


def do_mot_tai_lieu(duong_dan: Path, gioi_han_trang: int | None = None) -> dict | None:
    """
    Đo cả tài liệu, trả về trung vị kèm dải và số trang đo được.

    Ghi cả `nho_nhat` và `lon_nhat` chứ không chỉ trung vị, vì một tài liệu
    trộn nhiều lần quét khác nhau là chuyện có thật và trung vị một mình giấu
    mất điều đó. `so_trang_do_duoc` để người đọc biết trung vị dựa trên bao
    nhiêu trang — trung vị của 2 trang không đáng tin như trung vị của 50.
    """
    pdf = pdfium.PdfDocument(duong_dan)
    try:
        so_trang = len(pdf) if gioi_han_trang is None else min(len(pdf), gioi_han_trang)
        do_duoc = []
        for chi_so in range(so_trang):
            dpi = do_mot_trang(pdf[chi_so])
            if dpi is not None:
                do_duoc.append(dpi)
    finally:
        # Đóng trước khi dựng kết quả, và vì thế `so_trang` phải lấy xong từ
        # trên: mọi thuộc tính của PdfDocument đều đi qua con trỏ C, nên đọc
        # `len(pdf)` sau khi đóng ném ctypes.ArgumentError chứ không ném lỗi
        # Python đọc ra nghĩa.
        pdf.close()

    if not do_duoc:
        return None

    return {
        "trung_vi": round(statistics.median(do_duoc), 1),
        "nho_nhat": round(min(do_duoc), 1),
        "lon_nhat": round(max(do_duoc), 1),
        "so_trang_do_duoc": len(do_duoc),
        "so_trang_tong": so_trang,
    }


def main() -> int:
    bo_doc = argparse.ArgumentParser(description=__doc__)
    bo_doc.add_argument("--thu-muc", type=Path, default=THU_MUC_MAC_DINH)
    bo_doc.add_argument(
        "--ghi",
        action="store_true",
        help=f"ghi kết quả vào khoá {KHOA} của {DANH_MUC}",
    )
    tham_so = bo_doc.parse_args()

    danh_muc = json.loads(DANH_MUC.read_text(encoding="utf-8"))

    ket_qua = {}
    thieu = []
    for muc in danh_muc["tai_lieu"]:
        duong_dan = tham_so.thu_muc / f"{muc['doc_id']}.pdf"
        if not duong_dan.exists():
            thieu.append(muc["doc_id"])
            continue
        do_duoc = do_mot_tai_lieu(duong_dan)
        if do_duoc is None:
            # Tài liệu không có ảnh nào là ca đáng biết chứ không đáng bỏ
            # qua: nó sẽ là báo cáo PDF chữ đầu tiên tìm được, và phát hiện
            # "mọi báo cáo đều là ảnh quét" phải được xét lại.
            print(f"{muc['doc_id']:24s} KHÔNG có ảnh nhúng — xem lại, có thể là PDF chữ")
            continue
        ket_qua[muc["doc_id"]] = do_duoc

    if ket_qua:
        print(f"{'doc_id':24s} {'trung vị':>9s} {'nhỏ nhất':>9s} {'lớn nhất':>9s}  trang")
        for doc_id, do_duoc in sorted(ket_qua.items(), key=lambda c: c[1]["trung_vi"]):
            print(
                f"{doc_id:24s} {do_duoc['trung_vi']:9.1f} {do_duoc['nho_nhat']:9.1f} "
                f"{do_duoc['lon_nhat']:9.1f}  {do_duoc['so_trang_do_duoc']}"
                f"/{do_duoc['so_trang_tong']}"
            )
        cac_trung_vi = [d["trung_vi"] for d in ket_qua.values()]
        print(
            f"\nDải trên {len(ket_qua)} tài liệu: {min(cac_trung_vi):.1f} – "
            f"{max(cac_trung_vi):.1f} dpi, trung vị {statistics.median(cac_trung_vi):.1f}"
        )

    if thieu:
        print(f"\nChưa tải về {tham_so.thu_muc} — chạy `python src/tai_bctc.py`:")
        for doc_id in thieu:
            print(f"  {doc_id}")

    if tham_so.ghi:
        for muc in danh_muc["tai_lieu"]:
            if muc["doc_id"] in ket_qua:
                muc[KHOA] = ket_qua[muc["doc_id"]]
        DANH_MUC.write_text(
            json.dumps(danh_muc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"\nĐã ghi {len(ket_qua)} số đo vào {DANH_MUC}")

    return 1 if thieu else 0


if __name__ == "__main__":
    sys.exit(main())
