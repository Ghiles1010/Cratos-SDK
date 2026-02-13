"""Update batch mixin for TaskManager operations."""

import logging
import asyncio
import requests
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

if TYPE_CHECKING:
    from ....client import CratosClient
    from ....models.task import Task

from ....models.task import Task

logger = logging.getLogger(__name__)


class UpdateBatchMixin:
    """Mixin to add batch update functionality to TaskManager."""
    
    def __init__(self, client: "CratosClient"):
        """
        Initialize update batch mixin.
        
        Args:
            client: CratosClient instance
        """
        self._client = client
    
    async def update_many(
        self,
        tasks: List["Task"],
        max_workers: Optional[int] = None
    ) -> List["Task"]:
        """
        Update multiple tasks in parallel.
        
        Args:
            tasks: List of Task objects with task_id and fields to update
                   Only non-None fields will be updated
            max_workers: Maximum number of worker threads
                        (default: min(32, len(tasks) + 4))
        
        Returns:
            List of updated Task objects in the same order as input
        """
        if not tasks:
            return []
        
        if max_workers is None:
            max_workers = min(32, len(tasks) + 4)
        
        async def update_one(task: "Task") -> "Task":
            """Update a single task in a thread pool."""
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                return await loop.run_in_executor(
                    executor,
                    self._update_single,
                    task
                )
        
        # Update all tasks in parallel
        results = await asyncio.gather(*[update_one(task) for task in tasks])
        logger.info(f"Updated {len(results)} tasks in parallel using {max_workers} workers")
        return list(results)
    
    def _update_single(self, task: "Task") -> "Task":
        """Update a single task (synchronous, used by thread pool)."""
        if not task.task_id:
            raise ValueError("task_id is required for update")
        
        url = f"{self._client.base_url}/api/tasks/{task.task_id}/"
        
        # Build payload with only non-None fields (excluding task_id and read-only fields)
        read_only_fields = {
            'task_id', 'status', 'result', 'user', 'created_at', 
            'updated_at', 'started_at', 'completed_at', 'next_run_at',
            'last_run_at', 'run_count', 'retry_count', 'execution_time',
            'is_overdue', 'is_recurring', 'scheduler_info'
        }
        
        payload: Dict[str, Any] = {}
        task_dict = task.model_dump(exclude_none=True)
        
        for key, value in task_dict.items():
            if key not in read_only_fields:
                # Convert datetime objects to ISO strings
                if isinstance(value, datetime):
                    payload[key] = value.isoformat()
                else:
                    payload[key] = value
        
        try:
            response = self._client.session.patch(url, json=payload, timeout=self._client.timeout)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Task {task.task_id} updated successfully")
            return Task(**data)
        except requests.RequestException as e:
            logger.error(f"Failed to update task {task.task_id}: {e}")
            raise

