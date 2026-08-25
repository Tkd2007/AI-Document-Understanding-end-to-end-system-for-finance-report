"""
Đo xem TIÊU ĐỀ báo cáo có lọt vào vùng bảng đã cắt không.

Câu hỏi: `detect_standard()` nhận diện chuẩn mẫu biểu bằng TÊN báo cáo
("Bảng cân đối kế toán" của TT200 so với "Báo cáo tình hình tài chính" của
TT99), mà tên đó nằm ở tiêu đề trang. Pipeline lại chỉ đưa cho nó text của
các VÙNG BẢNG đã cắt, nới `PADDING` 8 pixel. Vậy tiêu đề có nằm trong vùng
cắt không?

VÌ SAO PHẢI ĐO CHỨ KHÔNG SUY: câu "tiêu đề gần như chắc chắn nằm ngoài
vùng cắt" là suy từ cấu trúc code — YOLO khoanh bảng, tiêu đề không phải
bảng. Suy luận đó nghe hợp lý và vẫn có thể sai, vì bảng BCTC thường không
kẻ khung đầy đủ nên box YOLO trả về hay trùm rộng hơn phần kẻ ô, và vì
trang không có bảng nào thì pipeline fail-open lấy NGUYÊN TRANG. Chọn giữa
ba hướng sửa (OCR cả trang, nới PADDING, nhận diện bằng bộ MÃ SỐ) mà chưa
có số này là chọn mù.

TÁCH HAI CÂU HỎI, vì chúng dẫn tới hai cách sửa khác nhau:

  (1) HÌNH HỌC — dòng chữ tiêu đề có nằm lọt trong bbox của vùng cắt
      không. Đo bằng cách OCR CẢ TRANG lấy toạ độ từng dòng rồi kiểm bao
      hàm. Nếu KHÔNG thì nới `PADDING` mới có nghĩa.
  (2) THỰC DỤNG — text mà pipeline THẬT SỰ nhìn thấy (OCR trên ảnh đã
      cắt) có đủ để `detect_standard()` kết luận không. Đây mới là thứ
      quyết định có cần đổi gì hay không, vì OCR trên ảnh cắt và OCR trên
      cả trang không cho ra cùng một chuỗi.

Có hai đường ra kết luận "nhận diện được" và phải tách chúng: trang mà YOLO
tìm thấy bảng, và trang KHÔNG có bảng nào nên fail-open lấy nguyên trang.
Đường thứ hai nhận diện được là chuyện tình cờ của trang bìa và trang mục
lục — nó không chứng minh gì cho các trang mang bảng, nên báo cáo phải ghi
rõ cột `fail_open`.

Chạy (chậm vì EasyOCR chạy CPU, mỗi trang OCR hai lượt):
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/do_tieu_de_trong_vung_cat.py \
        > data/output/tieu_de_trong_vung_cat.md
"""

import argparse
import io
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

# Cùng cái bẫy như moc3.py: chạy như script thì src/eval/ nằm đầu sys.path và
# eval/metrics.py che mất src/metrics.py. Gỡ ra trước khi import.
if __name__ == "__main__":
    _thu_muc_script = str(Path(__file__).resolve().parent)
    sys.path[:] = [p for p in sys.path if Path(p).resolve() != Path(_thu_muc_script)]

import numpy as np  # noqa: E402

from fields_config import STANDARD_MARKERS, Standard, _bo_dau, detect_standard  # noqa: E402
from layout_detection import ca_trang, get_table_regions  # noqa: E402
from ocr_baseline import count_pages, get_reader, load_page  # noqa: E402

PDF_MAC_DINH = "data/samples/20260429_VNM_BCTC_DA_SOAT_XET_Q1_2026_RIENG_VN_920896fa41.pdf"

# Chỉ đo vài trang đầu. Bộ chỉ tiêu nằm ở ba biểu mẫu đầu tiên của báo cáo,
# và pipeline dừng sớm nên các trang cuối không bao giờ được duyệt tới —
# nhận diện chuẩn ở trang 40 là vô ích kể cả khi nó chạy được.
SO_TRANG_MAC_DINH = 12

