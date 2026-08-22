"""
Tải hồ sơ 10-K và calculation linkbase từ EDGAR.

CẢNH BÁO — ĐỌC TRƯỚC KHI CHẠY:

Container của repo này KHÔNG có mạng tới sec.gov. Module này là SCRIPT CHO
NGƯỜI DÙNG CHẠY TRÊN MÁY HỌ, không phải thứ pipeline tự gọi. Đừng cố chạy
nó trong CI hay trong Docker rồi kết luận EDGAR hỏng.

SEC ra hai điều kiện bắt buộc, vi phạm là chặn IP chứ không phải trả lỗi:

  1. Header `User-Agent` phải có tên thật và email liên hệ. Module này ĐỌC
     từ biến môi trường `SEC_USER_AGENT` và NÉM LỖI khi thiếu, thay vì điền
     một giá trị mặc định — một User-Agent giả mạo vừa vi phạm điều kiện
     dùng của SEC vừa khiến IP của người dùng bị chặn mà họ không hiểu vì
     sao.
  2. Tối đa 10 request mỗi giây. Ở đây đặt trần 5 để còn biên an toàn, vì
     bị chặn IP tốn nhiều thời gian hơn hẳn phần tiết kiệm được.

Chạy:

    export SEC_USER_AGENT="Tên của bạn your@email.com"
    python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --out data/xbrl
    python src/eval/xbrl_tier/fetch.py --cik 0000320193 --n 3 --dry-run
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

BASE_SUBMISSIONS = "https://data.sec.gov/submissions"
BASE_COMPANYFACTS = "https://data.sec.gov/api/xbrl/companyfacts"
BASE_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"

# Trần request mỗi giây, đặt dưới mức SEC cho phép để còn biên.
SO_REQUEST_MOI_GIAY = 5.0


class _BoDieuToc:
    """
    Giữ nhịp request không vượt trần.

    Ngủ theo khoảng cách tới request TRƯỚC chứ không ngủ một khoảng cố định
    sau mỗi lần gọi: phần lớn thời gian một request là chờ mạng, nên ngủ
    thêm nguyên một chu kỳ nữa sẽ làm lượt tải chậm gấp đôi mà không an
    toàn hơn chút nào.
    """

    def __init__(self, moi_giay: float = SO_REQUEST_MOI_GIAY):
        self.khoang_cach = 1.0 / moi_giay
        self.lan_truoc = 0.0

    def cho(self) -> None:
        con_thieu = self.khoang_cach - (time.monotonic() - self.lan_truoc)
        if con_thieu > 0:
            time.sleep(con_thieu)
        self.lan_truoc = time.monotonic()


def user_agent() -> str:
    """
    User-Agent lấy từ biến môi trường, không có mặc định.

    Ném lỗi ngay thay vì để request đầu tiên trả 403: thông báo của SEC khi
    thiếu header không nói rõ nguyên nhân, còn dòng lỗi ở đây thì nói.
    """
    gia_tri = os.getenv("SEC_USER_AGENT", "").strip()
    if not gia_tri:
        raise RuntimeError(
            "Thiếu biến môi trường SEC_USER_AGENT. SEC yêu cầu User-Agent có "
            'tên thật và email, ví dụ: SEC_USER_AGENT="Tên bạn ban@email.com"'
        )
    return gia_tri


def cik_10_chu_so(cik: str) -> str:
    """CIK trong URL của SEC luôn là 10 chữ số có đệm 0 ở đầu."""
    return str(cik).strip().lstrip("CIK").zfill(10)


def url_submissions(cik: str) -> str:
    return f"{BASE_SUBMISSIONS}/CIK{cik_10_chu_so(cik)}.json"


def url_companyfacts(cik: str) -> str:
    return f"{BASE_COMPANYFACTS}/CIK{cik_10_chu_so(cik)}.json"


def url_thu_muc_ho_so(cik: str, accession: str) -> str:
    """
    Thư mục chứa mọi file của một hồ sơ.

    Số accession xuất hiện hai dạng trong cùng một URL: phần thư mục bỏ dấu
    gạch, phần tên file giữ nguyên. Nhầm hai dạng này là lỗi 404 khó đoán
    nhất khi làm việc với EDGAR.
    """
    return f"{BASE_ARCHIVES}/{int(cik_10_chu_so(cik))}/{accession.replace('-', '')}"


def _tai(url: str, dieu_toc: _BoDieuToc) -> bytes:
    dieu_toc.cho()
    yeu_cau = urllib.request.Request(url, headers={"User-Agent": user_agent()})
    with urllib.request.urlopen(yeu_cau, timeout=30) as tra_ve:
        return tra_ve.read()


def chon_ho_so(submissions: dict, form: str = "10-K", n: int = 5) -> list[dict]:
    """
    Lọc n hồ sơ gần nhất đúng loại từ JSON submissions.

    Tách khỏi phần tải để test được mà không cần mạng — cấu trúc JSON của
    SEC là thứ dễ đổi và cũng là thứ dễ đọc nhầm nhất ở đây.
    """
    gan_day = submissions.get("filings", {}).get("recent", {})
    cac_form = gan_day.get("form", [])
    accession = gan_day.get("accessionNumber", [])
    ngay = gan_day.get("filingDate", [])

    ket_qua = []
    for i, ten_form in enumerate(cac_form):
        if ten_form != form:
            continue
        ket_qua.append({"accession": accession[i], "filing_date": ngay[i]})
        if len(ket_qua) == n:
            break
    return ket_qua


def tim_file_linkbase(index: dict) -> str | None:
    """
    Tên file calculation linkbase trong index.json của một hồ sơ.

    Quy ước đặt tên của SEC là hậu tố `_cal.xml`. Trả None khi hồ sơ không
    có linkbase — chuyện có thật với hồ sơ cũ hoặc hồ sơ nộp thiếu, và khi
    đó tài liệu đó không dùng được cho tầng này. Nói ra bằng None để nơi gọi
    bỏ qua nó một cách tường minh.
    """
    for muc in index.get("directory", {}).get("item", []):
        ten = muc.get("name", "")
        if ten.endswith("_cal.xml"):
            return ten
    return None


def tai_ho_so(
    cik: str,
    n: int = 5,
    form: str = "10-K",
    out_dir: str = "data/xbrl",
    dry_run: bool = False,
) -> list[dict]:
    """
    Tải companyfacts và calculation linkbase của n hồ sơ gần nhất.

    `dry_run` in ra danh sách URL sẽ gọi rồi dừng, KHÔNG chạm mạng. Đây là
    cách kiểm cấu hình trong container không có mạng, và cũng là cách xem
    trước mình sắp gọi SEC bao nhiêu lần trước khi thật sự gọi.
    """
    thu_muc = Path(out_dir)
    dieu_toc = _BoDieuToc()

    if dry_run:
        print(f"[dry-run] {url_submissions(cik)}")
        print(f"[dry-run] {url_companyfacts(cik)}")
        print(f"[dry-run] {n} hồ sơ {form}, mỗi hồ sơ 2 request nữa (index + cal.xml)")
        print(f"[dry-run] ghi vào {thu_muc}")
        return []

    thu_muc.mkdir(parents=True, exist_ok=True)

    facts = _tai(url_companyfacts(cik), dieu_toc)
    (thu_muc / f"CIK{cik_10_chu_so(cik)}_facts.json").write_bytes(facts)

    submissions = json.loads(_tai(url_submissions(cik), dieu_toc))
    ho_so = chon_ho_so(submissions, form=form, n=n)

    da_tai = []
    for muc in ho_so:
        goc = url_thu_muc_ho_so(cik, muc["accession"])
        index = json.loads(_tai(f"{goc}/index.json", dieu_toc))

        ten_cal = tim_file_linkbase(index)
        if ten_cal is None:
            print(f"BỎ QUA {muc['accession']}: hồ sơ không có calculation linkbase")
            continue

        noi_dung = _tai(f"{goc}/{ten_cal}", dieu_toc)
        dich = thu_muc / f"{muc['accession']}_cal.xml"
        dich.write_bytes(noi_dung)
        da_tai.append({**muc, "cal_path": str(dich)})

    return da_tai


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")

    bo_phan_tich = argparse.ArgumentParser(description=__doc__)
    bo_phan_tich.add_argument("--cik", required=True, help="CIK của doanh nghiệp")
    bo_phan_tich.add_argument("--n", type=int, default=5, help="số hồ sơ gần nhất")
    bo_phan_tich.add_argument("--form", default="10-K")
    bo_phan_tich.add_argument("--out", default="data/xbrl")
    bo_phan_tich.add_argument(
        "--dry-run",
        action="store_true",
        help="in ra URL sẽ gọi rồi dừng, không chạm mạng",
    )
    doi_so = bo_phan_tich.parse_args()

    ket_qua = tai_ho_so(
        cik=doi_so.cik,
        n=doi_so.n,
        form=doi_so.form,
        out_dir=doi_so.out,
        dry_run=doi_so.dry_run,
    )
    for muc in ket_qua:
        print(f"{muc['filing_date']}  {muc['accession']}  {muc['cal_path']}")


if __name__ == "__main__":
    main()
