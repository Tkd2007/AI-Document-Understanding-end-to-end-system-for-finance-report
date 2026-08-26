"""
Chạy pipeline trên tập gold và chấm điểm — phép đo đầu tiên trên dữ liệu THẬT.

Mọi con số về chất lượng trích xuất tới nay đều lấy trên tầng XBRL Mỹ hoặc
trên đúng một báo cáo VNM. Script này là chỗ đầu tiên chấm pipeline trên bộ
tài liệu Việt Nam có nhãn tay, tức là chỗ đầu tiên con số nói được điều gì
đó về bài toán thật.

HAI CHẾ ĐỘ, và khoảng cách giữa chúng CHÍNH LÀ phép đo:

  * `--chuan-tu-gold` — chuẩn mẫu biểu lấy thẳng từ nhãn. Đây là điều kiện
    ORACLE: nó giả định bước nhận diện chuẩn đã hoàn hảo, nên đo được chất
    lượng trích xuất tách khỏi chất lượng nhận diện.
  * mặc định — không truyền chuẩn, để pipeline tự xoay xở. Đây là hiện
    trạng đầu-cuối.

Vì sao khoảng cách ấy đáng đo chứ không phải chi tiết vặt: `router.chon_chuan`
hiện KHÔNG có nguồn `nhan_dien`, nên khi không ai chỉ định nó lùi về
`DEFAULT_STANDARD` là TT99. Tập gold có cả TT200, và hai chuẩn dùng hai bảng
mã số dòng khác nhau — mã 270 của TT200 là mã 280 của TT99. Chạy sai bảng thì
kết quả hỏng vì lý do chẳng liên quan gì tới phương pháp. Hiệu số giữa hai chế
độ vì thế đo đúng một thứ: **bước D của phương án C đáng giá bao nhiêu**.

CHẤM ĐIỂM ở mức TRƯỜNG, gộp tử và mẫu qua các tài liệu chứ không lấy trung
bình của các tỷ lệ — hai tài liệu có số chỉ tiêu khác nhau (26 với TT200, 27
với TT99) nên trung bình của tỷ lệ không bằng tỷ lệ của tổng.

Kết quả ghi ra `data/output/tap_gold_<chế độ>.json` TRƯỚC khi in bảng. Đây là
bài học của lượt chạy Mốc 3 ngày 25/08: `bao_cao()` in thẳng ra stdout không
lưu gì, nên muốn in lại bảng theo cách khác phải chạy lại 103 phút.

CẢNH BÁO VỀ LUẬT 1 — đọc trước khi mở file JSON kia. Guideline mục 1 buộc
người gán nhãn phải MÙ với đầu ra pipeline. Tập gold hiện có 11 tài liệu và
phương án đo đồng thuận dự phòng là chính người ấy gán nhãn lại sau ít nhất
hai tuần. Nếu người sẽ gán nhãn lại đọc giá trị pipeline đoán cho từng ô của
những tài liệu này, lượt gán nhãn lại bị neo và phép đo đồng thuận mất giá
trị. Bảng in ra màn hình cố ý chỉ có số GỘP theo tài liệu, không có giá trị
từng ô; file JSON thì có, và nó tồn tại cho lượt phân tích về sau chứ không
phải để người gán nhãn đọc.

Chạy:
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --chuan-tu-gold
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --chi HPG BMP
"""

import argparse
import json
import sys
import traceback
from pathlib import Path

# Chạy như script thì thư mục src/eval/ nằm đầu sys.path và eval/metrics.py
# che mất src/metrics.py của pipeline. Cùng họ với vụ src/types.py — xem
# HANDOFF.md mục 9. Gỡ thư mục script ra trước khi import bất cứ thứ gì.
if __name__ == "__main__":
    _thu_muc_script = str(Path(__file__).resolve().parent)
    sys.path[:] = [p for p in sys.path if Path(p).resolve() != Path(_thu_muc_script)]

from eval.metrics import (  # noqa: E402
    document_fully_correct,
    field_accuracy,
    silent_error_rate,
)
from fields_config import Standard  # noqa: E402
from router import route_document  # noqa: E402

THU_MUC_GOLD = Path("data/gold")
THU_MUC_PDF = Path("data/bctc")
THU_MUC_RA = Path("data/output")

for _luong in (sys.stdout, sys.stderr):
    if hasattr(_luong, "reconfigure"):
        _luong.reconfigure(encoding="utf-8", errors="replace")


def doc_gold(duong_dan: Path) -> dict:
    return json.loads(duong_dan.read_text(encoding="utf-8"))


