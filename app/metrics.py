from __future__ import annotations

import statistics
import threading
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class Metric:
    op: str  # 'tts' or 'stt'
    ms: float
    ok: bool
    at: float  # epoch seconds
    meta: Dict[str, Any]


class Metrics:
    def __init__(self, capacity: int = 200) -> None:
        self._buf: List[Metric] = []
        self._cap = capacity
        self._lock = threading.Lock()

    def record(self, op: str, ms: float, ok: bool, **meta: Any) -> None:
        m = Metric(op=op, ms=ms, ok=ok, at=time.time(), meta=meta)
        with self._lock:
            self._buf.append(m)
            if len(self._buf) > self._cap:
                # keep last N
                self._buf = self._buf[-self._cap :]

    def recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            items = list(self._buf[-limit:])
        return [self._to_dict(x) for x in reversed(items)]

    def summary(self) -> Dict[str, Any]:
        with self._lock:
            buf = list(self._buf)
        by_op: Dict[str, List[Metric]] = {"tts": [], "stt": []}
        for m in buf:
            by_op.setdefault(m.op, []).append(m)
        def stats(items: List[Metric]) -> Dict[str, Any]:
            if not items:
                return {"count": 0, "ok": 0, "avg_ms": None, "p95_ms": None}
            ms = [i.ms for i in items]
            ok = sum(1 for i in items if i.ok)
            p95 = statistics.quantiles(ms, n=20)[-1] if len(ms) >= 2 else ms[0]
            return {"count": len(items), "ok": ok, "avg_ms": sum(ms) / len(ms), "p95_ms": p95}
        return {op: stats(items) for op, items in by_op.items()}

    @staticmethod
    def _to_dict(m: Metric) -> Dict[str, Any]:
        d = asdict(m)
        return d


metrics = Metrics()

