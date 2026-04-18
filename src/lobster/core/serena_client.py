"""Serena 客户端工具 - 直接调用 Serena Python API

提供代码理解、重构等 IDE 级别能力
"""

from __future__ import annotations

import importlib.util
from typing import Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass

if TYPE_CHECKING:
    from serena.agent import SerenaAgent
    from serena.project import Project
    from lobster.core.tools import ToolRegistry


@dataclass
class SerenaConfig:
    """Serena 配置"""

    project_path: str
    language_backend: str = "LSP"  # LSP or JETBRAINS


class SerenaClient:
    """Serena 客户端 - 直接调用 Serena Python API"""

    _instance: Optional["SerenaClient"] = None
    _agent: Optional["SerenaAgent"] = None
    _project: Optional["Project"] = None

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
        return self._agent is not None

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
                "error": "Serena 未安装。请运行: pip install serena-ai",
            }

        try:
            from serena.config.serena_config import SerenaConfig as SC, LanguageBackend
            from serena.agent import SerenaAgent
            from serena.project import Project

            self._config = SerenaConfig(
                project_path=project_path,
                language_backend=language_backend,
            )

            lb = (
                LanguageBackend.LSP
                if language_backend.upper() == "LSP"
                else LanguageBackend.JETBRAINS
            )

            serena_config = SC.load()
            serena_config.language_backend = lb

            self._agent = SerenaAgent(serena_config)

            project = Project.from_path(project_path)
            self._agent.activate_project(project)
            self._project = project

            return {
                "success": True,
                "project": project_path,
                "language_backend": language_backend,
                "languages": [lang.value for lang in self._agent.get_active_lsp_languages()],
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _ensure_initialized(self) -> Dict[str, Any]:
        """确保已初始化"""
        if self._agent is not None:
            return {"success": True}

        result = self.auto_initialize()
        if not result.get("success"):
            return result

        return {"success": True}

    def get_symbols_overview(self, relative_path: str, depth: int = 0) -> Dict[str, Any]:
        """获取文件符号概览

        Args:
            relative_path: 相对文件路径
            depth: 深度 (默认 0)
        """
        init_result = self._ensure_initialized()
        if not init_result.get("success"):
            return init_result

        try:
            from serena.tools.symbol_tools import GetSymbolsOverviewTool

            tool = GetSymbolsOverviewTool(self._agent)
            result = tool.get_symbol_overview(relative_path, depth=depth)

            return {
                "success": True,
                "file": relative_path,
                "symbols": result,
            }

        except Exception as e:
            return {"error": str(e)}

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
        init_result = self._ensure_initialized()
        if not init_result.get("success"):
            return init_result

        try:
            from serena.tools.symbol_tools import FindSymbolTool

            tool = FindSymbolTool(self._agent)
            result = tool.apply(
                name=name,
                relative_path=relative_path or "",
                include_body=include_body,
            )

            return {"success": True, "result": result}

        except Exception as e:
            return {"error": str(e)}

    def find_referencing_symbols(self, name: str, relative_path: str) -> Dict[str, Any]:
        """查找引用符号

        Args:
            name: 符号名称
            relative_path: 相对文件路径
        """
        init_result = self._ensure_initialized()
        if not init_result.get("success"):
            return init_result

        try:
            from serena.tools.symbol_tools import FindReferencingSymbolsTool

            tool = FindReferencingSymbolsTool(self._agent)
            result = tool.apply(name=name, relative_path=relative_path)

            return {"success": True, "result": result}

        except Exception as e:
            return {"error": str(e)}

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
        init_result = self._ensure_initialized()
        if not init_result.get("success"):
            return init_result

        try:
            from serena.tools.symbol_tools import RenameSymbolTool

            tool = RenameSymbolTool(self._agent)
            result = tool.apply(
                name=name,
                relative_path=relative_path,
                new_name=new_name,
            )

            return {"success": True, "result": result}

        except Exception as e:
            return {"error": str(e)}

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
        init_result = self._ensure_initialized()
        if not init_result.get("success"):
            return init_result

        try:
            from serena.tools.symbol_tools import ReplaceSymbolBodyTool

            tool = ReplaceSymbolBodyTool(self._agent)
            result = tool.apply(
                name=name,
                relative_path=relative_path,
                new_body=new_body,
            )

            return {"success": True, "result": result}

        except Exception as e:
            return {"error": str(e)}

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
        init_result = self._ensure_initialized()
        if not init_result.get("success"):
            return init_result

        try:
            from serena.tools.file_tools import SearchForPatternTool

            tool = SearchForPatternTool(self._agent)
            result = tool.apply(
                pattern=pattern,
                relative_dir=relative_dir,
                file_pattern=file_pattern,
            )

            return {"success": True, "result": result}

        except Exception as e:
            return {"error": str(e)}

    def list_dir(self, relative_path: str = ".", recursive: bool = False) -> Dict[str, Any]:
        """列出目录

        Args:
            relative_path: 相对路径
            recursive: 是否递归
        """
        init_result = self._ensure_initialized()
        if not init_result.get("success"):
            return init_result

        try:
            from serena.tools.file_tools import ListDirTool

            tool = ListDirTool(self._agent)
            result = tool.apply(
                relative_path=relative_path,
                recursive=recursive,
            )

            return {"success": True, "result": result}

        except Exception as e:
            return {"error": str(e)}

    def read_file(
        self, relative_path: str, start_line: int = 1, end_line: int = -1
    ) -> Dict[str, Any]:
        """读取文件

        Args:
            relative_path: 相对文件路径
            start_line: 起始行
            end_line: 结束行
        """
        init_result = self._ensure_initialized()
        if not init_result.get("success"):
            return init_result

        try:
            from serena.tools.file_tools import ReadFileTool

            tool = ReadFileTool(self._agent)
            result = tool.apply(
                relative_path=relative_path,
                start_line=start_line,
                end_line=end_line,
            )

            return {"success": True, "result": result}

        except Exception as e:
            return {"error": str(e)}

    def get_current_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        init_result = self._ensure_initialized()
        if not init_result.get("success"):
            return init_result

        try:
            from serena.tools.config_tools import GetCurrentConfigTool

            tool = GetCurrentConfigTool(self._agent)
            result = tool.apply()

            return {"success": True, "config": result}

        except Exception as e:
            return {"error": str(e)}


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
            description="初始化 Serena 客户端，连接到指定项目",
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
            description="查找符号的所有引用",
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
            name="serena_rename",
            description="重命名符号 (自动更新所有引用)",
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "当前符号名称",
                    },
                    "relative_path": {
                        "type": "string",
                        "description": "相对文件路径",
                    },
                    "new_name": {
                        "type": "string",
                        "description": "新名称",
                    },
                },
                "required": ["name", "relative_path", "new_name"],
            },
            handler=lambda name, relative_path, new_name: client.rename_symbol(
                name, relative_path, new_name
            ),
            category="serena",
        )
    )

    registry.register(
        Tool(
            name="serena_replace_body",
            description="替换符号体 (函数实现)",
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
                    "new_body": {
                        "type": "string",
                        "description": "新的函数体",
                    },
                },
                "required": ["name", "relative_path", "new_body"],
            },
            handler=lambda name, relative_path, new_body: client.replace_symbol_body(
                name, relative_path, new_body
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
