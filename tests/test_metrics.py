"""
Test bộ đếm toàn cục phục vụ endpoint /metrics.

Chạy được mà không cần model hay mạng: `merge_into_totals()` chỉ đọc
`RunMetrics.as_dict()`, nên dựng thẳng đối tượng RunMetrics là đủ, không
phải chạy qua pipeline.

Điều đáng test nhất ở đây không phải phép cộng, mà là counter lỗi có tồn
tại từ trước khi có lỗi hay không: Prometheus chưa thấy series thì alert
dựng trên `rate(...)` im lặng, và một hệ giám sát im lặng lúc đang hỏng
thì tệ hơn là không có.
"""

import sys
import threading

import pytest

import metrics
from metrics import RunMetrics, get_totals, merge_into_totals

# Chụp lại _totals ngay lúc import — thời điểm chưa lượt chạy nào được gộp
# — nên đây đúng là bộ counter mà metrics.py khởi tạo sẵn. Fixture bên dưới
# khôi phục theo ảnh chụp này, không theo một danh sách key chép cứng: chép
# cứng thì lần sau metrics.py thêm hoặc đổi tên một counter khởi tạo sẵn,
# fixture sẽ dựng lại trạng thái mà metrics.py chưa từng có — test vẫn xanh
# nhưng đang đo một thứ không tồn tại.
TOTALS_KHOI_TAO = dict(metrics._totals)


@pytest.fixture(autouse=True)
def totals_sach():
    """
    Trả `_totals` và `_histograms` về nguyên trạng sau mỗi test.

    Cả hai là state toàn cục ở mức module, sống suốt phiên pytest: không
    dọn thì test chạy trước làm sai kỳ vọng của test chạy sau, và thứ tự
    chạy lại là thứ không nên phụ thuộc vào.

    `_histograms` khởi tạo RỖNG chứ không có sẵn mục nào — khác `_totals`,
    vốn cố ý dựng sẵn ba counter bằng 0. Lý do khác nhau: counter cần tồn
    tại từ lượt scrape đầu để alert dựng trên rate() có series mà so, còn
    một histogram chưa có số đo nào thì không có gì để nội suy, dựng sẵn
    chỉ tạo ra một đường p99 bằng 0 trông như hệ thống đang rất nhanh.
    """
    metrics._totals.clear()
    metrics._totals.update(TOTALS_KHOI_TAO)
    metrics._histograms.clear()
    yield
    metrics._totals.clear()
    metrics._totals.update(TOTALS_KHOI_TAO)
    metrics._histograms.clear()


def luot_chay(status: str) -> RunMetrics:
    """Một lượt chạy đã kết thúc với status cho trước."""
    run = RunMetrics("bao_cao.pdf")
    run.status = status
    return run


def test_counter_loi_co_san_bang_0_truoc_khi_co_loi():
    totals = get_totals()

    assert totals["documents_error_total"] == 0
    assert totals["documents_ok_total"] == 0
    assert totals["documents_total"] == 0


def test_ok_va_error_dem_rieng_nhung_documents_total_gop_ca_hai():
    for status in ("ok", "ok", "error"):
        merge_into_totals(luot_chay(status))

    totals = get_totals()

    assert totals["documents_ok_total"] == 2
    assert totals["documents_error_total"] == 1
    assert totals["documents_total"] == 3


def test_status_ngoai_du_kien_van_duoc_dem_va_bao_ra_log(capsys):
    # "running" nghĩa là process chết trước cả khối finally của
    # route_document(). Nếu nuốt im lặng thì tổng các counter con nhỏ hơn
    # documents_total mà không chỗ nào giải thích khoản chênh.
    merge_into_totals(luot_chay("running"))

    totals = get_totals()

    assert totals["documents_running_total"] == 1
    assert totals["documents_total"] == 1
    assert totals["documents_ok_total"] == 0
    assert "running" in capsys.readouterr().out


def test_counter_khong_bi_lan_giua_cac_test():
    # Chốt luôn hiệu lực của fixture: nếu nó hỏng, test này thấy số dư của
    # những test chạy trước.
    assert get_totals()["documents_total"] == 0

    merge_into_totals(luot_chay("ok"))

    assert get_totals()["documents_total"] == 1


