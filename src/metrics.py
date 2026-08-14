"""
Monitoring & Observability

Thu thập số liệu của MỘT lượt xử lý document: thời gian từng giai đoạn,
số lần gọi VLM, số trang đã xử lý. Ghi ra data/output/metrics.jsonl —
mỗi dòng một lượt chạy, để sau này gộp lại phân tích.
"""

import json
import time
from contextlib import contextmanager
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
        # phần chạy trước khi vào khối with
        yield
        # phần chạy sau khi ra khỏi khối with