"""日志系统模块"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
from rich.logging import RichHandler
from rich.console import Console

console = Console()

LOG_DIR = Path.home() / ".lobster" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


class LobsterLogger:
    """Lobster 日志管理器"""

    _instance: Optional["LobsterLogger"] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is not None:
            return

        self._logger = logging.getLogger("lobster")
        self._logger.setLevel(logging.DEBUG)

        self._setup_handlers()

    def _setup_handlers(self):
        """设置日志处理器"""
        self._logger.handlers.clear()

        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
        )
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        self._logger.addHandler(console_handler)

        try:
            log_file = LOG_DIR / f"lobster_{datetime.now().strftime('%Y%m%d')}.log"
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            self._logger.addHandler(file_handler)
        except (PermissionError, OSError):
            pass

    def debug(self, message: str):
        """调试日志"""
        self._logger.debug(message)

    def info(self, message: str):
        """信息日志"""
        self._logger.info(message)

    def warning(self, message: str):
        """警告日志"""
        self._logger.warning(message)

    def error(self, message: str):
        """错误日志"""
        self._logger.error(message)

    def critical(self, message: str):
        """严重错误日志"""
        self._logger.critical(message)

    def exception(self, message: str):
        """异常日志"""
        self._logger.exception(message)

    def tool_call(self, tool_name: str, parameters: dict):
        """记录工具调用"""
        self.info(f"[Tool] {tool_name} called with: {parameters}")

    def tool_result(self, tool_name: str, success: bool, result: any):
        """记录工具结果"""
        status = "✓" if success else "✗"
        self.info(f"[Tool] {tool_name} {status}: {str(result)[:100]}")

    def api_request(self, method: str, path: str, status_code: int):
        """记录 API 请求"""
        self.info(f"[API] {method} {path} - {status_code}")

    def performance(self, operation: str, duration_ms: float):
        """记录性能指标"""
        if duration_ms > 1000:
            self.warning(f"[Perf] {operation} took {duration_ms:.2f}ms (slow)")
        else:
            self.debug(f"[Perf] {operation} took {duration_ms:.2f}ms")


logger = LobsterLogger()


def get_logger() -> LobsterLogger:
    """获取日志实例"""
    return logger
