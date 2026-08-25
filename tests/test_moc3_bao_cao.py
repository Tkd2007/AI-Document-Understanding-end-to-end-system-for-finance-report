"""
Test cách BÁO CÁO chỉ số định vị của Mốc 3, không test phần chạy thí nghiệm.

VÌ SAO ĐÁNG CÓ TEST RIÊNG: bảng Mốc 3 là thứ quyết định một mốc dừng của
`PREREGISTRATION.md`, và bản trước của nó đọc ra kết luận ngược với sự thật.
Nó chia số lần định vị đúng cho TỔNG số lượt, nên mỗi lần một phương pháp từ
chối trả lời bị tính là một lần định vị trượt — tức bảng đo **mức sẵn sàng
đoán** chứ không đo độ đúng, và baseline 9 (giải LP nên nặn được số thực bất
kỳ và không bao giờ bỏ phiếu trắng) trông như thắng.

Tu chính 25/08/2026 giữ con số cũ làm chỉ số CHÍNH và bắt buộc thêm hai con
số phụ đi kèm. Test ở đây chốt rằng cả ba đều có mặt và tính đúng, vì một
trong ba biến mất là bảng lại đọc ra kết luận sai mà không có gì nổ.

Bộ số dùng trong file này lấy đúng hình dạng của lượt chạy 26 hồ sơ ngày
24/08/2026 (`data/output/moc3_15congty.md`) để con số trong test đối chiếu
được với báo cáo thật.
"""

from collections import Counter

from eval.moc3 import bao_cao


def _ben(
    dinh_vi_dung: int, ra_tay: int, verified: int, abstain: int, luot_con_sai: int = 300
) -> dict:
    """Một phương pháp trong bảng tổng, chỉ điền các khoá bao_cao() đọc tới."""
    return {
        "luot_con_sai": luot_con_sai,
        "verdict": Counter({"VERIFIED": verified, "REPAIRED": ra_tay, "ABSTAIN": abstain}),
        "ly_do": Counter({"vuot_tran_thay_doi": abstain}),
        "dinh_vi_dung": dinh_vi_dung,
        "ra_tay": ra_tay,
        "cau_sai": 5,
        "cau_mau": 1000,
        "bia_sai": 5,
        "bia_mau": 1000,
        "thoa_rang_buoc": verified + ra_tay,
    }


def _ket_qua(de_xuat: dict, baseline9: dict, n_luot: int = 400) -> dict:
    return {
        "tong": {"de_xuat": de_xuat, "baseline9": baseline9},
        "n_luot": n_luot,
        "bo_qua": Counter(),
        "n_ho_so": 26,
        "n_cong_ty": 14,
    }


# Hình dạng thật của lượt chạy 24/08: đề xuất ra tay ít hơn một nửa nhưng
# trúng cao hơn hẳn trên mỗi lần ra tay.
DE_XUAT = _ben(dinh_vi_dung=85, ra_tay=122, verified=106, abstain=172)
BASELINE9 = _ben(dinh_vi_dung=118, ra_tay=234, verified=106, abstain=60)


def test_ba_con_so_dinh_vi_deu_co_mat_va_tinh_dung():
    """
    Cả ba mẫu số phải xuất hiện, và mỗi cái tính trên đúng mẫu số của nó.

    Đây là test chống hồi quy cho chính lỗi đã xảy ra: chỉ có con số chia
    cho tổng, nên bảng nói baseline 9 định vị tốt hơn trong khi cơ chế thật
    là nó đoán gấp đôi số lần và trúng ít hơn trên mỗi lần đoán.
    """
    ket = bao_cao(_ket_qua(DE_XUAT, BASELINE9))

    # Chia cho tổng 400 lượt — chỉ số CHÍNH.
    assert "0.212" in ket and "0.295" in ket

    # Chia cho số lượt CÓ RA TAY: 85/122 và 118/234.
    assert "0.697" in ket and "0.504" in ket

    # Chia cho số lượt lỗi CÓ SINH RESIDUAL, tức bỏ 106 lượt VERIFIED:
    # 85/294 và 118/294.
    assert "0.289" in ket and "0.401" in ket

    # Tỷ lệ ra tay: 122/400 và 234/400.
    assert "0.305" in ket and "0.585" in ket


