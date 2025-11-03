"""
A2A Protocol Service Implementation
Implements the Agent-to-Agent protocol according to standard specifications.
"""
from typing import Any, Dict, List, Optional
from app.core.logging import get_logger
from app.services.llm_service import get_llm_service
from app.schemas.a2a_models import A2AError
from app.agent.a2a_handler import get_a2a_handler

logger = get_logger(__name__)

class A2AService:
    """Service implementing A2A protocol methods."""
    
    def __init__(self):
        self._llm_service = get_llm_service()
        self._register_methods()
    
    def _register_methods(self):
        """Register all A2A protocol methods."""
        handler = get_a2a_handler()
        
        # Core A2A methods
        handler.register_method("ping", self.ping)
        handler.register_method("echo", self.echo)
        handler.register_method("capabilities", self.get_capabilities)
        handler.register_method("status", self.get_status)
        
        # AI-specific methods
        handler.register_method("ai.chat", self.ai_chat)
        handler.register_method("ai.complete", self.ai_complete)
        handler.register_method("ai.review_code", self.ai_review_code)
        handler.register_method("ai.explain_code", self.ai_explain_code)
        
        # Task management methods
        handler.register_method("task.create", self.create_task)
        handler.register_method("task.status", self.get_task_status)
        handler.register_method("task.cancel", self.cancel_task)
        
        logger.info("A2A methods registered successfully")
    
    # Core A2A Protocol Methods
    async def ping(self) -> Dict[str, Any]:
        """Ping method to test connectivity."""
        return {
            "status": "pong",
            "timestamp": "2024-01-01T00:00:00Z",
            "agent": "AI Code Reviewer"
        }
    
    async def echo(self, message: str) -> Dict[str, Any]:
        """Echo method to test message passing."""
        return {
            "echo": message,
            "length": len(message)
        }
    
    async def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities."""
        return {
            "agent_type": "ai_code_reviewer",
            "version": "1.0.0",
            "capabilities": [
                "code_review",
                "code_explanation", 
                "ai_chat",
                "text_completion"
            ],
            "supported_languages": [
                "python",
                "javascript",
                "typescript",
                "java",
                "go",
                "rust",
                "c++",
                "c#"
            ],
            "methods": [
                "ping",
                "echo", 
                "capabilities",
                "status",
                "ai.chat",
                "ai.complete",
                "ai.review_code",
                "ai.explain_code",
                "task.create",
                "task.status",
                "task.cancel"
            ]
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Return agent status."""
        try:
            llm_health = self._llm_service.health_check()
            return {
                "status": "online",
                "health": "healthy" if llm_health["status"] == "healthy" else "degraded",
                "services": {
                    "llm": llm_health
                },
                "uptime": "unknown",  # Could implement actual uptime tracking
                "load": "normal"
            }
        except Exception as e:
            logger.error(f"Status check failed: {str(e)}")
            return {
                "status": "online",
                "health": "degraded",
                "error": str(e)
            }
    
    # AI-specific Methods
    async def ai_chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle AI chat conversations."""
        try:
            if not message:
                raise A2AError(-32602, "Invalid params: message is required")
            
            response = self._llm_service.get_response(message)
            
            return {
                "response": response,
                "context": context or {},
                "model": self._llm_service._settings.mistral_model,
                "timestamp": "2024-01-01T00:00:00Z"
            }
        except Exception as e:
            logger.error(f"Error in ai.chat: {str(e)}")
            raise A2AError(-32603, f"Internal error: {str(e)}")
    
    async def ai_complete(self, prompt: str, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Complete text using AI."""
        try:
            if not prompt:
                raise A2AError(-32602, "Invalid params: prompt is required")
            
            # Use a completion-specific system prompt
            system_prompt = (
                "You are a helpful AI assistant. Complete the given text naturally and coherently. "
                "Provide only the completion, not the original prompt."
            )
            
            response = self._llm_service.get_response(prompt, system_prompt)
            
            return {
                "completion": response,
                "model": self._llm_service._settings.mistral_model,
                "tokens_used": len(response.split()),  # Rough estimate
                "timestamp": "2024-01-01T00:00:00Z"
            }
        except Exception as e:
            logger.error(f"Error in ai.complete: {str(e)}")
            raise A2AError(-32603, f"Internal error: {str(e)}")
    
    async def ai_review_code(self, code: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Review code and provide suggestions."""
        try:
            if not code:
                raise A2AError(-32602, "Invalid params: code is required")
            
            system_prompt = (
                "You are an expert code reviewer. Analyze the provided code and give constructive feedback. "
                "Focus on: 1) Code quality and best practices, 2) Potential bugs or issues, "
                "3) Performance improvements, 4) Security considerations. "
                "Provide specific, actionable suggestions."
            )
            
            prompt = f"Please review this {language or 'code'}:\n\n```\n{code}\n```"
            review = self._llm_service.get_response(prompt, system_prompt)
            
            return {
                "review": review,
                "language": language,
                "code_length": len(code),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        except Exception as e:
            logger.error(f"Error in ai.review_code: {str(e)}")
            raise A2AError(-32603, f"Internal error: {str(e)}")
    
    async def ai_explain_code(self, code: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Explain what the code does."""
        try:
            if not code:
                raise A2AError(-32602, "Invalid params: code is required")
            
            system_prompt = (
                "You are a helpful programming tutor. Explain the provided code clearly and concisely. "
                "Break down what each part does, explain the logic flow, and mention any important concepts. "
                "Make it understandable for developers at different skill levels."
            )
            
            prompt = f"Please explain this {language or 'code'}:\n\n```\n{code}\n```"
            explanation = self._llm_service.get_response(prompt, system_prompt)
            
            return {
                "explanation": explanation,
                "language": language,
                "code_length": len(code),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        except Exception as e:
            logger.error(f"Error in ai.explain_code: {str(e)}")
            raise A2AError(-32603, f"Internal error: {str(e)}")
    
    # Task Management Methods (Basic Implementation)
    async def create_task(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an asynchronous task."""
        # This is a basic implementation - in production you'd want proper task queuing
        try:
            task_id = f"task_{hash(str(params))}"
            
            # For now, execute immediately (in production, queue this)
            if method == "ai.chat":
                result = await self.ai_chat(**params)
            elif method == "ai.review_code":
                result = await self.ai_review_code(**params)
            elif method == "ai.explain_code":
                result = await self.ai_explain_code(**params)
            else:
                raise A2AError(-32601, f"Method not found: {method}")
            
            return {
                "task_id": task_id,
                "status": "completed",
                "result": result,
                "created_at": "2024-01-01T00:00:00Z",
                "completed_at": "2024-01-01T00:00:00Z"
            }
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            raise A2AError(-32603, f"Internal error: {str(e)}")
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status."""
        # Basic implementation - in production you'd check actual task storage
        return {
            "task_id": task_id,
            "status": "completed",
            "message": "Task status tracking not fully implemented"
        }
    
    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a task."""
        # Basic implementation
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task cancellation not fully implemented"
        }

# Global service instance
_a2a_service: Optional[A2AService] = None

def get_a2a_service() -> A2AService:
    """Get the global A2A service instance."""
    global _a2a_service
    if _a2a_service is None:
        _a2a_service = A2AService()
    return _a2a_service