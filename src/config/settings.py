"""Application settings using Pydantic for validation."""

from typing import Dict, Optional, Any
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Application
    app_env: str = Field(default="development", description="Application environment")
    
    # Embedding configuration
    embedding_model: str = Field(default="bge-m3", description="Embedding model type")
    embedding_model_name: str = Field(default="BAAI/bge-m3", description="BGE-M3 model name")
    embedding_cache_size: int = Field(default=10000, description="Embedding cache size")
    embedding_batch_size: int = Field(default=16, description="Batch size for embeddings")
    embedding_use_fp16: bool = Field(default=True, description="Use FP16 for BGE-M3")
    embedding_device: str = Field(default="cpu", description="Device for embedding model")
    log_level: str = Field(default="INFO", description="Logging level")
    api_port: int = Field(default=8000, description="API server port")
    api_host: str = Field(default="0.0.0.0", description="API server host")
    
    # LLM Configuration
    deepseek_api_key: Optional[str] = Field(default=None, description="DeepSeek API key")
    deepseek_api_base: str = Field(
        default="https://api.deepseek.com/v1", 
        description="DeepSeek API base URL"
    )
    aliyun_api_key: Optional[str] = Field(default=None, description="Aliyun API key")
    aliyun_api_endpoint: Optional[str] = Field(default=None, description="Aliyun endpoint")
    lm_studio_base_url: str = Field(
        default="http://localhost:1234/v1",
        description="LM Studio base URL"
    )
    lm_studio_model: str = Field(
        default="deepseek-r1-0528-qwen3-8b",
        description="LM Studio model name"
    )
    
    # Database
    database_url: str = Field(
        default="postgresql://agent_user:agent_pass@localhost:5432/agent_team_db",
        description="PostgreSQL connection URL"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # Vector Database
    pinecone_api_key: Optional[str] = Field(default=None, description="Pinecone API key")
    pinecone_environment: Optional[str] = Field(default=None, description="Pinecone environment")
    pinecone_index_name: str = Field(
        default="agent-team-memory",
        description="Pinecone index name"
    )
    
    # Agent Configuration
    max_agents_per_project: int = Field(default=10, description="Maximum agents per project")
    agent_timeout_seconds: int = Field(default=300, description="Agent operation timeout")
    agent_retry_attempts: int = Field(default=3, description="Agent retry attempts")
    
    # MCP Configuration
    mcp_filesystem_path: str = Field(
        default="/tmp/agent-projects",
        description="MCP filesystem server path"
    )
    mcp_git_enabled: bool = Field(default=True, description="Enable MCP Git server")
    mcp_shell_enabled: bool = Field(default=True, description="Enable MCP Shell server")
    mcp_puppeteer_enabled: bool = Field(default=True, description="Enable MCP Puppeteer server")
    
    # Agent LLM Mapping
    agent_llm_mapping: Dict[str, str] = Field(
        default={
            "manager": "deepseek",
            "pm": "deepseek",
            "architect": "qwen-max",
            "developer": "deepseek",
            "qa": "qwen-72b",
            "ui": "qwen-vl",
            "scrum": "local",
            "reviewer": "deepseek"
        },
        description="Mapping of agent types to LLM providers"
    )
    
    # Project paths
    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent
    
    @property
    def data_dir(self) -> Path:
        """Get data directory."""
        return self.project_root / "data"
    
    @property
    def logs_dir(self) -> Path:
        """Get logs directory."""
        return self.project_root / "logs"
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v.upper()
    
    def get_llm_config(self, provider: str) -> Dict[str, Any]:
        """Get LLM configuration for a specific provider."""
        configs = {
            "deepseek": {
                "api_key": self.deepseek_api_key,
                "base_url": self.deepseek_api_base,
                "model": "deepseek-chat",
            },
            "qwen-max": {
                "api_key": self.aliyun_api_key,
                "endpoint": self.aliyun_api_endpoint,
                "model": "qwen-max",
            },
            "qwen-72b": {
                "api_key": self.aliyun_api_key,
                "endpoint": self.aliyun_api_endpoint,
                "model": "qwen-72b-chat",
            },
            "qwen-vl": {
                "api_key": self.aliyun_api_key,
                "endpoint": self.aliyun_api_endpoint,
                "model": "qwen-vl-plus",
            },
            "local": {
                "base_url": self.lm_studio_base_url,
                "model": self.lm_studio_model,
                "api_key": "not-needed",  # LM Studio doesn't require API key
            }
        }
        
        if provider not in configs:
            raise ValueError(f"Unknown LLM provider: {provider}")
        
        return configs[provider]
    
    def get_mcp_servers(self, agent_type: str) -> Dict[str, Dict[str, Any]]:
        """Get MCP server configuration for a specific agent type."""
        mcp_configs = {
            "developer": {
                "filesystem": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-filesystem", self.mcp_filesystem_path]
                },
                "git": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-git"]
                } if self.mcp_git_enabled else None,
                "shell": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-shell"]
                } if self.mcp_shell_enabled else None,
            },
            "qa": {
                "filesystem": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-filesystem", f"{self.mcp_filesystem_path}/test-reports"]
                },
                "puppeteer": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-puppeteer"]
                } if self.mcp_puppeteer_enabled else None,
                "shell": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-shell"]
                } if self.mcp_shell_enabled else None,
            },
            "architect": {
                "filesystem": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-filesystem", self.mcp_filesystem_path]
                },
                "git": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-git"]
                } if self.mcp_git_enabled else None,
            }
        }
        
        # Remove None values
        if agent_type in mcp_configs:
            return {k: v for k, v in mcp_configs[agent_type].items() if v is not None}
        return {}


# Create global settings instance
settings = Settings()