def test_chi_so_chinh_duoc_neu_ten_thay_vi_de_nguoi_doc_tu_chon():
    """
    Bảng phải NÓI RA cái nào là chỉ số chính.

    Báo cáo ba con số mà không nói cái nào quyết định thì khi bảng ra, người
    đọc — kể cả chính tác giả — sẽ lấy con số có lợi và gọi đó là kết luận.
    Đó đúng là HARKing, thứ mà việc đăng ký trước sinh ra để ngăn, nên "nêu
    tên chỉ số chính" là một phần của tu chính chứ không phải trình bày.
    """
    ket = bao_cao(_ket_qua(DE_XUAT, BASELINE9))
    assert "CHÍNH" in ket


def test_dinh_vi_khi_ra_tay_khong_bao_gio_dung_mot_minh():
    """
    Con số 'khi ra tay' luôn phải có tỷ lệ ra tay đứng cùng bảng.

    Thiếu tỷ lệ ra tay thì chỉ số này bị hack bằng cách im lặng: một hệ trả
    lời đúng một lượt rồi từ chối 399 lượt còn lại đạt 1.000. Ca dưới đây
    dựng đúng hệ đó, và bảng phải để lộ ngay rằng nó chỉ ra tay 1/400 lượt.
    """
    im_lang = _ben(dinh_vi_dung=1, ra_tay=1, verified=0, abstain=399)
    ket = bao_cao(_ket_qua(im_lang, BASELINE9))

    assert "1.000" in ket  # định vị khi ra tay
    assert "0.003" in ket  # tỷ lệ ra tay 1/400, con số tố cáo nó
    assert "Tỷ lệ ra tay" in ket


def test_khong_chia_cho_khong_khi_mot_ben_khong_bao_gio_ra_tay():
    """
    Phương pháp từ chối mọi lượt phải cho ra dấu gạch, không phải nổ.

    Ca này KHÔNG giả định: `diagnose()` từ chối khi tập ứng viên đóng không
    chứa cách đọc hợp lệ nào, nên một tầng dữ liệu không có ảnh — tức không
    có nguồn ứng viên `o_lan_can` lẫn `phieu_vlm` — có thể đẩy nó về đúng 0
    lượt ra tay.
    """
    cam_tit = _ben(dinh_vi_dung=0, ra_tay=0, verified=0, abstain=400)
    ket = bao_cao(_ket_qua(cam_tit, BASELINE9))

    assert "—" in ket


def test_chi_so_H3_chinh_do_o_MUC_LUOT_khong_phai_muc_truong():
    """
    Dòng chính của H3 phải là tỷ lệ lượt, và hai dòng mức trường phải in đủ
    chữ số để đọc được hiệu số.

    Lý do là số học chứ không phải trình bày: hồ sơ XBRL có trung vị 158 chỉ
    tiêu mà mỗi lượt chỉ tiêm MỘT lỗi, nên tỷ lệ lỗi câm mức trường có trần
    tuyệt đối khoảng 0,0061 — toàn bộ dải hẹp hơn năm lần ngưỡng effect size
    3 điểm phần trăm đã chốt ở PREREGISTRATION mục 1. Giữ nó làm chỉ số
    chính thì mọi so sánh trên tầng này tự động bị tuyên là không khác biệt,
    và điều kiện phản chứng của H3 tự kích hoạt bất kể phương pháp tốt đến
    đâu.

    Ba chữ số thập phân trên một dải 0,0061 chỉ cho khoảng sáu giá trị phân
    biệt được, nên giữ hai dòng phụ mà in ba chữ số là giữ một thứ không đọc
    được.
    """
    de_xuat = _ben(85, 122, 106, 172, luot_con_sai=316)
    baseline9 = _ben(118, 234, 106, 60, luot_con_sai=280)
    ket = bao_cao(_ket_qua(de_xuat, baseline9))

    # 316/400 và 280/400 ở mức lượt. Tránh con số rơi đúng mép làm tròn
    # (315/400 = 0,7875) vì test khi đó gãy vì dấu phẩy động chứ không
    # phải vì hành vi sai.
    assert "0.790" in ket and "0.700" in ket
    assert "CHÍNH" in ket

    # Hai dòng mức trường in sáu chữ số: 5/1000 và 5/1000.
    assert "0.005000" in ket
