"""Cancel batch mixin for TaskManager operations."""

import logging
import asyncio
import requests
from typing import List, Optional, TYPE_CHECKING
from concurrent.futures import ThreadPoolExecutor

if TYPE_CHECKING:
    from ....client import CratosClient
    from ....models.task import Task

from ....models.task import Task

logger = logging.getLogger(__name__)


class CancelBatchMixin:
    """Mixin to add batch cancel functionality to TaskManager."""
    
    def __init__(self, client: "CratosClient"):
        """
        Initialize cancel batch mixin.
        
        Args:
            client: CratosClient instance
        """
        self._client = client
    
    async def cancel_many(
        self,
        task_ids: List[str],
        max_workers: Optional[int] = None
    ) -> List["Task"]:
        """
        Cancel multiple tasks in parallel.
        
        Args:
            task_ids: List of task IDs to cancel
            max_workers: Maximum number of worker threads (default: min(32, len(task_ids) + 4))
        
        Returns:
            List of updated Task objects in the same order as input
        """
        if not task_ids:
            return []
        
        if max_workers is None:
            max_workers = min(32, len(task_ids) + 4)
        
        async def cancel_one(task_id: str) -> "Task":
            """Cancel a single task in a thread pool."""
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                return await loop.run_in_executor(
                    executor,
                    self._cancel_single,
                    task_id
                )
        
        # Cancel all tasks in parallel
        results = await asyncio.gather(*[cancel_one(task_id) for task_id in task_ids])
        logger.info(f"Cancelled {len(results)} tasks in parallel using {max_workers} workers")
        return list(results)
    
    def _cancel_single(self, task_id: str) -> "Task":
        """Cancel a single task (synchronous, used by thread pool)."""
        url = f"{self._client.base_url}/api/tasks/{task_id}/cancel/"
        try:
            response = self._client.session.post(url, timeout=self._client.timeout)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Task {task_id} cancelled successfully")
            return Task(**data)
        except requests.RequestException as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            raise

