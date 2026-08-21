"""
Monitoring & Observability

Thu thập số liệu của MỘT lượt xử lý document: thời gian từng giai đoạn,
số lần gọi VLM, số trang đã xử lý. Ghi ra data/output/metrics.jsonl —
mỗi dòng một lượt chạy, để sau này gộp lại phân tích.
"""

import hashlib
import json
import os
import subprocess
import threading
import time
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
from pathlib import Path

METRICS_PATH = Path("data/output/metrics.jsonl")

_commit_hash: str | None = None
_da_tra_commit = False


def bam_prompt(prompt: str) -> str:
    """
    Băm NỘI DUNG prompt, không phải số phiên bản.

    Số phiên bản đòi con người nhớ tăng nó, và người ta không nhớ. Một
    prompt bị sửa mà số phiên bản đứng yên là hai lượt chạy khác nhau
    trông như một, và đó đúng là thứ phá hỏng việc so sánh giữa các lần
    chạy mà không ai phát hiện.

    16 ký tự đầu của SHA-256 là đủ: ta chỉ cần phân biệt các phiên bản
    prompt của chính dự án này, không chống va chạm có chủ đích.
    """
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


def commit_hash() -> str | None:
    """
    Commit hash của mã đang chạy, hoặc None nếu không đọc được.

    Cache lại vì nó không đổi trong vòng đời một process, và gọi git cho
    mỗi tài liệu trong một lượt chạy 60 tài liệu là lãng phí không cần
    thiết.

    Trả None thay vì ném lỗi: chạy trong Docker không có .git là chuyện
    bình thường, và một dòng metrics thiếu commit hash vẫn hơn là một lượt
    chạy bị hỏng vì không lấy được nó.
    """
    global _commit_hash, _da_tra_commit

    if _da_tra_commit:
        return _commit_hash

    _da_tra_commit = True
    try:
        _commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        _commit_hash = None

    return _commit_hash


def thong_tin_tai_lap(
    model: str | None = None,
    temperature: float | None = None,
    n_samples: int | None = None,
    seed: int | None = None,
    prompt_hash: str | None = None,
    standard: str | None = None,
) -> dict:
    """
    Bộ trường tối thiểu để một lượt chạy tái lập lại được.

    Ghi cho MỌI lượt chạy, không chỉ lượt cuối. Lý do: khi một bảng kết
    quả trông lạ, câu hỏi đầu tiên luôn là "lượt đó chạy bằng gì" — và nếu
    chỉ lượt cuối có thông tin thì mọi lượt trước thành không dùng được.

    experiment_id đọc từ biến môi trường để runner thí nghiệm đặt được mà
    không phải luồn tham số qua cả pipeline. Rỗng nghĩa là lượt chạy lẻ,
    không thuộc thí nghiệm nào.

    Nhận prompt_hash đã băm sẵn chứ không nhận nguyên văn prompt: prompt
    được dựng bên trong nhánh trích xuất và không đi ngược ra tới đây, còn
    băm thì nhẹ và mang đi được. Băm ở đúng chỗ dựng prompt cũng đảm bảo
    băm đúng chuỗi ĐÃ GỬI, không phải một chuỗi dựng lại.
    """
    return {
        "experiment_id": os.getenv("EXPERIMENT_ID", ""),
        "commit": commit_hash(),
        "model": model,
        "temperature": temperature,
        "n_samples": n_samples,
        "seed": seed,
        "prompt_hash": prompt_hash,
        "standard": standard,
    }


class RunMetrics:
    def __init__(self, document: str):
        self.document = document
        self.started_at = datetime.now(timezone.utc)
        self._run_start = time.perf_counter()

        self.stages: dict[str, float] = {}
        self.counters: dict[str, int] = {}
        self.info: dict = {}

        # Kết cục của lượt chạy, người gọi đặt lại thành "ok"/"error" ở
        # cuối. Là field hạng nhất chứ không nhét vào info: người đọc
        # metrics.jsonl phải biết được dòng nào thất bại bằng một khoá có
        # sẵn, đừng bắt họ suy ra qua sự VẮNG MẶT của một khoá khác — ràng
        # buộc ngầm kiểu đó vỡ ngay lần đầu có ai thêm set_info() ở nhánh
        # mới. Nếu một dòng còn mang "running" nghĩa là process chết trước
        # khi kịp chạy finally.
        self.status = "running"

    @contextmanager
    def stage(self, name: str):
        """
        Đo thời gian một giai đoạn:

            with metrics.stage("vlm_call"):
                ...

        Dùng try/finally để thời gian vẫn được ghi cả khi bên trong ném
        lỗi — nếu không thì đúng những lượt chạy thất bại, thứ đáng phân
        tích nhất, lại là thứ không có số liệu.
        """
        start = time.perf_counter()

        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self.stages[name] = self.stages.get(name, 0.0) + elapsed

    def count(self, name: str, amount: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + amount

    def set_info(self, **kwargs) -> None:
        self.info.update(kwargs)

    def as_dict(self) -> dict:
        return {
            "timestamp": self.started_at.isoformat(),
            "document": self.document,
            "status": self.status,
            "total_seconds": round(time.perf_counter() - self._run_start, 2),
            "stages": {name: round(value, 2) for name, value in self.stages.items()},
            "counters": dict(self.counters),
            "info": dict(self.info),
        }

    def save(self, path: Path = METRICS_PATH) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(self.as_dict(), ensure_ascii=False) + "\n")

        except OSError as e:
            print(f"[WARNING] Không ghi được metrics: {e}")

    def summary(self) -> str:
        """Một dòng tóm tắt để in ra cuối lượt chạy."""
        data = self.as_dict()
        parts = [data["status"], f"{data['total_seconds']}s tổng"]

        for name, value in sorted(data["stages"].items(), key=lambda x: -x[1]):
            parts.append(f"{name} {value}s")

        for name, value in data["counters"].items():
            parts.append(f"{name}={value}")

        return " | ".join(parts)


