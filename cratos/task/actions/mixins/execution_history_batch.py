"""Execution history batch mixin for TaskManager operations."""

import logging
import asyncio
import requests
from typing import List, Optional, TYPE_CHECKING
from concurrent.futures import ThreadPoolExecutor

if TYPE_CHECKING:
    from ....client import CratosClient
    from ....models.execution_history import ExecutionHistory

from ....models.execution_history import ExecutionHistory
from ....models.task import Task

logger = logging.getLogger(__name__)


class ExecutionHistoryBatchMixin:
    """Mixin to add batch execution history retrieval functionality to TaskManager."""
    
    def __init__(self, client: "CratosClient"):
        """
        Initialize execution history batch mixin.
        
        Args:
            client: CratosClient instance
        """
        self._client = client
    
    async def get_execution_history_many(
        self,
        task_ids: List[str],
        max_workers: Optional[int] = None
    ) -> List[Optional[List["ExecutionHistory"]]]:
        """
        Get execution history for multiple tasks in parallel.
        
        Args:
            task_ids: List of task IDs to retrieve execution history for
            max_workers: Maximum number of worker threads
                      (default: min(32, len(task_ids) + 4))
        
        Returns:
            List of ExecutionHistory lists (or None if task not found) in the same order as input
            Each inner list contains up to 20 most recent executions
        """
        if not task_ids:
            return []
        
        if max_workers is None:
            max_workers = min(32, len(task_ids) + 4)
        
        async def get_history_one(task_id: str) -> Optional[List["ExecutionHistory"]]:
            """Get execution history for a single task in a thread pool."""
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                return await loop.run_in_executor(
                    executor,
                    self._get_execution_history_single,
                    task_id
                )
        
        # Get history for all tasks in parallel
        results = await asyncio.gather(*[get_history_one(task_id) for task_id in task_ids])
        logger.info(f"Retrieved execution history for {len(results)} tasks in parallel using {max_workers} workers")
        return list(results)
    
    def _get_execution_history_single(self, task_id: str) -> Optional[List["ExecutionHistory"]]:
        """Get execution history for a single task (synchronous, used by thread pool)."""
        url = f"{self._client.base_url}/api/tasks/{task_id}/"
        try:
            response = self._client.session.get(url, timeout=self._client.timeout)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            task = Task(**data)
            
            # Extract execution_history from task
            if task.execution_history:
                return task.execution_history
            return []
        except requests.RequestException as e:
            logger.error(f"Failed to get execution history for task {task_id}: {e}")
            raise


