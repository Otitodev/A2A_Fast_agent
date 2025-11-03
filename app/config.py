"""
Configuration management for the application.
Centralizes all environment variables and settings.
"""
import os
from typing import Optional
from pydantic import Field
from dotenv import load_dotenv

# Import BaseSettings from the correct location based on pydantic version
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    app_name: str = Field(default="A2A Protocol Server", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # Mistral AI Configuration
    mistral_api_key: Optional[str] = Field(default=None, env="MISTRAL_API_KEY")
    mistral_model: str = Field(default="mistral-small-latest", env="MISTRAL_MODEL")
    
    # Redis Configuration (for future use)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get the application settings."""
    return settings