# TÁCH hai dấu hiệu của STANDARD_MARKERS ra, vì chúng nằm ở hai chỗ khác
# nhau trên trang và chỉ một cái liên quan tới câu hỏi đang hỏi.
#
# `STANDARD_MARKERS[chuan][0]` là TÊN BÁO CÁO — nằm ở tiêu đề, tức đúng thứ
# nghi là rơi ra ngoài vùng cắt. `[1]` là SỐ HIỆU thông tư ("99/2025"), nằm
# rải rác trong thuyết minh và trong dòng "Ban hành theo…". Gộp hai cái lại
# rồi kết luận "nhận diện được nên tiêu đề nằm trong vùng cắt" là một bước
# nhảy sai: `detect_standard()` có thể kết luận nhờ số hiệu trong khi tiêu
# đề đã rơi mất. Bản đầu của module này mắc đúng lỗi đó.
MAU_THEO_LOAI: dict[str, dict[Standard, str]] = {
    "ten": {chuan: mau[0] for chuan, mau in STANDARD_MARKERS.items()},
    "so_hieu": {chuan: mau[1] for chuan, mau in STANDARD_MARKERS.items()},
}


def _dau_hieu_trong(text: str, loai: str) -> list[str]:
    """Các chuẩn có dấu hiệu thuộc `loai` xuất hiện trong đoạn text này."""
    khong_dau = _bo_dau(text)
    return [
        chuan.value
        for chuan, mau in MAU_THEO_LOAI[loai].items()
        if re.search(mau, khong_dau)
    ]


def _khop_duoc_gi(text: str) -> list[str]:
    """
    Chuỗi THẬT đã khớp từng mẫu, để đọc bằng mắt xem có khớp oan không.

    Cần thiết vì mẫu số hiệu `99\\s*/\\s*2025` cho `\\s*` nuốt cả xuống dòng,
    nên trong text OCR nhiều dòng nó có thể khớp vào hai con số chẳng liên
    quan nằm cạnh nhau. Không in ra chuỗi đã khớp thì không phân biệt được
    "nhận diện đúng nhờ số hiệu" với "khớp oan mà may là đoán trúng".
    """
    khong_dau = _bo_dau(text)
    khop = []
    for loai, theo_chuan in MAU_THEO_LOAI.items():
        for chuan, mau in theo_chuan.items():
            for m in re.finditer(mau, khong_dau):
                khop.append(f"{chuan.value}/{loai}: {m.group(0)!r}")
    return khop


def _im_lang(text: str):
    """
    Gọi detect_standard() mà nuốt phần nó in ra.

    detect_standard() cố ý in log mỗi lần không kết luận được, và ở đây nó
    bị gọi hai lần mỗi trang chỉ để lấy giá trị trả về. Giữ lại thì log
    tiến độ — thứ thật sự cần theo dõi trong một lượt chạy vài chục phút —
    bị chôn giữa các dòng "không tìm thấy dấu hiệu" lặp đi lặp lại.
    """
    with redirect_stdout(io.StringIO()):
        return detect_standard(text)


def _hop_bao(diem: list) -> tuple[int, int, int, int]:
    """Hình chữ nhật bao quanh 4 đỉnh EasyOCR trả về, dạng (x1, y1, x2, y2)."""
    xs = [int(p[0]) for p in diem]
    ys = [int(p[1]) for p in diem]
    return min(xs), min(ys), max(xs), max(ys)


def _nam_trong(nho: tuple[int, int, int, int], lon: tuple[int, int, int, int]) -> bool:
    """Hình chữ nhật `nho` có nằm lọt hoàn toàn trong `lon` không."""
    return (
        nho[0] >= lon[0] and nho[1] >= lon[1] and nho[2] <= lon[2] and nho[3] <= lon[3]
    )


