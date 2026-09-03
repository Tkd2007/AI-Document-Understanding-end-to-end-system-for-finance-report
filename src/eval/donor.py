"""
Bảng donor cho baseline 9 trên tầng gold Việt Nam.

VÌ SAO FILE NÀY TỒN TẠI. `diagnose_fellegi_holt_donor()` — baseline 9, đối
chứng quyết định của H3 — nhận `donor_values` từ người gọi. Tầng XBRL có
`eval/moc3.py._du_lieu_donor()` dựng bảng ấy từ hồ sơ nhiều công ty; tầng
gold Việt Nam chưa có đường nào. Đây là đường đó.

NGUYÊN TẮC KẾ THỪA NGUYÊN VĂN TỪ TẦNG XBRL, và nó đã phải trả giá hai lần
để rút ra: donor phải đến từ một TỔNG THỂ NHIỀU THỰC THỂ, nơi giá trị donor
chẳng liên quan gì tới giá trị thật của bản ghi đang sửa. Hai bản trước ở
tầng XBRL đều sai theo cùng một chiều — làm lợi cho baseline 9:

  * bản 1 gộp cả hồ sơ đang xét, đo được 32% chỉ tiêu donor TRÙNG KHÍT giá
    trị thật; baseline khi đó là oracle được đưa sẵn đáp án;
  * bản 2 chỉ loại hồ sơ đang xét nhưng vẫn lấy từ báo cáo kỳ liền kề của
    CHÍNH công ty ấy, mà tổng tài sản một công ty lệch vài phần trăm giữa
    hai kỳ nên donor vẫn gần đáp án hơn thực tế nhiều.

Nên ở đây **loại theo MÃ CÔNG TY, không phải theo tài liệu**. Tập gold có 5
mã xuất hiện hai kỳ (DGC, HPG, MWG, SAB, TTF); loại theo tài liệu sẽ để đúng
mười tài liệu ấy mượn của chính mình.

HAI BIẾN THỂ, và cả hai đều được báo cáo — chưa chốt cái nào là chính:

  "tho"     trung vị thô của chỉ tiêu trên các công ty khác. Trung thành với
            Fellegi-Holt kinh điển và với tiền lệ tầng XBRL. Nhược điểm trên
            dữ liệu Việt Nam: quy mô doanh nghiệp trong tập gold trải hơn ba
            bậc độ lớn, nên donor thô lệch hàng chục lần là chuyện thường —
            và thắng một đối thủ rơm thì kết luận cũng chẳng đáng tin.

  "ty_trong" trung vị của TỶ TRỌNG `chỉ tiêu / tổng tài sản` trên các công ty
            khác, rồi nhân lại với tổng tài sản của chính tài liệu đang xét.
            Đây là bản "kê cao" đối thủ: donor đúng bậc độ lớn nên baseline 9
            mạnh hơn hẳn.

CHỖ PHẢI CÂN NHẮC KHI CHỐT, ghi ra để người sau khỏi phải suy lại: biến thể
`ty_trong` cho donor phụ thuộc vào một con số CỦA CHÍNH bản ghi đang sửa
(tổng tài sản), tức nó đi xa khỏi Fellegi-Holt kinh điển theo đúng chiều mà
nguyên tắc ở trên cấm. Lập luận bênh nó là `PREREGISTRATION.md` mô tả
baseline 9 là "ứng viên đến từ **phân phối hoặc donor**", và cùng tài liệu ấy
đã chốt rằng baseline mạnh hơn thì kết luận đáng tin hơn — đó là lý do
baseline 8 chuyển từ IRLS sang quy hoạch tuyến tính. Chạy cả hai rồi báo cáo
cả hai là cách duy nhất không phải chọn trước khi biết.

GIÁ TRỊ DONOR LẤY TỪ NHÃN GOLD của các tài liệu khác, không lấy từ đầu ra
pipeline. Lý do: donor mô phỏng một CƠ SỞ DỮ LIỆU đã sạch mà nhà thống kê
chính thức có sẵn — Fellegi-Holt không giả định bản ghi cho mượn cũng hỏng.
Dùng đầu ra pipeline sẽ trộn lỗi đọc của tài liệu khác vào đối chứng, và khi
ấy hiệu số giữa hai phe không còn đo đúng "đọc lại nguồn có đáng gì không".
"""

import json
import statistics
from pathlib import Path

BIEN_THE = ("tho", "ty_trong")

# Chỉ tiêu dùng làm mẫu số khi chuẩn hoá theo quy mô. Tổng tài sản là lựa
# chọn duy nhất hợp lý: nó có ở cả hai chuẩn, luôn dương, và là con số mà
# mọi tỷ trọng trong phân tích tài chính vốn đã quy về.
KHOA_QUY_MO = "tong_tai_san"


def ma_cong_ty(doc_id: str) -> str:
    """Mã công ty của một doc_id dạng `HPG_2022Q2_TT200`."""
    return doc_id.split("_")[0]


def doc_tap_gold(thu_muc: Path) -> list[dict]:
    """Đọc trọn tập nhãn. Mỗi phần tử là nội dung một file gold."""
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(thu_muc.glob("*.json"))]


