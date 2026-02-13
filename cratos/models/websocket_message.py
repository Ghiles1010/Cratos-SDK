"""WebSocket message models."""

from typing import Optional
from pydantic import BaseModel
from .enums import ExecutionStatus, WebSocketMessageType


class WebSocketMessage(BaseModel):
    """WebSocket message format from the gateway."""
    
    type: WebSocketMessageType
    task_id: Optional[str] = None
    status: Optional[ExecutionStatus] = None
    execution_number: Optional[int] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    http_status_code: Optional[int] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: Optional[int] = None
    is_retry: Optional[bool] = None
    topic: Optional[str] = None
    message: Optional[str] = None

