"""
Chấm HAI PHE của H3 trên tập gold, trong MỘT lượt trích xuất.

VÌ SAO MỘT LƯỢT LÀ ĐÚNG CHỨ KHÔNG PHẢI TIẾT KIỆM. `PREREGISTRATION.md` mục 2
đòi hai phe xuất phát từ cùng một bộ số: khác đúng một biến số là ứng viên
đến từ đâu. Chạy hai lượt riêng thì đầu vào của chúng đã khác nhau trước khi
so — nhánh VLM có tính ngẫu nhiên và hàng đợi tầng `:free` làm số lần gọi
đổi hẳn giữa hai lượt, đo được trên `BKG_2026Q2_TT99` ngày 03–04/09/2026: 42
lần gọi ở lượt này, 15 lần ở lượt kia, kết quả khác nhau. Chạy chung một lượt
thì hai phe nhận đúng cùng một `data`, và hiệu số giữa chúng đo đúng cái cần
đo.

BA CỘT ĐI RA, và phải giữ cả ba:

    tho        đầu ra tầng 1, chưa phe nào đụng vào — mốc "trước"
    de_xuat    sau `chay_tang_repair()`, ứng viên sinh từ TÀI LIỆU
    baseline9  sau `diagnose_fellegi_holt_donor()`, ứng viên từ DONOR

Bỏ cột `tho` đi thì không biết phe nào cải thiện được bao nhiêu; bỏ một
trong hai phe thì không có phép so.

HAI CHIỀU ĐỀU PHẢI BÁO CÁO, `PREREGISTRATION.md` H3 chốt trước:

  * chính     — tỷ lệ lỗi câm, kỳ vọng GIẢM
  * chống bịa — số ô ĐANG ĐÚNG mà bị sửa thành SAI, kỳ vọng KHÔNG TĂNG

Thắng chiều một mà thua chiều hai là **kết quả tiêu cực** và phải nói ra.
Script này đếm cả hai cho từng phe, không để người đọc tự suy.

Chạy:
    PYTHONIOENCODING=utf-8 PYTHONPATH=src BAT_TANG_REPAIR=true \\
        python src/eval/chay_hai_phe.py --so-luong 10 --bien-the ty_trong
"""

import argparse
import contextlib
import json
import sys
import traceback
from pathlib import Path

if __name__ == "__main__":
    _thu_muc_script = str(Path(__file__).resolve().parent)
    sys.path[:] = [p for p in sys.path if Path(p).resolve() != Path(_thu_muc_script)]

from eval.donor import BIEN_THE, bang_donor, do_ro_ri, doc_tap_gold  # noqa: E402
from eval.metrics import field_accuracy, khop_so, silent_error_rate  # noqa: E402
from fields_config import Standard  # noqa: E402
from router import BAT_TANG_REPAIR, route_document  # noqa: E402

THU_MUC_GOLD = Path("data/gold")
THU_MUC_PDF = Path("data/bctc")
THU_MUC_RA = Path("data/output")

for _luong in (sys.stdout, sys.stderr):
    if hasattr(_luong, "reconfigure"):
        _luong.reconfigure(encoding="utf-8", errors="replace")


def dem_bia(truoc: dict, sau: dict, that: dict) -> int:
    """
    Số ô ĐANG ĐÚNG bị một phe sửa thành SAI — chỉ số CHỐNG BỊA của H3.

    Đếm ở mức ô chứ không ở mức tài liệu: một phe sửa hỏng hai ô và một phe
    sửa hỏng một ô là hai chuyện khác nhau, mà đếm theo tài liệu thì cả hai
    ra cùng con số 1.
    """
    hong = 0
    for khoa, gt_that in that.items():
        if gt_that is None:
            continue
        dung_truoc = truoc.get(khoa) is not None and khop_so(truoc[khoa], gt_that)
        dung_sau = sau.get(khoa) is not None and khop_so(sau[khoa], gt_that)
        hong += dung_truoc and not dung_sau
    return hong


def cham_mot_cot(gia_tri: dict, that: dict) -> dict:
    return {
        "do_chinh_xac": field_accuracy(gia_tri, that),
        "loi_cam": silent_error_rate(gia_tri, that),
    }


def chay_mot_tai_lieu(gold: dict, pdf: Path, donor: dict, nhat_ky) -> dict:
    with contextlib.redirect_stdout(nhat_ky):
        ket_qua = route_document(
            str(pdf), save=False, standard=Standard(gold["standard"]),
            donor_values=donor,
        )

    that = gold["values"]
    # `values()` là bộ số SAU khi phe đề xuất đã chạy — đó là cột `de_xuat`.
    de_xuat = ket_qua.values()
    baseline9 = ket_qua.meta.get("gia_tri_baseline9")
    cc_dx = ket_qua.meta.get("chung_chi_repair") or {}
    cc_b9 = ket_qua.meta.get("chung_chi_baseline9") or {}

    # Cột `tho` dựng ngược từ `de_xuat` bằng cách hoàn tác đúng những ô phe
    # đề xuất đã đổi. Làm vậy thay vì chạy lại pipeline lần hai: chạy lại là
    # trả tiền API hai lần VÀ nhận một bộ số khác vì VLM ngẫu nhiên.
    tho = dict(de_xuat)
    for khoa, doi in (cc_dx.get("da_doi") or {}).items():
        tho[khoa] = doi["truoc"]

    diem = {
        "doc_id": gold["doc_id"],
        "quy_uoc_dau": ket_qua.meta.get("quy_uoc_dau"),
        "nguon_quy_uoc_dau": ket_qua.meta.get("nguon_quy_uoc_dau"),
        "chung_chi_de_xuat": cc_dx,
        "chung_chi_baseline9": cc_b9,
        "so_o_co_donor": cc_b9.get("so_o_co_donor"),
        "tho": cham_mot_cot(tho, that),
        "de_xuat": cham_mot_cot(de_xuat, that),
        "bia_de_xuat": dem_bia(tho, de_xuat, that),
    }
    if baseline9 is not None:
        diem["baseline9"] = cham_mot_cot(baseline9, that)
        diem["bia_baseline9"] = dem_bia(tho, baseline9, that)
    return diem


