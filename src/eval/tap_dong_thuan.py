"""
Ai còn được vào tập gán nhãn đôi, và ai đã mất quyền đó.

Phép đo đồng thuận chỉ có nghĩa khi lượt gán nhãn thứ hai KHÔNG bị neo vào
một con số nào sẵn có. Ở dự án này không có người gán nhãn thứ hai, nên
phương án đang dùng là chính người chủ trì gán nhãn lại sau ít nhất hai
tuần (`ANNOTATION-GUIDELINE.md` mục 5). Điều đó làm mối nguy nặng hơn hẳn
trường hợp hai người: người gán lại chính là người đã chạy pipeline, và
`data/output/tap_gold_*.json` cùng `..._pipeline.log` chứa giá trị máy đoán
cho TỪNG Ô của những tài liệu đã chạy. Chỉ cần mở nhầm một trong hai file là
lượt gán lại bị neo, mà không có cách nào phát hiện ngược từ dữ liệu — con
số đồng thuận vẫn ra, chỉ là nó đo trí nhớ chứ không đo tính nhất quán.

Quyết định ngày 28/08/2026 (Câu 12): **tài liệu đã chạy pipeline bị LOẠI
khỏi tập gán nhãn đôi**, không phải "cố giữ kỷ luật đừng mở file". Module
này là chỗ quyết định đó kiểm chứng được bằng máy thay vì bằng lời hứa.

HAI NGUỒN SỰ THẬT, CỐ Ý KHÔNG GỘP:

  * `data/nguon_gold.json` khoá `gan_nhan_doi` — CAM KẾT của giao thức. Nó
    bền: xoá `data/output/` đi thì việc "người này đã nhìn thấy máy đoán gì"
    vẫn đã xảy ra rồi, không rút lại được.
  * `data/output/` — BẰNG CHỨNG quan sát được lúc này.

`doi_chieu()` so hai nguồn ấy với nhau, và test khoá đúng chiều nguy hiểm:
có bằng chứng mà danh mục chưa đánh dấu. Chiều ngược lại (đánh dấu mà không
còn file) là bình thường và không bị coi là lỗi.

MODULE NÀY KHÔNG ĐƯỢC IMPORT VÀO `src/gan_nhan/`. Nó đọc `data/output/`, mà
công cụ gán nhãn bị cấm chạm vào thư mục đó — `tests/test_gan_nhan_mu_voi_
pipeline.py` cưỡng chế. Nó dành cho người phân tích, chạy trước khi CHỌN tài
liệu cho lượt gán nhãn đôi.

Chạy:
    PYTHONPATH=src python src/eval/tap_dong_thuan.py
"""

import json
import sys
from pathlib import Path

THU_MUC_OUTPUT = Path("data/output")
THU_MUC_GOLD = Path("data/gold")
DANH_MUC = Path("data/nguon_gold.json")

# Giá trị hợp lệ của khoá `gan_nhan_doi` trong danh mục nguồn.
#
# Ghi thành khoá TƯỜNG MINH chứ không để suy từ sự vắng mặt: một tài liệu
# chưa ai xét và một tài liệu đã xét rồi kết luận là dùng được phải phân
# biệt được, nếu không thì người chọn tập gán nhãn đôi không biết mình đang
# đọc một kết luận hay một chỗ bỏ sót.
LOAI_DA_CHAY = "loai_da_chay_pipeline"
DU_DIEU_KIEN = "du_dieu_kien"
CHUA_XET = "chua_xet"


