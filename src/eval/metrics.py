"""
Chỉ số đánh giá chất lượng trích xuất — mục 9 của proposal.

KHÔNG PHẢI `src/metrics.py`. Cái kia là monitoring của service: thời gian
từng giai đoạn, bộ đếm cho Prometheus. Cái này đo xem con số trích ra có
ĐÚNG không. Hai thứ không liên quan gì ngoài cái tên.

Mọi hàm ở đây nhận giá trị ĐÃ QUY ĐỔI VỀ ĐỒNG. So sánh trên đơn vị gốc của
từng báo cáo là cách chắc chắn nhất để có một bảng accuracy vô nghĩa.
"""

import numpy as np

# Dung sai so khớp số, tính theo tỷ lệ trên giá trị gold.
#
# Để RẤT hẹp vì báo cáo đã kiểm toán thì con số là con số — sai lệch duy
# nhất được phép là làm tròn ở đơn vị rút gọn. Dung sai rộng biến mọi phép
# đo thành lạc quan: với tổng tài sản 47 nghìn tỷ, mức 0,1% cho phép lệch
# tới 47 tỷ đồng, tức đọc nhầm một chữ số ở hàng chục tỷ vẫn tính là đúng.
TOL_RATIO = 1e-7


def khop_so(du_doan, thuc_te, tol_ratio: float = TOL_RATIO) -> bool:
    """
    Hai con số có coi là khớp không?

    None chỉ khớp với None. Đây là quyết định có hệ quả: nó nghĩa là trả
    null cho một chỉ tiêu CÓ giá trị bị tính là sai. Đúng như vậy — nhưng
    nó là lỗi ỒN, và tỷ lệ lỗi câm ở dưới tách riêng loại lỗi nguy hiểm
    hơn hẳn.
    """
    if du_doan is None or thuc_te is None:
        return du_doan is None and thuc_te is None

    return abs(du_doan - thuc_te) <= abs(thuc_te) * tol_ratio


def field_accuracy(pred: dict, gold: dict, tol_ratio: float = TOL_RATIO) -> dict:
    """
    Độ chính xác mức trường trên MỘT tài liệu.

    Trả về {"dung": int, "tong": int, "ty_le": float}. Trả cả tử và mẫu chứ
    không chỉ tỷ lệ, vì bootstrap theo cụm cần cộng dồn tử/mẫu qua nhiều tài
    liệu — trung bình của các tỷ lệ KHÁC tỷ lệ của tổng khi các tài liệu có
    số trường khác nhau.
    """
    tong = len(gold)
    dung = sum(1 for ten, gia_tri in gold.items() if khop_so(pred.get(ten), gia_tri, tol_ratio))

    return {"dung": dung, "tong": tong, "ty_le": dung / tong if tong else 0.0}


def silent_error_rate(pred: dict, gold: dict, tol_ratio: float = TOL_RATIO) -> dict:
    """
    Tỷ lệ lỗi câm: #(có giá trị, sai) / #(có giá trị).

    Đây là chỉ số TRỌNG TÂM. Lỗi ồn (trả null) vô hại vì hệ biết mình thất
    bại và có thể fallback hoặc đẩy cho người. Lỗi câm thì không có tín
    hiệu nào, và một giá trị sai trong báo cáo tài chính làm hỏng toàn bộ
    tỷ số, hồi quy, và quyết định dựng trên nó.

    VỀ MẶT HÌNH THỨC ĐÂY LÀ 1 TRỪ PRECISION trên tập non-null. Reviewer sẽ
    chỉ ra điều đó, nên trong paper phải hoặc gọi thẳng là precision rồi
    lập luận vì sao miền tài chính cần tách nó khỏi F1 tổng hợp, hoặc bỏ
    tên riêng. Đừng trình bày như một chỉ số mới.
    """
    co_gia_tri = [ten for ten in gold if pred.get(ten) is not None]
    sai = [ten for ten in co_gia_tri if not khop_so(pred[ten], gold[ten], tol_ratio)]

    return {
        "sai": len(sai),
        "co_gia_tri": len(co_gia_tri),
        "ty_le": len(sai) / len(co_gia_tri) if co_gia_tri else 0.0,
    }


def document_fully_correct(pred: dict, gold: dict, tol_ratio: float = TOL_RATIO) -> bool:
    """
    Cả tài liệu đúng hết chứ?

    Đây là thứ pipeline dữ liệu thật quan tâm. Accuracy 95% mức trường nghe
    rất tốt, nhưng với 25 trường một tài liệu thì nó tương đương khoảng 28%
    tài liệu đúng trọn vẹn — và một tài liệu có một trường sai thì vẫn phải
    người kiểm lại toàn bộ.
    """
    return all(khop_so(pred.get(ten), gia_tri, tol_ratio) for ten, gia_tri in gold.items())


