"""Execution history model for task executions."""

from typing import Optional
from pydantic import BaseModel, Field


class ExecutionHistory(BaseModel):
    """
    Execution history entry for a task.
    
    Represents a single execution record from the task's execution history.
    """
    
    execution_number: int = Field(..., ge=1, description="Sequential execution number for this task")
    status: str = Field(..., description="Execution status (success, failed, timeout)")
    started_at: Optional[str] = Field(None, description="ISO timestamp when execution started")
    completed_at: Optional[str] = Field(None, description="ISO timestamp when execution completed")
    duration_seconds: Optional[float] = Field(None, ge=0, description="Execution duration in seconds")
    http_status_code: Optional[int] = Field(None, ge=100, le=599, description="HTTP status code if applicable")
    error_type: Optional[str] = Field(None, description="Type of error if execution failed")
    error_message: Optional[str] = Field(None, description="Error message if execution failed")
    retry_count: int = Field(0, ge=0, description="Number of retry attempts")
    is_retry: bool = Field(False, description="Whether this is a retry execution")


