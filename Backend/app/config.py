from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import json


class Settings(BaseSettings):
    # Database - will read from DATABASE_URL environment variable (case-insensitive)
    # Priority: Environment variable > .env file
    database_url: str
    
    # Ollama
    ollama_base_url: str
    ollama_default_model: str
    
    # Tavily Search
    tavily_api_key: str
    
    # Langfuse
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_host: str
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # Application
    environment: str = "development"
    debug: bool = True
    cors_origins: List[str] = ["*"]
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    project_name: str = "AI Chat App"
    version: str = "1.0.0"
    
    # LlamaIndex Configuration
    chat_memory_buffer_size: int = 20
    llamaindex_max_iterations: int = 5
    llamaindex_verbose: bool = True
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from JSON string or return as-is if already a list."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                # Fallback to splitting by comma if not valid JSON
                return [origin.strip() for origin in v.split(",")]
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,  # Allows DATABASE_URL to map to database_url
        env_ignore_empty=True,
        extra="ignore",
    )

# Global settings instance
# Settings will automatically load from .env file and environment variables
# Environment variables take precedence over .env file values
settings = Settings()

