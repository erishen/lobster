"""Tests for configuration management"""

import pytest
from pathlib import Path
import tempfile
import json


def test_config_creation():
    """Test creating a configuration"""
    from lobster.core.config import LobsterConfig
    
    config = LobsterConfig()
    
    assert config.default_model == "ollama/gemma3"
    assert config.default_embedding_model == "nomic-embed-text"
    assert config.default_vector_store == "faiss"
    assert config.default_temperature == 0.7
    assert config.default_timeout == 30


def test_config_custom_values():
    """Test creating a configuration with custom values"""
    from lobster.core.config import LobsterConfig
    
    config = LobsterConfig(
        default_model="gpt-4o",
        default_temperature=0.5,
        default_timeout=60
    )
    
    assert config.default_model == "gpt-4o"
    assert config.default_temperature == 0.5
    assert config.default_timeout == 60


def test_config_manager():
    """Test configuration manager"""
    from lobster.core.config import ConfigManager, LobsterConfig
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ConfigManager()
        manager.config_dir = Path(tmpdir)
        manager.config_file = manager.config_dir / "config.json"
        
        # Test default config
        config = manager.load()
        assert isinstance(config, LobsterConfig)
        
        # Test save and load
        manager.update(default_model="test-model")
        assert manager.get("default_model") == "test-model"
        
        # Test reset
        manager.reset()
        assert manager.get("default_model") == "ollama/gemma3"


def test_config_persistence():
    """Test configuration persistence"""
    from lobster.core.config import ConfigManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ConfigManager()
        manager.config_dir = Path(tmpdir)
        manager.config_file = manager.config_dir / "config.json"
        
        # Set and save
        manager.set("default_model", "custom-model")
        
        # Create new manager to test persistence
        manager2 = ConfigManager()
        manager2.config_dir = Path(tmpdir)
        manager2.config_file = manager2.config_dir / "config.json"
        
        config = manager2.load()
        assert config.default_model == "custom-model"
