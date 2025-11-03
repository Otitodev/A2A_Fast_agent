from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.api.routes import main_router, a2a_router
from app.api.a2a_routes import router as a2a_main_router
from app.services.a2a_service import get_a2a_service
from app.exceptions import (
    AppException,
    http_exception_handler,
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler
)

# Initialize settings and logging
settings = get_settings()
setup_logging()
logger = get_logger(__name__)

# Initialize A2A service (this registers all the methods)
get_a2a_service()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Agent-to-Agent protocol implementation using FastAPI",
    version=settings.app_version,
    debug=settings.debug
)

# Include routers
app.include_router(main_router)
app.include_router(a2a_router)
app.include_router(a2a_main_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
from fastapi import HTTPException
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

logger.info(f"Starting {settings.app_name} v{settings.app_version}")

# Uvicorn command to run: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1