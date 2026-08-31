"""
Đo phạm vi của luật dấu trên tập gold — CHẠY LẠI TRÊN KẾT QUẢ ĐÃ LƯU.

Không tốn một lệnh gọi API nào: nó đọc `gia_tri_du_doan` trong file kết quả
của lượt chấm gold rồi so với nhãn tay. Nhờ vậy phép đo chạy lại được bất cứ
lúc nào, kể cả sau khi đổi luật, mà không phải trả lại ba tiếng rưỡi.

    PYTHONPATH=src python src/eval/do_luat_dau.py

ĐO HAI ĐIỀU KIỆN, và khoảng cách giữa chúng mới là thứ đáng đọc:

  thô               — đúng đầu ra pipeline như đã lưu, tức TRƯỚC bản vá
                      `chuan_hoa_dau()` (`a0cd5ab`). Ở đây còn nguyên 11 lỗi
                      đảo dấu, nên nó đo luật ở chế độ lỗi mà luật sinh ra để
                      bắt.
  sau chuẩn hoá dấu — sau khi `chuan_hoa_dau()` đã lật ba dòng khấu trừ. Đây
                      là hiện trạng thật của pipeline, và con số ở đây mới là
                      con số được phép trích dẫn cho phần đóng góp THÊM của
                      luật. Nó nhỏ hơn hẳn, đúng như phải vậy — hai cơ chế
                      chồng lên nhau ở cùng một chế độ lỗi.

CÁCH CHẤM, và vì sao nó khắt khe hơn "luật có ra tay không". Một lần ra tay
chỉ được tính là ĐÚNG khi chỉ tiêu luật gọi tên thật sự lộn dấu so với nhãn
tay, tức `dự đoán == −gold` và `gold != 0`. Ra tay trúng một chỉ tiêu sai vì
lý do KHÁC vẫn bị tính là BÁO NHẦM: luật này bán mệnh đề "tôi chứng minh được
đây là lỗi dấu", nên trúng vì may không phải là trúng.
"""

import json
import sys
from collections import Counter
from pathlib import Path

# Chạy bằng `python src/eval/do_luat_dau.py` thì Python đặt src/eval/ lên đầu
# sys.path, và thư mục đó có `metrics.py` che mất `src/metrics.py`. Gỡ nó ra
# trước khi import bất cứ thứ gì — cùng cái bẫy đã cắn ở moc3.py và
# chay_tap_gold.py, xem HANDOFF.md mục 5.7.
_THU_MUC_SCRIPT = str(Path(__file__).resolve().parent)
if sys.path and sys.path[0] == _THU_MUC_SCRIPT:
    sys.path.pop(0)

from constraints import build_matrix  # noqa: E402
from fields_config import Standard, chuan_hoa_dau, identities_for  # noqa: E402
from repair.candidates import generate as sinh_ung_vien  # noqa: E402
from repair.diagnose import diagnose  # noqa: E402
from repair.luat_dau import luat_dau_residual  # noqa: E402

KET_QUA_GOLD = Path("data/output/tap_gold_chuan_tu_gold.json")
THU_MUC_GOLD = Path("data/gold")
BAO_CAO = Path("data/output/luat_dau_tap_gold.md")


def _loi_dau_that(du_doan: dict, gold: dict) -> set[str]:
    """
    Tập chỉ tiêu thật sự bị lộn dấu: `dự đoán == −gold`, và gold khác 0.

    Loại gold bằng 0 ra vì `−0 == 0`, nên mọi ô gold bằng 0 mà dự đoán cũng
    bằng 0 sẽ tự khai là "lỗi dấu" và làm mẫu số phồng lên bằng những ca
    không có lỗi nào.
    """
    return {
        khoa
        for khoa, gt in gold.items()
        if gt not in (None, 0)
        and du_doan.get(khoa) is not None
        and du_doan[khoa] == -gt
    }


def _truong_sai(du_doan: dict, gold: dict) -> set[str]:
    return {
        khoa
        for khoa, gt in gold.items()
        if du_doan.get(khoa) is not None and du_doan[khoa] != gt
    }