def cham_mot_tai_lieu(gold: dict, du_doan: dict) -> dict:
    """
    Chấm một tài liệu, trả cả tử và mẫu chứ không chỉ tỷ lệ.

    Bootstrap theo cụm tài liệu cần cộng dồn tử/mẫu, và tỷ lệ một mình thì
    cộng dồn không được.
    """
    that = gold["values"]
    return {
        "do_chinh_xac": field_accuracy(du_doan, that),
        "loi_cam": silent_error_rate(du_doan, that),
        "dung_tron_ven": document_fully_correct(du_doan, that),
    }


def chay_mot_tai_lieu(gold: dict, pdf: Path, chuan_tu_gold: bool) -> dict:
    chuan = Standard(gold["standard"]) if chuan_tu_gold else None
    ket_qua = route_document(str(pdf), save=False, standard=chuan)
    du_doan = ket_qua.values()

    diem = cham_mot_tai_lieu(gold, du_doan)
    diem["doc_id"] = gold["doc_id"]
    diem["chuan_that"] = gold["standard"]
    diem["chuan_da_dung"] = ket_qua.meta.get("standard")
    # Nguồn của kết luận chuẩn, không chỉ kết luận: "TT99 vì người chỉ định"
    # và "TT99 vì lùi về mặc định" là hai lượt chạy khác hẳn nhau về độ tin
    # cậy, và gộp chúng lại là xoá mất một chế độ lỗi khỏi phép đo.
    diem["nguon_chuan"] = ket_qua.meta.get("standard_nguon")
    # Hệ số đơn vị là mỏ neo duy nhất phá được bất biến scale, nên sai nó
    # làm hỏng TOÀN BỘ các chỉ tiêu cùng lúc chứ không hỏng lẻ tẻ — tách ra
    # đếm riêng, đừng để nó lẫn vào tỷ lệ trường đúng.
    diem["he_so_don_vi_that"] = gold["unit_multiplier"]
    diem["he_so_don_vi_da_dung"] = ket_qua.meta.get("don_vi_tinh_he_so")
    diem["don_vi_tinh_raw"] = ket_qua.meta.get("don_vi_tinh_raw")
    diem["so_canh_bao"] = len(ket_qua.warnings)
    diem["gia_tri_du_doan"] = du_doan
    return diem


def gop(cac_diem: list[dict]) -> dict:
    """Gộp tử và mẫu qua các tài liệu — KHÔNG lấy trung bình của các tỷ lệ."""
    dung = sum(d["do_chinh_xac"]["dung"] for d in cac_diem)
    tong = sum(d["do_chinh_xac"]["tong"] for d in cac_diem)
    sai_cam = sum(d["loi_cam"]["sai"] for d in cac_diem)
    co_gia_tri = sum(d["loi_cam"]["co_gia_tri"] for d in cac_diem)

    return {
        "so_tai_lieu": len(cac_diem),
        "truong_dung": dung,
        "truong_tong": tong,
        "do_chinh_xac_truong": dung / tong if tong else 0.0,
        "loi_cam_sai": sai_cam,
        "loi_cam_co_gia_tri": co_gia_tri,
        "ty_le_loi_cam": sai_cam / co_gia_tri if co_gia_tri else 0.0,
        "tai_lieu_dung_tron_ven": sum(1 for d in cac_diem if d["dung_tron_ven"]),
        "chuan_dung": sum(1 for d in cac_diem if d["chuan_da_dung"] == d["chuan_that"]),
        "don_vi_dung": sum(
            1 for d in cac_diem if d["he_so_don_vi_da_dung"] == d["he_so_don_vi_that"]
        ),
    }


