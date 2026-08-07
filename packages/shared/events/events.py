from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime
import uuid

class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0"

class WorkflowStartedEvent(BaseEvent):
    event_type: str = "workflow.started"
    workflow_id: str
    workflow_name: str
    inputs: Dict[str, Any] = Field(default_factory=dict)

class WorkflowCompletedEvent(BaseEvent):
    event_type: str = "workflow.completed"
    workflow_id: str
    outputs: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: int

class WorkflowFailedEvent(BaseEvent):
    event_type: str = "workflow.failed"
    workflow_id: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None

class StepStartedEvent(BaseEvent):
    event_type: str = "step.started"
    workflow_id: str
    step_id: str
    step_name: str
    inputs: Dict[str, Any] = Field(default_factory=dict)

class StepCompletedEvent(BaseEvent):
    event_type: str = "step.completed"
    workflow_id: str
    step_id: str
    outputs: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: int

class StepFailedEvent(BaseEvent):
    event_type: str = "step.failed"
    workflow_id: str
    step_id: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
