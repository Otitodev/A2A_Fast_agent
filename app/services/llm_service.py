"""
LLM service for handling AI interactions.
Refactored from app/agent/core.py for better separation of concerns.
"""
from typing import Optional
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from app.config import get_settings
from app.core.logging import get_logger
from app.exceptions import LLMServiceError, ValidationError

logger = get_logger(__name__)

class LLMService:
    """Service for handling LLM interactions."""
    
    def __init__(self):
        self._client: Optional[MistralClient] = None
        self._settings = get_settings()
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Mistral client with proper error handling."""
        if not self._settings.mistral_api_key:
            logger.error("MISTRAL_API_KEY environment variable is not set")
            raise LLMServiceError("MISTRAL_API_KEY environment variable is not set")
        
        try:
            self._client = MistralClient(api_key=self._settings.mistral_api_key)
            logger.info("Mistral client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Mistral client: {str(e)}")
            raise LLMServiceError(f"Failed to initialize Mistral client: {str(e)}")
    
    def get_response(self, user_input: str, system_prompt: Optional[str] = None) -> str:
        """
        Get an AI response for the given input.
        
        Args:
            user_input: The input text to send to the LLM
            system_prompt: Optional system prompt to override default
            
        Returns:
            str: The generated response from the LLM
            
        Raises:
            LLMServiceError: If there's an issue with the LLM service
            ValidationError: If the input is invalid
        """
        if not user_input or not isinstance(user_input, str):
            raise ValidationError("Input must be a non-empty string")
        
        if not self._client:
            logger.error("LLM client not initialized")
            raise LLMServiceError("LLM service is currently unavailable")
        
        # Use provided system prompt or default
        if not system_prompt:
            system_prompt = self._get_default_system_prompt()
        
        try:
            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_input)
            ]
            
            response = self._client.chat(
                model=self._settings.mistral_model,
                messages=messages
            )
            
            if not response.choices or not response.choices[0].message.content:
                raise LLMServiceError("Received empty response from LLM service")
            
            result = response.choices[0].message.content.strip()
            logger.debug(f"Generated response of length: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get response from LLM service: {str(e)}")
            raise LLMServiceError(
                f"Failed to get response from LLM service: {str(e)}",
                details={"model": self._settings.mistral_model, "error_type": type(e).__name__}
            )
    
    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt for the AI agent."""
        return (
            "You are an **AI Code Reviewer and Helper Agent** for a developer platform. "
            "Your task is to analyze the user's input, which is often a code snippet. "
            "Based on the input, you should either: "
            "1. Provide a concise, constructive review, suggesting improvements for best practices, or "
            "2. Explain the code's purpose, or "
            "3. Answer a question related to the provided code. "
            "Keep your response professional, helpful, and format code using markdown blocks."
        )
    
    def health_check(self) -> dict:
        """
        Perform a health check on the LLM service.
        
        Returns:
            dict: Health check results
        """
        try:
            test_response = self.get_response(
                "Hello! Are you working? Please respond with a short confirmation that you're operational."
            )
            return {
                "status": "healthy",
                "model": self._settings.mistral_model,
                "response": test_response
            }
        except Exception as e:
            logger.error(f"LLM health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "model": self._settings.mistral_model,
                "error": str(e)
            }

# Global service instance
_llm_service: Optional[LLMService] = None

def get_llm_service() -> LLMService:
    """Get the global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service