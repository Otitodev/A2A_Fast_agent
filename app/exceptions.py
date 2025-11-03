from fastapi import HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional, List
from pydantic import BaseModel

# Import ErrorResponse from schemas to avoid duplication
from app.schemas import ErrorResponse

class AppException(Exception):
    """Base exception class for application-specific exceptions"""
    def __init__(self, message: str, status_code: int, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class LLMServiceError(AppException):
    """Raised when there's an error with the LLM service"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )

class ValidationError(AppException):
    """Raised when input validation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )

class NotFoundError(AppException):
    """Raised when a requested resource is not found"""
    def __init__(self, resource: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )

async def http_exception_handler(request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    from app.schemas import ErrorType
    error = ErrorResponse.create(
        error_type=ErrorType.BAD_REQUEST if exc.status_code == 400 else ErrorType.INTERNAL_ERROR,
        message=exc.detail,
        suggestion="Please check your request and try again"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump(exclude_none=True)
    )

async def app_exception_handler(request, exc: AppException):
    """Handle custom application exceptions"""
    from app.schemas import ErrorType
    error = ErrorResponse.create(
        error_type=ErrorType.INTERNAL_ERROR,
        message=exc.message,
        suggestion="Please try again later"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error.model_dump(exclude_none=True)
    )

async def validation_exception_handler(request, exc: RequestValidationError):
    """Handle request validation errors"""
    from app.schemas import ErrorType
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"]) or "request"
        errors.append(f"{field}: {error['msg']}")
    
    error_response = ErrorResponse.create(
        error_type=ErrorType.VALIDATION_ERROR,
        message="Request validation failed",
        suggestion="Please check your request parameters and try again"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump(exclude_none=True)
    )

async def generic_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions"""
    from app.schemas import ErrorType
    error = ErrorResponse.create(
        error_type=ErrorType.INTERNAL_ERROR,
        message="An unexpected error occurred",
        suggestion="Please try again later or contact support if the issue persists"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error.model_dump(exclude_none=True)
    )
