"""Serena 客户端工具 - 直接调用 Serena Python API

提供代码理解、重构等 IDE 级别能力

使用方式:
    设置 SERENA_DIR 环境变量指向 serena 项目路径，然后直接调用 serena 的 Python API
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from lobster.core.tools import ToolRegistry

_serena_available = False
_serena_agent_class = None
_serena_tools = {}

try:
    serena_dir = os.getenv("SERENA_DIR", "")
    if serena_dir and Path(serena_dir).exists():
        sys.path.insert(0, str(Path(serena_dir) / "src"))

    from serena.agent import SerenaAgent
    from serena.tools import (
        FindFileTool,
        FindReferencingSymbolsTool,
        FindSymbolTool,
        GetSymbolsOverviewTool,
        RenameSymbolTool,
        ReplaceSymbolBodyTool,
        SearchForPatternTool,
    )

    _serena_available = True
    _serena_agent_class = SerenaAgent
    _serena_tools = {
        "find_file": FindFileTool,
        "find_referencing_symbols": FindReferencingSymbolsTool,
        "find_symbol": FindSymbolTool,
        "get_symbols_overview": GetSymbolsOverviewTool,
        "rename_symbol": RenameSymbolTool,
        "replace_symbol_body": ReplaceSymbolBodyTool,
        "search_for_pattern": SearchForPatternTool,
    }
except ImportError:
    pass


@dataclass
class SerenaConfig:
    """Serena 配置"""

    project_path: str
    language_backend: str = "LSP"


class SerenaClient:
    """Serena 客户端 - 提供代码理解、重构等 IDE 级别能力"""

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
        self._agent: Optional[Any] = None

    def is_available(self) -> bool:
        """检查 Serena 是否可用"""
        return _serena_available

    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return self._agent is not None

    def initialize(self, project_path: str, language_backend: str = "LSP") -> Dict[str, Any]:
        """初始化 Serena 客户端

        Args:
            project_path: 项目路径
            language_backend: 语言后端 (LSP 或 JETBRAINS)
        """
        if not _serena_available:
            return {
                "success": False,
                "error": "Serena 未安装。请设置 SERENA_DIR 环境变量指向 serena 项目路径。",
                "hint": "export SERENA_DIR=/path/to/serena",
            }

        try:
            self._config = SerenaConfig(
                project_path=project_path,
                language_backend=language_backend,
            )
            self._agent = _serena_agent_class(project=project_path)

            return {
                "success": True,
                "project": project_path,
                "language_backend": language_backend,
                "message": "Serena 初始化成功",
                "available_tools": list(_serena_tools.keys()),
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Serena 初始化失败: {str(e)}",
            }

    def _get_tool(self, tool_class: type) -> Any:
        """获取工具实例"""
        if self._agent is None:
            raise RuntimeError("Serena 未初始化，请先调用 initialize()")
        return self._agent.get_tool(tool_class)

    def _execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """执行工具并返回结果"""
        if not _serena_available:
            return {"error": "Serena 未安装。请设置 SERENA_DIR 环境变量。"}

        if self._agent is None:
            return {"error": "Serena 未初始化，请先调用 initialize()"}

        try:
            tool_class = _serena_tools.get(tool_name)
            if tool_class is None:
                return {"error": f"未知工具: {tool_name}"}

            tool = self._get_tool(tool_class)
            result = self._agent.execute_task(lambda: tool.apply(**kwargs))
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}

    def get_symbols_overview(self, relative_path: str, depth: int = 0) -> Dict[str, Any]:
        """获取文件符号概览

        Args:
            relative_path: 相对文件路径
            depth: 深度 (默认 0)
        """
        return self._execute_tool(
            "get_symbols_overview",
            relative_path=relative_path,
            depth=depth,
        )

    def find_symbol(
        self,
        name_path_pattern: str,
        relative_path: Optional[str] = None,
        depth: int = 0,
        include_body: bool = False,
    ) -> Dict[str, Any]:
        """查找符号

        Args:
            name_path_pattern: 符号路径模式
            relative_path: 相对文件路径 (可选)
            depth: 获取子节点的深度
            include_body: 是否包含函数体
        """
        kwargs: Dict[str, Any] = {"name_path_pattern": name_path_pattern}
        if relative_path is not None:
            kwargs["relative_path"] = relative_path
        if depth > 0:
            kwargs["depth"] = depth
        if include_body:
            kwargs["include_body"] = True

        return self._execute_tool("find_symbol", **kwargs)

    def find_referencing_symbols(
        self,
        name_path: str,
        relative_path: str,
        include_kinds: Optional[List[int]] = None,
        exclude_kinds: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """查找引用特定符号的代码

        Args:
            name_path: 符号的完整路径
            relative_path: 包含该符号的文件路径
            include_kinds: 包含的符号类型
            exclude_kinds: 排除的符号类型
        """
        kwargs: Dict[str, Any] = {
            "name_path": name_path,
            "relative_path": relative_path,
        }
        if include_kinds is not None:
            kwargs["include_kinds"] = include_kinds
        if exclude_kinds is not None:
            kwargs["exclude_kinds"] = exclude_kinds

        return self._execute_tool("find_referencing_symbols", **kwargs)

    def rename_symbol(
        self,
        name_path: str,
        new_name: str,
        relative_path: str,
    ) -> Dict[str, Any]:
        """重命名符号

        Args:
            name_path: 当前符号名称
            relative_path: 相对文件路径
            new_name: 新名称
        """
        return self._execute_tool(
            "rename_symbol",
            name_path=name_path,
            new_name=new_name,
            relative_path=relative_path,
        )

    def replace_symbol_body(
        self,
        name_path: str,
        body: str,
        relative_path: str,
    ) -> Dict[str, Any]:
        """替换符号体

        Args:
            name_path: 符号名称
            relative_path: 相对文件路径
            body: 新的函数体
        """
        return self._execute_tool(
            "replace_symbol_body",
            name_path=name_path,
            body=body,
            relative_path=relative_path,
        )

    def search_for_pattern(
        self,
        substring_pattern: str,
        relative_path: Optional[str] = None,
        paths_include_glob: Optional[str] = None,
        paths_exclude_glob: Optional[str] = None,
        context_lines_before: int = 0,
        context_lines_after: int = 0,
        restrict_search_to_code_files: bool = False,
    ) -> Dict[str, Any]:
        """正则搜索

        Args:
            substring_pattern: 正则表达式
            relative_path: 限制搜索范围
            paths_include_glob: 包含文件模式
            paths_exclude_glob: 排除文件模式
            context_lines_before: 前置上下文行数
            context_lines_after: 后置上下文行数
            restrict_search_to_code_files: 是否限制为代码文件
        """
        kwargs: Dict[str, Any] = {"substring_pattern": substring_pattern}
        if relative_path is not None:
            kwargs["relative_path"] = relative_path
        if paths_include_glob is not None:
            kwargs["paths_include_glob"] = paths_include_glob
        if paths_exclude_glob is not None:
            kwargs["paths_exclude_glob"] = paths_exclude_glob
        if context_lines_before > 0:
            kwargs["context_lines_before"] = context_lines_before
        if context_lines_after > 0:
            kwargs["context_lines_after"] = context_lines_after
        if restrict_search_to_code_files:
            kwargs["restrict_search_to_code_files"] = True

        return self._execute_tool("search_for_pattern", **kwargs)

    def find_file(self, file_mask: str, relative_path: str = ".") -> Dict[str, Any]:
        """查找文件

        Args:
            file_mask: 文件名或通配符
            relative_path: 相对路径
        """
        return self._execute_tool(
            "find_file",
            file_mask=file_mask,
            relative_path=relative_path,
        )

    def get_current_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return {
            "available": _serena_available,
            "initialized": self._agent is not None,
            "config": self._config.__dict__ if self._config else None,
            "serena_dir": os.getenv("SERENA_DIR", "未设置"),
        }


serena_client = SerenaClient()


def get_serena_client() -> SerenaClient:
    """获取 Serena 客户端实例"""
    return serena_client


def register_serena_tools(registry: "ToolRegistry"):
    """注册 Serena 工具到注册表"""
    from lobster.core.tools import Tool

    client = get_serena_client()

    registry.register(
        Tool(
            name="serena_init",
            description="初始化 Serena 客户端，检查 Serena 是否可用并初始化项目",
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
            name="serena_status",
            description="获取 Serena 状态和配置信息",
            parameters={
                "type": "object",
                "properties": {},
                "required": [],
            },
            handler=lambda: client.get_current_config(),
            category="serena",
        )
    )

    registry.register(
        Tool(
            name="serena_symbols",
            description="获取文件的符号概览 (类、函数、变量等)",
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
            description="查找符号 (类、函数、变量)",
            parameters={
                "type": "object",
                "properties": {
                    "name_path_pattern": {
                        "type": "string",
                        "description": "符号路径模式",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "相对文件路径 (可选)",
                    },
                    "depth": {
                        "type": "integer",
                        "default": 0,
                        "description": "获取子节点的深度",
                    },
                    "include_body": {
                        "type": "boolean",
                        "default": False,
                        "description": "是否包含符号体代码",
                    },
                },
                "required": ["name_path_pattern"],
            },
            handler=lambda name_path_pattern, relative_path=None, depth=0, include_body=False: (
                client.find_symbol(name_path_pattern, relative_path, depth, include_body)
            ),
            category="serena",
        )
    )

    registry.register(
        Tool(
            name="serena_find_refs",
            description="查找符号的所有引用",
            parameters={
                "type": "object",
                "properties": {
                    "name_path": {
                        "type": "string",
                        "description": "符号的完整路径",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "包含该符号的文件路径",
                    },
                },
                "required": ["name_path", "relative_path"],
            },
            handler=lambda name_path, relative_path: client.find_referencing_symbols(
                name_path, relative_path
            ),
            category="serena",
        )
    )

    registry.register(
        Tool(
            name="serena_search",
            description="正则表达式搜索代码",
            parameters={
                "type": "object",
                "properties": {
                    "substring_pattern": {
                        "type": "string",
                        "description": "正则表达式",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "限制搜索范围",
                    },
                    "paths_include_glob": {
                        "type": "string",
                        "description": "包含文件glob模式",
                    },
                    "paths_exclude_glob": {
                        "type": "string",
                        "description": "排除文件glob模式",
                    },
                    "context_lines_before": {
                        "type": "integer",
                        "default": 0,
                        "description": "前置上下文行数",
                    },
                    "context_lines_after": {
                        "type": "integer",
                        "default": 0,
                        "description": "后置上下文行数",
                    },
                },
                "required": ["substring_pattern"],
            },
            handler=lambda substring_pattern, relative_path=None, paths_include_glob=None, paths_exclude_glob=None, context_lines_before=0, context_lines_after=0: (
                client.search_for_pattern(
                    substring_pattern,
                    relative_path,
                    paths_include_glob,
                    paths_exclude_glob,
                    context_lines_before,
                    context_lines_after,
                )
            ),
            category="serena",
        )
    )

    registry.register(
        Tool(
            name="serena_find_file",
            description="查找文件",
            parameters={
                "type": "object",
                "properties": {
                    "file_mask": {
                        "type": "string",
                        "description": "文件名或通配符",
                    },
                    "relative_path": {
                        "type": "string",
                        "default": ".",
                        "description": "相对路径",
                    },
                },
                "required": ["file_mask"],
            },
            handler=lambda file_mask, relative_path=".": client.find_file(file_mask, relative_path),
            category="serena",
        )
    )

    registry.register(
        Tool(
            name="serena_rename",
            description="重命名符号 (跨文件重构)",
            parameters={
                "type": "object",
                "properties": {
                    "name_path": {
                        "type": "string",
                        "description": "符号的完整路径",
                    },
                    "new_name": {
                        "type": "string",
                        "description": "新名称",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "包含该符号的文件路径",
                    },
                },
                "required": ["name_path", "new_name", "relative_path"],
            },
            handler=lambda name_path, new_name, relative_path: client.rename_symbol(
                name_path, new_name, relative_path
            ),
            category="serena",
        )
    )

    registry.register(
        Tool(
            name="serena_replace_body",
            description="替换符号体 (函数重构)",
            parameters={
                "type": "object",
                "properties": {
                    "name_path": {
                        "type": "string",
                        "description": "符号的完整路径",
                    },
                    "body": {
                        "type": "string",
                        "description": "新的符号体",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "包含该符号的文件路径",
                    },
                },
                "required": ["name_path", "body", "relative_path"],
            },
            handler=lambda name_path, body, relative_path: client.replace_symbol_body(
                name_path, body, relative_path
            ),
            category="serena",
        )
    )
