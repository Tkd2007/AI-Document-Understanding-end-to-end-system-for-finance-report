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

Kết quả ghi ra `data/output/tap_gold_<chế độ>.json` sau MỖI tài liệu, không
đợi tới cuối. Bản đầu chỉ ghi một lần ở cuối — bài học của lượt Mốc 3 ngày
25/08 mới được áp một nửa, và nửa còn thiếu đã trả giá ngay: lượt chạy đêm
26/08 chết lúc đang ở tài liệu 7/11, và **sáu tài liệu đã chấm xong biến mất
sạch** cùng với ba tiếng gọi API. Ghi ở cuối chỉ chống được lỗi định dạng
trong hàm in; nó không chống được tiến trình bị giết.

`--tiep-tuc` đọc file kết quả cũ và BỎ QUA những tài liệu đã có trong đó, nên
một lượt chạy đứt gánh nối lại được mà không trả tiền API hai lần.

CẢNH BÁO VỀ LUẬT 1, và một cái bẫy đã bắt được. Guideline mục 1 buộc người
gán nhãn phải MÙ với đầu ra pipeline. Tập gold hiện có 11 tài liệu và phương
án đo đồng thuận dự phòng là chính người ấy gán nhãn lại sau ít nhất hai
tuần. Nếu người sẽ gán nhãn lại đọc giá trị pipeline đoán cho từng ô của
những tài liệu này, lượt gán nhãn lại bị neo và phép đo đồng thuận mất giá
trị.

Bảng của script này cố ý chỉ có số GỘP theo tài liệu — nhưng chừng đó KHÔNG
đủ, và bản đầu đã hụt đúng chỗ đó. `route_document` tự in ra **stdout** một
bản kết xuất giá trị TỪNG Ô cho từng trang, nên `> file.txt` gom cả chúng lẫn
bảng sạch vào cùng một file: lượt chạy đầu tiên có 79 khối "Page N" như thế
nằm ngay phía trên bảng. Vì thế script nay CHẶN stdout của pipeline lại và đổ
vào `data/output/tap_gold_<chế độ>_pipeline.log`; chỉ bảng gộp mới ra stdout.

Hai file có giá trị từng ô là `..._pipeline.log` và file JSON kết quả. Cả hai
tồn tại cho lượt phân tích về sau, KHÔNG phải để người gán nhãn đọc.