def _doc_json(duong_dan: Path) -> dict | list | None:
    try:
        return json.loads(duong_dan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def doc_id_co_dau_ra_pipeline(
    thu_muc: Path = THU_MUC_OUTPUT, thu_muc_gold: Path = THU_MUC_GOLD
) -> dict[str, list[str]]:
    """
    Tài liệu nào đã có giá trị máy đoán nằm trong `data/output/`.

    Trả về {doc_id: [tên file làm bằng chứng]}. Danh sách bằng chứng đi kèm
    chứ không chỉ trả về tập doc_id, vì người đọc kết luận "tài liệu này mất
    quyền vào tập gán nhãn đôi" phải kiểm lại được kết luận đó đến từ đâu.

    Hai loại bằng chứng, độ chắc chắn KHÁC NHAU:

      * `tap_gold_*.json` — khớp CHÍNH XÁC theo `doc_id` ghi trong file.
      * `*_routed.json`, `*_vlm.json`, `*_raw_extracted.json` — tên file đặt
        theo tên PDF gốc chứ không theo `doc_id`, nên chỉ khớp được theo MÃ
        CHỨNG KHOÁN nằm ở đầu `doc_id`. Cách khớp này có thể bắt nhầm một
        tài liệu khác của cùng công ty.

    Nhận nhầm ở đây khiến một tài liệu bị loại oan khỏi tập gán nhãn đôi;
    bỏ sót khiến một tài liệu đã lộ đáp án lọt vào phép đo đồng thuận. Hai
    hậu quả không cùng hạng, nên chỗ này cố ý nghiêng về phía LOẠI.
    """
    bang_chung: dict[str, list[str]] = {}

    def them(doc_id: str, ten_file: str) -> None:
        bang_chung.setdefault(doc_id, [])
        if ten_file not in bang_chung[doc_id]:
            bang_chung[doc_id].append(ten_file)

    if not thu_muc.is_dir():
        return bang_chung

    for duong_dan in sorted(thu_muc.glob("tap_gold_*.json")):
        noi_dung = _doc_json(duong_dan)
        if not isinstance(noi_dung, dict):
            continue
        for muc in noi_dung.get("tung_tai_lieu", []):
            doc_id = muc.get("doc_id")
            if doc_id:
                them(doc_id, duong_dan.name)

    # Khớp theo mã chứng khoán cho các file đặt tên theo PDF. Chỉ xét những
    # doc_id ĐÃ có nhãn gold: quét ngược từ tên file ra mã sẽ nhận nhầm mọi
    # chuỗi in hoa trong tên file (VN, BCTC, Q1) thành mã chứng khoán.
    ma_theo_doc = {
        duong_dan.stem.split("_")[0]: duong_dan.stem
        for duong_dan in sorted(thu_muc_gold.glob("*.json"))
    }
    hau_to = ("_routed.json", "_vlm.json", "_raw_extracted.json")
    for duong_dan in sorted(thu_muc.glob("*.json")):
        if not duong_dan.name.endswith(hau_to):
            continue
        phan = duong_dan.stem.split("_")
        for ma, doc_id in ma_theo_doc.items():
            if ma in phan:
                them(doc_id, duong_dan.name)

    return bang_chung


def danh_muc_nguon(duong_dan: Path = DANH_MUC) -> list[dict]:
    """Danh sách tài liệu trong danh mục nguồn; danh mục hỏng thì trả rỗng."""
    noi_dung = _doc_json(duong_dan)
    if not isinstance(noi_dung, dict):
        return []
    return noi_dung.get("tai_lieu", [])


def doi_chieu(
    thu_muc_output: Path = THU_MUC_OUTPUT,
    duong_dan_danh_muc: Path = DANH_MUC,
    thu_muc_gold: Path = THU_MUC_GOLD,
) -> dict[str, dict]:
    """
    Trạng thái gán nhãn đôi của từng tài liệu trong danh mục nguồn.

    Mỗi mục: {"khai_bao": ..., "co_dau_ra_pipeline": bool, "bang_chung": [...],
    "khop": bool}. `khop` sai khi và chỉ khi có bằng chứng máy đã đoán trên
    tài liệu này mà danh mục vẫn để nó dùng được cho tập gán nhãn đôi — đó là
    chiều duy nhất làm hỏng phép đo đồng thuận.
    """
    bang_chung = doc_id_co_dau_ra_pipeline(thu_muc_output, thu_muc_gold)
    ket_qua: dict[str, dict] = {}

    for muc in danh_muc_nguon(duong_dan_danh_muc):
        doc_id = muc.get("doc_id", "")
        khai_bao = muc.get("gan_nhan_doi", CHUA_XET)
        cua_no = bang_chung.get(doc_id, [])
        ket_qua[doc_id] = {
            "khai_bao": khai_bao,
            "co_dau_ra_pipeline": bool(cua_no),
            "bang_chung": cua_no,
            "khop": not (cua_no and khai_bao != LOAI_DA_CHAY),
        }

    return ket_qua


def tai_lieu_ngoai_danh_muc(
    thu_muc_output: Path = THU_MUC_OUTPUT,
    duong_dan_danh_muc: Path = DANH_MUC,
    thu_muc_gold: Path = THU_MUC_GOLD,
) -> dict[str, list[str]]:
    """
    Tài liệu có nhãn gold và có đầu ra pipeline nhưng KHÔNG nằm trong danh mục.

    Hàm này tồn tại vì một ca có thật: `VNM_2026Q1_TT99` có file trong
    `data/gold/` và có đầu ra pipeline trong `data/output/`, nhưng
    `data/nguon_gold.json` không khai nó. Nếu chỉ duyệt theo danh mục thì nó
    vô hình với mọi phép đối chiếu — tức là đúng loại tài liệu dễ lọt vào
    lượt gán nhãn đôi nhất, vì không sổ nào ghi rằng đáp án của nó đã lộ.
    """
    trong_danh_muc = {muc.get("doc_id") for muc in danh_muc_nguon(duong_dan_danh_muc)}
    bang_chung = doc_id_co_dau_ra_pipeline(thu_muc_output, thu_muc_gold)

    return {
        doc_id: cac_file
        for doc_id, cac_file in sorted(bang_chung.items())
        if doc_id not in trong_danh_muc
    }


def tai_lieu_du_dieu_kien(
    thu_muc_output: Path = THU_MUC_OUTPUT,
    duong_dan_danh_muc: Path = DANH_MUC,
    thu_muc_gold: Path = THU_MUC_GOLD,
) -> list[str]:
    """
    Tài liệu còn được phép vào tập gán nhãn đôi, xếp theo `doc_id`.

    Đòi CẢ HAI điều kiện: danh mục khai `du_dieu_kien` và hiện không tìm
    thấy bằng chứng máy đã đoán. Danh sách này rỗng tính tới 28/08/2026 —
    mười tài liệu gold đầu tiên đều đã chạy pipeline — nên lượt gán nhãn đôi
    chỉ bắt đầu được sau khi tập gold vượt mốc 10.
    """
    return sorted(
        doc_id
        for doc_id, muc in doi_chieu(thu_muc_output, duong_dan_danh_muc, thu_muc_gold).items()
        if muc["khai_bao"] == DU_DIEU_KIEN and not muc["co_dau_ra_pipeline"]
    )


def bao_cao(
    thu_muc_output: Path = THU_MUC_OUTPUT,
    duong_dan_danh_muc: Path = DANH_MUC,
    thu_muc_gold: Path = THU_MUC_GOLD,
) -> str:
    """Bảng trạng thái để đọc bằng mắt trước khi chọn tài liệu gán nhãn đôi."""
    trang_thai = doi_chieu(thu_muc_output, duong_dan_danh_muc, thu_muc_gold)

    dong = [
        "| doc_id | khai báo | có đầu ra pipeline | bằng chứng |",
        "|---|---|---|---|",
    ]
    for doc_id, muc in sorted(trang_thai.items()):
        bc = ", ".join(muc["bang_chung"]) if muc["bang_chung"] else "—"
        dong.append(
            f"| `{doc_id}` | {muc['khai_bao']} | "
            f"{'CÓ' if muc['co_dau_ra_pipeline'] else 'không'} | {bc} |"
        )

    lech = [doc_id for doc_id, muc in trang_thai.items() if not muc["khop"]]
    du = tai_lieu_du_dieu_kien(thu_muc_output, duong_dan_danh_muc, thu_muc_gold)

    dong += [
        "",
        f"Đủ điều kiện vào tập gán nhãn đôi: **{len(du)}** "
        + (", ".join(f"`{d}`" for d in du) if du else "— chưa có tài liệu nào"),
        "",
    ]
    if lech:
        dong.append(
            "**LỆCH SỔ SÁCH:** " + ", ".join(f"`{d}`" for d in lech)
            + " có đầu ra pipeline nhưng danh mục chưa đánh dấu "
            f"`{LOAI_DA_CHAY}`. Sửa `data/nguon_gold.json` trước khi chọn tài liệu."
        )
    else:
        dong.append("Danh mục khớp với hiện trạng `data/output/`.")

    ngoai = tai_lieu_ngoai_danh_muc(thu_muc_output, duong_dan_danh_muc, thu_muc_gold)
    if ngoai:
        dong += [
            "",
            "**NGOÀI DANH MỤC** — có nhãn gold và có đầu ra pipeline nhưng "
            "`data/nguon_gold.json` không khai. Cũng bị loại khỏi tập gán nhãn đôi:",
            "",
        ]
        dong += [f"- `{doc_id}` — {', '.join(cac_file)}" for doc_id, cac_file in ngoai.items()]

    return "\n".join(dong) + "\n"


if __name__ == "__main__":
    # Console Windows mặc định cp1252 nên in tiếng Việt sẽ nổ
    # UnicodeEncodeError. Ép utf-8 để lệnh này chạy được ở mọi terminal.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print(bao_cao())
