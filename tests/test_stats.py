"""测试工具统计模块"""

from lobster.core.stats import (
    ToolStats,
    ToolStatsTracker,
    stats_tracker,
    get_stats_tracker,
)


class TestToolStats:
    """测试工具统计"""

    def test_initial_stats(self):
        """测试初始统计"""
        stats = ToolStats()
        assert stats.total_calls == 0
        assert stats.successful_calls == 0
        assert stats.failed_calls == 0
        assert stats.total_duration_ms == 0.0

    def test_success_rate_zero(self):
        """测试成功率为零"""
        stats = ToolStats()
        assert stats.success_rate == 0.0

    def test_success_rate_calculation(self):
        """测试成功率计算"""
        stats = ToolStats()
        stats.total_calls = 10
        stats.successful_calls = 8
        assert stats.success_rate == 80.0

    def test_avg_duration_zero(self):
        """测试平均执行时间为零"""
        stats = ToolStats()
        assert stats.avg_duration_ms == 0.0

    def test_avg_duration_calculation(self):
        """测试平均执行时间计算"""
        stats = ToolStats()
        stats.total_calls = 5
        stats.total_duration_ms = 100.0
        assert stats.avg_duration_ms == 20.0

    def test_to_dict(self):
        """测试转换为字典"""
        stats = ToolStats()
        stats.total_calls = 10
        stats.successful_calls = 8
        stats.failed_calls = 2
        stats.total_duration_ms = 100.0
        stats.min_duration_ms = 5.0
        stats.max_duration_ms = 20.0

        result = stats.to_dict()
        assert result["total_calls"] == 10
        assert result["successful_calls"] == 8
        assert result["failed_calls"] == 2
        assert result["success_rate"] == "80.0%"
        assert result["avg_duration_ms"] == 10.0


class TestToolStatsTracker:
    """测试统计追踪器"""

    def test_singleton(self):
        """测试单例模式"""
        tracker1 = ToolStatsTracker()
        tracker2 = ToolStatsTracker()
        assert tracker1 is tracker2

    def test_get_stats_tracker(self):
        """测试获取追踪器实例"""
        tracker = get_stats_tracker()
        assert tracker is stats_tracker

    def test_record_successful_call(self):
        """测试记录成功调用"""
        tracker = ToolStatsTracker()
        tracker.clear_stats()
        tracker.record_call("test_tool", True, 100.0)

        stats = tracker.get_stats("test_tool")
        assert stats is not None
        assert stats.total_calls == 1
        assert stats.successful_calls == 1
        assert stats.failed_calls == 0
        assert stats.total_duration_ms == 100.0

    def test_record_failed_call(self):
        """测试记录失败调用"""
        tracker = ToolStatsTracker()
        tracker.clear_stats()
        tracker.record_call("test_tool", False, 50.0, "Error message")

        stats = tracker.get_stats("test_tool")
        assert stats is not None
        assert stats.total_calls == 1
        assert stats.successful_calls == 0
        assert stats.failed_calls == 1
        assert "Error message" in stats.errors

    def test_record_multiple_calls(self):
        """测试记录多次调用"""
        tracker = ToolStatsTracker()
        tracker.clear_stats()
        tracker.record_call("tool_a", True, 100.0)
        tracker.record_call("tool_a", True, 200.0)
        tracker.record_call("tool_b", False, 50.0)

        all_stats = tracker.get_all_stats()
        assert len(all_stats) == 2

        stats_a = tracker.get_stats("tool_a")
        assert stats_a.total_calls == 2
        assert stats_a.successful_calls == 2

        stats_b = tracker.get_stats("tool_b")
        assert stats_b.total_calls == 1
        assert stats_b.failed_calls == 1

    def test_min_max_duration(self):
        """测试最小最大执行时间"""
        tracker = ToolStatsTracker()
        tracker.clear_stats()
        tracker.record_call("test_tool", True, 100.0)
        tracker.record_call("test_tool", True, 50.0)
        tracker.record_call("test_tool", True, 200.0)

        stats = tracker.get_stats("test_tool")
        assert stats.min_duration_ms == 50.0
        assert stats.max_duration_ms == 200.0

    def test_get_summary(self):
        """测试获取统计摘要"""
        tracker = ToolStatsTracker()
        tracker.clear_stats()
        tracker.record_call("tool_a", True, 100.0)
        tracker.record_call("tool_b", False, 50.0)

        summary = tracker.get_summary()
        assert summary["total_tools"] == 2
        assert summary["total_calls"] == 2
        assert summary["total_successful"] == 1
        assert summary["total_failed"] == 1

    def test_get_most_used(self):
        """测试获取最常用工具"""
        tracker = ToolStatsTracker()
        tracker.clear_stats()
        tracker.record_call("tool_a", True, 100.0)
        tracker.record_call("tool_a", True, 100.0)
        tracker.record_call("tool_a", True, 100.0)
        tracker.record_call("tool_b", True, 100.0)

        summary = tracker.get_summary()
        most_used = summary["most_used"]
        assert len(most_used) > 0
        assert most_used[0]["name"] == "tool_a"
        assert most_used[0]["calls"] == 3

    def test_get_slowest(self):
        """测试获取最慢工具"""
        tracker = ToolStatsTracker()
        tracker.clear_stats()
        tracker.record_call("fast_tool", True, 10.0)
        tracker.record_call("slow_tool", True, 1000.0)

        summary = tracker.get_summary()
        slowest = summary["slowest"]
        assert len(slowest) > 0
        assert slowest[0]["name"] == "slow_tool"

    def test_get_recent_calls(self):
        """测试获取最近调用"""
        tracker = ToolStatsTracker()
        tracker.clear_stats()
        tracker.record_call("tool_a", True, 100.0)
        tracker.record_call("tool_b", False, 50.0, "Error")

        recent = tracker.get_recent_calls(limit=10)
        assert len(recent) == 2
        assert recent[0]["tool_name"] == "tool_a"
        assert recent[0]["success"] is True
        assert recent[1]["tool_name"] == "tool_b"
        assert recent[1]["success"] is False

    def test_clear_stats(self):
        """测试清除统计"""
        tracker = ToolStatsTracker()
        tracker.record_call("test_tool", True, 100.0)
        tracker.clear_stats()

        stats = tracker.get_stats("test_tool")
        assert stats is None

        summary = tracker.get_summary()
        assert summary["total_tools"] == 0