def do_mot_trang(duong_dan: str, so_trang: int) -> dict:
    """
    Đo một trang: OCR cả trang lấy toạ độ, OCR từng vùng cắt lấy text thật.

    Trả về dict một dòng của bảng kết quả. Hai lượt OCR chứ không một:
    lượt cả trang trả lời câu hỏi HÌNH HỌC (tiêu đề nằm ở đâu), lượt trên
    ảnh đã cắt trả lời câu hỏi THỰC DỤNG (pipeline nhìn thấy gì). Dùng
    lượt cả trang để suy ra lượt kia là sai, vì OCR trên ảnh cắt cho ra
    chuỗi khác — đúng cái sai lầm mà phép đo này sinh ra để tránh.
    """
    anh = load_page(duong_dan, so_trang)
    vung = get_table_regions(anh)
    fail_open = not vung
    if fail_open:
        vung = [ca_trang(anh)]

    doc = get_reader()

    # (1) Cả trang, có toạ độ từng dòng.
    dong_ca_trang = doc.readtext(np.array(anh), detail=1)
    text_ca_trang = "\n".join(d[1] for d in dong_ca_trang)

    dong_tieu_de = []
    for diem, chu, _ in dong_ca_trang:
        if _dau_hieu_trong(chu, "ten"):
            hop = _hop_bao(diem)
            dong_tieu_de.append(
                {
                    "chu": chu,
                    "hop": hop,
                    "lot_vao_vung": any(_nam_trong(hop, v.bbox) for v in vung),
                }
            )

    # (2) Đúng thứ pipeline nhìn thấy: OCR trên các ảnh ĐÃ CẮT.
    text_vung = "\n".join("\n".join(doc.readtext(np.array(v.image), detail=0)) for v in vung)

    return {
        "trang": so_trang,
        "fail_open": fail_open,
        "so_vung": len(vung),
        "bbox": [v.bbox for v in vung],
        "ten_trong_ca_trang": _dau_hieu_trong(text_ca_trang, "ten"),
        "ten_trong_vung_cat": _dau_hieu_trong(text_vung, "ten"),
        "so_hieu_trong_vung_cat": _dau_hieu_trong(text_vung, "so_hieu"),
        "khop_trong_vung_cat": _khop_duoc_gi(text_vung),
        "dong_tieu_de": dong_tieu_de,
        "chuan_tu_vung_cat": _im_lang(text_vung),
        "chuan_tu_ca_trang": _im_lang(text_ca_trang),
    }


def chay(duong_dan: str, so_trang: int) -> list[dict]:
    """
    Đo lần lượt từng trang. stdout của phần ĐO bị đẩy hết sang stderr.

    Không phải để cho gọn: YOLO in một dòng thống kê cho MỖI ảnh nó suy
    luận, và `layout_detection` cùng `detect_standard` cũng in log của
    chúng. Tất cả đều ra stdout, tức trộn thẳng vào giữa bảng Markdown mà
    lệnh chạy đang chuyển hướng vào file. Ghi chúng sang stderr giữ được
    trọn vẹn phần log — thứ cần khi lượt đo có gì đó lạ — mà file kết quả
    vẫn là Markdown hợp lệ.
    """
    tong = min(so_trang, count_pages(duong_dan))
    ket_qua = []
    with redirect_stdout(sys.stderr):
        for i in range(1, tong + 1):
            print(f"[{i}/{tong}] đang đo trang {i}...", file=sys.stderr, flush=True)
            ket_qua.append(do_mot_trang(duong_dan, i))
    return ket_qua


def _o_chuan(ket: tuple) -> str:
    chuan, do_tin_cay = ket
    return "—" if chuan is None else f"{chuan.value} ({do_tin_cay:.2f})"