def test_dem_khong_mat_luot_khi_nhieu_thread_cong_don_cung_luc():
    """
    api.py chạy route_document() trong threadpool, nên nhiều request kết
    thúc cùng lúc sẽ gọi merge_into_totals() song song. Phép cộng dồn bên
    trong là read-modify-write, không atomic — thiếu khoá thì hai thread
    đọc chung một giá trị cũ rồi cùng ghi đè, và một lượt chạy biến mất
    khỏi counter mà không có cách nào phát hiện về sau.

    Hai thủ thuật để test thực sự bắt được lỗi đó chứ không xanh nhờ may:
      * Barrier ép mọi thread cùng xuất phát, thay vì thread đầu đã xong
        trước khi thread cuối kịp start.
      * Hạ switch interval để CPython đổi thread liên tục, mở rộng cửa sổ
        giữa lúc đọc và lúc ghi. Với giá trị mặc định 5ms, một hàm ngắn
        như thế này gần như không bao giờ bị cắt ngang giữa chừng, nên bỏ
        khoá đi test vẫn xanh — tức là test vô dụng.
    """
    SO_THREAD = 50
    SO_LUOT_MOI_THREAD = 20

    vach_xuat_phat = threading.Barrier(SO_THREAD)

    def cong_don():
        vach_xuat_phat.wait()
        for _ in range(SO_LUOT_MOI_THREAD):
            merge_into_totals(luot_chay("ok"))

    switch_interval_cu = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)
    try:
        cac_thread = [threading.Thread(target=cong_don) for _ in range(SO_THREAD)]
        for thread in cac_thread:
            thread.start()
        for thread in cac_thread:
            thread.join()
    finally:
        sys.setswitchinterval(switch_interval_cu)

    mong_doi = SO_THREAD * SO_LUOT_MOI_THREAD
    totals = get_totals()

    assert totals["documents_total"] == mong_doi
    assert totals["documents_ok_total"] == mong_doi


def test_bam_prompt_doi_khi_noi_dung_doi():
    """
    Băm NỘI DUNG chứ không phải số phiên bản. Số phiên bản đòi con người
    nhớ tăng nó, và người ta không nhớ — một prompt bị sửa mà số phiên bản
    đứng yên là hai lượt chạy khác nhau trông như một.
    """
    goc = metrics.bam_prompt("Trích xuất các chỉ tiêu sau")
    sua_mot_chu = metrics.bam_prompt("Trích xuất các chỉ tiêu sau.")

    assert goc != sua_mot_chu
    assert goc == metrics.bam_prompt("Trích xuất các chỉ tiêu sau")


def test_thong_tin_tai_lap_co_du_cac_khoa_bat_buoc():
    """
    Thiếu một khoá nào ở đây là một lượt chạy không dựng lại được. Ghi cho
    MỌI lượt chứ không chỉ lượt cuối: khi một bảng kết quả trông lạ, câu
    hỏi đầu tiên luôn là lượt đó chạy bằng gì.
    """
    thong_tin = metrics.thong_tin_tai_lap(
        model="google/gemma-4-31b-it:free",
        temperature=0.7,
        n_samples=5,
        seed=42,
        prompt_hash="abc123",
        standard="TT99",
    )

    assert set(thong_tin) == {
        "experiment_id",
        "commit",
        "model",
        "temperature",
        "n_samples",
        "seed",
        "prompt_hash",
        "standard",
    }
    assert thong_tin["n_samples"] == 5
    assert thong_tin["prompt_hash"] == "abc123"


def test_experiment_id_doc_tu_bien_moi_truong(monkeypatch):
    """
    Runner thí nghiệm đặt được biến này mà không phải luồn tham số qua cả
    pipeline. Rỗng nghĩa là lượt chạy lẻ, không thuộc thí nghiệm nào.
    """
    monkeypatch.setenv("EXPERIMENT_ID", "h1-xbrl-seed3")

    assert metrics.thong_tin_tai_lap()["experiment_id"] == "h1-xbrl-seed3"


def test_khong_co_git_thi_commit_la_none_chu_khong_no(monkeypatch):
    """
    Chạy trong Docker không có .git là chuyện bình thường. Một dòng metrics
    thiếu commit hash vẫn hơn một lượt chạy bị hỏng vì không lấy được nó.
    """
    monkeypatch.setattr(metrics, "_da_tra_commit", False)
    monkeypatch.setattr(metrics, "_commit_hash", None)
    monkeypatch.setattr(
        metrics.subprocess, "check_output", lambda *a, **k: (_ for _ in ()).throw(OSError())
    )

    assert metrics.commit_hash() is None


# --- Histogram thời gian ---------------------------------------------------
#
# Vì sao phần này tồn tại: tổng thời gian cộng dồn chia cho số lượt chạy chỉ
# cho TRUNG BÌNH, mà trung bình là con số vô dụng nhất với một pipeline có
# đuôi dài. Chín lượt 100 giây và một lượt 900 giây cho trung bình 180 —
# không lượt nào giống con số đó, và lượt duy nhất làm người dùng bỏ đi thì
# trung bình giấu mất.
#
# Các test dưới gọi thẳng metrics._ghi_histogram, vốn đòi người gọi đang giữ
# _totals_lock. Ở đây chỉ có một luồng nên không có tranh chấp, và gọi thẳng
# cho phép kiểm đúng biên bucket thay vì phải dàn dựng một lượt chạy dài
# đúng bằng số giây mong muốn.