def in_bang(cac_diem: list[dict], tong_hop: dict, hong: list[tuple[str, str]]) -> None:
    """
    In số GỘP theo tài liệu, KHÔNG in giá trị từng ô.

    Xem cảnh báo về Luật 1 ở đầu file: giá trị từng ô nằm trong file JSON,
    và người sẽ gán nhãn lại tập này không nên đọc chúng.
    """
    print(f"{'doc_id':24s} {'đúng':>9s} {'lỗi câm':>8s} {'chuẩn':>7s} {'đơn vị':>7s}")
    for d in sorted(cac_diem, key=lambda x: -x["do_chinh_xac"]["ty_le"]):
        dcx = d["do_chinh_xac"]
        print(
            f"{d['doc_id']:24s} {dcx['dung']:4d}/{dcx['tong']:<4d} "
            f"{d['loi_cam']['ty_le']:8.3f} "
            f"{'✓' if d['chuan_da_dung'] == d['chuan_that'] else '✗':>7s} "
            f"{'✓' if d['he_so_don_vi_da_dung'] == d['he_so_don_vi_that'] else '✗':>7s}"
        )

    n = tong_hop["so_tai_lieu"]
    print(
        f"\nGỘP trên {n} tài liệu\n"
        f"  Độ chính xác mức trường : {tong_hop['do_chinh_xac_truong']:.3f} "
        f"({tong_hop['truong_dung']}/{tong_hop['truong_tong']})\n"
        f"  Tỷ lệ lỗi câm           : {tong_hop['ty_le_loi_cam']:.3f} "
        f"({tong_hop['loi_cam_sai']}/{tong_hop['loi_cam_co_gia_tri']} ô có giá trị)\n"
        f"  Tài liệu đúng trọn vẹn  : {tong_hop['tai_lieu_dung_tron_ven']}/{n}\n"
        f"  Nhận diện chuẩn đúng    : {tong_hop['chuan_dung']}/{n}\n"
        f"  Hệ số đơn vị đúng       : {tong_hop['don_vi_dung']}/{n}"
    )

    if hong:
        # In riêng thay vì chỉ đếm: một tài liệu nổ giữa chừng làm mẫu số
        # nhỏ đi mà bảng vẫn trông đầy đủ, và đó đúng là cách một phép đo
        # tự tốt lên mà không ai thấy.
        print("\nKHÔNG CHẠY ĐƯỢC — mẫu số đã trừ những tài liệu này:")
        for doc_id, ly_do in hong:
            print(f"  {doc_id}: {ly_do}")


def main() -> int:
    bo_doc = argparse.ArgumentParser(description=__doc__)
    bo_doc.add_argument(
        "--chuan-tu-gold",
        action="store_true",
        help="lấy chuẩn mẫu biểu từ nhãn (điều kiện oracle) thay vì để pipeline tự xoay xở",
    )
    bo_doc.add_argument("--chi", nargs="*", help="chỉ chạy vài mã, vd --chi HPG BMP")
    bo_doc.add_argument("--thu-muc-pdf", type=Path, default=THU_MUC_PDF)
    tham_so = bo_doc.parse_args()

    cac_gold = sorted(THU_MUC_GOLD.glob("*.json"))
    if tham_so.chi:
        can = {m.upper() for m in tham_so.chi}
        cac_gold = [g for g in cac_gold if g.stem.split("_")[0].upper() in can]

    cac_diem: list[dict] = []
    hong: list[tuple[str, str]] = []
    thieu_pdf: list[str] = []

    for i, duong_dan_gold in enumerate(cac_gold, 1):
        gold = doc_gold(duong_dan_gold)
        pdf = tham_so.thu_muc_pdf / f"{gold['doc_id']}.pdf"
        if not pdf.exists():
            thieu_pdf.append(gold["doc_id"])
            continue

        print(f"[{i:2d}/{len(cac_gold)}] {gold['doc_id']} …", file=sys.stderr, flush=True)
        try:
            cac_diem.append(chay_mot_tai_lieu(gold, pdf, tham_so.chuan_tu_gold))
        except Exception as loi:  # noqa: BLE001
            # Bắt rộng có chủ đích: một tài liệu nổ không được phép giết cả
            # lượt chạy vốn tốn tiền gọi API cho những tài liệu đã xong.
            hong.append((gold["doc_id"], f"{type(loi).__name__}: {loi}"))
            traceback.print_exc(file=sys.stderr)

    if not cac_diem:
        print("Không tài liệu nào chạy được.", file=sys.stderr)
        if thieu_pdf:
            print(f"Chưa tải PDF: {', '.join(thieu_pdf)}", file=sys.stderr)
        return 1

    tong_hop = gop(cac_diem)
    che_do = "chuan_tu_gold" if tham_so.chuan_tu_gold else "dau_cuoi"

    # Ghi TRƯỚC khi in: lượt chạy này tốn tiền gọi API, nên một lỗi định
    # dạng ở hàm in không được phép làm mất kết quả.
    THU_MUC_RA.mkdir(parents=True, exist_ok=True)
    duong_dan_ra = THU_MUC_RA / f"tap_gold_{che_do}.json"
    duong_dan_ra.write_text(
        json.dumps(
            {
                "che_do": che_do,
                "tong_hop": tong_hop,
                "tung_tai_lieu": cac_diem,
                "khong_chay_duoc": hong,
                "thieu_pdf": thieu_pdf,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Chế độ: {che_do}\n")
    in_bang(cac_diem, tong_hop, hong)
    if thieu_pdf:
        print(f"\nChưa tải PDF, đã bỏ qua: {', '.join(thieu_pdf)}")
    print(f"\nKết quả đầy đủ: {duong_dan_ra}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