def bao_cao(duong_dan: str, ket_qua: list[dict]) -> str:
    """Bảng Markdown, kèm phần kết luận nói thẳng hướng nào còn sống."""
    dong = [
        "# Tiêu đề báo cáo có lọt vào vùng bảng đã cắt không",
        "",
        f"Tài liệu: `{duong_dan}` — {len(ket_qua)} trang đầu.",
        "",
        "`fail_open` = YOLO không tìm thấy bảng nào nên pipeline lấy NGUYÊN",
        "TRANG. Trang như vậy nhận diện được là chuyện tình cờ, không chứng",
        "minh gì cho các trang mang bảng.",
        "",
        "Hai cột dấu hiệu tách riêng vì chỉ cột TÊN liên quan tới câu hỏi:",
        "`detect_standard()` kết luận được nhờ SỐ HIỆU thông tư trong khi tiêu",
        "đề đã rơi ra ngoài vùng cắt là chuyện có thật, và gộp hai cột lại sẽ",
        "đọc ra kết luận ngược.",
        "",
        "| Trang | fail_open | Số vùng | TÊN trong cả trang | TÊN trong vùng cắt |"
        " SỐ HIỆU trong vùng cắt | Chuẩn từ vùng cắt | Chuẩn từ cả trang |",
        "|---:|---|---:|---|---|---|---|---|",
    ]

    for r in ket_qua:
        dong.append(
            f"| {r['trang']} | {'CÓ' if r['fail_open'] else '—'} | {r['so_vung']} "
            f"| {', '.join(r['ten_trong_ca_trang']) or '—'} "
            f"| {', '.join(r['ten_trong_vung_cat']) or '—'} "
            f"| {', '.join(r['so_hieu_trong_vung_cat']) or '—'} "
            f"| {_o_chuan(r['chuan_tu_vung_cat'])} | {_o_chuan(r['chuan_tu_ca_trang'])} |"
        )

    dong += ["", "## Dòng chữ mang tên báo cáo, và nó nằm trong hay ngoài vùng cắt", ""]
    co_dong = False
    for r in ket_qua:
        for d in r["dong_tieu_de"]:
            co_dong = True
            dong.append(
                f"- Trang {r['trang']}: `{d['chu']}` tại {d['hop']} — "
                f"{'LỌT VÀO' if d['lot_vao_vung'] else 'NẰM NGOÀI'} vùng cắt "
                f"{r['bbox']}"
            )
    if not co_dong:
        dong.append("- Không dòng nào mang tên báo cáo trong các trang đã đo.")

    dong += ["", "## Chuỗi thật đã khớp trong text vùng cắt", ""]
    for r in ket_qua:
        if r["khop_trong_vung_cat"]:
            dong.append(f"- Trang {r['trang']}: " + "; ".join(r["khop_trong_vung_cat"]))
    dong.append("")

    co_bang = [r for r in ket_qua if not r["fail_open"]]
    ten_lot_vao = [r for r in co_bang if r["ten_trong_vung_cat"]]
    nhan_duoc_tu_vung = [r for r in co_bang if r["chuan_tu_vung_cat"][0] is not None]
    nho_so_hieu = [r for r in nhan_duoc_tu_vung if not r["ten_trong_vung_cat"]]

    dong += [
        "## Số để chốt hướng đi",
        "",
        f"- Trang có bảng thật (không fail-open): **{len(co_bang)}/{len(ket_qua)}**. "
        "Phần còn lại YOLO không thấy bảng nào nên pipeline lấy nguyên trang, và "
        "câu hỏi vùng cắt không đặt ra ở đó.",
        f"- Trang mang bảng mà **TÊN báo cáo lọt vào vùng cắt**: "
        f"**{len(ten_lot_vao)}/{len(co_bang)}** ← đây mới là câu trả lời cho tiền đề.",
        f"- Trang mang bảng mà `detect_standard()` kết luận được từ text vùng cắt: "
        f"**{len(nhan_duoc_tu_vung)}/{len(co_bang)}**, trong đó "
        f"**{len(nho_so_hieu)}** kết luận được **nhờ SỐ HIỆU chứ không nhờ tên**.",
        "",
    ]

    if co_bang and not ten_lot_vao:
        dong += [
            "**Tiền đề ĐÚNG: tên báo cáo không lọt vào vùng cắt trên trang mang "
            "bảng nào.** Mọi lần nhận diện được từ vùng cắt đều nhờ số hiệu thông "
            "tư, tức nhờ một dấu hiệu KHÁC. Đó là chỗ phải cẩn thận: số hiệu chỉ "
            "xuất hiện trên báo cáo lập theo chuẩn mới còn nhắc văn bản ban hành, "
            "nên nó có thể vắng mặt hoàn toàn ở tài liệu khác, và mẫu "
            "`99\\s*/\\s*2025` cho `\\s*` nuốt cả xuống dòng nên còn khớp oan được. "
            "Xem phần chuỗi đã khớp ở trên trước khi tin con số này.",
        ]
    elif ten_lot_vao:
        dong += [
            f"**Tiền đề SAI với tài liệu này:** tên báo cáo lọt vào vùng cắt ở "
            f"{len(ten_lot_vao)}/{len(co_bang)} trang mang bảng (sớm nhất là trang "
            f"{ten_lot_vao[0]['trang']}), nên hướng nới `PADDING` mất lý do tồn tại.",
        ]
    else:
        dong += [
            "**Chưa trả lời được:** không trang nào trong khoảng đã đo có bảng thật, "
            "nên phép đo này không nói gì về vùng cắt. Đo thêm trang, hoặc đo trên "
            "tài liệu mà YOLO nhận ra bảng.",
        ]

    dong += [
        "",
        "**Một tài liệu không phải là bằng chứng cho mọi tài liệu.** Con số này "
        "đo trên đúng một báo cáo của một công ty, theo một chuẩn. Nó đủ để loại "
        "một hướng đi hiển nhiên sai, chưa đủ để chốt một hướng là đúng — muốn "
        "chốt thì đo lại trên tập gold khi có.",
        "",
    ]
    return "\n".join(dong) + "\n"


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    bo_phan_tich = argparse.ArgumentParser(description=__doc__)
    bo_phan_tich.add_argument("pdf", nargs="?", default=PDF_MAC_DINH)
    bo_phan_tich.add_argument("--so-trang", type=int, default=SO_TRANG_MAC_DINH)
    tham_so = bo_phan_tich.parse_args()

    print(bao_cao(tham_so.pdf, chay(tham_so.pdf, tham_so.so_trang)))