def _chay_mot_dieu_kien(du_doan: dict, gold: dict, standard: Standard) -> dict:
    """Chạy luật trên một bộ giá trị và chấm nó với nhãn tay."""
    # Chỉ dựng ma trận trên các chỉ tiêu ĐỌC ĐƯỢC. build_matrix() tự bỏ đẳng
    # thức nào có thành phần nằm ngoài danh sách — coi chỉ tiêu thiếu như 0 sẽ
    # dựng ra ràng buộc sai và báo cáo lạc quan hơn sự thật.
    co_gia_tri = [k for k, v in du_doan.items() if v is not None]
    A, field_order = build_matrix(co_gia_tri, identities_for(standard))

    if A.shape[0] == 0:
        return {"trang_thai": "khong_co_dang_thuc", "phan_xu": "khong_do_duoc"}

    kq = luat_dau_residual({k: du_doan[k] for k in field_order}, A, field_order)
    loi_dau = _loi_dau_that(du_doan, gold)

    if kq.trang_thai == "dinh_vi_duoc":
        phan_xu = "dinh_vi_dung" if kq.truong in loi_dau else "bao_nham"
    elif kq.trang_thai in ("nghi_ngo", "mo_ho"):
        # Ra tay mà không chỉ đúng một tên thì chỉ tính là ĐÚNG khi MỌI ứng
        # viên nó nêu đều là lỗi dấu thật. Nêu kèm một tên sai là đã dẫn người
        # đọc đi nhầm chỗ, dù phần còn lại đúng.
        đủ = bool(kq.cac_ung_vien) and set(kq.cac_ung_vien) <= loi_dau
        phan_xu = "chi_dung_ten" if đủ else "bao_nham"
    else:
        phan_xu = "im_lang_dung" if not loi_dau else "bo_sot"

    return {
        "trang_thai": kq.trang_thai,
        "phan_xu": phan_xu,
        "ung_vien": kq.cac_ung_vien,
        "so_loi_dau_that": len(loi_dau),
        "so_truong_sai": len(_truong_sai(du_doan, gold)),
        "so_dang_thuc": int(A.shape[0]),
        "so_dang_thuc_con_lech": kq.so_dang_thuc_con_lech,
    }


def _cham(du_doan: dict, gold: dict) -> tuple[int, int, int, int]:
    """
    (đúng, tổng, lỗi câm, ô có giá trị) cho MỘT tài liệu.

    Gộp tử và mẫu qua các tài liệu chứ không lấy trung bình của các tỷ lệ —
    TT200 có 26 chỉ tiêu còn TT99 có 27 nên hai cách cho hai con số khác nhau.
    Cùng quy ước với `chay_tap_gold.py`, nếu không thì hai bảng không so được.
    """
    dung = cam_sai = co_gia_tri = 0
    for khoa, gt in gold.items():
        p = du_doan.get(khoa)
        if p == gt:
            dung += 1
        if p is not None:
            co_gia_tri += 1
            if p != gt:
                cam_sai += 1
    return dung, len(gold), cam_sai, co_gia_tri


def _ap_tang_repair(du_doan: dict, standard: Standard) -> tuple[dict, list[str]]:
    """
    Chạy trọn tầng repair trên một bộ giá trị, trả (giá trị sau, chỉ tiêu đã đổi).

    Dựng ứng viên KHÔNG có `o_lan_can`, đúng như đường chạy thật hiện nay: đường
    VLM không sinh ra các ô số đã OCR trong vùng bảng. Cho nguồn đó chạy ở đây
    mà không chạy ở pipeline sẽ cho ra một con số không ai tái lập được.
    """
    co_gia_tri = [k for k, v in du_doan.items() if v is not None]
    A, field_order = build_matrix(co_gia_tri, identities_for(standard))
    if A.shape[0] == 0:
        return dict(du_doan), []

    gia_tri = {k: du_doan[k] for k in field_order}
    ung_vien = {k: sinh_ung_vien(k, gia_tri[k]) for k in field_order}
    do = diagnose(gia_tri, ung_vien, A, field_order)

    if do.verdict != "REPAIRED":
        return dict(du_doan), []

    sau = dict(du_doan)
    for ten, uv in do.changed_fields.items():
        sau[ten] = uv.value
    return sau, sorted(do.changed_fields)


def chay() -> dict:
    ket_qua = json.loads(KET_QUA_GOLD.read_text(encoding="utf-8"))
    dong = []

    for muc in ket_qua["tung_tai_lieu"]:
        doc_id = muc["doc_id"]
        gold = json.loads(
            (THU_MUC_GOLD / f"{doc_id}.json").read_text(encoding="utf-8")
        )["values"]
        du_doan = muc["gia_tri_du_doan"]
        standard = Standard(muc["chuan_that"])

        # chuan_hoa_dau() trả (giá trị, danh sách khoá đã lật) — chỉ cần cái đầu.
        da_chuan_hoa, _ = chuan_hoa_dau(dict(du_doan), standard)
        sau_repair, da_doi = _ap_tang_repair(da_chuan_hoa, standard)

        dong.append(
            {
                "doc_id": doc_id,
                "tho": _chay_mot_dieu_kien(du_doan, gold, standard),
                "sau_chuan_hoa": _chay_mot_dieu_kien(da_chuan_hoa, gold, standard),
                "repair_da_doi": da_doi,
                "cham": {
                    "tho": _cham(du_doan, gold),
                    "sau_chuan_hoa": _cham(da_chuan_hoa, gold),
                    "sau_repair": _cham(sau_repair, gold),
                },
            }
        )

    return {"tung_tai_lieu": dong}


