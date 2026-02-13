"""Task model - unified model for both creation and API response."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, HttpUrl, Field

from .execution_history import ExecutionHistory


class Task(BaseModel):
    """
    Task model - unified model for both creation and API response.
    
    When creating a task, only provide the required fields (task_name, callback_url).
    When receiving from API, all fields are populated.
    
    No methods, just data. All operations are done via TaskManager batch methods.
    
    Example (creation):
        ```python
        task = Task(
            task_name="my_task",
            callback_url="https://example.com/webhook",
            task_kwargs={"key": "value"}
        )
        tasks = [task]
        task_ids = await client.tasks.schedule(tasks)
        ```
    
    Example (from API):
        ```python
        tasks = client.tasks.list()
        task = tasks[0]  # All fields are populated
        ```
    """
    
    # Required for creation, present in response
    task_name: str = Field(..., description="Name of the task")
    callback_url: Union[HttpUrl, str] = Field(..., description="URL to notify when task executes")
    
    # Optional for creation, present in response
    task_id: Optional[str] = Field(None, description="Task ID (set by server)")
    status: Optional[str] = Field(None, description="Task status (set by server)")
    
    # Task arguments
    task_args: List[Any] = Field(default_factory=list, description="Positional arguments for the task")
    task_kwargs: Dict[str, Any] = Field(default_factory=dict, description="Keyword arguments for the task")
    
    # Scheduling
    schedule_type: str = Field("one_off", description="Type of schedule: one_off, cron, or interval")
    schedule_time: Optional[Union[datetime, str]] = Field(None, description="When to execute (datetime or ISO string)")
    cron_expression: str = Field("", description="Cron expression (required if schedule_type='cron')")
    interval_seconds: Optional[int] = Field(None, description="Repeat interval in seconds (required if schedule_type='interval')")
    ends_at: Optional[Union[datetime, str]] = Field(None, description="End time for recurring tasks (datetime or ISO string)")
    task_timezone: str = Field("UTC", description="IANA timezone, e.g. 'America/New_York'")
    next_run_at: Optional[str] = Field(None, description="Next scheduled run time (set by server)")
    last_run_at: Optional[str] = Field(None, description="Last execution time (set by server)")
    run_count: int = Field(0, description="Number of times task has run (set by server)")
    is_paused: bool = Field(False, description="Whether task is paused (set by server)")
    
    # Retry
    retry_policy: str = Field("none", description="Retry policy: none, fixed, linear, or exponential")
    max_retries: int = Field(0, description="Maximum retry attempts")
    retry_delay_seconds: int = Field(60, description="Base delay between retries in seconds")
    retry_count: int = Field(0, description="Current retry count (set by server)")
    
    # Status and result
    result: Optional[Any] = Field(None, description="Task execution result (set by server)")
    
    # Meta
    user: Optional[str] = Field(None, description="User who created the task (set by server)")
    created_at: Optional[str] = Field(None, description="Creation timestamp (set by server)")
    updated_at: Optional[str] = Field(None, description="Last update timestamp (set by server)")
    started_at: Optional[str] = Field(None, description="Start time of last execution (set by server)")
    completed_at: Optional[str] = Field(None, description="Completion time of last execution (set by server)")
    
    # Computed
    execution_time: Optional[float] = Field(None, description="Execution time in seconds (set by server)")
    is_overdue: Optional[bool] = Field(None, description="Whether task is overdue (set by server)")
    is_recurring: Optional[bool] = Field(None, description="Whether task is recurring (set by server)")
    scheduler_info: Optional[Dict[str, Any]] = Field(None, description="Scheduler metadata (set by server)")
    execution_history: Optional[List[ExecutionHistory]] = Field(None, description="Recent execution history (last 20 executions)")

