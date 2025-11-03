"""
Legacy core module - maintained for backward compatibility.
New code should use app.services.llm_service and app.services.telex_service.
"""
from app.services.llm_service import get_llm_service
from app.services.telex_service import get_telex_service
from app.schemas import WebhookMessage

# Backward compatibility functions
def get_ai_response(user_input: str) -> str:
    """
    Legacy function for getting AI responses.
    Delegates to the new LLM service.
    """
    return get_llm_service().get_response(user_input)

def process_telex_message(message: WebhookMessage) -> str:
    """
    Legacy function for processing Telex messages.
    Delegates to the new Telex service.
    """
    response = get_telex_service().process_message(message)
    return response.content