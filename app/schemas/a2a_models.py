from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from datetime import datetime

# --- Webhook Models ---
class WebhookMessage(BaseModel):
    """Schema for the incoming message from Telex.im webhook."""
    
    # These fields are crucial for sending a response back
    channel_id: str = Field(..., description="The ID of the conversation channel.")
    sender_id: str = Field(..., description="The ID of the user who sent the message.")
    
    # The actual message content
    content: str = Field(..., description="The text content of the user's message (e.g., code snippet).")
    
    # A few other typical fields you might receive
    timestamp: str = None
    event_type: str = "message_received"


class TelexResponse(BaseModel):
    """Schema for the JSON response the FastAPI app sends back to Telex.im."""
    channel_id: str
    recipient_id: str
    response_type: Literal["message"] = "message"  # Indicates a text response
    content: str
    # You might need to add: flow_id, agent_name, execution_status, etc.


# --- Error Handling ---
class ErrorType(str, Enum):
    """Standard error types for the API"""
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    INTERNAL_ERROR = "internal_error"
    BAD_REQUEST = "bad_request"
    SERVICE_UNAVAILABLE = "service_unavailable"


class ErrorDetail(BaseModel):
    """Detailed error information"""
    type: ErrorType
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None
    suggestion: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response format"""
    success: bool = False
    error: ErrorDetail
    meta: Optional[Dict[str, Any]] = None

    @classmethod
    def create(
        cls,
        error_type: ErrorType,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        suggestion: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> 'ErrorResponse':
        return cls(
            error=ErrorDetail(
                type=error_type,
                message=message,
                field=field,
                value=value,
                suggestion=suggestion
            ),
            meta=meta or {}
        )

    @classmethod
    def validation_error(
        cls,
        message: str = "Validation error",
        field: Optional[str] = None,
        value: Any = None,
        suggestion: Optional[str] = None
    ) -> 'ErrorResponse':
        return cls.create(
            error_type=ErrorType.VALIDATION_ERROR,
            message=message,
            field=field,
            value=value,
            suggestion=suggestion
        )

    @classmethod
    def not_found(
        cls,
        resource: str = "Resource",
        id: Optional[Any] = None,
        suggestion: Optional[str] = None
    ) -> 'ErrorResponse':
        message = f"{resource} not found"
        if id is not None:
            message += f" with id: {id}"
        return cls.create(
            error_type=ErrorType.NOT_FOUND,
            message=message,
            suggestion=suggestion or "Please check the resource ID and try again."
        )

    @classmethod
    def internal_error(
        cls,
        message: str = "An internal server error occurred",
        suggestion: Optional[str] = None
    ) -> 'ErrorResponse':
        return cls.create(
            error_type=ErrorType.INTERNAL_ERROR,
            message=message,
            suggestion=suggestion or "Please try again later or contact support if the problem persists."
        )


# --- A2A Protocol Models ---

class A2ARequest(BaseModel):
    """Base A2A request model following JSON-RPC 2.0 specification"""
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Union[Dict[str, Any], List[Any]]] = None
    id: Optional[Union[str, int, None]] = None

class A2AResponse(BaseModel):
    """Base A2A response model following JSON-RPC 2.0 specification"""
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int, None]]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

    @classmethod
    def success(cls, request_id: Union[str, int, None], result: Any = None):
        return cls(id=request_id, result=result)
    
    @classmethod
    def error(
        cls,
        request_id: Union[str, int, None],
        code: int,
        message: str,
        data: Any = None
    ):
        return cls(
            id=request_id,
            error={
                "code": code,
                "message": message,
                "data": data
            }
        )

class A2ANotification(A2ARequest):
    """A2A notification model (request without id)"""
    id: None = None

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ArtifactType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    DATA = "data"

class Artifact(BaseModel):
    """Represents any output or artifact from an agent"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: ArtifactType
    mime_type: str
    data: Any
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TaskRequest(BaseModel):
    """A2A Task request model"""
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    method: str
    params: Dict[str, Any] = {}
    timeout: Optional[int] = None
    webhook_url: Optional[str] = None

class TaskResponse(BaseModel):
    """A2A Task response model"""
    task_id: str
    status: TaskStatus
    result: Optional[Dict[str, Any]] = None
    artifacts: List[Artifact] = []
    error: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def add_artifact(self, artifact: Artifact):
        self.artifacts.append(artifact)
        self.updated_at = datetime.utcnow()
        return self

class A2AError(Exception):
    """Base exception for A2A protocol errors"""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(f"[{code}] {message}")
