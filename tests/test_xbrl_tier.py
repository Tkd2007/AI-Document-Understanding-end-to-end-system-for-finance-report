"""
Test tầng đánh giá XBRL.

Mọi test chạy được KHÔNG CẦN MẠNG: linkbase là chuỗi XML trong file này,
companyfacts là dict dựng tay, và phần tải chỉ được kiểm ở mức dựng URL và
chế độ dry-run. Container không có mạng tới sec.gov, nên một test gọi thật
sẽ đỏ vì lý do môi trường chứ không phải vì code sai — loại test tệ nhất.

Hai test quan trọng nhất:

  test_scale_toan_cuc_thi_moi_dang_thuc_van_thoa — chốt bằng thực nghiệm một
  mệnh đề chứng minh trong một dòng ở constraints.py, và là lý do mỏ neo
  tuyệt đối ở mục 6.3 proposal là bắt buộc.

  test_chi_lay_fact_cua_dung_mot_ho_so — nếu nó đỏ thì ground truth của cả
  tầng này sai, mà ground truth chắc chắn đúng là thứ duy nhất làm nên giá
  trị của tầng.
"""

import numpy as np
import pytest

from constraints import build_matrix
from eval.xbrl_tier import fetch
from eval.xbrl_tier.facts import build_table, cac_ky_cua_ho_so
from eval.xbrl_tier.inject import ErrorType, inject, inject_scale_toan_cuc
from eval.xbrl_tier.linkbase import (
    CalcEquation,
    concept_tu_href,
    concepts_xuat_hien,
    parse_calculation_linkbase,
    to_matrix,
)
from eval.xbrl_tier.render import _dinh_dang, ky_tu_khong_ve_duoc, render
from eval.xbrl_tier.table import FinancialTable

# --- Fixture: linkbase ba đẳng thức lồng nhau -------------------------------
#
#   Assets        = AssetsCurrent + AssetsNoncurrent
#   AssetsCurrent = Cash + Receivables
#   GrossProfit   = Revenues − CostOfRevenue      <- trọng số âm
#
# Đẳng thức thứ ba có trọng số −1, thứ mà FIELD_IDENTITIES của phía Việt Nam
# không có và cũng là lý do to_matrix phải là bản tổng quát có trọng số.

LINKBASE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<linkbase xmlns="http://www.xbrl.org/2003/linkbase"
          xmlns:xlink="http://www.w3.org/1999/xlink">
  <calculationLink xlink:type="extended" xlink:role="http://x/role/BalanceSheet">
    <loc xlink:href="us-gaap-2025.xsd#us-gaap_Assets" xlink:label="a"/>
    <loc xlink:href="us-gaap-2025.xsd#us-gaap_AssetsCurrent" xlink:label="ac"/>
    <loc xlink:href="us-gaap-2025.xsd#us-gaap_AssetsNoncurrent" xlink:label="anc"/>
    <loc xlink:href="us-gaap-2025.xsd#us-gaap_Cash" xlink:label="cash"/>
    <loc xlink:href="us-gaap-2025.xsd#us-gaap_Receivables" xlink:label="rec"/>
    <calculationArc xlink:from="a" xlink:to="ac" weight="1" order="1"/>
    <calculationArc xlink:from="a" xlink:to="anc" weight="1" order="2"/>
    <calculationArc xlink:from="ac" xlink:to="cash" weight="1" order="1"/>
    <calculationArc xlink:from="ac" xlink:to="rec" weight="1" order="2"/>
  </calculationLink>
  <calculationLink xlink:role="http://x/role/Income">
    <loc xlink:href="us-gaap-2025.xsd#us-gaap_GrossProfit" xlink:label="gp"/>
    <loc xlink:href="us-gaap-2025.xsd#us-gaap_Revenues" xlink:label="rev"/>
    <loc xlink:href="us-gaap-2025.xsd#us-gaap_CostOfRevenue" xlink:label="cor"/>
    <calculationArc xlink:from="gp" xlink:to="rev" weight="1"/>
    <calculationArc xlink:from="gp" xlink:to="cor" weight="-1"/>
  </calculationLink>
