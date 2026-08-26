"""
Test máy chủ gán nhãn — tập trung vào những chỗ nó TỪ CHỐI ghi.

Phần dựng ảnh và phần vẽ giao diện không test ở đây: hỏng thì người gán nhãn
thấy ngay trong hai giây. Phần đáng test là các đường từ chối, vì hỏng ở đó
nghĩa là một file gold thiếu sót được ghi ra trông y hệt một file đầy đủ, và
không ai phát hiện cho tới lúc phân tích kết quả cuối.
"""

import json
import re
import time

import pytest
from fastapi.testclient import TestClient

from eval.schema import GroundTruthDoc
from fields_config import Standard, fields_for
from gan_nhan import app as mod
from gan_nhan.kiem import O_NGUOI_PHAI_TICK


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Máy chủ ghi vào thư mục tạm, không đụng `data/gold/` thật."""
    monkeypatch.setattr(mod, "GOLD_DIR", tmp_path / "gold")
    monkeypatch.setattr(mod, "THU_MUC_PDF", tmp_path / "pdf")
    (tmp_path / "pdf").mkdir()
    monkeypatch.setattr(GroundTruthDoc, "save", lambda tu: _ghi(tu, tmp_path / "gold"))
    return TestClient(mod.app)


def _ghi(ban_ghi, thu_muc):
    thu_muc.mkdir(parents=True, exist_ok=True)
    duong_dan = thu_muc / f"{ban_ghi.doc_id}.json"
    duong_dan.write_text(ban_ghi.to_json(), encoding="utf-8")
    return duong_dan


def _than(**doi):
    than = {
        "doc_id": "TEST_2026Q1_TT99",
        "ticker": "TEST",
        "period": "2026Q1",
        "standard": "TT99",
        "unit_declared": "Đơn vị tính: VND",
        "values": dict.fromkeys(fields_for(Standard.TT99), "0"),
        "source_url": "https://example.vn/bctc.pdf",
        "downloaded_at": "2026-08-25",
        "annotator": "nguoi_kiem_thu",
        "danh_muc_kiem": dict.fromkeys(O_NGUOI_PHAI_TICK, True),
        "khong_do_gio": True,
    }
    than.update(doi)
    return than


def test_bo_chi_tieu_xep_theo_ma_so_chu_khong_theo_thu_tu_khai_bao(client):
    """
    Người gán nhãn đọc dọc theo tờ giấy, mà mã số tăng dần đúng bằng thứ tự
    dòng in trên biểu mẫu. Bắt họ nhảy qua nhảy lại giữa biểu mẫu và biểu
    nhập chính là nguồn lỗi lệch dòng — chế độ lỗi mà cả nghiên cứu đang đo.
    """
    d = client.get("/api/chi-tieu", params={"chuan": "TT99"}).json()

    assert [n["bieu_mau"] for n in d["nhom"]] == ["B01", "B02", "B03"]
    for nhom in d["nhom"]:
        ma_so = [int(c["ma_so"]) for c in nhom["chi_tieu"]]
        assert ma_so == sorted(ma_so)


def test_chuan_khong_hop_le_bi_tu_choi_thay_vi_lui_ve_mac_dinh(client):
    """
    Lùi về chuẩn mặc định ở đây sẽ cho ra một file gold gắn nhãn sai chuẩn mà
    không dấu hiệu nào — và nhận diện sai chuẩn vốn là một chế độ lỗi riêng
    mà nghiên cứu này phải đo được, không phải thứ tự tay tạo thêm.
    """
    assert client.get("/api/chi-tieu", params={"chuan": "TT_KHONG_CO"}).status_code == 400


def test_tu_choi_ghi_khi_danh_muc_kiem_chua_du(client):
    r = client.post("/api/luu", json=_than(danh_muc_kiem={}))

    assert r.status_code == 400
    assert r.json()["detail"]["loi"] == "danh_muc_kiem_chua_du"
    assert set(r.json()["detail"]["con_thieu"]) == set(O_NGUOI_PHAI_TICK)


def test_tu_choi_ghi_khi_con_o_chua_go(client):
    """
    Ô chưa gõ KHÔNG được lặng lẽ thành `null`. `null` trong tập gold có nghĩa
    hẹp là "có dòng mà đọc không ra"; biến ô bỏ quên thành `null` là tự tay
    khai rằng đã xem xét và chịu.
    """
    gia_tri = dict.fromkeys(fields_for(Standard.TT99), "0")
    gia_tri["hang_ton_kho"] = ""

    r = client.post("/api/luu", json=_than(values=gia_tri))

    assert r.status_code == 400
    assert r.json()["detail"] == {"loi": "o_khong_doc_duoc", "o": ["hang_ton_kho"]}


def test_tu_choi_ghi_khi_khong_doc_duoc_don_vi_va_chi_dan_dung_guideline(client):
    """
    Guideline mục 3.1 cấm suy hệ số đơn vị từ độ lớn con số, vì đó chính là
    việc ta muốn đo xem hệ thống làm được không. Máy chủ cũng không được tự
    suy, và thông báo phải nhắc đúng lối thoát hợp lệ.
    """
    r = client.post("/api/luu", json=_than(unit_declared="đơn vị bịa"))

    assert r.status_code == 400
    assert r.json()["detail"]["loi"] == "khong_doc_duoc_don_vi"
    assert "3.1" in r.json()["detail"]["chi_dan"]


def test_ghi_thanh_cong_thi_gia_tri_da_quy_ve_dong(client, tmp_path):
    gia_tri = dict.fromkeys(fields_for(Standard.TT99), "0")
    gia_tri["tong_tai_san"] = "29.403"

    r = client.post(
        "/api/luu", json=_than(unit_declared="Đơn vị tính: triệu đồng", values=gia_tri)
    )

    assert r.status_code == 200
    ghi = json.loads((tmp_path / "gold" / "TEST_2026Q1_TT99.json").read_text(encoding="utf-8"))
    assert ghi["unit_multiplier"] == 1_000_000
    assert ghi["values"]["tong_tai_san"] == 29_403_000_000


def test_dau_vet_kiem_toan_di_vao_file_gold(client, tmp_path):
    """
    Số lần kiểm đẳng thức và việc có sửa giá trị sau khi kiểm phải được GHI.

    Công cụ cho phép kiểm đẳng thức trên chính số người vừa gõ, nên rủi ro
    sửa một chữ số cho cân là có thật. Guideline mục 8 cấm việc đó nhưng lời
    cấm không tự kiểm chứng được; ghi lại dấu vết biến rủi ro thành đo được.
    """
    r = client.post("/api/luu", json=_than(so_lan_kiem=3, sua_sau_khi_kiem=True))

    assert r.status_code == 200
    ghi = json.loads((tmp_path / "gold" / "TEST_2026Q1_TT99.json").read_text(encoding="utf-8"))
    assert ghi["so_lan_kiem_dang_thuc"] == 3
    assert ghi["sua_gia_tri_sau_khi_kiem"] is True


def test_kiem_khong_tra_ve_gia_tri_de_nghi_qua_HTTP(client):
    """
    Ràng buộc chống-mớm-đáp-án phải giữ ở CẢ tầng HTTP, không chỉ ở hàm
    thuần. Thêm một khoá tiện tay vào đây là đủ để mớm đáp án cho người gán
    nhãn, dù `kiem_dang_thuc()` vẫn sạch.
    """
    gia_tri = dict.fromkeys(fields_for(Standard.TT99), "0")
    gia_tri["tai_san_ngan_han"] = "100"

    d = client.post(
        "/api/kiem",
        json={"standard": "TT99", "values": gia_tri, "unit_declared": "Đơn vị tính: VND"},
    ).json()

    assert set(d) == {"he_so_don_vi", "o_khong_ro", "dang_thuc", "dau_khau_tru"}
    for r in d["dang_thuc"]:
        assert set(r) == {"mo_ta", "trang_thai", "lech", "thieu"}
    for r in d["dau_khau_tru"]:
        assert set(r) == {"truong", "trang_thai", "ly_do"}
        # `ly_do` chỉ được nhắc mã số và số hiệu mục của guideline, không được
        # mang theo giá trị nào của tài liệu: nói "ghi dương" thì được, nói
        # dương bao nhiêu thì đúng là mớm đáp án. Mã số dài nhất là 3 chữ số,
        # còn giá trị trên BCTC luôn dài hơn thế nhiều.
        assert not re.search(r"\d{4,}", r["ly_do"])


def test_de_trong_don_vi_kem_ghi_chu_la_HOP_LE(client, tmp_path):
    """
    Guideline mục 3.1 quy định ĐÚNG lối này khi báo cáo không khai báo đơn vị:
    để trống `unit_declared`, hệ số bằng 1, và ghi lý do vào notes.

    Bản đầu của máy chủ từ chối ca này — tức chặn đúng lối thoát mà guideline
    chỉ ra, và người gán nhãn không còn cách nào ghi được một báo cáo thiếu
    dòng đơn vị. Lỗi lộ ra ở tài liệu đầu tiên.
    """
    r = client.post(
        "/api/luu",
        json=_than(unit_declared="", notes="Báo cáo không có dòng khai báo đơn vị tính."),
    )

    assert r.status_code == 200
    ghi = json.loads((tmp_path / "gold" / "TEST_2026Q1_TT99.json").read_text(encoding="utf-8"))
    assert ghi["unit_multiplier"] == 1
    assert ghi["unit_declared"] == ""


def test_de_trong_don_vi_ma_khong_ghi_chu_thi_bi_tu_choi(client):
    """
    Ghi chú là chỗ DUY NHẤT phân biệt "báo cáo không có dòng đó" với "người
    gán nhãn quên chép". Thiếu nó thì hai ca cho ra file gold giống hệt nhau,
    và về sau không ai tách lại được.
    """
    r = client.post("/api/luu", json=_than(unit_declared="", notes=""))

    assert r.status_code == 400
    assert r.json()["detail"]["loi"] == "de_trong_don_vi_ma_khong_ghi_chu"


def test_go_nham_don_vi_van_bi_tu_choi_chu_khong_lang_le_lay_he_so_1(client):
    """
    Người đã gõ một cái gì đó, nên im lặng lấy hệ số 1 là biến một dòng gõ
    sai thành tuyên bố "báo cáo ghi bằng đồng" — lệch tới một triệu lần mà
    không dấu hiệu nào trong file gold.
    """
    r = client.post("/api/luu", json=_than(unit_declared="đơn vị bịa", notes="có ghi chú"))

    assert r.status_code == 400
    assert r.json()["detail"]["loi"] == "khong_doc_duoc_don_vi"


def test_thieu_sieu_du_lieu_thi_bao_400_goi_ten_tung_o_chu_khong_no_500(client):
    """
    `GroundTruthDoc.__post_init__` cũng kiểm và ném ValueError, nhưng
    ValueError lọt ra khỏi handler thành lỗi 500 — người gán nhãn nhận một
    trang lỗi không nói được thiếu gì, đúng lúc họ chỉ quên điền một ô.

    Đây là lỗi đã làm mất hai vòng hỏi đáp ngay ở tài liệu đầu tiên, nên nó
    phải có test chứ không chỉ được sửa.
    """
    r = client.post("/api/luu", json=_than(source_url="", downloaded_at="   "))

    assert r.status_code == 400
    assert r.json()["detail"]["loi"] == "thieu_sieu_du_lieu"
    assert r.json()["detail"]["con_thieu"] == ["source_url", "downloaded_at"]


def test_doc_id_rong_bi_bat_o_tang_400_chu_khong_de_schema_nem(client):
    r = client.post("/api/luu", json=_than(doc_id=""))

    assert r.status_code == 400
    assert "doc_id" in r.json()["detail"]["con_thieu"]


def test_mo_lai_ban_da_luu_tra_ve_gia_tri_theo_THANG_CUA_BAO_CAO(client):
    """
    Giá trị lưu ở ĐỒNG, còn ô nhập nhận con số như in trên giấy. Trả nguyên
    giá trị đã quy đổi sẽ khiến lần lưu sau nhân hệ số thêm một lần nữa —
    lệch một triệu lần mà file vẫn trông hợp lệ.
    """
    gia_tri = dict.fromkeys(fields_for(Standard.TT99), "0")
    gia_tri["tong_tai_san"] = "29.403"
    client.post("/api/luu", json=_than(unit_declared="Đơn vị tính: triệu đồng", values=gia_tri))

    d = client.get("/api/gold/TEST_2026Q1_TT99").json()

    assert d["values"]["tong_tai_san"] == 29403
    assert d["unit_declared"] == "Đơn vị tính: triệu đồng"
    assert d["so_lan_ghi"] == 1


def test_mo_lai_ban_chua_co_thi_bao_404_chu_khong_tra_khung_rong(client):
    """
    Trả một khung rỗng ở đây sẽ xoá sạch những gì người vừa gõ mà không cảnh
    báo — mất công của họ vì một cú bấm nhầm.
    """
    assert client.get("/api/gold/KHONG_CO_2026Q1_TT99").status_code == 404


def test_ghi_de_thi_dem_so_lan_ghi_chu_khong_im_lang(client, tmp_path):
    """
    Sửa một file gold đã có là chuyện bình thường — phát hiện đọc nhầm một
    chữ số thì phải sửa được. Nhưng một bản ghi đã sửa ba lần và một bản viết
    một lần rồi thôi là hai thứ khác nhau khi phân tích chất lượng gán nhãn,
    và nếu không đếm thì chúng trông y hệt nhau trên đĩa.
    """
    client.post("/api/luu", json=_than())
    r = client.post("/api/luu", json=_than(notes="sửa lại mã 52, đọc nhầm 1 thành 0"))

    assert r.json()["so_lan_ghi"] == 2
    ghi = json.loads((tmp_path / "gold" / "TEST_2026Q1_TT99.json").read_text(encoding="utf-8"))
    assert ghi["so_lan_ghi"] == 2


# --- Đồng hồ do người tự bấm ------------------------------------------------
#
# Đồng hồ nuôi thẳng vào giao thức trần người: số phút đặt đồng hồ bằng
# 0,6 × trung vị `thoi_gian_giay` của 10 tài liệu gold đầu tiên
# (`PREREGISTRATION.md`, tu chính 25/08/2026). Một tài liệu quên bấm giờ chỉ
# lộ ra lúc gom số, và lúc đó không bấm lại cho quá khứ được nữa — nên các
# test dưới đây kiểm đúng chỗ đó.


@pytest.fixture(autouse=True)
def _dong_ho_sach():
    """Mỗi test một đồng hồ trắng: trạng thái này sống ở mức tiến trình."""
    mod._dong_ho.clear()
    yield
    mod._dong_ho.clear()


def test_chua_bam_gio_thi_tu_choi_ghi_chu_khong_lang_le_ghi_so_0(client):
    """
    Ghi lặng lẽ số 0 chính là cách `VNM_2026Q1_TT99` ra đời với một ô thời
    gian không ai đọc được nghĩa — không rõ vì không ai bấm giờ hay vì file
    được sửa tay. Đường từ chối này tồn tại để ca đó không lặp lại.
    """
    r = client.post("/api/luu", json=_than(khong_do_gio=False))

    assert r.status_code == 400
    assert r.json()["detail"]["loi"] == "dong_ho_chua_chay"


def test_khai_ro_khong_do_gio_thi_ghi_duoc_va_file_noi_ro_dieu_do(client, tmp_path):
    """
    Phải có lối thoát, vì gán nhãn lại một tài liệu cũ là việc hợp lệ mà con
    số thời gian ở đó vô nghĩa. Nhưng lối thoát là một hành động tường minh,
    và file ghi ra phải TỰ KHAI rằng nó không mang số đo nào.
    """
    r = client.post("/api/luu", json=_than(khong_do_gio=True))

    assert r.status_code == 200
    ghi = json.loads((tmp_path / "gold" / "TEST_2026Q1_TT99.json").read_text(encoding="utf-8"))
    assert ghi["trang_thai_dong_ho"] == "khong_do"
    assert ghi["thoi_gian_giay"] == 0


def test_da_bam_gio_thi_file_khai_da_do_chu_khong_de_suy_tu_con_so(client, tmp_path):
    """
    `thoi_gian_giay` bằng 0 không phân biệt được "không ai bấm giờ" với "bấm
    giờ ra 0 giây". Khoá trạng thái tường minh mới phân biệt được, và trung
    vị của giao thức trần người chỉ lấy trên các tài liệu `da_do`.
    """
    client.post("/api/dong-ho/TEST_2026Q1_TT99/bat-dau")
    r = client.post("/api/luu", json=_than(khong_do_gio=False))

    assert r.status_code == 200
    assert r.json()["trang_thai_dong_ho"] == "da_do"
    ghi = json.loads((tmp_path / "gold" / "TEST_2026Q1_TT99.json").read_text(encoding="utf-8"))
    assert ghi["trang_thai_dong_ho"] == "da_do"


def test_so_do_that_thang_loi_khai_khong_do_gio(client):
    """
    Hai thứ mâu thuẫn nhau thì giữ cái đo được. Giao diện chỉ hiện ô "không
    đo giờ" khi đồng hồ đứng yên, nên ca này chỉ tới được từ một client tự
    viết — và kể cả khi đó, vứt một số đo có thật vẫn là mất mát không cứu
    lại được, còn giữ nó thì cùng lắm là thừa một con số.
    """
    client.post("/api/dong-ho/TEST_2026Q1_TT99/bat-dau")
    r = client.post("/api/luu", json=_than(khong_do_gio=True))

    assert r.json()["trang_thai_dong_ho"] == "da_do"


def test_tam_dung_thi_dong_ho_dung_lai_va_dem_so_lan(client):
    """
    `thoi_gian_giay` đếm thời gian LÀM VIỆC, không đếm thời gian đồng hồ
    tường. Một tài liệu để mở qua buổi trưa và một tài liệu làm liền mạch mà
    ra cùng một con số thì trung vị dựng trên chúng không chốt được gì.
    """
    client.post("/api/dong-ho/D/bat-dau")
    d = client.post("/api/dong-ho/D/tam-dung").json()

    assert d["trang_thai"] == "tam_dung"
    assert d["so_lan_tam_dung"] == 1

    dung_yen = client.get("/api/dong-ho/D").json()["da_troi_giay"]
    time.sleep(1.1)
    assert client.get("/api/dong-ho/D").json()["da_troi_giay"] == dung_yen


def test_tiep_tuc_cong_don_chu_khong_dat_lai_ve_khong(client):
    """
    Nghỉ giữa chừng rồi làm tiếp là chuyện thường trong 100 tài liệu. Đặt
    lại về 0 ở đây sẽ biến mọi tài liệu bị ngắt quãng thành một số đo hụt.
    """
    client.post("/api/dong-ho/D/bat-dau")
    time.sleep(1.1)
    client.post("/api/dong-ho/D/tam-dung")
    d = client.post("/api/dong-ho/D/bat-dau").json()

    assert d["trang_thai"] == "dang_chay"
    assert d["da_troi_giay"] >= 1


def test_xem_dong_ho_chua_bam_tra_trang_thai_chu_khong_bao_404(client):
    """
    Giao diện phải vẽ đúng nút ngay lúc người gõ xong doc_id: tài liệu đang
    dừng giữa chừng phải hiện "Tiếp tục" chứ không hiện "Bắt đầu". Chưa bấm
    là một trạng thái hợp lệ, không phải một lỗi.
    """
    d = client.get("/api/dong-ho/CHUA_TUNG_MO").json()

    assert d["trang_thai"] == "chua_bat_dau"
    assert d["da_troi_giay"] == 0


def test_hanh_dong_la_khong_duoc_lang_le_bo_qua(client):
    r = client.post("/api/dong-ho/D/xoa-het")

    assert r.status_code == 400


def test_ghi_xong_thi_dong_ho_duoc_don_di(client):
    """
    Tài liệu kế tiếp phải bắt đầu từ 00:00. Giữ lại đồng hồ cũ nghĩa là con
    số của tài liệu trước cộng sang tài liệu sau mà không dấu hiệu nào.
    """
    client.post("/api/dong-ho/TEST_2026Q1_TT99/bat-dau")
    client.post("/api/luu", json=_than())

    assert client.get("/api/dong-ho/TEST_2026Q1_TT99").json()["trang_thai"] == "chua_bat_dau"
