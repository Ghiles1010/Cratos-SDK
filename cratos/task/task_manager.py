"""TaskManager class for managing task operations - batch only."""

import logging
from typing import List, Optional, Any, Dict, Union
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import CratosClient
    from ..models.task import Task
    from ..models.execution_history import ExecutionHistory

from ..models.task import Task
from .actions.mixins.schedule_batch import ScheduleBatchMixin
from .actions.mixins.list_batch import ListBatchMixin
from .actions.mixins.cancel_batch import CancelBatchMixin
from .actions.mixins.pause_batch import PauseBatchMixin
from .actions.mixins.resume_batch import ResumeBatchMixin
from .actions.mixins.retry_batch import RetryBatchMixin
from .actions.mixins.delete_batch import DeleteBatchMixin
from .actions.mixins.get_batch import GetBatchMixin
from .actions.mixins.update_batch import UpdateBatchMixin
from .actions.mixins.execution_history_batch import ExecutionHistoryBatchMixin

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Manager class for task operations - batch only.
    
    All operations are batch-only to prevent inefficient loops.
    Task is a simple data holder with no methods.
    """
    
    def __init__(self, client: "CratosClient"):
        """
        Initialize task manager.
        
        Args:
            client: CratosClient instance
        """
        self.client = client
        # Initialize batch mixins
        self._schedule_batch = ScheduleBatchMixin(client)
        self._list_batch = ListBatchMixin(client)
        self._cancel_batch = CancelBatchMixin(client)
        self._pause_batch = PauseBatchMixin(client)
        self._resume_batch = ResumeBatchMixin(client)
        self._retry_batch = RetryBatchMixin(client)
        self._delete_batch = DeleteBatchMixin(client)
        self._get_batch = GetBatchMixin(client)
        self._update_batch = UpdateBatchMixin(client)
        self._execution_history_batch = ExecutionHistoryBatchMixin(client)
    
    def list(self) -> List["Task"]:
        """List all tasks for the authenticated user."""
        return self._list_batch.list()
    
    def list_scheduled(self) -> List["Task"]:
        """List all scheduled tasks for the authenticated user."""
        return self._list_batch.list_scheduled()
    
    async def schedule(self, tasks: List["Task"], max_workers: Optional[int] = None) -> List[str]:
        """
        Schedule multiple tasks in parallel (batch only).
        
        Args:
            tasks: List of Task instances to schedule
            max_workers: Maximum number of worker threads
        
        Returns:
            List of task IDs in the same order as input
        """
        return await self._schedule_batch.schedule_many(tasks, max_workers=max_workers)
    
    async def cancel(self, task_ids: List[str], max_workers: Optional[int] = None) -> List["Task"]:
        """
        Cancel multiple tasks in parallel (batch only).
        
        Args:
            task_ids: List of task IDs to cancel
            max_workers: Maximum number of worker threads
        
        Returns:
            List of updated Task objects in the same order as input
        """
        return await self._cancel_batch.cancel_many(task_ids, max_workers=max_workers)
    
    async def pause(self, task_ids: List[str], max_workers: Optional[int] = None) -> List["Task"]:
        """
        Pause multiple recurring tasks in parallel (batch only).
        
        Args:
            task_ids: List of task IDs to pause
            max_workers: Maximum number of worker threads
        
        Returns:
            List of updated Task objects in the same order as input
        """
        return await self._pause_batch.pause_many(task_ids, max_workers=max_workers)
    
    async def resume(self, task_ids: List[str], max_workers: Optional[int] = None) -> List["Task"]:
        """
        Resume multiple paused tasks in parallel (batch only).
        
        Args:
            task_ids: List of task IDs to resume
            max_workers: Maximum number of worker threads
        
        Returns:
            List of updated Task objects in the same order as input
        """
        return await self._resume_batch.resume_many(task_ids, max_workers=max_workers)
    
    async def retry(self, task_ids: List[str], max_workers: Optional[int] = None) -> List["Task"]:
        """
        Retry multiple failed tasks in parallel (batch only).
        
        Args:
            task_ids: List of task IDs to retry
            max_workers: Maximum number of worker threads
        
        Returns:
            List of updated Task objects in the same order as input
        """
        return await self._retry_batch.retry_many(task_ids, max_workers=max_workers)
    
    async def delete(self, task_ids: List[str], max_workers: Optional[int] = None) -> List[bool]:
        """
        Delete multiple tasks in parallel (batch only).
        
        Args:
            task_ids: List of task IDs to delete
            max_workers: Maximum number of worker threads
        
        Returns:
            List of booleans indicating success in the same order as input
        """
        return await self._delete_batch.delete_many(task_ids, max_workers=max_workers)
    
    async def get(self, task_ids: List[str], max_workers: Optional[int] = None) -> List[Optional["Task"]]:
        """
        Get multiple tasks in parallel (batch only).
        
        Args:
            task_ids: List of task IDs to retrieve
            max_workers: Maximum number of worker threads
        
        Returns:
            List of Task objects (or None if not found) in the same order as input
        """
        return await self._get_batch.get_many(task_ids, max_workers=max_workers)
    
    async def update(self, tasks: List["Task"], max_workers: Optional[int] = None) -> List["Task"]:
        """
        Update multiple tasks in parallel (batch only).
        
        Args:
            tasks: List of Task objects with task_id and fields to update
                   Only non-None fields will be updated
            max_workers: Maximum number of worker threads
        
        Returns:
            List of updated Task objects in the same order as input
        """
        return await self._update_batch.update_many(tasks, max_workers=max_workers)
    
    async def get_execution_history(
        self, 
        task_ids: List[str], 
        max_workers: Optional[int] = None
    ) -> List[Optional[List["ExecutionHistory"]]]:
        """
        Get execution history for multiple tasks in parallel (batch only).
        
        Args:
            task_ids: List of task IDs to retrieve execution history for
            max_workers: Maximum number of worker threads
        
        Returns:
            List of ExecutionHistory lists (or None if task not found) in the same order as input
            Each inner list contains up to 20 most recent executions
        """
        return await self._execution_history_batch.get_execution_history_many(task_ids, max_workers=max_workers)

