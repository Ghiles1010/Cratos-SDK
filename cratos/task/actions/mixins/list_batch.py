"""List batch mixin for TaskManager operations."""

import logging
import requests
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ....client import CratosClient
    from ....models.task import Task

from ....models.task import Task

logger = logging.getLogger(__name__)


class ListBatchMixin:
    """Mixin to add list functionality to TaskManager."""
    
    def __init__(self, client: "CratosClient"):
        """Initialize list batch mixin."""
        self._client = client
    
    def list(self) -> List["Task"]:
        """
        List all tasks for the authenticated user.
        
        Returns:
            List of Task objects
        """
        url = f"{self._client.base_url}/api/tasks/"
        tasks = []
        params = {}
        while url:
            try:
                response = self._client.session.get(url, params=params, timeout=self._client.timeout)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    tasks.extend([Task(**item) for item in data['results']])
                    url = data.get('next')
                    params = {}
                elif isinstance(data, list):
                    tasks.extend([Task(**item) for item in data])
                    url = None
                else:
                    tasks.extend([Task(**item) for item in data.get('tasks', [])])
                    url = None
            except requests.RequestException as e:
                logger.error(f"Failed to list tasks: {e}")
                raise
        return tasks
    
    def list_scheduled(self) -> List["Task"]:
        """
        List all scheduled tasks for the authenticated user.
        
        Returns:
            List of Task objects with status 'scheduled'
        """
        url = f"{self._client.base_url}/api/tasks/scheduled/"
        try:
            response = self._client.session.get(url, timeout=self._client.timeout)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                return [Task(**item) for item in data]
            else:
                return [Task(**item) for item in data.get('tasks', [])]
        except requests.RequestException as e:
            logger.error(f"Failed to list scheduled tasks: {e}")
            raise