</linkbase>
"""

KY_MOI = "2025-12-31"
KY_TRUOC = "2024-12-31"

GIA_TRI = {
    "Assets": {KY_MOI: 1000.0, KY_TRUOC: 800.0},
    "AssetsCurrent": {KY_MOI: 400.0, KY_TRUOC: 300.0},
    "AssetsNoncurrent": {KY_MOI: 600.0, KY_TRUOC: 500.0},
    "Cash": {KY_MOI: 150.0, KY_TRUOC: 100.0},
    "Receivables": {KY_MOI: 250.0, KY_TRUOC: 200.0},
    "GrossProfit": {KY_MOI: 400.0, KY_TRUOC: 250.0},
    "Revenues": {KY_MOI: 900.0, KY_TRUOC: 700.0},
    "CostOfRevenue": {KY_MOI: 500.0, KY_TRUOC: 450.0},
}


def _bang() -> FinancialTable:
    thu_tu = list(GIA_TRI)
    return FinancialTable(
        doc_id="TEST_2025_10K",
        concepts=thu_tu,
        labels={ten: ten for ten in thu_tu},
        periods=[KY_MOI, KY_TRUOC],
        values={ten: dict(cot) for ten, cot in GIA_TRI.items()},
        unit_label="USD in thousands",
        unit_multiplier=1_000,
    )


def _residual(table: FinancialTable, ky: str) -> np.ndarray:
    pt = parse_calculation_linkbase(LINKBASE_XML)
    A, thu_tu = to_matrix(pt, concepts_xuat_hien(pt))
    x = np.array([table.get(ten, ky) for ten in thu_tu], dtype=float)
    return A @ x


# --- linkbase ---------------------------------------------------------------


def test_parse_linkbase_ra_dung_ba_dang_thuc_va_dung_dau():
    pt = parse_calculation_linkbase(LINKBASE_XML)
    theo_tong = {p.total: p for p in pt}

    assert set(theo_tong) == {"Assets", "AssetsCurrent", "GrossProfit"}
    assert theo_tong["Assets"].parts == (
        ("AssetsCurrent", 1.0),
        ("AssetsNoncurrent", 1.0),
    )
    assert theo_tong["GrossProfit"].parts == (
        ("Revenues", 1.0),
        ("CostOfRevenue", -1.0),
    )


def test_role_duoc_giu_lai():
    """
    Cùng một concept xuất hiện ở nhiều báo cáo với vai khác nhau, nên bỏ
    role đi là trộn lẫn các hệ ràng buộc vốn không nên trộn.
    """
    pt = parse_calculation_linkbase(LINKBASE_XML)
    theo_tong = {p.total: p.role for p in pt}

    assert theo_tong["Assets"].endswith("BalanceSheet")
    assert theo_tong["GrossProfit"].endswith("Income")


def test_concept_tu_href_cat_o_gach_duoi_DAU_TIEN():
    """
    Tên concept của taxonomy riêng từng doanh nghiệp có chứa gạch dưới, còn
    tiền tố thì không — cắt ở gạch cuối sẽ chặt cụt tên concept.
    """
    assert concept_tu_href("us-gaap-2025.xsd#us-gaap_AssetsCurrent") == "AssetsCurrent"
    assert concept_tu_href("x.xsd#vnm_Some_Custom_Tag") == "Some_Custom_Tag"
    assert concept_tu_href("#Assets") == "Assets"


def test_trong_so_ngoai_cong_tru_mot_thi_NEM_LOI():
    """
    Im lặng chấp nhận trọng số lạ sẽ dựng ra ma trận ràng buộc sai mà không
    có gì báo, và ràng buộc sai thì mọi kết luận về định vị đều sai theo.
    """
    xml = LINKBASE_XML.replace('xlink:to="cor" weight="-1"', 'xlink:to="cor" weight="2"')

    with pytest.raises(ValueError, match="trọng số"):
        parse_calculation_linkbase(xml)


def test_gia_tri_that_thoa_moi_dang_thuc():
    """Bộ số fixture phải cân — nếu không thì mọi test dưới đây vô nghĩa."""
    assert np.allclose(_residual(_bang(), KY_MOI), 0)
    assert np.allclose(_residual(_bang(), KY_TRUOC), 0)


def test_to_matrix_khop_build_matrix_cua_A2_khi_moi_trong_so_bang_1():
    """
    Hai bộ dựng ma trận phải cho ra ma trận GIỐNG HỆT NHAU trên phần chung.
    Chúng lệch nhau nghĩa là một trong hai đang dựng sai ràng buộc, mà ràng
    buộc sai là loại lỗi không có gì báo.
    """
    fields = ["AssetsCurrent", "AssetsNoncurrent", "Assets"]

    A_xbrl, thu_tu_xbrl = to_matrix(
        [CalcEquation("Assets", (("AssetsCurrent", 1.0), ("AssetsNoncurrent", 1.0)))],
        fields,
    )
    A_a2, thu_tu_a2 = build_matrix(
        fields,
        [(["AssetsCurrent", "AssetsNoncurrent"], "Assets", "tài sản")],
    )

    assert thu_tu_xbrl == thu_tu_a2
    assert np.array_equal(A_xbrl, A_a2)


def test_to_matrix_bo_dang_thuc_thieu_concept():
    """
    Không trích một chỉ tiêu thì không kiểm được đẳng thức chứa nó. Coi nó
    bằng 0 sẽ dựng ra ràng buộc sai và làm hạng cao lên giả tạo, tức báo cáo
    lạc quan hơn sự thật về khả năng định vị.
    """
    pt = parse_calculation_linkbase(LINKBASE_XML)
    A, _ = to_matrix(pt, ["Assets", "AssetsCurrent", "AssetsNoncurrent"])

    assert A.shape[0] == 1


# --- inject -----------------------------------------------------------------


def test_inject_voi_cung_seed_thi_tai_lap_tung_bit():
    lan_1, gt_1 = inject(_bang(), ErrorType.DIGIT_SUB, n_errors=2, seed=7)
    lan_2, gt_2 = inject(_bang(), ErrorType.DIGIT_SUB, n_errors=2, seed=7)

    assert gt_1 == gt_2
    assert lan_1.values == lan_2.values


def test_inject_khong_dung_toi_bang_goc():
    """
    Bảng gốc là ground truth của chính thí nghiệm đang chạy. Một hàm sửa tại
    chỗ sẽ âm thầm làm hỏng nó và không có gì báo.
    """
    goc = _bang()
    inject(goc, ErrorType.SIGN, n_errors=3, seed=1)

    assert goc.values == GIA_TRI


def test_digit_sub_giu_dau_va_giu_do_dai():
    """
    OCR đọc nhầm chữ số chứ không làm mất chữ số. Lỗi làm đổi số chữ số sẽ
    bị mọi biên độ lớn bắt ngay, tức sinh ra bài toán dễ hơn bài toán thật.
    """
    _, gt = inject(_bang(), ErrorType.DIGIT_SUB, n_errors=5, seed=3)

    for loi in gt:
        assert loi.corrupted != loi.original
        assert (loi.corrupted < 0) == (loi.original < 0)
        assert len(str(int(abs(loi.corrupted)))) == len(str(int(abs(loi.original))))


def test_row_shift_lay_dung_gia_tri_cua_dong_KE():
    _, gt = inject(_bang(), ErrorType.ROW_SHIFT, n_errors=4, seed=11)
    bang = _bang()

    for loi in gt:
        lay_tu = loi.detail["lay_tu_concept"]
        assert lay_tu in bang.hang_xom_doc(loi.concept)
        assert loi.corrupted == bang.get(lay_tu, loi.period)


def test_col_shift_lay_dung_gia_tri_cot_ky_so_sanh():
    _, gt = inject(_bang(), ErrorType.COL_SHIFT, n_errors=4, seed=5)
    bang = _bang()

    for loi in gt:
        assert loi.detail["lay_tu_ky"] == KY_TRUOC
        assert loi.corrupted == bang.get(loi.concept, KY_TRUOC)


def test_sign_chi_doi_dau():
    _, gt = inject(_bang(), ErrorType.SIGN, n_errors=3, seed=2)

    for loi in gt:
        assert loi.corrupted == -loi.original


def test_khong_du_o_hong_duoc_thi_NEM_LOI():
    """
    Trả ít lỗi hơn yêu cầu một cách im lặng làm mẫu số của mọi chỉ số H2 sai
    mà không có gì báo.
    """
    mot_ky = FinancialTable(
        doc_id="x",
        concepts=["Assets"],
        labels={"Assets": "Assets"},
        periods=[KY_MOI],
        values={"Assets": {KY_MOI: 1000.0}},
    )

    with pytest.raises(ValueError, match="chỉ inject được 0/1"):
        inject(mot_ky, ErrorType.COL_SHIFT, n_errors=1, seed=0)


def test_digit_sub_mot_truong_lam_vi_pham_dung_so_dang_thuc_chua_no():
    """
    `AssetsNoncurrent` nằm trong đúng một đẳng thức nên hỏng nó vi phạm đúng
    một dòng; `AssetsCurrent` nằm trong hai (một lần làm tổng, một lần làm
    thành phần) nên hỏng nó vi phạm hai dòng. Đây là kiểm chứng thực nghiệm
    cho bảng định vị mà H0 dựng bằng lý thuyết.
    """
    bang = _bang()

    for concept, so_dong_vi_pham in [("AssetsNoncurrent", 1), ("AssetsCurrent", 2)]:
        hong = bang.thay_gia_tri(concept, KY_MOI, bang.get(concept, KY_MOI) + 7.0)
        r = _residual(hong, KY_MOI)

        assert int(np.count_nonzero(np.abs(r) > 1e-9)) == so_dong_vi_pham


def test_scale_toan_cuc_thi_moi_dang_thuc_van_thoa():
    """
    Hệ ràng buộc kế toán là hệ THUẦN NHẤT nên mọi bội vô hướng của nghiệm
    cũng là nghiệm: sai đơn vị toàn cục LUÔN vô hình với mọi phương pháp dựa
    trên ràng buộc. Không phải "thường vô hình" — là luôn.

    Đây là lý do mỏ neo tuyệt đối ở mục 6.3 proposal là bắt buộc chứ không
    phải tuỳ chọn, và test này là bản chạy được của chứng minh một dòng ở
    constraints.py.
    """
    hong, gt = inject_scale_toan_cuc(_bang(), k=3)

    assert np.allclose(_residual(hong, KY_MOI), 0)
    assert np.allclose(_residual(hong, KY_TRUOC), 0)
    assert all(loi.detail["toan_cuc"] for loi in gt)
    assert hong.meta["scale_toan_cuc_k"] == 3


def test_scale_toan_cuc_dung_MOT_he_so_cho_moi_o():
    """
    Mỗi ô một hệ số khác nhau thì đó là n lỗi độc lập chứ không phải một lỗi
    đọc nhầm dòng đơn vị, và bảng sẽ không còn cân.
    """
    hong, _ = inject_scale_toan_cuc(_bang(), k=-3)

    for ten, cot in GIA_TRI.items():
        for ky, goc in cot.items():
            assert hong.get(ten, ky) == pytest.approx(goc / 1000)


# --- render -----------------------------------------------------------------


def test_dinh_dang_so_theo_kieu_bao_cao_tai_chinh():
    """
    Số âm in trong ngoặc đơn không phải chi tiết thẩm mỹ: nó chính là nguồn
    của chế độ lỗi mất dấu âm. Render bằng dấu trừ là xoá một chế độ lỗi
    khỏi tầng này.
    """
    assert _dinh_dang(1234567) == "1,234,567"
    assert _dinh_dang(-1234) == "(1,234)"
    assert _dinh_dang(None) == "-"


def test_font_thieu_glyph_thi_NEM_LOI_chu_khong_ve_o_vuong():
    """
    Đây là lỗi im lặng đúng nghĩa: ảnh vẫn ra một cái bảng trông bình
    thường, chỉ có chữ là ô vuông tofu, và không có gì báo cho tới khi ai đó
    mở ảnh ra xem — thường là sau khi đã chạy xong cả lượt thí nghiệm.

    Font đi kèm Pillow không có glyph tiếng Việt có dấu. Đó là lý do phần
    chữ cố định trên ảnh mặc định là tiếng Anh, và là lý do ablation
    "Transfer XBRL → BCTC Việt Nam" phải truyền font_path.
    """
    bang = _bang()
    bang.labels["Assets"] = "TỔNG CỘNG TÀI SẢN"

    with pytest.raises(ValueError, match="font không vẽ được"):
        render(bang)


def test_ky_tu_khong_ve_duoc_chi_bat_dung_ky_tu_thieu():
    from PIL import ImageFont

    font = ImageFont.load_default(size=20)

    assert ky_tu_khong_ve_duoc(font, "Assets 1,234 (5)") == set()
    assert ky_tu_khong_ve_duoc(font, "Tài sản") == {"à", "ả"}


def test_render_tra_bbox_cho_moi_o_va_nam_trong_anh():
    bang = _bang()
    ket_qua = render(bang)

    assert len(ket_qua.bboxes) == len(bang.concepts) * len(bang.periods)

    rong, cao = ket_qua.image.size
    for (x1, y1, x2, y2) in ket_qua.bboxes.values():
        assert 0 <= x1 < x2 <= rong
        assert 0 <= y1 < y2 <= cao


def test_render_tra_bbox_rieng_cho_dong_don_vi_tinh():
    """
    Dòng khai báo đơn vị là mỏ neo tuyệt đối duy nhất phá được bất biến
    scale, nên đọc được nó hay không tự nó là một phép đo — không phải chú
    thích của bảng.
    """
    ket_qua = render(_bang())
    x1, y1, x2, y2 = ket_qua.header_bbox

    assert x2 > x1 and y2 > y1


def test_render_tat_dinh():
    """
    Ảnh khác nhau giữa hai lần chạy là hai bộ dữ liệu khác nhau, và khi đó
    con số đo được ở hai nơi không so với nhau được nữa.
    """
    a = render(_bang())
    b = render(_bang())

    assert a.image.tobytes() == b.image.tobytes()
    assert a.bboxes == b.bboxes


# --- facts ------------------------------------------------------------------

COMPANYFACTS = {
    "cik": 320193,
    "entityName": "Test Corp",
    "facts": {
        "us-gaap": {
            "Assets": {
                "label": "Total assets",
                "units": {
                    "USD": [
                        {"end": KY_MOI, "val": 1000, "accn": "GOC", "form": "10-K"},
                        {"end": KY_MOI, "val": 9999, "accn": "SAU", "form": "10-K"},
                        {"end": KY_TRUOC, "val": 800, "accn": "GOC", "form": "10-K"},
                    ]
                },
            },
            "Revenues": {
                "label": "Revenues",
                "units": {
                    "USD": [
                        {
                            "start": "2025-01-01",
                            "end": KY_MOI,
                            "val": 900,
                            "accn": "GOC",
                            "form": "10-K",
                        },
                        {
                            "start": "2025-10-01",
                            "end": KY_MOI,
                            "val": 220,
                            "accn": "GOC",
                            "form": "10-K",
                        },
                    ]
                },
            },
        }
    },
}


def test_chi_lay_fact_cua_dung_mot_ho_so():
    """
    companyfacts gộp mọi lần công bố, nên cùng một ngày kết thúc kỳ có thể
    có nhiều giá trị: bản gốc và các bản trình bày lại. Trộn hai hồ sơ vào
    một bảng sẽ phá vỡ đẳng thức kế toán một cách âm thầm, và khi đó tầng
    này mất đúng thứ duy nhất làm nên giá trị của nó.
    """
    bang = build_table(COMPANYFACTS, ["Assets"], accn="GOC", periods=[KY_MOI])

    assert bang.get("Assets", KY_MOI) == 1000


def test_fact_thoi_ky_chi_nhan_ky_NAM():
    """
    Hồ sơ 10-K chứa cả fact quý lẫn fact năm cho cùng một chỉ tiêu. Lấy nhầm
    fact quý vào bảng năm làm đẳng thức không cân, và lỗi đó trông y hệt lỗi
    trích xuất.
    """
    bang = build_table(COMPANYFACTS, ["Revenues"], accn="GOC", periods=[KY_MOI])

    assert bang.get("Revenues", KY_MOI) == 900


def test_khong_co_fact_thi_de_trong_chu_khong_doan():
    bang = build_table(COMPANYFACTS, ["CostOfRevenue"], accn="GOC", periods=[KY_MOI])

    assert bang.get("CostOfRevenue", KY_MOI) is None


def test_cac_ky_sap_xep_moi_nhat_truoc():
    """
    Thứ tự này thành thứ tự cột, và quy ước "kỳ gần nhất đứng trước" phải
    khớp báo cáo thật — nếu không thì lỗi lệch cột sinh ra ở đây đi ngược
    chiều với lỗi lệch cột ngoài đời.
    """
    assert cac_ky_cua_ho_so(COMPANYFACTS, "GOC") == [KY_MOI, KY_TRUOC]


def test_nhan_hien_thi_lay_tu_companyfacts():
    bang = build_table(COMPANYFACTS, ["Assets"], accn="GOC", periods=[KY_MOI])

    assert bang.labels["Assets"] == "Total assets"


# --- fetch: chỉ kiểm phần không chạm mạng ------------------------------------


def test_cik_duoc_dem_du_muoi_chu_so():
    assert fetch.cik_10_chu_so("320193") == "0000320193"
    assert fetch.cik_10_chu_so("CIK0000320193") == "0000320193"


def test_url_thu_muc_ho_so_bo_dau_gach_o_phan_thu_muc():
    """
    Số accession xuất hiện hai dạng trong cùng một URL: phần thư mục bỏ dấu
    gạch, phần tên file giữ nguyên. Nhầm hai dạng là lỗi 404 khó đoán nhất
    khi làm việc với EDGAR.
    """
    url = fetch.url_thu_muc_ho_so("0000320193", "0000320193-25-000123")

    assert url.endswith("/320193/000032019325000123")


def test_chon_ho_so_loc_dung_loai_va_dung_so_luong():
    submissions = {
        "filings": {
            "recent": {
                "form": ["10-Q", "10-K", "8-K", "10-K", "10-K"],
                "accessionNumber": ["a", "b", "c", "d", "e"],
                "filingDate": ["1", "2", "3", "4", "5"],
            }
        }
    }

    ket_qua = fetch.chon_ho_so(submissions, form="10-K", n=2)

    assert [m["accession"] for m in ket_qua] == ["b", "d"]


def test_tim_file_linkbase():
    co = {"directory": {"item": [{"name": "x.htm"}, {"name": "abc_cal.xml"}]}}
    khong = {"directory": {"item": [{"name": "x.htm"}]}}

    assert fetch.tim_file_linkbase(co) == "abc_cal.xml"
    assert fetch.tim_file_linkbase(khong) is None


def test_thieu_SEC_USER_AGENT_thi_NEM_LOI_ngay(monkeypatch):
    """
    SEC chặn IP khi thiếu header này, và thông báo lỗi của họ không nói rõ
    nguyên nhân. Điền một User-Agent mặc định thì vừa vi phạm điều kiện dùng
    vừa khiến người dùng bị chặn mà không hiểu vì sao.
    """
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)

    with pytest.raises(RuntimeError, match="SEC_USER_AGENT"):
        fetch.user_agent()


def test_dry_run_khong_cham_mang_va_khong_tao_thu_muc(tmp_path, monkeypatch):
    """
    Đây là cách kiểm cấu hình trong container không có mạng. Nếu nó gọi mạng
    thì test này đỏ vì môi trường chứ không phải vì code sai.
    """

    def _cam(*_args, **_kwargs):
        raise AssertionError("dry-run không được chạm mạng")

    monkeypatch.setattr(fetch.urllib.request, "urlopen", _cam)
    dich = tmp_path / "chua_ton_tai"

    assert fetch.tai_ho_so("320193", n=2, out_dir=str(dich), dry_run=True) == []
    assert not dich.exists()


def test_bo_dieu_toc_ngu_dung_phan_con_thieu(monkeypatch):
    """
    Kiểm bằng đồng hồ GIẢ chứ không đo thời gian thật: độ phân giải bộ đếm
    của Windows đủ thô để một test ngủ vài mili giây đỏ ngẫu nhiên, và một
    test đỏ ngẫu nhiên thì tệ hơn không có test.

    Điều cần chốt là phép tính: ngủ đúng phần còn thiếu so với request
    TRƯỚC, không ngủ nguyên một chu kỳ sau mỗi lần gọi. Ngủ nguyên chu kỳ
    làm lượt tải chậm gấp đôi mà không an toàn hơn chút nào.
    """
    dong_ho = [1000.0]
    da_ngu = []

    monkeypatch.setattr(fetch.time, "monotonic", lambda: dong_ho[0])
    monkeypatch.setattr(fetch.time, "sleep", lambda giay: da_ngu.append(giay))

    dieu_toc = fetch._BoDieuToc(moi_giay=5.0)

    dieu_toc.cho()
    assert da_ngu == [], "request đầu tiên không có gì để chờ"

    dong_ho[0] += 0.05
    dieu_toc.cho()
    assert da_ngu == [pytest.approx(0.15)]

    dong_ho[0] += 10.0
    dieu_toc.cho()
    assert len(da_ngu) == 1, "đã trôi quá khoảng cách thì không ngủ nữa"