def bao_cao(kq: dict) -> str:
    d = ["# Luật dấu trên tập gold — đo lại trên kết quả đã lưu", ""]
    d.append("Sinh bằng `PYTHONPATH=src python src/eval/do_luat_dau.py`.")
    d.append("Không gọi API; đọc `tap_gold_chuan_tu_gold.json` rồi so với `data/gold/`.")
    d.append("")

    for nhan, khoa in (
        ("Điều kiện A — đầu ra thô, TRƯỚC bản vá `chuan_hoa_dau()`", "tho"),
        ("Điều kiện B — SAU `chuan_hoa_dau()`, tức hiện trạng pipeline", "sau_chuan_hoa"),
    ):
        d += [f"## {nhan}", ""]
        d.append(
            "| doc_id | Đẳng thức | Trường sai | Lỗi dấu thật "
            "| Trạng thái luật | Phán xử | Ứng viên |"
        )
        d.append("|---|---:|---:|---:|---|---|---|")
        for m in kq["tung_tai_lieu"]:
            r = m[khoa]
            d.append(
                f"| `{m['doc_id']}` | {r.get('so_dang_thuc', 0)} "
                f"| {r.get('so_truong_sai', 0)} | {r.get('so_loi_dau_that', 0)} "
                f"| `{r['trang_thai']}` | **{r['phan_xu']}** "
                f"| {', '.join(r.get('ung_vien') or []) or '—'} |"
            )
        dem = Counter(m[khoa]["phan_xu"] for m in kq["tung_tai_lieu"])
        d += ["", "| Phán xử | Số tài liệu |", "|---|---:|"]
        for ten, so in sorted(dem.items(), key=lambda kv: -kv[1]):
            d.append(f"| `{ten}` | {so} |")
        d.append("")
        d.append(f"**Báo nhầm: {dem.get('bao_nham', 0)} / {len(kq['tung_tai_lieu'])}**")
        d.append("")

    d += ["## Hiệu quả trên chỉ số của dự án", ""]
    d.append("| Điều kiện | Trường đúng | Lỗi câm |")
    d.append("|---|---:|---:|")
    for nhan, khoa in (
        ("Thô — như pipeline đã ghi ra", "tho"),
        ("Sau `chuan_hoa_dau()` (`a0cd5ab`)", "sau_chuan_hoa"),
        ("Sau `chuan_hoa_dau()` + **tầng repair**", "sau_repair"),
    ):
        dung = sum(m["cham"][khoa][0] for m in kq["tung_tai_lieu"])
        tong = sum(m["cham"][khoa][1] for m in kq["tung_tai_lieu"])
        cam = sum(m["cham"][khoa][2] for m in kq["tung_tai_lieu"])
        co = sum(m["cham"][khoa][3] for m in kq["tung_tai_lieu"])
        d.append(
            f"| {nhan} | {dung}/{tong} = **{dung / tong:.1%}** "
            f"| {cam}/{co} = **{cam / co:.1%}** |"
        )

    doi = {
        m["doc_id"]: m["repair_da_doi"]
        for m in kq["tung_tai_lieu"]
        if m["repair_da_doi"]
    }
    d += [
        "",
        f"Tầng repair đổi **{sum(len(v) for v in doi.values())} ô** trên "
        f"{len(kq['tung_tai_lieu'])} tài liệu:",
    ]
    for doc_id, cac in doi.items():
        d.append(f"- `{doc_id}` — {', '.join(cac)}")
    d += [
        "",
        "Đọc con số này cho đúng: phần đóng góp THÊM của tầng repair mỏng, vì "
        "`chuan_hoa_dau()` đã lấy hết phần dễ ở cùng chế độ lỗi. Giá trị của "
        "luật không nằm ở số ô nó sửa mà ở chỗ nó **chứng minh được** — và ở "
        "chỗ nó phân xử Câu 13 bằng số liệu thay vì bằng tranh luận câu chữ: "
        "cả hai lần ra tay đều rơi đúng vào `thue_tndn_hoan_lai`, chỉ tiêu mà "
        "guideline cũ bắt ghi dương.",
        "",
    ]

    return "\n".join(d)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    kq = chay()
    van_ban = bao_cao(kq)
    BAO_CAO.parent.mkdir(parents=True, exist_ok=True)
    BAO_CAO.write_text(van_ban, encoding="utf-8")
    print(van_ban)
    print(f"\nĐã ghi {BAO_CAO}")