def bang_donor(tap_gold: list[dict], doc_id: str, bien_the: str = "tho") -> dict:
    """
    Bảng {chỉ tiêu -> giá trị donor} cho một tài liệu.

    Loại MỌI tài liệu cùng mã công ty với `doc_id`, kể cả chính nó. Chỉ tiêu
    nào không công ty nào khác có giá trị thì vắng mặt khỏi bảng — vắng mặt
    và bằng 0 là hai chuyện khác nhau, và `diagnose_fellegi_holt_donor()` xử
    lý ca vắng mặt bằng cách lấy chính giá trị hiện tại làm mốc.
    """
    if bien_the not in BIEN_THE:
        raise ValueError(f"biến thể donor không hợp lệ: {bien_the!r}, phải là một trong {BIEN_THE}")

    ma_minh = ma_cong_ty(doc_id)
    khac = [g for g in tap_gold if ma_cong_ty(g["doc_id"]) != ma_minh]

    if bien_the == "tho":
        gom: dict[str, list[float]] = {}
        for g in khac:
            for khoa, gt in g["values"].items():
                if isinstance(gt, (int, float)):
                    gom.setdefault(khoa, []).append(float(gt))
        return {k: statistics.median(v) for k, v in gom.items() if v}

    # ty_trong: trung vị của tỷ trọng trên công ty khác, nhân lại quy mô của
    # chính tài liệu đang xét.
    quy_mo_minh = _quy_mo(tap_gold, doc_id)
    if not quy_mo_minh:
        # Không biết quy mô thì không chuẩn hoá được. Lùi về donor thô chứ
        # đừng trả bảng rỗng: bảng rỗng làm baseline 9 mất hết ứng viên và
        # thua oan, đúng thứ khiến cả thí nghiệm mất giá trị.
        return bang_donor(tap_gold, doc_id, "tho")

    gom_ty: dict[str, list[float]] = {}
    for g in khac:
        quy_mo = g["values"].get(KHOA_QUY_MO)
        if not isinstance(quy_mo, (int, float)) or quy_mo == 0:
            continue
        for khoa, gt in g["values"].items():
            # BỎ CHÍNH CHỈ TIÊU LÀM MẪU SỐ. Tỷ trọng của nó với chính nó luôn
            # bằng 1 ở mọi tài liệu, nên trung vị bằng 1, nhân lại quy mô ra
            # ĐÚNG giá trị thật — tức trao thẳng đáp án cho baseline 9 ở đúng
            # chỉ tiêu quan trọng nhất. `do_ro_ri()` bắt được chỗ này ngay lần
            # chạy đầu: tỷ lệ ô lệch dưới 1% là 8,6% với biến thể này so với
            # 0,5% của donor thô, và `tong_tai_san` là thủ phạm.
            #
            # Chỉ tiêu ấy lấy trung vị THÔ như biến thể "tho" — vẫn là một
            # donor thật, chỉ là không được chuẩn hoá bằng chính nó.
            if khoa == KHOA_QUY_MO:
                continue
            if isinstance(gt, (int, float)):
                gom_ty.setdefault(khoa, []).append(float(gt) / float(quy_mo))

    ra = {k: statistics.median(v) * quy_mo_minh for k, v in gom_ty.items() if v}
    tho = bang_donor(tap_gold, doc_id, "tho")
    if KHOA_QUY_MO in tho:
        ra[KHOA_QUY_MO] = tho[KHOA_QUY_MO]
    return ra


def _quy_mo(tap_gold: list[dict], doc_id: str) -> float | None:
    for g in tap_gold:
        if g["doc_id"] == doc_id:
            gt = g["values"].get(KHOA_QUY_MO)
            return float(gt) if isinstance(gt, (int, float)) and gt else None
    return None


def do_ro_ri(tap_gold: list[dict], bien_the: str = "tho") -> dict:
    """
    Đo mức độ donor TRÙNG với giá trị thật — phép kiểm chống oracle.

    Đây là phép đo bắt buộc chạy trước khi tin bất kỳ con số nào của baseline
    9, vì nó là đúng cái đã bắt được hai bản donor hỏng ở tầng XBRL. Trả về
    tỷ lệ ô mà donor lệch dưới 1% và dưới 10% so với nhãn tay. Donor tốt phải
    cho hai tỷ lệ này THẤP: donor gần đáp án nghĩa là baseline 9 đang được
    đưa sẵn lời giải, và hiệu số giữa hai phe khi đó không đo cái cần đo.
    """
    duoi_1 = duoi_10 = tong = 0
    for g in tap_gold:
        d = bang_donor(tap_gold, g["doc_id"], bien_the)
        for khoa, that in g["values"].items():
            if not isinstance(that, (int, float)) or that == 0 or khoa not in d:
                continue
            tong += 1
            lech = abs(d[khoa] - that) / abs(that)
            duoi_1 += lech < 0.01
            duoi_10 += lech < 0.10
    return {
        "so_o": tong,
        "ty_le_lech_duoi_1_phan_tram": duoi_1 / tong if tong else 0.0,
        "ty_le_lech_duoi_10_phan_tram": duoi_10 / tong if tong else 0.0,
    }
