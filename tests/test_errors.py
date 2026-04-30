"""测试错误处理模块"""

from lobster.core.errors import (
    ErrorCode,
    LobsterError,
    error_response,
    success_response,
)


class TestErrorCode:
    """测试错误码"""

    def test_error_code_values(self):
        """测试错误码值"""
        assert ErrorCode.SUCCESS.value == 0
        assert ErrorCode.UNKNOWN_ERROR.value == 1
        assert ErrorCode.FILE_NOT_FOUND.value == 100
        assert ErrorCode.NETWORK_ERROR.value == 200
        assert ErrorCode.TOOL_NOT_FOUND.value == 600

    def test_error_code_names(self):
        """测试错误码名称"""
        assert ErrorCode.FILE_NOT_FOUND.name == "FILE_NOT_FOUND"
        assert ErrorCode.TOOL_NOT_FOUND.name == "TOOL_NOT_FOUND"


class TestLobsterError:
    """测试 LobsterError 异常"""

    def test_basic_error(self):
        """测试基本错误"""
        error = LobsterError(ErrorCode.FILE_NOT_FOUND)
        assert error.code == ErrorCode.FILE_NOT_FOUND
        assert error.message == "文件不存在"
        assert error.details == {}

    def test_custom_message(self):
        """测试自定义消息"""
        error = LobsterError(ErrorCode.FILE_NOT_FOUND, "自定义错误消息")
        assert error.message == "自定义错误消息"

    def test_with_details(self):
        """测试带详情的错误"""
        error = LobsterError(
            ErrorCode.TOOL_NOT_FOUND,
            "工具不存在",
            {"tool_name": "test_tool"},
        )
        assert error.details == {"tool_name": "test_tool"}

    def test_to_dict(self):
        """测试转换为字典"""
        error = LobsterError(
            ErrorCode.FILE_NOT_FOUND,
            "文件不存在",
            {"path": "/tmp/test.txt"},
        )
        result = error.to_dict()
        assert result["success"] is False
        assert result["error"]["code"] == 100
        assert result["error"]["name"] == "FILE_NOT_FOUND"
        assert result["error"]["message"] == "文件不存在"
        assert result["error"]["details"]["path"] == "/tmp/test.txt"

    def test_str_representation(self):
        """测试字符串表示"""
        error = LobsterError(ErrorCode.FILE_NOT_FOUND, "文件不存在")
        assert str(error) == "[FILE_NOT_FOUND] 文件不存在"


class TestHelperFunctions:
    """测试辅助函数"""

    def test_error_response(self):
        """测试错误响应"""
        result = error_response(
            ErrorCode.FILE_NOT_FOUND,
            "文件不存在",
            {"path": "/tmp/test.txt"},
        )
        assert result["success"] is False
        assert result["error"]["code"] == ErrorCode.FILE_NOT_FOUND.value

    def test_success_response(self):
        """测试成功响应"""
        result = success_response({"data": "test"})
        assert result["success"] is True
        assert result["result"]["data"] == "test"
        assert "duration_ms" not in result

    def test_success_response_with_duration(self):
        """测试带执行时间的成功响应"""
        result = success_response({"data": "test"}, duration_ms=100.5)
        assert result["success"] is True
        assert result["duration_ms"] == 100.5

    def test_success_response_with_cached(self):
        """测试带缓存标记的成功响应"""
        result = success_response({"data": "test"}, cached=True)
        assert result["success"] is True
        assert result["cached"] is True
