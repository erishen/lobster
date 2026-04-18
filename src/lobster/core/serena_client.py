"""Serena 客户端工具 - 直接调用 Serena Python API

提供代码理解、重构等 IDE 级别能力

注意: Serena 工具需要通过 MCP 协议使用。
如果 Serena MCP 已配置，可以直接使用 mcp_serena-mcp_* 工具。
"""

from __future__ import annotations

import importlib.util
from typing import Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from lobster.core.tools import ToolRegistry


@dataclass
class SerenaConfig:
    """Serena 配置"""

    project_path: str
    language_backend: str = "LSP"


class SerenaClient:
    """Serena 客户端 - 提供 Serena 工具信息"""

    _instance: Optional["SerenaClient"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True
        self._config: Optional[SerenaConfig] = None

    def is_available(self) -> bool:
        """检查 Serena 是否可用"""
        return importlib.util.find_spec("serena") is not None

    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self.is_available()

    def auto_initialize(self) -> Dict[str, Any]:
        """从配置自动初始化"""
        from lobster.core.config import get_config

        config = get_config()
        if config.has_serena:
            return self.initialize(config.serena_project_path)
        return {"success": False, "error": "未配置 SERENA_PROJECT_PATH"}

    def initialize(self, project_path: str, language_backend: str = "LSP") -> Dict[str, Any]:
        """初始化 Serena 客户端

        Args:
            project_path: 项目路径
            language_backend: 语言后端 (LSP 或 JETBRAINS)
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Serena 未安装。请运行: pip install serena-agent",
            }

        self._config = SerenaConfig(
            project_path=project_path,
            language_backend=language_backend,
        )

        return {
            "success": True,
            "project": project_path,
            "language_backend": language_backend,
            "message": "Serena 已安装。请使用 MCP 工具 (mcp_serena-mcp_*) 进行代码分析。",
            "available_tools": [
                "mcp_serena-mcp_find_symbol",
                "mcp_serena-mcp_get_symbols_overview",
                "mcp_serena-mcp_find_referencing_symbols",
                "mcp_serena-mcp_search_for_pattern",
                "mcp_serena-mcp_read_file",
                "mcp_serena-mcp_list_dir",
            ],
        }

    def get_symbols_overview(self, relative_path: str, depth: int = 0) -> Dict[str, Any]:
        """获取文件符号概览

        Args:
            relative_path: 相对文件路径
            depth: 深度 (默认 0)
        """
        return {
            "error": "请使用 MCP 工具: mcp_serena-mcp_get_symbols_overview",
            "relative_path": relative_path,
            "depth": depth,
        }

    def find_symbol(
        self,
        name: str,
        relative_path: Optional[str] = None,
        include_body: bool = False,
    ) -> Dict[str, Any]:
        """查找符号

        Args:
            name: 符号名称
            relative_path: 相对文件路径 (可选)
            include_body: 是否包含函数体
        """
        return {
            "error": "请使用 MCP 工具: mcp_serena-mcp_find_symbol",
            "name": name,
            "relative_path": relative_path,
            "include_body": include_body,
        }

    def find_referencing_symbols(self, name: str, relative_path: str) -> Dict[str, Any]:
        """查找引用符号

        Args:
            name: 符号名称
            relative_path: 相对文件路径
        """
        return {
            "error": "请使用 MCP 工具: mcp_serena-mcp_find_referencing_symbols",
            "name": name,
            "relative_path": relative_path,
        }

    def rename_symbol(
        self,
        name: str,
        relative_path: str,
        new_name: str,
    ) -> Dict[str, Any]:
        """重命名符号

        Args:
            name: 当前符号名称
            relative_path: 相对文件路径
            new_name: 新名称
        """
        return {
            "error": "请使用 MCP 工具: mcp_serena-mcp_rename_symbol",
            "name": name,
            "relative_path": relative_path,
            "new_name": new_name,
        }

    def replace_symbol_body(
        self,
        name: str,
        relative_path: str,
        new_body: str,
    ) -> Dict[str, Any]:
        """替换符号体

        Args:
            name: 符号名称
            relative_path: 相对文件路径
            new_body: 新的函数体
        """
        return {
            "error": "请使用 MCP 工具: mcp_serena-mcp_replace_symbol_body",
            "name": name,
            "relative_path": relative_path,
            "new_body": new_body,
        }

    def search_for_pattern(
        self,
        pattern: str,
        relative_dir: str = ".",
        file_pattern: str = "*",
    ) -> Dict[str, Any]:
        """正则搜索

        Args:
            pattern: 正则表达式
            relative_dir: 相对目录
            file_pattern: 文件匹配模式
        """
        return {
            "error": "请使用 MCP 工具: mcp_serena-mcp_search_for_pattern",
            "pattern": pattern,
            "relative_dir": relative_dir,
            "file_pattern": file_pattern,
        }

    def list_dir(self, relative_path: str = ".", recursive: bool = False) -> Dict[str, Any]:
        """列出目录

        Args:
            relative_path: 相对路径
            recursive: 是否递归
        """
        return {
            "error": "请使用 MCP 工具: mcp_serena-mcp_list_dir",
            "relative_path": relative_path,
            "recursive": recursive,
        }

    def read_file(
        self, relative_path: str, start_line: int = 1, end_line: int = -1
    ) -> Dict[str, Any]:
        """读取文件

        Args:
            relative_path: 相对文件路径
            start_line: 起始行
            end_line: 结束行
        """
        return {
            "error": "请使用 MCP 工具: mcp_serena-mcp_read_file",
            "relative_path": relative_path,
            "start_line": start_line,
            "end_line": end_line,
        }

    def get_current_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return {
            "error": "请使用 MCP 工具: mcp_serena-mcp_get_current_config",
            "config": self._config.__dict__ if self._config else None,
        }


serena_client = SerenaClient()


def get_serena_client() -> SerenaClient:
    """获取 Serena 客户端实例"""
    return serena_client


def register_serena_tools(registry: "ToolRegistry"):  # type: ignore[name-defined]
    """注册 Serena 工具到注册表"""
    from lobster.core.tools import Tool

    client = get_serena_client()

    registry.register(
        Tool(
            name="serena_init",
            description="初始化 Serena 客户端，检查 Serena 是否可用并返回 MCP 工具列表",
            parameters={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "项目路径",
                    },
                    "language_backend": {
                        "type": "string",
                        "enum": ["LSP", "JETBRAINS"],
                        "default": "LSP",
                        "description": "语言后端",
                    },
                },
                "required": ["project_path"],
            },
            handler=lambda project_path, language_backend="LSP": client.initialize(
                project_path, language_backend
            ),
            category="serena",
        )
    )

    registry.register(
        Tool(
            name="serena_symbols",
            description="获取文件的符号概览 (类、函数、变量等)。建议使用 MCP 工具: mcp_serena-mcp_get_symbols_overview",
            parameters={
                "type": "object",
                "properties": {
                    "relative_path": {
                        "type": "string",
                        "description": "相对文件路径",
                    },
                    "depth": {
                        "type": "integer",
                        "default": 0,
                        "description": "符号深度",
                    },
                },
                "required": ["relative_path"],
            },
            handler=lambda relative_path, depth=0: client.get_symbols_overview(
                relative_path, depth
            ),
            category="serena",
        )
    )

    registry.register(
        Tool(
            name="serena_find_symbol",
            description="查找符号 (类、函数、变量)。建议使用 MCP 工具: mcp_serena-mcp_find_symbol",
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "符号名称",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "相对文件路径 (可选)",
                    },
                    "include_body": {
                        "type": "boolean",
                        "default": False,
                        "description": "是否包含函数体",
                    },
                },
                "required": ["name"],
            },
            handler=lambda name, relative_path=None, include_body=False: client.find_symbol(
                name, relative_path, include_body
            ),
            category="serena",
        )
    )

    registry.register(
        Tool(
            name="serena_find_refs",
            description="查找符号的所有引用。建议使用 MCP 工具: mcp_serena-mcp_find_referencing_symbols",
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "符号名称",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "相对文件路径",
                    },
                },
                "required": ["name", "relative_path"],
            },
            handler=lambda name, relative_path: client.find_referencing_symbols(
                name, relative_path
            ),
            category="serena",
        )
    )

    registry.register(
        Tool(
            name="serena_search",
            description="正则表达式搜索代码。建议使用 MCP 工具: mcp_serena-mcp_search_for_pattern",
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "正则表达式",
                    },
                    "relative_dir": {
                        "type": "string",
                        "default": ".",
                        "description": "相对目录",
                    },
                    "file_pattern": {
                        "type": "string",
                        "default": "*",
                        "description": "文件匹配模式",
                    },
                },
                "required": ["pattern"],
            },
            handler=lambda pattern, relative_dir=".", file_pattern="*": client.search_for_pattern(
                pattern, relative_dir, file_pattern
            ),
            category="serena",
        )
    )
