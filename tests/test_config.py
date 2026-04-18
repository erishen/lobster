"""Tests for configuration management"""

import pytest
from pathlib import Path
import tempfile
import json


def test_config_creation():
    """Test creating a configuration"""
    from lobster.core.config import LobsterConfig

    config = LobsterConfig()

    assert config.data_mode == "real"
    assert config.ai_model == "deepseek-chat"
    assert config.api_cache_ttl == 60
    assert config.ai_cache_ttl == 3600
    assert config.default_usd_rate == 7.1242
    assert config.default_hkd_rate == 0.9157


def test_config_custom_values():
    """Test creating a configuration with custom values"""
    from lobster.core.config import LobsterConfig

    config = LobsterConfig()
    config.data_mode = "sample"
    config.api_cache_ttl = 120

    assert config.data_mode == "sample"
    assert config.api_cache_ttl == 120


def test_config_manager():
    """Test configuration manager"""
    from lobster.core.config import ConfigManager, LobsterConfig

    manager = ConfigManager()

    assert manager.data_mode == "real"
    assert manager.ai_model == "deepseek-chat"

    manager.set("data_mode", "sample")
    assert manager.get("data_mode") == "sample"


def test_config_persistence():
    """Test configuration persistence"""
    from lobster.core.config import ConfigManager

    manager = ConfigManager()

    manager.set("data_mode", "sample")
    assert manager.get("data_mode") == "sample"

    config_dict = manager.to_dict()
    assert "data_mode" in config_dict
    assert config_dict["data_mode"] == "sample"


def test_config_has_api_keys():
    """Test API key detection"""
    from lobster.core.config import ConfigManager

    manager = ConfigManager()

    assert isinstance(manager.has_alphavantage, bool)
    assert isinstance(manager.has_tushare, bool)
    assert isinstance(manager.has_finnhub, bool)
    assert isinstance(manager.has_deepseek, bool)


def test_config_to_dict():
    """Test config to dict conversion"""
    from lobster.core.config import LobsterConfig

    config = LobsterConfig()
    config_dict = config.to_dict()

    assert "data_mode" in config_dict
    assert "has_alphavantage" in config_dict
    assert "has_tushare" in config_dict
    assert "ai_model" in config_dict
    assert "api_cache_ttl" in config_dict
