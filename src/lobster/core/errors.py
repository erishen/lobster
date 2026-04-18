"""错误处理模块

提供统一的错误码和错误信息管理
"""

from enum import Enum
from typing import Optional, Dict, Any


class ErrorCode(Enum):
    """错误码枚举"""

    SUCCESS = 0
    UNKNOWN_ERROR = 1

    FILE_NOT_FOUND = 100
    FILE_TOO_LARGE = 101
    FILE_READ_ERROR = 102
    FILE_WRITE_ERROR = 103
    FILE_DELETE_ERROR = 104
    PATH_INVALID = 105
    PATH_NOT_ALLOWED = 106

    NETWORK_ERROR = 200
    URL_INVALID = 201
    URL_BLOCKED = 202
    REQUEST_TIMEOUT = 203
    REQUEST_FAILED = 204

    COMMAND_BLOCKED = 300
    COMMAND_TIMEOUT = 301
    COMMAND_FAILED = 302

    CODE_DANGEROUS = 400
    CODE_TIMEOUT = 401
    CODE_ERROR = 402

    JSON_PARSE_ERROR = 500
    TEXT_PROCESS_ERROR = 501
    CALCULATE_ERROR = 502

    TOOL_NOT_FOUND = 600
    TOOL_INVALID_PARAMS = 601
    TOOL_EXECUTION_ERROR = 602

    AUTH_FAILED = 700
    AUTH_MISSING = 701


ERROR_MESSAGES: Dict[ErrorCode, str] = {
    ErrorCode.SUCCESS: "操作成功",
    ErrorCode.UNKNOWN_ERROR: "未知错误",
    ErrorCode.FILE_NOT_FOUND: "文件不存在",
    ErrorCode.FILE_TOO_LARGE: "文件过大",
    ErrorCode.FILE_READ_ERROR: "文件读取失败",
    ErrorCode.FILE_WRITE_ERROR: "文件写入失败",
    ErrorCode.FILE_DELETE_ERROR: "文件删除失败",
    ErrorCode.PATH_INVALID: "路径无效",
    ErrorCode.PATH_NOT_ALLOWED: "路径访问被禁止",
    ErrorCode.NETWORK_ERROR: "网络错误",
    ErrorCode.URL_INVALID: "URL 无效",
    ErrorCode.URL_BLOCKED: "URL 被禁止访问",
    ErrorCode.REQUEST_TIMEOUT: "请求超时",
    ErrorCode.REQUEST_FAILED: "请求失败",
    ErrorCode.COMMAND_BLOCKED: "命令被禁止",
    ErrorCode.COMMAND_TIMEOUT: "命令执行超时",
    ErrorCode.COMMAND_FAILED: "命令执行失败",
    ErrorCode.CODE_DANGEROUS: "代码包含危险操作",
    ErrorCode.CODE_TIMEOUT: "代码执行超时",
    ErrorCode.CODE_ERROR: "代码执行错误",
    ErrorCode.JSON_PARSE_ERROR: "JSON 解析错误",
    ErrorCode.TEXT_PROCESS_ERROR: "文本处理错误",
    ErrorCode.CALCULATE_ERROR: "计算错误",
    ErrorCode.TOOL_NOT_FOUND: "工具不存在",
    ErrorCode.TOOL_INVALID_PARAMS: "工具参数无效",
    ErrorCode.TOOL_EXECUTION_ERROR: "工具执行错误",
    ErrorCode.AUTH_FAILED: "认证失败",
    ErrorCode.AUTH_MISSING: "缺少认证信息",
}


class LobsterError(Exception):
    """Lobster 错误基类"""

    def __init__(
        self,
        code: ErrorCode,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message or ERROR_MESSAGES.get(code, "未知错误")
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": False,
            "error": {
                "code": self.code.value,
                "name": self.code.name,
                "message": self.message,
                "details": self.details,
            },
        }

    def __str__(self) -> str:
        return f"[{self.code.name}] {self.message}"


def error_response(
    code: ErrorCode,
    message: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """生成错误响应"""
    error = LobsterError(code, message, details)
    return error.to_dict()


def success_response(
    result: Any,
    duration_ms: Optional[float] = None,
    cached: bool = False,
) -> Dict[str, Any]:
    """生成成功响应"""
    response = {
        "success": True,
        "result": result,
    }
    if duration_ms is not None:
        response["duration_ms"] = duration_ms
    if cached:
        response["cached"] = True
    return response
