"""工具使用统计模块

追踪工具调用频率、成功率、执行时间等指标
"""

from __future__ import annotations

import json
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


STATS_DIR = Path.home() / ".lobster" / "stats"
STATS_DIR.mkdir(parents=True, exist_ok=True)
STATS_FILE = STATS_DIR / "tool_stats.json"


@dataclass
class ToolCallRecord:
    """工具调用记录"""

    tool_name: str
    timestamp: float
    success: bool
    duration_ms: float
    error: Optional[str] = None


@dataclass
class ToolStats:
    """单个工具的统计信息"""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    last_called: Optional[float] = None
    errors: Dict[str, int] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls * 100

    @property
    def avg_duration_ms(self) -> float:
        """平均执行时间"""
        if self.total_calls == 0:
            return 0.0
        return self.total_duration_ms / self.total_calls

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": f"{self.success_rate:.1f}%",
            "total_duration_ms": round(self.total_duration_ms, 2),
            "avg_duration_ms": round(self.avg_duration_ms, 2),
            "min_duration_ms": round(self.min_duration_ms, 2)
            if self.min_duration_ms != float("inf")
            else 0,
            "max_duration_ms": round(self.max_duration_ms, 2),
            "last_called": datetime.fromtimestamp(self.last_called).isoformat()
            if self.last_called
            else None,
            "errors": self.errors,
        }


class ToolStatsTracker:
    """工具统计追踪器"""

    _instance: Optional["ToolStatsTracker"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self._stats: Dict[str, ToolStats] = defaultdict(ToolStats)
        self._recent_calls: List[ToolCallRecord] = []
        self._max_recent_calls = 100
        self._load_stats()

    def _load_stats(self):
        """从文件加载统计数据"""
        if STATS_FILE.exists():
            try:
                with open(STATS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for tool_name, stats_data in data.get("tools", {}).items():
                        stats = ToolStats()
                        stats.total_calls = stats_data.get("total_calls", 0)
                        stats.successful_calls = stats_data.get("successful_calls", 0)
                        stats.failed_calls = stats_data.get("failed_calls", 0)
                        stats.total_duration_ms = stats_data.get("total_duration_ms", 0.0)
                        stats.min_duration_ms = stats_data.get("min_duration_ms", float("inf"))
                        stats.max_duration_ms = stats_data.get("max_duration_ms", 0.0)
                        stats.last_called = stats_data.get("last_called")
                        stats.errors = stats_data.get("errors", {})
                        self._stats[tool_name] = stats
            except Exception:
                pass

    def _save_stats(self):
        """保存统计数据到文件"""
        try:
            data = {
                "tools": {name: asdict(stats) for name, stats in self._stats.items()},
                "updated_at": datetime.now().isoformat(),
            }
            with open(STATS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def record_call(
        self,
        tool_name: str,
        success: bool,
        duration_ms: float,
        error: Optional[str] = None,
    ):
        """记录工具调用"""
        stats = self._stats[tool_name]
        stats.total_calls += 1
        stats.total_duration_ms += duration_ms
        stats.last_called = time.time()

        if duration_ms < stats.min_duration_ms:
            stats.min_duration_ms = duration_ms
        if duration_ms > stats.max_duration_ms:
            stats.max_duration_ms = duration_ms

        if success:
            stats.successful_calls += 1
        else:
            stats.failed_calls += 1
            if error:
                error_key = error[:50]
                stats.errors[error_key] = stats.errors.get(error_key, 0) + 1

        record = ToolCallRecord(
            tool_name=tool_name,
            timestamp=time.time(),
            success=success,
            duration_ms=duration_ms,
            error=error,
        )
        self._recent_calls.append(record)
        if len(self._recent_calls) > self._max_recent_calls:
            self._recent_calls = self._recent_calls[-self._max_recent_calls :]

        self._save_stats()

    def get_stats(self, tool_name: str) -> Optional[ToolStats]:
        """获取单个工具的统计信息"""
        return self._stats.get(tool_name)

    def get_all_stats(self) -> Dict[str, ToolStats]:
        """获取所有工具的统计信息"""
        return dict(self._stats)

    def get_summary(self) -> Dict[str, Any]:
        """获取统计摘要"""
        total_calls = sum(s.total_calls for s in self._stats.values())
        total_successful = sum(s.successful_calls for s in self._stats.values())
        total_failed = sum(s.failed_calls for s in self._stats.values())
        total_duration = sum(s.total_duration_ms for s in self._stats.values())

        return {
            "total_tools": len(self._stats),
            "total_calls": total_calls,
            "total_successful": total_successful,
            "total_failed": total_failed,
            "success_rate": f"{(total_successful / total_calls * 100) if total_calls > 0 else 0:.1f}%",
            "total_duration_ms": round(total_duration, 2),
            "avg_duration_ms": round(total_duration / total_calls, 2) if total_calls > 0 else 0,
            "most_used": self._get_most_used(5),
            "slowest": self._get_slowest(5),
        }

    def _get_most_used(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取使用最多的工具"""
        sorted_tools = sorted(self._stats.items(), key=lambda x: x[1].total_calls, reverse=True)
        return [{"name": name, "calls": stats.total_calls} for name, stats in sorted_tools[:limit]]

    def _get_slowest(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取执行最慢的工具"""
        sorted_tools = sorted(self._stats.items(), key=lambda x: x[1].avg_duration_ms, reverse=True)
        return [
            {"name": name, "avg_duration_ms": round(stats.avg_duration_ms, 2)}
            for name, stats in sorted_tools[:limit]
            if stats.total_calls > 0
        ]

    def get_recent_calls(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取最近的调用记录"""
        return [
            {
                "tool_name": r.tool_name,
                "timestamp": datetime.fromtimestamp(r.timestamp).isoformat(),
                "success": r.success,
                "duration_ms": round(r.duration_ms, 2),
                "error": r.error,
            }
            for r in self._recent_calls[-limit:]
        ]

    def clear_stats(self):
        """清除所有统计数据"""
        self._stats.clear()
        self._recent_calls.clear()
        self._save_stats()


stats_tracker = ToolStatsTracker()


def get_stats_tracker() -> ToolStatsTracker:
    """获取统计追踪器实例"""
    return stats_tracker