def timer(metrics, name: str):
    """
    Đo stage khi có metrics, không làm gì khi metrics=None.

    Nhờ vậy các hàm trong pipeline vẫn chạy standalone (metrics=None)
    mà không phải viết if/else quanh mỗi khối with.
    """
    return metrics.stage(name) if metrics is not None else nullcontext()


# Bộ đếm tích lũy từ lúc process khởi động, phục vụ endpoint /metrics.
# Prometheus mong đợi counter cộng dồn theo vòng đời process chứ không
# phải số liệu của một lượt chạy — nó tự tính tốc độ thay đổi giữa các
# lần scrape. Nên RunMetrics (per-run, ghi ra file) và bảng này (toàn
# cục, giữ trong RAM) phục vụ hai mục đích khác nhau.
#
# Ba counter dưới đây khởi tạo sẵn bằng 0 chứ không đợi lượt chạy đầu tiên
# tạo ra chúng. Lý do nằm ở phía Prometheus: chưa có series thì
# rate(doc_ai_documents_error_total[5m]) trả về RỖNG, mọi alert dựng trên
# biểu thức đó không bao giờ bắn — hệ thống giám sát im lặng đúng vào lúc
# chưa từng có lượt chạy nào thành công. Một series phẳng ở 0 thì alert có
# cái để so sánh ngay từ lần scrape đầu tiên.
_totals: dict[str, float] = {
    "documents_total": 0,
    "documents_ok_total": 0,
    "documents_error_total": 0,
}

# api.py chạy route_document() trong threadpool, nên nhiều request có thể
# gọi merge_into_totals() cùng lúc. Phép cộng dồn dưới đây là
# read-modify-write, KHÔNG atomic: hai thread đọc cùng một giá trị cũ rồi
# cùng ghi đè thì mất một lượt đếm. Counter sai lệch âm thầm còn tệ hơn
# không có counter, vì không có cách nào phát hiện.
_totals_lock = threading.Lock()


def merge_into_totals(run: "RunMetrics") -> None:
    """Cộng số liệu của một lượt chạy vừa xong vào bộ đếm toàn cục."""
    data = run.as_dict()

    status = data["status"]
    status_key = f"documents_{status}_total"

    with _totals_lock:
        # documents_total đếm MỌI lượt chạy (ok + error), giữ nguyên ý nghĩa
        # cũ vì README và bước kiểm tra Prometheus đang dựa vào nó. Tỷ lệ lỗi
        # tính bằng documents_error_total chia cho nó.
        _totals["documents_total"] = _totals.get("documents_total", 0) + 1

        if status_key not in _totals:
            # Status ngoài dự kiến — "running" nghĩa là process chết trước cả
            # khối finally của route_document(). Vẫn đếm nó thành series
            # riêng và kêu to ra log: bỏ qua im lặng thì tổng các counter con
            # nhỏ hơn documents_total mà không chỗ nào giải thích khoản chênh.
            print(f"[WARNING] Lượt chạy có status ngoài dự kiến: {status!r}")

        _totals[status_key] = _totals.get(status_key, 0) + 1
        _totals["seconds_total"] = _totals.get("seconds_total", 0) + data["total_seconds"]

        for name, value in data["stages"].items():
            key = f"stage_{name}_seconds_total"
            _totals[key] = _totals.get(key, 0) + value

        for name, value in data["counters"].items():
            key = f"{name}_total"
            _totals[key] = _totals.get(key, 0) + value


def get_totals() -> dict[str, float]:
    # Copy trong lock: dict(_totals) duyệt qua dict, sẽ nổ RuntimeError
    # nếu một request khác chèn key mới giữa chừng.
    with _totals_lock:
        return dict(_totals)
