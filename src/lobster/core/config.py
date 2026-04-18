"""配置管理模块

支持从环境变量和 .env 文件加载配置
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Any
from dataclasses import dataclass, field


def load_env_file(env_path: Optional[Path] = None) -> dict:
    """加载 .env 文件"""
    if env_path is None:
        env_path = Path.cwd() / ".env"

    if not env_path.exists():
        return {}

    env_vars = {}
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                env_vars[key] = value

    return env_vars


@dataclass
class LobsterConfig:
    """Lobster 配置"""

    data_mode: str = "sample"

    alphavantage_api_key: str = ""
    tushare_token: str = ""
    finnhub_api_key: str = ""

    deepseek_api_key: str = ""
    ai_model: str = "deepseek-chat"
    openai_api_key: str = ""

    serena_project_path: str = ""

    api_cache_ttl: int = 60
    ai_cache_ttl: int = 3600

    default_usd_rate: float = 7.1242
    default_hkd_rate: float = 0.9157

    output_format: str = "console"
    report_language: str = "zh"

    _env_loaded: bool = field(default=False, repr=False)

    def __post_init__(self):
        if not self._env_loaded:
            self.load_from_env()

    def load_from_env(self, env_path: Optional[Path] = None) -> "LobsterConfig":
        """从环境变量和 .env 文件加载配置"""
        env_vars = load_env_file(env_path)

        def get_env(key: str, default: Any = None, cast: type = str) -> Any:
            value = os.environ.get(key) or env_vars.get(key, default)
            if value is None:
                return default
            try:
                return cast(value)
            except (ValueError, TypeError):
                return default

        self.data_mode = get_env("DATA_MODE", self.data_mode)

        self.alphavantage_api_key = get_env("ALPHAVANTAGE_API_KEY", self.alphavantage_api_key)
        self.tushare_token = get_env("TUSHARE_TOKEN", self.tushare_token)
        self.finnhub_api_key = get_env("FINNHUB_API_KEY", self.finnhub_api_key)

        self.deepseek_api_key = get_env("DEEPSEEK_API_KEY", self.deepseek_api_key)
        self.ai_model = get_env("AI_MODEL", self.ai_model)
        self.openai_api_key = get_env("OPENAI_API_KEY", self.openai_api_key)

        self.serena_project_path = get_env("SERENA_PROJECT_PATH", self.serena_project_path)

        self.api_cache_ttl = get_env("API_CACHE_TTL", self.api_cache_ttl, int)
        self.ai_cache_ttl = get_env("AI_CACHE_TTL", self.ai_cache_ttl, int)

        self.default_usd_rate = get_env("DEFAULT_USD_RATE", self.default_usd_rate, float)
        self.default_hkd_rate = get_env("DEFAULT_HKD_RATE", self.default_hkd_rate, float)

        self.output_format = get_env("OUTPUT_FORMAT", self.output_format)
        self.report_language = get_env("REPORT_LANGUAGE", self.report_language)

        self._env_loaded = True
        return self

    @property
    def has_alphavantage(self) -> bool:
        """是否配置了 Alpha Vantage API"""
        return bool(self.alphavantage_api_key and not self.alphavantage_api_key.startswith("your_"))

    @property
    def has_tushare(self) -> bool:
        """是否配置了 Tushare API"""
        return bool(self.tushare_token and not self.tushare_token.startswith("your_"))

    @property
    def has_finnhub(self) -> bool:
        """是否配置了 Finnhub API"""
        return bool(self.finnhub_api_key and not self.finnhub_api_key.startswith("your_"))

    @property
    def has_deepseek(self) -> bool:
        """是否配置了 DeepSeek API"""
        return bool(self.deepseek_api_key and not self.deepseek_api_key.startswith("your_"))

    @property
    def has_serena(self) -> bool:
        """是否配置了 Serena 项目路径"""
        return bool(self.serena_project_path)

    def to_dict(self) -> dict:
        """转换为字典（隐藏敏感信息）"""
        return {
            "data_mode": self.data_mode,
            "has_alphavantage": self.has_alphavantage,
            "has_tushare": self.has_tushare,
            "has_finnhub": self.has_finnhub,
            "has_deepseek": self.has_deepseek,
            "has_serena": self.has_serena,
            "serena_project_path": self.serena_project_path,
            "ai_model": self.ai_model,
            "api_cache_ttl": self.api_cache_ttl,
            "ai_cache_ttl": self.ai_cache_ttl,
            "default_usd_rate": self.default_usd_rate,
            "default_hkd_rate": self.default_hkd_rate,
            "output_format": self.output_format,
            "report_language": self.report_language,
        }


config = LobsterConfig()


def get_config() -> LobsterConfig:
    """获取配置实例"""
    return config


class ConfigManager:
    """配置管理器 (兼容旧代码)

    这是 LobsterConfig 的兼容性别名
    """

    def __init__(self):
        self._config = get_config()

    def __getattr__(self, name):
        return getattr(self._config, name)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return getattr(self._config, key, default)

    def set(self, key: str, value: Any):
        """设置配置项"""
        setattr(self._config, key, value)

    def to_dict(self) -> dict:
        """转换为字典"""
        return self._config.to_dict()


__all__ = ["LobsterConfig", "config", "get_config", "ConfigManager", "load_env_file"]
