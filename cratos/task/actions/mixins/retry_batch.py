"""Retry batch mixin for TaskManager operations."""

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


class RetryBatchMixin:
    """Mixin to add batch retry functionality to TaskManager."""
    
    def __init__(self, client: "CratosClient"):
        """Initialize retry batch mixin."""
        self._client = client
    
    async def retry_many(
        self,
        task_ids: List[str],
        max_workers: Optional[int] = None
    ) -> List["Task"]:
        """Retry multiple tasks in parallel."""
        if not task_ids:
            return []
        
        if max_workers is None:
            max_workers = min(32, len(task_ids) + 4)
        
        async def retry_one(task_id: str) -> "Task":
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                return await loop.run_in_executor(executor, self._retry_single, task_id)
        
        results = await asyncio.gather(*[retry_one(task_id) for task_id in task_ids])
        logger.info(f"Retried {len(results)} tasks in parallel using {max_workers} workers")
        return list(results)
    
    def _retry_single(self, task_id: str) -> "Task":
        """Retry a single task (synchronous, used by thread pool)."""
        url = f"{self._client.base_url}/api/tasks/{task_id}/retry/"
        try:
            response = self._client.session.post(url, timeout=self._client.timeout)
            response.raise_for_status()
            return Task(**response.json())
        except requests.RequestException as e:
            logger.error(f"Failed to retry task {task_id}: {e}")
            raise

