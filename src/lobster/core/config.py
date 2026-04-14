"""Configuration management for Lobster CLI"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class LobsterConfig(BaseModel):
    """Lobster configuration model"""
    default_model: str = Field(default="ollama/gemma3", description="Default LLM model")
    default_embedding_model: str = Field(default="nomic-embed-text", description="Default embedding model")
    default_vector_store: str = Field(default="faiss", description="Default vector store type")
    default_temperature: float = Field(default=0.7, description="Default temperature")
    default_timeout: int = Field(default=30, description="Default timeout in seconds")
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama base URL")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    google_api_key: Optional[str] = Field(default=None, description="Google API key")
    
    class Config:
        env_prefix = "LOBSTER_"


class ConfigManager:
    """Configuration manager for Lobster CLI"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".lobster"
        self.config_file = self.config_dir / "config.json"
        # Don't create directory immediately, wait until save
        self._config: Optional[LobsterConfig] = None
    
    @property
    def config(self) -> LobsterConfig:
        """Get current configuration"""
        if self._config is None:
            self._config = self.load()
        return self._config
    
    def load(self) -> LobsterConfig:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                return LobsterConfig(**data)
            except Exception:
                pass
        return LobsterConfig()
    
    def save(self, config: Optional[LobsterConfig] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        # Create directory only when saving
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(config.model_dump(), f, indent=2)
        
        self._config = config
    
    def update(self, **kwargs):
        """Update configuration"""
        current = self.config.model_dump()
        current.update(kwargs)
        self._config = LobsterConfig(**current)
        self.save()
    
    def reset(self):
        """Reset configuration to defaults"""
        self._config = LobsterConfig()
        self.save()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value"""
        self.update(**{key: value})
    
    def show(self) -> Dict[str, Any]:
        """Show all configuration values"""
        return self.config.model_dump()
