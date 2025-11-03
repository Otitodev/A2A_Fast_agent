from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, TypeVar, Generic, Tuple
from fastapi import Request, HTTPException
from ..schemas import (
    A2ARequest, 
    A2AResponse, 
    A2ANotification, 
    A2AError, 
    TaskRequest, 
    TaskResponse,
    ErrorResponse,
    ErrorType
)
import json
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class A2ARequestContext:
    """Context for A2A requests"""
    def __init__(self, request: Request):
        self.request = request
        self.headers = dict(request.headers)
        self.method = request.method
        self.url = str(request.url)

class A2AResult(Generic[T]):
    """Generic result container for A2A operations"""
    def __init__(self, success: bool, data: T = None, error: ErrorResponse = None):
        self.success = success
        self.data = data
        self.error = error

    @classmethod
    def success(cls, data: T) -> 'A2AResult[T]':
        return cls(True, data=data)
    
    @classmethod
    def error(cls, error: ErrorResponse) -> 'A2AResult[T]':
        return cls(False, error=error)
    
    def to_dict(self) -> Dict[str, Any]:
        if self.success:
            return {"success": True, "data": self.data}
        return {"success": False, "error": self.error.model_dump(exclude_none=True)}

class A2AHandler:
    """Handler for A2A protocol messages"""
    
    def __init__(self):
        self._methods: Dict[str, Callable] = {}
    
    def register_method(self, name: str, handler: Callable):
        """Register a new method handler"""
        self._methods[name] = handler
        return handler
    
    def method(self, name: str):
        """Decorator to register a method handler"""
        def decorator(func):
            self.register_method(name, func)
            return func
        return decorator
    
    async def handle_request(self, request: Request) -> Dict[str, Any]:
        """Handle an incoming A2A request"""
        try:
            # Parse the request
            try:
                body = await request.json()
                if not body:
                    raise ValueError("Empty request body")
                    
                # Handle batch requests
                if isinstance(body, list):
                    results = []
                    for item in body:
                        result = await self._process_single_request(item, request)
                        results.append(result)
                    return results[0] if len(results) == 1 else results
                else:
                    return await self._process_single_request(body, request)
                    
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in request: {str(e)}")
                error = ErrorResponse.create(
                    error_type=ErrorType.BAD_REQUEST,
                    message="Invalid JSON in request body",
                    suggestion="Please check your request body is valid JSON"
                )
                return A2AResult.error(error).to_dict()
                
            except Exception as e:
                logger.exception(f"Error processing request: {str(e)}")
                error = ErrorResponse.create(
                    error_type=ErrorType.INTERNAL_ERROR,
                    message="An error occurred while processing your request",
                    suggestion="Please try again later"
                )
                return A2AResult.error(error).to_dict()
                
        except Exception as e:
            logger.exception("Unexpected error in A2A handler")
            error = ErrorResponse.create(
                error_type=ErrorType.INTERNAL_ERROR,
                message="An unexpected error occurred",
                suggestion="Please try again later"
            )
            return A2AResult.error(error).to_dict()
    
    async def _process_single_request(self, data: Dict[str, Any], request: Request) -> Dict[str, Any]:
        """Process a single A2A request"""
        try:
            # Create request context
            context = A2ARequestContext(request)
            
            # Parse the request
            a2a_request = A2ARequest(**data)
            
            # Check if method exists
            if a2a_request.method not in self._methods:
                error = ErrorResponse.create(
                    error_type=ErrorType.NOT_FOUND,
                    message=f"Method '{a2a_request.method}' not found",
                    suggestion="Check the method name and try again"
                )
                return A2AResult.error(error).to_dict()
            
            # Get the handler
            handler = self._methods[a2a_request.method]
            params = a2a_request.params or {}
            
            # Add context to params if handler accepts it
            handler_signature = handler.__annotations__
            if 'context' in handler_signature:
                if isinstance(params, dict):
                    params['context'] = context
                else:
                    params = list(params) + [context]
            
            # Execute the handler
            try:
                if isinstance(params, dict):
                    result = await handler(**params)
                else:
                    result = await handler(*params)
                
                # Create success response
                return A2AResult.success({
                    "jsonrpc": "2.0",
                    "id": a2a_request.id,
                    "result": result
                }).to_dict()
                
            except A2AError as e:
                logger.error(f"A2A error in {a2a_request.method}: {str(e)}")
                error = ErrorResponse.create(
                    error_type=ErrorType.BAD_REQUEST,
                    message=str(e),
                    suggestion="Check your request parameters and try again"
                )
                return A2AResult.error(error).to_dict()
                
            except Exception as e:
                logger.exception(f"Error executing method {a2a_request.method}")
                error = ErrorResponse.create(
                    error_type=ErrorType.INTERNAL_ERROR,
                    message=f"Error executing {a2a_request.method}",
                    suggestion="Please try again later"
                )
                return A2AResult.error(error).to_dict()
                
        except Exception as e:
            logger.exception(f"Error processing request: {str(e)}")
            error = ErrorResponse.create(
                error_type=ErrorType.INTERNAL_ERROR,
                message="An error occurred while processing your request",
                suggestion="Please try again later"
            )
            return A2AResult.error(error).to_dict()
    
    async def handle_notification(self, request: Request) -> None:
        """Handle an A2A notification (request without id)"""
        try:
            data = await request.json()
            if not data:
                logger.warning("Received empty notification")
                return
                
            # Handle batch notifications
            if isinstance(data, list):
                for item in data:
                    await self._process_single_notification(item, request)
            else:
                await self._process_single_notification(data, request)
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in notification: {str(e)}")
        except Exception as e:
            logger.exception(f"Error handling notification: {str(e)}")
    
    async def _process_single_notification(self, data: Dict[str, Any], request: Request) -> None:
        """Process a single A2A notification"""
        try:
            # Create notification context
            context = A2ARequestContext(request)
            
            # Parse the notification
            notification = A2ANotification(**data)
            
            # Check if method exists
            if notification.method not in self._methods:
                logger.warning(f"Notification method not found: {notification.method}")
                return
            
            # Get the handler
            handler = self._methods[notification.method]
            params = notification.params or {}
            
            # Add context to params if handler accepts it
            handler_signature = handler.__annotations__
            if 'context' in handler_signature:
                if isinstance(params, dict):
                    params['context'] = context
                else:
                    params = list(params) + [context]
            
            # Execute the handler
            try:
                if isinstance(params, dict):
                    await handler(**params)
                else:
                    await handler(*params)
                    
            except Exception as e:
                logger.exception(f"Error in notification handler {notification.method}")
                
        except Exception as e:
            logger.exception(f"Error processing notification: {str(e)}")

# Create a global instance
a2a_handler = A2AHandler()

def get_a2a_handler() -> A2AHandler:
    """Get the global A2A handler instance"""
    return a2a_handler