def test_bucket_la_cong_don_khong_phai_dem_rieng_tung_khoang():
    """
    Quy ước Prometheus: một số đo 7 giây làm tăng MỌI bucket có biên >= 7.
    Đếm không cộng dồn thì histogram_quantile() cho ra số vô nghĩa mà vẫn
    vẽ được đồ thị — sai lặng lẽ đúng kiểu tệ nhất.
    """
    metrics._ghi_histogram("thu", 7.0)

    buckets = metrics.get_histograms()["thu"]["buckets"]

    assert buckets[5.0] == 0
    assert buckets[10.0] == 1
    assert buckets[30.0] == 1
    assert buckets[600.0] == 1


def test_bien_bucket_la_nho_hon_hoac_bang():
    """`le` trong Prometheus nghĩa là less-or-equal, không phải less-than."""
    metrics._ghi_histogram("thu", 10.0)

    assert metrics.get_histograms()["thu"]["buckets"][10.0] == 1


def test_so_do_vuot_bucket_lon_nhat_van_duoc_dem_vao_count():
    """
    Một lượt chạy 900 giây không rơi vào bucket nào có biên hữu hạn. Nếu
    nó cũng không được đếm thì đúng lượt chạy đáng báo động nhất lại là
    lượt biến mất khỏi số liệu.
    """
    metrics._ghi_histogram("thu", 900.0)

    hist = metrics.get_histograms()["thu"]

    assert hist["buckets"][600.0] == 0
    assert hist["count"] == 1
    assert hist["sum"] == 900.0


def test_bien_bucket_tang_dan():
    """Bucket không tăng dần thì đường cong tích luỹ vô nghĩa."""
    assert list(metrics.BUCKETS_GIAY) == sorted(metrics.BUCKETS_GIAY)


def test_gop_luot_chay_sinh_histogram_tong_va_tung_giai_doan():
    run = luot_chay("ok")
    run.stages = {"pdf_convert": 12.0, "vlm": 70.0}

    merge_into_totals(run)
    hists = metrics.get_histograms()

    assert "document_seconds" in hists
    assert hists["stage_pdf_convert_seconds"]["sum"] == 12.0
    assert hists["stage_vlm_seconds"]["sum"] == 70.0


def test_count_cua_histogram_khop_voi_documents_total():
    """
    Hai bảng được cập nhật trong cùng một lượt gọi và phải nhất quán. Lệch
    nhau thì không ai giải thích được khoản chênh, và nghi ngờ số liệu là
    đủ để không ai dùng nó nữa.
    """
    for _ in range(4):
        merge_into_totals(luot_chay("ok"))

    assert metrics.get_histograms()["document_seconds"]["count"] == 4
    assert get_totals()["documents_total"] == 4


def test_get_histograms_tra_ban_sao_khong_sua_duoc_state_that():
    metrics._ghi_histogram("thu", 7.0)

    metrics.get_histograms()["thu"]["buckets"][10.0] = 999

    assert metrics.get_histograms()["thu"]["buckets"][10.0] == 1


# --- Định dạng exposition --------------------------------------------------


def test_render_co_bucket_vo_cuc_va_no_bang_count():
    """
    Thiếu bucket +Inf thì Prometheus coi histogram là hỏng và bỏ qua TOÀN
    BỘ series — không phải một điểm dữ liệu sai, mà là mất trắng metric.
    """
    metrics._ghi_histogram("document_seconds", 900.0)
    metrics._ghi_histogram("document_seconds", 7.0)

    text = metrics.render_prometheus()

    assert 'doc_ai_document_seconds_bucket{le="+Inf"} 2' in text
    assert "doc_ai_document_seconds_count 2" in text


def test_render_khai_bao_dung_kieu_cho_tung_metric():
    merge_into_totals(luot_chay("ok"))

    text = metrics.render_prometheus()

    assert "# TYPE doc_ai_documents_total counter" in text
    assert "# TYPE doc_ai_document_seconds histogram" in text


def test_nhan_bien_bucket_doc_duoc():
    """60.0 in ra "60" chứ không phải "60.0": Prometheus đọc được cả hai,
    người đọc log thì không nên phải chịu đựng cái sau."""
    metrics._ghi_histogram("document_seconds", 1.0)

    text = metrics.render_prometheus()

    assert 'le="60"' in text
    assert 'le="0.5"' in text
    assert 'le="2.5"' in text


def test_render_khong_co_luot_chay_nao_van_ra_counter():
    """
    Endpoint /metrics phải trả lời được ngay từ lượt scrape đầu tiên —
    smoke test của CI dựa vào đúng chuyện này.
    """
    text = metrics.render_prometheus()

    assert "doc_ai_documents_total 0" in text
