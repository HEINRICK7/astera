from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime

# Requests
class CreateWorkflowRequest(BaseModel):
    name: str
    description: Optional[str] = None
    configuration: Dict[str, Any] = Field(default_factory=dict)

class ExecuteWorkflowRequest(BaseModel):
    inputs: Dict[str, Any] = Field(default_factory=dict)
    callback_url: Optional[str] = None

class CreateStepRequest(BaseModel):
    name: str
    step_type: str
    config: Dict[str, Any] = Field(default_factory=dict)

# Responses
class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    status: str

class WorkflowExecutionResponse(BaseModel):
    execution_id: str
    workflow_id: str
    status: str
    message: str

class ExecutionStatusResponse(BaseModel):
    execution_id: str
    status: str
    outputs: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Dict[str, Any]] = None