def localization_top_k(ranking: list, true_error_fields, k: int) -> float:
    """
    Trong k trường bị nghi ngờ nhất, có bắt trúng trường sai không?

    ranking là danh sách field xếp theo mức nghi ngờ GIẢM DẦN.

    Trả 1.0 nếu top-k chứa ít nhất một trường sai thật, 0.0 nếu không, và
    0.0 khi tài liệu không có lỗi nào — ca đó không thuộc mẫu của H2 và
    người gọi phải lọc bỏ trước, xem cảnh báo dưới đây.

    CẢNH BÁO VỀ MẪU SỐ, chỗ dễ tự lừa nhất của cả nghiên cứu: N của H2 là
    SỐ TRƯỜNG BỊ LỖI, không phải tổng số trường. Với 60 tài liệu và 25
    trường thì tổng là 1500, nhưng nếu tỷ lệ lỗi 5-15% thì N thật chỉ
    75-225. Mọi bảng localization phải ghi N thật của bảng đó.
    """
    bi_loi = set(true_error_fields)
    if not bi_loi:
        return 0.0

    return 1.0 if bi_loi & set(ranking[:k]) else 0.0


def fabrication_rate(pred: dict, gold: dict, A, field_order: list, tol_ratio: float = TOL_RATIO,
                     residual_tol: float = 1e-6) -> dict:
    """
    Tỷ lệ trường THOẢ RÀNG BUỘC NHƯNG SAI SỰ THẬT.

    Đây là chỉ số chống bịa cho H3, và là thứ phải KHÔNG TĂNG sau khi sửa.
    Không có nó thì một hệ ép số cho khớp phương trình sẽ đạt điểm tuyệt
    đối ở mọi chỉ số khác: bảng cân đối cân hoàn hảo, chứng chỉ PASS, và
    mọi con số đều sai.

    Cách đo: chỉ đếm khi cả vector dự đoán THOẢ hệ ràng buộc (residual về
    0). Lúc đó mọi trường lệch gold là một giá trị vừa hợp lệ về hình thức
    vừa sai sự thật — đúng định nghĩa của việc bịa cho khớp. Nếu ràng buộc
    còn bị vi phạm thì hệ chưa "khớp" nên chưa bịa xong, và ca đó không
    tính vào đây.

    Thắng ở tỷ lệ lỗi câm mà thua ở chỉ số này là KẾT QUẢ TIÊU CỰC, và
    proposal đã đăng ký trước rằng phải báo cáo cả hai chiều.
    """
    co_gia_tri = [ten for ten in field_order if pred.get(ten) is not None]

    if len(co_gia_tri) < len(field_order):
        # Thiếu trường thì không dựng được vector để kiểm ràng buộc.
        return {"bia": 0, "co_gia_tri": len(co_gia_tri), "ty_le": 0.0, "thoa_rang_buoc": False}

    x = np.array([pred[ten] for ten in field_order], dtype=float)
    do_lon = np.linalg.norm(x) or 1.0
    thoa = bool(np.linalg.norm(A @ x) / do_lon <= residual_tol)

    if not thoa:
        return {"bia": 0, "co_gia_tri": len(co_gia_tri), "ty_le": 0.0, "thoa_rang_buoc": False}

    bia = [ten for ten in co_gia_tri if not khop_so(pred[ten], gold.get(ten), tol_ratio)]

    return {
        "bia": len(bia),
        "co_gia_tri": len(co_gia_tri),
        "ty_le": len(bia) / len(co_gia_tri) if co_gia_tri else 0.0,
        "thoa_rang_buoc": True,
    }


def gop_ty_le(cac_tai_lieu: list, khoa_tu: str, khoa_mau: str) -> float:
    """
    Gộp tỷ lệ qua nhiều tài liệu bằng cách cộng TỬ và cộng MẪU.

    Không lấy trung bình của các tỷ lệ. Hai cách đó chỉ trùng nhau khi mọi
    tài liệu có cùng mẫu số, mà điều đó không đúng: tài liệu thiếu trường
    có mẫu số nhỏ hơn. Trung bình của tỷ lệ cho mỗi tài liệu một trọng số
    bằng nhau bất kể nó đóng góp bao nhiêu quan sát.
    """
    tu = sum(tai_lieu[khoa_tu] for tai_lieu in cac_tai_lieu)
    mau = sum(tai_lieu[khoa_mau] for tai_lieu in cac_tai_lieu)

    return tu / mau if mau else 0.0
