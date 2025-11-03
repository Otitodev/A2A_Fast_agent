"""
Service for handling Telex webhook messages.
Extracted from main.py for better separation of concerns.
"""
from typing import Optional
from app.core.logging import get_logger
from app.schemas import WebhookMessage, TelexResponse
from app.exceptions import ValidationError, LLMServiceError

logger = get_logger(__name__)

class TelexService:
    """Service for processing Telex webhook messages."""
    
    def __init__(self):
        # Import here to avoid circular imports
        from app.services.llm_service import get_llm_service
        self._llm_service = get_llm_service()
    
    def process_message(self, message: WebhookMessage) -> TelexResponse:
        """
        Process incoming Telex message and generate an AI response.
        
        Args:
            message: The incoming webhook message from Telex
            
        Returns:
            TelexResponse: The response to send back to Telex
            
        Raises:
            ValidationError: If the message is invalid
            LLMServiceError: If there's an issue with the LLM service
        """
        if not message or not message.content:
            raise ValidationError("Empty message received")
        
        logger.info(f"Processing message from {message.sender_id} in channel {message.channel_id}")
        
        try:
            # Get AI response
            ai_response = self._llm_service.get_response(message.content)
            
            # Create response payload
            response = TelexResponse(
                channel_id=message.channel_id,
                recipient_id=message.sender_id,
                content=ai_response
            )
            
            logger.info(f"Generated response for message from {message.sender_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing Telex message: {str(e)}")
            raise

# Global service instance
_telex_service: Optional['TelexService'] = None

def get_telex_service() -> TelexService:
    """Get the global Telex service instance."""
    global _telex_service
    if _telex_service is None:
        _telex_service = TelexService()
    return _telex_service