Chạy:
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --chuan-tu-gold
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python src/eval/chay_tap_gold.py --chi HPG BMP
"""

import argparse
import contextlib
import json
import sys
import traceback
from pathlib import Path

# Chạy như script thì thư mục src/eval/ nằm đầu sys.path và eval/metrics.py
# che mất src/metrics.py của pipeline. Cùng họ với vụ src/types.py — xem
# HANDOFF.md mục 5.7. Gỡ thư mục script ra trước khi import bất cứ thứ gì.
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


def chay_mot_tai_lieu(gold: dict, pdf: Path, chuan_tu_gold: bool, nhat_ky) -> dict:
    chuan = Standard(gold["standard"]) if chuan_tu_gold else None

    # Chặn stdout của pipeline: nó in giá trị từng ô cho từng trang, và để
    # chúng lẫn vào stdout là làm hỏng đúng thứ mà bảng gộp cố giữ. Xem cảnh
    # báo về Luật 1 ở đầu file.
    with contextlib.redirect_stdout(nhat_ky):
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
    #
    # `he_so_don_vi_da_dung` là kết luận MỨC TÀI LIỆU, và từ khi đơn vị được
    # buộc theo bảng thì nó là hệ số áp cho ĐA SỐ chỉ tiêu chứ không còn là
    # hệ số đọc được đầu tiên (xem `extract_vlm._don_vi_tai_lieu`). Định
    # nghĩa phải đổi vì gold chỉ có một `unit_multiplier` cho mỗi tài liệu,
    # trong khi tài liệu thật có thể trộn hai đơn vị — so một tài liệu trộn
    # đơn vị với một con số duy nhất thì "đúng/sai" chỉ có nghĩa theo đa số.
    diem["he_so_don_vi_that"] = gold["unit_multiplier"]
    diem["he_so_don_vi_da_dung"] = ket_qua.meta.get("don_vi_tinh_he_so")
    diem["don_vi_tinh_raw"] = ket_qua.meta.get("don_vi_tinh_raw")
    # Certificate của cơ chế buộc đơn vị theo bảng, giữ CÙNG điểm số. Không có
    # nó thì một lượt chạy đúng đơn vị và một lượt chạy sai đơn vị nhưng được
    # kế thừa cứu trông giống hệt nhau trong bảng kết quả — đúng bài học của
    # mục 20.7 HANDOFF về lượt chạy 30/08.
    diem["he_so_don_vi_theo_truong"] = ket_qua.meta.get("he_so_don_vi_theo_truong")
    diem["don_vi_theo_vung"] = ket_qua.meta.get("don_vi_theo_vung")
    diem["so_canh_bao"] = len(ket_qua.warnings)
    # Certificate của tầng repair và kết luận lan ký hiệu mẫu đi CÙNG điểm số.
    # Bản trước chỉ giữ phần chấm điểm, nên một lượt chạy bật tầng repair không
    # để lại dấu vết nào về việc tầng ấy đã làm gì: không biết nguồn ô lân cận
    # có bật không, neo được bao nhiêu chỉ tiêu, hay verdict là gì. Bảng số khi
    # đó nói được kết quả nhưng không nói được vì sao — mà lượt chạy bật repair
    # sinh ra chính là để trả lời câu "vì sao".
    diem["chung_chi_repair"] = ket_qua.meta.get("chung_chi_repair")
    diem["ky_hieu_mau"] = ket_qua.meta.get("ky_hieu_mau")
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


def ghi_ket_qua(duong_dan, che_do, cac_diem, hong, thieu_pdf) -> None:
    """
    Ghi đè file kết quả bằng mọi thứ đã chấm tới lúc này.

    Gọi sau MỖI tài liệu chứ không chỉ ở cuối. Ghi đè trọn file thay vì nối
    thêm vì file nhỏ — vài chục KB — nên cái giá bằng không, còn đổi lại thì
    file luôn là JSON hợp lệ đọc được ngay cả khi tiến trình bị giết ở đúng
    tài liệu kế tiếp.
    """
    duong_dan.write_text(
        json.dumps(
            {
                "che_do": che_do,
                "tong_hop": gop(cac_diem) if cac_diem else {},
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


def main() -> int:
    bo_doc = argparse.ArgumentParser(description=__doc__)
    bo_doc.add_argument(
        "--chuan-tu-gold",
        action="store_true",
        help="lấy chuẩn mẫu biểu từ nhãn (điều kiện oracle) thay vì để pipeline tự xoay xở",
    )
    bo_doc.add_argument("--chi", nargs="*", help="chỉ chạy vài mã, vd --chi HPG BMP")
    bo_doc.add_argument(
        "--tiep-tuc",
        action="store_true",
        help="bỏ qua tài liệu đã có trong file kết quả cũ, chạy nốt phần còn lại",
    )
    bo_doc.add_argument("--thu-muc-pdf", type=Path, default=THU_MUC_PDF)
    tham_so = bo_doc.parse_args()

    cac_gold = sorted(THU_MUC_GOLD.glob("*.json"))
    if tham_so.chi:
        can = {m.upper() for m in tham_so.chi}
        cac_gold = [g for g in cac_gold if g.stem.split("_")[0].upper() in can]

    che_do = "chuan_tu_gold" if tham_so.chuan_tu_gold else "dau_cuoi"
    THU_MUC_RA.mkdir(parents=True, exist_ok=True)
    duong_dan_ra = THU_MUC_RA / f"tap_gold_{che_do}.json"
    duong_dan_nhat_ky = THU_MUC_RA / f"tap_gold_{che_do}_pipeline.log"

    cac_diem: list[dict] = []
    hong: list[tuple[str, str]] = []
    thieu_pdf: list[str] = []
    da_co: set[str] = set()

    if tham_so.tiep_tuc and duong_dan_ra.exists():
        cu = json.loads(duong_dan_ra.read_text(encoding="utf-8"))
        cac_diem = cu.get("tung_tai_lieu", [])
        hong = [tuple(h) for h in cu.get("khong_chay_duoc", [])]
        da_co = {d["doc_id"] for d in cac_diem}
        print(f"Nối tiếp: đã có {len(da_co)} tài liệu trong {duong_dan_ra}", file=sys.stderr)

    # Nhật ký mở ở chế độ nối thêm khi tiếp tục, để kết xuất của lượt trước
    # không bị xoá mất — nó là thứ duy nhất tra cứu được khi một tài liệu ra
    # số lạ.
    nhat_ky = duong_dan_nhat_ky.open("a" if tham_so.tiep_tuc else "w", encoding="utf-8")

    for i, duong_dan_gold in enumerate(cac_gold, 1):
        gold = doc_gold(duong_dan_gold)
        pdf = tham_so.thu_muc_pdf / f"{gold['doc_id']}.pdf"
        if not pdf.exists():
            thieu_pdf.append(gold["doc_id"])
            continue

        if gold["doc_id"] in da_co:
            print(f"[{i:2d}/{len(cac_gold)}] {gold['doc_id']} — đã có, bỏ qua", file=sys.stderr)
            continue

        print(f"[{i:2d}/{len(cac_gold)}] {gold['doc_id']} …", file=sys.stderr, flush=True)
        try:
            cac_diem.append(chay_mot_tai_lieu(gold, pdf, tham_so.chuan_tu_gold, nhat_ky))
        except Exception as loi:  # noqa: BLE001
            # Bắt rộng có chủ đích: một tài liệu nổ không được phép giết cả
            # lượt chạy vốn tốn tiền gọi API cho những tài liệu đã xong.
            hong.append((gold["doc_id"], f"{type(loi).__name__}: {loi}"))
            traceback.print_exc(file=sys.stderr)

        # Ghi NGAY sau mỗi tài liệu. Xem đầu file: ghi một lần ở cuối đã làm
        # mất sáu tài liệu khi tiến trình bị giết giữa chừng.
        ghi_ket_qua(duong_dan_ra, che_do, cac_diem, hong, thieu_pdf)
        nhat_ky.flush()

    nhat_ky.close()

    if not cac_diem:
        print("Không tài liệu nào chạy được.", file=sys.stderr)
        if thieu_pdf:
            print(f"Chưa tải PDF: {', '.join(thieu_pdf)}", file=sys.stderr)
        return 1

    tong_hop = gop(cac_diem)
    ghi_ket_qua(duong_dan_ra, che_do, cac_diem, hong, thieu_pdf)

    print(f"Chế độ: {che_do}\n")
    in_bang(cac_diem, tong_hop, hong)
    if thieu_pdf:
        print(f"\nChưa tải PDF, đã bỏ qua: {', '.join(thieu_pdf)}")
    print(
        f"\nKết quả đầy đủ: {duong_dan_ra}\n"
        f"Kết xuất thô của pipeline (CÓ giá trị từng ô — xem cảnh báo Luật 1 "
        f"ở đầu file này): {duong_dan_nhat_ky}"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
