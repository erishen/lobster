"""工具注册表 - 供 OpenClaw 龙虾助理调用

专注于 AI 助理需要的扩展能力：
- 文件操作
- 网络请求
- 代码执行
- 系统交互
- 数据处理
"""

from __future__ import annotations

import subprocess
import sys
import json
import time
import functools
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from lobster.core.errors import (
    ErrorCode,
    LobsterError,
    error_response,
    success_response,
)
from lobster.core.stats import stats_tracker
from lobster.core.cache import tool_cache
from lobster.core.investment import register_investment_tools
from lobster.core.serena_client import register_serena_tools


def measure_performance(func):
    """性能监控装饰器"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000

            from lobster.core.logger import logger

            logger.performance(func.__name__, duration_ms)
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            from lobster.core.logger import logger

            logger.error(f"{func.__name__} failed after {duration_ms:.2f}ms: {str(e)}")
            raise

    return wrapper


@dataclass
class Tool:
    """工具定义"""

    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable
    category: str = "general"


@dataclass
class SecurityConfig:
    """安全配置"""

    allowed_base_dirs: List[str] = field(default_factory=lambda: ["."])
    blocked_commands: List[str] = field(
        default_factory=lambda: [
            "rm -rf /",
            "rm -rf /*",
            "mkfs",
            "dd if=",
            ":(){ :|:& };:",
            "chmod 777 /",
            "chown -R",
            "wget",
            "curl -X DELETE",
        ]
    )
    allowed_commands: Optional[List[str]] = None
    max_file_size: int = 10 * 1024 * 1024
    max_content_size: int = 1 * 1024 * 1024


security_config = SecurityConfig()


def validate_path(path: str, allow_create: bool = False) -> Dict[str, Any]:
    """验证路径安全性"""
    try:
        file_path = Path(path).resolve()
    except Exception as e:
        return {
            "valid": False,
            "error": LobsterError(ErrorCode.PATH_INVALID, f"无效路径: {str(e)}"),
        }

    if not allow_create and not file_path.exists():
        return {
            "valid": False,
            "error": LobsterError(ErrorCode.FILE_NOT_FOUND, f"路径不存在: {path}"),
        }

    if file_path.exists() and file_path.stat().st_size > security_config.max_file_size:
        return {
            "valid": False,
            "error": LobsterError(
                ErrorCode.FILE_TOO_LARGE,
                f"文件过大 (最大 {security_config.max_file_size // 1024 // 1024}MB)",
            ),
        }

    for base_dir in security_config.allowed_base_dirs:
        try:
            base = Path(base_dir).resolve()
            if str(file_path).startswith(str(base)):
                return {"valid": True, "path": file_path}
        except Exception:
            continue

    return {"valid": True, "path": file_path}


def validate_command(command: str) -> Dict[str, Any]:
    """验证命令安全性"""
    command_lower = command.lower()

    for blocked in security_config.blocked_commands:
        if blocked.lower() in command_lower:
            return {
                "valid": False,
                "error": LobsterError(
                    ErrorCode.COMMAND_BLOCKED,
                    f"命令被禁止: 包含危险操作 '{blocked}'",
                ),
            }

    if security_config.allowed_commands is not None:
        command_name = command.split()[0] if command.split() else ""
        if command_name not in security_config.allowed_commands:
            return {
                "valid": False,
                "error": LobsterError(
                    ErrorCode.COMMAND_BLOCKED,
                    f"命令不在白名单中: {command_name}",
                ),
            }

    return {"valid": True}


def validate_url(url: str) -> Dict[str, Any]:
    """验证 URL 安全性"""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return {
                "valid": False,
                "error": LobsterError(
                    ErrorCode.URL_INVALID,
                    f"不支持的协议: {parsed.scheme}",
                ),
            }

        if parsed.hostname in ["localhost", "127.0.0.1", "0.0.0.0"]:
            return {
                "valid": False,
                "error": LobsterError(ErrorCode.URL_BLOCKED, "禁止访问本地地址"),
            }

        return {"valid": True}
    except Exception as e:
        return {"valid": False, "error": LobsterError(ErrorCode.URL_INVALID, f"无效 URL: {str(e)}")}


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """注册内置工具"""

        # ==================== 文件操作 ====================
        self.register(
            Tool(
                name="file_read",
                description="读取文件内容",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "文件路径"},
                        "encoding": {
                            "type": "string",
                            "default": "utf-8",
                            "description": "文件编码",
                        },
                    },
                    "required": ["path"],
                },
                handler=self._handle_file_read,
                category="file",
            )
        )

        self.register(
            Tool(
                name="file_write",
                description="写入文件内容",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "文件路径"},
                        "content": {"type": "string", "description": "文件内容"},
                        "mode": {
                            "type": "string",
                            "enum": ["write", "append"],
                            "default": "write",
                            "description": "写入模式",
                        },
                    },
                    "required": ["path", "content"],
                },
                handler=self._handle_file_write,
                category="file",
            )
        )

        self.register(
            Tool(
                name="file_list",
                description="列出目录内容",
                parameters={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "default": ".",
                            "description": "目录路径",
                        },
                        "pattern": {
                            "type": "string",
                            "default": "*",
                            "description": "文件匹配模式",
                        },
                    },
                    "required": [],
                },
                handler=self._handle_file_list,
                category="file",
            )
        )

        self.register(
            Tool(
                name="file_delete",
                description="删除文件",
                parameters={
                    "type": "object",
                    "properties": {"path": {"type": "string", "description": "文件路径"}},
                    "required": ["path"],
                },
                handler=self._handle_file_delete,
                category="file",
            )
        )

        # ==================== 网络请求 ====================
        self.register(
            Tool(
                name="http_get",
                description="发送 HTTP GET 请求",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "请求 URL"},
                        "headers": {
                            "type": "object",
                            "description": "请求头",
                            "additionalProperties": {"type": "string"},
                        },
                        "timeout": {
                            "type": "integer",
                            "default": 30,
                            "description": "超时时间(秒)",
                        },
                    },
                    "required": ["url"],
                },
                handler=self._handle_http_get,
                category="network",
            )
        )

        self.register(
            Tool(
                name="http_post",
                description="发送 HTTP POST 请求",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "请求 URL"},
                        "data": {"type": "object", "description": "请求数据"},
                        "headers": {
                            "type": "object",
                            "description": "请求头",
                            "additionalProperties": {"type": "string"},
                        },
                        "timeout": {
                            "type": "integer",
                            "default": 30,
                            "description": "超时时间(秒)",
                        },
                    },
                    "required": ["url"],
                },
                handler=self._handle_http_post,
                category="network",
            )
        )

        self.register(
            Tool(
                name="web_search",
                description="网络搜索（需要配置搜索 API）",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "搜索关键词"},
                        "limit": {
                            "type": "integer",
                            "default": 5,
                            "description": "返回结果数量",
                        },
                    },
                    "required": ["query"],
                },
                handler=self._handle_web_search,
                category="network",
            )
        )

        # ==================== 代码执行 ====================
        self.register(
            Tool(
                name="run_python",
                description="执行 Python 代码",
                parameters={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Python 代码"},
                        "timeout": {
                            "type": "integer",
                            "default": 30,
                            "description": "超时时间(秒)",
                        },
                    },
                    "required": ["code"],
                },
                handler=self._handle_run_python,
                category="code",
            )
        )

        self.register(
            Tool(
                name="run_shell",
                description="执行 Shell 命令",
                parameters={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell 命令"},
                        "timeout": {
                            "type": "integer",
                            "default": 30,
                            "description": "超时时间(秒)",
                        },
                    },
                    "required": ["command"],
                },
                handler=self._handle_run_shell,
                category="code",
            )
        )

        # ==================== 系统交互 ====================
        self.register(
            Tool(
                name="notify",
                description="发送系统通知",
                parameters={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "通知内容"},
                        "title": {
                            "type": "string",
                            "default": "OpenClaw",
                            "description": "通知标题",
                        },
                    },
                    "required": ["message"],
                },
                handler=self._handle_notify,
                category="system",
            )
        )

        self.register(
            Tool(
                name="clipboard",
                description="操作剪贴板",
                parameters={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["read", "write"],
                            "description": "操作类型",
                        },
                        "content": {
                            "type": "string",
                            "description": "写入内容 (write 时需要)",
                        },
                    },
                    "required": ["action"],
                },
                handler=self._handle_clipboard,
                category="system",
            )
        )

        # ==================== 数据处理 ====================
        self.register(
            Tool(
                name="json_parse",
                description="解析 JSON 数据",
                parameters={
                    "type": "object",
                    "properties": {
                        "data": {"type": "string", "description": "JSON 字符串"},
                        "path": {
                            "type": "string",
                            "description": "提取路径 (如: data.items.0.name)",
                        },
                    },
                    "required": ["data"],
                },
                handler=self._handle_json_parse,
                category="data",
            )
        )

        self.register(
            Tool(
                name="text_process",
                description="文本处理",
                parameters={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "输入文本"},
                        "operation": {
                            "type": "string",
                            "enum": [
                                "uppercase",
                                "lowercase",
                                "trim",
                                "lines",
                                "words",
                                "count",
                            ],
                            "description": "操作类型",
                        },
                    },
                    "required": ["text", "operation"],
                },
                handler=self._handle_text_process,
                category="data",
            )
        )

        self.register(
            Tool(
                name="calculate",
                description="执行数学计算",
                parameters={
                    "type": "object",
                    "properties": {"expression": {"type": "string", "description": "数学表达式"}},
                    "required": ["expression"],
                },
                handler=self._handle_calculate,
                category="data",
            )
        )

        # ==================== 投资工具 ====================
        register_investment_tools(self)

        # ==================== Serena 工具 ====================
        register_serena_tools(self)

    def register(self, tool: Tool):
        """注册工具"""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """获取工具"""
        return self._tools.get(name)

    def list_all(self) -> List[Dict[str, Any]]:
        """列出所有工具"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
                "category": tool.category,
            }
            for tool in self._tools.values()
        ]

    def list_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按类别列出工具"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in self._tools.values()
            if tool.category == category
        ]

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """获取 OpenAI Function Calling 格式的工具列表"""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in self._tools.values()
        ]

    def execute(self, name: str, use_cache: bool = True, **kwargs) -> Dict[str, Any]:
        """执行工具

        Args:
            name: 工具名称
            use_cache: 是否使用缓存 (默认 True)
            **kwargs: 工具参数
        """
        from lobster.core.logger import logger

        logger.tool_call(name, kwargs)

        tool = self.get(name)
        if not tool:
            logger.error(f"Tool not found: {name}")
            stats_tracker.record_call(name, False, 0, f"Tool not found: {name}")
            return error_response(
                ErrorCode.TOOL_NOT_FOUND,
                f"工具不存在: {name}",
                {"tool_name": name},
            )

        if use_cache:
            cached_result = tool_cache.get(name, kwargs)
            if cached_result is not None:
                logger.info(f"[Cache] Hit for {name}")
                return success_response(cached_result, 0, cached=True)

        start_time = time.time()
        try:
            result = tool.handler(**kwargs)
            duration_ms = (time.time() - start_time) * 1000

            if isinstance(result, dict) and "error" in result:
                logger.tool_result(name, False, result["error"])
                stats_tracker.record_call(name, False, duration_ms, result["error"])
                return error_response(
                    ErrorCode.TOOL_EXECUTION_ERROR,
                    result["error"],
                    {"tool_name": name, "duration_ms": duration_ms},
                )

            logger.tool_result(name, True, result)
            logger.performance(f"tool_{name}", duration_ms)
            stats_tracker.record_call(name, True, duration_ms)

            if use_cache and isinstance(result, dict):
                tool_cache.set(name, kwargs, result)

            return success_response(result, duration_ms)
        except LobsterError as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.tool_result(name, False, e.message)
            logger.exception(f"Tool {name} failed: {e.message}")
            stats_tracker.record_call(name, False, duration_ms, e.message)
            return e.to_dict()
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_msg = str(e)
            logger.tool_result(name, False, error_msg)
            logger.exception(f"Tool {name} failed: {error_msg}")
            stats_tracker.record_call(name, False, duration_ms, error_msg)
            return error_response(
                ErrorCode.TOOL_EXECUTION_ERROR,
                error_msg,
                {"tool_name": name, "duration_ms": duration_ms},
            )

    # ==================== 文件操作处理器 ====================
    def _handle_file_read(self, path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """读取文件"""
        validation = validate_path(path)
        if not validation["valid"]:
            error = validation["error"]
            return {"error": error.message if isinstance(error, LobsterError) else str(error)}

        file_path = validation["path"]
        if not file_path.exists():
            return {"error": LobsterError(ErrorCode.FILE_NOT_FOUND, f"文件不存在: {path}").message}

        try:
            content = file_path.read_text(encoding=encoding)
            if len(content) > security_config.max_content_size:
                content = content[: security_config.max_content_size]
                truncated = True
            else:
                truncated = False

            return {
                "content": content,
                "size": len(content),
                "lines": content.count("\n") + 1,
                "truncated": truncated,
            }
        except UnicodeDecodeError as e:
            return {
                "error": LobsterError(ErrorCode.FILE_READ_ERROR, f"文件编码错误: {str(e)}").message
            }
        except Exception as e:
            return {"error": LobsterError(ErrorCode.FILE_READ_ERROR, str(e)).message}

    def _handle_file_write(self, path: str, content: str, mode: str = "write") -> Dict[str, Any]:
        """写入文件"""
        if len(content) > security_config.max_content_size:
            return {
                "error": LobsterError(
                    ErrorCode.FILE_TOO_LARGE,
                    f"内容过大 (最大 {security_config.max_content_size // 1024 // 1024}MB)",
                ).message
            }

        validation = validate_path(path, allow_create=True)
        if not validation["valid"]:
            error = validation["error"]
            return {"error": error.message if isinstance(error, LobsterError) else str(error)}

        file_path = validation["path"]

        try:
            if mode == "append":
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(content)
            else:
                file_path.write_text(content, encoding="utf-8")

            return {"path": str(file_path.absolute()), "size": len(content)}
        except Exception as e:
            return {"error": LobsterError(ErrorCode.FILE_WRITE_ERROR, str(e)).message}

    def _handle_file_list(self, path: str = ".", pattern: str = "*") -> Dict[str, Any]:
        """列出目录内容"""
        dir_path = Path(path)

        if not dir_path.exists():
            return {"error": LobsterError(ErrorCode.FILE_NOT_FOUND, f"目录不存在: {path}").message}

        files = []
        for item in dir_path.glob(pattern):
            files.append(
                {
                    "name": item.name,
                    "path": str(item),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                }
            )

        return {"files": files, "count": len(files)}

    def _handle_file_delete(self, path: str) -> Dict[str, Any]:
        """删除文件"""
        file_path = Path(path)

        if not file_path.exists():
            return {"error": LobsterError(ErrorCode.FILE_NOT_FOUND, f"文件不存在: {path}").message}

        try:
            file_path.unlink()
            return {"deleted": str(file_path)}
        except Exception as e:
            return {"error": LobsterError(ErrorCode.FILE_DELETE_ERROR, str(e)).message}

    # ==================== 网络请求处理器 ====================
    def _handle_http_get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """发送 GET 请求"""
        validation = validate_url(url)
        if not validation["valid"]:
            error = validation["error"]
            return {"error": error.message if isinstance(error, LobsterError) else str(error)}

        try:
            import requests

            response = requests.get(url, headers=headers or {}, timeout=timeout)
            return {
                "status_code": response.status_code,
                "content": response.text[:5000],
                "headers": dict(response.headers),
            }
        except ImportError:
            return {"error": LobsterError(ErrorCode.NETWORK_ERROR, "requests 库未安装").message}
        except Exception as e:
            return {"error": LobsterError(ErrorCode.REQUEST_FAILED, str(e)).message}

    def _handle_http_post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
    ) -> Dict[str, Any]:
        """发送 POST 请求"""
        validation = validate_url(url)
        if not validation["valid"]:
            error = validation["error"]
            return {"error": error.message if isinstance(error, LobsterError) else str(error)}

        try:
            import requests

            response = requests.post(url, json=data, headers=headers or {}, timeout=timeout)
            return {
                "status_code": response.status_code,
                "content": response.text[:5000],
                "headers": dict(response.headers),
            }
        except ImportError:
            return {"error": LobsterError(ErrorCode.NETWORK_ERROR, "requests 库未安装").message}
        except Exception as e:
            return {"error": LobsterError(ErrorCode.REQUEST_FAILED, str(e)).message}

    def _handle_web_search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """网络搜索"""
        return {
            "results": [],
            "message": "需要配置搜索 API (如 SerpAPI, Google Custom Search)",
        }

    # ==================== 代码执行处理器 ====================
    def _handle_run_python(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """执行 Python 代码"""
        dangerous_imports = ["os.system", "subprocess", "eval(", "exec(", "__import__"]
        for dangerous in dangerous_imports:
            if dangerous in code:
                return {
                    "error": LobsterError(
                        ErrorCode.CODE_DANGEROUS, f"代码包含危险操作: {dangerous}"
                    ).message
                }

        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "error": LobsterError(ErrorCode.CODE_TIMEOUT, f"执行超时 ({timeout}秒)").message
            }
        except Exception as e:
            return {"error": LobsterError(ErrorCode.CODE_ERROR, str(e)).message}

    def _handle_run_shell(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """执行 Shell 命令"""
        validation = validate_command(command)
        if not validation["valid"]:
            error = validation["error"]
            return {"error": error.message if isinstance(error, LobsterError) else str(error)}

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "error": LobsterError(ErrorCode.COMMAND_TIMEOUT, f"执行超时 ({timeout}秒)").message
            }
        except Exception as e:
            return {"error": LobsterError(ErrorCode.COMMAND_FAILED, str(e)).message}

    # ==================== 系统交互处理器 ====================
    def _handle_notify(self, message: str, title: str = "OpenClaw") -> Dict[str, Any]:
        """发送通知"""
        import sys

        try:
            if sys.platform == "darwin":
                import subprocess

                script = f'display notification "{message}" with title "{title}"'
                subprocess.run(["osascript", "-e", script], check=True)
                return {"sent": True, "message": message}
            elif sys.platform == "linux":
                import subprocess

                subprocess.run(["notify-send", title, message], check=True)
                return {"sent": True, "message": message}
            else:
                return {"sent": False, "message": f"[{title}] {message}"}
        except Exception as e:
            return {"error": str(e)}

    def _handle_clipboard(self, action: str, content: str = None) -> Dict[str, Any]:
        """操作剪贴板"""
        import subprocess

        try:
            if action == "read":
                if subprocess.run(["which", "pbpaste"], capture_output=True).returncode == 0:
                    result = subprocess.run(["pbpaste"], capture_output=True, text=True)
                    return {"content": result.stdout}
                else:
                    return {"error": "剪贴板功能不可用"}

            elif action == "write" and content:
                if subprocess.run(["which", "pbcopy"], capture_output=True).returncode == 0:
                    subprocess.run(["pbcopy"], input=content, text=True)
                    return {"copied": content[:100]}
                else:
                    return {"error": "剪贴板功能不可用"}

            return {"error": "无效操作"}
        except Exception as e:
            return {"error": str(e)}

    # ==================== 数据处理处理器 ====================
    def _handle_json_parse(self, data: str, path: Optional[str] = None) -> Dict[str, Any]:
        """解析 JSON"""

        try:
            parsed = json.loads(data)

            if path:
                for key in path.split("."):
                    if key.isdigit():
                        parsed = parsed[int(key)]
                    else:
                        parsed = parsed[key]

            return {"data": parsed}
        except json.JSONDecodeError as e:
            return {
                "error": LobsterError(
                    ErrorCode.JSON_PARSE_ERROR, f"JSON 解析错误: {str(e)}"
                ).message
            }
        except (KeyError, IndexError) as e:
            return {
                "error": LobsterError(ErrorCode.JSON_PARSE_ERROR, f"路径不存在: {str(e)}").message
            }

    def _handle_text_process(self, text: str, operation: str) -> Dict[str, Any]:
        """文本处理"""
        operations = {
            "uppercase": text.upper(),
            "lowercase": text.lower(),
            "trim": text.strip(),
            "lines": text.split("\n"),
            "words": text.split(),
            "count": {
                "characters": len(text),
                "words": len(text.split()),
                "lines": len(text.split("\n")),
            },
        }

        if operation not in operations:
            return {
                "error": LobsterError(
                    ErrorCode.TEXT_PROCESS_ERROR, f"未知操作: {operation}"
                ).message
            }

        return {"result": operations[operation]}

    def _handle_calculate(self, expression: str) -> Dict[str, Any]:
        """数学计算"""
        import ast
        import operator

        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
        }

        def eval_expr(node):
            if isinstance(node, ast.Constant):
                return node.value
            elif isinstance(node, ast.BinOp):
                return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            elif isinstance(node, ast.UnaryOp):
                return ops[type(node.op)](eval_expr(node.operand))
            else:
                raise TypeError(f"不支持的操作: {type(node)}")

        try:
            tree = ast.parse(expression, mode="eval")
            result = eval_expr(tree.body)
            return {"expression": expression, "result": result}
        except Exception as e:
            return {"error": LobsterError(ErrorCode.CALCULATE_ERROR, f"计算错误: {str(e)}").message}


registry = ToolRegistry()
