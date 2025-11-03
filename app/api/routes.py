"""
API routes for the application.
Separated from main.py for better organization.
"""
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse

from app.core.logging import get_logger
from app.schemas import WebhookMessage, TelexResponse, ErrorResponse, ErrorType
from app.services.telex_service import get_telex_service
from app.services.llm_service import get_llm_service
from app.exceptions import AppException, LLMServiceError, ValidationError

logger = get_logger(__name__)

# Create routers
main_router = APIRouter()
a2a_router = APIRouter(prefix="/a2a", tags=["A2A"])

@main_router.get("/", status_code=status.HTTP_200_OK)
async def root():
    """Root endpoint that verifies the server is running."""
    return {
        "status": "Agent is running successfully!", 
        "service": "AI Code Reviewer with A2A Protocol",
        "endpoints": {
            "a2a": "/a2a (POST) - A2A Protocol endpoint",
            "webhook": "/webhook (POST) - Telex webhook endpoint",
            "test_llm": "/test-llm (GET) - Test LLM connection",
            "health": "/health (GET) - Health check"
        }
    }

@main_router.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        llm_health = get_llm_service().health_check()
        return {
            "status": "healthy",
            "services": {
                "llm": llm_health
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e)
        }

@main_router.post("/webhook", response_model=TelexResponse, status_code=status.HTTP_200_OK)
async def telex_webhook_handler(message: WebhookMessage):
    """
    Receives the message payload from Telex.im and sends an AI-generated response back.
    """
    try:
        telex_service = get_telex_service()
        response = telex_service.process_message(message)
        return response
        
    except ValidationError as e:
        logger.warning(f"Validation error in webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except LLMServiceError as e:
        logger.error(f"LLM service error in webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@main_router.get(
    "/test-llm",
    response_model=dict,
    responses={
        200: {"description": "Successfully connected to LLM service"},
        503: {"description": "LLM service unavailable"}
    }
)
async def test_llm_connection():
    """
    Test endpoint to verify LLM connection and basic functionality.
    """
    try:
        llm_service = get_llm_service()
        health_result = llm_service.health_check()
        
        if health_result["status"] == "healthy":
            return {
                "status": "success",
                "llm_response": health_result["response"],
                "message": "LLM connection is working correctly!"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"LLM service unavailable: {health_result.get('error', 'Unknown error')}"
            )
    except Exception as e:
        logger.error(f"LLM test failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"LLM service unavailable: {str(e)}"
        )

# A2A Protocol routes
@a2a_router.post("/ping")
async def ping():
    """Simple ping method to test the connection"""
    return {"status": "pong"}

@a2a_router.post("/chat")
async def ai_chat(message: str, context: dict = None):
    """Handle AI chat messages"""
    try:
        llm_service = get_llm_service()
        response = llm_service.get_response(message)
        return {
            "response": response,
            "context": context or {}
        }
    except Exception as e:
        logger.error(f"Error in ai.chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))