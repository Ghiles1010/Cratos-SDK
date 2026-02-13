"""Get batch mixin for TaskManager operations."""

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


class GetBatchMixin:
    """Mixin to add batch get functionality to TaskManager."""
    
    def __init__(self, client: "CratosClient"):
        """Initialize get batch mixin."""
        self._client = client
    
    async def get_many(
        self,
        task_ids: List[str],
        max_workers: Optional[int] = None
    ) -> List[Optional["Task"]]:
        """Get multiple tasks in parallel."""
        if not task_ids:
            return []
        
        if max_workers is None:
            max_workers = min(32, len(task_ids) + 4)
        
        async def get_one(task_id: str) -> Optional["Task"]:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                return await loop.run_in_executor(executor, self._get_single, task_id)
        
        results = await asyncio.gather(*[get_one(task_id) for task_id in task_ids])
        logger.info(f"Retrieved {len(results)} tasks in parallel using {max_workers} workers")
        return list(results)
    
    def _get_single(self, task_id: str) -> Optional["Task"]:
        """Get a single task (synchronous, used by thread pool)."""
        url = f"{self._client.base_url}/api/tasks/{task_id}/"
        try:
            response = self._client.session.get(url, timeout=self._client.timeout)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            return Task(**data)
        except requests.RequestException as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise

