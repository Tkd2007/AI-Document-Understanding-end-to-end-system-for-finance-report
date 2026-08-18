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
    Trả `_totals` về nguyên trạng sau mỗi test.

    Nó là state toàn cục ở mức module, sống suốt phiên pytest: không dọn
    thì test chạy trước làm sai kỳ vọng của test chạy sau, và thứ tự chạy
    lại là thứ không nên phụ thuộc vào.
    """
    metrics._totals.clear()
    metrics._totals.update(TOTALS_KHOI_TAO)
    yield
    metrics._totals.clear()
    metrics._totals.update(TOTALS_KHOI_TAO)


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
