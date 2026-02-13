"""Delete batch mixin for TaskManager operations."""

import logging
import asyncio
import requests
from typing import List, Optional, TYPE_CHECKING
from concurrent.futures import ThreadPoolExecutor

if TYPE_CHECKING:
    from ....client import CratosClient

logger = logging.getLogger(__name__)


class DeleteBatchMixin:
    """Mixin to add batch delete functionality to TaskManager."""
    
    def __init__(self, client: "CratosClient"):
        """Initialize delete batch mixin."""
        self._client = client
    
    async def delete_many(
        self,
        task_ids: List[str],
        max_workers: Optional[int] = None
    ) -> List[bool]:
        """Delete multiple tasks in parallel."""
        if not task_ids:
            return []
        
        if max_workers is None:
            max_workers = min(32, len(task_ids) + 4)
        
        async def delete_one(task_id: str) -> bool:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                return await loop.run_in_executor(executor, self._delete_single, task_id)
        
        results = await asyncio.gather(*[delete_one(task_id) for task_id in task_ids])
        logger.info(f"Deleted {len(results)} tasks in parallel using {max_workers} workers")
        return list(results)
    
    def _delete_single(self, task_id: str) -> bool:
        """Delete a single task (synchronous, used by thread pool)."""
        url = f"{self._client.base_url}/api/tasks/{task_id}/"
        try:
            response = self._client.session.delete(url, timeout=self._client.timeout)
            if response.status_code == 404:
                logger.warning(f"Task {task_id} not found")
                return False
            response.raise_for_status()
            logger.info(f"Task {task_id} deleted successfully")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise

