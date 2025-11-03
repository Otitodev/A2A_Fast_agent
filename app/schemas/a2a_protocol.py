"""
A2A Protocol Schema Definitions
Defines the standard Agent-to-Agent protocol schemas according to JSON-RPC 2.0 specification.
"""
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime

# JSON-RPC 2.0 Error Codes
class JSONRPCErrorCode(int, Enum):
    """Standard JSON-RPC 2.0 error codes."""
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # Custom application error codes (range: -32000 to -32099)
    SERVER_ERROR = -32000
    AGENT_UNAVAILABLE = -32001
    TASK_FAILED = -32002
    TIMEOUT_ERROR = -32003
    RATE_LIMITED = -32004

class A2ACapability(str, Enum):
    """Standard A2A agent capabilities."""
    CHAT = "chat"
    CODE_REVIEW = "code_review"
    CODE_GENERATION = "code_generation"
    TEXT_COMPLETION = "text_completion"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    TASK_EXECUTION = "task_execution"
    FILE_PROCESSING = "file_processing"

class AgentStatus(str, Enum):
    """Agent status values."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    MAINTENANCE = "maintenance"

class AgentHealth(str, Enum):
    """Agent health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

# Core A2A Protocol Models
class A2ARequest(BaseModel):
    """A2A request following JSON-RPC 2.0 specification."""
    jsonrpc: Literal["2.0"] = "2.0"
    method: str = Field(..., description="The method to be invoked")
    params: Optional[Union[Dict[str, Any], List[Any]]] = Field(None, description="Parameters for the method")
    id: Optional[Union[str, int]] = Field(None, description="Request identifier")

class A2AResponse(BaseModel):
    """A2A response following JSON-RPC 2.0 specification."""
    jsonrpc: Literal["2.0"] = "2.0"
    id: Optional[Union[str, int]] = Field(..., description="Request identifier")
    result: Optional[Any] = Field(None, description="Result of the method call")
    error: Optional[Dict[str, Any]] = Field(None, description="Error information if the call failed")
    
    @validator('result', 'error')
    def result_or_error(cls, v, values):
        """Ensure either result or error is present, but not both."""
        if 'result' in values and 'error' in values:
            if values.get('result') is not None and values.get('error') is not None:
                raise ValueError('Response cannot have both result and error')
            if values.get('result') is None and values.get('error') is None:
                raise ValueError('Response must have either result or error')
        return v

class A2ANotification(BaseModel):
    """A2A notification (request without id)."""
    jsonrpc: Literal["2.0"] = "2.0"
    method: str = Field(..., description="The method to be invoked")
    params: Optional[Union[Dict[str, Any], List[Any]]] = Field(None, description="Parameters for the method")

class A2AError(BaseModel):
    """A2A error object."""
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Any] = Field(None, description="Additional error data")

# Agent Information Models
class AgentInfo(BaseModel):
    """Agent information model."""
    id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Human-readable agent name")
    version: str = Field(..., description="Agent version")
    description: Optional[str] = Field(None, description="Agent description")
    capabilities: List[A2ACapability] = Field(..., description="Agent capabilities")
    supported_methods: List[str] = Field(..., description="Supported A2A methods")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class AgentStatusInfo(BaseModel):
    """Agent status information."""
    status: AgentStatus = Field(..., description="Current agent status")
    health: AgentHealth = Field(..., description="Agent health status")
    uptime: Optional[str] = Field(None, description="Agent uptime")
    load: Optional[str] = Field(None, description="Current load level")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    services: Optional[Dict[str, Any]] = Field(None, description="Service status information")

# Method-specific Models
class PingResponse(BaseModel):
    """Response for ping method."""
    status: Literal["pong"] = "pong"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent: Optional[str] = Field(None, description="Agent identifier")

class EchoRequest(BaseModel):
    """Request for echo method."""
    message: str = Field(..., description="Message to echo")

class EchoResponse(BaseModel):
    """Response for echo method."""
    echo: str = Field(..., description="Echoed message")
    length: int = Field(..., description="Message length")

class ChatRequest(BaseModel):
    """Request for ai.chat method."""
    message: str = Field(..., description="Chat message")
    context: Optional[Dict[str, Any]] = Field(None, description="Conversation context")
    system_prompt: Optional[str] = Field(None, description="System prompt override")

class ChatResponse(BaseModel):
    """Response for ai.chat method."""
    response: str = Field(..., description="AI response")
    context: Dict[str, Any] = Field(default_factory=dict, description="Updated context")
    model: Optional[str] = Field(None, description="Model used")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CodeReviewRequest(BaseModel):
    """Request for ai.review_code method."""
    code: str = Field(..., description="Code to review")
    language: Optional[str] = Field(None, description="Programming language")
    focus_areas: Optional[List[str]] = Field(None, description="Specific areas to focus on")

class CodeReviewResponse(BaseModel):
    """Response for ai.review_code method."""
    review: str = Field(..., description="Code review")
    language: Optional[str] = Field(None, description="Detected/specified language")
    issues_found: Optional[int] = Field(None, description="Number of issues found")
    severity: Optional[str] = Field(None, description="Overall severity level")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CodeExplanationRequest(BaseModel):
    """Request for ai.explain_code method."""
    code: str = Field(..., description="Code to explain")
    language: Optional[str] = Field(None, description="Programming language")
    detail_level: Optional[str] = Field("medium", description="Level of detail (basic, medium, detailed)")

class CodeExplanationResponse(BaseModel):
    """Response for ai.explain_code method."""
    explanation: str = Field(..., description="Code explanation")
    language: Optional[str] = Field(None, description="Detected/specified language")
    complexity: Optional[str] = Field(None, description="Code complexity level")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class TaskRequest(BaseModel):
    """Request for task.create method."""
    method: str = Field(..., description="Method to execute as task")
    params: Dict[str, Any] = Field(default_factory=dict, description="Method parameters")
    timeout: Optional[int] = Field(None, description="Task timeout in seconds")
    callback_url: Optional[str] = Field(None, description="Callback URL for task completion")

class TaskResponse(BaseModel):
    """Response for task operations."""
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Task status")
    result: Optional[Any] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

# Batch Request/Response Models
class A2ABatchRequest(BaseModel):
    """Batch request containing multiple A2A requests."""
    requests: List[Union[A2ARequest, A2ANotification]] = Field(..., description="List of requests")

class A2ABatchResponse(BaseModel):
    """Batch response containing multiple A2A responses."""
    responses: List[A2AResponse] = Field(..., description="List of responses")

# Utility Models
class MethodInfo(BaseModel):
    """Information about an A2A method."""
    name: str = Field(..., description="Method name")
    description: str = Field(..., description="Method description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameter schema")
    returns: Dict[str, Any] = Field(default_factory=dict, description="Return value schema")
    examples: Optional[List[Dict[str, Any]]] = Field(None, description="Usage examples")

class CapabilitiesResponse(BaseModel):
    """Response for capabilities method."""
    agent_type: str = Field(..., description="Type of agent")
    version: str = Field(..., description="Agent version")
    capabilities: List[A2ACapability] = Field(..., description="Agent capabilities")
    supported_languages: Optional[List[str]] = Field(None, description="Supported programming languages")
    methods: List[str] = Field(..., description="Available methods")
    method_info: Optional[Dict[str, MethodInfo]] = Field(None, description="Detailed method information")
    limits: Optional[Dict[str, Any]] = Field(None, description="Agent limits and constraints")