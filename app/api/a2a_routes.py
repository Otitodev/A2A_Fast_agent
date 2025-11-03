"""
A2A Protocol specific routes.
Handles the main A2A endpoint with comprehensive error handling.
"""
import json
import uuid
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.schemas import ErrorResponse, ErrorType
from app.agent.a2a_handler import get_a2a_handler
from app.exceptions import ValidationError

logger = get_logger(__name__)

router = APIRouter()

@router.post("/a2a")
async def a2a_endpoint(request: Request):
    """
    Handle A2A protocol requests with comprehensive error handling.
    
    This endpoint processes JSON-RPC 2.0 requests and returns appropriate responses.
    It handles both single requests and batch requests.
    """
    try:
        # Log incoming request details
        client_host = request.client.host if request.client else "unknown"
        logger.info(f"Received A2A request from {client_host}")
        
        # Process the request through the A2A handler
        response = await get_a2a_handler().handle_request(request)
        
        # Log successful processing
        logger.debug(f"Successfully processed A2A request from {client_host}")
        return response
        
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in request: {str(e)}"
        logger.error(error_msg)
        error = ErrorResponse.create(
            error_type=ErrorType.BAD_REQUEST,
            message="Invalid request format",
            details=error_msg,
            suggestion="Please ensure your request contains valid JSON"
        )
        return JSONResponse(
            status_code=400,
            content=error.model_dump(exclude_none=True)
        )
        
    except ValidationError as e:
        error_msg = f"Request validation failed: {str(e)}"
        logger.warning(error_msg)
        error = ErrorResponse.create(
            error_type=ErrorType.VALIDATION_ERROR,
            message="Invalid request parameters",
            details=str(e),
            suggestion="Please check your request parameters and try again"
        )
        return JSONResponse(
            status_code=422,
            content=error.model_dump(exclude_none=True)
        )
        
    except Exception as e:
        error_id = str(uuid.uuid4())
        error_msg = f"Unexpected error (ID: {error_id}): {str(e)}"
        logger.exception(f"Error processing A2A request: {error_msg}")
        
        error = ErrorResponse.create(
            error_type=ErrorType.INTERNAL_ERROR,
            message="An unexpected error occurred",
            details=f"Error ID: {error_id}",
            suggestion="Please try again later or contact support if the issue persists"
        )
        return JSONResponse(
            status_code=500,
            content=error.model_dump(exclude_none=True)
        )