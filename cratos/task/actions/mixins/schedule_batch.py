"""Schedule batch mixin for TaskManager operations."""

import logging
import requests
import asyncio
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

if TYPE_CHECKING:
    from ....client import CratosClient
    from ....models.task import Task

from ....models.task import Task

logger = logging.getLogger(__name__)


class ScheduleBatchMixin:
    """Mixin to add batch schedule functionality to TaskManager."""
    
    def __init__(self, client: "CratosClient"):
        """
        Initialize schedule batch mixin.
        
        Args:
            client: CratosClient instance
        """
        self._client = client
    
    def _schedule_single(
        self,
        task_name: str,
        callback_url: str,
        task_args: Optional[List[Any]] = None,
        task_kwargs: Optional[Dict[str, Any]] = None,
        schedule_time: Optional[Union[datetime, str]] = None,
        schedule_type: str = "one_off",
        cron_expression: Optional[str] = None,
        interval_seconds: Optional[int] = None,
        ends_at: Optional[Union[datetime, str]] = None,
        task_timezone: str = "UTC",
        retry_policy: str = "none",
        max_retries: int = 0,
        retry_delay_seconds: int = 60,
    ) -> str:
        """
        Schedule a single task (synchronous, used by thread pool).
        
        Args:
            task_name: Name of the task to execute
            callback_url: URL to notify when task is triggered
            task_args: Positional arguments for the task
            task_kwargs: Keyword arguments for the task
            schedule_time: When to execute (datetime or ISO string)
            schedule_type: "one_off", "cron", or "interval"
            cron_expression: Cron expression (required if schedule_type="cron")
            interval_seconds: Repeat interval (required if schedule_type="interval")
            ends_at: Stop recurring after this time
            task_timezone: IANA timezone, e.g. "America/New_York"
            retry_policy: "none", "fixed", "linear", or "exponential"
            max_retries: Max retry attempts (required if retry_policy != "none")
            retry_delay_seconds: Base delay between retries

        Returns:
            Task ID string
        """
        url = f"{self._client.base_url}/api/tasks/"
        payload: Dict[str, Any] = {
            'task_name': task_name,
            'task_args': task_args or [],
            'task_kwargs': task_kwargs or {},
            'callback_url': callback_url,
            'schedule_type': schedule_type,
            'task_timezone': task_timezone,
            'retry_policy': retry_policy,
            'max_retries': max_retries,
            'retry_delay_seconds': retry_delay_seconds,
        }
        if schedule_time:
            payload['schedule_time'] = schedule_time.isoformat() if isinstance(schedule_time, datetime) else schedule_time
        if cron_expression:
            payload['cron_expression'] = cron_expression
        if interval_seconds is not None:
            payload['interval_seconds'] = interval_seconds
        if ends_at:
            payload['ends_at'] = ends_at.isoformat() if isinstance(ends_at, datetime) else ends_at
        
        try:
            response = self._client.session.post(url, json=payload, timeout=self._client.timeout)
            response.raise_for_status()
            data = response.json()
            task_id = data.get('task_id')
            if not task_id:
                raise ValueError("No task_id in server response")
            logger.info(f"Task scheduled successfully: {task_id}")
            return task_id
        except requests.HTTPError as e:
            error_detail = "Unknown error"
            try:
                if e.response is not None:
                    error_detail = e.response.text or str(e.response.json() if e.response.content else "No response body")
            except:
                error_detail = str(e)
            logger.error(f"Failed to schedule task: {e}")
            logger.error(f"Error response: {error_detail}")
            logger.error(f"Request payload: {payload}")
            raise
        except requests.RequestException as e:
            logger.error(f"Failed to schedule task: {e}")
            raise
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid response from server: {e}")
            raise
    
    async def schedule_many(
        self,
        tasks: List["Task"],
        max_workers: Optional[int] = None
    ) -> List[str]:
        """
        Schedule multiple tasks in parallel using asyncio and thread pool.
        
        Args:
            tasks: List of Task instances to schedule
            max_workers: Maximum number of worker threads (default: min(32, len(tasks) + 4))
        
        Returns:
            List of task IDs in the same order as input
            
        Example:
            ```python
            tasks = [
                Task(task_name="task1", callback_url="https://..."),
                Task(task_name="task2", callback_url="https://..."),
            ]
            task_ids = await client.tasks.schedule(tasks)
            ```
        """
        if not tasks:
            return []
        
        if max_workers is None:
            max_workers = min(32, len(tasks) + 4)
        
        async def schedule_one(task: "Task") -> str:
            """Schedule a single task in a thread pool."""
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                return await loop.run_in_executor(
                    executor,
                    self._schedule_single,
                    task.task_name,
                    str(task.callback_url),
                    task.task_args,
                    task.task_kwargs,
                    task.schedule_time,
                    task.schedule_type,
                    task.cron_expression,
                    task.interval_seconds,
                    task.ends_at,
                    task.task_timezone,
                    task.retry_policy,
                    task.max_retries,
                    task.retry_delay_seconds,
                )
        
        # Schedule all tasks in parallel
        task_ids = await asyncio.gather(*[schedule_one(task) for task in tasks])
        logger.info(f"Scheduled {len(task_ids)} tasks in parallel using {max_workers} workers")
        return list(task_ids)