def gop(cac_diem: list, cot: str) -> dict:
    dung = tong = sai = co_gt = 0
    for d in cac_diem:
        if cot not in d:
            continue
        dung += d[cot]["do_chinh_xac"]["dung"]
        tong += d[cot]["do_chinh_xac"]["tong"]
        sai += d[cot]["loi_cam"]["sai"]
        co_gt += d[cot]["loi_cam"]["co_gia_tri"]
    return {
        "truong_dung": dung, "truong_tong": tong,
        "do_chinh_xac": dung / tong if tong else 0.0,
        "loi_cam_sai": sai, "loi_cam_co_gia_tri": co_gt,
        "ty_le_loi_cam": sai / co_gt if co_gt else 0.0,
    }


def main() -> None:
    bo = argparse.ArgumentParser(description=__doc__)
    bo.add_argument("--so-luong", type=int, default=10,
                    help="số tài liệu chấm; trung vị donor VẪN lấy trên trọn tập gold")
    bo.add_argument("--bien-the", choices=BIEN_THE, default="ty_trong")
    bo.add_argument("--chi", nargs="*", help="chỉ chấm các doc_id này")
    tham_so = bo.parse_args()

    if not BAT_TANG_REPAIR:
        print("BAT_TANG_REPAIR chưa bật — không phe nào chạy. Đặt BAT_TANG_REPAIR=true.",
              file=sys.stderr)
        raise SystemExit(1)

    tap_gold = doc_tap_gold(THU_MUC_GOLD)
    ro_ri = do_ro_ri(tap_gold, tham_so.bien_the)
    print(f"Donor `{tham_so.bien_the}` — kiểm chống oracle: "
          f"{ro_ri['ty_le_lech_duoi_1_phan_tram']:.2%} số ô lệch dưới 1% so với nhãn, "
          f"{ro_ri['ty_le_lech_duoi_10_phan_tram']:.2%} lệch dưới 10%.", file=sys.stderr)

    chon = tap_gold if not tham_so.chi else [g for g in tap_gold if g["doc_id"] in tham_so.chi]
    chon = chon[: tham_so.so_luong]

    duong_dan_ra = THU_MUC_RA / f"hai_phe_{tham_so.bien_the}.json"
    nhat_ky = (THU_MUC_RA / f"hai_phe_{tham_so.bien_the}_pipeline.log").open(
        "w", buffering=1, encoding="utf-8")

    cac_diem, hong = [], []
    with nhat_ky:
        for i, gold in enumerate(chon, 1):
            doc_id = gold["doc_id"]
            pdf = THU_MUC_PDF / f"{doc_id}.pdf"
            print(f"[{i:>2}/{len(chon)}] {doc_id} …", file=sys.stderr)
            if not pdf.exists():
                hong.append((doc_id, "thiếu PDF"))
                continue
            try:
                cac_diem.append(chay_mot_tai_lieu(
                    gold, pdf, bang_donor(tap_gold, doc_id, tham_so.bien_the), nhat_ky))
            except Exception:
                hong.append((doc_id, traceback.format_exc(limit=3)))
                continue
            duong_dan_ra.write_text(json.dumps({
                "bien_the_donor": tham_so.bien_the,
                "ro_ri_donor": ro_ri,
                "tung_tai_lieu": cac_diem,
                "khong_chay_duoc": hong,
            }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nĐã chấm {len(cac_diem)}/{len(chon)} | hỏng {len(hong)}")
    print(f"{'cột':<12} {'trường đúng':>20} {'lỗi câm':>20} {'ô bịa':>8}")
    for cot in ("tho", "de_xuat", "baseline9"):
        g = gop(cac_diem, cot)
        if not g["truong_tong"]:
            continue
        bia = "—" if cot == "tho" else sum(d.get(f"bia_{cot}", 0) for d in cac_diem)
        print(f"{cot:<12} {g['truong_dung']:>6}/{g['truong_tong']:<4} = {g['do_chinh_xac']:.4f}"
              f"  {g['loi_cam_sai']:>5}/{g['loi_cam_co_gia_tri']:<4} = {g['ty_le_loi_cam']:.4f}"
              f"  {bia:>8}")


if __name__ == "__main__":
    main()
