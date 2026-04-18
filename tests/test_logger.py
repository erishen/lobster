"""测试日志模块"""

import pytest
import logging
from unittest.mock import patch, MagicMock

from lobster.core.logger import LobsterLogger, logger, get_logger


class TestLobsterLogger:
    """测试 Lobster 日志器"""

    def test_singleton(self):
        """测试单例模式"""
        logger1 = LobsterLogger()
        logger2 = LobsterLogger()
        assert logger1 is logger2

    def test_get_logger(self):
        """测试获取日志实例"""
        result = get_logger()
        assert result is logger

    def test_logger_has_handlers(self):
        """测试日志器有处理器"""
        assert len(logger._logger.handlers) >= 2

    def test_debug_method(self):
        """测试 debug 方法"""
        with patch.object(logger._logger, "debug") as mock_debug:
            logger.debug("test debug message")
            mock_debug.assert_called_once_with("test debug message")

    def test_info_method(self):
        """测试 info 方法"""
        with patch.object(logger._logger, "info") as mock_info:
            logger.info("test info message")
            mock_info.assert_called_once_with("test info message")

    def test_warning_method(self):
        """测试 warning 方法"""
        with patch.object(logger._logger, "warning") as mock_warning:
            logger.warning("test warning message")
            mock_warning.assert_called_once_with("test warning message")

    def test_error_method(self):
        """测试 error 方法"""
        with patch.object(logger._logger, "error") as mock_error:
            logger.error("test error message")
            mock_error.assert_called_once_with("test error message")

    def test_critical_method(self):
        """测试 critical 方法"""
        with patch.object(logger._logger, "critical") as mock_critical:
            logger.critical("test critical message")
            mock_critical.assert_called_once_with("test critical message")

    def test_exception_method(self):
        """测试 exception 方法"""
        with patch.object(logger._logger, "exception") as mock_exception:
            logger.exception("test exception message")
            mock_exception.assert_called_once_with("test exception message")

    def test_tool_call(self):
        """测试工具调用日志"""
        with patch.object(logger._logger, "info") as mock_info:
            logger.tool_call("test_tool", {"param": "value"})
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "[Tool]" in call_args
            assert "test_tool" in call_args

    def test_tool_result_success(self):
        """测试工具成功结果日志"""
        with patch.object(logger._logger, "info") as mock_info:
            logger.tool_result("test_tool", True, {"result": "success"})
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "[Tool]" in call_args
            assert "test_tool" in call_args
            assert "✓" in call_args

    def test_tool_result_failure(self):
        """测试工具失败结果日志"""
        with patch.object(logger._logger, "info") as mock_info:
            logger.tool_result("test_tool", False, "Error message")
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "[Tool]" in call_args
            assert "test_tool" in call_args
            assert "✗" in call_args

    def test_api_request(self):
        """测试 API 请求日志"""
        with patch.object(logger._logger, "info") as mock_info:
            logger.api_request("GET", "/api/test", 200)
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "[API]" in call_args
            assert "GET" in call_args
            assert "/api/test" in call_args
            assert "200" in call_args

    def test_performance_fast(self):
        """测试快速操作性能日志"""
        with patch.object(logger._logger, "debug") as mock_debug:
            logger.performance("test_operation", 500.0)
            mock_debug.assert_called_once()
            call_args = mock_debug.call_args[0][0]
            assert "[Perf]" in call_args
            assert "test_operation" in call_args

    def test_performance_slow(self):
        """测试慢操作性能日志"""
        with patch.object(logger._logger, "warning") as mock_warning:
            logger.performance("test_operation", 1500.0)
            mock_warning.assert_called_once()
            call_args = mock_warning.call_args[0][0]
            assert "[Perf]" in call_args
            assert "slow" in call_args

    def test_result_truncation(self):
        """测试结果截断"""
        long_result = {"data": "x" * 200}
        with patch.object(logger._logger, "info") as mock_info:
            logger.tool_result("test_tool", True, long_result)
            call_args = mock_info.call_args[0][0]
            assert len(call_args) < 300
