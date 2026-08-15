"""
Monitoring & Observability

Thu thập số liệu của MỘT lượt xử lý document: thời gian từng giai đoạn,
số lần gọi VLM, số trang đã xử lý. Ghi ra data/output/metrics.jsonl —
mỗi dòng một lượt chạy, để sau này gộp lại phân tích.
"""

import json
import time
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
from pathlib import Path

METRICS_PATH = Path("data/output/metrics.jsonl")


class RunMetrics:
    def __init__(self, document: str):
        self.document=document
        self.started_at = datetime.now(timezone.utc)
        self._run_start=time.perf_counter()

        self.stages: dict[str, float] = {}
        self.counters: dict[str, int] = {}
        self.info: dict = {}

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

    def count(self, name:str, amount: int=1) -> None:
        self.counters[name] = self.counters.get(name, 0) + amount

    def set_info(self, **kwargs) -> None:
        self.info.update(kwargs)

    def as_dict(self) -> dict:
        return {
            "timestamp": self.started_at.isoformat(),
            "document": self.document,
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
        parts = [f"{data['total_seconds']}s tổng"]
 
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