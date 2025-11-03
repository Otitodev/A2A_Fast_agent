"""
Centralized logging configuration for the application.
"""
import logging
import sys
from typing import Optional
from app.config import get_settings

def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Configure application logging.
    
    Args:
        log_level: Override the default log level from settings
    """
    settings = get_settings()
    level = log_level or settings.log_level
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name."""
    return logging.getLogger(name)